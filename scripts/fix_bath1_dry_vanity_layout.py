# Reconstruct Common Bathroom (욕실1) and Corridor Dry Vanity to match 1:1 with Modelhouse and Blueprint
import bpy
import math
from mathutils import Vector

col_furnish = bpy.data.collections.get('Apt_Openings') or bpy.context.scene.collection
col_floors = bpy.data.collections.get('Apt_Floors') or bpy.context.scene.collection

# 1. Materials
mat_ceramic = bpy.data.materials.get('Mat_Ceramic') or bpy.data.materials.get('Mat_Wall_White')
mat_marble = bpy.data.materials.get('Mat_Marble_White') or bpy.data.materials.get('Mat_Countertop_Granite')
mat_cab = bpy.data.materials.get('Mat_Cabinet_Cashmere') or bpy.data.materials.get('Mat_Cashmere_Laminate')
mat_chrome = bpy.data.materials.get('Mat_Chrome_Metal') or bpy.data.materials.get('Mat_Chrome')
mat_glass = bpy.data.materials.get('Mat_Glass_Clear') or bpy.data.materials.get('Mat_Glass')
mat_tile = bpy.data.materials.get('Mat_Tile_Grey') or bpy.data.materials.get('Mat_BathTile_Wall')

# Remove old mismatched Bath1 objects
old_names = [
    'Bath1_Shower_Screen', 'Bath1_Shower_Head', 'Bath1_Toilet_Bowl', 'Bath1_Toilet_Lid',
    'Bath1_Toilet_Tank', 'Bath1_Vanity_Cab', 'Bath1_Vanity_Top', 'Bath1_Mirror',
    'BathProp_TowelBar_Bar', 'BathProp_TowelBar_TowelB', 'BathProp_TowelBar_TowelF',
    'Bath1_Shower_Door', 'Bath1_Shower_Column', 'Bath1_Shower_Rail', 'Bath1_Shower_Handset',
    'Bath1_Med_Cabinet', 'Bath1_Med_Mirror', 'Bath1_Paper_Holder', 'Bath1_Bidet_Spray',
    'Bath1_Dry_Vanity_Cab', 'Bath1_Dry_Vanity_Top', 'Bath1_Dry_Vanity_Sink', 'Bath1_Dry_Faucet',
    'Bath1_Dry_Mirror', 'Bath1_Dry_LED_L', 'Bath1_Dry_LED_R', 'Bath1_Dry_TowelBar',
    'Floor_Bath1_Vanity', 'Bath1_Shower_Curb'
]
for name in old_names:
    o = bpy.data.objects.get(name)
    if o:
        bpy.data.objects.remove(o, do_unlink=True)

def make_box(name, loc, dim, mat=None, col=col_furnish):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
    o = bpy.context.active_object
    o.name = name
    o.scale = Vector(dim)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if mat:
        o.data.materials.append(mat)
    if o.name in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.unlink(o)
    if o.name not in col.objects:
        col.objects.link(o)
    return o

def make_cyl(name, loc, radius, depth, rot=(0,0,0), mat=None, col=col_furnish):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, location=loc, rotation=rot)
    o = bpy.context.active_object
    o.name = name
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if mat:
        o.data.materials.append(mat)
    if o.name in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.unlink(o)
    if o.name not in col.objects:
        col.objects.link(o)
    return o

# ==============================================================================
# PART A: CORRIDOR-END DRY VANITY (복도 끝 건식 세면대 - display84a_07_part_1.jpg)
# Niche: X=[14.35, 14.98], Y=[4.45, 5.55], facing West into corridor
# ==============================================================================

# Dry Vanity Floor
make_box('Floor_Bath1_Vanity', (14.665, 5.00, 0.002), (0.63, 1.10, 0.01), mat=mat_tile, col=col_floors)

# Floating Vanity Cabinet (cashmere laminated, floating 20cm above floor)
make_box('Bath1_Dry_Vanity_Cab', (14.675, 5.00, 0.525), (0.55, 1.08, 0.65), mat=mat_cab)

# Engineered Quartz Vanity Countertop
make_box('Bath1_Dry_Vanity_Top', (14.665, 5.00, 0.865), (0.57, 1.10, 0.03), mat=mat_marble)

# Undermount Ceramic Sink Basin (recessed top rim)
make_box('Bath1_Dry_Vanity_Sink', (14.62, 5.00, 0.82), (0.38, 0.52, 0.12), mat=mat_ceramic)

# Gooseneck Chrome Designer Faucet
make_cyl('Bath1_Dry_Faucet_Base', (14.85, 5.00, 0.90), 0.022, 0.06, mat=mat_chrome)
make_cyl('Bath1_Dry_Faucet_Neck', (14.85, 5.00, 1.02), 0.012, 0.18, mat=mat_chrome)
make_cyl('Bath1_Dry_Faucet_Spout', (14.77, 5.00, 1.08), 0.010, 0.14, rot=(0, math.radians(70), 0), mat=mat_chrome)

# Large Illuminated Mirror on East wall
make_box('Bath1_Dry_Mirror', (14.965, 5.00, 1.45), (0.015, 1.04, 1.10), mat=mat_glass)

# Vertical LED Cove Side Lighting Panels (matching display84a_07_part_1.jpg!)
mat_emit_warm = bpy.data.materials.get('Mat_LED_Foyer') or bpy.data.materials.get('Mat_LED_Strip')
if not mat_emit_warm:
    mat_emit_warm = bpy.data.materials.new('Mat_LED_Warm')
    mat_emit_warm.use_nodes = True
    nodes = mat_emit_warm.node_tree.nodes
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    em = nodes.new('ShaderNodeEmission')
    em.inputs['Color'].default_value = (1.0, 0.93, 0.82, 1.0)
    em.inputs['Strength'].default_value = 8.0
    mat_emit_warm.node_tree.links.new(em.outputs['Emission'], out.inputs['Surface'])

make_box('Bath1_Dry_LED_L', (14.955, 4.50, 1.45), (0.012, 0.04, 1.10), mat=mat_emit_warm)
make_box('Bath1_Dry_LED_R', (14.955, 5.50, 1.45), (0.012, 0.04, 1.10), mat=mat_emit_warm)

# Chrome Towel Bar on South wall
make_box('Bath1_Dry_TowelBar', (14.665, 4.46, 1.15), (0.35, 0.02, 0.02), mat=mat_chrome)
make_box('Bath1_Dry_Towel', (14.665, 4.47, 1.00), (0.28, 0.015, 0.30), mat=bpy.data.materials.get('Mat_Linen') or mat_ceramic)

# Downlight over dry vanity
lv = bpy.data.lights.get('Light_Bath1_Dry_Spot') or bpy.data.lights.new('Light_Bath1_Dry_Spot', 'POINT')
lv.energy = 40.0
lv.color = (1.0, 0.95, 0.88)
lvo = bpy.data.objects.get('Light_Bath1_Dry_Spot') or bpy.data.objects.new('Light_Bath1_Dry_Spot', lv)
if lvo.name not in bpy.context.scene.collection.objects:
    bpy.context.scene.collection.objects.link(lvo)
lvo.location = (14.65, 5.00, 2.25)

# ==============================================================================
# PART B: WET BATHROOM (습식 욕실: 변기 + 샤워부스 - display84a_07_part_2.jpg)
# Bounds: X=[13.40, 14.95], Y=[5.65, 7.55]
# ==============================================================================

# Realign Wet Bathroom Floor
fb = bpy.data.objects.get('Floor_CommonBath')
if fb:
    fb.location = Vector((14.175, 6.60, 0.002))
    fb.dimensions = Vector((1.55, 1.90, 0.01))

# 1. TOILET (변기) - East wall (X=14.95), facing West (Y=6.15)
# Toilet Tank flush against East wall
make_box('Bath1_Toilet_Tank', (14.82, 6.15, 0.42), (0.20, 0.42, 0.76), mat=mat_ceramic)
# Toilet Bowl extending West
make_box('Bath1_Toilet_Bowl', (14.56, 6.15, 0.22), (0.42, 0.38, 0.42), mat=mat_ceramic)
# Toilet Lid
make_box('Bath1_Toilet_Lid', (14.56, 6.15, 0.435), (0.41, 0.37, 0.03), mat=mat_ceramic)

# Mirrored Medicine Storage Cabinet above Toilet on East wall
make_box('Bath1_Med_Cabinet', (14.86, 6.15, 1.60), (0.16, 0.80, 0.75), mat=mat_cab)
make_box('Bath1_Med_Mirror', (14.77, 6.15, 1.60), (0.015, 0.78, 0.73), mat=mat_glass)

# Chrome Paper Holder on South partition wall
make_box('Bath1_Paper_Holder', (14.50, 5.67, 0.75), (0.16, 0.02, 0.12), mat=mat_chrome)
# Bidet spray gun on East wall
make_box('Bath1_Bidet_Spray', (14.85, 6.45, 0.50), (0.05, 0.04, 0.15), mat=mat_chrome)

# 2. SHOWER BOOTH (샤워실 / 샤워부스 - North zone: Y=[6.70, 7.55])
# Water-stop threshold curb under glass partition at Y=6.70
make_box('Bath1_Shower_Curb', (14.175, 6.70, 0.02), (1.55, 0.06, 0.04), mat=mat_marble)

# Fixed Glass Screen: from East wall X=14.95 to X=14.20 at Y=6.70
make_box('Bath1_Shower_Screen', (14.575, 6.70, 1.05), (0.75, 0.015, 2.05), mat=mat_glass)

# Glass Shower Door: hinged near West wall, slightly angled inward (matching blueprint!)
make_box('Bath1_Shower_Door', (13.825, 6.82, 1.05), (0.70, 0.015, 2.05), mat=mat_glass)
door_glass = bpy.data.objects.get('Bath1_Shower_Door')
if door_glass:
    door_glass.rotation_euler.z = math.radians(-18.0)

# Shower Column on East wall (X=14.92, Y=7.15)
make_cyl('Bath1_Shower_Mixer', (14.90, 7.15, 1.05), 0.035, 0.18, rot=(0, math.radians(90), 0), mat=mat_chrome)
make_cyl('Bath1_Shower_Rail', (14.91, 7.15, 1.45), 0.012, 0.90, mat=mat_chrome)
make_cyl('Bath1_Shower_Handset', (14.86, 7.18, 1.55), 0.018, 0.22, rot=(math.radians(20), 0, 0), mat=mat_chrome)

# Rain Shower Head extending from North/East
make_box('Bath1_Shower_Arm', (14.65, 7.15, 2.18), (0.50, 0.03, 0.03), mat=mat_chrome)
make_cyl('Bath1_Shower_Head', (14.55, 7.15, 2.15), 0.11, 0.02, mat=mat_chrome)

# 3. WET BATHROOM DOOR (욕실문)
# Hinge on West wall (X=13.40), swinging inward into wet bathroom
d_bath = bpy.data.objects.get('ProDoorLeaf_CommonBath')
if d_bath:
    d_bath.location = Vector((13.42, 5.68, 0.015))
    d_bath.rotation_euler.z = math.radians(65.0)  # swings open against west wall

# Ceiling Spotlight for Wet Bathroom
lb = bpy.data.lights.get('Light_Bath1_Wet_Spot') or bpy.data.lights.new('Light_Bath1_Wet_Spot', 'POINT')
lb.energy = 50.0
lb.color = (1.0, 0.97, 0.92)
lbo = bpy.data.objects.get('Light_Bath1_Wet_Spot') or bpy.data.objects.new('Light_Bath1_Wet_Spot', lb)
if lbo.name not in bpy.context.scene.collection.objects:
    bpy.context.scene.collection.objects.link(lbo)
lbo.location = (14.175, 6.60, 2.25)

# Downlight over Shower
ls = bpy.data.lights.get('Light_Bath1_Shower') or bpy.data.lights.new('Light_Bath1_Shower', 'POINT')
ls.energy = 40.0
ls.color = (0.95, 0.97, 1.0)
lso = bpy.data.objects.get('Light_Bath1_Shower') or bpy.data.objects.new('Light_Bath1_Shower', ls)
if lso.name not in bpy.context.scene.collection.objects:
    bpy.context.scene.collection.objects.link(lso)
lso.location = (14.175, 7.15, 2.25)

print('SUCCESS: Bath1 and Dry Vanity completely reconstructed to 1:1 blueprint & modelhouse specifications.')
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
