"""Render Q12 gallery from the saved master; never save review settings."""
import os
import sys
from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'scripts'))
from plan_dimensions import point
sc=bpy.context.scene
sc.render.engine='CYCLES'; sc.cycles.samples=24; sc.cycles.use_denoising=True
prefs=bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type='OPTIX'; prefs.get_devices()
for device in prefs.devices: device.use=device.type=='OPTIX'
assert any(d.use for d in prefs.devices),'OPTIX GPU unavailable'
sc.cycles.device='GPU'
sc.render.use_persistent_data=True
sc.cycles.denoiser='OPENIMAGEDENOISE'; sc.cycles.use_adaptive_sampling=True
sc.render.threads_mode='FIXED'; sc.render.threads=12
sc.render.resolution_x=1100; sc.render.resolution_y=900; sc.render.resolution_percentage=100
sc.view_settings.exposure=.15
batch=globals().get('RENDER_BATCH')

def shot(loc,target,path,lens=22,ortho=None):
    if batch is not None and Path(path).name not in batch: return
    d=bpy.data.cameras.new('Q12_ReviewCamera'); c=bpy.data.objects.new(d.name,d)
    sc.collection.objects.link(c)
    c.location=(*point(*loc[:2]),loc[2]); target=Vector((*point(*target[:2]),target[2]))
    c.rotation_euler=(target-c.location).to_track_quat('-Z','Y').to_euler()
    d.lens=lens
    if ortho: d.type='ORTHO'; d.ortho_scale=ortho
    sc.camera=c; sc.render.filepath=str(ROOT/path)
    print('Q12 RENDER',path,flush=True); bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(c,do_unlink=True); bpy.data.cameras.remove(d)

views=[
((9.55,4.,1.58),(11.12,2.25,.85),'renders/review/render_33_study_pov.png',19),
((9.64,1.16,1.55),(11.2,3.23,.82),'renders/review/render_35_study_desks.png',19),
((12.55,3.85,1.55),(13.65,1.8,.85),'renders/review/render_30_yuna_pov.png',19),
((13.55,1.2,1.45),(13.55,3.65,1.15),'renders/review/render_32_yuna_basic_builtin.png',19),
((12.42,4.82,1.58),(11.95,6.7,1.18),'renders/review/render_23_foyer_open.png',20),
((12.4,6.73,1.58),(10.65,6.73,1.12),'renders/review/render_22_entry_pantry.png',18),
((7.55,5.95,1.55),(4.8,7.35,1.05),'renders/review/render_11_fridge_pov.png',28),
((6.9,8.72,1.55),(4.95,8.68,1.05),'renders/review/render_12_sink_door_pov.png',28),
((3.42,3.35,1.6),(2.78,.7,1.05),'renders/review/render_14_master_balcony_pov.png',22),
((13.4,5.04,1.53),(14.88,5.,1.2),'renders/review/render_25_dry_vanity_detail.png',23),
((13.82,5.88,1.55),(14.65,6.35,.95),'renders/review/render_26_common_toilet_detail.png',18),
((9.4,7.4,1.5),(9.3,8.85,1.05),'renders/review/render_19_utility_pov.png',20),
]
for args in views: shot(*args)
for name,path in [
('Cam_Living_POV','renders/review/render_29_oak_living.png'),
('Cam_Kitchen_POV','renders/presentation/render_3_kitchen_dining_pov.png'),
('Cam_Kitchen_Prep_POV','renders/presentation/render_9_kitchen_prep_pov.png'),
('Cam_MasterBed_POV','renders/presentation/render_4_master_bedroom_pov.png'),
('Cam_Dress_POV','renders/presentation/render_7_dress_pov.png')]:
    if batch is not None and Path(path).name not in batch: continue
    fill=None
    if name=='Cam_Dress_POV':
        data=bpy.data.lights.new('Q12_ReviewDressFill','AREA'); data.energy=90; data.shape='DISK'; data.size=1.2
        fill=bpy.data.objects.new(data.name,data); sc.collection.objects.link(fill)
        fill.location=(*point(1.5,8.2),2.25)
    sc.camera=bpy.data.objects[name]; sc.render.filepath=str(ROOT/path)
    print('Q12 RENDER',path,flush=True); bpy.ops.render.render(write_still=True)
    if fill:
        bpy.data.objects.remove(fill,do_unlink=True); bpy.data.lights.remove(data)
for o in bpy.data.objects:
    if o.name.startswith(('Ceiling_','Cove_','ProK_CeilStrip','Q10_Ceiling','Q11_Ceiling','Q2_Landscape')):
        o.hide_render=True
shot((10.52,2.53,8),(10.52,2.53,0),'renders/review/render_34_study_plan.png',ortho=4.5)
shot((13.45,2.35,8),(13.45,2.35,0),'renders/review/render_31_yuna_plan.png',ortho=4.6)
shot((9.25,8.7,8),(9.25,8.7,0),'renders/review/render_18_utility_plan.png',ortho=2.5)
print('Q12 CURRENT GALLERY DONE; master not saved',flush=True)
