"""Q6 AC-room finishes. Run after Q5 restores the traced wall boundary."""
import math
import os
import runpy
import sys
import bpy
from mathutils import Matrix, Vector

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import generate_high_detail_assets as A

for obj in list(bpy.data.objects):
    if obj.name.startswith(('Q6_', 'AC_Condenser_')) or obj.name in ('Floor_ACOutdoor', 'Floor_KitchenBalcony'):
        bpy.data.objects.remove(obj, do_unlink=True)
col = A.get_col('Apt_UtilityRoom')
wall = bpy.data.materials['Mat_Wall_Interior']
tile = bpy.data.materials['Mat_Tile_Grey']
frame = bpy.data.materials['Mat_WindowFrame_White']
metal = bpy.data.materials['Mat_Chrome_Metal']
dark = bpy.data.materials['Mat_AC_Grill']


def box(name, x1, x2, y1, y2, z1, z2, mat):
    return A.create_beveled_box(name, (x1+x2)/2, (y1+y2)/2, z1,
                                x2-x1, y2-y1, z2-z1, bevel=0.002, mat=mat, col=col)


# The hall floor void otherwise cuts under the eastern part of this room.
box('Q6_UtilityFloorBase', 8.662, 10.181, 8.175, 9.30, -0.15, 0.0, wall)
box('Q6_UtilityFloor', 8.662, 10.181, 8.175, 9.30, 0.002, 0.014, tile)
# shortcut: vent sill/head heights and louver profile are assumed; replace from facade details.
box('Q6_Vent_SillWall', 8.963, 9.9, 9.30, 9.469, 0.0, 0.65, wall)
box('Q6_Vent_Header', 8.963, 9.9, 9.30, 9.469, 2.10, 2.30, wall)
box('Q6_Vent_JambW', 8.963, 8.993, 9.30, 9.469, 0.65, 2.10, frame)
box('Q6_Vent_JambE', 9.87, 9.9, 9.30, 9.469, 0.65, 2.10, frame)
box('Q6_Vent_Sill', 8.993, 9.87, 9.30, 9.469, 0.65, 0.68, frame)
box('Q6_Vent_Head', 8.993, 9.87, 9.30, 9.469, 2.07, 2.10, frame)
# A dark backing prevents an exposed view into the unmodelled exterior/hall.
box('Q6_Vent_Back', 8.993, 9.87, 9.44, 9.46, 0.68, 2.07, dark)
for i in range(20):
    z = 0.70 + i * 0.069
    slat = box(f'Q6_Vent_Slat{i:02}', 8.993, 9.87, 9.32, 9.38, z, z+0.05, frame)
    slat.rotation_euler.x = math.radians(20)

# Keep the complete condenser/feet/pipes together, turned along the west wall.
A.create_ac_outdoor_unit('AC_Condenser', 0, 0, 0.014, facing='-y',
                         mat_body=bpy.data.materials['Mat_AC_Body'], mat_grill=dark,
                         mat_pipe=metal, col=col)
bpy.context.view_layer.update()
transform = Matrix.Translation(Vector((8.90, 8.775, 0))) @ Matrix.Rotation(math.pi/2, 4, 'Z')
for obj in col.objects:
    if obj.name.startswith('AC_Condenser_'):
        obj.matrix_world = transform @ obj.matrix_world
bpy.context.view_layer.update()
runpy.run_path(os.path.join(ROOT, 'scripts', 'verify_utility_room.py'))
runpy.run_path(os.path.join(ROOT, 'scripts', 'verify_alpha_room.py'))
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT, 'apt_84a_photoreal_tour.blend'))
print('Q6 UTILITY SAVED', flush=True)
