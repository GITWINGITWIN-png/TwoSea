"""ตัวเลขและข้อมูลทุกอย่างที่ฉากใช้ — ฉากห้ามพิมพ์ตัวเลขเอง ให้ดึงจากที่นี่

    F("pasc.andaman.plane.soi")      -> 14.26…        ค่าดิบจาก data/facts.json
    num("pasc.andaman.plane.soi", 1) -> "14.3"         ข้อความพร้อมขึ้นจอ
    derived()["andaman_mm_12m"]                        อาร์เรย์ที่ export_facts คำนวณไว้
    processed("wtc_q1.npz")                            ไฟล์ผลของโครงงาน DSP (อ่านอย่างเดียว)

ทุกค่ามาจาก tools/export_facts.py ซึ่งรันโค้ดของโครงงาน DSP เอง — ตัวเลขบนจอจึงเป็นเลขเดียวกับในรายงาน
"""

from __future__ import annotations

import json
import tomllib
from functools import cache
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
_FACTS = json.loads((ROOT / "data" / "facts.json").read_text())
DSP = (ROOT / Path(tomllib.loads((ROOT / "studio.toml").read_text())["sources"]["dsp_project"]).expanduser()).resolve()
PROC = DSP / "data" / "processed"


def F(key):
    """ค่าของ fact (ตัวเลข ลิสต์ หรือ dict) — KeyError ถ้าไม่มี เพื่อให้พังทันทีแทนการเดา"""
    return _FACTS[key]["value"]


def unit(key):
    return _FACTS[key]["unit"]


def num(key, digits=0, *, index=None, absval=False, round_to=None, sign=False):
    """ตัวเลขเป็นข้อความสำหรับขึ้นจอ

    digits   ทศนิยมกี่ตำแหน่ง · index ตำแหน่งในลิสต์ · absval ค่าสัมบูรณ์
    round_to ปัดเป็นหลักสิบ/ร้อย (เช่น 10 -> 466 กลายเป็น 470) · sign ใส่ + หน้าค่าบวก
    จำนวนเต็มตั้งแต่ 1,000 ขึ้นไปใส่จุลภาค
    """
    value = F(key)
    if index is not None:
        value = list(value.values())[index] if isinstance(value, dict) else value[index]
    if absval:
        value = abs(value)
    if round_to:
        value = round(value / round_to) * round_to
    if digits == 0:
        text = f"{round(value):,}"
    else:
        text = f"{value:,.{digits}f}"
    if sign and value > 0:
        text = "+" + text
    return text.replace("-", "−")  # เครื่องหมายลบตัวจริง (U+2212) อ่านง่ายกว่าขีดสั้น


@cache
def derived():
    """อาร์เรย์ที่คำนวณด้วยโค้ดของโครงงาน DSP แล้ว (data/derived.npz)"""
    return dict(np.load(ROOT / "data" / "derived.npz"))


@cache
def processed(name):
    """ไฟล์ผลใน data/processed/ ของโครงงาน DSP"""
    with np.load(PROC / name, allow_pickle=True) as z:
        return {k: z[k] for k in z.files}
