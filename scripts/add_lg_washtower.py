"""Q21: Model the LG TROMM Objet Collection WashTower WL21EGZU (official 700W x 1890H x 830D mm,
Nature Green 21kg dryer on top / Nature Beige 25kg washer below, centre control band) and place it in the
utility room (kitchen balcony) with its back to the west wall (x=3.775, 40mm hose gap) and its front (+X)
towards the Q20 turning door, following the model-house VR photo.

Front proportions are traced from references/furniture/lg-washtower/wl21egzu_front.png (photo-based approximation).
"""
from pathlib import Path
import math
import runpy
import shutil
import sys
import bpy
import bmesh

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))
import generate_high_detail_assets as A

backup = ROOT / 'models/backups/apt_84a_photoreal_tour_before_washtower.blend'
if not backup.exists():
    shutil.copy2(bpy.data.filepath, backup)

col = A.get_col('Apt_KitchenFinish')
for o in list(bpy.data.objects):
    if o.name.startswith(('Q21_WashTower_', 'Q21_UtilityTile_')):
        bpy.data.objects.remove(o, do_unlink=True)


def srgb(c):
    c /= 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def make_pbr_mat(name, rgb255, metallic=0.0, roughness=0.35, emission=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    nodes = m.node_tree.nodes
    nodes.clear()
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    rgba = (*[srgb(c) for c in rgb255], 1.0)
    bsdf.inputs['Base Color'].default_value = rgba
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Roughness'].default_value = roughness
    if emission:
        bsdf.inputs['Emission Color'].default_value = rgba
        bsdf.inputs['Emission Strength'].default_value = emission
    out = nodes.new('ShaderNodeOutputMaterial')
    m.node_tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return m


mat_green = make_pbr_mat('Mat_Q21_NatureGreen', (50, 68, 62), roughness=0.32)
mat_beige = make_pbr_mat('Mat_Q21_NatureBeige', (230, 226, 221), roughness=0.3)
mat_beige_dk = make_pbr_mat('Mat_Q21_BeigeTrim', (205, 200, 192), roughness=0.35)
mat_side = make_pbr_mat('Mat_Q21_SideSteel', (214, 214, 212), metallic=0.15, roughness=0.4)
mat_black = make_pbr_mat('Mat_Q21_DoorBlack', (8, 8, 9), roughness=0.5)
mat_black.node_tree.nodes['Principled BSDF'].inputs['Specular IOR Level'].default_value = 0.25
mat_champ = make_pbr_mat('Mat_Q21_ChampagneRim', (196, 172, 140), metallic=0.8, roughness=0.3)
mat_disp = make_pbr_mat('Mat_Q21_Display', (235, 238, 240), roughness=0.4, emission=0.6)
mat_logo = make_pbr_mat('Mat_Q21_Logo', (150, 156, 156), metallic=0.6, roughness=0.3)
mat_slot = make_pbr_mat('Mat_Q21_Slot', (70, 68, 64), roughness=0.5)
mat_glass = bpy.data.materials.get('Mat_Q10_Glass')
mat_drum = make_pbr_mat('Mat_Q21_Drum', (88, 92, 98), metallic=0.85, roughness=0.38)
assert mat_glass is not None, 'Mat_Q10_Glass missing'


def finish(o):
    bm = bmesh.new(); bm.from_mesh(o.data)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(o.data); bm.free()
    return o


def box(name, x1, x2, y1, y2, z1, z2, mat, bevel=0.001):
    o = A.create_beveled_box(name, (x1 + x2) / 2, (y1 + y2) / 2, z1, x2 - x1, y2 - y1, z2 - z1,
                             mat=mat, col=col, bevel=bevel, seg=2)
    for p in o.data.polygons:
        p.use_smooth = False
    return finish(o)


def join(name, objs):
    for o in bpy.data.objects:
        o.select_set(False)
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    if len(objs) > 1:
        bpy.ops.object.join()
    objs[0].name = name; objs[0].data.name = name + '_Mesh'
    objs[0].select_set(False)
    return objs[0]


def ring(name, cy, cz, r_in, r_out, x0, x1, mat, seg=96):
    """Annulus (or disc when r_in == 0) lying in the YZ plane, extruded along +X from x0 to x1."""
    bm = bmesh.new()
    def circle(r, x):
        return [bm.verts.new((x, cy + r * math.cos(2 * math.pi * i / seg), cz + r * math.sin(2 * math.pi * i / seg)))
                for i in range(seg)]
    of, ob = circle(r_out, x1), circle(r_out, x0)
    side = []
    for i in range(seg):
        j = (i + 1) % seg
        side.append(bm.faces.new((ob[i], ob[j], of[j], of[i])))
    if r_in > 0:
        inf, inb = circle(r_in, x1), circle(r_in, x0)
        for i in range(seg):
            j = (i + 1) % seg
            bm.faces.new((of[i], of[j], inf[j], inf[i]))
            bm.faces.new((ob[j], ob[i], inb[i], inb[j]))
            side.append(bm.faces.new((inf[i], inf[j], inb[j], inb[i])))
    else:
        bm.faces.new(of); bm.faces.new(list(reversed(ob)))
    for f in side:
        f.smooth = True
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    me = bpy.data.meshes.new(name + '_Mesh'); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); col.objects.link(o)
    me.materials.append(mat)
    return o


# Envelope: x 3.815..4.645 (830 incl. doors), y 9.030..9.730 (700), z ZB..ZB+1.890 standing on the Q21 tile floor
ZB = 0.014
X0, XB, XP = 3.815, 4.595, 4.603          # back, cabinet front, front-panel face
Y0, Y1 = 9.030, 9.730
YC = (Y0 + Y1) / 2
ZF, ZW, ZC, ZT = ZB + 0.016, ZB + 0.974, ZB + 1.073, ZB + 1.890  # feet top, washer top, control top, overall top

# --- Utility-room grey porcelain tile floor (300x300, 2mm grout) + square stainless drain ---------------------
# Room = south strip x3.175..4.975 / y8.360..9.015 and north bay x3.775..4.975 / y9.015..10.145 (wall faces).
# Grid origin at the doorway corner (x4.975, y8.360) so whole tiles meet the turning-door threshold.
mat_tile = make_pbr_mat('Mat_Q21_UtilityTile', (138, 135, 130), roughness=0.62)
mat_grout = bpy.data.materials.get('Mat_Q8_Grout') or make_pbr_mat('Mat_Q21_Grout', (120, 118, 114), roughness=0.9)
mat_steel = bpy.data.materials.get('Mat_Steel_Brushed') or mat_drum
ROOMS = [(3.175, 4.975, 8.360, 9.015), (3.775, 4.975, 9.015, 10.145)]
OX, OY, T, G = 4.975, 8.360, 0.300, 0.002
grout, tiles = [], []
for k, (rx0, rx1, ry0, ry1) in enumerate(ROOMS):
    grout.append(box(f'Q21_gr{k}', rx0, rx1, ry0, ry1, 0.0, 0.010, mat_grout, 0))
    i = 0
    while OX - (i + 1) * T < rx1 and OX - i * T > rx0 - 1e-6:
        j = 0
        while OY + j * T < ry1:
            x0, x1 = max(rx0, OX - (i + 1) * T + G / 2), min(rx1, OX - i * T - G / 2)
            y0, y1 = max(ry0, OY + j * T + G / 2), min(ry1, OY + (j + 1) * T - G / 2)
            if x1 - x0 > 0.01 and y1 - y0 > 0.01:
                tiles.append(box(f'Q21_t{k}_{i}_{j}', x0, x1, y0, y1, 0.010, ZB, mat_tile, 0.0006))
            j += 1
        i += 1
join('Q21_UtilityTile_Grout', grout)
join('Q21_UtilityTile_Floor', tiles)
join('Q21_UtilityTile_Drain', [box('Q21_dr0', 4.760, 4.880, 9.840, 9.960, ZB - 0.001, ZB + 0.002, mat_steel, 0.001)] +
     [box(f'Q21_dr{i + 1}', 4.775, 4.865, 9.856 + i * 0.016, 9.864 + i * 0.016, ZB + 0.002, ZB + 0.0025, mat_slot, 0)
      for i in range(6)])

join('Q21_WashTower_Feet', [box(f'Q21_ft{i}', fx - .02, fx + .02, fy - .02, fy + .02, ZB, ZF, mat_slot, .002)
                            for i, (fx, fy) in enumerate([(X0 + .06, Y0 + .05), (X0 + .06, Y1 - .05),
                                                          (XB - .05, Y0 + .05), (XB - .05, Y1 - .05)])])
box('Q21_WashTower_Washer_Body', X0, XB, Y0, Y1, ZF, ZC, mat_side, .004)
box('Q21_WashTower_Dryer_Body', X0, XB, Y0, Y1, ZC, ZT, mat_side, .004)
box('Q21_WashTower_Washer_Front', XB, XP, Y0, Y1, ZF, ZW, mat_beige, .002)
box('Q21_WashTower_Control_Panel', XB, XP, Y0, Y1, ZW, ZC, mat_black, .002)
box('Q21_WashTower_Dryer_Front', XB, XP, Y0, Y1, ZC, ZT, mat_green, .002)

# Dryer door (Nature Green cabinet): centre z 1.485, black bezel r .300, smoked glass r .203
DZ = 1.485
ring('Q21_WashTower_Dryer_Ring', YC, DZ, 0.203, 0.300, XP, 4.645, mat_black)
ring('Q21_WashTower_Dryer_Glass', YC, DZ, 0.0, 0.203, 4.630, 4.636, mat_glass)
join('Q21_WashTower_Dryer_Drum', [ring('Q21_dd0', YC, DZ, 0.0, 0.200, XP, XP + .003, mat_drum),
                                   ring('Q21_dd1', YC, DZ, 0.0, 0.045, XP, XP + .012, mat_drum)])

# Washer door (Nature Beige cabinet): centre z .538, champagne trim + black bezel r .300, glass r .219
WZ = 0.538
ring('Q21_WashTower_Washer_Rim', YC, WZ, 0.300, 0.306, XP, 4.640, mat_champ)
ring('Q21_WashTower_Washer_Ring', YC, WZ, 0.219, 0.300, XP, 4.645, mat_black)
ring('Q21_WashTower_Washer_Glass', YC, WZ, 0.0, 0.219, 4.630, 4.636, mat_glass)
join('Q21_WashTower_Washer_Drum', [ring('Q21_wd0', YC, WZ, 0.0, 0.216, XP, XP + .003, mat_drum),
                                    ring('Q21_wd1', YC, WZ, 0.0, 0.050, XP, XP + .014, mat_drum)])

# Image-left = south (-Y) when facing the +X front: auto-dose dispenser, filter cover, LG logo
join('Q21_WashTower_Dispenser', [box('Q21_dp0', XP, XP + .004, Y0 + .016, Y0 + .216, 0.848, 0.945, mat_beige_dk, .001),
                                  box('Q21_dp1', XP + .004, XP + .0055, Y0 + .032, Y0 + .154, 0.872, 0.906, mat_slot, .0005)])
box('Q21_WashTower_Filter_Cover', XP, XP + .002, Y0 + .062, Y0 + .225, 0.022, 0.135, mat_beige_dk, .0008)
box('Q21_WashTower_Logo', XP, XP + .0006, Y0 + .022, Y0 + .062, 1.855, 1.868, mat_logo, .0002)

disp = [box('Q21_ds0', XP, XP + .0008, YC - .05, YC + .05, 1.012, 1.036, mat_disp, .0002)]
for i, (yy, zz) in enumerate([(YC - .125, 1.040), (YC - .125, 1.005), (YC + .12, 1.040), (YC + .12, 1.005),
                              (YC - .03, 1.002), (YC, 1.002), (YC + .03, 1.002), (YC + .07, 1.022)]):
    disp.append(box(f'Q21_ds{i + 1}', XP, XP + .0008, yy - .004, yy + .004, zz - .004, zz + .004, mat_disp, .0002))
join('Q21_WashTower_Display', disp)

bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
bpy.context.scene['Q21_lg_washtower'] = 1
bpy.context.view_layer.update()
runpy.run_path(str(ROOT / 'scripts/verify_lg_washtower.py'), run_name='__main__')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / 'apt_84a_photoreal_tour.blend'))
print('Q21 LG WASHTOWER SAVED', flush=True)
