"""Q5 alpha-room review; changes cameras/display only, never saves the model."""
import os
import sys
import bpy
from mathutils import Vector

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
utility = '--utility' in sys.argv
scene = bpy.context.scene
scene.render.resolution_x = 1100
scene.render.resolution_y = 825
scene.render.resolution_percentage = 100


def shot(location, target, filename, ortho=None):
    data = bpy.data.cameras.new('Q5_ReviewCamera')
    camera = bpy.data.objects.new(data.name, data)
    scene.collection.objects.link(camera)
    camera.location = location
    camera.rotation_euler = (Vector(target) - camera.location).to_track_quat('-Z', 'Y').to_euler()
    data.lens = 20
    if ortho:
        data.type = 'ORTHO'
        data.ortho_scale = ortho
    scene.camera = camera
    scene.render.filepath = os.path.join(ROOT, 'renders', 'review', filename)
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(camera, do_unlink=True)
    bpy.data.cameras.remove(data)


scene.render.engine = 'BLENDER_WORKBENCH'
scene.display.shading.light = 'STUDIO'
scene.display.shading.color_type = 'MATERIAL'
scene.display.shading.show_shadows = True
scene.display.shading.show_cavity = True
hidden = [o for o in bpy.data.objects if o.type == 'MESH' and not o.hide_render and (
    o.name == 'Ceiling_Slab' or o.name.startswith(('Cove_', 'Q2_Landscape'))
    or 'Header' in o.name or o.name.endswith(('_Head', '_Headrail')))]
for obj in hidden:
    obj.hide_render = True
if utility:
    shot((9.42, 8.65, 10), (9.42, 8.65, 0), 'render_18_utility_plan.png', ortho=3.4)
else:
    shot((8.4, 7.0, 10), (8.4, 7.0, 0), 'render_16_alpha_plan.png', ortho=7.0)
for obj in hidden:
    obj.hide_render = False

scene.render.engine = 'CYCLES'
scene.cycles.samples = 48
scene.cycles.use_denoising = True
scene.cycles.denoiser = 'OPENIMAGEDENOISE'
scene.cycles.use_adaptive_sampling = True
scene.cycles.adaptive_threshold = 0.025
scene.view_settings.exposure = 0.35
# Review-only fill: this enclosed room has no direct window light.
light_data = bpy.data.lights.new('Q5_ReviewFill', 'AREA')
light_data.energy = 80
light_data.shape = 'DISK'
light_data.size = 1.5
light = bpy.data.objects.new(light_data.name, light_data)
scene.collection.objects.link(light)
light.location = (9.4, 8.65, 2.15) if utility else (9.2, 6.8, 2.15)
if utility:
    shot((9.42, 8.36, 1.55), (9.25, 9.35, 1.15), 'render_19_utility_pov.png')
else:
    shot((9.85, 5.98, 1.58), (8.65, 7.70, 1.15), 'render_17_alpha_pov.png')
print('Q5 REVIEW RENDERS DONE', flush=True)
