# Q12 compatibility dispatch: historical generators still verify their original frame.
import os, sys, bpy
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
def verify_legacy():
    """Blender regression: AC room enclosure, floor and condenser containment."""
    import bpy
    from mathutils import Vector

    assert not bpy.data.objects.get('Floor_KitchenBalcony'), 'Duplicate/oversized utility floor remains'
    assert bpy.data.objects.get('Q6_UtilityFloor'), 'Plan-aligned utility floor missing'
    for obj in bpy.data.objects:
        if obj.name.startswith('AC_Condenser_'):
            points = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
            assert all(8.662 < p.x < 10.181 and 8.194 < p.y < 9.30 for p in points), (obj.name, 'intersects room boundary')
    scene = bpy.context.scene
    deps = bpy.context.evaluated_depsgraph_get()
    for name, origin, direction, axis, expected in [
            ('west wall', (9.4, 8.6, 1.6), (-1, 0, 0), 0, 8.662),
            ('east wall', (9.9, 8.6, 1.6), (1, 0, 0), 0, 10.181),
            ('north vent', (9.4, 8.8, 1.6), (0, 1, 0), 1, 9.30),
            ('floor', (9.4, 8.6, 0.5), (0, 0, -1), 2, 0.014)]:
        hit, point, *_ = scene.ray_cast(deps, Vector(origin), Vector(direction), distance=1.5)
        assert hit and abs(point[axis] - expected) < 0.18, (name, tuple(point), 'boundary missing/misplaced')
    print('PASS UTILITY: enclosed room, single bounded floor, condenser clear of walls')

if bpy.context.scene.get("Q12_dimensions_version"):
    from verify_calibrated_rooms import verify_room
    verify_room('utility')
else:
    verify_legacy()
