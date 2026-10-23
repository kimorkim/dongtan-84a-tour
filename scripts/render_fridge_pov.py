"""Render fridge-run POV + sink-side utility door POV (Q3/Q18 check)."""
from pathlib import Path
from shutil import copyfile
import bpy
import os
from mathutils import Vector

ROOT = Path(__file__).resolve().parent.parent
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 32
scene.cycles.use_denoising = True
scene.cycles.denoiser = 'OPENIMAGEDENOISE'
scene.cycles.use_adaptive_sampling = True
scene.cycles.adaptive_threshold = 0.02
scene.cycles.device = 'CPU'
scene.render.use_persistent_data = True
scene.render.resolution_x = 1280
scene.render.resolution_y = 960
scene.render.resolution_percentage = 100
scene.view_settings.exposure = 0.25


def shot(name, loc, target, filename, lens=24):
    cam_data = bpy.data.cameras.new(name)
    cam = bpy.data.objects.new(name, cam_data)
    bpy.context.collection.objects.link(cam)
    cam.location = loc
    direction = Vector(target) - Vector(loc)
    cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    cam.data.lens = lens
    scene.camera = cam
    out_path = str(ROOT / "renders" / "review" / filename)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    scene.render.filepath = out_path
    print(f"Rendering {filename} ...")
    bpy.ops.render.render(write_still=True)
    print(f"Saved: {out_path}")
    bpy.data.objects.remove(cam, do_unlink=True)
    bpy.data.cameras.remove(cam_data)


shot("Cam_Fridge_POV2", (6.50, 7.15, 1.48), (4.80, 7.05, 1.22),
     "render_11_fridge_pov.png", lens=21)
shot("Cam_SinkDoor_POV", (6.78, 8.78, 1.55), (4.85, 8.60, 1.22),
     "render_12_sink_door_pov.png", lens=26)
copyfile(ROOT / "renders/review/render_11_fridge_pov.png",
         ROOT / "renders/presentation/render_6_kitchen_reverse.png")
print("Q3/Q18 POV RENDERS DONE")
