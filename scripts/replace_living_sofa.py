"""Q14: photo-based Seat&More Brest, ivory, closed recliners and folded centre tray.

shortcut: envelope follows official dimensions; upholstery/hinges are photo approximations,
replace with measured manufacturer assets before evaluating motor travel or fabrication.
"""
import math
from pathlib import Path
import runpy
import shutil
import sys
import bpy
import bmesh
from mathutils import Vector
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'scripts'))
import generate_high_detail_assets as A

assert bpy.context.scene.get('Q12_dimensions_version')==1
backup=ROOT/'models/backups/apt_84a_photoreal_tour_before_brest_sofa.blend'
if not backup.exists(): shutil.copy2(bpy.data.filepath,backup)
bpy.context.view_layer.update()
old=bpy.data.objects.get('Sofa_Living_Base')
if old:
    ys=[(old.matrix_world@Vector(c)).y for c in old.bound_box]
    cy=(min(ys)+max(ys))/2
else: cy=bpy.context.scene['Q14_sofa_centre_y']
for o in list(bpy.data.objects):
    if o.name.startswith(('Sofa_Living_','Q2_Sofa','Q14_Brest_')): bpy.data.objects.remove(o,do_unlink=True)
col=A.get_col('Apt_BrestSofa')
front=8.805-.150-1.000

def material(name,color,rough):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes=True; m.diffuse_color=(*color,1)
    bs=m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value=(*color,1); bs.inputs['Roughness'].default_value=rough
    return m
leather=material('Mat_Q14_IvoryLeather',(.67,.61,.52),.43)
stitch=material('Mat_Q14_LeatherSeam',(.40,.35,.28),.58)
dark=material('Mat_Q14_Mechanism',(.016,.018,.020),.55)
wood=material('Mat_Q14_WoodFeet',(.10,.042,.025),.40)
tray=material('Mat_Q14_Tray',(.18,.16,.13),.55)
metal=material('Mat_Q14_Switch',(.28,.28,.27),.26)
metal.node_tree.nodes.get('Principled BSDF').inputs['Metallic'].default_value=.7

def soft(name,v0,v1,u0,u1,z0,z1,r=.045,mat=leather,lean=0):
    half=Vector(((v1-v0)/2,(u1-u0)/2,(z1-z0)/2))
    centre=Vector((front+(v0+v1)/2,cy+(u0+u1)/2,(z0+z1)/2))
    r=min(r,min(half)*.9); vertices=[]; faces=[]; n=8
    for axis in range(3):
        a,b=[i for i in range(3) if i!=axis]
        for sign in (-1,1):
            start=len(vertices)
            for i in range(n+1):
                for j in range(n+1):
                    q=Vector((0,0,0)); q[axis]=sign*half[axis]
                    q[a]=half[a]*(2*i/n-1); q[b]=half[b]*(2*j/n-1)
                    core=Vector(tuple(max(-half[k]+r,min(half[k]-r,q[k])) for k in range(3)))
                    delta=q-core; p=core+delta.normalized()*r
                    p[axis]+=sign*.012*(1-(q[a]/half[a])**2)*(1-(q[b]/half[b])**2)
                    p.x+=lean*p.z/half.z
                    vertices.append(p)
            for i in range(n):
                for j in range(n):
                    k=start+i*(n+1)+j; faces.append((k,k+1,k+n+2,k+n+1))
    lo=Vector(tuple(min(v[i] for v in vertices) for i in range(3)))
    hi=Vector(tuple(max(v[i] for v in vertices) for i in range(3)))
    vertices=[tuple(centre[i]-half[i]+(v[i]-lo[i])*2*half[i]/(hi[i]-lo[i]) for i in range(3)) for v in vertices]
    mesh=bpy.data.meshes.new('Q14_Brest_'+name); mesh.from_pydata(vertices,[],faces); mesh.update()
    o=bpy.data.objects.new(mesh.name,mesh); col.objects.link(o); mesh.materials.append(mat)
    bm=bmesh.new(); bm.from_mesh(mesh)
    bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces)); bm.to_mesh(mesh); bm.free()
    for f in mesh.polygons: f.use_smooth=True
    return o

soft('RearShell',.84,1.0,-1.31,1.31,.07,.80,.055)
soft('Underframe',.09,.88,-1.25,1.25,.035,.13,.015,dark)
for side,u in enumerate((-1.305,1.305)):
    soft('Arm'+str(side)+'_Body',.03,.98,u-.10,u+.10,.055,.585,.04)
    soft('Arm'+str(side)+'_Wing',.70,1.0,u-.10,u+.10,.43,.94,.06,lean=.025)
    soft('Arm'+str(side)+'_Roll',.0,.70,u-.12,u+.12,.535,.65,.045)
    for v in (.08,.87):
        soft('Foot'+str(side)+str(v),v,v+.08,u-.09,u+.09,0,.065,.012,wood)
    inside=u+(.124 if side==0 else -.124)
    soft('Switch'+str(side),.23,.32,inside-.005,inside+.005,.49,.575,.003,metal)
    for j in range(2):
        soft('Button'+str(side)+str(j),.245+j*.032,.267+j*.032,inside-.007,inside+.007,.53,.55,.003,dark)
    soft('USB'+str(side),.258,.285,inside-.008,inside+.008,.501,.509,.001,dark)

seats=[]; footrests=[]
for i,u in enumerate((-.81,0,.81)):
    footrests.append(soft('Footrest'+str(i),0,.19,u-.394,u+.394,.07,.345,.045))
    seats.append(soft('Seat'+str(i),.035,.73,u-.395,u+.395,.335,.465,.048))
    if i!=1:
        soft('Lumbar'+str(i),.66,.925,u-.394,u+.394,.445,.765,.055,lean=.025)
        soft('Headrest'+str(i),.77,.995,u-.397,u+.397,.735,.95,.045,lean=.018)
soft('CentreBackPanel',.91,.985,-.397,.397,.47,.855,.025)
soft('CentreTraySupport',.47,.88,-.39,.39,.505,.60,.035)
soft('FoldTray',.50,.86,-.355,.355,.595,.614,.006,tray)
soft('TrayPaddedLip',.445,.51,-.397,.397,.52,.625,.027)

# Seams follow the cushion surface instead of floating in front of it.
bpy.context.view_layer.update()
def seam(name,o,z):
    ys=[v.co.y for v in o.data.vertices]; y0,y1=min(ys)+.035,max(ys)-.035
    pts=[]
    for i in range(25):
        hit,p,_,_=o.ray_cast(Vector((front-.1,y0+(y1-y0)*i/24,z)),Vector((1,0,0)))
        if hit: pts.append(p+Vector((-.001,0,0)))
    assert len(pts)>20
    data=bpy.data.curves.new('Q14_Brest_'+name,'CURVE'); data.dimensions='3D'
    data.bevel_depth=.0011; data.bevel_resolution=2
    spline=data.splines.new('POLY'); spline.points.add(len(pts)-1)
    for point,p in zip(spline.points,pts): point.co=(*p,1)
    o=bpy.data.objects.new(data.name,data); col.objects.link(o); data.materials.append(stitch)
    bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active=o
    bpy.ops.object.convert(target='MESH'); o.select_set(False)
for i,o in enumerate(seats): seam('SeatSeam'+str(i),o,.405)
for i,o in enumerate(footrests): seam('FootrestSeam'+str(i),o,.195)

bpy.context.scene['Q14_sofa_centre_y']=cy
bpy.context.scene['Q14_sofa']='Seat&More Brest 2850x1000x950 ivory, closed recliners, centre tray lowered'
bpy.context.view_layer.update()
runpy.run_path(str(ROOT/'scripts/verify_brest_sofa.py'),run_name='__main__')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'apt_84a_photoreal_tour.blend'))
print('Q14 BREST SAVED',flush=True)
