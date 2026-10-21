"""Q14: official closed envelope, replacement completeness and static room clearance."""
import bpy
from mathutils import Vector
bpy.context.view_layer.update()
def bounds(objects):
    points=[o.matrix_world@Vector(c) for o in objects for c in o.bound_box]
    assert points,'Brest sofa missing'
    return [min(p[i] for p in points) for i in range(3)],[max(p[i] for p in points) for i in range(3)]
parts=[o for o in bpy.data.objects if o.name.startswith('Q14_Brest_') and o.type in ('MESH','CURVE')]
lo,hi=bounds(parts)
for value,expected in zip([hi[i]-lo[i] for i in range(3)],[1.0,2.85,.95]):
    assert abs(value-expected)<.002,('Official closed envelope',lo,hi)
assert not any(o.name.startswith(('Sofa_Living_','Q2_Sofa')) for o in bpy.data.objects),'Old sofa/cushions remain'
assert abs(8.805-hi[0]-.15)<.002 and lo[1]>.92+.4 and hi[1]<5.75-.8
for name in ('Seat0','Seat1','Seat2','Headrest0','Headrest2','FoldTray','Arm0_Roll','Arm1_Roll','Footrest0','Footrest2'):
    assert bpy.data.objects.get('Q14_Brest_'+name),('Brest detail missing',name)
assert bpy.data.materials['Mat_Q14_IvoryLeather'].node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value[0]>.5
if not bpy.context.scene.get('Q15_living_finish'):
    coffee=bounds([bpy.data.objects['Q2_Coffee_Top']])
    assert lo[0]-coffee[1][0]>.65,'Closed sofa/table aisle too narrow'
assert len([o for o in bpy.data.objects if o.name.startswith('Q11_Equipment_')])==223
assert bpy.data.objects.get('Q13_Poeta800_Back') and bpy.data.objects.get('Q13_Poeta600_Back')
print('PASS Q14: Brest closed 2850x1000x950, ivory, old sofa removed, static wall/table clearance, Q13 retained')
