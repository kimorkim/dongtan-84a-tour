# AO and lighting math follow-up

User approved the recommended AO and light shader work. Preserve the earlier performance implementation (now bf7fb17), model detail, native DPR, AO precision and actual samples. No wall/room culling or deployment in this task. Execute inline in the current workspace.

- [x] Capture current Retina baseline (`math-before`) before changing production math.
- [x] Test sparse perspective inverse-projection detection, fallback and dynamic AO uniforms. Specialize AO arithmetic without changing texture samples or sample pattern.
- [x] Test and specialize inverse-square point-light attenuation, keeping arbitrary decay and unlimited-light fallback.
- [x] Measure each candidate independently against the existing improvements. Retain only measured improvements with negligible image differences and no shader errors/context loss.
- [x] Verify production build/main, smoke transitions and all tests; request read-only review after GPU measurements; update performance report and inventory. No commit/push/deployment.

Outcome: discard sparse projection/pow and inverse-square arithmetic changes (no measurable gain). Retain monochrome AO denoising plus RGBA16F -> R16F color targets and removal of unused AO depth attachments. Same native dimensions, half-float precision and actual16 samples. GPU3.3–9.3% faster at four fixed views; actual main33.96 ->34.72fps. AO color storage payload95.0 ->23.8MB at3024x1964. Tests18, typecheck, build and smoke pass; read-only review found no blockers. Not an M5 Pro measurement and no production deployment.
