"""ฐานของ deck ทุกตอน — หนึ่งตอน = หนึ่ง class · หนึ่งหน้า = หนึ่ง method ชื่อรหัสหน้า

    class SQ03(DeckSlide):
        SEQ = "SQ03"

        def sq03_s030(self):              # หน้า SQ03_S030 — ถ้าไม่มี method นี้ หน้าจะเป็นภาพสำรองอัตโนมัติ
            page = self.slide("SQ03_S030")  # คลิกแรกของหน้า: ล้างหน้าเก่า + หัวข้อ + ป้าย + โน้ต
            self.play(Create(axes))          # แอนิเมชันของขั้นที่ 1
            self.click()                     # คลิกถัดไปในหน้าเดียวกัน
            self.play(...)                   # ขั้นที่ 2

render หนึ่งตอน:  PYTHONPATH=manim uv run manim-slides render -ql manim/sq03_signal.py SQ03

ทำไมออกแบบแบบนี้
- deck ต้อง "นำเสนอได้ครบเสมอ": หน้าไหนยังไม่มีแอนิเมชันก็เป็นรูปจากรายงานไปก่อน (fallback)
  คนเขียนฉากแค่เพิ่ม method ทีละหน้า ไม่ต้องแตะส่วนอื่น · build_deck ดูว่าหน้าไหนมี method เพื่อนับสถานะ
- หัวข้อ ป้ายชนิดภาพ ป้ายบท โน้ต มาจาก context/script.md + shotlist.yaml ที่ตรวจด้วย check_claims แล้ว
  คนเขียนฉากจึงไม่ต้องพิมพ์ข้อความเหล่านี้เอง (และพิมพ์ผิดไม่ได้)
- ต้นขั้นแรกของทุกหน้า หัวข้อขึ้นแล้วทันที (ตัดภาพ ไม่ fade) → ภาพย่อ (poster = เฟรมแรก) ใน PowerPoint ไม่ว่าง
"""

from __future__ import annotations

import re
from functools import cache
from pathlib import Path

import yaml
from manim import (
    DOWN, LEFT, RIGHT, UL, UP, UR,
    FadeIn, ImageMobject, RoundedRectangle, VGroup, config,
)

from facts import ROOT
from plots import CHAPTERS, chapter_bar, summary_card
from slides_compat import Slide
from studio_style import (
    GREY, INK, MUTED, NAVY, PANEL, SIZE_SMALL, course_tag, kind_tag, setup_scene, tag, thai,
)

SCRIPT = ROOT / "context" / "script.md"
SHOTLIST = ROOT / "context" / "shotlist.yaml"
FIGS = ROOT / "00_input" / "report_figs"
APPENDIX = "SQ11"

# --- พื้นที่บนจอ (หน่วย Manim · จอกว้าง 14.2 สูง 8) ------------------------------------------------------
# แถบตอนอยู่บนสุด (y ≈ 3.6) → หัวข้อเริ่มใต้แถบ → เนื้อหาอยู่ระหว่างใต้หัวข้อถึง CONTENT_BOTTOM → เลขหน้ามุมขวาล่าง
LEFT_X = -config.frame_width / 2 + 0.6     # ขอบซ้ายของหัวข้อ
HEADLINE_TOP = 3.15
HEADLINE_SIZE = 40
HEADLINE_MAX_W = 12.9
CONTENT_TOP = 1.75                         # ขอบบนของพื้นที่เนื้อหาเมื่อหัวข้อยาวบรรทัดเดียว
CONTENT_BOTTOM = -3.35
CONTENT_W = 13.0


# --- ข้อมูลของหน้า (อ่านจากบท) ---------------------------------------------------------------------------

@cache
def pages():
    """{รหัสหน้า: รายการใน shotlist.yaml} ตามลำดับของ deck"""
    return {p["id"]: p for p in yaml.safe_load(SHOTLIST.read_text())}


def pages_of(seq):
    return [p for p in pages().values() if p["sequence"] == seq]


def page_number(page_id):
    """เลขหน้าที่เห็นบนจอ — หน้าหลักนับ 1..N · ภาคผนวกนับ ก1.. แยก"""
    main = [p for p in pages() if not p.startswith(APPENDIX)]
    if page_id in main:
        return f"{main.index(page_id) + 1} / {len(main)}"
    appx = [p for p in pages() if p.startswith(APPENDIX)]
    return f"ภาคผนวก {appx.index(page_id) + 1}"


@cache
def _notes():
    """{รหัสหน้า: [ประโยคในส่วน 'พูด:']} — ตัดป้าย [Cnn]/[F] ออก · คงเครื่องหมาย ✂ ไว้เตือนว่าตัดได้"""
    out, page, speaking = {}, None, False
    for line in SCRIPT.read_text().splitlines():
        if m := re.match(r"^### (SQ\d+_S\d+)", line):
            page, speaking = m.group(1), False
            out[page] = []
        elif page and line.startswith("พูด:"):
            speaking = True
        elif speaking and line.startswith("- "):
            out[page].append(re.sub(r"\s*\[(C\d+|F)\]", "", line[2:]).strip())
        elif speaking and line.strip():
            speaking = False
    return out


def notes(page_id):
    """โน้ตผู้พูดของหน้า: บรรทัดแรก = หัวข้อ (ไว้เหลือบดู) แล้วตามด้วยประโยคที่จะพูด"""
    head = pages()[page_id]["headline"]
    return "\n".join([f"▶ {head}", ""] + [f"• {s}" for s in _notes()[page_id]])


# --- ชิ้นส่วนบนจอ ---------------------------------------------------------------------------------------

def headline(text, size=HEADLINE_SIZE, max_width=HEADLINE_MAX_W):
    """หัวข้อชิดซ้ายใต้แถบตอน · ยาวเกินบรรทัดเดียว → ตัดเป็นสองบรรทัดที่ช่องว่างใกล้กลางที่สุด

    ภาษาไทยไม่มีช่องว่างระหว่างคำ จึงตัดได้เฉพาะช่องว่างที่บทเขียนไว้ (ระหว่างวลี) — ไม่ตัดกลางคำ
    """
    line = thai(text, size=size, color=INK, weight="SEMIBOLD")
    if line.width > max_width and " " in text:
        spaces = [i for i, ch in enumerate(text) if ch == " "]
        cut = min(spaces, key=lambda i: abs(i - len(text) / 2))
        lines = VGroup(*[thai(t, size=size, color=INK, weight="SEMIBOLD") for t in (text[:cut], text[cut + 1:])])
        line = lines.arrange(DOWN, aligned_edge=LEFT, buff=0.18)
    if line.width > max_width:
        line.scale_to_fit_width(max_width)
    return line.move_to([LEFT_X, HEADLINE_TOP, 0], aligned_edge=UL)


def content_box(head=None):
    """(กลาง, กว้าง, สูง) ของพื้นที่เนื้อหาใต้หัวข้อ — ใช้วางกราฟ/ภาพให้ไม่ชนหัวข้อ"""
    top = min(CONTENT_TOP, head.get_bottom()[1] - 0.35) if head is not None else CONTENT_TOP
    height = top - CONTENT_BOTTOM
    return (0.0, CONTENT_BOTTOM + height / 2, 0.0), CONTENT_W, height


def figure(name, head=None, max_w=None, max_h=None):
    """รูปจากรายงาน (00_input/report_figs/<name>.png) บนแผ่นสีอ่อน — ขยายให้เต็มพื้นที่เนื้อหาโดยไม่บิดสัดส่วน"""
    center, w, h = content_box(head)
    img = ImageMobject(str(FIGS / f"{name}.png"))
    img.scale_to_fit_width(max_w or w - 0.4)
    if img.height > (max_h or h - 0.3):
        img.scale_to_fit_height(max_h or h - 0.3)
    panel = RoundedRectangle(corner_radius=0.1, width=img.width + 0.3, height=img.height + 0.3,
                             fill_color="#F4F6F8", fill_opacity=1, stroke_width=0)
    panel.move_to(center)
    img.move_to(center)
    return panel, img


def page_tags(page):
    """ป้ายมุมขวาบน: ชนิดภาพ (ข้อมูลจริง/แผนภาพ/เปรียบเทียบ) + ป้ายบทเรียนทางซ้ายของมัน"""
    group = VGroup()
    kind = kind_tag(page["kind"]) if page["kind"] in ("data", "schematic", "analogy") else None
    if kind is not None:
        group.add(kind)
    if page["course"]:
        ct = course_tag(page["course"])
        if kind is not None:
            ct.next_to(kind, LEFT, buff=0.2).align_to(kind, UP)
        else:
            ct.to_corner(UR, buff=0.35)
        group.add(ct)
    return group


def appendix_bar():
    return thai("ภาคผนวก · ใช้ตอบคำถาม", size=SIZE_SMALL, color=MUTED).to_corner(UL, buff=0.32)


# --- class ฐาน ------------------------------------------------------------------------------------------

class DeckSlide(Slide):
    """ตอนหนึ่งของ deck — subclass ตั้ง SEQ แล้วเพิ่ม method ชื่อรหัสหน้า (ตัวเล็ก) สำหรับหน้าที่มีแอนิเมชัน"""

    SEQ = "SQ00"
    skip_reversing = True  # ไม่เล่นถอยหลังตอนย้อนหน้า → ไม่ต้องสร้างวิดีโอกลับด้าน render เร็วขึ้น

    # ---- ลำดับของตอน
    def construct(self):
        setup_scene(self)
        self.wait_time_between_slides = 0.1  # ให้เฟรมสุดท้ายของทุกขั้นนิ่งก่อนตัด (คำแนะนำของ manim-slides)
        n = int(self.SEQ[2:])
        bar = appendix_bar() if self.SEQ == APPENDIX else chapter_bar(n)
        self.add_to_canvas(bar=bar)
        self.add(bar)
        self._page = None
        for page in pages_of(self.SEQ):
            method = getattr(self, page["id"].lower(), None)
            if method is None:
                self.fallback(page["id"])
            else:
                method()

    @classmethod
    def animated_pages(cls):
        """รหัสหน้าที่มีแอนิเมชันแล้ว (ใช้นับสถานะใน build_deck)"""
        return [p["id"] for p in pages_of(cls.SEQ) if hasattr(cls, p["id"].lower())]

    # ---- หน้า + คลิก
    def slide(self, page_id, *, loop=False, show_headline=True, headline_text=None):
        """เริ่มหน้าใหม่ = คลิกแรกของหน้า · ล้างของหน้าก่อน (เหลือแถบตอน) · วางหัวข้อ ป้าย เลขหน้า ทันที

        headline_text: ใช้แทนหัวข้อเต็มชั่วคราว (เช่น ซ่อนเฉลยก่อนจุดทาย) — ต้องเป็นส่วนหนึ่งของหัวข้อในบท
        คืน dict: head (หัวข้อ), tags, number, box (กลาง, กว้าง, สูง ของพื้นที่เนื้อหา)
        """
        page = pages()[page_id]
        self._page = page_id
        self.next_slide(notes=notes(page_id), loop=loop)
        if self.mobjects_without_canvas:
            self.remove(*self.mobjects_without_canvas)
        parts = {"tags": page_tags(page),
                 "number": thai(page_number(page_id), size=SIZE_SMALL, color=MUTED).to_corner(RIGHT + DOWN, buff=0.3)}
        if show_headline:
            text = headline_text or page["headline"]
            if text not in page["headline"]:
                raise ValueError(f"{page_id}: headline_text ต้องเป็นส่วนของหัวข้อในบท — '{text}'")
            parts["head"] = headline(text)
        else:
            parts["head"] = None
        self.add(*[m for m in parts.values() if m is not None])
        parts["box"] = content_box(parts["head"])
        return parts

    def click(self, *, loop=False):
        """คลิกถัดไปในหน้าเดียวกัน (โน้ตเดิม)"""
        self.next_slide(notes=notes(self._page), loop=loop)

    def video(self, page_id, path):
        """หน้าที่เป็นวิดีโอภายนอกทั้งหน้า (เช่น Blender SQ08) — ต้องเป็น 1920×1080 · 30 fps (manim-slides ไม่ย่อขยายให้)"""
        self._page = page_id
        self.next_slide(src=Path(path), notes=notes(page_id))

    def summary(self, text):
        """คลิกใหม่ แล้วการ์ดสรุปท้ายตอนเลื่อนขึ้นจากล่าง (ข้อความตามบรรทัด 'การ์ดสรุป:' ในบท)"""
        self.click()
        card = summary_card(text)
        self.play(FadeIn(card, shift=UP * 0.3), run_time=0.6)
        return card

    # ---- ภาพสำรอง
    def fallback(self, page_id):
        """หน้าภาพสำรอง: หัวข้อ + รูปจากรายงาน (หรือการ์ดข้อความ) — คลิกเดียว"""
        page = pages()[page_id]
        parts = self.slide(page_id)
        kind, value = page["fallback"].split(":", 1)
        if kind == "fig":
            panel, img = figure(value, parts["head"])
            # ป้ายที่มาวางในมุมขวาบนของกรอบรูป — ไม่ชนเลขหน้า/การ์ดสรุปที่อยู่ล่างจอ
            source = tag("รูปจากรายงาน", GREY)
            source.move_to(panel.get_corner(UR) + DOWN * (source.height / 2 + 0.08) + LEFT * (source.width / 2 + 0.08))
            self.play(FadeIn(panel), FadeIn(img), FadeIn(source), run_time=0.4)
        else:
            card = thai(value, size=40, color=INK, weight="SEMIBOLD")
            card.scale_to_fit_width(min(card.width, CONTENT_W - 1))
            center, _, _ = parts["box"]
            box = RoundedRectangle(corner_radius=0.15, width=card.width + 1.0, height=card.height + 0.9,
                                   fill_color=PANEL, fill_opacity=1, stroke_color=NAVY, stroke_width=3).move_to(center)
            card.move_to(center)
            self.play(FadeIn(box), FadeIn(card), run_time=0.4)
        self.wait(0.3)


__all__ = [
    "DeckSlide", "pages", "pages_of", "notes", "headline", "content_box", "figure", "page_number",
    "CONTENT_TOP", "CONTENT_BOTTOM", "CONTENT_W", "LEFT_X", "CHAPTERS",
]
