import bpy

mat = bpy.data.materials.new("TempBrick")
mat.use_nodes = True
b = mat.node_tree.nodes.new('ShaderNodeTexBrick')
print("BRICK_INPUTS:", [i.name for i in b.inputs])
print("BRICK_OUTPUTS:", [o.name for o in b.outputs])
bpy.data.materials.remove(mat)
