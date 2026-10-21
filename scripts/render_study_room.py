"""Review saved Q11 study; never save review camera/lighting to the master."""
import os
import bpy
from mathutils import Vector

ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sc=bpy.context.scene
sc.render.engine='CYCLES'; sc.cycles.samples=24; sc.cycles.use_denoising=True
sc.cycles.use_adaptive_sampling=True
sc.render.threads_mode='FIXED'; sc.render.threads=12
sc.render.resolution_x=1100; sc.render.resolution_y=1000; sc.render.resolution_percentage=100
sc.view_settings.exposure=.15
out=os.environ.get('RENDER_DIR',os.path.join(ROOT,'renders/review'))
os.makedirs(out,exist_ok=True)

def shot(loc,target,file,lens=19,ortho=None):
    data=bpy.data.cameras.new('Q11_ReviewCamera'); cam=bpy.data.objects.new(data.name,data)
    sc.collection.objects.link(cam); cam.location=loc
    cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
    data.lens=lens
    if ortho: data.type='ORTHO'; data.ortho_scale=ortho
    sc.camera=cam; sc.render.filepath=os.path.join(out,file)
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(cam,do_unlink=True); bpy.data.cameras.remove(data)

shot((9.55,4.00,1.58),(11.12,2.25,.85),'render_33_study_pov.png')
shot((9.64,1.16,1.55),(11.20,3.23,.82),'render_35_study_desks.png')
for obj in bpy.data.objects:
    if obj.name.startswith(('Ceiling_','Cove_','Q11_Ceiling')): obj.hide_render=True
shot((10.52,2.53,8),(10.52,2.53,0),'render_34_study_plan.png',ortho=4.3)
print('Q11 REVIEW RENDERS DONE; master not saved',flush=True)
