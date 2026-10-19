import json, urllib.request, sys

def search(q, limit=40):
    url = f"https://ambientcg.com/api/v2/list?search={q}&limit={limit}&offset=0"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.loads(r.read().decode("utf-8"))
    print(f"=== {q} ({len(data.get('foundAssets', []))}) ===")
    for a in data.get("foundAssets", []):
        print(" ", a.get("assetId"), "|", a.get("displayName"), "| dl:", a.get("downloadCount"))
    sys.stdout.flush()

for q in ["Plaster", "WoodFloor", "Wood", "Fabric", "Marble", "Tile", "Concrete", "Wallpaper"]:
    try:
        search(q)
    except Exception as e:
        print(f"=== {q} ERR {e}")
