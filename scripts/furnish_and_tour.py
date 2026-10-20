import bpy
import math
import os

def create_mat(name, color, roughness=0.4, metallic=0.0, transmission=0.0, alpha=1.0):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = color
        bsdf.inputs['Roughness'].default_value = roughness
        bsdf.inputs['Metallic'].default_value = metallic
        if 'Transmission Weight' in bsdf.inputs:
            bsdf.inputs['Transmission Weight'].default_value = transmission
        elif 'Transmission' in bsdf.inputs:
            bsdf.inputs['Transmission'].default_value = transmission
    if alpha < 1.0:
        mat.blend_method = 'BLEND'
    return mat

def create_box(name, x, y, z, sx, sy, sz, mat=None, col=None):
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    if col:
        col.objects.link(obj)
    else:
        bpy.context.scene.collection.objects.link(obj)
        
    x1, x2 = x - sx/2, x + sx/2
    y1, y2 = y - sy/2, y + sy/2
    z1, z2 = z, z + sz
    
    verts = [
        (x1, y1, z1), (x2, y1, z1), (x2, y2, z1), (x1, y2, z1),
        (x1, y1, z2), (x2, y1, z2), (x2, y2, z2), (x1, y2, z2)
    ]
    faces = [
        (0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1),
        (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)
    ]
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    
    if mat:
        obj.data.materials.append(mat)
    return obj

def setup_interior():
    # 1. Collections setup
    col_furnish = bpy.data.collections.get("Apt_Furnishings")
    if not col_furnish:
        col_furnish = bpy.data.collections.new("Apt_Furnishings")
        bpy.context.scene.collection.children.link(col_furnish)
    else:
        for o in list(col_furnish.objects):
            bpy.data.objects.remove(o, do_unlink=True)

    col_doors = bpy.data.collections.get("Apt_Doors_Windows")
    if not col_doors:
        col_doors = bpy.data.collections.new("Apt_Doors_Windows")
        bpy.context.scene.collection.children.link(col_doors)
    else:
        for o in list(col_doors.objects):
            bpy.data.objects.remove(o, do_unlink=True)

    # 2. Materials definition
    mat_wood_floor = create_mat("Mat_WoodFloor", (0.76, 0.60, 0.45, 1.0), roughness=0.35)
    mat_tile_floor = create_mat("Mat_TileFloor", (0.85, 0.86, 0.88, 1.0), roughness=0.20)
    mat_dark_tile  = create_mat("Mat_DarkTile",  (0.30, 0.32, 0.35, 1.0), roughness=0.30)
    mat_wall       = create_mat("Mat_WallPaint",  (0.93, 0.93, 0.94, 1.0), roughness=0.60)
    mat_sofa       = create_mat("Mat_FabricSofa",(0.25, 0.26, 0.28, 1.0), roughness=0.85)
    mat_bed_wood   = create_mat("Mat_BedWood",   (0.55, 0.38, 0.25, 1.0), roughness=0.40)
    mat_bed_sheet  = create_mat("Mat_BedSheet",  (0.92, 0.90, 0.85, 1.0), roughness=0.70)
    mat_pillow     = create_mat("Mat_Pillow",    (0.80, 0.78, 0.72, 1.0), roughness=0.60)
    mat_kitchen_c  = create_mat("Mat_KitchenTop",(0.88, 0.88, 0.90, 1.0), roughness=0.15)
    mat_kitchen_b  = create_mat("Mat_KitchenCab",(0.95, 0.95, 0.95, 1.0), roughness=0.30)
    mat_dining_t   = create_mat("Mat_DiningWood",(0.50, 0.30, 0.15, 1.0), roughness=0.30)
    mat_ceramic    = create_mat("Mat_Ceramic",   (0.96, 0.96, 0.96, 1.0), roughness=0.10)
    mat_glass      = create_mat("Mat_Glass",     (0.85, 0.92, 0.98, 0.3), roughness=0.05, transmission=0.9, alpha=0.3)
    mat_door_wood  = create_mat("Mat_DoorWood",  (0.82, 0.75, 0.65, 1.0), roughness=0.40)
    mat_tv         = create_mat("Mat_TVScreen",  (0.05, 0.05, 0.05, 1.0), roughness=0.10)

    # Apply wall material to existing corrected structure
    struct_col = bpy.data.collections.get("Apt_Corrected_Structure")
    if struct_col:
        for o in struct_col.objects:
            if o.type == 'MESH':
                o.data.materials.clear()
                if "Floor" in o.name:
                    o.data.materials.append(mat_wood_floor)
                else:
                    o.data.materials.append(mat_wall)

    # 3. Add distinctive Floor Zones (Tiles for Balcony, Bathrooms, Entrance)
    # Master Balcony (X: [0.5, 2.5], Y: [0.5, 1.8])
    create_box("Floor_MasterBalcony_Tile", 1.5, 1.15, 0.01, 2.0, 1.3, 0.02, mat_tile_floor, col_furnish)
    # Utility Balcony 2 (X: [6.8, 8.4], Y: [8.5, 9.8])
    create_box("Floor_KitchenBalcony_Tile", 7.6, 9.15, 0.01, 1.6, 1.3, 0.02, mat_tile_floor, col_furnish)
    # Master Bathroom 2 (X: [2.5, 4.0], Y: [5.5, 7.2])
    create_box("Floor_MasterBath_Tile", 3.25, 6.35, 0.01, 1.5, 1.7, 0.02, mat_tile_floor, col_furnish)
    # Common Bathroom 1 (X: [13.2, 14.8], Y: [6.0, 7.8])
    create_box("Floor_CommonBath_Tile", 14.0, 6.90, 0.01, 1.6, 1.8, 0.02, mat_tile_floor, col_furnish)
    # Entrance Foyer Tile (X: [11.5, 13.0], Y: [7.5, 9.5])
    create_box("Floor_Foyer_DarkTile", 12.25, 8.50, 0.01, 1.5, 2.0, 0.02, mat_dark_tile, col_furnish)

    # 4. Master Bedroom (침실1) Furnishings (X: [0.5, 4.0], Y: [1.8, 5.0])
    # King Bed (Head against West wall X=1.2, Bed spans X: 1.2 to 3.2, Y: 2.5 to 4.5)
    create_box("Bed_Master_Frame", 2.2, 3.5, 0.0, 2.1, 1.9, 0.35, mat_bed_wood, col_furnish)
    create_box("Bed_Master_Headboard", 1.15, 3.5, 0.0, 0.15, 2.0, 1.1, mat_bed_wood, col_furnish)
    create_box("Bed_Master_Mattress", 2.25, 3.5, 0.35, 1.95, 1.8, 0.30, mat_bed_sheet, col_furnish)
    create_box("Bed_Master_Pillow1", 1.45, 3.1, 0.65, 0.45, 0.65, 0.15, mat_pillow, col_furnish)
    create_box("Bed_Master_Pillow2", 1.45, 3.9, 0.65, 0.45, 0.65, 0.15, mat_pillow, col_furnish)
    create_box("Bed_Master_Nightstand1", 1.3, 2.2, 0.0, 0.45, 0.50, 0.50, mat_bed_wood, col_furnish)
    create_box("Bed_Master_Nightstand2", 1.3, 4.8, 0.0, 0.45, 0.50, 0.50, mat_bed_wood, col_furnish)
    # TV Console on East partition (X=3.8)
    create_box("Console_Master_TV", 3.8, 3.5, 0.0, 0.35, 1.80, 0.50, mat_bed_wood, col_furnish)
    create_box("TV_Master", 3.8, 3.5, 0.50, 0.08, 1.30, 0.75, mat_tv, col_furnish)

    # 5. Master Bathroom & Dressroom
    # Bathtub / Shower in Master Bath
    create_box("Shower_Booth_Glass", 3.8, 6.0, 0.0, 0.05, 0.90, 2.00, mat_glass, col_furnish)
    create_box("Master_Vanity_Table", 2.8, 5.8, 0.0, 0.55, 0.90, 0.85, mat_kitchen_c, col_furnish)
    create_box("Master_Toilet", 2.8, 7.0, 0.0, 0.65, 0.45, 0.75, mat_ceramic, col_furnish)
    # Dressroom Wardrobe Racks (X: [0.5, 2.5], Y: [7.5, 9.8])
    create_box("Wardrobe_Dress_West", 0.7, 8.6, 0.0, 0.55, 2.2, 2.10, mat_door_wood, col_furnish)
    create_box("Wardrobe_Dress_North", 1.6, 9.7, 0.0, 1.3, 0.55, 2.10, mat_door_wood, col_furnish)

    # 6. Living Room (거실) Furnishings (X: [4.2, 8.5], Y: [1.0, 5.0])
    # 3-4 Seater Fabric Sofa against Bedroom 2 wall (X=8.2, facing West)
    create_box("Sofa_Living_Base", 8.0, 3.2, 0.0, 0.95, 2.60, 0.45, mat_sofa, col_furnish)
    create_box("Sofa_Living_Back", 8.4, 3.2, 0.45, 0.25, 2.60, 0.50, mat_sofa, col_furnish)
    create_box("Sofa_Living_ArmL", 8.0, 1.95, 0.0, 0.95, 0.25, 0.65, mat_sofa, col_furnish)
    create_box("Sofa_Living_ArmR", 8.0, 4.45, 0.0, 0.95, 0.25, 0.65, mat_sofa, col_furnish)
    # Living Room Coffee Table
    create_box("Table_Living_Coffee", 6.8, 3.2, 0.0, 0.70, 1.20, 0.35, mat_dining_t, col_furnish)
    # TV Media Console on Master Bedroom wall (X=4.4, facing East)
    create_box("Console_Living_TV", 4.4, 3.2, 0.0, 0.45, 2.40, 0.45, mat_bed_wood, col_furnish)
    create_box("TV_Living_Screen", 4.4, 3.2, 0.50, 0.08, 1.80, 1.05, mat_tv, col_furnish)

    # 7. Kitchen & Dining (주방 / 식당) Furnishings (X: [4.5, 7.5], Y: [5.5, 9.5])
    # 'ㄷ' Shaped Kitchen Counter
    # Peninsula / Island Counter (facing Living room, Y=6.2, X: [5.5, 7.4])
    create_box("Kitchen_Peninsula", 6.45, 6.2, 0.0, 1.90, 0.70, 0.88, mat_kitchen_c, col_furnish)
    # Back Counter along North Wall (Y=9.6, X: [4.8, 6.8])
    create_box("Kitchen_Back_Counter", 5.8, 9.6, 0.0, 2.00, 0.65, 0.88, mat_kitchen_c, col_furnish)
    # Sink in back counter
    create_box("Kitchen_Sink", 5.8, 9.6, 0.89, 0.75, 0.45, 0.02, mat_ceramic, col_furnish)
    # Side Connecting Counter (X=4.8, Y: [6.2, 9.6])
    create_box("Kitchen_Side_Counter", 4.8, 7.9, 0.0, 0.65, 2.80, 0.88, mat_kitchen_c, col_furnish)
    # Dining Table (Wood) with 4 chairs (X=6.45, Y=5.0)
    create_box("Dining_Table_Top", 6.45, 5.0, 0.73, 1.40, 0.85, 0.05, mat_dining_t, col_furnish)
    create_box("Dining_Table_Legs", 6.45, 5.0, 0.0, 1.20, 0.65, 0.73, mat_dining_t, col_furnish)
    # 4 Chairs
    chair_offsets = [(-0.4, 0.55), (0.4, 0.55), (-0.4, -0.55), (0.4, -0.55)]
    for i, (dx, dy) in enumerate(chair_offsets):
        create_box(f"Dining_Chair_{i+1}", 6.45 + dx, 5.0 + dy, 0.0, 0.42, 0.42, 0.45, mat_dining_t, col_furnish)

    # 8. Alpha Room (알파룸) Furnishings (X: [8.8, 11.2], Y: [6.0, 8.8])
    # Study Desk against East wall (X=10.9)
    create_box("Alpha_Desk", 10.5, 7.5, 0.0, 0.70, 1.40, 0.75, mat_dining_t, col_furnish)
    create_box("Alpha_Desk_Chair", 9.9, 7.5, 0.0, 0.45, 0.45, 0.50, mat_sofa, col_furnish)
    create_box("Alpha_Bookshelf", 9.2, 8.6, 0.0, 0.35, 1.20, 1.80, mat_bed_wood, col_furnish)

    # 9. Bedroom 2 (침실2) Furnishings (X: [8.8, 12.0], Y: [1.0, 4.8])
    # Single Bed against East wall (X=11.2, Y: 2.0 to 4.0)
    create_box("Bed2_Frame", 11.0, 3.2, 0.0, 1.20, 2.05, 0.35, mat_bed_wood, col_furnish)
    create_box("Bed2_Mattress", 11.0, 3.2, 0.35, 1.10, 1.95, 0.25, mat_bed_sheet, col_furnish)
    create_box("Bed2_Pillow", 11.0, 2.4, 0.60, 0.65, 0.45, 0.15, mat_pillow, col_furnish)
    # Desk against West partition (X=9.2)
    create_box("Bed2_Desk", 9.2, 3.2, 0.0, 0.60, 1.20, 0.75, mat_dining_t, col_furnish)

    # 10. Bedroom 3 (침실3) Furnishings (X: [12.6, 15.0], Y: [1.0, 4.8])
    # Single Bed against South wall (Y=1.8, X: 12.8 to 14.8)
    create_box("Bed3_Frame", 13.8, 1.8, 0.0, 1.95, 1.15, 0.35, mat_bed_wood, col_furnish)
    create_box("Bed3_Mattress", 13.8, 1.8, 0.35, 1.85, 1.05, 0.25, mat_bed_sheet, col_furnish)
    create_box("Bed3_Pillow", 13.0, 1.8, 0.60, 0.45, 0.65, 0.15, mat_pillow, col_furnish)
    # Desk against North partition (Y=4.2)
    create_box("Bed3_Desk", 13.8, 4.2, 0.0, 1.20, 0.60, 0.75, mat_dining_t, col_furnish)

    # 11. Common Bathroom 1 (욕실1) with Bathtub (X: [13.2, 15.0], Y: [6.0, 8.0])
    # Bathtub along North wall
    create_box("Bath1_Bathtub_Outer", 14.1, 7.4, 0.0, 1.50, 0.75, 0.55, mat_ceramic, col_furnish)
    create_box("Bath1_Washbasin", 14.1, 6.3, 0.0, 0.50, 0.55, 0.85, mat_ceramic, col_furnish)
    create_box("Bath1_Toilet", 13.5, 6.3, 0.0, 0.65, 0.45, 0.75, mat_ceramic, col_furnish)

    # 12. Entrance Foyer (현관) (X: [11.5, 13.0], Y: [7.5, 9.8])
    # Shoe Cabinet along West foyer wall (X=11.6)
    create_box("Shoe_Cabinet", 11.65, 8.6, 0.0, 0.40, 1.80, 2.10, mat_kitchen_b, col_furnish)

    # 13. Windows & Glass Openings
    # Living Room Main Sliding Window (South X: [4.4, 8.2], Y=0.25, Z: [0.0, 2.2])
    create_box("Window_Living_Glass", 6.3, 0.25, 0.05, 3.70, 0.04, 2.15, mat_glass, col_doors)
    # Master Balcony Outer Window (South X: [0.5, 2.4], Y=0.25)
    create_box("Window_MasterBalcony_Glass", 1.45, 0.25, 0.05, 1.90, 0.04, 2.15, mat_glass, col_doors)
    # Bed2 Window (South X: [9.0, 11.8], Y=0.25, Z: [0.8, 2.1])
    create_box("Window_Bed2_Glass", 10.4, 0.25, 0.80, 1.60, 0.04, 1.30, mat_glass, col_doors)
    # Bed3 Window (South X: [12.8, 14.8], Y=0.25, Z: [0.8, 2.1])
    create_box("Window_Bed3_Glass", 13.8, 0.25, 0.80, 1.60, 0.04, 1.30, mat_glass, col_doors)
    # Kitchen Window (North X: [5.2, 6.4], Y=10.2, Z: [1.1, 1.7])
    create_box("Window_Kitchen_Glass", 5.8, 10.2, 1.10, 1.20, 0.04, 0.60, mat_glass, col_doors)
    # Dressroom Window (North X: [1.0, 2.2], Y=10.2, Z: [1.1, 1.7])
    create_box("Window_Dress_Glass", 1.6, 10.2, 1.10, 1.20, 0.04, 0.60, mat_glass, col_doors)

    # 14. Interior Lighting for realistic ambiance
    # Living room warm ambient light
    light_data = bpy.data.lights.get("Light_Living_Warm") or bpy.data.lights.new("Light_Living_Warm", 'POINT')
    light_data.energy = 150.0
    light_data.color = (1.0, 0.95, 0.88)
    light_obj = bpy.data.objects.get("Light_Living_Warm") or bpy.data.objects.new("Light_Living_Warm", light_data)
    if light_obj.name not in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.link(light_obj)
    light_obj.location = (6.3, 3.2, 2.10)

    # Master bedroom warm light
    light_bed = bpy.data.lights.get("Light_Master_Warm") or bpy.data.lights.new("Light_Master_Warm", 'POINT')
    light_bed.energy = 80.0
    light_bed.color = (1.0, 0.92, 0.82)
    light_bed_obj = bpy.data.objects.get("Light_Master_Warm") or bpy.data.objects.new("Light_Master_Warm", light_bed)
    if light_bed_obj.name not in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.link(light_bed_obj)
    light_bed_obj.location = (2.2, 3.5, 2.10)

    # 15. First-Person Walkthrough Tour Camera Animation
    # Path: Foyer (X=12.2, Y=8.5) -> Corridor (X=9.0, Y=5.5) -> Alpha Room peek -> Living Room (X=6.5, Y=3.2) -> Master Bed (X=2.5, Y=3.5)
    cam_tour_data = bpy.data.cameras.get("Cam_Walkthrough") or bpy.data.cameras.new("Cam_Walkthrough")
    cam_tour_data.type = 'PERSP'
    cam_tour_data.lens = 22.0 # Wide angle for indoor walkthrough
    cam_tour_obj = bpy.data.objects.get("Cam_Walkthrough") or bpy.data.objects.new("Cam_Walkthrough", cam_tour_data)
    if cam_tour_obj.name not in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.link(cam_tour_obj)

    # Animation keyframes (250 frames total = ~10 sec)
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = 250

    waypoints = [
        # Frame 1: Entrance Foyer looking towards hallway
        (1,   (12.2, 8.8, 1.6), (math.radians(90), 0.0, math.radians(180))),
        # Frame 60: Moving through main corridor past Bathroom 1 & Bedroom 3
        (60,  (11.0, 5.5, 1.6), (math.radians(88), 0.0, math.radians(120))),
        # Frame 110: Looking at Alpha room and entering Living/Kitchen
        (110, (8.5,  4.5, 1.6), (math.radians(85), 0.0, math.radians(80))),
        # Frame 170: Center of Living Room looking at sofa, TV and kitchen
        (170, (6.2,  3.0, 1.6), (math.radians(85), 0.0, math.radians(45))),
        # Frame 250: Walking into Master Bedroom looking at King bed & Balcony
        (250, (3.0,  3.5, 1.6), (math.radians(85), 0.0, math.radians(-30)))
    ]

    for frame, loc, rot in waypoints:
        bpy.context.scene.frame_set(frame)
        cam_tour_obj.location = loc
        cam_tour_obj.rotation_euler = rot
        cam_tour_obj.keyframe_insert(data_path="location", frame=frame)
        cam_tour_obj.keyframe_insert(data_path="rotation_euler", frame=frame)

    # 16. Render Tour Keyframe Screenshots
    bpy.context.scene.camera = cam_tour_obj
    bpy.context.scene.render.resolution_x = 1280
    bpy.context.scene.render.resolution_y = 960

    # Screenshot 1: Foyer entrance
    bpy.context.scene.frame_set(1)
    os.makedirs("renders/archive/early-tour", exist_ok=True)
    bpy.context.scene.render.filepath = os.path.abspath("renders/archive/early-tour/tour_1_entrance_foyer.png")
    bpy.ops.render.render(write_still=True)

    # Screenshot 2: Living room & Kitchen perspective
    bpy.context.scene.frame_set(170)
    bpy.context.scene.render.filepath = os.path.abspath("renders/archive/early-tour/tour_2_living_kitchen.png")
    bpy.ops.render.render(write_still=True)

    # Screenshot 3: Master bedroom perspective
    bpy.context.scene.frame_set(250)
    bpy.context.scene.render.filepath = os.path.abspath("renders/archive/early-tour/tour_3_master_bedroom.png")
    bpy.ops.render.render(write_still=True)

    # Screenshot 4: Top-down orthographic 3D floor plan (like 84A.jpg)
    top_cam = bpy.data.objects.get("Cam_Corrected_Topdown")
    if top_cam:
        bpy.context.scene.camera = top_cam
        bpy.context.scene.render.filepath = os.path.abspath("renders/archive/early-tour/tour_topdown_furnished.png")
        bpy.ops.render.render(write_still=True)

    # 17. Save final blend file
    save_path = os.path.abspath("models/archive/apt_84a_furnished_tour.blend")
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=save_path)
    print("SUCCESS: Fully furnished apartment created and saved to:", save_path)

setup_interior()
