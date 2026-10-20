import test from 'node:test';
import assert from 'node:assert/strict';
import { Scene, PerspectiveCamera, Sprite, Mesh, BoxGeometry, MeshBasicMaterial } from 'three';
import { readFileSync } from 'node:fs';
import ts from 'typescript';

const source = readFileSync(new URL('../src/scene-gtao-pass.ts', import.meta.url), 'utf8');
const compiled = ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ES2020 } }).outputText
  .replace("'three/addons/postprocessing/GTAOPass.js'", JSON.stringify(import.meta.resolve('three/addons/postprocessing/GTAOPass.js')));
const { SceneGTAOPass } = await import(`data:text/javascript;base64,${Buffer.from(compiled).toString('base64')}`);

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
