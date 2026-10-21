"""Q11: bedroom 2 wall finish and two Erectus workstations.

shortcut: product silhouettes are modeled from public photos, not manufacturer CAD;
replace hardware/optical details with measured assets before procurement or fabrication.
"""
import math
import os
import runpy
import shutil
import sys
import bmesh
import bpy
from mathutils import Matrix, Vector

ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,os.path.join(ROOT,'scripts'))
import generate_high_detail_assets as A

backup=os.path.join(ROOT,'models/backups/apt_84a_photoreal_tour_before_study_room.blend')
if not os.path.exists(backup): shutil.copy2(bpy.data.filepath,backup)
backup=os.path.join(ROOT,'models/backups/apt_84a_photoreal_tour_before_study_equipment.blend')
if not os.path.exists(backup): shutil.copy2(bpy.data.filepath,backup)
for obj in list(bpy.data.objects):
    if obj.name.startswith(('Q11_','Bed2_','SillPatch_Bed2_','Liner_Bed2_','ProDoorHandle_Bed2_')):
        bpy.data.objects.remove(obj,do_unlink=True)
col=A.get_col('Apt_StudyRoom')

def mat(name,rgb,rough=.5,metal=0):
    m=bpy.data.materials.get('Mat_Q11_'+name) or bpy.data.materials.new('Mat_Q11_'+name)
    m.use_nodes=True; m.diffuse_color=(*rgb,1)
    bs=m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value=(*rgb,1)
    bs.inputs['Roughness'].default_value=rough
    bs.inputs['Metallic'].default_value=metal
    return m

white=mat('SuperWhite',(.82,.82,.79),.38)
frame=mat('WhiteFrame',(.73,.75,.74),.30,.25)
black=mat('BlackFrame',(.018,.021,.022),.4)
blackmesh=mat('BlackMesh',(.035,.039,.040),.82)
grey=mat('GreyFrame',(.35,.37,.36),.42)
greymesh=mat('GreyMesh',(.42,.44,.43),.82)
metal=mat('Metal',(.28,.30,.31),.22,.85)
rubber=mat('BlackRubber',(.012,.014,.015),.84)
display=mat('Display',(.005,.009,.012),.25)
digit=mat('Digits',(.35,.73,.9),.4)
bs=digit.node_tree.nodes.get('Principled BSDF')
bs.inputs['Emission Color'].default_value=(.35,.73,.9,1); bs.inputs['Emission Strength'].default_value=.8

def normals(obj):
    bm=bmesh.new(); bm.from_mesh(obj.data)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    bm.to_mesh(obj.data); bm.free()

def box(name,x,y,z,w,d,h,m,bevel=.008):
    obj=A.create_beveled_box('Q11_'+name,x,y,z,w,d,h,bevel=bevel,seg=4,mat=m,col=col)
    normals(obj)
    for f in obj.data.polygons: f.use_smooth=False
    return obj

def mesh(name,verts,faces,m):
    data=bpy.data.meshes.new('Q11_'+name); data.from_pydata(verts,[],faces); data.update()
    obj=bpy.data.objects.new('Q11_'+name,data); col.objects.link(obj); data.materials.append(m)
    return obj

def rod(name,a,b,r,m):
    a,b=Vector(a),Vector(b)
    bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=r,depth=(b-a).length,location=(a+b)/2)
    obj=bpy.context.object; obj.name='Q11_'+name
    obj.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler()
    for c in list(obj.users_collection): c.objects.unlink(obj)
    col.objects.link(obj); obj.data.materials.append(m)
    for f in obj.data.polygons: f.use_smooth=True
    return obj

def tube(name,points,r,m,closed=False):
    data=bpy.data.curves.new('Q11_'+name,'CURVE'); data.dimensions='3D'; data.bevel_depth=r; data.bevel_resolution=3
    p=data.splines.new('POLY'); p.points.add(len(points)-1)
    for v,co in zip(p.points,points): v.co=(*co,1)
    p.use_cyclic_u=closed
    obj=bpy.data.objects.new('Q11_'+name,data); col.objects.link(obj); data.materials.append(m)
    return obj

# Keep the CAD piers; complete the missing interior lining at the same plane as Q10b.
wall=bpy.data.materials['Mat_Wall_Interior']
for name,x1,x2,z1,z2 in [('Sill',9.17,11.868,0,.8),('Header',9.17,11.868,2.2,2.3),
                          ('W',9.17,9.45,.8,2.2),('E',11.18,11.868,.8,2.2)]:
    box('WindowWall_'+name,(x1+x2)/2,.675,z1,x2-x1,.35,z2-z1,wall,.001)
box('WindowSillCap',10.315,.795,.8,1.73,.17,.025,white,.003)
dy=.80-bpy.data.objects['Win_Bed2_Mullion'].location.y
for obj in bpy.data.objects:
    if obj.name.startswith('Win_Bed2_'):
        obj.location.y+=dy; normals(obj)
        if 'Glass' in obj.name:
            obj.data.materials.clear(); obj.data.materials.append(bpy.data.materials['Mat_Q10_Glass'])
for name in ('ExactWall_2','ExactWall_3','ProDoorTrim_Bed2'): normals(bpy.data.objects[name])
leaf=bpy.data.objects['ProDoorLeaf_Bed2']; leaf.rotation_euler.z=math.radians(-85)
for side,sign in [('A',1),('B',-1)]:
    h=box('Handle'+side,0,0,0,.11,.024,.024,metal,.01)
    h.name='ProDoorHandle_Bed2_'+side; h.parent=leaf; h.location=(.75,sign*.045,.97)
box('SkirtS',10.52,.863,0,2.66,.022,.065,white,.003)

def place(prefix,x,y):
    bpy.context.view_layer.update()
    transform=Matrix.Translation((x,y,0)) @ Matrix.Rotation(-math.pi/2,4,'Z')
    for o in col.objects:
        if o.name.startswith('Q11_'+prefix): o.matrix_world=transform @ o.matrix_world

def desk(key,width,depth,x,y):
    p='Desk'+key+'_'
    top=box(p+'Top',0,0,.715,width,depth,.025,white,.012)
    top['product_url']='https://erectus.co.kr/product/detail.html?product_no=136'
    top['size_mm']=f'{int(width*1000)}x{int(depth*1000)}'
    box(p+'Crossbeam',0,.03,.635,width-.28,.09,.065,frame)
    for i,s in enumerate((-1,1)):
        u=s*(width/2-.21)
        box(p+f'Foot{i}',u,0,.027,.08,depth-.10,.045,frame,.02)
        for j,t in enumerate((-.5,.5)):
            box(p+f'Pad{i}{j}',u,t*(depth-.18),.005,.065,.055,.025,rubber,.01)
        box(p+f'ColumnOuter{i}',u,.025,.072,.085,.085,.32,frame,.005)
        box(p+f'ColumnInner{i}',u,.025,.365,.070,.070,.285,frame,.004)
        box(p+f'TopSupport{i}',u,0,.685,.06,depth-.12,.03,frame)
        box(p+f'Motor{i}',u-s*.10,.03,.65,.20,.085,.06,frame)
    box(p+'Controller',width/2-.20,-depth/2+.028,.678,.13,.065,.035,black,.009)
    box(p+'Screen',width/2-.215,-depth/2-.005,.685,.045,.002,.017,display,.002)
    for i in range(3):
        box(p+'Button'+str(i),width/2-.17+i*.018,-depth/2-.006,.69,.010,.003,.008,frame,.002)
    # Cable slack stays under the tabletop, clear of both legs and the floor.
    tube(p+'Cable',[(0,.03,.64),(0,.06,.48),(.06,.1,.40),(.11,.10,.46),(.11,.10,.65)],.004,rubber)
    place('Desk'+key+'_',x,y)

desk('1800',1.8,.8,11.42,1.81)
desk('1400',1.4,.7,11.47,3.47)

def chair(color,x,y):
    p='Aeron'+color+'_'; f,m=(black,blackmesh) if color=='Black' else (grey,greymesh)
    rod(p+'GasLift',(0,0,.1),(0,0,.45),.028,metal)
    box(p+'TiltHousing',0,-.04,.34,.22,.25,.10,f,.04)
    for i in range(5):
        a=math.tau*i/5
        end=(.32*math.cos(a),.32*math.sin(a),.10)
        tube(p+'Spoke'+str(i),[(0,0,.17),(.16*math.cos(a),.16*math.sin(a),.13),end],.022,f)
        rod(p+'Fork'+str(i),end,(end[0],end[1],.048),.012,f)
        for j,s in enumerate((-1,1)):
            a0=(end[0]+s*.019-.009,end[1],.045); b0=(a0[0]+.018,a0[1],a0[2])
            rod(p+f'Caster{i}{j}',a0,b0,.036,f)
    def back(u,v):
        width=.215+.055*math.sin(math.pi*v)
        return (u*width,-.22-.10*v+.045*u*u,.51+.51*v)
    def seat(u,v):
        return (u*(.226-.020*(2*v-1)**4),-.235+.46*v,.475-.026*(1-u*u)+.014*(2*v-1)**2)
    for name,fn in [('Back',back),('Seat',seat)]:
        border=[fn(-1,i/30) for i in range(31)] + [fn(-1+2*i/30,1) for i in range(1,31)]
        border += [fn(1,1-i/30) for i in range(1,31)] + [fn(1-2*i/30,0) for i in range(1,30)]
        tube(p+name+'Frame',border,.014,f,True)
        verts=[]; faces=[]
        # Real holes between thin ribbons survive both Blender and the GLB exporter.
        for axis,count in ((0,45),(1,51)):
            for i in range(count):
                t=i/(count-1); half=.0011/.46
                for j in range(24):
                    a,b=j/24,(j+1)/24
                    points=[(max(0,t-half),a),(min(1,t+half),a),(min(1,t+half),b),(max(0,t-half),b)]
                    n=len(verts)
                    verts.extend(fn(2*s-1,v) if axis==0 else fn(2*v-1,s) for s,v in points)
                    faces.append((n,n+1,n+2,n+3))
        obj=mesh(p+name+'Mesh',verts,faces,m)
        for face in obj.data.polygons: face.use_smooth=True
    for i,s in enumerate((-1,1)):
        tube(p+'ArmSupport'+str(i),[(s*.19,-.18,.36),(s*.30,-.18,.51),(s*.30,-.12,.65)],.020,f)
        box(p+'ArmPad'+str(i),s*.30,-.03,.65,.09,.25,.038,f,.035)
    tube(p+'BackSpine',[(0,-.15,.37),(0,-.27,.51),(0,-.34,.71)],.025,f)
    for i,z in enumerate((.59,.69)):
        box(p+'PostureFit'+str(i),0,-.32-(z-.59)*.2,z,.13,.035,.075,f,.028)
    rod(p+'AdjustmentDial',(.16,-.12,.36),(.23,-.12,.36),.033,f)
    place('Aeron'+color+'_',x,y)

chair('Black',10.81,1.81)
chair('Grey',10.91,3.47)

# All equipment starts in desk coordinates: x across the top, +y toward the wall.
silver=mat('Aluminium',(.43,.46,.49),.29,.75)
screenmat=mat('ScreenOff',(.014,.025,.033),.19)
cone=mat('SpeakerCone',(.065,.067,.058),.8)
keymat=mat('Keycaps',(.65,.66,.64),.55)

def monitor(name,inch,x,y,z):
    width=inch*.0254*16/math.sqrt(337); height=width*9/16
    p='Equipment_'+name+'_'
    box(p+'Housing',x,y,z,width+.016,.046,height+.026,black,.009)
    box(p+'Screen',x,y-.024,z+.018,width,.002,height,screenmat,.002)
    box(p+'Chin',x,y-.025,z+.003,width,.003,.012,black,.002)
    box(p+'PowerLED',x+width/2-.018,y-.028,z+.007,.003,.001,.002,digit,.001)
    box(p+'RearVESA',x,y+.032,z+height/2-.045,.09,.020,.09,black,.008)
    if name.startswith('Dell'):
        # Raised geometric wordmark remains legible without external fonts/textures.
        data=bpy.data.curves.new(p+'Logo','FONT'); data.body='DELL'; data.align_x='CENTER'; data.size=.008
        obj=bpy.data.objects.new('Q11_'+p+'Logo',data); col.objects.link(obj)
        obj.location=(x,y-.028,z+.004); obj.rotation_euler=(math.pi/2,0,0); data.materials.append(silver)

def keyboard(key,x,y,width,m):
    p='Equipment_Keyboard'+key+'_'
    box(p+'Base',x,y,.741,width,.13,.016,m,.008)
    for row in range(5):
        count=14
        for i in range(count):
            if row==0 and 4<=i<=8: continue
            box(p+f'Key{row}_{i}',x-width/2+.018+i*(width-.036)/13,y-.05+row*.024,.757,
                (width-.05)/14,.018,.004,keymat if key=='1800' else black,.002)
    box(p+'Space',x,y-.05,.757,width*.34,.018,.004,keymat if key=='1800' else black,.002)

def mouse(key,x,y,m):
    p='Equipment_Mouse'+key+'_'
    box(p+'Body',x,y,.741,.060,.105,.030,m,.025)
    box(p+'Split',x,y+.02,.770,.001,.044,.001,black,.0004)
    box(p+'Wheel',x,y+.025,.770,.006,.018,.004,rubber,.002)

for side,x in [('L',-.315),('R',.315)]:
    monitor('Dell27_'+side,27,x,.13,.94)
    p='Equipment_Arm27_'+side+'_'
    box(p+'Clamp',x,.415,.69,.065,.025,.063,black,.004)
    box(p+'ClampPad',x,.365,.741,.070,.12,.012,black,.004)
    box(p+'ClampJaw',x,.38,.69,.055,.08,.012,black,.004)
    rod(p+'ClampScrew',(x,.36,.702),(x,.36,.714),.009,metal)
    rod(p+'Post',(x,.34,.753),(x,.34,1.09),.017,metal)
    tube(p+'Lower',[(x,.34,.99),(x+(.10 if side=='L' else -.10),.29,1.09)],.024,black)
    tube(p+'Upper',[(x+(.10 if side=='L' else -.10),.29,1.09),(x,.185,1.075)],.022,black)
    rod(p+'Joint',(x,.185,1.045),(x,.185,1.105),.030,black)
    tube(p+'Cable',[(x,.17,1.08),(x,.27,1.05),(x,.35,.88),(x,.35,.70)],.003,rubber)
    p='Equipment_A2_'+side+'_'; sx=-.765 if side=='L' else .765
    box(p+'Cabinet',sx,.22,.74,.1016,.13335,.1524,black,.006)
    rod(p+'WooferRim',(sx,.151,.796),(sx,.146,.796),.038,black)
    rod(p+'Woofer',(sx,.145,.796),(sx,.142,.796),.032,cone)
    rod(p+'DustCap',(sx,.141,.796),(sx,.139,.796),.013,black)
    rod(p+'TweeterRim',(sx,.151,.857),(sx,.146,.857),.015,black)
    rod(p+'Tweeter',(sx,.145,.857),(sx,.142,.857),.0095,cone)
    box(p+'SlotPort',sx,.151,.752,.073,.002,.007,rubber,.002)
    tube(p+'Cable',[(sx,.287,.79),(sx,.30,.76),(sx,.36,.70)],.002,rubber)

box('Equipment_MacBook_Stand',.665,.025,.741,.073,.18,.025,silver,.009)
for i,s in enumerate((-1,1)):
    box('Equipment_MacBook_StandJaw'+str(i),.665+s*.018,.025,.755,.014,.13,.060,silver,.006)
box('Equipment_MacBook_Closed',.665,.025,.766,.016,.221,.312,silver,.007)
box('Equipment_MacBook_LidSeam',.655,.025,.772,.001,.207,.299,black,.001)
tube('Equipment_MacBook_USBC',[(.675,-.03,.80),(.71,-.03,.77),(.72,.32,.752),(.4,.35,.70)],.0025,rubber)
keyboard('1800',-.08,-.24,.355,silver)
mouse('1800',.22,-.24,white)
place('Equipment_',11.42,1.81)

# Small desk uses a separate 120mm riser and a freestanding 32-inch display.
# shortcut: exact gaming monitor/tower models are unspecified; replace these generic 16:9 assets when known.
box('Small_GamingRiser_Top',0,.13,.842,.82,.25,.018,white,.008)
for i,s in enumerate((-1,1)):
    box('Small_GamingRiser_Leg'+str(i),s*.37,.13,.74,.025,.25,.102,white,.004)
monitor('Gaming32',32,0,.14,1.01)
# Move only this display into the small-desk namespace before its placement.
for o in col.objects:
    if o.name.startswith('Q11_Equipment_Gaming32_'): o.name=o.name.replace('Equipment_','Small_',1)
box('Small_Gaming32_Foot',0,.12,.86,.32,.19,.018,black,.015)
box('Small_Gaming32_Stem',0,.17,.878,.055,.05,.25,black,.009)
keyboard('1400',-.10,-.22,.43,black)
mouse('1400',.255,-.22,black)
for o in col.objects:
    if o.name.startswith(('Q11_Equipment_Keyboard1400_','Q11_Equipment_Mouse1400_')):
        o.name=o.name.replace('Equipment_','Small_',1)
box('Small_Desktop_Case',-.31,.04,.025,.19,.40,.45,black,.015)
box('Small_Desktop_Front',-.31,-.165,.045,.165,.008,.405,display,.005)
for i in range(18):
    box('Small_Desktop_Vent'+str(i),-.31,-.170,.07+i*.018,.135,.002,.003,rubber,.001)
box('Small_Desktop_Power',-.25,-.171,.435,.012,.003,.006,digit,.002)
place('Small_',11.47,3.47)
# Keep stable equipment names for verification and future room updates.
for o in col.objects:
    if o.name.startswith('Q11_Small_'): o.name=o.name.replace('Q11_Small_','Q11_Equipment_',1)

led=mat('Light',(.90,.91,.88),.4)
bs=led.node_tree.nodes.get('Principled BSDF')
bs.inputs['Emission Color'].default_value=(1,.97,.90,1); bs.inputs['Emission Strength'].default_value=2
rod('CeilingRim',(10.5,2.55,2.258),(10.5,2.55,2.283),.29,frame)
rod('CeilingDiffuser',(10.5,2.55,2.251),(10.5,2.55,2.258),.27,led)
ld=bpy.data.lights.new('Q11_RoomLight','AREA'); ld.energy=110; ld.shape='DISK'; ld.size=1.4
ld.color=(1,.97,.91)
light=bpy.data.objects.new(ld.name,ld); col.objects.link(light); light.location=(10.5,2.55,2.23)

# Curves must become meshes so the same chair and cable geometry reaches the web.
for obj in list(col.objects):
    if obj.type in ('CURVE','FONT'):
        bpy.ops.object.select_all(action='DESELECT'); obj.select_set(True); bpy.context.view_layer.objects.active=obj
        bpy.ops.object.convert(target='MESH')
runpy.run_path(os.path.join(ROOT,'scripts/verify_study_room.py'),run_name='__main__')
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,'apt_84a_photoreal_tour.blend'))
print('Q11 STUDY ROOM SAVED',flush=True)
