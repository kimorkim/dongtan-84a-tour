import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

// Blender (x, y, z) -> three.js (x, z, -y). glTF export already applied this
// to the model; use the same mapping for hand-placed lights.
const b2t = (x: number, y: number, z: number): [number, number, number] => [x, z, -y];

const CEILING_NAMES = ['Ceiling_Slab'];
const CEILING_PREFIXES = ['Ceiling_', 'Cove_', 'ProK_CeilStrip', 'Q10_Ceiling', 'Q11_Ceiling',
  'Q24_Ceiling', 'Q24_AccessPanel', 'Q24_Vent', 'Q24_Downlight'];

export interface World {
  model: THREE.Group;
  setCeilingVisible: (visible: boolean) => void;
}

export async function loadWorld(
  scene: THREE.Scene,
  renderer: THREE.WebGLRenderer,
  onProgress: (ratio: number) => void,
): Promise<World> {
  // Enable high-quality soft shadows
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;

  // Image-based ambience for PBR reflections (metals, glass, porcelain)
  const pmrem = new THREE.PMREMGenerator(renderer);
  scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
  pmrem.dispose();

  // Subtle natural ambient fill: cool sky daylight + warm interior floor bounce
  scene.add(new THREE.HemisphereLight(0xeef4fa, 0x443628, 0.22));
  scene.add(new THREE.AmbientLight(0xffeedd, 0.08));

  // Natural sunlight entering through the South balcony windows
  const sun = new THREE.DirectionalLight(0xfff1dc, 1.6);
  sun.position.set(...b2t(7.0, -4.5, 4.5));
  const sunTarget = new THREE.Object3D();
  sunTarget.position.set(...b2t(7.0, 3.2, 0.2));
  scene.add(sunTarget);
  sun.target = sunTarget;

  sun.castShadow = true;
  sun.shadow.mapSize.width = 2048;
  sun.shadow.mapSize.height = 2048;
  sun.shadow.camera.near = 0.5;
  sun.shadow.camera.far = 28;
  sun.shadow.camera.left = -9;
  sun.shadow.camera.right = 9;
  sun.shadow.camera.top = 9;
  sun.shadow.camera.bottom = -9;
  sun.shadow.bias = -0.0004;
  sun.shadow.normalBias = 0.02;
  scene.add(sun);

  // Modelhouse ceiling downlights (3000K warm white, inverse-square quadratic decay)
  const downlights: Array<{ pos: [number, number, number]; color: number; intensity: number; dist: number }> = [
    // Living Room
    { pos: [6.4, 3.2, 2.25], color: 0xffebd4, intensity: 14, dist: 7 },
    { pos: [4.8, 3.2, 2.25], color: 0xffe4c6, intensity: 10, dist: 5 }, // Art wall accent
    { pos: [8.0, 3.2, 2.25], color: 0xffebd4, intensity: 10, dist: 5 }, // Sofa side
    // Kitchen & Dining
    { pos: [6.4, 6.6, 1.82], color: 0xffd99f, intensity: 16, dist: 4.5 }, // Dining pendant
    { pos: [6.4, 8.2, 2.25], color: 0xfff2e0, intensity: 12, dist: 5 }, // Prep island
    // Corridor & Dry Vanity (호텔식 복도 건식 세면대 라인)
    { pos: [12.2, 5.0, 2.25], color: 0xffe8cf, intensity: 8, dist: 4 },
    { pos: [10.2, 5.0, 2.25], color: 0xffe8cf, intensity: 8, dist: 4 },
    { pos: [13.8, 5.0, 2.25], color: 0xffe8cf, intensity: 8, dist: 4 },
    { pos: [14.65, 5.0, 2.15], color: 0xffebd4, intensity: 12, dist: 3.5 }, // Dry vanity mirror downlight
    // Common Bath (inside wet bath)
    { pos: [14.65, 6.8, 2.15], color: 0xfff0e4, intensity: 8, dist: 4 },
    // Foyer
    { pos: [12.32, 6.65, 2.20], color: 0xffe4bc, intensity: 12, dist: 4 },
    { pos: [11.15, 6.70, 2.20], color: 0xffead6, intensity: 6, dist: 2.5 }, // Entry pantry
    // Master Bedroom & Bath
    { pos: [2.4, 3.7, 2.25], color: 0xffebd4, intensity: 12, dist: 6 },
    { pos: [3.45, 6.9, 2.15], color: 0xfff0e4, intensity: 8, dist: 4 },
    // Alpha Room & Bedrooms
    { pos: [9.1, 6.9, 2.25], color: 0xffebd4, intensity: 9, dist: 5 },
    { pos: [10.5, 2.5, 2.25], color: 0xffebd4, intensity: 9, dist: 5 },
    { pos: [13.6, 2.5, 2.25], color: 0xffebd4, intensity: 9, dist: 5 },
    { pos: [1.6, 7.8, 2.25], color: 0xffebd4, intensity: 7, dist: 4 }, // Dress room
  ];

  for (const dl of downlights) {
    const pl = new THREE.PointLight(dl.color, dl.intensity, dl.dist, 2);
    pl.position.set(...b2t(...dl.pos));
    scene.add(pl);
  }

  const loader = new GLTFLoader();
  const gltf = await loader.loadAsync('house.glb', (ev) => {
    if (ev.total > 0) {
      onProgress(ev.loaded / ev.total);
    }
  });
  const model = gltf.scene;
  scene.add(model);

  const ceilingMeshes: THREE.Object3D[] = [];
  model.traverse((o) => {
    const isCeil =
      CEILING_NAMES.includes(o.name) ||
      CEILING_PREFIXES.some((p) => o.name.startsWith(p));
    if (isCeil) {
      ceilingMeshes.push(o);
    }

    if ((o as THREE.Mesh).isMesh) {
      const m = o as THREE.Mesh;
      m.castShadow = true;
      m.receiveShadow = true;

      // Enhance materials for photoreal modelhouse appearance
      const mats = Array.isArray(m.material) ? m.material : [m.material];
      for (const mat of mats) {
        if (!mat) continue;
        const name = mat.name || '';

        // Textures sRGB color space check
        if ((mat as THREE.MeshStandardMaterial).map) {
          (mat as THREE.MeshStandardMaterial).map!.colorSpace = THREE.SRGBColorSpace;
          (mat as THREE.MeshStandardMaterial).map!.needsUpdate = true;
        }

        // Indirect Cove Lighting / LED Strip glow
        if (
          o.name.startsWith('Cove_') ||
          o.name.startsWith('ProK_CeilStrip') ||
          name.includes('LED') ||
          name.includes('Light_Warm') ||
          name.includes('Bulb')
        ) {
          (mat as THREE.MeshStandardMaterial).emissive = new THREE.Color(0xffd29f);
          (mat as THREE.MeshStandardMaterial).emissiveIntensity = 2.5;
        }

        // Glass transparency & reflections
        if (name.includes('Glass') || o.name.includes('Glass') || o.name.includes('Screen') || o.name.includes('Shower_Screen')) {
          const std = mat as THREE.MeshStandardMaterial;
          std.transparent = true;
          const frosted = name.includes('FrostedGlass');
          std.opacity = frosted ? 0.88 : 0.22;
          std.roughness = frosted ? 0.55 : 0.04;
          std.metalness = frosted ? 0.0 : 0.1;
          std.depthWrite = false;
          m.castShadow = false; // Prevent hard opaque shadow from glass
        }

        // Mirrors
        if (name.includes('Mirror') || o.name.includes('Mirror')) {
          const std = mat as THREE.MeshStandardMaterial;
          std.metalness = 0.98;
          std.roughness = 0.02;
        }

        // Cashmere Cabinets (Kitchen, Foyer, Dry Vanity)
        if (name.includes('Cabinet_Cashmere')) {
          const std = mat as THREE.MeshStandardMaterial;
          std.color = new THREE.Color(0xeae4db);
          std.roughness = 0.45;
        }

        // Porcelain Art Wall
        if (name.includes('ArtWall')) {
          const std = mat as THREE.MeshStandardMaterial;
          std.roughness = 0.28;
        }

        // Wood Flooring Satin Finish
        if (name.includes('Wood_LightPlank') || name.includes('Wood_WarmPlank')) {
          const std = mat as THREE.MeshStandardMaterial;
          std.roughness = 0.42;
        }
      }
    }
  });

  return {
    model,
    setCeilingVisible: (visible: boolean) => {
      for (const o of ceilingMeshes) {
        o.visible = visible;
      }
    },
  };
}
