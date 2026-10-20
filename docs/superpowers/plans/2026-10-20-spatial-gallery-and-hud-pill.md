# Spatial Gallery & HUD Pill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refine the collapsed HUD into an elegant floating pill capsule that never intrudes across the screen, and implement an in-world spatial gallery system with 3D camera pins and a categorized photo viewer for photorealistic renders.

**Architecture:**
- **HUD Pill:** Update `web/src/style.css` so `#hud.collapsed` uses `width: fit-content; right: auto; border-radius: 24px;`, keeping the toggle button neatly co-located with the title on both mobile and desktop.
- **Gallery Assets:** Python script `scripts/optimize_gallery.py` processes renders into WebP full-res (1600px) and thumbnails (320px) under `web/public/gallery/`.
- **Gallery Modal:** `web/src/gallery-modal.ts` manages a responsive full-screen photo overlay with room category filters, thumbnail carousel, swipe gestures, and keyboard navigation.
- **Spatial Hotspots:** `web/src/hotspots.ts` renders custom camera badge sprites in 3D space with subtle breathing pulse animation, wired to click/tap raycasting in `web/src/main.ts`.

**Tech Stack:** TypeScript (~5.6.3), Three.js (0.170.0), Python/Pillow, Vite (6.x), CSS3.

## Global Constraints

- `#hud.collapsed` must never stretch across full screen width (`right: auto; width: fit-content;`).
- All 3D hotspot coordinates must align with Three.js coordinate mapping ($x, \text{elevation}, -y$).
- Strict TypeScript typing (`tsc --noEmit`) and Vite build must pass without errors.
- Image assets must be optimized WebP format with total gallery bundle footprint under 4MB.

---

### Task 1: Refine HUD Collapsed Pill Layout

**Files:**
- Modify: `web/src/style.css`
- Modify: `web/index.html`

**Interfaces:**
- Consumes: `#hud`, `#hud-header`, `#btn-hud-toggle`
- Produces: Floating capsule (Pill) layout for collapsed HUD without screen-width intrusion

- [ ] **Step 1: Update `#hud-header` and `#hud.collapsed` CSS in `web/src/style.css`**

Update `.hud-header` to remove any conflicting margin and style `#hud.collapsed` as a sleek pill:
```css
.hud-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.hud-title {
  font-size: 15px;
  font-weight: 600;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

#hud-body {
  margin-top: 12px;
}

#hud.collapsed {
  width: fit-content;
  max-width: calc(100vw - 20px);
  padding: 6px 10px 6px 14px;
  border-radius: 24px;
  background: rgba(18, 22, 26, 0.88);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.35);
}

#hud.collapsed .hud-header {
  gap: 8px;
}

#hud.collapsed #hud-body {
  display: none;
}
```

In `@media (max-width: 640px)`:
Ensure `#hud.collapsed` does not inherit `right: 10px`:
```css
  #hud {
    top: 10px;
    left: 10px;
    right: 10px;
    width: auto;
    padding: 10px 14px;
    font-size: 13px;
  }

  #hud.collapsed {
    right: auto;
    width: fit-content;
    padding: 6px 10px 6px 14px;
  }
```

- [ ] **Step 2: Add Top-level Gallery Button to HUD header in `web/index.html`**

```html
        <div id="hud-header" class="hud-header">
          <div class="hud-title">84A 웹 투어 <span id="mode-label">걷기</span></div>
          <div class="hud-header-actions">
            <button id="btn-gallery-open" class="hud-gallery-btn" aria-label="렌더 갤러리 열기" title="렌더 갤러리 (사진첩)">🖼️ 갤러리</button>
            <button id="btn-hud-toggle" class="hud-toggle-btn" aria-label="HUD 접기/펼치기" aria-expanded="true" aria-controls="hud-body" title="HUD 접기/펼치기 (단축키: H)">▲</button>
          </div>
        </div>
```

Style `.hud-header-actions` and `.hud-gallery-btn`:
```css
.hud-header-actions {
  display: flex;
  align-items: center;
  gap: 6px;
}

.hud-gallery-btn {
  background: rgba(224, 168, 60, 0.18);
  border: 1px solid rgba(224, 168, 60, 0.4);
  color: #f6d365;
  border-radius: 14px;
  padding: 4px 10px;
  font-size: 12px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 4px;
  cursor: pointer;
  transition: all 0.15s ease;
  user-select: none;
  white-space: nowrap;
}

.hud-gallery-btn:hover {
  background: rgba(224, 168, 60, 0.3);
  border-color: rgba(224, 168, 60, 0.6);
  color: #fff;
}
```

- [ ] **Step 3: Run build to verify styling integration**

Run: `cd web; npm.cmd run build`
Expected: PASS with 0 errors.

- [ ] **Step 4: Commit changes**

```bash
git add web/index.html web/src/style.css
git commit -m "feat(web): refine HUD collapsed pill layout and add gallery trigger button"
```

---

### Task 2: Gallery Image Optimization Pipeline & Metadata

**Files:**
- Create: `scripts/optimize_gallery.py`
- Create: `web/src/gallery-data.ts`
- Populate: `web/public/gallery/` & `web/public/gallery/thumbs/`

**Interfaces:**
- Consumes: `renders/presentation/*.png`, `renders/review/*.png`
- Produces: `GalleryItem` array and optimized WebP files for web consumption

- [ ] **Step 1: Write `scripts/optimize_gallery.py`**

```python
"""Optimize presentation and review renders to web-friendly WebP assets."""
from pathlib import Path
from PIL import Image

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = REPO_ROOT / "web" / "public" / "gallery"
THUMB_DIR = OUTPUT_DIR / "thumbs"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
THUMB_DIR.mkdir(parents=True, exist_ok=True)

IMAGES = [
    # (id, src_rel, room, title, desc, world_pos: (blender_x, blender_y, blender_z))
    ("foyer", "renders/presentation/render_5_foyer_corridor_pov.png", "현관", "현관 및 복도", "중문과 현관 팬트리가 마주보는 진입 복도", (12.33, 7.0, 1.35)),
    ("foyer-pantry", "renders/review/render_22_entry_pantry.png", "현관", "현관 워크인 팬트리", "ㄷ자 시스템 선반이 설치된 대용량 수납공간", (11.15, 6.7, 1.35)),
    ("living", "renders/presentation/render_2_living_room_pov.png", "거실", "거실 아트월 및 우물천장", "대형 타일 아트월과 3000K 간접조명", (6.5, 3.8, 1.35)),
    ("kitchen-island", "renders/presentation/render_3_kitchen_dining_pov.png", "주방", "대면형 주방 및 식당", "11자형 아일랜드 조리대와 6인용 식탁", (6.8, 6.8, 1.35)),
    ("fridge-wall", "renders/review/render_11_fridge_pov.png", "주방", "냉장고장 및 빌트인 수납", "빌트인 냉장고·김치냉장고·밥솥장 라인", (6.0, 7.0, 1.35)),
    ("kitchen-prep", "renders/presentation/render_9_kitchen_prep_pov.png", "주방", "싱크대 및 조리 공간", "와이드 사각 싱크볼과 주방 환기창", (7.4, 7.2, 1.35)),
    ("master-bed", "renders/presentation/render_4_master_bedroom_pov.png", "안방", "안방 (침실 1)", "아늑한 마스터 베드룸 및 발코니 출입문", (2.5, 3.8, 1.35)),
    ("master-balcony", "renders/review/render_14_master_balcony_pov.png", "발코니", "안방 발코니", "세탁 공간과 연결되는 전면 발코니", (2.5, 1.6, 1.35)),
    ("dry-vanity", "renders/presentation/render_10_common_bath_dry_vanity_pov.png", "욕실", "호텔식 건식 세면대", "복도형 LED 원형 거울 건식 파우더 공간", (12.33, 5.2, 1.35)),
    ("bath", "renders/presentation/render_8_bath_pov.png", "욕실", "공용 욕실 (습식)", "샤워부스 및 고급 포세린 타일 마감", (14.65, 6.8, 1.35)),
    ("dressroom", "renders/presentation/render_7_dress_pov.png", "안방", "드레스룸 및 파우더장", "안방과 연결된 워크인 드레스룸 시스템", (2.2, 7.0, 1.35)),
    ("topdown", "renders/presentation/render_1_isometric_topdown.png", "전체", "84A 입체 평면도", "전체 공간 구조 및 가구 배치도", (7.15, 5.0, 8.0)),
]

def main():
    print(f"Processing {len(IMAGES)} gallery images...")
    for item_id, rel_path, room, title, desc, pos in IMAGES:
        src = REPO_ROOT / rel_path
        if not src.exists():
            print(f"WARNING: Missing {src}")
            continue

        im = Image.open(src).convert("RGB")
        
        # 1. Full web size (max 1600px)
        full_im = im.copy()
        full_im.thumbnail((1600, 1600), Image.Resampling.LANCZOS)
        full_out = OUTPUT_DIR / f"{item_id}.webp"
        full_im.save(full_out, "WEBP", quality=85)
        
        # 2. Thumbnail (max 320px)
        thumb_im = im.copy()
        thumb_im.thumbnail((360, 360), Image.Resampling.LANCZOS)
        thumb_out = THUMB_DIR / f"{item_id}.webp"
        thumb_im.save(thumb_out, "WEBP", quality=80)
        
        print(f"Saved {item_id}: full {full_out.stat().st_size // 1024}KB, thumb {thumb_out.stat().st_size // 1024}KB")

if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run `scripts/optimize_gallery.py`**

Run: `py -3 scripts/optimize_gallery.py`
Expected: 12 WebP files generated in `web/public/gallery/` and `web/public/gallery/thumbs/`.

- [ ] **Step 3: Write `web/src/gallery-data.ts`**

Export the typed data model:
```typescript
export interface GalleryItem {
  id: string;
  room: '전체' | '거실' | '주방' | '안방' | '욕실' | '현관' | '발코니';
  title: string;
  description: string;
  src: string;
  thumb: string;
  /** Three.js coordinates: [x, elevation, z] where z = -blender_y */
  worldPos?: [number, number, number];
}

export const GALLERY_ITEMS: GalleryItem[] = [
  {
    id: 'foyer',
    room: '현관',
    title: '현관 및 복도',
    description: '중문과 현관 팬트리가 마주보는 진입 복도',
    src: './gallery/foyer.webp',
    thumb: './gallery/thumbs/foyer.webp',
    worldPos: [12.33, 1.35, -7.0],
  },
  {
    id: 'foyer-pantry',
    room: '현관',
    title: '현관 워크인 팬트리',
    description: 'ㄷ자 시스템 선반이 설치된 대용량 수납공간',
    src: './gallery/foyer-pantry.webp',
    thumb: './gallery/thumbs/foyer-pantry.webp',
    worldPos: [11.15, 1.35, -6.7],
  },
  {
    id: 'living',
    room: '거실',
    title: '거실 아트월 및 우물천장',
    description: '대형 타일 아트월과 3000K 간접조명',
    src: './gallery/living.webp',
    thumb: './gallery/thumbs/living.webp',
    worldPos: [6.5, 1.35, -3.8],
  },
  {
    id: 'kitchen-island',
    room: '주방',
    title: '대면형 주방 및 식당',
    description: '11자형 아일랜드 조리대와 6인용 식탁',
    src: './gallery/kitchen-island.webp',
    thumb: './gallery/thumbs/kitchen-island.webp',
    worldPos: [6.8, 1.35, -6.8],
  },
  {
    id: 'fridge-wall',
    room: '주방',
    title: '냉장고장 및 빌트인 수납',
    description: '빌트인 냉장고·김치냉장고·밥솥장 라인',
    src: './gallery/fridge-wall.webp',
    thumb: './gallery/thumbs/fridge-wall.webp',
    worldPos: [6.0, 1.35, -7.0],
  },
  {
    id: 'kitchen-prep',
    room: '주방',
    title: '싱크대 및 조리 공간',
    description: '와이드 사각 싱크볼과 주방 환기창',
    src: './gallery/kitchen-prep.webp',
    thumb: './gallery/thumbs/kitchen-prep.webp',
    worldPos: [7.4, 1.35, -7.2],
  },
  {
    id: 'master-bed',
    room: '안방',
    title: '안방 (침실 1)',
    description: '아늑한 마스터 베드룸 및 발코니 출입문',
    src: './gallery/master-bed.webp',
    thumb: './gallery/thumbs/master-bed.webp',
    worldPos: [2.5, 1.35, -3.8],
  },
  {
    id: 'master-balcony',
    room: '발코니',
    title: '안방 발코니',
    description: '세탁 공간과 연결되는 전면 발코니',
    src: './gallery/master-balcony.webp',
    thumb: './gallery/thumbs/master-balcony.webp',
    worldPos: [2.5, 1.35, -1.6],
  },
  {
    id: 'dry-vanity',
    room: '욕실',
    title: '호텔식 건식 세면대',
    description: '복도형 LED 원형 거울 건식 파우더 공간',
    src: './gallery/dry-vanity.webp',
    thumb: './gallery/thumbs/dry-vanity.webp',
    worldPos: [12.33, 1.35, -5.2],
  },
  {
    id: 'bath',
    room: '욕실',
    title: '공용 욕실 (습식)',
    description: '샤워부스 및 고급 포세린 타일 마감',
    src: './gallery/bath.webp',
    thumb: './gallery/thumbs/bath.webp',
    worldPos: [14.65, 1.35, -6.8],
  },
  {
    id: 'dressroom',
    room: '안방',
    title: '드레스룸 및 파우더장',
    description: '안방과 연결된 워크인 드레스룸 시스템',
    src: './gallery/dressroom.webp',
    thumb: './gallery/thumbs/dressroom.webp',
    worldPos: [2.2, 1.35, -7.0],
  },
  {
    id: 'topdown',
    room: '전체',
    title: '84A 입체 평면도',
    description: '전체 공간 구조 및 가구 배치도',
    src: './gallery/topdown.webp',
    thumb: './gallery/thumbs/topdown.webp',
    worldPos: [7.15, 4.5, -5.0],
  },
];
```

- [ ] **Step 4: Typecheck and commit**

Run: `cd web; npm.cmd run typecheck`
Expected: PASS.

```bash
git add scripts/optimize_gallery.py web/src/gallery-data.ts web/public/gallery/
git commit -m "feat(web): add gallery optimization script, WebP assets, and metadata"
```

---

### Task 3: Gallery Modal Component & Styling

**Files:**
- Create: `web/src/gallery-modal.ts`
- Modify: `web/index.html`
- Modify: `web/src/style.css`

**Interfaces:**
- Consumes: `GALLERY_ITEMS`, `GalleryItem` from `./gallery-data`
- Produces: `GalleryModal` class with:
  - `constructor(onToggle?: (open: boolean) => void)`
  - `open(itemId?: string): void`
  - `close(): void`
  - `isOpen(): boolean`

- [ ] **Step 1: Add Gallery Modal DOM structure to `web/index.html`**

```html
      <!-- Gallery Modal -->
      <div id="gallery-modal" class="gallery-modal" hidden>
        <div class="gallery-backdrop"></div>
        <div class="gallery-container">
          <div class="gallery-header">
            <div class="gallery-tabs" id="gallery-tabs">
              <button class="gallery-tab active" data-room="전체">전체</button>
              <button class="gallery-tab" data-room="거실">거실</button>
              <button class="gallery-tab" data-room="주방">주방</button>
              <button class="gallery-tab" data-room="안방">안방</button>
              <button class="gallery-tab" data-room="욕실">욕실</button>
              <button class="gallery-tab" data-room="현관">현관</button>
            </div>
            <button id="btn-gallery-close" class="gallery-close-btn" aria-label="갤러리 닫기">✕</button>
          </div>

          <div class="gallery-stage">
            <button id="btn-gallery-prev" class="gallery-nav-btn prev" aria-label="이전 사진">‹</button>
            <div class="gallery-view">
              <img id="gallery-img" src="" alt="렌더링 뷰" />
              <div class="gallery-caption">
                <div id="gallery-title" class="gallery-caption-title"></div>
                <div id="gallery-desc" class="gallery-caption-desc"></div>
              </div>
            </div>
            <button id="btn-gallery-next" class="gallery-nav-btn next" aria-label="다음 사진">›</button>
          </div>

          <div class="gallery-thumbs-track" id="gallery-thumbs"></div>
        </div>
      </div>
```

- [ ] **Step 2: Add Gallery Modal Styles in `web/src/style.css`**

Add styles for backdrop blur, responsive modal container, tabs, stage, caption, and thumbnail strip.

- [ ] **Step 3: Implement `web/src/gallery-modal.ts`**

Implement image switching, category filtering, swipe navigation, thumbnail active indicator, and keyboard listeners (`Escape`, `ArrowLeft`, `ArrowRight`).

- [ ] **Step 4: Typecheck and build check**

Run: `cd web; npm.cmd run typecheck && npm.cmd run build`
Expected: PASS with 0 errors.

- [ ] **Step 5: Commit changes**

```bash
git add web/index.html web/src/style.css web/src/gallery-modal.ts
git commit -m "feat(web): add GalleryModal component with responsive viewer and category filter"
```

---

### Task 4: 3D Spatial Hotspot Pins & Interaction Integration

**Files:**
- Create: `web/src/hotspots.ts`
- Modify: `web/src/main.ts`

**Interfaces:**
- Consumes: `GalleryModal`, `GALLERY_ITEMS`, `THREE.Scene`, `THREE.Camera`
- Produces: `HotspotManager` rendering glowing 3D camera pins with raycasting click detection

- [ ] **Step 1: Write `web/src/hotspots.ts`**

Create Three.js sprite-based hotspots:
- Generate canvas texture with glowing golden ring and camera emoji/icon.
- Position sprites at `item.worldPos`.
- In `update(dt)`: apply subtle vertical float and scale pulse.
- Raycast handler on pointerdown/click to identify clicked hotspot sprite and open `galleryModal.open(item.id)`.

- [ ] **Step 2: Wire Hotspots and Gallery Modal into `web/src/main.ts`**

- Instantiate `GalleryModal` with callback to pause `touchControls` and keyboard controls while open.
- Instantiate `HotspotManager(scene, walkCam, overCam, (id) => galleryModal.open(id))`.
- Bind `#btn-gallery-open` click to `galleryModal.open()`.
- In render loop, call `hotspots.update(dt, activeCam)`.

- [ ] **Step 3: Verify with typecheck and production build**

Run: `cd web; npm.cmd run typecheck && npm.cmd run build`
Expected: PASS with 0 errors.

- [ ] **Step 4: Commit changes**

```bash
git add web/src/hotspots.ts web/src/main.ts
git commit -m "feat(web): integrate 3D camera hotspot pins and gallery modal into main tour"
```

---

### Task 5: End-to-End Verification, Master Push & Deployment

**Files:**
- Build: `web/dist/`
- Deploy: `gh-pages` branch
- Push: `master` branch

- [ ] **Step 1: Complete verification suite**

Run:
```bash
py -3 scripts/verify_master_balcony.py
cd web
npm.cmd run typecheck
npm.cmd run build
```
Expected: PASS with 0 errors.

- [ ] **Step 2: Push `master` to GitHub**

```bash
git push origin master
```

- [ ] **Step 3: Deploy to `gh-pages`**

Deploy `web/dist` to `gh-pages` using git plumbing and verify status. Confirm live URL loads with refined HUD pill, 3D camera pins, and gallery modal.
