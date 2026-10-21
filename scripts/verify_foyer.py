# Q12 compatibility dispatch: historical generators still verify their original frame.
import os, sys, bpy
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
def verify_legacy():
    """Run inside Blender: modelhouse foyer details and unobstructed entry paths."""
    import bpy
    from mathutils import Vector

    assert bpy.data.objects.get('Q7_MiddleDoor_Glass'), 'Frosted sliding middle door missing'
    assert not bpy.data.objects.get('Foyer_Mirror_Glass'), 'Old mirror blocks pantry opening'
    assert bpy.data.objects.get('ProDoorLeaf_EntryPantry_R'), 'Pantry needs two open hinged leaves'
    for obj in bpy.data.objects:
        if obj.name.startswith(('Q7_PantryShelf_', 'Q7_PantryPost_', 'Q7_PantryProp_')):
            points = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
            assert all(10.556 <= p.x <= 11.588 and 5.775 <= p.y <= 7.65 for p in points), (obj.name, 'outside pantry')
    for obj in (bpy.data.objects['ProDoorLeaf_EntryPantry'], bpy.data.objects['ProDoorLeaf_EntryPantry_R']):
        assert obj.dimensions.x > 0.40 and obj.dimensions.y < 0.06, 'Pantry leaves must park inside, not across opening'
    glass = bpy.data.objects['Q7_MiddleDoor_Glass']
    assert max((glass.matrix_world @ Vector(c)).x for c in glass.bound_box) < 11.775, 'Middle door obstructs foyer opening'
    deps = bpy.context.evaluated_depsgraph_get()
    for origin, direction in [((12.33, 6.50, 1.4), (0, -1, 0)),
                              ((12.0, 6.70, 1.4), (-1, 0, 0))]:
        hit, point, _, _, obj, _ = bpy.context.scene.ray_cast(deps, Vector(origin), Vector(direction), distance=0.95)
        assert not hit, (obj.name if obj else '', 'entry/pantry passage blocked', tuple(point))
    frost = glass.active_material.node_tree.nodes.get('Principled BSDF')
    assert frost.inputs['Roughness'].default_value > 0.35
    assert bpy.data.objects.get('Q7_MiddleDoor_Sensor') and bpy.data.objects.get('Q7_MiddleDoor_Switch')
    print('PASS FOYER: frosted middle door, two pantry leaves, bounded shelves/props, clear passages')

if bpy.context.scene.get("Q12_dimensions_version"):
    from verify_calibrated_rooms import verify_room
    verify_room('foyer')
else:
    verify_legacy()
