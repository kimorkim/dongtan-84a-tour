import bpy

for col_name in ["Apt_Furnishings", "Apt_Windows_Doors", "Apt_Flooring_Zones"]:
    col = bpy.data.collections.get(col_name)
    if col:
        for o in col.objects:
            if o.type == 'MESH':
                zs = [v.co.z for v in o.data.vertices]
                if zs and max(zs) > 1.8:
                    xs = [v.co.x for v in o.data.vertices]
                    ys = [v.co.y for v in o.data.vertices]
                    print(f"HIGH_OBJ: {o.name} z_range=({round(min(zs), 2)}, {round(max(zs), 2)}) at x={round(sum(xs)/len(xs), 2)}, y={round(sum(ys)/len(ys), 2)}")
