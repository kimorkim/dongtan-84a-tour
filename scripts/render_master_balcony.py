"""Q4 balcony/refuge review images; does not save changes to the model."""
import os
import bpy
from mathutils import Vector

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out_dir = os.path.join(ROOT, 'renders', 'review')
os.makedirs(out_dir, exist_ok=True)
scene = bpy.context.scene
scene.render.resolution_x = 1100
scene.render.resolution_y = 825
scene.render.resolution_percentage = 100


def shot(name, location, target, filename, lens=24, ortho=None):
    data = bpy.data.cameras.new(name)
    camera = bpy.data.objects.new(name, data)
    scene.collection.objects.link(camera)
    camera.location = location
    camera.rotation_euler = (Vector(target)-camera.location).to_track_quat('-Z', 'Y').to_euler()
    data.lens = lens
    if ortho:
        data.type = 'ORTHO'
        data.ortho_scale = ortho
    scene.camera = camera
    scene.render.filepath = os.path.join(out_dir, filename)
    print('RENDERING', filename, flush=True)
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(camera, do_unlink=True)


# A quick plan review first; headers are lifted out of this diagnostic view only.
scene.render.engine = 'BLENDER_WORKBENCH'
scene.display.shading.light = 'STUDIO'
scene.display.shading.color_type = 'MATERIAL'
scene.display.shading.show_shadows = True
scene.display.shading.show_cavity = True
scene.display.shading.background_type = 'WORLD'
scene.world.color = (0.25, 0.25, 0.25)
hidden = []
for obj in bpy.data.objects:
    if obj.type == 'MESH' and not obj.hide_render and (
            obj.name == 'Ceiling_Slab' or obj.name.startswith(('Cove_', 'Q2_Landscape'))
            or 'Header' in obj.name or obj.name.endswith(('_Head', '_Headrail'))):
        hidden.append(obj)
        obj.hide_render = True
shot('Q4_Cam_Plan', (2.25, 1.50, 10), (2.25, 1.50, 0),
     'render_13_master_balcony_plan.png', ortho=4.8)
for obj in hidden:
    obj.hide_render = False

scene.render.engine = 'CYCLES'
scene.cycles.samples = 48
scene.cycles.use_denoising = True
scene.cycles.denoiser = 'OPENIMAGEDENOISE'
scene.cycles.use_adaptive_sampling = True
scene.cycles.adaptive_threshold = 0.025
scene.view_settings.exposure = 0.35
shot('Q4_Cam_Balcony', (3.42, 3.35, 1.60), (2.78, 0.70, 1.05),
     'render_14_master_balcony_pov.png', lens=22)
shot('Q4_Cam_Refuge', (3.68, 1.15, 1.55), (1.10, 1.05, 0.90),
     'render_15_refuge_pov.png', lens=20)
print('Q4 REVIEW RENDERS DONE', flush=True)
