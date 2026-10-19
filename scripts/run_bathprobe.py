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
    n = o.name
    if "Bath" in n and ("Floor" in n or "Wall" in n) or n in ("Floor_Foyer", "EntrySlab_Front", "Floor_KitchenBalcony"):
        ws = [o.matrix_world @ Vector(c) for c in o.bound_box]
        xs = [v.x for v in ws]; ys = [v.y for v in ws]
        out.append({"n": n, "min": [round(min(xs),2), round(min(ys),2)], "max": [round(max(xs),2), round(max(ys),2)]})
cams = [o.name for o in bpy.data.objects if o.type == "CAMERA"]
print("PROBE:" + json.dumps({"floors": out, "cams": cams}))
'''
res = mcp_client.send_blender_command('execute_code', {'code': code}, timeout=60.0)
s = json.dumps(res, ensure_ascii=False)
i = s.find("PROBE:")
print(s[i:i+3000] if i >= 0 else s[:2000])
