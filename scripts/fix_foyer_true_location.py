"""Fix Apartment Entrance & Foyer to True Blueprint Location.

Ground Truth Analysis:
1. True Entrance Wall Opening:
   - Between ExactWall_7 (X=11.775) and ExactWall_5 (X=12.881) at Y=7.969 (width = 1.106m).
   - This is where the actual front door of the apartment is located!
2. Remove Bogus Exterior Floor & Floating Blue Door:
   - Cut out [11.775, 15.35] x [7.969, 10.35] from Exact_Floor so no fake wooden deck protrudes into the elevator lobby.
   - Remove the orphaned blue door ProDoorLeaf_FrontEntry and frame at Y=10.11.
3. Authentic Front Door (방화문) at Y=7.969:
   - Structural steel door frame & dark charcoal architectural fire door at X=12.328, Y=7.969.
   - Push-pull smart digital door lock.
   - Wall header above door (Z=2.15 to 2.30).
4. Authentic Interior Foyer (현관) at X=11.78 to 12.88, Y=6.45 to 7.95:
   - Porcelain stone floor tile (Mat_Tile_Grey).
   - Polished marble threshold step (현관 디딤석, Mat_Marble_White) at Y=6.45.
   - Full-height floating shoe cabinet (신발장, 하부 띄움 시공) on East wall with indirect warm LED strip.
   - Full-length mirror on West wall.
   - Recessed motion sensor spotlight in ceiling.
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
col_light = bpy.data.collections.get("Apt_Lighting")
col_struct = bpy.data.collections.get("Apt_Corrected_Structure")

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

def make_cylinder(name, loc, radius, depth, mat_name, col=col_furn, rot=(0,0,0)):
    safe_remove(name)
    mesh = bpy.data.meshes.new(name + "_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=24, radius1=radius, radius2=radius, depth=depth)
    bm.to_mesh(mesh)
    bm.free()
    
    obj.location = loc
    obj.rotation_euler = Euler(rot, 'XYZ')
    
    if mat_name:
        mat = bpy.data.materials.get(mat_name)
        if mat:
            obj.data.materials.append(mat)
            
    return obj

print("=== STARTING FOYER & ENTRANCE RECTIFICATION ===")

# -------------------------------------------------------------
# 1. REMOVE BOGUS BLUE DOOR & FLOATING FOYER AT Y=10.11
# -------------------------------------------------------------
safe_remove_matching([
    "EntryFrame_Front_", "ProDoorLeaf_FrontEntry",
    "ProDoorTrim_FrontEntry", "ProDoorHandle_FrontEntry_",
    "PBR_Fill_Foyer", "Floor_Foyer", "Foyer_Shoe_Cab"
])

# -------------------------------------------------------------
# 2. CARVE OUT ELEVATOR HALL VOID FROM Exact_Floor
# -------------------------------------------------------------
# The apartment does not exist for X >= 11.775 and Y >= 7.969.
# We cut out the corner [11.775, 15.35] x [7.969, 10.35] x [-0.20, 0.10].
cutter = make_box("Void_Elevator_Hall_Cutter", (13.56, 9.16, -0.075), (3.60, 2.45, 0.40), None, col=col_struct)
ef = bpy.data.objects.get("Exact_Floor")
if ef:
    # Add boolean difference to cut off the sticking out elevator hall deck
    bool_mod = ef.modifiers.get("Cut_ElevatorHall")
    if not bool_mod:
        bool_mod = ef.modifiers.new("Cut_ElevatorHall", 'BOOLEAN')
        bool_mod.operation = 'DIFFERENCE'
        bool_mod.solver = 'EXACT'
    bool_mod.object = cutter
    cutter.hide_render = True
    cutter.hide_viewport = True
    print("Applied boolean cutter to Exact_Floor to eliminate fake exterior deck")

# -------------------------------------------------------------
# 3. AUTHENTIC APARTMENT FRONT DOOR (방화문) AT Y=7.969
# -------------------------------------------------------------
# Opening between ExactWall_7 (X=11.775) and ExactWall_5 (X=12.881)
door_cx = (11.775 + 12.881) / 2.0 # 12.328
door_y = 7.969
door_w = 0.96 # standard 960mm front door
frame_w = 1.06

# 3a. Wall Header above door (Z=2.15 to 2.30):
make_box("Foyer_Wall_Header", (door_cx, door_y, 2.225), (1.106, 0.20, 0.15), "Mat_Wall_Base", col=col_struct)

# 3b. Architectural Steel Door Frame:
make_box("Front_Door_JambL", (door_cx - door_w/2.0 - 0.03, door_y, 1.075), (0.06, 0.14, 2.15), "Mat_Window_Frame", col=col_struct)
make_box("Front_Door_JambR", (door_cx + door_w/2.0 + 0.03, door_y, 1.075), (0.06, 0.14, 2.15), "Mat_Window_Frame", col=col_struct)
make_box("Front_Door_Head", (door_cx, door_y, 2.12), (frame_w, 0.14, 0.06), "Mat_Window_Frame", col=col_struct)

# 3c. Luxury Apartment Fire Door Leaf (방화문):
# Elegant dark bronze/charcoal steel door:
make_box("Front_Door_Leaf", (door_cx, door_y, 1.06), (door_w, 0.05, 2.08), "Mat_Window_Frame", bevel_width=0.004)

# 3d. Digital Smart Door Lock (삼성 푸시풀 스마트 도어록):
# Keypad escutcheon:
make_box("Front_Door_Lock_Body", (door_cx + 0.38, door_y - 0.028, 0.98), (0.08, 0.02, 0.36), "Mat_Window_Frame", bevel_width=0.003)
make_box("Front_Door_Lock_Keypad", (door_cx + 0.38, door_y - 0.039, 1.06), (0.06, 0.005, 0.12), "Mat_Induction_Glass")
make_box("Front_Door_Lock_Handle", (door_cx + 0.38, door_y - 0.045, 0.90), (0.04, 0.03, 0.18), "Mat_Steel_Brushed", bevel_width=0.002)

# -------------------------------------------------------------
# 4. AUTHENTIC INTERIOR FOYER (현관) AT X=11.78 to 12.88, Y=6.45 to 7.95
# -------------------------------------------------------------
foyer_cx = door_cx # 12.328
foyer_w = 1.10
foyer_y_start = 6.45
foyer_y_end = 7.95
foyer_depth = foyer_y_end - foyer_y_start # 1.50
foyer_cy = (foyer_y_start + foyer_y_end) / 2.0 # 7.20

# 4a. Porcelain Stone Floor Tile (600x600 neutral polished stone):
make_box("Floor_Foyer", (foyer_cx, foyer_cy, 0.002), (foyer_w, foyer_depth, 0.01), "Mat_Tile_Grey")

# 4b. Natural Marble Threshold Step (현관 디딤석):
# Transition from tile floor (Z=0.002) up to wood flooring (Z=0.025):
make_box("Foyer_Threshold", (foyer_cx, foyer_y_start, 0.015), (foyer_w, 0.10, 0.025), "Mat_Marble_White", bevel_width=0.003)

# 4c. Floating Cashmere Shoe Cabinet (신발장 - 하부 띄움 시공):
# Located on East wall: X=12.56 to 12.88 (depth 0.32), Y=6.55 to 7.90 (length 1.35)
cab_w = 0.32
cab_l = 1.35
cab_x = 12.88 - cab_w / 2.0 # 12.72
cab_y = (6.55 + 7.90) / 2.0 # 7.225
# Cabinet body (floating from Z=0.20 to 2.25):
make_box("Foyer_Shoe_Cabinet_Body", (cab_x, cab_y, 1.225), (cab_w, cab_l, 2.05), "Mat_Cabinet_Cashmere", bevel_width=0.004)
# 2 Handleless Cashmere Doors:
make_box("Foyer_Shoe_Door1", (cab_x - cab_w/2.0 - 0.009, 6.88, 1.225), (0.018, 0.66, 2.02), "Mat_Cabinet_Cashmere", bevel_width=0.003)
make_box("Foyer_Shoe_Door2", (cab_x - cab_w/2.0 - 0.009, 7.56, 1.225), (0.018, 0.66, 2.02), "Mat_Cabinet_Cashmere", bevel_width=0.003)
# Under-cabinet floating gap indirect warm LED strip (Z=0.19):
make_box("Foyer_Shoe_LED_Strip", (cab_x, cab_y, 0.195), (cab_w - 0.04, cab_l - 0.06, 0.01), "Mat_Light_Warm_Strip")

# Staged everyday shoes under floating cabinet:
make_box("Foyer_Shoe_Pair1_L", (cab_x, 6.85, 0.04), (0.10, 0.26, 0.07), "Mat_Fabric_Grey", bevel_width=0.01)
make_box("Foyer_Shoe_Pair1_R", (cab_x, 7.00, 0.04), (0.10, 0.26, 0.07), "Mat_Fabric_Grey", bevel_width=0.01)
make_box("Foyer_Shoe_Pair2_L", (cab_x, 7.45, 0.04), (0.10, 0.26, 0.07), "Mat_Window_Frame", bevel_width=0.01)
make_box("Foyer_Shoe_Pair2_R", (cab_x, 7.60, 0.04), (0.10, 0.26, 0.07), "Mat_Window_Frame", bevel_width=0.01)

# 4d. Full-Length Mirror on West Wall:
# X=11.78, Y=6.65 to 7.80, Z=0.30 to 2.10
make_box("Foyer_Mirror_Frame", (11.785, 7.225, 1.20), (0.015, 1.15, 1.80), "Mat_Window_Frame", bevel_width=0.002)
make_box("Foyer_Mirror_Glass", (11.792, 7.225, 1.20), (0.005, 1.11, 1.76), "Mat_Mirror")

# 4e. Recessed Ceiling Motion Spotlight:
make_cylinder("Foyer_Spot_Trim", (foyer_cx, foyer_cy, 2.295), 0.045, 0.01, "Mat_Window_Frame")
make_cylinder("Foyer_Spot_Lens", (foyer_cx, foyer_cy, 2.292), 0.035, 0.005, "Mat_Bulb_Warm")
safe_remove("Light_Foyer_Spot")
f_light = bpy.data.lights.new("Light_Foyer_Spot", 'POINT')
f_light.energy = 25.0
f_light.color = (1.0, 0.95, 0.88)
f_lobj = bpy.data.objects.new("Light_Foyer_Spot", f_light)
col_light.objects.link(f_lobj)
f_lobj.location = (foyer_cx, foyer_cy, 2.25)

# -------------------------------------------------------------
# 5. CAMERA ADJUSTMENT: Cam_Foyer_POV
# -------------------------------------------------------------
# View from inside the entrance threshold looking into the apartment corridor
cam_f = bpy.data.objects.get("Cam_Foyer_POV")
if cam_f:
    cam_f.location = Vector((foyer_cx, foyer_y_start - 0.20, 1.45))
    cam_f.rotation_euler = Euler((math.radians(88.0), 0.0, math.radians(-115.0)), 'XYZ')
    cam_f.data.lens = 20.0
    print("Cam_Foyer_POV positioned at entrance threshold looking down interior hallway")

bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print("=== FOYER & ENTRANCE RECTIFICATION COMPLETED & SAVED ===")
'''

res = mcp_client.send_blender_command('execute_code', {'code': py_code})
print("Result:", res)
