import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mcp_client, json

with open(os.path.join(os.path.dirname(__file__), "render_present_views.py"), "r", encoding="utf-8") as f:
    code = f.read()
# full HQ batch: all views, 180sp, 1600x1200, to project root
res = mcp_client.send_blender_command('execute_code', {'code': code}, timeout=280.0)
print(json.dumps(res, ensure_ascii=False)[:3000])
