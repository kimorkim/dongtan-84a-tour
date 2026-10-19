### Task 5: Basic Doors & Windows Blocking

**Files:**
- Create: `scripts/task5_openings.py`

**Interfaces:**
- Consumes: `Apt_Openings` collection in Blender scene.
- Produces: Simple block models for doors (`Door_Entrance`, `Door_Bed1`, `Door_Bed2`, `Door_Bed3`, `Door_Alpha`, `Door_Bath1`) and windows (`Window_LivingRoom`, `Window_Balcony1`, `Window_Bed2`, `Window_Bed3`, `Window_Kitchen_North`, `Window_DressRoom_North`) linked to `Apt_Openings`.

**Requirements:**
1. Write `scripts/task5_openings.py`:
   - Define `create_block(name, x1, x2, y1, y2, z1, z2, col_name="Apt_Openings")`.
   - Build door leaves (thickness ~0.04m, height 2.10m):
     - `Door_Entrance`: X: [1.35, 2.25], Y: [10.28, 10.34], Z: [0.0, 2.10]
     - `Door_Bed3`: X: [1.55, 2.35], Y: [5.11, 5.15], Z: [0.0, 2.10]
     - `Door_Bed2`: X: [3.95, 4.75], Y: [5.11, 5.15], Z: [0.0, 2.10]
     - `Door_Bed1`: X: [7.73, 7.77], Y: [4.05, 4.85], Z: [0.0, 2.10]
     - `Door_Alpha`: X: [4.88, 4.92], Y: [6.05, 6.85], Z: [0.0, 2.10]
     - `Door_Bath1`: X: [1.45, 2.25], Y: [7.03, 7.07], Z: [0.0, 2.10]
   - Build window blocks (thickness ~0.04m):
     - `Window_LivingRoom`: X: [5.05, 7.60], Y: [-0.12, -0.08], Z: [0.0, 2.20]
     - `Window_Balcony1`: X: [7.85, 9.75], Y: [-0.12, -0.08], Z: [0.0, 2.20]
     - `Window_Bed2`: X: [2.75, 4.65], Y: [-0.12, -0.08], Z: [0.80, 2.10]
     - `Window_Bed3`: X: [0.25, 2.25], Y: [-0.12, -0.08], Z: [0.80, 2.10]
     - `Window_Kitchen_North`: X: [5.50, 6.70], Y: [10.28, 10.32], Z: [1.10, 1.70]
     - `Window_DressRoom_North`: X: [8.20, 9.40], Y: [10.28, 10.32], Z: [1.10, 1.70]
2. Execute via `mcp_client.py`:
   `uv run python -c "from mcp_client import send_blender_command; print(send_blender_command('execute_code', {'code': open('scripts/task5_openings.py', encoding='utf-8').read()}))"`
3. Verify all 12 door and window objects exist in `Apt_Openings` with expected coordinates.
4. Commit:
   `git add scripts/task5_openings.py`
   `git commit -m "feat: add basic doors and windows opening blocks"`
