"""Render fridge-run POV + sink-side utility door POV (Q3 check)."""
import bpy
import os
from mathutils import Vector

scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 64
scene.cycles.use_denoising = True
try:
    scene.cycles.denoiser = 'OPTIX'
except Exception:
    scene.cycles.denoiser = 'OPENIMAGEDENOISE'
scene.cycles.use_adaptive_sampling = True
scene.cycles.adaptive_threshold = 0.02
scene.render.resolution_x = 1280
scene.render.resolution_y = 960
scene.render.resolution_percentage = 100
scene.view_settings.exposure = 0.35


def shot(name, loc, target, filename, lens=28):
    cam_data = bpy.data.cameras.new(name)
    cam = bpy.data.objects.new(name, cam_data)
    bpy.context.collection.objects.link(cam)
    cam.location = loc
    direction = Vector(target) - Vector(loc)
    cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    cam.data.lens = lens
    scene.camera = cam
    out_path = os.path.abspath(os.path.join("renders", "review", filename))
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    scene.render.filepath = out_path
    print(f"Rendering {filename} ...")
    bpy.ops.render.render(write_still=True)
    print(f"Saved: {out_path}")
    bpy.data.objects.remove(cam, do_unlink=True)


shot("Cam_Fridge_POV2", (7.55, 5.95, 1.55), (4.8, 7.35, 1.05),
     "render_11_fridge_pov.png")
shot("Cam_SinkDoor_POV", (6.9, 8.72, 1.55), (4.95, 8.68, 1.05),
     "render_12_sink_door_pov.png")
print("Q3 POV RENDERS DONE")
