import { Player } from './player';

export class TouchControls {
  private active = false;
  private joystickTouchId: number | null = null;
  private lookTouchId: number | null = null;

  private joystickOrigin = { x: 0, y: 0 };
  private analogMove = { x: 0, y: 0 };
  private lastLookPos = { x: 0, y: 0 };

  private readonly maxRadius = 45;
  private readonly lookSensitivity = 0.0035;

  private baseEl: HTMLElement;
  private knobEl: HTMLElement;

  constructor(
    private container: HTMLElement,
    private player: Player,
  ) {
    this.baseEl = document.createElement('div');
    this.baseEl.id = 'joystick-base';
    this.baseEl.className = 'joystick-base hidden';

    this.knobEl = document.createElement('div');
    this.knobEl.id = 'joystick-knob';
    this.knobEl.className = 'joystick-knob';

    this.baseEl.appendChild(this.knobEl);
    this.container.appendChild(this.baseEl);

    this.bindEvents();
  }

  getAnalogMove(): { x: number; y: number } {
    return this.analogMove;
  }

  setEnabled(enabled: boolean): void {
    this.active = enabled;
    if (!enabled) {
      this.resetJoystick();
      this.lookTouchId = null;
    }
  }

  private bindEvents(): void {
    this.container.addEventListener('touchstart', this.onTouchStart, { passive: false });
    window.addEventListener('touchmove', this.onTouchMove, { passive: false });
    window.addEventListener('touchend', this.onTouchEnd);
    window.addEventListener('touchcancel', this.onTouchEnd);
  }

  private onTouchStart = (ev: TouchEvent): void => {
    if (!this.active) return;

    const width = window.innerWidth;
    for (let i = 0; i < ev.changedTouches.length; i++) {
      const touch = ev.changedTouches[i];
      // Left half: joystick
      if (touch.clientX < width * 0.5 && this.joystickTouchId === null) {
        ev.preventDefault();
        this.joystickTouchId = touch.identifier;
        this.joystickOrigin = { x: touch.clientX, y: touch.clientY };

        this.baseEl.style.left = `${touch.clientX}px`;
        this.baseEl.style.top = `${touch.clientY}px`;
        this.baseEl.classList.remove('hidden');
        this.knobEl.style.transform = `translate(0px, 0px)`;
        this.analogMove = { x: 0, y: 0 };
      }
      // Right half: look
      else if (touch.clientX >= width * 0.5 && this.lookTouchId === null) {
        ev.preventDefault();
        this.lookTouchId = touch.identifier;
        this.lastLookPos = { x: touch.clientX, y: touch.clientY };
      }
    }
  };

  private onTouchMove = (ev: TouchEvent): void => {
    if (!this.active) return;

    for (let i = 0; i < ev.changedTouches.length; i++) {
      const touch = ev.changedTouches[i];

      if (touch.identifier === this.joystickTouchId) {
        ev.preventDefault();
        const dx = touch.clientX - this.joystickOrigin.x;
        const dy = touch.clientY - this.joystickOrigin.y;
        const dist = Math.hypot(dx, dy);
        const clampedDist = Math.min(dist, this.maxRadius);
        const angle = Math.atan2(dy, dx);

        const knobX = Math.cos(angle) * clampedDist;
        const knobY = Math.sin(angle) * clampedDist;
        this.knobEl.style.transform = `translate(${knobX}px, ${knobY}px)`;

        // Normalized vector: x (-1=left, 1=right), y (1=forward, -1=back)
        this.analogMove = {
          x: knobX / this.maxRadius,
          y: -knobY / this.maxRadius,
        };
      } else if (touch.identifier === this.lookTouchId) {
        ev.preventDefault();
        const dx = touch.clientX - this.lastLookPos.x;
        const dy = touch.clientY - this.lastLookPos.y;
        this.lastLookPos = { x: touch.clientX, y: touch.clientY };

        // Rotate player camera
        this.player.addLook(dx * (this.lookSensitivity / 0.0022), dy * (this.lookSensitivity / 0.0022));
      }
    }
  };

  private onTouchEnd = (ev: TouchEvent): void => {
    for (let i = 0; i < ev.changedTouches.length; i++) {
      const touch = ev.changedTouches[i];
      if (touch.identifier === this.joystickTouchId) {
        this.resetJoystick();
      }
      if (touch.identifier === this.lookTouchId) {
        this.lookTouchId = null;
      }
    }
  };

  private resetJoystick(): void {
    this.joystickTouchId = null;
    this.analogMove = { x: 0, y: 0 };
    this.baseEl.classList.add('hidden');
    this.knobEl.style.transform = `translate(0px, 0px)`;
  }

  destroy(): void {
    this.container.removeEventListener('touchstart', this.onTouchStart);
    window.removeEventListener('touchmove', this.onTouchMove);
    window.removeEventListener('touchend', this.onTouchEnd);
    window.removeEventListener('touchcancel', this.onTouchEnd);
    this.baseEl.remove();
  }
}
