"""Q15 checks the saved living-room finish and retained furnishings."""
from pathlib import Path
import runpy
import bpy
from mathutils import Vector
bpy.context.view_layer.update()
def bounds(name):
    o=bpy.data.objects[name]
    p=[o.matrix_world@Vector(v) for v in o.bound_box]
    return [min(v[i] for v in p) for i in range(3)],[max(v[i] for v in p) for i in range(3)]
assert bpy.context.scene.get('Q15_living_finish')==1
assert not any(o.name.startswith(('Q2_Coffee','Q2_Pouf','Q2_Living_Rug','Q2_Rug_Shape','Curtain_Living','Q2_Sheer_Living')) for o in bpy.data.objects)
lo,hi=bounds('Living_ArtWall_Tile')
assert abs(lo[1]-.92)<.001 and abs(hi[1]-4.75)<.001 and abs(hi[2]-2.3)<.001
for name,x0,x1 in [('Win_Living_Sill',4.755,8.355),('Win_Living_Head',4.755,8.355)]:
    lo,hi=bounds(name); assert abs(lo[0]-x0)<.001 and abs(hi[0]-x1)<.001
lo,hi=bounds('Win_Living_Glass1'); assert hi[0]-lo[0]>2.0
for name in ('Q15_Curtain_Left','Q15_Curtain_Right'):
    lo,hi=bounds(name); assert hi[1]-lo[1]>.05
assert bounds('Q15_Curtain_Left')[1][0]<4.81
assert bounds('Q15_Curtain_Right')[0][0]>8.30
rail=[bounds(o.name) for o in bpy.data.objects if o.name.startswith('Q2_Rail_Living_')]
assert max(hi[1] for lo,hi in rail)<.72 and abs(max(hi[2] for lo,hi in rail)-.83)<.001
im=bpy.data.images['Q2_Landscape']
assert im.packed_file and max(im.pixels[0:4096])>.3
for o in bpy.data.objects:
    if o.name.startswith('Q2_Landscape_') and o.type=='MESH':
        samples=[((o.matrix_world@o.data.vertices[l.vertex_index].co).z,o.data.uv_layers.active.data[l.index].uv.y) for l in o.data.loops]
        assert max(samples)[1]>.99 and min(samples)[1]<.01,'Landscape sky must be above ground'
assert bpy.data.objects.get('Q14_Brest_Seat0') and bpy.data.objects.get('Q13_Poeta800_Back')
if bpy.context.scene.get('Q17_tv_stand'):
    runpy.run_path(str(Path(__file__).with_name('verify_living_tv_stand.py')),run_name='__main__')
if bpy.context.scene.get('Q19_living_soundbar'):
    runpy.run_path(str(Path(__file__).with_name('verify_living_soundbar.py')),run_name='__main__')
print('PASS Q15: clear centre, full artwall, gathered curtains, wide centre sash, exterior rail, packed daylight backdrop')
