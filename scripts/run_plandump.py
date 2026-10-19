import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mcp_client, json

code = '''
import bpy
from mathutils import Vector
which = "%s"
names = which.split(",")
lines = []
for wname in names:
    o = bpy.data.objects.get(wname)
    me = o.data
    for p in me.polygons:
        if abs(p.normal.z) > 0.6 or len(p.vertices) != 4:
            continue
        c = o.matrix_world @ p.center
        wn = (o.matrix_world.to_3x3() @ p.normal).normalized()
        v = [(o.matrix_world @ me.vertices[i].co) for i in p.vertices]
        xs = [round(q.x, 2) for q in v]; ys = [round(q.y, 2) for q in v]
        lines.append(f"{wname} c=({c.x:.2f},{c.y:.2f}) n=({wn.x:.2f},{wn.y:.2f}) "
                     f"x=[{min(xs)},{max(xs)}] y=[{min(ys)},{max(ys)}]")
print("PLAN|" + wname + "|" + "\\n".join(lines))
'''
import sys as _s
walls = _s.argv[1] if len(_s.argv) > 1 else "ExactWall_11"
res = mcp_client.send_blender_command('execute_code', {'code': code % walls}, timeout=60.0)
s = json.dumps(res, ensure_ascii=False)
i = s.find("PLAN|")
print(s[i:i+8000] if i >= 0 else s[:2000])
