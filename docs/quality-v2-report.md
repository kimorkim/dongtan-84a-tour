# 84A 품질 개선 v2 리포트 (핵심 3공간: 거실·주방/식당·안방)

기준: 모델하우스 사진 `display84a_01.jpg`(거실), `display84a_03.jpg`(식당/주방),
`display84a_05.jpg`(침실1). 방식: 편집 가능한 실측 3D 유지 (Mode B).
산출물: `apt_84a_photoreal_tour.blend` 개선본, 재렌더 4뷰, 전후 비교 시트.

## 진단 (개선 전 수치 근거)

- 오브젝트 585개·메시 545개 중 20폴리곤 미만 박스형이 407개. 서브디비전 0개.
- 재질 46종 중 이미지 텍스처가 실제로 연결된 것은 5종뿐이었다.
  벽(`Mat_Wall_Interior`), 아트월, 대리석, 캐비닛, 욕실타일이 전부 단색이었다.
  저장소 `assets/textures`의 PBR 세트 62개 파일이 대부분 미배선 상태였다.
- 조명: 기본광 `Light`(포인트 1000W 잔존), 태양 2개(`Light_Sun`+`Sun_Natural`) 중복,
  포인트 25개 전부 그림자 활성 → 백화(특히 욕실·주방)와 이중 그림자.
- 컬러: Filmic Medium High Contrast, 노출 0.4 고정 (렌더 스크립트가 뷰마다 강제).

## 적용한 개선

### 전역 (`scripts/improve_quality_v2.py`, `v2b`, `v2c`)
- 잔존 기본광 비활성, 태양 단일화(4.5, 각도 2.5°), 포인트 에너지를 실측표로 재조정.
- AgX + 노출 POV 0.35, Cycles 바운스 6/6, 라이트 트리, 월드 필 강도 하향.
- 유리: Transmission(검게 읽힘) → 알파 0.15 Dithered로 교체. 창·다이닝 글라스 공통 해결.
- 조명 색을 주광 중성(1, 0.97, 0.93)으로. 웜은 펜던트·스콘스 액센트만 유지.

### 재질 배선
- 벽: `beige_wall_001` PBR (값 1.70, 채도 0.40으로 모델하우스 라이트 그레이지에 맞춤).
- 아트월: `marble_01` + 1.2m 그라우트 그리드, 명도 상향·채도 하향.
- 대리석: 저장소에 흰 대리석 에셋이 없어 노이즈 기반 화이트 카라라를 프로시저럴로 생성
  (`Mat_Marble_White`, `Mat_Countertop_Granite`). 상판·백스플래시·테이블 공통.
- 바닥재 2종, 타일, 소파·침구·커튼·의자 패브릭, 캐시미어 캐비닛(플라스터 노멀) 배선.

### 거실
- 모브 러그 + 추상 인레이 3종, 원형 대리석 커피테이블, 책 스택, 화분.
- 코르크 푸프 2개(로프 링), 소파 쿠션 5개(모델하우스 색: 슬레이트/라임/플럼/크림/페일블루).
- TV 프레임 블랙메탈 + OLED 저반사로 교체, 콘솔 위 화분·바스켓·책, 시어 커튼, 황동 스콘스.

### 주방·식당
- 수전 전 파츠 크롬 배정(기존 무재질), 인덕션·오븐도어 블랙글라스.
- 인덕션 냄비, 펜듈라 케틀·과일 바스켓, 도마, 싱크 화분.
- 다이닝 러그, 우븐 플레이스매트(기존 커튼 재질 오배정 수정), 의자 다리 브러시드 스틸.

### 안방
- 헤드보드 벽 패널 + 상·하 코브 LED, 기존 월넛 헤드보드를 부클레 패딩 재질로 교체·베벨.
- 베개 세워 배치, 세이지·플럼 쿠션, 라벤더 러너 단일화(기존 이중 겹침 제거).
- 타원 나이트스탠드(남측 신설·대리석 탑), 트윈 펜던트(코드·쉐이드·전구·실광원), 발코니 시어.

### 외부
- 남·북 풍경 카드(하늘·수목·녹지 그라데이션 생성 텍스처, 그림자 차단 해제),
  거실·안방 발코니 난간(상·하 레일 + 밸러스터).

## 검증
- 프리뷰 32샘플 3회 반복 렌더로 밝기·색·유리를 단계 교정 (어두움 → 중성 주광 → 유리 해결).
- 본렌더: Cycles 180샘플, 1600×1200, 루트 4뷰를 교체했다
  (`render_1_isometric_topdown.png`, `render_2_living_room_pov.png`,
  `render_3_kitchen_dining_pov.png`, `render_4_master_bedroom_pov.png`).
  전후 비교: `compare_living.jpg`, `compare_kitchen.jpg`, `compare_master.jpg`.
- 블렌드 재오픈 검증 완료: 오브젝트 696개(Q2 111개), 재질 65종, AgX,
  잔존 기본광·중복 태양 비활성, 벽 텍스처 노드 4개를 확인했다.

## 남은 격차 (정직한 목록)
- 식물 잎이 구형 클러스터라 모델하우스 화분보다 만화적이다. 잎 지오메트리 교체 필요.
- 쿠션·베개가 베벨 박스라 천의 주름·봉제선이 없다. 서브디비전+디스플레이스 여지.
- 풍경 카드는 평면 그림이다. 카메라를 크게 움직이면 입체감이 없다.
- 주방 시스템에어컨 벤트가 어둡다 (기존 그릴 디자인 유지).
- 침실2·3, 알파룸, 현관, 욕실, 드레스룸은 이번 범위 밖이라 구 품질 그대로다.
- 웹 투어(`web/public/house.glb`)는 아직 구 모델이다. GLB 재익스포트 + 충돌 베이크가 다음 단계다.

## 재현 방법
```powershell
Copy-Item apt_84a_photoreal_tour_before_quality_v2.blend apt_84a_photoreal_tour.blend  # (필요시 원복)
& "C:\Program Files\Blender Foundation\Blender 4.2\blender.exe" --background apt_84a_photoreal_tour.blend --python scripts\improve_quality_v2.py
& "C:\Program Files\Blender Foundation\Blender 4.2\blender.exe" --background apt_84a_photoreal_tour.blend --python scripts\improve_quality_v2b.py
& "C:\Program Files\Blender Foundation\Blender 4.2\blender.exe" --background apt_84a_photoreal_tour.blend --python scripts\improve_quality_v2c.py
```
렌더는 `scripts/render_quality_v2.py`를 드라이버에서 `PREVIEW`/`RENDER_DIR` 지정 후 실행.
