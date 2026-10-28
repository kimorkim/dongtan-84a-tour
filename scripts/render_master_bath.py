"""Q24 reference-aligned views; all render settings remain temporary."""
from pathlib import Path
import os,runpy
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parent.parent
sc=bpy.context.scene
sc.render.engine='CYCLES';sc.cycles.device='CPU';sc.cycles.samples=40;sc.cycles.use_denoising=True
sc.render.threads_mode='FIXED';sc.render.threads=12;sc.render.use_persistent_data=True
sc.render.resolution_x=1100;sc.render.resolution_y=900;sc.render.resolution_percentage=100
sc.view_settings.exposure=.15
batch=set(os.environ['RENDER_BATCH'].split(',')) if os.environ.get('RENDER_BATCH') else None
def path(relative):
    out=Path(os.environ['RENDER_DIR'])/Path(relative).name if os.environ.get('RENDER_DIR') else ROOT/relative
    out.parent.mkdir(parents=True,exist_ok=True);return out
def shot(loc,target,relative,lens=21,ortho=None):
    if batch is not None and Path(relative).name not in batch:return
    data=bpy.data.cameras.new('Q24_ReviewCamera');o=bpy.data.objects.new(data.name,data);sc.collection.objects.link(o)
    o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
    data.lens=lens;data.clip_start=.03
    if ortho:data.type='ORTHO';data.ortho_scale=ortho
    sc.camera=o;sc.render.filepath=str(path(relative))
    print('Q24 RENDER',sc.render.filepath,flush=True);bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(o,do_unlink=True);bpy.data.cameras.remove(data)
data=bpy.data.lights.new('Q24_ReviewFill','AREA');data.energy=18;data.size=1.0
o=bpy.data.objects.new(data.name,data);sc.collection.objects.link(o);o.location=(3.1,6.9,2.2);o.visible_glossy=False
shot((2.73,6.50,1.50),(3.99,6.87,1.12),'renders/review/render_54_master_bath_entry.png',18)
shot((2.91,6.83,1.53),(3.53,7.81,1.20),'renders/review/render_55_master_bath_tub.png',20)
for o in bpy.data.objects:
    if o.name.startswith(('Ceiling_','Cove_','Q10_Ceiling','Q11_Ceiling','Q24_Ceiling','Q24_AccessPanel','Q24_Vent','Q24_Downlight')) or o.name in ('Ground_Presentation',):o.hide_render=True
sc.render.engine='BLENDER_WORKBENCH';sc.display.shading.light='STUDIO';sc.display.shading.color_type='MATERIAL'
sc.display.shading.show_shadows=True;sc.display.shading.show_cavity=True
shot((3.04,7.1,10),(3.04,7.1,0),'renders/review/render_56_master_bath_plan.png',ortho=3.65)
if not os.environ.get('RENDER_DIR') and (batch is None or 'render_36_dimensioned_plan.png' in batch):
    runpy.run_path(str(ROOT/'scripts/render_dimensions.py'),run_name='__main__')
print('Q24 reviews complete; source not saved',flush=True)
