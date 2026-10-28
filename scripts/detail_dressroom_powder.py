"""Q23: clear the old continuous closet and fit a proposed makeup vanity."""
from pathlib import Path
import hashlib
import json
import shutil
import sys
import bpy
import bmesh
from mathutils import Vector

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT/'scripts'))
import generate_high_detail_assets as A

backup = ROOT/'models/backups/apt_84a_photoreal_tour_before_dressroom_powder.blend'
if not backup.exists():
    shutil.copy2(bpy.data.filepath, backup)
revision_backup = ROOT/'models/backups/apt_84a_photoreal_tour_before_powder_reference_fix.blend'
if bpy.context.scene.get('Q23_dressroom_powder') == 1 and not bpy.context.scene.get('Q23_reference_revision') and not revision_backup.exists():
    shutil.copy2(bpy.data.filepath, revision_backup)
fit_backup = ROOT/'models/backups/apt_84a_photoreal_tour_before_powder_wall_fit.blend'
if bpy.context.scene.get('Q23_reference_revision') and not bpy.context.scene.get('Q23_wall_fitted') and not fit_backup.exists():
    shutil.copy2(bpy.data.filepath, fit_backup)

def structure_hash():
    data = [(o.name, [list(row) for row in o.matrix_world],
             [list(v.co) for v in o.data.vertices],
             [list(p.vertices) for p in o.data.polygons])
            for o in sorted(bpy.data.objects, key=lambda o: o.name)
            if o.type == 'MESH' and o.name.startswith('ExactWall_')]
    return hashlib.sha256(json.dumps(data).encode()).hexdigest()

before = structure_hash()
for o in list(bpy.data.objects):
    if o.name.startswith(('Dress_Closet_', 'Wardrobe_Dress_', 'Q23_Powder_')):
        bpy.data.objects.remove(o, do_unlink=True)

col = A.get_col('Apt_DressroomPowder')
def material(name, color, roughness=.45, metallic=0., emission=0.):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    m.diffuse_color = (*color, 1.)
    bs = m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*color, 1.)
    bs.inputs['Roughness'].default_value = roughness
    bs.inputs['Metallic'].default_value = metallic
    if emission:
        bs.inputs['Emission Color'].default_value = (*color, 1.)
        bs.inputs['Emission Strength'].default_value = emission
    return m

cab = material('Mat_Q23_Greige', (.57,.53,.46), .40)
upper = material('Mat_Q23_SatinIvory', (.79,.78,.73), .23)
top = material('Mat_Q23_WarmWhite', (.81,.79,.73), .31)
mirror = material('Mat_Q23_Mirror', (.88,.91,.94), .035, 1.)
edge = material('Mat_Q23_Silver', (.62,.64,.65), .22, .8)
dark = material('Mat_Q23_Reveal', (.12,.11,.095), .65)

def box(name, x1,x2,y1,y2,z1,z2,mat,bevel=.001):
    o = A.create_beveled_box('Q23_Powder_'+name, (x1+x2)/2,(y1+y2)/2,z1,
                            x2-x1,y2-y1,z2-z1,mat=mat,col=col,bevel=bevel,seg=3)
    bm = bmesh.new(); bm.from_mesh(o.data)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(o.data); bm.free()
    for p in o.data.polygons:
        p.use_smooth = False
    return o

# User references: apartment-fitted powder niche, two shallow handleless drawers,
# continuous recessed lower storage, tall ivory side cupboards and a large mirror.
# Dimensions follow this room; the reference's brown colour is explicitly not copied.
box('Plinth',.510,.810,5.940,7.040,0.,.065,cab)
box('LowerCore',.495,.833,5.940,7.040,.065,.587,cab)
for side,y1,y2 in [('S',5.942,6.488), ('N',6.492,7.038)]:
    box('LowerDoor'+side,.835,.853,y1,y2,.068,.585,cab)
box('DrawerCore',.495,.922,5.940,7.040,.592,.730,cab)
for side,y1,y2 in [('S',5.942,6.488), ('N',6.492,7.038)]:
    box('Drawer'+side,.924,.943,y1,y2,.596,.726,cab)
box('Top',.495,.945,5.940,7.040,.730,.750,top,.002)
box('Upstand',.495,.515,5.940,7.040,.750,.880,upper)
# Shallow upper storage closes the niche to the 2300mm ceiling, without a gold
# picture-frame mirror or the decorative light bar of the rejected first draft.
for side,y1,y2 in [('S',5.940,6.110), ('N',6.870,7.040)]:
    box('UpperCab'+side,.495,.650,y1,y2,.880,2.280,upper)
    box('UpperDoor'+side,.652,.670,y1+.002,y2-.002,.884,2.278,upper)
box('UpperPelmet',.495,.670,5.940,7.040,2.280,2.299,upper)
box('MirrorBacking',.495,.651,6.112,6.868,.880,2.278,upper)
box('MirrorTrim',.651,.655,6.114,6.866,.884,2.276,edge,.0004)
box('Mirror',.655,.658,6.118,6.862,.888,2.272,mirror,.0004)
# Matching end liners visually integrate the counter into its wall recess.
for side,y1,y2 in [('S',5.940,5.952), ('N',7.028,7.040)]:
    box('NicheLiner'+side,.495,.945,y1,y2,.750,.880,upper)

bpy.context.view_layer.update()
# Fit the complete assembly between the actual south/north wall faces. These
# are slightly tapered Q12 meshes, so one fixed width leaves a visible gap or
# penetrates a wall. Map each mesh vertex to its own measured clear span.
wall=bpy.data.objects['ExactWall_13']
wall_inv=wall.matrix_world.inverted()
def side_y(x, direction):
    hit,p,*_=wall.ray_cast(wall_inv@Vector((x,6.45,1.2)),wall_inv.to_3x3()@Vector((0,direction,0)))
    assert hit, ('Missing powder side wall',x,direction)
    return (wall.matrix_world@p).y

for obj in col.objects:
    if obj.type!='MESH' or not obj.name.startswith('Q23_Powder_'):
        continue
    inv_obj=obj.matrix_world.inverted()
    for vertex in obj.data.vertices:
        p=obj.matrix_world@vertex.co
        ratio=(p.y-5.940)/1.100
        south=side_y(p.x,-1)+.0005
        north=side_y(p.x,1)-.0005
        p.y=south+ratio*(north-south)
        vertex.co=inv_obj@p
    obj.data.update()
bpy.context.view_layer.update()
assert structure_hash() == before, 'Structural wall geometry changed'
sc = bpy.context.scene
sc['Q23_dressroom_powder'] = 1
sc['Q23_structure_sha256'] = before
sc['Q23_reference_revision'] = 1
sc['Q23_wall_fitted'] = 1
sc['Q23_powder_spec'] = 'User photo type; fitted to actual tapered wall faces, approx1240mm wide x450 top750mm; side seam0.5mm'
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'apt_84a_photoreal_tour.blend'))
print('Q23b saved: user-reference fitted apartment powder unit; structural wall hash unchanged')
