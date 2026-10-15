"""SQ09 — หน้าในตอนนี้ (สเปกเต็มอยู่ใน context/script.md หัวข้อ ### SQ09_…):
    SQ09_S010  รันทั้งสายใหม่ 8 แบบ ข้อสรุปหลักผ่านครบ ข้อย่อยบางข้อไม่แน่น
    SQ09_S020  สัญญาณขาเข้าก็ต้องตรวจ: มาตรวัดภูเก็ตสองคลังแยกทางหลังปี 2005
    SQ09_S030  coherence ไม่ใช่เหตุและผล — ผลสอดคล้องกับกลไก ไม่ได้พิสูจน์มัน

ยังเป็นภาพสำรองทุกหน้า · แทนหน้าใดด้วยแอนิเมชัน = เพิ่ม method ชื่อรหัสหน้าตัวเล็กใน class
กฎ: context/scene-rules.md · render: PYTHONPATH=manim uv run manim-slides render -ql manim/sq09_robustness.py SQ09
"""

from slides_kit import DeckSlide


class SQ09(DeckSlide):
    SEQ = "SQ09"
