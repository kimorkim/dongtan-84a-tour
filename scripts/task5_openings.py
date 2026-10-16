import bpy

def create_block(name, x1, x2, y1, y2, z1, z2, col_name="Apt_Openings"):
    col = bpy.data.collections.get(col_name)
    if not col:
        col = bpy.data.collections.new(col_name)
        bpy.context.scene.collection.children.link(col)
        
    # Remove existing object and unlinked mesh if present
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
    
    verts = [
        (x1, y1, z1),  # 0: SW bottom
        (x2, y1, z1),  # 1: SE bottom
        (x2, y2, z1),  # 2: NE bottom
        (x1, y2, z1),  # 3: NW bottom
        (x1, y1, z2),  # 4: SW top
        (x2, y1, z2),  # 5: SE top
        (x2, y2, z2),  # 6: NE top
        (x1, y2, z2),  # 7: NW top
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

def build_openings():
    # 6 Door leaves (thickness ~0.04m, height 2.10m)
    doors = [
        ("Door_Entrance", 1.35, 2.25, 10.28, 10.34, 0.0, 2.10),
        ("Door_Bed3", 1.55, 2.35, 5.11, 5.15, 0.0, 2.10),
        ("Door_Bed2", 3.95, 4.75, 5.11, 5.15, 0.0, 2.10),
        ("Door_Bed1", 7.73, 7.77, 4.05, 4.85, 0.0, 2.10),
        ("Door_Alpha", 4.88, 4.92, 6.05, 6.85, 0.0, 2.10),
        ("Door_Bath1", 1.45, 2.25, 7.03, 7.07, 0.0, 2.10),
    ]

    # 6 Window blocks (thickness ~0.04m)
    windows = [
        ("Window_LivingRoom", 5.05, 7.60, -0.12, -0.08, 0.0, 2.20),
        ("Window_Balcony1", 7.85, 9.75, -0.12, -0.08, 0.0, 2.20),
        ("Window_Bed2", 2.75, 4.65, -0.12, -0.08, 0.80, 2.10),
        ("Window_Bed3", 0.25, 2.25, -0.12, -0.08, 0.80, 2.10),
        ("Window_Kitchen_North", 5.50, 6.70, 10.28, 10.32, 1.10, 1.70),
        ("Window_DressRoom_North", 8.20, 9.40, 10.28, 10.32, 1.10, 1.70),
    ]

    results = []
    for name, x1, x2, y1, y2, z1, z2 in doors + windows:
        obj = create_block(name, x1, x2, y1, y2, z1, z2, col_name="Apt_Openings")
        results.append(
            f"{obj.name}: dims=({obj.dimensions.x:.3f}, {obj.dimensions.y:.3f}, {obj.dimensions.z:.3f})"
        )
    print(f"SUCCESS: {len(doors) + len(windows)} opening blocks ({len(doors)} doors, {len(windows)} windows) generated -> " + ", ".join(results))

if __name__ == "__main__" or True:
    build_openings()
