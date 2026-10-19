"""Add baseboards along interior wall bases (idempotent).

Walks ExactWall/NewWall/SillPatch side faces reaching the floor, builds
70mm skirting (half-embedded, joined mesh). Skips bath-tile faces,
narrow jamb slivers, and exterior faces.
Run inside Blender.
"""
import bpy
import math
from mathutils import Vector
import bmesh
import mathutils

scene = bpy.context.scene
PREFIXES = ("ExactWall", "NewWall", "SillPatch")


def frame_material():
    m = bpy.data.materials.get("Mat_DoorFrame_White")
    if m is None:
        m = bpy.data.materials.new("Mat_DoorFrame_White")
        m.use_nodes = True
        bsdf = m.node_tree.nodes.get("Principled BSDF")
        bsdf.inputs["Base Color"].default_value = (0.93, 0.92, 0.90, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.5
        bsdf.inputs["Metallic"].default_value = 0.0
    return m


boxes = []
skipped_tile = 0
for o in bpy.data.objects:
    if o.type != "MESH" or not o.name.startswith(PREFIXES):
        continue
    me = o.data
    mw = o.matrix_world
    rot = mw.to_3x3()
    tile_idx = {i for i, s in enumerate(me.materials)
                if s is not None and s.name == "Mat_BathTile_Wall"}
    for p in me.polygons:
        if abs(p.normal.z) > 0.3 or len(p.vertices) < 4:
            continue
        if p.material_index in tile_idx:
            skipped_tile += 1
            continue
        vs = [mw @ me.vertices[i].co for i in p.vertices]
        zmin = min(v.z for v in vs)
        if zmin > 0.05:
            continue
        wn = (rot @ p.normal).normalized()
        c = mw @ p.center
        # exterior faces: skip
        if (c.y < 0.55 and wn.y < -0.5) or (c.y > 10.0 and wn.y > 0.5) or \
           (c.x < 0.50 and wn.x < -0.5) or (c.x > 15.0 and wn.x > 0.5):
            continue
        # bottom edge: two lowest verts
        sv = sorted(vs, key=lambda v: v.z)[:2]
        p0, p1 = sv[0], sv[1]
        d = Vector((p1.x - p0.x, p1.y - p0.y))
        L = d.length
        if L < 0.30:
            continue
        d = d / L
        mid = ((p0.x + p1.x) / 2, (p0.y + p1.y) / 2)
        yaw = math.atan2(d.y, d.x)
        boxes.append(((mid[0], mid[1], 0.002 + 0.035), (L - 0.02, 0.012, 0.07), yaw))

old = bpy.data.objects.get("ProBaseboards")
if old:
    bpy.data.objects.remove(old, do_unlink=True)

mesh = bpy.data.meshes.new("ProBaseboards_Mesh")
bm = bmesh.new()
for c, s, r in boxes:
    b = bmesh.ops.create_cube(bm, size=1.0)
    M = (mathutils.Matrix.Translation(Vector(c))
         @ mathutils.Matrix.Rotation(r, 4, 'Z')
         @ mathutils.Matrix.Diagonal((s[0], s[1], s[2], 1.0)))
    for v in b["verts"]:
        v.co = M @ v.co
bm.to_mesh(mesh)
bm.free()
mesh.materials.append(frame_material())
obj = bpy.data.objects.new("ProBaseboards", mesh)
scene.collection.objects.link(obj)
for p in mesh.polygons:
    p.use_smooth = False
print(f"[BASE] baked ProBaseboards: {len(boxes)} strips "
      f"(skipped {skipped_tile} bath-tile faces)")
