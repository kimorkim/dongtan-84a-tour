"""Check current tour collision data: foyer -> master -> balcony -> refuge."""
import json
import math
import re
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
data = json.loads((ROOT / 'web/public/colliders.json').read_text(encoding='utf-8'))
radius = float(re.search(r'PLAYER_RADIUS = ([\d.]+)',
                        (ROOT / 'web/src/player.ts').read_text(encoding='utf-8')).group(1))
STEP = 0.06


def blocked(x, y):
    return any((x - max(a, min(c, x))) ** 2 + (y - max(b, min(d, y))) ** 2
               < radius ** 2 - 1e-9 for a, b, c, d in data['boxes'])


start = (round(12.33 / STEP), round((6.50 + 0.6) / STEP))
queue = deque([start])
visited = {start}
tested = {start}
assert not blocked(start[0] * STEP, start[1] * STEP - 0.6), 'Foyer spawn is blocked'
while queue:
    i, j = queue.popleft()
    for a, b in ((i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)):
        if not (0 <= a * STEP <= 15.5 and 0 <= b * STEP <= 11.2) or (a, b) in tested:
            continue
        tested.add((a, b))
        if not blocked(a * STEP, b * STEP - 0.6):
            visited.add((a, b))
            queue.append((a, b))

for name, x, y in [('master aisle', 3.42, 2.30), ('balcony', 3.42, 1.05),
                    ('refuge entry', 2.05, 0.95), ('refuge interior', 1.32, 1.05),
                    ('kitchen sink door', 5.22, 8.68), ('AC room door', 9.36, 8.40),
                    ('alpha entry', 9.88, 5.70), ('alpha interior', 9.10, 6.70),
                    ('entry pantry', 11.24, 6.70), ('AC room interior', 9.42, 8.94),
                    ('middle door passage', 12.33, 5.70), ('foyer rear', 12.33, 7.45)]:
    distance = min(math.hypot(i * STEP - x, j * STEP - 0.6 - y) for i, j in visited)
    print(f'{name}: nearest reachable point {distance:.3f}m')
    assert distance < 0.12, f'{name} is not reachable with player radius {radius}'

for name, x, y in [('balcony outer window', 3.15, 0.37),
                    ('refuge outer window', 1.40, 0.35), ('west exterior wall', 0.35, 1.10),
                    ('balcony parked sliding panels', 2.60, 1.77),
                    ('AC west boundary', 8.40, 8.70), ('AC north vent', 9.40, 9.36),
                    ('AC east boundary', 10.28, 8.65)]:
    assert blocked(x, y), f'{name} must block walking'
print(f'PASS: {len(visited)} reachable positions; exterior walls/windows still block movement')
