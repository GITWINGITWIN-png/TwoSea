"""Render the two style-review stills from blend/lib/GEO_indian_ocean.blend.

    ~/.steam/steam/steamapps/common/Blender/blender -b --factory-startup \
        --python tools/blender/render_sample.py -- [--scale 100] [--only wide|peninsula] [--progress 0.45]

--scale is the resolution percentage (use 25 for quick looks while iterating).
"""
import argparse
import sys
import time
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[2]
ap = argparse.ArgumentParser()
ap.add_argument("--scale", type=int, default=100)
ap.add_argument("--only", choices=["wide", "peninsula"])
ap.add_argument("--progress", type=float, default=0.45)
ap.add_argument("--out", default=str(ROOT / "renders" / "samples"))
args = ap.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])

bpy.ops.wm.open_mainfile(filepath=str(ROOT / "blend" / "lib" / "GEO_indian_ocean.blend"))
scene = bpy.context.scene
scene.render.resolution_percentage = args.scale
scene.frame_set(1)


def shoot(cam_name, progress, out_name):
    cam = bpy.data.objects[cam_name]
    scene.camera = cam
    # the far camera needs thick coastlines, the near one thin ones (one curve set visible per camera)
    for name, key in (("GEO_coastline_wide", "wide"), ("GEO_coastline_close", "close")):
        bpy.data.objects[name].hide_render = cam["coast_set"] != key
    for name in ("GEO_station_ktn", "GEO_station_klk"):
        o = bpy.data.objects[name]
        o.scale = (o["base_radius"] * cam["marker_scale"],) * 3
    bpy.data.objects["FX_kelvin"]["progress"] = progress
    bpy.context.view_layer.update()
    scene.render.filepath = str(Path(args.out) / out_name)
    t = time.time()
    bpy.ops.render.render(write_still=True)
    print(f"RENDER {out_name}: {time.time() - t:.1f} s")


Path(args.out).mkdir(parents=True, exist_ok=True)
if args.only != "peninsula":
    shoot("CAM_SQ08_wide", args.progress, "sample_3d_wide.png")
if args.only != "wide":
    shoot("CAM_SQ01_peninsula", 0.0, "sample_3d_peninsula.png")
