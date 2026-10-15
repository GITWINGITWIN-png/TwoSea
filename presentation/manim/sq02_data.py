"""SQ02 — หน้าในตอนนี้ (สเปกเต็มอยู่ใน context/script.md หัวข้อ ### SQ02_…):
    SQ02_S010  สัญญาณที่มี: ระดับน้ำสองสถานี 865 เดือน และดัชนีภูมิอากาศ 8 ตัว
    SQ02_S040  โจทย์ DSP: สองสัญญาณสัมพันธ์กันที่คาบไหน เมื่อไร และเกิน noise หรือไม่

ยังเป็นภาพสำรองทุกหน้า · แทนหน้าใดด้วยแอนิเมชัน = เพิ่ม method ชื่อรหัสหน้าตัวเล็กใน class
กฎ: context/scene-rules.md · render: PYTHONPATH=manim uv run manim-slides render -ql manim/sq02_data.py SQ02
"""

from slides_kit import DeckSlide


class SQ02(DeckSlide):
    SEQ = "SQ02"
