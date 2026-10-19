"""Wire downloaded Polyhaven PBR sets into photoreal materials (idempotent).

- Splits ceiling into its own plaster material (was sharing Mat_Wall_Interior).
- Rebuilds target material node trees with Object+Box-projected image PBR.
- Assigns tile material to bathroom-facing wall faces only (per-face).
- Sets daylight HDRI world.
Run inside Blender (sent via mcp daemon).
"""
import bpy
import os

TEX = r"C:\Users\tamarand\orca\projects\apt\assets\textures"

BATH_RECTS = [
    (13.45, 5.75, 14.95, 7.55),   # common bath
    (2.72, 5.85, 4.18, 7.95),     # master bath
]


def load_img(path, srgb):
    path = os.path.abspath(path)
    for im in bpy.data.images:
        if im.filepath and os.path.abspath(bpy.path.abspath(im.filepath)) == path:
            im.colorspace_settings.name = "sRGB" if srgb else "Non-Color"
            return im
    im = bpy.data.images.load(path, check_existing=True)
    im.colorspace_settings.name = "sRGB" if srgb else "Non-Color"
    return im


def find_maps(aid):
    d = os.path.join(TEX, aid)
    files = os.listdir(d)
    def one(*keys):
        for f in files:
            fl = f.lower()
            if all(k in fl for k in keys):
                return os.path.join(d, f)
        return None
    diff = one("diff") or one("col")
    nor = one("nor")
    rough = one("rough")
    ao = one("ao")
    combined = rough is not None and ao is not None and rough == ao
    return diff, nor, rough, ao, combined


def build_pbr(mat_name, aid, span, tint=(1, 1, 1), desat=1.0, value=1.0,
             rough_mul=1.0, normal_strength=1.0, sheen=0.0,
             ao_fac=0.6, spec=0.5, flat=None):
    mat = bpy.data.materials.get(mat_name)
    if mat is None:
        mat = bpy.data.materials.new(mat_name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    nodes, links = nt.nodes, nt.links

    diff_p, nor_p, rough_p, ao_p, combined = find_maps(aid)
    if diff_p is None and flat is None:
        print(f"[PBR] {mat_name}: MISSING diff for {aid}")
        return None

    tex = nodes.new("ShaderNodeTexCoord")
    tex.location = (-900, 0)
    mapping = nodes.new("ShaderNodeMapping")
    mapping.location = (-700, 0)
    s = 1.0 / span
    mapping.inputs["Scale"].default_value = (s, s, s)
    links.new(tex.outputs["Object"], mapping.inputs["Vector"])

    def img_node(path, srgb, y):
        n = nodes.new("ShaderNodeTexImage")
        n.location = (-450, y)
        n.image = load_img(path, srgb)
        n.projection = "BOX"
        n.projection_blend = 0.15
        n.interpolation = "Linear"
        links.new(mapping.outputs["Vector"], n.inputs["Vector"])
        return n

    out = nodes.new("ShaderNodeOutputMaterial")
    out.location = (500, 0)
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (200, 0)
    bsdf.inputs["Metallic"].default_value = 0.0
    bsdf.inputs["Specular IOR Level"].default_value = spec
    if sheen > 0:
        bsdf.inputs["Sheen Weight"].default_value = sheen
        bsdf.inputs["Sheen Tint"].default_value = (1.0, 0.97, 0.93, 1.0)
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    # --- base color chain ---
    if flat is not None:
        rgb = nodes.new("ShaderNodeRGB")
        rgb.location = (-450, 300)
        rgb.outputs["Color"].default_value = (flat[0], flat[1], flat[2], 1.0)
        cur = rgb.outputs["Color"]
    else:
        cur = img_node(diff_p, True, 300).outputs["Color"]
    if desat < 1.0 or abs(value - 1.0) > 1e-6:
        hs = nodes.new("ShaderNodeHueSaturation")
        hs.location = (-150, 300)
        hs.inputs["Saturation"].default_value = desat
        hs.inputs["Value"].default_value = value
        links.new(cur, hs.inputs["Color"])
        cur = hs.outputs["Color"]
    if tint != (1, 1, 1):
        mx = nodes.new("ShaderNodeMixRGB")
        mx.location = (0, 300)
        mx.blend_type = "MULTIPLY"
        mx.inputs["Fac"].default_value = 1.0
        mx.inputs["Color2"].default_value = (tint[0], tint[1], tint[2], 1.0)
        links.new(cur, mx.inputs["Color1"])
        cur = mx.outputs["Color"]
    ao_src = None
    rough_src = None
    if combined and rough_p:
        sep = nodes.new("ShaderNodeSeparateColor")
        sep.location = (-150, -100)
        rimg = img_node(rough_p, False, -100)
        links.new(rimg.outputs["Color"], sep.inputs["Color"])
        ao_src = sep.outputs["Red"]
        rough_src = sep.outputs["Green"]
    else:
        if ao_p and ao_fac > 0:
            ao_src = img_node(ao_p, False, -250).outputs["Color"]
        if rough_p:
            rough_src = img_node(rough_p, False, -100).outputs["Color"]
    if ao_src is not None and ao_fac > 0:
        mx = nodes.new("ShaderNodeMixRGB")
        mx.location = (0, 150)
        mx.blend_type = "MULTIPLY"
        mx.inputs["Fac"].default_value = ao_fac
        links.new(cur, mx.inputs["Color1"])
        links.new(ao_src, mx.inputs["Color2"])
        cur = mx.outputs["Color"]
    links.new(cur, bsdf.inputs["Base Color"])

    # --- roughness ---
    if rough_src is not None:
        if abs(rough_mul - 1.0) > 1e-6:
            m = nodes.new("ShaderNodeMath")
            m.location = (0, -100)
            m.operation = "MULTIPLY"
            m.inputs[1].default_value = rough_mul
            m.use_clamp = True
            links.new(rough_src, m.inputs[0])
            links.new(m.outputs["Value"], bsdf.inputs["Roughness"])
        else:
            links.new(rough_src, bsdf.inputs["Roughness"])

    # --- normal (DirectX -> OpenGL green flip) ---
    if nor_p:
        nimg = img_node(nor_p, False, -400)
        sep = nodes.new("ShaderNodeSeparateColor")
        sep.location = (-150, -400)
        links.new(nimg.outputs["Color"], sep.inputs["Color"])
        inv = nodes.new("ShaderNodeInvert")
        inv.location = (-150, -550)
        links.new(sep.outputs["Green"], inv.inputs["Color"])
        comb = nodes.new("ShaderNodeCombineColor")
        comb.location = (0, -450)
        links.new(sep.outputs["Red"], comb.inputs["Red"])
        links.new(inv.outputs["Color"], comb.inputs["Green"])
        links.new(sep.outputs["Blue"], comb.inputs["Blue"])
        nmap = nodes.new("ShaderNodeNormalMap")
        nmap.location = (0, -300)
        nmap.inputs["Strength"].default_value = normal_strength
        links.new(comb.outputs["Color"], nmap.inputs["Color"])
        links.new(nmap.outputs["Normal"], bsdf.inputs["Normal"])

    print(f"[PBR] wired {mat_name} <- {aid} span={span}")
    return mat


def assign_ceiling():
    mat = build_pbr("Mat_Ceiling_Plaster", "white_plaster_02", 3.0,
                    rough_mul=1.0, normal_strength=0.5, ao_fac=0.15,
                    flat=(0.93, 0.92, 0.90))
    if mat is None:
        return
    for o in bpy.data.objects:
        if o.type != "MESH" or o.data is None:
            continue
        if o.name == "Ceiling_Slab" or o.name.startswith("Cove_Living_Trim"):
            for i, slot in enumerate(o.data.materials):
                if slot is not None and slot.name == "Mat_Wall_Interior":
                    o.data.materials[i] = mat
            print(f"[PBR] ceiling material -> {o.name}")


def assign_bath_faces(tile_mat_name="Mat_BathTile_Wall"):
    tile = bpy.data.materials.get(tile_mat_name)
    assert tile is not None, "bath tile material missing"
    import math
    targets = [o for o in bpy.data.objects
               if o.type == "MESH" and o.data is not None
               and (o.name.startswith("ExactWall") or o.name.startswith("NewWall")
                    or o.name.startswith("SillPatch"))]
    for o in targets:
        me = o.data
        idx = None
        for i, slot in enumerate(me.materials):
            if slot is not None and slot.name == tile_mat_name:
                idx = i
                break
        if idx is None:
            me.materials.append(tile)
            idx = len(me.materials) - 1
        n = 0
        mw = o.matrix_world
        rot = mw.to_3x3()
        for p in me.polygons:
            if abs(p.normal.z) > 0.6:
                continue
            c = mw @ p.center
            wn = (rot @ p.normal).normalized()
            ex, ey = c.x + wn.x * 0.3, c.y + wn.y * 0.3
            for (x0, y0, x1, y1) in BATH_RECTS:
                in_loose = (x0 - 0.12 <= c.x <= x1 + 0.12
                            and y0 - 0.12 <= c.y <= y1 + 0.12)
                end_tight = (x0 < ex < x1 and y0 < ey < y1)
                if in_loose and end_tight:
                    p.material_index = idx
                    n += 1
                    break
        if n:
            print(f"[PBR] bath faces -> {o.name}: {n}")


def set_hdri():
    import glob
    cands = glob.glob(os.path.join(TEX, "*", "*.hdr"))
    if not cands:
        print("[PBR] no HDRI found")
        return
    hp = cands[0]
    w = bpy.context.scene.world
    w.use_nodes = True
    nt = w.node_tree
    nt.nodes.clear()
    nodes, links = nt.nodes, nt.links
    tex = nodes.new("ShaderNodeTexCoord")
    tex.location = (-600, 0)
    mp = nodes.new("ShaderNodeMapping")
    mp.location = (-400, 0)
    mp.inputs["Rotation"].default_value = (0, 0, 0.6)
    links.new(tex.outputs["Generated"], mp.inputs["Vector"])
    env = nodes.new("ShaderNodeTexEnvironment")
    env.location = (-200, 0)
    env.image = load_img(hp, True)
    links.new(mp.outputs["Vector"], env.inputs["Vector"])
    # camera rays: bright HDRI sky; light rays: flat dim fill (no sun-disc nuke)
    lp = nodes.new("ShaderNodeLightPath")
    lp.location = (-200, -200)
    mr = nodes.new("ShaderNodeMapRange")
    mr.location = (0, -200)
    mr.inputs["From Min"].default_value = 0.0
    mr.inputs["From Max"].default_value = 1.0
    mr.inputs["To Min"].default_value = 0.6
    mr.inputs["To Max"].default_value = 0.85
    links.new(lp.outputs["Is Camera Ray"], mr.inputs["Value"])
    mx = nodes.new("ShaderNodeMixRGB")
    mx.location = (-200, -350)
    mx.blend_type = "MIX"
    mx.inputs["Color1"].default_value = (0.45, 0.48, 0.52, 1.0)
    links.new(env.outputs["Color"], mx.inputs["Color2"])
    links.new(lp.outputs["Is Camera Ray"], mx.inputs["Fac"])
    bg = nodes.new("ShaderNodeBackground")
    bg.location = (0, 0)
    links.new(mr.outputs["Result"], bg.inputs["Strength"])
    links.new(mx.outputs["Color"], bg.inputs["Color"])
    out = nodes.new("ShaderNodeOutputWorld")
    out.location = (200, 0)
    links.new(bg.outputs["Background"], out.inputs["Surface"])
    print(f"[PBR] HDRI world <- {os.path.basename(hp)}")


def build_artwall():
    """Large-format ivory porcelain: white marble face + 600mm grout grid."""
    mat_name = "Mat_ArtWall_Tile"
    mat = bpy.data.materials.get(mat_name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    nodes, links = nt.nodes, nt.links
    diff_p, nor_p, rough_p, ao_p, _ = find_maps("marble_01")

    tex = nodes.new("ShaderNodeTexCoord")
    tex.location = (-900, 0)
    map_m = nodes.new("ShaderNodeMapping")  # marble span 2m
    map_m.location = (-700, 200)
    map_m.inputs["Scale"].default_value = (0.5, 0.5, 0.5)
    links.new(tex.outputs["Object"], map_m.inputs["Vector"])
    map_g = nodes.new("ShaderNodeMapping")  # grout in meters
    map_g.location = (-700, -300)
    links.new(tex.outputs["Object"], map_g.inputs["Vector"])

    def mimg(path, srgb, y):
        n = nodes.new("ShaderNodeTexImage")
        n.location = (-450, y)
        n.image = load_img(path, srgb)
        n.projection = "BOX"
        n.projection_blend = 0.15
        links.new(map_m.outputs["Vector"], n.inputs["Vector"])
        return n

    brick = nodes.new("ShaderNodeTexBrick")
    brick.location = (-450, -300)
    brick.offset = 0.0
    brick.inputs["Scale"].default_value = 1.6667
    brick.inputs["Brick Width"].default_value = 1.0
    brick.inputs["Row Height"].default_value = 1.0
    brick.inputs["Mortar Size"].default_value = 0.005
    brick.inputs["Mortar Smooth"].default_value = 0.001
    links.new(map_g.outputs["Vector"], brick.inputs["Vector"])

    mcol = mimg(diff_p, True, 300).outputs["Color"]
    hs = nodes.new("ShaderNodeHueSaturation")
    hs.location = (-150, 300)
    hs.inputs["Value"].default_value = 1.08
    hs.inputs["Saturation"].default_value = 0.85
    links.new(mcol, hs.inputs["Color"])
    mix = nodes.new("ShaderNodeMixRGB")
    mix.location = (0, 200)
    mix.blend_type = "MIX"
    mix.inputs["Color2"].default_value = (0.78, 0.77, 0.75, 1.0)  # grout
    links.new(hs.outputs["Color"], mix.inputs["Color1"])
    links.new(brick.outputs["Fac"], mix.inputs["Fac"])

    out = nodes.new("ShaderNodeOutputMaterial")
    out.location = (500, 0)
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (200, 0)
    bsdf.inputs["Metallic"].default_value = 0.0
    bsdf.inputs["Specular IOR Level"].default_value = 0.5
    links.new(mix.outputs["Color"], bsdf.inputs["Base Color"])
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    if rough_p:
        rimg = mimg(rough_p, False, -100)
        m = nodes.new("ShaderNodeMath")
        m.location = (0, -100)
        m.operation = "MULTIPLY"
        m.inputs[1].default_value = 0.5
        m.use_clamp = True
        links.new(rimg.outputs["Color"], m.inputs[0])
        links.new(m.outputs["Value"], bsdf.inputs["Roughness"])
    print(f"[PBR] wired {mat_name} <- marble_01 + 600mm grout")


# ---------------- main ----------------
build_pbr("Mat_Wall_Interior", "beige_wall_001", 2.5,
          tint=(1.0, 0.99, 0.97), desat=0.5, value=1.65,
          normal_strength=0.4, ao_fac=0.25)
build_pbr("Mat_Wall_Cap", "beige_wall_001", 2.5,
          tint=(1.0, 0.99, 0.97), desat=0.5, value=1.6,
          normal_strength=0.4, ao_fac=0.25)
assign_ceiling()
build_pbr("Mat_Wood_LightPlank", "laminate_floor_02", 3.0,
          rough_mul=0.75, normal_strength=0.7, spec=0.5)
build_pbr("Mat_Wood_WarmPlank", "laminate_floor_03", 3.0,
          rough_mul=0.75, normal_strength=0.7, spec=0.5)
build_pbr("Mat_Tile_Grey", "floor_tiles_06", 1.2,
          desat=0.7, value=1.45, rough_mul=0.8, normal_strength=0.8)
build_pbr("Mat_Tile_DarkSlate", "floor_tiles_02", 1.2,
          rough_mul=0.7, normal_strength=0.7)
build_pbr("Mat_BathTile_Wall", "floor_tiles_06", 1.2,
          tint=(0.98, 0.99, 1.0), desat=0.7, value=1.5,
          rough_mul=0.55, normal_strength=0.7)
build_pbr("Mat_Fabric_Sofa", "fabric_pattern_07", 0.8,
          sheen=0.6, normal_strength=0.8, ao_fac=0.3,
          flat=(0.72, 0.70, 0.67))
build_pbr("Mat_Bed_Linen", "fabric_pattern_07", 1.2,
          sheen=0.5, normal_strength=0.5, ao_fac=0.2,
          flat=(0.96, 0.95, 0.93))
build_pbr("Mat_BedSheet", "fabric_pattern_07", 1.2,
          sheen=0.5, normal_strength=0.5, ao_fac=0.2,
          flat=(0.96, 0.95, 0.93))
build_pbr("Mat_Pillow", "fabric_pattern_07", 0.6,
          sheen=0.6, normal_strength=0.6, ao_fac=0.2,
          flat=(0.95, 0.94, 0.92))
build_pbr("Mat_Bed_Runner", "fabric_pattern_07", 1.0,
          sheen=0.4, normal_strength=0.5, ao_fac=0.25,
          flat=(0.87, 0.82, 0.70))
build_pbr("Mat_Curtain", "fabric_pattern_07", 1.5,
          tint=(0.95, 0.93, 0.89), desat=0.10, value=1.60, sheen=0.7,
          normal_strength=0.5, ao_fac=0.3)
build_artwall()
build_pbr("Mat_Marble_White", "marble_01", 2.0,
          value=1.12, rough_mul=0.5, normal_strength=0.4, spec=0.55,
          ao_fac=0.3)
assign_bath_faces()
set_hdri()
print("[PBR] DONE")
