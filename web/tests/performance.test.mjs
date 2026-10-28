import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import ts from 'typescript';

const source = readFileSync(new URL('../src/performance.ts', import.meta.url), 'utf8');
const compiled = ts.transpileModule(source, {
  compilerOptions: { module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ES2020 },
}).outputText;
const { AdaptivePixelRatio } = await import(
  `data:text/javascript;base64,${Buffer.from(compiled).toString('base64')}`
);

test('adaptive pixel ratio starts below the DPR cap and steps down under load', () => {
  const ratio = new AdaptivePixelRatio(2);
  assert.equal(ratio.value, 1.5);
  assert.deepEqual(ratio.levels, [2, 1.75, 1.5, 1.25, 1]);

  for (let i = 0; i < 29; i++) assert.equal(ratio.observe(40), null);
  assert.equal(ratio.observe(40), 1.25);
  assert.equal(ratio.value, 1.25);

  // A long tab-switch pause must not be treated as a slow rendered frame.
  for (let i = 0; i < 30; i++) ratio.observe(500);
  assert.equal(ratio.value, 1.25);
});

test('adaptive pixel ratio recovers only after two consecutive fast windows', () => {
  const ratio = new AdaptivePixelRatio(2);
  for (let i = 0; i < 30; i++) ratio.observe(40);
  assert.equal(ratio.value, 1.25);

  for (let i = 0; i < 30; i++) ratio.observe(10), null;
  assert.equal(ratio.value, 1.25, 'one fast window is not enough to raise quality');
  for (let i = 0; i < 29; i++) assert.equal(ratio.observe(10), null);
  assert.equal(ratio.observe(10), 1.5);
});

test('adaptive pixel ratio respects a lower device maximum', () => {
  assert.equal(new AdaptivePixelRatio(1.25).value, 1.25);
  assert.deepEqual(new AdaptivePixelRatio(1.25).levels, [1.25, 1]);
  assert.equal(new AdaptivePixelRatio(1).value, 1);
});
