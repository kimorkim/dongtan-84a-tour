import bpy, json
from mathutils import Vector
for o in bpy.data.objects:
    if o.type != 'MESH': continue
    p=[o.matrix_world @ Vector(c) for c in o.bound_box]
    lo=[round(min(v[i] for v in p),3) for i in range(3)]
    hi=[round(max(v[i] for v in p),3) for i in range(3)]
    if 'Bed2' in o.name or (lo[0]<11.87 and hi[0]>9.16 and lo[1]<4.42 and hi[1]>.51 and lo[2]<2.3):
        print(json.dumps([o.name,lo,hi]))
sc=bpy.context.scene; deps=bpy.context.evaluated_depsgraph_get()
for z in (.3,1.2,2.25):
    for x in (9.25,9.6,10.3,11.3,11.78):
        h,p,_,_,o,_=sc.ray_cast(deps,Vector((x,1.05,z)),Vector((0,-1,0)))
        print('SOUTH',x,z,tuple(round(v,3) for v in p),o.name if h else None)
