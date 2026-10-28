import { Material, Mesh, MeshStandardMaterial, ShaderChunk } from 'three';
import type { Object3D } from 'three';

/** Skip only mathematically zero direct-light terms, before attenuation and BRDF work.
 * Keep native pixels, light falloff, all contributing BRDF terms and shadow sampling.
 * Unlike per-mesh light lists this adds no material/program permutations or static assumptions.
 */
export function optimizePointLightShaders(root: Object3D): void {
  const chunk = ShaderChunk.lights_fragment_begin;
  const start = chunk.indexOf('#if ( NUM_POINT_LIGHTS > 0 )');
  const end = chunk.indexOf('#if ( NUM_SPOT_LIGHTS > 0 )');
  const first = 'getPointLightInfo( pointLight, geometryPosition, directLight );';
  const last = '\n\t}\n\t#pragma unroll_loop_end';
  const body = chunk.slice(start, end);
  // Use stock shading if a future dependency changes this pinned shader's structure.
  if (start < 0 || end < start || !body.includes(first) || !body.includes(last)) return;
  const guarded = chunk.slice(0, start) + body.replace(first, `{
    vec3 lightOffset = pointLight.position - geometryPosition;
    bool pointLightContributes = dot( geometryNormal, lightOffset ) > 0.0;
    #ifdef USE_CLEARCOAT
      pointLightContributes = pointLightContributes || dot( geometryClearcoatNormal, lightOffset ) > 0.0;
    #endif
    pointLightContributes = pointLightContributes && ( pointLight.distance <= 0.0 ||
      dot( lightOffset, lightOffset ) < pointLight.distance * pointLight.distance );
    if ( pointLightContributes ) {
      ${first}`)
    .replace(last, `\n    }\n    }${last}`) + chunk.slice(end);
  const seen = new Set<Material>();
  root.traverse(object => {
    if (!(object instanceof Mesh)) return;
    const materials = Array.isArray(object.material) ? object.material : [object.material];
    for (const material of materials) {
      if (!(material instanceof MeshStandardMaterial) || seen.has(material) ||
          material.onBeforeCompile !== Material.prototype.onBeforeCompile ||
          material.customProgramCacheKey !== Material.prototype.customProgramCacheKey) continue;
      seen.add(material);
      material.onBeforeCompile = shader => {
        shader.fragmentShader = shader.fragmentShader.replace('#include <lights_fragment_begin>', guarded);
      };
      material.customProgramCacheKey = () => 'point-light-contribution-v1';
      material.needsUpdate = true;
    }
  });
}
