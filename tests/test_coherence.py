"""ทดสอบ wtc/coherence.py — WTC

เกณฑ์ผ่าน (PLAN.md §6)
  - wtc(x, x) = 1 ทุกจุด ภายใน 1e-10
  - wtc ของ AR(1) อิสระสองเส้น: ค่าเฉลี่ยต้องใกล้ระดับ null ไม่ใช่ใกล้ 1
    (ถ้าได้ใกล้ 1 แปลว่าลืม smoothing)
  - 🚦 ประตูตาย G1: โค้ดเราเทียบ pycwt.wct — อยู่ใน scripts/validate_wtc.py
    (ต้องใช้ข้อมูลจริงและ pycwt จึงไม่เอามาไว้ใน unit test ที่ต้องรันเร็ว
     แต่มีตัวย่อส่วนที่ใช้ข้อมูลสังเคราะห์อยู่ในไฟล์นี้ ถ้าติดตั้ง pycwt ไว้)

⚠️ ห้ามใช้ KO LAK เป็นตัวตัดสินว่าโค้ดถูกหรือผิด — สถานีนั้นไม่มีสัญญาณจริง

เขียนแล้ว 2026-09-20 (W1)
"""
import numpy as np
import pytest

from wtc.coherence import wtc, xwt
from wtc.significance import ar1_surrogate, fit_ar1
from wtc.transform import DJ, DT_MONTHLY, cwt

N = 600


def _series(seed=0, a=0.5):
    rng = np.random.default_rng(seed)
    return ar1_surrogate(N, a, np.sqrt(1 - a ** 2), rng)


def test_wtc_of_series_with_itself_is_one():
    W, scales, _, _ = cwt(_series())
    R2, _ = wtc(W, W, DT_MONTHLY, DJ, scales)
    assert np.abs(R2 - 1).max() < 1e-10


def test_wtc_of_independent_series_is_not_one():
    """ถ้าได้ใกล้ 1 แปลว่า smoothing ไม่ทำงาน — เป็นบั๊กที่เงียบที่สุดของทั้งโปรเจกต์"""
    Wx, scales, _, _ = cwt(_series(seed=1))
    Wy, _, _, _ = cwt(_series(seed=2))
    R2, _ = wtc(Wx, Wy, DT_MONTHLY, DJ, scales)
    assert R2.mean() < 0.5
    assert R2.max() <= 1 + 1e-8


def test_wtc_stays_in_unit_interval():
    Wx, scales, _, _ = cwt(_series(seed=3, a=0.9))
    Wy, _, _, _ = cwt(_series(seed=4, a=0.1))
    R2, _ = wtc(Wx, Wy, DT_MONTHLY, DJ, scales)
    assert R2.min() >= 0
    assert R2.max() <= 1 + 1e-8


def test_phase_of_shifted_series_has_right_sign():
    """เลื่อนอนุกรมไปข้างหน้า -> เฟสต้องเปลี่ยนเครื่องหมายเมื่อสลับลำดับอาร์กิวเมนต์"""
    x = _series(seed=5)
    y = np.roll(x, 3)
    Wx, scales, _, _ = cwt(x)
    Wy, _, _, _ = cwt(y)
    _, ph_xy = wtc(Wx, Wy, DT_MONTHLY, DJ, scales)
    _, ph_yx = wtc(Wy, Wx, DT_MONTHLY, DJ, scales)
    assert np.allclose(ph_xy, -ph_yx, atol=1e-10)


def test_xwt_is_conjugate_symmetric():
    Wx, _, _, _ = cwt(_series(seed=6))
    Wy, _, _, _ = cwt(_series(seed=7))
    assert np.allclose(xwt(Wx, Wy), np.conj(xwt(Wy, Wx)))


def test_matches_pycwt_on_synthetic_data():
    """ประตู G1 ฉบับย่อ — ใช้ข้อมูลสังเคราะห์ ไม่ต้องรอไฟล์ข้อมูลจริง"""
    pycwt = pytest.importorskip("pycwt")
    from wtc.transform import OMEGA0, morlet_flambda
    x, y = _series(seed=8), _series(seed=9)
    dt, dj = DT_MONTHLY, DJ
    s0 = 2 * dt / morlet_flambda(OMEGA0)
    j = int(round(np.log2(N * dt / s0) / dj))
    Wx, scales, _, _ = cwt(x, dt, dj)
    Wy, _, _, _ = cwt(y, dt, dj)
    ours, _ = wtc(Wx, Wy, dt, dj, scales)
    theirs, _, _, _, _ = pycwt.wct(x, y, dt, dj=dj, s0=s0, J=j, sig=False,
                                   wavelet=pycwt.Morlet(OMEGA0), normalize=False)
    assert np.abs(ours - theirs).max() < 1e-10
