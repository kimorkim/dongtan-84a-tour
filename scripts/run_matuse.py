import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mcp_client, json

code = '''
import bpy, json
targets = ["Mat_Wall_Interior","Mat_Wall_Cap","Mat_Wood_WarmPlank","Mat_Wood_LightPlank",
"Mat_Tile_Grey","Mat_TileFloor","Mat_DarkTile","Mat_Tile_DarkSlate","Mat_KitchenTop",
"Mat_Countertop_Granite","Mat_Fabric_Sofa","Mat_FabricSofa","Mat_ArtWall_Tile",
"Mat_Marble_White","Mat_Ceramic_White","Mat_Cabinet_Cashmere","Mat_DoorWood","Mat_Door_Blue"]
out = {}
for mname in targets:
    m = bpy.data.materials.get(mname)
    if not m:
        out[mname] = "MISSING"
        continue
    users = []
    for o in bpy.data.objects:
        if o.type == "MESH" and o.data and m.name in [s.name if s else "" for s in o.data.materials]:
            users.append(o.name)
    out[mname] = users[:20]
print("MATUSE:" + json.dumps(out))
'''
res = mcp_client.send_blender_command('execute_code', {'code': code}, timeout=60.0)
s = json.dumps(res, ensure_ascii=False)
i = s.find("MATUSE:")
print(s[i:i+5000] if i >= 0 else s[:3000])
