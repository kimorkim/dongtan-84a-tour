import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mcp_client, json

code = '''
import bpy, json
from mathutils import Vector
out = []
for o in bpy.data.objects:
    if o.type != "MESH":
        continue
    if o.name.startswith("Liner_") or o.name.startswith("EntryFrame_"):
        ws = [o.matrix_world @ Vector(c) for c in o.bound_box]
        xs = [v.x for v in ws]; ys = [v.y for v in ws]; zs = [v.z for v in ws]
        out.append({"n": o.name, "min": [round(v,2) for v in (min(xs),min(ys),min(zs))],
                    "max": [round(v,2) for v in (max(xs),max(ys),max(zs))]})
print("LINERS:" + json.dumps(out))
'''
res = mcp_client.send_blender_command('execute_code', {'code': code}, timeout=60.0)
s = json.dumps(res, ensure_ascii=False)
i = s.find("LINERS:")
print(s[i:i+6000] if i >= 0 else s[:2000])
