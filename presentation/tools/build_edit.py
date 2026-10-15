"""สร้าง timeline ใน Blender VSE จาก renders/edit_plan.json -> blend/edit.blend (และ render ได้)

    blender -b --factory-startup --python tools/build_edit.py -- [--render renders/edit/edit_v000.mp4] [--half]

ช่อง (channel): 1 พื้นหลัง · 2 ภาพของช็อต · 3 ป้าย "ภาพสำรอง" · 4 เสียงพูด · 5 ดนตรี
หลังสร้างแล้วเปิด edit.blend ปรับมือได้ — แต่ถ้ารันสคริปต์นี้ใหม่ edit จะถูกสร้างใหม่ทั้งหมดจากแผน
"""

import json
import sys
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parent.parent
args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
render_to = args[args.index("--render") + 1] if "--render" in args else None
half = "--half" in args

plan = json.loads((ROOT / "renders" / "edit_plan.json").read_text())
scene = bpy.context.scene
scene.name = "EDIT_two_seas"
scene.render.resolution_x, scene.render.resolution_y = plan["width"], plan["height"]
scene.render.resolution_percentage = 50 if half else 100
scene.render.fps = plan["fps"]
scene.frame_start, scene.frame_end = 1, plan["frame_end"]
# ภาพจาก Manim/รายงานเป็น sRGB สำเร็จแล้ว — AgX (ค่าปริยาย) จะทำให้มืดและสีเพี้ยน
scene.view_settings.view_transform = "Standard"
scene.view_settings.look = "None"

se = scene.sequence_editor_create()
for strip in list(se.strips):
    se.strips.remove(strip)
scene.timeline_markers.clear()

bg = se.strips.new_effect("BG", "COLOR", 1, 1, length=plan["frame_end"])
bg.color = (0.0545, 0.102, 0.149)  # #0E1A26

for shot in plan["shots"]:
    media, start, frames = shot["media"], shot["start"], shot["frames"]
    if media["type"] == "movie":
        strip = se.strips.new_movie(shot["id"], media["path"], 2, start, fit_method="FIT")
        strip.frame_final_duration = min(frames, strip.frame_final_duration)
    else:
        strip = se.strips.new_image(shot["id"], media["path"], 2, start, fit_method="FIT")
        strip.frame_final_duration = frames
        if "card" not in media:  # รูปจากรายงาน (พื้นขาว) — เว้นขอบให้เห็นว่าเป็นภาพแทน
            strip.transform.scale_x = strip.transform.scale_y = 0.86
    if shot["status"] == "fallback":
        tag = se.strips.new_image(f"{shot['id']}_tag", plan["fallback_tag"], 3, start)
        tag.frame_final_duration = frames
        tag.blend_type = "ALPHA_OVER"
    if shot.get("audio"):
        se.strips.new_sound(f"{shot['id']}_vo", shot["audio"], 4, start)

for m in plan["markers"]:
    scene.timeline_markers.new(m["name"], frame=m["frame"])

out_blend = ROOT / "blend" / "edit.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(out_blend))
print("EDIT_SAVED", out_blend, "frames", plan["frame_end"])

if render_to:
    r = scene.render
    r.filepath = str(ROOT / render_to)
    r.image_settings.media_type = "VIDEO" if hasattr(r.image_settings, "media_type") else r.image_settings.media_type
    r.image_settings.file_format = "FFMPEG"
    r.ffmpeg.format, r.ffmpeg.codec = "MPEG4", "H264"
    r.ffmpeg.constant_rate_factor = "MEDIUM"
    r.ffmpeg.audio_codec, r.ffmpeg.audio_mixrate = "AAC", 48000
    bpy.ops.render.render(animation=True)
    print("EDIT_RENDERED", r.filepath)
