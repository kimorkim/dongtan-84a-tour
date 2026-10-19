import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mcp_client, json

code = '''
import bpy, json
from mathutils import Vector
out = {}
for name in ["ExactWall_11", "ExactWall_5", "ExactWall_6", "ExactWall_12", "ExactWall_4"]:
    o = bpy.data.objects.get(name)
    if not o:
        continue
    me = o.data
    polys = []
    for p in me.polygons:
        c = o.matrix_world @ p.center
        wn = (o.matrix_world.to_3x3() @ p.normal).normalized()
        polys.append({"c": [round(c.x,2), round(c.y,2), round(c.z,2)],
                      "n": [round(wn.x,2), round(wn.y,2), round(wn.z,2)],
                      "mi": p.material_index, "nv": len(p.vertices)})
    out[name] = {"npolys": len(polys), "mats": [s.name if s else "-" for s in me.materials],
                 "polys": polys[:40]}
print("POLYS:" + json.dumps(out))
'''
res = mcp_client.send_blender_command('execute_code', {'code': code}, timeout=60.0)
s = json.dumps(res, ensure_ascii=False)
i = s.find("POLYS:")
print(s[i:i+7000] if i >= 0 else s[:2000])
