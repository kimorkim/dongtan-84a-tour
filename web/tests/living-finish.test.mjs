import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {Box3,Matrix4,Quaternion,Vector3} from 'three';

test('living export has full artwall, gathered curtains and cleared centre',()=>{
  const bytes=readFileSync(new URL('../public/house.glb',import.meta.url));
  const g=JSON.parse(bytes.subarray(20,20+bytes.readUInt32LE(12)).toString());
  assert.ok(!g.nodes.some(n=>/^(Q2_Coffee|Q2_Pouf|Q2_Living_Rug|Q2_Rug_Shape|Curtain_Living|Q2_Sheer_Living)/.test(n.name??'')));
  function bounds(name) {
    const n=g.nodes.find(n=>n.name===name); assert.ok(n,name);
    const m=n.matrix?new Matrix4().fromArray(n.matrix):new Matrix4().compose(
      new Vector3(...(n.translation??[0,0,0])),new Quaternion(...(n.rotation??[0,0,0,1])),new Vector3(...(n.scale??[1,1,1])));
    const box=new Box3();
    for(const p of g.meshes[n.mesh].primitives) {
      const a=g.accessors[p.attributes.POSITION];
      box.union(new Box3(new Vector3(...a.min),new Vector3(...a.max)).applyMatrix4(m));
    }
    return box;
  }
  const wall=bounds('Living_ArtWall_Tile');
  assert.ok(Math.abs(wall.min.z+4.75)<.001 && Math.abs(wall.max.z+.92)<.001);
  assert.ok(Math.abs(wall.max.y-2.3)<.001);
  const glass=bounds('Win_Living_Glass1'); assert.ok(glass.max.x-glass.min.x>2);
  assert.ok(bounds('Q15_Curtain_Left').max.x<4.81);
  assert.ok(bounds('Q15_Curtain_Right').min.x>8.30);
  assert.ok(bounds('Q2_Rail_Living_Top').min.z>-.72);
  const c=JSON.parse(readFileSync(new URL('../public/colliders.json',import.meta.url)));
  assert.equal(c.living_finish_version,1);
  for(const id of ['living-window','living-artwall']) for(const dir of ['gallery','gallery/thumbs'])
    assert.ok(readFileSync(new URL(`../public/${dir}/${id}.webp`,import.meta.url)).length>1000);
});
