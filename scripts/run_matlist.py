import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mcp_client, json

code = '''
import bpy, json
out = []
for m in bpy.data.materials:
    if m.users == 0 and not m.use_fake_user:
        continue
    out.append({"name": m.name, "users": m.users})
print("MATLIST:" + json.dumps(out))
'''
res = mcp_client.send_blender_command('execute_code', {'code': code}, timeout=60.0)
print(json.dumps(res, ensure_ascii=False)[:6000])
