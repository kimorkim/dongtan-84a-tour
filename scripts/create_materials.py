import bpy

def get_or_create_mat(name):
    mat = bpy.data.materials.get(name)
    if not mat:
        mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    return mat

def create_pbr_materials():
    # 1. Mat_Wood_LightPlank (Living, Kitchen, Corridor, Bed 2/3 - Natural Oak Wide Plank)
    mat_light_wood = get_or_create_mat("Mat_Wood_LightPlank")
    nodes = mat_light_wood.node_tree.nodes
    links = mat_light_wood.node_tree.links
    nodes.clear()
    
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    tex_coord = nodes.new('ShaderNodeTexCoord')
    mapping = nodes.new('ShaderNodeMapping')
    brick = nodes.new('ShaderNodeTexBrick')
    noise = nodes.new('ShaderNodeTexNoise')
    ramp_color = nodes.new('ShaderNodeValToRGB')
    bump = nodes.new('ShaderNodeBump')
    
    # Brick plank config (0.90m x 0.14m planks matching Prugio wide gangmaru)
    brick.inputs['Scale'].default_value = 1.0
    brick.inputs['Mortar Size'].default_value = 0.003
    brick.inputs['Mortar Smooth'].default_value = 0.05
    brick.inputs['Row Height'].default_value = 0.14
    brick.inputs['Brick Width'].default_value = 0.90
    brick.inputs['Color1'].default_value = (0.2, 0.2, 0.2, 1.0)
    brick.inputs['Color2'].default_value = (0.8, 0.8, 0.8, 1.0)
    brick.inputs['Mortar'].default_value = (0.0, 0.0, 0.0, 1.0)
    
    # Color Ramp for warm Scandinavian natural oak
    ramp_color.color_ramp.elements[0].position = 0.05
    ramp_color.color_ramp.elements[0].color = (0.64, 0.49, 0.35, 1.0) # warm oak
    ramp_color.color_ramp.elements[1].position = 0.95
    ramp_color.color_ramp.elements[1].color = (0.78, 0.64, 0.48, 1.0) # light oak highlight
    
    bump.inputs['Strength'].default_value = 0.22
    bump.inputs['Distance'].default_value = 0.008
    
    links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])
    links.new(mapping.outputs['Vector'], brick.inputs['Vector'])
    links.new(brick.outputs['Color'], ramp_color.inputs['Fac'])
    links.new(ramp_color.outputs['Color'], bsdf.inputs['Base Color'])
    links.new(brick.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    
    bsdf.inputs['Roughness'].default_value = 0.38
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    
    # 2. Mat_Wood_WarmPlank (Master Bedroom - Warm Honey Oak)
    mat_warm_wood = get_or_create_mat("Mat_Wood_WarmPlank")
    nodes = mat_warm_wood.node_tree.nodes
    links = mat_warm_wood.node_tree.links
    nodes.clear()
    
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    tex_coord = nodes.new('ShaderNodeTexCoord')
    mapping = nodes.new('ShaderNodeMapping')
    brick = nodes.new('ShaderNodeTexBrick')
    ramp_color = nodes.new('ShaderNodeValToRGB')
    bump = nodes.new('ShaderNodeBump')
    
    brick.inputs['Scale'].default_value = 1.0
    brick.inputs['Mortar Size'].default_value = 0.003
    brick.inputs['Row Height'].default_value = 0.14
    brick.inputs['Brick Width'].default_value = 0.90
    brick.inputs['Color1'].default_value = (0.2, 0.2, 0.2, 1.0)
    brick.inputs['Color2'].default_value = (0.8, 0.8, 0.8, 1.0)
    
    ramp_color.color_ramp.elements[0].position = 0.05
    ramp_color.color_ramp.elements[0].color = (0.55, 0.38, 0.22, 1.0)
    ramp_color.color_ramp.elements[1].position = 0.95
    ramp_color.color_ramp.elements[1].color = (0.72, 0.53, 0.34, 1.0)
    
    bump.inputs['Strength'].default_value = 0.20
    bump.inputs['Distance'].default_value = 0.008
    
    links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])
    links.new(mapping.outputs['Vector'], brick.inputs['Vector'])
    links.new(brick.outputs['Color'], ramp_color.inputs['Fac'])
    links.new(ramp_color.outputs['Color'], bsdf.inputs['Base Color'])
    links.new(brick.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    
    bsdf.inputs['Roughness'].default_value = 0.35
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    
    # 3. Mat_Tile_Grey (Balconies & Bathrooms - 300x300 & 300x600 Tile)
    mat_tile = get_or_create_mat("Mat_Tile_Grey")
    nodes = mat_tile.node_tree.nodes
    links = mat_tile.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    tex_coord = nodes.new('ShaderNodeTexCoord')
    brick = nodes.new('ShaderNodeTexBrick')
    bump = nodes.new('ShaderNodeBump')
    
    brick.inputs['Scale'].default_value = 1.0
    brick.inputs['Mortar Size'].default_value = 0.004
    brick.inputs['Row Height'].default_value = 0.30
    brick.inputs['Brick Width'].default_value = 0.30
    brick.inputs['Color1'].default_value = (0.46, 0.47, 0.49, 1.0)
    brick.inputs['Color2'].default_value = (0.50, 0.51, 0.53, 1.0)
    brick.inputs['Mortar'].default_value = (0.32, 0.32, 0.33, 1.0)
    
    bump.inputs['Strength'].default_value = 0.35
    bump.inputs['Distance'].default_value = 0.01
    
    links.new(tex_coord.outputs['Object'], brick.inputs['Vector'])
    links.new(brick.outputs['Color'], bsdf.inputs['Base Color'])
    links.new(brick.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    bsdf.inputs['Roughness'].default_value = 0.65
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    
    # 4. Mat_Tile_DarkSlate (Foyer Entrance 600x600 Porcelain)
    mat_slate = get_or_create_mat("Mat_Tile_DarkSlate")
    nodes = mat_slate.node_tree.nodes
    links = mat_slate.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    tex_coord = nodes.new('ShaderNodeTexCoord')
    brick = nodes.new('ShaderNodeTexBrick')
    bump = nodes.new('ShaderNodeBump')
    
    brick.inputs['Scale'].default_value = 1.0
    brick.inputs['Mortar Size'].default_value = 0.003
    brick.inputs['Row Height'].default_value = 0.60
    brick.inputs['Brick Width'].default_value = 0.60
    brick.inputs['Color1'].default_value = (0.28, 0.29, 0.31, 1.0)
    brick.inputs['Color2'].default_value = (0.32, 0.33, 0.35, 1.0)
    brick.inputs['Mortar'].default_value = (0.18, 0.18, 0.19, 1.0)
    
    bump.inputs['Strength'].default_value = 0.25
    bump.inputs['Distance'].default_value = 0.005
    
    links.new(tex_coord.outputs['Object'], brick.inputs['Vector'])
    links.new(brick.outputs['Color'], bsdf.inputs['Base Color'])
    links.new(brick.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    bsdf.inputs['Roughness'].default_value = 0.40
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    
    # 5. Mat_ArtWall_Tile (Living Room TV Feature Art Wall - 600x600 Polished Ivory Stone Tile)
    mat_artwall = get_or_create_mat("Mat_ArtWall_Tile")
    nodes = mat_artwall.node_tree.nodes
    links = mat_artwall.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    tex_coord = nodes.new('ShaderNodeTexCoord')
    brick = nodes.new('ShaderNodeTexBrick')
    noise = nodes.new('ShaderNodeTexNoise')
    ramp = nodes.new('ShaderNodeValToRGB')
    bump = nodes.new('ShaderNodeBump')
    
    brick.inputs['Scale'].default_value = 1.0
    brick.inputs['Mortar Size'].default_value = 0.002
    brick.inputs['Row Height'].default_value = 0.60
    brick.inputs['Brick Width'].default_value = 0.60
    brick.inputs['Color1'].default_value = (0.88, 0.85, 0.81, 1.0) # warm ivory
    brick.inputs['Color2'].default_value = (0.91, 0.88, 0.84, 1.0)
    brick.inputs['Mortar'].default_value = (0.65, 0.62, 0.58, 1.0)
    
    noise.inputs['Scale'].default_value = 15.0
    noise.inputs['Detail'].default_value = 3.0
    
    bump.inputs['Strength'].default_value = 0.06
    bump.inputs['Distance'].default_value = 0.005
    
    links.new(tex_coord.outputs['Object'], brick.inputs['Vector'])
    links.new(brick.outputs['Color'], bsdf.inputs['Base Color'])
    links.new(brick.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    bsdf.inputs['Roughness'].default_value = 0.22 # honed satin finish
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])

    # 6. Mat_Wall_Interior (Milk White Wallpaper - Shinhan 97451-1)
    mat_wall = get_or_create_mat("Mat_Wall_Interior")
    nodes = mat_wall.node_tree.nodes
    links = mat_wall.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.94, 0.93, 0.91, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.85
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    
    # 7. Mat_Wall_Cap (Dark Charcoal Architectural Cut Section)
    mat_cap = get_or_create_mat("Mat_Wall_Cap")
    nodes = mat_cap.node_tree.nodes
    links = mat_cap.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.12, 0.13, 0.15, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.50
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    
    # 8. Mat_Countertop_Granite (Engineered Quartz Stone Countertop & Backsplash)
    mat_counter = get_or_create_mat("Mat_Countertop_Granite")
    nodes = mat_counter.node_tree.nodes
    links = mat_counter.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    tex_coord = nodes.new('ShaderNodeTexCoord')
    noise = nodes.new('ShaderNodeTexNoise')
    ramp = nodes.new('ShaderNodeValToRGB')
    
    noise.inputs['Scale'].default_value = 40.0
    noise.inputs['Detail'].default_value = 6.0
    noise.inputs['Roughness'].default_value = 0.65
    
    ramp.color_ramp.elements[0].position = 0.2
    ramp.color_ramp.elements[0].color = (0.84, 0.85, 0.86, 1.0) # subtle quartz grey
    ramp.color_ramp.elements[1].position = 0.8
    ramp.color_ramp.elements[1].color = (0.95, 0.95, 0.96, 1.0) # crisp white base
    
    links.new(tex_coord.outputs['Object'], noise.inputs['Vector'])
    links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.16 # polished stone
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    
    # 9. Mat_Cabinet_Cashmere (Kitchen Lower/Upper Cabinets - Warm Cashmere White)
    mat_cab = get_or_create_mat("Mat_Cabinet_Cashmere")
    nodes = mat_cab.node_tree.nodes
    links = mat_cab.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.92, 0.91, 0.89, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.40 # satin PET finish
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    
    # 10. Mat_Bespoke_Glass (Samsung Bespoke Refrigerator Panels - Soft White/Cotta)
    mat_fridge = get_or_create_mat("Mat_Bespoke_Glass")
    nodes = mat_fridge.node_tree.nodes
    links = mat_fridge.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.92, 0.93, 0.94, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.10 # reflective glass panel
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    
    # 11. Mat_Fabric_Sofa (Warm Grey High-End Texture Fabric)
    mat_sofa = get_or_create_mat("Mat_Fabric_Sofa")
    nodes = mat_sofa.node_tree.nodes
    links = mat_sofa.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    tex_coord = nodes.new('ShaderNodeTexCoord')
    noise = nodes.new('ShaderNodeTexNoise')
    ramp = nodes.new('ShaderNodeValToRGB')
    
    noise.inputs['Scale'].default_value = 100.0
    noise.inputs['Detail'].default_value = 5.0
    ramp.color_ramp.elements[0].position = 0.3
    ramp.color_ramp.elements[0].color = (0.50, 0.50, 0.52, 1.0)
    ramp.color_ramp.elements[1].position = 0.7
    ramp.color_ramp.elements[1].color = (0.62, 0.63, 0.65, 1.0)
    
    links.new(tex_coord.outputs['Object'], noise.inputs['Vector'])
    links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.88
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    
    # 12. Mat_Bed_Linen (Pure White Linen Sheets)
    mat_linen = get_or_create_mat("Mat_Bed_Linen")
    nodes = mat_linen.node_tree.nodes
    links = mat_linen.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.96, 0.96, 0.97, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.75
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    
    # 13. Mat_Bed_Runner (Warm Gold / Lavender Accent)
    mat_runner = get_or_create_mat("Mat_Bed_Runner")
    nodes = mat_runner.node_tree.nodes
    links = mat_runner.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.80, 0.68, 0.38, 1.0) # warm mustard gold
    bsdf.inputs['Roughness'].default_value = 0.70
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    
    # 14. Mat_Wood_Walnut (Dining Table, Doors, TV Console)
    mat_walnut = get_or_create_mat("Mat_Wood_Walnut")
    nodes = mat_walnut.node_tree.nodes
    links = mat_walnut.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.42, 0.28, 0.16, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.35
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    
    # 15. Mat_Chrome_Metal (Faucets, Door Handles)
    mat_chrome = get_or_create_mat("Mat_Chrome_Metal")
    nodes = mat_chrome.node_tree.nodes
    links = mat_chrome.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.95, 0.95, 0.95, 1.0)
    bsdf.inputs['Metallic'].default_value = 1.0
    bsdf.inputs['Roughness'].default_value = 0.10
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    
    # 16. Mat_Glass_Clear (Windows & Shower Booth)
    mat_glass = get_or_create_mat("Mat_Glass_Clear")
    nodes = mat_glass.node_tree.nodes
    links = mat_glass.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.95, 0.98, 1.0, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.02
    bsdf.inputs['IOR'].default_value = 1.52
    if 'Transmission Weight' in bsdf.inputs:
        bsdf.inputs['Transmission Weight'].default_value = 1.0
    elif 'Transmission' in bsdf.inputs:
        bsdf.inputs['Transmission'].default_value = 1.0
    mat_glass.blend_method = 'BLEND'
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    
    # 17. Mat_Window_Frame (Dark Charcoal Aluminum)
    mat_frame = get_or_create_mat("Mat_Window_Frame")
    nodes = mat_frame.node_tree.nodes
    links = mat_frame.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.16, 0.17, 0.19, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.3
    bsdf.inputs['Roughness'].default_value = 0.40
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    
    # 18. Mat_Door_Blue (Navy Entrance Door like 84A.jpg)
    mat_blue = get_or_create_mat("Mat_Door_Blue")
    nodes = mat_blue.node_tree.nodes
    links = mat_blue.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.07, 0.18, 0.32, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.35
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    
    # 19. Mat_Ceramic_White (Toilet, Bathtub, Basins)
    mat_ceramic = get_or_create_mat("Mat_Ceramic_White")
    nodes = mat_ceramic.node_tree.nodes
    links = mat_ceramic.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.97, 0.97, 0.98, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.08
    if 'Coat Weight' in bsdf.inputs:
        bsdf.inputs['Coat Weight'].default_value = 0.8
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    
    # 20. Mat_Screen_OLED (TV Screen)
    mat_screen = get_or_create_mat("Mat_Screen_OLED")
    nodes = mat_screen.node_tree.nodes
    links = mat_screen.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.02, 0.02, 0.02, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.05
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])

    # 21. Mat_Light_Warm_Strip (Under-cabinet linear LED lighting - 3000K warm white)
    mat_led = get_or_create_mat("Mat_Light_Warm_Strip")
    nodes = mat_led.node_tree.nodes
    links = mat_led.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    emission = nodes.new('ShaderNodeEmission')
    emission.inputs['Color'].default_value = (1.0, 0.92, 0.80, 1.0)
    emission.inputs['Strength'].default_value = 15.0
    links.new(emission.outputs['Emission'], out.inputs['Surface'])

    # 22. Mat_Curtain (Living Room & Bedroom sheer drapes)
    mat_curtain = get_or_create_mat("Mat_Curtain")
    nodes = mat_curtain.node_tree.nodes
    links = mat_curtain.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.80, 0.78, 0.74, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.92
    if 'Sheen Weight' in bsdf.inputs:
        bsdf.inputs['Sheen Weight'].default_value = 0.8
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    
    # 23. Mat_Hood_Metal (Range Hood Dark Metal)
    mat_hood = get_or_create_mat("Mat_Hood_Metal")
    nodes = mat_hood.node_tree.nodes
    links = mat_hood.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.22, 0.23, 0.25, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.8
    bsdf.inputs['Roughness'].default_value = 0.30
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    
    print("All PBR Materials successfully created!")


def _principled(mat):
    for n in mat.node_tree.nodes:
        if n.type == 'BSDF_PRINCIPLED':
            return n
    return None


def upgrade_floor_and_artwall():
    """In-place texture upgrade: finer floor grain/roughness, polished artwall."""
    # --- Wood floors: fine grain noise driving roughness + blended bump detail ---
    for name in ("Mat_Wood_LightPlank", "Mat_Wood_WarmPlank"):
        mat = bpy.data.materials.get(name)
        if not mat:
            continue
        nodes, links = mat.node_tree.nodes, mat.node_tree.links
        for stale in [n for n in nodes if n.name.startswith("UPG_")]:
            nodes.remove(stale)
        bsdf = _principled(mat)
        bump = next((n for n in nodes if n.type == 'BUMP'), None)
        if not bsdf or not bump:
            continue
        grain = nodes.new('ShaderNodeTexNoise')
        grain.name = "UPG_Grain"
        grain.inputs['Scale'].default_value = 90.0
        grain.inputs['Detail'].default_value = 5.0
        grain.inputs['Roughness'].default_value = 0.55
        tex = next((n for n in nodes if n.type in ('TEX_COORD', 'TEXCOORD')), None)
        if tex is None:
            tex = next((n for n in nodes if 'Coord' in n.bl_idname), None)
        if tex:
            links.new(tex.outputs['Object'], grain.inputs['Vector'])
        rough_ramp = nodes.new('ShaderNodeValToRGB')
        rough_ramp.name = "UPG_RoughRamp"
        rough_ramp.color_ramp.elements[0].position = 0.15
        rough_ramp.color_ramp.elements[0].color = (0.30, 0.30, 0.30, 1.0)
        rough_ramp.color_ramp.elements[1].position = 0.85
        rough_ramp.color_ramp.elements[1].color = (0.50, 0.50, 0.50, 1.0)
        links.new(grain.outputs['Fac'], rough_ramp.inputs['Fac'])
        links.new(rough_ramp.outputs['Color'], bsdf.inputs['Roughness'])
        # Blend plank gaps (brick Fac) with grain for finer relief
        bump_src = bump.inputs['Height'].links[0].from_socket if bump.inputs['Height'].links else None
        if bump_src:
            mix = nodes.new('ShaderNodeMix')
            mix.name = "UPG_BumpMix"
            mix.data_type = 'FLOAT'
            mix.blend_type = 'MIX'
            mix.inputs['Factor'].default_value = 0.35
            links.new(bump_src, mix.inputs['A'])
            links.new(grain.outputs['Fac'], mix.inputs['B'])
            links.new(mix.outputs['Result'], bump.inputs['Height'])
        bump.inputs['Strength'].default_value = 0.30
        bump.inputs['Distance'].default_value = 0.004
        print(f"Upgraded {name}: grain roughness + fine bump")

    # --- Artwall: polished stone sheen with subtle veining ---
    mat = bpy.data.materials.get("Mat_ArtWall_Tile")
    if mat:
        nodes, links = mat.node_tree.nodes, mat.node_tree.links
        for stale in [n for n in nodes if n.name.startswith("UPG_")]:
            nodes.remove(stale)
        bsdf = _principled(mat)
        brick = next((n for n in nodes if 'Brick' in n.bl_idname), None)
        if bsdf and brick:
            bsdf.inputs['Roughness'].default_value = 0.12
            if 'Coat Weight' in bsdf.inputs:
                bsdf.inputs['Coat Weight'].default_value = 0.55
            if 'Coat Roughness' in bsdf.inputs:
                bsdf.inputs['Coat Roughness'].default_value = 0.18
            brick.inputs['Mortar Size'].default_value = 0.0015
            vein = nodes.new('ShaderNodeTexNoise')
            vein.name = "UPG_Vein"
            vein.inputs['Scale'].default_value = 6.0
            vein.inputs['Detail'].default_value = 3.0
            tex = next((n for n in nodes if 'Coord' in n.bl_idname), None)
            if tex:
                links.new(tex.outputs['Object'], vein.inputs['Vector'])
            vramp = nodes.new('ShaderNodeValToRGB')
            vramp.name = "UPG_VeinRamp"
            vramp.color_ramp.elements[0].position = 0.25
            vramp.color_ramp.elements[0].color = (0.90, 0.90, 0.90, 1.0)
            vramp.color_ramp.elements[1].position = 0.75
            vramp.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1.0)
            links.new(vein.outputs['Fac'], vramp.inputs['Fac'])
            base_src = bsdf.inputs['Base Color'].links[0].from_socket if bsdf.inputs['Base Color'].links else None
            if base_src:
                mix = nodes.new('ShaderNodeMix')
                mix.name = "UPG_BaseMix"
                mix.data_type = 'RGBA'
                mix.blend_type = 'MULTIPLY'
                mix.inputs['Factor'].default_value = 0.35
                links.new(base_src, mix.inputs['A'])
                links.new(vramp.outputs['Color'], mix.inputs['B'])
                links.new(mix.outputs['Result'], bsdf.inputs['Base Color'])
            print("Upgraded Mat_ArtWall_Tile: polished coat + veining")


def _solid_mat(name, color, roughness=0.6, metallic=0.0):
    mat = get_or_create_mat(name)
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (*color, 1.0)
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = metallic
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat


def create_detail_materials():
    """Materials for enhancement props: pendants, books, steel, fruits, office."""
    # Pendant shade (matte charcoal) + warm bulb emissive
    _solid_mat("Mat_Pendant_Black", (0.10, 0.10, 0.11), roughness=0.45, metallic=0.25)

    mat_bulb = get_or_create_mat("Mat_Bulb_Warm")
    nodes, links = mat_bulb.node_tree.nodes, mat_bulb.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    emission = nodes.new('ShaderNodeEmission')
    emission.inputs['Color'].default_value = (1.0, 0.82, 0.62, 1.0)
    emission.inputs['Strength'].default_value = 6.0
    links.new(emission.outputs['Emission'], out.inputs['Surface'])

    # Laptop screen (soft cool glow, low emission so it reads as on)
    mat_lap = get_or_create_mat("Mat_Laptop_Screen")
    nodes, links = mat_lap.node_tree.nodes, mat_lap.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    emission = nodes.new('ShaderNodeEmission')
    emission.inputs['Color'].default_value = (0.82, 0.89, 0.95, 1.0)
    emission.inputs['Strength'].default_value = 1.2
    links.new(emission.outputs['Emission'], out.inputs['Surface'])

    # Brushed stainless steel (pot, kettle)
    _solid_mat("Mat_Steel_Brushed", (0.72, 0.73, 0.74), roughness=0.32, metallic=1.0)
    # AC condenser body + dark grill
    _solid_mat("Mat_AC_Body", (0.80, 0.81, 0.82), roughness=0.45, metallic=0.15)
    _solid_mat("Mat_AC_Grill", (0.16, 0.17, 0.18), roughness=0.60)
    # Table runner mat (natural woven beige)
    _solid_mat("Mat_TableRunner", (0.78, 0.72, 0.62), roughness=0.90)
    # Canvas + vase + plume
    _solid_mat("Mat_Canvas_Art", (0.93, 0.92, 0.89), roughness=0.85)
    _solid_mat("Mat_Vase_Ceramic", (0.88, 0.86, 0.82), roughness=0.25)
    _solid_mat("Mat_Plume", (0.82, 0.76, 0.64), roughness=0.95)
    # Fruit orange
    _solid_mat("Mat_Fruit_Orange", (0.95, 0.48, 0.10), roughness=0.55)
    # Office rug (muted warm grey)
    _solid_mat("Mat_Rug_Office", (0.62, 0.60, 0.57), roughness=0.96)
    # Evacuation sign plate (safety red)
    _solid_mat("Mat_Sign_Red", (0.75, 0.10, 0.08), roughness=0.40)
    # White aluminum window frames (e-modelhouse)
    _solid_mat("Mat_WindowFrame_White", (0.90, 0.91, 0.92), roughness=0.35, metallic=0.10)
    # Built-in oven black glass + flat hood matte black + railing dark metal
    _solid_mat("Mat_Oven_Black", (0.02, 0.02, 0.02), roughness=0.06)
    _solid_mat("Mat_Hood_Black", (0.05, 0.05, 0.06), roughness=0.40, metallic=0.30)
    _solid_mat("Mat_Rail_Dark", (0.15, 0.15, 0.16), roughness=0.50, metallic=0.60)

    # Polished white marble (countertop, backsplash, sill caps, console top)
    mat_marble = get_or_create_mat("Mat_Marble_White")
    nodes, links = mat_marble.node_tree.nodes, mat_marble.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    tex_coord = nodes.new('ShaderNodeTexCoord')
    vein = nodes.new('ShaderNodeTexNoise')
    vein.inputs['Scale'].default_value = 3.5
    vein.inputs['Detail'].default_value = 5.0
    vein.inputs['Roughness'].default_value = 0.60
    vramp = nodes.new('ShaderNodeValToRGB')
    vramp.color_ramp.elements[0].position = 0.35
    vramp.color_ramp.elements[0].color = (0.72, 0.73, 0.74, 1.0)
    vramp.color_ramp.elements[1].position = 0.75
    vramp.color_ramp.elements[1].color = (0.96, 0.96, 0.97, 1.0)
    soft = nodes.new('ShaderNodeTexNoise')
    soft.inputs['Scale'].default_value = 14.0
    soft.inputs['Detail'].default_value = 3.0
    sramp = nodes.new('ShaderNodeValToRGB')
    sramp.color_ramp.elements[0].position = 0.3
    sramp.color_ramp.elements[0].color = (0.93, 0.93, 0.94, 1.0)
    sramp.color_ramp.elements[1].position = 0.7
    sramp.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1.0)
    mix = nodes.new('ShaderNodeMix')
    mix.data_type = 'RGBA'
    mix.blend_type = 'MULTIPLY'
    mix.inputs['Factor'].default_value = 0.55
    links.new(tex_coord.outputs['Object'], vein.inputs['Vector'])
    links.new(tex_coord.outputs['Object'], soft.inputs['Vector'])
    links.new(vein.outputs['Fac'], vramp.inputs['Fac'])
    links.new(soft.outputs['Fac'], sramp.inputs['Fac'])
    links.new(vramp.outputs['Color'], mix.inputs['A'])
    links.new(sramp.outputs['Color'], mix.inputs['B'])
    links.new(mix.outputs['Result'], bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.12
    if 'Coat Weight' in bsdf.inputs:
        bsdf.inputs['Coat Weight'].default_value = 0.45
    if 'Coat Roughness' in bsdf.inputs:
        bsdf.inputs['Coat Roughness'].default_value = 0.20
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    # Book / cloth accent palette (muted editorial tones)
    for bname, col in [
        ("Mat_Book_Navy", (0.16, 0.24, 0.38)),
        ("Mat_Book_Terracotta", (0.66, 0.32, 0.22)),
        ("Mat_Book_Sage", (0.52, 0.58, 0.46)),
        ("Mat_Book_Mustard", (0.78, 0.62, 0.30)),
        ("Mat_Book_Charcoal", (0.25, 0.25, 0.27)),
        ("Mat_Book_Cream", (0.88, 0.85, 0.78)),
    ]:
        _solid_mat(bname, col, roughness=0.75)

    print("All detail prop materials created!")


if __name__ == "__main__":
    create_pbr_materials()
    create_detail_materials()
    upgrade_floor_and_artwall()
