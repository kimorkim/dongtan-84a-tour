"""Export web GLB with flattened materials (idempotent, non-destructive).

Image-PBR materials don't survive glTF (Object/Box mapping ignored), so
flatten the 14 wired materials to matching flat colors, export, then
RELOAD the saved blend to restore the full PBR setup. Saved file keeps PBR.
Run inside Blender.
"""
import bpy
import os

FLAT = {
    "Mat_Wall_Interior": ((0.93, 0.90, 0.86), 0.90),
    "Mat_Wall_Cap": ((0.92, 0.89, 0.85), 0.90),
    "Mat_Ceiling_Plaster": ((0.93, 0.92, 0.90), 0.95),
    "Mat_Wood_LightPlank": ((0.70, 0.52, 0.36), 0.60),
    "Mat_Wood_WarmPlank": ((0.50, 0.35, 0.24), 0.65),
    "Mat_Tile_Grey": ((0.58, 0.56, 0.54), 0.50),
    "Mat_Tile_DarkSlate": ((0.42, 0.42, 0.44), 0.50),
    "Mat_BathTile_Wall": ((0.63, 0.61, 0.59), 0.45),
    "Mat_Fabric_Sofa": ((0.72, 0.70, 0.67), 0.90),
    "Mat_Bed_Linen": ((0.96, 0.95, 0.93), 0.90),
    "Mat_BedSheet": ((0.96, 0.95, 0.93), 0.90),
    "Mat_Pillow": ((0.95, 0.94, 0.92), 0.90),
    "Mat_Bed_Runner": ((0.87, 0.82, 0.70), 0.90),
    "Mat_Curtain": ((0.90, 0.87, 0.80), 0.90),
    "Mat_ArtWall_Tile": ((0.78, 0.72, 0.62), 0.40),
    "Mat_Marble_White": ((0.94, 0.93, 0.90), 0.35),
}

saved = bpy.data.filepath
assert saved and os.path.exists(saved), "blend must be saved first"
print(f"[GLB] working file: {saved}")

n = 0
for name, (col, rough) in FLAT.items():
    m = bpy.data.materials.get(name)
    if m is None:
        print(f"[GLB] missing {name}")
        continue
    m.use_nodes = True
    m.node_tree.nodes.clear()
    nodes, links = m.node_tree.nodes, m.node_tree.links
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = (col[0], col[1], col[2], 1.0)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = 0.0
    out = nodes.new("ShaderNodeOutputMaterial")
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    n += 1
print(f"[GLB] flattened {n} materials")

root = os.path.dirname(saved)
out_path = os.path.join(root, "web", "public", "house.glb")
os.makedirs(os.path.dirname(out_path), exist_ok=True)

hidden = []
for o in bpy.data.objects:
    if o.type in ('LIGHT', 'CAMERA'):
        hidden.append(o)
        o.hide_viewport = True
        o.hide_render = True
bpy.ops.export_scene.gltf(filepath=out_path, export_format='GLB',
                          use_selection=False, export_apply=True)
size = os.path.getsize(out_path)
print(f"[GLB] exported {size / 1024 / 1024:.2f} MB -> {out_path}")

bpy.ops.wm.open_mainfile(filepath=saved)
print("[GLB] reloaded saved blend (PBR restored, flatten discarded)")
