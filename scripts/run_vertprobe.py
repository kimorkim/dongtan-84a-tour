import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mcp_client, json

code = '''
import bpy, json
from mathutils import Vector
seeds = {"Alpha": (10.40, 5.75), "CommonBath": (13.45, 5.75),
         "MasterBath": (2.80, 5.90), "MasterBed": (4.15, 5.20)}
out = {}
for o in bpy.data.objects:
    if o.type != "MESH" or not o.name.startswith(("ExactWall", "NewWall")):
        continue
    me = o.data
    for p in me.polygons:
        if abs(p.normal.z) > 0.6:
            continue
        c = o.matrix_world @ p.center
        for dn, (sx, sy) in seeds.items():
            if abs(c.x - sx) < 1.6 and abs(c.y - sy) < 1.6:
                vs = [[round(v, 2) for v in (o.matrix_world @ me.vertices[i].co)[:2]]
                      for i in p.vertices]
                wn = (o.matrix_world.to_3x3() @ p.normal).normalized()
                out.setdefault(dn, []).append({
                    "o": o.name, "c": [round(c.x, 2), round(c.y, 2)],
                    "n": [round(wn.x, 2), round(wn.y, 2)],
                    "z": [round((o.matrix_world @ me.vertices[i].co).z, 2) for i in p.vertices[:4]],
                    "vs": vs, "mi": p.material_index})
print("VERTS:" + json.dumps(out))
'''
res = mcp_client.send_blender_command('execute_code', {'code': code}, timeout=60.0)
s = json.dumps(res, ensure_ascii=False)
i = s.find("VERTS:")
txt = s[i:] if i >= 0 else s[:2000]
print(txt[:9000])
