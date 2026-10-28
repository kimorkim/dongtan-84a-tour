import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import ts from 'typescript';
import { Scene, PerspectiveCamera } from 'three';
import { GTAOPass } from 'three/addons/postprocessing/GTAOPass.js';

const source = readFileSync(new URL('../src/ao-output-pass.ts', import.meta.url), 'utf8');
const compiled = ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ES2020 } }).outputText
 .replaceAll("'three/addons/postprocessing/OutputPass.js'",JSON.stringify(import.meta.resolve('three/addons/postprocessing/OutputPass.js')))
 .replaceAll("'three/addons/postprocessing/GTAOPass.js'",JSON.stringify(import.meta.resolve('three/addons/postprocessing/GTAOPass.js')));
const { AOOutputPass }=await import(`data:text/javascript;base64,${Buffer.from(compiled).toString('base64')}`);

test('AO composition happens before the original tone mapping without full-screen copy/blend passes',()=>{
 const ao=new GTAOPass(new Scene(),new PerspectiveCamera(),48,32);
 const output=new AOOutputPass(ao);
 try {
  assert.equal(ao.output,GTAOPass.OUTPUT.Off);
  assert.equal(ao.needsSwap,false,'scene color buffer must remain available to output');
  assert.equal(output.uniforms.tAO.value,ao.gtaoMap);
  const code=output.material.fragmentShader;
  assert.ok(code.indexOf('mix( vec3( 1.0 )')<code.indexOf('// tone mapping'));
  assert.ok(code.includes('gl_FragColor.a *= ao.a'), 'preserve destination alpha multiplication');
  assert.equal(ao.gtaoRenderTarget.width,48,'AO remains at native resolution');
  assert.equal(ao.pdMaterial.defines.SAMPLES,16,'retain actual denoising samples');
 }finally{output.dispose();ao.dispose();}
});
