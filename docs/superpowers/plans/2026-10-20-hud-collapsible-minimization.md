# HUD Collapsible Minimization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Enable users to collapse/minimize the HUD into a slim top bar via a toggle button (`▲` / `▼`) and keyboard shortcut (`H`), defaulting to collapsed state on mobile.

**Architecture:** Separate the HUD into a fixed header bar (`#hud-header`) and collapsible body (`#hud-body`) in `web/index.html`. Style `#hud.collapsed` in `web/src/style.css` to hide the body and reduce padding. Wire up toggle logic and mobile detection in `web/src/main.ts`.

**Tech Stack:** TypeScript (~5.6.3), HTML5, CSS3, Vite (6.x).

## Global Constraints

- Preserve all existing buttons, slider, and coordinates functionality when HUD is expanded.
- Mode label indicator (`걷기` / `전체 보기`) must remain visible in `#hud-header` even when collapsed.
- Ensure strict TypeScript typing (`tsc --noEmit`) and build (`vite build`) pass without errors.
- Default to collapsed state when `isTouch` is true or viewport width $\le 640\text{px}$.

---

### Task 1: DOM Hierarchy & Styling for Collapsible HUD

**Files:**
- Modify: `web/index.html`
- Modify: `web/src/style.css`

**Interfaces:**
- Consumes: `#hud`, `#mode-label`
- Produces: `#hud-header`, `#btn-hud-toggle`, `#hud-body`, `#hud.collapsed` styling

- [ ] **Step 1: Update `web/index.html` DOM hierarchy**

Wrap the HUD content into `#hud-header` and `#hud-body`:
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

- [ ] **Step 2: Add Collapsible Styles in `web/src/style.css`**

Add header flex layout, toggle button styling, and collapsed rules:
```css
.hud-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.hud-toggle-btn {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #ddd;
  border-radius: 6px;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  cursor: pointer;
  padding: 0;
  transition: all 0.15s ease;
  user-select: none;
}

.hud-toggle-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  color: #fff;
  border-color: rgba(255, 255, 255, 0.35);
}

#hud.collapsed {
  padding: 8px 14px;
  width: auto;
  min-width: 200px;
}

#hud.collapsed .hud-header .hud-title {
  margin-bottom: 0;
}

#hud.collapsed #hud-body {
  display: none;
}
```

- [ ] **Step 3: Run build check**

Run: `cd web; npm.cmd run build`
Expected: PASS with 0 errors.

- [ ] **Step 4: Commit changes**

```bash
git add web/index.html web/src/style.css
git commit -m "feat(web): add DOM structure and styles for collapsible HUD"
```

---

### Task 2: Toggle Logic, Keyboard Shortcut & Mobile Default State

**Files:**
- Modify: `web/src/main.ts`

**Interfaces:**
- Consumes: `#hud`, `#btn-hud-toggle`, `isTouch`
- Produces: `setHudCollapsed(collapsed: boolean)` function, click listener, `KeyH` listener, initial state resolution

- [ ] **Step 1: Implement toggle logic in `web/src/main.ts`**

In `web/src/main.ts`:
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

  // Default to slim/collapsed HUD on mobile/touch devices
  if (isTouch || window.innerWidth <= 640) {
    setHudCollapsed(true);
  }
```

- [ ] **Step 2: Add 'KeyH' shortcut to `keydown` listener**

In `window.addEventListener('keydown', (ev) => ...)`:
```typescript
      case 'KeyH':
        setHudCollapsed(!hud.classList.contains('collapsed'));
        break;
```

- [ ] **Step 3: Run typecheck and build**

Run: `cd web; npm.cmd run typecheck && npm.cmd run build`
Expected: PASS with 0 errors.

- [ ] **Step 4: Commit changes**

```bash
git add web/src/main.ts
git commit -m "feat(web): wire up HUD collapse toggle, H shortcut, and mobile default"
```

---

### Task 3: Verification, Push & Deployment

**Files:**
- Build: `web/dist/`
- Deploy: `gh-pages` branch
- Push: `master` branch

- [ ] **Step 1: Run complete verification**

Run:
```bash
py -3 scripts/verify_master_balcony.py
cd web
npm.cmd run typecheck
npm.cmd run build
```
Expected: PASS.

- [ ] **Step 2: Push `master` to GitHub**

```bash
git push origin master
```

- [ ] **Step 3: Deploy `web/dist` to `gh-pages`**

Deploy using git plumbing and verify GitHub Pages build status (`gh api repos/kimorkim/dongtan-84a-tour/pages`).
Confirm live URL [https://kimorkim.github.io/dongtan-84a-tour/](https://kimorkim.github.io/dongtan-84a-tour/) loads with collapsible HUD.
