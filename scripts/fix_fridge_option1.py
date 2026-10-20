"""Fridge wall -> living-to-kitchen: fridge 1070 + kimchi 620 + rice 640.
+ planned appliances (LG Fit&Max style 600L drawer fridge, 300L kimchi)
+ rice-cooker drawer unit, and a real utility-room door (south wall).

Idempotent (Q3_* rebuilt). Run:
blender --background apt_84a_photoreal_tour.blend --python scripts/fix_fridge_option1.py
"""
import bpy
import os
import math

ROOT = r"C:\Users\tamarand\orca\projects\apt"

_g = {'__name__': 'q2lib'}
exec(compile(open(os.path.join(ROOT, "scripts", "improve_quality_v2.py"),
                 encoding="utf-8").read(), "improve_quality_v2.py", "exec"), _g)
box = _g['box']; cyl = _g['cyl']; sphere = _g['sphere']; cone = _g['cone']
flat_mat = _g['flat_mat']; assign = _g['assign']; _link = _g['_link']

# ---------- clean ----------
OLD = ("ProK_Bespoke_DoorBL", "ProK_Bespoke_DoorBR", "ProK_Bespoke_DoorTL",
       "ProK_Bespoke_DoorTR", "ProK_Bespoke_Frame", "ProK_Bespoke_Kimchi",
       "Kitchen_Fridge_Wall_Pantry_Door", "Kitchen_Fridge_Wall_Surround")
for o in list(bpy.data.objects):
    if o.name.startswith("Q3_") or o.name in OLD or o.name.startswith("ProDoorLeaf_Utility"):
        bpy.data.objects.remove(o, do_unlink=True)
_w9 = bpy.data.objects.get("ExactWall_9")
if _w9 is not None:
    bpy.data.objects.remove(_w9, do_unlink=True)
    print("[Q3] removed misplaced ExactWall_9 chunk (rebuilt thin below)")
print("[Q3] cleaned bespoke fridge wall")

CASH = bpy.data.materials["Mat_Cabinet_Cashmere"]
CHROME = bpy.data.materials.get("Mat_Chrome_Metal")
SEAM = flat_mat("Mat_Q3_Seam", "#17181A", rough=0.5, metallic=0.2)
TAUPE_L = flat_mat("Mat_Q3_TaupeL", "#B3A291", rough=0.38, metallic=0.12)
TAUPE_R = flat_mat("Mat_Q3_TaupeR", "#C4B8A6", rough=0.38, metallic=0.12)
CREAM = flat_mat("Mat_Q3_Cream", "#EAE5DB", rough=0.42, metallic=0.08)
KIMCHI = flat_mat("Mat_Q3_Kimchi", "#EEEAE1", rough=0.42, metallic=0.08)
BODY = flat_mat("Mat_Q3_Body", "#8F8B84", rough=0.6, metallic=0.3)
FRAME = bpy.data.materials.get("Mat_DoorFrame_White") or CASH

XF = 5.00   # front plane
XB = 4.43   # back wall face
XC = (XB + XF) / 2  # carcass centre x

# ---------- Option-1 carcass: usable front y 5.64..8.05 ----------
# North of y~8.08 the west wall steps east (x4.43 -> x5.12, ExactWall_11
# transverse wall at y8.19): the old row ran to y9.10, so the kimchi unit
# sat INSIDE that wall and blocked the utility door beside the sink.
# Row now ends at 8.05; utility door goes on the wall north of it.
# bays: rice 5.66-6.30, fridge 6.32-7.39, kimchi 7.41-8.03
box("Q3_SideS", (XC, 5.65, 1.14), (0.57, 0.02, 2.28), CASH)
box("Q3_SideN", (XC, 8.04, 1.14), (0.57, 0.02, 2.28), CASH)
box("Q3_Divider", (XC, 6.31, 0.95), (0.57, 0.02, 1.90), CASH)
box("Q3_Divider2", (XC, 7.40, 0.95), (0.57, 0.02, 1.90), CASH)
# top cabinet (sangbujang) z1900-2280
box("Q3_TopBottom", (XC, 6.845, 1.91), (0.57, 2.39, 0.02), CASH)
box("Q3_TopPanel", (XC, 6.845, 2.27), (0.57, 2.39, 0.02), CASH)
for i, (cy, w) in enumerate([(5.98, 0.60), (6.59, 0.50), (7.12, 0.50), (7.72, 0.58)]):
    box(f"Q3_TopDoor{i}", (4.99, cy, 2.09), (0.02, w, 0.34), CASH, bevel=0.004)
box("Q3_TopFiller", (4.99, 6.845, 1.855), (0.02, 2.39, 0.09), CASH)
print("[Q3] option-1 carcass (rice+fridge 1070+kimchi, top 1900, ends y8.05)")

# ---------- planned fridge: Fit&Max style, 912w in bay 6.32-7.39 ----------
box("Q3_FillerS", (4.985, 6.36, 0.95), (0.03, 0.079, 1.90), CASH)
box("Q3_FillerN", (4.985, 7.35, 0.95), (0.03, 0.079, 1.90), CASH)
box("Q3_Fridge_Body", (4.715, 6.855, 0.915), (0.57, 0.912, 1.79), BODY)
# top french doors (two-tone taupe), black groove, bottom 2 drawers (cream)
box("Q3_Fridge_DoorL", (5.005, 6.632, 1.44), (0.03, 0.446, 0.72), TAUPE_L, bevel=0.006)
box("Q3_Fridge_DoorR", (5.005, 7.078, 1.44), (0.03, 0.446, 0.72), TAUPE_R, bevel=0.006)
box("Q3_Fridge_Groove", (5.012, 6.855, 1.065), (0.012, 0.90, 0.02), SEAM)
box("Q3_Fridge_Drawer1", (5.005, 6.855, 0.815), (0.03, 0.902, 0.46), CREAM, bevel=0.006)
box("Q3_Fridge_Drawer2", (5.005, 6.855, 0.325), (0.03, 0.902, 0.46), CREAM, bevel=0.006)
box("Q3_Fridge_Display", (5.022, 7.225, 1.62), (0.006, 0.07, 0.03), SEAM)

# ---------- planned kimchi 300L slim: 600w in bay 7.41-8.03 ----------
box("Q3_Kimchi_Body", (4.715, 7.72, 0.915), (0.57, 0.60, 1.79), BODY)
box("Q3_Kimchi_Top", (5.005, 7.72, 1.54), (0.03, 0.59, 0.52), KIMCHI, bevel=0.006)
box("Q3_Kimchi_Mid", (5.005, 7.72, 0.98), (0.03, 0.59, 0.56), KIMCHI, bevel=0.006)
box("Q3_Kimchi_Bot", (5.005, 7.72, 0.37), (0.03, 0.59, 0.62), KIMCHI, bevel=0.006)
box("Q3_Kimchi_Line1", (5.012, 7.72, 1.265), (0.012, 0.58, 0.018), SEAM)
box("Q3_Kimchi_Line2", (5.012, 7.72, 0.685), (0.012, 0.58, 0.018), SEAM)
box("Q3_Kimchi_FillerS", (4.985, 7.42, 0.95), (0.03, 0.02, 1.90), CASH)
box("Q3_Kimchi_FillerN", (4.985, 8.02, 0.95), (0.03, 0.02, 1.90), CASH)
print("[Q3] fridge 912 + kimchi 600 modelled")

# ---------- rice-cooker drawer unit: south bay of the row ----------
# outer y 5.66..6.30 (640w), front 5.00, shares the row top-cabinet line
box("Q3_Drawer_SideS", (XC, 5.67, 1.14), (0.57, 0.02, 2.28), CASH)
box("Q3_Drawer_SideN", (XC, 6.29, 1.14), (0.57, 0.02, 2.28), CASH)
box("Q3_Drawer_TopBottom", (XC, 5.98, 1.91), (0.57, 0.60, 0.02), CASH)
box("Q3_Drawer_TopPanel", (XC, 5.98, 2.27), (0.57, 0.60, 0.02), CASH)
box("Q3_Drawer_TopCabDoor", (4.99, 5.98, 2.09), (0.02, 0.56, 0.34), CASH, bevel=0.004)
box("Q3_Drawer_Core", (4.71, 5.98, 0.43), (0.54, 0.56, 0.82), CASH)
box("Q3_Drawer_Front1", (4.995, 5.98, 0.64), (0.02, 0.56, 0.36), CASH, bevel=0.004)
box("Q3_Drawer_Front2", (4.995, 5.98, 0.24), (0.02, 0.56, 0.36), CASH, bevel=0.004)
for i, zz in enumerate((0.80, 0.40)):
    cyl(f"Q3_Drawer_Handle{i}", (5.03, 5.98, zz), 0.008, 0.32, CHROME,
        rot=(math.pi / 2, 0, 0), vertices=12)
# open rice niche z0.86..1.30 + upper door to 1900
box("Q3_Niche_Shelf", (4.72, 5.98, 0.855), (0.52, 0.56, 0.02), CASH)
box("Q3_Niche_Top", (4.72, 5.98, 1.315), (0.52, 0.56, 0.02), CASH)
box("Q3_Niche_Back", (4.465, 5.98, 1.09), (0.02, 0.56, 0.46), BODY)
box("Q3_Drawer_TopDoor", (4.995, 5.98, 1.615), (0.02, 0.56, 0.55), CASH, bevel=0.004)
CER = bpy.data.materials.get("Mat_Ceramic_White")
cyl("Q3_Cooker_Body", (4.72, 5.98, 0.975), 0.155, 0.21, CER)
sphere("Q3_Cooker_Lid", (4.72, 5.98, 1.085), 0.15, CER, scale=(1, 1, 0.5))
box("Q3_Cooker_Panel", (4.878, 5.98, 0.99), (0.012, 0.09, 0.035), SEAM)
print("[Q3] rice-cooker drawer unit (south bay 640w)")

# Move complete bays, including their upper doors, into the requested order.
# Construction above uses the original bay positions; these shifts run once per rebuild.
for o in bpy.data.objects:
    if o.name.startswith(("Q3_Fridge_", "Q3_Kimchi_", "Q3_Filler")) or o.name in (
            "Q3_TopDoor1", "Q3_TopDoor2", "Q3_TopDoor3"):
        o.location.y -= 0.66
    elif o.name.startswith(("Q3_Drawer_", "Q3_Niche_", "Q3_Cooker_")) or o.name == "Q3_TopDoor0":
        o.location.y += 1.73
bpy.data.objects["Q3_Divider"].location.y = 6.74
bpy.data.objects["Q3_Divider2"].location.y = 7.38
bpy.context.view_layer.update()
assert abs(bpy.data.objects["Q3_Fridge_Body"].location.y - 6.195) < 1e-5
assert abs(bpy.data.objects["Q3_Kimchi_Body"].location.y - 7.06) < 1e-5
assert abs(bpy.data.objects["Q3_Cooker_Body"].location.y - 7.71) < 1e-5
assert bpy.data.objects["Q3_Drawer_SideN"].location.y + 0.01 < 8.08
print("[Q3] living -> kitchen: fridge 5.66..6.73, kimchi 6.75..7.37, rice 7.39..8.03")

# ---------- utility door: use the original x9.00..9.731 opening ----------
# Preserve the thick west boundary; Q5 restores it from the plan.
for yy, tag in ((7.935, "S"), (8.19, "N")):
    box(f"Q3_Trim{tag}_L", (8.965, yy, 1.06), (0.07, 0.025, 2.12), FRAME)
    box(f"Q3_Trim{tag}_R", (9.766, yy, 1.06), (0.07, 0.025, 2.12), FRAME)
    box(f"Q3_Trim{tag}_Top", (9.3655, yy, 2.135), (0.871, 0.025, 0.07), FRAME)
box("ProDoorLeaf_Utility", (9.70, 8.535, 1.05), (0.04, 0.67, 2.07), CASH, bevel=0.006)
box("Q3_Utility_HandleBase", (9.66, 8.80, 1.02), (0.02, 0.05, 0.12), CHROME)
box("Q3_Utility_HandleBar", (9.65, 8.775, 1.06), (0.018, 0.11, 0.022), CHROME)
print("[Q3] utility door open at native alpha-room north opening")

# ---------- utility door beside the sink (west wall, north of the row) ----------
# The fridge row used to run past the wall step (y8.19) and block this spot.
# Door 800 wide at y8.28..9.08 in ExactWall_11, right beside the sink run
# (sink counter west end x4.98, y9.42+). Leaf opens into the utility side.
wall11 = bpy.data.objects.get("ExactWall_11")
cutter3 = box("Q3_Cutter_Temp3", (5.06, 8.68, 1.02), (0.56, 0.80, 2.24), None)
if wall11 is not None:
    bpy.context.view_layer.objects.active = wall11
    wall11.select_set(True)
    mod = wall11.modifiers.new("Q3SinkDoorCut", 'BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.solver = 'EXACT'
    mod.object = cutter3
    bpy.ops.object.modifier_apply(modifier=mod.name)
    wall11.select_set(False)
    print("[Q3] sink-side utility doorway cut 800x2100 in ExactWall_11")
bpy.data.objects.remove(cutter3, do_unlink=True)
for xx, tag in ((5.145, "K"), (4.995, "R")):
    box(f"Q3_SinkTrim{tag}_S", (xx, 8.315, 1.06), (0.025, 0.07, 2.12), FRAME)
    box(f"Q3_SinkTrim{tag}_N", (xx, 9.045, 1.06), (0.025, 0.07, 2.12), FRAME)
    box(f"Q3_SinkTrim{tag}_Top", (xx, 8.68, 2.135), (0.025, 0.80, 0.07), FRAME)
# leaf open 90 deg into the utility room (perpendicular, clear of cabinets)
box("ProDoorLeaf_UtilitySink", (4.62, 8.325, 1.04), (0.76, 0.035, 2.04), CASH, bevel=0.006)
box("Q3_SinkDoor_HandleBase", (4.32, 8.36, 1.02), (0.05, 0.02, 0.12), CHROME)
box("Q3_SinkDoor_HandleBar", (4.30, 8.385, 1.06), (0.16, 0.018, 0.022), CHROME)
print("[Q3] sink-side utility door installed (leaf open, utility side)")

# verification camera (excluded from GLB export like all cameras)
if bpy.data.objects.get("Q3_Cam_Fridge") is None:
    cam_data = bpy.data.cameras.new("Q3_Cam_Fridge")
    cam = bpy.data.objects.new("Q3_Cam_Fridge", cam_data)
    bpy.context.scene.collection.objects.link(cam)
else:
    cam = bpy.data.objects["Q3_Cam_Fridge"]
cam.location = (8.1, 6.1, 1.55)
from mathutils import Vector as _V
cam.rotation_euler = (_V((4.9, 7.45, 1.02)) - _V(cam.location)).to_track_quat('-Z', 'Y').to_euler()
cam.data.lens = 24
print("[Q3] fridge cam set")

bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT, "apt_84a_photoreal_tour.blend"))
print("[Q3] SAVED apt_84a_photoreal_tour.blend")
