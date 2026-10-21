import bpy
for o in bpy.data.objects:
    if o.type=='CAMERA':
        print('CAMERA',o.name,tuple(o.location),tuple(o.matrix_world.translation),tuple(o.rotation_euler),flush=True)
