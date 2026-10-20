import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mcp_client, json

code = '''
import bpy, os
scene = bpy.context.scene
cam = bpy.data.objects.get("Cam_Topdown")
assert cam, "Cam_Topdown missing"
d = cam.data
saved = (d.type, d.ortho_scale, tuple(cam.location), tuple(cam.rotation_euler))
d.type = "ORTHO"
d.ortho_scale = 19.0
cam.location = (7.5, 5.6, 15.0)
cam.rotation_euler = (0, 0, 0)
scene.camera = cam
scene.render.engine = "CYCLES"
scene.cycles.samples = 32
scene.cycles.use_denoising = True
scene.cycles.denoiser = "OPTIX"
scene.render.resolution_x = 1400
scene.render.resolution_y = 1000
out = os.path.abspath("renders/previews/plan_topdown.png")
os.makedirs(os.path.dirname(out), exist_ok=True)
scene.render.filepath = out
ceil = bpy.data.objects.get("Ceiling_Slab")
hsaved = ceil.hide_render if ceil else None
if ceil:
    ceil.hide_render = True
bpy.ops.render.render(write_still=True)
if ceil:
    ceil.hide_render = hsaved
d.type, d.ortho_scale = saved[0], saved[1]
cam.location, cam.rotation_euler = saved[2], saved[3]
print("PLAN SAVED " + out)
'''
res = mcp_client.send_blender_command('execute_code', {'code': code}, timeout=300.0)
print(json.dumps(res, ensure_ascii=False)[:2000])
