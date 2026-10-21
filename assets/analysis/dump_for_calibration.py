import bpy,json
from collections import Counter
from pathlib import Path
from mathutils import Vector
data=[]
for o in bpy.data.objects:
    if o.type not in ('MESH','LIGHT','CAMERA','CURVE'): continue
    p=[o.matrix_world @ Vector(c) for c in o.bound_box]
    data.append(dict(name=o.name,type=o.type,col=[c.name for c in o.users_collection],
                     lo=[min(v[i] for v in p) for i in range(3)],hi=[max(v[i] for v in p) for i in range(3)]))
Path('assets/analysis/calibration_objects.json').write_text(json.dumps(data),encoding='utf-8')
print(Counter(o['name'].split('_')[0] for o in data))
for o in data:
    if o['name'].startswith(('ProDoorLeaf','ProDoorTrim','Entry','NewWall','Win_')):
        print(o)
