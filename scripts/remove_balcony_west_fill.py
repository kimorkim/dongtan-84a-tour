import bpy
import shutil
from pathlib import Path
import runpy

ROOT = Path(__file__).resolve().parent.parent

# Backup
backup = ROOT / 'models/backups/apt_84a_photoreal_tour_before_remove_balcony_fill.blend'
if not backup.exists():
    shutil.copy2(bpy.data.filepath, backup)
    print(f'Backup saved to {backup.name}')

fill = bpy.data.objects.get('Q12_BalconyDoor_WestFill')
if fill:
    bpy.data.objects.remove(fill, do_unlink=True)
    print('Q12_BalconyDoor_WestFill removed')
else:
    print('Q12_BalconyDoor_WestFill not found')

bpy.context.scene['Q22_balcony_west_fill_removed'] = True
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / 'apt_84a_photoreal_tour.blend'))
print('Saved apt_84a_photoreal_tour.blend')
