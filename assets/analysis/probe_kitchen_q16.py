import bpy,json
from mathutils import Vector
rows=[]
for o in bpy.data.objects:
 if o.type=='MESH' and (o.name.startswith(('Kitchen','ProK_','Q2_Kitchen','Win_Kitchen','ExactWall_'))):
  p=[o.matrix_world@Vector(v) for v in o.bound_box]
  rows.append({'name':o.name,'lo':[round(min(v[i] for v in p),4) for i in range(3)],'hi':[round(max(v[i] for v in p),4) for i in range(3)],'mat':[m.name for m in o.data.materials if m]})
open('assets/analysis/q16_kitchen_before.json','w').write(json.dumps(rows,indent=2))
sc=bpy.context.scene
sc.render.engine='CYCLES';sc.cycles.samples=8;sc.cycles.use_denoising=True
sc.render.resolution_x=1000;sc.render.resolution_y=800;sc.render.resolution_percentage=100
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
sc.cycles.device='GPU'
d=bpy.data.cameras.new('Probe');o=bpy.data.objects.new('Probe',d);sc.collection.objects.link(o)
o.location=(6.25,8.0,1.6);o.rotation_euler=(Vector((6.25,9.75,1.15))-o.location).to_track_quat('-Z','Y').to_euler();d.lens=18
sc.camera=o;sc.render.filepath=r'C:/Users/tamarand/orca/projects/apt/renders/review/q16_kitchen_before.png';bpy.ops.render.render(write_still=True)

