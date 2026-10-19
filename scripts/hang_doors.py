"""Rehang 7 interior doors with measured openings (idempotent).

- Deletes old leaves/handles, raycasts wall openings from old leaf seeds.
- Builds jamb liners + casings (joined static trim), fresh leaves on hinge
  pivots with parented lever handles, sensible open angles.
Run inside Blender.
"""
import bpy
import math
from mathutils import Vector
from collections import defaultdict
import bmesh

scene = bpy.context.scene
deps = bpy.context.evaluated_depsgraph_get()

WALL_PREFIXES = ("ExactWall", "NewWall")


def is_wall(o):
    return o is not None and o.name.startswith(WALL_PREFIXES)


def ray_wall(origin, direction, maxd=8.0):
    """Nearest wall-mesh hit, advancing past non-wall blockers."""
    o = Vector(origin)
    d = Vector(direction).normalized()
    traveled = 0.0
    for _ in range(8):
        hit, loc, no, idx, obj, mat = scene.ray_cast(deps, o, d)
        if not hit:
            return None
        step = (loc - o).length
        if is_wall(obj):
            return traveled + step, loc, no, obj
        traveled += step + 0.05
        if traveled > maxd:
            return None
        o = loc + d * 0.05
    return None


def ray_any(origin, direction, maxd=6.0):
    hit, loc, *_ = scene.ray_cast(deps, Vector(origin), Vector(direction))
    if not hit:
        return maxd
    return min((loc - Vector(origin)).length, maxd)


DOORS = [
    # name, seed(xy), leaf material, open_deg
    ("Alpha", (11.65, 6.73), "Mat_Wood_Walnut", 35),
    ("Bed2", (9.64, 4.35), "Mat_Wood_Walnut", 35),
    ("Bed3", (12.46, 4.35), "Mat_Wood_Walnut", 35),
    ("CommonBath", (13.83, 5.65), "Mat_Cabinet_Cashmere", 30),
    ("MasterBath", (2.65, 6.24), "Mat_Cabinet_Cashmere", 30),
]
# Manual specs from plan-segment survey (center, axis, width, th, head, header?, swing)
# swing: +1/-1 along wall normal n, None = auto (more clearance)
MANUAL = {
    "Alpha": ((11.65, 6.73), 1, 0.94, 0.10, 2.10, True, None),
    "Bed2": ((9.64, 4.325), 0, 0.94, 0.17, 2.10, True, -1),
    "Bed3": ((12.46, 4.33), 0, 0.92, 0.18, 2.10, True, -1),
    "CommonBath": ((13.83, 5.65), 0, 0.80, 0.14, 2.10, True, -1),
    "MasterBath": ((2.645, 6.235), 1, 0.77, 0.11, 2.10, True, None),
    "FrontEntry": ((12.20, 10.11), 0, 0.90, 0.12, 2.09, False, -1),
}
FRONT_MAT = "Mat_Door_Blue"
HEADER = None  # TrimBuilder, set in main


def measure_opening(sx, sy):
    """Find opening (center, axis, width) near seed. axis=0 -> wall along X."""
    for ox, oy in [(0, 0), (0.25, 0), (-0.25, 0), (0, 0.25), (0, -0.25),
                   (0.4, 0), (-0.4, 0), (0, 0.4), (0, -0.4)]:
        px, py = sx + ox, sy + oy
        hx = ray_wall((px, py, 1.0), (1, 0, 0))
        hxn = ray_wall((px, py, 1.0), (-1, 0, 0))
        hy = ray_wall((px, py, 1.0), (0, 1, 0))
        hyn = ray_wall((px, py, 1.0), (0, -1, 0))
        if hx and hxn:
            w = hx[0] + hxn[0]
            if 0.55 <= w <= 1.20:
                cx = px + (hx[0] - hxn[0]) / 2
                # validate: through-opening rays must travel far
                if ray_any((cx, py, 1.0), (0, 1, 0)) > 1.2 and \
                   ray_any((cx, py, 1.0), (0, -1, 0)) > 1.2:
                    return (cx, py), 0, w
        if hy and hyn:
            w = hy[0] + hyn[0]
            if 0.55 <= w <= 1.20:
                cy = py + (hy[0] - hyn[0]) / 2
                if ray_any((px, cy, 1.0), (1, 0, 0)) > 1.2 and \
                   ray_any((px, cy, 1.0), (-1, 0, 0)) > 1.2:
                    return (px, cy), 1, w
    return None


def measure_wall(center, axis, width):
    """Wall thickness + center plane via offset solid point."""
    ax = Vector((1, 0, 0)) if axis == 0 else Vector((0, 1, 0))
    n = Vector((0, 1, 0)) if axis == 0 else Vector((1, 0, 0))
    solid = Vector((center[0], center[1], 1.0)) + ax * (width / 2 + 0.35)
    h1 = ray_wall(solid + n * 2.5, -n)
    h2 = ray_wall(solid - n * 2.5, n)
    if h1 and h2:
        t = abs((h1[1] - h2[1]).dot(n))
        if 0.06 <= t <= 0.50:
            cp = (h1[1] + h2[1]) / 2
            return t, (cp.x, cp.y)
    return 0.12, center


def measure_head(center):
    h = ray_wall((center[0], center[1], 1.0), (0, 0, 1))
    if h and 1.9 <= 1.0 + h[0] <= 2.3:
        return 1.0 + h[0]
    return 2.10


def cleanup_old():
    for o in list(bpy.data.objects):
        n = o.name
        if n.startswith("Door_") and ("_Leaf" in n or "_HBase" in n or "_HLever" in n):
            if "MasterBalcony" not in n:
                bpy.data.objects.remove(o, do_unlink=True)
                print(f"[DOOR] removed {n}")
    for o in list(bpy.data.objects):
        if o.name.startswith("ProDoor"):
            bpy.data.objects.remove(o, do_unlink=True)


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


class TrimBuilder:
    """Accumulates boxes, bakes to one mesh (no ops, no context)."""

    def __init__(self):
        self.boxes = []

    def add(self, center, size, rot_z=0.0):
        self.boxes.append((Vector(center), Vector(size), rot_z))

    def bake(self, name, mat):
        mesh = bpy.data.meshes.new(name + "_Mesh")
        bm = bmesh.new()
        for c, s, r in self.boxes:
            b = bmesh.ops.create_cube(bm, size=1.0)
            vs = b["verts"]
            import mathutils
            M = (mathutils.Matrix.Translation(c)
                 @ mathutils.Matrix.Rotation(r, 4, 'Z')
                 @ mathutils.Matrix.Diagonal((s.x, s.y, s.z, 1.0)))
            for v in vs:
                v.co = M @ v.co
        bm.to_mesh(mesh)
        bm.free()
        o = bpy.data.objects.new(name, mesh)
        if mat:
            mesh.materials.append(mat)
        scene.collection.objects.link(o)
        # autosmooth-ish: shade smooth off (trim is crisp)
        for p in mesh.polygons:
            p.use_smooth = False
        print(f"[DOOR] baked {name}: {len(self.boxes)} boxes")
        return o


def build_door(name, center, axis, width, th, plane_c, head_h, leaf_mat,
               open_deg, do_header=True, swing=None):
    trim = TrimBuilder()
    ax = Vector((1, 0)) if axis == 0 else Vector((0, 1))
    n = Vector((0, 1)) if axis == 0 else Vector((1, 0))
    C = Vector((plane_c[0], plane_c[1]))
    half = width / 2
    # opening edges (jamb faces)
    e_neg = C - ax * half
    e_pos = C + ax * half
    z_head = head_h

    # jamb liners (0.03 wide, 5mm embedded in wall to avoid coplanar fight)
    jw = 0.030
    for e, sgn in ((e_neg, 1), (e_pos, -1)):
        c2 = e + ax * (sgn * 0.010)
        sz = (jw, th, z_head) if axis == 0 else (th, jw, z_head)
        trim.add((c2.x, c2.y, z_head / 2), sz)
    hsz = (width, th, jw) if axis == 0 else (th, width, jw)
    trim.add((C.x, C.y, z_head - jw / 2), hsz)
    if do_header and z_head < 2.29:
        hh = 2.30 - z_head
        th2 = max(th - 0.01, 0.05)
        hsz2 = (width + 0.02, th2, hh) if axis == 0 else (th2, width + 0.02, hh)
        HEADER.add((C.x, C.y, z_head + hh / 2), hsz2)

    # casings both faces
    cw, ch, cd = 0.075, z_head + 0.075, 0.014
    for side in (1, -1):
        off = n * (side * (th / 2 + cd / 2 - 0.002))
        for e, sgn in ((e_neg, -1), (e_pos, 1)):
            c2 = e + ax * (sgn * (cw / 2 - 0.008)) + off
            sz = (cw, cd, ch) if axis == 0 else (cd, cw, ch)
            trim.add((c2.x, c2.y, ch / 2), sz)
        hc = C + off + n * 0.0
        hlen = width + 2 * cw - 0.016
        sz = (hlen, cd, cw) if axis == 0 else (cd, hlen, cw)
        trim.add((hc.x, hc.y, z_head + cw / 2 - 0.008), sz)

    trim_obj = trim.bake(f"ProDoorTrim_{name}", frame_material())

    # swing side: manual override or more open space
    if swing is None:
        d_pos = ray_any((C.x, C.y, 1.0), (n.x, n.y, 0))
        d_neg = ray_any((C.x, C.y, 1.0), (-n.x, -n.y, 0))
        s_sign = 1 if d_pos >= d_neg else -1
    else:
        s_sign = swing
    s = n * s_sign

    # hinge at -axis jamb, leaf spans toward +axis when closed
    hinge = e_neg + ax * 0.006
    leaf_w = width - 0.025
    leaf_t, leaf_h, leaf_z0 = 0.040, z_head - 0.03, 0.015
    u = ax  # closed direction hinge->strike
    u_ang = math.atan2(u.y, u.x)
    cross = u.x * s.y - u.y * s.x
    phi = u_ang + (1 if cross > 0 else -1) * math.radians(open_deg)

    mesh = bpy.data.meshes.new(f"ProDoorLeaf_{name}_Mesh")
    w, t, h = leaf_w, leaf_t, leaf_h
    verts = [(0, -t / 2, 0), (w, -t / 2, 0), (w, t / 2, 0), (0, t / 2, 0),
             (0, -t / 2, h), (w, -t / 2, h), (w, t / 2, h), (0, t / 2, h)]
    faces = [(0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1),
             (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    lm = bpy.data.materials.get(leaf_mat)
    if lm:
        mesh.materials.append(lm)
    leaf = bpy.data.objects.new(f"ProDoorLeaf_{name}", mesh)
    leaf.location = (hinge.x, hinge.y, leaf_z0)
    leaf.rotation_euler = (0, 0, phi)
    scene.collection.objects.link(leaf)

    # lever handles both sides, parented
    hm = bpy.data.materials.get("Mat_Chrome_Metal")
    import mathutils
    leaf.update_tag()
    R = mathutils.Matrix.Rotation(phi, 4, 'Z')
    for side_i, side_s in ((0, 1), (1, -1)):
        hg = Vector((w - 0.11, side_s * (t / 2 + 0.012), 0.95))
        lm2 = bpy.data.meshes.new(f"ProDoorHandle_{name}_{side_i}_Mesh")
        lw, lh, lt = 0.13, 0.024, 0.028
        vv = [(-lw/2, -lt/2, -lh/2), (lw/2, -lt/2, -lh/2),
              (lw/2, lt/2, -lh/2), (-lw/2, lt/2, -lh/2),
              (-lw/2, -lt/2, lh/2), (lw/2, -lt/2, lh/2),
              (lw/2, lt/2, lh/2), (-lw/2, lt/2, lh/2)]
        lm2.from_pydata(vv, [], faces)
        lm2.update()
        if hm:
            lm2.materials.append(hm)
        lever = bpy.data.objects.new(
            f"ProDoorHandle_{name}_{'A' if side_i == 0 else 'B'}", lm2)
        world = Vector((hinge.x, hinge.y, leaf_z0)) + R @ hg
        lever.location = world
        lever.rotation_euler = (0, 0, phi)
        scene.collection.objects.link(lever)
        lever.parent = leaf
        lever.matrix_parent_inverse = leaf.matrix_world.inverted()
    print(f"[DOOR] {name}: center=({C.x:.2f},{C.y:.2f}) axis={'X' if axis == 0 else 'Y'} "
          f"w={width:.2f} th={th:.2f} head={z_head:.2f} swing={' +n' if s_sign > 0 else ' -n'}")
    return leaf


cleanup_old()
HEADER = TrimBuilder()
built = []
for name, seed, mat, deg in DOORS:
    if name in MANUAL:
        center, axis, width, th, head, hdr, sw = MANUAL[name]
        build_door(name, center, axis, width, th, center, head, mat, deg,
                   do_header=hdr, swing=sw)
        built.append(name + "(manual)")
        continue
    m = measure_opening(*seed)
    if not m:
        print(f"[DOOR] {name}: OPENING NOT FOUND near {seed}")
        continue
    center, axis, width = m
    th, plane_c = measure_wall(center, axis, width)
    head = measure_head(center)
    pc = (center[0], plane_c[1]) if axis == 0 else (plane_c[0], center[1])
    build_door(name, center, axis, width, th, pc, head, mat, deg)
    built.append(name)

mc, ax, w, th, hd, hdr, sw = MANUAL["FrontEntry"]
build_door("FrontEntry", mc, ax, w, th, mc, hd, FRONT_MAT, 8,
           do_header=hdr, swing=sw)
built.append("FrontEntry(manual)")
HEADER.bake("ProDoorHeaders", bpy.data.materials.get("Mat_Wall_Interior"))
print(f"[DOOR] DONE built={built}")
