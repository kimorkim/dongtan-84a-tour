"""Q22 release regression against the saved source; no mutation or save."""
from pathlib import Path
import runpy

root=Path(__file__).resolve().parents[2]
for name in ('dimensions','alpha_room','utility_room','foyer','common_bath','flooring','yuna_room',
             'study_room','study_bookcases','brest_sofa','living_finish','kitchen_finish',
             'living_tv_stand','lg_lightwave_oven','living_soundbar','utility_turning_door',
             'lg_washtower','restandard_bed'):
    runpy.run_path(str(root/'scripts'/('verify_'+name+'.py')),run_name='__main__')
print('PASS Q22: all 18 saved Blender regression scripts')
