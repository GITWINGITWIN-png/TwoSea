"""Stage 0 — Blender เรนเดอร์ headless ได้ไหม และวางภาพป้ายไทย (PNG จาก Pango) บนแผ่นระนาบได้ไหม

รัน:  blender -b --factory-startup --python tools/blender_test.py -- <ภาพ.png> <ผลลัพธ์.png>

ทำไมไม่ใช้ข้อความของ Blender เอง: Blender ไม่ shape ภาษาไทย วรรณยุกต์จะชนสระ (ข้อค้นพบจาก spike S6)
จึงวาดป้ายไทยด้วย Pango (Manim) เป็น PNG โปร่งใส แล้ววางเป็นแผ่นภาพในฉาก 3D แทน
"""

import sys

import bpy

image_path, out_path = sys.argv[sys.argv.index("--") + 1:][:2]

scene = bpy.context.scene
engines = {e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items}
scene.render.engine = "BLENDER_EEVEE" if "BLENDER_EEVEE" in engines else "BLENDER_EEVEE_NEXT"
scene.render.resolution_x, scene.render.resolution_y = 960, 540
scene.render.filepath = out_path

# ล้างฉากเริ่มต้น เหลือกล้องใหม่ + แผ่นภาพ
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj)

img = bpy.data.images.load(image_path)
aspect = img.size[0] / img.size[1]
bpy.ops.mesh.primitive_plane_add(size=2)
plane = bpy.context.active_object
plane.scale = (aspect, 1, 1)

mat = bpy.data.materials.new("MAT_label")
mat.use_nodes = True
nodes, links = mat.node_tree.nodes, mat.node_tree.links
nodes.clear()
tex = nodes.new("ShaderNodeTexImage")
tex.image = img
emit = nodes.new("ShaderNodeEmission")
mix = nodes.new("ShaderNodeMixShader")
transp = nodes.new("ShaderNodeBsdfTransparent")
out = nodes.new("ShaderNodeOutputMaterial")
links.new(tex.outputs["Color"], emit.inputs["Color"])
links.new(tex.outputs["Alpha"], mix.inputs["Fac"])
links.new(transp.outputs[0], mix.inputs[1])
links.new(emit.outputs[0], mix.inputs[2])
links.new(mix.outputs[0], out.inputs["Surface"])
plane.data.materials.append(mat)

cam_data = bpy.data.cameras.new("CAM_test")
cam = bpy.data.objects.new("CAM_test", cam_data)
scene.collection.objects.link(cam)
cam.location = (0, -0.6, 4.2)
cam.rotation_euler = (0.15, 0, 0)
scene.camera = cam

bpy.ops.render.render(write_still=True)
print("BLENDER_TEST_OK", scene.render.engine, out_path)
