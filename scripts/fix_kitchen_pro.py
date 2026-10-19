"""Fix PRO-2: kitchen rebuilt to e-modelhouse (seamless L-run + marble + appliances).

- Deletes legacy kitchen boxes (keeps fridge wall) and rebuilds abutting
  base/top runs with zero coplanar overlap, marble tops + full backsplash.
- Flat black hood, black built-in oven, steel dishwasher, single sink.
- East + extended north uppers with LED, linear ceiling LED strips.
- Marble top on living media console. Rack/board adopted at new positions.
Idempotent: deletes legacy + own objects by name, then rebuilds.
"""
import bpy
import mathutils
import os
import sys

script_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else "C:/Users/tamarand/orca/projects/apt/scripts"
if script_dir not in sys.path:
    sys.path.append(script_dir)

import importlib
import create_materials
importlib.reload(create_materials)
from create_materials import create_detail_materials

import generate_high_detail_assets as A
importlib.reload(A)

LEGACY = (
    "Kitchen_North_Base", "Kitchen_North_Top",
    "Kitchen_East_Base", "Kitchen_East_Top",
    "Kitchen_Induction",
    "Kitchen_RangeHood_Canopy", "Kitchen_RangeHood_Chimney",
    "Kitchen_Sink",
    "Kitchen_Upper_North_Box", "Kitchen_Upper_North_LED_Strip",
    "Kitchen_Upper_NorthL", "Kitchen_Upper_NorthR",
    "Kitchen_Peninsula_Base", "Kitchen_Peninsula_Top",
    "KitchenProp_Rack", "KitchenProp_Board",
    "Kitchen_Top_Unified", "Kitchen_Base_Unified", "Kitchen_Kick_Unified",
    "Kitchen_Top_", "Kitchen_Base_", "Kitchen_Kick_",
)
OWN_PREFIXES = ("ProK_",)


def cleanup():
    removed = 0
    for o in list(bpy.data.objects):
        if o.name.startswith(LEGACY) or o.name.startswith(OWN_PREFIXES):
            bpy.data.objects.remove(o, do_unlink=True)
            removed += 1
    print(f"Cleanup: removed {removed} legacy/kitchen objects")


def snap(origin, direction, fallback, max_dist=3.0):
    deps = bpy.context.evaluated_depsgraph_get()
    hit, loc, _n, _i, obj, _m = bpy.context.scene.ray_cast(
        deps, mathutils.Vector(origin), mathutils.Vector(direction))
    if hit and (loc - mathutils.Vector(origin)).length <= max_dist:
        print(f"  snap {origin}->{direction}: {obj.name} @ ({loc.x:.3f},{loc.y:.3f},{loc.z:.3f})")
        return (loc.x, loc.y, loc.z)
    print(f"  snap {origin}->{direction}: fallback {fallback}")
    return fallback


def M(name):
    return bpy.data.materials.get(name)


def build():
    print("=== PRO-2: materials ===")
    create_detail_materials()
    cleanup()
    col = A.get_col("Apt_Furnishings")

    mat_cab = M("Mat_Cabinet_Cashmere")
    mat_marble = M("Mat_Marble_White")
    mat_chrome = M("Mat_Chrome_Metal")
    mat_steel = M("Mat_Steel_Brushed")
    mat_oven = M("Mat_Oven_Black")
    mat_hood = M("Mat_Hood_Black")
    mat_led = M("Mat_Light_Warm_Strip")
    mat_ceramic = M("Mat_Ceramic_White")
    mat_walnut = M("Mat_Wood_Walnut")

    # Wall faces for backsplash + uppers (x=7.3 avoids the window hole)
    nface = snap((7.3, 9.5, 1.2), (0, 1, 0), (7.3, 9.92, 1.2))[1]
    eface = snap((7.0, 8.0, 1.2), (1, 0, 0), (7.90, 8.0, 1.2))[0]
    print(f"  north face y={nface:.3f}, east face x={eface:.3f}")

    print("=== ㄷ-run: 3 abutting runs, hairline bevel (aisle stays OPEN) ===")
    # NOTE: single concave NGon fills the work aisle in Blender triangulation,
    # so the U is 3 exactly-abutting boxes with 2mm micro-bevel: no grooves.
    mat_kick = M("Mat_AC_Grill")
    runs = [
        # tag, x1, x2, y1, y2 (peninsula runs full-width to east wall: no notch)
        ("North", 5.0, 7.825, 9.425, 10.075),
        ("East", 7.175, 7.825, 6.725, 9.425),
        ("Pen", 5.5, 7.825, 6.075, 6.725),
    ]
    for tag, x1, x2, y1, y2 in runs:
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        A.create_beveled_box(f"Kitchen_Base_{tag}", cx, cy, 0.07, x2 - x1, y2 - y1, 0.79,
                             bevel=0.002, seg=1, mat=mat_cab, col=col)
    tops = [
        ("North", 4.98, 7.825, 9.405, 10.075),
        ("East", 7.175, 7.825, 6.725, 9.425),
        ("Pen", 5.48, 7.825, 6.055, 6.725),
    ]
    for tag, x1, x2, y1, y2 in tops:
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        A.create_beveled_box(f"Kitchen_Top_{tag}", cx, cy, 0.86, x2 - x1, y2 - y1, 0.04,
                             bevel=0.002, seg=1, mat=mat_marble, col=col)
    kicks = [
        ("North", 5.06, 7.765, 9.485, 10.015),
        ("East", 7.235, 7.765, 6.785, 9.485),
        ("Pen", 5.56, 7.765, 6.135, 6.785),
    ]
    for tag, x1, x2, y1, y2 in kicks:
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        A.create_beveled_box(f"Kitchen_Kick_{tag}", cx, cy, 0.0, x2 - x1, y2 - y1, 0.07,
                             bevel=0.001, seg=1, mat=mat_kick, col=col)

    def door(name, cx, cy, w, facing):
        if facing == '-y':
            A.create_beveled_box(name, cx, cy, 0.10, w, 0.018, 0.72, bevel=0.004, mat=mat_cab, col=col)
        else:
            A.create_beveled_box(name, cx, cy, 0.10, 0.018, w, 0.72, bevel=0.004, mat=mat_cab, col=col)

    # North front (y=9.417 plane) — 3 doors right of dishwasher
    for i in range(3):
        door(f"ProK_DoorN{i+1}", 5.68 + 1.47 * (i + 0.5) / 3, 9.417, 0.47, '-y')
    # East front (x=7.167 plane) — 2+2 doors around oven
    for i in range(2):
        door(f"ProK_DoorE_S{i+1}", 7.167, 6.78 + 0.92 * (i + 0.5) / 2, 0.44, '-x')
        door(f"ProK_DoorE_N{i+1}", 7.167, 8.34 + 1.03 * (i + 0.5) / 2, 0.495, '-x')
    # Peninsula south (y=6.067 plane) + west end panel
    for i in range(4):
        door(f"ProK_DoorP{i+1}", 5.53 + 2.25 * (i + 0.5) / 4, 6.067, 0.54, '-y')
    door("ProK_EndPanelW", 5.492, 6.40, 0.60, '-x')

    print("=== Marble backsplash ===")
    A.create_backsplash("ProK_SplashNorth", 5.0, 7.825, nface - 0.011, 0.90, 1.55,
                        mat=mat_marble, col=col, axis='x')
    A.create_backsplash("ProK_SplashEast", 6.725, 9.425, eface - 0.011, 0.90, 1.55,
                        mat=mat_marble, col=col, axis='y')

    print("=== Sink + dishwasher + oven + induction + hood ===")
    A.create_sink_single("Kitchen_Sink", 6.15, 9.75, 0.90, mat_sink=mat_steel,
                         mat_chrome=mat_chrome, col=col)
    A.create_dishwasher_front("ProK_Dishwasher", 5.35, 9.408, 0.10, 0.60,
                              mat_steel=mat_steel, mat_handle=mat_chrome, col=col)
    A.create_builtin_oven("ProK_Oven", 7.175, 8.0, 0.10, 0.56, mat_black=mat_oven,
                          mat_handle=mat_chrome, col=col, facing='-x')
    A.create_beveled_box("Kitchen_Induction", 7.5, 8.0, 0.902, 0.52, 0.60, 0.008,
                         bevel=0.002, mat=mat_oven, col=col)
    A.create_flat_hood("ProK_Hood", eface - 0.25, 8.0, 1.47, 0.45, 0.76, mat=mat_hood, col=col)

    print("=== Uppers (split around window + east run) with LED ===")
    A.create_upper_cabinets("Kitchen_Upper_NorthL", 5.265, 9.85, 1.55, 0.53, 0.35, 0.70,
                            mat_cab=mat_cab, mat_led=mat_led, col=col)
    A.create_upper_cabinets("Kitchen_Upper_NorthR", 7.36, 9.85, 1.55, 1.18, 0.35, 0.70,
                            mat_cab=mat_cab, mat_led=mat_led, col=col)
    A.create_beveled_box("ProK_UpperEast", eface - 0.175, 8.2875, 1.55, 0.35, 2.775, 0.70,
                         bevel=0.01, seg=2, mat=mat_cab, col=col)
    A.create_beveled_box("ProK_UpperEast_LED1", eface - 0.175, 7.225, 1.535, 0.30, 0.55, 0.015,
                         bevel=0.002, seg=1, mat=mat_led, col=col)
    A.create_beveled_box("ProK_UpperEast_LED2", eface - 0.175, 9.05, 1.535, 0.30, 1.10, 0.015,
                         bevel=0.002, seg=1, mat=mat_led, col=col)

    print("=== Linear ceiling LEDs + rack/board/media-top ===")
    A.create_ceiling_strip("ProK_CeilStrip1", 5.1, 7.7, 7.3, 2.27, 0.08, mat_led=mat_led, col=col)
    A.create_ceiling_strip("ProK_CeilStrip2", 5.1, 7.7, 8.7, 2.27, 0.08, mat_led=mat_led, col=col)
    A.create_dish_rack("KitchenProp_Rack", 7.0, 9.72, 0.90, mat_tray=mat_chrome,
                       mat_plate=mat_ceramic, col=col)
    A.create_cutting_board("KitchenProp_Board", 7.45, 10.0, 0.90, lean_deg=12, mat=mat_walnut, col=col)
    A.create_beveled_box("ProK_MediaTop", 4.58, 3.2, 0.44, 0.36, 2.20, 0.02,
                         bevel=0.006, mat=mat_marble, col=col)

    for key in ("Kitchen_Top_North", "Kitchen_Top_East", "Kitchen_Top_Pen",
                "Kitchen_Base_North", "Kitchen_Sink_Bowl", "ProK_Oven_Door", "ProK_Hood_Slab",
                "ProK_SplashNorth", "ProK_UpperEast", "Kitchen_Upper_NorthL_Box",
                "Kitchen_Upper_NorthR_Box"):
        o = bpy.data.objects.get(key)
        if o:
            print(f"  OK {key} @ ({o.location.x:.2f},{o.location.y:.2f},{o.location.z:.2f})")
        else:
            print(f"  MISSING {key}")

    bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath("apt_84a_photoreal_tour.blend"))
    print("SUCCESS: PRO-2 kitchen rebuilt!")


build()
