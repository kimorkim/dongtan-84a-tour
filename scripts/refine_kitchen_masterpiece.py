"""Refine Kitchen & Dining to Photorealistic Perfection matching Prugio 84A Modelhouse.

Key Refinements:
1. Carcass cleanup: Hollow out base cabinets under sink and oven to eliminate mesh overlap.
2. Sink & Faucet detailing: Goose-neck faucet with chrome shine, task light over sink, clear bowl definition.
3. Dining chairs: Warm cashmere/greige upholstery matching display_03_part_1.jpg.
4. Table staging: Elegant tableware with dusty rose & linen accents.
5. Pendants: Replace heavy black drums with sleek modern champagne/brass minimal pendants.
6. Refrigerator wall: Authentic Samsung Bespoke 4-door matte glass panels with recessed grip grooves.
7. Under-cabinet lighting: Soften emission from 15.0 to 2.8 for warm, natural ambient glow.
8. Two camera renders:
   - Cam_Kitchen_POV (overall view matching display_03_part_1.jpg)
   - Cam_Kitchen_Prep_POV (close-up corner matching display_03_part_2.jpg)
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

print("=== STARTING KITCHEN REFINEMENT ===")

# -------------------------------------------------------------
# 1. SOFTEN UNDER-CABINET LED EMISSION (NO MORE BLOWN OUT GLARE)
# -------------------------------------------------------------
mat_strip = bpy.data.materials.get("Mat_Light_Warm_Strip")
if mat_strip and mat_strip.use_nodes:
    for n in mat_strip.node_tree.nodes:
        if n.type == 'EMISSION':
            n.inputs['Strength'].default_value = 2.8 # gentle warm glow
            n.inputs['Color'].default_value = (1.0, 0.90, 0.78, 1.0) # 3000K warm LED
            print("Softened Mat_Light_Warm_Strip emission to 2.8")

# -------------------------------------------------------------
# 2. CREATE DEDICATED MATERIALS FOR BESPOKE, CHAIRS, ACCENTS
# -------------------------------------------------------------
def get_or_create_mat(mat_name):
    mat = bpy.data.materials.get(mat_name)
    if not mat:
        mat = bpy.data.materials.new(mat_name)
        mat.use_nodes = True
    return mat

# Bespoke Satin Glass Material:
mat_bespoke = get_or_create_mat("Mat_Bespoke_Glass")
bsdf_b = mat_bespoke.node_tree.nodes.get("Principled BSDF")
if bsdf_b:
    bsdf_b.inputs['Base Color'].default_value = (0.92, 0.92, 0.91, 1.0) # satin off-white
    bsdf_b.inputs['Roughness'].default_value = 0.08
    bsdf_b.inputs['IOR'].default_value = 1.52

# Chair Cashmere Fabric Material:
mat_chair_fab = get_or_create_mat("Mat_Chair_Fabric")
bsdf_c = mat_chair_fab.node_tree.nodes.get("Principled BSDF")
if bsdf_c:
    bsdf_c.inputs['Base Color'].default_value = (0.78, 0.73, 0.67, 1.0) # warm greige/cashmere
    bsdf_c.inputs['Roughness'].default_value = 0.85

# Champagne Brass Accent:
mat_brass = get_or_create_mat("Mat_Champagne_Brass")
bsdf_br = mat_brass.node_tree.nodes.get("Principled BSDF")
if bsdf_br:
    bsdf_br.inputs['Base Color'].default_value = (0.85, 0.78, 0.65, 1.0)
    bsdf_br.inputs['Metallic'].default_value = 0.90
    bsdf_br.inputs['Roughness'].default_value = 0.25

# Dusty Rose Ceramic Plate:
mat_rose = get_or_create_mat("Mat_Ceramic_Rose")
bsdf_r = mat_rose.node_tree.nodes.get("Principled BSDF")
if bsdf_r:
    bsdf_r.inputs['Base Color'].default_value = (0.78, 0.62, 0.60, 1.0) # dusty rose
    bsdf_r.inputs['Roughness'].default_value = 0.20

# -------------------------------------------------------------
# 3. BASE CABINETS DE-COLLISION & CLEAN SECTIONS
# -------------------------------------------------------------
safe_remove("Kitchen_Base_North")
safe_remove("Kitchen_Base_East")
safe_remove("Kitchen_Kick_North")
safe_remove("Kitchen_Kick_East")
safe_remove_matching(["ProK_DoorN"])
safe_remove_matching(["ProK_DoorE"])

# North Base Cabinets:
# X: 4.98 to 7.825
# 3a. Left Section (Dishwasher space X=4.98 to 5.65): Left end panel only
make_box("Kitchen_Base_North_EndL", (4.99, 9.725, 0.465), (0.02, 0.61, 0.79), "Mat_Cabinet_Cashmere")

# 3b. Middle Section (Sink base cabinet X=5.65 to 6.65, width=1.00m):
# Floor shelf at Z=0.07 to 0.09:
make_box("Kitchen_Base_Sink_Floor", (6.15, 9.725, 0.08), (0.98, 0.60, 0.02), "Mat_Cabinet_Cashmere")
# Left and Right partition uprights:
make_box("Kitchen_Base_Sink_DivL", (5.66, 9.725, 0.465), (0.02, 0.60, 0.77), "Mat_Cabinet_Cashmere")
make_box("Kitchen_Base_Sink_DivR", (6.64, 9.725, 0.465), (0.02, 0.60, 0.77), "Mat_Cabinet_Cashmere")
# Sink front doors (2 doors under sink):
make_box("ProK_DoorN_SinkL", (5.89, 9.41, 0.465), (0.47, 0.018, 0.73), "Mat_Cabinet_Cashmere", bevel_width=0.003)
make_box("ProK_DoorN_SinkR", (6.39, 9.41, 0.465), (0.47, 0.018, 0.73), "Mat_Cabinet_Cashmere", bevel_width=0.003)

# 3c. Right North Section (Storage cabinet X=6.65 to 7.825, width=1.175m):
make_box("Kitchen_Base_North_R", ((6.65 + 7.825)/2.0, 9.725, 0.465), (7.825 - 6.65, 0.61, 0.79), "Mat_Cabinet_Cashmere")
make_box("ProK_DoorN_R1", (6.93, 9.41, 0.465), (0.54, 0.018, 0.73), "Mat_Cabinet_Cashmere", bevel_width=0.003)
make_box("ProK_DoorN_R2", (7.49, 9.41, 0.465), (0.54, 0.018, 0.73), "Mat_Cabinet_Cashmere", bevel_width=0.003)

# North Kick Plate:
make_box("Kitchen_Kick_North", (6.40, 9.47, 0.035), (2.80, 0.02, 0.07), "Mat_AC_Grill")

# 3d. East Base Cabinets:
# Y: 6.72 to 9.40 (length=2.68m), Oven at Y=8.00 (Y=7.70 to 8.30)
# East North cabinet (Y=8.30 to 9.40):
make_box("Kitchen_Base_East_N", (7.50, (8.30 + 9.40)/2.0, 0.465), (0.61, 9.40 - 8.30, 0.79), "Mat_Cabinet_Cashmere")
make_box("ProK_DoorE_N1", (7.185, (8.30 + 9.40)/2.0, 0.465), (0.018, 9.40 - 8.30 - 0.02, 0.73), "Mat_Cabinet_Cashmere", bevel_width=0.003)

# East South cabinet (Y=6.72 to 7.70):
make_box("Kitchen_Base_East_S", (7.50, (6.72 + 7.70)/2.0, 0.465), (0.61, 7.70 - 6.72, 0.79), "Mat_Cabinet_Cashmere")
make_box("ProK_DoorE_S1", (7.185, (6.72 + 7.70)/2.0, 0.465), (0.018, 7.70 - 6.72 - 0.02, 0.73), "Mat_Cabinet_Cashmere", bevel_width=0.003)

# East Kick Plate:
make_box("Kitchen_Kick_East", (7.24, (6.72 + 9.40)/2.0, 0.035), (0.02, 9.40 - 6.72, 0.07), "Mat_AC_Grill")

# -------------------------------------------------------------
# 4. SINK & GOOSE-NECK FAUCET ENHANCEMENT
# -------------------------------------------------------------
# Scale up goose-neck faucet slightly so its silhouette rises above the window sill line
safe_remove_matching(["Kitchen_Faucet_"])
# Faucet base:
make_cylinder("Kitchen_Faucet_Base", (6.15, 9.99, 0.895), 0.028, 0.022, "Mat_Chrome_Polished")
# Tall vertical riser:
make_cylinder("Kitchen_Faucet_Riser", (6.15, 9.99, 1.08), 0.015, 0.35, "Mat_Chrome_Polished")
# Upper curve arch:
make_cylinder("Kitchen_Faucet_ArcH", (6.15, 9.92, 1.28), 0.015, 0.16, "Mat_Chrome_Polished", rot=(math.radians(90), 0, 0))
# Downward spout:
make_cylinder("Kitchen_Faucet_SpoutDown", (6.15, 9.83, 1.20), 0.015, 0.14, "Mat_Chrome_Polished")
make_cylinder("Kitchen_Faucet_Aerator", (6.15, 9.83, 1.12), 0.018, 0.025, "Mat_Steel_Brushed")
# Mixer lever handle:
make_cylinder("Kitchen_Faucet_LeverBase", (6.185, 9.99, 0.95), 0.012, 0.035, "Mat_Chrome_Polished", rot=(0, math.radians(90), 0))
make_cylinder("Kitchen_Faucet_LeverArm", (6.205, 9.99, 1.01), 0.007, 0.11, "Mat_Chrome_Polished")

# Dedicated soft task spot over the sink:
safe_remove("Light_Sink_Task")
sink_light = bpy.data.lights.new("Light_Sink_Task", 'SPOT')
sink_light.energy = 22.0
sink_light.color = (1.0, 0.95, 0.88)
sink_light.spot_size = math.radians(65)
sink_light.spot_blend = 0.4
sink_lobj = bpy.data.objects.new("Light_Sink_Task", sink_light)
col_light.objects.link(sink_lobj)
sink_lobj.location = (6.15, 9.80, 2.25)
sink_lobj.rotation_euler = Euler((0, 0, 0), 'XYZ')

# -------------------------------------------------------------
# 5. REFRIGERATOR BESPOKE CABINET REFINEMENT (WEST WALL)
# -------------------------------------------------------------
safe_remove_matching(["Kitchen_Fridge_Wall_Door_"])
safe_remove_matching(["ProK_Bespoke_"])

# Refrigerator Wall: X=4.65 to 5.00, Y=7.30 to 9.25
# 4 Bespoke Door Panels (2 Top, 2 Bottom) + Kimchi/Pantry Door
# Dark perimeter frame:
make_box("ProK_Bespoke_Frame", (4.985, 8.15, 1.10), (0.015, 1.70, 2.10), "Mat_Window_Frame")
# Bespoke Door 1 (Top Left):
make_box("ProK_Bespoke_DoorTL", (5.00, 7.71, 1.55), (0.02, 0.43, 0.94), "Mat_Bespoke_Glass", bevel_width=0.003)
# Bespoke Door 2 (Top Right):
make_box("ProK_Bespoke_DoorTR", (5.00, 8.17, 1.55), (0.02, 0.43, 0.94), "Mat_Bespoke_Glass", bevel_width=0.003)
# Bespoke Door 3 (Bottom Left):
make_box("ProK_Bespoke_DoorBL", (5.00, 7.71, 0.52), (0.02, 0.43, 0.94), "Mat_Bespoke_Glass", bevel_width=0.003)
# Bespoke Door 4 (Bottom Right):
make_box("ProK_Bespoke_DoorBR", (5.00, 8.17, 0.52), (0.02, 0.43, 0.94), "Mat_Bespoke_Glass", bevel_width=0.003)
# Kimchi / Tall Pantry Door on the right (Y=8.45 to 8.95):
make_box("ProK_Bespoke_Kimchi", (5.00, 8.70, 1.05), (0.02, 0.50, 2.00), "Mat_Bespoke_Glass", bevel_width=0.003)

# -------------------------------------------------------------
# 6. DINING CHAIRS & TABLEWARE UPDATE
# -------------------------------------------------------------
# Update all chair upholstery to Mat_Chair_Fabric
for c_obj in bpy.data.objects:
    if c_obj.name.startswith("Chair_N") or c_obj.name.startswith("Chair_S"):
        if "Seat" in c_obj.name or "Back" in c_obj.name:
            c_obj.data.materials.clear()
            c_obj.data.materials.append(mat_chair_fab)

# Update plates to dusty rose ceramic & glasses
for i in range(1, 4):
    p_n = bpy.data.objects.get(f"Dining_Plate_N{i}")
    if p_n:
        p_n.data.materials.clear()
        p_n.data.materials.append(mat_rose)
    p_s = bpy.data.objects.get(f"Dining_Plate_S{i}")
    if p_s:
        p_s.data.materials.clear()
        p_s.data.materials.append(mat_rose)

# -------------------------------------------------------------
# 7. SLEEK MODERN PENDANTS (CHAMPAGNE BRASS / GLASS ACCENT)
# -------------------------------------------------------------
safe_remove_matching(["Pendant_Dining"])
safe_remove_matching(["Light_Dining_Pendant"])

table_cx = 6.95
table_cy = 5.20
for p_idx, px in enumerate([table_cx - 0.42, table_cx + 0.42]):
    # Ultra-thin canopy:
    make_cylinder(f"Pendant_Dining{p_idx+1}_Canopy", (px, table_cy, 2.29), 0.04, 0.015, "Mat_Champagne_Brass")
    # Thin wire:
    make_cylinder(f"Pendant_Dining{p_idx+1}_Cord", (px, table_cy, 1.95), 0.003, 0.65, "Mat_Window_Frame")
    # Sleek champagne brass cylinder cap:
    make_cylinder(f"Pendant_Dining{p_idx+1}_BrassCap", (px, table_cy, 1.66), 0.035, 0.08, "Mat_Champagne_Brass")
    # Clear glass cylindrical shade:
    make_cylinder(f"Pendant_Dining{p_idx+1}_Glass", (px, table_cy, 1.55), 0.075, 0.16, "Mat_Glass_Clear")
    # Warm filament bulb:
    make_cylinder(f"Pendant_Dining{p_idx+1}_Bulb", (px, table_cy, 1.55), 0.025, 0.05, "Mat_Bulb_Warm")
    # Soft warm point light:
    pl = bpy.data.lights.new(f"Light_Dining_Pendant_{p_idx+1}", 'POINT')
    pl.energy = 16.0
    pl.color = (1.0, 0.94, 0.85)
    pl_obj = bpy.data.objects.new(f"Light_Dining_Pendant_{p_idx+1}", pl)
    col_light.objects.link(pl_obj)
    pl_obj.location = (px, table_cy, 1.52)

# -------------------------------------------------------------
# 8. TWO TARGET CAMERAS FOR PRESENTATION
# -------------------------------------------------------------
# 8a. Cam_Kitchen_POV (Overall modelhouse view matching display_03_part_1.jpg):
cam_k = bpy.data.objects.get("Cam_Kitchen_POV")
if cam_k:
    cam_k.location = Vector((5.75, 3.55, 1.50))
    cam_k.rotation_euler = Euler((math.radians(87.5), 0.0, math.radians(-18.5)), 'XYZ')
    cam_k.data.lens = 22.0

# 8b. Cam_Kitchen_Prep_POV (Corner close-up matching display_03_part_2.jpg):
safe_remove("Cam_Kitchen_Prep_POV")
cam_prep_data = bpy.data.cameras.new("Cam_Kitchen_Prep_POV")
cam_prep_data.lens = 19.0
cam_prep_obj = bpy.data.objects.new("Cam_Kitchen_Prep_POV", cam_prep_data)
col_furn.objects.link(cam_prep_obj)
cam_prep_obj.location = Vector((5.95, 7.30, 1.40))
cam_prep_obj.rotation_euler = Euler((math.radians(82.0), 0.0, math.radians(28.0)), 'XYZ')

bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print("=== KITCHEN REFINEMENT COMPLETED AND SAVED ===")
'''

res = mcp_client.send_blender_command('execute_code', {'code': py_code})
print("Result:", res)
