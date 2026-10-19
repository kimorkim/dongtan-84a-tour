import bpy

mat_wall = bpy.data.materials.get("Mat_Wall_Interior")
mat_cap = bpy.data.materials.get("Mat_Wall_Cap")

col = bpy.data.collections.get("Apt_Corrected_Structure")
if col:
    for obj in col.objects:
        if obj.type == 'MESH' and obj.name.startswith("ExactWall_"):
            obj.data.materials.clear()
            obj.data.materials.append(mat_wall) # index 0
            obj.data.materials.append(mat_cap)  # index 1
            
            # The top face is polygon index: len(polygons) - 2 (since faces[-2] was top, faces[-1] was bottom)
            # Or check normal: if normal.z > 0.9, it's the top face!
            for poly in obj.data.polygons:
                if poly.normal.z > 0.8:
                    poly.material_index = 1
                else:
                    poly.material_index = 0
            obj.data.update()

# Floor
floor = bpy.data.objects.get("Exact_Floor")
if floor:
    floor.data.materials.clear()
    mat_light_wood = bpy.data.materials.get("Mat_Wood_LightPlank")
    floor.data.materials.append(mat_light_wood)

print("Walls and Floor materials assigned with top cap!")
