"""Q16 regression checks use evaluated kitchen surfaces, not migration tables."""
import bpy
from mathutils import Vector
bpy.context.view_layer.update()
def bounds(name):
    o=bpy.data.objects[name]
    p=[o.matrix_world@Vector(v) for v in o.bound_box]
    return [min(v[i] for v in p) for i in range(3)],[max(v[i] for v in p) for i in range(3)]
# The dishwasher and sink doors must share the north cabinet front.
front=bounds('ProK_DoorN_SinkL')[0][1]
assert abs(bounds('ProK_Dishwasher_Door')[0][1]-front)<.025,'Dishwasher protrudes from sink cabinet run'
sc=bpy.context.scene;deps=bpy.context.evaluated_depsgraph_get()
for x,y in [(5.15,9.55),(5.50,9.55),(6.05,9.53),(6.05,10.10),(6.7,9.80),(7.4,9.50),(7.4,9.40),(7.4,8.63),(7.4,8.58),(6.6,8.2)]:
    surfaces=[]
    for obj in bpy.data.objects:
        if not obj.name.startswith('Kitchen_Top_'): continue
        evaluated=obj.evaluated_get(deps); inverse=obj.matrix_world.inverted()
        hit,p,_,_=evaluated.ray_cast(inverse@Vector((x,y,.905)),inverse.to_3x3()@Vector((0,0,-1)),distance=.06)
        if hit: surfaces.append((obj.matrix_world@p).z)
    assert surfaces and abs(max(surfaces)-.89)<.004,('Broken countertop',x,y)
lo,hi=bounds('Kitchen_Sink_Bottom')
assert abs(hi[0]-lo[0]-.84)<.002 and abs(hi[1]-lo[1]-.44)<.002,'Sink distorted'
# Sample the open right half of the bowl, clear of the removable rack and drain.
hit,p,_,_,obj,_=sc.ray_cast(deps,Vector((6.28,9.8,1.05)),Vector((0,0,-1)),distance=.5)
assert hit and obj.name=='Kitchen_Sink_Bottom' and .66<p.z<.69,('Sink opening blocked',obj.name if obj else None)
assert bounds('Kitchen_Faucet_Riser')[1][1]<10.12,'Faucet embedded in north wall'
for n in ('Kitchen_Upper_NorthL_Box','Kitchen_Upper_NorthR_Box'):
    lo,hi=bounds(n)
    assert hi[1]<=10.146 and (hi[0]<=5.455 or lo[0]>=6.655),'Upper cabinet obstructs window'
assert abs(bounds('Kitchen_Top_East')[0][1]-bounds('Kitchen_Top_Peninsula')[1][1])<.001,'East/peninsula seam separated'
assert abs(bounds('Kitchen_Top_East')[1][1]-bounds('Kitchen_Top_North')[0][1])<.001,'North/east seam separated'
assert bounds('ProK_SplashNorth_Mid')[1][2]<=1.1201,'Backsplash covers window'
assert sc.get('Q15_living_finish')==1 and bpy.data.objects.get('Q13_Poeta800_Back')
stone=bpy.data.materials.get('Mat_Q16_Stone')
assert stone and min(min(e.color[:3]) for e in stone.node_tree.nodes['Color Ramp'].color_ramp.elements)>.70,'Kitchen stone has dark cloudy bands'
print('PASS Q16: flush dishwasher, connected U tops, undistorted open sink, clear faucet/window, retained Q13-Q15')
