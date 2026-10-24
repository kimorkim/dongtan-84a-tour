"""Q22 real geometry checks for the approved K / no head / 115mm legs set."""
import bpy
from mathutils import Vector

bpy.context.view_layer.update()
assert bpy.context.scene.get('Q22_restandard_bed') == 1, 'Missing Q22 Restandard replacement'
assert not any(o.name.startswith(('Bed_Master_', 'Q2_Master_Cushion')) for o in bpy.data.objects), 'Legacy master bed remains'

def bounds(prefix):
    objs = [o for o in bpy.data.objects if o.type == 'MESH' and o.name.startswith(prefix)]
    assert objs, f'Missing {prefix}'
    points = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
    return Vector([min(p[i] for p in points) for i in range(3)]), Vector([max(p[i] for p in points) for i in range(3)])

def close(value, expected, label):
    assert abs(value-expected) < .0015, (label, value, expected)

lo, hi = bounds('Q22_Restandard_Mattress')
for i, size in enumerate((2., 1.6, .290)):
    close(hi[i]-lo[i], size, f'mattress axis{i}')
close(lo.z, .265, 'mattress rests on base')
deps=bpy.context.evaluated_depsgraph_get()
wall=bpy.data.objects['ExactWall_13'].evaluated_get(deps)
inv=wall.matrix_world.inverted()
hit,point,_,_=wall.ray_cast(inv @ Vector((2.,3.2222,1.)),inv.to_3x3() @ Vector((-1,0,0)))
assert hit, 'Master west wall missing'
wall_x=(wall.matrix_world @ point).x
close(lo.x, wall_x, 'head end flush to structural wall')
close((lo.x+hi.x)/2, wall_x+1., 'bed centre x')
close((lo.y+hi.y)/2, 3.2222, 'bed centre y')
for side in ('S', 'N'):
    a, b = bounds('Q22_Restandard_Base'+side)
    for i, size in enumerate((2., .8, .150)):
        close(b[i]-a[i], size, f'base{side} axis{i}')
    close(a.z, .115, 'base above legs')
legs = [o for o in bpy.data.objects if o.type == 'MESH' and o.name.startswith('Q22_Restandard_Leg')]
assert len(legs) == 8
for leg in legs:
    a, b = bounds(leg.name)
    close(a.z, .0, 'leg on wood floor'); close(b.z-a.z, .115, 'wood leg height')
    close(b.x-a.x, .065, 'wood leg diameter')
assert not any('Headboard' in o.name for o in bpy.data.objects if o.name.startswith('Q22_'))
for name in ('Q2_Master_Panel','Q2_Master_CoveTop','Q2_Master_CoveLow'):
    assert bpy.data.objects.get(name) is None, f'Unwanted decorative wall/strip remains: {name}'
assert bpy.data.objects.get('Q2_Master_Rug') is None, 'Unwanted master rug remains'
assert not any(o.name.startswith(('Nightstand_Master_', 'Q2_Night', 'Q2_Pendant')) for o in bpy.data.objects), 'Unwanted bedside furniture/light remains'
assert bpy.context.scene.get('Q21_lg_washtower') == 1, 'Latest utility model lost'
print('PASS Q22c: K1600x2000, legs on wood floor, top555mm, no rug/bedside decor, head end flush to west wall')
