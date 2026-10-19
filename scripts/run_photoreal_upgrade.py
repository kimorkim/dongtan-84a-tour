import os
import sys
sys.path.insert(0, os.path.abspath("."))
import mcp_client


with open("scripts/assemble_photoreal_scene.py", "r", encoding="utf-8") as f:
    code = f.read()

print("Sending execute_code for assemble_photoreal_scene.py to Blender MCP with timeout=300s...")
res = mcp_client.send_blender_command('execute_code', {'code': code}, timeout=300.0)
print("Execution Result:", res)
