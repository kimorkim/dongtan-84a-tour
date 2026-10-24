# Q22 Restandard Master Bed Implementation Plan

> Execute inline with the executing-plans workflow; preserve the current saved model.

**Goal:** Replace the master bed with the approved no-headboard K Restandard grey set on 115mm wood legs.
**Architecture:** A current-scene patch creates named Q22 meshes, leaving room structure and furnishings intact. Independent saved-mesh and exported-GLB checks enforce official sizes.
**Tech Stack:** Blender 4.2 Python, Pillow/NumPy, Three.js GLB tests, Vite.

## Global constraints

- K width1600/length2000; base150 + wood legs115 + upper mattress290mm.
- Centre1.805/3.2222, head west; rug support z=.022. Preserve Q12 and Q13–Q21.
- Back up root blend before mutation; do not rerun migrations or full scene generators.

## Task 1: Replacement and meaningful geometry checks

- [x] Add `scripts/verify_restandard_bed.py` and `web/tests/master-bed-model.test.mjs` checking real meshes/GLB bounds and legacy removal. Run before mutation and confirm missing Q22 failure.
- [x] Create `scripts/replace_master_bed.py`: backup current blend, remove only Bed_Master_/Q2_Master_Cushion, build upholstered twin bases, 8 wood legs, white quilted mattress and piping. Save root blend.
- [x] Run saved-mesh verifier and all Q12/Q13–Q21 regression scripts; bake collision with Q22 metadata, export using existing textured exporter. Run real GLB test and Python walk verifier.

## Task 2: Reviewable room and source records

- [x] Add `scripts/render_restandard_bed.py`: render room POV, product detail, overhead plus refresh presentation4 and overall plan36. Respect RENDER_DIR.
- [x] Inspect rendered PNGs and correct visible faults. Refresh master-bed and topdown WebP/thumbs only.
- [x] Document sources, approximations, scope and results in reference README, AGENTS and asset/quality documents. Update gallery description and targeted web checks.
- [x] Run all web tests/typecheck/build; compare build/public assets; review diff without committing or deploying unrelated work.

Ruling: work directly on the user's current Orca checkout, preserving its existing source and backup convention; no extra full model clone. User requested modification of this exact current model.

Ruling: omit a south-side walking goal after collision inspection showed the existing balcony door wall leaves a narrow gap. Preserve geometry and report the limit; validate north/foot routes instead.
Ruling: use CPU rendering. Querying OptiX devices exited the installed Blender process before render; CPU completed the same scene.

Q22b user amendment: remove decorative wall panel/LED strips, rigidly shift all bed components -320mm to the real west wall x=.485. Back up the pre-cleanup model; update generator, saved-mesh/GLB checks, export/collision and the same review/gallery slots. Product dimensions, rug, nightstand and structural walls stay intact.

Q22c user amendment: remove the bedroom rug and nightstand assembly including its tabletop lamp and hanging bedside pendant. Lower all bed parts22mm onto the wood floor z=0; keep wall alignment and nominal555mm set height. Back up before patching, update existing geometry/GLB checks and refresh the same exported assets/review/gallery slots.
