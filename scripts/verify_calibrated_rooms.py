"""Room semantics retained after Q12 changes the old absolute coordinates."""
import bpy
import bmesh
from mathutils import Vector
from plan_dimensions import ROOMS, point

def bounds(o):
    p=[o.matrix_world @ Vector(c) for c in o.bound_box]
    return [min(v[i] for v in p) for i in range(3)],[max(v[i] for v in p) for i in range(3)]

def verify_room(kind):
    bpy.context.view_layer.update()
    sc=bpy.context.scene; deps=bpy.context.evaluated_depsgraph_get()
    def ray(origin,direction,distance=3):
        x,y=point(origin[0],origin[1])
        return sc.ray_cast(deps,Vector((x,y,origin[2])),Vector(direction),distance=distance)
    def clear(origin,distance=.6,direction=(0,0,-1)):
        hit,p,_,_,o,_=ray(origin,direction,distance)
        if direction==(0,0,-1):
            assert hit and abs(p.z)<.03,('Blocked floor',kind,origin,o.name if o else None,p)
        else: assert not hit,('Blocked route',kind,origin,o.name if o else None,p)

    if kind=='alpha':
        wall=bpy.data.objects['ExactWall_8']; bm=bmesh.new(); bm.from_mesh(wall.data)
        assert all(e.is_manifold for e in bm.edges), 'Alpha wall is not closed'
        bm.free(); assert all(p.area>1e-10 for p in wall.data.polygons)
        assert not any(o.name.startswith(('Office_','Vent_ACRoom_')) for o in bpy.data.objects)
        r=ROOMS['alpha']
        ruglo,rughi=bounds(bpy.data.objects['Q2_Dining_Rug'])
        assert rughi[0]<=7.735-.05,'Dining rug touches kitchen side of alpha wall'
        assert bpy.data.objects.get('ProDoorLeaf_EntryPantry') and bpy.data.objects.get('ProDoorLeaf_Utility')
        for y in (6.0,6.6,7.6):
            hit,p,_,_,o,_=sc.ray_cast(deps,Vector((7.5,y,1.5)),Vector((1,0,0)),distance=.5)
            assert hit and abs(p.x-7.735)<.025,('Alpha west wall',y,o.name if o else None,p)
    elif kind=='utility':
        r=ROOMS['utility']
        assert not bpy.data.objects.get('Floor_KitchenBalcony') and not bpy.data.objects.get('Floor_ACOutdoor')
        for o in bpy.data.objects:
            if o.name.startswith('AC_Condenser_'):
                lo,hi=bounds(o)
                assert r[0]<lo[0]<hi[0]<r[1] and r[2]<lo[1]<hi[1]<r[3],(o.name,lo,hi)
        assert bpy.data.objects.get('Q6_UtilityFloor')
    elif kind=='foyer':
        assert not bpy.data.objects.get('Foyer_Mirror_Glass')
        assert bpy.data.objects.get('ProDoorLeaf_EntryPantry_R') and bpy.data.objects.get('Q12_Entry_Leaf')
        glass=bpy.data.objects['Q7_MiddleDoor_Glass']
        bs=glass.active_material.node_tree.nodes.get('Principled BSDF')
        assert bs.inputs['Roughness'].default_value>.35
        assert bounds(glass)[1][0]<ROOMS['foyer'][0], 'Sliding door blocks foyer'
        r=ROOMS['pantry']
        for o in bpy.data.objects:
            if o.name.startswith(('Q7_PantryShelf_','Q7_PantryPost_','Q7_PantryProp_')):
                lo,hi=bounds(o)
                assert r[0]-.015<=lo[0]<=hi[0]<=r[1]+.015 and r[2]-.015<=lo[1]<=hi[1]<=r[3]+.015,(o.name,lo,hi)
        clear((12.33,6.50,1.4),.9,(0,-1,0)); clear((12.0,6.7,1.4),.85,(-1,0,0))
    elif kind=='bath':
        hit,p,_,_,o,_=ray((14.62,5.,1.2),(0,0,-1))
        assert hit and .67<p.z<.79,('Sink recess',p,o.name if o else None)
        assert len(bpy.data.objects['Q8_Toilet_Body'].data.vertices)>100
        for name in ('Mat_Q8_WallTile','Mat_Q8_FloorTile'):
            assert any(n.type=='TEX_IMAGE' and n.image for n in bpy.data.materials[name].node_tree.nodes)
        assert all(bpy.data.objects.get(n) for n in ('Q8_Shower_Drain','Q8_Toilet_Tank','Q8_Dry_DoorN','Q8_Med_OpenShelf0'))
        clear((13.95,6.0,1.4),.65,(0,1,0))
        # The shower's shaft wall and lining must remain, without buried fittings.
        hit,p,_,_,o,_=ray((14.,7.,1.2),(1,0,0))
        assert hit and o.name.startswith('Q8_WetTile_ShaftW'),('Shower shaft lining',o.name if o else None,p)
        hit,p,_,_,o,_=ray((14.,7.,2.2),(-1,0,0))
        assert hit and o.name.startswith('Q8_WetTile_W_'),('Bath west lining',o.name if o else None,p)
    elif kind=='floor':
        floor=bpy.data.objects['Exact_Floor']; mat=bpy.data.materials['Mat_Q9_LightOak']
        uv=floor.data.uv_layers['FloorUV']
        for f in floor.data.polygons:
            if f.normal.z>.8:
                assert floor.data.materials[f.material_index]==mat
                for loop in f.loop_indices:
                    p=floor.data.vertices[floor.data.loops[loop].vertex_index].co
                    v=uv.data[loop].uv
                    assert abs(v.x-p.x/3)<1e-5 and abs(v.y-p.y/1.04)<1e-5
        assert len([n for n in mat.node_tree.nodes if n.type=='TEX_IMAGE' and min(n.image.size)>=2048])==3
        assert not any(bpy.data.objects.get(n) for n in ('Floor_AlphaRoom','Floor_Bedroom2','Floor_Bedroom3','Floor_MasterBed','Floor_DressRoom'))
        assert bpy.data.objects['Floor_Foyer'].active_material.name=='Mat_Q7_Stone'
        assert bpy.data.objects['Floor_CommonBath'].active_material.name=='Mat_Q8_Grout'
    elif kind=='yuna':
        r=ROOMS['yuna']
        assert not any(o.name.startswith(('Bed3_','Wardrobe_Bed3_')) for o in bpy.data.objects)
        assert bounds(bpy.data.objects['Q10_Mattress'])[1][2]<.5
        lo,hi=bounds(bpy.data.objects['Q10_Wardrobe_Back'])
        assert hi[2]>=2.28 and lo[1]>3.65 and hi[1]<=r[3]+.005
        for n in ('Win_Bed3_Glass1','Win_Bed3_Glass2'):
            assert bpy.data.objects[n].active_material.node_tree.nodes.get('Principled BSDF').inputs['Alpha'].default_value<.1
        for x,y in ((12.55,4.25),(13.4,2.75),(13.5,1.25),(13.55,3.25)):
            hit,p,_,_,o,_=sc.ray_cast(deps,Vector((x,y,1.8)),Vector((0,0,-1)))
            assert hit and abs(p.z)<.03,('Yuna room access',x,y,o.name if o else None)
        assert bpy.data.objects.get('Q10_Bunny_Body')
    elif kind=='study':
        for color,front in [('Black',10.930),('Grey',11.030)]:
            parts=[o for o in bpy.data.objects if o.name.startswith('Q11_Aeron'+color+'_')]
            assert len([o for o in parts if '_Caster' in o.name])==10
            assert bounds(bpy.data.objects['Q11_Aeron'+color+'_SeatFrame'])[1][0]>front+.01
            for o in parts:
                lo,hi=bounds(o)
                assert hi[2]<.71 or hi[0]<front,('Chair/tabletop overlap',o.name,hi)
        for x,y in ((9.8,1.3),(9.8,2.7),(9.8,4.0)):
            hit,p,_,_,o,_=sc.ray_cast(deps,Vector((x,y,1.85)),Vector((0,0,-1)))
            assert hit and abs(p.z)<.03,('Study aisle',x,y,o.name if o else None)
        for name,diag in [('Dell27_L',27),('Dell27_R',27),('Gaming32',32)]:
            o=bpy.data.objects['Q11_Equipment_'+name+'_Screen']
            assert abs(o.dimensions.length-diag*.0254)<.004
        r=ROOMS['study']
        for o in bpy.data.objects:
            if o.name.startswith('Q11_Equipment_'):
                lo,hi=bounds(o)
                assert r[0]<lo[0]<=hi[0]<r[1] and r[2]<lo[1]<=hi[1]<r[3],('Equipment outside study',o.name)
        for side in ('L','R'):
            lo,hi=bounds(bpy.data.objects['Q11_Equipment_A2_'+side+'_Cabinet'])
            assert abs(hi[2]-lo[2]-.1524)<.001 and abs(hi[1]-lo[1]-.1016)<.001
            assert abs(lo[2]-.74)<.001
        lo,hi=bounds(bpy.data.objects['Q11_Equipment_Desktop_Case'])
        assert lo[2]>=.02 and hi[2]<.60 and lo[0]>11.20 and hi[1]<4.00,'Tower blocks chair/desk leg'
        if sc.get('Q13_study_bookcases'):
            import runpy
            from pathlib import Path
            runpy.run_path(str(Path(__file__).with_name('verify_study_bookcases.py')))
    else: raise ValueError(kind)
    print('PASS Q12 room regression:',kind)
