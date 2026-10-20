"""Run inside Blender: alpha-room mesh/objects/openings regression checks."""
import bpy
import bmesh
from mathutils import Vector

wall = bpy.data.objects['ExactWall_8']
rug = bpy.data.objects['Q2_Dining_Rug'].evaluated_get(bpy.context.evaluated_depsgraph_get())
rug_points = [rug.matrix_world @ Vector(c) for c in rug.bound_box]
assert max(p.x for p in rug_points) <= 7.806, 'Dining rug crosses alpha wall or lacks 50mm clearance'
table = bpy.data.objects['Dining_Table_Top']
table_points = [table.matrix_world @ Vector(c) for c in table.bound_box]
for axis in (0, 1):
    assert min(p[axis] for p in rug_points) <= min(p[axis] for p in table_points)
    assert max(p[axis] for p in rug_points) >= max(p[axis] for p in table_points)
bm = bmesh.new()
try:
    bm.from_mesh(wall.data)
    assert all(e.is_manifold for e in bm.edges), 'Alpha boundary is not watertight'
finally:
    bm.free()
assert not any(p.area < 1e-10 for p in wall.data.polygons), 'Alpha boundary contains degenerate faces'
probe = wall.data.copy()
try:
    assert not probe.validate(verbose=False, clean_customdata=False), 'Alpha boundary mesh is invalid'
finally:
    bpy.data.meshes.remove(probe)
assert not any(o.name.startswith('Office_') for o in bpy.data.objects), 'Office furniture/props remain'
assert not any(o.name.startswith('Vent_ACRoom_') for o in bpy.data.objects), 'Old vent slab blocks the AC doorway'
for y in (5.95, 6.5, 7.5):
    for z in (0.5, 1.5, 2.2):
        hit, point, *_ = wall.ray_cast(Vector((7.6, y, z)), Vector((1, 0, 0)), distance=0.8)
        assert hit and abs(point.x - 7.856) < 0.01, (y, z, 'west wall missing')
for x in (8.10, 8.45, 8.80):
    hit, point, *_ = wall.ray_cast(Vector((x, 7.65, 1.4)), Vector((0, 1, 0)), distance=0.8)
    assert hit and point.y < 8.0, (x, 'extra opening in north wall')
assert bpy.data.objects['ProDoorLeaf_Alpha'].location.x < 10.5, 'Alpha door belongs at southern opening'
assert bpy.data.objects.get('ProDoorLeaf_EntryPantry'), 'Pantry door must be preserved'
assert bpy.data.objects.get('ProDoorLeaf_Utility'), 'AC room access must be preserved'
print('PASS ALPHA: valid closed wall mesh, no office furniture, plan-aligned entry and AC door')
