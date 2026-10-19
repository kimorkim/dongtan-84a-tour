import json, urllib.request, sys

req = urllib.request.Request(
    "https://api.polyhaven.com/assets?t=textures",
    headers={"User-Agent": "Mozilla/5.0"})
print("fetching...", flush=True)
with urllib.request.urlopen(req, timeout=120) as r:
    raw = r.read()
print(f"bytes={len(raw)}", flush=True)
data = json.loads(raw.decode("utf-8"))
print(f"assets={len(data)}", flush=True)

queries = {
    "PLASTER": ["plaster", "stucco", "wallpaper"],
    "WOODFLOOR": ["wood floor", "hardwood", "planks", "parquet"],
    "FABRIC": ["fabric", "linen", "sofa", "upholstery"],
    "MARBLE": ["marble"],
    "TILE": ["tile", "bathroom"],
    "CONCRETE": ["concrete"],
    "STONE": ["limestone", "sandstone", "travertine", "slate"],
}
for label, kws in queries.items():
    print(f"=== {label} ===")
    n = 0
    for aid, info in sorted(data.items(), key=lambda kv: -kv[1].get("download_count", 0)):
        blob = " ".join([
            info.get("name", ""),
            " ".join(info.get("categories", [])),
            " ".join(info.get("tags", [])),
        ]).lower()
        if any(k in blob for k in kws):
            print(f"  {aid} | dl={info.get('download_count')} | {info.get('name')}")
            n += 1
            if n >= 12:
                break
sys.stdout.flush()
