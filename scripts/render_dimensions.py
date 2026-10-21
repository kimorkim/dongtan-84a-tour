"""Q12 whole-unit footprint review, generated without saving review settings."""
import os
import bpy
from mathutils import Vector
root=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sc=bpy.context.scene
for o in bpy.data.objects:
    if o.name.startswith(('Ceiling_','Cove_','Q10_Ceiling','Q11_Ceiling')) or o.name=='Ground_Presentation':
        o.hide_render=True
camera=bpy.data.cameras.new('Q12_Review'); obj=bpy.data.objects.new(camera.name,camera)
sc.collection.objects.link(obj); obj.location=(7.7,5.3,24)
obj.rotation_euler=(Vector((7.7,5.3,0))-obj.location).to_track_quat('-Z','Y').to_euler()
camera.type='ORTHO'; camera.ortho_scale=17.5; sc.camera=obj
sc.render.engine='BLENDER_WORKBENCH'; sc.display.shading.light='STUDIO'
sc.display.shading.color_type='MATERIAL'; sc.display.shading.show_shadows=True
sc.display.shading.show_cavity=True; sc.display.shading.cavity_type='BOTH'
sc.display.shading.background_type='WORLD'; sc.world.color=(.8,.8,.8)
sc.render.resolution_x=1400; sc.render.resolution_y=1100; sc.render.resolution_percentage=100
sc.render.filepath=os.path.join(root,'renders/review/render_36_dimensioned_plan.png')
bpy.ops.render.render(write_still=True)
print('Q12 whole-unit footprint review rendered; master not saved')
