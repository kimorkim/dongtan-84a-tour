# Retina performance follow-up

User request: improve the live tour after Chrome on a MacBook M5 Pro remained below 30fps. This extends the approved full-detail performance work; execute in the current user workspace. No geometry, texture, light appearance, GTAO quality or display-resolution reduction. No commit, push or production deployment requested.

The live JavaScript already contains static batching and shadow caching. An actual production-page test on Radeon 8060S measured 60fps at 1280x720 DPR1, 27.3fps at 1512x982 DPR2 and 19.4fps at 1920x1080 DPR2. These are not M5 Pro measurements.

Options considered: lower display resolution (violates existing constraint), lower AO quality (violates constraint), or eliminate mathematically zero lighting work and redundant full-screen processing (selected). First isolate AO versus point-light cost at native Retina resolution. Only retain a change with measured GPU-time improvement and visual comparison at the same camera, resolution and settings.

Keep changes local until verified. Test finite-range light exclusion, tangent/intersection boundaries, lighting order and fallback behavior if applicable. Verify all existing tests, typecheck, build, real-page movement and mode transitions. Report actual measured performance without a MacBook guarantee.

Final implementation: keep material sharing and shader-program counts unchanged. At each point light, skip attenuation/shadow/BRDF work only when the fragment is outside its finite cutoff or both base/clearcoat normals face away. Preserve unlimited lights. Merge denoised AO multiplication with the original OutputPass before tone mapping, eliminating two full-screen draws. Retain all AO buffers and actual denoising samples; expect small rounding/noise differences from removing intermediate half-float writes. No per-mesh light pruning retained.
