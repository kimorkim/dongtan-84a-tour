# Spatial Gallery & HUD Pill Design

- **Date**: 2026-10-20
- **Status**: Approved
- **Scope**: Web 3D apartment walkthrough tour (`web/`)

## 1. Background & Goals
Users currently walk through the 84A 3D model in real time, but the repository also contains photorealistic offline Blender Cycles presentation renders of key rooms (living room art wall, kitchen island & fridge wall, master bedroom, hotel-style dry vanity, entrance foyer, etc.).

Additionally, when the HUD is collapsed on mobile, the container spans full width across the top of the screen (`left: 10px; right: 10px`), leaving the toggle button separated from the title and intruding into the central 3D view area.

The goals are:
1. **Refine HUD Collapsed Layout**: Transform the collapsed HUD into an elegant, self-contained floating capsule/pill (`border-radius: 20px`, `width: fit-content`) so it never stretches across the screen or invades other interactive zones.
2. **In-World Spatial Hotspot Pins**: Place 3D camera hotspot markers (`📷`) at key room locations. Clicking or tapping a hotspot opens the high-resolution render view for that specific room.
3. **Dedicated Photo Gallery Modal**: Provide a top-level `[ 🖼️ 갤러리 ]` entry point that opens a categorized gallery viewer (Living Room, Kitchen, Master Bed, Bath, Foyer) with carousel navigation, thumbnails, and optimized WebP images.

---

## 2. Refined HUD Collapsed Layout (`web/src/style.css`)

### 2.1 Floating Capsule (Pill) Behavior
- When `#hud.collapsed`:
  - `right: auto; width: fit-content; max-width: calc(100vw - 20px);`
  - `padding: 6px 10px 6px 14px;`
  - `border-radius: 24px;`
  - Aligns `.hud-title` and `.hud-toggle-btn` on the same horizontal baseline with a clean `gap: 10px`.
  - On mobile (`max-width: 640px`):
    - `top: 10px; left: 10px; right: auto;`
    - Preserves touch clearance while leaving the rest of the top and center screen completely unobstructed.
- In `#hud-header`:
  - Clean flex centering `align-items: center` with no conflicting bottom margin on `.hud-title`.

---

## 3. Gallery Asset Optimization & Public Directory Structure

### 3.1 Asset Pipeline (`scripts/optimize_gallery.py`)
Convert high-res presentation renders into web-optimized WebP assets in `web/public/gallery/`:
- **Full resolution**: Max dimension 1600px, WebP quality 85 (approx. 150–250KB per image).
- **Thumbnails**: Max dimension 320px, WebP quality 80 (approx. 20–30KB per image).

### 3.2 Key Rooms & Render Metadata (`web/src/gallery-data.ts`)
Each gallery item contains:
- `id`: unique string (e.g. `'living-artwall'`)
- `room`: `'거실' | '주방' | '안방' | '욕실' | '현관' | '발코니'`
- `title`: human-readable Korean title
- `src`: full-size WebP path (`/gallery/...webp`)
- `thumb`: thumbnail WebP path (`/gallery/thumbs/...webp`)
- `worldPos`: 3D coordinates `[x, y, z]` for spatial hotspot pin (in Three.js coordinates: $x, \text{elevation}, -y$)

Key Hotspots:
1. **현관/중문**: `x12.33, y7.20` -> Foyer & Middle door view
2. **거실**: `x6.50, y3.80` -> Living room & Artwall view
3. **주방/식당**: `x6.80, y6.80` -> Kitchen island & Dining view
4. **냉장고장**: `x6.00, y7.00` -> Refrigerator bay view
5. **안방**: `x2.50, y3.80` -> Master bedroom view
6. **건식 세면대/공용욕실**: `x12.33, y5.20` -> Hotel-style vanity view
7. **안방 발코니**: `x2.50, y1.60` -> Balcony & refuge view

---

## 4. 3D In-World Hotspots Architecture (`web/src/hotspots.ts`)

### 4.1 Visual Representation
- Each hotspot is represented as a Three.js `Sprite` with a custom canvas-rendered circular camera icon badge (`📷` with luminous ring and subtle breathing animation).
- Positioned at eye level ($y = 1.35\text{m}$) within the apartment.
- Raycasting / pointer listener detects clicks and taps on hotspot sprites.
- Hover effect: scales badge up slightly ($1.15\times$) with cursor pointer.

### 4.2 Interaction
- Clicking/tapping a hotspot opens the Gallery Modal focused directly on that room's photo.
- During `overview` mode, hotspots remain visible and clickable from the top-down perspective.

---

## 5. Gallery Modal UX (`web/src/gallery-modal.ts` & `index.html`)

### 5.1 Modal Components
- **Top Bar**:
  - Room category pills (`전체`, `거실`, `주방`, `안방`, `욕실`, `현관`)
  - Close button (`✕`)
- **Main View**:
  - Full-size image with responsive object-fit (`contain`)
  - Previous (`‹`) / Next (`›`) navigation arrows
  - Image title and caption overlay
- **Bottom Carousel**:
  - Horizontal scrollable thumbnail strip with active thumbnail indicator
  - Clicking any thumbnail smoothly transitions the main view

### 5.2 Event & Touch Integration
- Pauses walk/look touch controls while the modal is open (`touchControls.setEnabled(false)`).
- Supports swipe gestures (left/right) on mobile screens to advance photos.
- Keyboard support: `Escape` to close, `ArrowLeft` / `ArrowRight` to navigate.

---

## 6. Verification Plan

1. **Asset pipeline execution**:
   - Run `py -3 scripts/optimize_gallery.py` and verify `web/public/gallery/` is populated.
2. **Static check & build**:
   - `cd web; npm.cmd run typecheck`
   - `cd web; npm.cmd run build`
3. **Visual & Interaction Verification**:
   - Check HUD in collapsed state: confirm it forms a compact pill, does not stretch across mobile screen, and toggle button stays neatly inside.
   - Walk up to living room/kitchen: verify 3D camera pins are visible, pulsing, and clickable.
   - Click/tap pin: verify gallery modal opens on the selected photo.
   - Test thumbnail strip, previous/next, and category filters.
   - Verify desktop shortcut (`H`, `Escape`, arrow keys) and mobile swipe.
4. **Deployment**:
   - Commit to `master`, push to GitHub, build and deploy to `gh-pages`.
   - Verify live URL [https://kimorkim.github.io/dongtan-84a-tour/](https://kimorkim.github.io/dongtan-84a-tour/).
