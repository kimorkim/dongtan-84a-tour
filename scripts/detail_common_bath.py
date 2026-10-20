"""Q8: common bathroom from official 84A VR 015/016; preserve structural walls.

shortcut: photo albedo contains capture lighting, not manufacturer PBR scans;
replace with measured product maps when those become available.
"""
import math
import os
import runpy
import shutil
import sys
import bmesh
import bpy
from mathutils import Vector

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import generate_high_detail_assets as A

backup = os.path.join(ROOT, 'models/backups/apt_84a_photoreal_tour_before_common_bath_detail.blend')
if not os.path.exists(backup):
    shutil.copy2(bpy.data.filepath, backup)
for obj in list(bpy.data.objects):
    if obj.name.startswith(('Q8_', 'Bath1_', 'ProDoorHandle_CommonBath', 'ProDoorLeaf_CommonShower',
                            'Light_Bath1_')) or obj.name in ('Floor_CommonBath', 'Floor_Bath1_Vanity'):
        bpy.data.objects.remove(obj, do_unlink=True)
col = A.get_col('Apt_CommonBathDetail')

def material(name, color, roughness, metallic=0):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.diffuse_color = (*color, 1)
    shader = mat.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = (*color, 1)
    shader.inputs['Roughness'].default_value = roughness
    shader.inputs['Metallic'].default_value = metallic
    return mat

ivory = material('Mat_Q8_Cabinet', (.67, .635, .58), .43)
ceramic = material('Mat_Q8_Ceramic', (.83, .825, .80), .16)
quartz = material('Mat_Q8_Quartz', (.76, .75, .71), .28)
chrome = material('Mat_Q8_Chrome', (.65, .67, .69), .19, 1)
dark = material('Mat_Q8_Frame', (.035, .032, .028), .24, .8)
grout = material('Mat_Q8_Grout', (.42, .395, .36), .84)
mirror = material('Mat_Q8_Mirror', (.88, .89, .90), .018, 1)
towel = material('Mat_Q8_Towel', (.73, .68, .59), .92)
rubber = material('Mat_Q8_Rubber', (.055, .052, .05), .65)
glass = material('Mat_Q8_Glass', (.91, .96, .97), .06)
glass.node_tree.nodes.get('Principled BSDF').inputs['Transmission Weight'].default_value = 1
glass.node_tree.nodes.get('Principled BSDF').inputs['IOR'].default_value = 1.45
led = material('Mat_Q8_LED', (1, .88, .72), .4)
led.node_tree.nodes.get('Principled BSDF').inputs['Emission Color'].default_value = (1, .86, .67, 1)
led.node_tree.nodes.get('Principled BSDF').inputs['Emission Strength'].default_value = 2

photo = bpy.data.images.load(os.path.join(ROOT, 'references/modelhouse/vr84a/016_f.jpg'), check_existing=True)
photo.pack()
tiles = []
for name, roughness in [('WallTile', .52), ('FloorTile', .67)]:
    mat = material('Mat_Q8_'+name, (.48, .43, .38), roughness)
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    for node in list(nodes):
        if node.type not in ('BSDF_PRINCIPLED', 'OUTPUT_MATERIAL'):
            nodes.remove(node)
    image = nodes.new('ShaderNodeTexImage')
    image.image = photo
    image.interpolation = 'Linear'
    uv = nodes.new('ShaderNodeUVMap')
    uv.uv_map = 'TilePhotoUV'
    links.new(uv.outputs['UV'], image.inputs['Vector'])
    links.new(image.outputs['Color'], nodes.get('Principled BSDF').inputs['Base Color'])
    tiles.append(mat)
wall_tile, floor_tile = tiles

def box(name, x1, x2, y1, y2, z1, z2, mat, bevel=.002):
    obj = A.create_beveled_box(name, (x1+x2)/2, (y1+y2)/2, z1,
                               x2-x1, y2-y1, z2-z1, bevel=bevel, seg=3, mat=mat, col=col)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(obj.data)
    bm.free()
    for face in obj.data.polygons:
        face.use_smooth = False
    return obj

def tube(name, points, radius, mat):
    curve = bpy.data.curves.new(name, 'CURVE')
    curve.dimensions = '3D'
    curve.resolution_u = 12
    curve.bevel_depth = radius
    curve.bevel_resolution = 3
    spline = curve.splines.new('BEZIER')
    spline.bezier_points.add(len(points)-1)
    for point, co in zip(spline.bezier_points, points):
        point.co = co
        point.handle_left_type = point.handle_right_type = 'AUTO'
    obj = bpy.data.objects.new(name, curve)
    col.objects.link(obj)
    curve.materials.append(mat)
    return obj

def cylinder(name, a, b, radius, mat, seg=32):
    direction = Vector(b)-Vector(a)
    obj = A.create_cylinder(name, *a, radius, direction.length, seg=seg, mat=mat, col=col)
    obj.rotation_euler = direction.to_track_quat('Z', 'Y').to_euler()
    return obj

def loft(name, rings, mat, caps=True, count=64, power=2):
    """Elliptical ring loft, also supports an open-top bowl with an inner return."""
    def rounded(value):
        return math.copysign(abs(value)**(2/power), value)
    verts = [(cx+rx*rounded(math.cos(i*2*math.pi/count)), cy+ry*rounded(math.sin(i*2*math.pi/count)), z)
             for cx, cy, rx, ry, z in rings for i in range(count)]
    faces = [(j*count+i, j*count+(i+1)%count, (j+1)*count+(i+1)%count, (j+1)*count+i)
             for j in range(len(rings)-1) for i in range(count)]
    if caps:
        faces += [tuple(reversed(range(count))), tuple(range((len(rings)-1)*count, len(rings)*count))]
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    mesh.materials.append(mat)
    for face in mesh.polygons:
        face.use_smooth = len(face.vertices) == 4
    return obj

def photo_uv(obj):
    # Only the unobstructed centre of one real 300x600 tile, excluding labels/grout.
    mesh = obj.data
    layer = mesh.uv_layers.new(name='TilePhotoUV')
    for face in mesh.polygons:
        axes = [i for i in range(3) if i != max(range(3), key=lambda i: abs(face.normal[i]))]
        coords = [mesh.vertices[mesh.loops[i].vertex_index].co for i in face.loop_indices]
        lo = [min(p[a] for p in coords) for a in axes]
        hi = [max(p[a] for p in coords) for a in axes]
        for loop, p in zip(face.loop_indices, coords):
            u, v = [(p[a]-low)/max(high-low, 1e-8) for a, low, high in zip(axes, lo, hi)]
            layer.data[loop].uv = (.30625+u*.271875, .41875+v*.55625)

def tile_grid(tag, u1, u2, v1, v2, step_u, step_v, axis, depth, mat):
    """Clipped physical tiles keep grout and product scale independent of texture."""
    for i in range(math.ceil((u2-u1)/step_u)):
        for j in range(math.ceil((v2-v1)/step_v)):
            a, b = u1+i*step_u+.0012, min(u1+(i+1)*step_u, u2)-.0012
            c, d = v1+j*step_v+.0012, min(v1+(j+1)*step_v, v2)-.0012
            bounds = (depth[0], depth[1], a, b, c, d) if axis == 'x' else (
                (a, b, depth[0], depth[1], c, d) if axis == 'y' else (a, b, c, d, depth[0], depth[1]))
            obj = box(f'Q8_{tag}_{i}_{j}', *bounds, mat, bevel=.0005)
            photo_uv(obj)

def wall_grid(tag, start, end):
    # Follow the traced plan's slightly skewed faces, including the shaft returns.
    direction = Vector(end)-Vector(start)
    length = direction.length
    angle = math.atan2(direction.y, direction.x)
    before = set(col.objects)
    box('Q8_WallGrout_'+tag,0,length,0,.004,.014,2.29,grout,0)
    tile_grid('WetTile_'+tag,0,length,.014,2.29,.3,.6,'y',(.004,.012),wall_tile)
    for obj in set(col.objects)-before:
        u,v = obj.location.x,obj.location.y
        obj.location.x = start[0]+u*math.cos(angle)-v*math.sin(angle)
        obj.location.y = start[1]+u*math.sin(angle)+v*math.cos(angle)
        obj.rotation_euler.z = angle

# Original walls stay intact. Thin tile linings do not bridge any doorway.
box('Floor_CommonBath', 13.40, 14.97, 5.64, 7.525, -.008, .010, grout, 0)
tile_grid('WetTile_Floor', 13.40, 14.97, 5.74, 7.525, .3, .3, 'z', (.010, .014), floor_tile)
box('Q8_EntryThreshold', 13.45, 14.26, 5.64, 5.74, .010, .018, quartz)
for tag, start, end in [
    ('E',(14.981,5.756),(14.981,6.619)),
    ('ShaftS',(14.981,6.619),(14.475,6.656)),
    ('ShaftW',(14.475,6.656),(14.456,7.537)),
    ('N',(14.456,7.537),(13.463,7.537)),
    ('W',(13.463,7.537),(13.432,5.75)),
    ('S',(14.30,5.719),(14.944,5.719))]:
    wall_grid(tag,start,end)

box('Floor_Bath1_Vanity', 14.35, 14.96, 4.45, 5.55, -.004, .010, grout, 0)
tile_grid('DryTile_Floor', 14.35, 14.96, 4.45, 5.55, .3, .3, 'z', (.010, .014), floor_tile)
tile_grid('DryTile_Back', 4.45, 5.55, .90, 2.28, 1.1, 1.38, 'x', (14.955, 14.967), wall_tile)

# Cabinet shell has no solid block in the basin cavity.
box('Q8_Dry_Back', 14.925, 14.95, 4.47, 5.53, .21, .85, ivory)
box('Q8_Dry_Base', 14.42, 14.94, 4.47, 5.53, .21, .23, ivory)
for tag, a, b in [('S', 4.47, 4.49), ('N', 5.51, 5.53)]:
    box('Q8_Dry_Side'+tag, 14.42, 14.94, a, b, .21, .85, ivory)
for tag, a, b in [('S', 4.47, 4.997), ('N', 5.003, 5.53)]:
    box('Q8_Dry_Door'+tag, 14.398, 14.42, a, b, .215, .838, ivory)
box('Q8_Dry_PullReveal', 14.42, 14.45, 4.49, 5.51, .816, .843, rubber)
top = box('Q8_Dry_Counter', 14.38, 14.95, 4.45, 5.55, .85, .88, quartz)
cutter = loft('Q8_TempSinkCut', [(14.62,5,.185,.265,.70),
                               (14.62,5,.185,.265,.96)], ceramic, power=4)
bpy.context.view_layer.objects.active = top
bpy.ops.object.modifier_apply(modifier=top.modifiers[0].name)
bpy.context.view_layer.update()
boolean = top.modifiers.new('Actual sink opening', 'BOOLEAN')
boolean.operation = 'DIFFERENCE'
boolean.object = cutter
bpy.context.view_layer.objects.active = top
bpy.ops.object.modifier_apply(modifier=boolean.name)
bpy.data.objects.remove(cutter, do_unlink=True)
# Rounded elliptical ceramic bowl below the rectangular, softly bevelled cutout.
loft('Q8_Dry_Basin', [(14.62, 5, .19, .27, .854), (14.62, 5, .16, .235, .80),
                     (14.62, 5, .105, .15, .725), (14.62, 5, .025, .035, .715),
                     (14.62, 5, .001, .001, .715)], ceramic, caps=False, power=4)
cylinder('Q8_Dry_Waste', (14.62, 5, .716), (14.62, 5, .722), .024, chrome)
box('Q8_Dry_FaucetBody', 14.825, 14.877, 4.975, 5.025, .88, 1.025, chrome, .012)
box('Q8_Dry_FaucetSpout', 14.72, 14.86, 4.977, 5.023, .995, 1.02, chrome, .008)
box('Q8_Dry_FaucetLever', 14.812, 14.876, 4.98, 5.02, 1.034, 1.045, chrome, .004)
cylinder('Q8_Dry_Overflow', (14.795, 5, .815), (14.785, 5, .815), .012, chrome)
box('Q8_Dry_Backsplash', 14.935, 14.953, 4.45, 5.55, .88, 1.01, quartz)
box('Q8_Dry_Mirror', 14.931, 14.944, 4.65, 5.35, 1.13, 2.13, mirror)
for tag, a, b in [('S', 4.475, 4.49), ('N', 5.51, 5.525)]:
    box('Q8_Dry_LED_'+tag, 14.938, 14.949, a, b, 1.0, 2.28, led)
box('Q8_Dry_LED_Lower', 14.932, 14.94, 4.49, 5.51, 1.005, 1.014, led)
tube('Q8_Dry_TowelBar', [(14.53, 4.49, 1.37), (14.53, 4.52, 1.37), (14.85, 4.52, 1.37), (14.85, 4.49, 1.37)], .009, chrome)
box('Q8_Dry_Towel', 14.58, 14.81, 4.511, 4.529, .95, 1.37, towel, .008)
for i, y in enumerate((4.60, 4.71)):
    cylinder(f'Q8_Dry_Soap{i}', (14.84,y,.88), (14.84,y,1.02), .032, ivory)
    box(f'Q8_Dry_SoapPump{i}',14.817,14.86,y-.012,y+.012,1.02,1.05,chrome)

# Curved skirted toilet, separate seat/lid and rounded cistern (closed display pose).
loft('Q8_Toilet_Body', [(14.60,6.16,.19,.14,.016), (14.57,6.16,.205,.153,.07),
                       (14.57,6.16,.19,.15,.20), (14.54,6.16,.25,.185,.34),
                       (14.54,6.16,.265,.195,.405)], ceramic)
loft('Q8_Toilet_SeatSeal', [(14.54,6.16,.265,.195,.405), (14.54,6.16,.265,.195,.414)], rubber)
loft('Q8_Toilet_Seat', [(14.54,6.16,.267,.197,.414), (14.54,6.16,.267,.197,.435)], ceramic)
loft('Q8_Toilet_Lid', [(14.54,6.16,.264,.194,.44), (14.54,6.16,.26,.19,.457),
                      (14.54,6.16,.24,.175,.465)], ceramic)
box('Q8_Toilet_Tank', 14.76,14.944,5.955,6.365,.38,.765,ceramic,.035)
box('Q8_Toilet_TankLid',14.75,14.95,5.95,6.37,.765,.792,ceramic,.025)
cylinder('Q8_Toilet_Flush',(14.855,6.12,.793),(14.855,6.12,.799),.024,chrome)
box('Q8_Toilet_BidetControl',14.60,14.73,5.91,5.96,.41,.445,ivory,.012)
for i in range(3):
    cylinder(f'Q8_Toilet_ControlButton{i}',(14.62+i*.035,5.935,.446),(14.62+i*.035,5.935,.449),.007,chrome,16)

# Mirror cabinet with one open side bay, not a solid reflective slab.
box('Q8_Med_Back',14.93,14.956,5.79,6.58,1.18,2.14,ivory)
for tag,a,b in [('S',5.79,5.81),('N',6.56,6.58),('Mid',6.345,6.365)]:
    box('Q8_Med_Side'+tag,14.78,14.956,a,b,1.18,2.14,ivory)
for i,z in enumerate((1.18,1.50,1.82,2.12)):
    box(f'Q8_Med_OpenShelf{i}',14.78,14.94,6.365,6.56,z,z+.018,ivory)
for tag,a,b in [('A',5.81,6.073),('B',6.077,6.345)]:
    box('Q8_Med_Mirror'+tag,14.768,14.78,a,b,1.19,2.13,mirror)
box('Q8_Med_Prop',14.82,14.89,6.42,6.49,1.52,1.63,dark,.008)
box('Q8_Toilet_PaperPlate',14.58,14.82,5.759,5.778,.76,.97,chrome,.004)
cylinder('Q8_Toilet_PaperRoll',(14.62,5.812,.79),(14.78,5.812,.79),.047,ceramic)
box('Q8_Toilet_PaperFlap',14.61,14.79,5.785,5.86,.83,.846,chrome,.003)
tube('Q8_Toilet_BidetHose',[(14.94,6.48,.45),(14.80,6.50,.18),(14.80,6.50,.72)],.008,chrome)
cylinder('Q8_Toilet_BidetSpray',(14.80,6.50,.69),(14.80,6.50,.80),.014,chrome)

# Dark slim shower framing; door parks against west wall, leaving a walkable opening.
for tag,x in [('W',13.49),('E',14.45),('M',14.18)]:
    box('Q8_Shower_Post'+tag,x-.012,x+.012,6.588,6.614,.02,2.105,dark)
box('Q8_Shower_Headrail',13.478,14.462,6.586,6.616,2.08,2.115,dark)
box('Q8_Shower_Sill',13.48,14.462,6.58,6.62,.014,.022,quartz)
box('Q8_Shower_GlassFixed',14.193,14.438,6.598,6.606,.035,2.08,glass,0)
box('ProDoorLeaf_CommonShower',13.486,13.494,6.62,7.29,.035,2.08,glass,0)
for tag,y in [('Hinge',6.63),('Edge',7.28)]:
    box('Q8_Shower_OpenDoor'+tag,13.475,13.502,y-.01,y+.01,.035,2.08,dark)
tube('Q8_Shower_DoorHandle',[(13.50,6.95,1.02),(13.54,6.95,1.02),(13.54,7.17,1.02),(13.50,7.17,1.02)],.009,dark)
cylinder('Q8_Shower_Rail',(14.90,7.19,1.05),(14.90,7.19,1.98),.011,chrome)
for i,z in enumerate((1.10,1.91)):
    cylinder(f'Q8_Shower_RailMount{i}',(14.96,7.19,z),(14.89,7.19,z),.021,chrome)
tube('Q8_Shower_RainArm',[(14.95,7.19,2.13),(14.64,7.19,2.13),(14.55,7.19,2.10)],.013,chrome)
cylinder('Q8_Shower_RainHead',(14.55,7.19,2.075),(14.55,7.19,2.097),.105,chrome,48)
for i in range(32):
    angle=i*2*math.pi/32
    for j,r in enumerate((.047,.085)):
        x,y=14.55+r*math.cos(angle),7.19+r*math.sin(angle)
        cylinder(f'Q8_Shower_Nozzle{i}_{j}',(x,y,2.073),(x,y,2.077),.0028,rubber,8)
cylinder('Q8_Shower_Mixer',(14.94,7.19,.98),(14.80,7.19,.98),.033,chrome)
box('Q8_Shower_Lever',14.78,14.84,7.175,7.205,1.01,1.08,chrome,.007)
cylinder('Q8_Shower_HandsetGrip',(14.86,7.21,1.51),(14.84,7.21,1.66),.014,chrome)
cylinder('Q8_Shower_HandsetFace',(14.827,7.21,1.69),(14.811,7.21,1.69),.043,chrome)
tube('Q8_Shower_Hose',[(14.83,7.19,.96),(14.74,7.20,.56),(14.68,7.20,.71),(14.86,7.21,1.51)],.007,chrome)
for i,z in enumerate((.83,1.30)):
    box(f'Q8_Shower_Shelf{i}',14.74,14.95,7.29,7.49,z,z+.018,chrome,.025)
    tube(f'Q8_Shower_ShelfRail{i}',[(14.74,7.49,z+.06),(14.74,7.30,z+.06),(14.94,7.30,z+.06)],.006,chrome)
box('Q8_Shower_Drain',14.84,14.915,6.86,7.44,.0145,.018,chrome,.002)
for i in range(20):
    box(f'Q8_Shower_DrainSlot{i}',14.855,14.90,6.88+i*.027,6.885+i*.027,.018,.019,rubber,0)

# The service shaft's actual room face belongs to ExactWall_5 (x14.456~14.475),
# with ExactWall_6 behind it. Keep both intact and mount fittings in front.
fittings = ('Rail', 'Rain', 'Nozzle', 'Mixer', 'Lever', 'Handset', 'Hose', 'Shelf', 'Drain')
for obj in col.objects:
    if obj.name.startswith(tuple('Q8_Shower_'+name for name in fittings)):
        obj.location.x -= .50

door = bpy.data.objects.get('ProDoorLeaf_CommonBath')
if door:
    bpy.data.objects.remove(door, do_unlink=True)
box('ProDoorLeaf_CommonBath',13.44,13.475,5.76,6.54,.02,2.08,ivory)
tube('Q8_BathDoor_Handle',[(13.475,6.40,1.0),(13.51,6.40,1.0),(13.51,6.31,1.0)],.009,chrome)

for i,(x,y,energy) in enumerate(((14.61,5.0,20),(14.20,6.12,20),(14.16,7.15,17))):
    cylinder(f'Q8_Ceiling_Rim{i}',(x,y,2.273),(x,y,2.287),.063,ivory)
    cylinder(f'Q8_Ceiling_LED{i}',(x,y,2.270),(x,y,2.275),.049,led)
    data=bpy.data.lights.new(f'Q8_Downlight{i}','AREA')
    data.energy=energy
    data.color=(1,.91,.80)
    data.shape='DISK'
    data.size=.17
    obj=bpy.data.objects.new(data.name,data)
    col.objects.link(obj)
    obj.location=(x,y,2.25)

# Shared legacy box helper has inward winding; fix new geometry only, before booleans/rays/export.
for obj in col.objects:
    if obj.type == 'MESH':
        bm=bmesh.new()
        bm.from_mesh(obj.data)
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
        bm.to_mesh(obj.data)
        bm.free()
bpy.context.view_layer.update()
runpy.run_path(os.path.join(ROOT,'scripts/verify_common_bath.py'))
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print('Q8 COMMON BATH SAVED', flush=True)
