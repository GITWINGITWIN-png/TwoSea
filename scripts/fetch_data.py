#!/usr/bin/env python3
"""ดาวน์โหลดข้อมูลดิบทั้งหมดของโปรเจกต์ — รันซ้ำได้ ไม่โหลดทับของที่มีแล้ว

    uv run python scripts/fetch_data.py            # โหลดที่ยังไม่มี
    uv run python scripts/fetch_data.py --force    # โหลดใหม่ทั้งหมด

ทุก URL ในไฟล์นี้ **ยิงจริงและยืนยันแล้วเมื่อ 2026-09-09** (ดู data/MANIFEST.md)
ถ้าตัวไหนพัง อย่าเดา endpoint ใหม่เอง — เปิดหน้าเว็บของแหล่งนั้นแล้วหาเส้นทางจริง
เพราะ endpoint ที่เดาผิดจะคืน 404 หรือ (แย่กว่า) คืนหน้า HTML ที่ parse แล้วได้ค่าเพี้ยน
"""
from __future__ import annotations
import argparse, datetime as dt, html, re, sys, time, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UA = {"User-Agent": "dsp-course-project/1.0 (student research)"}
THIS_YEAR = dt.date.today().year      # ขอถึงปีปัจจุบัน เดือนที่ยังไม่มีข้อมูลจะคืนค่าหายมาเอง

# --- ตัวแปรตาม: ระดับน้ำทะเล ------------------------------------------------
# PSMSL RLR = Revised Local Reference, หน่วย mm, ค่าหาย -99999
PSMSL_STATIONS = {174: "ko_lak", 446: "ko_taphao_noi", 444: "fort_phrachula_chomklao"}
PSMSL = {
    f"psmsl/{name}_{kind}.rlrdata":
        f"https://psmsl.org/data/obtaining/rlr.{kind}.data/{sid}.rlrdata"
    for sid, name in PSMSL_STATIONS.items() for kind in ("monthly", "annual")
}

# UHSLC research-quality hourly — ใช้ตรวจสอบโซ่กรอง/ดีซิเมทเทียบกับค่าทางการของ PSMSL
UHSLC = {
    "uhslc/ko_taphao_noi_hourly.csv":
        "https://uhslc.soest.hawaii.edu/data/csv/rqds/indian/hourly/h148a.csv",
    "uhslc/ko_lak_hourly.csv":
        "https://uhslc.soest.hawaii.edu/data/csv/rqds/pacific/hourly/h328a.csv",
    # ค่ารายวันทางการของ UHSLC (ตัวกรองน้ำขึ้นน้ำลงของเขาเอง) — ตัวเทียบชั้นกลางของโซ่ decimate
    # ทำให้แยกได้ว่าความต่างกับ PSMSL มาจากขั้นรายวันหรือขั้นรายเดือน (เพิ่ม 2026-09-30)
    "uhslc/ko_taphao_noi_daily.csv":
        "https://uhslc.soest.hawaii.edu/data/csv/rqds/indian/daily/d148a.csv",
}

# --- ตัวแปรอิสระ: ดัชนีภูมิอากาศ (NOAA PSL, public domain) --------------------
INDICES = {
    "indices/nino34.data": "https://psl.noaa.gov/data/correlation/nina34.anom.data",
    "indices/soi.data":    "https://psl.noaa.gov/data/correlation/soi.data",
    "indices/pdo.data":    "https://psl.noaa.gov/data/correlation/pdo.data",
    "indices/amo.data":    "https://psl.noaa.gov/data/correlation/amon.us.data",
    "indices/nao.data":    "https://psl.noaa.gov/data/correlation/nao.data",
    "indices/whwp.data":   "https://psl.noaa.gov/data/correlation/whwp.data",
    # DMI (Indian Ocean Dipole) อยู่คนละ path กับตัวอื่น — เส้นทางนี้คือตัวที่ใช้ได้จริง
    "indices/dmi.data":
        "https://psl.noaa.gov/gcos_wgsp/Timeseries/Data/dmi.had.long.data",
    # TPI (Tripole Index ของ IPO, Henley et al. 2015) — 1 ใน 6 ดัชนีของเปเปอร์ต้นทาง
    # อยู่คนละที่กับ correlation/ และ **ค่าหายเป็น -99** ซึ่งยังต่ำกว่าเกณฑ์ -90 ของตัวอ่าน
    "indices/tpi.data":
        "https://psl.noaa.gov/data/timeseries/IPOTPI/tpi.timeseries.ersstv5.data",
}

# --- WNPMI: ดัชนีที่ต้องประกอบเอง ------------------------------------------
# Wang & Fan (1999): WNPMI = U850 เฉลี่ยพื้นที่กล่องใต้ − กล่องเหนือ
#     กล่องใต้  (5–15°N, 100–130°E)   กล่องเหนือ (20–30°N, 110–140°E)
# NOAA PSL ไม่มีไฟล์สำเร็จของดัชนีนี้ ต้องสั่งเครื่องมือ timeseries คำนวณค่าเฉลี่ยพื้นที่
# ให้ทีละกล่องแล้วเอามาลบกันเอง (การลบทำใน loaders.read_wnpmi ไม่ใช่ที่นี่ —
# ที่นี่เก็บเฉพาะ "ของดิบที่แหล่งให้มา" ส่วนของที่คำนวณเองถือเป็นผลลัพธ์ ไม่ใช่ข้อมูลดิบ)
#
# ⚠️ พารามิเตอร์ชุดนี้ยิงจริงแล้ว 2026-09-20 และมีสามจุดที่ผิดง่าย:
#   var=Zonal Wind  ไม่ใช่ "U-wind"  (ชื่อที่ฟอร์มใช้จริง — ใส่ผิดได้หน้า ERROR ที่ดูเหมือนสำเร็จ)
#   typeout=1       = raw data values (typeout=2 เป็นหน้ากราฟ ไม่ใช่ตัวเลข)
#   lat1 > lat2     ฟอร์มรับละติจูด **เหนือ → ใต้**
#   iarea=1         ถ่วงน้ำหนักพื้นที่ด้วย cos(lat) — ค่าเฉลี่ยพื้นที่ที่ถูกต้องกว่าแบบไม่ถ่วง
#                   (ต่างกัน <0.02 m/s แต่ประกาศไว้ให้ทำซ้ำได้)
PSL_TIMESERIES = "https://psl.noaa.gov/cgi-bin/data/timeseries/timeseries.pl"
U850_BOXES = {
    # ชื่อไฟล์ -> (lat เหนือ, lat ใต้, lon ตะวันตก, lon ตะวันออก)
    "indices/u850_box_south.data": (15, 5, 100, 130),
    "indices/u850_box_north.data": (30, 20, 110, 140),
}
U850 = {
    rel: (f"{PSL_TIMESERIES}?ntype=1&var=Zonal+Wind&level=850"
          f"&lat1={la1}&lat2={la2}&lon1={lo1}&lon2={lo2}"
          f"&iseas=0&mon1=0&mon2=11&iarea=1&typeout=1"
          f"&year1=1948&year2={THIS_YEAR}&Submit=Create+Timeseries")
    for rel, (la1, la2, lo1, lo2) in U850_BOXES.items()
}

ALL = {**PSMSL, **UHSLC, **INDICES}


def get(url: str, timeout: int, tries: int = 4) -> bytes:
    """ยิง GET พร้อมลองซ้ำ — เซิร์ฟเวอร์ของ NOAA PSL คืน 502 เป็นพัก ๆ จริง (เจอเมื่อ 2026-09-20)

    ความล้มเหลวชั่วคราวแบบนี้ไม่ควรทำให้ต้องมานั่งรันใหม่เองทั้งชุด แต่ก็ **ไม่ควรกลืนเงียบ**
    ⇒ ลองซ้ำแบบถอยเวลาเพิ่มขึ้น แล้วถ้ายังไม่ได้ให้โยน exception ตัวจริงออกไปให้เห็น
    """
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=timeout) as fh:
                return fh.read()
        except Exception:
            if attempt == tries - 1:
                raise
            time.sleep(5 * (attempt + 1))
    raise RuntimeError("ไม่ควรมาถึงบรรทัดนี้")


def fetch(rel: str, url: str, force: bool) -> str:
    dest = ROOT / "data" / "raw" / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and not force:
        return f"ข้าม (มีแล้ว)  {rel}  {dest.stat().st_size:,} B"
    try:
        body = get(url, timeout=120)
    except Exception as exc:
        return f"❌ ล้มเหลว     {rel}  <- {exc}"
    # กันกรณีเซิร์ฟเวอร์คืนหน้า error เป็น HTML แทนข้อมูล
    if body[:20].lstrip().lower().startswith(b"<!doctype") or b"<html" in body[:200].lower():
        return f"❌ ได้ HTML ไม่ใช่ข้อมูล  {rel}  <- {url}"
    dest.write_bytes(body)
    return f"✅ โหลดแล้ว    {rel}  {len(body):,} B"


def fetch_psl_timeseries(rel: str, url: str, force: bool) -> str:
    """เครื่องมือ timeseries ของ NOAA PSL คืนตัวเลขมา **ห่ออยู่ในหน้า HTML**

    ตัวดัก HTML ใน fetch() จึงใช้กับมันไม่ได้ ต้องแกะบล็อก <pre> ออกมาเอง
    แล้วเขียนลงไฟล์เป็น ASCII ล้วนให้เหมือนไฟล์ดัชนีตัวอื่น (read_noaa_index อ่านได้ทันที)

    ที่ต้องระวัง: หน้า **ERROR** ของเขาก็คืน HTTP 200 เหมือนกัน แต่ไม่มี <pre>
    ⇒ เช็คว่ามี <pre> และมีบรรทัดขึ้นต้นด้วยปี 4 หลักจริง ก่อนจะยอมเขียนไฟล์
    """
    dest = ROOT / "data" / "raw" / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and not force:
        return f"ข้าม (มีแล้ว)  {rel}  {dest.stat().st_size:,} B"
    try:
        page = get(url, timeout=180).decode("utf-8", "replace")
    except Exception as exc:
        return f"❌ ล้มเหลว     {rel}  <- {exc}"
    m = re.search(r"<pre>(.*?)</pre>", page, re.S | re.I)
    if not m:
        err = re.search(r"ERROR:.*?<p>(.*?)<p>", page, re.S)
        why = re.sub(r"<[^>]+>", "", err.group(1)).strip()[:120] if err else "ไม่พบบล็อก <pre>"
        return f"❌ PSL ไม่คืนข้อมูล  {rel}  <- {why}"
    body = html.unescape(m.group(1)).strip("\n") + "\n"
    if not re.search(r"^\s*\d{4}\s+-?\d", body, re.M):
        return f"❌ <pre> ไม่มีแถวข้อมูล  {rel}"
    dest.write_text(body)
    return f"✅ โหลดแล้ว    {rel}  {len(body):,} B  (แกะจาก <pre>)"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true", help="โหลดใหม่ทับของเดิม")
    args = ap.parse_args()
    bad = 0
    for rel, url in ALL.items():
        line = fetch(rel, url, args.force)
        print("  " + line)
        bad += line.startswith("❌")
    for rel, url in U850.items():
        line = fetch_psl_timeseries(rel, url, args.force)
        print("  " + line)
        bad += line.startswith("❌")
    print(f"\nรวม {len(ALL) + len(U850)} ไฟล์ · ล้มเหลว {bad}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
