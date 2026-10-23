"""Q19 verifies the Samsung 2.1ch Soundbar (858.8x75x59mm) on the TV stand in front of the TV
and the Wireless Subwoofer (184x295x343mm) on the floor next to the window-side armrest of the Brest sofa.
"""
import bpy
from mathutils import Vector

bpy.context.view_layer.update()

def bounds(name):
    o = bpy.data.objects[name]
    pts = [o.matrix_world @ Vector(v) for v in o.bound_box]
    return [min(v[i] for v in pts) for i in range(3)], [max(v[i] for v in pts) for i in range(3)]

def group_bounds(prefix):
    objs = [o for o in bpy.data.objects if o.name.startswith(prefix) and o.type == 'MESH']
    assert objs, f'Missing mesh objects with prefix {prefix}'
    pts = [o.matrix_world @ Vector(v) for o in objs for v in o.bound_box]
    return [min(v[i] for v in pts) for i in range(3)], [max(v[i] for v in pts) for i in range(3)]

assert bpy.context.scene.get('Q19_living_soundbar') == 1, 'Missing Q19_living_soundbar scene marker'

# 1. Verify Soundbar (858.8mm W x 75.0mm D x 59.0mm H) on TV stand in front of TV
sb_expected = ('Body', 'Grille', 'Buttons', 'Logo')
for part in sb_expected:
    name = f'Q19_Soundbar_{part}'
    assert bpy.data.objects.get(name) and bpy.data.objects[name].type == 'MESH', f'Missing {name}'

sb_lo, sb_hi = group_bounds('Q19_Soundbar_')
assert abs((sb_hi[0] - sb_lo[0]) - 0.075) < 0.002, f'Expected soundbar depth 75mm, got {sb_hi[0] - sb_lo[0]:.4f}'
assert abs((sb_hi[1] - sb_lo[1]) - 0.8588) < 0.002, f'Expected soundbar width 858.8mm, got {sb_hi[1] - sb_lo[1]:.4f}'
assert abs((sb_hi[2] - sb_lo[2]) - 0.059) < 0.002, f'Expected soundbar height 59mm, got {sb_hi[2] - sb_lo[2]:.4f}'
assert abs(sb_lo[0] - 4.680) < 0.002 and abs(sb_hi[0] - 4.755) < 0.002, f'Unexpected soundbar X: {sb_lo[0]:.4f}..{sb_hi[0]:.4f}'
assert abs((sb_lo[1] + sb_hi[1]) / 2 - 3.286) < 0.002, f'Soundbar not centered on TV stand Y=3.286: {(sb_lo[1]+sb_hi[1])/2:.4f}'
assert abs(sb_lo[2] - 0.513) < 0.002 and abs(sb_hi[2] - 0.572) < 0.002, f'Soundbar not resting on TV stand top Z=0.513: {sb_lo[2]:.4f}..{sb_hi[2]:.4f}'

# Soundbar must sit between the two TV feet without colliding
lf_lo, lf_hi = bounds('Q17_TV_Left_foot')
rf_lo, rf_hi = bounds('Q17_TV_Right_foot')
assert sb_lo[1] > lf_hi[1] + 0.05 and sb_hi[1] < rf_lo[1] - 0.05, 'Soundbar collides with TV feet'

# Soundbar front grille must face east (+X) toward the sofa
sb_body_lo, sb_body_hi = bounds('Q19_Soundbar_Body')
sb_grille_lo, sb_grille_hi = bounds('Q19_Soundbar_Grille')
assert sb_grille_hi[0] >= sb_body_hi[0] - 0.001, 'Soundbar grille must be on the east (+X) face'

# 2. Verify Wireless Subwoofer (184.0mm W x 295.0mm D x 343.0mm H) next to window-side of sofa
sw_expected = ('Body', 'Grille', 'Logo', 'Feet')
for part in sw_expected:
    name = f'Q19_Subwoofer_{part}'
    assert bpy.data.objects.get(name) and bpy.data.objects[name].type == 'MESH', f'Missing {name}'

sw_lo, sw_hi = group_bounds('Q19_Subwoofer_')
assert abs((sw_hi[0] - sw_lo[0]) - 0.295) < 0.002, f'Expected subwoofer depth 295mm, got {sw_hi[0] - sw_lo[0]:.4f}'
assert abs((sw_hi[1] - sw_lo[1]) - 0.184) < 0.002, f'Expected subwoofer width 184mm, got {sw_hi[1] - sw_lo[1]:.4f}'
assert abs((sw_hi[2] - sw_lo[2]) - 0.343) < 0.002, f'Expected subwoofer height 343mm, got {sw_hi[2] - sw_lo[2]:.4f}'
assert abs(sw_lo[0] - 8.360) < 0.002 and abs(sw_hi[0] - 8.655) < 0.002, f'Unexpected subwoofer X: {sw_lo[0]:.4f}..{sw_hi[0]:.4f}'
assert abs(sw_lo[1] - 1.373) < 0.002 and abs(sw_hi[1] - 1.557) < 0.002, f'Unexpected subwoofer Y: {sw_lo[1]:.4f}..{sw_hi[1]:.4f}'
assert abs(sw_lo[2] - 0.000) < 0.002 and abs(sw_hi[2] - 0.343) < 0.002, f'Unexpected subwoofer Z: {sw_lo[2]:.4f}..{sw_hi[2]:.4f}'

# Subwoofer must be on the south (window) side of the sofa, clear of both sofa and curtain
sofa_lo, sofa_hi = group_bounds('Q14_Brest_')
curtain_lo, curtain_hi = bounds('Q15_Curtain_Right')
assert sw_hi[1] < sofa_lo[1] - 0.05, f'Subwoofer must be south of sofa (sw_hi_y={sw_hi[1]:.3f}, sofa_lo_y={sofa_lo[1]:.3f})'
assert sw_lo[1] > curtain_hi[1] + 0.20, f'Subwoofer must be north of curtain (sw_lo_y={sw_lo[1]:.3f}, curtain_hi_y={curtain_hi[1]:.3f})'

# Subwoofer grille/logo must face west (-X) toward the living room
sw_grille_lo, _ = bounds('Q19_Subwoofer_Grille')
sw_body_lo, _ = bounds('Q19_Subwoofer_Body')
assert sw_grille_lo[0] <= sw_body_lo[0] + 0.001, 'Subwoofer grille must be on the west (-X) face'

print('PASS Q19: Soundbar (858.8x75x59mm) in front of TV & Subwoofer (184x295x343mm) next to window side of sofa verified')
