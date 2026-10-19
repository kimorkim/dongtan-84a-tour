"""Quality v2c patch: transparent glass, neutral daylight, lighter walls.
Self-contained (no v2 re-run). blender --background <blend> --python this.py
"""
import bpy
import os
import math

ROOT = r"C:\Users\tamarand\orca\projects\apt"

# ---- glass: transmission reads black here; use reliable alpha glass ----
m = bpy.data.materials.get("Mat_Glass_Clear")
if m and m.use_nodes:
    for n in m.node_tree.nodes:
        if n.type == 'BSDF_PRINCIPLED':
            n.inputs["Transmission Weight"].default_value = 0.0
            n.inputs["Alpha"].default_value = 0.15
            n.inputs["Roughness"].default_value = 0.05
            n.inputs["Base Color"].default_value = (0.95, 0.98, 1.0, 1.0)
    m.surface_render_method = 'DITHERED'
    print("[Q2c] glass -> alpha 0.15")

# ---- neutral daylight (modelhouse photos are daylight-balanced) ----
for o in bpy.data.objects:
    if o.type == 'LIGHT' and o.data.type in ('POINT', 'SPOT', 'AREA'):
        if 'Pendant' not in o.name and 'Sconce' not in o.name:
            o.data.color = (1.0, 0.97, 0.93)
sun = bpy.data.objects.get("Sun_Natural")
if sun:
    sun.data.color = (1.0, 0.99, 0.96)

# ---- walls lighter / less saturated (HueSat nodes from v2 build) ----
for mname in ("Mat_Wall_Interior", "Mat_Wall_Cap"):
    mat = bpy.data.materials.get(mname)
    if mat:
        for n in mat.node_tree.nodes:
            if n.type == 'HUE_SAT':
                n.inputs["Value"].default_value = 1.70
                n.inputs["Saturation"].default_value = 0.40
        print(f"[Q2c] {mname} value=1.70 sat=0.40")

# ---- master wall panel: mute fabric pattern (AO/normal down) ----
panel = bpy.data.materials.get("Mat_Q2_WallPanel")
if panel:
    for n in panel.node_tree.nodes:
        if n.type == 'MIX_RGB':
            n.inputs["Fac"].default_value = 0.03
        if n.type == 'NORMAL_MAP':
            n.inputs["Strength"].default_value = 0.08

# ---- landscape cards brighter ----
lm = bpy.data.materials.get("Mat_Q2_Landscape")
if lm:
    for n in lm.node_tree.nodes:
        if n.type == 'EMISSION':
            n.inputs["Strength"].default_value = 0.9

# ---- kitchen ceiling AC frame to cabinet white ----
cab = bpy.data.materials.get("Mat_Cabinet_Cashmere")
for name in ("Kitchen_System_AC_Frame",):
    o = bpy.data.objects.get(name)
    if o and cab:
        o.data.materials.clear(); o.data.materials.append(cab)

# ---- walnut door/panels inside master bedroom zone -> cashmere ----
if cab:
    for o in bpy.data.objects:
        if o.type != 'MESH':
            continue
        c = o.matrix_world.translation
        if 0 < c.x < 4.6 and 1.4 < c.y < 5.7:
            mats = [x.name if x else "" for x in o.data.materials]
            if mats == ["Mat_Wood_Walnut"] and not o.name.startswith("Bed_Master"):
                o.data.materials.clear(); o.data.materials.append(cab)
                print(f"[Q2c] master walnut->cashmere {o.name}")

# ---- accent cushions: casual tilt ----
for cname in ("Q2_Master_CushionS", "Q2_Master_CushionN"):
    c = bpy.data.objects.get(cname)
    if c:
        c.rotation_euler = (0, -0.50, 0.12)

bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT, "apt_84a_photoreal_tour.blend"))
print("[Q2c] SAVED")
