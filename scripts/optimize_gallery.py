"""Optimize presentation and review renders to web-friendly WebP assets."""
from pathlib import Path
from PIL import Image

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = REPO_ROOT / "web" / "public" / "gallery"
THUMB_DIR = OUTPUT_DIR / "thumbs"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
THUMB_DIR.mkdir(parents=True, exist_ok=True)

IMAGES = [
    ("yuna-room", "renders/review/render_30_yuna_pov.png", "아이방", "유나방 (침실3)", "방문 옆 기본 붙박이장을 고려한 낮은 침대·그림책 수납·놀이 공간", (13.4, 2.6, 1.35)),
    ("yuna-builtin", "renders/review/render_32_yuna_basic_builtin.png", "아이방", "유나방 기본 붙박이장", "방문 옆 천장 맞춤 기본형 장과 비워 둔 도어 앞 공간 — 규격은 가정값", None),
    # (id, src_rel, room, title, desc, world_pos: (blender_x, blender_y, blender_z))
    ("foyer", "renders/presentation/render_5_foyer_corridor_pov.png", "현관", "현관 및 복도", "중문과 현관 팬트리가 마주보는 진입 복도", (12.33, 7.0, 1.35)),
    ("foyer-pantry", "renders/review/render_22_entry_pantry.png", "현관", "현관 워크인 팬트리", "ㄷ자 시스템 선반이 설치된 대용량 수납공간", (11.15, 6.7, 1.35)),
    ("living", "renders/review/render_29_oak_living.png", "거실", "거실 아트월 및 우물천장", "밝은 오크 바닥과 아트월·우물천장", (6.5, 3.8, 1.35)),
    ("kitchen-island", "renders/presentation/render_3_kitchen_dining_pov.png", "주방", "대면형 주방 및 식당", "11자형 아일랜드 조리대와 6인용 식탁", (6.8, 6.8, 1.35)),
    ("fridge-wall", "renders/review/render_11_fridge_pov.png", "주방", "냉장고장 및 빌트인 수납", "빌트인 냉장고·김치냉장고·밥솥장 라인", (6.0, 7.0, 1.35)),
    ("kitchen-prep", "renders/presentation/render_9_kitchen_prep_pov.png", "주방", "싱크대 및 조리 공간", "와이드 사각 싱크볼과 주방 환기창", (7.4, 7.2, 1.35)),
    ("master-bed", "renders/presentation/render_4_master_bedroom_pov.png", "안방", "안방 (침실 1)", "아늑한 마스터 베드룸 및 발코니 출입문", (2.5, 3.8, 1.35)),
    ("master-balcony", "renders/review/render_14_master_balcony_pov.png", "발코니", "안방 발코니", "세탁 공간과 연결되는 전면 발코니", (2.5, 1.6, 1.35)),
    ("dry-vanity", "renders/review/render_25_dry_vanity_detail.png", "욕실", "호텔식 건식 세면대", "언더마운트 세면볼·양개 하부장·직사각 간접조명 거울", (14.0, 5.0, 1.35)),
    ("bath", "renders/review/render_26_common_toilet_detail.png", "욕실", "공용 욕실 (습식)", "곡면 도기 변기·거울 수납장·모델하우스 사진 기반 타일", (13.98, 6.45, 1.35)),
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
        
        # 2. Thumbnail (max 360px)
        thumb_im = im.copy()
        thumb_im.thumbnail((360, 360), Image.Resampling.LANCZOS)
        thumb_out = THUMB_DIR / f"{item_id}.webp"
        thumb_im.save(thumb_out, "WEBP", quality=80)
        
        print(f"Saved {item_id}: full {full_out.stat().st_size // 1024}KB, thumb {thumb_out.stat().st_size // 1024}KB")

if __name__ == "__main__":
    main()
