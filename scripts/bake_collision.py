"""Bake simplified collision AABBs from the Blender model.

Grid probe (down-ray height test; walls briefly lifted +0.05z) over the
unit, then greedy-merge blocked cells into axis-aligned boxes.
Writes web/public/colliders.json in BLENDER coords (x=east, y=north);
three.js converts (x, y) -> (x, -y).

Run inside Blender (via MCP execute_code). Idempotent.
"""
import bpy
import json
import os
from mathutils import Vector

EXCLUDE_PREFIXES = ("ProDoorLeaf_", "ProDoorHandle_",
                    "Vent_ACRoom_")  # louver door to the AC room: passable like other leaves

CELL = 0.12
X0, X1 = 0.0, 15.5
Y0, Y1 = -0.6, 10.6
RAY_Z = 1.85
OPEN_Z = 0.03  # at/below this (floor tops) counts as walkable


def bake():
    sc = bpy.context.scene
    # Lift full-height walls +0.05 so rays starting inside them exit above
    # floor level (wall bottoms are coplanar with the floor at z=0, which
    # otherwise reads as open floor). Restored after baking.
    lifted = [o for o in bpy.data.objects
              if o.type == 'MESH' and (o.name.startswith("ExactWall_") or o.name.startswith("NewWall_"))]
    for o in lifted:
        o.location.z += 0.05
    hidden = [o for o in bpy.data.objects
              if o.type == 'MESH' and o.name.startswith(EXCLUDE_PREFIXES)]
    for o in hidden:
        o.hide_viewport = True
    deps = bpy.context.evaluated_depsgraph_get()
    deps.update()
    nx = int((X1 - X0) / CELL)
    ny = int((Y1 - Y0) / CELL)
    blocked = [[False] * nx for _ in range(ny)]
    n_blocked = 0
    for j in range(ny):
        for i in range(nx):
            x = X0 + (i + 0.5) * CELL
            y = Y0 + (j + 0.5) * CELL
            hit, loc, _n, _idx, _obj, _m = sc.ray_cast(
                deps, Vector((x, y, RAY_Z)), Vector((0, 0, -1)))
            if not hit:
                continue
            if loc.z > OPEN_Z or loc.z < -0.005:
                blocked[j][i] = True
                n_blocked += 1
    for o in lifted:
        o.location.z -= 0.05
    for o in hidden:
        o.hide_viewport = False
    print(f"grid {nx}x{ny} cell={CELL}: blocked cells={n_blocked}")

    # Greedy merge: row runs, then vertical merge of identical runs
    boxes = []  # (i0, j0, i1, j1) inclusive-exclusive
    for j in range(ny):
        i = 0
        while i < nx:
            if not blocked[j][i]:
                i += 1
                continue
            i0 = i
            while i < nx and blocked[j][i]:
                i += 1
            boxes.append([i0, j, i, j + 1])
    merged = True
    while merged:
        merged = False
        by_key = {}
        out = []
        for b in boxes:
            key = (b[0], b[2], b[3])
            if key in by_key:
                prev = by_key.pop(key)
                prev[3] = b[3]
                by_key[(prev[0], prev[2], prev[3])] = prev
                out[out.index(prev)] = prev
                merged = True
            else:
                by_key[(b[0], b[2], b[3])] = b
                out.append(b)
        boxes = out
    print(f"merged boxes: {len(boxes)}")

    def to_world(b):
        return [round(X0 + b[0] * CELL, 3), round(Y0 + b[1] * CELL, 3),
                round(X0 + b[2] * CELL, 3), round(Y0 + b[3] * CELL, 3)]

    data = {"cell": CELL, "x0": X0, "y0": Y0, "nx": nx, "ny": ny,
            "boxes": [to_world(b) for b in boxes]}
    data['dimensions_version'] = bpy.context.scene.get('Q12_dimensions_version', 0)
    data['sofa_version'] = 14 if bpy.context.scene.get('Q14_sofa') else 0
    data['living_finish_version'] = bpy.context.scene.get('Q15_living_finish', 0)
    data['kitchen_finish_version'] = bpy.context.scene.get('Q16_kitchen_finish', 0)

    here = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else os.getcwd()
    root = os.path.dirname(here) if os.path.basename(here) == "scripts" else here
    out_dir = os.path.join(root, "web", "public")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "colliders.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f)
    print(f"SUCCESS: colliders.json written ({os.path.getsize(out_path)} bytes)")

    # Sanity: spawn cell (foyer) must be open
    si, sj = int((12.33 - X0) / CELL), int((6.50 - Y0) / CELL)
    print(f"spawn cell foyer(12.33,6.50) blocked={blocked[sj][si]}")
    for label, px, py in [("living", 6.4, 3.2), ("kitchen-aisle", 6.3, 8.0),
                          ("bed-master", 2.5, 3.5), ("alpha", 10.3, 6.9),
                          ("bath-common", 14.2, 6.6), ("bath-master", 3.4, 6.9),
                          ("bed2", 10.5, 2.5), ("bed3", 13.5, 2.5),
                          ("door-bed2", 9.64, 4.33), ("door-cbath", 13.83, 5.65)]:
        ci, cj = int((px - X0) / CELL), int((py - Y0) / CELL)
        print(f"  {label}({px},{py}) blocked={blocked[cj][ci]}")


bake()
