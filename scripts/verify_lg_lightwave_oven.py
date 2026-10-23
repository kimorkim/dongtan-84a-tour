"""Q18 verifies the LG Objet Collection Lightwave Oven (MLJ32EWSO, 527x480x394mm) in the rice-cooker unit upper bay."""
import bpy
from mathutils import Vector

bpy.context.view_layer.update()

def bounds(name):
    o = bpy.data.objects[name]
    pts = [o.matrix_world @ Vector(v) for v in o.bound_box]
    return [min(v[i] for v in pts) for i in range(3)], [max(v[i] for v in pts) for i in range(3)]

assert bpy.context.scene.get('Q18_lightwave_oven') == 1, 'Missing Q18_lightwave_oven scene marker'
assert bpy.data.objects.get('Q3_Drawer_TopDoor') is None, 'Old closed middle door Q3_Drawer_TopDoor still blocks oven bay'
assert bpy.data.objects.get('Q3_Cooker_Body') is not None, 'Rice cooker must remain in lower open bay'
assert bpy.data.objects.get('Q3_TopDoor0') is not None, 'Upper cabinet door Q3_TopDoor0 must remain above oven bay'

shelf_lo, shelf_hi = bounds('Q3_OvenNiche_Top')
assert abs(shelf_lo[2] - 1.400) < 0.002 and abs(shelf_hi[2] - 1.420) < 0.002, f'Unexpected Q3_OvenNiche_Top Z: {shelf_lo[2]}..{shelf_hi[2]}'

rc_shelf_lo, rc_shelf_hi = bounds('Q3_Niche_Shelf')
assert abs(rc_shelf_lo[2] - 0.562) < 0.002 and abs(rc_shelf_hi[2] - 0.582) < 0.002, f'Unexpected Q3_Niche_Shelf Z: {rc_shelf_lo[2]}..{rc_shelf_hi[2]}'

oven_shelf_lo, oven_shelf_hi = bounds('Q3_Niche_Top')
assert abs(oven_shelf_lo[2] - 0.940) < 0.002 and abs(oven_shelf_hi[2] - 0.960) < 0.002, f'Unexpected Q3_Niche_Top Z: {oven_shelf_lo[2]}..{oven_shelf_hi[2]}'

back_lo, back_hi = bounds('Q3_Niche_Back')
assert back_lo[2] <= 0.565 and back_hi[2] >= 1.415, f'Q3_Niche_Back must span both open bays: {back_lo[2]}..{back_hi[2]}'

cooker_lo, cooker_hi = bounds('Q3_Cooker_Body')
assert abs(cooker_lo[2] - 0.587) < 0.005, f'Rice cooker not lowered onto Q3_Niche_Shelf: z_lo={cooker_lo[2]}'

expected_parts = ('Body', 'DoorLower', 'DoorUpper', 'Window', 'Display', 'Dial')
for part in expected_parts:
    obj_name = f'Q18_LightwaveOven_{part}'
    obj = bpy.data.objects.get(obj_name)
    assert obj and obj.type == 'MESH', f'Missing lightwave oven mesh {obj_name}'

case_bounds = [bounds(f'Q18_LightwaveOven_{p}') for p in ('Body', 'DoorLower', 'DoorUpper')]
lo = [min(b[0][i] for b in case_bounds) for i in range(3)]
hi = [max(b[1][i] for b in case_bounds) for i in range(3)]

# Official MLJ32EWSO dimensions: 527mm(W, along Y) x 480mm(D, along X) x 394mm(H, along Z)
assert abs((hi[0] - lo[0]) - 0.480) < 0.002, f'Expected 480mm depth, got {hi[0] - lo[0]}'
assert abs((hi[1] - lo[1]) - 0.527) < 0.002, f'Expected 527mm width, got {hi[1] - lo[1]}'
assert abs((hi[2] - lo[2]) - 0.394) < 0.002, f'Expected 394mm height, got {hi[2] - lo[2]}'
assert abs(lo[0] - 4.420) < 0.002 and abs(hi[0] - 4.900) < 0.002, f'Unexpected X bounds: {lo[0]}..{hi[0]}'
assert abs((lo[1] + hi[1]) / 2 - 7.835) < 0.002, f'Unexpected Y centre: {(lo[1]+hi[1])/2}'
assert abs(lo[2] - 0.960) < 0.002 and abs(hi[2] - 1.354) < 0.002, f'Unexpected ergonomic Z bounds: {lo[2]}..{hi[2]}'

dial_lo, dial_hi = bounds('Q18_LightwaveOven_Dial')
assert dial_hi[0] > hi[0] + 0.005, 'Rotary dial must protrude on the east (+X) front face'

# Verify tight-fitted cabinet doors & drawers without empty gaps
td1_lo, td1_hi = bounds('Q3_TopDoor1')
td2_lo, td2_hi = bounds('Q3_TopDoor2')
td3_lo, td3_hi = bounds('Q3_TopDoor3')
td0_lo, td0_hi = bounds('Q3_TopDoor0')
assert 0.001 <= (td2_lo[1] - td1_hi[1]) <= 0.0035, f'Gap between TopDoor1 and TopDoor2 too large: {td2_lo[1] - td1_hi[1]:.4f}'
assert 0.001 <= (td3_lo[1] - td2_hi[1]) <= 0.0035, f'Gap between TopDoor2 and TopDoor3 too large: {td3_lo[1] - td2_hi[1]:.4f}'
assert 0.001 <= (td0_lo[1] - td3_hi[1]) <= 0.0035, f'Gap between TopDoor3 and TopDoor0 too large: {td0_lo[1] - td3_hi[1]:.4f}'

df1_lo, df1_hi = bounds('Q3_Drawer_Front1')
df2_lo, df2_hi = bounds('Q3_Drawer_Front2')
side_s_lo, side_s_hi = bounds('Q3_Drawer_SideS')
side_n_lo, side_n_hi = bounds('Q3_Drawer_SideN')
assert 0.0005 <= (df1_lo[1] - side_s_hi[1]) <= 0.003, f'Left gap on Drawer_Front1 too large: {df1_lo[1] - side_s_hi[1]:.4f}'
assert 0.0005 <= (side_n_lo[1] - df1_hi[1]) <= 0.003, f'Right gap on Drawer_Front1 too large: {side_n_lo[1] - df1_hi[1]:.4f}'
assert 0.001 <= (df1_lo[2] - df2_hi[2]) <= 0.0035, f'Vertical gap between drawers too large: {df1_lo[2] - df2_hi[2]:.4f}'

h0_lo, h0_hi = bounds('Q3_Drawer_Handle0')
assert abs(h0_lo[0] - df1_hi[0]) <= 0.002, f'Drawer handle floating in air: handle lo_x={h0_lo[0]:.4f} vs door hi_x={df1_hi[0]:.4f}'

div2_lo, div2_hi = bounds('Q3_Divider2')
assert abs(side_s_lo[1] - div2_hi[1]) <= 0.0005, f'Crack between Q3_Divider2 and Q3_Drawer_SideS: {side_s_lo[1] - div2_hi[1]:.4f}'

print('PASS Q18: LG MLJ32EWSO lightwave oven (527x480x394mm) & gap-free fridge cabinet verified')
