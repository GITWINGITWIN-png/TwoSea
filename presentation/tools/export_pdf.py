"""export deck (Slidev) เป็น PDF ส่งอาจารย์ — หน้าละสไลด์ ในสภาพคลิกสุดท้าย ขนาดเต็ม 1920×1080

    uv run python tools/export_pdf.py s009                  # -> export/two-seas_s009.pdf (ทุกหน้า รวมภาคผนวก)
    uv run python tools/export_pdf.py s009 --range 1-27     # เฉพาะหน้าหลัก

ใช้แทน `npx slidev export` (ขอบดำ / ข้อมูลที่โผล่ด้วยคลิกหาย — ดูเหตุผลใน tools/export_pdf.cjs)
สร้าง deck ใหม่จากบท → เปิด slidev dev server ของตัวเอง → พิมพ์ทีละหน้า → ปิด server
"""

from __future__ import annotations

import argparse
import os
import signal
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DECK = ROOT / "deck"


def wait_for(url: str, timeout: float = 60) -> None:
    """รอจน dev server ตอบ (Vite ใช้เวลาเริ่มหลายวินาที)"""
    end = time.time() + timeout
    while time.time() < end:
        try:
            urllib.request.urlopen(url, timeout=2)
            return
        except OSError:
            time.sleep(0.5)
    raise SystemExit(f"slidev dev server ไม่ตอบที่ {url}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("version", help="รุ่นผลลัพธ์ เช่น s009")
    ap.add_argument("--range", help="ช่วงหน้า เช่น 1-27 (ค่าเริ่มต้น = ทุกหน้า)")
    ap.add_argument("--port", type=int, default=8781)
    args = ap.parse_args()

    subprocess.run([sys.executable, str(ROOT / "tools" / "gen_deck.py")], check=True)
    output = ROOT / "export" / f"two-seas_{args.version}.pdf"
    # dev server (ไม่ใช่ build) เพราะตัว export อ่านจำนวนคลิกจาก window.__slidev__ ที่มีเฉพาะโหมด dev
    server = subprocess.Popen(["npx", "slidev", "--port", str(args.port)], cwd=DECK,
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    try:
        wait_for(f"http://localhost:{args.port}/")
        cmd = ["node", str(ROOT / "tools" / "export_pdf.cjs"), str(DECK / "node_modules"),
               str(args.port), str(output)]
        if args.range:
            cmd.append(args.range)
        subprocess.run(cmd, check=True)
    finally:
        # npx เปิด node (vite) เป็นลูกอีกชั้น — ปิดทั้งกลุ่ม ไม่งั้น server ค้าง
        os.killpg(server.pid, signal.SIGTERM)
    print(f"PDF อยู่ที่ {output.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
