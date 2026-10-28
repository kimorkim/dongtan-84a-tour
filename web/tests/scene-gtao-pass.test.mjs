import test from 'node:test';
import assert from 'node:assert/strict';
import { Scene, PerspectiveCamera, Sprite, Mesh, BoxGeometry, MeshBasicMaterial, RedFormat, RGBAFormat, HalfFloatType } from 'three';
import { readFileSync } from 'node:fs';
import ts from 'typescript';

const source = readFileSync(new URL('../src/scene-gtao-pass.ts', import.meta.url), 'utf8');
const compiled = ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ES2020 } }).outputText
  .replaceAll("'three'", JSON.stringify(import.meta.resolve('three')))
  .replace("'three/addons/postprocessing/GTAOPass.js'", JSON.stringify(import.meta.resolve('three/addons/postprocessing/GTAOPass.js')));
const { SceneGTAOPass } = await import(`data:text/javascript;base64,${Buffer.from(compiled).toString('base64')}`);

test('scalar AO denoising preserves samples and can restore the original shader',()=>{
  const pass=new SceneGTAOPass(new Scene(),new PerspectiveCamera(),32,32);
  try {
    const original=pass.pdMaterial.fragmentShader;
    const samples=pass.pdMaterial.defines.SAMPLES;
    const pattern=pass.pdMaterial.defines.SAMPLE_VECTORS;
    assert.equal(typeof pass.setMathOptimization,'function');
    pass.setMathOptimization(true);
    const code=pass.pdMaterial.fragmentShader;
    assert.ok(code.includes('in float center'));
    assert.ok(code.includes('inout float denoised'));
    assert.ok(code.includes('abs(neighborColor - center)'));
    assert.equal(pass.pdMaterial.defines.SAMPLES,samples);
    assert.equal(pass.pdMaterial.defines.SAMPLE_VECTORS,pattern);
    assert.equal(pass.gtaoRenderTarget.texture.format,RedFormat);
    assert.equal(pass.pdRenderTarget.texture.format,RedFormat);
    assert.equal(pass.gtaoRenderTarget.texture.type,HalfFloatType,'preserve 16-bit AO precision');
    assert.equal(pass.gtaoRenderTarget.depthBuffer,false,'fullscreen AO does not use a depth attachment');
    assert.equal(pass.pdRenderTarget.depthBuffer,false);
    assert.equal(pass.normalRenderTarget.depthBuffer,true,'normal/depth scene buffer is retained');
    assert.equal(pass.width,32);assert.equal(pass.height,32);
    pass.setMathOptimization(true);assert.equal(pass.pdMaterial.fragmentShader,code);
    pass.setMathOptimization(false);assert.equal(pass.pdMaterial.fragmentShader,original);
    assert.equal(pass.gtaoRenderTarget.texture.format,RGBAFormat);
    assert.equal(pass.pdRenderTarget.texture.format,RGBAFormat);
    assert.equal(pass.gtaoRenderTarget.depthBuffer,true);
    assert.equal(pass.pdRenderTarget.depthBuffer,true);
  }finally{pass.dispose();}
});

test('transparent hotspot quads do not enter AO, and visibility is restored', () => {
  const scene = new Scene();
  const badge = new Sprite();
  const hiddenBadge = new Sprite();
  hiddenBadge.visible = false;
  const wall = new Mesh(new BoxGeometry(), new MeshBasicMaterial());
  scene.add(badge, hiddenBadge, wall);
  const pass = new SceneGTAOPass(scene, new PerspectiveCamera(), 32, 32);
  try {
    pass.overrideVisibility();
    assert.equal(badge.visible, false, 'hotspot quad casts rectangular AO');
    assert.equal(wall.visible, true, 'real walls still contribute AO');
    pass.restoreVisibility();
    assert.equal(badge.visible, true, 'hotspot must reappear in the color pass');
    assert.equal(hiddenBadge.visible, false, 'hidden hotspots must stay hidden');
  } finally {
    pass.dispose();
    wall.geometry.dispose();
    wall.material.dispose();
  }
});
