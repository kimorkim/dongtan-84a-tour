"""Q17 checks the living-room TV stand (model.glb) and stand-mounted TV (tv.glb) replacement."""
import bpy
from mathutils import Vector

bpy.context.view_layer.update()

def bounds(name):
    o = bpy.data.objects[name]
    pts = [o.matrix_world @ Vector(v) for v in o.bound_box]
    return [min(v[i] for v in pts) for i in range(3)], [max(v[i] for v in pts) for i in range(3)]

assert bpy.context.scene.get('Q17_tv_stand') == 1, 'Missing Q17_tv_stand scene marker'
assert not any(o.name.startswith(('MediaUnit_Living', 'ProK_Media', 'Q2_Console', 'Living_TV_OLED')) for o in bpy.data.objects), \
    'Old living TV console, console props, or wall-mounted TV still exist'

expected_stand_parts = (
    'Leg_FL', 'Leg_FR', 'Leg_BL', 'Leg_BR',
    'Carcass', 'Shelf',
    'Door_Left', 'Door_Centre', 'Door_Right',
)
stand_bounds = []
for part in expected_stand_parts:
    obj_name = f'Q17_TVStand_{part}'
    obj = bpy.data.objects.get(obj_name)
    assert obj and obj.type == 'MESH', f'Missing TV stand mesh {obj_name}'
    stand_bounds.append(bounds(obj_name))

lo = [min(b[0][i] for b in stand_bounds) for i in range(3)]
hi = [max(b[1][i] for b in stand_bounds) for i in range(3)]

# Back flush with Living_ArtWall_Tile east face (x=4.330), depth 450mm, width 2000mm, height 513mm
assert abs(lo[0] - 4.330) < 0.002 and abs(hi[0] - 4.780) < 0.002, f'Unexpected stand X bounds: {lo[0]}..{hi[0]}'
assert abs((hi[1] - lo[1]) - 2.000) < 0.002, f'Unexpected stand Y width: {hi[1] - lo[1]}'
assert abs((lo[1] + hi[1]) / 2 - 3.286) < 0.002, f'Unexpected stand Y centre: {(lo[1]+hi[1])/2}'
assert abs(lo[2] - 0.000) < 0.002 and abs(hi[2] - 0.513) < 0.002, f'Unexpected stand Z bounds: {lo[2]}..{hi[2]}'

# Doors must face east (+X) toward the sofa, ordered Left(south) -> Centre -> Right(north)
dl_lo, dl_hi = bounds('Q17_TVStand_Door_Left')
dc_lo, dc_hi = bounds('Q17_TVStand_Door_Centre')
dr_lo, dr_hi = bounds('Q17_TVStand_Door_Right')
for d_lo in (dl_lo, dc_lo, dr_lo):
    assert d_lo[0] > 4.75, f'Door is not on the east front face: {d_lo[0]}'
assert (dl_lo[1] + dl_hi[1]) < (dc_lo[1] + dc_hi[1]) < (dr_lo[1] + dr_hi[1]), \
    'Doors must be ordered Left(south) -> Centre -> Right(north) when viewed from sofa'

fl_lo, _ = bounds('Q17_TVStand_Leg_FL')
bl_lo, _ = bounds('Q17_TVStand_Leg_BL')
assert fl_lo[0] > bl_lo[0] + 0.30, 'Front legs must be east of back legs'

# Stand-mounted TV (1225x270x765mm) on top of the TV stand (z=0.513..1.278)
expected_tv_parts = (
    'Chassis', 'Connectors', 'IR_receiver', 'Input_panel',
    'Left_foot', 'Lower_trim', 'Rear_shell', 'Right_foot',
    'Screen', 'VESA_screws', 'Ventilation',
)
tv_bounds = []
for part in expected_tv_parts:
    obj_name = f'Q17_TV_{part}'
    obj = bpy.data.objects.get(obj_name)
    assert obj and obj.type == 'MESH', f'Missing TV mesh {obj_name}'
    tv_bounds.append(bounds(obj_name))

tlo = [min(b[0][i] for b in tv_bounds) for i in range(3)]
thi = [max(b[1][i] for b in tv_bounds) for i in range(3)]
assert abs(tlo[0] - 4.420) < 0.002 and abs(thi[0] - 4.690) < 0.002, f'Unexpected TV X bounds: {tlo[0]}..{thi[0]}'
assert abs((thi[1] - tlo[1]) - 1.225) < 0.002, f'Unexpected TV Y width: {thi[1] - tlo[1]}'
assert abs((tlo[1] + thi[1]) / 2 - 3.286) < 0.002, f'Unexpected TV Y centre: {(tlo[1]+thi[1])/2}'
assert abs(tlo[2] - 0.513) < 0.002 and abs(thi[2] - 1.278) < 0.002, f'Unexpected TV Z bounds: {tlo[2]}..{thi[2]}'

scr_lo, _ = bounds('Q17_TV_Screen')
rear_lo, _ = bounds('Q17_TV_Rear_shell')
assert scr_lo[0] > rear_lo[0] + 0.015, 'TV screen must face east (+X) toward the sofa'

for mat_name in ('Mat_Q17_BlancMetal', 'Mat_Q17_BlancWhite', 'Mat_Q17_Interior', 'Mat_Q17_FrostedGlass'):
    assert bpy.data.materials.get(mat_name), f'Missing material {mat_name}'

for im in bpy.data.images:
    if im.filepath and not im.packed_file:
        assert im.size[0] > 0 and im.size[1] > 0, f'Unresolved texture image: {im.name} -> {im.filepath}'

print('PASS Q17: old media unit/props and wall TV removed, 2000x450x513mm TV stand and 1225x270x765mm stand TV aligned')
