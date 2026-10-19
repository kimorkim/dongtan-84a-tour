import mcp_client
import json

code = """
import bpy
import json

res = {
    'blender_version': bpy.app.version_string,
    'cycles_available': 'cycles' in bpy.context.preferences.addons,
    'devices': []
}
if 'cycles' in bpy.context.preferences.addons:
    cpref = bpy.context.preferences.addons['cycles'].preferences
    cpref.compute_device_type = 'OPTIX'
    cpref.get_devices()
    for d in cpref.devices:
        res['devices'].append({'name': d.name, 'type': d.type, 'use': d.use})

print('CYCLES_INFO:' + json.dumps(res))
"""

res = mcp_client.send_blender_command('execute_code', {'code': code})
print("Result:", res)
