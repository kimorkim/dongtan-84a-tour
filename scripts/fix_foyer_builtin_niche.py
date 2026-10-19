# Fix Foyer Built-in Shoe Cabinet Niche and Realign to Exact CAD Architecture
import bpy
import math
from mathutils import Vector

# 1. Update Floor_Foyer to span true bounds [11.775, 13.350] x [5.750, 7.969]
ff = bpy.data.objects.get('Floor_Foyer')
if ff:
    ff.location = Vector((12.5625, 6.8595, 0.002))
    ff.dimensions = Vector((1.575, 2.219, 0.01))

# 2. Update Foyer_Threshold to Y=5.75, X=[11.775, 12.881]
ft = bpy.data.objects.get('Foyer_Threshold')
if ft:
    ft.location = Vector((12.328, 5.75, 0.015))
    ft.dimensions = Vector((1.106, 0.10, 0.025))

# 3. Move Foyer_Shoe_Cabinet_Body into the built-in niche [12.885, 13.345] x [5.750, 7.650]
sc_body = bpy.data.objects.get('Foyer_Shoe_Cabinet_Body')
if sc_body:
    sc_body.location = Vector((13.115, 6.70, 1.25))
    sc_body.dimensions = Vector((0.46, 1.90, 2.10))

# 4. Remove old doors and recreate 3 flush cashmere doors facing west into the foyer
for old_d in ['Foyer_Shoe_Door1', 'Foyer_Shoe_Door2', 'Foyer_Shoe_Door3']:
    o = bpy.data.objects.get(old_d)
    if o:
        bpy.data.objects.remove(o, do_unlink=True)

mat_cashmere = bpy.data.materials.get('Mat_Cashmere_Laminate') or sc_body.active_material

door_h = 2.08
door_thick = 0.02
door_w = 1.90 / 3.0 - 0.004  # ~0.63m each
y_starts = [5.75 + i * (1.90 / 3.0) + 0.002 for i in range(3)]

for i, y_start in enumerate(y_starts):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(12.875, y_start + door_w/2, 1.25))
    d = bpy.context.active_object
    d.name = f'Foyer_Shoe_Door{i+1}'
    d.scale = Vector((door_thick, door_w, door_h))
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if mat_cashmere:
        d.data.materials.append(mat_cashmere)
    col = bpy.data.collections.get('Apt_Openings') or bpy.context.scene.collection
    if d.name in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.unlink(d)
    if d.name not in col.objects:
        col.objects.link(d)

# 5. Update LED strip along bottom of cabinet in the niche
led = bpy.data.objects.get('Foyer_Shoe_LED_Strip')
if led:
    led.location = Vector((13.115, 6.70, 0.195))
    led.dimensions = Vector((0.42, 1.84, 0.01))

# 6. Realign shoes under the floating cabinet
shoes = [
    ('Foyer_Shoe_Pair1_L', 13.05, 6.10),
    ('Foyer_Shoe_Pair1_R', 13.18, 6.10),
    ('Foyer_Shoe_Pair2_L', 13.05, 6.60),
    ('Foyer_Shoe_Pair2_R', 13.18, 6.60),
]
for sname, sx, sy in shoes:
    so = bpy.data.objects.get(sname)
    if so:
        so.location.x = sx
        so.location.y = sy
        so.location.z = 0.04

# 7. Create solid wall header closing the north end of the niche [12.881, 13.350] x [7.650, 7.969]
old_hw = bpy.data.objects.get('Foyer_Shoe_Niche_HeadWall')
if old_hw:
    bpy.data.objects.remove(old_hw, do_unlink=True)

bpy.ops.mesh.primitive_cube_add(size=1.0, location=(13.115, 7.8095, 1.15))
hw = bpy.context.active_object
hw.name = 'Foyer_Shoe_Niche_HeadWall'
hw.scale = Vector((0.469, 0.319, 2.30))
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
mat_wall = bpy.data.materials.get('Mat_Wall_Paint') or bpy.data.materials.get('Wall_White')
if mat_wall:
    hw.data.materials.append(mat_wall)
col_str = bpy.data.collections.get('Apt_OuterWalls') or bpy.data.collections.get('Apt_Corrected_Structure') or bpy.context.scene.collection
if hw.name in bpy.context.scene.collection.objects:
    bpy.context.scene.collection.objects.unlink(hw)
if hw.name not in col_str.objects:
    col_str.objects.link(hw)

# 8. Realign Mirror to center along West wall
mf = bpy.data.objects.get('Foyer_Mirror_Frame')
mg = bpy.data.objects.get('Foyer_Mirror_Glass')
if mf:
    mf.location = Vector((11.785, 6.85, 1.20))
    mf.dimensions = Vector((0.015, 1.20, 1.80))
if mg:
    mg.location = Vector((11.792, 6.85, 1.20))
    mg.dimensions = Vector((0.005, 1.16, 1.76))

# 9. Realign Ceiling Spotlight
lens = bpy.data.objects.get('Foyer_Spot_Lens')
trim = bpy.data.objects.get('Foyer_Spot_Trim')
light = bpy.data.objects.get('Light_Foyer_Spot')
if lens: lens.location = Vector((12.328, 6.85, 2.292))
if trim: trim.location = Vector((12.328, 6.85, 2.295))
if light: light.location = Vector((12.328, 6.85, 2.25))

print('SUCCESS: Foyer and built-in shoe cabinet niche completely realigned.')
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
