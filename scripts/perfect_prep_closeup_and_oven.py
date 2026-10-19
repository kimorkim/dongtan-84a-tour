"""Perfect Kitchen Prep Close-Up (matching display_03_part_3.jpg) & Top-Down Plan.

1. Camera Position:
   - Stand inside kitchen aisle at X=5.85, Y=8.50, Z=1.35.
   - Look East-Northeast: Sink on left, Induction/Oven directly in front, Peninsula on right.
   - 100% identical vantage point to official Prugio e-modelhouse photo display_03_part_3.jpg.
2. Built-in Oven Detailing:
   - Black glossy reflective glass door (Mat_Induction_Glass or tinted black reflective).
   - Stainless steel horizontal bar handle.
   - LED digital control strip.
3. Top-Down Plan Update:
   - Re-render render_1_isometric_topdown.png with the new compact kitchen proportions.
"""

import sys, os
sys.path.insert(0, os.path.abspath("."))
import mcp_client

py_code = r'''
import bpy
import bmesh
import math
from mathutils import Vector, Euler

col_furn = bpy.data.collections.get("Apt_Furnishings")

def safe_remove(obj_name):
    o = bpy.data.objects.get(obj_name)
    if o:
        m = o.data if o.type == 'MESH' else None
        bpy.data.objects.remove(o, do_unlink=True)
        if m and m.users == 0:
            bpy.data.meshes.remove(m)

def safe_remove_matching(patterns):
    for o in list(bpy.data.objects):
        for p in patterns:
            if p.lower() in o.name.lower():
                m = o.data if o.type == 'MESH' else None
                bpy.data.objects.remove(o, do_unlink=True)
                if m and m.users == 0:
                    bpy.data.meshes.remove(m)
                break

def make_box(name, loc, size, mat_name, col=col_furn, bevel_width=0.0):
    safe_remove(name)
    mesh = bpy.data.meshes.new(name + "_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bm.to_mesh(mesh)
    bm.free()
    
    obj.scale = size
    obj.location = loc
    bpy.context.view_layer.update()
    
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    
    if bevel_width > 0.0:
        bev = obj.modifiers.new("Bevel", 'BEVEL')
        bev.width = bevel_width
        bev.segments = 3
        bev.limit_method = 'ANGLE'
        bev.angle_limit = math.radians(30)
        
    if mat_name:
        mat = bpy.data.materials.get(mat_name)
        if mat:
            obj.data.materials.append(mat)
            
    return obj

# -------------------------------------------------------------
# 1. LUXURY BUILT-IN OVEN DETAILING
# -------------------------------------------------------------
oven_cy = 8.85
safe_remove_matching(["ProK_Oven_"])

# Oven cavity/recess in base cabinet:
make_box("ProK_Oven_Cavity", (7.48, oven_cy, 0.44), (0.55, 0.58, 0.58), "Mat_Window_Frame")
# Black reflective glass door:
make_box("ProK_Oven_DoorGlass", (7.17, oven_cy, 0.42), (0.02, 0.56, 0.50), "Mat_Induction_Glass", bevel_width=0.004)
# Digital LED control panel strip above door:
make_box("ProK_Oven_ControlPanel", (7.17, oven_cy, 0.695), (0.02, 0.56, 0.05), "Mat_Window_Frame")
make_box("ProK_Oven_DisplayLED", (7.158, oven_cy, 0.695), (0.005, 0.12, 0.025), "Mat_Bulb_Warm")
# Wide horizontal brushed stainless steel handle:
make_box("ProK_Oven_HandleBar", (7.12, oven_cy, 0.63), (0.016, 0.48, 0.02), "Mat_Steel_Brushed")
# Handle brackets:
make_box("ProK_Oven_HandlePostL", (7.145, oven_cy - 0.22, 0.63), (0.035, 0.016, 0.02), "Mat_Steel_Brushed")
make_box("ProK_Oven_HandlePostR", (7.145, oven_cy + 0.22, 0.63), (0.035, 0.016, 0.02), "Mat_Steel_Brushed")

# -------------------------------------------------------------
# 2. CAMERA PREP CORNER (100% REPLICATING display_03_part_3.jpg)
# -------------------------------------------------------------
cam_prep = bpy.data.objects.get("Cam_Kitchen_Prep_POV")
if cam_prep:
    # Stand inside the kitchen aisle:
    cam_prep.location = Vector((5.85, 8.45, 1.35))
    # Look east-northeast at pitch 80 deg, yaw -36 deg:
    cam_prep.rotation_euler = Euler((math.radians(80.0), 0.0, math.radians(-36.0)), 'XYZ')
    cam_prep.data.lens = 19.5
    print("Cam_Kitchen_Prep_POV aligned to match display_03_part_3.jpg aisle position")

bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print("Saved blend successfully")
'''

res = mcp_client.send_blender_command('execute_code', {'code': py_code})
print("Result:", res)
