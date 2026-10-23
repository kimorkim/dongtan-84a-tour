"""Q21 verifies the LG TROMM Objet Collection WashTower WL21EGZU in the utility room (kitchen balcony)
and the corrected CAD alcove dimension (y = 8.360..9.270, 910mm clear width x 600mm step depth).

1. Alcove wall in ExactWall_11 is at y = 9.270 (910mm clear width from y = 8.360, matching A02-102 1,010/1,115 chain).
2. Official WashTower envelope 700(W) x 1890(H) x 830(D) mm (bounds of all Q21_WashTower_* meshes).
3. Back faces the alcove west wall x = 3.175 with a 40mm hose gap (x = 3.215..4.045), front (+X) towards the turning door.
4. Sits inside the south-west washing machine alcove (y = 8.500..9.200 within 8.360..9.270), leaving the north window bay
   (x = 3.775..4.975, y = 9.270..10.145) and doorway aisle (x = 4.045..4.963) open.
5. Two-tone fronts (Nature Green dryer / Nature Beige washer), black centre control band, two round glass doors,
   and 300x300 grey utility room tile floor + drain.
"""
import bpy
from mathutils import Vector

bpy.context.view_layer.update()


def bounds_of(objs):
    lo = Vector((1e9, 1e9, 1e9)); hi = Vector((-1e9, -1e9, -1e9))
    for o in objs:
        for c in o.bound_box:
            w = o.matrix_world @ Vector(c)
            lo = Vector(map(min, lo, w)); hi = Vector(map(max, hi, w))
    return lo, hi


def b(name):
    o = bpy.data.objects.get(name)
    assert o is not None and o.type == 'MESH', f'Missing {name}'
    return bounds_of([o])


assert bpy.context.scene.get('Q21_lg_washtower') == 1, 'Missing Q21_lg_washtower scene marker'

# 1. Verify ExactWall_11 south-west alcove north wall is at y = 9.270 (910mm clear width from y = 8.360)
w11 = bpy.data.objects['ExactWall_11']
ps_south_ys = [
    (w11.matrix_world @ v.co).y
    for v in w11.data.vertices
    if 3.15 < (w11.matrix_world @ v.co).x < 3.80 and 8.90 < (w11.matrix_world @ v.co).y < 9.40
]
assert ps_south_ys, 'Missing ExactWall_11 PS south wall vertices'
for yval in ps_south_ys:
    assert abs(yval - 9.270) < 0.002, f'ExactWall_11 PS south wall not at y=9.270: y={yval:.4f}'

# 2. WashTower official envelope
parts = [o for o in bpy.data.objects if o.type == 'MESH' and o.name.startswith('Q21_WashTower_')]
assert parts, 'No Q21_WashTower_* meshes'
lo, hi = bounds_of(parts)
dx, dy, dz = hi - lo
assert abs(dx - 0.830) < 0.002, f'Depth {dx:.4f} != 0.830'
assert abs(dy - 0.700) < 0.002, f'Width {dy:.4f} != 0.700'
assert abs(dz - 1.890) < 0.002, f'Height {dz:.4f} != 1.890'

# 3. Tile floor & standing height
tf_lo, tf_hi = b('Q21_UtilityTile_Floor')
b('Q21_UtilityTile_Grout'); b('Q21_UtilityTile_Drain')
assert tf_lo.x <= 3.18 and tf_hi.x >= 4.97 and tf_lo.y <= 8.365 and tf_hi.y >= 10.14, f'Tile floor does not cover the utility room: {tf_lo}..{tf_hi}'
assert abs(tf_hi.z - 0.014) < 0.001, f'Tile top z={tf_hi.z:.4f}'
assert bpy.data.objects['Q21_UtilityTile_Floor'].active_material.name == 'Mat_Q21_UtilityTile'
assert abs(lo.z - tf_hi.z) < 0.001, f'WashTower not standing on the tile floor: z={lo.z:.4f}'

# 4. Alcove placement (x = 3.215..4.045, y = 8.500..9.200 inside 8.360..9.270) & orientation (+X)
assert 0.03 <= lo.x - 3.175 <= 0.05, f'Back gap to alcove west wall (x=3.175) is {lo.x - 3.175:.4f}'
assert lo.y >= 8.360 + 0.10 and hi.y <= 9.270 - 0.05, f'WashTower not inside y=8.360..9.270 alcove: {lo.y:.3f}..{hi.y:.3f}'
for side in ('Dryer', 'Washer'):
    g_lo, g_hi = b(f'Q21_WashTower_{side}_Glass')
    assert g_hi.x > hi.x - 0.03, f'{side} glass door does not face +X'
    r = (g_hi.y - g_lo.y) / 2
    assert 0.18 < r < 0.24, f'{side} glass radius {r:.3f}'

for o in bpy.data.objects:
    if o.type == 'MESH' and o.name.startswith(('ProDoorLeaf_UtilitySink_', 'Q20_TurningDoor_Frame_')):
        d_lo, d_hi = bounds_of([o])
        overlap = all(d_lo[i] < hi[i] and d_hi[i] > lo[i] for i in range(3))
        assert not overlap, f'WashTower overlaps {o.name}'
f_lo, _ = b('Q20_TurningDoor_Frame_S')
assert f_lo.x - hi.x >= 0.85, f'Front aisle to the door frame only {f_lo.x - hi.x:.3f}m'

# 5. Two-tone fronts, control band and doors
fg_lo, fg_hi = b('Q21_WashTower_Dryer_Front')
fb_lo, fb_hi = b('Q21_WashTower_Washer_Front')
cp_lo, cp_hi = b('Q21_WashTower_Control_Panel')
assert fb_hi.z <= cp_lo.z + 0.002 and cp_hi.z <= fg_lo.z + 0.002, 'Control band is not between washer and dryer'
assert fg_hi.z > fg_lo.z + 0.75 and fb_hi.z > fb_lo.z + 0.90, 'Front panels too short'
green = bpy.data.objects['Q21_WashTower_Dryer_Front'].active_material.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value
beige = bpy.data.objects['Q21_WashTower_Washer_Front'].active_material.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value
assert green[1] > green[0] and green[1] > green[2], 'Dryer front is not Nature Green'
assert beige[0] > beige[2] and beige[0] > 0.5, 'Washer front is not Nature Beige'
for p in ('Dryer_Ring', 'Washer_Ring', 'Dryer_Drum', 'Washer_Drum', 'Dispenser', 'Filter_Cover', 'Display', 'Feet'):
    b(f'Q21_WashTower_{p}')
print(f'PASS Q21: LG WashTower WL21EGZU in alcove x{lo.x:.3f}~{hi.x:.3f} y{lo.y:.3f}~{hi.y:.3f} z{lo.z:.3f}~{hi.z:.3f}')
