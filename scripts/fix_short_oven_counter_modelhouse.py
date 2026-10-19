"""Fix Kitchen East Counter Length to Match Official Modelhouse (display_03_part_3.jpg).

Ground Truth:
1. East Counter is SHORT and COMPACT:
   - North counter depth: 0.65m (Y=10.05 to 9.40).
   - East counter only extends ~1.60m from North wall!
   - Corner filler: Y=9.40 to 9.15 (0.25m).
   - 3-burner Induction & Oven: Y=9.15 to 8.55 (0.60m, centered at Y=8.85).
   - Peninsula transition: Y=8.55 to 8.45 (0.10m).
   - Peninsula Counter branches West: Y=7.75 to 8.45 (width=0.70m, X=6.55 to 7.825).
   - Once the oven is placed, the counter ends and turns into the peninsula!
2. Dining Table & Chairs:
   - Centered in front of the peninsula at Y=6.70 (X=6.95).
   - 6 chairs: North at Y=7.30, South at Y=6.05.
   - Pendants & downlight shifted to Y=6.70.
3. Upper Cabinets & East Backsplash:
   - Shortened to match East counter (Y=8.45 to 9.70).
   - Hood centered over induction at Y=8.85.
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

print("=== STARTING SHORT OVEN COUNTER RECTIFICATION ===")

# -------------------------------------------------------------
# 1. SHORTEN EAST COUNTERTOP & PENINSULA
# -------------------------------------------------------------
# North wall face: Y=10.05
# North counter: Y=9.40 to 10.05
# East counter: from Y=9.40 down to Y=8.45 (length = 0.95m!)
# Peninsula branches west: from Y=7.75 to 8.45 (width = 0.70m, X=6.55 to 7.825)

# 1a. East Countertop (Quartz):
make_box("Kitchen_Top_East", (7.50, (8.45 + 9.40)/2.0, 0.875), (0.65, 9.40 - 8.45, 0.03), "Mat_Marble_White", bevel_width=0.005)

# 1b. Peninsula Countertop (Island extension):
# Branches West: X=6.55 to 7.825 (length=1.275m), Y=7.75 to 8.45 (width=0.70m), Z=0.86 to 0.89
make_box("Kitchen_Top_Peninsula", ((6.55 + 7.825)/2.0, 8.10, 0.875), (7.825 - 6.55, 0.70, 0.03), "Mat_Marble_White", bevel_width=0.006)

# 1c. Peninsula Base Cabinet & Doors:
# Base under peninsula: X=6.57 to 7.80, Y=7.77 to 8.43, Z=0.07 to 0.86 (height=0.79)
make_box("Kitchen_Base_Pen", ((6.57 + 7.80)/2.0, 8.10, 0.465), (7.80 - 6.57, 0.64, 0.79), "Mat_Cabinet_Cashmere", bevel_width=0.005)
# Toe kick
make_box("Kitchen_Kick_Pen", ((6.60 + 7.80)/2.0, 8.13, 0.035), (7.80 - 6.60, 0.54, 0.07), "Mat_AC_Grill")
# Peninsula South Doors (facing dining room at Y=7.76):
make_box("ProK_DoorP1", (6.88, 7.76, 0.465), (0.58, 0.018, 0.73), "Mat_Cabinet_Cashmere", bevel_width=0.003)
make_box("ProK_DoorP2", (7.48, 7.76, 0.465), (0.58, 0.018, 0.73), "Mat_Cabinet_Cashmere", bevel_width=0.003)
# West Waterfall End Panel at X=6.56:
make_box("ProK_EndPanelW", (6.56, 8.10, 0.465), (0.02, 0.66, 0.75), "Mat_Cabinet_Cashmere", bevel_width=0.003)

# 1d. East Base Cabinet (under Induction & Oven):
safe_remove("Kitchen_Base_East_N")
safe_remove("Kitchen_Base_East_S")
safe_remove("ProK_DoorE_N1")
safe_remove("ProK_DoorE_S1")
safe_remove("Kitchen_Kick_East")

# Base cabinet under East counter: Y=8.45 to 9.40
make_box("Kitchen_Base_East", (7.50, (8.45 + 9.40)/2.0, 0.465), (0.61, 9.40 - 8.45, 0.79), "Mat_Cabinet_Cashmere")
# Corner filler panel on left of oven (Y=9.15 to 9.40):
make_box("ProK_DoorE_Corner", (7.185, (9.15 + 9.40)/2.0, 0.465), (0.018, 9.40 - 9.15 - 0.01, 0.73), "Mat_Cabinet_Cashmere", bevel_width=0.003)
# East Kick plate:
make_box("Kitchen_Kick_East", (7.24, (8.45 + 9.40)/2.0, 0.035), (0.02, 9.40 - 8.45, 0.07), "Mat_AC_Grill")

# -------------------------------------------------------------
# 2. INDUCTION, BUILT-IN OVEN, AND RANGE HOOD REPOSITIONING
# -------------------------------------------------------------
# Center of cooktop & oven: Y = 8.85 (X = 7.50)
oven_cy = 8.85
safe_remove("Kitchen_Induction_Glass")
safe_remove_matching(["Kitchen_Induction_Ring"])
safe_remove_matching(["ProK_Oven_"])
safe_remove_matching(["ProK_Hood_"])
safe_remove_matching(["KitchenProp_Pot"])
safe_remove_matching(["KitchenProp_Kettle"])

# 2a. 3-Burner Induction Cooktop:
make_box("Kitchen_Induction_Glass", (7.50, oven_cy, 0.892), (0.52, 0.58, 0.006), "Mat_Induction_Glass", bevel_width=0.002)
make_cylinder("Kitchen_Induction_Ring1", (7.50, oven_cy - 0.12, 0.896), 0.095, 0.002, "Mat_Steel_Brushed")
make_cylinder("Kitchen_Induction_Ring2", (7.43, oven_cy + 0.11, 0.896), 0.070, 0.002, "Mat_Steel_Brushed")
make_cylinder("Kitchen_Induction_Ring3", (7.57, oven_cy + 0.11, 0.896), 0.070, 0.002, "Mat_Steel_Brushed")

# Stainless cooking pot on front ring:
make_cylinder("KitchenProp_Pot_Body", (7.50, oven_cy - 0.12, 0.965), 0.10, 0.13, "Mat_Steel_Brushed")
make_cylinder("KitchenProp_Pot_Lid", (7.50, oven_cy - 0.12, 1.035), 0.105, 0.015, "Mat_Steel_Brushed")
make_cylinder("KitchenProp_Pot_Knob", (7.50, oven_cy - 0.12, 1.055), 0.018, 0.025, "Mat_Window_Frame")

# 2b. Built-in Black Glass Electric Oven (광파오븐):
make_box("ProK_Oven_Cavity", (7.50, oven_cy, 0.44), (0.58, 0.58, 0.58), "Mat_Window_Frame")
make_box("ProK_Oven_DoorGlass", (7.17, oven_cy, 0.44), (0.02, 0.56, 0.54), "Mat_Glass_Tinted", bevel_width=0.004)
make_box("ProK_Oven_Handle", (7.14, oven_cy, 0.63), (0.02, 0.46, 0.022), "Mat_Steel_Brushed")
make_box("ProK_Oven_ControlPanel", (7.168, oven_cy, 0.675), (0.015, 0.54, 0.06), "Mat_Window_Frame")

# 2c. Slim Range Hood directly above induction:
make_box("ProK_Hood_Body", (7.52, oven_cy, 1.51), (0.42, 0.72, 0.06), "Mat_Window_Frame")
make_box("ProK_Hood_Fascia", (7.30, oven_cy, 1.51), (0.02, 0.72, 0.05), "Mat_Steel_Brushed")
make_cylinder("ProK_Hood_Filter1", (7.52, oven_cy - 0.15, 1.478), 0.12, 0.008, "Mat_Steel_Brushed")
make_cylinder("ProK_Hood_Filter2", (7.52, oven_cy + 0.15, 1.478), 0.12, 0.008, "Mat_Steel_Brushed")

# -------------------------------------------------------------
# 3. EAST UPPER CABINETS & BACKSPLASH (SHORTENED)
# -------------------------------------------------------------
safe_remove("ProK_SplashEast")
safe_remove("ProK_UpperEast")
safe_remove_matching(["ProK_UpperEast_LED"])

# East Backsplash: Y=8.45 to 9.70 (length=1.25m, Z=0.89 to 1.55)
make_box("ProK_SplashEast", (7.835, (8.45 + 9.70)/2.0, 1.22), (0.02, 9.70 - 8.45, 0.66), "Mat_Marble_White")

# East Upper Cabinets: Y=8.45 to 9.70
make_box("ProK_UpperEast", (7.68, (8.45 + 9.70)/2.0, 1.90), (0.32, 9.70 - 8.45, 0.70), "Mat_Cabinet_Cashmere", bevel_width=0.004)
# Warm under-cabinet LED task strip:
make_box("ProK_UpperEast_LED", (7.68, (8.45 + 9.70)/2.0, 1.535), (0.28, 9.70 - 8.45 - 0.06, 0.015), "Mat_Light_Warm_Strip")

# -------------------------------------------------------------
# 4. PENINSULA ACCENTS (FRUIT BOWL & CUTTING BOARD)
# -------------------------------------------------------------
safe_remove_matching(["KitchenProp_Fruit"])
# Move fruit bowl / cutting board onto peninsula at X=7.10, Y=8.10, Z=0.89
make_cylinder("KitchenProp_Fruit_Bowl", (7.10, 8.10, 0.91), 0.14, 0.04, "Mat_Ceramic_Rose")
for f_i, (fx, fy) in enumerate([(7.08, 8.08), (7.13, 8.11), (7.07, 8.13), (7.10, 8.10)]):
    make_cylinder(f"KitchenProp_Fruit_Lemon{f_i+1}", (fx, fy, 0.94 + (0.025 if f_i==3 else 0)), 0.03, 0.04, "Mat_Bulb_Warm")

# -------------------------------------------------------------
# 5. HORIZONTAL 6-PERSON DINING TABLE & CHAIRS (REPOSITIONED TO Y=6.70)
# -------------------------------------------------------------
table_cx = 6.95
table_cy = 6.70
tw, td, th = 1.60, 0.85, 0.74
top_thick = 0.035

# Table top:
top_obj = bpy.data.objects.get("Dining_Table_Top")
if top_obj:
    top_obj.location = Vector((table_cx, table_cy, th - top_thick/2.0))

# Legs:
lx1, lx2 = table_cx - tw/2.0 + 0.07, table_cx + tw/2.0 - 0.07
ly1, ly2 = table_cy - td/2.0 + 0.07, table_cy + td/2.0 - 0.07
for idx, (lx, ly) in enumerate([(lx1, ly1), (lx2, ly1), (lx1, ly2), (lx2, ly2)]):
    leg = bpy.data.objects.get(f"Dining_Table_Leg_{idx+1}")
    if leg:
        leg.location = Vector((lx, ly, (th - top_thick)/2.0))

for a_name, ax, ay, sx, sy in [
    ("Dining_Table_ApronX1", table_cx, ly1, tw - 0.18, 0.03),
    ("Dining_Table_ApronX2", table_cx, ly2, tw - 0.18, 0.03),
    ("Dining_Table_ApronY1", lx1, table_cy, 0.03, td - 0.18),
    ("Dining_Table_ApronY2", lx2, table_cy, 0.03, td - 0.18),
]:
    ap = bpy.data.objects.get(a_name)
    if ap:
        ap.location = Vector((ax, ay, th - top_thick - 0.02))

# Chairs:
chair_xs = [table_cx - 0.52, table_cx, table_cx + 0.52]
north_y = table_cy + td/2.0 + 0.16 # 7.285
south_y = table_cy - td/2.0 - 0.18 # 6.095

for idx, cx in enumerate(chair_xs):
    # North chair:
    cname_n = f"Chair_N{idx+1}"
    for o in bpy.data.objects:
        if o.name.startswith(cname_n):
            dy = o.location.y - 5.785 # previous north_y
            o.location.y = north_y + dy
            
    # South chair:
    cname_s = f"Chair_S{idx+1}"
    for o in bpy.data.objects:
        if o.name.startswith(cname_s):
            dy = o.location.y - 4.595 # previous south_y
            o.location.y = south_y + dy

# Table Settings & Decor:
for idx, cx in enumerate(chair_xs):
    # North place settings:
    py_n = table_cy + 0.24
    for prefix in ["Dining_Mat_N", "Dining_Plate_N", "Dining_Bowl_N", "Dining_Glass_N"]:
        o = bpy.data.objects.get(f"{prefix}{idx+1}")
        if o:
            o.location.y = py_n + (0.08 if "Glass" in prefix else 0.0)
            
    # South place settings:
    py_s = table_cy - 0.24
    for prefix in ["Dining_Mat_S", "Dining_Plate_S", "Dining_Bowl_S", "Dining_Glass_S"]:
        o = bpy.data.objects.get(f"{prefix}{idx+1}")
        if o:
            o.location.y = py_s - (0.08 if "Glass" in prefix else 0.0)

# Centerpiece Vase:
for v_name in ["Dining_Vase_Base", "Dining_Vase_Flora1", "Dining_Vase_Flora2"]:
    o = bpy.data.objects.get(v_name)
    if o:
        o.location.y = table_cy

# Pendants:
for p_idx in [1, 2]:
    for part in ["Canopy", "Cord", "BrassCap", "Glass", "Bulb"]:
        o = bpy.data.objects.get(f"Pendant_Dining{p_idx}_{part}")
        if o:
            o.location.y = table_cy
    lp = bpy.data.objects.get(f"Light_Dining_Pendant_{p_idx}")
    if lp:
        lp.location.y = table_cy

# Downlight over dining table:
dl_d = bpy.data.objects.get("Downlight_Dining")
if dl_d:
    dl_d.location = Vector((table_cx, table_cy, 2.25))

# -------------------------------------------------------------
# 6. CAMERA UPDATES MATCHING MODELHOUSE COMPOSITION
# -------------------------------------------------------------
# Cam_Kitchen_POV (Overall modelhouse view):
cam_k = bpy.data.objects.get("Cam_Kitchen_POV")
if cam_k:
    cam_k.location = Vector((5.75, 4.40, 1.50))
    cam_k.rotation_euler = Euler((math.radians(87.0), 0.0, math.radians(-19.0)), 'XYZ')
    cam_k.data.lens = 22.0

# Cam_Kitchen_Prep_POV (display_03_part_3.jpg: Standing in front of peninsula looking at sink & compact oven corner):
cam_prep = bpy.data.objects.get("Cam_Kitchen_Prep_POV")
if cam_prep:
    cam_prep.location = Vector((6.20, 7.50, 1.35))
    cam_prep.rotation_euler = Euler((math.radians(82.0), 0.0, math.radians(26.0)), 'XYZ')
    cam_prep.data.lens = 19.5

bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print("=== SHORT OVEN COUNTER RECTIFICATION COMPLETED & SAVED ===")
'''

res = mcp_client.send_blender_command('execute_code', {'code': py_code})
print("Result:", res)
