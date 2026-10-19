import bpy
m = bpy.data.meshes.new("TestClear")
print("Has clear_geometry:", hasattr(m, 'clear_geometry'))
bpy.data.meshes.remove(m)
