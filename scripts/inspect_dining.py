import bpy

for o in bpy.data.objects:
    if o.type == 'MESH':
        xs = [v.co.x for v in o.data.vertices]
        ys = [v.co.y for v in o.data.vertices]
        zs = [v.co.z for v in o.data.vertices]
        if xs and ys and zs:
            cx = sum(xs)/len(xs) + o.location.x
            cy = sum(ys)/len(ys) + o.location.y
            cz = sum(zs)/len(zs) + o.location.z
            if 6.0 <= cx <= 7.2 and 4.2 <= cy <= 5.8:
                print(f"OBJ: {o.name} at ({round(cx, 2)}, {round(cy, 2)}, {round(cz, 2)}) z_range=({round(min(zs)+o.location.z, 2)}, {round(max(zs)+o.location.z, 2)}) mat={[m.name for m in o.data.materials]}")
