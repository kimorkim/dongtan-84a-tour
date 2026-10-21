"""Q13: product envelopes, joined cases, door swing and workstation clearance."""
import bpy
from mathutils import Vector

bpy.context.view_layer.update()
def bounds(objects):
    p=[o.matrix_world@Vector(c) for o in objects for c in o.bound_box]
    assert p,'Missing Poeta bookcases'
    return [min(v[i] for v in p) for i in range(3)],[max(v[i] for v in p) for i in range(3)]

cases=[]
for size,width in [('800',.8),('600',.6)]:
    prefix='Q13_Poeta'+size+'_'
    parts=[o for o in bpy.data.objects if o.name.startswith(prefix) and o.type=='MESH']
    lo,hi=bounds(parts); cases.append((lo,hi))
    assert all(abs(a-b)<.001 for a,b in zip([hi[i]-lo[i] for i in range(3)],[.3,width,2.014])),(size,lo,hi)
    assert 9.09<=lo[0]<hi[0]<=9.40 and .92<lo[1]<hi[1]<3.0
    assert len([o for o in parts if '_Shelf' in o.name and '_Edge' not in o.name])==7
    assert bpy.data.objects[prefix+'Back'].active_material.name=='Mat_Q13_PoetaBlack'
    assert bpy.data.objects[prefix+'Shelf0_Edge'].active_material.name=='Mat_Q13_PoetaWoodEdge'
    for edge in (o for o in parts if o.name.endswith('_Edge')):
        body=bpy.data.objects[edge.name.removesuffix('_Edge')]
        assert bounds([edge])[1][0]-bounds([body])[1][0]>.001,('Coplanar wood/black faces',edge.name)
assert abs(cases[0][1][1]-cases[1][0][1])<.001,'Cases must touch'
leaf=bpy.data.objects['ProDoorLeaf_Bed2']
assert bounds([leaf])[0][1]-cases[1][1][1]>.6,'Bookcase conflicts with the open door'
for color in ('Black','Grey'):
    chair=[o for o in bpy.data.objects if o.name.startswith('Q11_Aeron'+color+'_')]
    assert bounds(chair)[0][0]-cases[0][1][0]>.65,'Bookcase/chair aisle too narrow'
assert len([o for o in bpy.data.objects if o.name.startswith('Q11_Equipment_')])==223
deps=bpy.context.evaluated_depsgraph_get()
hit,p,_,_,edge,_=bpy.context.scene.ray_cast(deps,Vector((9.6,1.359,1.8)),Vector((-1,0,0)),distance=.6)
assert hit and edge.active_material.name=='Mat_Q13_PoetaWoodEdge',('Wood edge hidden behind black panel',edge.name if edge else None)
for y in (1.3,1.8,2.4,3.0,4.0):
    hit,p,_,_,o,_=bpy.context.scene.ray_cast(deps,Vector((9.8,y,1.8)),Vector((0,0,-1)))
    assert hit and abs(p.z)<.03,('Bookcase blocks study aisle',y,o.name if o else None)
print('PASS Q13: adjacent 800/600 six-tier cases, black/wood edges, clear door and chair aisle, equipment retained')
