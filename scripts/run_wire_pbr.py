import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mcp_client

with open(os.path.join(os.path.dirname(__file__), "wire_pbr_textures.py"), "r", encoding="utf-8") as f:
    code = f.read()

res = mcp_client.send_blender_command('execute_code', {'code': code}, timeout=180.0)
import json
s = json.dumps(res, ensure_ascii=False)
print(s[:8000])
