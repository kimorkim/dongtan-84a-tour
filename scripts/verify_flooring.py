"""Run in Blender: uniform wood level/UV, real texture detail, protected tile floors."""
import bpy
import numpy as np
from mathutils import Vector

bpy.context.view_layer.update()
deps = bpy.context.evaluated_depsgraph_get()
wood_floors = [o for o in bpy.data.objects if o.type == 'MESH' and
               (o.name == 'Exact_Floor' or o.name in ('Floor_AlphaRoom', 'Floor_Bedroom2',
                'Floor_Bedroom3', 'Floor_MasterBed', 'Floor_DressRoom'))]
heights = []
for x,y in [(6.3,5.0),(9.7,4.7),(9.7,4.1),(12.5,4.7),(12.5,4.1),
            (3.42,2.3),(1.8,5.4),(1.8,6.2),(9.1,6.7)]:
    surfaces = []
    for original in wood_floors:
        obj = original.evaluated_get(deps)
        origin = obj.matrix_world.inverted() @ Vector((x,y,.04))
        hit, point, _, face_index = obj.ray_cast(origin, Vector((0,0,-1)))
        if hit:
            surfaces.append((obj.matrix_world @ point).z)
            if original.name == 'Exact_Floor' and bpy.data.materials.get('Mat_Q9_LightOak'):
                face = obj.data.polygons[face_index]
                assert obj.data.materials[face.material_index].name == 'Mat_Q9_LightOak', 'Visible top uses subfloor material; slab normals inverted'
    assert surfaces, ('missing wood floor', x,y)
    heights.append(max(surfaces))
assert max(heights)-min(heights) < .001, ('Room patches cause height steps', heights)
floor = bpy.data.objects['Exact_Floor']
mat = bpy.data.materials.get('Mat_Q9_LightOak')
assert mat and any(m == mat for m in floor.data.materials), 'Continuous light oak finish missing'
uv = floor.data.uv_layers.get('FloorUV')
assert uv, 'Explicit world-aligned floor UV missing'
samples = []
for face in floor.data.polygons:
    for loop in face.loop_indices:
        p = floor.matrix_world @ floor.data.vertices[floor.data.loops[loop].vertex_index].co
        if abs(p.x-15.3)<.001 and abs(p.y-10.3)<.001:
            samples.append(uv.data[loop].uv)
assert samples and all(abs(v.x-5.1)<.001 and abs(v.y-9.903846)<.001 for v in samples), 'Wood direction/scale/phase mismatch'
images = [n.image for n in mat.node_tree.nodes if n.type == 'TEX_IMAGE']
assert len(images) == 3 and all(max(im.size) >= 2048 for im in images), '2K albedo/normal/roughness missing'
albedo = next(im for im in images if 'albedo' in im.name)
pixels = np.empty(len(albedo.pixels),np.float32)
albedo.pixels.foreach_get(pixels)
assert .60 < pixels[::4096].mean() < .69, 'Oak tone too bright/dark for the web lighting'
assert bpy.data.objects['Floor_Foyer'].active_material.name == 'Mat_Q7_Stone'
assert bpy.data.objects['Floor_CommonBath'].active_material.name == 'Mat_Q8_Grout'
assert bpy.data.objects.get('Q4_Floor_Balcony') and bpy.data.objects.get('Q6_UtilityFloor')
print('PASS FLOORING: continuous level/UV, corridor-aligned 130mm oak, 2K PBR, tile floors retained')
