import runpy
runpy.run_path('scripts/render_calibrated_gallery.py',init_globals={'RENDER_BATCH':[
    'render_29_oak_living.png','render_3_kitchen_dining_pov.png','render_9_kitchen_prep_pov.png',
    'render_4_master_bedroom_pov.png','render_7_dress_pov.png']})
