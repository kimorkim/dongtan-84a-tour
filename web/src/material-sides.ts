import * as THREE from 'three';

export interface MaterialSideStats {
  materialsSeen: number;
  materialsRestricted: number;
  meshesChecked: number;
  watertightMeshes: number;
}

interface MaterialUse {
  opaqueOnly: boolean;
  allWatertight: boolean;
}

type PositionAttribute = THREE.BufferAttribute | THREE.InterleavedBufferAttribute;

function vertexKey(position: PositionAttribute, index: number): string {
  return `${position.getX(index).toFixed(6)},${position.getY(index).toFixed(6)},${position.getZ(index).toFixed(6)}`;
}

function isWatertightGeometry(geometry: THREE.BufferGeometry): boolean {
  const position = geometry.getAttribute('position');
  if (!position || position.count < 3) return false;
  const indices = geometry.index;
  const vertexCount = indices ? indices.count : position.count;
  if (vertexCount < 3 || vertexCount % 3 !== 0) return false;

  const vertexIds = new Map<string, number>();
  const canonical: number[] = [];
  for (let i = 0; i < position.count; i++) {
    const key = vertexKey(position, i);
    let id = vertexIds.get(key);
    if (id === undefined) {
      id = vertexIds.size;
      vertexIds.set(key, id);
    }
    canonical.push(id);
  }

  const edgeBase = vertexIds.size + 1;
  const edges = new Map<number, number>();
  for (let i = 0; i < vertexCount; i += 3) {
    const source = [
      indices ? indices.getX(i) : i,
      indices ? indices.getX(i + 1) : i + 1,
      indices ? indices.getX(i + 2) : i + 2,
    ];
    const [a, b, c] = source.map((vertex) => canonical[vertex]);
    if (a === b || b === c || a === c) return false;
    for (const [from, to] of [[a, b], [b, c], [c, a]] as const) {
      const key = Math.min(from, to) * edgeBase + Math.max(from, to);
      edges.set(key, (edges.get(key) ?? 0) + 1);
    }
  }
  if (edges.size === 0) return false;
  for (const count of edges.values()) {
    if (count !== 2) return false;
  }
  return true;
}

/**
 * Restricts double-sided rendering only where every opaque user of a material
 * is a closed surface. Open cards, curtains and transparent materials are kept.
 */
export function restrictDoubleSidedMaterials(root: THREE.Object3D): MaterialSideStats {
  const uses = new Map<THREE.Material, MaterialUse>();
  const watertightByGeometry = new Map<THREE.BufferGeometry, boolean>();
  let meshesChecked = 0;
  let watertightMeshes = 0;

  root.traverse((object) => {
    const mesh = object as THREE.Mesh;
    if (!mesh.isMesh) return;
    meshesChecked++;
    let watertight = watertightByGeometry.get(mesh.geometry);
    if (watertight === undefined) {
      watertight = isWatertightGeometry(mesh.geometry);
      watertightByGeometry.set(mesh.geometry, watertight);
    }
    if (watertight) watertightMeshes++;

    const materials = Array.isArray(mesh.material) ? mesh.material : [mesh.material];
    for (const material of materials) {
      if (!material) continue;
      const candidate = material as THREE.Material & { transparent?: boolean; transmission?: number };
      let use = uses.get(material);
      if (!use) {
        use = { opaqueOnly: true, allWatertight: true };
        uses.set(material, use);
      }
      if (candidate.transparent || (candidate.transmission ?? 0) > 0) use.opaqueOnly = false;
      if (!watertight) use.allWatertight = false;
    }
  });

  let materialsRestricted = 0;
  for (const [material, use] of uses) {
    if (!use.opaqueOnly || !use.allWatertight || material.side !== THREE.DoubleSide) continue;
    material.side = THREE.FrontSide;
    materialsRestricted++;
  }

  return {
    materialsSeen: uses.size,
    materialsRestricted,
    meshesChecked,
    watertightMeshes,
  };
}
