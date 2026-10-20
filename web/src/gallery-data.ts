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
