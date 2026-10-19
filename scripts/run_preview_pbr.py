import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mcp_client, json

BATCH = [
    "render_1_isometric_topdown.png",
    "render_2_living_room_pov.png",
    "render_3_kitchen_dining_pov.png",
    "render_4_master_bedroom_pov.png",
    "render_5_foyer_corridor_pov.png",
    "render_6_kitchen_reverse.png",
    "render_7_dress_pov.png",
    "render_8_bath_pov.png",
]

with open(os.path.join(os.path.dirname(__file__), "render_present_views.py"), "r", encoding="utf-8") as f:
    code = f.read()

prelude = (
    "RENDER_BATCH = %r\nPREVIEW = True\nRENDER_DIR = %r\n"
    % (BATCH, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "previews_pbr"))
)
os.makedirs(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "previews_pbr"), exist_ok=True)
res = mcp_client.send_blender_command('execute_code', {'code': prelude + code}, timeout=300.0)
s = json.dumps(res, ensure_ascii=False)
print(s[:4000])
