"""Q21 review renders of the LG WashTower in the utility room (master is not saved)."""
from pathlib import Path
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parent.parent
sc = bpy.context.scene
sc.render.engine = 'CYCLES'; sc.cycles.samples = 48; sc.cycles.use_denoising = True
sc.cycles.denoiser = 'OPENIMAGEDENOISE'; sc.cycles.use_adaptive_sampling = True
sc.cycles.device = 'CPU'; sc.render.use_persistent_data = True
sc.render.resolution_x = 1080; sc.render.resolution_y = 1350; sc.render.resolution_percentage = 100
sc.view_settings.exposure = 0.35

# Temporary review fill light inside the small utility room (not saved).
ld = bpy.data.lights.new('Q21_ReviewFill', 'AREA'); ld.energy = 60; ld.size = 0.8
lo = bpy.data.objects.new('Q21_ReviewFill', ld); sc.collection.objects.link(lo)
lo.location = (4.45, 9.40, 2.20)


def shot(loc, target, name, lens):
    d = bpy.data.cameras.new('Q21_Review'); o = bpy.data.objects.new(d.name, d); sc.collection.objects.link(o)
    o.location = loc; o.rotation_euler = (Vector(target) - o.location).to_track_quat('-Z', 'Y').to_euler(); d.lens = lens
    d.clip_start = 0.05
    sc.camera = o; sc.render.filepath = str(ROOT / 'renders/review' / name)
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(o, do_unlink=True); bpy.data.cameras.remove(d)
    print('Saved', name, flush=True)


# Standing in the doorway / south pocket, looking north-west at the WashTower front.
shot((4.93, 8.50, 1.50), (4.05, 9.45, 1.05), 'render_46_utility_washtower.png', 15)
# From the north window corner, looking back south-west (side + front, tile floor and drain).
shot((4.90, 10.08, 1.55), (4.10, 9.10, 0.75), 'render_47_utility_washtower_side.png', 15)
bpy.data.objects.remove(lo, do_unlink=True); bpy.data.lights.remove(ld)
print('Q21 REVIEW RENDERS DONE; master not saved')
