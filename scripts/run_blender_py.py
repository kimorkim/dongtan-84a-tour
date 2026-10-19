import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mcp_client, json

which = sys.argv[1] if len(sys.argv) > 1 else "wire"
path = {"wire": "wire_pbr_textures.py", "lit": "tune_lighting.py",
        "door": "hang_doors.py", "base": "add_baseboards.py",
        "glb": "export_glb_flat.py", "bake": "bake_collision.py",
        "glbtex": "export_glb_textured.py"}[which]
with open(os.path.join(os.path.dirname(__file__), path), "r", encoding="utf-8") as f:
    code = f.read()
res = mcp_client.send_blender_command('execute_code', {'code': code}, timeout=180.0)
print(json.dumps(res, ensure_ascii=False)[:6000])
