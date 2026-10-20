import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { Matrix4, Quaternion, Vector3 } from 'three';

test('exported oak covers the visible floor with continuous UV and 2K PBR', () => {
  const data = readFileSync(new URL('../public/house.glb', import.meta.url));
  const length = data.readUInt32LE(12);
  const gltf = JSON.parse(data.subarray(20,20+length).toString());
  const binary = 28+length;
  function floats(index, size) {
    const a = gltf.accessors[index], view = gltf.bufferViews[a.bufferView];
    assert.equal(a.componentType,5126);
    return Array.from({length:a.count},(_,i) => Array.from({length:size},(_,k) =>
      data.readFloatLE(binary+(view.byteOffset||0)+(a.byteOffset||0)+i*(view.byteStride||size*4)+k*4)));
  }
  const parents = new Map();
  gltf.nodes.forEach((n,i)=>(n.children||[]).forEach(c=>parents.set(c,i)));
  function world(index) {
    const n = gltf.nodes[index];
    const m = n.matrix ? new Matrix4().fromArray(n.matrix) : new Matrix4().compose(
      new Vector3(...(n.translation||[0,0,0])),new Quaternion(...(n.rotation||[0,0,0,1])),
      new Vector3(...(n.scale||[1,1,1])));
    return parents.has(index) ? world(parents.get(index)).multiply(m) : m;
  }
  const materialIndex = gltf.materials.findIndex(m=>m.name==='Mat_Q9_LightOak');
  assert(materialIndex>=0,'oak material missing from export');
  const index = gltf.nodes.findIndex(n=>n.name==='Exact_Floor');
  const matrix = world(index);
  let topVertices = 0;
  for(const p of gltf.meshes[gltf.nodes[index].mesh].primitives) {
    if(p.material!==materialIndex) continue;
    const positions=floats(p.attributes.POSITION,3),normals=floats(p.attributes.NORMAL,3);
    const uv=floats(p.attributes.TEXCOORD_0,2);
    positions.forEach((v,i)=>{
      if(new Vector3(...normals[i]).transformDirection(matrix).y<.9) return;
      const point=new Vector3(...v).applyMatrix4(matrix);
      assert(Math.abs(point.y)<.0001,'wood assigned to underside instead of visible top');
      assert(Math.abs(uv[i][0]-point.x/3)<.0001,'grain scale/phase differs in web');
      assert(Math.abs(uv[i][1]-(1+point.z/1.04))<.0001,'board width/UV flip differs in web');
      topVertices++;
    });
  }
  assert(topVertices>=4,'visible floor has no oak surface');
  const mat=gltf.materials[materialIndex],pbr=mat.pbrMetallicRoughness;
  for(const texture of [pbr.baseColorTexture,pbr.metallicRoughnessTexture,mat.normalTexture]) {
    assert(texture,'PBR map missing');
    const image=gltf.images[gltf.textures[texture.index].source];
    const view=gltf.bufferViews[image.bufferView];
    const bytes=data.subarray(binary+(view.byteOffset||0),binary+(view.byteOffset||0)+view.byteLength);
    let width,height;
    if(bytes.subarray(1,4).toString()==='PNG') {
      width=bytes.readUInt32BE(16);height=bytes.readUInt32BE(20);
    } else {
      for(let k=2;k<bytes.length-9;) {
        if(bytes[k]!==255){k++;continue;}
        const marker=bytes[k+1];
        if([0xc0,0xc1,0xc2].includes(marker)){height=bytes.readUInt16BE(k+5);width=bytes.readUInt16BE(k+7);break;}
        k+=2+bytes.readUInt16BE(k+2);
      }
    }
    assert.equal(width,2048,'floor map was downsampled');
    assert.equal(height,2048);
  }
  assert(!gltf.nodes.some(n=>['Floor_AlphaRoom','Floor_Bedroom2','Floor_Bedroom3','Floor_MasterBed','Floor_DressRoom'].includes(n.name)),
    'overlapping room patches returned');
});
