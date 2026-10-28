"""Q23 geometry, retained structure and practical approach checks."""
import bpy
import hashlib
import json
from mathutils import Vector

assert not any(o.name.startswith(('Dress_Closet_', 'Wardrobe_Dress_')) for o in bpy.data.objects), 'Legacy closet intersects the dressing-room partition'
assert bpy.context.scene.get('Q23_dressroom_powder') == 1, 'Missing powder vanity'
structure = [(o.name, [list(row) for row in o.matrix_world],
              [list(v.co) for v in o.data.vertices],
              [list(p.vertices) for p in o.data.polygons])
             for o in sorted(bpy.data.objects, key=lambda o: o.name)
             if o.type == 'MESH' and o.name.startswith('ExactWall_')]
assert hashlib.sha256(json.dumps(structure).encode()).hexdigest() == bpy.context.scene['Q23_structure_sha256'], 'Structural walls changed since the Q23 backup'

def bounds(name):
    o = bpy.data.objects[name]
    pts = [o.matrix_world @ Vector(c) for c in o.bound_box]
    return Vector([min(p[i] for p in pts) for i in range(3)]), Vector([max(p[i] for p in pts) for i in range(3)])

def close(a, b):
    assert abs(a-b) < .002, (a, b)

lo, hi = bounds('Q23_Powder_Top')
close(lo.x,.495); close(hi.x,.945); close(lo.z,.730); close(hi.z,.750)
# Solid wall face along the entire rear of the assembly; never intersect a wall.
wall = bpy.data.objects['ExactWall_13']
inv = wall.matrix_world.inverted()
for y in (5.94,6.45,7.04):
    hit, p, *_ = wall.ray_cast(inv @ Vector((1.5,y,1.)), inv.to_3x3() @ Vector((-1,0,0)))
    assert hit
    close((wall.matrix_world @ p).x, .485)
    assert lo.x - (wall.matrix_world @ p).x > .005
# Side-wall faces are slightly tapered in the retained Q12 mesh. The fitted top
# must follow the actual faces, with at most a 1mm seam instead of side gaps.
for name in ('Top','UpperCabS','UpperCabN','LowerDoorS','LowerDoorN'):
    obj=bpy.data.objects['Q23_Powder_'+name]
    for v in obj.data.vertices:
        p=obj.matrix_world@v.co
        if not (p.y < 5.95 or p.y > 7.0):
            continue
        direction=1 if p.y>6.45 else -1
        hit,q,*_=wall.ray_cast(inv@Vector((p.x,6.45,1.2)),inv.to_3x3()@Vector((0,direction,0)))
        assert hit
        seam=abs(p.y-(wall.matrix_world@q).y)
        allowed=.004 if name.startswith('LowerDoor') else .0011
        assert seam<allowed, ('Side gap',name,p.x,p.y,seam)
# Reference type: full-width lower storage and a ceiling-height upper surround.
for name in ('UpperCabS','UpperCabN','UpperPelmet','LowerDoorS','LowerDoorN','DrawerS','DrawerN'):
    assert bpy.data.objects.get('Q23_Powder_'+name), 'Missing apartment built-in element: '+name
assert not any(o.name.startswith(('Q23_Powder_Pull','Q23_Powder_Pencil','Q23_Powder_LightBar','Q23_Powder_LightDiffuser')) for o in bpy.data.objects), 'Standalone vanity styling remains'
for side in ('S','N'):
    a,b=bounds('Q23_Powder_UpperCab'+side)
    close(b.z,2.280)
    assert a.z < .90
mirror_lo,mirror_hi=bounds('Q23_Powder_Mirror')
assert mirror_hi.z > 2.20 and mirror_hi.y-mirror_lo.y > .70, 'Reference mirror must fill upper niche'
deps = bpy.context.evaluated_depsgraph_get()
for y in (6.19,6.45,6.71):
    hit, p, _, _, o, _ = bpy.context.scene.ray_cast(deps,Vector((1.4,y,.40)),Vector((-1,0,0)))
    assert hit and o.name.startswith('Q23_Powder_Lower'), ('Missing continuous lower storage', y, o.name if o else None)
door_lo, _ = bounds('ProDoorLeaf_MasterBath')
assert door_lo.x-hi.x > 1.10, 'Open bathroom door obstructs vanity approach'
for o in bpy.data.objects:
    if o.type == 'MESH' and o.name.startswith('Q23_Powder_'):
        a,b=bounds(o.name)
        assert a.x > .485 and b.x < .946 and a.y >= 5.83 and b.y <= 7.11
assert 'Master_Vanity_Top' in bpy.data.objects, 'Existing bathroom basin removed'
assert bpy.context.scene.get('Q22_restandard_bed') == 1
print('PASS Q23b: closet cleared; full built-in lower storage/upper cupboards/large mirror; structure and door clear')
