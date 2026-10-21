"""Q14 living-room views; review-only cameras do not change the saved master."""
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
cy=sc['Q14_sofa_centre_y']

def shot(loc,target,file,lens=22,ortho=None):
    d=bpy.data.cameras.new('Q14_Review'); o=bpy.data.objects.new(d.name,d); sc.collection.objects.link(o)
    o.location=loc; o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
    d.lens=lens
    if ortho: d.type='ORTHO'; d.ortho_scale=ortho
    sc.camera=o; sc.render.filepath=str(ROOT/'renders/review'/file)
    print('Q14 RENDER',file,flush=True); bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(o,do_unlink=True); bpy.data.cameras.remove(d)

shot((7.65,4.9,1.55),(6.45,.80,1.23),'render_40_living_window.png',23)
shot((7.65,4.7,1.5),(4.32,2.9,1.1),'render_41_living_artwall.png',22)
shot((6.25,1.1,1.5),(8.15,cy,.57),'render_38_brest_sofa.png',22)
shot((5.0,5.2,1.55),(7.75,2.7,.65),'render_29_oak_living.png',22)
for o in bpy.data.objects:
    if o.name.startswith(('Ceiling_','Cove_','Q2_Landscape')): o.hide_render=True
shot((6.55,3.2,9),(6.55,3.2,0),'render_39_brest_living_plan.png',ortho=5.3)
print('Q15 RENDERS DONE; master not saved',flush=True)
