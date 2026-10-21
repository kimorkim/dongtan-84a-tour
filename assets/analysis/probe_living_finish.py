import bpy,json
from mathutils import Vector
from pathlib import Path
bpy.context.view_layer.update()
rows=[]
for o in bpy.data.objects:
    if o.type!='MESH': continue
    pts=[o.matrix_world@Vector(c) for c in o.bound_box]
    lo=[min(p[i] for p in pts) for i in range(3)]; hi=[max(p[i] for p in pts) for i in range(3)]
    if 4.0<lo[0]<8.9 and .0<lo[1]<5.8 and hi[2]<2.6:
        rows.append(dict(name=o.name,lo=lo,hi=hi,mats=[m.name for m in o.data.materials if m]))
Path('assets/analysis/q15_living_objects.json').write_text(json.dumps(rows,indent=2))
wall=bpy.data.objects['ExactWall_4']
for y in (.92,1,2,3,4,4.6,4.8,5.1,5.6,5.75):
    hits=[]
    for z in (.4,1.5,2.25):
        hit,p,_,_=wall.ray_cast(Vector((4.7,y,z)),Vector((-1,0,0)))
        hits.append(tuple(round(v,3) for v in p) if hit else None)
    print('WEST WALL',y,hits,flush=True)
print('LIVING OBJECTS',[(r['name'],r['lo'],r['hi']) for r in rows if any(s in r['name'] for s in ('Curtain','Sheer','ArtWall','Rug','Coffee','Pouf','Console','TV_'))],flush=True)
