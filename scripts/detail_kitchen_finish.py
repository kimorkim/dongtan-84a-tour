"""Q16 repair of current kitchen; never reruns the Q12 whole-unit migration.

Structure/window dimensions stay Q12. Cabinet depths and divisions are photo-based.
Fine sink/appliance parts are recovered from pre-Q12 geometry as rigid assemblies.
"""
from pathlib import Path
import sys, shutil, runpy
import bpy, bmesh
from mathutils import Vector, Matrix
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'scripts'))
import generate_high_detail_assets as A
backup=ROOT/'models/backups/apt_84a_photoreal_tour_before_kitchen_finish.blend'
if not backup.exists(): shutil.copy2(bpy.data.filepath,backup)
col=A.get_col('Apt_KitchenFinish')

def bounds(o):
    p=[o.matrix_world@Vector(v) for v in o.bound_box]
    return Vector(tuple(min(v[i] for v in p) for i in range(3))),Vector(tuple(max(v[i] for v in p) for i in range(3)))

def remove(o): bpy.data.objects.remove(o,do_unlink=True)

def box(name,x1,x2,y1,y2,z1,z2,mat='Mat_Cabinet_Cashmere',bevel=.001):
    old=bpy.data.objects.get(name)
    if old: remove(old)
    o=A.create_beveled_box(name,(x1+x2)/2,(y1+y2)/2,z1,x2-x1,y2-y1,z2-z1,
                          mat=bpy.data.materials[mat],col=col,bevel=bevel,seg=2)
    bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
    for p in o.data.polygons:p.use_smooth=False
    return o

# Only the damaged kitchen assemblies are replaced; structural meshes are untouched.
# Also remove duplicate Q2_Pot* and excluded built-in oven option (ProK_Oven_*).
prefixes=('Kitchen_Base_','Kitchen_Kick_','Kitchen_Top_','Kitchen_Upper_North',
          'ProK_DoorN','ProK_DoorE','ProK_DoorP','ProK_EndPanel','ProK_Splash','ProK_UpperEast','Q16_',
          'ProK_Oven_','Q2_Pot')
fine=('Kitchen_Sink_','Kitchen_Faucet_','Kitchen_Induction_','KitchenProp_Pot_',
      'ProK_Hood_','ProK_Dishwasher_')
for o in list(bpy.data.objects):
    if o.name.startswith(prefixes+fine):remove(o)

# Closed sink/appliance assemblies must translate together, without per-part scaling.
with bpy.data.libraries.load(str(ROOT/'models/backups/apt_84a_photoreal_tour_before_dimensions.blend'),link=False) as (src,dst):
    dst.objects=[n for n in src.objects if n.startswith(fine)]
loaded=dst.objects
for o in loaded:
    col.objects.link(o)
    if o.type=='MESH':
        for i,m in enumerate(o.data.materials):
            if m:
                canonical=bpy.data.materials.get(m.name.rsplit('.',1)[0])
                if canonical:o.data.materials[i]=canonical
bpy.context.view_layer.update()

def shift_group(prefix,delta):
    for o in loaded:
        if o.name.startswith(prefix):o.matrix_world=Matrix.Translation(delta)@o.matrix_world

def align_group(prefix,anchor,axis,target,centre=False):
    bpy.context.view_layer.update();lo,hi=bounds(bpy.data.objects[anchor])
    delta=[0,0,0];delta[axis]=target-((lo[axis]+hi[axis])/2 if centre else lo[axis])
    shift_group(prefix,delta)

# Align clear of west partition wall ExactWall_10 (east finished face x=5.075):
# - Left end panel: x=5.080..5.095
# - Dishwasher (590mm): x=5.095..5.685 (center x=5.390)
# - Sink bowl (840mm): x=5.715..6.555 (within 1200mm kitchen window x=5.455..6.655)
shift_group(('Kitchen_Sink_','Kitchen_Faucet_'),(-.015,.10,0))
align_group('ProK_Dishwasher_','ProK_Dishwasher_Door',1,9.482)
align_group('ProK_Dishwasher_','ProK_Dishwasher_Door',0,5.390,True)
align_group(('Kitchen_Induction_','KitchenProp_Pot_'),'Kitchen_Induction_Glass',0,7.40,True)
align_group(('Kitchen_Induction_','KitchenProp_Pot_'),'Kitchen_Induction_Glass',1,9.03,True)
align_group('ProK_Hood_','ProK_Hood_Body',1,9.03,True)
bpy.context.view_layer.update();hi=bounds(bpy.data.objects['ProK_Hood_Body'])[1]
shift_group('ProK_Hood_', (7.725-hi.x,0,0))
for n in ('ProK_Hood_Fascia','ProK_Hood_Body'):
    bpy.data.objects[n].data.materials[0]=bpy.data.materials['Mat_Q2_BlackGlass']

# Photo shows pale stone; isolate it from the shared living/bath marble material.
stone='Mat_Q16_Stone'
material=bpy.data.materials.get(stone)
if material is None:
    material=bpy.data.materials['Mat_Marble_White'].copy();material.name=stone
nodes=material.node_tree.nodes
ramp=nodes['Color Ramp'].color_ramp
for element in ramp.elements:
    value=.78+.10*element.position
    element.color=(value,value-.01,value-.025,1)
nodes['Mapping'].inputs['Scale'].default_value=(.65,3.5,1)
nodes['Bump'].inputs['Strength'].default_value=.025
nodes['Bump'].inputs['Distance'].default_value=.001
# Shared finished faces: west x5.075, north y10.145, east x7.735; 5-10mm clearance for stone.
top=box('Kitchen_Top_North',5.080,7.725,9.485,10.135,.86,.89,stone,0)
# One closed ring avoids four independently calibrated rim segments and their gaps.
cutter=box('Q16_SinkCutter',5.730,6.540,9.605,10.015,.60,1.05,bevel=0)
mod=top.modifiers.new('Undermount opening','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
bpy.context.view_layer.objects.active=top
bpy.ops.object.modifier_apply(modifier=mod.name);remove(cutter)
bev=top.modifiers.new('Stone edge','BEVEL');bev.width=.0008;bev.segments=2
box('Kitchen_Top_East',7.075,7.725,8.595,9.485,.86,.89,stone,0)
box('Kitchen_Top_Peninsula',6.44,7.725,7.945,8.595,.86,.89,stone,0)
# Carcasses are hollow around the sink; east lower cabinet is a full storage cabinet (no oven).
box('Kitchen_Base_North_EndL',5.080,5.095,9.505,10.125,.07,.86)
box('Kitchen_Base_Sink_Floor',5.690,6.590,9.505,10.125,.07,.09)
for name,x in [('DivL',5.690),('DivR',6.570)]:
    box('Kitchen_Base_Sink_'+name,x,x+.02,9.505,10.125,.09,.86)
box('Kitchen_Base_North_R',6.590,7.725,9.505,10.125,.07,.86)
for i,(a,b) in enumerate([(5.690,6.138),(6.141,6.589),(6.592,7.073)]):
    name=['ProK_DoorN_SinkL','ProK_DoorN_SinkR','ProK_DoorN_R1'][i]
    box(name,a,b,9.482,9.500,.10,.845)
# East lower cabinet under cooktop: matching cashmere cabinet carcass and two storage doors.
box('Kitchen_Base_East',7.095,7.725,8.595,9.505,.07,.86)
for tag,(a,b) in [('L',(8.597,9.037)),('R',(9.040,9.480))]:
    box('ProK_DoorE_'+tag,7.072,7.090,a,b,.10,.845)
box('Kitchen_Base_Pen',6.46,7.725,7.965,8.595,.07,.86)
for i in range(2):
    a=6.46+i*.6325
    box('ProK_DoorP'+str(i+1),a+.002,a+.6305,7.947,7.965,.10,.845)
box('ProK_EndPanelW',6.44,6.46,7.965,8.595,.07,.86)
for name,coords in [('North',(5.095,7.725,9.54,9.56)),('East',(7.13,7.15,8.595,9.54)),('Pen',(6.49,7.725,8.00,8.02))]:
    box('Kitchen_Kick_'+name,*coords,0,.07,'Mat_AC_Grill',0)

# Window remains the Q12 1200x1150 opening; stone and uppers stop at its jambs and west wall x5.080.
for tag,a,b,h in [('L',5.080,5.455,1.55),('Mid',5.455,6.655,1.12),('R',6.655,7.725,1.55)]:
    box('ProK_SplashNorth_'+tag,a,b,10.115,10.145,.89,h,stone,0)
box('ProK_SplashEast',7.705,7.735,8.595,10.115,.89,1.55,stone,0)
for tag,a,b in [('L',5.080,5.445),('R',6.665,7.405)]:
    box('Kitchen_Upper_North'+tag+'_Box',a,b,9.805,10.145,1.55,2.29)
    box('Kitchen_Upper_North'+tag+'_LED_Strip',a+.02,b-.02,9.825,10.10,1.535,1.549,'Mat_Light_Warm_Strip')
    if tag=='R':
        box('Q16_UpperNorth_Division',(a+b)/2-.001,(a+b)/2+.001,9.804,9.806,1.56,2.28,'Mat_AC_Grill',0)
box('ProK_UpperEast',7.405,7.735,8.595,10.145,1.55,2.29)
for i,(a,b) in enumerate([(8.60,8.73),(9.33,9.79)]):
    box('Q16_UpperEast_LED'+str(i),7.425,7.69,a,b,1.535,1.549,'Mat_Light_Warm_Strip')
for i,y in enumerate([8.73,9.33,9.79]):
    box('Q16_UpperEast_Division'+str(i),7.404,7.406,y-.001,y+.001,1.56,2.28,'Mat_AC_Grill',0)
# Keep existing staging, bring the leaning board clear of the finished wall.
bpy.context.view_layer.update()
for o in bpy.data.objects:
    if o.name.startswith(('KitchenProp_Board','KitchenProp_Rack_','Q2_SinkPlant')) and o.type=='MESH':
        lo,hi=bounds(o)
        if hi.y>10.105:o.location.y-=hi.y-10.105
bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
bpy.context.scene['Q16_kitchen_finish']=1
bpy.context.view_layer.update()
runpy.run_path(str(ROOT/'scripts/verify_kitchen_finish.py'))
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'apt_84a_photoreal_tour.blend'))
print('Q16 saved current master; other rooms and Q12 structure retained')
