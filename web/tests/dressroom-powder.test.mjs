import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { Box3, Matrix4, Quaternion, Vector3 } from 'three';

test('powder vanity replaces the wall-crossing closet and leaves bathroom and dressing approaches clear', () => {
  const bytes = readFileSync(new URL('../public/house.glb', import.meta.url));
  const g = JSON.parse(bytes.subarray(20, 20 + bytes.readUInt32LE(12)).toString());
  assert.ok(!g.nodes.some(n => /^(Dress_Closet_|Wardrobe_Dress_)/.test(n.name ?? '')), 'Wall-crossing closet retained');
  const world = new Map();
  function visit(i, parent) {
    const n = g.nodes[i];
    const local = n.matrix ? new Matrix4().fromArray(n.matrix) : new Matrix4().compose(
      new Vector3(...(n.translation ?? [0,0,0])), new Quaternion(...(n.rotation ?? [0,0,0,1])), new Vector3(...(n.scale ?? [1,1,1])));
    const m = parent.clone().multiply(local);
    world.set(i, m);
    for (const child of n.children ?? []) visit(child, m);
  }
  for (const i of g.scenes[g.scene ?? 0].nodes) visit(i, new Matrix4());
  const boxes = new Map();
  for (const [i,m] of world) {
    const n = g.nodes[i];
    if (n.mesh === undefined) continue;
    const box = new Box3();
    for (const p of g.meshes[n.mesh].primitives) {
      const a = g.accessors[p.attributes.POSITION];
      box.union(new Box3(new Vector3(...a.min), new Vector3(...a.max)).applyMatrix4(m));
    }
    boxes.set(n.name,box);
  }
  const top = boxes.get('Q23_Powder_Top');
  assert.ok(top, 'Missing proposed makeup vanity');
  // Blender(x,y,z) -> glTF(x,z,-y).
  assert.ok(top.min.x > .485 && top.max.x < .947, 'Top intersects west wall or projects into aisle');
  assert.ok(top.min.z > -7.10 && top.min.z < -7.08 && top.max.z > -5.86 && top.max.z < -5.84,
    'Fitted top must reach both niche wall faces');
  assert.ok(Math.abs(top.max.y-.750) < .002);
  for (const side of ['S','N']) {
    const upper=boxes.get('Q23_Powder_UpperCab'+side);
    assert.ok(upper, 'Missing tall side storage: '+side);
    assert.ok(upper.max.y>2.27 && upper.min.y<.90);
    assert.ok(boxes.get('Q23_Powder_LowerDoor'+side));
  }
  const mirror=boxes.get('Q23_Powder_Mirror');
  assert.ok(mirror && mirror.max.y>2.20 && mirror.min.y<.90);
  assert.ok(![...boxes.keys()].some(n => /Q23_Powder_(Pull|Pencil|LightBar|LightDiffuser)/.test(n)), 'Old standalone styling retained');
  assert.ok(boxes.get('ProDoorLeaf_MasterBath').min.x-top.max.x > 1.1);
  const data = JSON.parse(readFileSync(new URL('../public/colliders.json', import.meta.url)));
  assert.equal(data.dressroom_powder_version,23);
  const blocked = (x,y) => data.boxes.some(([a,b,c,d]) => x>=a && x<=c && y>=b && y<=d);
  assert.ok(blocked(.70,6.0), 'Vanity pedestal absent from collision');
  for (const [x,y] of [[1.45,6.45],[1.85,6.35],[1.60,7.55],[1.45,9.2]])
    assert.ok(!blocked(x,y), `Approach blocked at ${x},${y}`);
});
