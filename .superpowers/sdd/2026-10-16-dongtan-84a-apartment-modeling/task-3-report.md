# Task 3 Report: Outer Perimeter & Party Walls Modeling

## Status
- **Status:** DONE
- **Date:** 2026-10-16
- **Commit:** `38e537d` (`feat: model outer perimeter and party walls with openings`)

## Implementation Details
1. **Script Creation (`scripts/task3_outer_walls.py`)**:
   - Implemented `create_wall_box(name, x1, x2, y1, y2, z1=0.0, z2=2.30, col_name="Apt_OuterWalls")` which creates a 3D box mesh linked to collection `Apt_OuterWalls`.
   - Included idempotent cleanup logic that removes previous object and unlinked mesh datablocks of the same name before recreating.
   - Configured exact counter-clockwise face winding order with outward-facing normals for all 6 faces (bottom, top, south, east, north, west).
   - Modeled 11 outer perimeter and party wall components:
     - **West Party Wall**:
       - `Wall_Party_West`: X: [-0.200, 0.000], Y: [-0.200, 10.415], Z: [0.000, 2.300], dims: (0.200, 10.615, 2.300)
     - **East Side Wall**:
       - `Wall_Party_East`: X: [9.865, 10.065], Y: [-0.200, 10.415], Z: [0.000, 2.300], dims: (0.200, 10.615, 2.300)
     - **North Wall Segments**:
       - `Wall_North_Segment1`: X: [0.000, 1.300], Y: [10.215, 10.415], Z: [0.000, 2.300], dims: (1.300, 0.200, 2.300)
       - `Wall_North_DoorHeader`: X: [1.300, 2.300], Y: [10.215, 10.415], Z: [2.100, 2.300], dims: (1.000, 0.200, 0.200) (entrance door opening below at Z: [0.000, 2.100])
       - `Wall_North_Segment2`: X: [2.300, 9.865], Y: [10.215, 10.415], Z: [0.000, 2.300], dims: (7.565, 0.200, 2.300)
     - **South Wall (Window Openings & Headers)**:
       - `Wall_South_Header_All`: X: [0.000, 9.865], Y: [-0.200, 0.000], Z: [2.200, 2.300], dims: (9.865, 0.200, 0.100) (continuous upper lintel/header across entire south elevation)
       - `Wall_South_Sill_Bed3`: X: [0.200, 2.300], Y: [-0.200, 0.000], Z: [0.000, 0.800], dims: (2.100, 0.200, 0.800) (Bed 3 window sill)
       - `Wall_South_Sill_Bed2`: X: [2.700, 4.700], Y: [-0.200, 0.000], Z: [0.000, 0.800], dims: (2.000, 0.200, 0.800) (Bed 2 window sill)
       - `Wall_South_Col1`: X: [2.400, 2.600], Y: [-0.200, 0.000], Z: [0.000, 2.200], dims: (0.200, 0.200, 2.200) (intermediate column between Bed3 and Bed2)
       - `Wall_South_Col2`: X: [4.800, 5.000], Y: [-0.200, 0.000], Z: [0.000, 2.200], dims: (0.200, 0.200, 2.200) (intermediate column between Bed2 and Living room)
       - `Wall_South_Col3`: X: [7.650, 7.850], Y: [-0.200, 0.000], Z: [0.000, 2.200], dims: (0.200, 0.200, 2.200) (intermediate column between Living room and Balcony 1)

2. **Execution via MCP**:
   - Executed against live Blender 4.2 LTS instance on `localhost:9876`:
     ```bash
     uv run python -c "from mcp_client import send_blender_command; print(send_blender_command('execute_code', {'code': open('scripts/task3_outer_walls.py', encoding='utf-8').read()}))"
     ```
   - Command response:
     ```
     {'status': 'success', 'result': {'executed': True, 'result': 'SUCCESS: Outer perimeter walls and party walls generated -> Wall_Party_West: dims=(0.200, 10.615, 2.300), Wall_Party_East: dims=(0.200, 10.615, 2.300), Wall_North_Segment1: dims=(1.300, 0.200, 2.300), Wall_North_DoorHeader: dims=(1.000, 0.200, 0.200), Wall_North_Segment2: dims=(7.565, 0.200, 2.300), Wall_South_Header_All: dims=(9.865, 0.200, 0.100), Wall_South_Sill_Bed3: dims=(2.100, 0.200, 0.800), Wall_South_Sill_Bed2: dims=(2.000, 0.200, 0.800), Wall_South_Col1: dims=(0.200, 0.200, 2.200), Wall_South_Col2: dims=(0.200, 0.200, 2.200), Wall_South_Col3: dims=(0.200, 0.200, 2.200)\n'}}
     ```

## Verification Summary
1. **Scene Collections & Containment**:
   - `Apt_OuterWalls`: Contains exactly the 11 outer wall objects.
   - Each wall object's `users_collection` is strictly `['Apt_OuterWalls']`.
   - `Apt_Floors`: Preserved all 8 floor slabs (`Floor_AlphaRoom`, `Floor_Balcony1`, `Floor_Bed1`, `Floor_Bed2`, `Floor_Bed3`, `Floor_Entrance_Bath1`, `Floor_Living_Dining`, `Floor_MasterSuite_North`) without modification.
   - `_DefaultObjects`: Preserved 3 hidden objects (`Cube`, `Light`, `Camera`).
   - `Apt_InteriorWalls` and `Apt_Openings`: Empty collections (0 objects), ready for subsequent tasks.

2. **Mesh Topology & Normal Orientation**:
   - Each wall box has exactly 8 vertices and 6 quad polygons.
   - Face normals verified pointing outward: (-Z, +Z, -Y, +X, +Y, -X).
   - Datablock hygiene: Exactly 20 mesh datablocks total (Cube + 8 floors + 11 walls), 0 orphaned unlinked meshes.

3. **Dimensional & Coordinate Precision**:

| Object Name | Dimensions (X, Y, Z) | X Range | Y Range | Z Range |
| :--- | :---: | :---: | :---: | :---: |
| `Wall_Party_West` | 0.200 × 10.615 × 2.300 m | [-0.200, 0.000] | [-0.200, 10.415] | [0.000, 2.300] |
| `Wall_Party_East` | 0.200 × 10.615 × 2.300 m | [9.865, 10.065] | [-0.200, 10.415] | [0.000, 2.300] |
| `Wall_North_Segment1` | 1.300 × 0.200 × 2.300 m | [0.000, 1.300] | [10.215, 10.415] | [0.000, 2.300] |
| `Wall_North_DoorHeader` | 1.000 × 0.200 × 0.200 m | [1.300, 2.300] | [10.215, 10.415] | [2.100, 2.300] |
| `Wall_North_Segment2` | 7.565 × 0.200 × 2.300 m | [2.300, 9.865] | [10.215, 10.415] | [0.000, 2.300] |
| `Wall_South_Header_All` | 9.865 × 0.200 × 0.100 m | [0.000, 9.865] | [-0.200, 0.000] | [2.200, 2.300] |
| `Wall_South_Sill_Bed3` | 2.100 × 0.200 × 0.800 m | [0.200, 2.300] | [-0.200, 0.000] | [0.000, 0.800] |
| `Wall_South_Sill_Bed2` | 2.000 × 0.200 × 0.800 m | [2.700, 4.700] | [-0.200, 0.000] | [0.000, 0.800] |
| `Wall_South_Col1` | 0.200 × 0.200 × 2.200 m | [2.400, 2.600] | [-0.200, 0.000] | [0.000, 2.200] |
| `Wall_South_Col2` | 0.200 × 0.200 × 2.200 m | [4.800, 5.000] | [-0.200, 0.000] | [0.000, 2.200] |
| `Wall_South_Col3` | 0.200 × 0.200 × 2.200 m | [7.650, 7.850] | [-0.200, 0.000] | [0.000, 2.200] |

## Deliverables
- [task3_outer_walls.py](file:///C:/Users/tamarand/orca/projects/apt/scripts/task3_outer_walls.py)
- Report: [.superpowers/sdd/2026-10-16-dongtan-84a-apartment-modeling/task-3-report.md](file:///C:/Users/tamarand/orca/projects/apt/.superpowers/sdd/2026-10-16-dongtan-84a-apartment-modeling/task-3-report.md)
