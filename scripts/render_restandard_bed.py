"""Q22 room/detail/plan reviews. Cameras and lighting are never saved."""
import os
from pathlib import Path
import runpy
import bpy
from mathutils import Vector

ROOT=Path(__file__).resolve().parent.parent
sc=bpy.context.scene
sc.render.engine='CYCLES'; sc.cycles.samples=48; sc.cycles.use_denoising=True
sc.cycles.denoiser='OPENIMAGEDENOISE'; sc.cycles.use_adaptive_sampling=True
sc.render.use_persistent_data=True
sc.cycles.device='CPU'
sc.render.resolution_x=1200; sc.render.resolution_y=960; sc.render.resolution_percentage=100
sc.view_settings.exposure=.15
# Temporary photographic fill makes the grey fabric and shallow tufting legible.
fill_data=bpy.data.lights.new('Q22_ReviewFill','AREA'); fill_data.energy=60; fill_data.size=2.0
fill=bpy.data.objects.new(fill_data.name,fill_data); sc.collection.objects.link(fill)
fill.location=(2.6,3.25,2.15)

def path(relative):
    override=os.environ.get('RENDER_DIR')
    result=Path(override)/Path(relative).name if override else ROOT/relative
    result.parent.mkdir(parents=True,exist_ok=True)
    return str(result)

def shot(loc,target,relative,lens=28,ortho=None):
    data=bpy.data.cameras.new('Q22_ReviewCamera'); obj=bpy.data.objects.new(data.name,data)
    sc.collection.objects.link(obj); obj.location=loc
    obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
    data.lens=lens; data.clip_start=.05
    if ortho: data.type='ORTHO'; data.ortho_scale=ortho
    sc.camera=obj; sc.render.filepath=path(relative)
    print('Q22 RENDER',sc.render.filepath,'device',sc.cycles.device,flush=True)
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(obj,do_unlink=True); bpy.data.cameras.remove(data)

# Reuse the current room camera for the existing gallery slot.
sc.camera=bpy.data.objects['Cam_MasterBed_POV']
sc.render.filepath=path('renders/presentation/render_4_master_bedroom_pov.png')
print('Q22 ROOM RENDER on CPU',flush=True)
bpy.ops.render.render(write_still=True)
if not os.environ.get('RENDER_DIR'):
    import shutil
    shutil.copy2(sc.render.filepath,ROOT/'renders/review/render_48_restandard_master.png')
else:
    import shutil
    shutil.copy2(sc.render.filepath,Path(os.environ['RENDER_DIR'])/'render_48_restandard_master.png')
shot((.75,2.55,.75),(3.2,3.55,.30),'renders/review/render_49_restandard_detail.png',22)
for obj in bpy.data.objects:
    if obj.name.startswith(('Ceiling_','Cove_','Q10_Ceiling','Q11_Ceiling','Q2_Landscape')):
        obj.hide_render=True
shot((2.1,3.2,8),(2.1,3.2,0),'renders/review/render_50_restandard_plan.png',ortho=4.6)
if not os.environ.get('RENDER_DIR'):
    runpy.run_path(str(ROOT/'scripts/render_dimensions.py'),run_name='__main__')
else:
    # Existing plan renderer has a fixed path, so override only its output string.
    source=(ROOT/'scripts/render_dimensions.py').read_text(encoding='utf-8')
    source=source.replace("os.path.join(root,'renders/review/render_36_dimensioned_plan.png')",repr(path('renders/review/render_36_dimensioned_plan.png')))
    exec(compile(source,'render_dimensions.py','exec'),{'__file__':str(ROOT/'scripts/render_dimensions.py'),'__name__':'__main__'})
print('Q22 RENDERS DONE; master not saved',flush=True)
