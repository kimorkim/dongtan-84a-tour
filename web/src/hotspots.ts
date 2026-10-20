import * as THREE from 'three';
import { GALLERY_ITEMS, type GalleryItem } from './gallery-data';

export interface HotspotEntry {
  id: string;
  item: GalleryItem;
  sprite: THREE.Sprite;
  basePos: THREE.Vector3;
  baseScale: { x: number; y: number };
}

function drawRoundRect(
  ctx: CanvasRenderingContext2D,
  x: number,
  y: number,
  w: number,
  h: number,
  r: number,
): void {
  if (typeof ctx.roundRect === 'function') {
    ctx.roundRect(x, y, w, h, r);
  } else {
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.arcTo(x + w, y, x + w, y + h, r);
    ctx.arcTo(x + w, y + h, x, y + h, r);
    ctx.arcTo(x, y + h, x, y, r);
    ctx.arcTo(x, y, x + w, y, r);
    ctx.closePath();
  }
}

/**
 * Creates a circular camera badge texture with title pill on HTML5 Canvas.
 */
function createHotspotTexture(title: string): THREE.CanvasTexture {
  const width = 512;
  const height = 256;
  const canvas = document.createElement('canvas');
  canvas.width = width;
  canvas.height = height;
  const ctx = canvas.getContext('2d');
  if (!ctx) {
    throw new Error('Canvas 2D context not available');
  }

  ctx.clearRect(0, 0, width, height);

  const cx = width / 2;
  const cy = 85;

  // 1. Outer golden luminous glow
  const glow = ctx.createRadialGradient(cx, cy, 18, cx, cy, 65);
  glow.addColorStop(0, 'rgba(251, 191, 36, 0.45)');
  glow.addColorStop(0.5, 'rgba(245, 158, 11, 0.20)');
  glow.addColorStop(1, 'rgba(245, 158, 11, 0)');
  ctx.fillStyle = glow;
  ctx.beginPath();
  ctx.arc(cx, cy, 65, 0, Math.PI * 2);
  ctx.fill();

  // 2. Dark circular disc
  ctx.beginPath();
  ctx.arc(cx, cy, 38, 0, Math.PI * 2);
  const discGrad = ctx.createRadialGradient(cx, cy - 10, 5, cx, cy, 38);
  discGrad.addColorStop(0, 'rgba(38, 30, 20, 0.96)');
  discGrad.addColorStop(1, 'rgba(16, 14, 12, 0.96)');
  ctx.fillStyle = discGrad;
  ctx.fill();

  // 3. Golden outer ring border
  ctx.lineWidth = 3.5;
  ctx.strokeStyle = '#fbbf24';
  ctx.shadowColor = 'rgba(245, 158, 11, 0.8)';
  ctx.shadowBlur = 10;
  ctx.stroke();
  ctx.shadowBlur = 0; // reset shadow

  // 4. Camera icon inside disc
  const bx = cx - 17;
  const by = cy - 8;

  // Top bump / viewfinder
  drawRoundRect(ctx, cx - 7, by - 5, 14, 6, 2);
  ctx.fillStyle = '#f59e0b';
  ctx.fill();

  // Camera main body
  drawRoundRect(ctx, bx, by, 34, 22, 4);
  ctx.fillStyle = '#1e2430';
  ctx.fill();
  ctx.lineWidth = 2;
  ctx.strokeStyle = '#fbbf24';
  ctx.stroke();

  // Lens ring & center
  ctx.beginPath();
  ctx.arc(cx, by + 11, 7.5, 0, Math.PI * 2);
  ctx.fillStyle = '#fbbf24';
  ctx.fill();

  ctx.beginPath();
  ctx.arc(cx, by + 11, 4.5, 0, Math.PI * 2);
  ctx.fillStyle = '#0f172a';
  ctx.fill();

  // Flash / sensor dot
  ctx.beginPath();
  ctx.arc(bx + 27, by + 5, 2, 0, Math.PI * 2);
  ctx.fillStyle = '#fef08a';
  ctx.fill();

  // 5. Vertical connector stem from badge bottom to pill top
  ctx.beginPath();
  ctx.moveTo(cx, cy + 38);
  ctx.lineTo(cx, 168);
  ctx.lineWidth = 2;
  ctx.strokeStyle = 'rgba(251, 191, 36, 0.65)';
  ctx.stroke();

  // 6. Title Pill
  ctx.font = 'bold 22px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Pretendard", sans-serif';
  const textWidth = ctx.measureText(title).width;
  const pillPadding = 18;
  const pillWidth = Math.min(480, textWidth + pillPadding * 2);
  const pillHeight = 38;
  const pillX = cx - pillWidth / 2;
  const pillY = 168;

  drawRoundRect(ctx, pillX, pillY, pillWidth, pillHeight, 19);
  ctx.fillStyle = 'rgba(15, 20, 28, 0.90)';
  ctx.fill();
  ctx.lineWidth = 1.5;
  ctx.strokeStyle = 'rgba(251, 191, 36, 0.65)';
  ctx.stroke();

  ctx.fillStyle = '#ffffff';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText(title, cx, pillY + pillHeight / 2 + 1);

  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  texture.needsUpdate = true;
  return texture;
}

export class HotspotManager {
  private readonly hotspots: HotspotEntry[] = [];
  private readonly sprites: THREE.Sprite[] = [];
  private readonly group = new THREE.Group();
  private readonly raycaster = new THREE.Raycaster();
  private time = 0;
  private currentCamera: THREE.Camera;
  private pointerDownPos = { x: 0, y: 0 };
  private pointerDownTime = 0;
  private visible = true;

  constructor(
    private readonly scene: THREE.Scene,
    walkCam: THREE.Camera,
    _overCam: THREE.Camera,
    private readonly onClick: (id: string) => void,
    private readonly domElement: HTMLElement = document.getElementById('scene') ?? document.body,
  ) {
    this.currentCamera = walkCam;
    this.group.name = 'HotspotsGroup';
    this.scene.add(this.group);

    this.createHotspots();
    this.bindEvents();
  }

  private createHotspots(): void {
    const validItems = GALLERY_ITEMS.filter(
      (item): item is GalleryItem & { worldPos: [number, number, number] } => Boolean(item.worldPos),
    );

    for (const item of validItems) {
      const texture = createHotspotTexture(item.title);
      const material = new THREE.SpriteMaterial({
        map: texture,
        transparent: true,
        depthTest: true,
        depthWrite: false,
      });

      const sprite = new THREE.Sprite(material);
      sprite.position.set(item.worldPos[0], item.worldPos[1], item.worldPos[2]);
      // 2:1 aspect ratio: 0.70m x 0.35m base dimension
      const baseScale = { x: 0.7, y: 0.35 };
      sprite.scale.set(baseScale.x, baseScale.y, 1);
      sprite.userData = { id: item.id };
      sprite.renderOrder = 10;

      this.group.add(sprite);
      this.sprites.push(sprite);

      this.hotspots.push({
        id: item.id,
        item,
        sprite,
        basePos: sprite.position.clone(),
        baseScale,
      });
    }
  }

  private bindEvents(): void {
    this.domElement.addEventListener('pointerdown', this.onPointerDown);
    this.domElement.addEventListener('pointerup', this.onPointerUp);
    this.domElement.addEventListener('click', this.onClickEvent);
    this.domElement.addEventListener('pointermove', this.onPointerMove);
  }

  private onPointerDown = (ev: PointerEvent): void => {
    this.pointerDownPos = { x: ev.clientX, y: ev.clientY };
    this.pointerDownTime = performance.now();
  };

  private onPointerMove = (ev: PointerEvent): void => {
    if (!this.visible) return;
    // Only update cursor style when pointer lock is NOT active and device is not touch
    if (document.pointerLockElement !== this.domElement && ev.pointerType !== 'touch') {
      const rect = this.domElement.getBoundingClientRect();
      const ndcX = ((ev.clientX - rect.left) / rect.width) * 2 - 1;
      const ndcY = -((ev.clientY - rect.top) / rect.height) * 2 + 1;
      const hitId = this.raycastAtNDC(ndcX, ndcY);
      this.domElement.style.cursor = hitId ? 'pointer' : '';
    }
  };

  private onPointerUp = (ev: PointerEvent): void => {
    if (!this.visible) return;
    // For touch devices, tap detection on pointerup (since touchstart might prevent default click)
    if (ev.pointerType === 'touch') {
      const dist = Math.hypot(ev.clientX - this.pointerDownPos.x, ev.clientY - this.pointerDownPos.y);
      const duration = performance.now() - this.pointerDownTime;
      if (dist < 12 && duration < 400) {
        const rect = this.domElement.getBoundingClientRect();
        const ndcX = ((ev.clientX - rect.left) / rect.width) * 2 - 1;
        const ndcY = -((ev.clientY - rect.top) / rect.height) * 2 + 1;
        const hitId = this.raycastAtNDC(ndcX, ndcY);
        if (hitId) {
          ev.preventDefault();
          this.onClick(hitId);
        }
      }
    }
  };

  private onClickEvent = (ev: MouseEvent): void => {
    if (!this.visible) return;
    if ((ev as PointerEvent).pointerType === 'touch') return; // Handled in pointerup

    const dist = Math.hypot(ev.clientX - this.pointerDownPos.x, ev.clientY - this.pointerDownPos.y);
    if (dist > 8) {
      // User was dragging camera / orbit controls
      return;
    }

    let ndcX = 0;
    let ndcY = 0;

    if (document.pointerLockElement === this.domElement) {
      // In pointer lock walk mode, raycast from center of screen (crosshair)
      ndcX = 0;
      ndcY = 0;
    } else {
      // Free mouse cursor
      const rect = this.domElement.getBoundingClientRect();
      ndcX = ((ev.clientX - rect.left) / rect.width) * 2 - 1;
      ndcY = -((ev.clientY - rect.top) / rect.height) * 2 + 1;
    }

    const hitId = this.raycastAtNDC(ndcX, ndcY);
    if (hitId) {
      ev.preventDefault();
      ev.stopImmediatePropagation();
      this.onClick(hitId);
    }
  };

  public raycastAtNDC(ndcX: number, ndcY: number): string | null {
    if (!this.visible || this.sprites.length === 0) return null;

    this.raycaster.setFromCamera(new THREE.Vector2(ndcX, ndcY), this.currentCamera);
    const intersects = this.raycaster.intersectObjects(this.sprites, false);
    if (intersects.length === 0) return null;

    const hit = intersects[0];
    const targetId = hit.object.userData.id as string | undefined;
    if (!targetId) return null;

    // Line of sight check: ensure no opaque scene mesh is blocking the hotspot
    const sceneHits = this.raycaster.intersectObjects(this.scene.children, true);
    for (const sceneHit of sceneHits) {
      if (sceneHit.object instanceof THREE.Sprite) continue;
      if (sceneHit.distance < hit.distance - 0.05) {
        const mesh = sceneHit.object as THREE.Mesh;
        if (mesh.isMesh && mesh.visible) {
          const mat = mesh.material;
          const isClearGlass = Array.isArray(mat)
            ? mat.some((m) => (m as THREE.MeshStandardMaterial).opacity < 0.4)
            : (mat as THREE.MeshStandardMaterial).opacity < 0.4;
          if (!isClearGlass) {
            // Blocked by opaque wall/furniture
            return null;
          }
        }
      }
    }

    return targetId;
  }

  public update(dt: number, camera: THREE.Camera): void {
    if (!this.visible) return;

    this.time += dt;
    this.currentCamera = camera;

    for (let i = 0; i < this.hotspots.length; i++) {
      const h = this.hotspots[i];

      // Subtle vertical float
      const floatY = Math.sin(this.time * 2.2 + i * 0.7) * 0.035;
      h.sprite.position.y = h.basePos.y + floatY;

      // Pulse and distance-based scale adjustment
      const dist = camera.position.distanceTo(h.sprite.position);
      const distScale = Math.max(0.75, Math.min(0.5 + dist * 0.08, 1.8));
      const pulse = 1.0 + Math.sin(this.time * 3.0 + i * 0.8) * 0.04;
      const s = distScale * pulse;

      h.sprite.scale.set(h.baseScale.x * s, h.baseScale.y * s, 1);
    }
  }

  public setVisible(visible: boolean): void {
    this.visible = visible;
    this.group.visible = visible;
    if (!visible) {
      this.domElement.style.cursor = '';
    }
  }

  public destroy(): void {
    this.domElement.removeEventListener('pointerdown', this.onPointerDown);
    this.domElement.removeEventListener('pointerup', this.onPointerUp);
    this.domElement.removeEventListener('click', this.onClickEvent);
    this.domElement.removeEventListener('pointermove', this.onPointerMove);

    for (const h of this.hotspots) {
      h.sprite.material.map?.dispose();
      h.sprite.material.dispose();
      this.group.remove(h.sprite);
    }
    this.scene.remove(this.group);
  }
}
