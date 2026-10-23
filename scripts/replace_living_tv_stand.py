"""Q17: Replace the living room TV console and wall-mounted TV with model.glb and tv.glb.

Removes the old MediaUnit_Living, ProK_MediaTop, Q2_Console* props, and wall-mounted
Living_TV_OLED_*, placing the 2000x450x513mm TV stand against the west artwall (x=4.330)
and the 1225x270x765mm stand-mounted TV centered on top of it (z=0.513..1.278).
"""
import math
from pathlib import Path
import runpy
import shutil
import sys
import bpy
from mathutils import Matrix, Vector

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))
import generate_high_detail_assets as A

assert bpy.context.scene.get('Q15_living_finish') == 1, 'Expected Q15_living_finish before Q17'
backup = ROOT / 'models/backups/apt_84a_photoreal_tour_before_tv_stand.blend'
if not backup.exists():
    shutil.copy2(bpy.data.filepath, backup)

bpy.context.view_layer.update()
old_tv = bpy.data.objects.get('Living_TV_OLED_Frame')
if old_tv:
    tv_pts = [old_tv.matrix_world @ Vector(v) for v in old_tv.bound_box]
    tv_cy = round((min(p.y for p in tv_pts) + max(p.y for p in tv_pts)) / 2, 4)
else:
    tv_cy = 3.286

for o in list(bpy.data.objects):
    if o.name.startswith(('MediaUnit_Living', 'ProK_Media', 'Q2_Console', 'Living_TV_OLED', 'Q17_TVStand_', 'Q17_TV_')):
        bpy.data.objects.remove(o, do_unlink=True)

col = A.get_col('Apt_LivingFinish')
stand_glb_path = ROOT / 'references/furniture/living-tv-stand/model.glb'
tv_glb_path = ROOT / 'references/furniture/living-tv/tv.glb'
assert stand_glb_path.exists(), f'Missing reference GLB: {stand_glb_path}'
assert tv_glb_path.exists(), f'Missing reference GLB: {tv_glb_path}'

mat_map = {
    'BlancMetal': 'Mat_Q17_BlancMetal',
    'BlancWhite': 'Mat_Q17_BlancWhite',
    'Interior': 'Mat_Q17_Interior',
    'FrostedPanel': 'Mat_Q17_FrostedGlass',
    'Anodised graphite edge': 'Mat_Q17_TV_Graphite',
    'OLED off - black optical glass': 'Mat_Q17_TV_ScreenGlass',
    'Rubber and dark recesses': 'Mat_Q17_TV_Rubber',
    'Satin charcoal rear polymer': 'Mat_Q17_TV_RearPolymer',
    'Satin titanium grey feet': 'Mat_Q17_TV_FeetMetal',
    'Smoked receiver window': 'Mat_Q17_TV_ReceiverWindow',
    'Socket and screw metal': 'Mat_Q17_TV_SocketMetal',
}

for new_name in mat_map.values():
    existing = bpy.data.materials.get(new_name)
    if existing:
        bpy.data.materials.remove(existing, do_unlink=True)

rot_z = Matrix.Rotation(math.pi / 2, 4, 'Z')

def import_and_place(glb_path, obj_prefix, origin_xyz):
    before_objs = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(glb_path))
    bpy.context.view_layer.update()
    imported = [o for o in bpy.data.objects if o not in before_objs]

    for o in imported:
        if o.type != 'MESH':
            continue
        for idx, m in enumerate(o.data.materials):
            if not m:
                continue
            base_name = m.name.split('.')[0]
            target_name = mat_map.get(base_name)
            if target_name:
                canonical = bpy.data.materials.get(target_name)
                if canonical is None:
                    m.name = target_name
                    canonical = m
                    if target_name == 'Mat_Q17_FrostedGlass' and canonical.use_nodes:
                        bsdf = canonical.node_tree.nodes.get('Principled BSDF')
                        if bsdf:
                            bsdf.inputs['Roughness'].default_value = 0.55
                            bsdf.inputs['Alpha'].default_value = 0.72
                            if 'Transmission Weight' in bsdf.inputs:
                                bsdf.inputs['Transmission Weight'].default_value = 0.0
                o.data.materials[idx] = canonical

    target_origin = Matrix.Translation(origin_xyz)
    mesh_objs = [o for o in imported if o.type == 'MESH']
    for o in mesh_objs:
        base = o.name.split('.')[0]
        o.name = f'{obj_prefix}{base}'
        o.data = o.data.copy()
        o.data.name = o.name
        world_xf = target_origin @ rot_z @ o.matrix_world
        o.parent = None
        o.matrix_world = Matrix.Identity(4)
        o.data.transform(world_xf)
        o.data.update()
        for c in list(o.users_collection):
            c.objects.unlink(o)
        col.objects.link(o)

    for o in imported:
        if o.type != 'MESH' and o.name in bpy.data.objects:
            bpy.data.objects.remove(o, do_unlink=True)

# 1. TV Stand (2000x450x513mm) flush with x=4.330 artwall
import_and_place(stand_glb_path, 'Q17_TVStand_', (4.330 + 0.225, tv_cy, 0.0))

# 2. Stand-mounted TV (1225x270x765mm) centered on top of TV stand (z=0.513)
import_and_place(tv_glb_path, 'Q17_TV_', (4.330 + 0.225, tv_cy, 0.513))

bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
bpy.context.scene['Q17_tv_stand'] = 1
old_root = r'C:\Users\tamarand\orca\projects\apt'
for im in bpy.data.images:
    if im.filepath and old_root.lower() in im.filepath.lower():
        rel = im.filepath[len(old_root):].lstrip('\\/')
        candidate = ROOT / rel
        if candidate.exists():
            im.filepath = str(candidate)
            if not im.packed_file:
                im.reload()
bpy.context.view_layer.update()
runpy.run_path(str(ROOT / 'scripts/verify_living_tv_stand.py'), run_name='__main__')
runpy.run_path(str(ROOT / 'scripts/verify_living_finish.py'), run_name='__main__')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / 'apt_84a_photoreal_tour.blend'))
print('Q17 TV STAND AND TV SAVED', flush=True)
