### Task 2: Floor Base Modeling

**Files:**
- Create: `scripts/task2_floors.py`

**Interfaces:**
- Consumes: `Apt_Floors` collection in Blender scene.
- Produces: Mesh objects `Floor_Living_Dining`, `Floor_Bed1`, `Floor_Balcony1`, `Floor_Bed2`, `Floor_Bed3`, `Floor_AlphaRoom`, `Floor_Entrance_Bath1`, `Floor_MasterSuite_North` with accurate bounding coordinates and thickness 0.15m (Z from -0.15 to 0.0).

**Requirements:**
1. Write `scripts/task2_floors.py`:
   - Define `create_floor_slab(name, min_x, max_x, min_y, max_y, thickness=0.15, z_top=0.0)` which creates a solid 3D box mesh linked to `Apt_Floors`.
   - Build floors matching the 84A floor plan layout:
     - `Floor_Living_Dining`: X: [4.90, 7.75], Y: [1.45, 10.215]
     - `Floor_Bed1`: X: [7.75, 9.865], Y: [1.45, 5.18]
     - `Floor_Balcony1`: X: [7.75, 9.865], Y: [0.0, 1.45]
     - `Floor_Bed2`: X: [2.50, 4.90], Y: [0.0, 5.18]
     - `Floor_Bed3`: X: [0.0, 2.50], Y: [0.0, 5.18]
     - `Floor_AlphaRoom`: X: [2.50, 4.90], Y: [5.18, 10.215]
     - `Floor_Entrance_Bath1`: X: [0.0, 2.50], Y: [5.18, 10.215]
     - `Floor_MasterSuite_North`: X: [7.75, 9.865], Y: [5.18, 10.215]
   - Print created objects and their bounding dimensions.
2. Execute via `mcp_client.py`:
   `uv run python -c "from mcp_client import send_blender_command; print(send_blender_command('execute_code', {'code': open('scripts/task2_floors.py', encoding='utf-8').read()}))"`
3. Verify that all 8 floor objects exist in Blender, are linked to `Apt_Floors`, and have dimensions matching the coordinates.
4. Commit changes:
   `git add scripts/task2_floors.py`
   `git commit -m "feat: model base floor slabs for all 84A rooms"`
