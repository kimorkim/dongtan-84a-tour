import bpy
import os

def setup_baseline():
    # 1. Ensure existing objects are preserved in _DefaultObjects collection
    default_col = bpy.data.collections.get("_DefaultObjects")
    if not default_col:
        init_col = bpy.data.collections.get("Collection")
        if init_col:
            init_col.name = "_DefaultObjects"
            default_col = init_col
        else:
            default_col = bpy.data.collections.new("_DefaultObjects")
            bpy.context.scene.collection.children.link(default_col)

    if default_col.name not in bpy.context.scene.collection.children:
        bpy.context.scene.collection.children.link(default_col)

    for obj_name in ["Cube", "Light", "Camera"]:
        obj = bpy.data.objects.get(obj_name)
        if obj:
            if obj.name not in default_col.objects:
                default_col.objects.link(obj)
            for col in list(obj.users_collection):
                if col != default_col:
                    col.objects.unlink(obj)
            obj.hide_viewport = True
            obj.hide_render = True

    default_col.hide_viewport = True
    default_col.hide_render = True

    # 2. Create structural collections
    for col_name in ["Apt_Floors", "Apt_OuterWalls", "Apt_InteriorWalls", "Apt_Openings"]:
        col = bpy.data.collections.get(col_name)
        if not col:
            col = bpy.data.collections.new(col_name)
            bpy.context.scene.collection.children.link(col)
        elif col.name not in bpy.context.scene.collection.children:
            bpy.context.scene.collection.children.link(col)

    # 3. Save baseline blend
    save_path = os.path.abspath("models/archive/apt_v00_initial.blend")
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=save_path)
    print(f"SUCCESS: Baseline configured and saved to {save_path}")

setup_baseline()
