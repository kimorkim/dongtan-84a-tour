import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {Box3,Matrix4,Quaternion,Vector3} from 'three';

test('exported kitchen has connected tops, flush dishwasher and undistorted sink',()=>{
  const bytes=readFileSync(new URL('../public/house.glb',import.meta.url));
  const g=JSON.parse(bytes.subarray(20,20+bytes.readUInt32LE(12)).toString());
  function bounds(name) {
    const n=g.nodes.find(n=>n.name===name);assert.ok(n,name);
    const m=n.matrix?new Matrix4().fromArray(n.matrix):new Matrix4().compose(
      new Vector3(...(n.translation??[0,0,0])),new Quaternion(...(n.rotation??[0,0,0,1])),new Vector3(...(n.scale??[1,1,1])));
    const b=new Box3();
    for(const p of g.meshes[n.mesh].primitives) {
      const a=g.accessors[p.attributes.POSITION];
      b.union(new Box3(new Vector3(...a.min),new Vector3(...a.max)).applyMatrix4(m));
    }
    return b;
  }
  const north=bounds('Kitchen_Top_North'),east=bounds('Kitchen_Top_East'),pen=bounds('Kitchen_Top_Peninsula');
  assert.ok(Math.abs(north.max.z-east.min.z)<.002,'North/east gap');
  assert.ok(Math.abs(east.max.z-pen.min.z)<.002,'East/peninsula gap');
  assert.ok(Math.abs(bounds('ProK_Dishwasher_Door').max.z-bounds('ProK_DoorN_SinkL').max.z)<.025,'Protruding dishwasher');
  const sink=bounds('Kitchen_Sink_Bottom');
  assert.ok(Math.abs(sink.max.x-sink.min.x-.84)<.002 && Math.abs(sink.max.z-sink.min.z-.44)<.002);
  assert.ok(bounds('Kitchen_Faucet_Riser').min.z>-10.12,'Embedded faucet');
  assert.ok(g.materials.some(m=>m.name==='Mat_Q16_Stone' && m.pbrMetallicRoughness.baseColorTexture),'Missing web stone texture');
  const c=JSON.parse(readFileSync(new URL('../public/colliders.json',import.meta.url)));
  assert.equal(c.kitchen_finish_version,1);
  for(const [x,y] of [[6.05,9.10],[6.65,9.03],[5.4,9.10]])
    assert.ok(!c.boxes.some(([a,b,d,e])=>(x-Math.max(a,Math.min(d,x)))**2+(y-Math.max(b,Math.min(e,y)))**2<.28**2),'Blocked kitchen approach');
});
