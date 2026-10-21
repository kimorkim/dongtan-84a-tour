"""Q12: apply A02-102 constraints to the Q11b baseline, preserving approved furniture.

Reproducible migration: always starts from before_dimensions.blend, never from a
previous Q12 result. Do not use this baseline migration after later model edits.
"""
import json
import math
import os
import runpy
import shutil
import sys
from pathlib import Path
import bmesh
import bpy
from mathutils import Matrix,Vector

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'scripts'))
import plan_dimensions as P
import generate_high_detail_assets as A

backup=ROOT/'models/backups/apt_84a_photoreal_tour_before_dimensions.blend'
if not backup.exists(): shutil.copy2(bpy.data.filepath,backup)
bpy.ops.wm.open_mainfile(filepath=str(backup))
sc=bpy.context.scene
col=A.get_col('Apt_DimensionCorrection')

def bounds(o):
    p=[o.matrix_world @ Vector(c) for c in o.bound_box]
    return [min(v[i] for v in p) for i in range(3)],[max(v[i] for v in p) for i in range(3)]

original={o.name:(o.matrix_world.copy(),bounds(o)) for o in bpy.data.objects}
# Keep world transforms before detaching old leaf/handle parents.
for o in bpy.data.objects:
    if o.parent:
        matrix=o.matrix_world.copy(); o.parent=None; o.matrix_world=matrix

def clean(o):
    bm=bmesh.new(); bm.from_mesh(o.data)
    bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
    bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-7)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    bm.to_mesh(o.data); bm.free(); o.data.update()

def box(name,x1,x2,y1,y2,z1,z2,mat,bevel=.001):
    o=A.create_beveled_box(name,(x1+x2)/2,(y1+y2)/2,z1,x2-x1,y2-y1,z2-z1,
                          bevel=bevel,seg=3,mat=mat,col=col)
    clean(o)
    for f in o.data.polygons: f.use_smooth=False
    return o

wall=bpy.data.materials['Mat_Wall_Interior']
frame=bpy.data.materials['Mat_WindowFrame_White']
glass=bpy.data.materials['Mat_Q10_Glass']
cashmere=bpy.data.materials['Mat_Cabinet_Cashmere']
metal=bpy.data.materials['Mat_Chrome_Metal']

# Incorrect whole-apartment rectangle additions are outside the unit footprint.
remove_prefixes=('NewWall_North','NewWall_EastN','EntryFrame_','EntrySlab_','Front_Door_',
                 'Win_Bed2_','Win_Bed3_','Win_Living_','Win_Kitchen_','Win_Dress_',
                 'SillPatch_','Liner_Bed2_','Liner_Bed3_','Liner_Living_',
                 'Liner_Kitchen_','Liner_Dress_',
                 'Q10_Window','Q11_Window','Q4_RefugeWindow','Q4_BalconyWindow',
                 'ProDoorTrim_Bed2','ProDoorTrim_Bed3','ProDoorHeaders',
                 'Rail_South_','BalconySlab_South')
for o in list(bpy.data.objects):
    if o.name.startswith(remove_prefixes): bpy.data.objects.remove(o,do_unlink=True)

# Rigid groups preserve every product dimension and internal part alignment.
fixed={}
def move_group(names,delta):
    for o in list(bpy.data.objects):
        if names(o.name): fixed[o.name]=delta

big=(11.775-.045-.4-11.42,.920+.06+.9-1.81)
small=(11.775-.045-.35-11.47,4.330-.067-.7-3.47)
move_group(lambda n:n.startswith(('Q11_Desk1800_','Q11_AeronBlack_')) or
           n.startswith('Q11_Equipment_') and not any(s in n for s in ('Gaming','Desktop','Keyboard1400','Mouse1400')),big)
move_group(lambda n:n.startswith(('Q11_Desk1400_','Q11_AeronGrey_')) or
           n.startswith('Q11_Equipment_') and any(s in n for s in ('Gaming','Desktop','Keyboard1400','Mouse1400')),small)
move_group(lambda n:n.startswith(('Q10_Bed_','Q10_BedGuard','Q10_Headboard','Q10_Mattress',
           'Q10_Duvet','Q10_FoldedThrow','Q10_QuiltSeam','Q10_Pillow','Q10_Cloud','Q10_Bunny_')),(-.058,.070))
move_group(lambda n:n.startswith(('Q10_Bookcase','Q10_BookRail','Q10_ToyBasket','Q10_BasketLabel',
           'Q10_PictureBook','Q10_BookMotif','Q10_Activity','Q10_TableLeg','Q10_Chair','Q10_Crayon','Q10_Drawing')),(-.076,.070))
move_group(lambda n:n.startswith('Q10_Wardrobe'),(-.076,.111))
move_group(lambda n:n.startswith(('Q10_Curtain','Q10_CurtainTrack')),(-.085,.070))
move_group(lambda n:n.startswith(('Q3_Fridge_','Q3_Kimchi_','Q3_Cooker_')),(-.095,.110))
move_group(lambda n:n.startswith('AC_Condenser_'),(-.130,.185))
move_group(lambda n:n.startswith(('ProDoorLeaf_Bed2','ProDoorHandle_Bed2','ProDoorLeaf_Bed3','ProDoorHandle_Bed3')),(-.071,.110))

for prefixes,origin in [
    (('Sofa_Living_','Q2_Sofa_'),(7.2,2.6)),
    (('Dining_','Chair_N','Chair_S','Pendant_Dining','Q2_Dining_'),(6.85,6.7)),
    (('Bed_Master_','Q2_Master_Cushion','Nightstand_Master_'),(2.7,3.5)),
    (('ProK_Oven_','ProK_Dishwasher_'),(7.1,9.0))]:
    nx,ny=P.point(*origin); dx=nx-origin[0]; dy=ny-origin[1]
    if origin==(6.85,6.7): dx-=.02
    move_group(lambda n,p=prefixes:n.startswith(p),(dx,dy))

for o in list(bpy.data.objects):
    name=o.name
    matrix,(lo,hi)=original[name]
    if name in fixed:
        dx,dy=fixed[name]; o.matrix_world=Matrix.Translation((dx,dy,0)) @ matrix
        continue
    if o.type!='MESH':
        p=matrix.translation; nx,ny=P.point(p.x,p.y)
        o.matrix_world=Matrix.Translation((nx-p.x,ny-p.y,0)) @ matrix
        continue
    if name in ('Ground_Presentation','Exact_Floor','Ceiling_Slab'): continue
    o.data=o.data.copy()
    structure=name.startswith(('ExactWall_','ProBaseboards'))
    pantry_fit=name.startswith(('Q7_PantryShelf_','Q7_PantryPost_','Q7_PantryProp_',
                               'Q7_PantryRail_','Q7_PantryBracket_','Q7_PantryHinge',
                               'Q7_PantryPull_','ProDoorLeaf_EntryPantry'))
    balcony_fit=name.startswith(('Q4_BalconyDoor_','Q4_BalconySidelight','ProDoorLeaf_MasterBalcony'))
    refuge_fit=name.startswith('Q4_RefugeDoor_')
    if balcony_fit or refuge_fit:
        for v in o.data.vertices:
            p=matrix @ v.co; nx,ny=P.point(p.x,p.y)
            if balcony_fit: nx=2.285+(p.x-2.240)*1.500/1.670
            if refuge_fit: ny=.650+(p.y-.544)*.750/.768
            v.co=(nx,ny,p.z)
    elif pantry_fit:
        for v in o.data.vertices:
            p=matrix @ v.co
            v.co=(10.385+(p.x-10.556)*1.190/1.032,5.860+(p.y-5.775)*1.800/1.875,p.z)
    elif structure:
        for v in o.data.vertices:
            p=matrix @ v.co
            nx,ny=P.solid_point(p.x,p.y)
            if name=='ExactWall_4': nx=round(P.interpolate(p.x,P.X_MAP)/.005)*.005
            v.co=(nx,ny,p.z)
    else:
        cx,cy=(lo[0]+hi[0])/2,(lo[1]+hi[1])/2
        ncx,ncy=P.point(cx,cy)
        left=P.point(lo[0],cy)[0]; right=P.point(hi[0],cy)[0]
        bottom=P.point(cx,lo[1])[1]; top=P.point(cx,hi[1])[1]
        sx=(right-left)/(hi[0]-lo[0]) if hi[0]-lo[0]>.15 else 1
        sy=(top-bottom)/(hi[1]-lo[1]) if hi[1]-lo[1]>.15 else 1
        # Wall fit may change a cabinet span, never collapse thin trim/tile faces.
        sx=max(.65,min(1.5,sx)); sy=max(.65,min(1.5,sy))
        for v in o.data.vertices:
            p=matrix @ v.co; v.co=(ncx+(p.x-cx)*sx,ncy+(p.y-cy)*sy,p.z)
    o.matrix_world=Matrix.Identity(4)
    clean(o)

bpy.context.view_layer.update()
# Tile slabs are fitted to the exact room faces, keeping their existing materials.
for name,room in [('Floor_Foyer','foyer'),('Floor_EntrancePantry','pantry'),('Q6_UtilityFloor','utility'),
                  ('Q6_UtilityFloorBase','utility'),('Floor_MasterBath','master_bath')]:
    o=bpy.data.objects[name]; lo,hi=bounds(o); r=P.ROOMS[room]
    for v in o.data.vertices:
        p=o.matrix_world @ v.co
        p.x=r[0]+(p.x-lo[0])/(hi[0]-lo[0])*(r[1]-r[0])
        p.y=r[2]+(p.y-lo[1])/(hi[1]-lo[1])*(r[3]-r[2])
        v.co=o.matrix_world.inverted() @ p
    o.data.update()
bpy.context.view_layer.update()
# Curtains stay on the room side of the rebuilt south windows.
for o in bpy.data.objects:
    if o.name.startswith(('Curtain_Living_','Q2_Sheer_Living')) and o.type=='MESH':
        lo,hi=bounds(o)
        o.location.y+=1.00-(lo[1]+hi[1])/2
    if o.name.startswith('Q8_WetTile_W_') and o.type=='MESH':
        lo,hi=bounds(o)
        o.location.x+=13.405-hi[0]

middle=bpy.data.objects['Q7_MiddleDoor_Glass']
_,middle_hi=bounds(middle)
middle_dx=min(0,11.625-middle_hi[0])
for o in bpy.data.objects:
    if o.name.startswith(('Q7_MiddleDoor_Leaf','Q7_MiddleDoor_Glass','Q7_MiddleDoor_Guide')):
        o.location.x+=middle_dx

# Exact outer floor and ceiling, rather than an oversized rectangular walking area.
outline=[(.215,.350),(4.305,.350),(4.305,.600),(15.175,.600),(15.175,7.895),
         (10.315,7.895),(10.315,9.725),(8.015,9.725),(8.015,10.385),(.215,10.385)]
def slab(name,z1,z2,materials):
    o=bpy.data.objects[name]
    n=len(outline)
    vs=[(x,y,z) for z in (z1,z2) for x,y in outline]
    fs=[tuple(reversed(range(n))),tuple(range(n,2*n))]
    fs += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    mesh=bpy.data.meshes.new('Q12_'+name); mesh.from_pydata(vs,[],fs); mesh.update()
    o.data=mesh; o.matrix_world=Matrix.Identity(4)
    for mat in materials: mesh.materials.append(mat)
    clean(o)
    if name=='Exact_Floor':
        uv=mesh.uv_layers.new(name='FloorUV')
        for f in mesh.polygons:
            f.material_index=1 if f.normal.z>.8 else 0
            for loop in f.loop_indices:
                p=mesh.vertices[mesh.loops[loop].vertex_index].co
                uv.data[loop].uv=(p.x/3,p.y/1.04)

floor=bpy.data.objects['Exact_Floor']
base=floor.data.materials[0]; oak=bpy.data.materials['Mat_Q9_LightOak']
slab('Exact_Floor',-.15,0,[base,oak])
slab('Ceiling_Slab',2.30,2.38,[bpy.data.materials['Mat_Ceiling_Plaster']])
# Narrow traced openings to the drawing's nominal plan widths; keep the sliding pose.
box('Q12_BalconyDoor_WestFill',2.115,2.285,1.920,2.150,0,2.15,wall)
box('Q12_RefugeDoor_NorthFill',2.115,2.255,1.400,1.715,0,2.10,wall)

# South piers, main-room lining and all dimensioned window units.
for tag,(x1,x2,yy,z,h) in P.WINDOWS.items():
    prefix={'MasterBalcony':'Q4_BalconyWindow','Refuge':'Q4_RefugeWindow'}.get(tag,'Win_'+tag)
    A.create_window_unit(prefix,(x1+x2)/2,yy,z,x2-x1,.16,h,
                         panes=3 if tag=='Living' else 2,mat_frame=frame,mat_glass=glass,col=col)
    for o in col.objects:
        if o.name.startswith(prefix) and o.type=='MESH': clean(o)
    if tag in ('Bed2','Bed3','Living'):
        r=P.ROOMS[{'Bed2':'study','Bed3':'yuna','Living':'living'}[tag]]
        # 200mm south concrete plus the drawing's 120mm internal insulation lining.
        box('Q12_'+tag+'_SillWall',r[0],r[1],.600,.920,0,z,wall)
        box('Q12_'+tag+'_Header',r[0],r[1],.600,.920,z+h,2.30,wall)
        box('Q12_'+tag+'_PierW',r[0],x1,.600,.920,z,z+h,wall)
        box('Q12_'+tag+'_PierE',x2,r[1],.600,.920,z,z+h,wall)
        box('Q12_'+tag+'_StoneSill',x1,x2,.715,.945,z-.015,z,frame)
    elif tag in ('Kitchen','Dress','KitchenBalcony'):
        box('Q12_'+tag+'_SillWall',x1,x2,10.145,10.385,0,z,wall)
        box('Q12_'+tag+'_Header',x1,x2,10.145,10.385,z+h,2.30,wall)
    else:
        box(prefix+'_SillWall',x1,x2,.350,.550,0,z,wall)
        box(prefix+'_HeaderWall',x1,x2,.350,.550,z+h,2.30,wall)

# Close the northern perimeter only at the actual foyer entrance (FSD 11x22).
box('Q12_Entry_Header',11.645,12.745,7.660,7.895,2.10,2.30,wall)
for side,a,b in [('W',11.645,11.675),('E',12.715,12.745)]:
    box('Q12_Entry_Jamb'+side,a,b,7.650,7.905,0,2.10,cashmere)
box('Q12_Entry_Leaf',11.675,12.715,7.775,7.825,.015,2.085,cashmere,.005)
box('Q12_Entry_Lever',12.53,12.64,7.740,7.775,.96,1.00,metal,.005)

# Nominal 900mm bedroom openings, with the existing 85-degree open leaves retained.
for tag,a,b in [('Bed2',9.075,9.975),('Bed3',11.905,12.805)]:
    box('Q12_'+tag+'_DoorHeader',a,b,4.330,4.550,2.10,2.30,wall)
    for side,u in [('W',a),('E',b)]:
        box('ProDoorTrim_'+tag+'_'+side,u-.024,u+.024,4.315,4.565,0,2.13,cashmere)
    box('ProDoorTrim_'+tag+'_Head',a-.024,b+.024,4.315,4.565,2.09,2.14,cashmere)

# Master bedroom entrance is in the east wall, not its dressing-room opening.
box('Q12_Master_DoorHeader',4.085,4.305,4.750,5.750,2.10,2.30,wall)
for tag,y in [('S',4.750),('N',5.750)]:
    box('Q12_Master_DoorJamb'+tag,4.070,4.320,y-.025,y+.025,0,2.13,cashmere)
box('Q12_Master_DoorLeaf',3.105,4.075,5.675,5.715,.015,2.085,cashmere,.005)
box('Q12_Master_DoorHandle',3.19,3.30,5.72,5.75,.96,.99,metal,.008)

# Repair the remaining old double-transformed handle without changing the bathroom leaf.
for o in list(bpy.data.objects):
    if o.name.startswith('ProDoorHandle_MasterBath_'): bpy.data.objects.remove(o,do_unlink=True)
box('ProDoorHandle_MasterBath_A',2.39,2.50,6.22,6.25,.97,1.0,metal,.008)

bpy.context.view_layer.update()
# Clear outliners of render-only hidden state for the corrected spaces.
def visible(layer):
    if layer.name.startswith('Apt_'): layer.hide_viewport=False
    for child in layer.children: visible(child)
visible(bpy.context.view_layer.layer_collection)
sc['Q12_dimensions_version']=1
sc['Q12_source']='84a 평면도.pdf / A02-102 / 2025.10'
sc['Q12_main_finished_floor_SL_offset_m']=.12
bpy.context.view_layer.update()
runpy.run_path(str(ROOT/'scripts/verify_dimensions.py'),run_name='__main__')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'apt_84a_photoreal_tour.blend'))
(ROOT/'assets/analysis/q12_dimensions.json').write_text(json.dumps(dict(
    x_axes=P.X_AXES,north_x_axes=P.NORTH_X_AXES,y_axes=P.Y_AXES,rooms=P.ROOMS,windows=P.WINDOWS,
    source='A02-102',version=1),indent=2),encoding='utf-8')
print('Q12 CALIBRATED MASTER SAVED',flush=True)
