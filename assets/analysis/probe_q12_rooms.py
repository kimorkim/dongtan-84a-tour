import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'scripts'))
import bpy
from verify_calibrated_rooms import verify_room,bounds
for tag in ('alpha','utility','foyer','bath','floor','yuna','study'):
    try: verify_room(tag)
    except Exception as e: print('FAIL',tag,repr(e))
for name in ('Q7_MiddleDoor_Glass','Q10_Wardrobe_Back','Q8_Toilet_Body','Q11_AeronBlack_SeatFrame'):
    print(name,bounds(bpy.data.objects[name]))
