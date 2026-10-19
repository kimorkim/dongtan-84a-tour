import mcp_client

code = """
import bpy

mat = bpy.data.materials.new("Test_PBR")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links
bsdf = nodes.get("Principled BSDF")

# Test creating procedural wood floor nodes
tex_coord = nodes.new('ShaderNodeTexCoord')
mapping = nodes.new('ShaderNodeMapping')
wave = nodes.new('ShaderNodeTexWave')
noise = nodes.new('ShaderNodeTexNoise')
color_ramp = nodes.new('ShaderNodeValToRGB')
bump = nodes.new('ShaderNodeBump')

links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])
links.new(mapping.outputs['Vector'], wave.inputs['Vector'])
links.new(wave.outputs['Color'], color_ramp.inputs['Fac'])
links.new(color_ramp.outputs['Color'], bsdf.inputs['Base Color'])

print("Procedural shader node setup test SUCCESS!")
"""

res = mcp_client.send_blender_command('execute_code', {'code': code})
print(res)
