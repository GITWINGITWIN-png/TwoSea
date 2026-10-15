"""การ์ดข้อความสำหรับช็อตที่ภาพสำรองเป็น 'card:' + ป้าย 'ภาพสำรอง' แบบโปร่งใส

เรียกจาก tools/plan_edit.py (อ่าน renders/cards/cards.json) — ไม่ต้องรันเอง
หนึ่ง scene บันทึกหลายภาพ: วาดทีละการ์ดแล้วเก็บเฟรมเป็น PNG ทีละไฟล์
"""

import json
from pathlib import Path

from manim import DOWN, UR, Scene
from PIL import Image

from facts import ROOT
from plots import CHAPTERS, chapter_bar
from studio_style import ALERT, MUTED, SIZE_SMALL, SIZE_TITLE, setup_scene, tag, thai

OUT = ROOT / "renders" / "cards"


def _save(scene, path):
    scene.renderer.update_frame(scene)
    Image.fromarray(scene.renderer.get_frame()).save(path)


class Cards(Scene):
    def construct(self):
        setup_scene(self)
        for card in json.loads((OUT / "cards.json").read_text()):
            self.clear()
            n = int(card["sequence"][2:])
            title = thai(card["text"], size=SIZE_TITLE, weight="SEMIBOLD")
            title.scale_to_fit_width(min(title.width, 12.5))
            note = thai(f"{CHAPTERS[n - 1]} · {card['id']}", size=SIZE_SMALL, color=MUTED).next_to(title, DOWN, buff=0.5)
            self.add(chapter_bar(n), title, note)
            _save(self, OUT / f"{card['id']}.png")


class FallbackTag(Scene):
    """ป้ายมุมขวาบนบอกว่าช็อตนี้ยังเป็นภาพสำรอง — รันด้วย -t (พื้นโปร่งใส)"""

    def construct(self):
        self.add(tag("ภาพสำรองจากรายงาน · ยังไม่ใช่ภาพจริง", ALERT).to_corner(UR, buff=0.35).shift(DOWN * 0.75))
        _save(self, OUT / "fallback_tag.png")
