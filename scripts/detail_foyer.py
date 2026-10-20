"""Q7: 84A official VR scenes 017/018 -> detailed foyer and entry pantry.

Run after Q4/Q5/Q6. Opening coordinates follow the plan; hardware dimensions
and the fully open sliding-panel parking position are modelling assumptions.
"""
import math
import os
import runpy
import sys
import bmesh
import bpy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import generate_high_detail_assets as A

for obj in list(bpy.data.objects):
    if obj.name.startswith(('Q7_', 'Foyer_Shoe_', 'Foyer_Mirror_',
                            'ProDoorLeaf_EntryPantry', 'ProDoorTrim_EntryPantry',
                            'ProDoorHandle_EntryPantry')) or obj.name in (
            'Floor_EntrancePantry', 'Floor_Foyer', 'Foyer_Threshold'):
        bpy.data.objects.remove(obj, do_unlink=True)
col = A.get_col('Apt_FoyerDetail')


def material(name, color, roughness, metallic=0.0, alpha=1.0):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.diffuse_color = (*color, alpha)
    shader = mat.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = (*color, 1)
    shader.inputs['Roughness'].default_value = roughness
    shader.inputs['Metallic'].default_value = metallic
    shader.inputs['Alpha'].default_value = alpha
    return mat


ivory = material('Mat_Q7_Ivory', (0.72, 0.69, 0.63), 0.48)
aluminium = material('Mat_Q7_Aluminium', (0.49, 0.48, 0.45), 0.30, 0.75)
charcoal = material('Mat_Q7_Charcoal', (0.045, 0.043, 0.040), 0.52, 0.25)
tile = material('Mat_Q7_Stone', (0.36, 0.35, 0.33), 0.58)
grout = material('Mat_Q7_Grout', (0.19, 0.18, 0.17), 0.82)
white = material('Mat_Q7_StorageWhite', (0.82, 0.80, 0.75), 0.54)
dark = material('Mat_Q7_ShoeInterior', (0.095, 0.075, 0.058), 0.65)
frost = material('Mat_Q7_FrostedGlass', (0.73, 0.70, 0.64), 0.55, alpha=0.88)
frost.node_tree.nodes.get('Principled BSDF').inputs['Transmission Weight'].default_value = 0.25
led = material('Mat_Q7_LED', (1.0, 0.84, 0.64), 0.4)
led_shader = led.node_tree.nodes.get('Principled BSDF')
led_shader.inputs['Emission Color'].default_value = (1.0, 0.80, 0.56, 1)
led_shader.inputs['Emission Strength'].default_value = 3.0


def box(name, x1, x2, y1, y2, z1, z2, mat, bevel=0.002):
    return A.create_beveled_box(name, (x1+x2)/2, (y1+y2)/2, z1,
                                x2-x1, y2-y1, z2-z1, bevel=bevel, seg=3, mat=mat, col=col)


def cylinder(name, x, y, z, radius, height, mat):
    return A.create_cylinder(name, x, y, z, radius, height, seg=16, mat=mat, col=col)


# One continuous finish, with physical fine grout lines instead of a plain slab.
box('Floor_Foyer', 11.775, 13.35, 5.75, 7.969, 0.002, 0.014, tile)
box('Floor_EntrancePantry', 10.556, 11.588, 5.775, 7.65, 0.002, 0.014, tile)
for i, x in enumerate((11.18, 11.80, 12.40, 13.0)):
    low, high = (5.775, 7.65) if x < 11.588 else (5.75, 7.969)
    box(f'Q7_GroutX{i}', x-0.0015, x+0.0015, low, high, 0.014, 0.0148, grout, bevel=0)
for i, y in enumerate((6.35, 6.95, 7.55)):
    for tag, a, b in [('F', 11.775, 13.35), ('P', 10.556, 11.588)]:
        box(f'Q7_GroutY{tag}{i}', a, b, y-0.0015, y+0.0015, 0.014, 0.0148, grout, bevel=0)
box('Foyer_Threshold', 11.775, 12.881, 5.70, 5.80, 0.014, 0.025,
    bpy.data.materials['Mat_Marble_White'])
for tag, x1, x2, y1, y2 in [('FoyerW_N', 11.715, 11.775, 7.23, 7.87),
                           ('FoyerW_S', 11.715, 11.775, 5.77, 6.23),
                           ('PantryW', 10.556, 10.575, 5.79, 7.63)]:
    box('Q7_Skirting_'+tag, x1, x2, y1, y2, 0.014, 0.085, ivory)

# Closed cabinetry matches the reference; the shell and interior shelves are real meshes.
box('Q7_Shoe_Back', 13.30, 13.33, 5.78, 7.63, 0.20, 2.29, dark)
for tag, a, b in [('S', 5.78, 5.80), ('N', 7.61, 7.63)]:
    box('Q7_Shoe_Side'+tag, 12.88, 13.33, a, b, 0.20, 2.29, ivory)
for i, z in enumerate((0.20, 0.48, 0.74, 1.00, 1.26, 1.52, 1.78, 2.04, 2.27)):
    box(f'Q7_Shoe_Shelf{i}', 12.89, 13.30, 5.80, 7.61, z, z+0.02, dark)
for i in range(4):
    a = 5.78 + i * 1.85/4
    box(f'Q7_Shoe_Door{i}', 12.855, 12.878, a+0.002, a+1.85/4-0.002, 0.205, 2.285, ivory)
    box(f'Q7_Shoe_Reveal{i}', 12.878, 12.887, a+0.002, a+1.85/4-0.002, 0.205, 2.285, dark)
box('Q7_Shoe_LED', 12.90, 12.92, 5.83, 7.58, 0.186, 0.194, led)
# Small rounded sole/upper/toe geometry avoids the previous rectangular shoe props.
for i, y in enumerate((6.07, 6.22, 6.60, 6.75)):
    shoe_mat = charcoal if i > 1 else white
    box(f'Q7_ShoeProp_Sole{i}', 12.97, 13.22, y, y+0.10, 0.016, 0.028, dark, bevel=0.018)
    box(f'Q7_ShoeProp_Upper{i}', 13.0, 13.20, y+0.005, y+0.095, 0.028, 0.075, shoe_mat, bevel=0.025)

# Flush ivory double leaves park INSIDE the pantry; no orphaned handles/mirror over the opening.
for tag, y1, y2 in [('S', 6.235, 6.263), ('N', 7.20, 7.228)]:
    box('Q7_PantryJamb_'+tag, 11.588, 11.72, y1, y2, 0.014, 2.105, ivory)
box('Q7_PantryJamb_Head', 11.588, 11.72, 6.235, 7.228, 2.08, 2.12, ivory)
for tag, name, y in [('L', 'ProDoorLeaf_EntryPantry', 6.28),
                      ('R', 'ProDoorLeaf_EntryPantry_R', 7.155)]:
    box(name, 11.11, 11.57, y, y+0.026, 0.025, 2.08, ivory)
    box('Q7_PantryPull_'+tag, 11.115, 11.13, y+0.026, y+0.032, 0.92, 1.10, aluminium)
    for i, z in enumerate((0.30, 1.08, 1.86)):
        hinge = cylinder(f'Q7_PantryHinge_{tag}{i}', 11.535, y+0.029, z, 0.021, 0.004, aluminium)
        hinge.rotation_euler.x = math.pi/2
        box(f'Q7_PantryHingeArm_{tag}{i}', 11.54, 11.595, y+0.006, y+0.022, z-0.01, z+0.01, aluminium)

# U-shaped shelving and aluminium uprights from official scene 018.
for i, z in enumerate((0.28, 0.76, 1.24, 1.72, 2.12)):
    for tag, x1, x2, y1, y2 in [('W', 10.58, 10.80, 6.02, 7.40),
                                ('S', 10.58, 11.55, 5.80, 6.02),
                                ('N', 10.58, 11.55, 7.40, 7.62)]:
        box(f'Q7_PantryShelf_{tag}{i}', x1, x2, y1, y2, z, z+0.022, ivory, bevel=0.006)
        if tag == 'W':
            box(f'Q7_PantryRail_{tag}{i}', 10.79, 10.81, y1, y2, z-0.015, z, aluminium)
        else:
            yy = 6.005 if tag == 'S' else 7.395
            box(f'Q7_PantryRail_{tag}{i}', x1, x2, yy, yy+0.02, z-0.015, z, aluminium)
for i, (x, y) in enumerate(((10.80, 6.02), (10.80, 6.70), (10.80, 7.40),
                            (11.50, 6.02), (11.50, 7.40))):
    cylinder(f'Q7_PantryPost_{i}', x, y, 0.014, 0.014, 2.19, aluminium)
    for j, z in enumerate((0.28, 0.76, 1.24, 1.72, 2.12)):
        box(f'Q7_PantryBracket_{i}_{j}', x-0.021, x+0.021, y-0.022, y+0.022, z-0.018, z+0.026, aluminium)
for i, (x, y, z, w, d, h) in enumerate(((10.69, 6.35, 0.302, 0.18, 0.30, 0.27),
        (10.69, 6.80, 1.262, 0.18, 0.32, 0.22), (10.99, 5.91, 1.742, 0.30, 0.16, 0.24),
        (11.24, 7.51, 0.782, 0.30, 0.16, 0.25), (10.96, 7.51, 1.742, 0.25, 0.16, 0.22))):
    box(f'Q7_PantryProp_Bin{i}', x-w/2, x+w/2, y-d/2, y+d/2, z, z+h, white, bevel=0.014)
    box(f'Q7_PantryProp_Lid{i}', x-w/2-0.002, x+w/2+0.002, y-d/2-0.002, y+d/2+0.002,
        z+h-0.018, z+h, ivory, bevel=0.006)
    box(f'Q7_PantryProp_Pull{i}', x+w/2, x+w/2+0.004, y-0.025, y+0.025, z+h*0.65, z+h*0.65+0.015, aluminium)
for i, x in enumerate((11.02, 11.30)):
    cylinder(f'Q7_PantryProp_Bottle{i}', x, 5.91, 0.782, 0.035, 0.23, white)
    cylinder(f'Q7_PantryProp_BottleCap{i}', x, 5.91, 1.012, 0.027, 0.03, charcoal)

# The tour keeps the automatic sliding door open, parked along the corridor-side wall.
box('Q7_MiddleDoor_Rail', 10.65, 12.90, 5.57, 5.69, 2.12, 2.24, ivory)
box('Q7_MiddleDoor_RailGroove', 10.67, 12.88, 5.565, 5.57, 2.125, 2.135, aluminium)
for tag, a, b in [('W', 11.755, 11.79), ('E', 12.86, 12.895)]:
    box('Q7_MiddleDoor_Jamb'+tag, a, b, 5.57, 5.70, 0.014, 2.12, ivory)
for tag, a, b in [('W', 10.67, 10.695), ('E', 11.725, 11.75)]:
    box('Q7_MiddleDoor_Leaf'+tag, a, b, 5.585, 5.625, 0.035, 2.115, aluminium)
for tag, z1, z2 in [('Bottom', 0.035, 0.065), ('Top', 2.085, 2.115)]:
    box('Q7_MiddleDoor_Leaf'+tag, 10.695, 11.725, 5.585, 5.625, z1, z2, aluminium)
box('Q7_MiddleDoor_Glass', 10.695, 11.725, 5.597, 5.609, 0.065, 2.085, frost)
box('Q7_MiddleDoor_Sensor', 12.27, 12.37, 5.69, 5.72, 2.17, 2.23, ivory)
box('Q7_MiddleDoor_SensorLens', 12.29, 12.35, 5.719, 5.723, 2.18, 2.22, charcoal)
box('Q7_MiddleDoor_Switch', 12.865, 12.90, 5.88, 5.98, 0.98, 1.13, charcoal)
box('Q7_MiddleDoor_Guide', 11.72, 11.75, 5.58, 5.63, 0.014, 0.028, aluminium)
# Entrance hardware remains at the existing plan opening, not the modelhouse exhibition hall.
for obj in bpy.data.objects:
    if obj.name.startswith('Front_Door_'):
        obj.data.materials.clear()
        obj.data.materials.append(charcoal if 'Lock' in obj.name else aluminium)
for i, z in enumerate((0.35, 1.10, 1.85)):
    cylinder(f'Q7_FrontHinge{i}', 11.85, 7.93, z, 0.012, 0.065, aluminium)

# Real fixture geometry plus warm lighting; web lights are placed at these same rooms.
for i, (x, y, energy) in enumerate(((12.32, 6.65, 24), (11.15, 6.42, 13), (11.15, 7.05, 13))):
    cylinder(f'Q7_Downlight_Rim{i}', x, y, 2.28, 0.047, 0.015, ivory)
    cylinder(f'Q7_Downlight_LED{i}', x, y, 2.275, 0.035, 0.005, led)
    data = bpy.data.lights.new(f'Q7_Light{i}', 'AREA')
    data.energy = energy
    data.color = (1.0, 0.90, 0.78)
    data.shape = 'DISK'
    data.size = 0.35
    obj = bpy.data.objects.new(data.name, data)
    col.objects.link(obj)
    obj.location = (x, y, 2.26)

for obj in col.objects:
    if obj.type == 'MESH':
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
        bm.to_mesh(obj.data)
        bm.free()
bpy.context.view_layer.update()
runpy.run_path(os.path.join(ROOT, 'scripts', 'verify_foyer.py'))
runpy.run_path(os.path.join(ROOT, 'scripts', 'verify_alpha_room.py'))
runpy.run_path(os.path.join(ROOT, 'scripts', 'verify_utility_room.py'))
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT, 'apt_84a_photoreal_tour.blend'))
print('Q7 FOYER SAVED', flush=True)
