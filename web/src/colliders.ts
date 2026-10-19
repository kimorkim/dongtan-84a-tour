// Collision boxes baked from the Blender model (see scripts/bake_collision.py).
// Blender coords (x=east, y=north) are converted to three.js (x, z=-y) here.

export interface ColliderBox {
  minX: number;
  minZ: number;
  maxX: number;
  maxZ: number;
}

interface CollidersJson {
  cell: number;
  boxes: [number, number, number, number][];
}

export async function loadColliders(url = 'colliders.json'): Promise<ColliderBox[]> {
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`colliders load failed: ${res.status} ${url}`);
  }
  const data = (await res.json()) as CollidersJson;
  return data.boxes.map(([x1, y1, x2, y2]) => ({
    minX: Math.min(x1, x2),
    minZ: Math.min(-y1, -y2),
    maxX: Math.max(x1, x2),
    maxZ: Math.max(-y1, -y2),
  }));
}

/** Push a circle (x, z, r) out of every overlapping box. Two passes settle corners. */
export function collideCircle(
  boxes: ColliderBox[],
  x: number,
  z: number,
  r: number,
): { x: number; z: number } {
  for (let pass = 0; pass < 2; pass++) {
    for (const b of boxes) {
      if (x < b.minX - r || x > b.maxX + r || z < b.minZ - r || z > b.maxZ + r) {
        continue;
      }
      const cx = Math.max(b.minX, Math.min(x, b.maxX));
      const cz = Math.max(b.minZ, Math.min(z, b.maxZ));
      const dx = x - cx;
      const dz = z - cz;
      const d2 = dx * dx + dz * dz;
      if (d2 >= r * r) {
        continue;
      }
      if (d2 < 1e-9) {
        // Center inside the box: exit along the least-penetration axis.
        const pl = x - b.minX;
        const pr = b.maxX - x;
        const pn = z - b.minZ;
        const pf = b.maxZ - z;
        const m = Math.min(pl, pr, pn, pf);
        if (m === pl) {
          x = b.minX - r;
        } else if (m === pr) {
          x = b.maxX + r;
        } else if (m === pn) {
          z = b.minZ - r;
        } else {
          z = b.maxZ + r;
        }
      } else {
        const d = Math.sqrt(d2);
        x = cx + (dx / d) * r;
        z = cz + (dz / d) * r;
      }
    }
  }
  return { x, z };
}
