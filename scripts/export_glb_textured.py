"""Export web GLB WITH PBR image textures (non-destructive).

Blender's Object/Box mapping doesn't transfer to glTF, so this:
1. Bakes adjusted texture copies (desat/value/tint/rough-mul/DX->GL/grid)
   to assets/textures_export/ at max 1K JPEG.
2. Adds world-unit cube-projection UVs ("ExportUV") on target-material faces.
3. Builds exporter-friendly materials (UVMap+Mapping->KHR_texture_transform).
4. Exports house.glb, then RELOADS the saved blend (PBR setup restored).
Run inside Blender.
"""
import bpy
import os
import numpy as np

TEX_SRC = r"C:\Users\tamarand\orca\projects\apt\assets\textures"
TEX_EXP = r"C:\Users\tamarand\orca\projects\apt\assets\textures_export"
os.makedirs(TEX_EXP, exist_ok=True)
LUM = np.array([0.2126, 0.7152, 0.0722], np.float32)


def src_pixels(aid, kind):
    """Load source map pixels (copy, max 1024px). kind: diff|nor|rough|rough_ao."""
    d = os.path.join(TEX_SRC, aid)
    want = {"diff": ("diff", "col"), "nor": ("nor",),
            "rough": ("rough",), "rough_ao": ("rough_ao",)}[kind]
    for f in sorted(os.listdir(d)):
        fl = f.lower()
        if fl.endswith(".jpg") and any(k in fl for k in want):
            if kind == "rough" and "rough_ao" in fl:
                continue
            im0 = bpy.data.images.load(os.path.join(d, f), check_existing=True)
            im = im0.copy()
            w, h = im.size
            if max(w, h) > 1024:
                s = 1024 / max(w, h)
                im.scale(int(w * s), int(h * s))
                w, h = im.size
            arr = np.empty((h, w, 4), np.float32)
            im.pixels.foreach_get(arr.ravel())
            bpy.data.images.remove(im)
            return arr, w, h
    raise RuntimeError(f"no {kind} map in {aid}")


def save_pixels(arr, name):
    h, w, _ = arr.shape
    im = bpy.data.images.new("tmp_exp", w, h, alpha=True)
    im.pixels.foreach_set(np.clip(arr, 0, 1).ravel())
    path = os.path.join(TEX_EXP, name)
    im.filepath_raw = path
    im.file_format = 'JPEG'
    im.save()
    bpy.data.images.remove(im)
    print(f"[GLBTEX] {name} {w}x{h}")
    return path


def adjust_diff(arr, desat=1.0, value=1.0, tint=(1, 1, 1)):
    rgb = arr[..., :3].copy()
    if desat < 1.0:
        lum = rgb @ LUM
        rgb = lum[..., None] + (rgb - lum[..., None]) * desat
    rgb = rgb * value * np.array(tint, np.float32)
    out = arr.copy()
    out[..., :3] = np.clip(rgb, 0, 1)
    return out


def flip_g(arr):
    out = arr.copy()
    out[..., 1] = 1.0 - out[..., 1]
    return out


def ch_g(arr, mul=1.0):
    out = np.ones_like(arr)
    out[..., :3] = arr[..., 1:2] * mul
    return out


def gray_mul(arr, mul):
    out = arr.copy()
    out[..., :3] = np.clip(arr[..., :3] * mul, 0, 1)
    return out


def add_grid(arr, tiles=4, lw=2, color=(0.78, 0.77, 0.75)):
    h, w, _ = arr.shape
    step = w / tiles
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    gx = np.minimum(xx % step, step - xx % step) < lw
    gy = np.minimum(yy % step, step - yy % step) < lw
    out = arr.copy()
    out[gx | gy, :3] = np.array(color, np.float32)
    return out


# ---------------- prep textures ----------------
P = {}  # key -> filepath
A, _, _ = src_pixels("beige_wall_001", "diff")
P["wall_diff"] = save_pixels(adjust_diff(A, 0.5, 1.65, (1.0, 0.99, 0.97)), "wall_diff.jpg")
P["wall_cap_diff"] = save_pixels(adjust_diff(A, 0.5, 1.6, (1.0, 0.99, 0.97)), "wall_cap_diff.jpg")
A, _, _ = src_pixels("beige_wall_001", "nor")
P["wall_nor"] = save_pixels(flip_g(A), "wall_nor.jpg")
A, _, _ = src_pixels("beige_wall_001", "rough")
P["wall_rough"] = save_pixels(A, "wall_rough.jpg")

A, _, _ = src_pixels("white_plaster_02", "nor")
P["plaster_nor"] = save_pixels(flip_g(A), "plaster_nor.jpg")
A, _, _ = src_pixels("white_plaster_02", "rough_ao")
P["plaster_rough"] = save_pixels(ch_g(A), "plaster_rough.jpg")

A, _, _ = src_pixels("laminate_floor_02", "diff")
P["lam02_diff"] = save_pixels(A, "lam02_diff.jpg")
A, _, _ = src_pixels("laminate_floor_02", "nor")
P["lam02_nor"] = save_pixels(flip_g(A), "lam02_nor.jpg")
A, _, _ = src_pixels("laminate_floor_02", "rough")
P["lam02_rough"] = save_pixels(gray_mul(A, 0.75), "lam02_rough.jpg")

A, _, _ = src_pixels("laminate_floor_03", "diff")
P["lam03_diff"] = save_pixels(A, "lam03_diff.jpg")
A, _, _ = src_pixels("laminate_floor_03", "nor")
P["lam03_nor"] = save_pixels(flip_g(A), "lam03_nor.jpg")
A, _, _ = src_pixels("laminate_floor_03", "rough")
P["lam03_rough"] = save_pixels(gray_mul(A, 0.75), "lam03_rough.jpg")

A, _, _ = src_pixels("floor_tiles_06", "diff")
P["t06_diff"] = save_pixels(adjust_diff(A, 0.7, 1.45), "t06_diff.jpg")
P["t06w_diff"] = save_pixels(adjust_diff(A, 0.7, 1.5, (0.98, 0.99, 1.0)), "t06w_diff.jpg")
A, _, _ = src_pixels("floor_tiles_06", "nor")
P["t06_nor"] = save_pixels(flip_g(A), "t06_nor.jpg")
A, _, _ = src_pixels("floor_tiles_06", "rough")
P["t06_rough"] = save_pixels(gray_mul(A, 0.8), "t06_rough.jpg")
P["t06w_rough"] = save_pixels(gray_mul(A, 0.55), "t06w_rough.jpg")

A, _, _ = src_pixels("floor_tiles_02", "diff")
P["t02_diff"] = save_pixels(A, "t02_diff.jpg")
A, _, _ = src_pixels("floor_tiles_02", "nor")
P["t02_nor"] = save_pixels(flip_g(A), "t02_nor.jpg")
A, _, _ = src_pixels("floor_tiles_02", "rough_ao")
P["t02_rough"] = save_pixels(ch_g(A, 0.7), "t02_rough.jpg")

A, _, _ = src_pixels("fabric_pattern_07", "nor")
P["fab_nor"] = save_pixels(flip_g(A), "fab_nor.jpg")
A, _, _ = src_pixels("fabric_pattern_07", "rough")
P["fab_rough"] = save_pixels(A, "fab_rough.jpg")
A, _, _ = src_pixels("fabric_pattern_07", "diff")
P["curtain_diff"] = save_pixels(
    adjust_diff(A, 0.10, 1.60, (0.95, 0.93, 0.89)), "curtain_diff.jpg")

A, _, _ = src_pixels("marble_01", "diff")
P["marble_diff"] = save_pixels(adjust_diff(A, 1.0, 1.12), "marble_diff.jpg")
P["artwall_diff"] = save_pixels(
    add_grid(adjust_diff(A, 0.85, 1.08)), "artwall_diff.jpg")
A, _, _ = src_pixels("marble_01", "nor")
P["marble_nor"] = save_pixels(flip_g(A), "marble_nor.jpg")
A, _, _ = src_pixels("marble_01", "rough")
P["marble_rough"] = save_pixels(gray_mul(A, 0.5), "marble_rough.jpg")

# ---------------- export material specs ----------------
# name: (span, diff_key|None, flat_rgb|None, nor_key, rough_key, normal_strength)
SPEC = {
    "Mat_Wall_Interior": (2.5, "wall_diff", None, "wall_nor", "wall_rough", 0.4),
    "Mat_Wall_Cap": (2.5, "wall_cap_diff", None, "wall_nor", "wall_rough", 0.4),
    "Mat_Ceiling_Plaster": (3.0, None, (0.93, 0.92, 0.90), "plaster_nor", "plaster_rough", 0.5),
    "Mat_Wood_LightPlank": (3.0, "lam02_diff", None, "lam02_nor", "lam02_rough", 0.7),
    "Mat_Wood_WarmPlank": (3.0, "lam03_diff", None, "lam03_nor", "lam03_rough", 0.7),
    "Mat_Tile_Grey": (1.2, "t06_diff", None, "t06_nor", "t06_rough", 0.8),
    "Mat_Tile_DarkSlate": (1.2, "t02_diff", None, "t02_nor", "t02_rough", 0.7),
    "Mat_BathTile_Wall": (1.2, "t06w_diff", None, "t06_nor", "t06w_rough", 0.7),
    "Mat_Fabric_Sofa": (0.8, None, (0.72, 0.70, 0.67), "fab_nor", "fab_rough", 0.8),
    "Mat_Bed_Linen": (1.2, None, (0.96, 0.95, 0.93), "fab_nor", "fab_rough", 0.5),
    "Mat_BedSheet": (1.2, None, (0.96, 0.95, 0.93), "fab_nor", "fab_rough", 0.5),
    "Mat_Pillow": (0.6, None, (0.95, 0.94, 0.92), "fab_nor", "fab_rough", 0.6),
    "Mat_Bed_Runner": (1.0, None, (0.87, 0.82, 0.70), "fab_nor", "fab_rough", 0.5),
    "Mat_Curtain": (1.5, "curtain_diff", None, "fab_nor", "fab_rough", 0.5),
    "Mat_ArtWall_Tile": (2.4, "artwall_diff", None, "marble_nor", "marble_rough", 0.5),
    "Mat_Marble_White": (2.0, "marble_diff", None, "marble_nor", "marble_rough", 0.4),
}
TARGETS = set(SPEC)

# ---------------- cube-projection UVs ----------------
import bmesh
from mathutils import Vector

n_uv = 0
for o in bpy.data.objects:
    if o.type != "MESH" or o.data is None:
        continue
    slots = [s.name if s else None for s in o.data.materials]
    if not any(s in TARGETS for s in slots):
        continue
    me = o.data
    if me.users > 1:
        o.data = me.copy()
        me = o.data
        slots = [s.name if s else None for s in me.materials]
    mw = o.matrix_world
    rot = mw.to_3x3()
    bm = bmesh.new()
    bm.from_mesh(me)
    uv_layer = bm.loops.layers.uv.get("ExportUV") or bm.loops.layers.uv.new("ExportUV")
    for f in bm.faces:
        if f.material_index >= len(slots) or slots[f.material_index] not in TARGETS:
            continue
        wn = (rot @ f.normal).normalized()
        ax = 0 if abs(wn.x) >= abs(wn.y) and abs(wn.x) >= abs(wn.z) else (
             1 if abs(wn.y) >= abs(wn.z) else 2)
        for loop in f.loops:
            wp = mw @ loop.vert.co
            loop[uv_layer].uv = (wp.y, wp.z) if ax == 0 else (
                (wp.x, wp.z) if ax == 1 else (wp.x, wp.y))
        n_uv += 1
    bm.to_mesh(me)
    bm.free()
print(f"[GLBTEX] cube UVs on {n_uv} faces")


def load_img(path, srgb):
    for im in bpy.data.images:
        if im.filepath and os.path.abspath(bpy.path.abspath(im.filepath)) == os.path.abspath(path):
            im.colorspace_settings.name = "sRGB" if srgb else "Non-Color"
            return im
    im = bpy.data.images.load(path, check_existing=True)
    im.colorspace_settings.name = "sRGB" if srgb else "Non-Color"
    return im


for name, (span, dk, flat, nk, rk, nstr) in SPEC.items():
    m = bpy.data.materials.get(name)
    if m is None:
        print(f"[GLBTEX] missing {name}")
        continue
    m.use_nodes = True
    m.node_tree.nodes.clear()
    nodes, links = m.node_tree.nodes, m.node_tree.links
    uv = nodes.new("ShaderNodeUVMap")
    uv.uv_map = "ExportUV"
    mp = nodes.new("ShaderNodeMapping")
    s = 1.0 / span
    mp.inputs["Scale"].default_value = (s, s, 1.0)
    links.new(uv.outputs["UV"], mp.inputs["Vector"])
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Metallic"].default_value = 0.0
    if dk is None:
        bsdf.inputs["Base Color"].default_value = (flat[0], flat[1], flat[2], 1.0)
    else:
        di = nodes.new("ShaderNodeTexImage")
        di.image = load_img(P[dk], True)
        links.new(mp.outputs["Vector"], di.inputs["Vector"])
        links.new(di.outputs["Color"], bsdf.inputs["Base Color"])
    ni = nodes.new("ShaderNodeTexImage")
    ni.image = load_img(P[nk], False)
    links.new(mp.outputs["Vector"], ni.inputs["Vector"])
    nm = nodes.new("ShaderNodeNormalMap")
    nm.inputs["Strength"].default_value = nstr
    links.new(ni.outputs["Color"], nm.inputs["Color"])
    links.new(nm.outputs["Normal"], bsdf.inputs["Normal"])
    ri = nodes.new("ShaderNodeTexImage")
    ri.image = load_img(P[rk], False)
    links.new(mp.outputs["Vector"], ri.inputs["Vector"])
    links.new(ri.outputs["Color"], bsdf.inputs["Roughness"])
    out = nodes.new("ShaderNodeOutputMaterial")
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
print("[GLBTEX] export materials built")

# ---------------- export + restore ----------------
saved = bpy.data.filepath
assert saved and os.path.exists(saved)
out_path = os.path.join(os.path.dirname(saved), "web", "public", "house.glb")
hidden = []
for o in bpy.data.objects:
    if o.type in ('LIGHT', 'CAMERA'):
        hidden.append(o)
        o.hide_viewport = True
        o.hide_render = True
bpy.ops.export_scene.gltf(filepath=out_path, export_format='GLB',
                          use_selection=False, export_apply=True)
print(f"[GLBTEX] exported {os.path.getsize(out_path) / 1024 / 1024:.2f} MB")
bpy.ops.wm.open_mainfile(filepath=saved)
print("[GLBTEX] reloaded saved blend (PBR restored)")
