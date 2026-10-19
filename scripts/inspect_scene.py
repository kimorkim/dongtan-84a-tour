import mcp_client
import json

code = """
import bpy
import json

data = {
    'collections': [c.name for c in bpy.data.collections],
    'struct_objects': [o.name for o in bpy.data.collections.get('Apt_Corrected_Structure', bpy.context.scene.collection).objects]
}
print('SCENE_DATA:' + json.dumps(data))
"""

res = mcp_client.send_blender_command('execute_code', {'code': code})
print("Result:", res)
