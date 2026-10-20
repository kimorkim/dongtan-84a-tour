# 84A 웹 투어 (Three.js)

도면·참고 사진·렌더·모델 백업의 위치는 [자료 안내](../docs/asset-guide.md)와
[파일 목록](../docs/asset-inventory.md)을 참고한다. 현재 작업 모델은 프로젝트 루트에 유지한다.

Blender 모델(`apt_84a_photoreal_tour.blend`)을 원본으로 하는 1인칭 집 투어.
집 구조를 웹에서 다시 만들지 않고 `house.glb`를 그대로 불러온다.

시작과 위치 초기화는 현관문 안쪽(Blender x12.33/y7.40), 눈높이 1.65m에서
남쪽 중문·복도를 정면으로 바라본다. 초기화 버튼과 R 키도 같은 설정을 사용한다.

## 실행

```powershell
cd web
npm install
npm run dev
```

브라우저에서 http://localhost:5173 을 연다.

## 조작

| 입력 | 동작 |
| --- | --- |
| 클릭 | 마우스 잡기 (포인터 락) |
| WASD / 방향키 | 이동 |
| 마우스 | 시선 전환 |
| Shift | 빠르게 이동 |
| V | 걷기 / 전체 보기 전환 |
| R 또는 버튼 | 현관 스폰으로 위치 초기화 |
| Esc | 마우스 해제 (브라우저 기본 동작) |
| 슬라이더 | 이동 속도 1~8 m/s (눈높이 1.65m 고정) |

전체 보기 모드에서는 드래그 회전 / 휠 줌이 되며, 천장이 자동으로 숨는다.

## 모델 갱신 (Blender → 웹)

Blender 데몬이 떠 있는 상태에서 프로젝트 루트(`apt/`)에서 순서대로 실행:

```powershell
& "C:\Program Files\Blender Foundation\Blender 4.2\4.2\python\bin\python.exe" "$env:TEMP\mcp_run.py" "scripts\export_house_glb.py" 600
& "C:\Program Files\Blender Foundation\Blender 4.2\4.2\python\bin\python.exe" "$env:TEMP\mcp_run.py" "scripts\bake_collision.py" 600
```

`web/public/house.glb`와 `web/public/colliders.json`이 덮어써진다.
dev 서버가 켜져 있으면 브라우저 새로고침만으로 반영된다.

## 구성

- `public/house.glb` — Blender 익스포트 (Blender 조명/카메라 제외)
- `public/colliders.json` — 베이크된 단순 충돌 박스 547개 (Blender 좌표)
- `src/main.ts` — 부팅, UI, 걷기/전체 모드, 렌더 루프
- `src/player.ts` — 1인칭 이동 + 축분리 충돌 슬라이딩 (반경 0.28m)
- `src/colliders.ts` — 충돌 JSON 로드 + 원/박스 해결
- `src/world.ts` — GLB 로드 + v1 기본 조명

## 알려진 v1 한계 (다음 단계)

- Blender 프로시저럴 재질(벽돌/노이즈/베인)은 GLB에 실리지 않는다.
  지금은 평탄 색상 + 금속/거칠기 수치 + 발광만 넘어온다.
- 조명은 기본(반구/태양/룸별 포인트, 그림자 없음)이다.
- PBR 텍스처 베이크, 그림자/라이트맵은 투어 동작 확인 후 별도 작업.

## 안내 아이콘 음영 회귀 검사

`npm test`는 안내 아이콘이 AO 계산에서 제외되고 이후 원래 가시성으로 복원되는지 검사한다.
개발 서버의 `/tests/hotspot-ao.html`은 실제 욕실 모델을 고정 카메라로 보여 준다.
`?legacy`를 붙이면 수정 전 사각 음영을 재현한다. 테스트 페이지는 배포 빌드 진입점이 아니다.

## 우드 바닥 검증

Q9는 `Exact_Floor` 상면 하나에 2K 오크 PBR와 공통 UV를 사용한다. 방별 우드 덧판은 제거했다.
`npm test`에 실제 GLB의 상면 재질·UV·2K 맵·덧판 제거 검사가 포함된다.
개발 서버 `/tests/floor-review.html`에서 고정 복도 시점으로 확인할 수 있다.
Blender 재현과 사진/제품 추정의 한계는 [품질 보고서](../docs/quality-v2-report.md)의 Q9를 본다.

## 유나방 (침실3)

거실 욕실 옆 동쪽 작은방은 Q10b 유나방이다. 사용자 옵션에 맞춰 방문 옆 기본 붙박이장과 일자 창 벽으로 교정했다.
갤러리 '아이방'에는 전체 방과 기본장 두 사진이 있으며, 방 안 사진 아이콘으로도 열 수 있다.
`/tests/yuna-review.html`은 실제 GLB를 같은 조명·AO로 검토하는 개발용 고정 시점이며 배포 진입점은 아니다.
Blender 검사 `scripts/verify_yuna_room.py`와 일반 Python 보행 검사 `scripts/verify_master_balcony.py`를 함께 실행한다.
전자는 문·창·가구·바닥·러그를, 후자는 현관에서 출입구·놀이 공간·창 앞까지의 연결을 확인한다.
가구·색은 제안이며 실제 제품 치수·안전 인증을 대신하지 않는다.
