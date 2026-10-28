# Q23 Dressroom and Powder Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans inline for this approved change.

**Goal:** Clear the intersecting closet and install an approved fitted makeup vanity opposite the master bathroom.

**Q23c ruling (completed):** User requested no side gaps. Replace the1100mm width with actual south/north wall measurements at every mesh vertex, leaving0.5mm seams. Actual width is about1235–1249mm. All19 model checks,39 walking goals,10 web tests, typecheck/build, render review and4 release asset hashes pass.

**Architecture:** Modify the current saved Blender scene with a scoped, repeatable script, retaining structural geometry. Export the same scene to collision and GLB assets; refresh review images and gallery.

**Tech Stack:** Blender 4.2 Python, existing asset helpers, Pillow, Three.js/Node tests, Vite.

**Q23b ruling:** User photos supersede the first draft. Replace the knee void and drawer pedestals with full recessed lower storage,2 shallow handleless drawers, a tall central mirror and ceiling-height side cupboards. Keep the location and bright room colours. See `references/furniture/powder-reference.md`. Revised geometry and GLB checks failed on the draft before replacement and pass after it.

## Global Constraints

- Keep Q12 structure/windows and Q22d bed; never rerun whole-scene migrations.
- Vanity x=.495~.945/y5.940~7.040/top=.750m; +X front; continuous lower storage and ceiling-height upper cupboards/mirror.
- Clear Dress_Closet_* and Wardrobe_Dress_*; leave the north dressing room empty.
- Photo-based style and proposed dimensions are not manufacturer specifications.

### Task 1: Model repair

- [x] Add `scripts/verify_dressroom_powder.py`; fail on retained closet, missing vanity or incorrect clearance. Run it against the unchanged source and confirm failure.
- [x] Add `scripts/detail_dressroom_powder.py`: backup to `models/backups/apt_84a_photoreal_tour_before_dressroom_powder.blend`, clear scoped old furniture, build Q23_Powder_* materials and meshes, save source. Store structural geometry fingerprint for verification.
- [x] Run new check and all18 saved-model regression checks. Inspect actual mesh rays/door clearance and reference-style lower/upper storage.

### Task 2: Export and review

- [x] Add Q23 collision metadata in `scripts/bake_collision.py`, add powder approach/bath approach/north dressroom goals to `scripts/verify_master_balcony.py`.
- [x] Run collision bake and textured GLB export from the saved source. Add real GLB check `web/tests/dressroom-powder.test.mjs` with hierarchy-aware world bounds.
- [x] Add `scripts/render_dressroom_powder.py` for powder POV, empty north room and regional plan; also refresh presentation7 and whole plan36 without saving temporary settings.
- [x] Update gallery text/position and only affected WebP images. Update AGENTS, asset guide/inventory and quality report with sources and limitations.
- [x] Confirm all model, walk, web, typecheck/build results; visually inspect new renders and final git diff.
