"""Q21 review renders of the LG WashTower in the south-west utility room alcove (master is not saved)."""
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

# Temporary review fill light inside the utility room (not saved).
ld = bpy.data.lights.new('Q21_ReviewFill', 'AREA'); ld.energy = 60; ld.size = 0.8
lo = bpy.data.objects.new('Q21_ReviewFill', ld); sc.collection.objects.link(lo)
lo.location = (4.45, 9.20, 2.20)


def shot(loc, target, name, lens):
    d = bpy.data.cameras.new('Q21_Review'); o = bpy.data.objects.new(d.name, d); sc.collection.objects.link(o)
    o.location = loc; o.rotation_euler = (Vector(target) - o.location).to_track_quat('-Z', 'Y').to_euler(); d.lens = lens
    d.clip_start = 0.05
    sc.camera = o; sc.render.filepath = str(ROOT / 'renders/review' / name)
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(o, do_unlink=True); bpy.data.cameras.remove(d)
    print('Saved', name, flush=True)


# 1. From the doorway looking straight into the south-west alcove & north window bay (matches user POV).
shot((5.18, 8.78, 1.50), (3.65, 9.00, 1.00), 'render_46_utility_washtower.png', 18)
# 2. From inside the north window bay looking south-west at the WashTower front + PS wall step + floor drain.
shot((4.85, 9.85, 1.55), (3.65, 8.85, 0.90), 'render_47_utility_washtower_side.png', 16)
bpy.data.objects.remove(lo, do_unlink=True); bpy.data.lights.remove(ld)
print('Q21 REVIEW RENDERS DONE; master not saved')
