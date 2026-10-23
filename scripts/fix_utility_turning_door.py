"""Q20: Fix the slanted wall & baseboard gap between the fridge cabinet and the utility room doorway,
add the missing upper door header wall, and replace the floating trims and opaque wooden door with an
integrated uPVC Turning Door (frame + glazed door leaf + gaskets + compression lever handle).
"""
from pathlib import Path
import runpy
import shutil
import sys
import bpy
import bmesh
from mathutils import Vector

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))
import generate_high_detail_assets as A

backup = ROOT / 'models/backups/apt_84a_photoreal_tour_before_turning_door.blend'
if not backup.exists():
    shutil.copy2(bpy.data.filepath, backup)

col = A.get_col('Apt_KitchenFinish')

# 1. Remove old floating trims, old handle, old opaque door leaf, and any previous Q20 objects
OLD_NAMES = (
    'Q3_SinkTrimK_N', 'Q3_SinkTrimK_S', 'Q3_SinkTrimK_Top',
    'Q3_SinkTrimR_N', 'Q3_SinkTrimR_S', 'Q3_SinkTrimR_Top',
    'Q3_SinkDoor_HandleBar', 'Q3_SinkDoor_HandleBase',
    'ProDoorLeaf_UtilitySink',
)
for o in list(bpy.data.objects):
    if (
        o.name in OLD_NAMES
        or o.name.startswith('Q20_')
        or o.name.startswith('ProDoorLeaf_UtilitySink_')
    ):
        bpy.data.objects.remove(o, do_unlink=True)

# 2. Straighten ExactWall_11 north fridge-alcove wing wall to y = 8.1760 (flush with Q3_SideN)
w11 = bpy.data.objects['ExactWall_11']
inv_w11 = w11.matrix_world.inverted()
for v in w11.data.vertices:
    wp = w11.matrix_world @ v.co
    if 4.30 < wp.x < 5.10 and 8.17 < wp.y < 8.30:
        wp.y = 8.1760
        v.co = inv_w11 @ wp
bm = bmesh.new()
bm.from_mesh(w11.data)
bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
bm.to_mesh(w11.data)
bm.free()
w11.data.update()

# 3. Remove the protruding wedge block in ProBaseboards inside the fridge-to-utility alcove (x=4.32..5.09, y=8.172..8.32)
bb_obj = bpy.data.objects.get('ProBaseboards')
if bb_obj and bb_obj.type == 'MESH':
    bm = bmesh.new()
    bm.from_mesh(bb_obj.data)
    faces_to_del = []
    for f in bm.faces:
        wcoords = [bb_obj.matrix_world @ v.co for v in f.verts]
        if all(4.32 < p.x < 5.09 and 8.172 < p.y < 8.32 for p in wcoords):
            faces_to_del.append(f)
    if faces_to_del:
        bmesh.ops.delete(bm, geom=faces_to_del, context='FACES')
        bm.to_mesh(bb_obj.data)
    bm.free()
    bb_obj.data.update()

# 4. Materials for Header Wall, uPVC Turning Door Frame, Gasket, Glass, and Lever Handle
wall_mat = bpy.data.materials['Mat_Wall_Interior']
frame_mat = bpy.data.materials['Mat_DoorFrame_White']
chrome_mat = bpy.data.materials['Mat_Chrome_Metal']
glass_mat = bpy.data.materials.get('Mat_Q10_Glass')
if glass_mat is None:
    glass_mat = bpy.data.materials.new('Mat_Q10_Glass')
    glass_mat.use_nodes = True
    bsdf = glass_mat.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.88, 0.93, 0.95, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.08
        bsdf.inputs['Alpha'].default_value = 0.08

gasket_mat = bpy.data.materials.get('Mat_Q20_TurningGasket')
if gasket_mat is None:
    gasket_mat = bpy.data.materials.new('Mat_Q20_TurningGasket')
gasket_mat.use_nodes = True
gasket_mat.node_tree.nodes.clear()
nodes = gasket_mat.node_tree.nodes
links = gasket_mat.node_tree.links
bsdf = nodes.new('ShaderNodeBsdfPrincipled')
bsdf.inputs['Base Color'].default_value = (0.045, 0.045, 0.048, 1.0)
bsdf.inputs['Metallic'].default_value = 0.05
bsdf.inputs['Roughness'].default_value = 0.65
out = nodes.new('ShaderNodeOutputMaterial')
links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])

def make_box(name, x1, x2, y1, y2, z1, z2, mat, bevel=0.001):
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

def join_boxes(name, specs, mat, bevel=0.0008):
    parts = []
    for i, (x1, x2, y1, y2, z1, z2) in enumerate(specs):
        parts.append(make_box(f'{name}_tmp_{i}', x1, x2, y1, y2, z1, z2, mat, bevel=bevel))
    for o in bpy.data.objects:
        o.select_set(False)
    bpy.context.view_layer.objects.active = parts[0]
    for p in parts:
        p.select_set(True)
    if len(parts) > 1:
        bpy.ops.object.join()
    main = parts[0]
    main.name = name
    main.data.name = f'{name}_Mesh'
    main.select_set(False)
    return main

# 5. Add Upper Door Header Wall (z = 2.150 .. 2.300) closing the gap above the utility door up to the ceiling
make_box('Q20_UtilityDoor_Header', 4.9750, 5.0750, 8.3600, 9.0150, 2.1500, 2.3000, wall_mat, bevel=0.0)

# 6. Build Integrated uPVC Turning Door Frame wrapping the full wall thickness (x = 4.963 .. 5.087)
make_box('Q20_TurningDoor_Frame_S',   4.9630, 5.0870, 8.3450, 8.4100, 0.0000, 2.1550, frame_mat, bevel=0.001)
make_box('Q20_TurningDoor_Frame_N',   4.9630, 5.0870, 8.9650, 9.0300, 0.0000, 2.1550, frame_mat, bevel=0.001)
make_box('Q20_TurningDoor_Frame_Top', 4.9630, 5.0870, 8.3450, 9.0300, 2.1000, 2.1550, frame_mat, bevel=0.001)
make_box('Q20_TurningDoor_Frame_Bot', 4.9680, 5.0820, 8.4100, 8.9650, 0.0000, 0.0220, frame_mat, bevel=0.001)

# Airtight EPDM gasket channel inside the frame opening
join_boxes(
    'Q20_TurningDoor_Frame_Gasket',
    [
        (5.0150, 5.0350, 8.4100, 8.4160, 0.0220, 2.1000),
        (5.0150, 5.0350, 8.9590, 8.9650, 0.0220, 2.1000),
        (5.0150, 5.0350, 8.4160, 8.9590, 2.0940, 2.1000),
        (5.0150, 5.0350, 8.4160, 8.9590, 0.0220, 0.0270),
    ],
    gasket_mat,
    bevel=0.0003,
)

# 7. Build Turning Door Leaf (opened 90 degrees into utility room along -X from south hinge y=8.412..8.456)
#    All parts prefixed with ProDoorLeaf_UtilitySink_ so bake_collision.py treats them as passable door leaf.
join_boxes(
    'ProDoorLeaf_UtilitySink_Frame',
    [
        (4.8900, 4.9700, 8.4120, 8.4560, 0.0250, 2.0980),  # East hinge stile (80mm)
        (4.4150, 4.4950, 8.4120, 8.4560, 0.0250, 2.0980),  # West latch stile (80mm)
        (4.4950, 4.8900, 8.4120, 8.4560, 0.0250, 0.1250),  # Bottom rail (100mm)
        (4.4950, 4.8900, 8.4120, 8.4560, 2.0180, 2.0980),  # Top rail (80mm)
    ],
    frame_mat,
    bevel=0.0012,
)

join_boxes(
    'ProDoorLeaf_UtilitySink_Gasket',
    [
        (4.4950, 4.5020, 8.4200, 8.4480, 0.1250, 2.0180),
        (4.8830, 4.8900, 8.4200, 8.4480, 0.1250, 2.0180),
        (4.5020, 4.8830, 8.4200, 8.4480, 0.1250, 0.1320),
        (4.5020, 4.8830, 8.4200, 8.4480, 2.0110, 2.0180),
    ],
    gasket_mat,
    bevel=0.0003,
)

make_box('ProDoorLeaf_UtilitySink_Glass', 4.5020, 4.8830, 8.4280, 8.4400, 0.1320, 2.0110, glass_mat, bevel=0.0)

join_boxes(
    'ProDoorLeaf_UtilitySink_Handle',
    [
        (4.4420, 4.4680, 8.4060, 8.4620, 0.9600, 1.0800),  # Dual escutcheon plates + spindle
        (4.4420, 4.4680, 8.3820, 8.4860, 1.0120, 1.0280),  # Lever spindle neck
        (4.4420, 4.5750, 8.3820, 8.3940, 1.0110, 1.0290),  # South lever handle
        (4.4420, 4.5750, 8.4740, 8.4860, 1.0110, 1.0290),  # North lever handle
    ],
    chrome_mat,
    bevel=0.0008,
)

bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
bpy.context.scene['Q20_utility_turning_door'] = 1
bpy.context.view_layer.update()
runpy.run_path(str(ROOT / 'scripts/verify_utility_turning_door.py'), run_name='__main__')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / 'apt_84a_photoreal_tour.blend'))
print('Q20 UTILITY TURNING DOOR & WALL GAP FIX SAVED', flush=True)
