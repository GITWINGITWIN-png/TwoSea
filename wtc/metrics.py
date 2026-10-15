"""★ PASC และ AWC — ตัววัดผลที่ใช้เทียบกับเปเปอร์ต้นทางได้ตรง ๆ

    PASC = 100 * พื้นที่ที่มีนัยสำคัญ / (พื้นที่ที่มีนัยสำคัญ + พื้นที่ที่ไม่มีนัยสำคัญ)
    AWC  = ค่าเฉลี่ยของ coherence **เฉพาะในพื้นที่ที่มีนัยสำคัญ**

ข้อสังเกตจากเปเปอร์ต้นทางที่ต้องจำ (docs/source-paper-detail.md §3.5)
  - ตัวชี้ว่าปัจจัยไหนเป็นตัวหลักคือ **PASC ไม่ใช่ AWC**
    (AWC ของทั้ง 6 ดัชนีในงานเขาต่างกันไม่ถึง 0.1 — แยกอะไรแทบไม่ได้)
  - AWC เป็นสถิติแบบมีเงื่อนไข: เฉลี่ยเฉพาะพื้นที่ที่ถูกเลือกเพราะมีค่าสูง
    -> เทียบข้ามชุดที่พื้นที่ต่างกันไม่ได้ตรง ๆ
  - เกณฑ์ว่าดัชนีที่เพิ่มเข้ามา "สำคัญ" = PASC เพิ่มอย่างน้อย 5% (Hu et al. 2017)

สามจุดที่เปเปอร์ต้นทางไม่บอก และเราตัดสินใจเองแล้ว (PLAN.md §4)
  1. **ตัด** พื้นที่นอก cone of influence ออกจากทั้งเศษและส่วน
  2. นับ pixel บนแกน **log-scale** — แกนสเกลของ CWT วางแบบดยาดิก (ห่างกันเท่ากันใน log2)
     ⇒ "นับ pixel เฉย ๆ" คือ "นับพื้นที่บนแกน log" อยู่แล้ว ไม่ต้องถ่วงน้ำหนักเพิ่ม
     (ถ้าอยากได้พื้นที่บนแกนเชิงเส้นต้องถ่วงด้วยความกว้างสเกล ซึ่งจะให้สเกลใหญ่ครองผลเกือบหมด)
  3. ตัดจุดที่หน้าต่าง smoothing มีของเติมช่องว่างเกิน 50% ออกด้วย
     (mask มาจาก preprocess.fill_gaps · คิดแยกรายสเกลเพราะหน้าต่างกว้างไม่เท่ากัน)

รายงานทั้งระนาบ **และ** แยกแถบ 2-7 ปี (ENSO) กับ 8-16 ปี (PDO/IPO)

เขียนแล้ว 2026-09-30 (W4)
"""
from __future__ import annotations
import numpy as np

from .smoothing import smooth_time
from .transform import coi_mask

MAX_FILLED_FRACTION = 0.5
BANDS: dict[str, tuple[float, float] | None] = {
    "ทั้งระนาบ": None,
    "2–7 ปี": (2.0, 7.0),        # ENSO
    "8–16 ปี": (8.0, 16.0),      # PDO / IPO
}


def filled_fraction(filled: np.ndarray, scales: np.ndarray, dt: float) -> np.ndarray:
    """(nscale, ntime) สัดส่วนของ "ของเติม" ภายในหน้าต่าง S_time ของแต่ละสเกล

    ใช้ Gaussian ตัวเดียวกับที่ smoothing ใช้จริง ⇒ วัดได้ตรงว่าค่า R^2 ที่จุดนั้น
    ได้อิทธิพลจากข้อมูลที่เราแต่งขึ้นเองมากแค่ไหน
    หารด้วยผล smooth ของ "1 ทุกจุด" เพื่อให้ขอบอนุกรมยังเป็นสัดส่วนที่ถูก (smoothing
    เติมศูนย์ที่ขอบ ถ้าไม่ normalize ขอบจะดูเหมือนมีของเติมน้อยกว่าความจริง)
    """
    f = np.broadcast_to(np.asarray(filled, float)[None, :], (len(scales), len(filled)))
    num = smooth_time(f, dt, scales)
    den = smooth_time(np.ones_like(f), dt, scales)
    return num / den


def valid_mask(periods: np.ndarray, coi: np.ndarray, scales: np.ndarray, dt: float,
               *filled: np.ndarray, max_filled: float = MAX_FILLED_FRACTION) -> np.ndarray:
    """จุดที่นับได้ = อยู่ในกรวย COI **และ** ของเติมในหน้าต่างไม่เกิน max_filled (ทุกอนุกรม)"""
    ok = coi_mask(periods, coi)
    for m in filled:
        if m is not None and np.any(m):
            ok &= filled_fraction(m, scales, dt) <= max_filled
    return ok


def band_rows(periods: np.ndarray, band: tuple[float, float] | None) -> np.ndarray:
    if band is None:
        return np.ones(len(periods), bool)
    return (periods >= band[0]) & (periods <= band[1])


def pasc(sig: np.ndarray, valid: np.ndarray, periods: np.ndarray,
         band: tuple[float, float] | None = None) -> float:
    """ร้อยละของพื้นที่ที่มีนัยสำคัญ **ในบรรดาจุดที่นับได้** ของแถบคาบที่ระบุ"""
    rows = band_rows(periods, band)
    v = valid[rows]
    n = int(v.sum())
    return float("nan") if n == 0 else 100.0 * float((sig[rows] & v).sum()) / n


def awc(R2: np.ndarray, sig: np.ndarray, valid: np.ndarray, periods: np.ndarray,
        band: tuple[float, float] | None = None) -> float:
    """ค่าเฉลี่ยของ R^2 เฉพาะจุดที่มีนัยสำคัญและนับได้ — NaN ถ้าไม่มีจุดเลย"""
    rows = band_rows(periods, band)
    m = sig[rows] & valid[rows]
    return float("nan") if not m.any() else float(R2[rows][m].mean())


def significance(R2: np.ndarray, threshold_per_scale: np.ndarray) -> np.ndarray:
    """จุดที่ R^2 เกิน threshold ของสเกลตัวเอง (สเกลที่ threshold เป็น NaN = ไม่มีนัยสำคัญ)"""
    thr = np.asarray(threshold_per_scale, float)[:, None]
    with np.errstate(invalid="ignore"):
        return np.where(np.isfinite(thr), R2 > thr, False)


def summarize(R2: np.ndarray, sig: np.ndarray, valid: np.ndarray,
              periods: np.ndarray) -> dict[str, dict[str, float]]:
    """PASC / AWC / จำนวนจุดที่นับได้ ของทุกแถบใน BANDS"""
    out = {}
    for name, band in BANDS.items():
        rows = band_rows(periods, band)
        out[name] = {"pasc": pasc(sig, valid, periods, band),
                     "awc": awc(R2, sig, valid, periods, band),
                     "n_valid": int(valid[rows].sum())}
    return out
