import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mcp_client, json

code = '''
import bpy, json
from mathutils import Vector
out = []
for o in bpy.data.objects:
    n = o.name
    if o.type != "MESH":
        continue
    ln = n.lower()
    if ln.startswith("exactwall") or ln.startswith("newwall") or ("wall" in ln and "art" not in ln) or "ceiling" in ln or "cove" in ln:
        ws = [o.matrix_world @ Vector(c) for c in o.bound_box]
        xs = [v.x for v in ws]; ys = [v.y for v in ws]; zs = [v.z for v in ws]
        mats = [s.name if s else "-" for s in (o.data.materials if o.data else [])]
        out.append({"n": n, "min": [round(min(xs),2), round(min(ys),2), round(min(zs),2)],
                    "max": [round(max(xs),2), round(max(ys),2), round(max(zs),2)], "mats": mats})
print("WALLS:" + json.dumps(out))
'''
res = mcp_client.send_blender_command('execute_code', {'code': code}, timeout=60.0)
s = json.dumps(res, ensure_ascii=False)
i = s.find("WALLS:")
print(s[i:i+6000] if i >= 0 else s[:3000])
