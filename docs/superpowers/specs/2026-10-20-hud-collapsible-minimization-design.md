# HUD Collapsible Minimization Design

- **Date**: 2026-10-20
- **Status**: Approved
- **Scope**: Web 3D apartment walkthrough viewer (`web/`)

## 1. Background & Goals
The apartment tour viewer displays an overlay HUD containing mode switch buttons, position coordinates, movement speed slider, and help text. On mobile displays (and desktop), this HUD covers a significant portion of the upper screen, obstructing the 3D apartment view and camera sightlines.

The goal is to allow users to collapse/minimize the HUD into a slim single-line bar, freeing up screen real estate for the 3D walkthrough:
- A dedicated toggle button (`▲` / `▼`) on the top-right of the HUD header.
- Keyboard shortcut (`H`) on desktop to toggle HUD collapse.
- Default to slim/collapsed state on mobile devices (`max-width: 640px` or touch devices) so the full view is immediately accessible.
- Retain current mode indicator (`걷기` / `전체 보기`) even when collapsed.

---

## 2. DOM & Architecture Changes

### 2.1 DOM Hierarchy (`web/index.html`)
Separate `#hud` into `#hud-header` and collapsible `#hud-body`:
```html
<div id="hud">
  <div id="hud-header" class="hud-header">
    <div class="hud-title">84A 웹 투어 <span id="mode-label">걷기</span></div>
    <button id="btn-hud-toggle" class="hud-toggle-btn" aria-label="HUD 접기/펼치기" title="HUD 접기/펼치기 (단축키: H)">▲</button>
  </div>
  <div id="hud-body" class="hud-body">
    <div class="hud-row">
      <button id="btn-walk" class="active">걷기</button>
      <button id="btn-over">전체 보기</button>
      <button id="btn-reset">위치 초기화</button>
    </div>
    <div class="hud-row">
      <label>이동 속도 <span id="speed-val">3.5 m/s</span></label>
      <input id="speed" type="range" min="1" max="8" step="0.5" value="3.5" />
    </div>
    <div id="pos">x — · y —</div>
    <div class="hud-help">WASD 이동 · 마우스 시선 · Shift 빠르게 · V 모드 전환 · Esc 마우스 해제</div>
  </div>
</div>
```

---

## 3. Styling & Responsive Behavior (`web/src/style.css`)

### 3.1 Base & Collapsed Styles
- `.hud-header`: Flex row, `align-items: center`, `justify-content: space-between`.
- `.hud-toggle-btn`: Compact subtle button (approx. 28×28px, transparent background, border `1px solid rgba(255, 255, 255, 0.2)`), hover/focus effects.
- `#hud.collapsed`:
  - Padding reduced to `8px 14px`.
  - `#hud-body`: `display: none`.
  - `.hud-title`: Margin reset (`margin: 0`).
  - `.hud-toggle-btn`: Displays `▼` (down arrow).
- `#hud:not(.collapsed)`:
  - `.hud-toggle-btn`: Displays `▲` (up arrow).

### 3.2 Mobile Default State
- On mobile screen width (`@media (max-width: 640px)`):
  - When `#hud` is collapsed, it spans as a sleek top bar or compact floating chip:
    `top: 10px; left: 10px; right: 10px;` (or fit-content / auto).
  - Minimum tap height: 38px for touch comfort.

---

## 4. Script Logic (`web/src/main.ts`)

### 4.1 Toggle Functionality
```typescript
const hud = el('hud');
const btnHudToggle = el<HTMLButtonElement>('btn-hud-toggle');

function setHudCollapsed(collapsed: boolean): void {
  hud.classList.toggle('collapsed', collapsed);
  btnHudToggle.textContent = collapsed ? '▼' : '▲';
}

btnHudToggle.addEventListener('click', (ev) => {
  ev.stopPropagation();
  setHudCollapsed(!hud.classList.contains('collapsed'));
});
```

### 4.2 Initial State on Mobile
- If `isTouch || window.innerWidth <= 640`:
  `setHudCollapsed(true);`
- Otherwise default to expanded on desktop (`setHudCollapsed(false)`).

### 4.3 Desktop Shortcut
- In `keydown` event listener:
  `case 'KeyH': setHudCollapsed(!hud.classList.contains('collapsed')); break;`

---

## 5. Verification Plan
1. Static checking: `cd web; npm.cmd run typecheck && npm.cmd run build` (zero errors).
2. Behavior verification:
   - On desktop: defaults to expanded, clicking `▲` collapses to single line with `▼`, pressing `H` toggles collapse.
   - On mobile viewport (<= 640px): defaults to slim bar at top, tapping `▼` reveals full buttons and speed slider.
3. Git commit, push to `master`, build deployment to `gh-pages` branch, and verification on live GitHub Pages.
