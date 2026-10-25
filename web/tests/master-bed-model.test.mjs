import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { Box3, Matrix4, Quaternion, Vector3 } from 'three';

test('master bedroom exports the approved Restandard K set without a headboard', () => {
  const bytes = readFileSync(new URL('../public/house.glb', import.meta.url));
  const g = JSON.parse(bytes.subarray(20, 20 + bytes.readUInt32LE(12)).toString());
  const selected = prefix => g.nodes.filter(n => n.mesh !== undefined && n.name?.startsWith(prefix));
  const box = prefix => {
    const out = new Box3();
    const nodes = selected(prefix);
    assert.ok(nodes.length, `Missing ${prefix}`);
    for (const n of nodes) {
      const m = n.matrix ? new Matrix4().fromArray(n.matrix) : new Matrix4().compose(
        new Vector3(...(n.translation ?? [0,0,0])), new Quaternion(...(n.rotation ?? [0,0,0,1])), new Vector3(...(n.scale ?? [1,1,1])));
      for (const p of g.meshes[n.mesh].primitives) {
        const a = g.accessors[p.attributes.POSITION];
        out.union(new Box3(new Vector3(...a.min), new Vector3(...a.max)).applyMatrix4(m));
      }
    }
    return out;
  };
  const close = (a,b) => assert.ok(Math.abs(a-b) < .002, `${a} != ${b}`);
  const mattress = box('Q22_Restandard_Mattress');
  const size = mattress.getSize(new Vector3());
  close(size.x, 2); close(size.y, .290); close(size.z, 1.6);
  close(mattress.min.y, .265); close(mattress.max.y, .555);
  close(mattress.min.x, 2.085); close(mattress.max.x, 4.085); close(-mattress.max.z, 3.10); close(-mattress.min.z, 4.70);
  for (const name of ['Q2_Master_Panel','Q2_Master_CoveTop','Q2_Master_CoveLow']) {
    assert.ok(!g.nodes.some(n => n.name === name), `Unwanted decorative wall/strip: ${name}`);
  }
  const all = box('Q22_Restandard_');
  close(all.min.y, 0);
  assert.equal(selected('Q22_Restandard_Leg').length, 8);
  assert.ok(!g.nodes.some(n => n.name?.startsWith('Bed_Master_') || n.name?.startsWith('Q2_Master_Cushion')));
  for (const side of ['S','N']) {
    const b = box('Q22_Restandard_Base'+side).getSize(new Vector3());
    close(b.x, 2); close(b.y, .15); close(b.z, .8);
  }
  assert.ok(!g.nodes.some(n => n.name === 'Q2_Master_Rug' || n.name?.startsWith('Nightstand_Master_') || n.name?.startsWith('Q2_Night') || n.name?.startsWith('Q2_Pendant')));
  assert.ok(selected('Q21_WashTower_').length);
  const collisions = JSON.parse(readFileSync(new URL('../public/colliders.json', import.meta.url)));
  assert.equal(collisions.master_bed_version, 22);
});
