import bpy
import math
import os

def setup_illumination():
    """Configure ambient world lighting, GTAO, and directional sun light."""
    # 1. Ambient World Lighting
    if not bpy.context.scene.world:
        world = bpy.data.worlds.new("World")
        bpy.context.scene.world = world
    bpy.context.scene.world.use_nodes = True
    bg_node = bpy.context.scene.world.node_tree.nodes.get("Background")
    if bg_node:
        bg_node.inputs["Color"].default_value = (0.90, 0.92, 0.95, 1.0)
        bg_node.inputs["Strength"].default_value = 0.80

    # 2. Ambient Occlusion (GTAO in EEVEE Next)
    if hasattr(bpy.context.scene, "eevee"):
        try:
            bpy.context.scene.eevee.use_gtao = True
            bpy.context.scene.eevee.gtao_distance = 1.0
            bpy.context.scene.eevee.gtao_factor = 1.5
        except Exception as e:
            print(f"Notice: GTAO setup: {e}")

    # 3. Directional Sun Light
    sun_name = "Light_Sun"
    sun_data = bpy.data.lights.get(sun_name) or bpy.data.lights.new(sun_name, type="SUN")
    sun_data.energy = 3.5
    sun_data.color = (1.0, 0.98, 0.95)
    
    sun_obj = bpy.data.objects.get(sun_name) or bpy.data.objects.new(sun_name, sun_data)
    if sun_obj.name not in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.link(sun_obj)
    sun_obj.location = (5.0, 5.0, 15.0)
    sun_obj.rotation_euler = (math.radians(40), math.radians(20), math.radians(-35))
    sun_obj.hide_render = False
    sun_obj.hide_viewport = False
    print("SUCCESS: Illumination configured (Sun + World Ambient + GTAO).")

def numerical_audit():
    """Iterate through all mesh objects in apartment collections and audit dimensions."""
    collections = [
        ("Apt_Floors", 8),
        ("Apt_OuterWalls", 11),
        ("Apt_InteriorWalls", 21),
        ("Apt_Openings", 12),
    ]
    
    print("\n" + "=" * 70)
    print("=== DONGTAN 84A APARTMENT NUMERICAL AUDIT REPORT ===")
    print("=" * 70)
    
    total_audited = 0
    all_matched = True
    
    for cname, expected_count in collections:
        col = bpy.data.collections.get(cname)
        if not col:
            print(f"ERROR: Missing expected collection '{cname}'")
            all_matched = False
            continue
        
        objects = sorted([o for o in col.objects if o.type == "MESH"], key=lambda o: o.name)
        actual_count = len(objects)
        status = "MATCH" if actual_count == expected_count else "MISMATCH"
        if status != "MATCH":
            all_matched = False
            
        print(f"\n--- {cname} [{actual_count}/{expected_count} objects - {status}] ---")
        for obj in objects:
            total_audited += 1
            print(
                f"{obj.name:<28} | Collection: {cname:<18} | "
                f"Loc: ({obj.location.x:5.2f}, {obj.location.y:5.2f}, {obj.location.z:5.2f}) | "
                f"Dims: ({obj.dimensions.x:5.2f}, {obj.dimensions.y:5.2f}, {obj.dimensions.z:5.2f})"
            )
            
    print("\n" + "=" * 70)
    print(f"Total Structural Objects Audited: {total_audited} (Expected: 52)")
    print(f"Audit Status: {'ALL 52 OBJECTS VERIFIED' if all_matched and total_audited == 52 else 'AUDIT WARNING'}")
    print("=" * 70 + "\n")
    return all_matched

def render_view(cam_name, filepath, location, rotation, is_ortho=False, ortho_scale=15.5, lens=22.0):
    """Set up camera and render a clean screenshot."""
    cam_data = bpy.data.cameras.get(cam_name) or bpy.data.cameras.new(cam_name)
    cam_obj = bpy.data.objects.get(cam_name) or bpy.data.objects.new(cam_name, cam_data)
    
    if cam_obj.name not in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.link(cam_obj)
        
    cam_obj.location = location
    cam_obj.rotation_euler = rotation
    cam_obj.hide_render = False
    cam_obj.hide_viewport = False
    
    if is_ortho:
        cam_data.type = "ORTHO"
        cam_data.ortho_scale = ortho_scale
    else:
        cam_data.type = "PERSP"
        cam_data.lens = lens
        
    bpy.context.scene.camera = cam_obj
    bpy.context.scene.render.resolution_x = 1280
    bpy.context.scene.render.resolution_y = 960
    abs_path = os.path.abspath(filepath)
    bpy.context.scene.render.filepath = abs_path
    
    bpy.ops.render.render(write_still=True)
    file_size = os.path.getsize(abs_path) if os.path.exists(abs_path) else 0
    print(f"SUCCESS: Rendered {filepath} ({file_size:,} bytes) at {abs_path}")
    return abs_path

def main():
    # 1. Illumination
    setup_illumination()
    
    # 2. Numerical Audit
    audit_ok = numerical_audit()
    
    # 3. Top-down orthographic view
    # Center of apartment: X ≈ 4.93, Y ≈ 5.10; ortho_scale = 15.5 comfortably frames all 10.6m depth
    render_view(
        cam_name="Cam_Topdown",
        filepath="verification_topdown.png",
        location=(4.93, 5.10, 15.0),
        rotation=(0.0, 0.0, 0.0),
        is_ortho=True,
        ortho_scale=15.5,
    )
    
    # 4. Living Room eye-level (Z=1.6m) perspective POV view looking into apartment interior (North)
    render_view(
        cam_name="Cam_Living_POV",
        filepath="verification_living_pov.png",
        location=(6.0, 2.0, 1.6),
        rotation=(math.radians(82), 0.0, math.radians(0)),
        is_ortho=False,
        lens=22.0,
    )
    
    # 5. Alpha Room eye-level (Z=1.6m) perspective POV view looking through room (North)
    render_view(
        cam_name="Cam_Alpha_POV",
        filepath="verification_alpha_pov.png",
        location=(3.7, 5.6, 1.6),
        rotation=(math.radians(85), 0.0, math.radians(0)),
        is_ortho=False,
        lens=20.0,
    )
    
    # 6. Save milestone .blend file
    save_path = os.path.abspath("apt_v01_structure.blend")
    bpy.ops.wm.save_as_mainfile(filepath=save_path)
    blend_size = os.path.getsize(save_path) if os.path.exists(save_path) else 0
    print(f"SUCCESS: Saved milestone model to {save_path} ({blend_size:,} bytes)")

if __name__ == "__main__" or True:
    main()
