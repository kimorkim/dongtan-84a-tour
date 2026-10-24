"""Q22c: remove bedroom rug/nightstands/decor and lower the bed onto the wood floor."""
from pathlib import Path
import runpy
import shutil
import bpy
from mathutils import Vector

ROOT=Path(__file__).resolve().parent.parent
sc=bpy.context.scene
assert sc.get('Q22_restandard_bed')==1 and sc.get('Q22_master_bed_wall_aligned'), 'Current wall-aligned Q22 bed required'
backup=ROOT/'models/backups/apt_84a_photoreal_tour_before_master_bedside_cleanup.blend'
if not backup.exists(): shutil.copy2(bpy.data.filepath,backup)
removed=[]
for obj in list(bpy.data.objects):
    if obj.name=='Q2_Master_Rug' or obj.name.startswith(('Nightstand_Master_', 'Q2_Night', 'Q2_Pendant')):
        removed.append(obj.name); bpy.data.objects.remove(obj,do_unlink=True)
bpy.context.view_layer.update()
legs=[o for o in bpy.data.objects if o.name.startswith('Q22_Restandard_Leg')]
assert len(legs)==8
support=min((o.matrix_world @ Vector(c)).z for o in legs for c in o.bound_box)
for obj in bpy.data.objects:
    if obj.name.startswith(('Q22_Restandard_', 'Q22_Detail_')):
        obj.location.z-=support
sc['Q22_master_bedside_cleared']=True
sc['Q22_master_bed_support']='wood floor z=0'
bpy.context.view_layer.update()
runpy.run_path(str(ROOT/'scripts/verify_restandard_bed.py'),run_name='__main__')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'apt_84a_photoreal_tour.blend'))
print(f'Q22c SAVED: removed {len(removed)} bedside/rug objects, lowered bed {support:.3f}m',flush=True)
print('REMOVED:',', '.join(removed),flush=True)
