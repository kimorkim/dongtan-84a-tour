import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mcp_client, json

code = '''
import bpy
m = bpy.data.materials.get("Mat_Wall_Interior")
imgs = [n.image.name if n.image else "?" for n in m.node_tree.nodes if n.type == "TEX_IMAGE"]
print("RESTORE_CHECK nodes=%d images=%s" % (len(m.node_tree.nodes), imgs[:2]))
print("DOORS_EXIST ProDoorLeaf_Bed2=%s ProBaseboards=%s" % (
    bpy.data.objects.get("ProDoorLeaf_Bed2") is not None,
    bpy.data.objects.get("ProBaseboards") is not None))
'''
res = mcp_client.send_blender_command('execute_code', {'code': code}, timeout=60.0)
s = json.dumps(res, ensure_ascii=False)
i = s.find("RESTORE_CHECK")
print(s[i:i+800] if i >= 0 else s[:1500])
