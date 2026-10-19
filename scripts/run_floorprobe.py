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
    if o.name.startswith("Floor_") or o.name in ("Exact_Floor",):
        ws = [o.matrix_world @ Vector(c) for c in o.bound_box]
        xs = [v.x for v in ws]; ys = [v.y for v in ws]
        mats = [s.name if s else "-" for s in (o.data.materials if o.data else [])]
        out.append({"n": o.name, "x": [round(min(xs),2), round(max(xs),2)],
                    "y": [round(min(ys),2), round(max(ys),2)], "m": mats})
print("FLOORS:" + json.dumps(out))
'''
res = mcp_client.send_blender_command('execute_code', {'code': code}, timeout=60.0)
s = json.dumps(res, ensure_ascii=False)
i = s.find("FLOORS:")
print(s[i:i+4000] if i >= 0 else s[:2000])
