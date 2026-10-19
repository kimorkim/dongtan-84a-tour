import bpy

for o in bpy.data.objects:
    if o.type == 'MESH':
        zs = [v.co.z for v in o.data.vertices]
        if zs and max(zs) > 1.2:
            xs = [v.co.x for v in o.data.vertices]
            ys = [v.co.y for v in o.data.vertices]
            cx = sum(xs)/len(xs) + o.location.x
            cy = sum(ys)/len(ys) + o.location.y
            cz = sum(zs)/len(zs) + o.location.z
            print(f"ALL_OBJ: {o.name} in col={[c.name for c in o.users_collection]} at ({round(cx, 2)}, {round(cy, 2)}, {round(cz, 2)}) mat={[m.name for m in o.data.materials]}")
