"""SQ05 — หน้าในตอนนี้ (สเปกเต็มอยู่ใน context/script.md หัวข้อ ### SQ05_…):
    SQ05_S010  จาก filter bank ในวิชา: แยกแถบต่ำซ้ำ ได้แถบแบบ octave
    SQ05_S020  CWT: เลื่อน Morlet ω0 = 6 ไปตามเวลา ทุกขนาด 12 สเกลต่อ octave
    SQ05_S030  ระนาบเวฟเล็ตบอกว่าจังหวะไหนแรงเมื่อไร — และขอบที่เชื่อไม่ได้ต้องตัดด้วย COI

ยังเป็นภาพสำรองทุกหน้า · แทนหน้าใดด้วยแอนิเมชัน = เพิ่ม method ชื่อรหัสหน้าตัวเล็กใน class
กฎ: context/scene-rules.md · render: PYTHONPATH=manim uv run manim-slides render -ql manim/sq05_wavelet.py SQ05
"""

from slides_kit import DeckSlide


class SQ05(DeckSlide):
    SEQ = "SQ05"
