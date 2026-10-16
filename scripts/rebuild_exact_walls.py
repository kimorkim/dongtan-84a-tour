import bpy
import json
import os
import math

def build_exact():
    # 1. Hide old mismatched collections
    for old_col_name in ["Apt_Floors", "Apt_OuterWalls", "Apt_InteriorWalls", "Apt_Openings"]:
        c = bpy.data.collections.get(old_col_name)
        if c:
            c.hide_viewport = True
            c.hide_render = True

    # 2. Create new collection for corrected layout
    col_name = "Apt_Corrected_Structure"
    col = bpy.data.collections.get(col_name)
    if not col:
        col = bpy.data.collections.new(col_name)
        bpy.context.scene.collection.children.link(col)
    else:
        # Clear previous objects in this collection if any
        for obj in list(col.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
            
    col.hide_viewport = False
    col.hide_render = False

    # 3. Load polygon contours
    with open("polys.json", "r") as f:
        polys_data = json.load(f)

    wall_height = 2.30

    for idx, poly in enumerate(polys_data):
        if len(poly) < 3:
            continue
        mesh = bpy.data.meshes.new(f"ExactWall_{idx+1}_Mesh")
        obj = bpy.data.objects.new(f"ExactWall_{idx+1}", mesh)
        col.objects.link(obj)

        verts = []
        n = len(poly)
        # bottom vertices (z = 0.0)
        for x, y in poly:
            verts.append((x, y, 0.0))
        # top vertices (z = wall_height)
        for x, y in poly:
            verts.append((x, y, wall_height))

        faces = []
        # side quad faces
        for i in range(n):
            next_i = (i + 1) % n
            faces.append((i, next_i, next_i + n, i + n))

        # top cap polygon
        faces.append(list(range(n, 2 * n)))
        # bottom cap polygon
        faces.append(list(reversed(range(n))))

        mesh.from_pydata(verts, [], faces)
        mesh.update()

    # 4. Create base floor slab for the whole apartment footprint
    floor_mesh = bpy.data.meshes.new("Exact_Floor_Mesh")
    floor_obj = bpy.data.objects.new("Exact_Floor", floor_mesh)
    col.objects.link(floor_obj)
    # Extents: X: 0.0 to 15.3, Y: 0.0 to 10.3, Z: -0.15 to 0.0
    f_verts = [
        (0.0, 0.0, -0.15), (15.3, 0.0, -0.15), (15.3, 10.3, -0.15), (0.0, 10.3, -0.15),
        (0.0, 0.0, 0.0), (15.3, 0.0, 0.0), (15.3, 10.3, 0.0), (0.0, 10.3, 0.0)
    ]
    f_faces = [
        (0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1),
        (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)
    ]
    floor_mesh.from_pydata(f_verts, [], f_faces)
    floor_mesh.update()

    # 5. Position camera for top-down orthographic preview
    cam_name = "Cam_Corrected_Topdown"
    cam_data = bpy.data.cameras.get(cam_name) or bpy.data.cameras.new(cam_name)
    cam_obj = bpy.data.objects.get(cam_name) or bpy.data.objects.new(cam_name, cam_data)
    if cam_obj.name not in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.link(cam_obj)

    cam_data.type = 'ORTHO'
    cam_data.ortho_scale = 17.5
    cam_obj.location = (7.65, 5.15, 20.0)
    cam_obj.rotation_euler = (0.0, 0.0, 0.0)

    bpy.context.scene.camera = cam_obj
    bpy.context.scene.render.resolution_x = 1280
    bpy.context.scene.render.resolution_y = 960
    bpy.context.scene.render.filepath = os.path.abspath("exact_structure_preview.png")
    bpy.ops.render.render(write_still=True)
    print("SUCCESS: Exact structure generated and preview rendered to exact_structure_preview.png")

build_exact()
