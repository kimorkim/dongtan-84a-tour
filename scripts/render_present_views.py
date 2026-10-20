"""HQ presentation renders for 84A photoreal tour (8 views).

Batch control: define RENDER_BATCH (list of filenames) in the exec namespace
before this code to render a subset; otherwise all views render.
"""
import bpy
import os

ALL_VIEWS = [
    ("Cam_Photoreal_Topdown", "render_1_isometric_topdown.png", True),
    ("Cam_Living_POV", "render_2_living_room_pov.png", False),
    ("Cam_Kitchen_POV", "render_3_kitchen_dining_pov.png", False),
    ("Cam_MasterBed_POV", "render_4_master_bedroom_pov.png", False),
    ("Cam_Foyer_POV", "render_5_foyer_corridor_pov.png", False),
    ("Cam_Kitchen_Reverse", "render_6_kitchen_reverse.png", False),
    ("Cam_Dress_POV", "render_7_dress_pov.png", False),
    ("Cam_Bath_POV", "render_8_bath_pov.png", False),
    ("Cam_Kitchen_Prep_POV", "render_9_kitchen_prep_pov.png", False),
    ("Cam_CommonBath_POV", "render_10_common_bath_dry_vanity_pov.png", False),
]

batch = globals().get("RENDER_BATCH", None)
preview = globals().get("PREVIEW", False)
render_dir = globals().get("RENDER_DIR") or os.path.abspath("renders/presentation")
os.makedirs(render_dir, exist_ok=True)
views = [v for v in ALL_VIEWS if (batch is None or v[1] in batch)]
print(f"HQ render batch: {[v[1] for v in views]} (preview={preview})")

scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 32 if preview else 180
scene.cycles.use_denoising = True
scene.cycles.denoiser = 'OPTIX'
if preview:
    scene.render.resolution_x = 960
    scene.render.resolution_y = 720
else:
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 1200
scene.render.resolution_percentage = 100

ceil_elements = [
    o for o in bpy.data.objects
    if o.name == "Ceiling_Slab" or o.name.startswith("Cove_Living_") or o.name.startswith("ProK_CeilStrip")
]
for cam_name, filename, hide_ceiling in views:
    cam = bpy.data.objects.get(cam_name)
    if cam is None:
        print(f"SKIP {filename}: camera {cam_name} missing")
        continue
    for co in ceil_elements:
        co.hide_render = hide_ceiling
    for ln in ("Light_Sun", "Sun_Natural", "Light"):
        lo = bpy.data.objects.get(ln)
        if lo is not None:
            lo.hide_render = False
    # dollhouse view gets a soft sun rig; POVs get full daylight punch
    sun_rig = {"Light_Sun": 1.2, "Sun_Natural": 1.2} if hide_ceiling \
        else {"Light_Sun": 4.0, "Sun_Natural": 4.2}
    for ln, e in sun_rig.items():
        lo = bpy.data.objects.get(ln)
        if lo is not None:
            lo.data.energy = e
    scene.view_settings.exposure = -0.2 if hide_ceiling else 0.4
    scene.camera = cam
    out_path = os.path.join(render_dir, filename)
    scene.render.filepath = out_path
    print(f"Rendering {filename} (hide_ceiling={hide_ceiling}) ...")
    bpy.ops.render.render(write_still=True)
    print(f"Saved: {out_path}")

bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath("apt_84a_photoreal_tour.blend"))
print("SUCCESS: HQ batch done, blend saved.")
