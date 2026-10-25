"""Q22d: move the Restandard K bed so its head end sits on the east (bedroom-door side) wall."""
from pathlib import Path
import math, runpy, shutil
import bpy
from mathutils import Vector, Matrix

ROOT=Path(__file__).resolve().parent.parent
sc=bpy.context.scene
assert sc.get('Q22_restandard_bed')==1, 'Current Q22 bed required'
backup=ROOT/'models/backups/apt_84a_photoreal_tour_before_bed_door_wall.blend'
if not backup.exists(): shutil.copy2(bpy.data.filepath,backup)
bpy.context.view_layer.update()
deps=bpy.context.evaluated_depsgraph_get()
wall=bpy.data.objects['ExactWall_4'].evaluated_get(deps)
inv=wall.matrix_world.inverted()
hit,point,_,_=wall.ray_cast(inv @ Vector((2.,3.2222,1.)),inv.to_3x3() @ Vector((1,0,0)))
assert hit, 'East door-side wall face not found'
wall_x=(wall.matrix_world @ point).x
objs=[o for o in bpy.data.objects if o.name.startswith(('Q22_Restandard_','Q22_Detail_'))]
roots=[o for o in objs if o.parent not in objs]
m=bpy.data.objects['Q22_Restandard_Mattress']
pts=[m.matrix_world @ Vector(c) for c in m.bound_box]
cx=(min(p.x for p in pts)+max(p.x for p in pts))/2; cy=(min(p.y for p in pts)+max(p.y for p in pts))/2
# rotate 180deg about bed centre (head end now faces east), then place head on east wall
T=Matrix.Translation((wall_x-1.-cx+cx,0,0))
R=Matrix.Translation((cx,cy,0))@Matrix.Rotation(math.pi,4,'Z')@Matrix.Translation((-cx,-cy,0))
shift=Matrix.Translation((wall_x-1.-cx,3.90-cy,0))  # 950mm walk zone to balcony door (y2.15); 50mm short of bedroom door jamb (y4.75)
for o in roots: o.matrix_world=shift@R@o.matrix_world
sc['Q22_master_bed_wall_x']=wall_x
sc['Q22_master_bed_wall_side']='east_door'
bpy.context.view_layer.update()
runpy.run_path(str(ROOT/'scripts/verify_restandard_bed.py'),run_name='__main__')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'apt_84a_photoreal_tour.blend'))
print(f'Q22d SAVED: head on east door-side wall x={wall_x:.3f}',flush=True)


