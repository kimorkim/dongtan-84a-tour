import bpy
import shutil
from pathlib import Path
import mathutils

ROOT = Path(__file__).resolve().parent.parent

# Backup
backup = ROOT / 'models/backups/apt_84a_photoreal_tour_before_bed_nightstand_shift.blend'
if not backup.exists():
    shutil.copy2(bpy.data.filepath, backup)
    print(f'Backup saved: {backup.name}')

# Current bed center
m = bpy.data.objects['Q22_Restandard_Mattress']
pts = [m.matrix_world @ mathutils.Vector(c) for c in m.bound_box]
curr_cy = (min(p.y for p in pts) + max(p.y for p in pts)) / 2
target_cy = 3.50 # Leaves 450mm to door jamb (y=4.75), 550mm to balcony door (y=2.15)
delta_y = target_cy - curr_cy
print(f'Shifting bed in Y: curr={curr_cy:.3f}, target={target_cy:.3f}, delta={delta_y:.3f}')

objs = [o for o in bpy.data.objects if o.name.startswith(('Q22_Restandard_', 'Q22_Detail_'))]
roots = [o for o in objs if o.parent not in objs]
for o in roots:
    o.location.y += delta_y

bpy.context.scene['Q22_master_bed_center_y'] = target_cy
bpy.context.scene['Q22_master_bed_nightstand_gap'] = 0.450
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / 'apt_84a_photoreal_tour.blend'))
print(f'Saved apt_84a_photoreal_tour.blend with bed center y={target_cy:.3f}')
