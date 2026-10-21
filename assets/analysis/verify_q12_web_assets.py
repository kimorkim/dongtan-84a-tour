"""Compare the final model, collisions and all gallery images across export/build/HTTP."""
from pathlib import Path
from hashlib import sha256
from urllib.request import urlopen
root=Path(__file__).resolve().parents[2]
public=root/'web/public'; dist=root/'web/dist'
files=[Path('house.glb'),Path('colliders.json')]
files.extend(p.relative_to(public) for p in (public/'gallery').rglob('*.webp'))
for rel in files:
    expected=sha256((public/rel).read_bytes()).digest()
    assert sha256((dist/rel).read_bytes()).digest()==expected,('Build differs',str(rel))
    with urlopen('http://127.0.0.1:5174/'+rel.as_posix(),timeout=15) as response:
        assert response.status==200
        assert sha256(response.read()).digest()==expected,('HTTP differs',str(rel))
print(f'PASS: {len(files)} model/collision/gallery assets identical in public, dist and HTTP')
