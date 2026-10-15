"""ทดสอบ wtc/significance.py และ wtc/metrics.py — นัยสำคัญของ WTC + PASC/AWC (W4)

เกณฑ์ผ่าน (PLAN.md §6)
  - **คู่ AR(1) ที่ไม่เกี่ยวกัน ต้องได้ PASC ทั้งระนาบเฉลี่ยใกล้ 5%** — นิยามของเกณฑ์ 95%
    ถ้าได้ต่ำหรือสูงกว่านี้มาก แปลว่า threshold หรือการนับพื้นที่ผิด
  - PASC ของระนาบที่มีนัยสำคัญทั้งหมด = 100 · ไม่มีเลย = 0
  - พื้นที่นอก COI / ที่มีของเติมเกินครึ่งต้องไม่ถูกนับทั้งในเศษและในส่วน
  - fit_ar1 ที่รับ mask ต้องไม่ถูกช่องว่างที่เติม 0 ดึงค่า a

เขียนแล้ว 2026-09-30 (W4)
"""
import numpy as np
import pytest

from wtc.coherence import wtc
from wtc.metrics import (awc, filled_fraction, pasc, significance, summarize,
                         valid_mask)
from wtc.significance import (ar1_surrogate, empirical_p, fit_ar1, pasc_null,
                              threshold_wtc)
from wtc.transform import DJ, DT_MONTHLY, cwt

N = 600


@pytest.fixture(scope="module")
def thr():
    return threshold_wtc(N, 0.6, 0.8, 0.9, np.sqrt(1 - 0.81), nmc=80, seed=3)


def test_null_pairs_give_about_five_percent(thr):
    rng = np.random.default_rng(42)
    got = []
    for _ in range(25):
        Wy, sc, per, coi = cwt(ar1_surrogate(N, 0.6, 0.8, rng))
        Wx, _, _, _ = cwt(ar1_surrogate(N, 0.9, np.sqrt(1 - 0.81), rng))
        R2, _ = wtc(Wy, Wx, DT_MONTHLY, DJ, sc)
        got.append(pasc(significance(R2, thr.per_scale),
                        valid_mask(per, coi, sc, DT_MONTHLY), per))
    assert 3.0 < np.mean(got) < 7.5


def test_identical_series_are_significant_everywhere(thr):
    x = ar1_surrogate(N, 0.6, 0.8, np.random.default_rng(1))
    W, sc, per, coi = cwt(x)
    R2, _ = wtc(W, W, DT_MONTHLY, DJ, sc)
    sig = significance(R2, thr.per_scale)
    v = valid_mask(per, coi, sc, DT_MONTHLY)
    assert pasc(sig, v, per) == pytest.approx(100.0)
    assert awc(R2, sig, v, per) == pytest.approx(1.0)


def test_threshold_is_in_unit_interval_and_u_shaped(thr):
    """threshold รูปตัว U: สองปลายของแกนสเกลสูงกว่าช่วงกลาง (เหตุผลใน threshold_wtc)

    เคยเขียนเทสต์นี้ว่า "สเกลใหญ่ต้องสูงกว่าสเกลเล็ก" แล้วพัง — สเกลเล็กสุดก็สูงเหมือนกัน
    """
    ok = np.isfinite(thr.per_scale)
    t = thr.per_scale[ok]
    assert np.all((t > 0) & (t < 1))
    middle = np.median(t[len(t) // 3: 2 * len(t) // 3])
    assert t[0] > middle and t[-1] > middle


def test_pasc_bounds_and_empty():
    per = np.array([1.0, 3.0, 10.0])
    valid = np.ones((3, 4), bool)
    assert pasc(np.ones((3, 4), bool), valid, per) == 100.0
    assert pasc(np.zeros((3, 4), bool), valid, per) == 0.0
    assert np.isnan(awc(np.ones((3, 4)), np.zeros((3, 4), bool), valid, per))


def test_pasc_ignores_points_that_are_not_valid():
    """จุดที่ไม่ valid ต้องหายไปทั้งจากเศษและส่วน — ไม่ใช่นับเป็น "ไม่มีนัยสำคัญ" """
    per = np.array([1.0, 3.0])
    sig = np.array([[True, True, False, False], [True, False, False, False]])
    valid = np.array([[True, True, False, False], [True, True, True, True]])
    # ที่นับได้ 6 จุด มีนัยสำคัญ 3 ⇒ 50%
    assert pasc(sig, valid, per) == pytest.approx(50.0)


def test_band_restricts_rows():
    per = np.array([1.0, 3.0, 10.0])
    sig = np.array([[True] * 4, [False] * 4, [True] * 4])
    valid = np.ones((3, 4), bool)
    assert pasc(sig, valid, per, (2.0, 7.0)) == 0.0
    assert pasc(sig, valid, per, (8.0, 16.0)) == 100.0


def test_filled_fraction_is_high_inside_long_gap_and_zero_far_away():
    sc = np.array([0.2, 1.0])
    f = np.zeros(600, bool)
    f[200:400] = True
    frac = filled_fraction(f, sc, DT_MONTHLY)
    assert frac[0, 300] > 0.99 and frac[0, 50] < 1e-6
    assert np.all((frac >= -1e-12) & (frac <= 1 + 1e-12))


def test_fit_ar1_ignores_interpolated_gaps():
    """ช่องว่างสั้นที่เติมด้วยเส้นตรงเรียบเกินจริง ⇒ ถ้าไม่ตัดออก a จะถูกดันขึ้น"""
    from wtc.preprocess import fill_gaps
    z = ar1_surrogate(2000, 0.3, np.sqrt(1 - 0.09), np.random.default_rng(5))
    for a in range(20, 1980, 12):
        z[a:a + 3] = np.nan                         # รู 3 เดือนถี่ ๆ ⇒ interp เชิงเส้น
    filled_z, filled = fill_gaps(z)
    a_masked, _ = fit_ar1(filled_z, filled)
    a_naive, _ = fit_ar1(filled_z)
    assert abs(a_masked - 0.3) < 0.07
    assert a_naive - 0.3 > 0.1                      # ยืนยันว่าเทสต์นี้วัดปัญหาจริง


def test_empirical_p():
    null = np.arange(100.0)
    assert empirical_p(1000.0, null) == pytest.approx(1 / 101)
    assert empirical_p(-1.0, null) == pytest.approx(1.0)


def test_pasc_null_mean_near_five_percent(thr):
    null = pasc_null(thr, N, 0.8, np.sqrt(1 - 0.81), nmc=30)
    assert 3.0 < np.mean(null["ทั้งระนาบ"]) < 7.5


def test_summarize_has_all_bands(thr):
    x = ar1_surrogate(N, 0.6, 0.8, np.random.default_rng(7))
    W, sc, per, coi = cwt(x)
    R2, _ = wtc(W, W, DT_MONTHLY, DJ, sc)
    s = summarize(R2, significance(R2, thr.per_scale), valid_mask(per, coi, sc, DT_MONTHLY), per)
    assert set(s) == {"ทั้งระนาบ", "2–7 ปี", "8–16 ปี"}
