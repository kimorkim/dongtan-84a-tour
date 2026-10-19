### Task 4: Interior Partition Walls with Door Openings

**Files:**
- Create: `scripts/task4_interior_walls.py`

**Interfaces:**
- Consumes: `Apt_InteriorWalls` collection in Blender scene.
- Produces: Partition walls separating rooms (thickness 0.10m, height 2.30m) with 0.90m x 2.10m doorway openings.

**Requirements:**
1. Write `scripts/task4_interior_walls.py`:
   - Define `create_wall(name, x1, x2, y1, y2, z1=0.0, z2=2.30)` linked to `Apt_InteriorWalls`.
   - Build interior partition walls separating rooms:
     - Main transverse corridor wall separating south rooms from north zone (at Y = 5.18):
       - `Wall_Bed3_North_A`: X: [0.0, 1.50], Y: [5.08, 5.18], Z: [0.0, 2.30]
       - `Wall_Bed3_North_DoorHeader`: X: [1.50, 2.40], Y: [5.08, 5.18], Z: [2.10, 2.30]
       - `Wall_Bed3_North_B`: X: [2.40, 2.50], Y: [5.08, 5.18], Z: [0.0, 2.30]
       - `Wall_Bed2_North_A`: X: [2.50, 3.90], Y: [5.08, 5.18], Z: [0.0, 2.30]
       - `Wall_Bed2_North_DoorHeader`: X: [3.90, 4.80], Y: [5.08, 5.18], Z: [2.10, 2.30]
       - `Wall_Bed2_North_B`: X: [4.80, 4.90], Y: [5.08, 5.18], Z: [0.0, 2.30]
     - Partitions between bedrooms:
       - `Wall_Bed3_Bed2`: X: [2.45, 2.55], Y: [0.0, 5.08], Z: [0.0, 2.30]
       - `Wall_Bed2_Living`: X: [4.85, 4.95], Y: [0.0, 5.08], Z: [0.0, 2.30]
       - `Wall_Living_Bed1_A`: X: [7.70, 7.80], Y: [1.45, 4.00], Z: [0.0, 2.30]
       - `Wall_Living_Bed1_DoorHeader`: X: [7.70, 7.80], Y: [4.00, 4.90], Z: [2.10, 2.30]
       - `Wall_Living_Bed1_B`: X: [7.70, 7.80], Y: [4.90, 5.08], Z: [0.0, 2.30]
     - Bed1 / Balcony1 inner sliding window partition (at Y = 1.45):
       - `Wall_Bed1_Balcony_Header`: X: [7.75, 9.865], Y: [1.40, 1.50], Z: [2.20, 2.30]
     - Alpha Room partitions (X: [2.50, 4.90], Y: [5.18, 10.215]):
       - `Wall_Alpha_East_A`: X: [4.85, 4.95], Y: [5.18, 6.00], Z: [0.0, 2.30]
       - `Wall_Alpha_East_DoorHeader`: X: [4.85, 4.95], Y: [6.00, 6.90], Z: [2.10, 2.30]
       - `Wall_Alpha_East_B`: X: [4.85, 4.95], Y: [6.90, 10.215], Z: [0.0, 2.30]
     - Bathroom 1 & Foyer partitions:
       - `Wall_Foyer_Bath1_Div`: X: [2.45, 2.55], Y: [5.18, 10.215], Z: [0.0, 2.30]
       - `Wall_Bath1_DoorHeader`: X: [1.40, 2.30], Y: [7.00, 7.10], Z: [2.10, 2.30]
       - `Wall_Bath1_South`: X: [0.0, 1.40], Y: [7.00, 7.10], Z: [0.0, 2.30]
       - `Wall_Bath1_East`: X: [2.30, 2.45], Y: [7.00, 7.10], Z: [0.0, 2.30]
     - Master Suite North zone (Bath 2 & Walk-in Dress room):
       - `Wall_DressRoom_South`: X: [7.75, 9.865], Y: [7.45, 7.55], Z: [0.0, 2.30]
       - `Wall_Bath2_Div`: X: [8.75, 8.85], Y: [5.18, 7.45], Z: [0.0, 2.30]
2. Execute via `mcp_client.py`:
   `uv run python -c "from mcp_client import send_blender_command; print(send_blender_command('execute_code', {'code': open('scripts/task4_interior_walls.py', encoding='utf-8').read()}))"`
3. Verify all interior wall objects exist in `Apt_InteriorWalls` and print their dimensions and locations.
4. Commit:
   `git add scripts/task4_interior_walls.py`
   `git commit -m "feat: model interior partition walls with doorway openings"`
