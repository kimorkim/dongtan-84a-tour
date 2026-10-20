import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { GTAOPass } from 'three/addons/postprocessing/GTAOPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import './style.css';
import { loadColliders } from './colliders';
import { Player } from './player';
import { TouchControls } from './touch';
import { loadWorld } from './world';

type Mode = 'walk' | 'overview';

// Just inside the front door, looking straight through the middle door into the corridor.
const SPAWN = { x: 12.33, z: -7.40 };
const SPAWN_TARGET = { x: 12.33, z: -5.0 };
const SPAWN_YAW = Math.atan2(-(SPAWN_TARGET.x - SPAWN.x), -(SPAWN_TARGET.z - SPAWN.z));
const OVER_TARGET = new THREE.Vector3(7.15, 0, -4.95);

function el<T extends HTMLElement>(id: string): T {
  const node = document.getElementById(id);
  if (!node) {
    throw new Error(`missing #${id}`);
  }
  return node as T;
}

async function boot(): Promise<void> {
  const isTouch = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
  if (isTouch) {
    document.body.classList.add('is-touch');
  }

  const canvas = el<HTMLCanvasElement>('scene');
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, isTouch ? 1.5 : 2));
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.05;

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x101418);

  const walkCam = new THREE.PerspectiveCamera(
    68,
    window.innerWidth / window.innerHeight,
    0.05,
    120,
  );
  const overCam = new THREE.PerspectiveCamera(
    50,
    window.innerWidth / window.innerHeight,
    0.1,
    200,
  );
  overCam.position.set(OVER_TARGET.x, 14, OVER_TARGET.z + 6.5);

  const fill = el('loader-fill');
  const loaderText = el('loader-text');
  const [world, boxes] = await Promise.all([
    loadWorld(scene, renderer, (r) => {
      fill.style.width = `${Math.round(r * 100)}%`;
    }),
    loadColliders('colliders.json'),
  ]);
  loaderText.textContent = `충돌 박스 ${boxes.length}개 로드됨`;
  el('loader').style.display = 'none';

  // Postprocessing setup (GTAO Ambient Occlusion)
  let composer: EffectComposer | null = null;
  let renderPass: RenderPass | null = null;
  let gtaoPass: GTAOPass | null = null;
  if (!isTouch) {
    try {
      composer = new EffectComposer(renderer);
      renderPass = new RenderPass(scene, walkCam);
      composer.addPass(renderPass);

      gtaoPass = new GTAOPass(scene, walkCam, window.innerWidth, window.innerHeight);
      gtaoPass.blendIntensity = 0.85;
      gtaoPass.pdRings = 2;
      gtaoPass.pdSamples = 8;
      gtaoPass.pdRadiusExponent = 2.0;
      composer.addPass(gtaoPass);

      const outputPass = new OutputPass();
      composer.addPass(outputPass);
    } catch (err) {
      console.warn('Postprocessing GTAO failed to initialize, falling back to standard renderer:', err);
      composer = null;
      renderPass = null;
      gtaoPass = null;
    }
  }

  const player = new Player(walkCam);
  player.setColliders(boxes);
  player.spawn(SPAWN.x, SPAWN.z, SPAWN_YAW);
  const touchControls = new TouchControls(canvas, player);

  const orbit = new OrbitControls(overCam, renderer.domElement);
  orbit.target.copy(OVER_TARGET);
  orbit.enableDamping = true;
  orbit.dampingFactor = 0.08;
  orbit.minDistance = 4;
  orbit.maxDistance = 30;
  orbit.maxPolarAngle = 1.45;
  orbit.enabled = false;

  let mode: Mode = 'walk';

  const btnWalk = el<HTMLButtonElement>('btn-walk');
  const btnOver = el<HTMLButtonElement>('btn-over');
  const btnReset = el<HTMLButtonElement>('btn-reset');
  const modeLabel = el('mode-label');
  const crosshair = el('crosshair');
  const lockHint = el('lock-hint');
  const posEl = el('pos');
  const speedInput = el<HTMLInputElement>('speed');
  const speedVal = el('speed-val');
  const hudHelp = document.querySelector('.hud-help');
  if (isTouch && hudHelp) {
    hudHelp.textContent = '왼손 조이스틱 이동 · 오른손 드래그 시선 · V 전체 보기';
  }

  player.speed = Number(speedInput.value);

  function setMode(next: Mode): void {
    mode = next;
    const walk = mode === 'walk';
    touchControls.setEnabled(walk);
    btnWalk.classList.toggle('active', walk);
    btnOver.classList.toggle('active', !walk);
    modeLabel.textContent = walk ? '걷기' : '전체 보기';
    orbit.enabled = !walk;
    world.setCeilingVisible(walk);
    const activeCam = walk ? walkCam : overCam;
    if (renderPass) renderPass.camera = activeCam;
    if (gtaoPass) gtaoPass.camera = activeCam;
    crosshair.hidden = !walk || document.pointerLockElement !== canvas;
    if (!walk && document.pointerLockElement === canvas) {
      document.exitPointerLock();
    }
    updateLockHint();
  }

  function updateLockHint(): void {
    const locked = document.pointerLockElement === canvas;
    lockHint.hidden = mode !== 'walk' || locked;
    crosshair.hidden = mode !== 'walk' || !locked;
  }

  btnWalk.addEventListener('click', () => setMode('walk'));
  btnOver.addEventListener('click', () => setMode('overview'));
  btnReset.addEventListener('click', () => {
    player.spawn(SPAWN.x, SPAWN.z, SPAWN_YAW);
    setMode('walk');
  });
  speedInput.addEventListener('input', () => {
    player.speed = Number(speedInput.value);
    speedVal.textContent = `${player.speed.toFixed(1)} m/s`;
  });

  const keys = { forward: false, back: false, left: false, right: false, sprint: false };
  window.addEventListener('keydown', (ev) => {
    switch (ev.code) {
      case 'KeyW':
      case 'ArrowUp':
        keys.forward = true;
        break;
      case 'KeyS':
      case 'ArrowDown':
        keys.back = true;
        break;
      case 'KeyA':
      case 'ArrowLeft':
        keys.left = true;
        break;
      case 'KeyD':
      case 'ArrowRight':
        keys.right = true;
        break;
      case 'ShiftLeft':
      case 'ShiftRight':
        keys.sprint = true;
        break;
      case 'KeyV':
        setMode(mode === 'walk' ? 'overview' : 'walk');
        break;
      case 'KeyR':
        player.spawn(SPAWN.x, SPAWN.z, SPAWN_YAW);
        break;
    }
  });
  window.addEventListener('keyup', (ev) => {
    switch (ev.code) {
      case 'KeyW':
      case 'ArrowUp':
        keys.forward = false;
        break;
      case 'KeyS':
      case 'ArrowDown':
        keys.back = false;
        break;
      case 'KeyA':
      case 'ArrowLeft':
        keys.left = false;
        break;
      case 'KeyD':
      case 'ArrowRight':
        keys.right = false;
        break;
      case 'ShiftLeft':
      case 'ShiftRight':
        keys.sprint = false;
        break;
    }
  });

  canvas.addEventListener('click', () => {
    if (!isTouch && mode === 'walk' && document.pointerLockElement !== canvas) {
      canvas.requestPointerLock();
    }
  });
  document.addEventListener('pointerlockchange', updateLockHint);
  document.addEventListener('mousemove', (ev) => {
    if (mode === 'walk' && document.pointerLockElement === canvas) {
      player.addLook(ev.movementX, ev.movementY);
    }
  });
  document.addEventListener('pointerlockerror', () => {
    loaderText.textContent = '마우스 잠금 실패 — 클릭 후 다시 시도하세요';
  });

  window.addEventListener('resize', () => {
    const w = window.innerWidth;
    const h = window.innerHeight;
    renderer.setSize(w, h);
    if (composer) {
      composer.setSize(w, h);
    }
    walkCam.aspect = w / h;
    walkCam.updateProjectionMatrix();
    overCam.aspect = w / h;
    overCam.updateProjectionMatrix();
  });

  const clock = new THREE.Clock();
  renderer.setAnimationLoop(() => {
    const dt = Math.min(clock.getDelta(), 0.05);
    if (mode === 'walk') {
      const analog = touchControls.getAnalogMove();
      player.update(dt, { ...keys, analogMove: analog });
      // Show Blender coords (x=east, y=north) for cross-reference with the model.
      posEl.textContent = `x ${player.pos.x.toFixed(2)} · y ${(-player.pos.z).toFixed(2)}`;
    } else {
      orbit.update();
    }

    if (composer) {
      composer.render();
    } else {
      renderer.render(scene, mode === 'walk' ? walkCam : overCam);
    }
  });

  setMode('walk');
}

boot().catch((err: unknown) => {
  el('loader-text').textContent = `시작 실패: ${err instanceof Error ? err.message : String(err)}`;
});
