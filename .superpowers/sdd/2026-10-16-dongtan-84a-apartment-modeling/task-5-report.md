# Task 5 Report: Basic Doors & Windows Blocking

## Status
- **Status:** DONE
- **Date:** 2026-10-16
- **Commit:** `6c417f2` (`feat: add basic doors and windows opening blocks`)

## Implementation Details
1. **Script Creation (`scripts/task5_openings.py`)**:
   - Implemented `create_block(name, x1, x2, y1, y2, z1, z2, col_name="Apt_Openings")` generating 3D box meshes linked to the `Apt_Openings` collection.
   - Incorporated idempotent cleanup that purges any pre-existing object and unlinked mesh datablocks matching the name prior to generation.
   - Built 12 opening components: 6 door leaf blocks (~0.04m to 0.06m thick, 2.10m high) and 6 window opening blocks (~0.04m thick):
     - **Door Leaves (Z: 0.00 to 2.10m)**:
       - `Door_Entrance`: X: [1.350, 2.250], Y: [10.280, 10.340], Z: [0.000, 2.100] (Entrance main entry door, width 0.900m)
       - `Door_Bed3`: X: [1.550, 2.350], Y: [5.110, 5.150], Z: [0.000, 2.100] (Bedroom 3 door leaf, width 0.800m)
       - `Door_Bed2`: X: [3.950, 4.750], Y: [5.110, 5.150], Z: [0.000, 2.100] (Bedroom 2 door leaf, width 0.800m)
       - `Door_Bed1`: X: [7.730, 7.770], Y: [4.050, 4.850], Z: [0.000, 2.100] (Master Bedroom 1 door leaf, width 0.800m)
       - `Door_Alpha`: X: [4.880, 4.920], Y: [6.050, 6.850], Z: [0.000, 2.100] (Alpha Room door leaf, width 0.800m)
       - `Door_Bath1`: X: [1.450, 2.250], Y: [7.030, 7.070], Z: [0.000, 2.100] (Common Bathroom 1 door leaf, width 0.800m)
     - **Window Blocks**:
       - `Window_LivingRoom`: X: [5.050, 7.600], Y: [-0.120, -0.080], Z: [0.000, 2.200] (Living Room south full-height glazing, width 2.550m, height 2.200m)
       - `Window_Balcony1`: X: [7.850, 9.750], Y: [-0.120, -0.080], Z: [0.000, 2.200] (Balcony 1 south full-height glazing, width 1.900m, height 2.200m)
       - `Window_Bed2`: X: [2.750, 4.650], Y: [-0.120, -0.080], Z: [0.800, 2.100] (Bedroom 2 south sill window, width 1.900m, height 1.300m)
       - `Window_Bed3`: X: [0.250, 2.250], Y: [-0.120, -0.080], Z: [0.800, 2.100] (Bedroom 3 south sill window, width 2.000m, height 1.300m)
       - `Window_Kitchen_North`: X: [5.500, 6.700], Y: [10.280, 10.320], Z: [1.100, 1.700] (Kitchen north ribbon window, width 1.200m, height 0.600m)
       - `Window_DressRoom_North`: X: [8.200, 9.400], Y: [10.280, 10.320], Z: [1.100, 1.700] (Dress room north ribbon window, width 1.200m, height 0.600m)

2. **Execution via MCP**:
   - Executed against the live Blender 4.2 LTS instance on `localhost:9876`:
     ```bash
     uv run python -c "from mcp_client import send_blender_command; print(send_blender_command('execute_code', {'code': open('scripts/task5_openings.py', encoding='utf-8').read()}))"
     ```
   - Command response:
     ```
     SUCCESS: 12 opening blocks (6 doors, 6 windows) generated -> Door_Entrance: dims=(0.900, 0.060, 2.100), Door_Bed3: dims=(0.800, 0.040, 2.100), Door_Bed2: dims=(0.800, 0.040, 2.100), Door_Bed1: dims=(0.040, 0.800, 2.100), Door_Alpha: dims=(0.040, 0.800, 2.100), Door_Bath1: dims=(0.800, 0.040, 2.100), Window_LivingRoom: dims=(2.550, 0.040, 2.200), Window_Balcony1: dims=(1.900, 0.040, 2.200), Window_Bed2: dims=(1.900, 0.040, 1.300), Window_Bed3: dims=(2.000, 0.040, 1.300), Window_Kitchen_North: dims=(1.200, 0.040, 0.600), Window_DressRoom_North: dims=(1.200, 0.040, 0.600)
     ```

## Verification Summary
1. **Scene Collections & Containment**:
   - `Apt_Openings`: Contains exactly the 12 opening objects.
   - Each opening object's `users_collection` is strictly `['Apt_Openings']`.
   - Pre-existing collections remained intact:
     - `_DefaultObjects`: 3 objects (`Cube`, `Light`, `Camera`)
     - `Apt_Floors`: 8 slab objects
     - `Apt_OuterWalls`: 11 perimeter wall objects
     - `Apt_InteriorWalls`: 21 interior partition wall objects
   - Total scene object count: 55 objects.

2. **Mesh Topology & Scene Hygiene**:
   - Each opening block consists of exactly 8 vertices and 6 quad polygons.
   - Face normals are oriented consistently outward.
   - Total meshes in `bpy.data.meshes`: 53 (`1 Cube + 8 floors + 11 outer walls + 21 interior walls + 12 openings`), with 0 unlinked or orphaned meshes.
   - Re-running `task5_openings.py` is fully idempotent: no duplicate objects or mesh datablocks created.

3. **Dimensional & Coordinate Precision**:

| Object Name | Type | Dimensions (X × Y × Z) | X Range [min, max] | Y Range [min, max] | Z Range [min, max] |
| :--- | :---: | :---: | :---: | :---: | :---: |
| `Door_Entrance` | Door Leaf | 0.900 × 0.060 × 2.100 m | [1.350, 2.250] | [10.280, 10.340] | [0.000, 2.100] |
| `Door_Bed3` | Door Leaf | 0.800 × 0.040 × 2.100 m | [1.550, 2.350] | [5.110, 5.150] | [0.000, 2.100] |
| `Door_Bed2` | Door Leaf | 0.800 × 0.040 × 2.100 m | [3.950, 4.750] | [5.110, 5.150] | [0.000, 2.100] |
| `Door_Bed1` | Door Leaf | 0.040 × 0.800 × 2.100 m | [7.730, 7.770] | [4.050, 4.850] | [0.000, 2.100] |
| `Door_Alpha` | Door Leaf | 0.040 × 0.800 × 2.100 m | [4.880, 4.920] | [6.050, 6.850] | [0.000, 2.100] |
| `Door_Bath1` | Door Leaf | 0.800 × 0.040 × 2.100 m | [1.450, 2.250] | [7.030, 7.070] | [0.000, 2.100] |
| `Window_LivingRoom` | Window Block | 2.550 × 0.040 × 2.200 m | [5.050, 7.600] | [-0.120, -0.080] | [0.000, 2.200] |
| `Window_Balcony1` | Window Block | 1.900 × 0.040 × 2.200 m | [7.850, 9.750] | [-0.120, -0.080] | [0.000, 2.200] |
| `Window_Bed2` | Window Block | 1.900 × 0.040 × 1.300 m | [2.750, 4.650] | [-0.120, -0.080] | [0.800, 2.100] |
| `Window_Bed3` | Window Block | 2.000 × 0.040 × 1.300 m | [0.250, 2.250] | [-0.120, -0.080] | [0.800, 2.100] |
| `Window_Kitchen_North` | Window Block | 1.200 × 0.040 × 0.600 m | [5.500, 6.700] | [10.280, 10.320] | [1.100, 1.700] |
| `Window_DressRoom_North` | Window Block | 1.200 × 0.040 × 0.600 m | [8.200, 9.400] | [10.280, 10.320] | [1.100, 1.700] |

## Deliverables
- [task5_openings.py](file:///C:/Users/tamarand/orca/projects/apt/scripts/task5_openings.py)
- Report: [.superpowers/sdd/2026-10-16-dongtan-84a-apartment-modeling/task-5-report.md](file:///C:/Users/tamarand/orca/projects/apt/.superpowers/sdd/2026-10-16-dongtan-84a-apartment-modeling/task-5-report.md)
