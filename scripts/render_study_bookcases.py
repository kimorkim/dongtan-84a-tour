"""Q13 review: show the joined cases and preserve the two existing workstation views."""
from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parent.parent
sc=bpy.context.scene
sc.render.engine='CYCLES'; sc.cycles.samples=24; sc.cycles.use_denoising=True
sc.cycles.denoiser='OPENIMAGEDENOISE'; sc.cycles.use_adaptive_sampling=True
prefs=bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type='OPTIX'; prefs.get_devices()
for d in prefs.devices: d.use=d.type=='OPTIX'
assert any(d.use for d in prefs.devices)
sc.cycles.device='GPU'; sc.render.use_persistent_data=True
sc.render.resolution_x=1100; sc.render.resolution_y=900; sc.render.resolution_percentage=100
sc.view_settings.exposure=.15

def shot(loc,target,file,lens=20,ortho=None):
    d=bpy.data.cameras.new('Q13_Review'); c=bpy.data.objects.new(d.name,d); sc.collection.objects.link(c)
    c.location=loc; c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler()
    d.lens=lens
    if ortho: d.type='ORTHO'; d.ortho_scale=ortho
    sc.camera=c; sc.render.filepath=str(ROOT/'renders/review'/file)
    print('Q13 RENDER',file,flush=True); bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(c,do_unlink=True); bpy.data.cameras.remove(d)

shot((10.65,3.65,1.55),(9.2,2.0,1.05),'render_37_study_bookcases.png',22)
shot((10.3,1.15,1.55),(10.35,3.0,1.0),'render_33_study_pov.png',18)
shot((9.55,1.3,1.55),(11.1,3.32,.82),'render_35_study_desks.png',19)
for o in bpy.data.objects:
    if o.name.startswith(('Ceiling_','Cove_','Q11_Ceiling')): o.hide_render=True
shot((10.425,2.625,8),(10.425,2.625,0),'render_34_study_plan.png',ortho=4.5)
print('Q13 REVIEW DONE; master not saved',flush=True)
