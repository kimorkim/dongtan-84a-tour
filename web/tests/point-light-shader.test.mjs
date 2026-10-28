import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import ts from 'typescript';
import { Group, Mesh, BoxGeometry, MeshStandardMaterial, MeshPhysicalMaterial, ShaderChunk } from 'three';

const source = readFileSync(new URL('../src/point-light-shader.ts', import.meta.url), 'utf8');
const compiled = ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ES2020 } }).outputText
  .replaceAll("'three'", JSON.stringify(import.meta.resolve('three')));
const { optimizePointLightShaders } = await import(`data:text/javascript;base64,${Buffer.from(compiled).toString('base64')}`);

test('zero-contribution guard encloses point-light BRDF and shadows, preserving other lights', () => {
  const root = new Group();const mat = new MeshStandardMaterial();
  root.add(new Mesh(new BoxGeometry(),mat));
  optimizePointLightShaders(root);
  const shader = { fragmentShader: '#include <lights_fragment_begin>' };
  mat.onBeforeCompile(shader, {});
  const code=shader.fragmentShader;
  assert.ok(code.includes('pointLight.distance <= 0.0'), 'unlimited lights must remain');
  assert.ok(code.includes('dot( lightOffset, lightOffset ) < pointLight.distance * pointLight.distance'));
  assert.ok(code.includes('dot( geometryClearcoatNormal, lightOffset ) > 0.0'), 'clearcoat can face the light when the base normal does not');
  assert.ok(code.indexOf('if ( pointLightContributes )') < code.indexOf('getPointLightInfo('));
  assert.ok(code.includes('getPointShadow('), 'retain original shadow computation');
  const tail=ShaderChunk.lights_fragment_begin.indexOf('#if ( NUM_SPOT_LIGHTS > 0 )');
  assert.equal(code.slice(code.indexOf('#if ( NUM_SPOT_LIGHTS > 0 )')), ShaderChunk.lights_fragment_begin.slice(tail));
  assert.notEqual(mat.customProgramCacheKey(), new MeshStandardMaterial().customProgramCacheKey());
});

test('material sharing, physical parameters and custom shader hooks are preserved', () => {
  const root = new Group();const mat = new MeshPhysicalMaterial({clearcoat:1,roughness:.3});
  root.add(new Mesh(new BoxGeometry(), mat), new Mesh(new BoxGeometry(), [mat,mat]));
  const custom = new MeshStandardMaterial();const hook = () => {};custom.onBeforeCompile=hook;
  root.add(new Mesh(new BoxGeometry(),custom));
  optimizePointLightShaders(root);const key=mat.customProgramCacheKey();
  optimizePointLightShaders(root);
  assert.equal(mat.customProgramCacheKey(), key, 'idempotent preparation');
  assert.equal(root.children[0].material, mat, 'no material clones or extra shader permutations');
  assert.equal(mat.clearcoat,1);assert.equal(mat.roughness,.3);
  assert.equal(custom.onBeforeCompile, hook);
});
