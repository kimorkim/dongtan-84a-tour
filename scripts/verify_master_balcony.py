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


spawn_y=7.15 if data.get('dimensions_version') == 1 else 6.50
start = (round(12.33 / STEP), round((spawn_y + 0.6) / STEP))
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

goals=[('master aisle', 3.42, 2.30), ('balcony', 3.42, 1.05),
                    ('refuge entry', 2.05, 0.95), ('refuge interior', 1.32, 1.05),
                    ('kitchen sink door', 5.22, 8.68), ('AC room door', 9.36, 8.40),
                    ('alpha entry', 9.88, 5.70), ('alpha interior', 9.10, 6.70),
                    ('entry pantry', 11.24, 6.70), ('AC room interior', 9.42, 8.94),
                    ('middle door passage', 12.33, 5.70), ('foyer rear', 12.33, 7.45),
                    ('dry vanity approach', 14.00, 5.00), ('common bathroom aisle', 13.98, 6.20),
                    ('common shower interior', 13.98, 7.15),
                    ('Yuna room entry', 12.55, 4.32), ('Yuna play area', 13.40, 2.75),
                    ('Yuna window approach', 13.50, 1.20), ('Yuna built-in approach',13.55,3.25),
                    ('Study entry',9.75,4.30), ('Study aisle',9.85,2.70),
                    ('Study window approach',9.90,1.20),
                    ('Study black chair approach',9.90,1.81),
                    ('Study grey chair approach',9.90,3.47)]
if data.get('dimensions_version') == 1:
    corrected={'common bathroom aisle':(13.8,6.3),'common shower interior':(13.85,7.2),'foyer rear':(12.33,7.15),
               'AC room interior':(9.42,9.0),'AC room door':(9.225,8.4),'Yuna window approach':(13.5,1.3),
               'Study window approach':(9.9,1.3)}
    goals=[(name,*corrected.get(name,(x,y))) for name,x,y in goals]
if data.get('sofa_version') == 14:
    goals.extend([('Brest sofa front aisle',7.3,3.0),('Brest sofa north passage',7.8,5.1)])
if data.get('living_finish_version') == 15 or data.get('living_finish_version') == 1:
    goals.extend([('Living cleared centre',6.4,3.2),('Living window approach',6.4,1.4)])
if data.get('kitchen_finish_version') == 1:
    goals.extend([('Kitchen sink approach',6.05,9.10),('Kitchen cooktop approach',6.65,9.03),
                  ('Kitchen dishwasher approach',5.4,9.10)])
if data.get('tv_stand_version') == 17:
    goals.append(('Living TV stand approach',5.15,3.286))
for name,x,y in goals:
    distance = min(math.hypot(i * STEP - x, j * STEP - 0.6 - y) for i, j in visited)
    print(f'{name}: nearest reachable point {distance:.3f}m')
    assert distance < 0.12, f'{name} is not reachable with player radius {radius}'

boundaries=[('balcony outer window', 3.15, 0.37),
                    ('refuge outer window', 1.40, 0.35), ('west exterior wall', 0.35, 1.10),
                    ('balcony parked sliding panels', 2.60, 1.77),
                    ('AC west boundary', 8.40, 8.70), ('AC north vent', 9.40, 9.36),
                    ('AC east boundary', 10.28, 8.65)]
if data.get('dimensions_version') == 1:
    corrected={'west exterior wall':(.25,1.1),'balcony parked sliding panels':(2.5,2.0),
               'AC west boundary':(8.6,8.9),'AC north vent':(9.4,9.55),
               'AC east boundary':(10.2,8.9)}
    boundaries=[(name,*corrected.get(name,(x,y))) for name,x,y in boundaries]
for name,x,y in boundaries:
    assert blocked(x, y), f'{name} must block walking'
print(f'PASS: {len(visited)} reachable positions; exterior walls/windows still block movement')
