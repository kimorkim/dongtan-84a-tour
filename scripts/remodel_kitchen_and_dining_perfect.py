"""Remodel Kitchen and Dining to 100% Match Official Prugio 84A Blueprint and E-Modelhouse.

Blueprint & Modelhouse Ground Truth:
1. Dining Table:
   - Oriented HORIZONTALLY (East-West) in front of peninsula and Alpha room wall.
   - 6-person seating (3 chairs North facing South, 3 chairs South facing North).
   - Polished white engineered stone top (Mat_Marble_White) with slim champagne/white steel frame.
   - Clears the West corridor (>1.5m wide) completely for open flow into the kitchen.
2. Kitchen Countertop ('ㄷ'자 연속 상판):
   - Single continuous height (Z = 0.86 to 0.89m) across North, East, and Peninsula.
   - North counter has an actual 880mm x 480mm cutout aperture for the undermount sink.
   - Peninsula has a flat single-level surface with matching bevel and cashmere base cabinet.
3. Kitchen Sink & Faucet:
   - Deep rectangular undermount stainless sink bowl (860mm x 460mm x 220mm deep).
   - Stainless dish drying rack on left, sponge basket on right, drain strainer at bottom.
   - Chrome swan-neck / goose-neck swivel faucet with side lever centered under Win_Kitchen (X=6.15).
4. Dishwasher & Refrigerator Wall:
   - Built-in stainless dishwasher under North counter (X=5.05 to 5.65).
   - Bespoke built-in refrigerator cabinet on West wall.
   - System air conditioner (시스템 에어컨) mounted on kitchen ceiling.
5. Cooktop, Oven, Hood:
   - Flush 3-burner induction cooktop on East counter (Y=8.00).
   - Built-in black glass electric oven with stainless bar handle directly underneath.
   - Slim black sliding range hood above induction under upper cabinet.
6. Lighting & Materials:
   - Remove harsh fluorescent bars (ProK_CeilStrip1/2); add recessed LED downlights.
   - Full-height Calacatta marble backsplash (Mat_Marble_White) from counter to upper cabinets.
7. Camera Tuning:
   - Cam_Kitchen_POV framed to replicate display_03_part_1.jpg.
"""

import sys, os
sys.path.insert(0, os.path.abspath("."))
import mcp_client

py_code = r'''
import bpy
import bmesh
import math
from mathutils import Vector, Euler

def get_or_create_col(col_name):
    col = bpy.data.collections.get(col_name)
    if not col:
        col = bpy.data.collections.new(col_name)
        bpy.context.scene.collection.children.link(col)
    return col

col_furn = get_or_create_col("Apt_Furnishings")
col_light = get_or_create_col("Apt_Lighting")
col_struct = get_or_create_col("Apt_Corrected_Structure")

def safe_remove(obj_name):
    o = bpy.data.objects.get(obj_name)
    if o:
        m = o.data if o.type == 'MESH' else None
        bpy.data.objects.remove(o, do_unlink=True)
        if m and m.users == 0:
            bpy.data.meshes.remove(m)
        print(f"Removed {obj_name}")

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
    
    # Apply scale
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

print("=== STARTING COMPLETE KITCHEN & DINING REMODEL ===")

# -------------------------------------------------------------
# 1. REMOVE OLD/INACCURATE DINING & PENINSULA OBJECTS
# -------------------------------------------------------------
safe_remove_matching([
    "Chair_W1", "Chair_W2", "Chair_E1", "Chair_E2",
    "Dining_Leg", "Dining_Table_Top", "DiningProp_",
    "ProK_CeilStrip1", "ProK_CeilStrip2",
    "Pendant_Dining", "Downlight_Dining"
])

# -------------------------------------------------------------
# 2. CREATE CONTINUOUS 'ㄷ'자 KITCHEN COUNTERTOP WITH SINK APERTURE
# -------------------------------------------------------------
# Remove old countertops
safe_remove("Kitchen_Top_North")
safe_remove("Kitchen_Top_East")
safe_remove("Kitchen_Top_Pen")
safe_remove("Kitchen_Base_Pen")
safe_remove("Kitchen_Kick_Pen")
safe_remove("ProK_DoorP3")
safe_remove("ProK_DoorP4")
safe_remove("ProK_EndPanelW")

# North Counter Dimensions:
# X: 4.98 to 7.825 (width = 2.845)
# Y: 9.40 to 10.05 (depth = 0.65)
# Z: 0.86 to 0.89 (thickness = 0.03)
# Sink cutout at X: 5.71 to 6.59 (width = 0.88), Y: 9.47 to 9.95 (depth = 0.48)
# To create a clean geometry with sink opening, we build North Counter from 3 pieces:
# NorthLeft (X=4.98 to 5.71), NorthBridgeFront (under sink Y=9.40 to 9.47), NorthBridgeBack (behind sink Y=9.95 to 10.05), NorthRight (X=6.59 to 7.825)

# 2a. Countertop North Left:
w_nl = 5.71 - 4.98 # 0.73
x_nl = 4.98 + w_nl / 2.0
make_box("Kitchen_Top_North_L", (x_nl, 9.725, 0.875), (w_nl, 0.65, 0.03), "Mat_Marble_White", bevel_width=0.005)

# 2b. Countertop North Front Rim (in front of sink):
w_sink = 6.59 - 5.71 # 0.88
x_sink = (5.71 + 6.59) / 2.0 # 6.15
d_frim = 9.47 - 9.40 # 0.07
y_frim = 9.40 + d_frim / 2.0
make_box("Kitchen_Top_North_RimF", (x_sink, y_frim, 0.875), (w_sink, d_frim, 0.03), "Mat_Marble_White", bevel_width=0.004)

# 2c. Countertop North Back Deck (behind sink, faucet mounts here):
d_brim = 10.05 - 9.95 # 0.10
y_brim = 9.95 + d_brim / 2.0
make_box("Kitchen_Top_North_RimB", (x_sink, y_brim, 0.875), (w_sink, d_brim, 0.03), "Mat_Marble_White", bevel_width=0.004)

# 2d. Countertop North Right:
w_nr = 7.825 - 6.59 # 1.235
x_nr = 6.59 + w_nr / 2.0
make_box("Kitchen_Top_North_R", (x_nr, 9.725, 0.875), (w_nr, 0.65, 0.03), "Mat_Marble_White", bevel_width=0.005)

# 2e. Countertop East (Cooktop side):
# X: 7.175 to 7.825 (width = 0.65), Y: 6.72 to 9.40 (length = 2.68), Z: 0.86 to 0.89
make_box("Kitchen_Top_East", (7.50, (6.72 + 9.40) / 2.0, 0.875), (0.65, 9.40 - 6.72, 0.03), "Mat_Marble_White", bevel_width=0.005)

# 2f. Peninsula Countertop (Island extension):
# Branches west from East counter: X: 6.50 to 7.825 (length = 1.325), Y: 6.07 to 6.72 (width = 0.65), Z: 0.86 to 0.89
make_box("Kitchen_Top_Peninsula", ((6.50 + 7.825)/2.0, 6.395, 0.875), (7.825 - 6.50, 0.65, 0.03), "Mat_Marble_White", bevel_width=0.006)

# 2g. Peninsula Base Cabinet & End Panel:
# Base cabinet underneath peninsula: X: 6.52 to 7.80, Y: 6.09 to 6.70, Z: 0.07 to 0.86 (height = 0.79)
make_box("Kitchen_Base_Pen", ((6.52 + 7.80)/2.0, 6.395, 0.07 + 0.395), (7.80 - 6.52, 0.61, 0.79), "Mat_Cabinet_Cashmere", bevel_width=0.005)
# Toe kick
make_box("Kitchen_Kick_Pen", ((6.55 + 7.80)/2.0, 6.43, 0.035), (7.80 - 6.55, 0.52, 0.07), "Mat_AC_Grill")
# Peninsula South Cabinet Doors (2 handleless slab doors):
make_box("ProK_DoorP1", (6.84, 6.08, 0.10 + 0.36), (0.58, 0.018, 0.72), "Mat_Cabinet_Cashmere", bevel_width=0.003)
make_box("ProK_DoorP2", (7.44, 6.08, 0.10 + 0.36), (0.58, 0.018, 0.72), "Mat_Cabinet_Cashmere", bevel_width=0.003)
# Peninsula West Waterfall / End Panel:
make_box("ProK_EndPanelW", (6.51, 6.395, 0.10 + 0.375), (0.02, 0.63, 0.75), "Mat_Cabinet_Cashmere", bevel_width=0.003)

# -------------------------------------------------------------
# 3. KITCHEN SINK, BASIN, RACK, STRAINER, AND GOOSE-NECK FAUCET
# -------------------------------------------------------------
safe_remove_matching(["Kitchen_Sink_"])

# 3a. Deep Rectangular Stainless Undermount Sink Bowl:
# Outer: 0.86 x 0.46, Z from 0.67 to 0.875 (depth = 0.205)
# We make an open box bowl: bottom slab + 4 walls + inside bevel
# Bottom slab:
make_box("Kitchen_Sink_Bottom", (6.15, 9.71, 0.675), (0.84, 0.44, 0.015), "Mat_Steel_Brushed")
# 4 interior walls:
make_box("Kitchen_Sink_WallF", (6.15, 9.495, 0.775), (0.84, 0.015, 0.19), "Mat_Steel_Brushed")
make_box("Kitchen_Sink_WallB", (6.15, 9.925, 0.775), (0.84, 0.015, 0.19), "Mat_Steel_Brushed")
make_box("Kitchen_Sink_WallL", (5.735, 9.71, 0.775), (0.015, 0.43, 0.19), "Mat_Steel_Brushed")
make_box("Kitchen_Sink_WallR", (6.565, 9.71, 0.775), (0.015, 0.43, 0.19), "Mat_Steel_Brushed")

# 3b. Circular Drain Strainer & Cover:
make_cylinder("Kitchen_Sink_DrainOuter", (6.25, 9.68, 0.685), 0.065, 0.008, "Mat_Steel_Brushed")
make_cylinder("Kitchen_Sink_DrainCover", (6.25, 9.68, 0.690), 0.052, 0.005, "Mat_Steel_Brushed")

# 3c. Stainless Wire Drying Rack (식기 건조 바구니 on Left side):
make_box("Kitchen_Sink_Rack_Frame", (5.90, 9.71, 0.865), (0.30, 0.42, 0.012), "Mat_Steel_Brushed")
for i, rx in enumerate([5.78, 5.84, 5.90, 5.96, 6.02]):
    make_cylinder(f"Kitchen_Sink_Rack_Wire{i}", (rx, 9.71, 0.865), 0.003, 0.40, "Mat_Steel_Brushed", rot=(math.radians(90), 0, 0))

# 3d. Modern Chrome Goose-Neck Faucet (스완넥 폭포수 수전):
# Base escutcheon at back deck:
make_cylinder("Kitchen_Faucet_Base", (6.15, 9.99, 0.895), 0.026, 0.020, "Mat_Chrome_Polished")
# Vertical riser neck:
make_cylinder("Kitchen_Faucet_Riser", (6.15, 9.99, 1.05), 0.014, 0.28, "Mat_Chrome_Polished")
# Top forward curve:
make_cylinder("Kitchen_Faucet_ArcH", (6.15, 9.93, 1.22), 0.014, 0.14, "Mat_Chrome_Polished", rot=(math.radians(90), 0, 0))
# Downward spout tip:
make_cylinder("Kitchen_Faucet_SpoutDown", (6.15, 9.85, 1.16), 0.014, 0.12, "Mat_Chrome_Polished")
make_cylinder("Kitchen_Faucet_Aerator", (6.15, 9.85, 1.09), 0.016, 0.02, "Mat_Steel_Brushed")
# Single side lever handle:
make_cylinder("Kitchen_Faucet_LeverBase", (6.18, 9.99, 0.94), 0.012, 0.03, "Mat_Chrome_Polished", rot=(0, math.radians(90), 0))
make_cylinder("Kitchen_Faucet_LeverArm", (6.20, 9.99, 0.99), 0.006, 0.10, "Mat_Chrome_Polished")

# -------------------------------------------------------------
# 4. DISHWASHER UNDER NORTH COUNTER (식기세척기)
# -------------------------------------------------------------
safe_remove_matching(["ProK_Dishwasher"])
make_box("ProK_Dishwasher_Body", (5.35, 9.72, 0.08 + 0.385), (0.59, 0.60, 0.77), "Mat_Cabinet_Cashmere")
make_box("ProK_Dishwasher_Door", (5.35, 9.41, 0.10 + 0.37), (0.588, 0.022, 0.74), "Mat_Steel_Brushed", bevel_width=0.004)
make_box("ProK_Dishwasher_Control", (5.35, 9.398, 0.81), (0.57, 0.005, 0.06), "Mat_Window_Frame")
make_box("ProK_Dishwasher_Handle", (5.35, 9.385, 0.77), (0.46, 0.016, 0.020), "Mat_Steel_Brushed")

# -------------------------------------------------------------
# 5. INDUCTION COOKTOP & BUILT-IN OVEN (3구 인덕션 & 광파오븐)
# -------------------------------------------------------------
safe_remove("Kitchen_Induction")
safe_remove_matching(["ProK_Oven"])
safe_remove_matching(["ProK_Hood"])

# 5a. Induction Cooktop (flush mounted on East counter at Y=8.00):
make_box("Kitchen_Induction_Glass", (7.50, 8.00, 0.892), (0.52, 0.60, 0.006), "Mat_Induction_Glass", bevel_width=0.002)
# 3 cooking zones (burner rings):
make_cylinder("Kitchen_Induction_Ring1", (7.50, 7.85, 0.896), 0.10, 0.002, "Mat_Steel_Brushed")
make_cylinder("Kitchen_Induction_Ring2", (7.43, 8.12, 0.896), 0.075, 0.002, "Mat_Steel_Brushed")
make_cylinder("Kitchen_Induction_Ring3", (7.57, 8.12, 0.896), 0.075, 0.002, "Mat_Steel_Brushed")

# 5b. Built-in Electric Oven underneath (광파오븐):
# Base cabinet opening at Y=8.00:
make_box("ProK_Oven_Cavity", (7.50, 8.00, 0.44), (0.58, 0.58, 0.60), "Mat_Window_Frame")
make_box("ProK_Oven_DoorGlass", (7.17, 8.00, 0.44), (0.02, 0.56, 0.56), "Mat_Glass_Tinted", bevel_width=0.004)
make_box("ProK_Oven_Handle", (7.14, 8.00, 0.64), (0.02, 0.46, 0.022), "Mat_Steel_Brushed")
make_box("ProK_Oven_ControlPanel", (7.168, 8.00, 0.68), (0.015, 0.54, 0.07), "Mat_Window_Frame")

# 5c. Range Hood above (슬림 슬라이딩 후드 at Z=1.48 to 1.55):
make_box("ProK_Hood_Body", (7.52, 8.00, 1.51), (0.42, 0.75, 0.06), "Mat_Window_Frame")
make_box("ProK_Hood_Fascia", (7.30, 8.00, 1.51), (0.02, 0.75, 0.05), "Mat_Steel_Brushed")
make_box("ProK_Hood_FilterL", (7.52, 7.86, 1.478), (0.36, 0.22, 0.008), "Mat_Steel_Brushed")
make_box("ProK_Hood_FilterR", (7.52, 8.14, 1.478), (0.36, 0.22, 0.008), "Mat_Steel_Brushed")

# -------------------------------------------------------------
# 6. FULL-HEIGHT CALACATTA MARBLE BACKSPLASH (주방 벽체)
# -------------------------------------------------------------
safe_remove("ProK_SplashNorth")
safe_remove("ProK_SplashEast")
# North wall backsplash (from counter Z=0.89 to upper cab Z=1.55, surrounding window):
# Left of window: X: 4.98 to 5.54 (width=0.56)
make_box("ProK_SplashNorth_L", (4.98 + 0.28, 10.04, 0.89 + 0.33), (0.56, 0.02, 0.66), "Mat_Marble_White")
# Right of window: X: 6.76 to 7.825 (width=1.065)
make_box("ProK_SplashNorth_R", (6.76 + 0.532, 10.04, 0.89 + 0.33), (1.065, 0.02, 0.66), "Mat_Marble_White")
# Under window sill strip: X: 5.54 to 6.76 (width=1.22, Z: 0.89 to 1.10)
make_box("ProK_SplashNorth_Mid", (6.15, 10.04, 0.89 + 0.105), (1.22, 0.02, 0.21), "Mat_Marble_White")
# East wall backsplash: Y: 6.55 to 9.72 (length=3.17, Z: 0.89 to 1.55)
make_box("ProK_SplashEast", (7.835, (6.55 + 9.72)/2.0, 0.89 + 0.33), (0.02, 9.72 - 6.55, 0.66), "Mat_Marble_White")

# -------------------------------------------------------------
# 7. 6-PERSON HORIZONTAL DINING TABLE & MODERN CHAIRS
# -------------------------------------------------------------
# Center of dining table: X = 6.95, Y = 5.20
# Width along X = 1.60m, Depth along Y = 0.85m, Tabletop height = 0.74m
table_cx, table_cy = 6.95, 5.20
tw, td, th = 1.60, 0.85, 0.74
top_thick = 0.035

# 7a. Table Top (Polished Engineered Quartz / White Marble):
make_box("Dining_Table_Top", (table_cx, table_cy, th - top_thick/2.0), (tw, td, top_thick), "Mat_Marble_White", bevel_width=0.008)

# 7b. Modern Slender Steel Legs (4 tapered tubular legs):
lx1, lx2 = table_cx - tw/2.0 + 0.07, table_cx + tw/2.0 - 0.07
ly1, ly2 = table_cy - td/2.0 + 0.07, table_cy + td/2.0 - 0.07
for idx, (lx, ly) in enumerate([(lx1, ly1), (lx2, ly1), (lx1, ly2), (lx2, ly2)]):
    make_cylinder(f"Dining_Table_Leg_{idx+1}", (lx, ly, (th - top_thick)/2.0), 0.022, th - top_thick, "Mat_Steel_Brushed")
# Under-table support apron frame:
make_box("Dining_Table_ApronX1", (table_cx, ly1, th - top_thick - 0.02), (tw - 0.18, 0.03, 0.04), "Mat_Steel_Brushed")
make_box("Dining_Table_ApronX2", (table_cx, ly2, th - top_thick - 0.02), (tw - 0.18, 0.03, 0.04), "Mat_Steel_Brushed")
make_box("Dining_Table_ApronY1", (lx1, table_cy, th - top_thick - 0.02), (0.03, td - 0.18, 0.04), "Mat_Steel_Brushed")
make_box("Dining_Table_ApronY2", (lx2, table_cy, th - top_thick - 0.02), (0.03, td - 0.18, 0.04), "Mat_Steel_Brushed")

# 7c. 6 Modern Dining Chairs (Modelhouse Style: Curved Backrest + Cashmere/Beige Fabric Seat Pad):
# North Chairs (3 facing South towards table):
chair_xs = [table_cx - 0.52, table_cx, table_cx + 0.52] # 6.43, 6.95, 7.47
north_y = table_cy + td/2.0 + 0.16 # 5.785
south_y = table_cy - td/2.0 - 0.18 # 4.595

def build_chair(cname, cx, cy, facing_angle_rad):
    # Seat height = 0.45m, size = 0.44m x 0.42m
    # Cushion:
    make_box(f"{cname}_Seat", (cx, cy, 0.45), (0.44, 0.42, 0.05), "Mat_Fabric_Grey", bevel_width=0.012)
    # 4 Legs:
    leg_r = 0.015
    for l_i, (dx, dy) in enumerate([(-0.17, -0.16), (0.17, -0.16), (-0.17, 0.16), (0.17, 0.16)]):
        make_cylinder(f"{cname}_Leg{l_i+1}", (cx + dx, cy + dy, 0.21), leg_r, 0.42, "Mat_Steel_Brushed")
    # Backrest upright posts and curved cushion:
    # If facing south (facing_angle = pi), back is at +Y
    back_y_sign = 1.0 if facing_angle_rad > 2.0 else -1.0
    by = cy + back_y_sign * 0.18
    make_cylinder(f"{cname}_PostL", (cx - 0.16, by, 0.58), 0.012, 0.30, "Mat_Steel_Brushed")
    make_cylinder(f"{cname}_PostR", (cx + 0.16, by, 0.58), 0.012, 0.30, "Mat_Steel_Brushed")
    # Curved backrest bar:
    make_box(f"{cname}_Back", (cx, by, 0.72), (0.42, 0.035, 0.14), "Mat_Fabric_Grey", bevel_width=0.010)

# Build 3 North Chairs (facing South):
for idx, cx in enumerate(chair_xs):
    build_chair(f"Chair_N{idx+1}", cx, north_y, math.pi)

# Build 3 South Chairs (facing North):
for idx, cx in enumerate(chair_xs):
    build_chair(f"Chair_S{idx+1}", cx, south_y, 0.0)

# 7d. Dining Table Settings & Decor (D/P Display Props):
# 6 place settings:
for idx, cx in enumerate(chair_xs):
    # North place settings:
    py_n = table_cy + 0.24
    make_box(f"Dining_Mat_N{idx+1}", (cx, py_n, th + 0.002), (0.36, 0.26, 0.004), "Mat_Curtain")
    make_cylinder(f"Dining_Plate_N{idx+1}", (cx, py_n, th + 0.008), 0.11, 0.010, "Mat_Steel_Brushed")
    make_cylinder(f"Dining_Bowl_N{idx+1}", (cx, py_n, th + 0.020), 0.065, 0.024, "Mat_Marble_White")
    make_cylinder(f"Dining_Glass_N{idx+1}", (cx + 0.12, py_n + 0.08, th + 0.045), 0.032, 0.085, "Mat_Glass_Clear")
    
    # South place settings:
    py_s = table_cy - 0.24
    make_box(f"Dining_Mat_S{idx+1}", (cx, py_s, th + 0.002), (0.36, 0.26, 0.004), "Mat_Curtain")
    make_cylinder(f"Dining_Plate_S{idx+1}", (cx, py_s, th + 0.008), 0.11, 0.010, "Mat_Steel_Brushed")
    make_cylinder(f"Dining_Bowl_S{idx+1}", (cx, py_s, th + 0.020), 0.065, 0.024, "Mat_Marble_White")
    make_cylinder(f"Dining_Glass_S{idx+1}", (cx + 0.12, py_s - 0.08, th + 0.045), 0.032, 0.085, "Mat_Glass_Clear")

# Centerpiece Vase & Flowers:
make_cylinder("Dining_Vase_Base", (table_cx, table_cy, th + 0.08), 0.045, 0.16, "Mat_Glass_Tinted")
make_cylinder("Dining_Vase_Flora1", (table_cx - 0.02, table_cy, th + 0.24), 0.005, 0.22, "Mat_Curtain")
make_cylinder("Dining_Vase_Flora2", (table_cx + 0.02, table_cy + 0.01, th + 0.25), 0.005, 0.24, "Mat_Curtain")

# 7e. Dining Pendant Lighting (Centered over the Horizontal Table):
# Two stylish Scandinavian minimalist pendants hanging at X=6.55 and X=7.35:
for p_idx, px in enumerate([table_cx - 0.40, table_cx + 0.40]):
    make_cylinder(f"Pendant_Dining{p_idx+1}_Cord", (px, table_cy, 1.85), 0.005, 0.70, "Mat_Window_Frame")
    make_cylinder(f"Pendant_Dining{p_idx+1}_Shade", (px, table_cy, 1.55), 0.11, 0.16, "Mat_Pendant_Black")
    # Soft warm emission bulb inside shade:
    bulb = make_cylinder(f"Pendant_Dining{p_idx+1}_Bulb", (px, table_cy, 1.50), 0.035, 0.035, "Mat_Bulb_Warm")
    # Real point light for gentle table illumination:
    light_name = f"Light_Dining_Pendant_{p_idx+1}"
    safe_remove(light_name)
    ldata = bpy.data.lights.new(light_name, 'POINT')
    ldata.energy = 25.0
    ldata.color = (1.0, 0.94, 0.85)
    lobj = bpy.data.objects.new(light_name, ldata)
    col_light.objects.link(lobj)
    lobj.location = (px, table_cy, 1.48)

# -------------------------------------------------------------
# 8. CEILING SYSTEM AC & RECESSED SPOTLIGHTS (시스템 에어컨 & 매립등)
# -------------------------------------------------------------
safe_remove_matching(["Kitchen_System_AC", "Downlight_Kitchen_"])

# Ceiling System AC above corridor/fridge:
make_box("Kitchen_System_AC_Frame", (5.30, 6.80, 2.29), (0.48, 1.10, 0.02), "Mat_AC_Grill", bevel_width=0.004)
make_box("Kitchen_System_AC_Louver", (5.30, 6.80, 2.285), (0.38, 0.96, 0.01), "Mat_Cabinet_Cashmere")

# Clean, recessed ceiling downlights (matching display_03_part_1.jpg):
# 4 recessed spots in kitchen work zone:
for s_i, (sx, sy) in enumerate([(6.15, 9.20), (7.00, 8.00), (6.00, 7.50), (6.95, 6.50)]):
    make_cylinder(f"Downlight_Kitchen_Trim_{s_i+1}", (sx, sy, 2.295), 0.045, 0.01, "Mat_Window_Frame")
    make_cylinder(f"Downlight_Kitchen_Lens_{s_i+1}", (sx, sy, 2.292), 0.035, 0.005, "Mat_Bulb_Warm")
    dl_name = f"Light_Kitchen_Spot_{s_i+1}"
    safe_remove(dl_name)
    dl_data = bpy.data.lights.new(dl_name, 'POINT')
    dl_data.energy = 28.0
    dl_data.color = (1.0, 0.96, 0.90)
    dl_obj = bpy.data.objects.new(dl_name, dl_data)
    col_light.objects.link(dl_obj)
    dl_obj.location = (sx, sy, 2.25)

# -------------------------------------------------------------
# 9. CAMERA KITCHEN POV OPTIMIZATION (MATCHING display_03_part_1.jpg)
# -------------------------------------------------------------
cam_k = bpy.data.objects.get("Cam_Kitchen_POV")
if cam_k:
    cam_k.location = Vector((5.65, 3.45, 1.38))
    # Look slightly right and up towards kitchen counter and dining table:
    cam_k.rotation_euler = Euler((math.radians(88.0), 0.0, math.radians(-20.0)), 'XYZ')
    cam_k.data.lens = 22.0 # Wide angle matching official architectural photography
    print("Cam_Kitchen_POV adjusted to match display_03_part_1.jpg framing")

# Save file
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print("=== COMPLETE KITCHEN & DINING REMODEL FINISHED AND SAVED ===")
'''

res = mcp_client.send_blender_command('execute_code', {'code': py_code})
print("Result:", res)
