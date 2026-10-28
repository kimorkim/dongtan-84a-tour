import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import ts from 'typescript';
import { BoxGeometry, Group, Mesh, MeshStandardMaterial, Box3, Vector3 } from 'three';

const source = readFileSync(new URL('../src/static-model.ts', import.meta.url), 'utf8');
const compiled = ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ES2020 } }).outputText
  .replaceAll("'three'", JSON.stringify(import.meta.resolve('three')))
  .replaceAll("'three/addons/utils/BufferGeometryUtils.js'", JSON.stringify(import.meta.resolve('three/addons/utils/BufferGeometryUtils.js')));
const { optimizeStaticModel } = await import(`data:text/javascript;base64,${Buffer.from(compiled).toString('base64')}`);

function meshes(root) {
  const out=[]; root.traverseVisible(o=>{if(o.isMesh)out.push(o);}); return out;
}
function points(root) {
  root.updateMatrixWorld(true);
  return meshes(root).flatMap(m=>{
    const p=m.geometry.attributes.position, uv=m.geometry.attributes.uv, normal=m.geometry.attributes.normal;
    return Array.from({length:p.count},(_,i)=>{
      const v=new Vector3().fromBufferAttribute(p,i).applyMatrix4(m.matrixWorld);
      const n=new Vector3().fromBufferAttribute(normal,i).transformDirection(m.matrixWorld);
      return [...v.toArray(),...n.toArray(),uv.getX(i),uv.getY(i)].map(x=>x.toFixed(4)).join(',');
    });
  }).sort();
}
function box(root) { return new Box3().setFromObject(root,true).getSize(new Vector3()).toArray(); }

test('static batching reduces draws while preserving transformed vertices, normals, UVs and triangles',()=>{
  const root=new Group();root.position.set(5,1,5);root.rotation.y=.4;
  const parent=new Group();parent.position.set(1,0,1);parent.rotation.y=.2;root.add(parent);
  const mat=new MeshStandardMaterial();
  for(let i=0;i<3;i++) {
    const m=new Mesh(new BoxGeometry(.1,.2,.3),mat);m.position.set(.2+i*.2,.5,.2);
    m.rotation.y=i*.1;m.castShadow=true;m.receiveShadow=true;parent.add(m);
  }
  const before=points(root), bounds=box(root);
  const stats=optimizeStaticModel(root,[]);
  assert.equal(stats.meshesBefore,3);assert.equal(stats.meshesAfter,1);
  assert.equal(stats.trianglesBefore,36);assert.equal(stats.trianglesAfter,36);
  assert.deepEqual(points(root),before);
  box(root).forEach((n,i)=>assert.ok(Math.abs(n-bounds[i])<1e-5));
  assert.equal(meshes(root)[0].material,mat);
  assert.equal(meshes(root)[0].castShadow,true);
  assert.equal(meshes(root)[0].receiveShadow,true);
});

test('ceiling batches remain independent, and transparency, spatial culling and shadow flags survive',()=>{
  const root=new Group(), ceiling=new Group();root.add(ceiling);
  const mat=new MeshStandardMaterial(), glass=new MeshStandardMaterial({transparent:true,opacity:.2});
  for(let i=0;i<2;i++) {
    const wall=new Mesh(new BoxGeometry(.1,.1,.1),mat);wall.position.set(.3+i*.2,.3,.3);root.add(wall);
    const top=new Mesh(new BoxGeometry(.1,.1,.1),mat);top.position.set(.3+i*.2,.8,.3);ceiling.add(top);
  }
  const far=new Mesh(new BoxGeometry(.1,.1,.1),mat);far.position.x=20;root.add(far);
  const transparent=new Mesh(new BoxGeometry(),glass);root.add(transparent);
  const caster=new Mesh(new BoxGeometry(.1,.1,.1),mat);caster.castShadow=true;root.add(caster);
  const stats=optimizeStaticModel(root,[ceiling]);
  assert.equal(stats.meshesBefore,7);assert.equal(stats.meshesAfter,5);
  assert.equal(transparent.parent,root);assert.equal(transparent.material,glass);
  assert.equal(far.parent,root);assert.equal(caster.parent,root);
  stats.ceilingMeshes.forEach(o=>{o.visible=false;});
  assert.equal(meshes(root).length,4,'only ceiling geometry should disappear');
  stats.ceilingMeshes.forEach(o=>{o.visible=true;});
  assert.equal(meshes(root).length,5);
});

test('hidden, mirrored and multi-material meshes are kept intact',()=>{
  const root=new Group(),mat=new MeshStandardMaterial();
  const hidden=new Mesh(new BoxGeometry(),mat);hidden.visible=false;root.add(hidden);
  const mirror=new Mesh(new BoxGeometry(),mat);mirror.scale.x=-1;root.add(mirror);
  const multi=new Mesh(new BoxGeometry(),[mat,mat,mat,mat,mat,mat]);root.add(multi);
  optimizeStaticModel(root,[]);
  assert.equal(hidden.visible,false);assert.equal(hidden.parent,root);
  assert.equal(mirror.parent,root);assert.equal(multi.parent,root);
});
