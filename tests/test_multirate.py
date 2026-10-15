import numpy as np
import pytest

from wtc.multirate import (TIDES_CPD, compare, daily_to_monthly, decimal_year_to_month,
                           design_lowpass, fir_at, hourly_to_daily, kaiser_beta,
                           kaiser_numtaps, kaiser_window, monthly_to_annual, naive_daily)

SPEC = dict(f_pass=0.1, f_stop=0.5, atten_db=70.0, fs=24.0)


@pytest.fixture(scope="module")
def design():
    return design_lowpass(**SPEC)


def _hourly_grid(n_days=400, start="2001-01-01"):
    t0 = np.datetime64(start, "h")
    return np.arange(t0, t0 + np.timedelta64(n_days * 24, "h"))


def test_kaiser_parameters_match_scipy():
    signal = pytest.importorskip("scipy.signal")
    n_ref, beta_ref = signal.kaiserord(70.0, (0.5 - 0.1) / 12)
    assert kaiser_numtaps(70.0, 0.1, 0.5, 24.0) == n_ref
    assert kaiser_beta(70.0) == pytest.approx(beta_ref, abs=1e-12)


def test_kaiser_window_matches_scipy():
    signal = pytest.importorskip("scipy.signal")
    for n, beta in ((261, 6.7553), (51, 3.0), (11, 0.0)):
        assert np.abs(kaiser_window(n, beta) - signal.windows.kaiser(n, beta)).max() < 1e-12


def test_taps_match_scipy_firwin(design):
    signal = pytest.importorskip("scipy.signal")
    ref = signal.firwin(design.numtaps, design.cutoff, window=("kaiser", design.beta), fs=24.0)
    assert np.abs(ref - design.taps).max() < 1e-12


def test_design_meets_its_own_spec(design):
    assert design.measured_stopband_db() >= SPEC["atten_db"]
    assert design.numtaps % 2 == 1
    assert abs(design.taps.sum() - 1) < 1e-12
    assert np.allclose(design.taps, design.taps[::-1])


def test_every_tidal_constituent_is_below_spec(design):
    gains_db = 20 * np.log10(design.gain_at(list(TIDES_CPD.values())))
    assert np.all(gains_db <= -SPEC["atten_db"])


def test_fir_at_equals_filter_everything_then_pick(design):
    x = np.random.default_rng(0).normal(size=5000)
    centers = np.arange(300, 4700, 24)
    full = np.convolve(x, design.taps, mode="same")
    assert np.abs(fir_at(x, design.taps, centers) - full[centers]).max() < 1e-12


def test_tones_above_new_nyquist_do_not_survive(design):
    t = _hourly_grid()
    h = np.arange(len(t), dtype=float)
    x = sum(1000.0 * np.cos(2 * np.pi * f * h / 24 + k)
            for k, f in enumerate(TIDES_CPD.values()))
    _, daily = hourly_to_daily(t, x, design)
    residual = np.nanmax(np.abs(daily))
    assert residual < 8000 * 10 ** (-SPEC["atten_db"] / 20)


def test_without_filter_tides_alias_into_slow_bands():
    t = _hourly_grid(n_days=3 * 365)
    h = np.arange(len(t), dtype=float)
    x = 1000.0 * np.cos(2 * np.pi * TIDES_CPD["K1"] * h / 24)
    _, daily = naive_daily(t, x)
    spec = np.abs(np.fft.rfft(daily - daily.mean()))
    f = np.fft.rfftfreq(len(daily), d=1.0)
    peak_period = 1 / f[np.argmax(spec[1:]) + 1]
    assert 300 < peak_period < 450
    assert np.ptp(daily) > 1000


def test_slow_signal_passes_unchanged(design):
    t = _hourly_grid(n_days=200)
    h = np.arange(len(t), dtype=float)
    slow = 100.0 * np.sin(2 * np.pi * h / (24 * 60))
    _, daily = hourly_to_daily(t, slow, design)
    truth = slow[12::24]
    ok = np.isfinite(daily)
    assert np.abs(daily[ok] - truth[ok]).max() < 0.1


def test_nan_anywhere_in_the_window_gives_nan(design):
    t = _hourly_grid(n_days=60)
    x = np.zeros(len(t))
    x[30 * 24] = np.nan
    days, daily = hourly_to_daily(t, x, design)
    bad = np.flatnonzero(np.isnan(daily))
    half = design.numtaps // 2
    centers = np.arange(12, len(t), 24)
    expected = np.flatnonzero(np.abs(centers - 30 * 24) <= half)
    edge = np.flatnonzero((centers < half) | (centers >= len(t) - half))
    assert set(bad) == set(expected) | set(edge)


def test_monthly_mean_uses_calendar_months_and_min_days():
    days = np.arange(np.datetime64("2001-01-01"), np.datetime64("2001-04-01"))
    x = np.where(days.astype("datetime64[M]") == np.datetime64("2001-02"), 20.0, 10.0)
    x[days.astype("datetime64[M]") == np.datetime64("2001-03")] = np.nan
    x[np.flatnonzero(days.astype("datetime64[M]") == np.datetime64("2001-03"))[:14]] = 30.0
    months, mean, counts = daily_to_monthly(days, x, min_days=15)
    assert list(months.astype(str)) == ["2001-01", "2001-02", "2001-03"]
    assert mean[0] == 10.0 and mean[1] == 20.0
    assert np.isnan(mean[2]) and counts[2] == 14


def test_annual_requires_all_twelve_months():
    months = np.arange(np.datetime64("2001-01"), np.datetime64("2003-01"))
    x = np.ones(len(months))
    x[5] = np.nan
    years, mean, counts = monthly_to_annual(months, x)
    assert list(years) == [2001, 2002]
    assert np.isnan(mean[0]) and counts[0] == 11
    assert mean[1] == 1.0


def test_decimal_year_to_month_survives_four_decimal_rounding():
    t = np.round(1985 + (np.arange(36) + 0.5) / 12, 4)
    m = decimal_year_to_month(t)
    assert np.array_equal(m, np.arange(np.datetime64("1985-01"), np.datetime64("1988-01")))


def test_compare_removes_constant_offset():
    k = np.arange(np.datetime64("2001-01"), np.datetime64("2002-01"))
    a = np.arange(12.0)
    c = compare(k, a + 4827.0, k, a)
    assert c.offset == pytest.approx(4827.0)
    assert c.rms < 1e-12 and c.n == 12
