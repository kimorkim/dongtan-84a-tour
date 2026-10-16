import bpy

def create_wall(name, x1, x2, y1, y2, z1=0.0, z2=2.30, col_name="Apt_InteriorWalls"):
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

def build_interior_walls():
    walls = [
        # Main transverse corridor wall separating south rooms from north zone (at Y = 5.18):
        ("Wall_Bed3_North_A", 0.0, 1.50, 5.08, 5.18, 0.0, 2.30),
        ("Wall_Bed3_North_DoorHeader", 1.50, 2.40, 5.08, 5.18, 2.10, 2.30),
        ("Wall_Bed3_North_B", 2.40, 2.50, 5.08, 5.18, 0.0, 2.30),
        ("Wall_Bed2_North_A", 2.50, 3.90, 5.08, 5.18, 0.0, 2.30),
        ("Wall_Bed2_North_DoorHeader", 3.90, 4.80, 5.08, 5.18, 2.10, 2.30),
        ("Wall_Bed2_North_B", 4.80, 4.90, 5.08, 5.18, 0.0, 2.30),
        
        # Partitions between bedrooms:
        ("Wall_Bed3_Bed2", 2.45, 2.55, 0.0, 5.08, 0.0, 2.30),
        ("Wall_Bed2_Living", 4.85, 4.95, 0.0, 5.08, 0.0, 2.30),
        ("Wall_Living_Bed1_A", 7.70, 7.80, 1.45, 4.00, 0.0, 2.30),
        ("Wall_Living_Bed1_DoorHeader", 7.70, 7.80, 4.00, 4.90, 2.10, 2.30),
        ("Wall_Living_Bed1_B", 7.70, 7.80, 4.90, 5.08, 0.0, 2.30),
        
        # Bed1 / Balcony1 inner sliding window partition (at Y = 1.45):
        ("Wall_Bed1_Balcony_Header", 7.75, 9.865, 1.40, 1.50, 2.20, 2.30),
        
        # Alpha Room partitions (X: [2.50, 4.90], Y: [5.18, 10.215]):
        ("Wall_Alpha_East_A", 4.85, 4.95, 5.18, 6.00, 0.0, 2.30),
        ("Wall_Alpha_East_DoorHeader", 4.85, 4.95, 6.00, 6.90, 2.10, 2.30),
        ("Wall_Alpha_East_B", 4.85, 4.95, 6.90, 10.215, 0.0, 2.30),
        
        # Bathroom 1 & Foyer partitions:
        ("Wall_Foyer_Bath1_Div", 2.45, 2.55, 5.18, 10.215, 0.0, 2.30),
        ("Wall_Bath1_DoorHeader", 1.40, 2.30, 7.00, 7.10, 2.10, 2.30),
        ("Wall_Bath1_South", 0.0, 1.40, 7.00, 7.10, 0.0, 2.30),
        ("Wall_Bath1_East", 2.30, 2.45, 7.00, 7.10, 0.0, 2.30),
        
        # Master Suite North zone (Bath 2 & Walk-in Dress room):
        ("Wall_DressRoom_South", 7.75, 9.865, 7.45, 7.55, 0.0, 2.30),
        ("Wall_Bath2_Div", 8.75, 8.85, 5.18, 7.45, 0.0, 2.30),
    ]
    
    results = []
    for name, x1, x2, y1, y2, z1, z2 in walls:
        obj = create_wall(name, x1, x2, y1, y2, z1=z1, z2=z2, col_name="Apt_InteriorWalls")
        results.append(
            f"{obj.name}: dims=({obj.dimensions.x:.3f}, {obj.dimensions.y:.3f}, {obj.dimensions.z:.3f})"
        )
    print(f"SUCCESS: {len(walls)} interior partition walls generated -> " + ", ".join(results))

if __name__ == "__main__" or True:
    build_interior_walls()
