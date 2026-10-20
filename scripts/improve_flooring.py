"""Q9: one continuous pale-oak floor; explicit UV and export-ready 2K PBR.

Run after Q8. Keeps the original structural slab, exterior void and all tile floors.
shortcut: 130mm boards and pale-oak tint are photo-based assumptions, not a product specification.
"""
import os
import runpy
import shutil
import bmesh
import bpy
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
backup = os.path.join(ROOT, 'models/backups/apt_84a_photoreal_tour_before_flooring.blend')
if not os.path.exists(backup):
    shutil.copy2(bpy.data.filepath, backup)

def source(kind, color):
    filename = f'laminate_floor_02_{kind}_2k.jpg'
    im = bpy.data.images.load(os.path.join(ROOT, 'assets/textures/laminate_floor_02', filename), check_existing=True)
    im.colorspace_settings.name = 'sRGB' if color else 'Non-Color'
    w,h = im.size
    pixels = np.empty(w*h*4, np.float32)
    im.pixels.foreach_get(pixels)
    return pixels.reshape(h,w,4).copy()

def baked(name, pixels, color):
    image_name = 'Q9_'+name
    old = bpy.data.images.get(image_name)
    if old:
        bpy.data.images.remove(old, do_unlink=True)
    h,w,_ = pixels.shape
    im = bpy.data.images.new(image_name, width=w, height=h, alpha=False)
    im.colorspace_settings.name = 'sRGB' if color else 'Non-Color'
    im.pixels.foreach_set(np.clip(pixels,0,1).ravel())
    im.filepath_raw = os.path.join(ROOT, 'assets/textures_export', image_name.lower()+'.jpg')
    im.file_format = 'JPEG'
    im.save()
    # Reload the actual exported JPEG so Blender and glTF use identical encoded pixels.
    path = im.filepath_raw
    bpy.data.images.remove(im)
    im = bpy.data.images.load(path, check_existing=False)
    im.name = image_name
    im.colorspace_settings.name = 'sRGB' if color else 'Non-Color'
    im.pack()
    return im

albedo = source('diff', True)
rgb = albedo[:,:,:3].copy()
lum = rgb @ np.array((.2126,.7152,.0722),np.float32)
albedo[:,:,:3] = np.array((.65,.625,.575),np.float32) + (lum-lum.mean())[:,:,None]*.65 + (rgb-lum[:,:,None])*.03
normal = source('nor_dx', False)
normal[:,:,1] = 1-normal[:,:,1]
rough = source('rough', False)
rough[:,:,:3] = np.clip(.62+(rough[:,:,:3]-rough[:,:,:3].mean())*.25,.50,.74)
images = [baked('oak_albedo',albedo,True), baked('oak_normal',normal,False), baked('oak_roughness',rough,False)]

mat = bpy.data.materials.get('Mat_Q9_LightOak') or bpy.data.materials.new('Mat_Q9_LightOak')
mat.use_nodes = True
mat.diffuse_color = (.51,.46,.38,1)
nodes, links = mat.node_tree.nodes, mat.node_tree.links
nodes.clear()
shader = nodes.new('ShaderNodeBsdfPrincipled')
shader.inputs['Roughness'].default_value = .62
shader.inputs['Metallic'].default_value = 0
shader.inputs['Specular IOR Level'].default_value = .35
uv_node = nodes.new('ShaderNodeUVMap')
uv_node.uv_map = 'FloorUV'
textures = []
for im in images:
    node = nodes.new('ShaderNodeTexImage')
    node.image = im
    node.interpolation = 'Linear'
    links.new(uv_node.outputs['UV'],node.inputs['Vector'])
    textures.append(node)
links.new(textures[0].outputs['Color'],shader.inputs['Base Color'])
normal_node = nodes.new('ShaderNodeNormalMap')
normal_node.uv_map = 'FloorUV'
normal_node.inputs['Strength'].default_value = .20
links.new(textures[1].outputs['Color'],normal_node.inputs['Color'])
links.new(normal_node.outputs['Normal'],shader.inputs['Normal'])
links.new(textures[2].outputs['Color'],shader.inputs['Roughness'])
out = nodes.new('ShaderNodeOutputMaterial')
links.new(shader.outputs['BSDF'],out.inputs['Surface'])

# Remove offset wood patches; the original slab already covers these rooms and their doorways.
for name in ('Floor_AlphaRoom','Floor_Bedroom2','Floor_Bedroom3','Floor_MasterBed','Floor_DressRoom'):
    obj = bpy.data.objects.get(name)
    if obj:
        bpy.data.objects.remove(obj,do_unlink=True)
floor = bpy.data.objects['Exact_Floor']
bm = bmesh.new()
bm.from_mesh(floor.data)
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
bm.to_mesh(floor.data)
bm.free()
floor.data.update()
subfloor = bpy.data.materials.get('Mat_Q9_Subfloor') or bpy.data.materials.new('Mat_Q9_Subfloor')
subfloor.diffuse_color = (.16,.15,.14,1)
floor.data.materials.clear()
floor.data.materials.append(mat)
floor.data.materials.append(subfloor)
uv = floor.data.uv_layers.get('FloorUV') or floor.data.uv_layers.new(name='FloorUV')
floor.data.uv_layers.active = uv
for face in floor.data.polygons:
    face.material_index = 0 if face.normal.z > .5 else 1
    for loop in face.loop_indices:
        p = floor.matrix_world @ floor.data.vertices[floor.data.loops[loop].vertex_index].co
        # Eight board courses in the source atlas -> 1.04/8 = 130mm width.
        uv.data[loop].uv = (p.x/3.0,p.y/1.04)
floor.data.update()
bpy.context.view_layer.update()
runpy.run_path(os.path.join(ROOT,'scripts/verify_flooring.py'))
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print('Q9 FLOORING SAVED; five overlapping room patches removed, tile finishes preserved',flush=True)
