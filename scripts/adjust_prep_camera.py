"""Adjust Cam_Kitchen_Prep_POV to frame the short oven counter and sink corner exactly as display_03_part_3.jpg."""

import sys, os
sys.path.insert(0, os.path.abspath("."))
import mcp_client

py_code = r'''
import bpy
import math
from mathutils import Vector, Euler

# Cam_Kitchen_Prep_POV (Corner View matching display_03_part_3.jpg):
cam_prep = bpy.data.objects.get("Cam_Kitchen_Prep_POV")
if cam_prep:
    # Position in front of the peninsula:
    cam_prep.location = Vector((6.10, 6.70, 1.40))
    # Look northeast towards sink (left) and induction/oven (right):
    cam_prep.rotation_euler = Euler((math.radians(82.0), 0.0, math.radians(-38.0)), 'XYZ')
    cam_prep.data.lens = 19.5
    print("Cam_Kitchen_Prep_POV positioned at (6.10, 6.70, 1.40) rot -38 deg")

# Also ensure Cam_Kitchen_POV (Overall Dining/Kitchen view matching display_03_part_1.jpg):
cam_k = bpy.data.objects.get("Cam_Kitchen_POV")
if cam_k:
    cam_k.location = Vector((5.75, 4.40, 1.48))
    cam_k.rotation_euler = Euler((math.radians(86.5), 0.0, math.radians(-19.0)), 'XYZ')
    cam_k.data.lens = 22.0

bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print("Saved cameras successfully")
'''

res = mcp_client.send_blender_command('execute_code', {'code': py_code})
print("Result:", res)
