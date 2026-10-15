"""SQ01 — หน้าในตอนนี้ (สเปกเต็มอยู่ใน context/script.md หัวข้อ ### SQ01_…):
    SQ01_S030  ทะเลสองฝั่ง ฟังภูมิอากาศคนละแบบ
    SQ01_S010  สองทะเลห่างกันราว 470 กม. — ตอบสนองต่อภูมิอากาศเหมือนกันไหม

ยังเป็นภาพสำรองทุกหน้า · แทนหน้าใดด้วยแอนิเมชัน = เพิ่ม method ชื่อรหัสหน้าตัวเล็กใน class
กฎ: context/scene-rules.md · render: PYTHONPATH=manim uv run manim-slides render -ql manim/sq01_opening.py SQ01
"""

from slides_kit import DeckSlide


class SQ01(DeckSlide):
    SEQ = "SQ01"
