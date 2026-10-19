### Task 3: Outer Perimeter & Party Walls Modeling

**Files:**
- Create: `scripts/task3_outer_walls.py`

**Interfaces:**
- Consumes: `Apt_OuterWalls` collection in Blender scene.
- Produces: `Wall_Party_West`, `Wall_Party_East`, `Wall_North_Segment1`, `Wall_North_DoorHeader`, `Wall_North_Segment2`, `Wall_South_Header_All`, `Wall_South_Sill_Bed3`, `Wall_South_Sill_Bed2`, `Wall_South_Col1`, `Wall_South_Col2`, `Wall_South_Col3` with accurate coordinates, thickness 0.20m, height 2.30m (Z: 0.0 to 2.30m).

**Requirements:**
1. Write `scripts/task3_outer_walls.py`:
   - Define `create_wall_box(name, x1, x2, y1, y2, z1=0.0, z2=2.30, col_name="Apt_OuterWalls")`.
   - Build perimeter outer walls and party walls:
     - West Party Wall: X: [-0.20, 0.0], Y: [-0.20, 10.415], Z: [0.0, 2.30]
     - East Side Wall: X: [9.865, 10.065], Y: [-0.20, 10.415], Z: [0.0, 2.30]
     - North Wall Segments:
       - `Wall_North_Segment1`: X: [0.0, 1.30], Y: [10.215, 10.415], Z: [0.0, 2.30]
       - `Wall_North_DoorHeader`: X: [1.30, 2.30], Y: [10.215, 10.415], Z: [2.10, 2.30] (entrance door opening below)
       - `Wall_North_Segment2`: X: [2.30, 9.865], Y: [10.215, 10.415], Z: [0.0, 2.30]
     - South Wall (Window Openings & Headers):
       - `Wall_South_Header_All`: X: [0.0, 9.865], Y: [-0.20, 0.0], Z: [2.20, 2.30]
       - `Wall_South_Sill_Bed3`: X: [0.20, 2.30], Y: [-0.20, 0.0], Z: [0.0, 0.80]
       - `Wall_South_Sill_Bed2`: X: [2.70, 4.70], Y: [-0.20, 0.0], Z: [0.0, 0.80]
       - `Wall_South_Col1`: X: [2.40, 2.60], Y: [-0.20, 0.0], Z: [0.0, 2.20]
       - `Wall_South_Col2`: X: [4.80, 5.00], Y: [-0.20, 0.0], Z: [0.0, 2.20]
       - `Wall_South_Col3`: X: [7.65, 7.85], Y: [-0.20, 0.0], Z: [0.0, 2.20]
2. Execute via `mcp_client.py`:
   `uv run python -c "from mcp_client import send_blender_command; print(send_blender_command('execute_code', {'code': open('scripts/task3_outer_walls.py', encoding='utf-8').read()}))"`
3. Verify all wall objects exist in `Apt_OuterWalls` and print their dimensions and locations.
4. Commit:
   `git add scripts/task3_outer_walls.py`
   `git commit -m "feat: model outer perimeter and party walls with openings"`
