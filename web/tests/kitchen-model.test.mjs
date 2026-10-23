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
  for(const name of ['Kitchen_Top_North','Kitchen_Base_North_EndL','Kitchen_Kick_North','ProK_Dishwasher_Body','ProK_Dishwasher_Door','ProK_SplashNorth_L','Kitchen_Upper_NorthL_Box'])
    assert.ok(bounds(name).min.x>=5.075,`${name} penetrates west kitchen wall`);
  assert.ok(!g.nodes.some(n=>n.name?.startsWith('Q2_Pot')||n.name?.startsWith('ProK_Oven_')||n.name?.startsWith('Q16_Oven')||n.name==='Q3_Drawer_TopDoor'),'Duplicate pot, removed built-in oven, or closed rice-unit door still in GLB');
  assert.ok(bounds('KitchenProp_Pot_Body'),'Missing stove pot');
  for(const name of ['ProK_DoorE_L','ProK_DoorE_R']) {
    const d=bounds(name);
    assert.ok(Math.abs(d.min.x-7.072)<.002 && Math.abs(d.max.x-7.090)<.002 && Math.abs(d.min.y-.10)<.002 && Math.abs(d.max.y-.845)<.002,`Invalid east door ${name}`);
  }
  const ovenShelf=bounds('Q3_OvenNiche_Top');
  assert.ok(Math.abs(ovenShelf.min.y-1.400)<.002 && Math.abs(ovenShelf.max.y-1.420)<.002,'Missing upper oven niche shelf');
  const ovenCase=new Box3();
  for(const p of ['Body','DoorLower','DoorUpper']) ovenCase.union(bounds(`Q18_LightwaveOven_${p}`));
  for(const p of ['Window','Display','Dial']) assert.ok(bounds(`Q18_LightwaveOven_${p}`));
  assert.ok(Math.abs((ovenCase.max.x-ovenCase.min.x)-.480)<.002,'Lightwave oven depth != 480mm');
  assert.ok(Math.abs((ovenCase.max.y-ovenCase.min.y)-.394)<.002,'Lightwave oven height != 394mm');
  assert.ok(Math.abs((ovenCase.max.z-ovenCase.min.z)-.527)<.002,'Lightwave oven width != 527mm');
  assert.ok(Math.abs(ovenCase.min.y-.960)<.002,'Lightwave oven not resting on z=0.960 shelf');
  assert.ok(bounds('Q18_LightwaveOven_Dial').max.x>ovenCase.max.x+.005,'Rotary dial must protrude east');
  const td1=bounds('Q3_TopDoor1'),td2=bounds('Q3_TopDoor2'),td3=bounds('Q3_TopDoor3'),td0=bounds('Q3_TopDoor0');
  assert.ok(td1.min.z-td2.max.z<=.0035 && td2.min.z-td3.max.z<=.0035 && td3.min.z-td0.max.z<=.0035,'Upper fridge cabinet doors have wide gaps');
  const df1=bounds('Q3_Drawer_Front1'),df2=bounds('Q3_Drawer_Front2'),sideS=bounds('Q3_Drawer_SideS'),sideN=bounds('Q3_Drawer_SideN');
  assert.ok(sideS.min.z-df1.max.z<=.003 && df1.min.z-sideN.max.z<=.003 && df1.min.y-df2.max.y<=.0035,'Lower fridge cabinet drawers have wide gaps');
  assert.ok(Math.abs(bounds('Q3_Drawer_Handle0').min.x-df1.max.x)<=.002,'Drawer handle floating in air');
  assert.ok(!g.nodes.some(n=>/^(Q3_SinkTrim|ProDoorLeaf_UtilitySink$)/.test(n.name??'')),'Old floating utility trims or opaque door still in GLB');
  const hdr=bounds('Q20_UtilityDoor_Header');
  assert.ok(Math.abs(hdr.max.y-2.300)<.002 && Math.abs(hdr.max.z+8.360)<.002 && Math.abs(hdr.min.z+9.015)<.002,'Missing utility door header wall');
  for(const part of ['S','N','Top','Bot','Gasket']) assert.ok(bounds(`Q20_TurningDoor_Frame_${part}`));
  for(const part of ['Frame','Glass','Gasket','Handle']) assert.ok(bounds(`ProDoorLeaf_UtilitySink_${part}`));
  // Q21 LG WashTower WL21EGZU (700W x 1890H x 830D) against the utility room west wall, front +X.
  const wt=new Box3();
  for(const n of g.nodes) if(n.name?.startsWith('Q21_WashTower_')) wt.union(bounds(n.name));
  assert.ok(!wt.isEmpty(),'Missing Q21 WashTower in GLB');
  assert.ok(Math.abs((wt.max.x-wt.min.x)-.830)<.003,'WashTower depth != 830mm');
  assert.ok(Math.abs((wt.max.y-wt.min.y)-1.890)<.003,'WashTower height != 1890mm');
  assert.ok(Math.abs((wt.max.z-wt.min.z)-.700)<.003,'WashTower width != 700mm');
  assert.ok(wt.min.x>=3.20 && wt.max.x<=4.06 && -wt.max.z>=8.360 && -wt.min.z<=9.270,'WashTower not inside south-west utility alcove');
  for(const p of ['Dryer_Glass','Washer_Glass','Control_Panel','Dryer_Front','Washer_Front']) assert.ok(bounds(`Q21_WashTower_${p}`),`Missing WashTower ${p}`);
  const tile=bounds('Q21_UtilityTile_Floor');
  assert.ok(tile.min.x<=3.18 && tile.max.x>=4.97 && -tile.max.z<=8.365 && -tile.min.z>=10.14,'Utility tile floor does not cover the room');
  assert.ok(Math.abs(tile.max.y-.014)<.001 && Math.abs(wt.min.y-tile.max.y)<.001,'WashTower must stand on the utility tile floor');
  assert.ok(bounds('Q21_UtilityTile_Drain'),'Missing utility floor drain');
  assert.ok(Math.abs(bounds('ProK_Dishwasher_Door').max.z-bounds('ProK_DoorN_SinkL').max.z)<.025,'Protruding dishwasher');
  const sink=bounds('Kitchen_Sink_Bottom');
  assert.ok(bounds('ProK_Dishwasher_Body').max.x<=sink.min.x-.02,'Dishwasher collides with sink');
  assert.ok(sink.min.x>=5.455 && sink.max.x<=6.655,'Sink outside kitchen window span');
  assert.ok(Math.abs(sink.max.x-sink.min.x-.84)<.002 && Math.abs(sink.max.z-sink.min.z-.44)<.002);
  assert.ok(bounds('Kitchen_Faucet_Riser').min.z>-10.12,'Embedded faucet');
  assert.ok(g.materials.some(m=>m.name==='Mat_Q16_Stone' && m.pbrMetallicRoughness.baseColorTexture),'Missing web stone texture');
  const c=JSON.parse(readFileSync(new URL('../public/colliders.json',import.meta.url)));
  assert.equal(c.kitchen_finish_version,1);
  for(const [x,y] of [[6.05,9.10],[6.65,9.03],[5.4,9.10]])
    assert.ok(!c.boxes.some(([a,b,d,e])=>(x-Math.max(a,Math.min(d,x)))**2+(y-Math.max(b,Math.min(e,y)))**2<.28**2),'Blocked kitchen approach');
  assert.ok(c.boxes.some(([a,b,d,e])=>a<=3.63&&d>=3.63&&b<=8.85&&e>=8.85),'WashTower footprint in alcove is not a collider');
});
