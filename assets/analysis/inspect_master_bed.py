"""Read-only Q22 inventory of the existing master bedroom furniture."""
import bpy
from mathutils import Vector

for obj in bpy.data.objects:
    if obj.type == 'MESH' and obj.name.startswith(('Bed_Master', 'Q2_Master', 'Nightstand_Master')):
        points = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
        bounds = [[round(min(p[i] for p in points), 4), round(max(p[i] for p in points), 4)] for i in range(3)]
        print('MASTER_OBJECT', obj.name, bounds, [m.name for m in obj.data.materials])
for name in ('Cam_MasterBed_POV',):
    obj = bpy.data.objects.get(name)
    print('MASTER_CAMERA', name, tuple(obj.location), tuple(obj.rotation_euler), obj.data.lens)
deps=bpy.context.evaluated_depsgraph_get()
wall=bpy.data.objects['ExactWall_13'].evaluated_get(deps)
inv=wall.matrix_world.inverted()
hit,p,n,index=wall.ray_cast(inv @ Vector((2.,3.2222,1.0)),inv.to_3x3() @ Vector((-1,0,0)))
print('WEST_STRUCTURE_FACE',wall.matrix_world @ p)
for obj in bpy.data.objects:
    if ('Master' in obj.name or 'Bed' in obj.name) and (obj.type=='LIGHT' or 'Pendant' in obj.name or 'Cove' in obj.name):
        print('BEDROOM_LIGHT',obj.name,obj.type,tuple(obj.location))
for x,y in ((1.805,3.2222),(1.455,3.15),(2.5,3.2)):
    result=bpy.context.scene.ray_cast(deps,Vector((x,y,1.5)),Vector((0,0,-1)))
    print('BED_TOP_RAY',x,y,result[1].z,result[4].name if result[0] else None)
obj=bpy.data.objects.get('Q22_Restandard_Mattress')
if obj:
    print('Q22_TOP_Z_RANGE',min(v.co.z for v in obj.data.vertices if v.co.z>.10),max(v.co.z for v in obj.data.vertices))
for obj in bpy.data.objects:
    if obj.type!='MESH' or obj.name.startswith(('Q22_', 'Exact','Q2_Master','Nightstand','Ceiling','Cove_')): continue
    ps=[obj.matrix_world @ Vector(c) for c in obj.bound_box]
    lo=[min(p[i] for p in ps) for i in range(3)]; hi=[max(p[i] for p in ps) for i in range(3)]
    if lo[0]<2.8 and hi[0]>.8 and lo[1]<4.0 and hi[1]>2.4 and lo[2]<.7 and hi[2]>.1:
        print('OTHER_BED_OVERLAP',obj.name,lo,hi)
