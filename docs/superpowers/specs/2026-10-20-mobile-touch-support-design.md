# Mobile Touch Support & Responsive Controls Design

- **Date**: 2026-10-20
- **Status**: Approved
- **Scope**: Web 3D apartment walkthrough tour (`web/`)

## 1. Background & Goals
The 84A apartment web tour currently supports desktop controls (WASD keys + mouse pointer lock for first-person walking, mouse orbit for overview mode). On mobile and tablet devices, pointer lock and keyboard input are unavailable, preventing users from walking through the unit or comfortably interacting with the 3D model.

The goal is to provide a smooth, mobile-friendly walkthrough experience on touchscreens:
- **Left thumb**: Floating virtual joystick for planar walking (forward, backward, strafe left/right, and analog angles).
- **Right thumb**: Touch drag on the right side of the screen for camera look (yaw/pitch).
- **Responsive HUD**: Compact, touch-friendly UI without desktop keyboard hints or pointer-lock banners.
- **Mobile performance**: Optimized rendering (standard WebGL pipeline with bounded pixel ratio) ensuring consistent 60fps.

---

## 2. Touch Controls Architecture (`web/src/touch.ts`)

### 2.1 Touch Zones & Multi-touch Separation
- The screen is divided logically into two interaction zones during `walk` mode:
  - **Joystick Zone** (left 50% of the screen):
    - On `touchstart` in this zone, an active touch identifier is registered for the joystick.
    - If no joystick UI exists at touch position, a floating joystick appears centered at the initial touch point (or fixed at bottom-left within a comfortable margin).
    - As the touch moves (`touchmove`), the displacement vector from center is calculated:
      - Max radius clamp: $R = 45\text{px}$.
      - Knob displacement: bounded within $R$.
      - Normalized analog vector: $(v_x, v_y) \in [-1, 1]^2$.
    - On `touchend`/`touchcancel`, the joystick resets to neutral $(0, 0)$ and knob returns to center.
  - **Look Zone** (right 50% of the screen):
    - Any touch starting in the right 50% is designated as the look control.
    - On `touchmove`, delta $(\Delta x, \Delta y)$ is computed from the previous touch position.
    - Passes delta to camera look rotation with touch sensitivity scaling:
      - `yaw -= dx * 0.0035`
      - `pitch -= dy * 0.0035` (clamped to $[-1.45, 1.45]$)
    - On `touchend`/`touchcancel`, the look touch identifier is cleared.

### 2.2 Gesture & Scroll Suppression
- `touch-action: none` applied to `#app` and `#scene` elements.
- `preventDefault()` called on active canvas touch events to prevent browser back/forward swipe navigation, pinch-to-zoom on the viewport, and pull-to-refresh.

---

## 3. Player Class Integration (`web/src/player.ts`)

### 3.1 Input Interface Extension
Extend `WalkInput` to accept continuous analog movement:
```typescript
export interface WalkInput {
  forward: boolean;
  back: boolean;
  left: boolean;
  right: boolean;
  sprint: boolean;
  analogMove?: { x: number; y: number }; // x: strafe (-1=left, 1=right), y: forward/back (-1=back, 1=forward)
}
```

### 3.2 Movement Update Logic
- If `analogMove` is present and $|analogMove| > 0.05$:
  - Calculate movement direction in camera yaw space:
    $$\Delta x = (-\sin(\text{yaw}) \cdot y + \cos(\text{yaw}) \cdot x) \cdot v \cdot \text{magnitude}$$
    $$\Delta z = (-\cos(\text{yaw}) \cdot y - \sin(\text{yaw}) \cdot x) \cdot v \cdot \text{magnitude}$$
  - Apply circle-AABB collider resolution per axis as existing sliding collision.
- If `analogMove` is absent or zero, fall back to keyboard discrete `WalkInput` boolean flags.

---

## 4. UI & Responsive Styling (`web/src/style.css` & `index.html`)

### 4.1 Touch Device Detection
- Detect touch capability:
  `const isTouch = 'ontouchstart' in window || navigator.maxTouchPoints > 0;`
- When `isTouch` is true:
  - Add `.is-touch` class to `document.body` or `#app`.
  - Permanently hide `#lock-hint` and `#crosshair`.
  - Update `#hud-help` text to: `왼손 조이스틱 이동 · 오른손 드래그 시선`.
  - Bypass `canvas.requestPointerLock()` on canvas click.

### 4.2 HUD Layout for Small Screens
- Add mobile media queries (`@media (max-width: 640px)`):
  - Position `#hud` at the top with reduced padding and compact layout:
    - Title and mode switch buttons in a single flex row.
    - Speed slider compact or collapsed by default.
    - Floating joystick positioned at bottom-left:
      - Outer ring: 90px diameter, subtle translucent dark background (`rgba(255, 255, 255, 0.15)`), border `1px solid rgba(255, 255, 255, 0.3)`.
      - Inner knob: 40px diameter, white/gold translucent circle (`#e0a83c`).
  - Overview mode (`OrbitControls`):
    - Hide joystick when switching to `overview` mode.
    - Allow standard OrbitControls touch gestures (1-finger rotate, 2-finger pinch zoom/pan).

---

## 5. Performance & Resource Optimization

### 5.1 Post-Processing & Shader Fallback
- On touch/mobile devices:
  - Disable heavy `GTAOPass` by default, or bypass `EffectComposer` directly to `WebGLRenderer.render(scene, camera)`.
  - Cap pixel ratio at `Math.min(window.devicePixelRatio, 1.5)` to conserve GPU fillrate on high-DPI displays (Retina, OLED).

---

## 6. Verification Plan

1. **Static Analysis & Build**:
   - `cd web; npm.cmd run typecheck`
   - `cd web; npm.cmd run build`
2. **Interactive Emulation Verification**:
   - Test using browser mobile simulation (iPhone 14 / Galaxy S20 viewport) with touch events enabled:
     - Verify left joystick appears and controls player position smoothly with wall collision.
     - Verify right screen swipe rotates yaw and pitch smoothly without page scroll.
     - Verify clicking '전체 보기' switches to top-down view and hides the joystick.
     - Verify clicking '위치 초기화' resets player to front door entrance.
3. **Deployment**:
   - Commit changes to `master` and push to `origin/master`.
   - Update `gh-pages` branch with new production build and verify on GitHub Pages live URL.
