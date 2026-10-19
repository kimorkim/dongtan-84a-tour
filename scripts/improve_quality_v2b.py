"""Quality v2b patch: brightness, white marble, fabric subtlety, north view.

Run after improve_quality_v2.py on the saved blend. Idempotent.
blender --background apt_84a_photoreal_tour.blend --python scripts/improve_quality_v2b.py
"""
import bpy
import os
import math

ROOT = r"C:\Users\tamarand\orca\projects\apt"
exec(compile(open(os.path.join(ROOT, "scripts", "improve_quality_v2.py"),
                 encoding="utf-8").read(), "improve_quality_v2.py", "exec"),
     globals())

# ---- 1. lighting: restore modelhouse daylight brightness, single sun ----
ENERGY = {
    "BathProp_CeilingLight": 30, "Downlight_Hallway": 26, "Downlight_Kitchen": 30,
    "Dress_CeilingLight": 30, "Light_Bath1_Dry_Spot": 30, "Light_Bath1_Shower": 25,
    "Light_Bath1_Wet_Spot": 30, "Light_Dining_Pendant_1": 14, "Light_Dining_Pendant_2": 14,
    "Light_Foyer_Spot": 20, "Light_Kitchen_Spot_1": 24, "Light_Kitchen_Spot_2": 24,
    "Light_Kitchen_Spot_3": 24, "Light_Kitchen_Spot_4": 24, "Light_Living_Warm": 70,
    "Light_Master_Warm": 55, "Light_Sink_Task": 28, "PBR_Down_Bath1": 20,
    "PBR_Down_Bath2": 20, "PBR_Fill_Corridor": 12, "PBR_Fill_MasterBed": 12,
    "Q2_SconceLight": 6, "Q2_PendantLightS": 8, "Q2_PendantLightN": 8,
}
for name, e in ENERGY.items():
    o = bpy.data.objects.get(name)
    if o:
        o.data.energy = e
sun = bpy.data.objects.get("Sun_Natural")
if sun:
    sun.data.energy = 4.5
    sun.data.angle = 2.5
w = bpy.context.scene.world
if w and w.use_nodes:
    for n in w.node_tree.nodes:
        if n.type == 'MAP_RANGE':
            n.inputs["To Min"].default_value = 0.55
            n.inputs["To Max"].default_value = 0.85
print("[Q2b] lighting restored")

# ---- 2. walls / artwall lighter + desaturated, larger artwall tiles ----
build_pbr("Mat_Wall_Interior", "beige_wall_001", 2.5, value=1.45, normal_strength=0.3, ao_fac=0.18)
build_pbr("Mat_Wall_Cap", "beige_wall_001", 2.5, value=1.40, normal_strength=0.3, ao_fac=0.18)
for mname in ("Mat_Wall_Interior", "Mat_Wall_Cap"):
    for n in bpy.data.materials[mname].node_tree.nodes:
        if n.type == 'HUE_SAT':
            n.inputs["Saturation"].default_value = 0.55
build_artwall()
for n in bpy.data.materials["Mat_ArtWall_Tile"].node_tree.nodes:
    if n.type == 'HUE_SAT':
        n.inputs["Value"].default_value = 1.28
        n.inputs["Saturation"].default_value = 0.5
    if n.type == 'TEX_BRICK':
        n.inputs["Scale"].default_value = 0.85
        n.inputs["Mortar Size"].default_value = 0.004

# ---- 3. procedural white Carrara marble (repo has only beige marble) ----
def white_marble(mat_name):
    mat = bpy.data.materials.get(mat_name) or bpy.data.materials.new(mat_name)
    mat.use_nodes = True
    nt = mat.node_tree; nt.nodes.clear()
    nodes, links = nt.nodes, nt.links
    tex = nodes.new("ShaderNodeTexCoord"); tex.location = (-1000, 0)
    mapping = nodes.new("ShaderNodeMapping"); mapping.location = (-820, 0)
    mapping.inputs["Scale"].default_value = (0.6, 0.6, 0.6)
    links.new(tex.outputs["Object"], mapping.inputs["Vector"])
    noise = nodes.new("ShaderNodeTexNoise"); noise.location = (-620, 120)
    noise.inputs["Scale"].default_value = 2.2
    noise.inputs["Detail"].default_value = 6.0
    noise.inputs["Roughness"].default_value = 0.75
    links.new(mapping.outputs["Vector"], noise.inputs["Vector"])
    ramp = nodes.new("ShaderNodeValToRGB"); ramp.location = (-380, 120)
    ramp.color_ramp.elements[0].position = 0.42
    ramp.color_ramp.elements[0].color = (0.92, 0.92, 0.91, 1)
    ramp.color_ramp.elements[1].position = 0.52
    ramp.color_ramp.elements[1].color = (0.45, 0.47, 0.50, 1)
    el = ramp.color_ramp.elements.new(0.60)
    el.color = (0.88, 0.88, 0.87, 1)
    links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    bsdf = nodes.new("ShaderNodeBsdfPrincipled"); bsdf.location = (0, 0)
    bsdf.inputs["Roughness"].default_value = 0.14
    bsdf.inputs["Specular IOR Level"].default_value = 0.55
    links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    bump = nodes.new("ShaderNodeBump"); bump.location = (-150, -220)
    bump.inputs["Strength"].default_value = 0.06
    bump.inputs["Distance"].default_value = 0.02
    links.new(noise.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    out = nodes.new("ShaderNodeOutputMaterial"); out.location = (260, 0)
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    print(f"[Q2b] white marble -> {mat_name}")
    return mat

white_marble("Mat_Marble_White")
white_marble("Mat_Countertop_Granite")

# ---- 4. fabrics: subtler pattern on large surfaces ----
build_pbr("Mat_Q2_WallPanel", "fabric_pattern_07", 3.0, flat="#DCD4C4", sheen=0.35, normal_strength=0.18, ao_fac=0.08)
build_pbr("Mat_Q2_Boucle", "fabric_pattern_07", 1.2, flat="#D8CCB8", sheen=0.6, normal_strength=0.3, ao_fac=0.12)
build_pbr("Mat_Bed_Linen", "fabric_pattern_07", 1.4, flat="#F4F1EC", sheen=0.45, normal_strength=0.22, ao_fac=0.08)
build_pbr("Mat_Curtain", "fabric_pattern_07", 1.6, flat="#CCC4B6", sheen=0.6, normal_strength=0.3, ao_fac=0.15)
build_pbr("Mat_Q2_Lilac", "fabric_pattern_07", 1.2, flat="#BDB2D4", sheen=0.45, normal_strength=0.3, ao_fac=0.12)

# ---- 5. north landscape facing + no shadow blocking from cards/sheers ----
north = bpy.data.objects.get("Q2_Landscape_North")
if north:
    north.rotation_euler = (math.pi / 2, 0, 0)
for n in ("Q2_Landscape_South", "Q2_Landscape_North",
          "Q2_Sheer_LivingL", "Q2_Sheer_LivingR", "Q2_Sheer_MasterL", "Q2_Sheer_MasterR"):
    o = bpy.data.objects.get(n)
    if o:
        o.visible_shadow = False

# ---- 6. master bedding arrangement ----
throw = bpy.data.objects.get("Q2_Master_Throw")
if throw:
    bpy.data.objects.remove(throw, do_unlink=True)
for pname, yy in (("Bed_Master_Pillow1", 2.60), ("Bed_Master_Pillow2", 3.60)):
    p = bpy.data.objects.get(pname)
    if p:
        p.location = (1.06, yy, 0.76)
        p.rotation_euler = (0, -0.60, 0)
for cname, yy in (("Q2_Master_CushionS", 2.60), ("Q2_Master_CushionN", 3.60)):
    c = bpy.data.objects.get(cname)
    if c:
        c.location = (1.38, yy, 0.72)
        c.dimensions = (0.12, 0.44, 0.32)
        c.rotation_euler = (0, -0.50, 0)

# ---- 7. chair legs to brushed steel, sconce mount, leaf flatten ----
steel = bpy.data.materials.get("Mat_Steel_Brushed")
for o in bpy.data.objects:
    if o.name.startswith("Chair_") and ("_Leg" in o.name or "_Post" in o.name):
        _link(o, steel)
    if "_Leaf" in o.name and o.name.startswith("Q2_"):
        o.scale.z = 0.55
box("Q2_SconceMount", (4.46, 4.62, 1.88), (0.04, 0.07, 0.20),
    bpy.data.materials["Mat_Q2_Brass"], bevel=0.008)

bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT, "apt_84a_photoreal_tour.blend"))
print("[Q2b] SAVED")
