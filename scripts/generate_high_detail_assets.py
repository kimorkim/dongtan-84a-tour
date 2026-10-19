import bpy
import math

def get_col(name):
    col = bpy.data.collections.get(name)
    if not col:
        col = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(col)
    return col

def clear_col(col):
    for obj in list(col.objects):
        bpy.data.objects.remove(obj, do_unlink=True)

def create_beveled_box(name, x, y, z, sx, sy, sz, bevel=0.01, seg=2, mat=None, col=None):
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    if col:
        col.objects.link(obj)
    else:
        bpy.context.scene.collection.objects.link(obj)
        
    # Local coordinates: centered at XY (0,0), base at Z=0
    x1, x2 = -sx/2, sx/2
    y1, y2 = -sy/2, sy/2
    z1, z2 = 0.0, sz
    
    verts = [
        (x1, y1, z1), (x2, y1, z1), (x2, y2, z1), (x1, y2, z1),
        (x1, y1, z2), (x2, y1, z2), (x2, y2, z2), (x1, y2, z2)
    ]
    faces = [
        (0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1),
        (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)
    ]
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    
    obj.location = (x, y, z)
    
    for poly in mesh.polygons:
        poly.use_smooth = True
        
    if bevel > 0:
        bev = obj.modifiers.new("Bevel", 'BEVEL')
        bev.width = bevel
        bev.segments = seg
        bev.limit_method = 'ANGLE'
        bev.angle_limit = math.radians(35)
        
    if mat:
        obj.data.materials.append(mat)
    return obj

def create_cylinder(name, x, y, z, r, h, seg=16, mat=None, col=None):
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    if col:
        col.objects.link(obj)
    else:
        bpy.context.scene.collection.objects.link(obj)
        
    verts = []
    # bottom circle in local space
    for i in range(seg):
        theta = 2 * math.pi * i / seg
        verts.append((r * math.cos(theta), r * math.sin(theta), 0.0))
    # top circle in local space
    for i in range(seg):
        theta = 2 * math.pi * i / seg
        verts.append((r * math.cos(theta), r * math.sin(theta), h))
        
    faces = []
    for i in range(seg):
        next_i = (i + 1) % seg
        faces.append((i, next_i, next_i + seg, i + seg))
    faces.append(list(reversed(range(seg))))
    faces.append(list(range(seg, 2 * seg)))
    
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    
    obj.location = (x, y, z)
    
    for poly in mesh.polygons:
        poly.use_smooth = True
        
    bev = obj.modifiers.new("Bevel", 'BEVEL')
    bev.width = min(0.005, r * 0.2)
    bev.segments = 2
    
    if mat:
        obj.data.materials.append(mat)
    return obj

def create_chair(name, x, y, z, rot_z_deg=0, mat_wood=None, mat_cushion=None, col=None):
    leg_r = 0.016
    leg_h = 0.42
    span_x = 0.36
    span_y = 0.36
    
    rad = math.radians(rot_z_deg)
    cos_r = math.cos(rad)
    sin_r = math.sin(rad)
    
    def transform_pt(lx, ly):
        gx = x + lx * cos_r - ly * sin_r
        gy = y + lx * sin_r + ly * cos_r
        return gx, gy
    
    # 4 Legs
    for idx, (lx, ly) in enumerate([(-span_x/2, -span_y/2), (span_x/2, -span_y/2), (-span_x/2, span_y/2), (span_x/2, span_y/2)]):
        gx, gy = transform_pt(lx, ly)
        create_cylinder(f"{name}_Leg_{idx+1}", gx, gy, z, leg_r, leg_h, mat=mat_wood, col=col)
        
    # Padded Seat Cushion
    seat = create_beveled_box(f"{name}_Seat", x, y, z + leg_h, 0.44, 0.44, 0.05, bevel=0.015, seg=3, mat=mat_cushion, col=col)
    seat.rotation_euler.z = rad
    
    # Backrest Posts
    back_y = span_y / 2
    post_h = 0.36
    p1_gx, p1_gy = transform_pt(-span_x/2 + 0.02, back_y)
    p2_gx, p2_gy = transform_pt(span_x/2 - 0.02, back_y)
    create_cylinder(f"{name}_Post1", p1_gx, p1_gy, z + leg_h, 0.014, post_h, mat=mat_wood, col=col)
    create_cylinder(f"{name}_Post2", p2_gx, p2_gy, z + leg_h, 0.014, post_h, mat=mat_wood, col=col)
    
    # Backrest top curved bar
    back_bar_gx, back_bar_gy = transform_pt(0, back_y)
    bar = create_beveled_box(f"{name}_BackBar", back_bar_gx, back_bar_gy, z + leg_h + post_h - 0.10, 0.44, 0.04, 0.10, bevel=0.015, seg=3, mat=mat_wood, col=col)
    bar.rotation_euler.z = rad

def create_window_unit(name, x, y, z, width, depth, height, panes=2, mat_frame=None, mat_glass=None, col=None):
    frame_th = 0.05
    # Bottom sill
    create_beveled_box(f"{name}_Sill", x, y, z, width, depth + 0.04, frame_th, bevel=0.005, mat=mat_frame, col=col)
    # Top frame
    create_beveled_box(f"{name}_Head", x, y, z + height - frame_th, width, depth, frame_th, bevel=0.005, mat=mat_frame, col=col)
    # Left jamb
    create_beveled_box(f"{name}_JambL", x - width/2 + frame_th/2, y, z + frame_th, frame_th, depth, height - 2*frame_th, bevel=0.005, mat=mat_frame, col=col)
    # Right jamb
    create_beveled_box(f"{name}_JambR", x + width/2 - frame_th/2, y, z + frame_th, frame_th, depth, height - 2*frame_th, bevel=0.005, mat=mat_frame, col=col)
    
    if panes == 1:
        pane_w = width - 2*frame_th
        create_beveled_box(f"{name}_Glass", x, y, z + frame_th + 0.02, pane_w, 0.015, height - 2*frame_th - 0.04, bevel=0.002, mat=mat_glass, col=col)
    elif panes == 2:
        create_beveled_box(f"{name}_Mullion", x, y, z + frame_th, frame_th*0.8, depth*0.9, height - 2*frame_th, bevel=0.004, mat=mat_frame, col=col)
        pane_w = (width - 3*frame_th) / 2
        create_beveled_box(f"{name}_Glass1", x - width/4 + frame_th/4, y, z + frame_th + 0.02, pane_w, 0.015, height - 2*frame_th - 0.04, bevel=0.002, mat=mat_glass, col=col)
        create_beveled_box(f"{name}_Glass2", x + width/4 - frame_th/4, y, z + frame_th + 0.02, pane_w, 0.015, height - 2*frame_th - 0.04, bevel=0.002, mat=mat_glass, col=col)
    elif panes == 3:
        step = (width - 4*frame_th) / 3
        create_beveled_box(f"{name}_Mullion1", x - width/2 + frame_th + step, y, z + frame_th, frame_th*0.8, depth*0.9, height - 2*frame_th, bevel=0.004, mat=mat_frame, col=col)
        create_beveled_box(f"{name}_Mullion2", x + width/2 - frame_th - step, y, z + frame_th, frame_th*0.8, depth*0.9, height - 2*frame_th, bevel=0.004, mat=mat_frame, col=col)
        for i in range(3):
            px = x - width/2 + frame_th + step * (i + 0.5)
            create_beveled_box(f"{name}_Glass_{i+1}", px, y, z + frame_th + 0.02, step - 0.02, 0.015, height - 2*frame_th - 0.04, bevel=0.002, mat=mat_glass, col=col)

def create_interior_door(name, hinge_x, hinge_y, z, width, height, swing_deg=55, mat_door=None, mat_handle=None, col=None):
    door_th = 0.04
    rad = math.radians(swing_deg)
    
    # Door leaf: hinge at local (0, 0), spans [0, width] in local X
    mesh = bpy.data.meshes.new(f"{name}_Leaf_Mesh")
    leaf = bpy.data.objects.new(f"{name}_Leaf", mesh)
    if col:
        col.objects.link(leaf)
    else:
        bpy.context.scene.collection.objects.link(leaf)
        
    x1, x2 = 0.0, width
    y1, y2 = -door_th/2, door_th/2
    z1, z2 = 0.0, height
    verts = [
        (x1, y1, z1), (x2, y1, z1), (x2, y2, z1), (x1, y2, z1),
        (x1, y1, z2), (x2, y1, z2), (x2, y2, z2), (x1, y2, z2)
    ]
    faces = [
        (0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1),
        (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)
    ]
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    
    leaf.location = (hinge_x, hinge_y, z)
    leaf.rotation_euler.z = rad
    
    bev = leaf.modifiers.new("Bevel", 'BEVEL')
    bev.width = 0.006
    bev.segments = 2
    if mat_door:
        leaf.data.materials.append(mat_door)
        
    # Silver Lever Handle at width - 0.08
    hx = hinge_x + (width - 0.08) * math.cos(rad)
    hy = hinge_y + (width - 0.08) * math.sin(rad)
    h_base = create_cylinder(f"{name}_HBase", hx, hy, z + 0.95, 0.025, 0.02, mat=mat_handle, col=col)
    h_base.rotation_euler.y = math.radians(90)
    
    lever = create_beveled_box(f"{name}_HLever", hx + 0.05 * math.cos(rad + math.pi/2), hy + 0.05 * math.sin(rad + math.pi/2), z + 0.94, 0.11, 0.018, 0.015, bevel=0.003, mat=mat_handle, col=col)
    lever.rotation_euler.z = rad

def create_luxury_bed(name, x, y, z, width, length, is_king=True, mat_wood=None, mat_sheet=None, mat_pillow=None, mat_runner=None, col=None):
    return create_luxury_bed_oriented(name, x, y, z, width, length, orientation='W_TO_E', is_king=is_king, mat_wood=mat_wood, mat_sheet=mat_sheet, mat_pillow=mat_pillow, mat_runner=mat_runner, col=col)

def create_luxury_bed_oriented(name, cx, cy, z, width, length, orientation='W_TO_E', is_king=False, mat_wood=None, mat_sheet=None, mat_pillow=None, mat_runner=None, col=None):
    head_h = 1.05
    head_th = 0.12
    
    if orientation == 'W_TO_E':
        create_beveled_box(f"{name}_Headboard", cx - length/2 + head_th/2, cy, z, head_th, width + 0.1, head_h, bevel=0.02, seg=3, mat=mat_wood, col=col)
        create_beveled_box(f"{name}_Base", cx + head_th/2, cy, z, length - head_th, width, 0.30, bevel=0.015, seg=2, mat=mat_wood, col=col)
        create_beveled_box(f"{name}_Mattress", cx + head_th/2 + 0.02, cy, z + 0.28, length - head_th - 0.04, width - 0.04, 0.32, bevel=0.035, seg=4, mat=mat_sheet, col=col)
        duvet_len = (length - head_th) * 0.72
        duvet_cx = cx + head_th/2 + (length - head_th - duvet_len)/2 + 0.15
        create_beveled_box(f"{name}_Duvet", duvet_cx, cy, z + 0.58, duvet_len, width - 0.02, 0.05, bevel=0.025, seg=3, mat=mat_sheet, col=col)
        runner_w = 0.38
        runner_cx = cx + length/2 - runner_w/2 - 0.12
        create_beveled_box(f"{name}_Runner", runner_cx, cy, z + 0.62, runner_w, width + 0.01, 0.015, bevel=0.005, mat=mat_runner, col=col)
        pillow_w = 0.60 if is_king else 0.52
        pillow_l = 0.40
        pillow_h = 0.14
        px = cx - length/2 + head_th + pillow_l/2 + 0.06
        if is_king:
            create_beveled_box(f"{name}_Pillow1", px, cy - width/4, z + 0.60, pillow_l, pillow_w, pillow_h, bevel=0.05, seg=4, mat=mat_pillow, col=col)
            create_beveled_box(f"{name}_Pillow2", px, cy + width/4, z + 0.60, pillow_l, pillow_w, pillow_h, bevel=0.05, seg=4, mat=mat_pillow, col=col)
        else:
            create_beveled_box(f"{name}_Pillow", px, cy, z + 0.60, pillow_l, pillow_w, pillow_h, bevel=0.05, seg=4, mat=mat_pillow, col=col)

    elif orientation == 'N_TO_S':
        create_beveled_box(f"{name}_Headboard", cx, cy + length/2 - head_th/2, z, width + 0.1, head_th, head_h, bevel=0.02, seg=3, mat=mat_wood, col=col)
        create_beveled_box(f"{name}_Base", cx, cy - head_th/2, z, width, length - head_th, 0.30, bevel=0.015, seg=2, mat=mat_wood, col=col)
        create_beveled_box(f"{name}_Mattress", cx, cy - head_th/2 - 0.02, z + 0.28, width - 0.04, length - head_th - 0.04, 0.32, bevel=0.035, seg=4, mat=mat_sheet, col=col)
        duvet_len = (length - head_th) * 0.72
        duvet_cy = cy - head_th/2 - (length - head_th - duvet_len)/2 - 0.15
        create_beveled_box(f"{name}_Duvet", cx, duvet_cy, z + 0.58, width - 0.02, duvet_len, 0.05, bevel=0.025, seg=3, mat=mat_sheet, col=col)
        runner_w = 0.38
        runner_cy = cy - length/2 + runner_w/2 + 0.12
        create_beveled_box(f"{name}_Runner", cx, runner_cy, z + 0.62, width + 0.01, runner_w, 0.015, bevel=0.005, mat=mat_runner, col=col)
        pillow_w = 0.55
        pillow_l = 0.40
        py = cy + length/2 - head_th - pillow_l/2 - 0.06
        create_beveled_box(f"{name}_Pillow", cx, py, z + 0.60, pillow_w, pillow_l, 0.14, bevel=0.05, seg=4, mat=mat_pillow, col=col)

    elif orientation == 'E_TO_W':
        create_beveled_box(f"{name}_Headboard", cx + length/2 - head_th/2, cy, z, head_th, width + 0.1, head_h, bevel=0.02, seg=3, mat=mat_wood, col=col)
        create_beveled_box(f"{name}_Base", cx - head_th/2, cy, z, length - head_th, width, 0.30, bevel=0.015, seg=2, mat=mat_wood, col=col)
        create_beveled_box(f"{name}_Mattress", cx - head_th/2 - 0.02, cy, z + 0.28, length - head_th - 0.04, width - 0.04, 0.32, bevel=0.035, seg=4, mat=mat_sheet, col=col)
        duvet_len = (length - head_th) * 0.72
        duvet_cx = cx - head_th/2 - (length - head_th - duvet_len)/2 - 0.15
        create_beveled_box(f"{name}_Duvet", duvet_cx, cy, z + 0.58, duvet_len, width - 0.02, 0.05, bevel=0.025, seg=3, mat=mat_sheet, col=col)
        runner_w = 0.38
        runner_cx = cx - length/2 + runner_w/2 + 0.12
        create_beveled_box(f"{name}_Runner", runner_cx, cy, z + 0.62, runner_w, width + 0.01, 0.015, bevel=0.005, mat=mat_runner, col=col)
        pillow_w = 0.55
        pillow_l = 0.40
        px = cx + length/2 - head_th - pillow_l/2 - 0.06
        create_beveled_box(f"{name}_Pillow", px, cy, z + 0.60, pillow_l, pillow_w, 0.14, bevel=0.05, seg=4, mat=mat_pillow, col=col)

def create_luxury_sofa(name, x, y, z, length, depth, mat_fabric=None, mat_cushion=None, col=None):
    back_th = 0.22
    arm_w = 0.22
    arm_h = 0.64
    
    # Base frame
    create_beveled_box(f"{name}_Base", x, y, z, depth, length, 0.15, bevel=0.01, mat=mat_fabric, col=col)
    
    # 3 Seat Cushions
    cushion_len = (length - 2*arm_w) / 3
    for i in range(3):
        cy = y - (length - 2*arm_w)/2 + cushion_len * (i + 0.5)
        create_beveled_box(f"{name}_Seat_{i+1}", x - back_th/4, cy, z + 0.15, depth - back_th - 0.04, cushion_len - 0.02, 0.28, bevel=0.04, seg=4, mat=mat_fabric, col=col)
        
    # Backrest Main Bar
    create_beveled_box(f"{name}_BackBar", x + depth/2 - back_th/2, y, z + 0.15, back_th, length, 0.48, bevel=0.03, seg=3, mat=mat_fabric, col=col)
    
    # 3 Backrest Pillows
    for i in range(3):
        cy = y - (length - 2*arm_w)/2 + cushion_len * (i + 0.5)
        create_beveled_box(f"{name}_BackCushion_{i+1}", x + depth/2 - back_th - 0.06, cy, z + 0.42, 0.16, cushion_len - 0.04, 0.38, bevel=0.04, seg=4, mat=mat_fabric, col=col)
        
    # Left & Right Armrests
    create_beveled_box(f"{name}_ArmL", x, y - length/2 + arm_w/2, z, depth, arm_w, arm_h, bevel=0.04, seg=3, mat=mat_fabric, col=col)
    create_beveled_box(f"{name}_ArmR", x, y + length/2 - arm_w/2, z, depth, arm_w, arm_h, bevel=0.04, seg=3, mat=mat_fabric, col=col)
    
    # 2 Decorative Throw Cushions
    create_beveled_box(f"{name}_Throw1", x, y - length/2 + arm_w + 0.18, z + 0.42, 0.14, 0.36, 0.36, bevel=0.04, seg=3, mat=mat_cushion, col=col)
    create_beveled_box(f"{name}_Throw2", x, y + length/2 - arm_w - 0.18, z + 0.42, 0.14, 0.36, 0.36, bevel=0.04, seg=3, mat=mat_cushion, col=col)

def create_sink_and_faucet(name, x, y, z, mat_sink=None, mat_chrome=None, col=None):
    # Stainless double undermount sink basin
    create_beveled_box(f"{name}_BasinRim", x, y, z, 0.82, 0.48, 0.02, bevel=0.005, mat=mat_sink, col=col)
    create_beveled_box(f"{name}_Bowl1", x - 0.20, y, z - 0.18, 0.36, 0.40, 0.18, bevel=0.02, mat=mat_sink, col=col)
    create_beveled_box(f"{name}_Bowl2", x + 0.20, y, z - 0.18, 0.36, 0.40, 0.18, bevel=0.02, mat=mat_sink, col=col)
    
    # Chrome Gooseneck Faucet
    create_cylinder(f"{name}_FaucetBase", x, y + 0.18, z + 0.02, 0.025, 0.05, mat=mat_chrome, col=col)
    create_cylinder(f"{name}_FaucetNeck", x, y + 0.18, z + 0.07, 0.014, 0.26, mat=mat_chrome, col=col)
    create_beveled_box(f"{name}_FaucetSpoutH", x, y + 0.10, z + 0.32, 0.024, 0.18, 0.024, bevel=0.005, mat=mat_chrome, col=col)
    create_cylinder(f"{name}_FaucetTip", x, y + 0.02, z + 0.25, 0.012, 0.07, mat=mat_chrome, col=col)
    create_cylinder(f"{name}_FaucetLever", x + 0.04, y + 0.18, z + 0.12, 0.008, 0.08, mat=mat_chrome, col=col)

def create_bathtub(name, x, y, z, length=1.50, width=0.75, height=0.55, mat_ceramic=None, mat_chrome=None, col=None):
    create_beveled_box(f"{name}_Shell", x, y, z, length, width, height, bevel=0.03, seg=3, mat=mat_ceramic, col=col)
    create_beveled_box(f"{name}_InnerBasin", x, y, z + 0.05, length - 0.16, width - 0.16, height - 0.04, bevel=0.06, seg=4, mat=mat_ceramic, col=col)
    create_cylinder(f"{name}_Tap", x + length/2 - 0.10, y, z + height, 0.02, 0.10, mat=mat_chrome, col=col)
    create_beveled_box(f"{name}_Spout", x + length/2 - 0.18, y, z + height + 0.08, 0.15, 0.03, 0.025, bevel=0.005, mat=mat_chrome, col=col)

def create_toilet(name, x, y, z, rot_z_deg=0, mat_ceramic=None, col=None):
    rad = math.radians(rot_z_deg)
    tank = create_beveled_box(f"{name}_Tank", x, y + 0.20, z, 0.42, 0.20, 0.75, bevel=0.025, seg=3, mat=mat_ceramic, col=col)
    bowl = create_beveled_box(f"{name}_Bowl", x, y - 0.10, z, 0.38, 0.44, 0.40, bevel=0.04, seg=4, mat=mat_ceramic, col=col)
    lid  = create_beveled_box(f"{name}_Lid",  x, y - 0.08, z + 0.40, 0.37, 0.42, 0.03, bevel=0.015, seg=2, mat=mat_ceramic, col=col)
    for o in [tank, bowl, lid]:
        o.rotation_euler.z = rad

def create_wall_tv(name, x, y, z, width=1.65, height=0.95, mat_frame=None, mat_screen=None, col=None):
    # Slim OLED TV mounted on wall
    th = 0.03
    bezel = 0.012
    create_beveled_box(f"{name}_Frame", x, y, z, th, width, height, bevel=0.003, seg=2, mat=mat_frame, col=col)
    create_beveled_box(f"{name}_Screen", x + 0.008, y, z + bezel, 0.005, width - 2*bezel, height - 2*bezel, bevel=0.001, seg=1, mat=mat_screen, col=col)

def create_fridge_cabinet(name, x, y, z, width=2.0, depth=0.70, height=2.25, mat_cab=None, mat_fridge=None, col=None):
    # Tall refrigerator cabinet housing (West kitchen wall)
    create_beveled_box(f"{name}_Surround", x, y, z, depth, width, height, bevel=0.01, seg=2, mat=mat_cab, col=col)
    
    # 4-Door Bespoke Fridge front panels (slightly recessed or flush)
    fridge_w = 1.05
    door_w = fridge_w / 2 - 0.01
    top_h = 1.05
    bot_h = 0.75
    fx = x + depth/2 + 0.01
    fy = y - (width - fridge_w)/2 + 0.10
    
    # Upper left & right doors
    create_beveled_box(f"{name}_Door_TL", fx, fy - door_w/2 - 0.005, z + bot_h + 0.05, 0.03, door_w, top_h, bevel=0.008, seg=2, mat=mat_fridge, col=col)
    create_beveled_box(f"{name}_Door_TR", fx, fy + door_w/2 + 0.005, z + bot_h + 0.05, 0.03, door_w, top_h, bevel=0.008, seg=2, mat=mat_fridge, col=col)
    # Lower left & right doors
    create_beveled_box(f"{name}_Door_BL", fx, fy - door_w/2 - 0.005, z + 0.05, 0.03, door_w, bot_h, bevel=0.008, seg=2, mat=mat_fridge, col=col)
    create_beveled_box(f"{name}_Door_BR", fx, fy + door_w/2 + 0.005, z + 0.05, 0.03, door_w, bot_h, bevel=0.008, seg=2, mat=mat_fridge, col=col)
    
    # Tall pantry cabinet door on the other side
    pantry_w = width - fridge_w - 0.15
    py = y + (width - pantry_w)/2 - 0.05
    create_beveled_box(f"{name}_Pantry_Door", fx, py, z + 0.05, 0.02, pantry_w, height - 0.10, bevel=0.008, seg=2, mat=mat_cab, col=col)

def create_upper_cabinets(name, x, y, z, sx, sy, sz, mat_cab=None, mat_led=None, col=None):
    # Upper cabinet box
    create_beveled_box(f"{name}_Box", x, y, z, sx, sy, sz, bevel=0.01, seg=2, mat=mat_cab, col=col)
    # Under-cabinet warm LED light strip
    if mat_led:
        create_beveled_box(f"{name}_LED_Strip", x, y, z - 0.015, sx * 0.95, sy * 0.85, 0.015, bevel=0.002, seg=1, mat=mat_led, col=col)

def create_range_hood(name, x, y, z, sx=0.55, sy=0.85, sz=0.45, mat_hood=None, col=None):
    # Modern chimney/canopy range hood
    create_beveled_box(f"{name}_Canopy", x, y, z, sx, sy, 0.08, bevel=0.01, seg=2, mat=mat_hood, col=col)
    create_beveled_box(f"{name}_Chimney", x, y, z + 0.08, sx * 0.6, sy * 0.5, sz - 0.08, bevel=0.005, seg=2, mat=mat_hood, col=col)

def create_curtain(name, x, y, z, width, height, mat_curtain=None, col=None):
    # Drapes on both sides of South window (aligned with X axis)
    panel_w = width * 0.18
    th = 0.08
    create_beveled_box(f"{name}_Left",  x - width/2 + panel_w/2, y, z, panel_w, th, height, bevel=0.03, seg=3, mat=mat_curtain, col=col)
    create_beveled_box(f"{name}_Right", x + width/2 - panel_w/2, y, z, panel_w, th, height, bevel=0.03, seg=3, mat=mat_curtain, col=col)


def create_nightstand(name, x, y, z, mat_wood=None, mat_lamp=None, col=None):
    create_beveled_box(f"{name}_Cab", x, y, z, 0.45, 0.45, 0.48, bevel=0.02, seg=2, mat=mat_wood, col=col)
    create_cylinder(f"{name}_LampBase", x, y, z + 0.48, 0.09, 0.02, mat=mat_lamp, col=col)
    create_cylinder(f"{name}_LampPole", x, y, z + 0.50, 0.012, 0.22, mat=mat_lamp, col=col)
    create_cylinder(f"{name}_LampShade", x, y, z + 0.65, 0.12, 0.14, mat=mat_wood, col=col)

def create_sphere(name, x, y, z, r, mat=None, col=None, seg=20, rings=12):
    """UV sphere centered at (x, y, z)."""
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    if col:
        col.objects.link(obj)
    else:
        bpy.context.scene.collection.objects.link(obj)

    verts = []
    for j in range(rings + 1):
        phi = math.pi * j / rings
        sp, cp = math.sin(phi), math.cos(phi)
        for i in range(seg):
            theta = 2 * math.pi * i / seg
            verts.append((r * sp * math.cos(theta), r * sp * math.sin(theta), r * cp))
    faces = []
    for j in range(rings):
        for i in range(seg):
            a = j * seg + i
            b = j * seg + (i + 1) % seg
            c = (j + 1) * seg + (i + 1) % seg
            d = (j + 1) * seg + i
            if j == 0:
                faces.append((b, c, d))
            elif j == rings - 1:
                faces.append((a, b, d))
            else:
                faces.append((a, b, c, d))
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj.location = (x, y, z)
    for poly in mesh.polygons:
        poly.use_smooth = True
    if mat:
        obj.data.materials.append(mat)
    return obj


def create_cone_shade(name, x, y, z_base, r_bottom, r_top, h, mat=None, col=None, seg=24):
    """Open-bottom cone/lampshade shell, base ring at z_base, opening faces down."""
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    if col:
        col.objects.link(obj)
    else:
        bpy.context.scene.collection.objects.link(obj)

    verts = []
    for i in range(seg):
        theta = 2 * math.pi * i / seg
        verts.append((r_bottom * math.cos(theta), r_bottom * math.sin(theta), 0.0))
    for i in range(seg):
        theta = 2 * math.pi * i / seg
        verts.append((r_top * math.cos(theta), r_top * math.sin(theta), h))
    cx_top = len(verts)
    verts.append((0.0, 0.0, h))
    faces = []
    for i in range(seg):
        ni = (i + 1) % seg
        faces.append((i, ni, ni + seg, i + seg))
        faces.append((cx_top, ni + seg, i + seg))
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj.location = (x, y, z_base)
    for poly in mesh.polygons:
        poly.use_smooth = True
    if mat:
        obj.data.materials.append(mat)
    return obj


def create_pendant_light(name, x, y, z_ceiling, shade_bottom_z, shade_r=0.14, shade_h=0.20,
                         mat_shade=None, mat_bulb=None, mat_cord=None, col=None,
                         add_light=True, energy=20.0):
    """Hanging pendant: ceiling cord + cone shade + bulb + optional real point light."""
    cord_top, cord_bot = z_ceiling, shade_bottom_z + shade_h
    cord_h = max(0.05, cord_top - cord_bot)
    create_cylinder(f"{name}_Cord", x, y, cord_bot, 0.006, cord_h, seg=8, mat=mat_cord, col=col)
    create_cylinder(f"{name}_Canopy", x, y, z_ceiling - 0.025, 0.035, 0.025, seg=12, mat=mat_cord, col=col)
    create_cone_shade(f"{name}_Shade", x, y, shade_bottom_z, shade_r, shade_r * 0.35, shade_h,
                      mat=mat_shade, col=col)
    create_sphere(f"{name}_Bulb", x, y, shade_bottom_z + 0.03, 0.028, mat=mat_bulb, col=col)
    if add_light:
        lcol = bpy.data.collections.get("Apt_Lighting")
        ld = bpy.data.lights.get(name) or bpy.data.lights.new(name, 'POINT')
        ld.energy = energy
        ld.color = (1.0, 0.88, 0.74)
        ld.shadow_soft_size = 0.06
        lo = bpy.data.objects.get(name) or bpy.data.objects.new(name, ld)
        if lcol and lo.name not in lcol.objects:
            lcol.objects.link(lo)
        elif not lcol and col:
            col.objects.link(lo)
        lo.location = (x, y, shade_bottom_z - 0.02)


def create_place_setting(name, x, y, z_top, mat_mat=None, mat_plate=None, mat_glass=None, col=None):
    """Dining place setting: woven mat + ceramic plate + drinking glass."""
    create_beveled_box(f"{name}_Mat", x, y, z_top, 0.34, 0.26, 0.006, bevel=0.002, seg=1, mat=mat_mat, col=col)
    create_cylinder(f"{name}_Plate", x, y, z_top + 0.006, 0.115, 0.018, seg=24, mat=mat_plate, col=col)
    create_cylinder(f"{name}_Bowl", x, y, z_top + 0.024, 0.055, 0.035, seg=20, mat=mat_plate, col=col)
    create_cylinder(f"{name}_Glass", x + 0.10, y + 0.07, z_top + 0.006, 0.032, 0.085, seg=16, mat=mat_glass, col=col)


def create_table_vase(name, x, y, z_top, mat_vase=None, mat_stem=None, mat_plume=None, col=None):
    """Small ceramic vase with dried stems as dining centerpiece."""
    create_cylinder(f"{name}_Body", x, y, z_top, 0.045, 0.16, seg=16, mat=mat_vase, col=col)
    create_cylinder(f"{name}_Neck", x, y, z_top + 0.16, 0.022, 0.06, seg=12, mat=mat_vase, col=col)
    for i, (dx, dy, tilt) in enumerate([(-0.02, 0.0, 0.10), (0.02, 0.01, -0.08), (0.0, -0.02, 0.05)]):
        stem = create_cylinder(f"{name}_Stem{i+1}", x + dx, y + dy, z_top + 0.20, 0.003, 0.30, seg=6, mat=mat_stem, col=col)
        stem.rotation_euler.y = tilt
        create_sphere(f"{name}_Plume{i+1}", x + dx - tilt * 0.28, y + dy, z_top + 0.52, 0.022, mat=mat_plume, col=col, seg=10, rings=6)


def create_pot(name, x, y, z_top, r=0.13, h=0.12, mat_steel=None, mat_handle=None, col=None):
    """Stock pot with lid on cooktop surface at z_top."""
    create_cylinder(f"{name}_Body", x, y, z_top, r, h, seg=24, mat=mat_steel, col=col)
    create_cylinder(f"{name}_Lid", x, y, z_top + h, r + 0.005, 0.015, seg=24, mat=mat_steel, col=col)
    create_sphere(f"{name}_Knob", x, y, z_top + h + 0.025, 0.018, mat=mat_handle, col=col, seg=12, rings=8)
    create_beveled_box(f"{name}_HandleL", x - r - 0.015, y, z_top + h * 0.55, 0.05, 0.03, 0.02, bevel=0.005, mat=mat_handle, col=col)
    create_beveled_box(f"{name}_HandleR", x + r + 0.015, y, z_top + h * 0.55, 0.05, 0.03, 0.02, bevel=0.005, mat=mat_handle, col=col)


def create_kettle(name, x, y, z_top, r=0.085, h=0.16, mat_steel=None, mat_handle=None, col=None):
    """Stovetop kettle with spout and arch handle."""
    create_cylinder(f"{name}_Body", x, y, z_top, r, h, seg=20, mat=mat_steel, col=col)
    create_cylinder(f"{name}_Lid", x, y, z_top + h, r * 0.55, 0.02, seg=16, mat=mat_handle, col=col)
    spout = create_cylinder(f"{name}_Spout", x + r * 0.9, y, z_top + h * 0.45, 0.018, 0.12, seg=10, mat=mat_steel, col=col)
    spout.rotation_euler.y = math.radians(-35)
    post1 = create_cylinder(f"{name}_PostL", x, y - r * 0.7, z_top + h, 0.008, 0.09, seg=8, mat=mat_handle, col=col)
    post2 = create_cylinder(f"{name}_PostR", x, y + r * 0.7, z_top + h, 0.008, 0.09, seg=8, mat=mat_handle, col=col)
    create_beveled_box(f"{name}_Grip", x, y, z_top + h + 0.085, 0.025, r * 1.4 + 0.03, 0.02, bevel=0.006, mat=mat_handle, col=col)


def create_cutting_board(name, x, y, z_top, lean_deg=12, mat=None, col=None):
    """Wooden cutting board leaning against backsplash."""
    board = create_beveled_box(name, x, y, z_top, 0.30, 0.025, 0.42, bevel=0.008, seg=2, mat=mat, col=col)
    board.rotation_euler.x = math.radians(-lean_deg)
    return board


def create_dish_rack(name, x, y, z_top, mat_tray=None, mat_plate=None, col=None):
    """Countertop dish drying rack with vertical plates."""
    create_beveled_box(f"{name}_Tray", x, y, z_top, 0.42, 0.30, 0.03, bevel=0.008, mat=mat_tray, col=col)
    for i in range(3):
        plate = create_cylinder(f"{name}_Plate{i+1}", x - 0.12 + i * 0.09, y, z_top + 0.03, 0.10, 0.012, seg=20, mat=mat_plate, col=col)
        plate.rotation_euler.x = math.radians(90)
        plate.location.z = z_top + 0.13
    create_cylinder(f"{name}_Cup1", x + 0.13, y + 0.06, z_top + 0.03, 0.035, 0.07, seg=14, mat=mat_plate, col=col)
    create_cylinder(f"{name}_Cup2", x + 0.13, y - 0.06, z_top + 0.03, 0.035, 0.07, seg=14, mat=mat_plate, col=col)


def create_fruit_bowl(name, x, y, z_top, mat_bowl=None, mat_fruit=None, col=None):
    """Low wooden bowl with oranges on peninsula counter."""
    create_cylinder(f"{name}_Base", x, y, z_top, 0.07, 0.02, seg=16, mat=mat_bowl, col=col)
    create_cylinder(f"{name}_Bowl", x, y, z_top + 0.02, 0.14, 0.05, seg=20, mat=mat_bowl, col=col)
    for i, (dx, dy, dz) in enumerate([(-0.05, 0.03, 0.09), (0.05, -0.02, 0.09), (0.0, 0.05, 0.085), (0.01, -0.01, 0.15)]):
        create_sphere(f"{name}_Fruit{i+1}", x + dx, y + dy, z_top + dz, 0.038, mat=mat_fruit, col=col, seg=14, rings=10)


def create_gallery_frame(name, x, y, z_center, w, h, facing='-x', mat_frame=None, mat_canvas=None, mat_accent=None, col=None):
    """Wall-mounted art frame with abstract accent bars. facing: '-x' means art faces -X."""
    th = 0.035
    if facing in ('-x', '+x'):
        s = -1 if facing == '-x' else 1
        create_beveled_box(f"{name}_Frame", x, y, z_center - h / 2, th, w, h, bevel=0.005, mat=mat_frame, col=col)
        create_beveled_box(f"{name}_Canvas", x + s * (th / 2), y, z_center - h / 2 + 0.03, 0.008, w - 0.06, h - 0.06, bevel=0.002, seg=1, mat=mat_canvas, col=col)
        if mat_accent:
            create_beveled_box(f"{name}_Bar1", x + s * (th / 2 + 0.006), y - w * 0.14, z_center - 0.02, 0.006, w * 0.30, 0.045, bevel=0.002, seg=1, mat=mat_accent, col=col)
            create_beveled_box(f"{name}_Bar2", x + s * (th / 2 + 0.006), y + w * 0.16, z_center + h * 0.10, 0.006, w * 0.18, 0.10, bevel=0.002, seg=1, mat=mat_accent, col=col)
    else:
        s = -1 if facing == '-y' else 1
        create_beveled_box(f"{name}_Frame", x, y, z_center - h / 2, w, th, h, bevel=0.005, mat=mat_frame, col=col)
        create_beveled_box(f"{name}_Canvas", x, y + s * (th / 2), z_center - h / 2 + 0.03, w - 0.06, 0.008, h - 0.06, bevel=0.002, seg=1, mat=mat_canvas, col=col)
        if mat_accent:
            create_beveled_box(f"{name}_Bar1", x - w * 0.14, y + s * (th / 2 + 0.006), z_center - 0.02, w * 0.30, 0.006, 0.045, bevel=0.002, seg=1, mat=mat_accent, col=col)


def create_wall_pad(name, x, y, z_center, facing='-x', mat_body=None, mat_screen=None, mat_switch=None, col=None):
    """Smart wall pad (intercom + thermostat look) with a 2-gang light switch beside it."""
    if facing in ('-x', '+x'):
        s = -1 if facing == '-x' else 1
        create_beveled_box(f"{name}_Body", x, y, z_center - 0.14, 0.025, 0.20, 0.28, bevel=0.006, mat=mat_body, col=col)
        create_beveled_box(f"{name}_Screen", x + s * 0.012, y, z_center - 0.10, 0.006, 0.16, 0.20, bevel=0.002, seg=1, mat=mat_screen, col=col)
        create_beveled_box(f"{name}_Switch", x, y + 0.22, z_center - 0.06, 0.015, 0.075, 0.12, bevel=0.004, mat=mat_switch, col=col)
        create_beveled_box(f"{name}_Toggle1", x + s * 0.008, y + 0.20, z_center - 0.045, 0.006, 0.028, 0.045, bevel=0.002, seg=1, mat=mat_switch, col=col)
        create_beveled_box(f"{name}_Toggle2", x + s * 0.008, y + 0.24, z_center - 0.045, 0.006, 0.028, 0.045, bevel=0.002, seg=1, mat=mat_switch, col=col)
    else:
        s = -1 if facing == '-y' else 1
        create_beveled_box(f"{name}_Body", x, y, z_center - 0.14, 0.20, 0.025, 0.28, bevel=0.006, mat=mat_body, col=col)
        create_beveled_box(f"{name}_Screen", x, y + s * 0.010, z_center - 0.10, 0.16, 0.006, 0.20, bevel=0.002, seg=1, mat=mat_screen, col=col)
        create_beveled_box(f"{name}_Switch", x + 0.22, y, z_center - 0.06, 0.075, 0.015, 0.12, bevel=0.004, mat=mat_switch, col=col)


def create_cove_molding(name, x1, x2, y1, y2, z_ceil_bottom, trim_w=0.10, trim_h=0.055, mat_trim=None, mat_led=None, col=None):
    """Rectangular recessed-cove trim ring hung just below ceiling with inner LED line."""
    zt = z_ceil_bottom - trim_h
    create_beveled_box(f"{name}_TrimS", (x1 + x2) / 2, y1 + trim_w / 2, zt, x2 - x1, trim_w, trim_h, bevel=0.004, mat=mat_trim, col=col)
    create_beveled_box(f"{name}_TrimN", (x1 + x2) / 2, y2 - trim_w / 2, zt, x2 - x1, trim_w, trim_h, bevel=0.004, mat=mat_trim, col=col)
    create_beveled_box(f"{name}_TrimW", x1 + trim_w / 2, (y1 + y2) / 2, zt, trim_w, y2 - y1 - 2 * trim_w, trim_h, bevel=0.004, mat=mat_trim, col=col)
    create_beveled_box(f"{name}_TrimE", x2 - trim_w / 2, (y1 + y2) / 2, zt, trim_w, y2 - y1 - 2 * trim_w, trim_h, bevel=0.004, mat=mat_trim, col=col)
    if mat_led:
        lw, eps = 0.030, 0.004
        zl = z_ceil_bottom - 0.012
        create_beveled_box(f"{name}_LEDS", (x1 + x2) / 2, y1 + trim_w + lw / 2 + eps, zl, x2 - x1 - 2 * trim_w, lw, 0.012, bevel=0.001, seg=1, mat=mat_led, col=col)
        create_beveled_box(f"{name}_LEDN", (x1 + x2) / 2, y2 - trim_w - lw / 2 - eps, zl, x2 - x1 - 2 * trim_w, lw, 0.012, bevel=0.001, seg=1, mat=mat_led, col=col)
        create_beveled_box(f"{name}_LEDW", x1 + trim_w + lw / 2 + eps, (y1 + y2) / 2, zl, lw, y2 - y1 - 2 * trim_w, 0.012, bevel=0.001, seg=1, mat=mat_led, col=col)
        create_beveled_box(f"{name}_LEDE", x2 - trim_w - lw / 2 - eps, (y1 + y2) / 2, zl, lw, y2 - y1 - 2 * trim_w, 0.012, bevel=0.001, seg=1, mat=mat_led, col=col)


def create_ac_outdoor_unit(name, x, y, z, facing='-y', mat_body=None, mat_grill=None, mat_pipe=None, col=None):
    """AC condenser unit with fan grill and refrigerant pipes."""
    w, d, h = 0.90, 0.34, 0.72
    if facing in ('-y', '+y'):
        create_beveled_box(f"{name}_Body", x, y, z + 0.06, w, d, h, bevel=0.012, seg=2, mat=mat_body, col=col)
        s = -1 if facing == '-y' else 1
        fan = create_cylinder(f"{name}_Fan", x, y + s * (d / 2 + 0.005), z + 0.06 + h / 2, 0.24, 0.015, seg=24, mat=mat_grill, col=col)
        fan.rotation_euler.x = math.radians(90 if s < 0 else -90)
        for i in range(3):
            create_beveled_box(f"{name}_Slat{i+1}", x, y + s * (d / 2 + 0.012), z + 0.22 + i * 0.14, w * 0.86, 0.012, 0.02, bevel=0.003, seg=1, mat=mat_grill, col=col)
        create_cylinder(f"{name}_Pipe1", x + w / 2 - 0.10, y - s * d / 2, z + 0.06, 0.022, h + 0.5, seg=10, mat=mat_pipe, col=col)
        create_cylinder(f"{name}_Pipe2", x + w / 2 - 0.04, y - s * d / 2, z + 0.06, 0.016, h + 0.5, seg=10, mat=mat_pipe, col=col)
        create_beveled_box(f"{name}_FootL", x - w / 2 + 0.08, y, z, 0.10, d + 0.04, 0.06, bevel=0.005, mat=mat_grill, col=col)
        create_beveled_box(f"{name}_FootR", x + w / 2 - 0.08, y, z, 0.10, d + 0.04, 0.06, bevel=0.005, mat=mat_grill, col=col)
    else:
        create_beveled_box(f"{name}_Body", x, y, z + 0.06, d, w, h, bevel=0.012, seg=2, mat=mat_body, col=col)
        s = -1 if facing == '-x' else 1
        fan = create_cylinder(f"{name}_Fan", x + s * (d / 2 + 0.005), y, z + 0.06 + h / 2, 0.24, 0.015, seg=24, mat=mat_grill, col=col)
        fan.rotation_euler.y = math.radians(-90 if s < 0 else 90)


def create_louver_door(name, x, y, z, w, h, facing='-x', mat=None, col=None):
    """Ventilated louver door slab for AC/utility room."""
    th = 0.045
    if facing in ('-x', '+x'):
        create_beveled_box(f"{name}_Slab", x, y, z, th, w, h, bevel=0.005, mat=mat, col=col)
        for i in range(9):
            slat = create_beveled_box(f"{name}_Slat{i+1}", x, y, z + h * 0.24 + i * (h * 0.52 / 8), th + 0.014, w - 0.16, 0.045, bevel=0.003, seg=1, mat=mat, col=col)
            slat.rotation_euler.y = math.radians(30)
    else:
        create_beveled_box(f"{name}_Slab", x, y, z, w, th, h, bevel=0.005, mat=mat, col=col)
        for i in range(9):
            slat = create_beveled_box(f"{name}_Slat{i+1}", x, y, z + h * 0.24 + i * (h * 0.52 / 8), w - 0.16, th + 0.014, 0.045, bevel=0.003, seg=1, mat=mat, col=col)
            slat.rotation_euler.x = math.radians(30)


def create_refuge_door(name, x, y, z, facing='+x', mat_door=None, mat_sign=None, col=None):
    """Balcony evacuation/refuge area door with exit sign plate."""
    w, h, th = 0.95, 2.0, 0.05
    if facing in ('-x', '+x'):
        s = -1 if facing == '-x' else 1
        create_beveled_box(f"{name}_Panel", x, y, z, th, w, h, bevel=0.006, mat=mat_door, col=col)
        create_beveled_box(f"{name}_Sign", x + s * 0.030, y, z + h - 0.35, 0.012, 0.30, 0.12, bevel=0.003, seg=1, mat=mat_sign, col=col)
        create_beveled_box(f"{name}_Kick", x + s * 0.028, y, z + 0.02, 0.010, w - 0.1, 0.18, bevel=0.003, seg=1, mat=mat_door, col=col)
    else:
        s = -1 if facing == '-y' else 1
        create_beveled_box(f"{name}_Panel", x, y, z, w, th, h, bevel=0.006, mat=mat_door, col=col)
        create_beveled_box(f"{name}_Sign", x, y + s * 0.030, z + h - 0.35, 0.30, 0.012, 0.12, bevel=0.003, seg=1, mat=mat_sign, col=col)


def create_wardrobe(name, x_center, y_back, z, width, depth, height, facing='-y', mat_cab=None, mat_handle=None, col=None):
    """Floor-to-near-ceiling built-in wardrobe with sliding doors. y_back = wall-side back face."""
    s = -1 if facing == '-y' else 1
    yc = y_back + s * depth / 2
    create_beveled_box(f"{name}_Carcass", x_center, yc, z + 0.06, width, depth, height - 0.06, bevel=0.008, mat=mat_cab, col=col)
    create_beveled_box(f"{name}_Plinth", x_center, yc, z, width - 0.04, depth - 0.06, 0.06, bevel=0.004, mat=mat_cab, col=col)
    door_y = yc + s * (depth / 2 + 0.008)
    dw = width / 2 - 0.008
    create_beveled_box(f"{name}_DoorL", x_center - width / 4, door_y, z + 0.06, dw, 0.018, height - 0.10, bevel=0.004, mat=mat_cab, col=col)
    create_beveled_box(f"{name}_DoorR", x_center + width / 4, door_y + s * 0.020, z + 0.06, dw, 0.018, height - 0.10, bevel=0.004, mat=mat_cab, col=col)
    create_beveled_box(f"{name}_HandleL", x_center - 0.03, door_y + s * 0.022, z + 0.75, 0.025, 0.025, 0.55, bevel=0.006, mat=mat_handle, col=col)
    create_beveled_box(f"{name}_HandleR", x_center + 0.03, door_y + s * 0.042, z + 0.75, 0.025, 0.025, 0.55, bevel=0.006, mat=mat_handle, col=col)


def create_desk(name, x, y, z, w, d, h=0.73, mat_top=None, mat_leg=None, col=None):
    """Simple home-office desk with side panel legs."""
    create_beveled_box(f"{name}_Top", x, y, z + h, w, d, 0.035, bevel=0.008, seg=2, mat=mat_top, col=col)
    create_beveled_box(f"{name}_LegL", x - w / 2 + 0.025, y, z, 0.05, d - 0.06, h, bevel=0.005, mat=mat_leg, col=col)
    create_beveled_box(f"{name}_LegR", x + w / 2 - 0.025, y, z, 0.05, d - 0.06, h, bevel=0.005, mat=mat_leg, col=col)
    create_beveled_box(f"{name}_Modesty", x, y + d / 2 - 0.04, z + 0.25, w - 0.1, 0.025, 0.38, bevel=0.004, mat=mat_leg, col=col)


def create_office_chair(name, x, y, z, rot_z_deg=180, mat_seat=None, mat_frame=None, col=None):
    """Task chair: 5-star base suggestion, gas lift, seat and backrest."""
    rad = math.radians(rot_z_deg)
    for i in range(5):
        a = rad + 2 * math.pi * i / 5
        fx, fy = x + 0.26 * math.cos(a), y + 0.26 * math.sin(a)
        foot = create_beveled_box(f"{name}_Foot{i+1}", (x + fx) / 2, (y + fy) / 2, z + 0.02, 0.28, 0.045, 0.03, bevel=0.01, mat=mat_frame, col=col)
        foot.rotation_euler.z = a
        create_sphere(f"{name}_Caster{i+1}", fx, fy, z + 0.03, 0.028, mat=mat_frame, col=col, seg=10, rings=8)
    create_cylinder(f"{name}_Lift", x, y, z + 0.05, 0.025, 0.35, seg=12, mat=mat_frame, col=col)
    seat = create_beveled_box(f"{name}_Seat", x, y, z + 0.40, 0.46, 0.44, 0.07, bevel=0.025, seg=3, mat=mat_seat, col=col)
    seat.rotation_euler.z = rad
    bx = x - 0.24 * math.cos(rad)
    by = y - 0.24 * math.sin(rad)
    back = create_beveled_box(f"{name}_Back", bx, by, z + 0.55, 0.09, 0.44, 0.52, bevel=0.03, seg=3, mat=mat_seat, col=col)
    back.rotation_euler.z = rad


def create_bookshelf(name, y_center, x_back, z, width, depth, height, facing='+x', mat_wood=None, mat_books=None, col=None):
    """Bookcase against a wall running along Y. x_back = wall-side back face."""
    s = 1 if facing == '+x' else -1
    xc = x_back + s * depth / 2
    mat_books = mat_books or []
    create_beveled_box(f"{name}_SideB", x_back + s * 0.015, y_center, z, 0.03, width, height, bevel=0.005, mat=mat_wood, col=col)
    create_beveled_box(f"{name}_SideL", xc, y_center - width / 2 + 0.015, z, depth, 0.03, height, bevel=0.005, mat=mat_wood, col=col)
    create_beveled_box(f"{name}_SideR", xc, y_center + width / 2 - 0.015, z, depth, 0.03, height, bevel=0.005, mat=mat_wood, col=col)
    create_beveled_box(f"{name}_Top", xc, y_center, z + height - 0.03, depth, width, 0.03, bevel=0.005, mat=mat_wood, col=col)
    shelf_zs = [z + 0.02, z + 0.52, z + 1.02, z + 1.45]
    for si, sz in enumerate(shelf_zs):
        create_beveled_box(f"{name}_Shelf{si+1}", xc, y_center, sz, depth - 0.02, width - 0.06, 0.025, bevel=0.004, mat=mat_wood, col=col)
    if not mat_books:
        return
    inner = width - 0.12
    for si, sz in enumerate(shelf_zs):
        y = y_center - inner / 2 + 0.03
        bi = 0
        while y < y_center + inner / 2 - 0.05:
            bw = 0.028 + 0.014 * ((si * 7 + bi * 3) % 4) / 3.0
            bh = 0.21 + 0.06 * ((si * 5 + bi * 2) % 5) / 4.0
            gap = 0.0 if ((si + bi) % 6) else 0.03
            y += gap + bw / 2
            book = create_beveled_box(f"{name}_B{si+1}_{bi+1}", xc + s * 0.01, y, sz + 0.025, depth - 0.10, bw, bh, bevel=0.003, seg=1, mat=mat_books[(si * 3 + bi) % len(mat_books)], col=col)
            if (si + bi) % 7 == 3:
                book.rotation_euler.x = 0.10
            y += bw / 2 + 0.004
            bi += 1


def create_desk_lamp(name, x, y, z_desk, mat_arm=None, mat_shade=None, mat_bulb=None, col=None):
    """Articulated desk lamp with warm bulb."""
    create_cylinder(f"{name}_Base", x, y, z_desk, 0.07, 0.02, seg=16, mat=mat_arm, col=col)
    arm1 = create_cylinder(f"{name}_Arm1", x, y + 0.03, z_desk + 0.02, 0.011, 0.30, seg=8, mat=mat_arm, col=col)
    arm1.rotation_euler.x = math.radians(-18)
    arm2 = create_cylinder(f"{name}_Arm2", x, y - 0.02, z_desk + 0.30, 0.010, 0.26, seg=8, mat=mat_arm, col=col)
    arm2.rotation_euler.x = math.radians(38)
    create_cone_shade(f"{name}_Head", x, y - 0.10, z_desk + 0.38, 0.075, 0.03, 0.10, mat=mat_shade, col=col)
    create_sphere(f"{name}_Bulb", x, y - 0.10, z_desk + 0.40, 0.020, mat=mat_bulb, col=col, seg=12, rings=8)


def create_laptop(name, x, y, z_desk, rot_z_deg=0, mat_body=None, mat_screen=None, mat_key=None, col=None):
    """Open laptop; screen faces local -Y (user sits on -Y side). Tilt exact at rot 0."""
    rad = math.radians(rot_z_deg)
    dx, dy = math.sin(rad), math.cos(rad)
    base = create_beveled_box(f"{name}_Base", x, y, z_desk, 0.32, 0.22, 0.016, bevel=0.004, mat=mat_body, col=col)
    base.rotation_euler.z = rad
    lid = create_beveled_box(f"{name}_Lid", x + 0.100 * dx, y + 0.100 * dy, z_desk + 0.10, 0.32, 0.012, 0.21, bevel=0.003, seg=1, mat=mat_body, col=col)
    lid.rotation_euler.z = rad
    lid.rotation_euler.x = math.radians(-12)
    scr = create_beveled_box(f"{name}_Screen", x + 0.093 * dx, y + 0.093 * dy, z_desk + 0.105, 0.30, 0.004, 0.19, bevel=0.001, seg=1, mat=mat_screen, col=col)
    scr.rotation_euler.z = rad
    scr.rotation_euler.x = math.radians(-12)


def create_mug(name, x, y, z_desk, mat=None, col=None):
    """Coffee mug with simple handle."""
    create_cylinder(f"{name}_Cup", x, y, z_desk, 0.038, 0.09, seg=16, mat=mat, col=col)
    create_beveled_box(f"{name}_HandleT", x + 0.050, y, z_desk + 0.065, 0.028, 0.012, 0.012, bevel=0.004, seg=1, mat=mat, col=col)
    create_beveled_box(f"{name}_HandleB", x + 0.050, y, z_desk + 0.025, 0.028, 0.012, 0.012, bevel=0.004, seg=1, mat=mat, col=col)
    create_beveled_box(f"{name}_HandleV", x + 0.062, y, z_desk + 0.025, 0.012, 0.012, 0.052, bevel=0.004, seg=1, mat=mat, col=col)


def create_rug(name, x, y, z, w, d, mat=None, col=None):
    """Thin low-pile area rug."""
    return create_beveled_box(name, x, y, z, w, d, 0.012, bevel=0.005, seg=1, mat=mat, col=col)


def create_bath_mirror(name, x, y, z_bottom, w, h, facing='-x', mat_mirror=None, mat_frame=None, mat_led=None, col=None):
    """Framed vanity mirror with slim top LED bar."""
    if facing in ('-x', '+x'):
        s = -1 if facing == '-x' else 1
        create_beveled_box(f"{name}_Frame", x, y, z_bottom, 0.030, w, h, bevel=0.004, mat=mat_frame, col=col)
        create_beveled_box(f"{name}_Glass", x + s * 0.015, y, z_bottom + 0.025, 0.006, w - 0.05, h - 0.05, bevel=0.001, seg=1, mat=mat_mirror, col=col)
        if mat_led:
            create_beveled_box(f"{name}_LEDBAR", x + s * 0.023, y, z_bottom + h - 0.035, 0.010, w - 0.10, 0.018, bevel=0.002, seg=1, mat=mat_led, col=col)
    else:
        s = -1 if facing == '-y' else 1
        create_beveled_box(f"{name}_Frame", x, y, z_bottom, w, 0.030, h, bevel=0.004, mat=mat_frame, col=col)
        create_beveled_box(f"{name}_Glass", x, y + s * 0.015, z_bottom + 0.025, w - 0.05, 0.006, h - 0.05, bevel=0.001, seg=1, mat=mat_frame, col=col)
        if mat_led:
            create_beveled_box(f"{name}_LEDBAR", x, y + s * 0.023, z_bottom + h - 0.035, w - 0.10, 0.010, 0.018, bevel=0.002, seg=1, mat=mat_led, col=col)


def create_towel_bar(name, x, y, z, length, axis='y', mat_chrome=None, mat_towel=None, col=None):
    """Wall towel bar with one draped hand towel."""
    if axis == 'y':
        bar = create_cylinder(f"{name}_Bar", x, y, z, 0.011, length, seg=10, mat=mat_chrome, col=col)
        bar.rotation_euler.x = math.radians(90)
        bar.location.y = y + length / 2
        create_beveled_box(f"{name}_TowelF", x, y + 0.02, z - 0.30, 0.02, 0.30, 0.30, bevel=0.008, seg=2, mat=mat_towel, col=col)
        create_beveled_box(f"{name}_TowelB", x, y - 0.02, z - 0.26, 0.02, 0.30, 0.26, bevel=0.008, seg=2, mat=mat_towel, col=col)
    else:
        bar = create_cylinder(f"{name}_Bar", x - length / 2, y, z, 0.011, length, seg=10, mat=mat_chrome, col=col)
        bar.rotation_euler.y = math.radians(90)
        create_beveled_box(f"{name}_TowelF", x + 0.02, y, z - 0.30, 0.30, 0.02, 0.30, bevel=0.008, seg=2, mat=mat_towel, col=col)
        create_beveled_box(f"{name}_TowelB", x - 0.02, y, z - 0.26, 0.30, 0.02, 0.26, bevel=0.008, seg=2, mat=mat_towel, col=col)


def create_folded_towels(name, x, y, z_top, mat1=None, mat2=None, col=None):
    """Stack of two folded bath towels."""
    create_beveled_box(f"{name}_Lower", x, y, z_top, 0.30, 0.22, 0.07, bevel=0.025, seg=3, mat=mat1, col=col)
    create_beveled_box(f"{name}_Upper", x, y, z_top + 0.07, 0.26, 0.19, 0.06, bevel=0.025, seg=3, mat=mat2, col=col)


def create_dress_closet(name, x_center, y_back, z, width, depth=0.55, height=2.05, facing='-y', mat_wood=None, mat_chrome=None, mat_cloths=None, col=None):
    """Open dress-room wardrobe: side panels, top shelf, hanging rod with garments."""
    s = -1 if facing == '-y' else 1
    yc = y_back - s * depth / 2
    mat_cloths = mat_cloths or []
    create_beveled_box(f"{name}_SideL", x_center - width / 2 + 0.02, yc, z, 0.04, depth, height, bevel=0.005, mat=mat_wood, col=col)
    create_beveled_box(f"{name}_SideR", x_center + width / 2 - 0.02, yc, z, 0.04, depth, height, bevel=0.005, mat=mat_wood, col=col)
    create_beveled_box(f"{name}_TopShelf", x_center, yc, z + height - 0.22, width - 0.04, depth - 0.02, 0.035, bevel=0.004, mat=mat_wood, col=col)
    create_beveled_box(f"{name}_BotShelf", x_center, yc, z + 0.35, width - 0.04, depth - 0.02, 0.035, bevel=0.004, mat=mat_wood, col=col)
    rod = create_cylinder(f"{name}_Rod", x_center - (width - 0.1) / 2, yc, z + height - 0.32, 0.014, width - 0.1, seg=10, mat=mat_chrome, col=col)
    rod.rotation_euler.y = math.radians(90)
    if mat_cloths:
        n = min(6, len(mat_cloths) + 2)
        for i in range(n):
            gx = x_center - (width - 0.3) / 2 + i * ((width - 0.3) / max(1, n - 1))
            gh = 0.75 + 0.15 * ((i * 3) % 3) / 2.0
            create_beveled_box(f"{name}_Garment{i+1}", gx, yc, z + height - 0.32 - gh, 0.16, 0.10, gh, bevel=0.03, seg=2, mat=mat_cloths[i % len(mat_cloths)], col=col)


def create_dress_closet_y(name, y_center, x_back, z, width, depth=0.55, height=2.05, facing='+x', mat_wood=None, mat_chrome=None, mat_cloths=None, col=None):
    """Open wardrobe run along Y (against an X-facing wall). x_back = wall-side face."""
    s = 1 if facing == '+x' else -1
    xc = x_back + s * depth / 2
    mat_cloths = mat_cloths or []
    create_beveled_box(f"{name}_SideL", xc, y_center - width / 2 + 0.02, z, depth, 0.04, height, bevel=0.005, mat=mat_wood, col=col)
    create_beveled_box(f"{name}_SideR", xc, y_center + width / 2 - 0.02, z, depth, 0.04, height, bevel=0.005, mat=mat_wood, col=col)
    create_beveled_box(f"{name}_TopShelf", xc, y_center, z + height - 0.22, depth - 0.02, width - 0.04, 0.035, bevel=0.004, mat=mat_wood, col=col)
    create_beveled_box(f"{name}_BotShelf", xc, y_center, z + 0.35, depth - 0.02, width - 0.04, 0.035, bevel=0.004, mat=mat_wood, col=col)
    rod = create_cylinder(f"{name}_Rod", xc, y_center - (width - 0.1) / 2, z + height - 0.32, 0.014, width - 0.1, seg=10, mat=mat_chrome, col=col)
    rod.rotation_euler.x = math.radians(90)
    rod.location.y = y_center + (width - 0.1) / 2
    if mat_cloths:
        n = min(6, len(mat_cloths) + 2)
        for i in range(n):
            gy = y_center - (width - 0.3) / 2 + i * ((width - 0.3) / max(1, n - 1))
            gh = 0.75 + 0.15 * ((i * 3) % 3) / 2.0
            create_beveled_box(f"{name}_Garment{i+1}", xc, gy, z + height - 0.32 - gh, 0.10, 0.16, gh, bevel=0.03, seg=2, mat=mat_cloths[i % len(mat_cloths)], col=col)


def create_sink_single(name, x, y, z, mat_sink=None, mat_chrome=None, col=None):
    """Single large square undermount sink with high-arc faucet (e-modelhouse)."""
    create_beveled_box(f"{name}_BasinRim", x, y, z, 0.80, 0.50, 0.02, bevel=0.005, mat=mat_sink, col=col)
    create_beveled_box(f"{name}_Bowl", x, y, z - 0.20, 0.68, 0.42, 0.20, bevel=0.025, mat=mat_sink, col=col)
    create_cylinder(f"{name}_FaucetBase", x, y + 0.19, z + 0.02, 0.026, 0.05, mat=mat_chrome, col=col)
    create_cylinder(f"{name}_FaucetNeck", x, y + 0.19, z + 0.07, 0.015, 0.30, mat=mat_chrome, col=col)
    create_beveled_box(f"{name}_FaucetSpoutH", x, y + 0.10, z + 0.36, 0.026, 0.20, 0.026, bevel=0.005, mat=mat_chrome, col=col)
    create_cylinder(f"{name}_FaucetTip", x, y + 0.01, z + 0.28, 0.013, 0.08, mat=mat_chrome, col=col)
    create_cylinder(f"{name}_FaucetLever", x + 0.05, y + 0.19, z + 0.13, 0.009, 0.09, mat=mat_chrome, col=col)


def create_flat_hood(name, x, y, z, sx, sy, mat=None, col=None):
    """Slim flat black glass hood slab with filter grooves underneath."""
    create_beveled_box(f"{name}_Slab", x, y, z, sx, sy, 0.05, bevel=0.008, seg=2, mat=mat, col=col)
    create_beveled_box(f"{name}_Filter1", x, y - sy * 0.18, z - 0.008, sx * 0.86, sy * 0.22, 0.012, bevel=0.003, seg=1, mat=mat, col=col)
    create_beveled_box(f"{name}_Filter2", x, y + sy * 0.18, z - 0.008, sx * 0.86, sy * 0.22, 0.012, bevel=0.003, seg=1, mat=mat, col=col)


def create_builtin_oven(name, x_front, y_center, z_base, width, height=0.60, mat_black=None, mat_handle=None, col=None, facing='-x'):
    """Black glass built-in oven under cooktop. x_front = cabinet front plane."""
    s = -1 if facing == '-x' else 1
    create_beveled_box(f"{name}_Cavity", x_front - s * 0.28, y_center, z_base, 0.56, width, height, bevel=0.008, mat=mat_black, col=col)
    create_beveled_box(f"{name}_Door", x_front + s * 0.008, y_center, z_base + 0.03, 0.024, width - 0.06, height - 0.10, bevel=0.004, mat=mat_black, col=col)
    bar = create_cylinder(f"{name}_Handle", x_front + s * 0.045, y_center - (width - 0.12) / 2, z_base + height - 0.10, 0.011, width - 0.12, seg=10, mat=mat_handle, col=col)
    bar.rotation_euler.x = math.radians(90)
    bar.location.y = y_center + (width - 0.12) / 2
    create_beveled_box(f"{name}_Trim", x_front + s * 0.006, y_center, z_base + height - 0.015, 0.020, width - 0.04, 0.03, bevel=0.003, seg=1, mat=mat_handle, col=col)


def create_dishwasher_front(name, x_center, y_front, z_base, width, mat_steel=None, mat_handle=None, col=None):
    """Steel dishwasher door flush with base cabinet front (faces -Y)."""
    create_beveled_box(f"{name}_Door", x_center, y_front + 0.012, z_base, width, 0.024, 0.80, bevel=0.006, mat=mat_steel, col=col)
    bar = create_cylinder(f"{name}_Handle", x_center - (width - 0.12) / 2, y_front - 0.020, z_base + 0.68, 0.011, width - 0.12, seg=10, mat=mat_handle, col=col)
    bar.rotation_euler.y = math.radians(90)


def create_backsplash(name, x1, x2, y, z1, z2, mat=None, col=None, axis='x'):
    """Full-height stone splash panel between counter and uppers."""
    if axis == 'x':
        create_beveled_box(name, (x1 + x2) / 2, y, z1, x2 - x1, 0.02, z2 - z1, bevel=0.002, seg=1, mat=mat, col=col)
    else:
        create_beveled_box(name, y, (x1 + x2) / 2, z1, 0.02, x2 - x1, z2 - z1, bevel=0.002, seg=1, mat=mat, col=col)


def create_ceiling_strip(name, x1, x2, y, z, width, mat_led=None, col=None):
    """Recessed linear LED bar just below ceiling."""
    create_beveled_box(name, (x1 + x2) / 2, y, z, x2 - x1, width, 0.018, bevel=0.002, seg=1, mat=mat_led, col=col)


def create_sill_and_header(name, x1, x2, y1, y2, z_sill_top, z_head_bottom, z_top=2.30, mat_wall=None, mat_cap=None, col=None, cap_dy=0.0):
    """Masonry below sill + stone cap + masonry above head for punched windows."""
    xc, yc = (x1 + x2) / 2, (y1 + y2) / 2
    w, d = x2 - x1, y2 - y1
    if z_sill_top > 0.01:
        create_beveled_box(f"{name}_SillWall", xc, yc, 0.0, w, d, z_sill_top, bevel=0.004, mat=mat_wall, col=col)
    if mat_cap and z_sill_top > 0.01:
        create_beveled_box(f"{name}_SillCap", xc, yc + cap_dy, z_sill_top, w + 0.02, d + 0.03, 0.025, bevel=0.004, mat=mat_cap, col=col)
    if z_head_bottom < z_top - 0.01:
        create_beveled_box(f"{name}_Header", xc, yc, z_head_bottom, w, d, z_top - z_head_bottom, bevel=0.004, mat=mat_wall, col=col)


def create_jamb_liners(name, x1, x2, y1, y2, z1, z2, mat=None, col=None):
    """White reveal liners on opening sides + head (wall thickness depth)."""
    t = 0.018
    create_beveled_box(f"{name}_L", x1 + t / 2, (y1 + y2) / 2, z1, t, y2 - y1, z2 - z1, bevel=0.002, seg=1, mat=mat, col=col)
    create_beveled_box(f"{name}_R", x2 - t / 2, (y1 + y2) / 2, z1, t, y2 - y1, z2 - z1, bevel=0.002, seg=1, mat=mat, col=col)
    create_beveled_box(f"{name}_Head", (x1 + x2) / 2, (y1 + y2) / 2, z2 - t, x2 - x1, y2 - y1, t, bevel=0.002, seg=1, mat=mat, col=col)


def create_railing(name, x1, x2, y, z_base, height=1.10, mat=None, col=None):
    """Balcony guardrail: top/mid rails + balusters."""
    n = max(2, int((x2 - x1) / 0.55))
    for i in range(n + 1):
        px = x1 + (x2 - x1) * i / n
        create_cylinder(f"{name}_Post{i+1}", px, y, z_base, 0.022, height, seg=8, mat=mat, col=col)
    top = create_cylinder(f"{name}_TopRail", x1, y, z_base + height - 0.03, 0.030, x2 - x1, seg=10, mat=mat, col=col)
    top.rotation_euler.y = math.radians(90)
    mid = create_cylinder(f"{name}_MidRail", x1, y, z_base + height * 0.55, 0.016, x2 - x1, seg=8, mat=mat, col=col)
    mid.rotation_euler.y = math.radians(90)


def create_balcony_slab(name, x1, x2, y1, y2, z_top, thickness=0.15, mat=None, col=None):
    """Exterior balcony floor slab outside south windows."""
    return create_beveled_box(name, (x1 + x2) / 2, (y1 + y2) / 2, z_top - thickness, x2 - x1, y2 - y1, thickness, bevel=0.005, mat=mat, col=col)


def create_entry_frame(name, x1, x2, y, z_top, mat=None, col=None):
    """Front door surround: jambs + head."""
    t, w = 0.06, 0.10
    create_beveled_box(f"{name}_JambL", x1 + t / 2, y, 0.0, t, w, z_top, bevel=0.004, mat=mat, col=col)
    create_beveled_box(f"{name}_JambR", x2 - t / 2, y, 0.0, t, w, z_top, bevel=0.004, mat=mat, col=col)
    create_beveled_box(f"{name}_Head", (x1 + x2) / 2, y, z_top - t, x2 - x1, w, t, bevel=0.004, mat=mat, col=col)


print("Updated generate_high_detail_assets with complete Prugio apartment asset builders!")

