import bpy

for col_name in ["Apt_Furnishings", "Apt_Windows_Doors", "Apt_Flooring_Zones"]:
    col = bpy.data.collections.get(col_name)
    if col:
        for o in col.objects:
            if o.location.z > 1.8:
                print(f"HIGH_OBJ: {o.name} at loc={tuple(round(v, 2) for v in o.location)} dim={tuple(round(v, 2) for v in o.dimensions)}")
