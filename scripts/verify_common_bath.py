"""Run inside Blender: catch a filled sink, box toilet, tiled door or blocked shower."""
import bpy
from mathutils import Vector

bpy.context.view_layer.update()
scene = bpy.context.scene
deps = bpy.context.evaluated_depsgraph_get()

def ray(origin, direction, distance=3):
    hit, point, _, _, obj, _ = scene.ray_cast(deps, Vector(origin), Vector(direction), distance=distance)
    assert hit, ('missing surface', origin)
    return point, obj

point, obj = ray((14.62, 5.0, 1.2), (0, 0, -1))
assert 0.67 < point.z < 0.79, ('Sink must be recessed, not a solid countertop', point.z, obj.name)
point, _ = ray((14.43, 5.38, 1.1), (0, 0, -1))
assert 0.86 < point.z < 0.90, 'Countertop rim is missing'
toilet = bpy.data.objects.get('Q8_Toilet_Body')
assert toilet and len(toilet.data.vertices) > 100, 'Toilet must have a curved ceramic body'
for obj in bpy.data.objects:
    if obj.name.startswith(('Q8_WetTile_', 'Q8_Toilet_', 'Q8_Shower_')):
        points = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
        assert all(13.38 <= p.x <= 14.985 and 5.63 <= p.y <= 7.54 and -0.01 <= p.z <= 2.30 for p in points), (obj.name, 'outside bathroom')
for origin, direction in [((13.95, 6.0, 1.4), (0, 1, 0)), ((14.0, 5.1, 1.3), (1, 0, 0))]:
    hit, point, _, _, obj, _ = scene.ray_cast(deps, Vector(origin), Vector(direction), distance=0.70)
    assert not hit, ('Blocked walking/view corridor', obj.name if obj else '', tuple(point))
for name in ('Mat_Q8_WallTile', 'Mat_Q8_FloorTile'):
    mat = bpy.data.materials.get(name)
    assert mat and any(n.type == 'TEX_IMAGE' and n.image for n in mat.node_tree.nodes), 'Photo tile texture missing'
assert bpy.data.objects.get('Q8_Shower_Drain') and bpy.data.objects.get('Q8_Toilet_Tank')
point, obj = ray((14.0, 7.19, 1.85), (1, 0, 0))
assert obj.name.startswith('Q8_Shower_Rail') and point.x < 14.456, ('Shower rail buried in service shaft', obj.name, tuple(point))
point, obj = ray((14.0, 7.0, 1.2), (1, 0, 0))
assert obj.name.startswith('Q8_WetTile_ShaftW'), 'Old mismatched tile exposed on service shaft'
point, obj = ray((14.0, 7.0, 2.2), (-1, 0, 0))
assert obj.name.startswith('Q8_WetTile_W_'), 'Old mismatched tile exposed on west wall'
assert bpy.data.objects.get('Q8_Dry_DoorN') and bpy.data.objects.get('Q8_Med_OpenShelf0')
print('PASS COMMON BATH: recessed sink, curved toilet, photo tiles, bounded fixtures and open passages')
