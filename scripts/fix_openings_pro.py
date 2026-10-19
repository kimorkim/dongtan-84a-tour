"""Fix PRO-1: window/wall integration rebuilt to surveyed openings + e-modelhouse.

- Deletes misaligned window units, rebuilds white-frame units fitted to the
  exact wall holes (surveyed from ExactWall meshes + official plan).
- Adds sill/header masonry, stone sill caps, white jamb liners.
- Adds missing exterior walls (north + east-north), entry frame/slab.
- Adds balcony slab + guardrail outside living/master windows.
- Repositions living/master curtains to new opening centers.
Idempotent: removes its own + legacy window/curtain objects, then rebuilds.
"""
import bpy
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

LEGACY_PREFIXES = (
    "Win_Living", "Win_MasterBalcony", "Win_Bed2", "Win_Bed3",
    "Win_Kitchen", "Win_Dress", "Door_MasterBalcony_Glass",
    "Curtain_Living", "Curtain_Master",
)
OWN_PREFIXES = (
    "SillPatch_", "Liner_", "Rail_", "BalconySlab_", "NewWall_",
    "EntryFrame_", "EntrySlab_",
)


def cleanup():
    removed = 0
    for o in list(bpy.data.objects):
        if o.name.startswith(LEGACY_PREFIXES) or o.name.startswith(OWN_PREFIXES):
            bpy.data.objects.remove(o, do_unlink=True)
            removed += 1
    print(f"Cleanup: removed {removed} legacy/opening objects")


def M(name):
    return bpy.data.materials.get(name)


def build():
    print("=== PRO-1: materials ===")
    create_pbr_materials()
    create_detail_materials()
    upgrade_floor_and_artwall()
    cleanup()

    col_open = A.get_col("Apt_Windows_Doors")
    col_struct = bpy.data.collections.get("Apt_Corrected_Structure")
    col_furn = A.get_col("Apt_Furnishings")

    mat_frame_w = M("Mat_WindowFrame_White")
    mat_glass = M("Mat_Glass_Clear")
    mat_wall = M("Mat_Wall_Interior")
    mat_cap = M("Mat_Wall_Cap")
    mat_liner = M("Mat_Cabinet_Cashmere")
    mat_marble = M("Mat_Marble_White")
    mat_tile = M("Mat_Tile_Grey")
    mat_rail = M("Mat_Rail_Dark")
    mat_curtain = M("Mat_Curtain")
    mat_slate = M("Mat_Tile_DarkSlate")
    mat_door_blue = M("Mat_Door_Blue")

    print("=== South windows (white frames, fitted to holes) ===")
    wins = [
        # name, x, y, z, w, depth, h, panes
        ("Win_MasterVent", 0.705, 0.385, 0.0, 0.41, 0.16, 2.20, 1),
        ("Win_MasterMain", 3.15, 0.385, 0.0, 1.52, 0.16, 2.20, 2),
        ("Win_Living", 6.65, 0.385, 0.0, 3.60, 0.16, 2.20, 3),
        ("Win_Bed2", 10.315, 0.385, 0.80, 1.71, 0.16, 1.40, 2),
        ("Win_Bed3", 13.39, 0.385, 0.80, 2.00, 0.16, 1.40, 2),
        ("Win_Kitchen", 6.15, 10.07, 1.10, 1.22, 0.16, 0.70, 2),
        ("Win_Dress", 1.33, 10.07, 1.10, 1.40, 0.16, 0.70, 2),
        ("Door_MasterBalcony_Glass", 3.075, 1.77, 0.0, 1.67, 0.10, 2.15, 2),
    ]
    for name, x, y, z, w, d, h, panes in wins:
        A.create_window_unit(name, x, y, z, w, d, h, panes=panes,
                             mat_frame=mat_frame_w, mat_glass=mat_glass, col=col_open)
    print(f"  rebuilt {len(wins)} units")

    print("=== Sill + header masonry with stone caps ===")
    A.create_sill_and_header("SillPatch_Bed2", 9.45, 11.18, 0.26, 0.51, 0.80, 2.20,
                             mat_wall=mat_wall, mat_cap=mat_marble, col=col_struct, cap_dy=0.01)
    A.create_sill_and_header("SillPatch_Bed3", 12.38, 14.40, 0.26, 0.51, 0.80, 2.20,
                             mat_wall=mat_wall, mat_cap=mat_marble, col=col_struct, cap_dy=0.01)
    A.create_sill_and_header("SillPatch_Kitchen", 5.53, 6.77, 9.92, 10.22, 1.10, 1.80,
                             mat_wall=mat_wall, mat_cap=mat_marble, col=col_struct, cap_dy=-0.01)
    A.create_sill_and_header("SillPatch_Dress", 0.62, 2.04, 9.92, 10.22, 1.10, 1.80,
                             mat_wall=mat_wall, mat_cap=mat_marble, col=col_struct, cap_dy=-0.01)

    print("=== Jamb liners ===")
    liners = [
        ("Liner_MasterVent", 0.49, 0.92, 0.26, 0.51, 0.0, 2.20),
        ("Liner_MasterMain", 2.38, 3.92, 0.26, 0.51, 0.0, 2.20),
        ("Liner_Living", 4.84, 8.46, 0.26, 0.51, 0.0, 2.20),
        ("Liner_Bed2", 9.45, 11.18, 0.26, 0.51, 0.80, 2.20),
        ("Liner_Bed3", 12.38, 14.40, 0.26, 0.51, 0.80, 2.20),
        ("Liner_Kitchen", 5.53, 6.77, 9.92, 10.22, 1.10, 1.80),
        ("Liner_Dress", 0.62, 2.04, 9.92, 10.22, 1.10, 1.80),
        ("Liner_BalconyDoor", 2.23, 3.92, 1.70, 1.84, 0.0, 2.15),
    ]
    for name, x1, x2, y1, y2, z1, z2 in liners:
        A.create_jamb_liners(name, x1, x2, y1, y2, z1, z2, mat=mat_liner, col=col_open)

    print("=== Missing exterior walls (north + east-north) ===")
    new_walls = [
        ("NewWall_NorthW", 8.18, 11.72, 10.00, 10.22, 0.0, 2.30),
        ("NewWall_NorthE", 12.68, 15.03, 10.00, 10.22, 0.0, 2.30),
        ("NewWall_NorthHead", 11.72, 12.68, 10.00, 10.22, 2.15, 2.30),
        ("NewWall_EastN", 14.98, 15.23, 7.97, 10.22, 0.0, 2.30),
    ]
    for name, x1, x2, y1, y2, z1, z2 in new_walls:
        o = A.create_beveled_box(name, (x1 + x2) / 2, (y1 + y2) / 2, z1,
                                 x2 - x1, y2 - y1, z2 - z1, bevel=0.004, col=col_struct)
        o.data.materials.clear()
        o.data.materials.append(mat_wall)
        o.data.materials.append(mat_cap)
        for poly in o.data.polygons:
            poly.material_index = 1 if poly.normal.z > 0.8 else 0
        o.data.update()
    A.create_entry_frame("EntryFrame_Front", 11.72, 12.68, 10.11, 2.15, mat=mat_door_blue, col=col_open)
    A.create_balcony_slab("EntrySlab_Front", 11.2, 13.2, 10.22, 11.3, -0.02, mat=mat_slate, col=col_open)

    print("=== Balcony slab + guardrail (south) ===")
    A.create_balcony_slab("BalconySlab_South", 0.3, 8.6, -1.4, 0.26, -0.02, mat=mat_tile, col=col_open)
    A.create_railing("Rail_South", 0.4, 8.5, -1.25, -0.02, height=1.10, mat=mat_rail, col=col_open)

    print("=== Curtains repositioned to new centers ===")
    A.create_curtain("Curtain_Living", 6.65, 0.45, 0.0, 3.62, 2.30, mat_curtain=mat_curtain, col=col_furn)
    A.create_curtain("Curtain_Master", 3.075, 1.90, 0.0, 1.69, 2.20, mat_curtain=mat_curtain, col=col_furn)

    for key in ("Win_Living_Glass_2", "Win_Kitchen_Mullion", "SillPatch_Bed2_SillCap",
                "NewWall_EastN", "Rail_South_TopRail", "Curtain_Master_Left"):
        o = bpy.data.objects.get(key)
        print(f"  {'OK' if o else 'MISSING'} {key}")

    bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath("apt_84a_photoreal_tour.blend"))
    print("SUCCESS: PRO-1 openings rebuilt!")


build()
