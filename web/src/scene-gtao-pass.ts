import { RedFormat } from 'three';
import type { Sprite } from 'three';
import { GTAOPass } from 'three/addons/postprocessing/GTAOPass.js';

export class SceneGTAOPass extends GTAOPass {
  private originalDenoiseShader?: string;
  private scalarMath = false;
  private originalAoFormat = this.gtaoRenderTarget.texture.format;
  private originalPdFormat = this.pdRenderTarget.texture.format;
  private originalAoDepth = this.gtaoRenderTarget.depthBuffer;
  private originalPdDepth = this.pdRenderTarget.depthBuffer;

  /** AO is monochrome: keep its half-float precision in one channel instead of four. */
  setMathOptimization(enabled: boolean): void {
    if (enabled === this.scalarMath) return;
    this.originalDenoiseShader ??= this.pdMaterial.fragmentShader;
    const replacements = [
      ['in vec3 center', 'in float center'],
      ['inout vec3 denoised', 'inout float denoised'],
      ['vec3 neighborColor = sampleTexel.rgb;', 'float neighborColor = sampleTexel.r;'],
      ['getLuminance(neighborColor) - getLuminance(center)', 'neighborColor - center'],
      ['vec3 center = texel.rgb;', 'float center = texel.r;'],
      ['vec3 denoised = texel.rgb;', 'float denoised = texel.r;'],
      ['vec4(denoised, 1.)', 'vec4(vec3(denoised), 1.)'],
    ];
    if (enabled && replacements.some(([from]) => !this.originalDenoiseShader!.includes(from))) return;
    this.pdMaterial.fragmentShader = enabled ? replacements.reduce((code, [from, to]) =>
      code.replace(from, to), this.originalDenoiseShader) : this.originalDenoiseShader;
    this.pdMaterial.needsUpdate = true;
    for (const [target, originalFormat, originalDepth] of [[this.gtaoRenderTarget, this.originalAoFormat, this.originalAoDepth],
      [this.pdRenderTarget, this.originalPdFormat, this.originalPdDepth]] as const) {
      target.dispose();
      target.texture.format = enabled ? RedFormat : originalFormat;
      target.depthBuffer = enabled ? false : originalDepth;
      target.texture.needsUpdate = true;
    }
    this.scalarMath = enabled;
  }

  override overrideVisibility(): void {
    super.overrideVisibility();
    // GTAO's normal override drops sprite alpha; the inherited cache restores it afterwards.
    this.scene.traverse((object) => {
      if ((object as Sprite).isSprite) object.visible = false;
    });
  }
}
