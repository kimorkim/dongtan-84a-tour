"""Q8 review images; renders saved fixtures, does not save the model."""
import os
import bpy
from mathutils import Vector

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
scene = bpy.context.scene
scene.render.resolution_x = 1100
scene.render.resolution_y = 825
scene.render.resolution_percentage = 100

def shot(location, target, filename, lens=21, ortho=None):
    data = bpy.data.cameras.new('Q8_ReviewCamera')
    camera = bpy.data.objects.new(data.name, data)
    scene.collection.objects.link(camera)
    camera.location = location
    camera.rotation_euler = (Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
    data.lens = lens
    if ortho:
        data.type = 'ORTHO'
        data.ortho_scale = ortho
    scene.camera = camera
    scene.render.filepath = os.path.join(ROOT,'renders/review',filename)
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(camera,do_unlink=True)
    bpy.data.cameras.remove(data)

scene.render.engine = 'BLENDER_WORKBENCH'
scene.display.shading.light = 'STUDIO'
scene.display.shading.color_type = 'MATERIAL'
scene.display.shading.show_shadows = True
scene.display.shading.show_cavity = True
hidden = [o for o in bpy.data.objects if o.type == 'MESH' and not o.hide_render and (
    o.name == 'Ceiling_Slab' or o.name.startswith(('Cove_', 'Q2_Landscape', 'Q8_Ceiling_'))
    or 'Header' in o.name or o.name.endswith('_Head'))]
for obj in hidden:
    obj.hide_render = True
shot((14.2,6.0,10),(14.2,6.0,0),'render_24_common_bath_plan.png',ortho=3.8)
for obj in hidden:
    obj.hide_render = False
scene.render.engine = 'CYCLES'
scene.cycles.samples = 48
scene.cycles.use_denoising = True
scene.cycles.denoiser = 'OPENIMAGEDENOISE'
scene.cycles.use_adaptive_sampling = True
scene.view_settings.exposure = .15
shot((13.40,5.04,1.53),(14.88,5.0,1.20),'render_25_dry_vanity_detail.png',lens=23)
shot((13.82,5.88,1.55),(14.65,6.35,.95),'render_26_common_toilet_detail.png',lens=18)
shot((13.95,6.87,1.55),(14.40,7.20,1.30),'render_27_shower_detail.png',lens=18)
print('Q8 REVIEW RENDERS DONE; model not saved',flush=True)
