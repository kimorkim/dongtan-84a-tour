import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { Matrix4, Quaternion, Ray, Vector3 } from 'three';

test('exported tour has calibrated wall faces and a clear foyer spawn', () => {
  const bytes=readFileSync(new URL('../public/house.glb',import.meta.url));
  const jsonLength=bytes.readUInt32LE(12);
  const g=JSON.parse(bytes.subarray(20,20+jsonLength).toString());
  const bin=bytes.subarray(28+jsonLength);
  function values(id) {
    const a=g.accessors[id],v=g.bufferViews[a.bufferView];
    const offset=(v.byteOffset??0)+(a.byteOffset??0);
    const width={5121:1,5123:2,5125:4,5126:4}[a.componentType];
    const count={SCALAR:1,VEC3:3}[a.type];
    const read={5121:'readUInt8',5123:'readUInt16LE',5125:'readUInt32LE',5126:'readFloatLE'}[a.componentType];
    assert.ok(width && count && read);
    return Array.from({length:a.count},(_,i)=>Array.from({length:count},(_,j)=>
      bin[read](offset+i*(v.byteStride??count*width)+j*width)));
  }
  function face(name,x,y,dx) {
    const n=g.nodes.find(n=>n.name===name); assert.ok(n, name);
    const m=n.matrix ? new Matrix4().fromArray(n.matrix) : new Matrix4().compose(
      new Vector3(...(n.translation??[0,0,0])),new Quaternion(...(n.rotation??[0,0,0,1])),
      new Vector3(...(n.scale??[1,1,1])));
    const ray=new Ray(new Vector3(x,1.5,-y),new Vector3(dx,0,0));
    let distance=Infinity,hit;
    for(const p of g.meshes[n.mesh].primitives) {
      const positions=values(p.attributes.POSITION).map(v=>new Vector3(...v).applyMatrix4(m));
      const indices=p.indices===undefined ? positions.map((_,i)=>[i]) : values(p.indices);
      for(let i=0;i<indices.length;i+=3) {
        const point=ray.intersectTriangle(...indices.slice(i,i+3).map(([j])=>positions[j]),false,new Vector3());
        if(point && point.distanceTo(ray.origin)<distance) { distance=point.distanceTo(ray.origin); hit=point.x; }
      }
    }
    assert.ok(Number.isFinite(hit),`${name} missing physical face`); return hit;
  }
  for(const y of [1.5,2.5,3.8]) {
    const sw=face('ExactWall_3',10.5,y,-1),se=face('ExactWall_2',10.5,y,1);
    const yw=face('ExactWall_2',13.4,y,-1),ye=face('ExactWall_5',13.4,y,1);
    const lw=face('ExactWall_4',6.5,y,-1),le=face('ExactWall_3',6.5,y,1);
    for(const [actual,expected] of [[se-sw,2.7],[ye-yw,3],[yw-se,.13],[le-lw,4.5],[sw-le,.27]]) {
      assert.ok(Math.abs(actual-expected)<.001,`wall dimension ${actual} != ${expected}`);
    }
  }
  const c=JSON.parse(readFileSync(new URL('../public/colliders.json',import.meta.url)));
  assert.equal(c.dimensions_version,1);
  const main=readFileSync(new URL('../src/main.ts',import.meta.url),'utf8');
  const [,sx,sz]=main.match(/const SPAWN = \{ x: ([\d.]+), z: (-?[\d.]+) \}/);
  const x=Number(sx),y=-Number(sz);
  assert.ok(!c.boxes.some(([a,b,d,e])=>(x-Math.max(a,Math.min(d,x)))**2+
    (y-Math.max(b,Math.min(e,y)))**2<.28**2),'Spawn overlaps calibrated entrance');
});
