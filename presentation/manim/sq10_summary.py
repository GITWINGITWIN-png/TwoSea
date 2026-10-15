"""SQ10 — หน้าในตอนนี้ (สเปกเต็มอยู่ใน context/script.md หัวข้อ ### SQ10_…):
    SQ10_S010  DSP ที่ทำอย่างระวังทำให้ได้ยินความต่างของสองทะเลอย่างมั่นใจ
    SQ10_S020  ขอบคุณครับ · ถาม-ตอบ

ยังเป็นภาพสำรองทุกหน้า · แทนหน้าใดด้วยแอนิเมชัน = เพิ่ม method ชื่อรหัสหน้าตัวเล็กใน class
กฎ: context/scene-rules.md · render: PYTHONPATH=manim uv run manim-slides render -ql manim/sq10_summary.py SQ10
"""

from slides_kit import DeckSlide


class SQ10(DeckSlide):
    SEQ = "SQ10"
