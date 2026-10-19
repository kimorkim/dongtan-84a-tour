import * as THREE from 'three';
import { type ColliderBox, collideCircle } from './colliders';

export const EYE_HEIGHT = 1.65;
export const PLAYER_RADIUS = 0.28;

export interface WalkInput {
  forward: boolean;
  back: boolean;
  left: boolean;
  right: boolean;
  sprint: boolean;
}

/** First-person walker on a flat floor with axis-separated AABB sliding. */
export class Player {
  readonly pos = new THREE.Vector3(); // feet position
  yaw = 0;
  pitch = 0;
  speed = 3.5;
  readonly radius = PLAYER_RADIUS;

  private boxes: ColliderBox[] = [];

  constructor(private camera: THREE.PerspectiveCamera) {
    camera.rotation.order = 'YXZ';
  }

  setColliders(boxes: ColliderBox[]): void {
    this.boxes = boxes;
  }

  spawn(x: number, z: number, yaw: number): void {
    this.pos.set(x, 0, z);
    this.yaw = yaw;
    this.pitch = 0;
    this.applyToCamera();
  }

  addLook(dx: number, dy: number): void {
    this.yaw -= dx * 0.0022;
    this.pitch -= dy * 0.0022;
    this.pitch = Math.max(-1.45, Math.min(1.45, this.pitch));
  }

  update(dt: number, input: WalkInput): void {
    const f = (input.forward ? 1 : 0) - (input.back ? 1 : 0);
    const s = (input.right ? 1 : 0) - (input.left ? 1 : 0);
    if (f === 0 && s === 0) {
      this.applyToCamera();
      return;
    }
    const v = (input.sprint ? this.speed * 1.7 : this.speed) * dt;
    const sin = Math.sin(this.yaw);
    const cos = Math.cos(this.yaw);
    // Forward on -Z at yaw 0; strafe right on +X.
    const dx = (-sin * f + cos * s) * v;
    const dz = (-cos * f - sin * s) * v;
    // Axis-separated resolve: each axis slides along walls.
    let solved = collideCircle(this.boxes, this.pos.x + dx, this.pos.z, this.radius);
    this.pos.x = solved.x;
    solved = collideCircle(this.boxes, this.pos.x, this.pos.z + dz, this.radius);
    this.pos.z = solved.z;
    this.applyToCamera();
  }

  private applyToCamera(): void {
    this.camera.position.set(this.pos.x, EYE_HEIGHT, this.pos.z);
    this.camera.rotation.set(this.pitch, this.yaw, 0);
  }
}
