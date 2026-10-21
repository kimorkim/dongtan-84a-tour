# Q12 compatibility dispatch: historical generators still verify their original frame.
import os, sys, bpy
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
def verify_legacy():
    """Q10: catch displaced handles, blocked access and room-envelope penetrations."""
    import bpy
    from mathutils import Vector

    def bounds(obj):
        pts = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
        return [min(p[i] for p in pts) for i in range(3)], [max(p[i] for p in pts) for i in range(3)]

    for suffix in ('A', 'B'):
        lo, hi = bounds(bpy.data.objects['ProDoorHandle_Bed3_' + suffix])
        assert 11.963 < lo[0] < hi[0] < 13.0 and 3.3 < lo[1] < hi[1] < 4.4, 'Bed3 handle detached from door or inside west wall'

    required = ['Bed_Base', 'Mattress', 'Wardrobe_Back', 'Bookcase_Back', 'ActivityTop', 'Rug_Center', 'Bunny_Body']
    assert all('Q10_' + n in bpy.data.objects for n in required), 'Yuna furnishings missing'
    lo, hi = bounds(bpy.data.objects['Q10_Wardrobe_Back'])
    assert lo[1] > 3.6 and hi[2] >= 2.28, 'Basic built-in must be beside the entrance, fitted to the ceiling'
    for obj in bpy.data.objects:
        if obj.name.startswith('Q10_') and obj.type == 'MESH':
            lo, hi = bounds(obj)
            assert 11.963 <= lo[0] <= hi[0] <= 14.981, (obj.name, 'east/west wall penetration', lo, hi)
            south_limit=.49 if obj.name.startswith('Q10_Window') else .849
            assert south_limit <= lo[1] <= hi[1] <= 4.219, (obj.name, 'north/south wall penetration', lo, hi)
            assert lo[2] >= -.001 and hi[2] <= 2.30, (obj.name, 'floor/ceiling penetration')
            if not obj.name.startswith(('Q10_Wardrobe','Q10_Skirt','Q10_Window')):
                overlaps = hi[0]>13.15 and lo[0]<14.91 and hi[1]>3.15 and lo[1]<3.59 and hi[2]>.03 and lo[2]<2.19
                assert not overlaps, ('Furniture intersects built-in door swing strip',obj.name)
    lo, hi = bounds(bpy.data.objects['Q10_Mattress'])
    assert hi[2] < .5, 'Bed is no longer low'
    assert bounds(bpy.data.objects['Q10_Headboard'])[1][1] < 2.92, 'Bed head blocks the entrance-to-room passage'
    for name in ('Win_Bed3_Glass1','Win_Bed3_Glass2'):
        shader=bpy.data.objects[name].data.materials[0].node_tree.nodes.get('Principled BSDF')
        assert shader.inputs['Alpha'].default_value < .1, 'Bedroom window must use the tour alpha-glass path, not dark refraction'

    sc = bpy.context.scene
    deps = bpy.context.evaluated_depsgraph_get()
    # Door is open, not a sheet across the opening; no furniture in the central play/walking strip.
    for x,y in [(12.5,4.33),(12.6,3.65),(13.4,3.3),(13.4,2.75),(13.5,1.2)]:
        hit, loc, _, _, obj, _ = sc.ray_cast(deps, Vector((x,y,1.8)), Vector((0,0,-1)))
        assert hit and abs(loc.z) < .03, ('Walking/play strip blocked', x,y,obj.name if obj else None, loc)
    for origin, direction, expected in [
        ((13.4,2.9,1.7), (1,0,0), 'ExactWall_5'),
        ((13.4,3.4,1.7), (-1,0,0), 'ExactWall_2'),
        ((13.4,2.3,1.7), (0,1,0), 'Q10_Wardrobe_Door'),
        ((13.8,2.3,1.7), (0,-1,0), 'Win_Bed3_Glass'),
    ]:
        hit, loc, normal, _, obj, _ = sc.ray_cast(deps, Vector(origin), Vector(direction))
        assert hit and obj.name.startswith(expected), ('Broken room envelope', origin,direction,obj)
        assert normal.dot(Vector(direction)) < -.9, ('Inverted wall/window face',obj.name)
    # The window wall used to step back by 320mm between corner piers.
    for z in (.20,2.27):
        for x in (12.10,12.80,13.40,14.70):
            hit,loc,_,_,obj,_=sc.ray_cast(deps,Vector((x,1.01,z)),Vector((0,-1,0)))
            assert hit and abs(loc.y-.85)<.012, ('Window finish line is not straight',x,z,loc,obj)
    # Sample the whole door-opening strip, not just one standing point.
    for x in (13.2,13.65,14.1,14.6):
        for y in (3.12,3.36,3.55):
            hit,loc,_,_,obj,_=sc.ray_cast(deps,Vector((x,y,1.85)),Vector((0,0,-1)))
            assert hit and abs(loc.z)<.03, ('Built-in door clearance blocked',x,y,obj.name if obj else None)
    # Intersecting petal disks once produced black coplanar patches in Cycles.
    tops=[]
    for obj in bpy.data.objects:
        if obj.name.startswith('Q10_Rug') and obj.type == 'MESH':
            evaluated=obj.evaluated_get(deps)
            inverse=evaluated.matrix_world.inverted()
            hit,loc,_,_=evaluated.ray_cast(inverse @ Vector((13.79,2.58,.1)),inverse.to_3x3() @ Vector((0,0,-1)))
            if hit: tops.append((evaluated.matrix_world @ loc).z)
    assert all(abs(a-b) > .0001 for i,a in enumerate(tops) for b in tops[i+1:]), 'Coplanar rug surfaces overlap'
    assert not any(o.name.startswith(('Bed3_', 'Wardrobe_Bed3_')) for o in bpy.data.objects), 'Old furniture overlaps new room'
    assert bpy.data.objects['Exact_Floor'].data.materials.get('Mat_Q9_LightOak'), 'Shared oak floor lost'
    print('PASS Q10: attached handles, low bed, clear doorway/play strip, intact walls/window and shared oak')

if bpy.context.scene.get("Q12_dimensions_version"):
    from verify_calibrated_rooms import verify_room
    verify_room('yuna')
else:
    verify_legacy()
