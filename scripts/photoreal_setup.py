import bpy
import bmesh
import math
import os
import json

def setup_cycles_gpu():
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    
    # Enable GPU and OptiX
    prefs = bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type = 'OPTIX'
    prefs.get_devices()
    for d in prefs.devices:
        if d.type == 'OPTIX':
            d.use = True
            print(f"Using OptiX device: {d.name}")
        elif d.type == 'CPU':
            d.use = False
            
    scene.cycles.device = 'GPU'
    scene.cycles.preview_samples = 32
    scene.cycles.samples = 128
    scene.cycles.use_denoising = True
    scene.cycles.denoiser = 'OPTIX'
    
    # Bounces & performance
    scene.cycles.max_bounces = 12
    scene.cycles.diffuse_bounces = 4
    scene.cycles.glossy_bounces = 4
    scene.cycles.transmission_bounces = 8
    scene.cycles.transparent_max_bounces = 8
    
    # Color management
    scene.view_settings.view_transform = 'Filmic'
    scene.view_settings.look = 'Medium High Contrast'
    print("Cycles GPU OptiX successfully configured!")

print("Loaded module setup_cycles_gpu")
