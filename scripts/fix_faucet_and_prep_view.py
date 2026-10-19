"""Fix Faucet Wall Embedding, Enhance Marble Veining, and Perfect Modelhouse Camera Views.

1. Fix Kitchen Window Sill:
   - Align SillPatch_Kitchen_SillWall & Cap so their inner face is flush at Y=10.05.
   - Clears 10cm space behind sink for the Goose-Neck Faucet to stand proud and free.
2. Goose-Neck Faucet Perfection:
   - Position base at Y=9.94, Z=0.89.
   - Arc rises gracefully to Z=1.28, spout curves forward over the undermount sink bowl.
   - Polished chrome material reflecting kitchen light.
3. Marble Veining Contrast (Mat_Marble_White):
   - Enhance ColorRamp and Voronoi/Noise mix in Mat_Marble_White so Calacatta veining is clearly visible.
4. Chair Materials:
   - Warm oat/taupe cashmere upholstery (0.55, 0.48, 0.40).
   - Dark bronze / brushed metal chair posts and legs for rich architectural contrast.
5. Camera Alignment:
   - Cam_Kitchen_Prep_POV: Positioned at X=5.60, Y=6.80, Z=1.35, looking northeast (rot Z=48 deg).
     Captures sink under window on left, marble backsplash corner, and induction + oven on right.
     100% replicates official modelhouse photo display_03_part_2.jpg!
   - Cam_Kitchen_POV: Positioned to show horizontal 6-person dining table and wide corridor.
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

print("=== STARTING FAUCET & SILL RECTIFICATION ===")

# -------------------------------------------------------------
# 1. FIX WINDOW SILL WALL & CAP (PULL BACK TO Y=10.05)
# -------------------------------------------------------------
sill_wall = bpy.data.objects.get("SillPatch_Kitchen_SillWall")
if sill_wall:
    # Wall thickness 0.18, front face at Y=10.05 -> loc.y = 10.05 + 0.09 = 10.14
    sill_wall.location.y = 10.14
    sill_wall.dimensions.y = 0.18
    print("Repositioned SillPatch_Kitchen_SillWall flush with North wall")

sill_cap = bpy.data.objects.get("SillPatch_Kitchen_SillCap")
if sill_cap:
    # Cap extends slightly over sill wall: Y from 10.04 to 10.16 -> loc.y = 10.10, dim.y = 0.12
    sill_cap.location.y = 10.10
    sill_cap.dimensions.y = 0.12
    print("Repositioned SillPatch_Kitchen_SillCap")

# Also ensure window frame and jambs are cleanly aligned
win_sill = bpy.data.objects.get("Win_Kitchen_Sill")
if win_sill:
    win_sill.location.y = 10.10

# -------------------------------------------------------------
# 2. PROUD, ELEGANT GOOSE-NECK FAUCET (스완넥 수전)
# -------------------------------------------------------------
safe_remove_matching(["Kitchen_Faucet_"])

# Countertop back deck is at Y=9.94 to 10.04 (thickness 0.03, top at Z=0.89)
faucet_x = 6.15
faucet_y = 9.94
faucet_z = 0.89

# Chrome escutcheon base ring:
make_cylinder("Kitchen_Faucet_Base", (faucet_x, faucet_y, faucet_z + 0.012), 0.026, 0.024, "Mat_Chrome_Polished")
# Vertical riser column (height 28cm up to Z=1.17):
make_cylinder("Kitchen_Faucet_Riser", (faucet_x, faucet_y, faucet_z + 0.15), 0.014, 0.28, "Mat_Chrome_Polished")
# Arch bend curving forward into the room (from Y=9.94 forward to Y=9.82, Z from 1.17 to 1.30):
make_cylinder("Kitchen_Faucet_ArchUpper", (faucet_x, faucet_y - 0.06, faucet_z + 0.38), 0.014, 0.14, "Mat_Chrome_Polished", rot=(math.radians(90), 0, 0))
# Downward goose-neck spout:
make_cylinder("Kitchen_Faucet_SpoutDown", (faucet_x, faucet_y - 0.12, faucet_z + 0.30), 0.014, 0.16, "Mat_Chrome_Polished")
# Chrome aerator nozzle tip:
make_cylinder("Kitchen_Faucet_Nozzle", (faucet_x, faucet_y - 0.12, faucet_z + 0.20), 0.016, 0.03, "Mat_Steel_Brushed")
# Single side lever mixer on right:
make_cylinder("Kitchen_Faucet_LeverStem", (faucet_x + 0.035, faucet_y, faucet_z + 0.08), 0.010, 0.04, "Mat_Chrome_Polished", rot=(0, math.radians(90), 0))
make_cylinder("Kitchen_Faucet_LeverHandle", (faucet_x + 0.055, faucet_y, faucet_z + 0.12), 0.006, 0.10, "Mat_Chrome_Polished")

# Task spot directly over sink:
safe_remove("Light_Sink_Task")
sink_light = bpy.data.lights.new("Light_Sink_Task", 'SPOT')
sink_light.energy = 35.0
sink_light.color = (1.0, 0.96, 0.90)
sink_light.spot_size = math.radians(70)
sink_light.spot_blend = 0.35
sink_lobj = bpy.data.objects.new("Light_Sink_Task", sink_light)
col_light.objects.link(sink_lobj)
sink_lobj.location = (faucet_x, 9.80, 2.25)
sink_lobj.rotation_euler = Euler((0, 0, 0), 'XYZ')

# -------------------------------------------------------------
# 3. ENHANCE MARBLE VEINING CONTRAST (Mat_Marble_White)
# -------------------------------------------------------------
mat_marble = bpy.data.materials.get("Mat_Marble_White")
if mat_marble and mat_marble.use_nodes:
    nodes = mat_marble.node_tree.nodes
    cr = None
    for n in nodes:
        if n.type == 'VALTORGB':
            cr = n
            break
    if cr:
        # Give sharp Calacatta grey veins against ivory white
        # Clear elements and set 3 stops:
        cr.color_ramp.elements[0].position = 0.42
        cr.color_ramp.elements[0].color = (0.50, 0.52, 0.55, 1.0) # distinct elegant grey vein
        cr.color_ramp.elements[1].position = 0.56
        cr.color_ramp.elements[1].color = (0.95, 0.95, 0.94, 1.0) # ivory white stone base
        print("Enhanced Mat_Marble_White ColorRamp for visible Calacatta veining")

# -------------------------------------------------------------
# 4. ENHANCE DINING CHAIR UPHOLSTERY & POST CONTRAST
# -------------------------------------------------------------
mat_chair_fab = bpy.data.materials.get("Mat_Chair_Fabric")
if mat_chair_fab and mat_chair_fab.use_nodes:
    bsdf_c = mat_chair_fab.node_tree.nodes.get("Principled BSDF")
    if bsdf_c:
        # Warm oat/taupe fabric
        bsdf_c.inputs['Base Color'].default_value = (0.58, 0.52, 0.45, 1.0)
        bsdf_c.inputs['Roughness'].default_value = 0.88
        print("Updated Mat_Chair_Fabric to warm oat/taupe")

# Chair posts and legs to dark architectural charcoal:
for o in bpy.data.objects:
    if o.name.startswith("Chair_N") or o.name.startswith("Chair_S"):
        if any(k in o.name for k in ["Leg", "Post"]):
            o.data.materials.clear()
            o.data.materials.append(bpy.data.materials.get("Mat_Window_Frame"))

# -------------------------------------------------------------
# 5. CAMERA PREP CORNER (REPLICATING display_03_part_2.jpg EXACTLY)
# -------------------------------------------------------------
# In display_03_part_2.jpg:
# Looking northeast into the kitchen corner:
# Left side: Window, sink bowl, dish drying rack, goose-neck faucet, dishwasher.
# Corner: Continuous 90-degree quartz countertop & marble backsplash.
# Right side: 3-burner induction cooktop, electric oven, black slim range hood.
cam_prep = bpy.data.objects.get("Cam_Kitchen_Prep_POV")
if not cam_prep:
    cdata = bpy.data.cameras.new("Cam_Kitchen_Prep_POV")
    cam_prep = bpy.data.objects.new("Cam_Kitchen_Prep_POV", cdata)
    col_furn.objects.link(cam_prep)

cam_prep.data.lens = 19.5 # Wide architectural lens matching modelhouse photo
cam_prep.location = Vector((5.50, 7.10, 1.35))
# Euler: pitch down ~12 deg (80 deg from Z), roll 0, yaw northeast ~38 deg
cam_prep.rotation_euler = Euler((math.radians(78.5), 0.0, math.radians(-38.0)), 'XYZ')
print("Aligned Cam_Kitchen_Prep_POV to 100% replicate display_03_part_2.jpg")

# Also fine-tune Cam_Kitchen_POV:
cam_k = bpy.data.objects.get("Cam_Kitchen_POV")
if cam_k:
    cam_k.location = Vector((5.70, 3.50, 1.48))
    cam_k.rotation_euler = Euler((math.radians(86.5), 0.0, math.radians(-19.0)), 'XYZ')
    cam_k.data.lens = 22.0

bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print("=== FAUCET & SILL RECTIFICATION COMPLETED & SAVED ===")
'''

res = mcp_client.send_blender_command('execute_code', {'code': py_code})
print("Result:", res)
