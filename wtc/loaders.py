"""ตัวอ่านข้อมูลดิบทั้งสามชนิดของโปรเจกต์นี้ — ตรวจสอบแล้วกับไฟล์จริง 2026-09-09

รูปแบบไฟล์ทั้งสามไม่เหมือนกันเลย และแต่ละอันมีรหัสค่าหายคนละแบบ
ถ้าอ่านผิด ทุกอย่างที่ตามมาผิดหมดโดยไม่มีอะไรเตือน — จึงแยกมาเป็นไฟล์เดียว
"""
from __future__ import annotations
import re
from pathlib import Path
import numpy as np

PSMSL_MISSING = -99999.0     # PSMSL ใช้ค่านี้ ไม่ใช่ NaN
NOAA_MISSING = -90.0         # NOAA PSL ใช้ค่าติดลบมาก ๆ (-99.99 / -9.9) ตัดที่ -90
UHSLC_MISSING = -32767       # UHSLC ใช้ค่านี้


def read_psmsl(path: str | Path) -> tuple[np.ndarray, np.ndarray]:
    """PSMSL .rlrdata -> (เวลาเป็นปีทศนิยม, ระดับน้ำ mm ใน RLR datum)

    รูปแบบ: `เวลา; ค่า; วันที่ขาด; flag` คั่นด้วย ';'
    ทั้งชุดรายเดือนและรายปีใช้ตัวอ่านเดียวกันได้
    """
    t, v = [], []
    for line in Path(path).read_text().splitlines():
        parts = [p.strip() for p in line.split(";")]
        if len(parts) < 2:
            continue
        val = float(parts[1])
        t.append(float(parts[0]))
        v.append(np.nan if val == PSMSL_MISSING else val)
    return np.asarray(t), np.asarray(v)


def read_noaa_index(path: str | Path) -> tuple[np.ndarray, np.ndarray]:
    """NOAA PSL .data -> (เวลาเป็นปีทศนิยม, ค่าดัชนีรายเดือน)

    รูปแบบ: บรรทัดแรกคือ `ปีเริ่ม ปีจบ` แล้วตามด้วยบรรทัดละ `ปี` + 12 คอลัมน์
    ท้ายไฟล์มีบรรทัด metadata ที่ต้องข้าม จึงกรองด้วย regex ปี 4 หลัก
    """
    lines = [l.rstrip() for l in Path(path).read_text().splitlines() if l.strip()]
    t, v = [], []
    for line in lines[1:]:
        parts = line.split()
        if len(parts) != 13 or not re.fullmatch(r"\d{4}", parts[0]):
            continue                     # บรรทัด metadata ท้ายไฟล์
        year = int(parts[0])
        for month, raw in enumerate(parts[1:]):
            x = float(raw)
            t.append(year + (month + 0.5) / 12)
            v.append(np.nan if x < NOAA_MISSING else x)
    return np.asarray(t), np.asarray(v)


def read_uhslc(path: str | Path) -> tuple[np.ndarray, np.ndarray]:
    """UHSLC hourly CSV -> (เวลาเป็นปีทศนิยมโดยประมาณ, ระดับน้ำ mm)

    รูปแบบ: `ปี,เดือน,วัน,ชั่วโมง,ค่า` ไม่มีหัวตาราง
    เวลาเป็นค่าประมาณแบบ 365.25 วัน/ปี — พอสำหรับการ decimate
    แต่ถ้าต้องการความแม่นระดับชั่วโมงให้ใช้ datetime แทน
    """
    import datetime as dt
    t, v = [], []
    for line in Path(path).read_text().splitlines():
        if not line.strip():
            continue
        y, mo, d, h, val = (int(x) for x in line.split(","))
        doy = dt.date(y, mo, d).timetuple().tm_yday
        t.append(y + ((doy - 1) * 24 + h) / (365.25 * 24))
        v.append(np.nan if val == UHSLC_MISSING else float(val))
    return np.asarray(t), np.asarray(v)


def read_uhslc_grid(path: str | Path) -> tuple[np.ndarray, np.ndarray]:
    """UHSLC hourly CSV -> (เวลาแบบ datetime64[h], ระดับน้ำ mm) บนกริดรายชั่วโมงที่ **ต่อเนื่องจริง**

    ต่างจาก read_uhslc() ตรงที่ใช้ปฏิทินจริงแทนปีทศนิยมโดยประมาณ — โซ่ decimate
    ต้องจัดกลุ่มตาม "วัน" และ "เดือนปฏิทิน" ให้ตรงกับที่ PSMSL ใช้ ปีทศนิยมแบบ 365.25 วัน
    จะทำให้ขอบเดือนเพี้ยนไปได้หลายชั่วโมงในปีที่ไม่ใช่ปีอธิกสุรทิน

    ตรวจว่ากริดไม่มีแถวขาด (ห่างกัน 1 ชั่วโมงพอดีทุกแถว) — ตัวกรอง FIR ถือว่าตัวอย่าง
    อยู่ห่างกันเท่ากันเสมอ ถ้าแถวหายไปแบบเงียบ ๆ ความถี่ที่ตัวกรองเห็นจะเพี้ยนทั้งหมด
    ⇒ ถ้าไม่ต่อเนื่องให้ล้มทันที ไม่ใช่ซ่อมเงียบ ๆ
    """
    raw = np.loadtxt(path, delimiter=",", dtype=np.int64, ndmin=2)
    days = np.array([f"{y:04d}-{m:02d}-{d:02d}" for y, m, d in raw[:, :3]],
                    dtype="datetime64[D]")
    t = days.astype("datetime64[h]") + raw[:, 3].astype("timedelta64[h]")
    step = np.diff(t).astype(int)
    if not np.all(step == 1):
        bad = int(np.flatnonzero(step != 1)[0])
        raise ValueError(f"กริดรายชั่วโมงไม่ต่อเนื่องที่แถว {bad}: {t[bad]} -> {t[bad + 1]}")
    v = raw[:, 4].astype(float)
    v[raw[:, 4] == UHSLC_MISSING] = np.nan
    return t, v


def read_uhslc_daily(path: str | Path) -> tuple[np.ndarray, np.ndarray]:
    """UHSLC daily CSV -> (วัน datetime64[D], ระดับน้ำ mm)

    รูปแบบ: `ปี,เดือน,วัน,ค่า` ไม่มีหัวตาราง · ค่าหาย -32767 เหมือนรายชั่วโมง
    ค่ารายวันของ UHSLC ผ่านตัวกรองน้ำขึ้นน้ำลงของเขาเองมาแล้ว — ใช้เป็นตัวเทียบ
    ขั้นรายวันของโซ่ decimate ที่เราเขียนเอง (wtc/multirate.py)
    """
    raw = np.loadtxt(path, delimiter=",", dtype=np.int64, ndmin=2)
    days = np.array([f"{y:04d}-{m:02d}-{d:02d}" for y, m, d in raw[:, :3]],
                    dtype="datetime64[D]")
    v = raw[:, 3].astype(float)
    v[raw[:, 3] == UHSLC_MISSING] = np.nan
    return days, v


def read_wnpmi(indices_dir: str | Path) -> tuple[np.ndarray, np.ndarray]:
    """WNPMI (Wang & Fan 1999) -> (เวลาเป็นปีทศนิยม, ดัชนีมรสุมแปซิฟิกตะวันตกเฉียงเหนือ)

        WNPMI = U850 เฉลี่ยพื้นที่ (5-15N, 100-130E)  -  U850 เฉลี่ยพื้นที่ (20-30N, 110-140E)

    NOAA PSL ไม่มีไฟล์สำเร็จของดัชนีนี้ — `fetch_data.py` โหลดค่าเฉลี่ยพื้นที่ของสองกล่อง
    มาเป็นไฟล์ดิบสองไฟล์ ส่วน **การลบทำที่นี่** เพราะเป็นการคำนวณ ไม่ใช่ข้อมูลที่แหล่งให้มา

    ค่าบวก = ลมตะวันตกที่ระดับ 850 hPa แรงผิดปกติเหนือทะเลจีนใต้ = มรสุมฤดูร้อนแรง
    (ตรวจแล้วกับไฟล์จริง: ค่าเฉลี่ยรายเดือนสูงสุด ก.ค.-ก.ย. +4 ถึง +6 m/s ต่ำสุด ธ.ค.-มี.ค.)
    """
    d = Path(indices_dir)
    ts, vs = read_noaa_index(d / "u850_box_south.data")
    tn, vn = read_noaa_index(d / "u850_box_north.data")
    if len(ts) != len(tn) or not np.allclose(ts, tn):
        raise ValueError("แกนเวลาของสองกล่องไม่ตรงกัน — โหลดมาคนละช่วงปีหรือเปล่า")
    return ts, vs - vn          # NaN ของกล่องไหนก็ตามจะลาม -> เป็น NaN ทั้งคู่ ซึ่งถูกแล้ว


def to_monthly_grid(t: np.ndarray, v: np.ndarray,
                    start: float, stop: float) -> tuple[np.ndarray, np.ndarray]:
    """จับข้อมูลลงกริดรายเดือนสม่ำเสมอ **โดยยังคง NaN ไว้ตามเดิม**

    ⚠️ ตั้งใจไม่เติมช่องว่างให้ — การเลือกวิธีเติมคือการตัดสินใจเชิงวิธีของโปรเจกต์นี้
    (ดู docs/feasibility.md §ผลทดสอบเบื้องต้น) ห้ามซ่อนไว้ในตัวอ่านไฟล์

    🐛 **แก้บั๊ก 2026-09-20** ของเดิมดูเพื่อนบ้านข้างเดียว (เฉพาะ index ที่ searchsorted คืนมา)
    ซึ่งเป็นตัวที่อยู่ "ถัดไป" เสมอ ⇒ เดือนที่เวลาในไฟล์ปัดลงมาต่ำกว่าจุดกริดนิดเดียว
    เช่น PSMSL เขียน 1951.2083 แต่จุดกริดคือ 1951.208333... จะถูกมองข้าม แล้วไปเทียบกับ
    เดือนถัดไปที่ห่าง 1/12 แทน ⇒ **หลุดทุกเดือนที่สาม** (ได้ 560 จาก 865 จุดแทนที่จะได้ 843)
    อาการคือข้อมูลหายเงียบ ๆ 35% โดยที่ไม่มีอะไร error — ต้องดูเพื่อนบ้าน **ทั้งสองข้าง**
    (ต้นเหตุจริงคือ PSMSL เก็บเวลาเป็นทศนิยม 4 ตำแหน่ง จึงไม่มีทางตรงกับ k/12 เป๊ะ ๆ)
    """
    grid = np.arange(start + 1 / 24, stop, 1 / 12)
    out = np.full_like(grid, np.nan)
    good = ~np.isnan(v)
    tg, vg = t[good], v[good]
    if len(tg) == 0:
        return grid, out
    hi = np.clip(np.searchsorted(tg, grid), 0, len(tg) - 1)
    lo = np.clip(hi - 1, 0, len(tg) - 1)
    pick = np.where(np.abs(tg[lo] - grid) <= np.abs(tg[hi] - grid), lo, hi)
    near = np.abs(tg[pick] - grid) < 1 / 24         # ต้องอยู่ในเดือนเดียวกันจริง
    out[near] = vg[pick][near]
    return grid, out
