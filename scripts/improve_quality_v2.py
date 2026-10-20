"""Quality v2: modelhouse match for Living / Kitchen-Dining / Master.

Idempotent: Q2_* objects and materials are rebuilt on each run.
Run: blender --background apt_84a_photoreal_tour.blend --python scripts/improve_quality_v2.py
Saves back to apt_84a_photoreal_tour.blend (backup *_before_quality_v2.blend).
"""
import bpy
import os
import math
from mathutils import Vector

ROOT = r"C:\Users\tamarand\orca\projects\apt"
TEX = os.path.join(ROOT, "assets", "textures")

def srgb(hexstr):
    h = hexstr.lstrip('#')
    vals = []
    for i in (0, 2, 4):
        c = int(h[i:i+2], 16) / 255.0
        vals.append(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
    return tuple(vals)

def load_img(path, srgb_flag):
    ap = os.path.abspath(path)
    for im in bpy.data.images:
        if im.filepath and os.path.abspath(bpy.path.abspath(im.filepath)) == ap:
            im.colorspace_settings.name = "sRGB" if srgb_flag else "Non-Color"
            return im
    im = bpy.data.images.load(ap, check_existing=True)
    im.colorspace_settings.name = "sRGB" if srgb_flag else "Non-Color"
    return im

def find_maps(aid):
    d = os.path.join(TEX, aid)
    files = os.listdir(d)
    def one(*keys):
        for f in files:
            if all(k in f.lower() for k in keys):
                return os.path.join(d, f)
        return None
    return one("diff") or one("col"), one("nor"), one("rough"), one("ao")

def build_pbr(mat_name, aid, span, flat=None, value=1.0, rough_mul=1.0,
              normal_strength=0.6, ao_fac=0.3, sheen=0.0, spec=0.5, rough_flat=None):
    mat = bpy.data.materials.get(mat_name) or bpy.data.materials.new(mat_name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    nodes, links = nt.nodes, nt.links
    diff_p, nor_p, rough_p, ao_p = find_maps(aid) if aid else (None, None, None, None)
    tex = nodes.new("ShaderNodeTexCoord"); tex.location = (-900, 0)
    mapping = nodes.new("ShaderNodeMapping"); mapping.location = (-700, 0)
    s = 1.0 / span
    mapping.inputs["Scale"].default_value = (s, s, s)
    links.new(tex.outputs["Object"], mapping.inputs["Vector"])
    def img_node(path, is_srgb, y):
        n = nodes.new("ShaderNodeTexImage")
        n.location = (-450, y)
        n.image = load_img(path, is_srgb)
        n.projection = "BOX"; n.projection_blend = 0.15
        links.new(mapping.outputs["Vector"], n.inputs["Vector"])
        return n
    out = nodes.new("ShaderNodeOutputMaterial"); out.location = (500, 0)
    bsdf = nodes.new("ShaderNodeBsdfPrincipled"); bsdf.location = (200, 0)
    bsdf.inputs["Metallic"].default_value = 0.0
    bsdf.inputs["Specular IOR Level"].default_value = spec
    if sheen > 0:
        bsdf.inputs["Sheen Weight"].default_value = sheen
        bsdf.inputs["Sheen Tint"].default_value = (1.0, 0.97, 0.93, 1.0)
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    if flat is not None:
        rgb = nodes.new("ShaderNodeRGB"); rgb.location = (-450, 300)
        c = srgb(flat)
        rgb.outputs["Color"].default_value = (c[0], c[1], c[2], 1.0)
        cur = rgb.outputs["Color"]
    else:
        cur = img_node(diff_p, True, 300).outputs["Color"]
        if abs(value - 1.0) > 1e-6:
            hs = nodes.new("ShaderNodeHueSaturation"); hs.location = (-150, 300)
            hs.inputs["Value"].default_value = value
            links.new(cur, hs.inputs["Color"]); cur = hs.outputs["Color"]
    ao_src = rough_src = None
    if ao_p and ao_fac > 0:
        ao_src = img_node(ao_p, False, -250).outputs["Color"]
    if rough_p:
        rough_src = img_node(rough_p, False, -100).outputs["Color"]
    if ao_src is not None:
        mx = nodes.new("ShaderNodeMixRGB"); mx.location = (0, 150)
        mx.blend_type = "MULTIPLY"; mx.inputs["Fac"].default_value = ao_fac
        links.new(cur, mx.inputs["Color1"]); links.new(ao_src, mx.inputs["Color2"])
        cur = mx.outputs["Color"]
    links.new(cur, bsdf.inputs["Base Color"])
    if rough_src is not None:
        if abs(rough_mul - 1.0) > 1e-6:
            m = nodes.new("ShaderNodeMath"); m.location = (0, -100)
            m.operation = "MULTIPLY"; m.inputs[1].default_value = rough_mul; m.use_clamp = True
            links.new(rough_src, m.inputs[0]); links.new(m.outputs["Value"], bsdf.inputs["Roughness"])
        else:
            links.new(rough_src, bsdf.inputs["Roughness"])
    elif rough_flat is not None:
        bsdf.inputs["Roughness"].default_value = rough_flat
    if nor_p:
        nimg = img_node(nor_p, False, -400)
        sep = nodes.new("ShaderNodeSeparateColor"); sep.location = (-150, -400)
        links.new(nimg.outputs["Color"], sep.inputs["Color"])
        inv = nodes.new("ShaderNodeInvert"); inv.location = (-150, -550)
        links.new(sep.outputs["Green"], inv.inputs["Color"])
        comb = nodes.new("ShaderNodeCombineColor"); comb.location = (0, -450)
        links.new(sep.outputs["Red"], comb.inputs["Red"])
        links.new(inv.outputs["Color"], comb.inputs["Green"])
        links.new(sep.outputs["Blue"], comb.inputs["Blue"])
        nmap = nodes.new("ShaderNodeNormalMap"); nmap.location = (0, -300)
        nmap.inputs["Strength"].default_value = normal_strength
        links.new(comb.outputs["Color"], nmap.inputs["Color"])
        links.new(nmap.outputs["Normal"], bsdf.inputs["Normal"])
    print(f"[Q2-PBR] {mat_name} <- {aid} flat={flat}")
    return mat

def flat_mat(name, hexcol, rough=0.6, metallic=0.0, sheen=0.0):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree; nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    c = srgb(hexcol)
    bsdf.inputs["Base Color"].default_value = (c[0], c[1], c[2], 1.0)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metallic
    if sheen > 0:
        bsdf.inputs["Sheen Weight"].default_value = sheen
        bsdf.inputs["Sheen Tint"].default_value = (1.0, 0.97, 0.93, 1.0)
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat

def build_artwall():
    mat = bpy.data.materials.get("Mat_ArtWall_Tile") or bpy.data.materials.new("Mat_ArtWall_Tile")
    mat.use_nodes = True
    nt = mat.node_tree; nt.nodes.clear()
    nodes, links = nt.nodes, nt.links
    diff_p, nor_p, rough_p, ao_p = find_maps("marble_01")
    tex = nodes.new("ShaderNodeTexCoord"); tex.location = (-900, 0)
    map_m = nodes.new("ShaderNodeMapping"); map_m.location = (-700, 200)
    map_m.inputs["Scale"].default_value = (0.5, 0.5, 0.5)
    links.new(tex.outputs["Object"], map_m.inputs["Vector"])
    map_g = nodes.new("ShaderNodeMapping"); map_g.location = (-700, -300)
    links.new(tex.outputs["Object"], map_g.inputs["Vector"])
    def mimg(path, is_srgb, y):
        n = nodes.new("ShaderNodeTexImage"); n.location = (-450, y)
        n.image = load_img(path, is_srgb)
        n.projection = "BOX"; n.projection_blend = 0.15
        links.new(map_m.outputs["Vector"], n.inputs["Vector"])
        return n
    brick = nodes.new("ShaderNodeTexBrick"); brick.location = (-450, -300)
    brick.offset = 0.0
    brick.inputs["Scale"].default_value = 1.6667
    brick.inputs["Brick Width"].default_value = 1.0
    brick.inputs["Row Height"].default_value = 1.0
    brick.inputs["Mortar Size"].default_value = 0.006
    brick.inputs["Mortar Smooth"].default_value = 0.001
    links.new(map_g.outputs["Vector"], brick.inputs["Vector"])
    mcol = mimg(diff_p, True, 300).outputs["Color"]
    hs = nodes.new("ShaderNodeHueSaturation"); hs.location = (-150, 300)
    hs.inputs["Value"].default_value = 1.02; hs.inputs["Saturation"].default_value = 0.8
    links.new(mcol, hs.inputs["Color"])
    mix = nodes.new("ShaderNodeMixRGB"); mix.location = (0, 200)
    mix.blend_type = "MIX"
    g = srgb("#B9B4AA"); mix.inputs["Color2"].default_value = (g[0], g[1], g[2], 1.0)
    links.new(hs.outputs["Color"], mix.inputs["Color1"])
    links.new(brick.outputs["Fac"], mix.inputs["Fac"])
    out = nodes.new("ShaderNodeOutputMaterial"); out.location = (500, 0)
    bsdf = nodes.new("ShaderNodeBsdfPrincipled"); bsdf.location = (200, 0)
    bsdf.inputs["Specular IOR Level"].default_value = 0.5
    links.new(mix.outputs["Color"], bsdf.inputs["Base Color"])
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    if rough_p:
        rimg = mimg(rough_p, False, -100)
        m = nodes.new("ShaderNodeMath"); m.location = (0, -100)
        m.operation = "MULTIPLY"; m.inputs[1].default_value = 0.45; m.use_clamp = True
        links.new(rimg.outputs["Color"], m.inputs[0])
        links.new(m.outputs["Value"], bsdf.inputs["Roughness"])
    print("[Q2-PBR] Mat_ArtWall_Tile <- marble_01 + grout")
    return mat

# ---------- geometry helpers ----------
def clean_q2():
    for o in list(bpy.data.objects):
        if o.name.startswith("Q2_"):
            bpy.data.objects.remove(o, do_unlink=True)
    print("[Q2] cleaned previous Q2 objects")

def _link(obj, mat):
    if mat is not None:
        if obj.data and hasattr(obj.data, "materials"):
            obj.data.materials.clear()
            obj.data.materials.append(mat)
    return obj

def box(name, loc, dims, mat=None, bevel=0.0, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(location=loc, rotation=rot)
    o = bpy.context.active_object; o.name = name
    o.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel > 0:
        mod = o.modifiers.new("Q2Bevel", 'BEVEL'); mod.width = bevel; mod.segments = 3
    _link(o, mat)
    return o

def cyl(name, loc, radius, depth, mat=None, rot=(0, 0, 0), scale_y=1.0, vertices=32):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc, rotation=rot)
    o = bpy.context.active_object; o.name = name
    o.scale.y = scale_y
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    _link(o, mat)
    return o

def cone(name, loc, r1, r2, depth, mat=None, vertices=32):
    bpy.ops.mesh.primitive_cone_add(vertices=vertices, radius1=r1, radius2=r2, depth=depth, location=loc)
    o = bpy.context.active_object; o.name = name
    _link(o, mat)
    return o

def sphere(name, loc, radius, mat=None, scale=(1, 1, 1)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=loc, segments=24, ring_count=16)
    o = bpy.context.active_object; o.name = name
    o.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    _link(o, mat)
    return o

def assign(obj_name, mat):
    o = bpy.data.objects.get(obj_name)
    if o and o.type == 'MESH' and mat is not None:
        o.data.materials.clear(); o.data.materials.append(mat)
    return o

def add_bevel(obj_name, width=0.03):
    o = bpy.data.objects.get(obj_name)
    if o and not any(m.type == 'BEVEL' for m in o.modifiers):
        mod = o.modifiers.new("Q2Bevel", 'BEVEL'); mod.width = width; mod.segments = 3
    return o

def plant(name, loc, pot_mat, leaf_mat, scale=1.0):
    cone(name + "_Pot", loc, 0.09 * scale, 0.07 * scale, 0.22 * scale, pot_mat)
    cyl(name + "_Stem", (loc[0], loc[1], loc[2] + 0.22 * scale), 0.008, 0.3 * scale, leaf_mat)
    top = loc[2] + 0.42 * scale
    for i, (dx, dy, dz, s) in enumerate([(0, 0, 0.08, 0.11), (0.07, 0.03, 0.03, 0.09),
                                         (-0.06, -0.04, 0.04, 0.09), (0.02, -0.07, 0.0, 0.08),
                                         (-0.03, 0.06, 0.0, 0.08)]):
        sphere(f"{name}_Leaf{i}", (loc[0] + dx * scale, loc[1] + dy * scale, top + dz * scale),
               s * scale, leaf_mat, scale=(1.2, 1.0, 0.7))

def book_stack(name, loc, mats, rot_z=0.0):
    z = loc[2]
    for i, (w, d, h, m) in enumerate([(0.24, 0.17, 0.025, mats[0]), (0.21, 0.15, 0.02, mats[1]),
                                      (0.18, 0.13, 0.018, mats[2 % len(mats)])]):
        box(f"{name}_{i}", (loc[0], loc[1], z + h / 2), (w, d, h), m, bevel=0.004,
            rot=(0, 0, rot_z + i * 0.18))
        z += h

def landscape_image():
    import numpy as np
    name = "Q2_Landscape"
    if name in bpy.data.images:
        return bpy.data.images[name]
    W, H = 1024, 512
    y = np.linspace(0, 1, H)[:, None]
    x = np.linspace(0, 1, W)[None, :]
    # sky top -> horizon, then tree band, then green field bottom
    sky = np.zeros((H, W, 3))
    sky[:, :, 0] = 0.62 + 0.25 * (1 - y[:, :, 0] if False else 1)
    img = np.zeros((H, W, 4), dtype=np.float32)
    # build per-row colors (row 0 = bottom in Blender image space)
    for r in range(H):
        t = r / H  # 0 bottom(field) -> 1 top(sky)
        if t < 0.38:
            k = t / 0.38
            col = (0.36 + 0.10 * k, 0.48 + 0.08 * k, 0.26 + 0.05 * k)  # field green
        elif t < 0.46:
            col = (0.24, 0.33, 0.20)  # tree line
        else:
            k = (t - 0.46) / 0.54
            col = (0.78 - 0.18 * k, 0.86 - 0.10 * k, 0.95 - 0.02 * k)  # sky
        img[r, :, 0] = col[0]; img[r, :, 1] = col[1]; img[r, :, 2] = col[2]; img[r, :, 3] = 1.0
    # soft cloud blobs in sky rows
    import random
    rnd = random.Random(84)
    for _ in range(26):
        cx, cy = rnd.uniform(0, W), rnd.uniform(H * 0.62, H * 0.95)
        rx, ry = rnd.uniform(60, 170), rnd.uniform(10, 26)
        x0, x1 = max(0, int(cx - rx)), min(W, int(cx + rx))
        y0, y1 = max(0, int(cy - ry)), min(H, int(cy + ry))
        for rr in range(y0, y1):
            for cc in range(x0, x1):
                d = ((cc - cx) / rx) ** 2 + ((rr - cy) / ry) ** 2
                if d < 1:
                    a = 0.20 * (1 - d)
                    img[rr, cc, 0] = img[rr, cc, 0] * (1 - a) + 1.0 * a
                    img[rr, cc, 1] = img[rr, cc, 1] * (1 - a) + 1.0 * a
                    img[rr, cc, 2] = img[rr, cc, 2] * (1 - a) + 1.0 * a
    im = bpy.data.images.new(name, W, H, alpha=False)
    im.pixels = img.ravel().tolist()
    im.update()
    return im

def landscape_mat():
    mat = bpy.data.materials.get("Mat_Q2_Landscape") or bpy.data.materials.new("Mat_Q2_Landscape")
    mat.use_nodes = True
    nt = mat.node_tree; nt.nodes.clear()
    tex = nt.nodes.new("ShaderNodeTexImage"); tex.image = landscape_image()
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Roughness"].default_value = 1.0
    emis = nt.nodes.new("ShaderNodeEmission")
    emis.inputs["Strength"].default_value = 0.55
    add = nt.nodes.new("ShaderNodeAddShader")
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    nt.links.new(tex.outputs["Color"], emis.inputs["Color"])
    nt.links.new(bsdf.outputs["BSDF"], add.inputs[0])
    nt.links.new(emis.outputs["Emission"], add.inputs[1])
    nt.links.new(add.outputs["Shader"], out.inputs["Surface"])
    return mat

def fix_lighting_and_render():
    sc = bpy.context.scene
    # legacy default light (1000W point) washes every POV: disable
    legacy = bpy.data.objects.get("Light")
    if legacy:
        legacy.hide_render = True; legacy.hide_viewport = True
        legacy.data.energy = 0
        print("[Q2-LIGHT] disabled legacy Light 1000W")
    # single sun only
    dup = bpy.data.objects.get("Light_Sun")
    if dup:
        dup.hide_render = True
        print("[Q2-LIGHT] disabled duplicate Light_Sun")
    sun = bpy.data.objects.get("Sun_Natural")
    if sun:
        sun.data.energy = 3.0
        sun.data.angle = 1.5
        sun.data.use_shadow = True
        print("[Q2-LIGHT] Sun_Natural energy=3.0 angle=1.5")
    scale = {"Light_Living_Warm": 35, "Light_Master_Warm": 28}
    for o in bpy.data.objects:
        if o.type != 'LIGHT' or o.name in ("Sun_Natural", "Light_Sun", "Light"):
            continue
        if o.name in scale:
            o.data.energy = scale[o.name]
        elif o.data.type == 'POINT':
            o.data.energy = max(4.0, o.data.energy * 0.55)
        if hasattr(o.data, "shadow_soft_size"):
            o.data.shadow_soft_size = 0.18
    # emissive strips: keep glow but avoid blowout
    for mname, strength in [("Mat_Light_Warm_Strip", 3.2), ("Mat_LED_Warm", 3.2), ("Mat_Bulb_Warm", 2.6)]:
        m = bpy.data.materials.get(mname)
        if m and m.use_nodes:
            for n in m.node_tree.nodes:
                if n.type == 'EMISSION':
                    n.inputs["Strength"].default_value = strength
    # world: dimmer light-ray fill, camera sky stays bright
    w = sc.world
    if w and w.use_nodes:
        for n in w.node_tree.nodes:
            if n.type == 'MAP_RANGE':
                n.inputs["To Min"].default_value = 0.40
                n.inputs["To Max"].default_value = 0.65
    # colour management: AgX (fallback Filmic)
    try:
        sc.view_settings.view_transform = 'AgX'
    except Exception:
        sc.view_settings.view_transform = 'Filmic'
    try:
        sc.view_settings.look = 'Medium High Contrast'
    except Exception:
        pass
    sc.view_settings.exposure = 0.0
    sc.view_settings.gamma = 1.0
    # cycles quality
    sc.render.engine = 'CYCLES'
    sc.cycles.use_denoising = True
    try:
        sc.cycles.denoiser = 'OPTIX'
    except Exception:
        sc.cycles.denoiser = 'OPENIMAGEDENOISE'
    sc.cycles.diffuse_bounces = 6
    sc.cycles.glossy_bounces = 6
    sc.cycles.transmission_bounces = 4
    sc.cycles.transparent_max_bounces = 8
    sc.cycles.caustics_reflective = False
    sc.cycles.caustics_refractive = False
    sc.cycles.blur_glossy = 0.5
    try:
        sc.cycles.use_light_tree = True
    except Exception:
        pass
    print("[Q2-LIGHT] AgX + cycles bounces set")

def build_materials():
    build_pbr("Mat_Wall_Interior", "beige_wall_001", 2.5, value=1.06, normal_strength=0.35, ao_fac=0.22)
    build_pbr("Mat_Wall_Cap", "beige_wall_001", 2.5, value=1.04, normal_strength=0.35, ao_fac=0.22)
    build_artwall()
    build_pbr("Mat_Marble_White", "marble_01", 1.6, value=1.03, rough_mul=0.45, normal_strength=0.35, ao_fac=0.25, spec=0.55)
    build_pbr("Mat_Countertop_Granite", "marble_01", 1.2, value=1.0, rough_mul=0.4, normal_strength=0.35, ao_fac=0.25, spec=0.55)
    build_pbr("Mat_Tile_Grey", "floor_tiles_06", 1.2, value=1.12, rough_mul=0.8, normal_strength=0.7)
    build_pbr("Mat_BathTile_Wall", "floor_tiles_06", 1.2, value=1.12, rough_mul=0.55, normal_strength=0.6)
    build_pbr("Mat_Wood_LightPlank", "laminate_floor_02", 3.0, rough_mul=0.7, normal_strength=0.65, spec=0.5)
    build_pbr("Mat_Wood_WarmPlank", "laminate_floor_03", 3.0, rough_mul=0.7, normal_strength=0.65, spec=0.5)
    build_pbr("Mat_Fabric_Sofa", "fabric_pattern_07", 0.7, flat="#CFC8BC", sheen=0.6, normal_strength=0.7, ao_fac=0.3)
    build_pbr("Mat_Bed_Linen", "fabric_pattern_07", 1.1, flat="#F2EFE9", sheen=0.5, normal_strength=0.45, ao_fac=0.2)
    build_pbr("Mat_Curtain", "fabric_pattern_07", 1.4, flat="#C9C2B4", sheen=0.7, normal_strength=0.5, ao_fac=0.3)
    build_pbr("Mat_Chair_Fabric", "fabric_pattern_07", 0.6, flat="#B8AFA0", sheen=0.5, normal_strength=0.6, ao_fac=0.3)
    build_pbr("Mat_Cabinet_Cashmere", "white_plaster_02", 2.0, flat="#E3DDD2", normal_strength=0.25, ao_fac=0.15, rough_flat=0.42)
    build_pbr("Mat_Ceiling_Plaster", "white_plaster_02", 3.0, flat="#F4F2ED", normal_strength=0.3, ao_fac=0.1, rough_flat=0.9)
    mats = {}
    mats['oled'] = flat_mat("Mat_Screen_OLED", "#050607", rough=0.06, metallic=0.1)
    mats['blackglass'] = flat_mat("Mat_Q2_BlackGlass", "#0A0C0E", rough=0.08, metallic=0.2)
    mats['blackmetal'] = flat_mat("Mat_Q2_BlackMetal", "#1C1E20", rough=0.35, metallic=0.8)
    mats['brass'] = flat_mat("Mat_Q2_Brass", "#C9A86A", rough=0.3, metallic=1.0)
    mats['cork'] = flat_mat("Mat_Q2_Cork", "#C8A87E", rough=0.85, sheen=0.2)
    mats['ceramic'] = flat_mat("Mat_Ceramic_White", "#F5F3EF", rough=0.12)
    mats['leaf'] = flat_mat("Mat_Q2_Foliage", "#4A6741", rough=0.95, sheen=0.3)
    mats['rug'] = build_pbr("Mat_Q2_Rug", "fabric_pattern_07", 1.6, flat="#C4B2AC", sheen=0.4, normal_strength=0.5, ao_fac=0.25)
    mats['terra'] = flat_mat("Mat_Q2_Terracotta", "#B96F4E", rough=0.9, sheen=0.3)
    mats['slate'] = flat_mat("Mat_Q2_Slate", "#7A8694", rough=0.9, sheen=0.3)
    mats['cream'] = flat_mat("Mat_Q2_CreamFabric", "#E6DDCE", rough=0.9, sheen=0.5)
    mats['boucle'] = build_pbr("Mat_Q2_Boucle", "fabric_pattern_07", 0.8, flat="#D3C6B2", sheen=0.65, normal_strength=0.7, ao_fac=0.3)
    mats['panel'] = build_pbr("Mat_Q2_WallPanel", "fabric_pattern_07", 1.8, flat="#DAD2C2", sheen=0.4, normal_strength=0.4, ao_fac=0.2)
    mats['lilac'] = build_pbr("Mat_Q2_Lilac", "fabric_pattern_07", 1.0, flat="#A79BC0", sheen=0.5, normal_strength=0.5, ao_fac=0.25)
    mats['sage'] = flat_mat("Mat_Q2_Sage", "#9AA88F", rough=0.9, sheen=0.5)
    mats['plum'] = flat_mat("Mat_Q2_Plum", "#6E5A6E", rough=0.9, sheen=0.5)
    mats['slateblue'] = flat_mat("Mat_Q2_SlateBlue", "#7E93A8", rough=0.9, sheen=0.5)
    mats['lime'] = flat_mat("Mat_Q2_Lime", "#CBD08A", rough=0.9, sheen=0.5)
    mats['paleblue'] = flat_mat("Mat_Q2_PaleBlue", "#B9CBD6", rough=0.9, sheen=0.5)
    mats['placemat'] = build_pbr("Mat_Q2_Placemat", "fabric_pattern_07", 0.5, flat="#D9CFC2", sheen=0.3, normal_strength=0.6, ao_fac=0.2)
    # sheer curtain (alpha)
    sheer = flat_mat("Mat_Q2_Sheer", "#F1ECE2", rough=0.9, sheen=0.6)
    bsdf = [n for n in sheer.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'][0]
    bsdf.inputs["Alpha"].default_value = 0.45
    sheer.surface_render_method = 'DITHERED'
    mats['sheer'] = sheer
    print("[Q2-MAT] materials built")
    return mats

def build_exterior(mats):
    lm = landscape_mat()
    black = mats['blackmetal']
    bpy.ops.mesh.primitive_plane_add(size=2, location=(6.6, -2.6, 1.35), rotation=(-math.pi / 2, 0, 0))
    o = bpy.context.active_object; o.name = "Q2_Landscape_South"; o.dimensions = (17.0, 3.4, 0)
    _link(o, lm)
    bpy.ops.mesh.primitive_plane_add(size=2, location=(6.2, 12.4, 1.35), rotation=(-math.pi / 2, 0, math.pi))
    o = bpy.context.active_object; o.name = "Q2_Landscape_North"; o.dimensions = (14.0, 3.4, 0)
    _link(o, lm)
    # living balcony railing (south windows y=0.38)
    cyl("Q2_Rail_Living_Top", (6.65, 0.14, 1.04), 0.018, 3.7, black, rot=(0, math.pi / 2, 0))
    cyl("Q2_Rail_Living_Bot", (6.65, 0.14, 0.28), 0.014, 3.7, black, rot=(0, math.pi / 2, 0))
    for i in range(14):
        cyl(f"Q2_Rail_Living_B{i}", (4.95 + i * 0.262, 0.14, 0.66), 0.007, 0.78, black, vertices=10)
    # master balcony railing (door y=1.77, floor edge y~0.5)
    cyl("Q2_Rail_Master_Top", (3.08, 0.48, 1.04), 0.018, 1.7, black, rot=(0, math.pi / 2, 0))
    cyl("Q2_Rail_Master_Bot", (3.08, 0.48, 0.28), 0.014, 1.7, black, rot=(0, math.pi / 2, 0))
    for i in range(7):
        cyl(f"Q2_Rail_Master_B{i}", (2.32 + i * 0.253, 0.48, 0.66), 0.007, 0.78, black, vertices=10)
    print("[Q2-EXT] landscape + railings")

def build_living(m):
    marble = bpy.data.materials["Mat_Marble_White"]
    # rug + abstract inlays (modelhouse mauve rug)
    box("Q2_Living_Rug", (6.50, 3.00, 0.012), (3.30, 2.55, 0.024), m['rug'], bevel=0.01)
    cyl("Q2_Rug_ShapeA", (5.95, 2.42, 0.028), 0.34, 0.006, m['terra'], scale_y=0.6)
    cyl("Q2_Rug_ShapeB", (7.05, 3.62, 0.028), 0.28, 0.006, m['slate'], scale_y=0.55)
    box("Q2_Rug_ShapeC", (6.55, 3.05, 0.028), (0.70, 0.16, 0.006), m['cream'], bevel=0.003, rot=(0, 0, 0.5))
    # round marble coffee table + decor
    cyl("Q2_Coffee_Top", (6.45, 3.00, 0.40), 0.52, 0.035, marble)
    cyl("Q2_Coffee_Base", (6.45, 3.00, 0.19), 0.27, 0.38, m['ceramic'])
    book_stack("Q2_CoffeeBooks", (6.30, 2.80, 0.42),
               [bpy.data.materials["Mat_Book_Charcoal"], bpy.data.materials["Mat_Book_Cream"],
                bpy.data.materials["Mat_Book_Sage"]], rot_z=0.3)
    plant("Q2_CoffeePlant", (6.68, 3.28, 0.42), m['ceramic'], m['leaf'], scale=0.75)
    # cork poufs near window (modelhouse stools)
    for i, yy in enumerate((2.02, 4.02)):
        cyl(f"Q2_Pouf{i}", (5.62, yy, 0.20), 0.18, 0.40, m['cork'])
        bpy.ops.mesh.primitive_torus_add(major_radius=0.18, minor_radius=0.012,
                                         location=(5.62, yy, 0.30), rotation=(0, 0, 0))
        t = bpy.context.active_object; t.name = f"Q2_Pouf{i}_Rope"; _link(t, m['terra'])
    # sofa throw cushions in modelhouse colours (S->N: slate, lime, plum, cream, pale)
    cols = [m['slateblue'], m['lime'], m['plum'], m['cream'], m['paleblue']]
    for i, (yy, cm) in enumerate(zip((2.18, 2.52, 2.95, 3.38, 3.82), cols)):
        box(f"Q2_SofaCushion{i}", (8.58, yy, 0.66), (0.17, 0.40, 0.40), cm, bevel=0.06,
            rot=(0, -0.28, 0.06 if i % 2 else -0.05))
    for n in ("Sofa_Living_ArmL", "Sofa_Living_ArmR", "Sofa_Living_BackBar",
              "Sofa_Living_BackCushion_1", "Sofa_Living_BackCushion_2", "Sofa_Living_BackCushion_3",
              "Sofa_Living_Seat_1", "Sofa_Living_Seat_2", "Sofa_Living_Seat_3", "Sofa_Living_Base"):
        add_bevel(n, 0.025)
    # TV wall: black frame + tuned OLED, console decor
    assign("Living_TV_OLED_Frame", m['blackmetal'])
    assign("Living_TV_OLED_Screen", m['oled'])
    plant("Q2_ConsolePlant", (4.58, 2.02, 0.46), m['ceramic'], m['leaf'], scale=0.6)
    cyl("Q2_ConsoleBasket", (4.58, 4.05, 0.53), 0.09, 0.14, m['cork'])
    book_stack("Q2_ConsoleBooks", (4.58, 4.32, 0.46),
               [bpy.data.materials["Mat_Book_Navy"], bpy.data.materials["Mat_Book_Cream"],
                bpy.data.materials["Mat_Book_Charcoal"]], rot_z=-0.2)
    # sheer curtains inside living windows
    box("Q2_Sheer_LivingL", (5.60, 0.46, 1.15), (0.80, 0.02, 2.26), m['sheer'])
    box("Q2_Sheer_LivingR", (7.70, 0.46, 1.15), (0.80, 0.02, 2.26), m['sheer'])
    # wall sconce glow by TV wall north end
    sphere("Q2_SconceBulb", (4.52, 4.62, 1.88), 0.035, bpy.data.materials.get("Mat_Bulb_Warm"))
    bpy.ops.object.light_add(type='POINT', location=(4.68, 4.55, 1.85))
    li = bpy.context.active_object; li.name = "Q2_SconceLight"
    li.data.energy = 5; li.data.color = (1.0, 0.90, 0.78)
    li.data.use_custom_distance = True; li.data.cutoff_distance = 2.5
    print("[Q2-LIVING] done")

def build_kitchen(m):
    marble = bpy.data.materials["Mat_Marble_White"]
    chrome = bpy.data.materials.get("Mat_Chrome_Metal")
    steel = bpy.data.materials.get("Mat_Steel_Brushed")
    for o in bpy.data.objects:
        if o.name.startswith("Kitchen_Faucet_"):
            _link(o, chrome)
    assign("Kitchen_Induction_Glass", m['blackglass'])
    assign("ProK_Oven_DoorGlass", m['blackglass'])
    # dining rug
    box("Q2_Dining_Rug", (6.85, 6.70, 0.010), (1.90, 1.75, 0.020), m['cream'], bevel=0.008)
    # pot on induction (east run x=7.50)
    cyl("Q2_PotBody", (7.50, 8.85, 0.96), 0.115, 0.11, steel)
    cyl("Q2_PotLid", (7.50, 8.85, 1.025), 0.10, 0.018, steel)
    sphere("Q2_PotKnob", (7.50, 8.85, 1.05), 0.022, m['blackmetal'])
    # kettle + board + basket + sink plant
    cone("Q2_Kettle", (7.35, 7.90, 0.955), 0.075, 0.055, 0.13, steel)
    walnut = bpy.data.materials.get("Mat_Wood_Walnut")
    box("Q2_CutBoard", (6.85, 9.60, 0.905), (0.34, 0.22, 0.018), walnut, bevel=0.006, rot=(0, 0, 0.25))
    cyl("Q2_PenBasket", (7.48, 8.30, 0.945), 0.11, 0.09, m['cork'])
    for i, (dx, dy, cm) in enumerate([(0, 0, m['terra']), (0.07, 0.04, m['sage']), (-0.06, 0.05, m['lime'])]):
        sphere(f"Q2_Fruit{i}", (7.48 + dx, 8.30 + dy, 1.01), 0.032, cm)
    plant("Q2_SinkPlant", (5.48, 9.78, 0.90), m['ceramic'], m['leaf'], scale=0.5)
    # dining: woven placemats, chair legs to black metal, vase foliage
    for o in bpy.data.objects:
        if o.name.startswith("Dining_Mat_"):
            _link(o, m['placemat'])
        if o.name.startswith("Chair_") and ("_Leg" in o.name or "_Post" in o.name):
            _link(o, m['blackmetal'])
        if o.name.startswith("Dining_Vase_Flora"):
            _link(o, m['leaf'])
    assign("Dining_Vase_Base", m['ceramic'])
    print("[Q2-KITCHEN] done")

def build_master(m):
    marble = bpy.data.materials["Mat_Marble_White"]
    cabinet = bpy.data.materials["Mat_Cabinet_Cashmere"]
    led = bpy.data.materials.get("Mat_Light_Warm_Strip")
    # upholstered wall panel + cove strips behind headboard (west wall x~0.8)
    box("Q2_Master_Panel", (0.74, 3.10, 1.28), (0.04, 3.00, 2.30), m['panel'], bevel=0.01)
    box("Q2_Master_CoveTop", (0.79, 3.10, 2.26), (0.025, 2.86, 0.025), led)
    box("Q2_Master_CoveLow", (0.79, 3.10, 0.50), (0.025, 2.86, 0.025), led)
    assign("Bed_Master_Headboard", m['boucle']); add_bevel("Bed_Master_Headboard", 0.05)
    assign("Bed_Master_Base", m['boucle'])
    add_bevel("Bed_Master_Pillow1", 0.06); add_bevel("Bed_Master_Pillow2", 0.06)
    add_bevel("Bed_Master_Duvet", 0.02)
    assign("Bed_Master_Runner", m['lilac'])
    # lavender throw across foot + accent cushions
    box("Q2_Master_Throw", (2.58, 3.10, 0.655), (0.50, 2.02, 0.07), m['lilac'], bevel=0.03)
    box("Q2_Master_CushionS", (1.44, 2.60, 0.70), (0.16, 0.46, 0.34), m['sage'], bevel=0.06, rot=(0, 0.30, 0.05))
    box("Q2_Master_CushionN", (1.44, 3.60, 0.70), (0.16, 0.46, 0.34), m['plum'], bevel=0.06, rot=(0, 0.30, -0.05))
    # bed rug (visible at sides/foot)
    box("Q2_Master_Rug", (2.05, 3.10, 0.011), (2.90, 2.85, 0.022), m['cream'], bevel=0.01)
    # nightstands: cream existing (north) + new oval south, marble tops
    assign("Nightstand_Master_Cab", cabinet)
    assign("Nightstand_Master_LampShade", m['cream'])
    cyl("Q2_NightTopN", (1.85, 4.35, 0.495), 0.26, 0.03, marble, scale_y=1.15)
    cyl("Q2_NightSouth", (1.85, 1.82, 0.24), 0.26, 0.48, cabinet, scale_y=1.15)
    cyl("Q2_NightTopS", (1.85, 1.82, 0.495), 0.27, 0.03, marble, scale_y=1.15)
    plant("Q2_NightPlantS", (1.85, 1.82, 0.51), m['ceramic'], m['leaf'], scale=0.5)
    # twin pendants over nightstands (modelhouse hanging lights)
    bulb = bpy.data.materials.get("Mat_Bulb_Warm")
    for tag, yy in (("S", 1.82), ("N", 4.38)):
        cyl(f"Q2_Pendant{tag}_Cord", (1.85, yy, 1.93), 0.006, 0.74, m['blackmetal'], vertices=10)
        cone(f"Q2_Pendant{tag}_Shade", (1.85, yy, 1.52), 0.11, 0.045, 0.10, m['cream'])
        sphere(f"Q2_Pendant{tag}_Bulb", (1.85, yy, 1.45), 0.032, bulb)
        bpy.ops.object.light_add(type='POINT', location=(1.85, yy, 1.42))
        li = bpy.context.active_object; li.name = f"Q2_PendantLight{tag}"
        li.data.energy = 6; li.data.color = (1.0, 0.92, 0.80)
        li.data.use_custom_distance = True; li.data.cutoff_distance = 3.0
    # sheer at balcony door
    box("Q2_Sheer_MasterL", (2.67, 1.84, 1.15), (0.68, 0.02, 2.20), m['sheer'])
    box("Q2_Sheer_MasterR", (3.48, 1.84, 1.15), (0.68, 0.02, 2.20), m['sheer'])
    print("[Q2-MASTER] done")

def main():
    clean_q2()
    fix_lighting_and_render()
    mats = build_materials()
    build_exterior(mats)
    build_living(mats)
    build_kitchen(mats)
    build_master(mats)
    # cameras: keep framing, just tighten near clip
    for n in ("Cam_Living_POV", "Cam_Kitchen_POV", "Cam_MasterBed_POV"):
        c = bpy.data.objects.get(n)
        if c:
            c.data.clip_start = 0.05
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT, "apt_84a_photoreal_tour.blend"))
    print("[Q2] SAVED apt_84a_photoreal_tour.blend")

if __name__ == "__main__":
    main()




