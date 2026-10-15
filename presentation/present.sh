#!/usr/bin/env bash
# นำเสนอ deck จากโน้ตบุ๊ก (หลัง uv run python tools/build_deck.py <v>)
#
#   ./present.sh            เต็มจอ บนจอที่ 1 (เมื่อต่อโปรเจกเตอร์: จอโน้ตผู้พูดขึ้นบนอีกจออัตโนมัติ)
#   ./present.sh -S 0       เลือกจอที่ใช้ฉาย (0 = จอโน้ตบุ๊ก)
#   ./present.sh --sa 7,0   เริ่มที่ตอนลำดับ 7 (นับจาก 0) หน้าแรก — ใช้กระโดดตอนถาม-ตอบ
#
# ปุ่ม: → / Space = ถัดไป · ← = ย้อน · Q = ออก
# QT_QPA_PLATFORM=xcb: ตัวเล่น Qt 6.12 พังบน GNOME Wayland (fit test 2026-10-10) จึงรันผ่าน XWayland
set -euo pipefail
cd "$(dirname "$0")"
SEQS=$(ls manim/sq[0-9][0-9]_*.py | sed -E 's#manim/(sq[0-9]+)_.*#\1#' | tr a-z A-Z | tr '\n' ' ')
QT_QPA_PLATFORM=xcb exec uv run manim-slides present -F "$@" $SEQS
