import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import { GTAOPass } from 'three/addons/postprocessing/GTAOPass.js';
import type { IUniform, WebGLRenderer, WebGLRenderTarget } from 'three';

/** Combine denoised AO and output conversion in one draw, retaining native AO buffers. */
export class AOOutputPass extends OutputPass {
  declare uniforms: Record<string, IUniform>;
  constructor(private readonly ao: GTAOPass) {
    super();
    this.uniforms.tAO = { value: ao.gtaoMap };
    this.uniforms.aoIntensity = { value: ao.blendIntensity };
    this.material.fragmentShader = this.material.fragmentShader
      .replace('uniform sampler2D tDiffuse;', 'uniform sampler2D tDiffuse;\nuniform sampler2D tAO;\nuniform float aoIntensity;')
      .replace('gl_FragColor = texture2D( tDiffuse, vUv );', `gl_FragColor = texture2D( tDiffuse, vUv );
        vec4 ao = texture2D( tAO, vUv );
        gl_FragColor.rgb *= mix( vec3( 1.0 ), vec3( ao.r ), aoIntensity );
        gl_FragColor.a *= ao.a;`);
    // GTAOPass.OUTPUT.Off: compute normals, AO and denoising, then leave scene color alone.
    this.material.needsUpdate = true;
    ao.output = GTAOPass.OUTPUT.Off;
    ao.needsSwap = false;
  }

  override render(renderer: WebGLRenderer, writeBuffer: WebGLRenderTarget, readBuffer: WebGLRenderTarget,
    deltaTime = 0, maskActive = false): void {
    this.uniforms.tAO.value = this.ao.gtaoMap;
    this.uniforms.aoIntensity.value = this.ao.blendIntensity;
    super.render(renderer, writeBuffer, readBuffer, deltaTime, maskActive);
  }
}
