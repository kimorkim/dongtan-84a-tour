# Q24 Master Bathroom Implementation Plan

> **For agentic workers:** Execute inline with superpowers:executing-plans; review the complete result.

**Goal:** Rebuild the master bathroom from official scene011 and reverse the wrongly outward door.

**Architecture:** Scoped Blender script on saved current source; new Q24 assemblies, preserved structural walls and Q23c powder unit. Export and test the same saved scene, then render/gallery updates.

**Tech Stack:** Blender4.2 Python, existing mesh helpers, Three.js GLB tests, Pillow/Vite.

## Global Constraints

- Preserve x2.595~4.095/y5.970~8.170 structural envelope; main ceiling2300mm.
- Door opens inward/east from south hinge; no fixture or wall intersection during its sweep.
- Use scene011 official photos, keep northern tub/eastern sink and toilet; no invented shower enclosure.
- Keep Q23c fitted powder and Q22d bed unchanged.

### Task1: Physical model

- [x] Add `verify_master_bath.py`; fail on outward door and missing actual basin/cabinet/tile components.
- [x] Add `detail_master_bath.py`; back up current source, remove only obsolete master-bath assemblies, rebuild tile surfaces/fixtures/door/lighting, assert original wall geometry hash unchanged, save source.
- [x] Check saved geometry, door sweep/clearance and existing19 regression scripts.

### Task2: Web and visual verification

- [x] Add master-bath collision metadata and entry/interior/tub approach goals. Bake collision and export textured GLB.
- [x] Add real hierarchy-aware GLB tests for inward door, basin cavity, room bounds and cabinet/tile components.
- [x] Render entry view54, fixture view55, bath plan56 and refresh whole plan36/affected powder51+gallery.
- [x] Add master-bath gallery item and generated assets; update source/assumption docs and AGENTS.
- [x] Run web tests/typecheck/build and release hash checks. Inspect all new views against official photos; review changes.
