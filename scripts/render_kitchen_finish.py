"""Q16 saved-master review views; no scene settings saved."""
from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parent.parent
sc=bpy.context.scene
sc.render.engine='CYCLES';sc.cycles.samples=32;sc.cycles.use_denoising=True
sc.cycles.denoiser='OPENIMAGEDENOISE';sc.cycles.use_adaptive_sampling=True
sc.cycles.device='CPU';sc.render.use_persistent_data=True
sc.render.resolution_x=1200;sc.render.resolution_y=960;sc.render.resolution_percentage=100
sc.view_settings.exposure=.15

def shot(loc,target,name,lens=20,ortho=None):
    d=bpy.data.cameras.new('Q16_Review');o=bpy.data.objects.new(d.name,d);sc.collection.objects.link(o)
    o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();d.lens=lens
    if ortho:d.type='ORTHO';d.ortho_scale=ortho
    sc.camera=o;sc.render.filepath=str(ROOT/'renders/review'/name)
    bpy.ops.render.render(write_still=True);bpy.data.objects.remove(o,do_unlink=True);bpy.data.cameras.remove(d)
shot((6.25,8.0,1.6),(6.25,9.75,1.15),'render_42_kitchen_sink.png',18)
shot((5.7,8.15,1.5),(6.8,9.3,1.12),'render_43_kitchen_corner.png',18)
shot((6.5,5.25,1.55),(6.25,9.3,1.10),'render_45_kitchen_dining.png',21)
shot((6.78,8.78,1.55),(4.85,8.80,1.05),'render_12_sink_door_pov.png',28)
# Keep the existing consumer paths current as well.
from shutil import copyfile
copyfile(ROOT/'renders/review/render_43_kitchen_corner.png',ROOT/'renders/presentation/render_9_kitchen_prep_pov.png')
copyfile(ROOT/'renders/review/render_45_kitchen_dining.png',ROOT/'renders/presentation/render_3_kitchen_dining_pov.png')
for o in bpy.data.objects:
    if o.name.startswith(('Ceiling_','Cove_','ProK_CeilStrip','Q2_Landscape','Kitchen_Upper_',
                          'ProK_UpperEast','Q16_Upper','ProK_Hood_','Downlight_')):o.hide_render=True
shot((6.3,8.2,10),(6.3,8.2,0),'render_44_kitchen_plan.png',ortho=5.0)
print('Q16 review renders done; master not saved')
