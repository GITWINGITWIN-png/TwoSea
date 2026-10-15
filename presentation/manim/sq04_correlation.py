"""SQ04 — หน้าในตอนนี้ (สเปกเต็มอยู่ใน context/script.md หัวข้อ ### SQ04_…):
    SQ04_S020  สหสัมพันธ์ทั้งอนุกรมได้แค่ 0.30 และ 0.10 เพราะความสัมพันธ์ไม่คงที่ตามเวลา

ยังเป็นภาพสำรองทุกหน้า · แทนหน้าใดด้วยแอนิเมชัน = เพิ่ม method ชื่อรหัสหน้าตัวเล็กใน class
กฎ: context/scene-rules.md · render: PYTHONPATH=manim uv run manim-slides render -ql manim/sq04_correlation.py SQ04
"""

from slides_kit import DeckSlide


class SQ04(DeckSlide):
    SEQ = "SQ04"
