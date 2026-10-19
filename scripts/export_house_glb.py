"""Export the apartment to web/public/house.glb for the Three.js tour.

Run inside Blender (via MCP execute_code). Overwrites the previous export.
Blender lights/cameras are excluded (three.js authors its own).
"""
import bpy
import os

# Resolve workspace: script dir's parent, else CWD
here = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else os.getcwd()
root = os.path.dirname(here) if os.path.basename(here) == "scripts" else here
out_dir = os.path.join(root, "web", "public")
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, "house.glb")

hidden = []
for o in bpy.data.objects:
    if o.type in ('LIGHT', 'CAMERA'):
        hidden.append((o, o.hide_viewport, o.hide_render))
        o.hide_viewport = True
        o.hide_render = True

print(f"Exporting GLB to {out_path} ...")
bpy.ops.export_scene.gltf(
    filepath=out_path,
    export_format='GLB',
    use_selection=False,
    export_apply=True,
)
for o, hv, hr in hidden:
    o.hide_viewport = hv
    o.hide_render = hr

size = os.path.getsize(out_path)
print(f"SUCCESS: house.glb exported ({size / 1024 / 1024:.2f} MB)")
