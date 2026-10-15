"""เตรียมอนุกรมให้พร้อมเข้า CWT — ตัดแนวโน้ม/ฤดูกาล เติมช่องว่าง จัดแนวกริด

ลำดับที่ตั้งใจให้เป็น (และเหตุผลว่าทำไมสลับไม่ได้)

    1. จัดลงกริดรายเดือนร่วม           align()              ← NaN ยังอยู่ครบ
    2. ตัดแนวโน้ม + ฤดูกาล + normalize  detrend_deseason()   ← ฟิตบนจุดที่มีจริงเท่านั้น
    3. เติมช่องว่าง                     fill_gaps()          ← เติมบน anomaly ไม่ใช่บนค่าดิบ

**สลับ 2 กับ 3 ไม่ได้** ถ้าเติมก่อนฟิต ของที่เราเดาขึ้นมาเองจะเข้าไปออกเสียงในสัมประสิทธิ์
ของแนวโน้มและฤดูกาล แล้วผลที่ได้จะขึ้นกับวิธีเติมช่องว่าง ซึ่งเป็นสิ่งที่ไม่ควรเกิด
(นี่คือจุดที่ scripts/baseline_pycwt.py ทำหยาบไว้ — ที่นั่น interp ก่อนแล้วค่อย deseason
ตอนนี้เราทำกลับด้านให้ถูก)

การตัดสินใจที่ประกาศไว้ใน PLAN.md §4 และทำจริงในไฟล์นี้
  - ฟิต `แนวโน้มเชิงเส้น + ฮาร์มอนิก 1 ปี และ 1/2 ปี` บนจุดที่มีข้อมูลจริงเท่านั้น
  - ช่องว่าง <=3 เดือน -> interp เชิงเส้น · >3 เดือน -> เติม 0 (= ค่าปกติทางภูมิอากาศ)
  - **คืน mask ของที่เติมออกมาด้วยเสมอ** metrics.py ต้องใช้ตัดคอลัมน์เวลาที่หน้าต่าง
    smoothing มีของเติมเกิน 50% ออกจากการนับ PASC — ห้ามให้ mask หายไปในฟังก์ชัน

เขียนแล้ว 2026-09-20 (ดึงมาจาก W2 เพราะ build_series.py ของ W1 ต้องใช้)
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np

from .loaders import to_monthly_grid

MAX_INTERP_MONTHS = 3      # ยาวกว่านี้ไม่ interp — ดูเหตุผลใน fill_gaps()


@dataclass
class DeseasonInfo:
    """ของที่ถอดออกไป — เก็บไว้รายงานและพล็อต ไม่ใช่ผลข้างเคียงที่ทิ้งได้"""
    slope: float              # แนวโน้มเชิงเส้น ต่อหนึ่งหน่วยเวลา (ปี)
    annual_amp: float         # แอมพลิจูดของวงรอบ 1 ปี
    semiannual_amp: float     # แอมพลิจูดของวงรอบ 1/2 ปี
    frac_trend: float         # สัดส่วนความแปรปรวนที่แนวโน้มอธิบาย
    frac_season: float        # สัดส่วนที่ฤดูกาลอธิบาย (ของที่เหลือหลังตัดแนวโน้ม)
    resid_std: float          # ส่วนเบี่ยงเบนของ anomaly ก่อน normalize (หน่วยเดิม)
    n_used: int               # จำนวนจุดที่เอาไปฟิตจริง


def _design(t: np.ndarray) -> np.ndarray:
    """เมทริกซ์ออกแบบ: [แนวโน้ม, ค่าคงที่, sin/cos 1 ปี, sin/cos 1/2 ปี]

    t เป็นปีทศนิยม ⇒ 2*pi*k*t ให้วงรอบ 1 ปี (k=1) และ 1/2 ปี (k=2) ตรง ๆ
    ใช้ harmonic regression แทนตัวกรอง เพราะข้อมูลมีช่องว่าง — การ fit ไม่ต้องการกริดที่ครบ
    แต่ตัวกรองต้องการ (ประเด็นเดียวกับที่ check_data.seasonal_split ใช้อยู่)
    """
    return np.column_stack(
        [t - t.mean(), np.ones_like(t)] +
        [f(2 * np.pi * k * t) for k in (1, 2) for f in (np.sin, np.cos)]
    )


def detrend_deseason(t: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, DeseasonInfo]:
    """ตัดแนวโน้มเชิงเส้น + วงรอบปี/ครึ่งปี แล้ว normalize ให้ความแปรปรวนเป็น 1

    **NaN ที่เข้ามายังเป็น NaN ที่ออกไป** — ฟังก์ชันนี้ไม่เติมช่องว่างให้ นั่นเป็นหน้าที่
    ของ fill_gaps() ที่แยกไว้ต่างหากโดยตั้งใจ

    ทำไมต้อง normalize: coherence ไม่สนใจสเกลของแอมพลิจูดอยู่แล้ว (มันหารกันหายไป)
    แต่ significance ที่สร้างจาก AR(1) สนใจ ⇒ ทำให้ทุกอนุกรมอยู่บนหน่วยเดียวกันไว้ก่อน
    """
    t = np.asarray(t, float)
    y = np.asarray(y, float)
    g = np.isfinite(y)
    if g.sum() < 24:
        raise ValueError(f"มีข้อมูลจริงแค่ {g.sum()} จุด — น้อยเกินกว่าจะฟิตฤดูกาลได้")

    A = _design(t)
    coef = np.linalg.lstsq(A[g], y[g], rcond=None)[0]
    resid = y - A @ coef                     # NaN ลามต่อไปเองตรงจุดที่ไม่มีข้อมูล

    # สถิติไว้รายงาน — คิดบนจุดที่มีข้อมูลจริงเท่านั้นทั้งหมด
    trend_only = A[:, :2] @ coef[:2]
    after_trend = y - trend_only
    info = DeseasonInfo(
        slope=float(coef[0]),
        annual_amp=float(np.hypot(coef[2], coef[3])),
        semiannual_amp=float(np.hypot(coef[4], coef[5])),
        frac_trend=float(1 - np.var(after_trend[g]) / np.var(y[g])),
        frac_season=float(1 - np.var(resid[g]) / np.var(after_trend[g])),
        resid_std=float(np.std(resid[g])),
        n_used=int(g.sum()),
    )
    z = (resid - np.mean(resid[g])) / info.resid_std
    return z, info


def fill_gaps(y: np.ndarray, max_interp: int = MAX_INTERP_MONTHS
              ) -> tuple[np.ndarray, np.ndarray]:
    """เติมช่องว่างบน anomaly -> (y_filled, filled_mask)

    ช่องว่างสั้น (<= max_interp) -> interp เชิงเส้น
        สมเหตุสมผลเพราะ anomaly ของระดับน้ำทะเลมี autocorrelation สูงที่ lag 1-3 เดือน

    ช่องว่างยาว (> max_interp) -> **เติม 0 ไม่ใช่ interp**
        0 บน anomaly ที่ normalize แล้ว = "ค่าปกติทางภูมิอากาศ" การ interp ข้ามช่องว่าง
        ยาว ๆ จะสร้างเส้นตรงเนียน ๆ ที่ดูเหมือนสัญญาณคาบยาวของจริง แล้วมันจะไปโผล่เป็น
        coherence ปลอมที่แถบคาบยาว ซึ่งเป็นแถบที่เราจะรายงานพอดี (ปี 2004 ที่หายทั้งปี
        ทั้งสามสถานีคือกรณีตัวอย่าง) การเติม 0 ทำให้ power ตรงนั้น "จืด" ซึ่งเป็นความผิด
        ที่ปลอดภัยกว่า — และ mask ที่คืนไปด้วยทำให้ตัดบริเวณนั้นออกจากการนับได้ภายหลัง

    mask ที่คืน: True = ตำแหน่งที่เป็นของเติม ไม่ใช่ของจริง
    """
    y = np.asarray(y, float).copy()
    filled = ~np.isfinite(y)
    if not filled.any():
        return y, filled
    if filled.all():
        raise ValueError("ไม่มีข้อมูลจริงเลยสักจุด")

    idx = np.arange(len(y))
    good = ~filled

    # ไล่หาช่วงที่หายติดกันเป็นก้อน แล้วตัดสินใจทีละก้อนตามความยาว
    edges = np.flatnonzero(np.diff(np.r_[0, filled.view(np.int8), 0]))
    for a, b in zip(edges[::2], edges[1::2]):        # ช่องว่างคือ y[a:b]
        run = b - a
        touches_edge = a == 0 or b == len(y)         # ขอบอนุกรม: interp ไม่ได้อยู่ดี
        if run <= max_interp and not touches_edge:
            y[a:b] = np.interp(idx[a:b], idx[good], y[good])
        else:
            y[a:b] = 0.0
    return y, filled


def common_window(series: dict[str, tuple[np.ndarray, np.ndarray]]) -> tuple[float, float]:
    """หน้าต่างเวลาที่ทุกอนุกรม "มีข้อมูลจริง" ทับกัน (ปีทศนิยม)

    คิดจากจุดที่ไม่ใช่ NaN เท่านั้น — อนุกรมหลายตัวมีแถวของเดือนที่ยังไม่มีค่าต่อท้ายไฟล์
    ถ้าดูแค่ช่วงของแกนเวลา จะได้หน้าต่างที่ยาวเกินจริง
    **ต้องคำนวณจากไฟล์จริงทุกครั้ง ห้าม hard-code** (PLAN.md §1.3)
    """
    lo = max(t[np.isfinite(v)][0] for t, v in series.values())
    hi = min(t[np.isfinite(v)][-1] for t, v in series.values())
    if hi <= lo:
        raise ValueError("ไม่มีหน้าต่างที่ทุกอนุกรมทับกัน")
    return float(lo), float(hi)


def align(series: dict[str, tuple[np.ndarray, np.ndarray]],
          start: float, stop: float) -> tuple[np.ndarray, dict[str, np.ndarray]]:
    """จับทุกอนุกรมลงกริดรายเดือนร่วมอันเดียว โดย **ยังคง NaN ไว้ตามเดิม**

    กริดมาจาก loaders.to_monthly_grid ซึ่งจับค่าที่อยู่ในเดือนเดียวกันจริง ๆ เท่านั้น
    (ห่างเกินครึ่งเดือนถือว่าไม่มีค่า) ⇒ ถ้าแหล่งข้อมูลนิยามเวลาคนละแบบเล็กน้อย
    จะกลายเป็น NaN ให้เห็น ไม่ใช่ค่าที่ถูกลากมาจากเดือนอื่นแบบเงียบ ๆ

    🐛 **กับดักที่เจอจริงตอนรันครั้งแรก 2026-09-20** — to_monthly_grid สร้างกริดเป็น
    `arange(start + 1/24, stop, 1/12)` คือมันคาดว่า start เป็น **ขอบปี/ขอบเดือน**
    แล้วบวก 1/24 เองเพื่อไปอยู่กลางเดือน แต่ common_window() คืนเวลาของจุดข้อมูลจริง
    ซึ่ง**กลางเดือนอยู่แล้ว** ⇒ กริดเลื่อนไปครึ่งเดือน แล้วเกณฑ์ "ห่างไม่เกินครึ่งเดือน"
    ก็ตัดข้อมูลทิ้งเกือบหมด (เหลือ 279 จาก 864 จุด ที่สถานี และเหลือ 2 จุดที่ดัชนี)
    อาการคือ "ข้อมูลหายเฉย ๆ" ซึ่งถ้าไม่มีตัวพิมพ์จำนวนจุดออกมาดูก็จะไม่มีอะไรเตือนเลย
    ⇒ ที่นี่จึง **ปัดหน้าต่างลงไปที่ขอบเดือนก่อน** แล้วค่อยส่งต่อ
    """
    start = np.floor(start * 12) / 12          # ขอบเดือนของเดือนที่ start อยู่
    stop = np.ceil(stop * 12) / 12             # ขอบเดือนถัดจากเดือนที่ stop อยู่ (รวมเดือนนั้นด้วย)
    grid = None
    out: dict[str, np.ndarray] = {}
    for name, (t, v) in series.items():
        g, vv = to_monthly_grid(np.asarray(t, float), np.asarray(v, float), start, stop)
        if grid is None:
            grid = g
        elif len(g) != len(grid) or not np.allclose(g, grid):
            raise ValueError(f"กริดของ {name} ไม่ตรงกับตัวอื่น")
        out[name] = vv
    assert grid is not None
    return grid, out
