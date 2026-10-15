"""สไตล์กลางของคลิป — ทุกฉากต้อง import จากที่นี่ ห้ามตั้งสี/ฟอนต์เอง

ทำไมต้องมีไฟล์นี้: คลิป ~45 ช็อตเขียนโดยหลายคน (session หลัก + subagent) ถ้าแต่ละฉากเลือกสีเอง
"อันดามัน = น้ำเงิน, อ่าวไทย = ส้ม" จะเพี้ยนทันที และคนดูจะสับสนว่าเส้นไหนคือทะเลไหน

2026-10-13: เปลี่ยนเป็น theme D (พื้นสว่าง · context/design-brief.md "การตัดสินใจ") — คลิปวางอยู่ในการ์ดสีขาวของหน้า
Slidev จึงใช้พื้นขาวตรงกับการ์ด · สีข้อมูลตรงกับตัวแปรใน deck/style.css · ชุดสีพื้นเข้มเดิมอยู่ใน git (clip-v1 / main)
"""

from manim import (
    DOWN, LEFT, RIGHT, UP, UL, UR,
    ManimColor, RoundedRectangle, Text, VGroup, config,
)

# --- สี -------------------------------------------------------------------------------------------------
BG = "#FFFFFF"        # พื้นคลิป = สีการ์ดของหน้า (คลิปวางในการ์ดขาว)
PANEL = "#EAF3F6"     # กล่อง/การ์ดในคลิป = สีพื้นหน้า deck
INK = "#12303D"       # ตัวหนังสือหลัก
MUTED = "#5B7480"     # ตัวหนังสือรอง แกน กริด
NAVY = "#12303D"      # พื้นฟองข้อความ / แถบเข้ม
ANDAMAN = "#2F74C0"   # ทะเลอันดามัน (= --andaman)
GULF = "#D9822B"      # อ่าวไทย (= --gulf) — ห้ามใช้ส้มกับอย่างอื่น
NINO = "#2E3A46"      # Niño3.4 (= --nino)
DMI = "#7B61B0"       # DMI (= --dmi)
OK = "#1C8A5A"        # ผ่าน
AMBER = "#C98A12"     # ก้ำกึ่ง
ALERT = "#C0392B"     # เตือน / ไม่ผ่าน / aliasing (แดง ไม่ใช่ส้ม)
GREY = "#7F8FA0"      # อนุมาน
EVENT = "#FFD7A8"     # แถบไฮไลต์ช่วงเหตุการณ์ (= --event)
SEA_LOW = "#2F74C0"   # ระดับน้ำต่ำกว่าปกติ: น้ำเงินเข้ม (ทึบ 0.6)
SEA_HIGH = "#9CC0E6"  # ระดับน้ำสูงกว่าปกติ: น้ำเงินอ่อน

# --- ฟอนต์ ----------------------------------------------------------------------------------------------
# Anuphan = ฟอนต์เนื้อความของ deck (theme D) · ติดตั้งที่ ~/.local/share/fonts/two-seas/ · Pango shape ไทยให้ถูก
FONT = "Anuphan"
FONT_HEAD = "Kanit"   # ตัวเลขเด่น / หัวการ์ดในคลิป
# ขนาดตามสเปกใหม่ (ที่ 1080p): เนื้อ ≈ 24 px · เล็กสุด ≈ 20 px — font_size 26 เดิมได้ ≈ 36 px
SIZE_TITLE = 40
SIZE_BODY = 22
SIZE_SMALL = 18   # เล็กสุดที่ยอมให้ขึ้นจอ (≈ 20 px ที่ 1080p ในคลิปกว้าง 1680) — ห้ามเล็กกว่านี้


def thai(text, size=SIZE_BODY, color=INK, weight="NORMAL", **kwargs):
    """ข้อความไทย/อังกฤษผสมด้วยฟอนต์ของคลิป — ใช้แทน Text() ตรง ๆ ทุกที่"""
    return Text(text, font=FONT, font_size=size, color=color, weight=weight, **kwargs)


# --- ป้าย -----------------------------------------------------------------------------------------------
# ป้ายบอกชนิดของภาพ: คนดูต้องรู้เสมอว่ากำลังดู "ข้อมูลจริง" หรือ "ภาพอธิบาย"
KIND_TAGS = {
    "data": ("ข้อมูลจริง", OK),
    "schematic": ("แผนภาพ", AMBER),
    "analogy": ("เปรียบเทียบ", GREY),
}
# ป้ายระดับหลักฐาน — ชุดเดียวกับรายงาน
EVIDENCE_TAGS = {
    "strong": ("หนักแน่น", OK),
    "single": ("งานเดียว", AMBER),
    "inferred": ("อนุมาน", GREY),
}


def tag(label, color, size=SIZE_SMALL):
    """ป้ายสี่เหลี่ยมมุมมน ตัวหนังสือขาวบนพื้นสี

    ไทยมีสระบน-ล่าง (ที่, อนุ) ถ้าจัดกึ่งกลางตามกรอบของข้อความ ป้ายที่มีสระล่างตัวหนังสือจะลอยขึ้น
    จึงพิมพ์ "ก" นำหน้าไว้เป็นตัวอ้างอิง (พยัญชนะที่ไม่มีหาง) จัดกึ่งกลางป้ายที่ตัว "ก"
    แล้วค่อยลบออก — ทุกป้ายจึงวางบนเส้นฐานเดียวกัน
    """
    text = thai("ก" + label, size=size, color="#FFFFFF", weight="SEMIBOLD")
    ref = text[0]
    glyphs = VGroup(*text[1:])
    height = ref.height * 2.1
    box = RoundedRectangle(
        corner_radius=0.08, width=glyphs.width + 0.35, height=height,
        fill_color=color, fill_opacity=0.9, stroke_width=0,
    )
    box.move_to([glyphs.get_center()[0], ref.get_center()[1], 0])
    return VGroup(box, glyphs)


def kind_tag(kind):
    """ป้ายมุมขวาบน: ข้อมูลจริง / แผนภาพ / เปรียบเทียบ"""
    label, color = KIND_TAGS[kind]
    return tag(label, color).to_corner(UR, buff=0.35)


def evidence_tag(level):
    label, color = EVIDENCE_TAGS[level]
    return tag(label, color)


def course_tag(text):
    """ป้ายบทเรียนมุมซ้ายบน เช่น 'บทที่ 3 · Down-sampling' — ผูกคลิปกับวิชา"""
    return tag(text, NAVY).to_corner(UL, buff=0.35)


def setup_scene(scene):
    """เรียกต้น construct() ทุกฉาก

    ห่อด้วย ManimColor (ไม่ใช่สตริง) เพราะ manim-slides อ่านสีพื้นหลังด้วย .to_hex() ตอนเขียนไฟล์สไลด์
    """
    scene.camera.background_color = ManimColor(BG)


config.background_color = BG
