import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import ts from 'typescript';

const source = readFileSync(new URL('../src/performance.ts', import.meta.url), 'utf8');
const compiled = ts.transpileModule(source, {
  compilerOptions: { module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ES2020 },
}).outputText;
const { AdaptivePixelRatio, AOFrameScheduler, aoUpdateInterval } = await import(
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

  for (let i = 0; i < 30; i++) assert.equal(ratio.observe(10), null);
  assert.equal(ratio.value, 1.25, 'one fast window is not enough to raise quality');
  for (let i = 0; i < 29; i++) assert.equal(ratio.observe(10), null);
  assert.equal(ratio.observe(10), 1.5);
});

test('adaptive pixel ratio respects a lower device maximum', () => {
  assert.equal(new AdaptivePixelRatio(1.25).value, 1.25);
  assert.deepEqual(new AdaptivePixelRatio(1.25).levels, [1.25, 1]);
  assert.equal(new AdaptivePixelRatio(1).value, 1);
});

test('AO scheduler reuses the previous AO while the camera moves', () => {
  assert.equal(aoUpdateInterval(1.5), 2);
  assert.equal(aoUpdateInterval(1.25), 3);

  const scheduler = new AOFrameScheduler();
  assert.equal(scheduler.shouldUpdate(false, 1.5), true, 'first frame builds AO');
  assert.equal(scheduler.shouldUpdate(true, 1.5), false);
  assert.equal(scheduler.shouldUpdate(true, 1.5), true);
  assert.equal(scheduler.shouldUpdate(true, 1.25), false);
  assert.equal(scheduler.shouldUpdate(true, 1.25), false);
  assert.equal(scheduler.shouldUpdate(true, 1.25), true);
  scheduler.forceUpdate();
  assert.equal(scheduler.shouldUpdate(true, 1.25), true, 'mode and visibility changes refresh AO immediately');
  assert.equal(scheduler.shouldUpdate(false, 1.25), true, 'a still camera always receives fresh AO');
});
