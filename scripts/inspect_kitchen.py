import sys, os
sys.path.insert(0, os.path.abspath("."))
import mcp_client
import json

code = """
import bpy
pen_objs = [o for o in bpy.data.objects if any(k in o.name.lower() for k in ['pen', 'island', 'prok_doorp', 'prok_endpanel'])]
for o in pen_objs:
    mats = [m.name for m in o.data.materials] if o.type == 'MESH' else []
    print(f'{o.name:25s} | loc=({o.location.x:6.3f}, {o.location.y:6.3f}, {o.location.z:6.3f}) | dim=({o.dimensions.x:6.3f}, {o.dimensions.y:6.3f}, {o.dimensions.z:6.3f}) | mats={mats}')
"""

res = mcp_client.send_blender_command('execute_code', {'code': code})
print(res['result']['result'])
