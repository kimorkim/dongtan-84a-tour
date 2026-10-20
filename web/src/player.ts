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
  analogMove?: { x: number; y: number };
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

  addLook(dx: number, dy: number, sensitivity = 0.0022): void {
    this.yaw -= dx * sensitivity;
    this.pitch -= dy * sensitivity;
    this.pitch = Math.max(-1.45, Math.min(1.45, this.pitch));
  }

  update(dt: number, input: WalkInput): void {
    let f = 0;
    let s = 0;
    const speedMult = input.sprint ? 1.7 : 1.0;

    if (input.analogMove && (Math.abs(input.analogMove.x) > 0.05 || Math.abs(input.analogMove.y) > 0.05)) {
      s = input.analogMove.x;
      f = input.analogMove.y;
      const mag = Math.hypot(s, f);
      if (mag > 1) {
        s /= mag;
        f /= mag;
      }
    } else {
      f = (input.forward ? 1 : 0) - (input.back ? 1 : 0);
      s = (input.right ? 1 : 0) - (input.left ? 1 : 0);
    }

    if (f === 0 && s === 0) {
      this.applyToCamera();
      return;
    }

    const v = this.speed * speedMult * dt;
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
