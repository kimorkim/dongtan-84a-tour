import bpy
from mathutils import Vector
deps=bpy.context.evaluated_depsgraph_get()
for origin,direction in [((9.4,8.9,1.8),(-1,0,0)),((9.4,8.9,1.8),(1,0,0)),
                         ((9.9,8.9,1.8),(0,-1,0)),((9.9,8.9,1.8),(0,1,0)),
                         ((1.5,9.0,1.8),(-1,0,0)),((1.5,9.0,1.8),(1,0,0)),
                         ((6.5,9.0,1.8),(-1,0,0)),((6.5,9.0,1.8),(1,0,0))]:
    hits=[]
    for o in bpy.data.objects:
        if not o.name.startswith('ExactWall_'): continue
        inv=o.matrix_world.inverted()
        hit,p,_,_=o.ray_cast(inv@Vector(origin),inv.to_3x3()@Vector(direction))
        if hit:
            p=o.matrix_world@p; hits.append(((p-Vector(origin)).length,o.name,tuple(round(v,4) for v in p)))
    print('BOUNDARY',origin,direction,sorted(hits)[:2],flush=True)
