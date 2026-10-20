"""Q10: preserve CAD shell; furnish bedroom 3 as Yuna's pastel play/reading room.

shortcut: furniture sizes and pastel finishes are design assumptions, not product specifications;
replace with measured furniture before using this model for purchasing or construction.
"""
import math
import os
import runpy
import shutil
import sys
import bmesh
import bpy
from mathutils import Matrix, Vector

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import generate_high_detail_assets as A

backup = os.path.join(ROOT, 'models/backups/apt_84a_photoreal_tour_before_yuna_room.blend')
if not os.path.exists(backup):
    shutil.copy2(bpy.data.filepath, backup)
backup = os.path.join(ROOT, 'models/backups/apt_84a_photoreal_tour_before_yuna_basic_correction.blend')
if not os.path.exists(backup):
    shutil.copy2(bpy.data.filepath, backup)
for obj in list(bpy.data.objects):
    if obj.name.startswith(('Q10_', 'Bed3_', 'Wardrobe_Bed3_', 'ProDoorHandle_Bed3',
                            'SillPatch_Bed3_', 'Liner_Bed3_')):
        bpy.data.objects.remove(obj, do_unlink=True)
col = A.get_col('Apt_YunaRoom')

def material(name, rgb, rough=.65, metal=0):
    mat = bpy.data.materials.get('Mat_Q10_' + name) or bpy.data.materials.new('Mat_Q10_' + name)
    mat.use_nodes = True
    mat.diffuse_color = (*rgb, 1)
    bs = mat.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*rgb, 1)
    bs.inputs['Roughness'].default_value = rough
    bs.inputs['Metallic'].default_value = metal
    return mat

cream = material('Cream', (.79,.735,.655), .48)
pink = material('Blush', (.67,.37,.36), .86)
lightpink = material('Petal', (.83,.59,.55), .86)
blue = material('Sky', (.40,.61,.69), .86)
sage = material('Sage', (.49,.61,.46), .8)
linen = material('Linen', (.86,.81,.71), .92)
wood = material('Birch', (.57,.40,.24), .55)
gold = material('Brass', (.48,.32,.15), .32, .8)
ink = material('Ink', (.065,.042,.035), .65)
white = material('White', (.88,.86,.80), .65)
sun = material('Butter', (.88,.69,.35), .9)
glass = material('Glass',(.97,.99,1),.035)
glass.node_tree.nodes.get('Principled BSDF').inputs['Alpha'].default_value=.06
glass.node_tree.nodes.get('Principled BSDF').inputs['Transmission Weight'].default_value=0
glass.surface_render_method='DITHERED'  # Match the tour's alpha-glass path; refractive glass renders dark here.
glass.node_tree.nodes.get('Principled BSDF').inputs['IOR'].default_value=1.45
for name in ('Win_Bed3_Glass1','Win_Bed3_Glass2'):
    bpy.data.objects[name].data.materials.clear()
    bpy.data.objects[name].data.materials.append(glass)

def box(name, x1,x2,y1,y2,z1,z2,mat,bevel=.012):
    obj = A.create_beveled_box('Q10_'+name,(x1+x2)/2,(y1+y2)/2,z1,x2-x1,y2-y1,z2-z1,
                               bevel=bevel,seg=4,mat=mat,col=col)
    bm = bmesh.new(); bm.from_mesh(obj.data)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    bm.to_mesh(obj.data); bm.free()
    for f in obj.data.polygons: f.use_smooth = False
    return obj

def sphere(name, center, scale, mat):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,location=center)
    obj = bpy.context.object; obj.name = 'Q10_'+name
    for c in list(obj.users_collection): c.objects.unlink(obj)
    col.objects.link(obj)
    obj.scale = scale
    obj.data.materials.append(mat)
    for f in obj.data.polygons: f.use_smooth = True
    return obj

def cylinder(name,x,y,z,r,h,mat):
    bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=r,depth=h,location=(x,y,z+h/2))
    obj = bpy.context.object; obj.name = 'Q10_'+name
    for c in list(obj.users_collection): c.objects.unlink(obj)
    col.objects.link(obj); obj.data.materials.append(mat)
    bevel = obj.modifiers.new('Soft edge','BEVEL'); bevel.width=.008; bevel.segments=3
    obj.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return obj

# Preserve structural outlines; correct normals and align the interior window finish.
shell_names = ['ExactWall_2','ExactWall_5','ProDoorTrim_Bed3']
shell_names += [o.name for o in bpy.data.objects if o.name.startswith('Win_Bed3_')]
for name in shell_names:
    obj = bpy.data.objects[name]
    bm = bmesh.new(); bm.from_mesh(obj.data)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    bm.to_mesh(obj.data); bm.free()

# The old sill ended at y=.51 while the corner piers ended at y=.84.
# Add the missing interior lining, not a cut through the shared structural piers.
wallmat=bpy.data.materials['Mat_Wall_Interior']
box('WindowWall_Sill',11.964,14.979,.50,.85,0,.80,wallmat,.002)
box('WindowWall_Header',11.964,14.979,.50,.85,2.20,2.30,wallmat,.002)
box('WindowWall_W',11.964,12.38,.50,.85,.80,2.20,wallmat,.002)
box('WindowWall_E',14.40,14.979,.50,.85,.80,2.20,wallmat,.002)
box('WindowSillCap',12.38,14.40,.71,.88,.80,.825,cream,.004)
dy=.80-bpy.data.objects['Win_Bed3_Mullion'].location.y
for obj in bpy.data.objects:
    if obj.name.startswith('Win_Bed3_'):
        obj.location.y += dy

# Reuse the existing hinge, with handles in leaf-local coordinates (not world coordinates twice).
leaf = bpy.data.objects['ProDoorLeaf_Bed3']
leaf.data.materials.clear(); leaf.data.materials.append(cream)
leaf.rotation_euler.z = math.radians(-85)  # Leave handle clearance against the west wall.
for side, sign in [('A',1),('B',-1)]:
    handle = box('DoorHandle_'+side,-.045,.065,-.012,.012,0,.025,gold,.01)
    handle.name = 'ProDoorHandle_Bed3_'+side
    handle.parent = leaf
    handle.location = (.75,sign*.045,.97)

# Baseboard follows real room walls; no strip crosses the entrance or window.
box('Skirt_E',14.956,14.979,.85,4.19,0,.065,cream,.003)
box('Skirt_W',11.965,11.985,.85,3.38,0,.065,cream,.003)
box('Skirt_N',12.99,14.95,4.19,4.217,0,.065,cream,.003)
box('Skirt_S',11.986,14.95,.851,.875,0,.065,cream,.003)

# Basic entrance-side built-in, per user option (not the VR's window-side wardrobe).
# shortcut: 1.82m width/0.60m depth are provisional until the option drawing is supplied.
box('Wardrobe_Back',13.12,14.94,4.18,4.215,0,2.30,cream,.003)
box('Wardrobe_SideW',13.12,13.145,3.61,4.18,0,2.30,cream,.003)
box('Wardrobe_SideE',14.915,14.94,3.61,4.18,0,2.30,cream,.003)
box('Wardrobe_TopFiller',13.145,14.915,3.59,4.18,2.19,2.30,cream,.003)
box('Wardrobe_Plinth',13.145,14.915,3.63,4.18,0,.065,cream,.003)
for i in range(4):
    a=13.15+i*.44
    box('Wardrobe_Door'+str(i),a,a+.434,3.59,3.615,.065,2.185,cream,.004)
    hx=a+.37 if i%2==0 else a+.06
    box('Wardrobe_Handle'+str(i),hx,hx+.012,3.56,3.59,.93,1.16,wood,.006)

# East-wall low single bed: 1.04 x 2.10m, mattress top 400mm.
box('Bed_Base',13.82,14.88,1.10,3.22,.04,.22,cream,.055)
box('Mattress',13.86,14.84,1.14,3.18,.22,.40,linen,.075)
box('Duvet',13.85,14.85,1.12,2.57,.397,.455,lightpink,.07)
box('FoldedThrow',13.84,14.86,1.33,1.68,.45,.478,blue,.025)
for i in range(7):
    box('QuiltSeam'+str(i),13.87,14.83,1.85+i*.10,1.854+i*.10,.454,.456,pink,.001)
box('Pillow',13.99,14.72,2.70,3.07,.40,.53,white,.085)
sphere('CloudCushion',(14.35,2.94,.58),(.23,.10,.15),blue)
for i,dx in enumerate([-.16,0,.16]):
    sphere('CloudPuff'+str(i),(14.35+dx,2.92,.64),(.115,.10,.10),blue)
# Rounded arched headboard, extruded along y; geometric, not a flat decal.
profile = [(-.54,.09),(.54,.09),(.54,.66)]
profile += [(.54*math.cos(t),.66+.22*math.sin(t)) for t in [i*math.pi/24 for i in range(1,25)]]
verts = [(14.35+x,y,z) for y in (3.18,3.25) for x,z in profile]
n=len(profile); faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]
faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
mesh=bpy.data.meshes.new('Q10_ArchedHead'); mesh.from_pydata(verts,[],faces); mesh.update()
obj=bpy.data.objects.new('Q10_Headboard',mesh); col.objects.link(obj); mesh.materials.append(pink)
bev=obj.modifiers.new('Upholstered edge','BEVEL'); bev.width=.025; bev.segments=4
box('BedGuard_E',14.82,14.88,2.25,3.18,.38,.61,cream,.03)
box('BedGuard_W',13.82,13.88,2.65,3.17,.38,.61,cream,.03)

# North wall picture-book display and toy baskets; entrance corner remains empty.
box('Bookcase_Back',13.25,14.77,4.14,4.175,.08,.83,cream)
box('Bookcase_Top',13.24,14.78,3.88,4.175,.80,.84,wood)
for i,x in enumerate([13.25,13.75,14.25,14.75]):
    box('Bookcase_Upright'+str(i),x,x+.022,3.90,4.14,.08,.80,cream,.005)
box('Bookcase_Shelf',13.27,14.75,3.90,4.14,.40,.42,cream,.005)
for i,x in enumerate([13.31,13.82,14.32]):
    box('ToyBasket'+str(i),x,x+.36,3.915,4.13,.10,.36,[lightpink,blue,sage][i],.04)
    box('BasketLabel'+str(i),x+.12,x+.24,3.907,3.914,.23,.27,linen,.008)
for i in range(9):
    x=13.34+i*.147
    box('PictureBook'+str(i),x,x+.105,3.94,4.03,.43,.66+(i%3)*.025,[pink,blue,sage,sun][i%4],.004)
    sphere('BookMotif'+str(i),(x+.05,3.932,.56),(.026,.006,.026),cream)
box('BookRail',13.29,14.74,3.905,3.93,.48,.515,cream,.006)

# Small activity table and a round-backed child chair, well outside the entry line.
cylinder('ActivityTop',12.71,2.95,.49,.31,.035,cream)
for i,(x,y) in enumerate([(12.51,2.82),(12.91,2.82),(12.71,3.17)]):
    box('TableLeg'+str(i),x-.022,x+.022,y-.022,y+.022,0,.49,wood,.015)
cylinder('ChairSeat',12.61,2.36,.265,.16,.035,lightpink)
for i,(x,y) in enumerate([(12.50,2.25),(12.72,2.25),(12.50,2.47),(12.72,2.47)]):
    box('ChairLeg'+str(i),x-.018,x+.018,y-.018,y+.018,0,.28,wood,.012)
box('ChairBack',12.44,12.78,2.17,2.21,.29,.55,lightpink,.055)
box('DrawingPaper',12.56,12.83,2.88,3.06,.526,.528,white,.002)
for i in range(3):
    box('Crayon'+str(i),12.67,12.80,3.09+i*.025,3.10+i*.025,.526,.539,[pink,blue,sage][i],.004)

# A single scalloped outline avoids coplanar overlaps between separate petal disks.
outline=[]
for i in range(192):
    a=i*math.tau/192
    r=.46+.065*math.cos(8*a)
    outline.append((13.22+r*math.cos(a),1.98+r*math.sin(a)))
verts=[(x,y,z) for z in (.001,.010) for x,y in outline]
n=len(outline)
faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]
faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
mesh=bpy.data.meshes.new('Q10_FlowerRugMesh'); mesh.from_pydata(verts,[],faces); mesh.update()
obj=bpy.data.objects.new('Q10_Rug_Center',mesh); col.objects.link(obj); mesh.materials.append(lightpink)
cylinder('RugMedallion',13.22,1.98,.011,.24,.002,linen)

# Generic floppy-eared rabbit, not a licensed character asset.
sphere('Bunny_Body',(14.51,2.54,.59),(.105,.09,.14),linen)
sphere('Bunny_Head',(14.51,2.53,.77),(.10,.085,.095),linen)
for i,x in enumerate([14.456,14.565]):
    sphere('Bunny_Ear'+str(i),(x,2.54,.92),(.033,.027,.13),linen)
    sphere('Bunny_EarInner'+str(i),(x,2.516,.92),(.018,.008,.095),lightpink)
for i,x in enumerate([14.476,14.544]):
    sphere('Bunny_Eye'+str(i),(x,2.45,.79),(.008,.006,.01),ink)
sphere('Bunny_Nose',(14.51,2.442,.76),(.012,.008,.008),pink)
for i,x in enumerate([14.43,14.59]):
    sphere('Bunny_Foot'+str(i),(x,2.46,.49),(.05,.07,.04),linen)
for obj in col.objects:
    if obj.name.startswith('Q10_Bunny_'):
        obj.location.y = 5.08-obj.location.y
        obj.rotation_euler.z = math.pi

# Gathered curtains live inside the existing opening; they do not cover the glass with opaque planes.
for side,a,b in [('W',12.46,12.65),('E',14.13,14.32)]:
    verts=[]
    for z in (.08,2.23):
        verts += [(a+(b-a)*i/32,1.02+.028*math.cos(i*math.pi/2),z) for i in range(33)]
    mesh=bpy.data.meshes.new('Q10_CurtainMesh'+side)
    mesh.from_pydata(verts,[],[(i,i+1,i+34,i+33) for i in range(32)])
    mesh.update(); obj=bpy.data.objects.new('Q10_Curtain'+side,mesh); col.objects.link(obj)
    mesh.materials.append(linen)
    solid=obj.modifiers.new('Cloth thickness','SOLIDIFY'); solid.thickness=.003
    for face in mesh.polygons: face.use_smooth=True
box('CurtainTrack',12.44,14.34,1.0,1.04,2.24,2.265,cream,.006)

# Simple botanical wall relief above the bookcase, plus a little bedside shelf/lamp.
box('WallFrame',13.68,14.30,4.16,4.19,1.10,1.85,wood,.018)
box('WallArtPaper',13.71,14.27,4.147,4.16,1.13,1.82,linen,.003)
for i,(x,z,c) in enumerate([(13.84,1.51,pink),(14.10,1.59,blue),(14.0,1.36,sage)]):
    sphere('ArtPetal'+str(i),(x,4.14,z),(.07,.012,.11),c)
box('BedWallFrame',14.94,14.975,2.14,2.80,1.25,1.95,wood,.016)
box('BedWallPaper',14.927,14.94,2.17,2.77,1.28,1.92,linen,.004)
for i in range(6):
    a=i*math.tau/6
    sphere('BedArtPetal'+str(i),(14.919,2.47+.115*math.cos(a),1.62+.115*math.sin(a)),(.008,.08,.08),lightpink)
sphere('BedArtCenter',(14.908,2.47,1.62),(.008,.068,.068),sun)
box('BedsideShelf',14.50,14.88,3.39,3.71,.42,.46,cream,.025)
cylinder('LampBase',14.69,3.55,.46,.075,.018,wood)
cylinder('LampStem',14.69,3.55,.478,.012,.16,wood)
sphere('LampShade',(14.69,3.55,.67),(.10,.10,.08),linen)

# Keep the approved furnishings, but arrange them around the fixed basic wardrobe.
bpy.data.objects.remove(bpy.data.objects['Q10_BedsideShelf'],do_unlink=True)
bpy.context.view_layer.update()
def relocate(prefixes, old, new, angle=0):
    transform=Matrix.Translation(Vector(new)) @ Matrix.Rotation(angle,4,'Z') @ Matrix.Translation(-Vector(old))
    for obj in col.objects:
        if obj.name.startswith(prefixes):
            obj.matrix_world=transform @ obj.matrix_world

relocate(('Q10_Bed_Base','Q10_BedGuard','Q10_Headboard','Q10_Mattress','Q10_Duvet',
          'Q10_FoldedThrow','Q10_QuiltSeam','Q10_Pillow','Q10_Cloud','Q10_Bunny_'),
         (0,0,0),(-1.80,0,0))
# A junior bed keeps a usable passage between its head and the fixed built-in.
bpy.context.view_layer.update()
compact=Matrix.Translation((0,1.1,0)) @ Matrix.Diagonal((1,1.8/2.15,1,1)) @ Matrix.Translation((0,-1.1,0))
for obj in col.objects:
    if obj.name.startswith(('Q10_Bed_Base','Q10_BedGuard','Q10_Headboard','Q10_Mattress','Q10_Duvet',
                            'Q10_FoldedThrow','Q10_QuiltSeam','Q10_Pillow','Q10_Cloud','Q10_Bunny_')):
        obj.matrix_world=compact @ obj.matrix_world
relocate(('Q10_Bookcase_','Q10_ToyBasket','Q10_BasketLabel','Q10_PictureBook','Q10_BookMotif',
          'Q10_BookRail','Q10_WallFrame','Q10_WallArtPaper','Q10_ArtPetal'),
         (14.01,4.04,0),(14.81,1.85,0),-math.pi/2)
relocate(('Q10_ActivityTop','Q10_TableLeg','Q10_Chair','Q10_DrawingPaper','Q10_Crayon'),
         (0,0,0),(1.35,-.20,0))
relocate(('Q10_Rug',),(0,0,0),(.20,.45,0))
relocate(('Q10_BedWall','Q10_BedArt'),(13.47,2.47,0),(13.47,2.47,0),math.pi)
relocate(('Q10_Lamp',),(0,0,0),(.10,-1.45,.38))

led = material('Light',(.91,.84,.69),.4)
bs=led.node_tree.nodes.get('Principled BSDF')
bs.inputs['Emission Color'].default_value=(1,.84,.65,1)
bs.inputs['Emission Strength'].default_value=2
cylinder('CeilingRim',13.45,2.5,2.255,.30,.022,cream)
cylinder('CeilingDiffuser',13.45,2.5,2.249,.27,.006,led)
lightdata=bpy.data.lights.new('Q10_RoomLight','AREA'); lightdata.energy=38; lightdata.shape='DISK'; lightdata.size=1.3
lightdata.color=(1,.90,.80)
lightobj=bpy.data.objects.new(lightdata.name,lightdata); col.objects.link(lightobj); lightobj.location=(13.4,2.5,2.23)

bpy.context.view_layer.update()
runpy.run_path(os.path.join(ROOT,'scripts/verify_yuna_room.py'),run_name='__main__')
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,'apt_84a_photoreal_tour.blend'))
print('Q10 YUNA ROOM SAVED',flush=True)
