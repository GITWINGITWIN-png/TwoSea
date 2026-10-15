#!/usr/bin/env python3
"""ตรวจความพร้อมของข้อมูลดิบ — รันทุกครั้งหลัง fetch_data.py

    uv run python scripts/check_data.py

พิมพ์: จำนวนจุด · ค่าหาย · หน้าต่างที่ทับกัน · แนวโน้ม · สัดส่วนวงรอบตามฤดู
สิ่งเหล่านี้ไม่ใช่ผลการวิจัย มันคือ **ด่านตรวจว่าข้อมูลยังเป็นอย่างที่คิด**
ถ้าตัวเลขเปลี่ยนไปจาก data/MANIFEST.md แปลว่าแหล่งข้อมูลอัปเดต ต้องอ่านก่อนเดินต่อ
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from wtc.loaders import (read_psmsl, read_noaa_index, read_uhslc,   # noqa: E402
                         read_wnpmi)

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
STATIONS = {"ko_lak": "KO LAK (อ่าวไทย)",
            "ko_taphao_noi": "KO TAPHAO NOI (อันดามัน)",
            "fort_phrachula_chomklao": "FORT PHRACHULA (อ่าวไทยตอนบน)"}
# ชุดที่ใช้ค้นหาจริง 8 ตัว (PLAN.md §1.3) = 6 ตัวของเปเปอร์ต้นทาง + DMI + WNPMI
# WHWP โหลดไว้แต่ไม่ได้ใช้ (โหมดแอตแลนติก) — ตรวจไว้เฉย ๆ ไม่เอาไปคิดหน้าต่างที่ทับกัน
INDICES_USED = ["nino34", "soi", "pdo", "amo", "nao", "tpi", "dmi"]   # + wnpmi ที่ประกอบเอง
INDICES_SPARE = ["whwp"]


def seasonal_split(t, y):
    """แยก y ออกเป็น (แนวโน้ม, วงรอบปี+ครึ่งปี, ส่วนที่เหลือ) ด้วย least squares

    ใช้ harmonic regression ไม่ใช่ตัวกรอง เพราะข้อมูลมีช่องว่าง — ตัวกรองต้องการ
    กริดที่ครบ ส่วนการ fit ไม่ต้อง (นี่คือประเด็นของบทที่ 1 เรื่องการสุ่มตัวอย่าง)
    """
    g = ~np.isnan(y)
    t, y = t[g], y[g]
    A = np.column_stack([t - t.mean(), np.ones_like(t)])
    trend = A @ np.linalg.lstsq(A, y, rcond=None)[0]
    r = y - trend
    H = np.column_stack([np.ones_like(t)] +
                        [f(2 * np.pi * k * t) for k in (1, 2) for f in (np.sin, np.cos)])
    c = np.linalg.lstsq(H, r, rcond=None)[0]
    seas = H @ c
    slope = np.polyfit(t, y, 1)[0]
    amp = float(np.hypot(c[1], c[2]))
    return slope, amp, 1 - np.var(r - seas) / np.var(r), 1 - np.var(y - trend) / np.var(y), r - seas


def main() -> int:
    print("=" * 78)
    print("PSMSL — ระดับน้ำทะเล (ตัวแปรตาม)")
    print("=" * 78)
    spans = []
    for key, label in STATIONS.items():
        for kind in ("annual", "monthly"):
            t, v = read_psmsl(RAW / "psmsl" / f"{key}_{kind}.rlrdata")
            n_ok = int((~np.isnan(v)).sum())
            miss = int(np.isnan(v).sum())
            print(f"  {label:28s} {kind:7s} n={len(v):5d} ใช้ได้={n_ok:5d} "
                  f"หาย={miss:3d} ({miss/len(v):5.1%}) ช่วง {t[0]:.2f}–{t[-1]:.2f}")
            if kind == "monthly":
                spans.append((t[~np.isnan(v)][0], t[~np.isnan(v)][-1]))
                sl, amp, sfrac, tfrac, _ = seasonal_split(t, v)
                print(f"  {'':28s}         แนวโน้ม {sl:+.2f} mm/ปี (อธิบาย {tfrac:.1%}) · "
                      f"วงรอบปี+ครึ่งปี {amp:.0f} mm (อธิบาย {sfrac:.1%} ของที่เหลือ)")
    print()
    print("=" * 78)
    print("NOAA PSL — ดัชนีภูมิอากาศ (ตัวแปรอิสระ)")
    print("=" * 78)
    for name in INDICES_USED + INDICES_SPARE:
        t, v = read_noaa_index(RAW / "indices" / f"{name}.data")
        g = ~np.isnan(v)
        used = "ใช้" if name in INDICES_USED else "สำรอง"
        print(f"  {name:8s} [{used:6s}] n={len(v):5d} ใช้ได้={int(g.sum()):5d} "
              f"ช่วง {t[g][0]:.2f}–{t[g][-1]:.2f}")
        if name in INDICES_USED:
            spans.append((t[g][0], t[g][-1]))
    # WNPMI ไม่ใช่ไฟล์เดียว — ประกอบจาก U850 สองกล่องแล้วลบกัน (loaders.read_wnpmi)
    t, v = read_wnpmi(RAW / "indices")
    g = ~np.isnan(v)
    print(f"  {'wnpmi':8s} [{'ใช้':6s}] n={len(v):5d} ใช้ได้={int(g.sum()):5d} "
          f"ช่วง {t[g][0]:.2f}–{t[g][-1]:.2f}  (= U850 ใต้ − เหนือ)")
    mo = np.round((t % 1) * 12 - 0.5).astype(int)
    clim = [np.nanmean(v[mo == m]) for m in range(12)]
    print(f"  {'':8s}          วงรอบรายเดือน (ม.ค.→ธ.ค.): "
          + " ".join(f"{c:+.1f}" for c in clim))
    print(f"  {'':8s}          ต้องบวกสุดช่วง ก.ค.–ก.ย. (มรสุมตะวันตกเฉียงใต้) "
          f"— ถ้าไม่ใช่แปลว่าสลับกล่องกัน")
    spans.append((t[g][0], t[g][-1]))
    lo = max(s[0] for s in spans); hi = min(s[1] for s in spans)
    print(f"\n  🔴 หน้าต่างที่ดัชนี 8 ตัวที่ใช้จริงทับกัน: {lo:.2f}–{hi:.2f} = {hi-lo:.0f} ปี")
    print("     (ตัวจำกัดคือ SOI ที่เริ่มช้าสุด และ AMO ที่จบก่อนเพื่อน"
          " — ตัด AMO ออกจะได้ยาวขึ้นอีกปีกว่า)")
    print()
    print("=" * 78)
    print("UHSLC — รายชั่วโมง (ใช้ตรวจโซ่กรอง/ดีซิเมท ไม่ใช่ตัวแปรหลัก)")
    print("=" * 78)
    for key in ("ko_taphao_noi", "ko_lak"):
        t, v = read_uhslc(RAW / "uhslc" / f"{key}_hourly.csv")
        miss = int(np.isnan(v).sum())
        print(f"  {STATIONS[key]:28s} n={len(v):7d} หาย={miss:6d} ({miss/len(v):5.2%}) "
              f"ช่วง {t[0]:.2f}–{t[-1]:.2f}")
    print("\n✅ ตรวจครบ — เทียบตัวเลขกับ data/MANIFEST.md ถ้าต่างแปลว่าแหล่งข้อมูลอัปเดต")
    return 0


if __name__ == "__main__":
    sys.exit(main())
