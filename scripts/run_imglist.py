import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mcp_client, json

code = '''
import bpy
for im in bpy.data.images:
    print("IMG %s %dx%d %s" % (im.name, im.size[0], im.size[1], im.filepath))
'''
res = mcp_client.send_blender_command('execute_code', {'code': code}, timeout=60.0)
print(json.dumps(res, ensure_ascii=False)[:3000])
