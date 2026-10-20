"""Q9 review: saved materials/lighting; no changes saved to the master model."""
import os
import bpy
from mathutils import Vector

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 32
scene.cycles.use_denoising = True
scene.cycles.denoiser = 'OPENIMAGEDENOISE'
scene.cycles.use_adaptive_sampling = True
scene.render.resolution_x = 1100
scene.render.resolution_y = 825
scene.render.resolution_percentage = 100
scene.view_settings.exposure = .15
for location,target,filename,lens in [
    ((12.70,5.05,1.50),(8.4,5.05,.65),'render_28_oak_corridor.png',22),
    ((8.10,4.70,1.35),(6.3,2.15,.30),'render_29_oak_living.png',22)]:
    data = bpy.data.cameras.new('Q9_ReviewCamera')
    camera = bpy.data.objects.new(data.name,data)
    scene.collection.objects.link(camera)
    camera.location = location
    camera.rotation_euler = (Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
    data.lens = lens
    scene.camera = camera
    scene.render.filepath = os.path.join(ROOT,'renders/review',filename)
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(camera,do_unlink=True)
    bpy.data.cameras.remove(data)
print('Q9 REVIEW RENDERS DONE; model not saved',flush=True)
