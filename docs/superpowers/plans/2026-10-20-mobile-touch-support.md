# Mobile Touch Support & Responsive Controls Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Enable first-person apartment walking and responsive UI on mobile/touch devices using a floating virtual joystick, right-side swipe look, and mobile-optimized WebGL rendering.

**Architecture:** A standalone `TouchControls` module (`web/src/touch.ts`) handles multi-touch tracking, dividing the screen into a left joystick zone and right camera look zone. It integrates with an extended `Player.update()` method in `web/src/player.ts` supporting continuous analog vectors alongside existing keyboard inputs. Responsive CSS styles compact the HUD and style the joystick elements.

**Tech Stack:** TypeScript (~5.6.3), Three.js (0.170.0), Vite (6.x), Vanilla DOM/CSS.

## Global Constraints

- No external joystick or gesture libraries (implement with native Touch Events).
- Preserve all existing desktop keyboard/mouse controls and pointer lock behavior.
- Ensure strict TypeScript typing (`tsc --noEmit` must pass with zero errors).
- Maximum joystick radius $R = 45\text{px}$; inner knob radius $r = 20\text{px}$.
- Maintain 60fps on mobile by capping pixel ratio to 1.5 and bypassing GTAOPass on touch devices.

---

### Task 1: Extend `Player` with Analog Movement Support

**Files:**
- Modify: `web/src/player.ts`

**Interfaces:**
- Consumes: `ColliderBox`, `collideCircle` from `./colliders`
- Produces: `WalkInput.analogMove?: { x: number; y: number }` for continuous velocity calculation in `Player.update()`

- [ ] **Step 1: Update `WalkInput` interface in `web/src/player.ts`**

Add `analogMove?: { x: number; y: number }` to `WalkInput`:
```typescript
export interface WalkInput {
  forward: boolean;
  back: boolean;
  left: boolean;
  right: boolean;
  sprint: boolean;
  analogMove?: { x: number; y: number };
}
```

- [ ] **Step 2: Update `Player.update()` to calculate motion from `analogMove`**

In `web/src/player.ts`:
```typescript
  update(dt: number, input: WalkInput): void {
    let f = 0;
    let s = 0;
    let speedMult = input.sprint ? 1.7 : 1.0;

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
```

- [ ] **Step 3: Run TypeScript typecheck to verify**

Run: `cd web; npm.cmd run typecheck`
Expected: PASS with 0 errors.

- [ ] **Step 4: Commit changes**

```bash
git add web/src/player.ts
git commit -m "feat(web): support analog vector movement in Player update"
```

---

### Task 2: Create `TouchControls` Module (`web/src/touch.ts`)

**Files:**
- Create: `web/src/touch.ts`

**Interfaces:**
- Consumes: `Player` from `./player`
- Produces: `TouchControls` class with:
  - `constructor(container: HTMLElement, player: Player)`
  - `getAnalogMove(): { x: number; y: number }`
  - `setEnabled(enabled: boolean): void`
  - `destroy(): void`

- [ ] **Step 1: Write `web/src/touch.ts`**

```typescript
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
```

- [ ] **Step 2: Typecheck `web/src/touch.ts`**

Run: `cd web; npm.cmd run typecheck`
Expected: PASS with 0 errors.

- [ ] **Step 3: Commit changes**

```bash
git add web/src/touch.ts
git commit -m "feat(web): add TouchControls module for virtual joystick and drag look"
```

---

### Task 3: HTML & CSS Responsive Styling for Mobile

**Files:**
- Modify: `web/index.html`
- Modify: `web/src/style.css`

**Interfaces:**
- Consumes: `#app`, `#hud`, `#joystick-base`, `#joystick-knob`
- Produces: Mobile-friendly styles with media queries, touch prevention, and joystick visuals

- [ ] **Step 1: Update viewport & style meta in `web/index.html`**

Ensure `web/index.html` prevents unwanted pinch zoom and overflow on mobile:
```html
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover" />
```

- [ ] **Step 2: Add Joystick and Mobile CSS to `web/src/style.css`**

Add styles for joystick and responsive HUD layout:
```css
/* Touch-action and Mobile Base */
#app {
  touch-action: none;
  user-select: none;
  -webkit-user-select: none;
}

/* Virtual Joystick */
.joystick-base {
  position: absolute;
  width: 90px;
  height: 90px;
  margin-left: -45px;
  margin-top: -45px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.08);
  border: 1.5px solid rgba(255, 255, 255, 0.25);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
  pointer-events: none;
  z-index: 50;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: opacity 0.15s ease;
}

.joystick-base.hidden {
  opacity: 0;
  pointer-events: none;
}

.joystick-knob {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: radial-gradient(circle at 35% 35%, #f6d365, #e0a83c);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.5);
  pointer-events: none;
}

/* Touch device specific adjustments */
body.is-touch #lock-hint,
body.is-touch #crosshair {
  display: none !important;
}

/* Mobile responsive layout */
@media (max-width: 640px) {
  #hud {
    top: 10px;
    left: 10px;
    right: 10px;
    width: auto;
    padding: 10px 14px;
    font-size: 13px;
  }

  .hud-title {
    font-size: 14px;
    margin-bottom: 8px;
  }

  .hud-row button {
    padding: 6px 10px;
    font-size: 12px;
  }

  .hud-help {
    font-size: 11px;
    margin-top: 6px;
  }
}
```

- [ ] **Step 3: Run build to verify styling integration**

Run: `cd web; npm.cmd run build`
Expected: PASS.

- [ ] **Step 4: Commit changes**

```bash
git add web/index.html web/src/style.css
git commit -m "feat(web): add responsive mobile HUD layout and joystick styling"
```

---

### Task 4: Integrate TouchControls & Mobile Optimizations in `web/src/main.ts`

**Files:**
- Modify: `web/src/main.ts`

**Interfaces:**
- Consumes: `TouchControls` from `./touch`, `Player` from `./player`
- Produces: Integrated walk loop with touch analog motion, touch device detection, and performance fallback

- [ ] **Step 1: Import and initialize `TouchControls` in `web/src/main.ts`**

Import `TouchControls`:
```typescript
import { TouchControls } from './touch';
```

Detect touch device:
```typescript
const isTouch = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
if (isTouch) {
  document.body.classList.add('is-touch');
}
```

Set pixel ratio bounded to 1.5 on touch devices:
```typescript
renderer.setPixelRatio(Math.min(window.devicePixelRatio, isTouch ? 1.5 : 2));
```

Bypass `composer` (GTAOPass) on touch devices to guarantee 60fps:
```typescript
if (!isTouch) {
  try {
    composer = new EffectComposer(renderer);
    renderPass = new RenderPass(scene, walkCam);
    // ...
  } catch (err) { ... }
}
```

Instantiate `TouchControls`:
```typescript
const touchControls = new TouchControls(canvas, player);
```

- [ ] **Step 2: Update `setMode` and render loop to synchronize `TouchControls`**

In `setMode(next: Mode)`:
```typescript
touchControls.setEnabled(walk);
```

In `renderer.setAnimationLoop`:
Combine `keys` and `touchControls.getAnalogMove()`:
```typescript
const analog = touchControls.getAnalogMove();
player.update(dt, { ...keys, analogMove: analog });
```

Update HUD help text for touch devices:
```typescript
const hudHelp = document.querySelector('.hud-help');
if (isTouch && hudHelp) {
  hudHelp.textContent = '왼손 조이스틱 이동 · 오른손 드래그 시선 · V 전체 보기';
}
```

Bypass `canvas.requestPointerLock()` when `isTouch` is true.

- [ ] **Step 3: Verify with typecheck and production build**

Run: `cd web; npm.cmd run typecheck && npm.cmd run build`
Expected: PASS with 0 errors.

- [ ] **Step 4: Commit changes**

```bash
git add web/src/main.ts
git commit -m "feat(web): integrate TouchControls and mobile rendering optimizations"
```

---

### Task 5: End-to-End Verification, Deployment & Release

**Files:**
- Verify: `web/dist/`
- Deploy: `gh-pages` branch
- Push: `master` branch

- [ ] **Step 1: Run complete verification**

Run:
```bash
python scripts/verify_master_balcony.py
cd web
npm.cmd run typecheck
npm.cmd run build
```
Expected: All verification checks pass.

- [ ] **Step 2: Push `master` to GitHub**

```bash
git push origin master
```

- [ ] **Step 3: Deploy `web/dist` to `gh-pages` branch**

Deploy built files to `origin/gh-pages` and verify GitHub Pages build status (`gh api repos/kimorkim/dongtan-84a-tour/pages`).

- [ ] **Step 4: Verify live site on mobile**

Visit `https://kimorkim.github.io/dongtan-84a-tour/` to confirm mobile touch walkthrough.
