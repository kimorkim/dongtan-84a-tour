import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { Box3, Matrix4, Quaternion, Vector3 } from 'three';

test('actual tour preserves desk sizes, workstation equipment and both mesh chairs', () => {
  const bytes=readFileSync(new URL('../public/house.glb',import.meta.url));
  const gltf=JSON.parse(bytes.subarray(20,20+bytes.readUInt32LE(12)).toString());
  const nodes=gltf.nodes;
  for(const name of ['Dell27_L_Screen','Dell27_R_Screen','Gaming32_Screen','MacBook_Closed',
    'MacBook_Stand','A2_L_Cabinet','A2_R_Cabinet','Arm27_L_Clamp','Arm27_R_Clamp',
    'GamingRiser_Top','Desktop_Case','Keyboard1800_Base','Mouse1800_Body',
    'Keyboard1400_Base','Mouse1400_Body']) {
    const node=nodes.find(n=>n.name==='Q11_Equipment_'+name);
    assert.ok(node && node.mesh!==undefined,`${name} missing from actual tour`);
  }
  assert.ok(!nodes.some(n=>n.name?.startsWith('Bed2_')),'Old bed remains');
  for (const [size,w,d] of [['1800',1.8,.8],['1400',1.4,.7]]) {
    const n=nodes.find(n=>n.name==='Q11_Desk'+size+'_Top');
    assert.ok(n,'Desk missing');
    const matrix=n.matrix ? new Matrix4().fromArray(n.matrix) : new Matrix4().compose(
      new Vector3(...n.translation),new Quaternion(...n.rotation),new Vector3(...(n.scale??[1,1,1])));
    const box=new Box3();
    for(const p of gltf.meshes[n.mesh].primitives) {
      const a=gltf.accessors[p.attributes.POSITION];
      box.union(new Box3(new Vector3(...a.min),new Vector3(...a.max)).applyMatrix4(matrix));
    }
    assert.ok(Math.abs(box.max.x-box.min.x-d)<.002 && Math.abs(box.max.z-box.min.z-w)<.002);
    assert.ok(box.max.x<11.775 && box.min.z> -4.33 && box.max.z<-.92,'Desk outside room');
  }
  for(const color of ['Black','Grey']) {
    for(const part of ['BackFrame','BackMesh','SeatFrame','SeatMesh','Spoke0','Caster00']) {
      const n=nodes.find(n=>n.name===`Q11_Aeron${color}_${part}`);
      assert.ok(n && n.mesh!==undefined,`${color} ${part} lost during export`);
    }
  }
  for(const id of ['study-room','study-desks']) {
    for(const dir of ['gallery','gallery/thumbs']) {
      assert.ok(readFileSync(new URL(`../public/${dir}/${id}.webp`,import.meta.url)).length>1000);
    }
  }
});
