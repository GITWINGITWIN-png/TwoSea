#!/usr/bin/env python3
"""Q7 — โซ่ anti-alias + decimation ที่เขียนเอง ให้ค่าตรงกับ PSMSL ทางการไหม

    uv run python scripts/verify_decimation.py

    UHSLC รายชั่วโมง (KO TAPHAO NOI 1985–2019)
      ──[ FIR Kaiser 70 dB ]──> รายวัน   เทียบ UHSLC daily (ตัวกรองทางการของ UHSLC)
      ──[ เฉลี่ยเดือนปฏิทิน ]──> รายเดือน เทียบ PSMSL รายเดือน
      ──[ เฉลี่ย 12 เดือน ]───> รายปี    เทียบ PSMSL รายปี

เกณฑ์ (proposal §4 · PLAN.md §6): **รายงาน RMS จริง พร้อมอธิบายที่มาของผลต่างที่เหลือ**
ไม่ตั้งเกณฑ์ลอย ๆ ไว้ล่วงหน้า ⇒ สคริปต์นี้แยกการเทียบตามช่วงเวลาที่ datum ของสองแหล่ง
ต่างกันอย่างมีเอกสารรองรับ (ดู docstring ของ PERIODS) เพื่อให้ตัวเลขแต่ละตัวตอบคำถามเดียว

ผลเมื่อ 2026-09-30 (ใช้เป็นเลขอ้างอิงถ้ารันใหม่แล้วต่าง)
    ตัวกรอง       261 taps · beta 6.7553 · stopband วัดได้ 70.07 dB
    รายวัน         vs UHSLC daily   RMS  3.0 mm
    รายเดือน 1988–2005 (datum นิ่ง)  median|d| 1.2 mm · 90% ภายใน ±5 mm
    รายเดือน 2015–2019 (นิ่งอีกครั้ง) median|d| 1.1 mm · 85% ภายใน ±5 mm แต่ offset ขยับไป −100.7 mm
    รายเดือน 2006–2012               ส่วนต่างไม่นิ่ง ← สองแหล่งไม่ตรงกันเอง ไม่ใช่ตัวกรอง
    ไม่กรองเลย                       RMS 152 mm · offset ขยับ 290 mm (= S2 พับลง DC)
"""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from wtc.loaders import read_psmsl, read_uhslc_daily, read_uhslc_grid  # noqa: E402
from wtc.multirate import (TIDES_CPD, compare, daily_to_monthly,        # noqa: E402
                           decimal_year_to_month, design_lowpass, hourly_to_daily,
                           monthly_mean_direct, monthly_to_annual, naive_daily)

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "processed" / "decimation.npz"

# สเปกตัวกรอง — ที่มาของแต่ละตัวเลขอยู่ใน wtc/multirate.py หัวไฟล์
SPEC = dict(f_pass=0.1, f_stop=0.5, atten_db=70.0, fs=24.0)

# ช่วงเวลาที่ใช้แยกการเทียบ — แต่ละรอยต่อมีเอกสารของ PSMSL สถานี 446 รองรับ
# (psmsl.org/data/obtaining/stations/446.php · Documentation added 2011-07-12)
#   "From 1987 onwards the benchmark was BM 105 ..."
#   "In 1988 the datum was raised 14mm."
#   "In 1998 the primary benchmark became AS-1/2531 ..."
# และปี 2004 คือปีสึนามิที่มาตรวัดเสียหาย (หายทั้งปีในทุกแหล่ง)
#
# ช่วงหลังปี 2004 แบ่งตามที่ข้อมูลแสดงเอง (ไม่มีเอกสารของ PSMSL รองรับ):
#   2005        ยังต่างคงที่เท่ายุคก่อน (มาตรวัดที่ติดตั้งใหม่ยังตรงกันทั้งสองแหล่ง)
#   2006–2012   ส่วนต่างไม่นิ่ง แกว่งเป็นหลักสิบถึงร้อย mm
#   2015–2019   กลับมานิ่งอีกครั้ง แต่ที่ระดับต่างจากยุคแรก ~101 mm = ขั้นบันไดของ datum
PERIODS = {
    "1985–1987 (ก่อนยก datum 14 mm)": ("1985-01", "1988-01"),
    "1988–2005 (datum นิ่ง ยุคแรก)":   ("1988-01", "2006-01"),
    "2006–2012 (ส่วนต่างไม่นิ่ง)":     ("2006-01", "2013-01"),
    "2015–2019 (นิ่งอีกครั้ง)":        ("2015-01", "2020-01"),
}
STABLE_A, STABLE_B = "1988–2005 (datum นิ่ง ยุคแรก)", "2015–2019 (นิ่งอีกครั้ง)"


def run() -> dict:
    t, v = read_uhslc_grid(RAW / "uhslc" / "ko_taphao_noi_hourly.csv")
    design = design_lowpass(**SPEC)
    days, daily = hourly_to_daily(t, v, design)
    months, monthly, n_days = daily_to_monthly(days, daily)
    years, annual, n_months = monthly_to_annual(months, monthly)

    ud, uval = read_uhslc_daily(RAW / "uhslc" / "ko_taphao_noi_daily.csv")
    tp, vp = read_psmsl(RAW / "psmsl" / "ko_taphao_noi_monthly.rlrdata")
    ta, va = read_psmsl(RAW / "psmsl" / "ko_taphao_noi_annual.rlrdata")
    pm, py = decimal_year_to_month(tp), np.floor(ta).astype(int)

    # ตัวเปรียบเทียบ: ไม่ผ่าน FIR เลย / ไม่กรองแล้วสุ่มวันละครั้ง / ใช้ daily ของ UHSLC แทนของเรา
    dm, dmv, _ = monthly_mean_direct(t, v)
    nd, ndv = naive_daily(t, v, hour=0)
    nm, nmv, _ = daily_to_monthly(nd, ndv)
    um, umv, _ = daily_to_monthly(ud, uval)

    return dict(t=t, v=v, design=design, days=days, daily=daily, months=months,
                monthly=monthly, n_days=n_days, years=years, annual=annual,
                n_months=n_months, ud=ud, uval=uval, pm=pm, vp=vp, py=py, va=va,
                direct=(dm, dmv), naive=(nm, nmv), uhslc_monthly=(um, umv))


def main() -> int:
    r = run()
    d = r["design"]
    print("ตัวกรอง anti-alias (รายชั่วโมง -> รายวัน)")
    print(f"  สเปก   passband <= {d.f_pass} cpd · stopband >= {d.f_stop} cpd · {d.atten_db:.0f} dB")
    print(f"  ได้     {d.numtaps} taps ({d.numtaps / 24:.1f} วัน) · beta {d.beta:.4f} · "
          f"สูตร Kaiser ทำนาย {d.formula_numtaps}")
    print(f"  วัดจริง stopband {d.measured_stopband_db():.2f} dB · "
          f"passband ripple {d.measured_passband_ripple():.1e}")
    for note in d.notes:
        print(f"  ⚠️ {note}")
    g = d.gain_at(list(TIDES_CPD.values()))
    print("  gain ที่น้ำขึ้นน้ำลงหลัก: " +
          " · ".join(f"{k} {20 * np.log10(x):.0f} dB" for k, x in zip(TIDES_CPD, g)))
    assert d.measured_stopband_db() >= d.atten_db, "ตัวกรองไม่ผ่านสเปกของตัวเอง"

    ok = np.isfinite(r["daily"])
    print(f"\nรายวัน {len(r['days'])} วัน ใช้ได้ {ok.mean():.1%} · "
          f"รายเดือน {np.isfinite(r['monthly']).sum()}/{len(r['months'])} · "
          f"รายปี {np.isfinite(r['annual']).sum()}/{len(r['years'])}")

    def row(label, c):
        # median|d| และ "ภายใน ±5 mm" วัดรอบ **ค่ากลาง** ของส่วนต่าง ไม่ใช่รอบค่าเฉลี่ย
        # เพราะค่าโดดไม่กี่เดือน (±250 mm) ดึงค่าเฉลี่ยจนเดือนปกติทั้งหมดดูเหมือนต่างกันหลายมิลลิเมตร
        # ส่วน RMS ยังคิดรอบค่าเฉลี่ยตามนิยาม — สองตัวนี้ตอบคนละคำถามจึงรายงานทั้งคู่
        rob = c.diff + c.offset - c.median_offset
        print(f"  {label:40s} n={c.n:5d} offset={c.offset:+8.1f} (ค่ากลาง {c.median_offset:+8.1f}) "
              f"RMS={c.rms:6.2f} median|d|={np.median(np.abs(rob)):6.2f} "
              f"±5mm={np.mean(np.abs(rob) <= 5):4.0%}")
        return dict(n=c.n, offset=c.offset, median_offset=c.median_offset,
                    rms=c.rms, corr=c.corr, max_abs=c.max_abs,
                    median_abs=float(np.median(np.abs(rob))),
                    within_5mm=float(np.mean(np.abs(rob) <= 5)))

    results = {}
    print("\nเทียบกับค่าอ้างอิง (หลังลบ offset คงที่ของ datum)")
    results["daily_vs_uhslc"] = row("รายวัน: เรา vs UHSLC daily",
                                    compare(r["days"], r["daily"], r["ud"], r["uval"]))
    results["monthly_all"] = row("รายเดือน: เรา vs PSMSL ทั้งช่วง",
                                 compare(r["months"], r["monthly"], r["pm"], r["vp"]))
    for label, (lo, hi) in PERIODS.items():
        sel = (r["months"] >= np.datetime64(lo)) & (r["months"] < np.datetime64(hi))
        results[f"monthly {label}"] = row(f"  {label}",
                                          compare(r["months"][sel], r["monthly"][sel],
                                                  r["pm"], r["vp"]))
    step = (results[f"monthly {STABLE_B}"]["median_offset"]
            - results[f"monthly {STABLE_A}"]["median_offset"])
    results["datum_step_mm"] = step
    print(f"  ⚠️ ขั้นบันไดของ datum ระหว่างสองยุคที่นิ่ง = {step:+.1f} mm "
          f"(ไม่มีเอกสารของ PSMSL อธิบาย — ยังบอกไม่ได้ว่าอยู่ในแหล่งไหน)")
    results["annual"] = row("รายปี: เรา vs PSMSL",
                            compare(r["years"], r["annual"], r["py"], r["va"]))

    print("\nตัวเปรียบเทียบ — แยกว่าความต่างมาจากขั้นไหน")
    results["direct"] = row("เฉลี่ยตรงจากรายชั่วโมง (ไม่ผ่าน FIR)",
                            compare(*r["direct"], r["pm"], r["vp"]))
    results["uhslc_daily_monthly"] = row("UHSLC daily -> เฉลี่ยรายเดือน",
                                         compare(*r["uhslc_monthly"], r["pm"], r["vp"]))
    results["naive"] = row("ไม่กรองเลย (สุ่ม 00:00 วันละครั้ง)",
                           compare(*r["naive"], r["pm"], r["vp"]))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(OUT, taps=d.taps, days=r["days"].astype(str), daily=r["daily"],
                        months=r["months"].astype(str), monthly=r["monthly"],
                        n_days=r["n_days"], years=r["years"], annual=r["annual"],
                        results=json.dumps(results, ensure_ascii=False),
                        spec=json.dumps(SPEC))
    print(f"\n✅ เขียนแล้ว {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
