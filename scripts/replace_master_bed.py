"""Q22 current-model patch: Restandard grey K, no head, 115mm wood legs.

Official dimensions, photo-derived stitching/quilting/leg arrangement. Not a
manufacturer CAD model. Run on the current master, never on an old migration.
"""
from pathlib import Path
import math
import runpy
import shutil
import sys
import bpy
import bmesh
import numpy as np
from mathutils import Vector

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))
import generate_high_detail_assets as A

sc = bpy.context.scene
assert sc.get('Q21_lg_washtower') == 1, 'Apply only to current Q21 or later master'
backup = ROOT / 'models/backups/apt_84a_photoreal_tour_before_restandard_bed.blend'
if not backup.exists():
    shutil.copy2(bpy.data.filepath, backup)
for obj in list(bpy.data.objects):
    if obj.name.startswith(('Bed_Master_', 'Q2_Master_Cushion', 'Q22_Restandard_', 'Q22_Detail_', 'Nightstand_Master_', 'Q2_Night', 'Q2_Pendant')) or obj.name in ('Q2_Master_Panel','Q2_Master_CoveTop','Q2_Master_CoveLow','Q2_Master_Rug'):
        bpy.data.objects.remove(obj, do_unlink=True)
col = A.get_col('Apt_RestandardBed')
bpy.context.view_layer.update()
wall=bpy.data.objects['ExactWall_13']
inv=wall.matrix_world.inverted()
hit,wall_point,_,_=wall.ray_cast(inv @ Vector((2.,3.2222,1.)),inv.to_3x3() @ Vector((-1,0,0)))
assert hit, 'Master west wall missing'
wall_x=(wall.matrix_world @ wall_point).x
CX, CY, FLOOR = wall_x+1., 3.2222, .0

def fabric(name, color, wood=False):
    """Packed UV texture survives the existing glTF exporter, including weave."""
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.diffuse_color = (*color, 1)
    nodes = mat.node_tree.nodes; nodes.clear(); links = mat.node_tree.links
    bs = nodes.new('ShaderNodeBsdfPrincipled')
    bs.inputs['Roughness'].default_value = .49 if wood else .86
    bs.inputs['Sheen Weight'].default_value = .04 if wood else .15
    tex = nodes.new('ShaderNodeTexImage')
    rng = np.random.default_rng(22)
    yy, xx = np.mgrid[:256, :256]
    if wood:
        variation = .07*np.sin(xx*.23+np.sin(yy*.035)*1.8) + rng.normal(0,.012,(256,256))
    else:
        variation = .025*((xx%4<2).astype(float)-(yy%4<2).astype(float)) + rng.normal(0,.013,(256,256))
    rgba = np.ones((256,256,4), np.float32)
    rgba[:,:,:3] = np.clip(np.array(color)[None,None,:]+variation[:,:,None],0,1)
    im = bpy.data.images.get(name+'_Weave') or bpy.data.images.new(name+'_Weave',256,256)
    im.pixels.foreach_set(rgba.ravel())
    im.filepath_raw = str(ROOT/'assets/textures_export'/('q22_'+('wood' if wood else name.split('_')[-1].lower())+'.png'))
    im.file_format = 'PNG'; im.save(); im.pack()
    tex.image = im
    links.new(tex.outputs['Color'],bs.inputs['Base Color'])
    bump=nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=.12
    bump.inputs['Distance'].default_value=.00035
    links.new(tex.outputs['Color'],bump.inputs['Height']); links.new(bump.outputs['Normal'],bs.inputs['Normal'])
    out=nodes.new('ShaderNodeOutputMaterial'); links.new(bs.outputs['BSDF'],out.inputs['Surface'])
    return mat

grey = fabric('Mat_Q22_Grey', (.47,.455,.435))
white = fabric('Mat_Q22_White', (.88,.86,.815))
wood = fabric('Mat_Q22_Wood', (.29,.15,.075), True)

def plain(name, color, rough=.8):
    mat=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes=True; mat.diffuse_color=(*color,1)
    bs=mat.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value=(*color,1); bs.inputs['Roughness'].default_value=rough
    return mat

grey_seam=plain('Mat_Q22_GreyPiping',(.24,.23,.21))
cream_seam=plain('Mat_Q22_CreamPiping',(.72,.69,.62))
tag_mat=plain('Mat_Q22_Label',(.73,.72,.67))

def uv_map(obj):
    uv=obj.data.uv_layers.new(name='Q22UV')
    for poly in obj.data.polygons:
        axis=max(range(3),key=lambda i:abs(poly.normal[i]))
        a,b=[i for i in range(3) if i != axis]
        for li in poly.loop_indices:
            p=obj.data.vertices[obj.data.loops[li].vertex_index].co
            uv.data[li].uv=(p[a]/.16,p[b]/.16)

def soft_box(name, center, size, radius, mat, quilting=False, ribbing=False):
    """Rounded, closed upholstered envelope with shallow sewn depressions."""
    half=Vector(size)/2; verts=[]; faces=[]
    for axis in range(3):
        a,b=[i for i in range(3) if i != axis]
        spacing=.018 if quilting and axis==2 else .035
        na=max(6,math.ceil(size[a]/spacing)); nb=max(6,math.ceil(size[b]/spacing))
        for sign in (-1,1):
            start=len(verts)
            for i in range(na+1):
                for j in range(nb+1):
                    q=Vector((0,0,0)); q[axis]=sign*half[axis]
                    q[a]=-half[a]+size[a]*i/na; q[b]=-half[b]+size[b]*j/nb
                    core=Vector([max(-half[k]+radius,min(half[k]-radius,q[k])) for k in range(3)])
                    n=(q-core).normalized(); p=core+n*radius
                    if ribbing and axis in (0,1):
                        along=p[1 if axis==0 else 0]
                        d=((along+.04)%.08)-.04
                        fade=max(0,1-(p.z/half.z)**4)
                        p[axis]-=sign*.0024*math.exp(-(d/.007)**2)*fade
                    if quilting and axis==2 and sign==1:
                        # Staggered round tufting with a gently inflated pillow top.
                        row=round((p.y+.7)/.21)
                        dx=((p.x+.9+(row%2)*.11+.11)%.22)-.11
                        dy=((p.y+.7+.105)%.21)-.105
                        edge=min(half.x-abs(p.x),half.y-abs(p.y))
                        p.z-=.022*math.exp(-(dx*dx+dy*dy)/(.047**2))*min(1,max(0,edge/.06))
                    verts.append(tuple(p))
            for i in range(na):
                for j in range(nb):
                    k=start+i*(nb+1)+j
                    faces.append((k,k+nb+1,k+nb+2,k+1))
    mesh=bpy.data.meshes.new(name+'_Mesh'); mesh.from_pydata(verts,[],faces); mesh.update()
    bm=bmesh.new(); bm.from_mesh(mesh)
    bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00001)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces)); bm.to_mesh(mesh); bm.free()
    obj=bpy.data.objects.new(name,mesh); col.objects.link(obj); obj.location=center
    mesh.materials.append(mat)
    for poly in mesh.polygons: poly.use_smooth=True
    uv_map(obj)
    return obj

def line_mesh(name, paths, radius, mat):
    curve=bpy.data.curves.new(name,'CURVE'); curve.dimensions='3D'
    curve.resolution_u=1; curve.bevel_depth=radius; curve.bevel_resolution=1
    for points, closed in paths:
        spline=curve.splines.new('POLY'); spline.points.add(len(points)-1)
        for p,co in zip(spline.points,points): p.co=(*co,1)
        spline.use_cyclic_u=closed
    obj=bpy.data.objects.new(name,curve); col.objects.link(obj); curve.materials.append(mat)
    bpy.ops.object.select_all(action='DESELECT'); obj.select_set(True); bpy.context.view_layer.objects.active=obj
    bpy.ops.object.convert(target='MESH')
    return bpy.context.object

def rounded_outline(cx,cy,l,w,z,r=.028):
    points=[]
    for sx,sy,start in ((1,1,0),(-1,1,90),(-1,-1,180),(1,-1,270)):
        for k in range(9):
            a=math.radians(start+k*90/8)
            points.append((cx+sx*(l/2-r)+r*math.cos(a),cy+sy*(w/2-r)+r*math.sin(a),z))
    return points

for side, y in (('S',CY-.4),('N',CY+.4)):
    soft_box('Q22_Restandard_Base'+side,(CX,y,FLOOR+.190),(2.,.8,.150),.023,grey,ribbing=True)
    # Underside/top piping is inset so the nominal envelope stays exact.
    for suffix,z in (('Top',FLOOR+.261),('Bottom',FLOOR+.119)):
        line_mesh('Q22_Detail_Base'+side+suffix,[(rounded_outline(CX,y,1.992,.792,z),True)],.0015,grey_seam)
    for xoff in (-.85,.85):
        for yoff in (-.275,.275):
            leg=A.create_cylinder(f'Q22_Restandard_Leg{side}_{xoff}_{yoff}',CX+xoff,y+yoff,FLOOR,.0325,.115,seg=32,mat=wood,col=col)
            # Apply rounded foot edges, retaining a true 65mm diameter and 115mm height.
            bpy.context.view_layer.objects.active=leg
            bpy.ops.object.modifier_apply(modifier=leg.modifiers[0].name)
            uv_map(leg)

soft_box('Q22_Restandard_Mattress',(CX,CY,FLOOR+.410),(2.,1.6,.290),.036,white,quilting=True,ribbing=True)
quilting_paths=[]
for row in range(7):
    y=-.7+row*.21
    for k in range(10):
        x=k*.22-.9-(row%2)*.11
        if abs(x)>.83: continue
        ring=[]
        for n in range(24):
            angle=2*math.pi*n/24; radius=.024
            px=x+radius*math.cos(angle); py=y+radius*math.sin(angle)
            # The tiny sewn circle follows the depressed upholstered surface.
            z=FLOOR+.555-.022*math.exp(-(radius**2)/(.047**2))+.0008
            ring.append((CX+px,CY+py,z))
        quilting_paths.append((ring,True))
line_mesh('Q22_Detail_QuiltingStitches',quilting_paths,.00055,cream_seam)
for suffix,z in (('Top',FLOOR+.548),('Bottom',FLOOR+.270)):
    line_mesh('Q22_Detail_MattressPiping'+suffix,[(rounded_outline(CX,CY,1.990,1.590,z,.035),True)],.002,cream_seam)

# Actual sewn fabric handles on the two long edges; size/position approximate.
for sign in (-1,1):
    for x in (CX-.48,CX+.48):
        soft_box(f'Q22_Detail_Handle_{sign}_{x}',(x,CY+sign*.797,FLOOR+.403),(.042,.004,.140),.0018,white)
        button=A.create_cylinder(f'Q22_Detail_HandleButton_{sign}_{x}',x,CY+sign*.800,FLOOR+.403,.0045,.0015,seg=12,mat=wood,col=col)
        button.rotation_euler.x=math.pi/2

# Restrained care label and small dark brand tab on the mattress foot.
soft_box('Q22_Detail_CareLabel',(CX+.999,CY-.48,FLOOR+.447),(.002,.065,.095),.0008,tag_mat)
soft_box('Q22_Detail_BrandTab',(CX+.999,CY-.425,FLOOR+.453),(.002,.027,.069),.0008,grey_seam)

sc['Q22_restandard_bed']=1
sc['Q22_master_bed_width_mm']=1600
sc['Q22_master_bed_leg_mm']=115
sc['Q22_master_bed_headboard']=False
sc['Q22_master_bed_wall_aligned']=True
sc['Q22_master_bed_wall_x']=wall_x
sc['Q22_master_bedside_cleared']=True
sc['Q22_master_bed_support']='wood floor z=0'
sc['Q22_master_bed_mattress']='Restandard independent 290mm; default set option'
bpy.context.view_layer.update()
runpy.run_path(str(ROOT/'scripts/verify_restandard_bed.py'),run_name='__main__')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'apt_84a_photoreal_tour.blend'))
print('Q22 SAVED: Restandard grey K / no head / wood115, backup preserved',flush=True)
