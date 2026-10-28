import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import ts from 'typescript';
import {
  BoxGeometry,
  DoubleSide,
  FrontSide,
  Group,
  Mesh,
  MeshStandardMaterial,
  PlaneGeometry,
} from 'three';

const source = readFileSync(new URL('../src/material-sides.ts', import.meta.url), 'utf8');
const compiled = ts.transpileModule(source, {
  compilerOptions: { module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ES2020 },
}).outputText
  .replaceAll("'three'", JSON.stringify(import.meta.resolve('three')));
const { restrictDoubleSidedMaterials } = await import(`data:text/javascript;base64,${Buffer.from(compiled).toString('base64')}`);

test('closed opaque geometry becomes front-sided while open planes stay double-sided', () => {
  const root = new Group();
  const cabinetMaterial = new MeshStandardMaterial({ side: DoubleSide });
  const cardMaterial = new MeshStandardMaterial({ side: DoubleSide });
  const cabinet = new Mesh(new BoxGeometry(1, 1, 1), cabinetMaterial);
  const card = new Mesh(new PlaneGeometry(1, 1), cardMaterial);
  root.add(cabinet, card);

  const stats = restrictDoubleSidedMaterials(root);

  assert.equal(cabinetMaterial.side, FrontSide);
  assert.equal(cardMaterial.side, DoubleSide, 'single-surface cards must remain visible from behind');
  assert.equal(stats.materialsRestricted, 1);
  assert.equal(stats.watertightMeshes, 1);
});

test('a material shared with an open mesh and transparent materials are preserved', () => {
  const root = new Group();
  const shared = new MeshStandardMaterial({ side: DoubleSide });
  const glass = new MeshStandardMaterial({ side: DoubleSide, transparent: true, opacity: 0.3 });
  root.add(
    new Mesh(new BoxGeometry(1, 1, 1), shared),
    new Mesh(new PlaneGeometry(1, 1), shared),
    new Mesh(new BoxGeometry(1, 1, 1), glass),
  );

  const stats = restrictDoubleSidedMaterials(root);

  assert.equal(shared.side, DoubleSide, 'one open user prevents a material-wide side change');
  assert.equal(glass.side, DoubleSide, 'transparent materials keep their existing side');
  assert.equal(stats.materialsRestricted, 0);
});
