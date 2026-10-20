import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mcp_client, json

BATCH = ["render_1_isometric_topdown.png", "render_2_living_room_pov.png"]
with open(os.path.join(os.path.dirname(__file__), "render_present_views.py"), "r", encoding="utf-8") as f:
    code = f.read()
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
prelude = "RENDER_BATCH = %r\nPREVIEW = True\nRENDER_DIR = %r\n" % (BATCH, os.path.join(root, "renders", "previews"))
res = mcp_client.send_blender_command('execute_code', {'code': prelude + code}, timeout=300.0)
print(json.dumps(res, ensure_ascii=False)[:2000])
