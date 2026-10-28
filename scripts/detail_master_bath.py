"""Q24 master bathroom from official84A VR011; preserve Q12 walls/Q23c."""
from pathlib import Path
import bpy, bmesh, math, hashlib, json, shutil, sys
from mathutils import Vector
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'scripts'))
import generate_high_detail_assets as A
backup=ROOT/'models/backups/apt_84a_photoreal_tour_before_master_bath_detail.blend'
if not backup.exists(): shutil.copy2(bpy.data.filepath,backup)

def wall_hash():
    rows=[(o.name,[list(r) for r in o.matrix_world],[list(v.co) for v in o.data.vertices],
           [list(p.vertices) for p in o.data.polygons]) for o in sorted(bpy.data.objects,key=lambda o:o.name)
          if o.type=='MESH' and o.name.startswith('ExactWall_')]
    return hashlib.sha256(json.dumps(rows).encode()).hexdigest()
before=wall_hash()
for o in list(bpy.data.objects):
    if o.name.startswith(('Q24_','Master_Bathtub_','Master_Toilet_','BathProp_Master',
                          'ProDoorLeaf_MasterBath','ProDoorHandle_MasterBath','ProDoorTrim_MasterBath',
                          'ProDoorPivot_MasterBath')) or o.name in ('Master_Vanity_Top','Floor_MasterBath','PBR_Down_Bath2'):
        bpy.data.objects.remove(o,do_unlink=True)
col=A.get_col('Apt_MasterBathDetail')

def mat(name,color,rough=.45,metal=0):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes=True; m.diffuse_color=(*color,1)
    s=m.node_tree.nodes.get('Principled BSDF')
    s.inputs['Base Color'].default_value=(*color,1);s.inputs['Roughness'].default_value=rough;s.inputs['Metallic'].default_value=metal
    return m
ceramic=mat('Mat_Q24_Ceramic',(.84,.84,.82),.16)
stone=mat('Mat_Q24_Stone',(.70,.69,.65),.32)
grout=mat('Mat_Q24_Grout',(.43,.42,.39),.85)
chrome=mat('Mat_Q24_Chrome',(.67,.69,.70),.16,1)
mirror=mat('Mat_Q24_Mirror',(.89,.91,.93),.025,1)
ivory=mat('Mat_Q24_Ivory',(.78,.77,.73),.35)
dark=mat('Mat_Q24_Dark',(.045,.045,.04),.65)
towel=mat('Mat_Q24_Towel',(.78,.76,.71),.96)
band=mat('Mat_Q24_TowelBand',(.37,.36,.34),.95)
led=mat('Mat_Q24_LED',(1.,.94,.83),.4)
led.node_tree.nodes.get('Principled BSDF').inputs['Emission Color'].default_value=(1.,.94,.83,1)
led.node_tree.nodes.get('Principled BSDF').inputs['Emission Strength'].default_value=2
photo=bpy.data.images.load(str(ROOT/'assets/textures_export/q24_tile_albedo.png'),check_existing=True);photo.pack()
tiles=[]
for name,rough in [('WallTile',.55),('FloorTile',.72)]:
    m=mat('Mat_Q24_'+name,(.60,.59,.56),rough)
    nodes=m.node_tree.nodes; links=m.node_tree.links
    for node in list(nodes):
        if node.type not in ('BSDF_PRINCIPLED','OUTPUT_MATERIAL'):nodes.remove(node)
    image=nodes.new('ShaderNodeTexImage');image.image=photo
    uv=nodes.new('ShaderNodeUVMap');uv.uv_map='TilePhotoUV'
    links.new(uv.outputs['UV'],image.inputs['Vector'])
    links.new(image.outputs['Color'],nodes.get('Principled BSDF').inputs['Base Color'])
    tiles.append(m)

def box(name,x1,x2,y1,y2,z1,z2,material,bevel=.001):
    o=A.create_beveled_box(name,(x1+x2)/2,(y1+y2)/2,z1,x2-x1,y2-y1,z2-z1,mat=material,col=col,bevel=bevel,seg=3)
    bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
    for p in o.data.polygons:p.use_smooth=False
    return o

def cylinder(name,a,b,r,material):
    d=Vector(b)-Vector(a)
    o=A.create_cylinder(name,*a,r,d.length,seg=32,mat=material,col=col)
    o.rotation_euler=d.to_track_quat('Z','Y').to_euler()
    return o

def tube(name,points,r,material):
    c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.bevel_depth=r;c.bevel_resolution=3
    sp=c.splines.new('BEZIER');sp.bezier_points.add(len(points)-1)
    for p,co in zip(sp.bezier_points,points):p.co=co;p.handle_left_type='AUTO';p.handle_right_type='AUTO'
    o=bpy.data.objects.new(name,c);col.objects.link(o);c.materials.append(material)
    return o

def loft(name,rings,material,power=4,caps=True):
    count=64
    def rounded(v):return math.copysign(abs(v)**(2/power),v)
    verts=[(cx+rx*rounded(math.cos(i*2*math.pi/count)),cy+ry*rounded(math.sin(i*2*math.pi/count)),z)
           for cx,cy,rx,ry,z in rings for i in range(count)]
    faces=[(j*count+i,j*count+(i+1)%count,(j+1)*count+(i+1)%count,(j+1)*count+i)
           for j in range(len(rings)-1) for i in range(count)]
    if caps:faces += [tuple(reversed(range(count))),tuple(range((len(rings)-1)*count,len(rings)*count))]
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update()
    bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
    o=bpy.data.objects.new(name,mesh);col.objects.link(o);mesh.materials.append(material)
    for p in mesh.polygons:p.use_smooth=len(p.vertices)==4
    return o

def photo_uv(o):
    mesh=o.data;layer=mesh.uv_layers.new(name='TilePhotoUV')
    for face in mesh.polygons:
        axes=[i for i in range(3) if i!=max(range(3),key=lambda i:abs(face.normal[i]))]
        coords=[mesh.vertices[mesh.loops[i].vertex_index].co for i in face.loop_indices]
        lo=[min(p[a] for p in coords) for a in axes];hi=[max(p[a] for p in coords) for a in axes]
        for loop,p in zip(face.loop_indices,coords):
            u,v=[(p[a]-l)/max(h-l,1e-8) for a,l,h in zip(axes,lo,hi)]
            layer.data[loop].uv=(u,v)

def grid(tag,u1,u2,v1,v2,su,sv,axis,depth,material):
    for i in range(math.ceil((u2-u1)/su)):
        for j in range(math.ceil((v2-v1)/sv)):
            a,b=u1+i*su+.001,min(u1+(i+1)*su,u2)-.001
            c,d=v1+j*sv+.001,min(v1+(j+1)*sv,v2)-.001
            if a>=b or c>=d:continue
            bounds=(*depth,a,b,c,d) if axis=='x' else ((a,b,*depth,c,d) if axis=='y' else (a,b,c,d,*depth))
            o=box(f'Q24_Tile_{tag}_{i}_{j}',*bounds,material,.0004);photo_uv(o)

# Thin linings stay inside the preserved clear envelope; no tile crosses the door.
box('Floor_MasterBath',2.595,4.095,5.970,8.170,.002,.012,grout,0)
grid('Floor',2.607,4.083,5.982,8.158,.3,.3,'z',(.012,.016),tiles[1])
for tag,u1,u2,axis,depth in [('E',5.970,8.170,'x',(4.083,4.095)),
                           ('W',6.750,8.170,'x',(2.595,2.607)),
                           ('S',2.595,4.095,'y',(5.970,5.982)),
                           ('N',2.595,4.095,'y',(8.158,8.170))]:
    backing=(depth[0]+.004,depth[1]) if tag in ('E','N') else (depth[0],depth[1]-.004)
    box('Q24_Grout_'+tag,*((*backing,u1,u2,.016,2.28) if axis=='x' else (u1,u2,*backing,.016,2.28)),grout,0)
    grid(tag,u1,u2,.016,2.280,.6,.3,axis,depth,tiles[0])
grid('DoorHeader',5.970,6.750,2.150,2.280,.6,.3,'x',(2.595,2.607),tiles[0])
box('Q24_Threshold',2.445,2.620,5.970,6.750,.012,.027,stone)
box('Q24_FloorDrain',3.145,3.285,6.735,6.875,.016,.019,chrome)
for i in range(7):box('Q24_DrainSlot'+str(i),3.157+i*.017,3.163+i*.017,6.748,6.862,.019,.0195,dark,.0002)

# Hollow bath across the north end, with hand shower rather than an invented cubicle.
loft('Q24_Tub',[(3.345,7.7875,.68,.31,.020),(3.345,7.7875,.735,.3675,.530),
               (3.345,7.7875,.735,.3675,.550),(3.345,7.7875,.637,.270,.550),
               (3.345,7.7875,.590,.230,.180),(3.345,7.7875,.480,.170,.145),
               (3.345,7.7875,.001,.001,.145)],ceramic,power=8)
box('Q24_TubApron',2.612,4.078,7.415,7.431,.020,.531,ceramic,.004)
cylinder('Q24_TubDrain',(3.78,7.78,.145),(3.78,7.78,.148),.027,chrome)

# Wall-hung ceramic washbasin and half pedestal, with a genuine inner bowl.
loft('Master_Vanity_Top',[(3.79,6.90,.280,.340,.825),(3.79,6.90,.280,.340,.850),
                         (3.79,6.90,.230,.280,.850),(3.79,6.90,.230,.280,.825)],ceramic,caps=False)
loft('Q24_Basin',[(3.79,6.90,.150,.210,.650),(3.79,6.90,.270,.330,.815),
                 (3.79,6.90,.230,.280,.833),(3.79,6.90,.185,.235,.765),
                 (3.79,6.90,.085,.110,.705),(3.79,6.90,.001,.001,.700)],ceramic)
loft('Q24_BasinPedestal',[(3.98,6.9,.045,.080,.270),(3.98,6.9,.075,.110,.400),
                         (3.98,6.9,.095,.145,.670)],ceramic)
cylinder('Q24_BasinDrain',(3.79,6.9,.700),(3.79,6.9,.703),.025,chrome)
cylinder('Q24_FaucetStem',(4.015,6.90,.850),(4.015,6.90,1.000),.027,chrome)
box('Q24_FaucetSpout',3.885,4.040,6.875,6.925,.977,1.002,chrome,.006)
box('Q24_FaucetLever',3.970,4.050,6.887,6.913,.995,1.010,chrome,.003)

# Toilet faces west, fully inside the room; the old bowl crossed the south wall.
loft('Q24_Toilet_Bowl',[(3.73,6.32,.18,.145,.018),(3.70,6.32,.22,.16,.12),
                       (3.68,6.32,.255,.185,.34),(3.68,6.32,.260,.190,.405)],ceramic)
loft('Q24_Toilet_Lid',[(3.68,6.32,.260,.190,.414),(3.68,6.32,.255,.185,.445)],ceramic)
box('Q24_Toilet_Tank',3.925,4.075,6.120,6.520,.380,.760,ceramic,.025)
box('Q24_Toilet_TankLid',3.918,4.078,6.115,6.525,.760,.779,ceramic,.016)
box('Q24_Toilet_BidetControl',3.60,3.79,6.516,6.555,.420,.450,ivory,.012)
cylinder('Q24_Toilet_Flush',(3.99,6.32,.779),(3.99,6.32,.785),.024,chrome)

# Continuous mirrored wall cabinet and a shallow stone shelf beneath it.
box('Q24_MirrorCabinet_Back',4.055,4.079,6.080,7.405,1.175,2.120,ivory)
for tag,y in [('S',6.080),('N',7.385)]:box('Q24_MirrorCabinet_'+tag,3.865,4.075,y,y+.020,1.175,2.120,ivory)
for tag,z in [('Top',2.100),('Bottom',1.175)]:box('Q24_MirrorCabinet_'+tag,3.865,4.075,6.080,7.405,z,z+.020,ivory)
for i,(y1,y2) in enumerate(((6.083,6.521),(6.524,6.962),(6.965,7.402))):
    box('Q24_MirrorDoor'+str(i),3.854-i*.002,3.859-i*.002,y1,y2,1.185,2.110,mirror,.001)
box('Q24_MirrorShelf',3.925,4.081,6.080,7.405,1.020,1.040,stone,.002)

# Photo-observed shower rail/mixer/handset/hose and two corner shelves.
cylinder('Q24_Shower_Rail',(4.035,7.77,.970),(4.035,7.77,1.850),.012,chrome)
for z in (1.,1.81):cylinder('Q24_Shower_Mount'+str(z),(4.035,7.77,z),(4.081,7.77,z),.020,chrome)
cylinder('Q24_Shower_Head',(3.982,7.77,1.850),(3.940,7.77,1.810),.064,chrome)
cylinder('Q24_Shower_Face',(3.940,7.77,1.810),(3.937,7.77,1.807),.059,ivory)
cylinder('Q24_Shower_Mixer',(4.000,7.640,.780),(4.000,7.890,.780),.027,chrome)
tube('Q24_Shower_Hose',[(4.,7.81,.76),(3.94,7.85,.57),(3.90,7.70,.60),(3.98,7.77,1.80)],.009,chrome)
tube('Q24_TubSpout',[(4.02,7.65,.79),(3.92,7.65,.79),(3.89,7.65,.74)],.018,chrome)
for i,z in enumerate((1.12,1.40)):
    box('Q24_CornerShelf'+str(i),3.84,4.075,7.98,8.15,z,z+.016,chrome,.008)

# Towel rail/rack on west wall beyond the door opening, paper dispenser on south.
for y in (6.94,7.48):cylinder('Q24_TowelMount'+str(y),(2.607,y,1.20),(2.675,y,1.20),.018,chrome)
cylinder('Q24_TowelRail',(2.675,6.94,1.20),(2.675,7.48,1.20),.012,chrome)
box('Q24_Towel',2.676,2.697,7.025,7.385,.660,1.205,towel,.006)
box('Q24_TowelBand',2.697,2.699,7.025,7.385,.710,.800,band,.001)
for y in (7.0,7.55):cylinder('Q24_RackArm'+str(y),(2.607,y,1.78),(2.84,y,1.78),.012,chrome)
for x in (2.66,2.74,2.82):cylinder('Q24_RackRail'+str(x),(x,7.0,1.78),(x,7.55,1.78),.009,chrome)
box('Q24_FoldedTowel',2.65,2.82,7.07,7.47,1.79,1.84,towel,.015)
box('Q24_PaperBack',3.475,3.655,5.984,5.996,.690,.940,chrome,.004)
box('Q24_PaperCover',3.475,3.655,5.996,6.065,.770,.805,chrome,.004)
cylinder('Q24_PaperRoll',(3.495,6.04,.744),(3.635,6.04,.744),.036,towel)

# Door: south hinge, opens85deg into the bathroom. This leaves the handle clear
# of the south tiled wall; the former automatic swing chose the powder side.
for tag,y1,y2 in [('S',5.940,5.970),('N',6.750,6.780)]:
    box('ProDoorTrim_MasterBath_'+tag,2.445,2.620,y1,y2,.016,2.145,ivory,.002)
box('ProDoorTrim_MasterBath_Head',2.445,2.620,5.940,6.780,2.115,2.155,ivory,.002)
hinge=bpy.data.objects.new('ProDoorPivot_MasterBath',None);col.objects.link(hinge);hinge.location=(2.610,6.010,0)
leaf=box('ProDoorLeaf_MasterBath',2.590,2.630,6.010,6.750,.027,2.100,ivory,.003)
handleparts=[]
for side,x1,x2 in [('A',2.550,2.590),('B',2.630,2.670)]:
    handleparts.append(box('ProDoorHandle_MasterBath_'+side,x1,x2,6.600,6.720,.972,.996,chrome,.006))
    handleparts.append(cylinder('ProDoorHandle_MasterBath_Rose'+side,(x1,6.64,.985),(x2,6.64,.985),.025,chrome))
bpy.context.view_layer.update()
for obj in [leaf,*handleparts]:obj.parent=hinge;obj.matrix_parent_inverse=hinge.matrix_world.inverted()
hinge.rotation_euler.z=-math.radians(85)

box('Q24_Ceiling',2.595,4.095,5.970,8.170,2.280,2.295,ivory,0)
box('Q24_AccessPanel',3.10,3.62,7.30,7.82,2.275,2.280,ivory,.004)
box('Q24_Vent',2.88,3.08,6.85,7.05,2.272,2.280,ivory,.004)
for i in range(7):box('Q24_VentSlot'+str(i),2.900+i*.023,2.908+i*.023,6.87,7.03,2.270,2.272,dark,.0005)
for i,y in enumerate((6.45,7.55)):
    cylinder('Q24_Downlight'+str(i),(3.35,y,2.268),(3.35,y,2.277),.060,led)
    data=bpy.data.lights.new('Q24_Light'+str(i),'AREA');data.energy=32;data.shape='DISK';data.size=.18
    obj=bpy.data.objects.new(data.name,data);col.objects.link(obj);obj.location=(3.35,y,2.26)
bpy.context.view_layer.update()
assert wall_hash()==before,'Structural geometry changed'
sc=bpy.context.scene;sc['Q24_master_bath']=1;sc['Q24_wall_sha256']=before
sc['Q24_master_bath_source']='Official84A VR011; dimensions and hardware detail photo-based'
sc['Q24_door_open_degrees']=85
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'apt_84a_photoreal_tour.blend'))
print('Q24 saved: official-photo bathroom, inward85deg door, preserved structural walls')
