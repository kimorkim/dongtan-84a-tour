"""Comprehensive Fix for Dongtan Foretpark Prugio 84A 3D Model.

Fixes:
1. Deletes fake walls (NewWall_NorthW, NewWall_NorthE, NewWall_NorthHead, NewWall_EastN).
2. Deletes fake South balcony slab, entry slab, and exterior railing (BalconySlab_South, EntrySlab_Front, Rail_South_*).
3. Deletes Office_Shelf objects that blocked the Alpha room doorway.
4. Moves dining table, chairs, table settings, and pendants +0.18m along Y to sit flush against the kitchen peninsula.
5. Restores official Prugio PBR materials:
   - Mat_Wall_Cap: architectural dark charcoal (0.12, 0.13, 0.15)
   - Mat_Tile_Grey & Mat_BathTile_Wall: neutral modern 300x300 floor / 300x600 wall tiles (NO checkerboard)
   - Mat_Marble_White & Mat_Countertop_Granite: crisp white engineered quartz (NO yellowish stains)
   - Mat_Curtain: solid off-white sheer linen (NO plaid pattern)
   - Mat_ArtWall_Tile: polished ivory 600x600 stone tile
6. Ensures all wall top faces (normal.z > 0.8) have Mat_Wall_Cap.
7. Boosts lighting for Dress Room and Master Bath.
8. Saves updated scene to apt_84a_photoreal_tour.blend.
"""
import bpy
import math

def remove_objects_by_name(names_or_prefixes):
    removed = 0
    for o in list(bpy.data.objects):
        match = False
        for target in names_or_prefixes:
            if o.name == target or o.name.startswith(target):
                match = True
                break
        if match:
            mesh = o.data if o.type == 'MESH' else None
            bpy.data.objects.remove(o, do_unlink=True)
            if mesh and mesh.users == 0:
                bpy.data.meshes.remove(mesh)
            removed += 1
    print(f"[CLEANUP] Removed {removed} objects matching {names_or_prefixes}")
    return removed

def fix_structure_and_openings():
    # 1. Fake walls created by Muse
    fake_walls = ["NewWall_NorthW", "NewWall_NorthE", "NewWall_NorthHead", "NewWall_EastN"]
    remove_objects_by_name(fake_walls)
    
    # 2. Fake South balcony, entry slab, and railing
    fake_slabs_rails = ["BalconySlab_South", "EntrySlab_Front", "Rail_South"]
    remove_objects_by_name(fake_slabs_rails)
    
    # 3. Alpha room blocking shelf
    remove_objects_by_name(["Office_Shelf"])

def align_dining_group():
    # Delta Y: +0.18m flush to peninsula
    delta_y = 0.180
    dining_objs = [
        o for o in bpy.data.objects 
        if any(k in o.name.lower() for k in [
            'dining_', 'diningprop_', 'pendant_dining', 'chair_e', 'chair_w'
        ])
    ]
    for o in dining_objs:
        o.location.y += delta_y
    print(f"[DINING] Shifted {len(dining_objs)} dining elements by dy={delta_y:+.3f}m")

def restore_pbr_materials():
    # 1. Mat_Wall_Cap (Architectural Dark Charcoal)
    mat_cap = bpy.data.materials.get("Mat_Wall_Cap") or bpy.data.materials.new("Mat_Wall_Cap")
    mat_cap.use_nodes = True
    nodes = mat_cap.node_tree.nodes
    links = mat_cap.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.12, 0.13, 0.15, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.45
    bsdf.inputs['Specular IOR Level'].default_value = 0.5
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    print("[MAT] Restored Mat_Wall_Cap (dark charcoal)")

    # 2. Mat_Wall_Interior (Shinhan Milk White Wallpaper)
    mat_wall = bpy.data.materials.get("Mat_Wall_Interior") or bpy.data.materials.new("Mat_Wall_Interior")
    mat_wall.use_nodes = True
    nodes = mat_wall.node_tree.nodes
    links = mat_wall.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.94, 0.93, 0.91, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.85
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    print("[MAT] Restored Mat_Wall_Interior (milk white)")

    # 3. Mat_Tile_Grey (Neutral 300x300 Porcelain Non-Slip Floor Tile)
    mat_tile = bpy.data.materials.get("Mat_Tile_Grey") or bpy.data.materials.new("Mat_Tile_Grey")
    mat_tile.use_nodes = True
    nodes = mat_tile.node_tree.nodes
    links = mat_tile.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    tex_coord = nodes.new('ShaderNodeTexCoord')
    mapping = nodes.new('ShaderNodeMapping')
    brick = nodes.new('ShaderNodeTexBrick')
    bump = nodes.new('ShaderNodeBump')
    
    brick.offset = 0.0
    brick.inputs['Scale'].default_value = 1.0
    brick.inputs['Mortar Size'].default_value = 0.003
    brick.inputs['Row Height'].default_value = 0.30
    brick.inputs['Brick Width'].default_value = 0.30
    brick.inputs['Color1'].default_value = (0.47, 0.48, 0.50, 1.0)
    brick.inputs['Color2'].default_value = (0.51, 0.52, 0.54, 1.0)
    brick.inputs['Mortar'].default_value = (0.34, 0.34, 0.35, 1.0)
    
    bump.inputs['Strength'].default_value = 0.25
    bump.inputs['Distance'].default_value = 0.008
    
    links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])
    links.new(mapping.outputs['Vector'], brick.inputs['Vector'])
    links.new(brick.outputs['Color'], bsdf.inputs['Base Color'])
    links.new(brick.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    bsdf.inputs['Roughness'].default_value = 0.55
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    print("[MAT] Restored Mat_Tile_Grey (neutral 300x300 porcelain tile)")

    # 4. Mat_BathTile_Wall (Neutral 300x600 Greige Horizontal Wall Tile)
    mat_bath_wall = bpy.data.materials.get("Mat_BathTile_Wall") or bpy.data.materials.new("Mat_BathTile_Wall")
    mat_bath_wall.use_nodes = True
    nodes = mat_bath_wall.node_tree.nodes
    links = mat_bath_wall.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    tex_coord = nodes.new('ShaderNodeTexCoord')
    brick = nodes.new('ShaderNodeTexBrick')
    bump = nodes.new('ShaderNodeBump')
    
    brick.offset = 0.5
    brick.inputs['Scale'].default_value = 1.0
    brick.inputs['Mortar Size'].default_value = 0.002
    brick.inputs['Row Height'].default_value = 0.30
    brick.inputs['Brick Width'].default_value = 0.60
    brick.inputs['Color1'].default_value = (0.82, 0.81, 0.79, 1.0)
    brick.inputs['Color2'].default_value = (0.85, 0.84, 0.82, 1.0)
    brick.inputs['Mortar'].default_value = (0.65, 0.64, 0.62, 1.0)
    
    bump.inputs['Strength'].default_value = 0.15
    bump.inputs['Distance'].default_value = 0.004
    
    links.new(tex_coord.outputs['Object'], brick.inputs['Vector'])
    links.new(brick.outputs['Color'], bsdf.inputs['Base Color'])
    links.new(brick.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    bsdf.inputs['Roughness'].default_value = 0.28
    if 'Coat Weight' in bsdf.inputs:
        bsdf.inputs['Coat Weight'].default_value = 0.45
    if 'Coat Roughness' in bsdf.inputs:
        bsdf.inputs['Coat Roughness'].default_value = 0.15
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    print("[MAT] Restored Mat_BathTile_Wall (warm greige 300x600 horizontal tile)")

    # 5. Mat_Marble_White & Mat_Countertop_Granite (Crisp White Engineered Quartz)
    for mat_name in ["Mat_Marble_White", "Mat_Countertop_Granite"]:
        mat = bpy.data.materials.get(mat_name) or bpy.data.materials.new(mat_name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        nodes.clear()
        out = nodes.new('ShaderNodeOutputMaterial')
        bsdf = nodes.new('ShaderNodeBsdfPrincipled')
        tex_coord = nodes.new('ShaderNodeTexCoord')
        noise_coarse = nodes.new('ShaderNodeTexNoise')
        noise_fine = nodes.new('ShaderNodeTexNoise')
        ramp_vein = nodes.new('ShaderNodeValToRGB')
        mix = nodes.new('ShaderNodeMix')
        mix.data_type = 'RGBA'
        mix.blend_type = 'MULTIPLY'
        mix.inputs['Factor'].default_value = 0.35
        
        noise_coarse.inputs['Scale'].default_value = 4.0
        noise_coarse.inputs['Detail'].default_value = 6.0
        noise_coarse.inputs['Roughness'].default_value = 0.55
        
        ramp_vein.color_ramp.elements[0].position = 0.30
        ramp_vein.color_ramp.elements[0].color = (0.78, 0.79, 0.81, 1.0)
        ramp_vein.color_ramp.elements[1].position = 0.70
        ramp_vein.color_ramp.elements[1].color = (0.95, 0.95, 0.96, 1.0)
        
        links.new(tex_coord.outputs['Object'], noise_coarse.inputs['Vector'])
        links.new(noise_coarse.outputs['Fac'], ramp_vein.inputs['Fac'])
        
        # Base color
        rgb_base = nodes.new('ShaderNodeRGB')
        rgb_base.outputs['Color'].default_value = (0.95, 0.95, 0.96, 1.0)
        
        links.new(rgb_base.outputs['Color'], mix.inputs['A'])
        links.new(ramp_vein.outputs['Color'], mix.inputs['B'])
        links.new(mix.outputs['Result'], bsdf.inputs['Base Color'])
        
        bsdf.inputs['Roughness'].default_value = 0.14
        if 'Coat Weight' in bsdf.inputs:
            bsdf.inputs['Coat Weight'].default_value = 0.50
        if 'Coat Roughness' in bsdf.inputs:
            bsdf.inputs['Coat Roughness'].default_value = 0.15
        links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
        print(f"[MAT] Restored {mat_name} (crisp white engineered quartz)")

    # 6. Mat_Curtain (Solid Off-White Sheer Linen)
    mat_curtain = bpy.data.materials.get("Mat_Curtain") or bpy.data.materials.new("Mat_Curtain")
    mat_curtain.use_nodes = True
    nodes = mat_curtain.node_tree.nodes
    links = mat_curtain.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.92, 0.91, 0.89, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.85
    if 'Sheen Weight' in bsdf.inputs:
        bsdf.inputs['Sheen Weight'].default_value = 0.85
    if 'Sheen Tint' in bsdf.inputs:
        bsdf.inputs['Sheen Tint'].default_value = (1.0, 0.98, 0.95, 1.0)
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    print("[MAT] Restored Mat_Curtain (solid off-white sheer linen)")

    # 7. Mat_ArtWall_Tile (Polished Ivory 600x600 Porcelain Art Wall Slab)
    mat_artwall = bpy.data.materials.get("Mat_ArtWall_Tile") or bpy.data.materials.new("Mat_ArtWall_Tile")
    mat_artwall.use_nodes = True
    nodes = mat_artwall.node_tree.nodes
    links = mat_artwall.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    tex_coord = nodes.new('ShaderNodeTexCoord')
    brick = nodes.new('ShaderNodeTexBrick')
    bump = nodes.new('ShaderNodeBump')
    
    brick.offset = 0.0
    brick.inputs['Scale'].default_value = 1.0
    brick.inputs['Mortar Size'].default_value = 0.002
    brick.inputs['Row Height'].default_value = 0.60
    brick.inputs['Brick Width'].default_value = 0.60
    brick.inputs['Color1'].default_value = (0.90, 0.88, 0.85, 1.0)
    brick.inputs['Color2'].default_value = (0.92, 0.90, 0.87, 1.0)
    brick.inputs['Mortar'].default_value = (0.75, 0.73, 0.70, 1.0)
    
    bump.inputs['Strength'].default_value = 0.05
    bump.inputs['Distance'].default_value = 0.004
    
    links.new(tex_coord.outputs['Object'], brick.inputs['Vector'])
    links.new(brick.outputs['Color'], bsdf.inputs['Base Color'])
    links.new(brick.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    bsdf.inputs['Roughness'].default_value = 0.18
    if 'Coat Weight' in bsdf.inputs:
        bsdf.inputs['Coat Weight'].default_value = 0.50
    if 'Coat Roughness' in bsdf.inputs:
        bsdf.inputs['Coat Roughness'].default_value = 0.18
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    print("[MAT] Restored Mat_ArtWall_Tile (polished ivory 600x600 slab)")

    # 8. Re-assign Mat_Wall_Cap to wall tops (normal.z > 0.8)
    for o in bpy.data.objects:
        if o.type == 'MESH' and (o.name.startswith("ExactWall") or o.name.startswith("SillPatch")):
            me = o.data
            # Ensure slot 0 is interior wallpaper and slot 1 is cap
            if len(me.materials) == 0:
                me.materials.append(mat_wall)
                me.materials.append(mat_cap)
            elif len(me.materials) == 1:
                me.materials.append(mat_cap)
            else:
                me.materials[0] = mat_wall
                me.materials[1] = mat_cap
            
            cap_count = 0
            for poly in me.polygons:
                if poly.normal.z > 0.8:
                    poly.material_index = 1
                    cap_count += 1
                elif poly.material_index == 1:
                    poly.material_index = 0
            me.update()
            if cap_count > 0:
                print(f"[CAP] {o.name}: {cap_count} top faces -> Mat_Wall_Cap")

def tune_interior_lighting():
    # Boost Dress room and Bath lights for POV visibility
    lights_config = {
        "Dress_CeilingLight": ((1.60, 7.85, 2.15), 45.0, (1.0, 0.95, 0.88)),
        "BathProp_CeilingLight": ((3.45, 6.90, 2.15), 40.0, (1.0, 0.95, 0.88)),
        "Downlight_Hallway": ((11.0, 5.5, 2.25), 35.0, (1.0, 0.92, 0.82)),
        "Downlight_Living": ((6.4, 3.2, 2.25), 50.0, (1.0, 0.92, 0.82)),
        "Downlight_Dining": ((6.6, 5.2, 2.25), 40.0, (1.0, 0.92, 0.82)),
    }
    col_lights = bpy.data.collections.get("Apt_Lighting")
    for name, (loc, energy, color) in lights_config.items():
        lo = bpy.data.objects.get(name)
        if lo is None:
            ld = bpy.data.lights.new(name, 'POINT')
            lo = bpy.data.objects.new(name, ld)
            if col_lights:
                col_lights.objects.link(lo)
        lo.location = loc
        lo.data.energy = energy
        lo.data.color = color
        lo.data.shadow_soft_size = 0.15
        lo.hide_render = False
        print(f"[LIGHT] Tuned {name}: energy={energy}W @ {loc}")

def main():
    print("=== STARTING COMPREHENSIVE 84A CLEANUP & UPGRADE ===")
    fix_structure_and_openings()
    align_dining_group()
    restore_pbr_materials()
    tune_interior_lighting()
    
    # Save master file
    bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
    print("=== COMPREHENSIVE 84A CLEANUP COMPLETE & SAVED ===")

main()
