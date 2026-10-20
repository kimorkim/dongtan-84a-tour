"""Q10 review renders of the saved room, without changing the master file."""
import os
import bpy
from mathutils import Vector

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sc = bpy.context.scene
sc.render.engine = 'CYCLES'
sc.cycles.samples = 24
sc.render.threads_mode = 'FIXED'
sc.render.threads = 12
sc.cycles.use_denoising = True
sc.cycles.use_adaptive_sampling = True
sc.render.resolution_x = 1100
sc.render.resolution_y = 1000
sc.render.resolution_percentage = 100
sc.view_settings.exposure = .15

def shot(location, target, filename, lens=22, ortho=None):
    data = bpy.data.cameras.new('Q10_ReviewCamera')
    camera = bpy.data.objects.new(data.name,data)
    sc.collection.objects.link(camera)
    camera.location = location
    camera.rotation_euler = (Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
    data.lens = lens
    if ortho:
        data.type = 'ORTHO'
        data.ortho_scale = ortho
    sc.camera = camera
    sc.render.filepath = os.path.join(ROOT,'renders/review',filename)
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(camera,do_unlink=True)
    bpy.data.cameras.remove(data)

shot((12.55,3.85,1.55),(13.65,1.8,.85),'render_30_yuna_pov.png',19)
shot((13.55,1.20,1.45),(13.55,3.65,1.15),'render_32_yuna_basic_builtin.png',19)
for obj in bpy.data.objects:
    if obj.name.startswith(('Ceiling_', 'Q10_Ceiling', 'Q10_RoomLight')):
        obj.hide_render = True
shot((13.45,2.35,8),(13.45,2.35,0),'render_31_yuna_plan.png',ortho=4.6)
print('Q10 REVIEW RENDERS DONE; model not saved',flush=True)
