"""ทดสอบไปป์ไลน์ต้นน้ำ — preprocess, multirate, metrics

เกณฑ์ผ่าน (PLAN.md §6)

  preprocess   ✅ เขียนแล้ว 2026-09-20
    - detrend_deseason ต้องฟิตบนจุดที่มีข้อมูลจริงเท่านั้น
      (ทดสอบด้วยการเจาะรูในอนุกรมสังเคราะห์แล้วดูว่าสัมประสิทธิ์ไม่ขยับ)
    - fill_gaps ต้องคืน mask ที่ True ตรงตำแหน่งที่เติมจริงทุกตำแหน่ง

  multirate    ✅ ย้ายไป tests/test_multirate.py แล้ว (2026-09-30)
  metrics      ✅ อยู่ใน tests/test_significance.py (2026-09-30)
"""
import numpy as np
import pytest

from wtc.preprocess import align, common_window, detrend_deseason, fill_gaps

T = np.arange(1951 + 1 / 24, 2023, 1 / 12)


def _synthetic(slope=2.5, amp=30.0, noise=0.0, seed=0):
    rng = np.random.default_rng(seed)
    return (slope * (T - T.mean()) + amp * np.sin(2 * np.pi * T)
            + rng.normal(0, noise, len(T)))


def test_detrend_recovers_known_coefficients():
    _, info = detrend_deseason(T, _synthetic())
    assert info.slope == pytest.approx(2.5, abs=1e-6)
    assert info.annual_amp == pytest.approx(30.0, abs=1e-6)


def test_detrend_fits_only_on_observed_points():
    """เจาะรูแล้วสัมประสิทธิ์ต้องแทบไม่ขยับ — ถ้าขยับแปลว่าเผลอเอา NaN/ของเติมไปฟิต"""
    y = _synthetic(noise=3.0, seed=1)
    holed = y.copy()
    holed[100:103] = np.nan
    holed[500:520] = np.nan
    a = detrend_deseason(T, y)[1]
    b = detrend_deseason(T, holed)[1]
    assert b.slope == pytest.approx(a.slope, abs=0.02)
    assert b.annual_amp == pytest.approx(a.annual_amp, abs=0.2)
    assert b.n_used == len(T) - 23


def test_detrend_keeps_nan_where_input_had_nan():
    y = _synthetic(noise=1.0)
    y[200:210] = np.nan
    z, _ = detrend_deseason(T, y)
    assert np.isnan(z[200:210]).all()
    assert np.isfinite(np.delete(z, np.s_[200:210])).all()


def test_detrend_normalises_to_unit_variance():
    z, _ = detrend_deseason(T, _synthetic(noise=7.0, seed=2))
    assert np.nanstd(z) == pytest.approx(1.0, abs=1e-12)


def test_fill_gaps_mask_marks_every_filled_point():
    z = np.arange(100.0)
    z[10:12] = np.nan          # รูสั้น -> interp
    z[40:60] = np.nan          # รูยาว -> เติม 0
    filled, mask = fill_gaps(z, max_interp=3)
    assert mask.sum() == 22
    assert np.array_equal(np.flatnonzero(mask), np.r_[10:12, 40:60])
    assert np.isfinite(filled).all()


def test_fill_gaps_short_gap_is_interpolated_long_gap_is_zero():
    z = np.arange(100.0)
    z[10:12] = np.nan
    z[40:60] = np.nan
    filled, _ = fill_gaps(z, max_interp=3)
    assert filled[10] == pytest.approx(10.0)      # เส้นตรงเดิม
    assert filled[11] == pytest.approx(11.0)
    assert np.all(filled[40:60] == 0.0)


def test_fill_gaps_at_the_edges_uses_zero_not_extrapolation():
    """ขอบอนุกรม interp ไม่ได้ (ไม่มีจุดอีกข้าง) ⇒ ต้องเป็น 0 ไม่ใช่การลากเส้นออกไป"""
    z = np.arange(50.0)
    z[:2] = np.nan
    z[-1] = np.nan
    filled, mask = fill_gaps(z, max_interp=3)
    assert np.all(filled[:2] == 0.0) and filled[-1] == 0.0
    assert mask[:2].all() and mask[-1]


def test_common_window_uses_finite_points_only():
    t = np.arange(1950, 1960, 1 / 12)
    a = np.ones_like(t); a[:12] = np.nan          # เริ่มช้ากว่า 1 ปี
    b = np.ones_like(t); b[-24:] = np.nan         # จบเร็วกว่า 2 ปี
    lo, hi = common_window({"a": (t, a), "b": (t, b)})
    assert lo == pytest.approx(t[12])
    assert hi == pytest.approx(t[-25])


def test_align_puts_every_series_on_one_grid():
    t1 = np.arange(1950 + 1 / 24, 1960, 1 / 12)
    t2 = t1 + 1e-5                                 # เวลาปัดเศษต่างกันนิดหน่อย
    grid, out = align({"a": (t1, np.arange(len(t1), dtype=float)),
                       "b": (t2, np.arange(len(t2), dtype=float))}, 1951.0, 1955.0)
    assert len(grid) == len(out["a"]) == len(out["b"])
    assert np.allclose(out["a"], out["b"])         # ความต่าง 1e-5 ต้องไม่ทำให้หลุดกริด
    assert np.isfinite(out["a"]).all()
