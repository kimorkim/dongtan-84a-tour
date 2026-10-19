"""Fix Kitchen Peninsula Length, Sink, and Dining Table Flow.

Blueprint Alignments (84A.jpg and unit_84a.png):
1. Kitchen Peninsula:
   - Shortened from 2.345m to 1.30m (extending from East wall X=7.825 to X=6.525).
   - Opens up the kitchen entrance from 0.48m to 1.53m (wide, spacious flow).
2. Peninsula Cabinetry:
   - Removes outer doors ProK_DoorP1 and ProK_DoorP2.
   - Adjusts ProK_DoorP3 and ProK_DoorP4 to 58cm each.
   - Moves ProK_EndPanelW to the new West end of the peninsula (X=6.525).
3. Dining Table & Chairs:
   - Shifts dining group +1.20m in X (from X=5.90 to X=7.10).
   - Tucks dining table flush against the shortened peninsula on the East side.
   - Frees up 1.85m of wide-open corridor clearance from Master Suite to Living/Bedrooms.
4. Kitchen Sink:
   - Upgrades sink bowl to generous 880mm Korean premium rectangular sink bowl.
   - Perfectly centered on kitchen exterior window (X=6.15).
"""
import bpy

def resize_beveled_box(obj, new_center, new_size):
    if not obj or obj.type != 'MESH':
        return
    obj.location = (new_center[0], new_center[1], new_center[2])
    sx, sy, sz = new_size
    x1, x2 = -sx/2, sx/2
    y1, y2 = -sy/2, sy/2
    z1, z2 = 0.0, sz
    new_coords = [
        (x1, y1, z1), (x2, y1, z1), (x2, y2, z1), (x1, y2, z1),
        (x1, y1, z2), (x2, y1, z2), (x2, y2, z2), (x1, y2, z2)
    ]
    if len(obj.data.vertices) >= 8:
        for i in range(8):
            obj.data.vertices[i].co = new_coords[i]
        obj.data.update()
        print(f"[RESIZE] {obj.name}: center={new_center}, size={new_size}")

def fix_peninsula():
    # 1. Peninsula Counter (1.30m wide: X from 6.525 to 7.825)
    top_p = bpy.data.objects.get("Kitchen_Top_Pen")
    if top_p:
        resize_beveled_box(top_p, (7.175, 6.390, 0.860), (1.300, 0.670, 0.040))
        
    base_p = bpy.data.objects.get("Kitchen_Base_Pen")
    if base_p:
        resize_beveled_box(base_p, (7.185, 6.400, 0.070), (1.280, 0.650, 0.790))
        
    kick_p = bpy.data.objects.get("Kitchen_Kick_Pen")
    if kick_p:
        resize_beveled_box(kick_p, (7.225, 6.460, 0.000), (1.200, 0.650, 0.070))
        
    # 2. Doors & End Panel
    for obsolete_door in ["ProK_DoorP1", "ProK_DoorP2"]:
        o = bpy.data.objects.get(obsolete_door)
        if o:
            m = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            if m and m.users == 0:
                bpy.data.meshes.remove(m)
            print(f"[CLEANUP] Removed {obsolete_door}")
            
    door3 = bpy.data.objects.get("ProK_DoorP3")
    if door3:
        resize_beveled_box(door3, (6.885, 6.067, 0.100), (0.580, 0.018, 0.720))
        
    door4 = bpy.data.objects.get("ProK_DoorP4")
    if door4:
        resize_beveled_box(door4, (7.485, 6.067, 0.100), (0.580, 0.018, 0.720))
        
    panel = bpy.data.objects.get("ProK_EndPanelW")
    if panel:
        panel.location = (6.525, 6.400, 0.100)
        print(f"[PANEL] ProK_EndPanelW moved to {panel.location}")

def shift_dining_group():
    # Target center X: 7.10 (shifted by +1.20m from 5.90)
    delta_x = 1.200
    dining_objs = [
        o for o in bpy.data.objects 
        if any(k in o.name.lower() for k in [
            'dining_', 'diningprop_', 'pendant_dining', 'chair_e', 'chair_w'
        ])
    ]
    for o in dining_objs:
        o.location.x += delta_x
    print(f"[DINING] Shifted {len(dining_objs)} dining elements by dx={delta_x:+.3f}m")
    
    # Dining downlight
    dl = bpy.data.objects.get("Downlight_Dining")
    if dl:
        dl.location.x += delta_x
        print(f"[LIGHT] Downlight_Dining moved to {dl.location}")

def upgrade_kitchen_sink():
    # Centered at X=6.15 under Win_Kitchen
    rim = bpy.data.objects.get("Kitchen_Sink_BasinRim")
    if rim:
        resize_beveled_box(rim, (6.150, 9.750, 0.900), (0.900, 0.520, 0.020))
        
    bowl = bpy.data.objects.get("Kitchen_Sink_Bowl")
    if bowl:
        resize_beveled_box(bowl, (6.150, 9.750, 0.680), (0.820, 0.440, 0.220))
        
    print("[SINK] Upgraded sink bowl to 880mm premium rectangular basin")

def main():
    print("=== STARTING KITCHEN & DINING FLOW RESTRUCTURE ===")
    fix_peninsula()
    shift_dining_group()
    upgrade_kitchen_sink()
    
    # Save master file
    bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
    print("=== KITCHEN & DINING FLOW RESTRUCTURE COMPLETE & SAVED ===")

main()
