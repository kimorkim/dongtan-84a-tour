import runpy,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
for n in ['verify_kitchen_finish','verify_dimensions','verify_alpha_room','verify_utility_room','verify_foyer','verify_common_bath','verify_flooring','verify_yuna_room','verify_study_room','verify_study_bookcases','verify_brest_sofa','verify_living_finish']:
 print('CHECK',n,flush=True);runpy.run_path(str(ROOT/'scripts'/f'{n}.py'))
runpy.run_path(str(ROOT/'scripts/bake_collision.py'))
