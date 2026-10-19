### Task 1: Scene Baseline & Initial Version Backup

**Files:**
- Create: `scripts/task1_baseline.py`
- Output: `apt_v00_initial.blend`

**Interfaces:**
- Consumes: Running Blender instance on `localhost:9876`.
- Produces: Collection `_DefaultObjects` containing original `Cube`, `Light`, `Camera`, and saved `apt_v00_initial.blend`.

**Requirements:**
1. Write `scripts/task1_baseline.py`:
   - Preserve existing objects (`Cube`, `Light`, `Camera`) in a collection named `_DefaultObjects`.
   - Hide them in viewport and render (`hide_viewport = True`, `hide_render = True`).
   - Create empty structural collections: `Apt_Floors`, `Apt_OuterWalls`, `Apt_InteriorWalls`, `Apt_Openings`.
   - Save current scene to `apt_v00_initial.blend`.
2. Execute the script via `mcp_client.py` using command:
   `uv run python -c "from mcp_client import send_blender_command; print(send_blender_command('execute_code', {'code': open('scripts/task1_baseline.py', encoding='utf-8').read()}))"`
3. Verify that `apt_v00_initial.blend` exists.
4. Commit changes:
   `git add scripts/task1_baseline.py`
   `git commit -m "feat: establish baseline scene and save apt_v00_initial.blend"`
