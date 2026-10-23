"""Q16 regression checks use evaluated kitchen surfaces, not migration tables."""
import bpy
from mathutils import Vector
bpy.context.view_layer.update()
def bounds(name):
    o=bpy.data.objects[name]
    p=[o.matrix_world@Vector(v) for v in o.bound_box]
    return [min(v[i] for v in p) for i in range(3)],[max(v[i] for v in p) for i in range(3)]
# The dishwasher and sink doors must share the north cabinet front and stay clear of the west wall (x=5.075).
front=bounds('ProK_DoorN_SinkL')[0][1]
assert abs(bounds('ProK_Dishwasher_Door')[0][1]-front)<.025,'Dishwasher protrudes from sink cabinet run'
for n in ('Kitchen_Top_North','Kitchen_Base_North_EndL','Kitchen_Kick_North',
          'ProK_Dishwasher_Body','ProK_Dishwasher_Door','ProK_SplashNorth_L','Kitchen_Upper_NorthL_Box'):
    assert bounds(n)[0][0]>=5.075,f'{n} penetrates west kitchen wall (x < 5.075)'
assert bounds('ProK_Dishwasher_Body')[1][0]<=bounds('Kitchen_Sink_WallL')[0][0]-.02,'Dishwasher collides with sink bowl'
assert not any(o.name.startswith(('Q2_Pot','ProK_Oven_','Q16_Oven','ProK_DoorE_Corner')) for o in bpy.data.objects),'Duplicate pot or removed oven option still present'
assert bpy.data.objects.get('KitchenProp_Pot_Body'),'Missing stove pot'
for n in ('ProK_DoorE_L','ProK_DoorE_R'):
    lo,hi=bounds(n)
    assert abs(lo[0]-7.072)<.002 and abs(hi[0]-7.090)<.002 and abs(lo[2]-.10)<.002 and abs(hi[2]-.845)<.002,f'Invalid east cabinet door {n}'
sc=bpy.context.scene;deps=bpy.context.evaluated_depsgraph_get()
for x,y in [(5.15,9.55),(5.50,9.55),(6.13,9.53),(6.13,10.10),(6.7,9.80),(7.4,9.50),(7.4,9.40),(7.4,8.63),(7.4,8.58),(6.6,8.2)]:
    surfaces=[]
    for obj in bpy.data.objects:
        if not obj.name.startswith('Kitchen_Top_'): continue
        evaluated=obj.evaluated_get(deps); inverse=obj.matrix_world.inverted()
        hit,p,_,_=evaluated.ray_cast(inverse@Vector((x,y,.905)),inverse.to_3x3()@Vector((0,0,-1)),distance=.06)
        if hit: surfaces.append((obj.matrix_world@p).z)
    assert surfaces and abs(max(surfaces)-.89)<.004,('Broken countertop',x,y)
lo,hi=bounds('Kitchen_Sink_Bottom')
assert abs(hi[0]-lo[0]-.84)<.002 and abs(hi[1]-lo[1]-.44)<.002,'Sink distorted'
assert lo[0]>=5.455 and hi[0]<=6.655,'Sink outside kitchen window span'
# Sample the open right half of the bowl, clear of the removable rack and drain.
hit,p,_,_,obj,_=sc.ray_cast(deps,Vector((6.38,9.8,1.05)),Vector((0,0,-1)),distance=.5)
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
if sc.get('Q18_lightwave_oven')==1:
    from pathlib import Path
    import runpy
    runpy.run_path(str(Path(__file__).with_name('verify_lg_lightwave_oven.py')),run_name='__main__')
if sc.get('Q20_utility_turning_door')==1:
    from pathlib import Path
    import runpy
    runpy.run_path(str(Path(__file__).with_name('verify_utility_turning_door.py')),run_name='__main__')
print('PASS Q16: flush dishwasher, clear of west wall, single pot, east lower doors without oven, connected U tops, undistorted open sink, clear faucet/window, retained Q13-Q15')
