### Task 6: 2-Stage Verification & Milestone Save

**Files:**
- Create: `scripts/task6_verify_and_save.py`
- Output: `verification_topdown.png`, `verification_living_pov.png`, `verification_alpha_pov.png`, `apt_v01_structure.blend`

**Interfaces:**
- Consumes: Fully populated scene (Apt_Floors, Apt_OuterWalls, Apt_InteriorWalls, Apt_Openings).
- Produces: Orthographic top-down and perspective POV screenshots, numerical audit report, and milestone save `apt_v01_structure.blend`.

**Requirements:**
1. Write `scripts/task6_verify_and_save.py`:
   - Add illumination (Sun light or Ambient world background color) so rendered images are clear and bright.
   - Perform numerical audit: iterate through all mesh objects in the apartment collections, print name, collection, location, and dimensions.
   - Render Top-down orthographic view (`verification_topdown.png`) showing all rooms, walls, and openings clearly.
   - Render Living Room eye-level (Z=1.6m) perspective POV view (`verification_living_pov.png`) looking into the apartment interior.
   - Render Alpha Room eye-level (Z=1.6m) perspective POV view (`verification_alpha_pov.png`).
   - Save the milestone `.blend` file to `apt_v01_structure.blend`.
2. Execute via `mcp_client.py`:
   `uv run python -c "from mcp_client import send_blender_command; print(send_blender_command('execute_code', {'code': open('scripts/task6_verify_and_save.py', encoding='utf-8').read()}))"`
3. Verify all 3 output images and `apt_v01_structure.blend` are created and valid.
4. Commit:
   `git add scripts/task6_verify_and_save.py`
   `git commit -m "feat: complete structural verification and save apt_v01_structure.blend"`
