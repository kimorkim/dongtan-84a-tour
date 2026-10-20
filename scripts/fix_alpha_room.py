"""Restore the alpha boundary from traced plan data and remove its office set.

Run after Q3/Q4 on the saved master blend. Rebuilds the damaged ExactWall_8,
keeps its kitchen boundary, and uses the plan's southern entry/northern AC door.
"""
import json
import os
import sys

import bmesh
import bpy
from mathutils import Vector

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import generate_high_detail_assets as A

# The old "Alpha" door is actually the neighbouring entry pantry door.
old_leaf = bpy.data.objects.get('ProDoorLeaf_Alpha')
if old_leaf and (old_leaf.matrix_world @ Vector(old_leaf.bound_box[0])).x > 10.8:
    for obj in bpy.data.objects:
        if obj.name.startswith(('ProDoorLeaf_Alpha', 'ProDoorTrim_Alpha', 'ProDoorHandle_Alpha')):
            obj.name = obj.name.replace('_Alpha', '_EntryPantry')

for obj in list(bpy.data.objects):
    if obj.name.startswith(('Office_', 'Vent_ACRoom_', 'Q5_', 'Q3_Trim', 'Q3_Utility_Handle',
                            'ProDoorLeaf_Alpha', 'ProDoorTrim_Alpha', 'ProDoorHandle_Alpha',
                            'ProDoorHandle_Utility_')) or obj.name in (
            'ProDoorLeaf_Utility', 'Q3_UtilityWestWall', 'Floor_AlphaRoom'):
        bpy.data.objects.remove(obj, do_unlink=True)

col = A.get_col('Apt_AlphaRoom')
wall_mat = bpy.data.materials['Mat_Wall_Interior']
cap = bpy.data.materials['Mat_Wall_Cap']
frame = bpy.data.materials['Mat_DoorFrame_White']
door = bpy.data.materials['Mat_Cabinet_Cashmere']
metal = bpy.data.materials['Mat_Chrome_Metal']
wood = bpy.data.materials['Mat_Wood_LightPlank']


def box(name, x1, x2, y1, y2, z1, z2, mat):
    return A.create_beveled_box(name, (x1+x2)/2, (y1+y2)/2, z1,
                                x2-x1, y2-y1, z2-z1, bevel=0.002, mat=mat, col=col)


# Repeated booleans had produced thousands of zero-area/duplicate faces.
with open(os.path.join(ROOT, 'assets', 'analysis', 'polys.json'), encoding='utf-8') as stream:
    outline = json.load(stream)[7]
count = len(outline)
vertices = [(x, y, z) for z in (0.0, 2.30) for x, y in outline]
faces = [(i, (i+1) % count, (i+1) % count+count, i+count) for i in range(count)]
faces += [tuple(reversed(range(count))), tuple(range(count, count*2))]
mesh = bpy.data.meshes.new('Q5_AlphaBoundaryMesh')
mesh.from_pydata(vertices, [], faces)
mesh.update()
wall = bpy.data.objects['ExactWall_8']
wall.data = mesh
mesh.materials.append(wall_mat)
mesh.materials.append(cap)
bm = bmesh.new()
bm.from_mesh(mesh)
bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
bmesh.ops.triangulate(bm, faces=list(bm.faces))
bm.to_mesh(mesh)
bm.free()

# The thick west boundary is present in the plan; do not carve a second passage into it.
bm = bmesh.new()
bm.from_mesh(wall.data)
bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=1e-6)
bmesh.ops.dissolve_degenerate(bm, edges=list(bm.edges), dist=1e-6)
bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
bm.to_mesh(wall.data)
bm.free()
wall.data.update()
for polygon in wall.data.polygons:
    polygon.material_index = 1 if polygon.normal.z > 0.8 else 0
assert not wall.data.validate(verbose=False, clean_customdata=False)
assert all(p.area > 1e-10 for p in wall.data.polygons)

box('Floor_AlphaRoom', 7.987, 10.387, 5.737, 7.931, 0.002, 0.014, wood)
# South: the actual alpha-room entry from the hall.
box('Q5_AlphaEntry_Header', 9.412, 10.35, 5.644, 5.737, 2.10, 2.30, wall_mat)
for tag, a, b in [('W', 9.37, 9.412), ('E', 10.35, 10.392)]:
    box('ProDoorTrim_Alpha_'+tag, a, b, 5.62, 5.76, 0.0, 2.10, frame)
box('ProDoorTrim_Alpha_Head', 9.37, 10.392, 5.62, 5.76, 2.07, 2.13, frame)
box('ProDoorLeaf_Alpha', 10.29, 10.33, 5.76, 6.63, 0.015, 2.085, door)
box('ProDoorHandle_Alpha_A', 10.255, 10.29, 6.49, 6.60, 0.97, 1.00, metal)

# North: the native plan opening is x9.00..9.731, not the extra x8.05..8.85 cut.
box('Q5_ACDoor_Header', 9.0, 9.731, 7.95, 8.175, 2.10, 2.30, wall_mat)
for tag, a, b in [('W', 8.955, 9.0), ('E', 9.731, 9.776)]:
    box('Q5_ACDoor_Jamb'+tag, a, b, 7.925, 8.20, 0.0, 2.10, frame)
box('Q5_ACDoor_Head', 8.955, 9.776, 7.925, 8.20, 2.07, 2.13, frame)
box('ProDoorLeaf_Utility', 9.68, 9.72, 8.20, 8.87, 0.015, 2.085, door)
box('ProDoorHandle_Utility_A', 9.645, 9.68, 8.72, 8.83, 0.97, 1.00, metal)

bpy.context.view_layer.update()
# Keep the dining rug west of the alpha wall (x7.856), including 50mm clearance.
rug = bpy.data.objects['Q2_Dining_Rug']
rug.location.x = 6.85
rug.dimensions.x = 1.90
bpy.context.view_layer.update()
exec(compile(open(os.path.join(ROOT, 'scripts', 'verify_alpha_room.py'), encoding='utf-8').read(),
             'verify_alpha_room.py', 'exec'))
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT, 'apt_84a_photoreal_tour.blend'))
print('Q5 ALPHA SAVED: clean boundary, empty room, plan-aligned hall/AC openings')
