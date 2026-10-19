"""Daylight + interior fill tuning (idempotent). Run inside Blender."""
import bpy

scene = bpy.context.scene

# --- existing lights report + sun boost ---
for o in bpy.data.objects:
    if o.type == "LIGHT":
        d = o.data
        print(f"[LIT] {o.name} type={d.type} energy={getattr(d, 'energy', '?')} "
              f"color={tuple(round(c, 3) for c in d.color)}")
sun = bpy.data.objects.get("Light_Sun")
if sun and sun.type == "LIGHT":
    print(f"[LIT] sun energy {sun.data.energy} -> 4.0")
    sun.data.energy = 4.0

# --- HDRI strength (MapRange: light rays dim, camera rays bright) ---
w = scene.world
if w and w.use_nodes:
    for n in w.node_tree.nodes:
        if n.type == "MAP_RANGE":
            n.inputs["To Min"].default_value = 0.6
            n.inputs["To Max"].default_value = 0.85
            print("[LIT] HDRI MapRange -> light-fill 0.6 / camera-sky 0.85")

# --- exposure ---
vs = scene.view_settings
print(f"[LIT] view={vs.view_transform} look={vs.look} exposure={vs.exposure} -> 0.4")
vs.exposure = 0.4

# --- dress room ceiling light boost (POV verified dark) ---
dress = bpy.data.objects.get("Dress_CeilingLight")
if dress and dress.type == "LIGHT":
    dress.data.energy = 30.0
    if dress.location.z > 2.25:
        dress.location.z = 2.10
    print(f"[LIT] Dress_CeilingLight -> 30W @ z={dress.location.z:.2f}")

# --- downlights / fills (recreate idempotently) ---
SPOTS = [
    ("PBR_Down_Bath1", (14.20, 6.65, 2.10), 25.0),
    ("PBR_Down_Bath2", (3.45, 6.90, 2.10), 25.0),
    ("PBR_Fill_Foyer", (12.55, 8.80, 2.10), 20.0),
    ("PBR_Fill_Corridor", (9.90, 8.80, 2.10), 15.0),
    ("PBR_Fill_MasterBed", (2.40, 3.50, 2.10), 15.0),
]
mw = bpy.data.objects.get("Light_Master_Warm")
if mw and mw.type == "LIGHT":
    print(f"[LIT] Light_Master_Warm {mw.data.energy} -> 120W")
    mw.data.energy = 120.0
for name, loc, energy in SPOTS:
    old = bpy.data.objects.get(name)
    if old:
        bpy.data.objects.remove(old, do_unlink=True)
        if name in bpy.data.lights:
            bpy.data.lights.remove(bpy.data.lights[name])
    ld = bpy.data.lights.new(name, "POINT")
    ld.energy = energy
    ld.color = (1.0, 0.95, 0.88)
    ld.shadow_soft_size = 0.05
    o = bpy.data.objects.new(name, ld)
    o.location = loc
    scene.collection.objects.link(o)
    print(f"[LIT] added {name} @ {loc} {energy}W")
print("[LIT] DONE")
