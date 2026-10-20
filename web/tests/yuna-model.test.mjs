import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { Box3, Matrix4, Quaternion, Vector3 } from 'three';

test('Yuna furnishings and alpha glass survive the actual GLB export', () => {
  const bytes = readFileSync(new URL('../public/house.glb', import.meta.url));
  const length = bytes.readUInt32LE(12);
  const gltf = JSON.parse(bytes.subarray(20, 20 + length).toString());
  const names = gltf.nodes.map(node => node.name ?? '');
  for (const name of ['Q10_Mattress', 'Q10_Wardrobe_Back', 'Q10_ActivityTop', 'Q10_Rug_Center', 'Q10_Bunny_Body']) {
    assert.ok(names.includes(name), `${name} missing from tour`);
  }
  assert.ok(!names.some(name => name.startsWith('Bed3_') || name.startsWith('Wardrobe_Bed3_')));
  const parents = new Map();
  gltf.nodes.forEach((node,i)=>(node.children||[]).forEach(child=>parents.set(child,i)));
  function world(index) {
    const node=gltf.nodes[index];
    const matrix=node.matrix ? new Matrix4().fromArray(node.matrix) : new Matrix4().compose(
      new Vector3(...(node.translation||[0,0,0])),new Quaternion(...(node.rotation||[0,0,0,1])),
      new Vector3(...(node.scale||[1,1,1])));
    return parents.has(index) ? world(parents.get(index)).multiply(matrix) : matrix;
  }
  const index=names.indexOf('Q10_Wardrobe_Back');
  const cabinet=new Box3();
  for (const primitive of gltf.meshes[gltf.nodes[index].mesh].primitives) {
    const position=gltf.accessors[primitive.attributes.POSITION];
    cabinet.union(new Box3(new Vector3(...position.min),new Vector3(...position.max)).applyMatrix4(world(index)));
  }
  assert.ok(cabinet.max.z < -3.6 && cabinet.max.y >= 2.28 && cabinet.min.y < .01,
    'Basic built-in moved away from the entrance wall or no longer fits the ceiling');
  for (const name of ['Win_Bed3_Glass1', 'Win_Bed3_Glass2']) {
    const node = gltf.nodes.find(node => node.name === name);
    assert.ok(node && node.mesh !== undefined, `${name} missing`);
    for (const primitive of gltf.meshes[node.mesh].primitives) {
      const material = gltf.materials[primitive.material];
      assert.equal(material.alphaMode, 'BLEND', `${name} exported opaque`);
      assert.ok(material.pbrMetallicRoughness.baseColorFactor[3] < .1);
    }
  }
  for (const image of ['gallery/yuna-room.webp', 'gallery/thumbs/yuna-room.webp']) {
    assert.ok(readFileSync(new URL('../public/' + image, import.meta.url)).length > 1000);
  }
});
