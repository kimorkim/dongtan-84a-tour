"""Q12 independent checks against A02-102 printed dimensions, on real saved meshes."""
import bpy
from mathutils import Vector

bpy.context.view_layer.update()
deps=bpy.context.evaluated_depsgraph_get()

def face(objname,origin,direction):
    obj=bpy.data.objects[objname].evaluated_get(deps)
    inv=obj.matrix_world.inverted()
    hit,p,n,_=obj.ray_cast(inv @ Vector(origin),inv.to_3x3() @ Vector(direction))
    assert hit,('Missing wall',objname,origin,direction)
    return obj.matrix_world @ p

checks=[]

def nearest_wall(origin,direction):
    hits=[]
    for o in bpy.data.objects:
        if not o.name.startswith('ExactWall_'): continue
        inv=o.matrix_world.inverted()
        hit,p,_,_=o.ray_cast(inv@Vector(origin),inv.to_3x3()@Vector(direction))
        if hit:
            p=o.matrix_world@p; hits.append(((p-Vector(origin)).length,p))
    assert hits,('No structural boundary',origin,direction)
    return min(hits,key=lambda v:v[0])[1]
def measure(label,value,expected,tol=.001):
    checks.append((label,value,expected))
    assert abs(value-expected)<=tol,(label,round(value*1000,2),round(expected*1000,2),'mm')

for y in (1.5,2.5,3.8):
    xw=face('ExactWall_3',(10.5,y,1.5),(-1,0,0)).x
    xe=face('ExactWall_2',(10.5,y,1.5),(1,0,0)).x
    yw=face('ExactWall_2',(13.4,y,1.5),(-1,0,0)).x
    ye=face('ExactWall_5',(13.4,y,1.5),(1,0,0)).x
    measure(f'Bed2 width at y{y}',xe-xw,2.700)
    measure(f'Bed3 width at y{y}',ye-yw,3.000)
    measure(f'Bed2/3 partition at y{y}',yw-xe,.130)
    lw=face('ExactWall_4',(6.5,y,1.5),(-1,0,0)).x
    le=face('ExactWall_3',(6.5,y,1.5),(1,0,0)).x
    measure(f'Living width at y{y}',le-lw,4.500)
    measure(f'Living/Bed2 wall at y{y}',xw-le,.270)
for y in (2.5,3.5,4.5):
    a=face('ExactWall_13',(2.5,y,1.5),(-1,0,0)).x
    b=face('ExactWall_4',(2.5,y,1.5),(1,0,0)).x
    measure(f'Master width at y{y}',b-a,3.600)
south=nearest_wall((3.95,3.5,1.5),(0,-1,0)).y
north=nearest_wall((3.95,3.5,1.5),(0,1,0)).y
measure('Master clear depth',north-south,3.600)
for tag,x,y,west,east,width in [
    ('alpha',9.0,6.5,'ExactWall_8','ExactWall_7',2.400),
    ('pantry',11.0,7.5,'ExactWall_7','ExactWall_7',1.190),
    ('foyer',12.2,7.5,'ExactWall_7','ExactWall_5',1.600),
    ('master bath',3.4,7.5,'ExactWall_11','ExactWall_11',1.500)]:
    a=face(west,(x,y,1.8),(-1,0,0)).x
    b=face(east,(x,y,1.8),(1,0,0)).x
    measure(tag+' clear width',b-a,width)

def bounds(obj):
    p=[obj.matrix_world @ Vector(c) for c in obj.bound_box]
    return [min(v[i] for v in p) for i in range(3)],[max(v[i] for v in p) for i in range(3)]

for tag,width,sill,height in [('Bed2',1.700,1.120,1.150),('Bed3',2.000,1.120,1.150),
                               ('Living',3.600,.270,2.000),('Kitchen',1.200,1.120,1.150),
                               ('Dress',.900,1.420,.850),('KitchenBalcony',.900,1.120,1.050),
                               ('MasterBalcony',1.500,.270,2.000),('Refuge',.900,1.120,1.150)]:
    prefix={'MasterBalcony':'Q4_BalconyWindow','Refuge':'Q4_RefugeWindow'}.get(tag,'Win_'+tag)
    lo,hi=bounds(bpy.data.objects[prefix+'_Sill'])
    measure(tag+' window width',hi[0]-lo[0],width)
    measure(tag+' window sill',lo[2],sill)
    _,top=bounds(bpy.data.objects[prefix+'_Head'])
    measure(tag+' window height',top[2]-lo[2],height)
for tag,width in [('1800',1.8),('1400',1.4)]:
    lo,hi=bounds(bpy.data.objects['Q11_Desk'+tag+'_Top'])
    measure(tag+' preserved desktop',hi[1]-lo[1],width)
for room,x,northwall in [('Bed2',10.7,'ExactWall_2'),('Bed3',13.7,'ExactWall_5')]:
    n=face(northwall,(x,2.5,.3),(0,1,0)).y
    s=face('Q12_'+room+'_SillWall',(x,2.5,.3),(0,-1,0)).y
    measure(room+' clear depth',n-s,3.410)
for tag,x,w,expected in [('alpha',8.2,'ExactWall_8',2.280),('master bath',3.5,'ExactWall_11',2.200)]:
    n=face(w,(x,6.5,1.8),(0,1,0)).y
    s=face(w,(x,6.5,1.8),(0,-1,0)).y
    measure(tag+' clear depth',n-s,expected)
for name,width,depth in [('Floor_Foyer',1.6,1.8),('Floor_EntrancePantry',1.19,1.8),('Q6_UtilityFloor',1.525,1.125)]:
    lo,hi=bounds(bpy.data.objects[name])
    measure(name+' clear width',hi[0]-lo[0],width)
    measure(name+' clear depth',hi[1]-lo[1],depth)
# Independent wall faces also verify the provisional utility bay, not just its floor.
a=face('ExactWall_8',(9.4,8.9,1.8),(-1,0,0)).x
b=face('ExactWall_7',(9.4,8.9,1.8),(1,0,0)).x
measure('Utility provisional wall width',b-a,1.525)
a=face('ExactWall_7',(9.9,8.9,1.8),(0,-1,0)).y
b=face('ExactWall_7',(9.9,8.9,1.8),(0,1,0)).y
measure('Utility provisional wall depth',b-a,1.125)
a=face('ExactWall_13',(1.5,9.0,1.8),(-1,0,0)).x
b=face('ExactWall_11',(1.5,9.0,1.8),(1,0,0)).x
measure('Dress north clear width',b-a,1.970)
lo,hi=bounds(bpy.data.objects['AC_Condenser_Body'])
measure('Condenser preserved length',hi[1]-lo[1],.900)
lo,hi=bounds(bpy.data.objects['Q4_BalconyDoor_Threshold'])
measure('Balcony sliding nominal width',hi[0]-lo[0],1.500)
lo,hi=bounds(bpy.data.objects['Q4_RefugeDoor_Header'])
measure('Refuge nominal width',hi[1]-lo[1],.750)
measure('General ceiling height',face('Ceiling_Slab',(12,2.5,1.5),(0,0,1)).z,2.3)
measure('Living coffer height',face('Ceiling_Coffer',(6.5,3,1.5),(0,0,1)).z,2.4)
for tag in ('Bed2','Bed3','Master'):
    lo,hi=bounds(bpy.data.objects['Q12_'+tag+'_DoorHeader'])
    measure(tag+' nominal door height',lo[2],2.2)
railparts=[o for o in bpy.data.objects if o.name.startswith('Q2_Rail_Living_')]
measure('Living rail top above main FL',max(bounds(o)[1][2] for o in railparts),.830)
railparts=[o for o in bpy.data.objects if o.name.startswith('Q4_BalconyRail_')]
measure('Balcony rail top above main FL',max(bounds(o)[1][2] for o in railparts),.830)
assert len([o for o in bpy.data.objects if o.name.startswith('Q11_Equipment_')])==223
assert bpy.data.objects.get('Q10_Wardrobe_Back') and bpy.data.objects.get('Q10_Mattress')
assert bpy.data.objects.get('Q7_MiddleDoor_Glass') and bpy.data.objects.get('ProDoorLeaf_MasterBalcony_Glass')
assert not any(o.name.startswith(('Front_Door_','NewWall_North','NewWall_EastN')) for o in bpy.data.objects)
assert bpy.context.scene.get('Q12_dimensions_version')==1
for name in ('Cam_Living_POV','Cam_Kitchen_POV','Cam_MasterBed_POV','Cam_Dress_POV'):
    assert bpy.data.objects[name].location.z>1,('Legacy camera at origin',name)
print(f'PASS Q12: {len(checks)} real-mesh dimension checks, 223 equipment parts and approved options retained')
