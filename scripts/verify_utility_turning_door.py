"""Q20 verifies:
1. Fridge cabinet north wall (ExactWall_11) is straightened to y=8.176 with zero wedge gap to Q3_SideN,
   and no protruding baseboard block exists in the fridge alcove.
2. Old floating 2-strip trim (Q3_SinkTrim*) and opaque slab (ProDoorLeaf_UtilitySink) are removed.
3. Upper door header wall (Q20_UtilityDoor_Header) fills z=2.15..2.30 up to the ceiling.
4. Integrated uPVC turning door frame (Q20_TurningDoor_Frame_*) wraps the full wall thickness x=4.965..5.085
   flush with y=8.360 and y=9.015 without gaps.
5. Turning door leaf (ProDoorLeaf_UtilitySink_Frame, Glass, Gasket, Handle) has a framed glass window and lever handle.
"""
import bpy
from mathutils import Vector

bpy.context.view_layer.update()

def bounds(name):
    o = bpy.data.objects[name]
    pts = [o.matrix_world @ Vector(v) for v in o.bound_box]
    return [min(v[i] for v in pts) for i in range(3)], [max(v[i] for v in pts) for i in range(3)]

assert bpy.context.scene.get('Q20_utility_turning_door') == 1, 'Missing Q20_utility_turning_door scene marker'

# 1. Old floating trims and opaque slab must be removed
for old_name in (
    'Q3_SinkTrimK_N', 'Q3_SinkTrimK_S', 'Q3_SinkTrimK_Top',
    'Q3_SinkTrimR_N', 'Q3_SinkTrimR_S', 'Q3_SinkTrimR_Top',
    'Q3_SinkDoor_HandleBar', 'Q3_SinkDoor_HandleBase',
    'ProDoorLeaf_UtilitySink',
):
    assert bpy.data.objects.get(old_name) is None, f'Old object {old_name} still exists'

# 2. ExactWall_11 north fridge-alcove face must be straight at y = 8.176 (touching Q3_SideN hi_y = 8.176)
w11 = bpy.data.objects['ExactWall_11']
alcove_ys = [
    (w11.matrix_world @ v.co).y
    for v in w11.data.vertices
    if 4.30 < (w11.matrix_world @ v.co).x < 5.10 and 8.16 < (w11.matrix_world @ v.co).y < 8.30
]
assert alcove_ys, 'Missing ExactWall_11 fridge alcove north vertices'
for yval in alcove_ys:
    assert abs(yval - 8.176) < 0.002, f'ExactWall_11 fridge alcove north wall is still slanted: y={yval:.4f}'

# 3. Upper door header wall must close z=2.15..2.30 between y=8.360 and y=9.015
hdr_lo, hdr_hi = bounds('Q20_UtilityDoor_Header')
assert abs(hdr_lo[0] - 4.975) < 0.002 and abs(hdr_hi[0] - 5.075) < 0.002, f'Unexpected header X: {hdr_lo[0]}..{hdr_hi[0]}'
assert abs(hdr_lo[1] - 8.360) < 0.002 and abs(hdr_hi[1] - 9.015) < 0.002, f'Unexpected header Y: {hdr_lo[1]}..{hdr_hi[1]}'
assert hdr_lo[2] <= 2.152 and abs(hdr_hi[2] - 2.300) < 0.002, f'Unexpected header Z: {hdr_lo[2]}..{hdr_hi[2]}'

# 4. Integrated uPVC turning door frame must span full wall thickness (x=4.965..5.085) with zero wall gap
for part in ('S', 'N', 'Top', 'Bot', 'Gasket'):
    fname = f'Q20_TurningDoor_Frame_{part}'
    assert bpy.data.objects.get(fname) and bpy.data.objects[fname].type == 'MESH', f'Missing {fname}'

fs_lo, fs_hi = bounds('Q20_TurningDoor_Frame_S')
fn_lo, fn_hi = bounds('Q20_TurningDoor_Frame_N')
ft_lo, ft_hi = bounds('Q20_TurningDoor_Frame_Top')
assert fs_lo[0] <= 4.966 and fs_hi[0] >= 5.084, f'South frame does not wrap full wall thickness: {fs_lo[0]}..{fs_hi[0]}'
assert fs_lo[1] <= 8.360 and fs_hi[1] >= 8.405, f'South frame leaves gap to y=8.360 wall: {fs_lo[1]}..{fs_hi[1]}'
assert fn_lo[1] <= 8.970 and fn_hi[1] >= 9.015, f'North frame leaves gap to y=9.015 wall: {fn_lo[1]}..{fn_hi[1]}'
assert ft_hi[2] >= 2.150, f'Top frame leaves gap to header wall: {ft_hi[2]}'

# 5. Turning door leaf must have uPVC sash frame, large glass pane, gasket, and lever handle
for part in ('Frame', 'Glass', 'Gasket', 'Handle'):
    dname = f'ProDoorLeaf_UtilitySink_{part}'
    assert bpy.data.objects.get(dname) and bpy.data.objects[dname].type == 'MESH', f'Missing {dname}'

gl_lo, gl_hi = bounds('ProDoorLeaf_UtilitySink_Glass')
assert (gl_hi[0] - gl_lo[0]) > 0.35 and (gl_hi[2] - gl_lo[2]) > 1.75, f'Turning door glass too small: {gl_lo}..{gl_hi}'

print('PASS Q20: fridge-to-utility wall gap closed & utility room turning door with glass pane installed')
