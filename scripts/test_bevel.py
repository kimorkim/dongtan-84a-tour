import mcp_client

code = """
import bpy

bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0,0,0))
cube = bpy.context.active_object
cube.name = "Test_Bevel_Cube"

bev = cube.modifiers.new("Bevel", 'BEVEL')
bev.width = 0.02
bev.segments = 3

# Test shading
for p in cube.data.polygons:
    p.use_smooth = True

bpy.data.objects.remove(cube, do_unlink=True)
print("Bevel & Smooth test SUCCESS!")
"""

res = mcp_client.send_blender_command('execute_code', {'code': code})
print(res)
