# 84A Apartment Structural Modeling Implementation Plan

> Historical plan: later layout/dimension corrections supersede parts of this document.
> Read the [current report](../../quality-v2-report.md) and [asset guide](../../asset-guide.md) first.
> File locations below are historical; use the [relocation index](../../asset-inventory.md).

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a 1:1 scale 3D structural model (floors, perimeter walls, interior partition walls, doors, windows) of the Dongtan A76-2BL 84A (Alpha Room) apartment in Blender via Blender MCP, verified by numerical queries and top-down/indoor POV screenshots.

**Architecture:** A Python automation script executed via the running Blender MCP socket server (`localhost:9876`) generates granular, cleanly named Blender mesh objects in separate collections. Each task adds or modifies modular objects without recreating or deleting existing objects, followed by automated verification and checkpoint blend saves.

**Tech Stack:** Blender 4.2 LTS (`bpy`), Blender MCP server (`mcp-for-blender`), Python 3.13, PyMuPDF.

## Global Constraints

- Never delete existing scene objects (`Cube`, `Light`, `Camera`) without user permission; preserve them in `_DefaultObjects`.
- Prioritize explicit floor plan dimensions (Width 9.865m, South balcony depth 1.45m, Living/Bedroom depth 3.73m, Hallway/Mid depth 2.115m, North utility depth 2.92m, Total Depth 10.215m).
- Apply estimated dimensions list: Ceiling height 2.30m, Outer wall thickness 0.20m, Interior wall thickness 0.10m, Interior door 0.90m x 2.10m, Entrance door 1.00m x 2.10m, Slab thickness 0.15m.
- Do NOT add furniture, materials, textures, or decorations during this structural phase.
- Use explicit standardized English object names (`Wall_LivingRoom`, `Wall_AlphaRoom`, `Floor_Main`, `Door_Main`, `Window_LivingRoom`).
- Verify each stage numerically (location + bounding dimensions) and visually (top-down view + indoor POV screenshots).
- Save separate version files before major changes (`apt_v00_initial.blend`, `apt_v01_structure.blend`).

---

### Task 1: Scene Baseline & Initial Version Backup

**Files:**
- Create: `scripts/task1_baseline.py`
- Output: `apt_v00_initial.blend`

**Interfaces:**
- Consumes: Running Blender instance on `localhost:9876`.
- Produces: Collection `_DefaultObjects` containing original `Cube`, `Light`, `Camera`, and saved `apt_v00_initial.blend`.

- [ ] **Step 1: Write baseline management script**

```python
# scripts/task1_baseline.py
import bpy
import os

def setup_baseline():
    # 1. Ensure existing objects are preserved in _DefaultObjects collection
    default_col = bpy.data.collections.get("_DefaultObjects")
    if not default_col:
        default_col = bpy.data.collections.new("_DefaultObjects")
        bpy.context.scene.collection.children.link(default_col)

    for obj_name in ["Cube", "Light", "Camera"]:
        obj = bpy.data.objects.get(obj_name)
        if obj:
            # Unlink from other collections and link to _DefaultObjects
            for col in obj.users_collection:
                col.unlink(obj)
            default_col.objects.link(obj)
            obj.hide_viewport = True
            obj.hide_render = True

    # 2. Create structural collections
    for col_name in ["Apt_Floors", "Apt_OuterWalls", "Apt_InteriorWalls", "Apt_Openings"]:
        if not bpy.data.collections.get(col_name):
            col = bpy.data.collections.new(col_name)
            bpy.context.scene.collection.children.link(col)

    # 3. Save baseline blend
    save_path = os.path.abspath("apt_v00_initial.blend")
    bpy.ops.wm.save_as_mainfile(filepath=save_path)
    print(f"SUCCESS: Baseline configured and saved to {save_path}")

setup_baseline()
```

- [ ] **Step 2: Execute Task 1 script via MCP client**

Run: `uv run python -c "from mcp_client import send_blender_command; print(send_blender_command('execute_code', {'code': open('scripts/task1_baseline.py', encoding='utf-8').read()}))"`
Expected: `{"status": "success", "result": "SUCCESS: Baseline configured..."}`

- [ ] **Step 3: Verify baseline state and file creation**

Run: `Test-Path "apt_v00_initial.blend"`
Expected: `True`

- [ ] **Step 4: Commit**

```bash
git add scripts/task1_baseline.py
git commit -m "feat: establish baseline scene and save apt_v00_initial.blend"
```

---

### Task 2: Floor Base Modeling

**Files:**
- Create: `scripts/task2_floors.py`

**Interfaces:**
- Consumes: `Apt_Floors` collection in Blender scene.
- Produces: Mesh objects `Floor_Living_Dining`, `Floor_Bedrooms`, `Floor_AlphaRoom`, `Floor_Bathrooms`, `Floor_Balcony1`, `Floor_Balcony2` with accurate bounding coordinates.

- [ ] **Step 1: Write floor modeling script**

```python
# scripts/task2_floors.py
import bpy

def create_floor_slab(name, min_x, max_x, min_y, max_y, thickness=0.15, z_top=0.0):
    col = bpy.data.collections.get("Apt_Floors") or bpy.context.scene.collection
    
    # Remove existing object with same name if any
    existing = bpy.data.objects.get(name)
    if existing:
        bpy.data.objects.remove(existing, do_unlink=True)
        
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    
    z_bottom = z_top - thickness
    verts = [
        (min_x, min_y, z_bottom),
        (max_x, min_y, z_bottom),
        (max_x, max_y, z_bottom),
        (min_x, max_y, z_bottom),
        (min_x, min_y, z_top),
        (max_x, min_y, z_top),
        (max_x, max_y, z_top),
        (min_x, max_y, z_top),
    ]
    faces = [
        (0, 1, 2, 3), # Bottom
        (4, 7, 6, 5), # Top
        (0, 4, 5, 1), # South
        (1, 5, 6, 2), # East
        (2, 6, 7, 3), # North
        (3, 7, 4, 0), # West
    ]
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    return obj

def build_floors():
    # Width: 0.0 to 9.865
    # Depth: 0.0 to 10.215
    floors = [
        ("Floor_Living_Dining", 4.90, 7.75, 1.45, 10.215),
        ("Floor_Bed1", 7.75, 9.865, 1.45, 5.18),
        ("Floor_Balcony1", 7.75, 9.865, 0.0, 1.45),
        ("Floor_Bed2", 2.50, 4.90, 0.0, 5.18),
        ("Floor_Bed3", 0.0, 2.50, 0.0, 5.18),
        ("Floor_AlphaRoom", 2.50, 4.90, 5.18, 10.215),
        ("Floor_Entrance_Bath1", 0.0, 2.50, 5.18, 10.215),
        ("Floor_MasterSuite_North", 7.75, 9.865, 5.18, 10.215),
    ]
    results = []
    for name, x1, x2, y1, y2 in floors:
        obj = create_floor_slab(name, x1, x2, y1, y2)
        results.append(f"{obj.name}: dims=({obj.dimensions.x:.2f}, {obj.dimensions.y:.2f}, {obj.dimensions.z:.2f})")
    print("SUCCESS: Floors created -> " + ", ".join(results))

build_floors()
```

- [ ] **Step 2: Execute floor script via MCP client**

Run: `uv run python -c "from mcp_client import send_blender_command; print(send_blender_command('execute_code', {'code': open('scripts/task2_floors.py', encoding='utf-8').read()}))"`
Expected: `{"status": "success", "result": "SUCCESS: Floors created..."}`

- [ ] **Step 3: Verify numerical dimensions of floors**

Run: `uv run python -c "from mcp_client import send_blender_command; res = send_blender_command('get_scene_info'); print([o['name'] for o in res['result']['objects'] if 'Floor' in o['name']])"`
Expected: List of 8 created floor slab objects.

- [ ] **Step 4: Commit**

```bash
git add scripts/task2_floors.py
git commit -m "feat: model base floor slabs for all 84A rooms"
```

---

### Task 3: Outer Perimeter & Party Walls Modeling

**Files:**
- Create: `scripts/task3_outer_walls.py`

**Interfaces:**
- Consumes: `Apt_OuterWalls` collection in Blender scene.
- Produces: `Wall_Outer_South`, `Wall_Outer_North`, `Wall_Party_West`, `Wall_Party_East` (thickness 0.20m, height 2.30m) with window/door cutouts.

- [ ] **Step 1: Write outer walls script**

```python
# scripts/task3_outer_walls.py
import bpy

def create_wall_box(name, x1, x2, y1, y2, z1=0.0, z2=2.30, col_name="Apt_OuterWalls"):
    col = bpy.data.collections.get(col_name) or bpy.context.scene.collection
    existing = bpy.data.objects.get(name)
    if existing:
        bpy.data.objects.remove(existing, do_unlink=True)
        
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    
    verts = [
        (x1, y1, z1), (x2, y1, z1), (x2, y2, z1), (x1, y2, z1),
        (x1, y1, z2), (x2, y1, z2), (x2, y2, z2), (x1, y2, z2),
    ]
    faces = [
        (0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1),
        (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0),
    ]
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    return obj

def build_outer_walls():
    # Outer boundaries: X: [0.0, 9.865], Y: [0.0, 10.215]
    # Thickness = 0.20m, Height = 2.30m
    
    # West Party Wall (X: -0.20 to 0.0, Y: 0.0 to 10.215)
    create_wall_box("Wall_Party_West", -0.20, 0.0, -0.20, 10.415)
    
    # East Side Wall (X: 9.865 to 10.065, Y: 0.0 to 10.215)
    create_wall_box("Wall_Party_East", 9.865, 10.065, -0.20, 10.415)
    
    # North Outer Wall with Entrance Doorway cutout and Kitchen/Dressroom window spandrels
    # Entrance door at X: [1.30, 2.30] -> wall segments: [0.0, 1.30], header above door [1.30, 2.30, z: 2.10-2.30], [2.30, 9.865]
    create_wall_box("Wall_North_Segment1", 0.0, 1.30, 10.215, 10.415)
    create_wall_box("Wall_North_DoorHeader", 1.30, 2.30, 10.215, 10.415, z1=2.10, z2=2.30)
    create_wall_box("Wall_North_Segment2", 2.30, 9.865, 10.215, 10.415)
    
    # South Outer Wall with window openings (Bed3, Bed2, Living, Balcony1)
    # Sill height 0.80m for Bed3 & Bed2; Full height for Living & Balcony1 (header 2.20 to 2.30)
    # Headers along south:
    create_wall_box("Wall_South_Header_All", 0.0, 9.865, -0.20, 0.0, z1=2.20, z2=2.30)
    # Sills for Bed3 [0.0, 2.50] and Bed2 [2.50, 4.90]:
    create_wall_box("Wall_South_Sill_Bed3", 0.20, 2.30, -0.20, 0.0, z1=0.0, z2=0.80)
    create_wall_box("Wall_South_Sill_Bed2", 2.70, 4.70, -0.20, 0.0, z1=0.0, z2=0.80)
    # Intermediate columns between south bays
    create_wall_box("Wall_South_Col1", 2.40, 2.60, -0.20, 0.0, z1=0.0, z2=2.20)
    create_wall_box("Wall_South_Col2", 4.80, 5.00, -0.20, 0.0, z1=0.0, z2=2.20)
    create_wall_box("Wall_South_Col3", 7.65, 7.85, -0.20, 0.0, z1=0.0, z2=2.20)
    
    print("SUCCESS: Outer perimeter walls and party walls generated.")

build_outer_walls()
```

- [ ] **Step 2: Execute outer walls script via MCP client**

Run: `uv run python -c "from mcp_client import send_blender_command; print(send_blender_command('execute_code', {'code': open('scripts/task3_outer_walls.py', encoding='utf-8').read()}))"`
Expected: `{"status": "success", "result": "SUCCESS: Outer perimeter walls and party walls generated."}`

- [ ] **Step 3: Verify outer wall dimensions**

Run: `uv run python -c "from mcp_client import send_blender_command; res = send_blender_command('get_scene_info'); print(len([o for o in res['result']['objects'] if 'Wall_' in o['name']]))"`
Expected: Count of created wall segments >= 7.

- [ ] **Step 4: Commit**

```bash
git add scripts/task3_outer_walls.py
git commit -m "feat: model outer perimeter and party walls with openings"
```

---

### Task 4: Interior Partition Walls with Door Openings

**Files:**
- Create: `scripts/task4_interior_walls.py`

**Interfaces:**
- Consumes: `Apt_InteriorWalls` collection in Blender scene.
- Produces: Partition walls separating rooms (thickness 0.10m, height 2.30m) with 0.90m x 2.10m door openings.

- [ ] **Step 1: Write interior walls script**

```python
# scripts/task4_interior_walls.py
import bpy

def create_wall(name, x1, x2, y1, y2, z1=0.0, z2=2.30):
    col = bpy.data.collections.get("Apt_InteriorWalls") or bpy.context.scene.collection
    existing = bpy.data.objects.get(name)
    if existing:
        bpy.data.objects.remove(existing, do_unlink=True)
        
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    
    verts = [
        (x1, y1, z1), (x2, y1, z1), (x2, y2, z1), (x1, y2, z1),
        (x1, y1, z2), (x2, y1, z2), (x2, y2, z2), (x1, y2, z2),
    ]
    faces = [
        (0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1),
        (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0),
    ]
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    return obj

def build_interior_walls():
    # 1. Main transverse corridor wall (separating south rooms from north zone at Y = 5.18)
    # Openings into Living room [4.90, 7.75] is open
    # Wall behind Bed3 [0.0, 2.50] with door cutout at [1.50, 2.40]:
    create_wall("Wall_Bed3_North_A", 0.0, 1.50, 5.08, 5.18)
    create_wall("Wall_Bed3_North_DoorHeader", 1.50, 2.40, 5.08, 5.18, z1=2.10, z2=2.30)
    create_wall("Wall_Bed3_North_B", 2.40, 2.50, 5.08, 5.18)
    
    # Wall behind Bed2 [2.50, 4.90] with door cutout at [3.90, 4.80]:
    create_wall("Wall_Bed2_North_A", 2.50, 3.90, 5.08, 5.18)
    create_wall("Wall_Bed2_North_DoorHeader", 3.90, 4.80, 5.08, 5.18, z1=2.10, z2=2.30)
    create_wall("Wall_Bed2_North_B", 4.80, 4.90, 5.08, 5.18)

    # 2. Partitions between bedrooms
    # Between Bed3 and Bed2 at X = 2.50 (Y: 0.0 to 5.08)
    create_wall("Wall_Bed3_Bed2", 2.45, 2.55, 0.0, 5.08)
    # Between Bed2 and Living at X = 4.90 (Y: 0.0 to 5.08)
    create_wall("Wall_Bed2_Living", 4.85, 4.95, 0.0, 5.08)
    # Between Living and Bed1 at X = 7.75 (Y: 1.45 to 5.08) with door at [4.0, 4.90]:
    create_wall("Wall_Living_Bed1_A", 7.70, 7.80, 1.45, 4.00)
    create_wall("Wall_Living_Bed1_DoorHeader", 7.70, 7.80, 4.00, 4.90, z1=2.10, z2=2.30)
    create_wall("Wall_Living_Bed1_B", 7.70, 7.80, 4.90, 5.08)
    
    # 3. Bed1 (Master) front wall separating from Balcony1 at Y = 1.45
    # Inner sliding window/door between Bed1 and Balcony1
    create_wall("Wall_Bed1_Balcony_Header", 7.75, 9.865, 1.40, 1.50, z1=2.20, z2=2.30)
    
    # 4. Alpha Room partitions (X: 2.50 to 4.90, Y: 5.18 to 10.215)
    # Alpha room East wall at X = 4.90 (facing Kitchen/Dining) with door cutout at Y: [6.0, 6.90]:
    create_wall("Wall_Alpha_East_A", 4.85, 4.95, 5.18, 6.00)
    create_wall("Wall_Alpha_East_DoorHeader", 4.85, 4.95, 6.00, 6.90, z1=2.10, z2=2.30)
    create_wall("Wall_Alpha_East_B", 4.85, 4.95, 6.90, 10.215)
    
    # 5. Bathroom 1 & Foyer partition at X = 2.50 (Y: 5.18 to 10.215)
    create_wall("Wall_Foyer_Bath1_Div", 2.45, 2.55, 5.18, 10.215)
    # Bathroom 1 door cutout facing corridor
    create_wall("Wall_Bath1_DoorHeader", 1.40, 2.30, 7.00, 7.10, z1=2.10, z2=2.30)
    create_wall("Wall_Bath1_South", 0.0, 1.40, 7.00, 7.10)
    create_wall("Wall_Bath1_East", 2.30, 2.45, 7.00, 7.10)
    
    # 6. Master Suite North zone (Powder, Bath2, Walk-in Dressroom at X: 7.75 to 9.865)
    # Dress room partition wall at Y = 7.50
    create_wall("Wall_DressRoom_South", 7.75, 9.865, 7.45, 7.55)
    # Bath2 partition wall at X = 8.80 (Y: 5.18 to 7.45)
    create_wall("Wall_Bath2_Div", 8.75, 8.85, 5.18, 7.45)
    
    print("SUCCESS: Interior partition walls and door headers generated.")

build_interior_walls()
```

- [ ] **Step 2: Execute interior walls script via MCP client**

Run: `uv run python -c "from mcp_client import send_blender_command; print(send_blender_command('execute_code', {'code': open('scripts/task4_interior_walls.py', encoding='utf-8').read()}))"`
Expected: `{"status": "success", "result": "SUCCESS: Interior partition walls and door headers generated."}`

- [ ] **Step 3: Verify interior wall objects in scene**

Run: `uv run python -c "from mcp_client import send_blender_command; res = send_blender_command('get_scene_info'); print(len([o for o in res['result']['objects'] if 'Wall_' in o['name']]))"`
Expected: Count of all wall segments >= 20.

- [ ] **Step 4: Commit**

```bash
git add scripts/task4_interior_walls.py
git commit -m "feat: model interior partition walls with doorway openings"
```

---

### Task 5: Basic Doors & Windows Blocking

**Files:**
- Create: `scripts/task5_openings.py`

**Interfaces:**
- Consumes: `Apt_Openings` collection in Blender scene.
- Produces: Simple block models for doors (`Door_Entrance`, `Door_Bed1`, `Door_Bed2`, `Door_Bed3`, `Door_Alpha`, `Door_Bath1`, `Door_Bath2`) and window frames/glass.

- [ ] **Step 1: Write doors and windows script**

```python
# scripts/task5_openings.py
import bpy

def create_block(name, x1, x2, y1, y2, z1, z2, col_name="Apt_Openings"):
    col = bpy.data.collections.get(col_name) or bpy.context.scene.collection
    existing = bpy.data.objects.get(name)
    if existing:
        bpy.data.objects.remove(existing, do_unlink=True)
        
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    
    verts = [
        (x1, y1, z1), (x2, y1, z1), (x2, y2, z1), (x1, y2, z1),
        (x1, y1, z2), (x2, y1, z2), (x2, y2, z2), (x1, y2, z2),
    ]
    faces = [
        (0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1),
        (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0),
    ]
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    return obj

def build_openings():
    # Interior door leaf thickness: 0.04m, height 2.10m
    doors = [
        ("Door_Entrance", 1.35, 2.25, 10.28, 10.34, 0.0, 2.10),
        ("Door_Bed3", 1.55, 2.35, 5.11, 5.15, 0.0, 2.10),
        ("Door_Bed2", 3.95, 4.75, 5.11, 5.15, 0.0, 2.10),
        ("Door_Bed1", 7.73, 7.77, 4.05, 4.85, 0.0, 2.10),
        ("Door_Alpha", 4.88, 4.92, 6.05, 6.85, 0.0, 2.10),
        ("Door_Bath1", 1.45, 2.25, 7.03, 7.07, 0.0, 2.10),
    ]
    for name, x1, x2, y1, y2, z1, z2 in doors:
        create_block(name, x1, x2, y1, y2, z1, z2)
        
    # Windows
    windows = [
        ("Window_LivingRoom", 5.05, 7.60, -0.12, -0.08, 0.0, 2.20),
        ("Window_Balcony1", 7.85, 9.75, -0.12, -0.08, 0.0, 2.20),
        ("Window_Bed2", 2.75, 4.65, -0.12, -0.08, 0.80, 2.10),
        ("Window_Bed3", 0.25, 2.25, -0.12, -0.08, 0.80, 2.10),
        ("Window_Kitchen_North", 5.50, 6.70, 10.28, 10.32, 1.10, 1.70),
        ("Window_DressRoom_North", 8.20, 9.40, 10.28, 10.32, 1.10, 1.70),
    ]
    for name, x1, x2, y1, y2, z1, z2 in windows:
        create_block(name, x1, x2, y1, y2, z1, z2)

    print("SUCCESS: Door leaves and window frames/glass blocked.")

build_openings()
```

- [ ] **Step 2: Execute doors and windows script via MCP client**

Run: `uv run python -c "from mcp_client import send_blender_command; print(send_blender_command('execute_code', {'code': open('scripts/task5_openings.py', encoding='utf-8').read()}))"`
Expected: `{"status": "success", "result": "SUCCESS: Door leaves and window frames/glass blocked."}`

- [ ] **Step 3: Verify openings objects**

Run: `uv run python -c "from mcp_client import send_blender_command; res = send_blender_command('get_scene_info'); print([o['name'] for o in res['result']['objects'] if 'Door_' in o['name'] or 'Window_' in o['name']])"`
Expected: List of 6 door objects and 6 window objects.

- [ ] **Step 4: Commit**

```bash
git add scripts/task5_openings.py
git commit -m "feat: add basic doors and windows opening blocks"
```

---

### Task 6: 2-Stage Verification & Milestone Save

**Files:**
- Create: `scripts/task6_verify_and_save.py`
- Output: `verification_topdown.png`, `verification_living_pov.png`, `verification_alpha_pov.png`, `apt_v01_structure.blend`

**Interfaces:**
- Consumes: Complete modeled scene in Blender.
- Produces: Orthographic top-down and perspective POV screenshots, numerical audit report, and milestone save `apt_v01_structure.blend`.

- [ ] **Step 1: Write verification and rendering script**

```python
# scripts/task6_verify_and_save.py
import bpy
import math
import os

def render_view(cam_name, filepath, location, rotation, is_ortho=False, ortho_scale=12.0):
    cam_data = bpy.data.cameras.get(cam_name) or bpy.data.cameras.new(cam_name)
    cam_obj = bpy.data.objects.get(cam_name) or bpy.data.objects.new(cam_name, cam_data)
    
    if cam_obj.name not in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.link(cam_obj)
        
    cam_obj.location = location
    cam_obj.rotation_euler = rotation
    
    if is_ortho:
        cam_data.type = 'ORTHO'
        cam_data.ortho_scale = ortho_scale
    else:
        cam_data.type = 'PERSP'
        cam_data.lens = 24.0 # wide angle for indoor
        
    bpy.context.scene.camera = cam_obj
    bpy.context.scene.render.resolution_x = 1280
    bpy.context.scene.render.resolution_y = 960
    bpy.context.scene.render.filepath = os.path.abspath(filepath)
    bpy.ops.render.render(write_still=True)
    print(f"Rendered: {filepath}")

def run_verification():
    # 1. Numerical audit of all objects
    print("\n=== NUMERICAL AUDIT ===")
    total_objs = 0
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH' and not obj.name.startswith("Cube"):
            total_objs += 1
            print(f"[{obj.name}] Loc=({obj.location.x:.2f}, {obj.location.y:.2f}, {obj.location.z:.2f}) Dims=({obj.dimensions.x:.2f}, {obj.dimensions.y:.2f}, {obj.dimensions.z:.2f})")
    print(f"Total custom structural objects: {total_objs}")
    
    # 2. Render Top-down orthographic view
    # Center of apartment: X ≈ 5.0, Y ≈ 5.0
    render_view(
        "Cam_Topdown",
        "verification_topdown.png",
        location=(4.93, 5.10, 15.0),
        rotation=(0.0, 0.0, 0.0),
        is_ortho=True,
        ortho_scale=13.0
    )
    
    # 3. Render Living Room POV (Eye height 1.6m looking towards Kitchen and North)
    render_view(
        "Cam_Living_POV",
        "verification_living_pov.png",
        location=(6.0, 2.0, 1.6),
        rotation=(math.radians(80), 0.0, math.radians(0))
    )
    
    # 4. Render Alpha Room POV (Eye height 1.6m looking around)
    render_view(
        "Cam_Alpha_POV",
        "verification_alpha_pov.png",
        location=(3.7, 6.0, 1.6),
        rotation=(math.radians(85), 0.0, math.radians(-30))
    )
    
    # 5. Save milestone blend file
    save_path = os.path.abspath("apt_v01_structure.blend")
    bpy.ops.wm.save_as_mainfile(filepath=save_path)
    print(f"SUCCESS: Saved milestone model to {save_path}")

run_verification()
```

- [ ] **Step 2: Execute verification script via MCP client**

Run: `uv run python -c "from mcp_client import send_blender_command; print(send_blender_command('execute_code', {'code': open('scripts/task6_verify_and_save.py', encoding='utf-8').read()}))"`
Expected: `{"status": "success", "result": "...SUCCESS: Saved milestone model to apt_v01_structure.blend"}`

- [ ] **Step 3: Verify all output images and blend file**

Run: `Test-Path "verification_topdown.png", "verification_living_pov.png", "verification_alpha_pov.png", "apt_v01_structure.blend"`
Expected: `True True True True`

- [ ] **Step 4: Commit**

```bash
git add scripts/task6_verify_and_save.py
git commit -m "feat: complete structural verification and save apt_v01_structure.blend"
```
