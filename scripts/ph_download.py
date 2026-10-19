import json, os, urllib.request, sys

ROOT = r"C:\Users\tamarand\orca\projects\apt\assets\textures"
os.makedirs(ROOT, exist_ok=True)

def get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))

ALIASES = {
    "diffuse": ["diffuse", "diff", "albedo", "col"],
    "nor": ["nor_gl", "normal", "nor"],
    "rough": ["rough"],
    "ao": ["ao", "ambientocclusion"],
}

def pick(files, res, kinds):
    """files: {Map: {res: {fmt: {url}}}}; return [(filename, url)]"""
    out = []
    for kind in kinds:
        found = None
        for mapname, reses in files.items():
            ml = mapname.lower()
            if any(a in ml for a in ALIASES[kind]):
                r = reses.get(res) or reses.get("1k")
                if r and "jpg" in r:
                    found = r["jpg"]["url"]
                    break
        if found:
            out.append((found.rsplit("/", 1)[-1], found))
    return out

WANT = {
    "beige_wall_001": ("1k", ["diffuse", "nor", "rough", "ao"]),
    "white_plaster_02": ("1k", ["diffuse", "nor", "rough", "ao"]),
    "laminate_floor_02": ("2k", ["diffuse", "nor", "rough", "ao"]),
    "laminate_floor_03": ("1k", ["diffuse", "nor", "rough", "ao"]),
    "fabric_pattern_07": ("1k", ["diffuse", "nor", "rough", "ao"]),
    "marble_01": ("2k", ["diffuse", "nor", "rough", "ao"]),
    "floor_tiles_06": ("1k", ["diffuse", "nor", "rough", "ao"]),
    "marble_tiles": ("1k", ["diffuse", "nor", "rough", "ao"]),
    "floor_tiles_02": ("1k", ["diffuse", "nor", "rough", "ao"]),
}

def dl(url, path):
    if os.path.exists(path) and os.path.getsize(path) > 10000:
        print(f"  skip {os.path.basename(path)}")
        return
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=120) as r, open(path, "wb") as f:
        while True:
            chunk = r.read(65536)
            if not chunk:
                break
            f.write(chunk)
    print(f"  got {os.path.basename(path)} {os.path.getsize(path)//1024}KB")

for aid, (res, kinds) in WANT.items():
    d = os.path.join(ROOT, aid)
    os.makedirs(d, exist_ok=True)
    print(f"== {aid} {res} ==", flush=True)
    try:
        files = get_json(f"https://api.polyhaven.com/files/{aid}")
        items = pick(files, res, kinds)
        print(f"  files: {[i[0] for i in items]}", flush=True)
        for fn, url in items:
            dl(url, os.path.join(d, fn))
    except Exception as e:
        print(f"  ERR {e}", flush=True)

# HDRI: pick top daylight sky
print("== HDRI search ==", flush=True)
try:
    hdris = get_json("https://api.polyhaven.com/assets?t=hdris")
    cands = []
    for aid, info in hdris.items():
        blob = (info.get("name", "") + " " + " ".join(info.get("tags", []))).lower()
        if any(k in blob for k in ["pure sky", "clear sky", "day", "noon", "morning", "sunny"]):
            cands.append((info.get("download_count", 0), aid, info.get("name")))
    cands.sort(reverse=True)
    for dl_, aid, name in cands[:8]:
        print(f"  {aid} | dl={dl_} | {name}")
    if cands:
        aid = cands[0][1]
        files = get_json(f"https://api.polyhaven.com/files/{aid}")
        d = os.path.join(ROOT, aid)
        os.makedirs(d, exist_ok=True)
        got = False
        for mapname, reses in files.items():
            r = reses.get("1k") or reses.get("2k")
            if r and "hdr" in r:
                url = r["hdr"]["url"]
                print(f"== HDRI {aid} ==", flush=True)
                dl(url, os.path.join(d, url.rsplit("/", 1)[-1]))
                got = True
                break
        if not got:
            print(f"  HDRI maps: {list(files.keys())}")
except Exception as e:
    print(f"  HDRI ERR {e}", flush=True)
print("DONE", flush=True)
