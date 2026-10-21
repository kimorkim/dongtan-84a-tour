"""Q15: modelhouse-photo living finishes, preserving the calibrated structure.

shortcut: sash divisions and curtain folds are photo estimates; use shop drawings
before ordering joinery. The restored landscape is an illustrative backdrop.
"""
from pathlib import Path
import sys, shutil, math, runpy
import bpy, bmesh
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'scripts'))
import generate_high_detail_assets as A
import improve_quality_v2 as Q
assert bpy.context.scene.get('Q14_sofa')
backup=ROOT/'models/backups/apt_84a_photoreal_tour_before_living_finish.blend'
if not backup.exists(): shutil.copy2(bpy.data.filepath,backup)
col=A.get_col('Apt_LivingFinish')
def mat(name,rgb,rough=.6,metal=0):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes=True; m.diffuse_color=(*rgb,1)
    p=m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*rgb,1)
    p.inputs['Roughness'].default_value=rough; p.inputs['Metallic'].default_value=metal
    return m
def box(name,x0,x1,y0,y1,z0,z1,m):
    o=A.create_beveled_box(name,(x0+x1)/2,(y0+y1)/2,z0,x1-x0,y1-y0,z1-z0,bevel=0,mat=m,col=col)
    bm=bmesh.new(); bm.from_mesh(o.data)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces)); bm.to_mesh(o.data); bm.free()
    return o
for o in list(bpy.data.objects):
    if o.name.startswith(('Q2_Coffee','Q2_Pouf','Q2_Living_Rug','Q2_Rug_Shape','Curtain_Living','Q2_Sheer_Living','Q2_Rail_Living_','Win_Living_','Q15_')) or o.name=='Living_ArtWall_Tile':
        bpy.data.objects.remove(o,do_unlink=True)
tile=bpy.data.materials['Mat_ArtWall_Tile']
box('Living_ArtWall_Tile',4.305,4.330,.92,4.75,0,2.3,tile)
box('Q15_ArtWall_DoorHeader',4.305,4.330,4.75,5.75,2.2,2.3,tile)
box('Q15_ArtWall_EndReturn',4.085,4.330,4.735,4.75,0,2.2,tile)
white=mat('Mat_Q15_PVC',(.76,.76,.73),.36)
seal=mat('Mat_Q15_Gasket',(.018,.020,.021),.72)
steel=mat('Mat_Q15_RailSteel',(.035,.040,.043),.38,.65)
glass=bpy.data.materials['Mat_Q10_Glass']
box('Win_Living_Sill',4.755,8.355,.70,.90,.27,.32,white)
box('Win_Living_Head',4.755,8.355,.72,.88,2.22,2.27,white)
for name,x in [('JambL',4.755),('JambR',8.305)]:
    box('Win_Living_'+name,x,x+.05,.72,.88,.32,2.22,white)
for i,x in enumerate((5.505,7.605)):
    box('Win_Living_Mullion'+str(i+1),x-.025,x+.025,.735,.865,.32,2.22,white)
for i,(a,b) in enumerate(((4.805,5.480),(5.530,7.580),(7.630,8.305))):
    box('Win_Living_Glass'+str(i),a+.006,b-.006,.7925,.8075,.34,2.20,glass)
    for x in (a,b-.006): box('Q15_SealV'+str(i)+str(x),x,x+.006,.78,.82,.33,2.21,seal)
    for z in (.33,2.204): box('Q15_SealH'+str(i)+str(z),a,b,.78,.82,z,z+.006,seal)
for i,y in enumerate((.745,.785,.825,.865)):
    box('Q15_SashTrack'+str(i),4.805,8.305,y,y+.004,.319,.323,seal)
for name,z0,z1 in [('Top',.815,.83),('Bottom',.31,.325)]:
    box('Q2_Rail_Living_'+name,4.755,8.355,.632,.658,z0,z1,steel)
for i in range(33):
    x=4.77+i*(3.57/32)
    box('Q2_Rail_Living_B'+str(i),x-.006,x+.006,.639,.651,.325,.815,steel)
cloth=mat('Mat_Q15_Curtain',(.29,.27,.245),.95)
cloth.node_tree.nodes.get('Principled BSDF').inputs['Sheen Weight'].default_value=.4
for name,a,b in [('Left',4.345,4.795),('Right',8.315,8.765)]:
    verts=[]; faces=[]; n=120
    for i in range(n+1):
        x=a+(b-a)*i/n; y=1.035+.035*math.cos(i/n*12*math.pi)
        verts.extend([(x,y,.015),(x,y,2.28)])
        if i: faces.append((2*i-2,2*i,2*i+1,2*i-1))
    mesh=bpy.data.meshes.new('Q15_Curtain_'+name); mesh.from_pydata(verts,[],faces); mesh.materials.append(cloth)
    o=bpy.data.objects.new('Q15_Curtain_'+name,mesh); col.objects.link(o)
    for p in mesh.polygons: p.use_smooth=True
    mod=o.modifiers.new('Cloth thickness','SOLIDIFY'); mod.thickness=.0012
box('Q15_Curtain_Track',4.32,8.79,1.01,1.065,2.28,2.30,white)
# Regenerate the lost generated-image pixels and pack them so reopening keeps them.
old=bpy.data.images.get('Q2_Landscape')
if old: old.name='Q15_EmptyLandscape'
im=Q.landscape_image()
for m in bpy.data.materials:
    if m.use_nodes:
        for node in m.node_tree.nodes:
            if node.type=='TEX_IMAGE' and node.image==old: node.image=im
land=bpy.data.materials['Mat_Q2_Landscape']; nt=land.node_tree; nt.nodes.clear()
tex=nt.nodes.new('ShaderNodeTexImage'); tex.image=im
bs=nt.nodes.new('ShaderNodeBsdfPrincipled'); bs.inputs['Roughness'].default_value=1
bs.inputs['Emission Strength'].default_value=.55
out=nt.nodes.new('ShaderNodeOutputMaterial')
nt.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
nt.links.new(tex.outputs['Color'],bs.inputs['Emission Color'])
nt.links.new(bs.outputs['BSDF'],out.inputs['Surface'])
bpy.context.view_layer.update()
for o in bpy.data.objects:
    if o.name.startswith('Q2_Landscape_') and o.type=='MESH':
        points=[o.matrix_world@v.co for v in o.data.vertices]
        z0=min(p.z for p in points); z1=max(p.z for p in points)
        x0=min(p.x for p in points); x1=max(p.x for p in points)
        uv=o.data.uv_layers.active or o.data.uv_layers.new(name='UVMap')
        for loop in o.data.loops:
            p=points[loop.vertex_index]
            uv.data[loop.index].uv=((p.x-x0)/(x1-x0),(p.z-z0)/(z1-z0))
im.filepath_raw=str(ROOT/'assets/textures_export/q2_landscape.jpg'); im.file_format='JPEG'
im.save(); im.pack()
if old: bpy.data.images.remove(old)
bpy.context.scene['Q15_living_finish']=1
bpy.context.view_layer.update()
runpy.run_path(str(ROOT/'scripts/verify_living_finish.py'),run_name='__main__')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'apt_84a_photoreal_tour.blend'))
print('Q15 LIVING SAVED',flush=True)
