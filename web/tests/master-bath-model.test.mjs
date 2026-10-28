import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { Box3, Matrix4, Quaternion, Vector3 } from 'three';

test('master bath follows VR011 fixtures and its door opens into the bathroom', () => {
  const bytes=readFileSync(new URL('../public/house.glb',import.meta.url));
  const g=JSON.parse(bytes.subarray(20,20+bytes.readUInt32LE(12)).toString());
  const world=new Map();
  function visit(i,parent) {
    const n=g.nodes[i];
    const local=n.matrix ? new Matrix4().fromArray(n.matrix) : new Matrix4().compose(
      new Vector3(...(n.translation??[0,0,0])),new Quaternion(...(n.rotation??[0,0,0,1])),new Vector3(...(n.scale??[1,1,1])));
    const matrix=parent.clone().multiply(local);world.set(i,matrix);
    for(const child of n.children??[])visit(child,matrix);
  }
  for(const i of g.scenes[g.scene??0].nodes)visit(i,new Matrix4());
  const boxes=new Map();
  for(const [i,m] of world) {
    const n=g.nodes[i];if(n.mesh===undefined)continue;
    const b=new Box3();
    for(const p of g.meshes[n.mesh].primitives) {
      const a=g.accessors[p.attributes.POSITION];
      b.union(new Box3(new Vector3(...a.min),new Vector3(...a.max)).applyMatrix4(m));
    }
    boxes.set(n.name,b);
  }
  const door=boxes.get('ProDoorLeaf_MasterBath');
  assert.ok(door.min.x>2.59 && door.max.x<3.38,'Bathroom door protrudes into powder room');
  assert.ok(door.min.z> -6.11 && door.max.z< -5.985,'Door must open along bathroom south wall');
  for(const name of ['Q24_Tub','Q24_Basin','Q24_Toilet_Bowl','Q24_MirrorDoor0','Q24_MirrorDoor1','Q24_MirrorDoor2','Q24_Shower_Rail','Q24_FloorDrain'])assert.ok(boxes.has(name),'Missing '+name);
  assert.ok(![...boxes.keys()].some(n=>/^(Master_Toilet_|Master_Bathtub_|BathProp_Master)/.test(n)));
  for(const [n,b]of boxes) {
    if(/^(Q24_Tub$|Q24_Basin$|Q24_Toilet_)/.test(n))
      assert.ok(b.min.x>=2.602 && b.max.x<=4.085 && b.min.z>=-8.160 && b.max.z<=-5.985,'Fixture outside bath: '+n);
  }
  const tile=boxes.get('Q24_Tile_E_0_0').getSize(new Vector3());
  assert.ok(Math.abs(tile.y-.298)<.002 && Math.abs(tile.z-.598)<.002,'Wall tile must be horizontal600x300mm');
  const data=JSON.parse(readFileSync(new URL('../public/colliders.json',import.meta.url)));
  assert.equal(data.master_bath_version,24);
  assert.ok(boxes.has('Q23_Powder_Top'));
});
