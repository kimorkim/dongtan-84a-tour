import * as THREE from 'three';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';

export interface StaticModelStats {
  meshesBefore: number;
  meshesAfter: number;
  trianglesBefore: number;
  trianglesAfter: number;
  ceilingMeshes: THREE.Object3D[];
}

/** Batch static, opaque leaves in small cells, without simplifying any geometry. */
export function optimizeStaticModel(
  root: THREE.Object3D,
  ceilings: THREE.Object3D[],
): StaticModelStats {
  root.updateMatrixWorld(true);
  const rootInverse = root.matrixWorld.clone().invert();
  const ceilingSet = new Set(ceilings);
  const buckets = new Map<string, { meshes: THREE.Mesh[]; ceiling: boolean }>();
  const count = (): [number, number] => {
    let meshes = 0, triangles = 0;
    root.traverseVisible(o => {
      if (!(o instanceof THREE.Mesh)) return;
      meshes++;
      triangles += (o.geometry.index?.count ?? o.geometry.attributes.position.count) / 3;
    });
    return [meshes, triangles];
  };
  const [meshesBefore, trianglesBefore] = count();
  root.traverseVisible(o => {
    if (!(o instanceof THREE.Mesh) || o instanceof THREE.SkinnedMesh || o instanceof THREE.InstancedMesh ||
        o.children.length || o.morphTargetInfluences || Array.isArray(o.material) ||
        o.material.transparent || o.material.transmission > 0 ||
        o.customDepthMaterial || o.customDistanceMaterial || o.matrixWorld.determinant() <= 0) return;
    const geometry: THREE.BufferGeometry = o.geometry;
    // Preserve partial draws and animated geometry verbatim.
    if (geometry.drawRange.start !== 0 || geometry.drawRange.count !== Infinity ||
        Object.keys(geometry.morphAttributes).length > 0) return;
    let ceiling = false;
    for (let p: THREE.Object3D | null = o; p; p = p.parent) {
      if (ceilingSet.has(p)) ceiling = true;
      if (p === root) break;
    }
    geometry.computeBoundingBox();
    const center = geometry.boundingBox!.clone().applyMatrix4(o.matrixWorld).getCenter(new THREE.Vector3());
    const cell = [center.x, center.y, center.z].map(v => Math.floor(v / 2.5)).join(',');
    const attributes = Object.entries(geometry.attributes).sort(([a], [b]) => a.localeCompare(b))
      .map(([name, a]) => `${name}:${a.itemSize}:${a.normalized}:${a.array.constructor.name}`).join('|');
    const key = [cell, o.material.uuid, o.castShadow, o.receiveShadow, o.layers.mask,
      o.renderOrder, ceiling, !!geometry.index, attributes].join('/');
    let bucket = buckets.get(key);
    if (!bucket) { bucket = { meshes: [], ceiling }; buckets.set(key, bucket); }
    bucket.meshes.push(o);
  });
  const ceilingMeshes = [...ceilings];
  for (const { meshes, ceiling } of buckets.values()) {
    if (meshes.length < 2) continue;
    const copies = meshes.map(m => m.geometry.clone().applyMatrix4(
      new THREE.Matrix4().multiplyMatrices(rootInverse, m.matrixWorld),
    ));
    const geometry = mergeGeometries(copies);
    copies.forEach(g => g.dispose());
    if (!geometry) continue;
    geometry.computeBoundingBox();
    geometry.computeBoundingSphere();
    const first = meshes[0];
    const batch = new THREE.Mesh(geometry, first.material);
    batch.name = `StaticBatch_${root.children.length}`;
    batch.castShadow = first.castShadow;
    batch.receiveShadow = first.receiveShadow;
    batch.layers.mask = first.layers.mask;
    batch.renderOrder = first.renderOrder;
    root.add(batch);
    if (ceiling) ceilingMeshes.push(batch);
    meshes.forEach(m => m.removeFromParent());
  }
  const [meshesAfter, trianglesAfter] = count();
  root.updateMatrixWorld(true);
  root.traverse(o => {
    o.matrixAutoUpdate = false;
    o.matrixWorldAutoUpdate = false;
  });
  return { meshesBefore, meshesAfter, trianglesBefore, trianglesAfter, ceilingMeshes };
}
