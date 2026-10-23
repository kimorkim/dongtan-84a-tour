"""Q18: Add an upper open appliance bay above the rice cooker in the fridge cabinet unit
and place the modelled LG Objet Collection Lightwave Oven (MLJ32EWSO, 527x480x394mm).
"""
import math
from pathlib import Path
import runpy
import shutil
import sys
import bpy
import bmesh
from mathutils import Euler, Matrix, Vector

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))
import generate_high_detail_assets as A

backup = ROOT / 'models/backups/apt_84a_photoreal_tour_before_lightwave_oven.blend'
if not backup.exists():
    shutil.copy2(bpy.data.filepath, backup)

col = A.get_col('Apt_KitchenFinish')

def remove_if_exists(name):
    o = bpy.data.objects.get(name)
    if o:
        bpy.data.objects.remove(o, do_unlink=True)

for o in list(bpy.data.objects):
    if o.name.startswith('Q18_LightwaveOven_') or o.name in (
        'Q3_Drawer_TopDoor', 'Q3_OvenNiche_Top',
        'Q3_Drawer_TopCabDoor', 'Q3_Drawer_TopBottom', 'Q3_Drawer_TopPanel',
        'Q3_OvenUpper_Core', 'Q3_OvenUpper_Door',
    ):
        bpy.data.objects.remove(o, do_unlink=True)

cashmere = bpy.data.materials['Mat_Cabinet_Cashmere']
body_back_mat = bpy.data.materials.get('Mat_Q3_Body') or cashmere

def make_box(name, x1, x2, y1, y2, z1, z2, mat, bevel=0.001):
    remove_if_exists(name)
    o = A.create_beveled_box(
        name, (x1 + x2) / 2, (y1 + y2) / 2, z1,
        x2 - x1, y2 - y1, z2 - z1,
        mat=mat, col=col, bevel=bevel, seg=2
    )
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(o.data)
    bm.free()
    for p in o.data.polygons:
        p.use_smooth = False
    return o

def set_box_bounds(name, x1, x2, y1, y2, z1, z2):
    o = bpy.data.objects.get(name)
    assert o is not None and o.type == 'MESH', f'Missing box object {name}'
    pts = [o.matrix_world @ Vector(c) for c in o.bound_box]
    cx = (min(p.x for p in pts) + max(p.x for p in pts)) / 2
    cy = (min(p.y for p in pts) + max(p.y for p in pts)) / 2
    cz = (min(p.z for p in pts) + max(p.z for p in pts)) / 2
    inv = o.matrix_world.inverted()
    for v in o.data.vertices:
        wp = o.matrix_world @ v.co
        nx = x1 if wp.x < cx else x2
        ny = y1 if wp.y < cy else y2
        nz = z1 if wp.z < cz else z2
        v.co = inv @ Vector((nx, ny, nz))
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(o.data)
    bm.free()
    for p in o.data.polygons:
        p.use_smooth = False
    o.data.update()
    return o

def shift_mesh_bounds(name, target_x1, target_y_center, target_z_center):
    o = bpy.data.objects.get(name)
    assert o is not None and o.type == 'MESH', f'Missing mesh {name}'
    pts = [o.matrix_world @ Vector(c) for c in o.bound_box]
    cur_x1 = min(p.x for p in pts)
    cur_yc = (min(p.y for p in pts) + max(p.y for p in pts)) / 2
    cur_zc = (min(p.z for p in pts) + max(p.z for p in pts)) / 2
    delta = Vector((target_x1 - cur_x1, target_y_center - cur_yc, target_z_center - cur_zc))
    inv = o.matrix_world.inverted()
    for v in o.data.vertices:
        wp = (o.matrix_world @ v.co) + delta
        v.co = inv @ wp
    o.data.update()
    return o

# 1a. Tighten all Q3 fridge cabinet panels, upper doors, and lower drawers to eliminate gaps & Z-fighting:
# Outer side panels reaching ceiling (z = 0.000 .. 2.300)
set_box_bounds('Q3_SideS', 4.3353, 4.9260, 5.7464, 5.7664, 0.0000, 2.3000)
set_box_bounds('Q3_SideN', 4.3353, 4.9260, 8.1560, 8.1760, 0.0000, 2.3000)

# Upper solid backing carcass, ceiling moulding, and 4 full-overlay upper doors (2mm seams)
set_box_bounds('Q3_TopBottom', 4.3353, 4.9040, 5.7664, 8.1560, 1.8100, 1.8300)
set_box_bounds('Q3_TopFiller', 4.3353, 4.9040, 5.7664, 8.1560, 1.8300, 2.2620)
set_box_bounds('Q3_TopPanel',  4.3353, 4.9260, 5.7664, 8.1560, 2.2620, 2.3000)

set_box_bounds('Q3_TopDoor1',  4.9060, 4.9260, 5.7684, 6.3180, 1.8120, 2.2600)
set_box_bounds('Q3_TopDoor2',  4.9060, 4.9260, 6.3200, 6.8706, 1.8120, 2.2600)
set_box_bounds('Q3_TopDoor3',  4.9060, 4.9260, 6.8726, 7.4900, 1.8120, 2.2600)
set_box_bounds('Q3_TopDoor0',  4.9060, 4.9260, 7.4920, 8.1540, 1.8120, 2.2600)

# Column 1 (4-Door Fridge) & surrounding fillers
set_box_bounds('Q3_FillerS',       4.3353, 4.9250, 5.7664, 5.8520, 0.0000, 1.8100)
set_box_bounds('Q3_FillerN',       4.3353, 4.9250, 6.7580, 6.8616, 0.0000, 1.8100)
set_box_bounds('Q3_Fridge_Body',   4.3353, 4.9040, 5.8500, 6.7600, 0.0000, 1.8100)
set_box_bounds('Q3_Fridge_DoorL',  4.8950, 4.9250, 5.8540, 6.3035, 1.0750, 1.8050)
set_box_bounds('Q3_Fridge_DoorR',  4.8950, 4.9250, 6.3065, 6.7560, 1.0750, 1.8050)
set_box_bounds('Q3_Fridge_Groove', 4.9050, 4.9200, 5.8540, 6.7560, 1.0550, 1.0750)
set_box_bounds('Q3_Fridge_Drawer1',4.8950, 4.9250, 5.8540, 6.7560, 0.5600, 1.0550)
set_box_bounds('Q3_Fridge_Drawer2',4.8950, 4.9250, 5.8540, 6.7560, 0.0400, 0.5450)

# Column 2 (Kimchi Fridge) & dividers
set_box_bounds('Q3_Divider',        4.3353, 4.9260, 6.8616, 6.8816, 0.0000, 1.8100)
set_box_bounds('Q3_Kimchi_Body',    4.3353, 4.9040, 6.8816, 7.4790, 0.0000, 1.8100)
set_box_bounds('Q3_Kimchi_FillerS', 4.3353, 4.9040, 6.8816, 6.8860, 0.0000, 1.8100)
set_box_bounds('Q3_Kimchi_FillerN', 4.3353, 4.9040, 7.4745, 7.4790, 0.0000, 1.8100)
set_box_bounds('Q3_Kimchi_Top',     4.8950, 4.9250, 6.8836, 7.4770, 1.2740, 1.8050)
set_box_bounds('Q3_Kimchi_Line1',   4.9050, 4.9200, 6.8836, 7.4770, 1.2580, 1.2740)
set_box_bounds('Q3_Kimchi_Mid',     4.8950, 4.9250, 6.8836, 7.4770, 0.6940, 1.2580)
set_box_bounds('Q3_Kimchi_Line2',   4.9050, 4.9200, 6.8836, 7.4770, 0.6780, 0.6940)
set_box_bounds('Q3_Kimchi_Bot',     4.8950, 4.9250, 6.8836, 7.4770, 0.0400, 0.6780)

# Column 3 (Appliance Tower: lower drawers + rice cooker bay + lightwave oven bay + middle-upper cabinet)
set_box_bounds('Q3_Divider2',      4.3353, 4.9260, 7.4790, 7.4910, 0.0000, 1.8100)
set_box_bounds('Q3_Drawer_SideS',  4.3353, 4.9260, 7.4910, 7.5033, 0.0000, 1.4200)
set_box_bounds('Q3_Drawer_SideN',  4.3353, 4.9260, 8.1359, 8.1560, 0.0000, 1.4200)
set_box_bounds('Q3_Drawer_Core',   4.3353, 4.9040, 7.5033, 8.1359, 0.0000, 0.5620)
set_box_bounds('Q3_Drawer_Front2', 4.9060, 4.9260, 7.5050, 8.1342, 0.0400, 0.2990)
set_box_bounds('Q3_Drawer_Front1', 4.9060, 4.9260, 7.5050, 8.1342, 0.3010, 0.5600)
shift_mesh_bounds('Q3_Drawer_Handle0', 4.9255, 7.8196, 0.5100)
shift_mesh_bounds('Q3_Drawer_Handle1', 4.9255, 7.8196, 0.2490)

# 1b. Ergonomic two stacked open bays + upper storage door above lightwave oven:
#    - Lower bay (rice cooker): z = 0.582 .. 0.940 (shelf z = 0.562 .. 0.582)
#    - Upper bay (LG lightwave oven): z = 0.960 .. 1.400 (shelf z = 0.940 .. 0.960, top z = 1.400 .. 1.420)
#    - Middle-upper storage door above oven: z = 1.422 .. 1.8095
make_box('Q3_Niche_Shelf',   4.3658, 4.9250, 7.5033, 8.1359, 0.5620, 0.5820, cashmere)
make_box('Q3_Niche_Top',     4.3658, 4.9250, 7.5033, 8.1359, 0.9400, 0.9600, cashmere)
make_box('Q3_OvenNiche_Top', 4.3658, 4.9250, 7.5033, 8.1359, 1.4000, 1.4200, cashmere)
make_box('Q3_Niche_Back',    4.3458, 4.3658, 7.5033, 8.1359, 0.5620, 1.4200, cashmere, bevel=0.0)
make_box('Q3_OvenUpper_Core',4.3353, 4.9040, 7.5033, 8.1359, 1.4200, 1.8100, cashmere, bevel=0.0)
make_box('Q3_OvenUpper_Door',4.9060, 4.9260, 7.4920, 8.1540, 1.4220, 1.8095, cashmere, bevel=0.0005)

# Move Rice Cooker assembly (Q3_Cooker_Body, Q3_Cooker_Lid, Q3_Cooker_Panel) onto lowered Q3_Niche_Shelf (z=0.582)
cooker_body = bpy.data.objects['Q3_Cooker_Body']
cb_pts = [cooker_body.matrix_world @ Vector(c) for c in cooker_body.bound_box]
cooker_dz = 0.5870 - min(p.z for p in cb_pts)
for cname in ('Q3_Cooker_Body', 'Q3_Cooker_Lid', 'Q3_Cooker_Panel'):
    co = bpy.data.objects.get(cname)
    if co:
        co.location.z += cooker_dz

# 2. Build materials for LG Objet Collection Lightwave Oven (MLJ32EWSO)
def make_pbr_mat(name, rgba, metallic=0.0, roughness=0.3):
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials.new(name)
    m.use_nodes = True
    m.node_tree.nodes.clear()
    nodes = m.node_tree.nodes
    links = m.node_tree.links
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = rgba
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Roughness'].default_value = roughness
    out = nodes.new('ShaderNodeOutputMaterial')
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return m

mat_body_white = make_pbr_mat('Mat_Q18_OvenBodyWhite', (0.91, 0.91, 0.90, 1.0), metallic=0.15, roughness=0.32)
mat_cream_edge = make_pbr_mat('Mat_Q18_OvenCreamEdge', (0.78, 0.75, 0.69, 1.0), metallic=0.0, roughness=0.22)
mat_black_glass = make_pbr_mat('Mat_Q18_OvenBlackGlass', (0.012, 0.012, 0.014, 1.0), metallic=0.0, roughness=0.08)
mat_dial_metal = make_pbr_mat('Mat_Q18_OvenDialMetal', (0.06, 0.062, 0.065, 1.0), metallic=0.85, roughness=0.28)

tex_path = ROOT / 'assets/textures_export/q18_lg_lightwave_front.jpg'
assert tex_path.exists(), f'Missing front texture: {tex_path}'
front_img = None
for im in bpy.data.images:
    if im.filepath and Path(bpy.path.abspath(im.filepath)).resolve() == tex_path.resolve():
        front_img = im
        break
if front_img is None:
    front_img = bpy.data.images.load(str(tex_path), check_existing=True)
front_img.colorspace_settings.name = 'sRGB'

mat_front_tex = bpy.data.materials.get('Mat_Q18_OvenFrontTex')
if mat_front_tex is None:
    mat_front_tex = bpy.data.materials.new('Mat_Q18_OvenFrontTex')
mat_front_tex.use_nodes = True
mat_front_tex.node_tree.nodes.clear()
nodes = mat_front_tex.node_tree.nodes
links = mat_front_tex.node_tree.links
uv_node = nodes.new('ShaderNodeUVMap')
uv_node.uv_map = 'UVMap'
tex_node = nodes.new('ShaderNodeTexImage')
tex_node.image = front_img
bsdf = nodes.new('ShaderNodeBsdfPrincipled')
bsdf.inputs['Metallic'].default_value = 0.04
bsdf.inputs['Roughness'].default_value = 0.14
out = nodes.new('ShaderNodeOutputMaterial')
links.new(uv_node.outputs['UV'], tex_node.inputs['Vector'])
links.new(tex_node.outputs['Color'], bsdf.inputs['Base Color'])
links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])

# 3. Model LG MLJ32EWSO (527mm W x 480mm D x 394mm H)
#    Placed at:
#    x = 4.420 .. 4.900 (depth 480mm)
#    y = 7.5715 .. 8.0985 (width 527mm, centered at y = 7.835)
#    z = 0.960 .. 1.354 (height 394mm, resting on Q3_Niche_Top z = 0.960)
X0, X_DOOR, X1 = 4.420, 4.882, 4.900
Y0, Y1 = 7.5715, 8.0985
Z0, Z_DOOR0, Z_SPLIT, Z1 = 0.960, 1.001, 1.147, 1.354

# Body enclosure (4.420..4.882, full 527w x 394h, plus bottom recessed base lip extending to x=4.896)
body = make_box('Q18_LightwaveOven_Body', X0, X_DOOR, Y0, Y1, Z0, Z1, mat_body_white, bevel=0.002)
base_lip = make_box('Q18_LightwaveOven_BaseLipTmp', X_DOOR, 4.896, Y0 + 0.004, Y1 - 0.004, Z0, Z_DOOR0 - 0.002, mat_body_white, bevel=0.001)
bpy.context.view_layer.objects.active = body
for o in bpy.data.objects:
    o.select_set(False)
body.select_set(True)
base_lip.select_set(True)
bpy.ops.object.join()
body.select_set(False)

def map_door_uv(obj, edge_mat):
    bpy.context.view_layer.update()
    obj.data.materials.clear()
    obj.data.materials.append(edge_mat)       # slot 0: side/top/bottom bevels
    obj.data.materials.append(mat_front_tex)  # slot 1: +X front face
    mw = obj.matrix_world
    rot = mw.to_3x3()
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    uv_layer = bm.loops.layers.uv.get('UVMap') or bm.loops.layers.uv.new('UVMap')
    for f in bm.faces:
        wn = (rot @ f.normal).normalized()
        if wn.x > 0.75:
            f.material_index = 1
        else:
            f.material_index = 0
        for loop in f.loops:
            wp = mw @ loop.vert.co
            u = (wp.y - Y0) / (Y1 - Y0)
            v = (wp.z - Z_DOOR0) / (Z1 - Z_DOOR0)
            loop[uv_layer].uv = (min(max(u, 0.0), 1.0), min(max(v, 0.0), 1.0))
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.uv_layers.active = obj.data.uv_layers['UVMap']

door_lower = make_box('Q18_LightwaveOven_DoorLower', X_DOOR, X1, Y0, Y1, Z_DOOR0, Z_SPLIT, mat_cream_edge, bevel=0.0)
map_door_uv(door_lower, mat_cream_edge)

door_upper = make_box('Q18_LightwaveOven_DoorUpper', X_DOOR, X1, Y0, Y1, Z_SPLIT, Z1, mat_black_glass, bevel=0.0)
map_door_uv(door_upper, mat_black_glass)

# Viewing window & upper display mapped seamlessly on the front plane
win = make_box('Q18_LightwaveOven_Window', 4.9003, 4.9010, 7.645, 8.025, 1.157, 1.240, mat_black_glass, bevel=0.0)
map_door_uv(win, mat_black_glass)

disp = make_box('Q18_LightwaveOven_Display', 4.9003, 4.9010, 7.783, 7.835, 1.287, 1.329, mat_black_glass, bevel=0.0)
map_door_uv(disp, mat_black_glass)

# 3D Rotary dial knob on the upper control bar (+X face)
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=0.0185,
    depth=0.011,
    location=(4.9045, 7.8737, 1.3118),
    rotation=(0.0, math.pi / 2, 0.0),
)
dial = bpy.context.active_object
dial.name = 'Q18_LightwaveOven_Dial'
dial.data.name = 'Q18_LightwaveOven_Dial'
dial.data.materials.append(mat_dial_metal)
dial_xf = dial.matrix_world.copy()
dial.matrix_world = Matrix.Identity(4)
dial.data.transform(dial_xf)
dial.data.update()
for c in list(dial.users_collection):
    c.objects.unlink(dial)
col.objects.link(dial)

bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
bpy.context.scene['Q18_lightwave_oven'] = 1
bpy.context.view_layer.update()
runpy.run_path(str(ROOT / 'scripts/verify_lg_lightwave_oven.py'), run_name='__main__')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / 'apt_84a_photoreal_tour.blend'))
print('Q18 LG LIGHTWAVE OVEN SAVED', flush=True)
