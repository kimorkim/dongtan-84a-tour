"""Q22b: remove the old decorative panel/LED strips and align the bed to the real west wall."""
from pathlib import Path
import runpy
import shutil
import bpy
from mathutils import Vector

ROOT=Path(__file__).resolve().parent.parent
sc=bpy.context.scene
assert sc.get('Q22_restandard_bed')==1, 'Current Q22 bed required'
backup=ROOT/'models/backups/apt_84a_photoreal_tour_before_master_wall_cleanup.blend'
if not backup.exists(): shutil.copy2(bpy.data.filepath,backup)
for name in ('Q2_Master_Panel','Q2_Master_CoveTop','Q2_Master_CoveLow'):
    obj=bpy.data.objects.get(name)
    if obj: bpy.data.objects.remove(obj,do_unlink=True)
bpy.context.view_layer.update()
deps=bpy.context.evaluated_depsgraph_get()
wall=bpy.data.objects['ExactWall_13'].evaluated_get(deps)
inv=wall.matrix_world.inverted()
hit,point,_,_=wall.ray_cast(inv @ Vector((2.,3.2222,1.)),inv.to_3x3() @ Vector((-1,0,0)))
assert hit, 'West structural wall face not found'
wall_x=(wall.matrix_world @ point).x
mattress=bpy.data.objects['Q22_Restandard_Mattress']
head_x=min((mattress.matrix_world @ Vector(c)).x for c in mattress.bound_box)
delta=wall_x-head_x
for obj in bpy.data.objects:
    if obj.name.startswith(('Q22_Restandard_','Q22_Detail_')):
        obj.location.x+=delta
sc['Q22_master_bed_wall_aligned']=True
sc['Q22_master_bed_wall_x']=wall_x
bpy.context.view_layer.update()
runpy.run_path(str(ROOT/'scripts/verify_restandard_bed.py'),run_name='__main__')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'apt_84a_photoreal_tour.blend'))
print(f'Q22b SAVED: panel and strips removed, rigid bed shift {delta:.3f}m, head x={wall_x:.3f}',flush=True)
