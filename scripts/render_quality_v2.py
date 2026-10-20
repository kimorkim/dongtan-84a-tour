"""Render Q2 views. Namespaces: RENDER_BATCH, PREVIEW, RENDER_DIR like before,
but WITHOUT the old double-sun/exposure overrides."""
import bpy
import os

ALL_VIEWS = [
    ("Cam_Photoreal_Topdown", "render_1_isometric_topdown.png", True),
    ("Cam_Living_POV", "render_2_living_room_pov.png", False),
    ("Cam_Kitchen_POV", "render_3_kitchen_dining_pov.png", False),
    ("Cam_MasterBed_POV", "render_4_master_bedroom_pov.png", False),
]
batch = globals().get("RENDER_BATCH", None)
preview = globals().get("PREVIEW", False)
render_dir = globals().get("RENDER_DIR") or os.path.abspath("renders/presentation")
os.makedirs(render_dir, exist_ok=True)
views = [v for v in ALL_VIEWS if (batch is None or v[1] in batch)]
print(f"Q2 render batch: {[v[1] for v in views]} preview={preview} dir={render_dir}")

scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 32 if preview else 180
scene.cycles.use_denoising = True
try:
    scene.cycles.denoiser = 'OPTIX'
except Exception:
    scene.cycles.denoiser = 'OPENIMAGEDENOISE'
scene.cycles.use_adaptive_sampling = True
scene.cycles.adaptive_threshold = 0.02 if preview else 0.01
if preview:
    scene.render.resolution_x = 960
    scene.render.resolution_y = 720
else:
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 1200
scene.render.resolution_percentage = 100

ceil = [o for o in bpy.data.objects
        if o.name == "Ceiling_Slab" or o.name.startswith("Cove_Living_")
        or o.name.startswith("ProK_CeilStrip")]
# landscape cards are for POV windows only; from above they read as a solid bar
cards = [o for o in bpy.data.objects if o.name.startswith("Q2_Landscape_")]
for cam_name, filename, hide_ceiling in views:
    cam = bpy.data.objects.get(cam_name)
    if cam is None:
        print(f"SKIP {filename}: {cam_name} missing")
        continue
    for co in ceil:
        co.hide_render = hide_ceiling
    for co in cards:
        co.hide_render = hide_ceiling
    scene.view_settings.exposure = 0.15 if hide_ceiling else 0.35
    scene.camera = cam
    out_path = os.path.join(render_dir, filename)
    scene.render.filepath = out_path
    print(f"Rendering {filename} hide_ceiling={hide_ceiling} ...")
    bpy.ops.render.render(write_still=True)
    print(f"Saved: {out_path}")
print("Q2 RENDER DONE")
