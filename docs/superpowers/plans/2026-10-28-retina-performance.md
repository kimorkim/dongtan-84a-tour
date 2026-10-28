# Retina performance implementation plan

Goal: reduce native Retina GPU rendering cost without reducing detail or output quality.

Architecture: retain the renderer and asset pipeline; profile development-only switches, then skip zero-contribution work in the existing rendering path. Execute inline in the user-selected workspace.

- [x] Extend `scripts/benchmark_web.cjs` with viewport/DPR/query options; record native Retina baseline and AO/light isolation.
- [x] Add failing behavior tests for the selected optimization; verify failure, implement the smallest production change, and verify pass.
- [x] Compare baseline/optimized GPU timing and screenshots at identical Retina resolution for foyer/living/bath/overview. Check real main page and mode transitions.
- [x] Run all web tests, typecheck and build; review diff; document scope, results and limitations in the performance report and asset inventory.

Outcome: retain a per-pixel zero-contribution point-light guard and fused AO/output pass. Discard per-mesh light masks because extra material variants increased CPU/GPU cost. Initial unscoped loop-variable experiment failed shader compilation; its timings and images were discarded. The final benchmark rejects shader console errors and GPU context loss and uses a unique debug port per browser. Native Retina build/main measurement: 26.93 -> 33.96fps on Radeon8060S, not a MacBook measurement. Reviewer found no blocking correctness issues; applied constant naming and shader-update hardening. No commit/push/deployment performed.
