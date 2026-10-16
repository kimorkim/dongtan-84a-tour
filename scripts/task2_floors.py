import bpy

def create_floor_slab(name, min_x, max_x, min_y, max_y, thickness=0.15, z_top=0.0):
    col = bpy.data.collections.get("Apt_Floors")
    if not col:
        col = bpy.data.collections.new("Apt_Floors")
        bpy.context.scene.collection.children.link(col)
    
    # Remove existing object and its mesh data if present
    existing_obj = bpy.data.objects.get(name)
    if existing_obj:
        existing_mesh = existing_obj.data
        bpy.data.objects.remove(existing_obj, do_unlink=True)
        if existing_mesh and existing_mesh.users == 0:
            bpy.data.meshes.remove(existing_mesh)
            
    existing_mesh = bpy.data.meshes.get(f"{name}_Mesh")
    if existing_mesh and existing_mesh.users == 0:
        bpy.data.meshes.remove(existing_mesh)
        
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    
    z_bottom = z_top - thickness
    verts = [
        (min_x, min_y, z_bottom),  # 0: bottom south-west
        (max_x, min_y, z_bottom),  # 1: bottom south-east
        (max_x, max_y, z_bottom),  # 2: bottom north-east
        (min_x, max_y, z_bottom),  # 3: bottom north-west
        (min_x, min_y, z_top),     # 4: top south-west
        (max_x, min_y, z_top),     # 5: top south-east
        (max_x, max_y, z_top),     # 6: top north-east
        (min_x, max_y, z_top),     # 7: top north-west
    ]
    faces = [
        (0, 3, 2, 1),  # Bottom (-Z)
        (4, 5, 6, 7),  # Top (+Z)
        (0, 1, 5, 4),  # South (-Y)
        (1, 2, 6, 5),  # East (+X)
        (2, 3, 7, 6),  # North (+Y)
        (3, 0, 4, 7),  # West (-X)
    ]
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    return obj

def build_floors():
    # 84A floor plan layout
    # Total width: 0.0 to 9.865m
    # Total depth: 0.0 to 10.215m
    floors = [
        ("Floor_Living_Dining", 4.90, 7.75, 1.45, 10.215),
        ("Floor_Bed1", 7.75, 9.865, 1.45, 5.18),
        ("Floor_Balcony1", 7.75, 9.865, 0.0, 1.45),
        ("Floor_Bed2", 2.50, 4.90, 0.0, 5.18),
        ("Floor_Bed3", 0.0, 2.50, 0.0, 5.18),
        ("Floor_AlphaRoom", 2.50, 4.90, 5.18, 10.215),
        ("Floor_Entrance_Bath1", 0.0, 2.50, 5.18, 10.215),
        ("Floor_MasterSuite_North", 7.75, 9.865, 5.18, 10.215),
    ]
    results = []
    for name, x1, x2, y1, y2 in floors:
        obj = create_floor_slab(name, x1, x2, y1, y2)
        results.append(
            f"{obj.name}: dims=({obj.dimensions.x:.3f}, {obj.dimensions.y:.3f}, {obj.dimensions.z:.3f})"
        )
    print("SUCCESS: Floors created -> " + ", ".join(results))

build_floors()
