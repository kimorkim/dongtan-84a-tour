# Web performance with full model detail

User authorization: improve web performance while retaining high detail. The existing proposal to reduce redundant shadows and draw calls is approved by the user's instruction to proceed. Do not reduce geometry, texture resolution, lighting, GTAO quality, or display resolution.

Use runtime spatial batching of compatible static opaque meshes, after material adjustments. Keep separate batches for ceiling visibility, material, shadow flags, and spatial cells. Preserve transforms, normals, UVs, material groups, transparent sorting, and door assembly transforms. Keep original GLB and Blender source unchanged. Cache the static sun shadow and invalidate it when ceiling visibility changes. Freeze static model transforms after preparation.

Measure identical fixed cameras before/after using the real GLB, lighting, GTAO, and pixel ratio. Record draw calls, submitted triangles, frame times, GPU renderer, and image differences. Browser benchmark frames are controlled measurements, not a guarantee of FPS on the user's device. Run existing GLB tests, regression tests of batching/visibility, typecheck, and production build.
