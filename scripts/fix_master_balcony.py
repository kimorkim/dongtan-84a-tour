"""Repair the master balcony/refuge from the mirrored plan and modelhouse photo.

Run from the project root against the saved master blend. Rebuilds Q4 objects only.
XY openings follow the traced plan; window heights/hardware are modelling assumptions.
"""
import os
import sys

import bpy
from mathutils import Vector

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import generate_high_detail_assets as A

col = A.get_col('Apt_MasterBalcony')
legacy = ('Q4_', 'ProDoorLeaf_MasterBalcony', 'ProDoorLeaf_MasterRefuge',
          'Win_MasterVent', 'Win_MasterMain', 'Liner_MasterVent', 'Liner_MasterMain',
          'Door_MasterBalcony_Glass', 'Liner_BalconyDoor', 'Refuge_Balcony',
          'Q2_Rail_Master', 'Curtain_Master', 'Q2_Sheer_Master',
          'Q2_NightSouth', 'Q2_NightTopS', 'Q2_NightPlantS',
          'Q2_PendantS_', 'Q2_PendantLightS')
for obj in list(bpy.data.objects):
    if obj.name.startswith(legacy) or obj.name == 'Floor_MasterBalcony':
        bpy.data.objects.remove(obj, do_unlink=True)

wall = bpy.data.materials['Mat_Wall_Interior']
tile = bpy.data.materials['Mat_Tile_Grey']
frame = bpy.data.materials['Mat_WindowFrame_White']
glass = bpy.data.materials['Mat_Glass_Clear']
metal = bpy.data.materials['Mat_Chrome_Metal']
door_mat = bpy.data.materials['Mat_Cabinet_Cashmere']
rail_mat = bpy.data.materials.get('Mat_Rail_Dark') or metal


def box(name, x1, x2, y1, y2, z1, z2, mat):
    return A.create_beveled_box(name, (x1+x2)/2, (y1+y2)/2, z1,
                                x2-x1, y2-y1, z2-z1, bevel=0.002, mat=mat, col=col)


# Two separate rooms, matching the plan's x2.23..2.38 partition and side doorway.
box('Q4_Floor_Refuge', 0.45, 2.23, 0.431, 1.744, 0.002, 0.014, tile)
box('Q4_Floor_Balcony', 2.381, 4.106, 0.469, 1.744, 0.002, 0.014, tile)
box('Q4_RefugeDoor_Header', 2.231, 2.381, 0.544, 1.312, 2.10, 2.30, wall)
for name, y1, y2 in [('S', 0.544, 0.574), ('N', 1.282, 1.312)]:
    box('Q4_RefugeDoor_Jamb'+name, 2.225, 2.39, y1, y2, 0.014, 2.10, frame)
box('Q4_RefugeDoor_Head', 2.225, 2.39, 0.544, 1.312, 2.07, 2.10, frame)
box('Q4_RefugeDoor_Threshold', 2.225, 2.39, 0.574, 1.282, 0.014, 0.022, metal)
# Open 90 degrees into the balcony, as other passable tour doors are displayed.
box('ProDoorLeaf_MasterRefuge_Panel', 2.32, 3.02, 0.565, 0.610, 0.024, 2.06, door_mat)
box('ProDoorLeaf_MasterRefuge_Handle', 2.89, 2.99, 0.612, 0.635, 1.00, 1.025, metal)

# The two squares shown in the plan are represented as flush covers only.
# shortcut: cover/device specification is absent in the MEP plan; replace from an architectural detail.
for i, x in enumerate((0.98, 1.70), 1):
    box(f'Q4_RefugeFloorCover{i}_Frame', x-0.32, x+0.32, 0.94, 1.58, 0.014, 0.025, metal)
    box(f'Q4_RefugeFloorCover{i}_Panel', x-0.30, x+0.30, 0.96, 1.56, 0.025, 0.028, tile)
for name, bounds in [('W', (0.45, 0.47, 0.45, 1.72)),
                     ('N', (0.47, 2.23, 1.72, 1.744))]:
    box('Q4_RefugeSkirting_'+name, *bounds, 0.014, 0.075, frame)

# Actual refuge front opening is x0.919..1.856. The old x0.50..0.91 window sat in solid wall.
box('Q4_RefugeWindow_SillWall', 0.919, 1.856, 0.263, 0.431, 0.0, 0.90, wall)
box('Q4_RefugeWindow_Header', 0.919, 1.856, 0.263, 0.431, 2.10, 2.30, wall)
A.create_window_unit('Q4_RefugeWindow', 1.3875, 0.347, 0.90, 0.937, 0.168, 1.20,
                     panes=2, mat_frame=frame, mat_glass=glass, col=col)
box('Q4_BalconyWindow_Curb', 2.381, 3.919, 0.263, 0.469, 0.0, 0.05, wall)
box('Q4_BalconyWindow_Header', 2.381, 3.919, 0.263, 0.469, 2.20, 2.30, wall)
A.create_window_unit('Q4_BalconyWindow', 3.15, 0.366, 0.05, 1.538, 0.16, 2.15,
                     panes=2, mat_frame=frame, mat_glass=glass, col=col)
A.create_railing('Q4_BalconyRail', 2.40, 3.90, 0.22, 0.05, height=1.05,
                 mat=rail_mat, col=col)

# Two-track sliding door: eastern leaf parked over the western panel.
box('Q4_BalconyDoor_Header', 2.231, 3.919, 1.70, 1.84, 2.15, 2.30, wall)
for name, x1, x2 in [('L', 2.24, 2.29), ('R', 3.86, 3.91)]:
    box('Q4_BalconyDoor_Jamb'+name, x1, x2, 1.72, 1.82, 0.014, 2.15, frame)
box('Q4_BalconyDoor_Head', 2.24, 3.91, 1.72, 1.82, 2.10, 2.15, frame)
box('Q4_BalconyDoor_Threshold', 2.24, 3.91, 1.70, 1.84, 0.014, 0.024, metal)
for track, yy in enumerate((1.735, 1.81), 1):
    box(f'Q4_BalconyDoor_Track{track}', 2.29, 3.86, yy-0.009, yy+0.009, 0.024, 0.028, metal)
    box(f'Q4_BalconyDoor_TopTrack{track}', 2.29, 3.86, yy-0.012, yy+0.012, 2.08, 2.10, frame)
A.create_window_unit('Q4_BalconySidelight', 2.69, 1.735, 0.028, 0.80, 0.05, 2.052,
                     panes=1, mat_frame=frame, mat_glass=glass, col=col)
A.create_window_unit('ProDoorLeaf_MasterBalcony', 2.69, 1.81, 0.028, 0.80, 0.05, 2.052,
                     panes=1, mat_frame=frame, mat_glass=glass, col=col)
box('ProDoorLeaf_MasterBalcony_Handle', 3.045, 3.075, 1.836, 1.844, 0.97, 1.10, metal)

# Park curtains beside the opening rather than across the walking route.
sheer = bpy.data.materials.get('Mat_Q2_Sheer') or bpy.data.materials['Mat_Curtain']
box('Q4_Curtain_W', 2.30, 2.54, 1.88, 1.92, 0.05, 2.25, sheer)
box('Q4_Curtain_E', 3.98, 4.12, 1.88, 1.92, 0.05, 2.25, sheer)
bpy.context.view_layer.update()

assert not any(o.name.startswith('Refuge_Balcony') for o in bpy.data.objects)
assert bpy.data.objects.get('Q2_NightSouth') is None  # Old table intersected the bedroom/refuge wall.
assert abs(bpy.data.objects['Q4_RefugeWindow_Glass1'].location.y - 0.347) < 1e-5
# Sliding leaf remains parallel to the wall and leaves the eastern passage clear.
leaf = bpy.data.objects['ProDoorLeaf_MasterBalcony_Glass']
points = [leaf.matrix_world @ Vector(v) for v in leaf.bound_box]
assert max(p.y for p in points) - min(p.y for p in points) < 0.08
assert max(p.x for p in points) < 3.10
assert bpy.data.objects.get('Q4_BalconyDoor_Hinge') is None
assert bpy.data.objects['Q4_BalconyDoor_Threshold'].dimensions.z < 0.03
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT, 'apt_84a_photoreal_tour.blend'))
print('Q4 BALCONY/REFUGE SAVED: two open doorways, closed exterior windows, traced walls preserved')
