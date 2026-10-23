"""Q19: Model and place the Samsung 2.1ch Soundbar (858.8x75x59mm) in front of the TV on the living room TV stand,
and the Wireless Subwoofer (184x295x343mm) next to the south (window-side) armrest of the Brest sofa.
"""
from pathlib import Path
import runpy
import shutil
import sys
import bpy
import bmesh
from mathutils import Vector

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))
import generate_high_detail_assets as A

backup = ROOT / 'models/backups/apt_84a_photoreal_tour_before_soundbar.blend'
if not backup.exists():
    shutil.copy2(bpy.data.filepath, backup)

col = A.get_col('Apt_LivingFinish')

for o in list(bpy.data.objects):
    if o.name.startswith(('Q19_Soundbar_', 'Q19_Subwoofer_')):
        bpy.data.objects.remove(o, do_unlink=True)

def make_pbr_mat(name, rgba, metallic=0.0, roughness=0.4):
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials.new(name)
    m.use_nodes = True
    m.node_tree.nodes.clear()
    nodes = m.node_tree.nodes
    links = m.node_tree.links
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = rgba
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Roughness'].default_value = roughness
    out = nodes.new('ShaderNodeOutputMaterial')
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return m

mat_body   = make_pbr_mat('Mat_Q19_SoundbarBody',   (0.035, 0.035, 0.038, 1.0), metallic=0.12, roughness=0.42)
mat_grille = make_pbr_mat('Mat_Q19_SoundbarGrille', (0.022, 0.022, 0.025, 1.0), metallic=0.45, roughness=0.55)
mat_sub_gr = make_pbr_mat('Mat_Q19_SubGrille',      (0.028, 0.028, 0.030, 1.0), metallic=0.02, roughness=0.78)
mat_logo   = make_pbr_mat('Mat_Q19_SilverLogo',     (0.68,  0.69,  0.71,  1.0), metallic=0.85, roughness=0.25)
mat_btn    = make_pbr_mat('Mat_Q19_Button',         (0.08,  0.08,  0.09,  1.0), metallic=0.20, roughness=0.30)

def make_box(name, x1, x2, y1, y2, z1, z2, mat, bevel=0.001):
    o = A.create_beveled_box(
        name, (x1 + x2) / 2, (y1 + y2) / 2, z1,
        x2 - x1, y2 - y1, z2 - z1,
        mat=mat, col=col, bevel=bevel, seg=2
    )
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(o.data)
    bm.free()
    for p in o.data.polygons:
        p.use_smooth = False
    return o

def join_boxes(name, specs, mat, bevel=0.0005):
    parts = []
    for i, (x1, x2, y1, y2, z1, z2) in enumerate(specs):
        parts.append(make_box(f'{name}_tmp_{i}', x1, x2, y1, y2, z1, z2, mat, bevel=bevel))
    for o in bpy.data.objects:
        o.select_set(False)
    bpy.context.view_layer.objects.active = parts[0]
    for p in parts:
        p.select_set(True)
    if len(parts) > 1:
        bpy.ops.object.join()
    main = parts[0]
    main.name = name
    main.data.name = f'{name}_Mesh'
    main.select_set(False)
    return main

# 1. Soundbar on TV Stand in front of TV:
#    Envelope: x = [4.680, 4.755] (75.0mm), y = [2.8566, 3.7154] (858.8mm, center 3.286), z = [0.513, 0.572] (59.0mm)
SB_X0, SB_X1 = 4.6800, 4.7550
SB_Y0, SB_Y1 = 2.8566, 3.7154
SB_Z0, SB_Z1 = 0.5130, 0.5720

# Body with two low-profile rubber pads underneath so total Z is 0.5130..0.5720
sb_body = join_boxes(
    'Q19_Soundbar_Body',
    [
        (SB_X0, SB_X1 - 0.0020, SB_Y0, SB_Y1, SB_Z0 + 0.0020, SB_Z1 - 0.0004),
        (SB_X0 + 0.010, SB_X1 - 0.010, SB_Y0 + 0.060, SB_Y0 + 0.140, SB_Z0, SB_Z0 + 0.0020),
        (SB_X0 + 0.010, SB_X1 - 0.010, SB_Y1 - 0.140, SB_Y1 - 0.060, SB_Z0, SB_Z0 + 0.0020),
    ],
    mat_body,
    bevel=0.0025,
)

# Perforated front grille on the +X face (4.7525..4.7550)
make_box('Q19_Soundbar_Grille', SB_X1 - 0.0025, SB_X1, SB_Y0 + 0.0015, SB_Y1 - 0.0015, SB_Z0 + 0.0025, SB_Z1 - 0.0008, mat_grille, bevel=0.001)

# 4 top touch buttons at center Y = 3.286
btn_specs = []
for i, dy in enumerate((-0.018, -0.006, 0.006, 0.018)):
    yc = 3.2860 + dy
    btn_specs.append((4.7140, 4.7210, yc - 0.0030, yc + 0.0030, SB_Z1 - 0.0006, SB_Z1))
join_boxes('Q19_Soundbar_Buttons', btn_specs, mat_btn, bevel=0.0003)

# Top-left Samsung logo badge
make_box('Q19_Soundbar_Logo', 4.7120, 4.7200, SB_Y0 + 0.0180, SB_Y0 + 0.0460, SB_Z1 - 0.0005, SB_Z1, mat_logo, bevel=0.0002)

# 2. Wireless Subwoofer next to window-side (south) armrest of Brest sofa:
#    Envelope: x = [8.360, 8.655] (295.0mm), y = [1.373, 1.557] (184.0mm), z = [0.000, 0.343] (343.0mm)
SW_X0, SW_X1 = 8.3600, 8.6550
SW_Y0, SW_Y1 = 1.3730, 1.5570
SW_Z0, SW_Z1 = 0.0000, 0.3430

# 4 rubber feet at z = 0.000 .. 0.004
feet_specs = [
    (SW_X0 + 0.015, SW_X0 + 0.045, SW_Y0 + 0.015, SW_Y0 + 0.040, SW_Z0, SW_Z0 + 0.0040),
    (SW_X0 + 0.015, SW_X0 + 0.045, SW_Y1 - 0.040, SW_Y1 - 0.015, SW_Z0, SW_Z0 + 0.0040),
    (SW_X1 - 0.045, SW_X1 - 0.015, SW_Y0 + 0.015, SW_Y0 + 0.040, SW_Z0, SW_Z0 + 0.0040),
    (SW_X1 - 0.045, SW_X1 - 0.015, SW_Y1 - 0.040, SW_Y1 - 0.015, SW_Z0, SW_Z0 + 0.0040),
]
join_boxes('Q19_Subwoofer_Feet', feet_specs, mat_btn, bevel=0.0005)

# Main enclosure body (x = 8.365 .. 8.655, y = 1.373 .. 1.557, z = 0.004 .. 0.343)
make_box('Q19_Subwoofer_Body', SW_X0 + 0.0050, SW_X1, SW_Y0, SW_Y1, SW_Z0 + 0.0040, SW_Z1, mat_body, bevel=0.003)

# Front fabric grille on the -X face (x = 8.3605 .. 8.3655)
make_box('Q19_Subwoofer_Grille', SW_X0 + 0.0005, SW_X0 + 0.0055, SW_Y0 + 0.0020, SW_Y1 - 0.0020, SW_Z0 + 0.0060, SW_Z1 - 0.0020, mat_sub_gr, bevel=0.0015)

# Front bottom silver Samsung badge on the -X face (x = 8.3600 .. 8.3608)
sw_yc = (SW_Y0 + SW_Y1) / 2
make_box('Q19_Subwoofer_Logo', SW_X0, SW_X0 + 0.0008, sw_yc - 0.0160, sw_yc + 0.0160, SW_Z0 + 0.0320, SW_Z0 + 0.0370, mat_logo, bevel=0.0002)

bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
bpy.context.scene['Q19_living_soundbar'] = 1
bpy.context.view_layer.update()
runpy.run_path(str(ROOT / 'scripts/verify_living_soundbar.py'), run_name='__main__')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / 'apt_84a_photoreal_tour.blend'))
print('Q19 LIVING SOUNDBAR & SUBWOOFER SAVED', flush=True)
