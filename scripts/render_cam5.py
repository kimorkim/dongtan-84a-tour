import os
import sys
sys.path.insert(0, os.path.abspath("."))
import mcp_client

code = """
import bpy
import math
import mathutils
import os

def look_at(cam_obj, target_pos):
    loc = cam_obj.location
    tgt = mathutils.Vector(target_pos)
    direction = tgt - loc
    cam_obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()

col_lights = bpy.data.collections.get("Apt_Lighting")
cam_foy_data = bpy.data.cameras.get("Cam_Foyer_POV") or bpy.data.cameras.new("Cam_Foyer_POV")
cam_foy_data.type = 'PERSP'
cam_foy_data.lens = 20.0
cam_foy_obj = bpy.data.objects.get("Cam_Foyer_POV") or bpy.data.objects.new("Cam_Foyer_POV", cam_foy_data)
if cam_foy_obj.name not in col_lights.objects:
    col_lights.objects.link(cam_foy_obj)

# Place in hallway looking into Living Room & Kitchen
cam_foy_obj.location = (11.0, 5.1, 1.40)
look_at(cam_foy_obj, (6.0, 4.2, 1.15))

ceil_obj = bpy.data.objects.get("Ceiling_Slab")
if ceil_obj:
    ceil_obj.hide_render = False

bpy.context.scene.camera = cam_foy_obj
out_path = os.path.abspath("render_5_foyer_corridor_pov.png")
bpy.context.scene.render.filepath = out_path
print("Rendering updated Camera 5...")
bpy.ops.render.render(write_still=True)
print("Saved:", out_path)
"""

res = mcp_client.send_blender_command('execute_code', {'code': code}, timeout=120.0)
print("Result:", res)
