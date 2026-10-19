import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mcp_client, json

code = '''
import bpy, json
from mathutils import Vector
scene = bpy.context.scene
deps = bpy.context.evaluated_depsgraph_get()
pts = {"Bed2": (9.64, 4.35), "Bed3": (12.46, 4.35), "Front": (12.20, 10.11),
       "CBath_S": (14.20, 5.72), "CBath_W": (13.44, 6.65),
       "MBath_S": (3.40, 5.86), "MBath_W": (2.71, 7.00), "MBath_E": (4.22, 6.96),
       "Alpha": (10.48, 6.20), "MBed": (4.15, 5.20)}
out = {}
for name, (x, y) in pts.items():
    # ray up: any object
    hit, loc, no, idx, obj, mat = scene.ray_cast(deps, Vector((x, y, 1.0)), Vector((0, 0, 1)))
    up = {"z": round(loc.z, 2), "obj": obj.name if obj else None} if hit else None
    # rays along x both ways (wall only, 1 bounce)
    row = {"up": up}
    for dn, dd in (("px", (1,0,0)), ("nx", (-1,0,0)), ("py", (0,1,0)), ("ny", (0,-1,0))):
        o = Vector((x, y, 1.0)); d = Vector(dd); trav = 0.0; found = None
        for _ in range(6):
            h, l, _, _, ob, _ = scene.ray_cast(deps, o, d)
            if not h:
                break
            step = (l - o).length
            if ob and ob.name.startswith(("ExactWall", "NewWall")):
                found = {"d": round(trav + step, 2), "obj": ob.name,
                         "at": [round(v, 2) for v in l]}
                break
            trav += step + 0.05
            if trav > 8:
                break
            o = l + d * 0.05
        row[dn] = found
    out[name] = row
print("HEADPROBE:" + json.dumps(out))
'''
res = mcp_client.send_blender_command('execute_code', {'code': code}, timeout=60.0)
s = json.dumps(res, ensure_ascii=False)
i = s.find("HEADPROBE:")
print(s[i:i+5000] if i >= 0 else s[:2000])
