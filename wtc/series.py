"""สร้างเมทริกซ์วิเคราะห์ (Y สถานี × X ดัชนี บนกริดรายเดือนร่วม) — แบบมาตรฐานและแบบทดสอบความไว

    build_series(BASELINE)            = สิ่งที่ scripts/build_series.py เขียนลง series.npz
    build_series(VARIANTS["cut_2004"]) = แบบทดสอบความไวของ W7

ย้ายมาจาก scripts/build_series.py เมื่อ 2026-10-07 (W7) เพื่อให้สคริปต์ทดสอบความไวสร้างอนุกรมแบบอื่น
ได้ด้วยโค้ดเส้นเดียวกันทุกบรรทัด — ถ้าแต่ละแบบมีโค้ดสร้างอนุกรมของตัวเอง ความต่างของผลอาจมาจาก
โค้ดที่ต่างกัน ไม่ใช่จากสิ่งที่ตั้งใจเปลี่ยน ⇒ **แต่ละแบบเปลี่ยนได้แค่ทีละหนึ่งอย่าง** (ดู Variant)

เทสต์บังคับว่า build_series(BASELINE) ต้องได้เลขเดียวกับ series.npz ทุกหลัก (tests/test_series.py)
"""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
import numpy as np

from .loaders import read_noaa_index, read_psmsl, read_uhslc_grid, read_wnpmi
from .preprocess import MAX_INTERP_MONTHS, align, common_window, detrend_deseason, fill_gaps
from .qc import apply_exclusions

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"

STATIONS = {"ko_lak": "KO LAK (อ่าวไทย)",
            "ko_taphao_noi": "KO TAPHAO NOI (อันดามัน)",
            "fort_phrachula_chomklao": "FORT PHRACHULA (อ่าวไทยตอนบน)"}
# 8 ตัวของ PLAN.md §1.3 — 6 ตัวของเปเปอร์ต้นทาง + DMI + WNPMI · WHWP ไม่อยู่ในนี้
INDEX_FILES = ["nino34", "soi", "pdo", "amo", "nao", "tpi", "dmi"]
INDEX_NAMES = INDEX_FILES + ["wnpmi"]
UHSLC_STATIONS = ("ko_taphao_noi", "ko_lak")      # สถานีที่มี UHSLC รายชั่วโมง (ใช้ในแบบ y_q7)


@dataclass(frozen=True)
class Variant:
    """หนึ่งแบบของการเตรียมข้อมูล — ทุกช่องมีค่าปริยายเท่ากับแบบมาตรฐาน"""
    name: str
    label: str
    max_interp: int = MAX_INTERP_MONTHS          # ช่องว่างยาวกว่านี้เติม 0 แทน interp
    max_filled: float = 0.5                      # เกณฑ์ของเติมในหน้าต่าง smoothing (ใช้ตอนนับ PASC)
    exclude: tuple[float, float] | None = None   # ช่วงปีของ Y ที่ทำให้เป็นช่องว่างก่อนเตรียม
    indices: tuple[str, ...] = tuple(INDEX_NAMES)
    y_source: str = "psmsl"                      # "psmsl" หรือ "q7" (UHSLC รายชั่วโมงผ่านโซ่ Q7)
    stations: tuple[str, ...] = tuple(STATIONS)
    window: tuple[float, float] | None = None    # บังคับหน้าต่างเวลา (ตัดให้แคบลงจากหน้าต่างร่วม)
    why: str = ""


BASELINE = Variant("baseline", "แบบมาตรฐาน")

VARIANTS: dict[str, Variant] = {v.name: v for v in (
    BASELINE,
    Variant("interp_all", "interp ทุกช่องว่าง", max_interp=10 ** 6,
            why="แบบมาตรฐานเติม 0 ในช่องว่างยาว — ถ้า interp แทน ข้อสรุปเปลี่ยนไหม"),
    Variant("fill25", "เกณฑ์ของเติม 25%", max_filled=0.25,
            why="นับเฉพาะจุดที่ของเติมในหน้าต่างไม่เกิน 25% (แบบมาตรฐาน 50%)"),
    Variant("cut_2004", "ตัดปี 2004–2005", exclude=(2004.0, 2006.0),
            why="ปีสึนามิ มาตรวัดเสียหาย — ทำให้เป็นช่องว่างทั้งสองปีแล้วไม่นับ"),
    Variant("no_amo", "ตัด AMO (ยาวถึง 2025)",
            indices=tuple(k for k in INDEX_NAMES if k != "amo"),
            why="AMO จบปี 2023 เป็นตัวจำกัดท้ายหน้าต่าง — ตัดออกแล้วข้อมูลยาวขึ้น"),
    Variant("short_1985", "PSMSL ช่วง 1985–2019", stations=UHSLC_STATIONS, window=(1985.0, 2020.0),
            why="คู่เทียบของ y_q7: ความยาวเท่ากันแต่ยังใช้ PSMSL ⇒ แยกผลของ 'ข้อมูลสั้นลง' "
                "ออกจากผลของ 'เปลี่ยนแหล่งข้อมูล'"),
    Variant("pre_2006", "PSMSL ก่อน 2006 (1951–2005)", window=(1951.0, 2006.0),
            why="เพิ่ม 2026-10-07 หลังเห็นผลของ y_q7: PSMSL กับ UHSLC ของ KO TAPHAO NOI ตรงกันระดับ mm "
                "ถึงปี 2005 แล้วแยกทางกัน ⇒ ตัดช่วงที่น่าสงสัยทิ้งทั้งหมด ดูว่าข้อสรุปยังอยู่ไหม"),
    Variant("y_q7", "Y จากโซ่ Q7 (UHSLC 1985–2019)", y_source="q7", stations=UHSLC_STATIONS,
            why="PSMSL ของ KO TAPHAO NOI มีขั้นบันได datum −100.7 mm ที่ไม่มีเอกสาร — "
                "ใช้ UHSLC ผ่านตัวกรองที่เราออกแบบเองแทน (เทียบกับ short_1985)"),
)}


def q7_monthly(station: str) -> tuple[np.ndarray, np.ndarray]:
    """ระดับน้ำรายเดือนจาก UHSLC รายชั่วโมง ผ่านโซ่ anti-alias + decimation ของ Q7

    ใช้ตัวกรองและสเปกเดียวกับ scripts/verify_decimation.py ทุกประการ
    (เดือนที่มีวันใช้ได้ < 15 วัน ⇒ NaN ตามกฎของ daily_to_monthly)
    -> (ปีทศนิยมกลางเดือน, mm)
    """
    from .multirate import daily_to_monthly, design_lowpass, hourly_to_daily
    spec = dict(f_pass=0.1, f_stop=0.5, atten_db=70.0, fs=24.0)    # = verify_decimation.SPEC
    t, v = read_uhslc_grid(RAW / "uhslc" / f"{station}_hourly.csv")
    days, daily = hourly_to_daily(t, v, design_lowpass(**spec))
    months, monthly, _ = daily_to_monthly(days, daily)
    m = months.astype("datetime64[M]").astype(int)                # เดือนนับจาก 1970-01
    return 1970 + m / 12 + 1 / 24, monthly


def load_raw(variant: Variant = BASELINE, verbose: bool = False
             ) -> dict[str, tuple[np.ndarray, np.ndarray]]:
    series = {}
    for k in variant.stations:
        if variant.y_source == "q7":
            series[k] = q7_monthly(k)
            continue
        t, v = read_psmsl(RAW / "psmsl" / f"{k}_monthly.rlrdata")
        v, cut = apply_exclusions(k, t, v)          # ค่าที่พิสูจน์แล้วว่าผิด (wtc/qc.py)
        if cut and verbose:
            print(f"  ตัดค่าที่พิสูจน์แล้วว่าผิดของ {k}: {', '.join(cut)} (หลักฐานใน wtc/qc.py)")
        series[k] = (t, v)
    series |= {n: read_noaa_index(RAW / "indices" / f"{n}.data")
               for n in INDEX_FILES if n in variant.indices}
    if "wnpmi" in variant.indices:
        series["wnpmi"] = read_wnpmi(RAW / "indices")
    return series


def build_series(variant: Variant = BASELINE, verbose: bool = False) -> dict:
    """-> dict(t, Y, Y_fill, X, X_fill, y_names, x_names, meta, stats, variant)

    หน้าต่างเวลา
      psmsl  กำหนดโดย **ดัชนี** (SOI เริ่มช้าสุด · AMO จบก่อนเพื่อน) — PSMSL ครอบคลุม 1940–2024 อยู่แล้ว
             จึงไม่เอามาคิด เพื่อไม่ให้ช่องว่างของสถานีใดสถานีหนึ่งไปตัดหน้าต่างของทั้งงาน
      q7     ต้องตัดด้วยช่วงของ Y ด้วย เพราะ UHSLC มีแค่ 1985–2019
    """
    raw = load_raw(variant, verbose)
    window_series = {n: raw[n] for n in variant.indices}
    if variant.y_source == "q7":
        window_series |= {k: raw[k] for k in variant.stations}
    start, stop = common_window(window_series)
    if variant.window is not None:                   # แคบลงได้อย่างเดียว ไม่ยืดเกินที่ข้อมูลมี
        start, stop = max(start, variant.window[0]), min(stop, variant.window[1] - 1e-6)
    grid, aligned = align(raw, start, stop)

    if variant.exclude is not None:
        a, b = variant.exclude
        cut = (grid >= a) & (grid < b)
        for k in variant.stations:
            aligned[k] = np.where(cut, np.nan, aligned[k])

    rows, stats = {}, {}
    for name in list(variant.stations) + list(variant.indices):
        z, info = detrend_deseason(grid, aligned[name])
        filled_series, mask = fill_gaps(z, variant.max_interp)
        rows[name] = (filled_series, mask)
        stats[name] = info.__dict__ | {"n_filled": int(mask.sum())}

    y_names, x_names = list(variant.stations), list(variant.indices)
    out = dict(t=grid,
               Y=np.array([rows[k][0] for k in y_names]),
               Y_fill=np.array([rows[k][1] for k in y_names]),
               X=np.array([rows[k][0] for k in x_names]),
               X_fill=np.array([rows[k][1] for k in x_names]),
               y_names=np.array(y_names), x_names=np.array(x_names),
               stats=stats, variant=variant,
               meta={"window": [start, stop], "n": len(grid), "dt": 1 / 12,
                     "max_interp_months": variant.max_interp,
                     "detrend": "linear trend + harmonics 1yr & 0.5yr, fitted on observed points only",
                     "normalized": "unit variance of residual before gap filling",
                     "variant": variant.name, "stats": stats})
    assert np.isfinite(out["Y"]).all() and np.isfinite(out["X"]).all(), "ยังมี NaN หลงเหลือ"
    return out
