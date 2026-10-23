import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {Box3,Matrix4,Quaternion,Vector3} from 'three';

test('living export has full artwall, gathered curtains, cleared centre and Q17 TV stand + TV',()=>{
  const bytes=readFileSync(new URL('../public/house.glb',import.meta.url));
  const g=JSON.parse(bytes.subarray(20,20+bytes.readUInt32LE(12)).toString());
  assert.ok(!g.nodes.some(n=>/^(Q2_Coffee|Q2_Pouf|Q2_Living_Rug|Q2_Rug_Shape|Curtain_Living|Q2_Sheer_Living|MediaUnit_Living|ProK_Media|Q2_Console|Living_TV_OLED)/.test(n.name??'')));
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
  const standParts=['Leg_FL','Leg_FR','Leg_BL','Leg_BR','Carcass','Shelf','Door_Left','Door_Centre','Door_Right'];
  const tvStand=new Box3();
  for(const part of standParts) tvStand.union(bounds(`Q17_TVStand_${part}`));
  const tvParts=['Chassis','Connectors','IR_receiver','Input_panel','Left_foot','Lower_trim','Rear_shell','Right_foot','Screen','VESA_screws','Ventilation'];
  const tv=new Box3();
  for(const part of tvParts) tv.union(bounds(`Q17_TV_${part}`));
  assert.ok(Math.abs(tvStand.min.x-4.330)<.002 && Math.abs(tvStand.max.x-4.780)<.002);
  assert.ok(Math.abs(tvStand.min.y)<.002 && Math.abs(tvStand.max.y-.513)<.002);
  assert.ok(Math.abs((tvStand.max.z-tvStand.min.z)-2.000)<.002);
  assert.ok(Math.abs(tv.min.x-4.420)<.002 && Math.abs(tv.max.x-4.690)<.002);
  assert.ok(Math.abs(tv.min.y-.513)<.002 && Math.abs(tv.max.y-1.278)<.002);
  assert.ok(Math.abs((tv.max.z-tv.min.z)-1.225)<.002);
  assert.ok(Math.abs((tvStand.min.z+tvStand.max.z)/2-(tv.min.z+tv.max.z)/2)<.002);
  assert.ok(bounds('Q17_TVStand_Door_Centre').min.x>4.75);
  assert.ok(bounds('Q17_TV_Screen').min.x>bounds('Q17_TV_Rear_shell').min.x+.015);
  const sb=new Box3();
  for(const part of ['Body','Grille','Buttons','Logo']) sb.union(bounds(`Q19_Soundbar_${part}`));
  assert.ok(Math.abs((sb.max.x-sb.min.x)-.075)<.002 && Math.abs((sb.max.y-sb.min.y)-.059)<.002 && Math.abs((sb.max.z-sb.min.z)-.8588)<.002,'Soundbar dimensions mismatch');
  assert.ok(Math.abs(sb.min.x-4.680)<.002 && Math.abs(sb.min.y-.513)<.002,'Soundbar position mismatch');
  const sw=new Box3();
  for(const part of ['Body','Grille','Logo','Feet']) sw.union(bounds(`Q19_Subwoofer_${part}`));
  assert.ok(Math.abs((sw.max.x-sw.min.x)-.295)<.002 && Math.abs((sw.max.y-sw.min.y)-.343)<.002 && Math.abs((sw.max.z-sw.min.z)-.184)<.002,'Subwoofer dimensions mismatch');
  assert.ok(Math.abs(sw.min.x-8.360)<.002 && Math.abs(sw.max.x-8.655)<.002 && Math.abs(sw.min.y)<.002,'Subwoofer position mismatch');
  const wall=bounds('Living_ArtWall_Tile');
  assert.ok(Math.abs(wall.min.z+4.75)<.001 && Math.abs(wall.max.z+.92)<.001);
  assert.ok(Math.abs(wall.max.y-2.3)<.001);
  const glass=bounds('Win_Living_Glass1'); assert.ok(glass.max.x-glass.min.x>2);
  assert.ok(bounds('Q15_Curtain_Left').max.x<4.81);
  assert.ok(bounds('Q15_Curtain_Right').min.x>8.30);
  assert.ok(bounds('Q2_Rail_Living_Top').min.z>-.72);
  const c=JSON.parse(readFileSync(new URL('../public/colliders.json',import.meta.url)));
  assert.equal(c.living_finish_version,1);
  assert.equal(c.tv_stand_version,17);
  assert.equal(c.soundbar_version,19);
  for(const id of ['living-window','living-artwall']) for(const dir of ['gallery','gallery/thumbs'])
    assert.ok(readFileSync(new URL(`../public/${dir}/${id}.webp`,import.meta.url)).length>1000);
});
