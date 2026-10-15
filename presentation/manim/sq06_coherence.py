"""SQ06 — หน้าในตอนนี้ (สเปกเต็มอยู่ใน context/script.md หัวข้อ ### SQ06_…):
    SQ06_S010  coherence ในวิชาต้องเฉลี่ยหลายท่อนแบบ Welch ไม่อย่างนั้นได้ 1 เสมอ
    SQ06_S020  WTC ใช้การปรับเรียบในเวลาและสเกล แทนการเฉลี่ยแบบ Welch — ได้ทั้งขนาดและเฟส
    SQ06_S030  อันดามันมีก้อน coherence ใหญ่ที่คาบ 2–5 ปี ส่วนอ่าวไทยมีแต่จุดกระจาย
    SQ06_S040  MWC: coherence ของหลายดัชนีพร้อมกัน — ค้นครบ 218 ชุดด้วย Cholesky แบบเพิ่มทีละตัว

ยังเป็นภาพสำรองทุกหน้า · แทนหน้าใดด้วยแอนิเมชัน = เพิ่ม method ชื่อรหัสหน้าตัวเล็กใน class
กฎ: context/scene-rules.md · render: PYTHONPATH=manim uv run manim-slides render -ql manim/sq06_coherence.py SQ06
"""

from slides_kit import DeckSlide


class SQ06(DeckSlide):
    SEQ = "SQ06"
