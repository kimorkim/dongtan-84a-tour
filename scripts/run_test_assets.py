import mcp_client

with open("scripts/generate_high_detail_assets.py", "r", encoding="utf-8") as f:
    code = f.read()

res = mcp_client.send_blender_command('execute_code', {'code': code})
print("Result:", res)
