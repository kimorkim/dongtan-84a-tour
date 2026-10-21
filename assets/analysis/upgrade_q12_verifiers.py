"""Preserve legacy checks for backup/generator use; dispatch saved Q12 rooms to new coordinates."""
from pathlib import Path
root=Path(__file__).resolve().parents[2]
for file,kind in [('verify_alpha_room.py','alpha'),('verify_utility_room.py','utility'),
 ('verify_foyer.py','foyer'),('verify_common_bath.py','bath'),('verify_flooring.py','floor'),
 ('verify_yuna_room.py','yuna'),('verify_study_room.py','study')]:
    path=root/'scripts'/file
    text=path.read_text(encoding='utf-8')
    if '# Q12 compatibility dispatch' in text: continue
    result='# Q12 compatibility dispatch: historical generators still verify their original frame.\n'
    result+='import os, sys, bpy\nsys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))\n'
    result+='def verify_legacy():\n'+''.join('    '+line+'\n' for line in text.splitlines())
    result+=f'\nif bpy.context.scene.get("Q12_dimensions_version"):\n    from verify_calibrated_rooms import verify_room\n    verify_room({kind!r})\nelse:\n    verify_legacy()\n'
    compile(result,str(path),'exec')
    path.write_text(result,encoding='utf-8')
    print('updated',file)
