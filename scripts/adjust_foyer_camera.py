"""Fix Cam_Foyer_POV position and angle to view from the front door into the foyer and corridor."""

import sys, os
sys.path.insert(0, os.path.abspath("."))
import mcp_client

py_code = r'''
import bpy
import math
from mathutils import Vector, Euler

cam_f = bpy.data.objects.get("Cam_Foyer_POV")
if cam_f:
    # Stand inside front door at Y=7.65, looking south into foyer and hallway:
    cam_f.location = Vector((12.25, 7.65, 1.45))
    cam_f.rotation_euler = Euler((math.radians(85.0), 0.0, math.radians(-155.0)), 'XYZ')
    cam_f.data.lens = 18.0
    print("Cam_Foyer_POV adjusted to stand inside front entrance looking south")

bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print("Saved blend successfully")
'''

res = mcp_client.send_blender_command('execute_code', {'code': py_code})
print("Result:", res)
