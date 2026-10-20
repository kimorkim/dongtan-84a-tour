import bpy
import bmesh
import math
import os
import sys

# Ensure local script dir is in sys.path
script_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else "C:/Users/tamarand/orca/projects/apt/scripts"
if script_dir not in sys.path:
    sys.path.append(script_dir)

import importlib
import create_materials
importlib.reload(create_materials)
from create_materials import create_pbr_materials

import generate_high_detail_assets
importlib.reload(generate_high_detail_assets)
from generate_high_detail_assets import (
    get_col, clear_col, create_beveled_box, create_cylinder,
    create_chair, create_window_unit, create_interior_door,
    create_luxury_bed, create_luxury_bed_oriented, create_luxury_sofa, create_sink_and_faucet,
    create_bathtub, create_toilet,
    create_wall_tv, create_fridge_cabinet, create_upper_cabinets, create_range_hood,
    create_curtain, create_nightstand
)

def setup_cycles():
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    
    prefs = bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type = 'OPTIX'
    prefs.get_devices()
    for d in prefs.devices:
        if d.type == 'OPTIX':
            d.use = True
        elif d.type == 'CPU':
            d.use = False
            
    scene.cycles.device = 'GPU'
    scene.cycles.preview_samples = 32
    scene.cycles.samples = 128
    scene.cycles.use_denoising = True
    scene.cycles.denoiser = 'OPTIX'
    
    scene.cycles.max_bounces = 12
    scene.cycles.diffuse_bounces = 4
    scene.cycles.glossy_bounces = 4
    scene.cycles.transmission_bounces = 8
    scene.cycles.transparent_max_bounces = 8
    
    scene.view_settings.view_transform = 'Filmic'
    scene.view_settings.look = 'Medium High Contrast'

def run():
    print("Starting Photorealistic Apartment Upgrade with Authentic Prugio Details...")
    setup_cycles()
    create_pbr_materials()
    
    # Material shortcuts
    mat_light_wood = bpy.data.materials.get("Mat_Wood_LightPlank")
    mat_warm_wood  = bpy.data.materials.get("Mat_Wood_WarmPlank")
    mat_tile_grey  = bpy.data.materials.get("Mat_Tile_Grey")
    mat_foyer_tile = bpy.data.materials.get("Mat_Tile_DarkSlate")
    mat_artwall    = bpy.data.materials.get("Mat_ArtWall_Tile")
    mat_wall_int   = bpy.data.materials.get("Mat_Wall_Interior")
    mat_wall_cap   = bpy.data.materials.get("Mat_Wall_Cap")
    mat_counter    = bpy.data.materials.get("Mat_Countertop_Granite")
    mat_cab        = bpy.data.materials.get("Mat_Cabinet_Cashmere")
    mat_fridge     = bpy.data.materials.get("Mat_Bespoke_Glass")
    mat_sofa       = bpy.data.materials.get("Mat_Fabric_Sofa")
    mat_cushion    = bpy.data.materials.get("Mat_Bed_Runner")
    mat_linen      = bpy.data.materials.get("Mat_Bed_Linen")
    mat_runner     = bpy.data.materials.get("Mat_Bed_Runner")
    mat_walnut     = bpy.data.materials.get("Mat_Wood_Walnut")
    mat_chrome     = bpy.data.materials.get("Mat_Chrome_Metal")
    mat_glass      = bpy.data.materials.get("Mat_Glass_Clear")
    mat_frame      = bpy.data.materials.get("Mat_Window_Frame")
    mat_door_blue  = bpy.data.materials.get("Mat_Door_Blue")
    mat_ceramic    = bpy.data.materials.get("Mat_Ceramic_White")
    mat_screen     = bpy.data.materials.get("Mat_Screen_OLED")
    mat_led        = bpy.data.materials.get("Mat_Light_Warm_Strip")
    mat_curtain    = bpy.data.materials.get("Mat_Curtain")
    mat_hood       = bpy.data.materials.get("Mat_Hood_Metal")
    
    # 1. Update Existing Walls & Base Floor in Apt_Corrected_Structure
    struct_col = bpy.data.collections.get("Apt_Corrected_Structure")
    if struct_col:
        for obj in struct_col.objects:
            if obj.type == 'MESH':
                if obj.name.startswith("ExactWall_"):
                    obj.data.materials.clear()
                    obj.data.materials.append(mat_wall_int) # slot 0: sides
                    obj.data.materials.append(mat_wall_cap) # slot 1: top cap
                    for poly in obj.data.polygons:
                        if poly.normal.z > 0.8:
                            poly.material_index = 1
                        else:
                            poly.material_index = 0
                    obj.data.update()
                elif obj.name == "Exact_Floor":
                    obj.data.materials.clear()
                    obj.data.materials.append(mat_light_wood)
                    obj.data.update()
                    
    # 2. Collections Setup
    col_zones = get_col("Apt_Flooring_Zones")
    clear_col(col_zones)
    
    col_openings = get_col("Apt_Windows_Doors")
    clear_col(col_openings)
    
    col_furnish = get_col("Apt_Furnishings")
    clear_col(col_furnish)
    
    col_lights = get_col("Apt_Lighting")
    clear_col(col_lights)
    
    # Completely remove obsolete collections and their objects
    for old_c in ["Apt_Floors", "Apt_OuterWalls", "Apt_InteriorWalls", "Apt_Openings", "Apt_Doors_Windows"]:
        c = bpy.data.collections.get(old_c)
        if c:
            for o in list(c.objects):
                bpy.data.objects.remove(o, do_unlink=True)
            bpy.data.collections.remove(c)

    # 3. Create Flooring Zones matching official Prugio finishes (slightly above base floor z=0.002)
    # Master Bedroom (Warm Oak: X: [0.6, 4.2], Y: [1.8, 5.6])
    create_beveled_box("Floor_MasterBed", 2.4, 3.7, 0.002, 3.6, 3.6, 0.01, bevel=0, mat=mat_warm_wood, col=col_zones)
    # Master Balcony 1 (Grey Tile: X: [0.6, 4.2], Y: [0.4, 1.8])
    create_beveled_box("Floor_MasterBalcony", 2.4, 1.1, 0.002, 3.6, 1.3, 0.01, bevel=0, mat=mat_tile_grey, col=col_zones)
    # Master Bath (Grey Tile: X: [2.7, 4.2], Y: [5.8, 8.0])
    create_beveled_box("Floor_MasterBath", 3.45, 6.9, 0.002, 1.45, 2.1, 0.01, bevel=0, mat=mat_tile_grey, col=col_zones)
    # Dress Room (Warm Oak: X: [0.6, 2.6], Y: [5.8, 9.9])
    create_beveled_box("Floor_DressRoom", 1.6, 7.85, 0.002, 1.9, 3.9, 0.01, bevel=0, mat=mat_warm_wood, col=col_zones)
    
    # One AC-room floor inside the traced wall boundary; Q6 finishes the opening.
    create_beveled_box("Floor_ACOutdoor", 9.4215, 8.7375, 0.002, 1.519, 1.125, 0.012, bevel=0, mat=mat_tile_grey, col=col_zones)
    
    # Alpha Room (west of the entrance pantry, bounded by traced walls)
    create_beveled_box("Floor_AlphaRoom", 9.187, 6.834, 0.002, 2.4, 2.194, 0.01, bevel=0, mat=mat_light_wood, col=col_zones)
    # Bedroom 2 (Warm Oak: X: [9.0, 12.0], Y: [0.5, 4.4])
    create_beveled_box("Floor_Bedroom2", 10.5, 2.45, 0.002, 2.9, 3.8, 0.01, bevel=0, mat=mat_light_wood, col=col_zones)
    # Bedroom 3 (Warm Oak: X: [12.2, 15.0], Y: [0.5, 4.4])
    create_beveled_box("Floor_Bedroom3", 13.6, 2.45, 0.002, 2.7, 3.8, 0.01, bevel=0, mat=mat_light_wood, col=col_zones)
    
    # Common Bathroom 1 (Grey Tile: X: [13.4, 15.0], Y: [5.7, 7.6])
    create_beveled_box("Floor_CommonBath", 14.2, 6.65, 0.002, 1.5, 1.8, 0.01, bevel=0, mat=mat_tile_grey, col=col_zones)
    # Entrance Foyer (Dark Slate 600x600 Porcelain: X: [11.8, 13.3], Y: [7.6, 10.0])
    create_beveled_box("Floor_Foyer", 12.55, 8.8, 0.002, 1.45, 2.3, 0.01, bevel=0, mat=mat_foyer_tile, col=col_zones)

    # 4. Realistic 3D Window Units (with dark charcoal frames and glass)
    create_window_unit("Win_Living", 6.6, 0.35, 0.0, 4.0, 0.16, 2.20, panes=3, mat_frame=mat_frame, mat_glass=mat_glass, col=col_openings)
    create_window_unit("Win_MasterBalcony", 2.4, 0.35, 0.0, 3.5, 0.16, 2.20, panes=2, mat_frame=mat_frame, mat_glass=mat_glass, col=col_openings)
    create_window_unit("Win_Bed2", 10.5, 0.35, 0.80, 2.2, 0.16, 1.40, panes=2, mat_frame=mat_frame, mat_glass=mat_glass, col=col_openings)
    create_window_unit("Win_Bed3", 13.6, 0.35, 0.80, 2.0, 0.16, 1.40, panes=2, mat_frame=mat_frame, mat_glass=mat_glass, col=col_openings)
    create_window_unit("Win_Kitchen", 5.8, 10.05, 1.10, 1.4, 0.16, 0.70, panes=2, mat_frame=mat_frame, mat_glass=mat_glass, col=col_openings)
    create_window_unit("Win_Dress", 1.6, 10.05, 1.10, 1.2, 0.16, 0.70, panes=2, mat_frame=mat_frame, mat_glass=mat_glass, col=col_openings)
    create_window_unit("Door_MasterBalcony_Glass", 2.4, 1.80, 0.0, 2.8, 0.10, 2.15, panes=2, mat_frame=mat_frame, mat_glass=mat_glass, col=col_openings)

    # Window Curtains
    create_curtain("Curtain_Living", 6.6, 0.45, 0.0, 4.0, 2.30, mat_curtain=mat_curtain, col=col_furnish)
    create_curtain("Curtain_Master", 2.4, 1.90, 0.0, 2.8, 2.20, mat_curtain=mat_curtain, col=col_furnish)

    # 5. Realistic Open Interior Doors (matching 84A.jpg)
    create_interior_door("Door_MasterBed", 4.15, 5.2, 0.0, 0.88, 2.10, swing_deg=-135, mat_door=mat_walnut, mat_handle=mat_chrome, col=col_openings)
    create_interior_door("Door_MasterBath", 2.8, 5.9, 0.0, 0.80, 2.10, swing_deg=55, mat_door=mat_cab, mat_handle=mat_chrome, col=col_openings)
    create_interior_door("Door_Bed2", 9.2, 4.35, 0.0, 0.88, 2.10, swing_deg=-60, mat_door=mat_walnut, mat_handle=mat_chrome, col=col_openings)
    create_interior_door("Door_Bed3", 12.4, 4.35, 0.0, 0.88, 2.10, swing_deg=-60, mat_door=mat_walnut, mat_handle=mat_chrome, col=col_openings)
    create_interior_door("Door_Alpha", 10.4, 5.75, 0.0, 0.88, 2.10, swing_deg=65, mat_door=mat_walnut, mat_handle=mat_chrome, col=col_openings)
    create_interior_door("Door_CommonBath", 13.45, 5.75, 0.0, 0.80, 2.10, swing_deg=60, mat_door=mat_cab, mat_handle=mat_chrome, col=col_openings)
    create_interior_door("Door_FrontEntry", 12.2, 9.9, 0.0, 0.95, 2.15, swing_deg=-45, mat_door=mat_door_blue, mat_handle=mat_chrome, col=col_openings)

    # 6. Master Bedroom (침실1) Furnishings
    create_luxury_bed_oriented("Bed_Master", 1.85, 3.10, 0.0, width=2.0, length=2.15, orientation='W_TO_E', is_king=True, mat_wood=mat_walnut, mat_sheet=mat_linen, mat_pillow=mat_linen, mat_runner=mat_runner, col=col_furnish)
    create_nightstand("Nightstand_Master", 1.85, 4.35, 0.0, mat_wood=mat_walnut, mat_lamp=mat_chrome, col=col_furnish)

    # 7. Living Room (거실) Furnishings (matching 84A.jpg & Prugio e-modelhouse)
    # Living Room Art Wall Cladding on West wall (X=4.41, Y: [1.8, 4.6])
    create_beveled_box("Living_ArtWall_Tile", 4.41, 3.2, 0.0, 0.015, 2.70, 2.30, bevel=0.002, seg=1, mat=mat_artwall, col=col_furnish)
    # Wall-mounted OLED TV on the Art Wall
    create_wall_tv("Living_TV_OLED", 4.43, 3.2, 1.15, width=1.65, height=0.96, mat_frame=mat_frame, mat_screen=mat_screen, col=col_furnish)
    # Low-profile Sleek Floating Media Unit below TV
    create_beveled_box("MediaUnit_Living", 4.58, 3.2, 0.12, 0.36, 2.20, 0.32, bevel=0.01, seg=2, mat=mat_cab, col=col_furnish)
    # 3-4 Seater Fabric Sofa on East wall against Bedroom 2
    create_luxury_sofa("Sofa_Living", 8.55, 3.0, 0.0, 2.45, 0.92, mat_fabric=mat_sofa, mat_cushion=mat_cushion, col=col_furnish)
    # Center of living room remains open, matching 84A.jpg

    # 8. 'ㄷ' Shaped Kitchen & Modern Dining
    # West kitchen wall: Built-in 4-door Bespoke Refrigerator Cabinet & Tall Pantry (matching display84a_03.jpg!)
    create_fridge_cabinet("Kitchen_Fridge_Wall", 4.65, 8.4, 0.0, width=2.20, depth=0.68, height=2.25, mat_cab=mat_cab, mat_fridge=mat_fridge, col=col_furnish)

    # North counter with sink (Y=9.75, X: [5.0, 7.8])
    create_beveled_box("Kitchen_North_Base", 6.4, 9.75, 0.0, 2.8, 0.65, 0.86, bevel=0.01, mat=mat_cab, col=col_furnish)
    create_beveled_box("Kitchen_North_Top", 6.4, 9.75, 0.86, 2.8, 0.68, 0.04, bevel=0.008, mat=mat_counter, col=col_furnish)
    create_sink_and_faucet("Kitchen_Sink", 5.8, 9.75, 0.90, mat_sink=mat_chrome, mat_chrome=mat_chrome, col=col_furnish)

    # North Upper Cabinets above sink with warm under-cabinet LED light strip
    create_upper_cabinets("Kitchen_Upper_North", 6.4, 9.85, 1.55, 2.8, 0.35, 0.70, mat_cab=mat_cab, mat_led=mat_led, col=col_furnish)

    # East counter along the wall to Alpha room (X=7.5, Y: [6.4, 9.75])
    create_beveled_box("Kitchen_East_Base", 7.5, 8.0, 0.0, 0.65, 2.85, 0.86, bevel=0.01, mat=mat_cab, col=col_furnish)
    create_beveled_box("Kitchen_East_Top", 7.5, 8.0, 0.86, 0.68, 2.85, 0.04, bevel=0.008, mat=mat_counter, col=col_furnish)
    # 3-Burner Induction Cooktop on East counter
    create_beveled_box("Kitchen_Induction", 7.5, 8.0, 0.902, 0.52, 0.60, 0.008, bevel=0.002, mat=mat_screen, col=col_furnish)
    # Modern Range Hood above induction cooktop
    create_range_hood("Kitchen_RangeHood", 7.45, 8.0, 1.60, sx=0.55, sy=0.85, sz=0.55, mat_hood=mat_hood, col=col_furnish)

    # Peninsula counter extending West from East counter (Y=6.4, X: [5.2, 7.8])
    create_beveled_box("Kitchen_Peninsula_Base", 6.5, 6.4, 0.0, 2.0, 0.65, 0.86, bevel=0.01, mat=mat_cab, col=col_furnish)
    create_beveled_box("Kitchen_Peninsula_Top", 6.5, 6.4, 0.86, 2.0, 0.68, 0.04, bevel=0.008, mat=mat_counter, col=col_furnish)

    # Dining Table (Walnut) extending SOUTH from Peninsula (North-South vertical orientation)
    create_beveled_box("Dining_Table_Top", 5.9, 5.15, 0.72, 0.85, 1.45, 0.04, bevel=0.012, seg=3, mat=mat_walnut, col=col_furnish)
    for dx, dy in [(-0.34, -0.62), (0.34, -0.62), (-0.34, 0.62), (0.34, 0.62)]:
        create_cylinder("Dining_Leg", 5.9 + dx, 5.15 + dy, 0.0, 0.022, 0.72, mat=mat_walnut, col=col_furnish)

    # 4 Dining Chairs: 2 on West side (facing East), 2 on East side (facing West)
    create_chair("Chair_W1", 5.25, 5.60, 0.0, rot_z_deg=90,  mat_wood=mat_walnut, mat_cushion=mat_sofa, col=col_furnish)
    create_chair("Chair_W2", 5.25, 4.70, 0.0, rot_z_deg=90,  mat_wood=mat_walnut, mat_cushion=mat_sofa, col=col_furnish)
    create_chair("Chair_E1", 6.55, 5.60, 0.0, rot_z_deg=-90, mat_wood=mat_walnut, mat_cushion=mat_sofa, col=col_furnish)
    create_chair("Chair_E2", 6.55, 4.70, 0.0, rot_z_deg=-90, mat_wood=mat_walnut, mat_cushion=mat_sofa, col=col_furnish)

    # 9. Master Bathroom (부부욕실 - Left): BATHTUB + Sink + Toilet (matching 84A.jpg & display84a_07.jpg!)
    create_bathtub("Master_Bathtub", 3.4, 7.6, 0.0, length=1.45, width=0.72, height=0.55, mat_ceramic=mat_ceramic, mat_chrome=mat_chrome, col=col_furnish)
    create_beveled_box("Master_Vanity_Top", 3.8, 6.7, 0.85, 0.55, 0.65, 0.03, bevel=0.006, mat=mat_ceramic, col=col_furnish)
    create_toilet("Master_Toilet", 3.8, 6.0, 0.0, rot_z_deg=180, mat_ceramic=mat_ceramic, col=col_furnish)

    # 10. Common Bathroom (욕실1 - Right): SHOWER BOOTH + Toilet + Vanity (matching 84A.jpg & display84a_07.jpg!)
    create_beveled_box("Bath1_Shower_Screen", 14.2, 7.2, 0.0, 0.015, 0.85, 2.05, bevel=0.002, mat=mat_glass, col=col_furnish)
    create_cylinder("Bath1_Shower_Head", 14.6, 7.2, 2.10, 0.10, 0.02, mat=mat_chrome, col=col_furnish)
    create_toilet("Bath1_Toilet", 13.8, 7.0, 0.0, rot_z_deg=90, mat_ceramic=mat_ceramic, col=col_furnish)
    create_beveled_box("Bath1_Vanity_Cab", 14.60, 6.05, 0.30, 0.60, 0.52, 0.55, bevel=0.01, mat=mat_cab, col=col_furnish)
    create_beveled_box("Bath1_Vanity_Top", 14.60, 6.05, 0.85, 0.63, 0.55, 0.03, bevel=0.006, mat=mat_counter, col=col_furnish)
    create_beveled_box("Bath1_Mirror", 14.60, 5.80, 1.05, 0.60, 0.03, 0.80, bevel=0.005, mat=mat_glass, col=col_furnish)

    # 11. Bedroom 2 (침실2): Bed running North-to-South along East wall
    create_luxury_bed_oriented("Bed2", 11.2, 3.25, 0.0, width=1.15, length=2.05, orientation='N_TO_S', mat_wood=mat_walnut, mat_sheet=mat_linen, mat_pillow=mat_linen, mat_runner=mat_runner, col=col_furnish)

    # 12. Bedroom 3 (침실3): Bed running East-to-West along South wall
    create_luxury_bed_oriented("Bed3", 13.8, 1.35, 0.0, width=1.10, length=2.05, orientation='E_TO_W', mat_wood=mat_walnut, mat_sheet=mat_linen, mat_pillow=mat_linen, mat_runner=mat_runner, col=col_furnish)

    # 13. Foyer: Full-height Shoe Cabinet along East wall (X=12.95, Y: 8.0 to 9.8)
    create_beveled_box("Foyer_Shoe_Cab", 12.95, 8.8, 0.15, 0.38, 1.90, 2.05, bevel=0.01, mat=mat_cab, col=col_furnish)

    # 14. Cinematic Lighting & Presentation Background
    import mathutils
    sun_data = bpy.data.lights.get("Sun_Natural") or bpy.data.lights.new("Sun_Natural", 'SUN')
    sun_data.energy = 4.2
    sun_data.color = (1.0, 0.96, 0.90) # Warm golden sunlight
    sun_data.angle = math.radians(2.0)
    sun_obj = bpy.data.objects.get("Sun_Natural") or bpy.data.objects.new("Sun_Natural", sun_data)
    if sun_obj.name not in col_lights.objects:
        col_lights.objects.link(sun_obj)
    sun_obj.location = (7.6, 5.0, 15.0)

    # Sun shining from South-Southwest (mimicking 84A.jpg)
    dir_vec = mathutils.Vector((0.45, 0.75, -0.85)).normalized()
    sun_obj.rotation_euler = dir_vec.to_track_quat('-Z', 'Y').to_euler()

    # World Sky / Ambient Fill
    world = bpy.context.scene.world or bpy.data.worlds.new("World_Interior")
    bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs['Color'].default_value = (0.94, 0.96, 1.0, 1.0)
        bg.inputs['Strength'].default_value = 0.55

    # Warm Recessed Ceiling Downlights
    for name, loc, energy in [
        ("Downlight_Living", (6.4, 3.2, 2.25), 45.0),
        ("Downlight_Dining", (6.6, 5.0, 2.25), 35.0),
        ("Downlight_Kitchen", (6.0, 8.0, 2.25), 40.0),
        ("Downlight_Hallway", (11.0, 5.5, 2.25), 25.0)
    ]:
        ld = bpy.data.lights.get(name) or bpy.data.lights.new(name, 'POINT')
        ld.energy = energy
        ld.color = (1.0, 0.90, 0.78)
        ld.shadow_soft_size = 0.15
        lo = bpy.data.objects.get(name) or bpy.data.objects.new(name, ld)
        if lo.name not in col_lights.objects:
            col_lights.objects.link(lo)
        lo.location = loc

    # Pure White Seamless Ground Plane (for 84A.jpg style presentation)
    plane_mesh = bpy.data.meshes.get("Ground_Presentation_Mesh") or bpy.data.meshes.new("Ground_Presentation_Mesh")
    plane_obj = bpy.data.objects.get("Ground_Presentation") or bpy.data.objects.new("Ground_Presentation", plane_mesh)
    if plane_obj.name not in col_lights.objects:
        col_lights.objects.link(plane_obj)
    verts = [(-30, -30, -0.16), (45, -30, -0.16), (45, 40, -0.16), (-30, 40, -0.16)]
    faces = [(0, 1, 2, 3)]
    plane_mesh.clear_geometry()
    plane_mesh.from_pydata(verts, [], faces)
    plane_mesh.update()
    
    mat_white_bg = bpy.data.materials.get("Mat_White_Presentation") or bpy.data.materials.new("Mat_White_Presentation")
    mat_white_bg.use_nodes = True
    bg_bsdf = mat_white_bg.node_tree.nodes.get("Principled BSDF")
    if bg_bsdf:
        bg_bsdf.inputs['Base Color'].default_value = (1.0, 1.0, 1.0, 1.0)
        bg_bsdf.inputs['Roughness'].default_value = 0.9
    plane_obj.data.materials.clear()
    plane_obj.data.materials.append(mat_white_bg)

    # 15. Ceiling Slab for enclosed interior views (hidden during topdown render)
    ceil_mesh = bpy.data.meshes.get("Ceiling_Mesh") or bpy.data.meshes.new("Ceiling_Mesh")
    ceil_obj = bpy.data.objects.get("Ceiling_Slab") or bpy.data.objects.new("Ceiling_Slab", ceil_mesh)
    if ceil_obj.name not in col_lights.objects:
        col_lights.objects.link(ceil_obj)
    c_verts = [(-1.0, -1.0, 2.30), (16.0, -1.0, 2.30), (16.0, 11.0, 2.30), (-1.0, 11.0, 2.30),
               (-1.0, -1.0, 2.35), (16.0, -1.0, 2.35), (16.0, 11.0, 2.35), (-1.0, 11.0, 2.35)]
    c_faces = [(0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
    ceil_mesh.clear_geometry()
    ceil_mesh.from_pydata(c_verts, [], c_faces)
    ceil_mesh.update()
    ceil_obj.data.materials.clear()
    ceil_obj.data.materials.append(mat_wall_int)

    # 16. Camera Setups & Renders
    def look_at(cam_obj, target_pos):
        loc = cam_obj.location
        tgt = mathutils.Vector(target_pos)
        direction = tgt - loc
        cam_obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()

    # Camera 1: Isometric Top-Down 3D Plan (like 84A.jpg)
    cam_top_data = bpy.data.cameras.get("Cam_Photoreal_Topdown") or bpy.data.cameras.new("Cam_Photoreal_Topdown")
    cam_top_data.type = 'ORTHO'
    cam_top_data.ortho_scale = 19.5
    cam_top_obj = bpy.data.objects.get("Cam_Photoreal_Topdown") or bpy.data.objects.new("Cam_Photoreal_Topdown", cam_top_data)
    if cam_top_obj.name not in col_lights.objects:
        col_lights.objects.link(cam_top_obj)
    cam_top_obj.location = (7.65, 4.6, 22.0)
    cam_top_obj.rotation_euler = (math.radians(10), 0.0, 0.0)

    # Camera 2: Living Room Eye-Level POV (facing Art Wall and TV)
    cam_liv_data = bpy.data.cameras.get("Cam_Living_POV") or bpy.data.cameras.new("Cam_Living_POV")
    cam_liv_data.type = 'PERSP'
    cam_liv_data.lens = 22.0
    cam_liv_obj = bpy.data.objects.get("Cam_Living_POV") or bpy.data.objects.new("Cam_Living_POV", cam_liv_data)
    if cam_liv_obj.name not in col_lights.objects:
        col_lights.objects.link(cam_liv_obj)
    cam_liv_obj.location = (7.4, 2.0, 1.35)
    look_at(cam_liv_obj, (5.0, 3.3, 1.15))

    # Camera 3: Kitchen & Dining POV (facing Dining Table, Peninsula, and Bespoke Fridge)
    cam_kit_data = bpy.data.cameras.get("Cam_Kitchen_POV") or bpy.data.cameras.new("Cam_Kitchen_POV")
    cam_kit_data.type = 'PERSP'
    cam_kit_data.lens = 22.0
    cam_kit_obj = bpy.data.objects.get("Cam_Kitchen_POV") or bpy.data.objects.new("Cam_Kitchen_POV", cam_kit_data)
    if cam_kit_obj.name not in col_lights.objects:
        col_lights.objects.link(cam_kit_obj)
    cam_kit_obj.location = (5.80, 3.20, 1.35)
    look_at(cam_kit_obj, (7.10, 6.50, 1.05))

    # Camera 4: Master Bedroom POV (looking directly at King bed and Balcony)
    cam_bed_data = bpy.data.cameras.get("Cam_MasterBed_POV") or bpy.data.cameras.new("Cam_MasterBed_POV")
    cam_bed_data.type = 'PERSP'
    cam_bed_data.lens = 22.0
    cam_bed_obj = bpy.data.objects.get("Cam_MasterBed_POV") or bpy.data.objects.new("Cam_MasterBed_POV", cam_bed_data)
    if cam_bed_obj.name not in col_lights.objects:
        col_lights.objects.link(cam_bed_obj)
    cam_bed_obj.location = (3.4, 2.4, 1.30)
    look_at(cam_bed_obj, (1.85, 3.40, 0.85))

    # Camera 5: Entrance Hallway looking into Living & Dining
    cam_foy_data = bpy.data.cameras.get("Cam_Foyer_POV") or bpy.data.cameras.new("Cam_Foyer_POV")
    cam_foy_data.type = 'PERSP'
    cam_foy_data.lens = 22.0
    cam_foy_obj = bpy.data.objects.get("Cam_Foyer_POV") or bpy.data.objects.new("Cam_Foyer_POV", cam_foy_data)
    if cam_foy_obj.name not in col_lights.objects:
        col_lights.objects.link(cam_foy_obj)
    cam_foy_obj.location = (12.2, 7.6, 1.45)
    look_at(cam_foy_obj, (7.5, 3.8, 1.15))


    # Render settings
    bpy.context.scene.render.resolution_x = 1280
    bpy.context.scene.render.resolution_y = 960

    renders = [
        (cam_top_obj, "render_1_isometric_topdown.png", True),   # Hide ceiling for topdown view
        (cam_liv_obj, "render_2_living_room_pov.png", False),     # Show ceiling for enclosed POV
        (cam_kit_obj, "render_3_kitchen_dining_pov.png", False),
        (cam_bed_obj, "render_4_master_bedroom_pov.png", False),
        (cam_foy_obj, "render_5_foyer_corridor_pov.png", False)
    ]

    for cam, filename, hide_ceiling in renders:
        ceil_obj.hide_render = hide_ceiling
        bpy.context.scene.camera = cam
        out_path = os.path.abspath(os.path.join("renders", "presentation", filename))
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        bpy.context.scene.render.filepath = out_path
        print(f"Rendering {filename} with Cycles GPU OptiX (hide_ceiling={hide_ceiling})...")
        bpy.ops.render.render(write_still=True)
        print(f"Saved: {out_path}")

    # Save milestone blend file
    save_file = os.path.abspath("apt_84a_photoreal_tour.blend")
    bpy.ops.wm.save_as_mainfile(filepath=save_file)
    print(f"Photoreal Milestone saved to: {save_file}")
    print("SUCCESS: All photorealistic assets, shaders, lighting, and renders complete!")

run()
