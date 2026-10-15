"""SQ08 — หน้าในตอนนี้ (สเปกเต็มอยู่ใน context/script.md หัวข้อ ### SQ08_…):
    SQ08_S020  ตีความทางกายภาพ: ลมที่ศูนย์สูตร → คลื่นเคลวิน → อันดามัน · อ่าวไทยตื้นและอยู่นอกเส้นทาง
    SQ08_S050  ใช้เฟสทดสอบการตีความ: ทายทิศไว้ก่อนดูผล แล้วตรงทั้งสี่ดัชนี

ยังเป็นภาพสำรองทุกหน้า · แทนหน้าใดด้วยแอนิเมชัน = เพิ่ม method ชื่อรหัสหน้าตัวเล็กใน class
กฎ: context/scene-rules.md · render: PYTHONPATH=manim uv run manim-slides render -ql manim/sq08_mechanism.py SQ08
"""

from slides_kit import DeckSlide


class SQ08(DeckSlide):
    SEQ = "SQ08"
