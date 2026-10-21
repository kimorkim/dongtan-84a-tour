import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { Box3, Matrix4, Quaternion, Vector3 } from 'three';

test('Brest ivory sofa replaces the old sofa at the official closed size',()=>{
  const bytes=readFileSync(new URL('../public/house.glb',import.meta.url));
  const g=JSON.parse(bytes.subarray(20,20+bytes.readUInt32LE(12)).toString());
  assert.ok(!g.nodes.some(n=>n.name?.startsWith('Sofa_Living_') || n.name?.startsWith('Q2_Sofa')));
  const parts=g.nodes.filter(n=>n.name?.startsWith('Q14_Brest_') && n.mesh!==undefined);
  assert.ok(parts.length>25);
  const box=new Box3();
  for(const n of parts) {
    const m=n.matrix ? new Matrix4().fromArray(n.matrix) : new Matrix4().compose(
      new Vector3(...(n.translation??[0,0,0])),new Quaternion(...(n.rotation??[0,0,0,1])),
      new Vector3(...(n.scale??[1,1,1])));
    for(const p of g.meshes[n.mesh].primitives) {
      const a=g.accessors[p.attributes.POSITION];
      box.union(new Box3(new Vector3(...a.min),new Vector3(...a.max)).applyMatrix4(m));
    }
  }
  for(const [value,expected] of [[box.max.x-box.min.x,1],[box.max.y-box.min.y,.95],
    [box.max.z-box.min.z,2.85],[8.805-box.max.x,.15]]) assert.ok(Math.abs(value-expected)<.002);
  for(const name of ['FoldTray','Headrest0','Headrest2','Footrest0','Footrest2']) {
    assert.ok(parts.some(n=>n.name==='Q14_Brest_'+name));
  }
  const leather=g.materials.find(m=>m.name==='Mat_Q14_IvoryLeather');
  assert.ok(leather?.pbrMetallicRoughness.baseColorFactor[0]>.5);
  for(const dir of ['gallery','gallery/thumbs']) {
    assert.ok(readFileSync(new URL(`../public/${dir}/brest-sofa.webp`,import.meta.url)).length>1000);
  }
});
