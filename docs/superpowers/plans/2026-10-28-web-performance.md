# Full detail web performance implementation plan

**Goal:** Reduce runtime render costs without simplifying the model or lowering visual settings.

**Architecture:** Prepare static meshes once after GLB/material loading. Batch compatible opaque geometry within spatial cells and separate ceiling visibility. Reuse static shadow maps until visibility changes.

**Tech Stack:** Three.js 0.170, TypeScript, Vite, Node tests, Chromium/Playwright.

## Constraints

- Preserve all geometry, textures, lighting, GTAO settings, pixel ratio, Blender source, GLB, collision data and galleries.
- Transparent and unsupported animated/skinned geometry remain unbatched.
- No external package dependency needed in the web app.

## Tasks

- [x] Baseline: add `web/tests/performance-review.html` with fixed foyer/living/bath/overview cameras, actual composer, per-frame renderer counters and frame timing. Measure using local Chromium and keep images under `assets/analysis/web-performance/`.
- [x] Batching RED: add behavioral tests to `web/tests/static-model.test.mjs`. Verify world-space vertices, UVs, materials, triangle count, ceiling isolation, transparency, parent transforms, and spatial separation; run and observe missing implementation failure.
- [x] Batching GREEN: implement `web/src/static-model.ts` using `mergeGeometries`, single-material opaque primitives, local transforms and spatial cells; integrate after material processing in `world.ts`.
- [x] Shadows: cache sun shadow after first render and mark it dirty when ceiling visibility changes; verify mode transitions in the browser. Freeze static model local/world matrices after preparation.
- [x] Compare: benchmark baseline/optimized toggles at identical cameras and resolution; verify image equivalence and draw-call savings. Keep changes only if measurements support them.
- [x] Verify: `npm.cmd test`, `npm.cmd run typecheck`, `npm.cmd run build`, browser smoke tests and `git diff --check`. Document exact results and limitations in web README/report and asset inventory.

## Execution record

Using the current user-selected workspace; source assets remain untouched. Execute inline without new agents. Design approval is the user's request to proceed with high detail after the preceding performance proposal. Commit/push is outside this implementation task unless requested.
