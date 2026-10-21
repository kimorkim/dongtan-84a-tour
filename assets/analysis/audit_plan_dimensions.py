"""Read-only dimensional audit of saved mesh surfaces against the supplied 84A plan."""
import bpy
from mathutils import Vector

def ray(name, origin, direction):
    obj=bpy.data.objects[name]
    inv=obj.matrix_world.inverted()
    hit,p,_,_=obj.ray_cast(inv @ Vector(origin),inv.to_3x3() @ Vector(direction))
    assert hit,(name,origin,direction)
    return obj.matrix_world @ p

y,z=2.5,1.5
w=ray('ExactWall_3',(10.5,y,z),(-1,0,0)).x
partition_w=ray('ExactWall_2',(10.5,y,z),(1,0,0)).x
partition_e=ray('ExactWall_2',(13.4,y,z),(-1,0,0)).x
e=ray('ExactWall_5',(13.4,y,z),(1,0,0)).x
living_w=ray('ExactWall_4',(6.5,y,z),(-1,0,0)).x
living_e=ray('ExactWall_3',(6.5,y,z),(1,0,0)).x
master_w=ray('ExactWall_13',(2.5,3.0,z),(-1,0,0)).x
master_e=ray('ExactWall_4',(2.5,3.0,z),(1,0,0)).x
for label,plan,model in [('Bed2 clear width',2700,(partition_w-w)*1000),
                         ('Bed3 clear width',3000,(e-partition_e)*1000),
                         ('Bed2/3 partition',130,(partition_e-partition_w)*1000),
                         ('Living clear width',4500,(living_e-living_w)*1000),
                         ('Master clear width',3600,(master_e-master_w)*1000)]:
    print(f'{label}: plan={plan}mm model={model:.1f}mm delta={model-plan:+.1f}mm')
for name,expected in [('Win_Bed2_Sill',1700),('Win_Bed3_Sill',2000)]:
    o=bpy.data.objects[name]
    pts=[o.matrix_world @ Vector(v) for v in o.bound_box]
    width=(max(v.x for v in pts)-min(v.x for v in pts))*1000
    print(f'{name}: plan nominal={expected}mm model frame={width:.1f}mm')
print('Read-only; source model not saved or modified')
