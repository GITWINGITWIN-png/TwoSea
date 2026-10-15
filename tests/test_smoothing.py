import numpy as np
import pytest

from wtc.smoothing import (DELTA_J0, boxcar_scale_weights, gaussian_time_weights,
                           smooth, smooth_scale, smooth_time)

DT = 1 / 12
DJ = 1 / 12
SCALES = 2 * DT / 1.033 * 2 ** (np.arange(60) * DJ)


def test_gaussian_weights_sum_to_one():
    for scale in (0.2, 1.0, 8.0):
        w = gaussian_time_weights(scale, DT)
        assert abs(w.sum() - 1) < 1e-12


def test_boxcar_weights_sum_to_one():
    for dj in (1 / 4, 1 / 12, 1 / 24):
        assert abs(boxcar_scale_weights(dj).sum() - 1) < 1e-12


def test_boxcar_is_trapezoid_not_flat():
    w = boxcar_scale_weights(DJ)
    assert len(w) == round(2 * DELTA_J0 / DJ)
    assert w[0] == pytest.approx(w[len(w) // 2] / 2)
    assert w[-1] == pytest.approx(w[len(w) // 2] / 2)


def test_gaussian_width_grows_with_scale():
    widths = [len(gaussian_time_weights(s, DT)) for s in (0.25, 1.0, 4.0)]
    assert widths[0] < widths[1] < widths[2]


def test_smooth_constant_stays_constant():
    C = np.full((len(SCALES), 300), 2.5)
    out = smooth_scale(smooth_time(C, DT, SCALES, pad="wrap"), DJ)
    assert np.abs(out - 2.5).max() < 1e-12


def test_smooth_zero_pad_keeps_interior_constant():
    C = np.full((20, 2000), 2.5)
    scales = SCALES[:20]
    out = smooth(C, DT, DJ, scales)
    mid = out[:, 800:1200]
    assert np.abs(mid - 2.5).max() < 1e-9


def test_fft_path_matches_explicit_kernel():
    rng = np.random.default_rng(0)
    x = rng.normal(size=(1, 2000))
    scale = 0.5
    fast = smooth_time(x, DT, np.array([scale]), pad="wrap")[0]
    slow = np.convolve(x[0], gaussian_time_weights(scale, DT), mode="same")
    assert np.abs(fast[600:1400] - slow[600:1400]).max() < 1e-8


def test_scale_edge_renormalisation_is_a_row_scaling():
    rng = np.random.default_rng(1)
    A = rng.normal(size=(40, 50)) ** 2
    ratio = smooth_scale(A, DJ, edge="renorm") / smooth_scale(A, DJ, edge="zero")
    assert np.allclose(ratio, ratio[:, :1])
