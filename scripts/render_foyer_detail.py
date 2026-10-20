"""Q7 review renders. Closed middle-door shot is a temporary inspection pose."""
import os
import bpy
from mathutils import Vector

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
scene = bpy.context.scene
scene.render.resolution_x = 1100
scene.render.resolution_y = 825
scene.render.resolution_percentage = 100


def shot(location, target, filename, lens=20, ortho=None):
    data = bpy.data.cameras.new('Q7_ReviewCamera')
    camera = bpy.data.objects.new(data.name, data)
    scene.collection.objects.link(camera)
    camera.location = location
    camera.rotation_euler = (Vector(target)-camera.location).to_track_quat('-Z', 'Y').to_euler()
    data.lens = lens
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
    or 'Header' in o.name or o.name.endswith(('_Head', '_Headrail'))
    or o.name in ('Q7_MiddleDoor_Rail', 'Q7_MiddleDoor_RailGroove'))]
for obj in hidden:
    obj.hide_render = True
shot((11.85, 6.65, 10), (11.85, 6.65, 0), 'render_20_foyer_plan.png', ortho=4.7)
for obj in hidden:
    obj.hide_render = False
scene.render.engine = 'CYCLES'
scene.cycles.samples = 48
scene.cycles.use_denoising = True
scene.cycles.denoiser = 'OPENIMAGEDENOISE'
scene.cycles.use_adaptive_sampling = True
scene.cycles.adaptive_threshold = 0.025
scene.view_settings.exposure = 0.35

# Only for the material/detail comparison: restore the open pose immediately afterwards.
panels = [o for o in bpy.data.objects if o.name.startswith('Q7_MiddleDoor_Leaf')
          or o.name == 'Q7_MiddleDoor_Glass']
for obj in panels:
    obj.location.x += 1.11
shot((12.33, 7.25, 1.58), (12.33, 5.63, 1.25), 'render_21_middle_door_detail.png', lens=19)
for obj in panels:
    obj.location.x -= 1.11
shot((12.40, 6.73, 1.58), (10.65, 6.73, 1.12), 'render_22_entry_pantry.png', lens=18)
shot((12.42, 4.82, 1.58), (11.95, 6.70, 1.18), 'render_23_foyer_open.png', lens=20)
print('Q7 REVIEW RENDERS DONE; model not saved', flush=True)
