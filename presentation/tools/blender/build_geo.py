"""Build blend/lib/GEO_indian_ocean.blend  (the reusable 3D base for SQ01 + SQ08).

    uv run python tools/blender/prep_geo.py          # once: makes data/geo/*.npy + coastlines.json
    ~/.steam/steam/steamapps/common/Blender/blender -b --factory-startup \
        --python tools/blender/build_geo.py

Scripts are the source of truth: delete the .blend and re-run this to get it back.
NO Blender text objects anywhere (Thai can't be shaped) - labels are composited later.

Map: equirectangular, x = (lon - 90) * cos(5 deg), y = lat, so 1 unit ~ 1 degree ~ 111.2 km.
"""
import json
import math
from pathlib import Path

import bpy
import numpy as np
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
GEO = ROOT / "data" / "geo"
OUT = ROOT / "blend" / "lib" / "GEO_indian_ocean.blend"
facts = json.loads((ROOT / "data" / "facts.json").read_text())

# ---------------------------------------------------------------- constants
KM_PER_UNIT = 111.195            # one degree of latitude
LON_C, X_SCALE = 90.0, math.cos(math.radians(5))
TERRAIN_EXAG = 20.0              # vertical exaggeration of land (z = metres * 20 / 111195)
SKIRT_Z = -0.4                   # sea floor under the ocean: flat & deep enough to hide behind the Kelvin dip
LAND_LIFT = 0.01                 # land sits just above sea level -> no z-fighting with the ocean plane
KELVIN_AMP = 0.28                # Kelvin dip depth in units (= 31 km drawn!) - see report for the factor
KELVIN_SIGMA_ALONG, KELVIN_SIGMA_ACROSS = 7.0, 1.7   # units (~degrees): FWHM ~16 deg, ~28 deg to the +-2 sigma ends; ~4 deg wide
BG = "#0E1A26"
ANDAMAN, GULF = "#4A9BE0", "#E8913A"
# World colour in LINEAR light chosen (by a small calibration render) so that, after AgX + the look below,
# the empty background displays as exactly #0E1A26. Plain hex_lin(BG) would come out almost black.
BG_WORLD_LINEAR = (0.013539, 0.022144, 0.036871, 1.0)
SEA_LOW = "#E06C5A"              # studio colour for "lower than normal" - the wave is tinted with it


def xy(lon, lat):
    return (np.asarray(lon) - LON_C) * X_SCALE, np.asarray(lat)


def hex_lin(h, s=1.0):
    """#RRGGBB (sRGB) -> linear RGBA, because Blender colour sockets are linear."""
    c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    c = [(v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4) * s for v in c]
    return (*c, 1.0)


# ---------------------------------------------------------------- scene reset
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.name = "GEO_indian_ocean"
scene.unit_settings.system = 'METRIC'


def link(obj, coll="Collection"):
    bpy.context.scene.collection.objects.link(obj)
    return obj


def node_mat(name):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    return m, nt.nodes, nt.links


def emission_mat(name, color, strength):
    m, n, l = node_mat(name)
    e, o = n.new("ShaderNodeEmission"), n.new("ShaderNodeOutputMaterial")
    e.inputs["Color"].default_value = color
    e.inputs["Strength"].default_value = strength
    l.new(e.outputs[0], o.inputs[0])
    return m


def ramp(nodes, stops):
    cr = nodes.new("ShaderNodeValToRGB")
    el = cr.color_ramp.elements
    while len(el) > 1:
        el.remove(el[-1])
    for i, (pos, col) in enumerate(stops):
        e = el[0] if i == 0 else el.new(pos)
        e.position, e.color = pos, hex_lin(col) if isinstance(col, str) else col
    return cr



def finish_with_edge_fade(n, l, shader_out, out_node):
    """Fade the map tile into the background colour near its border, so it doesn't read as a hard-edged
    rectangle. Mixing with an Emission of the BG colour == the world colour, so the seam is invisible."""
    pos, sep = n.new("ShaderNodeNewGeometry"), n.new("ShaderNodeSeparateXYZ")
    l.new(pos.outputs["Position"], sep.inputs[0])
    def edge(axis_out, centre, half, fade):          # 1 inside, ramps to 0 over `fade` units at the border
        sub = n.new("ShaderNodeMath"); sub.operation = 'SUBTRACT'; sub.inputs[1].default_value = centre
        ab = n.new("ShaderNodeMath"); ab.operation = 'ABSOLUTE'
        mr = n.new("ShaderNodeMapRange"); mr.clamp = True
        mr.inputs[1].default_value, mr.inputs[2].default_value = half - fade, half
        mr.inputs[3].default_value, mr.inputs[4].default_value = 1.0, 0.0
        mr.interpolation_type = 'SMOOTHSTEP'
        l.new(axis_out, sub.inputs[0]); l.new(sub.outputs[0], ab.inputs[0]); l.new(ab.outputs[0], mr.inputs[0])
        return mr.outputs[0]
    fx_ = edge(sep.outputs["X"], 0.0, 49.8, 10.0)
    fy_ = edge(sep.outputs["Y"], 2.5, 27.5, 8.0)
    both = n.new("ShaderNodeMath"); both.operation = 'MULTIPLY'
    l.new(fx_, both.inputs[0]); l.new(fy_, both.inputs[1])
    bg_e = n.new("ShaderNodeEmission"); bg_e.inputs["Color"].default_value = BG_WORLD_LINEAR
    mix = n.new("ShaderNodeMixShader")
    l.new(both.outputs[0], mix.inputs[0]); l.new(bg_e.outputs[0], mix.inputs[1]); l.new(shader_out, mix.inputs[2])
    l.new(mix.outputs[0], out_node.inputs[0])


# ---------------------------------------------------------------- data
elev = np.load(GEO / "elevation.npy")                      # [lat, lon] metres, 3 arc-min
meta = json.loads((GEO / "elevation_meta.json").read_text())
lons = meta["lon0"] + meta["step"] * np.arange(meta["cols"])
lats = meta["lat0"] + meta["step"] * np.arange(meta["rows"])


def grid_to_mesh(name, X, Y, Z, quad_mask=None, attrs=None):
    """Fast numpy -> mesh. X,Y,Z are [rows, cols]; quad_mask [rows-1, cols-1] keeps only some quads."""
    R, C = X.shape
    vid = np.arange(R * C).reshape(R, C)
    quads = np.stack([vid[:-1, :-1], vid[:-1, 1:], vid[1:, 1:], vid[1:, :-1]], -1)
    quads = quads.reshape(-1, 4) if quad_mask is None else quads[quad_mask]
    used = np.unique(quads)                                  # drop vertices no quad uses
    remap = np.full(R * C, -1); remap[used] = np.arange(len(used))
    quads = remap[quads]
    co = np.stack([X.ravel(), Y.ravel(), Z.ravel()], -1)[used].astype(np.float32)
    me = bpy.data.meshes.new(name)
    me.vertices.add(len(used)); me.vertices.foreach_set("co", co.ravel())
    me.loops.add(quads.size); me.loops.foreach_set("vertex_index", quads.ravel())
    me.polygons.add(len(quads))
    me.polygons.foreach_set("loop_start", np.arange(len(quads)) * 4)
    me.polygons.foreach_set("use_smooth", np.ones(len(quads), bool))
    me.update(calc_edges=True)
    for aname, arr in (attrs or {}).items():
        a = me.attributes.new(aname, 'FLOAT', 'POINT')
        a.data.foreach_set("value", arr.ravel()[used].astype(np.float32))
    return me


# ---------------------------------------------------------------- terrain (land only)
LON, LAT = np.meshgrid(lons, lats)
TX, TY = xy(LON, LAT)
is_land = elev > 0
TZ = np.where(is_land, elev * TERRAIN_EXAG / (KM_PER_UNIT * 1000) + LAND_LIFT, SKIRT_Z)
# keep a quad if any corner is land: ocean quads are never drawn (the ocean plane covers them)
qm = is_land[:-1, :-1] | is_land[:-1, 1:] | is_land[1:, :-1] | is_land[1:, 1:]
terrain = link(bpy.data.objects.new("GEO_terrain", grid_to_mesh("GEO_terrain", TX, TY, TZ, qm)))

m, n, l = node_mat("MAT_land")
pos, sep = n.new("ShaderNodeNewGeometry"), n.new("ShaderNodeSeparateXYZ")
mr = n.new("ShaderNodeMapRange")
mr.inputs[1].default_value, mr.inputs[2].default_value = 0.0, 0.8      # height in units -> 0..1
cr = ramp(n, [(0.00, "#B7AB86"),   # sand near the coast
              (0.06, "#8E9672"),   # muted grey-green lowlands
              (0.25, "#6E7C68"),
              (0.55, "#8B8F8E"),   # grey mountains
              (1.00, "#C9CED1")])
bsdf, out = n.new("ShaderNodeBsdfPrincipled"), n.new("ShaderNodeOutputMaterial")
bsdf.inputs["Roughness"].default_value = 1.0
bsdf.inputs["Specular IOR Level"].default_value = 0.0   # matte: no milky sky reflections
l.new(pos.outputs["Position"], sep.inputs[0]); l.new(sep.outputs["Z"], mr.inputs[0])
l.new(mr.outputs[0], cr.inputs[0]); l.new(cr.outputs[0], bsdf.inputs["Base Color"])
finish_with_edge_fade(n, l, bsdf.outputs[0], out)
terrain.data.materials.append(m)

# ---------------------------------------------------------------- ocean surface
OS = 2                                                   # ocean grid = every 2nd ETOPO sample = 0.1 deg
oe = elev[::OS, ::OS]
OX, OY = xy(*np.meshgrid(lons[::OS], lats[::OS]))
depth = np.clip(-oe, 20, None)
# 'shade' 0..1 on a log depth scale: 20 m -> 0 (shelf, light), 200 m -> 0.40, 6000 m -> 1 (deep, navy)
shade = np.clip(np.log(depth / 20) / np.log(300), 0, 1)
ocean = link(bpy.data.objects.new("GEO_ocean", grid_to_mesh("GEO_ocean", OX, OY, np.zeros_like(OX), attrs={"shade": shade})))

m, n, l = node_mat("MAT_ocean")
sh, kv = n.new("ShaderNodeAttribute"), n.new("ShaderNodeAttribute")
sh.attribute_name, kv.attribute_name = "shade", "kelvin"
cr = ramp(n, [(0.00, "#6FB5BF"),    # < ~50 m: Gulf of Thailand, Sunda shelf - clearly lighter
              (0.30, "#3D86A8"),
              (0.45, "#235B85"),    # ~ 300 m shelf break
              (0.70, "#12385F"),
              (1.00, "#0A2240")])   # deep navy
tint = n.new("ShaderNodeMix"); tint.data_type = 'RGBA'
tint.inputs["B"].default_value = hex_lin(SEA_LOW)
k_rng = n.new("ShaderNodeMapRange")                   # kelvin 0..1 -> tint strength, so the wave edge reads
k_rng.inputs[1].default_value, k_rng.inputs[2].default_value = 0.05, 0.85
k_rng.inputs[3].default_value, k_rng.inputs[4].default_value = 0.0, 0.60
bsdf, out = n.new("ShaderNodeBsdfPrincipled"), n.new("ShaderNodeOutputMaterial")
bsdf.inputs["Roughness"].default_value = 0.8
bsdf.inputs["Specular IOR Level"].default_value = 0.15
l.new(sh.outputs["Fac"], cr.inputs[0])
l.new(kv.outputs["Fac"], k_rng.inputs[0])
l.new(k_rng.outputs[0], tint.inputs["Factor"])
l.new(cr.outputs[0], tint.inputs["A"])
l.new(tint.outputs["Result"], bsdf.inputs["Base Color"])
finish_with_edge_fade(n, l, bsdf.outputs[0], out)
ocean.data.materials.append(m)

# ---------------------------------------------------------------- Kelvin wave path (points carrying arclength 's')
# waypoints (lon, lat): along the equator from the west, hit the Sumatra shelf, turn north along
# the coast (kept offshore of the Barisan coast), round Banda Aceh, then east to Phuket.
KTN, KLK = facts["stations.ktn_latlon"]["value"], facts["stations.klk_latlon"]["value"]
way = [(30, 0), (60, 0), (95, 0), (96.8, 1.5), (95.2, 3.8), (94.6, 6.3), (96.5, 7.5), (98.0, KTN[0])]
wx, wy = xy([p[0] for p in way], [p[1] for p in way])
seg = np.hypot(np.diff(wx), np.diff(wy))
cum = np.concatenate([[0], np.cumsum(seg)])
s_at_60E = cum[1]
dense = np.arange(0, cum[-1], 0.1)
px, py = np.interp(dense, cum, wx), np.interp(dense, cum, wy)
s_vals = dense - s_at_60E                                 # s = 0 at 60E on the equator
S_95 = cum[2] - s_at_60E                                  # s where the head is at 95E  (progress 0.6)
S_END = cum[-1] - s_at_60E                                # s at Phuket                 (progress 1.0)
pm = bpy.data.meshes.new("FX_kelvin_path")
pm.vertices.add(len(dense))
pm.vertices.foreach_set("co", np.stack([px, py, np.zeros_like(px)], -1).astype(np.float32).ravel())
pa = pm.attributes.new("s", 'FLOAT', 'POINT'); pa.data.foreach_set("value", s_vals.astype(np.float32))
path_obj = link(bpy.data.objects.new("FX_kelvin_path", pm))
path_obj.hide_render = True; path_obj.hide_viewport = True

# the empty that carries the user-facing controls
fx = link(bpy.data.objects.new("FX_kelvin", None))
fx.empty_display_type = 'ARROWS'
fx["progress"] = 0.0           # 0 = head at 60E | 0.6 = 95E | 1.0 = at Phuket
fx["amplitude"] = KELVIN_AMP   # dip depth in Blender units (exaggerated!)
fx["note"] = "progress 0..1; amplitude is EXAGGERATED height, see build_geo.py header"

# ---------------------------------------------------------------- Kelvin geometry nodes (on the ocean)
ng = bpy.data.node_groups.new("FX_kelvin_nodes", "GeometryNodeTree")
ng.interface.new_socket("Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
ng.interface.new_socket("Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')
ng.interface.new_socket("progress", in_out='INPUT', socket_type='NodeSocketFloat')
ng.interface.new_socket("amplitude", in_out='INPUT', socket_type='NodeSocketFloat')
N = ng.nodes
gin, gout = N.new("NodeGroupInput"), N.new("NodeGroupOutput")


def nd(kind, **props):
    x = N.new(kind)
    for k, v in props.items():
        setattr(x, k, v)
    return x


def math_(op, a=None, b=None, c=None, **kw):
    x = nd("ShaderNodeMath", operation=op, **kw)
    for i, v in enumerate((a, b, c)):
        if v is None:
            continue
        if isinstance(v, (int, float)):
            x.inputs[i].default_value = v
        else:
            ng.links.new(v, x.inputs[i])
    return x.outputs[0]


# head position along the path: s_head = map(progress,0..0.6 -> 0..S_95) + map(progress,0.6..1 -> 0..S_END-S_95)
def map_range(value, a, b, c, d):
    x = nd("ShaderNodeMapRange", clamp=True)
    ng.links.new(value, x.inputs[0])
    for i, v in enumerate((a, b, c, d), start=1):
        x.inputs[i].default_value = v
    return x.outputs[0]


prog = gin.outputs["progress"]
s_head = math_('ADD', map_range(prog, 0, 0.6, 0, S_95), map_range(prog, 0.6, 1.0, 0, S_END - S_95))

pinfo = nd("GeometryNodeObjectInfo", transform_space='ORIGINAL'); pinfo.inputs[0].default_value = path_obj
pos = nd("GeometryNodeInputPosition")
near = nd("GeometryNodeSampleNearest", domain='POINT')
ng.links.new(pinfo.outputs["Geometry"], near.inputs["Geometry"])
ng.links.new(pos.outputs[0], near.inputs["Sample Position"])
s_attr = nd("GeometryNodeInputNamedAttribute", data_type='FLOAT'); s_attr.inputs["Name"].default_value = "s"
s_at = nd("GeometryNodeSampleIndex", data_type='FLOAT', domain='POINT')
ng.links.new(pinfo.outputs["Geometry"], s_at.inputs["Geometry"])
ng.links.new(s_attr.outputs[0], s_at.inputs["Value"]); ng.links.new(near.outputs[0], s_at.inputs["Index"])
p_at = nd("GeometryNodeSampleIndex", data_type='FLOAT_VECTOR', domain='POINT')
ng.links.new(pinfo.outputs["Geometry"], p_at.inputs["Geometry"])
ng.links.new(pos.outputs[0], p_at.inputs["Value"]); ng.links.new(near.outputs[0], p_at.inputs["Index"])
dist = nd("ShaderNodeVectorMath", operation='DISTANCE')
ng.links.new(pos.outputs[0], dist.inputs[0]); ng.links.new(p_at.outputs[0], dist.inputs[1])

u = math_('SUBTRACT', s_at.outputs[0], s_head)                  # distance behind(+)/ahead(-) of the head along the path
ex_a = math_('DIVIDE', math_('MULTIPLY', u, u), 2 * KELVIN_SIGMA_ALONG ** 2)
d = dist.outputs["Value"]
ex_c = math_('DIVIDE', math_('MULTIPLY', d, d), 2 * KELVIN_SIGMA_ACROSS ** 2)
w = math_('EXPONENT', math_('MULTIPLY', math_('ADD', ex_a, ex_c), -1.0))   # Gaussian 0..1
dz = math_('MULTIPLY', math_('MULTIPLY', w, gin.outputs["amplitude"]), -1.0)
vec = nd("ShaderNodeCombineXYZ"); ng.links.new(dz, vec.inputs["Z"])
setp = nd("GeometryNodeSetPosition")
ng.links.new(gin.outputs["Geometry"], setp.inputs["Geometry"]); ng.links.new(vec.outputs[0], setp.inputs["Offset"])
store = nd("GeometryNodeStoreNamedAttribute", data_type='FLOAT', domain='POINT')
store.inputs["Name"].default_value = "kelvin"
ng.links.new(setp.outputs[0], store.inputs["Geometry"]); ng.links.new(w, store.inputs["Value"])
ng.links.new(store.outputs[0], gout.inputs[0])

mod = ocean.modifiers.new("FX_kelvin", 'NODES')
mod.node_group = ng
idents = {it.name: it.identifier for it in ng.interface.items_tree if getattr(it, "in_out", "") == 'INPUT'}
# (Blender 5.2: modifier inputs live under .properties.inputs.<identifier>.value)
# drive both inputs from the FX_kelvin empty's custom properties -> one place to animate
for prop in ("progress", "amplitude"):
    fc = ocean.driver_add(f'modifiers["FX_kelvin"].properties.inputs.{idents[prop]}.value')
    var = fc.driver.variables.new(); var.name = "v"; var.type = 'SINGLE_PROP'
    var.targets[0].id = fx; var.targets[0].data_path = f'["{prop}"]'
    fc.driver.expression = "v"

# ---------------------------------------------------------------- coastlines (two thicknesses: far and near cameras)
coast = json.loads((GEO / "coastlines.json").read_text())
coast_mat = emission_mat("MAT_coast", hex_lin("#E4F1FA"), 2.0)


def coast_curve(name, runs, width):
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '3D'; cu.bevel_depth = width; cu.bevel_resolution = 1
    for run in runs:
        a = np.asarray(run)
        x, y = xy(a[:, 0], a[:, 1])
        sp = cu.splines.new('POLY'); sp.points.add(len(a) - 1)
        sp.points.foreach_set("co", np.stack([x, y, np.full_like(x, 0.04), np.ones_like(x)], -1).ravel())
    cu.materials.append(coast_mat)
    return link(bpy.data.objects.new(name, cu))


c_wide = coast_curve("GEO_coastline_wide", coast["wide"], 0.07)     # ~2 px at the SQ08 camera
c_close = coast_curve("GEO_coastline_close", coast["close"], 0.014)  # ~2 px at the SQ01 camera
c_close.hide_render = True                                          # render_sample.py switches the pair per camera

# ---------------------------------------------------------------- station markers
def marker(name, latlon, hexcol):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, segments=32, ring_count=16)
    o = bpy.context.active_object
    o.name = name
    for c in o.users_collection:
        c.objects.unlink(o)
    link(o)
    x, y = xy(latlon[1], latlon[0])
    o.location = (float(x), float(y), 0.05)
    o.scale = (0.12,) * 3                                    # render_sample.py rescales per camera
    o["base_radius"] = 0.12
    o.data.materials.append(emission_mat("MAT_" + name, hex_lin(hexcol), 1.6))
    bpy.ops.object.shade_smooth()
    return o


marker("GEO_station_ktn", KTN, ANDAMAN)
marker("GEO_station_klk", KLK, GULF)

# ---------------------------------------------------------------- cameras
def camera(name, loc, target, lens, **props):
    cd = bpy.data.cameras.new(name)
    cd.lens, cd.clip_start, cd.clip_end = lens, 0.1, 500
    o = link(bpy.data.objects.new(name, cd))
    o.location = loc
    # aim: camera looks down its -Z axis with +Y up
    o.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    for k, v in props.items():
        o[k] = v
    return o


cx, _ = xy(99.2, 0)
CAM_WIDE = camera("CAM_SQ08_wide", (0, -62, 70), (0, 4, 0), 36, coast_set="wide", marker_scale=4.0)
CAM_PEN = camera("CAM_SQ01_peninsula", (float(cx) - 1.5, -2.5, 10), (float(cx) + 0.2, 9.5, 0), 40, coast_set="close", marker_scale=1.4)
scene.camera = CAM_WIDE

# ---------------------------------------------------------------- lights + world
sun = bpy.data.lights.new("LGT_sun", 'SUN'); sun.energy, sun.angle = 3.5, math.radians(3)
sun_o = link(bpy.data.objects.new("LGT_sun", sun))
# low sun from the north-west so relief and the Kelvin dip catch light and shadow
sun_o.rotation_euler = (math.radians(50), math.radians(10), math.radians(150))
fill = bpy.data.lights.new("LGT_fill", 'SUN'); fill.energy = 0.6
fill_o = link(bpy.data.objects.new("LGT_fill", fill))
fill_o.rotation_euler = (math.radians(35), 0, math.radians(-30))

world = bpy.data.worlds.new("WORLD_bg"); world.use_nodes = True
bg = world.node_tree.nodes["Background"]
bg.inputs["Color"].default_value = BG_WORLD_LINEAR
bg.inputs["Strength"].default_value = 1.0   # keep 1.0: the edge-fade emission matches it exactly
scene.world = world

# ---------------------------------------------------------------- render settings
r = scene.render
engines = {e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items}
r.engine = "BLENDER_EEVEE" if "BLENDER_EEVEE" in engines else "BLENDER_EEVEE_NEXT"
r.resolution_x, r.resolution_y, r.resolution_percentage, r.fps = 1920, 1080, 100, 30
scene.view_settings.view_transform = 'AgX'
try:
    scene.view_settings.look = 'AgX - Medium High Contrast'   # a bit more punch for the projector
except TypeError:
    scene.view_settings.look = 'None'
scene.eevee.taa_render_samples = 64
r.image_settings.file_format = 'PNG'

OUT.parent.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT), compress=True)
print("saved", OUT, "S_95=%.2f S_END=%.2f" % (S_95, S_END))
