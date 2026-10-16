import bpy

def create_wall_box(name, x1, x2, y1, y2, z1=0.0, z2=2.30, col_name="Apt_OuterWalls"):
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

def build_outer_walls():
    walls = [
        # Party & Side Walls
        ("Wall_Party_West", -0.20, 0.0, -0.20, 10.415, 0.0, 2.30),
        ("Wall_Party_East", 9.865, 10.065, -0.20, 10.415, 0.0, 2.30),
        
        # North Wall Segments
        ("Wall_North_Segment1", 0.0, 1.30, 10.215, 10.415, 0.0, 2.30),
        ("Wall_North_DoorHeader", 1.30, 2.30, 10.215, 10.415, 2.10, 2.30),
        ("Wall_North_Segment2", 2.30, 9.865, 10.215, 10.415, 0.0, 2.30),
        
        # South Wall (Window Openings & Headers)
        ("Wall_South_Header_All", 0.0, 9.865, -0.20, 0.0, 2.20, 2.30),
        ("Wall_South_Sill_Bed3", 0.20, 2.30, -0.20, 0.0, 0.0, 0.80),
        ("Wall_South_Sill_Bed2", 2.70, 4.70, -0.20, 0.0, 0.0, 0.80),
        ("Wall_South_Col1", 2.40, 2.60, -0.20, 0.0, 0.0, 2.20),
        ("Wall_South_Col2", 4.80, 5.00, -0.20, 0.0, 0.0, 2.20),
        ("Wall_South_Col3", 7.65, 7.85, -0.20, 0.0, 0.0, 2.20),
    ]
    
    results = []
    for name, x1, x2, y1, y2, z1, z2 in walls:
        obj = create_wall_box(name, x1, x2, y1, y2, z1=z1, z2=z2, col_name="Apt_OuterWalls")
        results.append(
            f"{obj.name}: dims=({obj.dimensions.x:.3f}, {obj.dimensions.y:.3f}, {obj.dimensions.z:.3f})"
        )
    print("SUCCESS: Outer perimeter walls and party walls generated -> " + ", ".join(results))

build_outer_walls()
