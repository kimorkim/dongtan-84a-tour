# Q12 compatibility dispatch: historical generators still verify their original frame.
import os, sys, bpy
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
def verify_legacy():
    """Q11: check the real room envelope, desk clearances and chair dimensions in Blender."""
    import bpy
    from mathutils import Vector

    bpy.context.view_layer.update()
    sc = bpy.context.scene
    deps = bpy.context.evaluated_depsgraph_get()
    for z in (.3, 2.25):
        for x in (9.25, 9.6, 10.3, 11.3, 11.78):
            hit, p, _, _, obj, _ = sc.ray_cast(deps, Vector((x, 1.05, z)), Vector((0,-1,0)))
            assert hit and abs(p.y-.85)<.006, ('Uneven south wall',x,z,p,obj.name if obj else None)

    def bounds(obj):
        pts=[obj.matrix_world @ Vector(c) for c in obj.bound_box]
        return [min(p[i] for p in pts) for i in range(3)], [max(p[i] for p in pts) for i in range(3)]

    desks=[]
    for key, w, d in [('1800',1.8,.8),('1400',1.4,.7)]:
        obj=bpy.data.objects['Q11_Desk'+key+'_Top']
        lo,hi=bounds(obj)
        assert abs(hi[1]-lo[1]-w)<.001 and abs(hi[0]-lo[0]-d)<.001, ('Wrong desk size',key)
        assert 9.20<lo[0]<hi[0]<11.869 and .875<lo[1]<hi[1]<4.22, ('Desk outside room',key,lo,hi)
        assert abs(hi[2]-.74)<.001
        desks.append((lo,hi))
    assert desks[1][0][1]-desks[0][1][1] >= .05, 'Desks touch'
    for color in ('Black','Grey'):
        parts=[o for o in bpy.data.objects if o.name.startswith('Q11_Aeron'+color+'_')]
        assert parts and len([o for o in parts if '_Caster' in o.name])==10
        a=[bounds(o) for o in parts]
        lo=[min(v[0][i] for v in a) for i in range(3)]
        hi=[max(v[1][i] for v in a) for i in range(3)]
        assert .67<hi[1]-lo[1]<.77 and .90<hi[2]<1.10, ('Chair envelope',color,lo,hi)
        assert lo[0]>10.4 and hi[0]<11.29, ('Chair was not tucked in',color,lo,hi)
        assert hi[1]<4.21 and lo[1]>.88
        for o in parts:
            assert o.active_material.name.startswith('Mat_Q11_'+color) or 'Metal' in o.active_material.name
    for y in (1.2,1.8,2.7,3.5,4.05):
        hit,p,_,_,obj,_=sc.ray_cast(deps,Vector((9.9,y,1.85)),Vector((0,0,-1)))
        assert hit and abs(p.z)<.03, ('Main aisle blocked',y,obj.name if obj else None)
    for side in ('A','B'):
        lo,hi=bounds(bpy.data.objects['ProDoorHandle_Bed2_'+side])
        assert 9.16<lo[0]<hi[0]<10.15 and 3.3<lo[1]<hi[1]<4.5, 'Detached door handle'
    assert not any(o.name.startswith('Bed2_') for o in bpy.data.objects), 'Old bed remains'
    assert abs(bpy.data.objects['Win_Bed2_Mullion'].location.y-.80)<.001
    assert bpy.data.objects['Exact_Floor'].data.materials.get('Mat_Q9_LightOak')
    for name, diagonal in [('Dell27_L',27),('Dell27_R',27),('Gaming32',32)]:
        screen=bpy.data.objects['Q11_Equipment_'+name+'_Screen']
        assert abs((screen.dimensions.x**2+screen.dimensions.y**2+screen.dimensions.z**2)**.5-diagonal*.0254)<.004, ('Wrong display diagonal',name)
    for name in ('MacBook_Closed','MacBook_Stand','Keyboard1800_Base','Mouse1800_Body',
                 'Keyboard1400_Base','Mouse1400_Body','GamingRiser_Top','Desktop_Case',
                 'Arm27_L_Clamp','Arm27_R_Clamp','A2_L_Cabinet','A2_R_Cabinet'):
        assert bpy.data.objects.get('Q11_Equipment_'+name), ('Equipment missing',name)
    for obj in bpy.data.objects:
        if obj.name.startswith('Q11_Equipment_'):
            lo,hi=bounds(obj)
            assert 11.0<lo[0]<=hi[0]<11.869 and .90<lo[1]<=hi[1]<4.20, ('Equipment outside desk bay',obj.name,lo,hi)
    for side in ('L','R'):
        lo,hi=bounds(bpy.data.objects['Q11_Equipment_A2_'+side+'_Cabinet'])
        assert abs(hi[2]-lo[2]-.1524)<.001 and abs(hi[1]-lo[1]-.1016)<.001
        assert abs(lo[2]-.74)<.001
    lo,hi=bounds(bpy.data.objects['Q11_Equipment_Desktop_Case'])
    assert lo[2]>=.02 and hi[2]<.60 and lo[0]>11.29 and hi[1]<3.90, 'Tower blocks chair/desk leg'
    for color,front in [('Black',11.02),('Grey',11.12)]:
        seatlo,seathi=bounds(bpy.data.objects['Q11_Aeron'+color+'_SeatFrame'])
        assert seathi[0]>front+.01, 'Chair seat not under desktop'
        for o in bpy.data.objects:
            if o.name.startswith('Q11_Aeron'+color+'_'):
                lo,hi=bounds(o)
                assert hi[2]<.71 or hi[0]<front, ('Chair intersects tabletop',o.name)
    print('PASS Q11b: flush wall, desk equipment/dimensions, tucked chairs without tabletop overlap, clear aisle and shared oak')

if bpy.context.scene.get("Q12_dimensions_version"):
    from verify_calibrated_rooms import verify_room
    verify_room('study')
else:
    verify_legacy()
