"""Q13: add adjacent Poeta 800/600 six-tier cases to the current Q12 master.

shortcut: photo-based MDF joinery; replace with measured manufacturer CAD for fabrication.
"""
from pathlib import Path
import runpy
import shutil
import sys
import bpy
import bmesh
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'scripts'))
import generate_high_detail_assets as A

assert bpy.context.scene.get('Q12_dimensions_version')==1,'Requires the calibrated current master'
backup=ROOT/'models/backups/apt_84a_photoreal_tour_before_study_bookcases.blend'
if not backup.exists(): shutil.copy2(bpy.data.filepath,backup)
for o in list(bpy.data.objects):
    if o.name.startswith('Q13_Poeta'): bpy.data.objects.remove(o,do_unlink=True)
col=A.get_col('Apt_StudyBookcases')

def material(name,rgb,rough):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes=True; m.diffuse_color=(*rgb,1)
    bs=m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value=(*rgb,1); bs.inputs['Roughness'].default_value=rough
    return m
black=material('Mat_Q13_PoetaBlack',(.024,.026,.025),.52)
wood=material('Mat_Q13_PoetaWoodEdge',(.48,.32,.17),.48)

def box(name,x1,x2,y1,y2,z1,z2,mat):
    o=A.create_beveled_box(name,(x1+x2)/2,(y1+y2)/2,z1,x2-x1,y2-y1,z2-z1,
                          bevel=.0007,seg=2,mat=mat,col=col)
    bm=bmesh.new(); bm.from_mesh(o.data)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces)); bm.to_mesh(o.data); bm.free()
    for f in o.data.polygons: f.use_smooth=False
    return o

back,front=9.095,9.395
height,thick=2.014,.018
for size,width,y0 in [('800',.8,1.35),('600',.6,2.15)]:
    p='Q13_Poeta'+size+'_'; y1=y0+width
    box(p+'Back',back,back+.008,y0,y1,0,height,black)
    box(p+'Plinth',back+.01,front-.025,y0+.018,y1-.018,0,.055,black)
    for label,a,b in [('S',y0,y0+thick),('N',y1-thick,y1)]:
        box(p+'Side'+label,back,front-.0015,a,b,0,height,black)
        box(p+'Side'+label+'_Edge',front-.0015,front,a,b,0,height,wood)
    levels=[.055,.445,.790,1.055,1.445,1.705,1.996] if size=='800' else [
        .055+i*(height-.055-thick)/6 for i in range(7)]
    for i,z in enumerate(levels):
        box(p+'Shelf'+str(i),back+.008,front-.0015,y0+thick,y1-thick,z,z+thick,black)
        box(p+'Shelf'+str(i)+'_Edge',front-.0015,front,y0+thick,y1-thick,z,z+thick,wood)
    # Alternating partitions match the photographed black Poeta 800; the 600 has six open bays.
    if size=='800':
        for i,fraction in enumerate((.28,.74,.50,.25,.50)):
            y=y0+width*fraction
            z1,z2=levels[i]+thick,levels[i+1]
            box(p+'Divider'+str(i),back+.008,front-.0015,y-thick/2,y+thick/2,z1,z2,black)
            box(p+'Divider'+str(i)+'_Edge',front-.0015,front,y-thick/2,y+thick/2,z1,z2,wood)
bpy.context.scene['Q13_study_bookcases']='Casamia Poeta 6-tier 800+600, black with wood edges; west shared living wall'
bpy.context.view_layer.update()
runpy.run_path(str(ROOT/'scripts/verify_study_bookcases.py'),run_name='__main__')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'apt_84a_photoreal_tour.blend'))
print('Q13 STUDY BOOKCASES SAVED',flush=True)
