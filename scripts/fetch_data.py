#!/usr/bin/env python3
from __future__ import annotations
import argparse, datetime as dt, html, re, sys, time, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UA = {"User-Agent": "dsp-course-project/1.0 (student research)"}
THIS_YEAR = dt.date.today().year

PSMSL_STATIONS = {174: "ko_lak", 446: "ko_taphao_noi", 444: "fort_phrachula_chomklao"}
PSMSL = {
    f"psmsl/{name}_{kind}.rlrdata":
        f"https://psmsl.org/data/obtaining/rlr.{kind}.data/{sid}.rlrdata"
    for sid, name in PSMSL_STATIONS.items() for kind in ("monthly", "annual")
}

UHSLC = {
    "uhslc/ko_taphao_noi_hourly.csv":
        "https://uhslc.soest.hawaii.edu/data/csv/rqds/indian/hourly/h148a.csv",
    "uhslc/ko_lak_hourly.csv":
        "https://uhslc.soest.hawaii.edu/data/csv/rqds/pacific/hourly/h328a.csv",
    "uhslc/ko_taphao_noi_daily.csv":
        "https://uhslc.soest.hawaii.edu/data/csv/rqds/indian/daily/d148a.csv",
}

INDICES = {
    "indices/nino34.data": "https://psl.noaa.gov/data/correlation/nina34.anom.data",
    "indices/soi.data":    "https://psl.noaa.gov/data/correlation/soi.data",
    "indices/pdo.data":    "https://psl.noaa.gov/data/correlation/pdo.data",
    "indices/amo.data":    "https://psl.noaa.gov/data/correlation/amon.us.data",
    "indices/nao.data":    "https://psl.noaa.gov/data/correlation/nao.data",
    "indices/whwp.data":   "https://psl.noaa.gov/data/correlation/whwp.data",
    "indices/dmi.data":
        "https://psl.noaa.gov/gcos_wgsp/Timeseries/Data/dmi.had.long.data",
    "indices/tpi.data":
        "https://psl.noaa.gov/data/timeseries/IPOTPI/tpi.timeseries.ersstv5.data",
}

PSL_TIMESERIES = "https://psl.noaa.gov/cgi-bin/data/timeseries/timeseries.pl"
U850_BOXES = {
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
    if body[:20].lstrip().lower().startswith(b"<!doctype") or b"<html" in body[:200].lower():
        return f"❌ ได้ HTML ไม่ใช่ข้อมูล  {rel}  <- {url}"
    dest.write_bytes(body)
    return f"✅ โหลดแล้ว    {rel}  {len(body):,} B"


def fetch_psl_timeseries(rel: str, url: str, force: bool) -> str:
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
