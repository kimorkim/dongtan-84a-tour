"""Q23 review images; never save temporary cameras or lighting."""
from pathlib import Path
import os
import runpy
import shutil
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parent.parent
sc = bpy.context.scene
sc.render.engine = 'CYCLES'
sc.cycles.samples = 32
sc.cycles.use_denoising = True
sc.cycles.device = 'CPU'
sc.render.threads_mode = 'FIXED'
sc.render.threads = 12
sc.render.resolution_x = 1100
sc.render.resolution_y = 900
sc.render.resolution_percentage = 100
sc.render.use_persistent_data = True
sc.view_settings.exposure = .15
batch = set(os.environ['RENDER_BATCH'].split(',')) if os.environ.get('RENDER_BATCH') else None

def output(relative):
    p = Path(os.environ['RENDER_DIR'])/Path(relative).name if os.environ.get('RENDER_DIR') else ROOT/relative
    p.parent.mkdir(parents=True,exist_ok=True)
    return p

def shot(loc,target,relative,lens=24,ortho=None):
    if batch is not None and Path(relative).name not in batch:
        return
    data = bpy.data.cameras.new('Q23_ReviewCamera')
    obj = bpy.data.objects.new(data.name,data); sc.collection.objects.link(obj)
    obj.location = loc
    obj.rotation_euler = (Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
    data.lens = lens; data.clip_start = .03
    if ortho:
        data.type = 'ORTHO'; data.ortho_scale = ortho
    sc.camera = obj; sc.render.filepath = str(output(relative))
    print('Q23 RENDER', relative, sc.cycles.device,flush=True)
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(obj,do_unlink=True); bpy.data.cameras.remove(data)

for y,energy in [(6.45,45),(8.8,55)]:
    data = bpy.data.lights.new('Q23_ReviewFill','AREA'); data.energy=energy; data.size=1.2
    obj = bpy.data.objects.new(data.name,data); sc.collection.objects.link(obj)
    obj.location = (1.5,y,2.22)
    obj.visible_glossy = False
shot((2.22,6.72,1.45),(.54,6.49,1.20),'renders/review/render_51_powder_vanity.png',20)
if batch is None or 'render_51_powder_vanity.png' in batch:
    shutil.copy2(output('renders/review/render_51_powder_vanity.png'),output('renders/presentation/render_7_dress_pov.png'))
shot((1.80,7.52,1.50),(1.45,9.40,1.10),'renders/review/render_52_dressroom_cleared.png',22)
for obj in bpy.data.objects:
    if obj.name.startswith(('Ceiling_','Cove_','Q10_Ceiling','Q11_Ceiling','Q24_Ceiling','Q24_AccessPanel','Q24_Vent','Q24_Downlight','Q2_Landscape')) or obj.name=='Ground_Presentation':
        obj.hide_render=True
sc.render.engine='BLENDER_WORKBENCH'
sc.display.shading.light='STUDIO'; sc.display.shading.color_type='MATERIAL'
sc.display.shading.show_shadows=True; sc.display.shading.show_cavity=True
shot((2.28,7.95,12),(2.28,7.95,0),'renders/review/render_53_dressroom_powder_plan.png',ortho=5.8)
if not os.environ.get('RENDER_DIR') and (batch is None or 'render_36_dimensioned_plan.png' in batch):
    runpy.run_path(str(ROOT/'scripts/render_dimensions.py'),run_name='__main__')
print('Q23 reviews complete; source unchanged',flush=True)
