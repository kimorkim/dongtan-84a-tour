"""Q24 independent saved geometry and inward door checks."""
import bpy
import math
import hashlib,json
import numpy as np
from mathutils import Vector

def bounds(name):
    o=bpy.data.objects[name]
    pts=[o.matrix_world@Vector(c) for c in o.bound_box]
    return Vector([min(p[i] for p in pts) for i in range(3)]),Vector([max(p[i] for p in pts) for i in range(3)])

lo,hi=bounds('ProDoorLeaf_MasterBath')
assert lo.x>2.59 and hi.x<3.38, 'Master bathroom door opens into powder room instead of bathroom'
assert lo.y>5.985 and hi.y<6.10, 'Open bathroom door must lie along the inside south wall'
assert bpy.context.scene.get('Q24_master_bath')==1
structure=[(o.name,[list(r) for r in o.matrix_world],[list(v.co) for v in o.data.vertices],
            [list(p.vertices) for p in o.data.polygons]) for o in sorted(bpy.data.objects,key=lambda o:o.name)
           if o.type=='MESH' and o.name.startswith('ExactWall_')]
assert hashlib.sha256(json.dumps(structure).encode()).hexdigest()==bpy.context.scene['Q24_wall_sha256']
for name in ('Q24_Tub','Master_Vanity_Top','Q24_Basin','Q24_Toilet_Bowl',
             'Q24_MirrorCabinet_Back','Q24_Shower_Rail','Q24_FloorDrain','Q24_Threshold'):
    assert bpy.data.objects.get(name), 'Missing '+name
assert not any(o.name.startswith(('Master_Toilet_','Master_Bathtub_','BathProp_Master')) for o in bpy.data.objects)
assert bounds('Q24_Grout_E')[0].x>bounds('Q24_Tile_E_0_0')[0].x+.001, 'Wall tile/grout are coplanar'
assert bounds('Q24_FaucetLever')[1].z<bounds('Q24_MirrorShelf')[0].z-.005, 'Faucet lever intersects shelf'
tilemat=bpy.data.materials['Mat_Q24_WallTile']
image=next(n.image for n in tilemat.node_tree.nodes if n.type=='TEX_IMAGE')
pixels=np.array(image.pixels[:],dtype=np.float32).reshape(-1,4)[:,:3]
assert pixels.std(axis=0).max()<.05, 'Photographed lighting/grout dominates repeating tile'
for o in bpy.data.objects:
    if o.type=='MESH' and o.name.startswith('ProDoorHandle_MasterBath'):
        a,b=bounds(o.name)
        assert a.y>5.983 and a.x>2.59 and b.x<3.40, ('Door handle hits wall',o.name,a,b)
for o in bpy.data.objects:
    if o.type=='MESH' and o.name.startswith(('Q24_Tub','Q24_Basin','Q24_Toilet_','Q24_MirrorCabinet')):
        a,b=bounds(o.name)
        assert a.x>=2.602 and b.x<=4.085 and a.y>=5.985 and b.y<=8.160, ('Fixture outside room',o.name,a,b)
# Real cavity, not a rectangular solid pretending to be a basin/tub.
deps=bpy.context.evaluated_depsgraph_get()
for x,y,top in [(3.79,6.90,.80),(3.34,7.80,.40)]:
    hit,p,_,_,o,_=bpy.context.scene.ray_cast(deps,Vector((x,y,1.0)),Vector((0,0,-1)))
    assert hit and p.z<top, ('Blocked basin cavity',x,y,p.z,o.name if o else None)
# Fixtures must stay outside the entire quarter-circle swept by the 740mm leaf.
for degrees in range(0,91,5):
    angle=math.radians(degrees)
    for radius in (.12,.30,.50,.72):
        x=2.610+radius*math.sin(angle); y=6.010+radius*math.cos(angle)
        for z in (.35,.70,1.1):
            for o in bpy.data.objects:
                if o.type=='MESH' and o.name.startswith(('Q24_Toilet_','Q24_Basin','Master_Vanity_Top')):
                    a,b=bounds(o.name)
                    assert not (a.x-.025<x<b.x+.025 and a.y-.025<y<b.y+.025 and a.z-.025<z<b.z+.025), ('Door sweep hits fixture',degrees,o.name)
print('PASS Q24: inward bathroom door/sweep; hollow basin/tub; fixtures inside retained envelope')
