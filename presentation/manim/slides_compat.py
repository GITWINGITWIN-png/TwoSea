"""ให้ manim-slides 5.7.0 ทำงานกับ Manim 0.22 — import Slide จากที่นี่เท่านั้น

    from slides_compat import Slide

ทำไมต้องมี (เจอใน fit test 2026-10-10): manim-slides 5.7.0 อ่าน/ตั้ง config ของ Manim 7 ตัว
Manim 0.22 ปรับระบบ config/cache แล้วมี 3 ตัวที่ใช้ไม่ได้ — แกนหลัก (partial_movie_files) ยังอยู่ครบ
จึงแก้ที่ชั้น config อย่างเดียว ไม่แตะไฟล์ใน .venv (แก้ใน .venv จะหายเมื่อติดตั้งใหม่และไม่อยู่ใน git)

  write_to_movie    ถูกลบใน 0.22 · manim-slides ตั้งเป็น True ทุกครั้ง → รับค่าแล้วทิ้ง (0.22 เขียนวิดีโอเสมออยู่แล้ว)
  flush_cache       ถูกลบใน 0.22 · manim-slides แค่อ่านว่าต้องล้าง cache ไหม → ตอบ False
  max_files_cached  manim-slides ตั้ง inf ชั่วคราวระหว่าง render · 0.22 รับแค่จำนวนเต็ม และใช้ -1 = ไม่จำกัด → แปลงให้

ถ้า manim-slides รุ่นใหม่รองรับ Manim 0.22 แล้ว ลบไฟล์นี้ได้ และเปลี่ยน import เป็น `from manim_slides import Slide`
"""

from manim._config.utils import ManimConfig

if not hasattr(ManimConfig, "write_to_movie"):
    ManimConfig.write_to_movie = property(lambda self: True, lambda self, value: None)

if not hasattr(ManimConfig, "flush_cache"):
    ManimConfig.flush_cache = property(lambda self: False, lambda self, value: None)

_max_files = ManimConfig.max_files_cached


def _set_max_files(self, value):
    _max_files.fset(self, -1 if value == float("inf") else value)


ManimConfig.max_files_cached = property(_max_files.fget, _set_max_files)

from manim_slides import Slide  # noqa: E402 — ต้อง import หลังแก้ config

__all__ = ["Slide"]
