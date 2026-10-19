"""84A photoreal enhancement pass (additive, idempotent).

Adds interior detail props, lifestyle dressing, alpha-room home office,
new cameras - without touching existing collections' contents.
Run inside Blender (via MCP execute_code or blender --python).
"""
import bpy
import math
import mathutils
import os
import sys

script_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else "C:/Users/tamarand/orca/projects/apt/scripts"
if script_dir not in sys.path:
    sys.path.append(script_dir)

import importlib
import create_materials
importlib.reload(create_materials)
from create_materials import create_pbr_materials, create_detail_materials, upgrade_floor_and_artwall

import generate_high_detail_assets as A
importlib.reload(A)

# Prefixes owned by this pass: removed and rebuilt on every run (idempotent).
OWN_PREFIXES = (
    "Pendant_", "DiningProp_", "KitchenProp_", "Gallery_", "WallPad_",
    "Cove_", "AC_", "Vent_", "Refuge_", "Wardrobe_Bed3", "Office_",
    "BathProp_", "Dress_",
)


def snap_wall(origin, direction, fallback, max_dist=3.0):
    """Raycast from room air toward a wall; return hit point or fallback."""
    deps = bpy.context.evaluated_depsgraph_get()
    hit, loc, _nor, _idx, obj, _m = bpy.context.scene.ray_cast(
        deps, mathutils.Vector(origin), mathutils.Vector(direction))
    if hit and (loc - mathutils.Vector(origin)).length <= max_dist:
        print(f"  snap {origin}->{direction}: hit {obj.name} @ ({loc.x:.3f},{loc.y:.3f},{loc.z:.3f})")
        return (loc.x, loc.y, loc.z)
    print(f"  snap {origin}->{direction}: NO HIT -> fallback {fallback}")
    return fallback


def cleanup_previous_pass():
    removed = 0
    for o in list(bpy.data.objects):
        if o.name.startswith(OWN_PREFIXES):
            bpy.data.objects.remove(o, do_unlink=True)
            removed += 1
    # Pendant light datablocks share the object name; purge orphan lights
    for ld in list(bpy.data.lights):
        if ld.users == 0 and ld.name.startswith(OWN_PREFIXES):
            bpy.data.lights.remove(ld)
    print(f"Cleanup: removed {removed} objects from previous enhancement pass")


def M(name):
    mat = bpy.data.materials.get(name)
    if mat is None:
        print(f"  WARNING: material {name} missing")
    return mat


def build():
    print("=== 84A Enhancement Pass: materials ===")
    create_pbr_materials()
    create_detail_materials()
    upgrade_floor_and_artwall()

    cleanup_previous_pass()
    col = A.get_col("Apt_Furnishings")

    # Material shortcuts
    mat_runner = M("Mat_Bed_Runner")
    mat_linen = M("Mat_Bed_Linen")
    mat_walnut = M("Mat_Wood_Walnut")
    mat_chrome = M("Mat_Chrome_Metal")
    mat_glass = M("Mat_Glass_Clear")
    mat_frame = M("Mat_Window_Frame")
    mat_ceramic = M("Mat_Ceramic_White")
    mat_cab = M("Mat_Cabinet_Cashmere")
    mat_led = M("Mat_Light_Warm_Strip")
    mat_sofa = M("Mat_Fabric_Sofa")
    mat_screen = M("Mat_Screen_OLED")
    mat_wall = M("Mat_Wall_Interior")
    mat_steel = M("Mat_Steel_Brushed")
    mat_shade = M("Mat_Pendant_Black")
    mat_bulb = M("Mat_Bulb_Warm")
    mat_mat = M("Mat_TableRunner")
    mat_canvas = M("Mat_Canvas_Art")
    mat_vase = M("Mat_Vase_Ceramic")
    mat_plume = M("Mat_Plume")
    mat_fruit = M("Mat_Fruit_Orange")
    mat_books = [M(n) for n in ("Mat_Book_Navy", "Mat_Book_Terracotta", "Mat_Book_Sage",
                                "Mat_Book_Mustard", "Mat_Book_Charcoal", "Mat_Book_Cream")]
    mat_cloths = [mat_linen, mat_runner, mat_sofa, M("Mat_Book_Sage"), M("Mat_Book_Navy"), M("Mat_Book_Cream")]

    print("=== Dining pendants + table dressing ===")
    A.create_pendant_light("Pendant_Dining1", 5.9, 4.78, 2.30, 1.58, mat_shade=mat_shade,
                           mat_bulb=mat_bulb, mat_cord=mat_frame, col=col, energy=18.0)
    A.create_pendant_light("Pendant_Dining2", 5.9, 5.52, 2.30, 1.58, mat_shade=mat_shade,
                           mat_bulb=mat_bulb, mat_cord=mat_frame, col=col, energy=18.0)
    for i, (px, py) in enumerate([(5.68, 4.78), (5.68, 5.52), (6.12, 4.78), (6.12, 5.52)]):
        A.create_place_setting(f"DiningProp_Set{i+1}", px, py, 0.76, mat_mat=mat_mat,
                               mat_plate=mat_ceramic, mat_glass=mat_glass, col=col)
    A.create_table_vase("DiningProp_Vase", 5.9, 5.15, 0.76, mat_vase=mat_vase,
                        mat_stem=mat_walnut, mat_plume=mat_plume, col=col)

    print("=== Kitchen countertop props ===")
    A.create_pot("KitchenProp_Pot", 7.5, 7.82, 0.91, mat_steel=mat_steel, mat_handle=mat_frame, col=col)
    A.create_kettle("KitchenProp_Kettle", 7.5, 8.18, 0.91, mat_steel=mat_steel, mat_handle=mat_frame, col=col)
    A.create_cutting_board("KitchenProp_Board", 7.45, 10.0, 0.90, lean_deg=12, mat=mat_walnut, col=col)
    A.create_dish_rack("KitchenProp_Rack", 7.0, 9.72, 0.90, mat_tray=mat_chrome, mat_plate=mat_ceramic, col=col)
    A.create_fruit_bowl("KitchenProp_Fruit", 7.05, 6.40, 0.90, mat_bowl=mat_walnut, mat_fruit=mat_fruit, col=col)

    print("=== Living: gallery frames + wall pad (wall-snapped) ===")
    for i, gy in enumerate([2.30, 3.00, 3.70]):
        hit = snap_wall((8.0, gy, 1.78), (1, 0, 0), (9.01, gy, 1.78))
        A.create_gallery_frame(f"Gallery_Art{i+1}", hit[0] - 0.020, gy, 1.78, 0.55, 0.45,
                               facing='-x', mat_frame=mat_frame, mat_canvas=mat_canvas,
                               mat_accent=mat_books[i * 2 % len(mat_books)], col=col)
    hit = snap_wall((8.0, 4.10, 1.35), (1, 0, 0), (8.925, 4.10, 1.35))
    A.create_wall_pad("WallPad_Living", hit[0] - 0.015, 4.10, 1.35, facing='-x',
                      mat_body=mat_frame, mat_screen=mat_screen, mat_switch=mat_ceramic, col=col)

    print("=== Living: cove ceiling molding + LED ===")
    A.create_cove_molding("Cove_Living", 4.70, 8.70, 0.90, 5.30, 2.30,
                          mat_trim=mat_wall, mat_led=mat_led, col=col)

    print("=== Utility: AC condenser + vent + balcony refuge door ===")
    hit = snap_wall((8.9, 8.6, 0.5), (0, 1, 0), (8.9, 9.85, 0.5))
    A.create_ac_outdoor_unit("AC_Condenser", 8.9, hit[1] - 0.17 - 0.14, 0.0, facing='-y',
                             mat_body=M("Mat_AC_Body"), mat_grill=M("Mat_AC_Grill"),
                             mat_pipe=mat_chrome, col=col)
    hit = snap_wall((8.9, 9.0, 1.3), (0, -1, 0), (8.9, 8.20, 1.3))
    A.create_louver_door("Vent_ACRoom", 8.9, hit[1] + 0.03, 0.35, 0.90, 1.60, facing='+y', mat=mat_cab, col=col)
    hit = snap_wall((1.5, 1.1, 1.2), (-1, 0, 0), (0.70, 1.1, 1.2))
    A.create_refuge_door("Refuge_Balcony", hit[0] + 0.035, 1.1, 0.0, facing='+x',
                         mat_door=mat_cab, mat_sign=M("Mat_Sign_Red"), col=col)

    print("=== Bedroom 3: built-in wardrobe (wall-snapped) ===")
    hit = snap_wall((13.9, 3.0, 1.2), (0, 1, 0), (13.9, 4.30, 1.2))
    A.create_wardrobe("Wardrobe_Bed3", 13.9, hit[1] - 0.01, 0.0, 2.0, 0.60, 2.15,
                      facing='-y', mat_cab=mat_cab, mat_handle=mat_chrome, col=col)

    print("=== Alpha room: home office set ===")
    # North wall solid only for X<10.35 (jog/opening east of it); west side is
    # open plan, so the bookcase stands as a freestanding study divider.
    hit_n = snap_wall((10.2, 6.5, 1.0), (0, 1, 0), (10.2, 7.934, 1.0))
    desk_y = hit_n[1] - 0.34
    A.create_desk("Office_Desk", 9.9, desk_y, 0.0, 1.2, 0.6, mat_top=mat_walnut, mat_leg=mat_cab, col=col)
    desk_top = 0.765
    A.create_office_chair("Office_Chair", 9.9, desk_y - 0.78, 0.0, rot_z_deg=90,
                          mat_seat=mat_sofa, mat_frame=mat_frame, col=col)
    A.create_bookshelf("Office_Shelf", 6.8, 9.15, 0.0, 1.7, 0.32, 1.9,
                       facing='+x', mat_wood=mat_walnut, mat_books=mat_books, col=col)
    A.create_desk_lamp("Office_Lamp", 9.45, desk_y + 0.12, desk_top, mat_arm=mat_frame,
                       mat_shade=mat_shade, mat_bulb=mat_bulb, col=col)
    A.create_laptop("Office_Laptop", 9.95, desk_y - 0.02, desk_top, mat_body=mat_frame,
                    mat_screen=M("Mat_Laptop_Screen"), col=col)
    A.create_mug("Office_Mug", 10.3, desk_y + 0.05, desk_top, mat=mat_ceramic, col=col)
    A.create_rug("Office_Rug", 9.95, desk_y - 0.75, 0.012, 1.7, 1.3, mat=M("Mat_Rug_Office"), col=col)

    print("=== Dress room: open closet (wall-snapped) ===")
    hit = snap_wall((1.6, 7.9, 1.2), (-1, 0, 0), (0.70, 7.9, 1.2))
    A.create_dress_closet_y("Dress_Closet", 7.9, hit[0] + 0.02, 0.0, 2.4,
                            facing='+x', mat_wood=mat_walnut, mat_chrome=mat_chrome,
                            mat_cloths=mat_cloths, col=col)

    print("=== Bathrooms: mirror + towels ===")
    hit = snap_wall((3.5, 6.7, 1.4), (1, 0, 0), (4.10, 6.7, 1.4))
    A.create_bath_mirror("BathProp_MasterMirror", hit[0] - 0.025, 6.7, 1.02, 0.55, 0.75,
                         facing='-x', mat_mirror=mat_glass, mat_frame=mat_frame, mat_led=mat_led, col=col)
    A.create_folded_towels("BathProp_MasterTowels", 3.62, 6.95, 0.88, mat1=mat_linen, mat2=mat_runner, col=col)
    hit = snap_wall((14.2, 6.4, 1.3), (1, 0, 0), (14.90, 6.4, 1.3))
    A.create_towel_bar("BathProp_TowelBar", hit[0] - 0.06, 6.4, 1.25, 0.5, axis='y',
                       mat_chrome=mat_chrome, mat_towel=mat_linen, col=col)

    print("=== New presentation cameras ===")
    col_lights = A.get_col("Apt_Lighting")

    def look_at(cam_obj, target_pos):
        direction = mathutils.Vector(target_pos) - cam_obj.location
        cam_obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()

    def add_cam(name, loc, tgt):
        data = bpy.data.cameras.get(name) or bpy.data.cameras.new(name)
        data.type = 'PERSP'
        data.lens = 22.0
        obj = bpy.data.objects.get(name) or bpy.data.objects.new(name, data)
        if obj.name not in col_lights.objects:
            col_lights.objects.link(obj)
        obj.location = loc
        look_at(obj, tgt)
        print(f"  camera {name} @ {loc} -> {tgt}")

    add_cam("Cam_Kitchen_Reverse", (5.55, 9.0, 1.45), (6.7, 0.4, 0.95))
    add_cam("Cam_Dress_POV", (1.95, 6.1, 1.5), (1.15, 8.2, 1.0))
    add_cam("Cam_Bath_POV", (2.85, 6.6, 1.5), (3.5, 7.6, 0.4))

    print("=== Bath + dress ceiling fill lights ===")
    for lname, lloc, energy in [
        ("BathProp_CeilingLight", (3.45, 6.9, 2.15), 15.0),
        ("Dress_CeilingLight", (1.6, 7.8, 2.10), 12.0),
    ]:
        ld = bpy.data.lights.get(lname) or bpy.data.lights.new(lname, 'POINT')
        ld.energy = energy
        ld.color = (1.0, 0.93, 0.84)
        ld.shadow_soft_size = 0.12
        lo = bpy.data.objects.get(lname) or bpy.data.objects.new(lname, ld)
        if lo.name not in col_lights.objects:
            col_lights.objects.link(lo)
        lo.location = lloc

    # Verification summary
    owned = [o for o in bpy.data.objects if o.name.startswith(OWN_PREFIXES)]
    print(f"Enhancement objects in scene: {len(owned)}")
    for key in ("Pendant_Dining1", "Gallery_Art1_Frame", "Office_Desk_Top",
                "Wardrobe_Bed3_Carcass", "AC_Condenser_Body", "Cove_Living_TrimS"):
        o = bpy.data.objects.get(key)
        if o:
            print(f"  OK {key} @ ({o.location.x:.2f},{o.location.y:.2f},{o.location.z:.2f})")
        else:
            print(f"  MISSING {key}")

    save_file = os.path.abspath("apt_84a_photoreal_tour.blend")
    bpy.ops.wm.save_as_mainfile(filepath=save_file)
    print(f"Enhancement saved to: {save_file}")
    print("SUCCESS: enhancement pass complete!")


build()
