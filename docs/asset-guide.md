# 자료 안내 — 동탄 84A 모델링 프로젝트

정리일: 2026-10-20. 루트의 이미지·도면·과거 모델과 기존 렌더 폴더를 분류했다.
파일명과 내용은 유지했고, 103개 이동 파일의 SHA-256이 이동 전후 일치함을 확인했다.
전체 104개 자료(이미지 95, Blender 모델 7, PDF 1, JSON 1)의 이동표는 [파일 목록](asset-inventory.md)을 본다.
자동 백업 `*.blend1`, 텍스처, 소스 코드, 웹 빌드 파일은 이 목록의 대상이 아니다.

## 먼저 볼 파일

- **현재 치수는 Q12**: [도면 치수 교정 기록](dimension-correction-q12.md),
  [교정된 전체 평면](../renders/review/render_36_dimensioned_plan.png)을 먼저 본다.
  아래 Q4~Q11의 배치 선택은 유지했지만 옛 좌표·미갱신 렌더는 현행 치수 근거가 아니다.

- 현재 모델: [apt_84a_photoreal_tour.blend](../apt_84a_photoreal_tour.blend).
  작업과 익스포트의 기준이며, 루트 위치를 유지한다.
- 현재 냉장고장 배치: [냉장고 POV](../renders/review/render_11_fridge_pov.png),
  [싱크 옆 문 POV](../renders/review/render_12_sink_door_pov.png).
  거실(남) → 냉장고 → 김치냉장고 → 밥솥장 → 부엌(북) 순서다.
- 현재 안방 발코니·대피실: `renders/review/`의 13번 평면 검토, 14번 발코니, 15번 대피실 POV.
  Q4 보수에서 두 출입문·외창·외벽을 고치고 보행 경로를 열었다. 세부 가정은 품질 보고서를 본다.
  안방→발코니는 미닫이이며, 초기 여닫이 해석은 사용자 확인 후 수정했다.
- 변경 이력·검증·남은 한계: [품질 보고서](quality-v2-report.md).
- 현재 알파룸: `renders/review/` 16번 평면·17번 POV. 벽 복구와 책상·의자 제거 후 상태다.
  식탁 러그 침범 수정 후 두 이미지를 갱신했으며, 16번은 식탁까지 함께 보여 준다.
- 현재 실외기실: 18번 평면·19번 POV. Q6에서 벽·바닥·루버·실외기 위치를 정리했다.
  16·17번에는 실외기실 Q6 보수 전 모습이 남아 있다.
- 현재 현관: 20번 평면·22번 팬트리·23번 열린 현관. 21번 중문은 재질 비교용 임시 닫힘 상태다.
  Q7의 공식 VR 원본 8장과 장면별 해석은 [참고 이미지 출처](../references/modelhouse/vr84a/README.md)를 본다.
- 다른 에이전트의 시작점: [AGENTS.md](../AGENTS.md).
- 현재 우드 바닥: Q9의 `renders/review/` 28번 복도·29번 거실 및 `web_floor_before/after.jpg`.
  방별 덧판 대신 공통 상면과 같은 UV를 사용하며, 기존 타일은 유지한다.
- 현재 유나방(침실3): Q10b의 갱신된 30번 POV·31번 평면·32번 기본장과 `web_yuna_after.jpg`.
  사용자 옵션은 방문 옆 기본 붙박이장이다. 공식 VR 013의 창 옆 장은 다른 옵션이며 재현 대상이 아니다.
  기본장 규격은 가정값이고, 창 쪽 실내 마감선을 일자로 보완했다.
- 현재 침실2 서재: Q11의 33번 POV·34번 평면·35번 책상 뷰 및 웹 갤러리 '서재'.
  창 벽 마감선을 맞추고 동쪽 벽에 화이트 1800/1400 모션테이블과 검정/그레이 에어론 형태 의자를 배치했다.
  공식 제품 페이지·사진은 `references/furniture/erectus/`에 있으며 제조사 CAD와 구분한다.
  Q11b에서 델 듀얼 모니터·클램쉘 맥북·A2 및 작은 책상 게이밍/본체 장비를 추가했고,
  같은 33~35번을 갱신했다. 제품 지정/치수 가정은 `references/furniture/workstation.md`를 본다.
- 현재 거실 욕실: `renders/review/` 24번 평면·25번 건식 세면대·26번 변기·27번 샤워실.
  Q8 근거 사진은 공식 VR 015/016이며 기존 발표용 욕실 렌더보다 최신이다.
- 실제 웹 투어: `web/public/house.glb`와 `web/public/colliders.json`.
  [웹 실행 안내](../web/README.md)를 참고한다.

## 분류와 사용 목적

| 폴더 | 개수 | 내용과 사용 기준 |
| --- | ---: | --- |
| `references/drawings/original/` | 1 | 정보공개 도면 원본 PDF. 치수·구조를 검토할 때 원본과 대조한다. |
| `references/drawings/pages/` | 10 | `page_1,2,3,4,17,18,32,46,60,74.png`. 도면 페이지 추출 이미지. |
| `references/drawings/crops/` | 11 | CAD 현관·주방 확대, 치수 부분, 74페이지 세대 발췌와 좌우 반전본. |
| `references/layout/original/` | 2 | `84A.jpg` 입체 평면 참고도와 `unit_84a.png` 평면 이미지. CAD 실측값과 구별한다. |
| `references/layout/crops/` | 11 | 입체·평면 참고도의 방별 발췌, 주방/중앙 구역/욕실 확대. |
| `references/modelhouse/original/` | 6 | `display84a_01,03,05,06,07,08.jpg` 모델하우스 웹페이지 캡처. 원본 CAD가 아니다. |
| `references/modelhouse/crops/` | 7 | 주방 3장, 욕실·건식 세면대 4장의 부분 이미지. |
| `references/modelhouse/vr84a/` | 20 JPG | 공식 84A VR 013 침실3·015/016 욕실·017 현관/018 현관창고 큐브맵 면. README에 출처·사진 해석 기록. |
| `references/materials/` | 1 | `prugio_84a_finishes.jpg` 마감·자재 참고 이미지. |
| `assets/analysis/` | 5 | 벽 마스크·윤곽 오버레이·좌표 격자·`polys.json`. 도면에서 가공한 작업 데이터. |
| `renders/review/` | 29 | 가전 11·12번, 발코니·대피실 13~15번, 알파룸 16·17번, 실외기실 18·19번, 현관 20~23번, 욕실 24~27번, 바닥 28·29번, 유나방 30~32번, 웹 시작/갤러리/아이콘 음영/바닥 전후/유나방 캡처. |
| `renders/presentation/` | 10 | 탑뷰·거실·주방·안방·현관·욕실 등의 발표용 렌더. 생성 시점이 서로 다르다. |
| `renders/comparisons/` | 3 | 거실·주방·안방 품질 개선 전후 비교. 현재 배치 전체를 증명하는 이미지가 아니다. |
| `renders/previews/` | 9 | 이전 `previews_pbr/`. 저샘플 PBR/평면 검토 이미지. |
| `renders/verification/structure/` | 4 | 골조 검증 3뷰와 `exact_structure_preview.png`. 과거 작업 검증 자료. |
| `renders/verification/crops/` | 3 | 과거 렌더의 현관·욕실 부분 확대. 실물 참고 사진이 아니다. |
| `renders/archive/early-tour/` | 4 | 초기 가구 배치 투어. 현재 모델보다 이전 단계다. |
| `renders/archive/before-quality-v2/` | 8 | 이전 `renders_prev/`. 품질 개선 이전 렌더 보관본. |
| `models/archive/` | 4 | 초기·골조·초기 가구 모델. 현행 모델로 오인하지 않는다. |
| `models/backups/` | 11 | 품질 개선 전, 냉장고장 변경 전, 발코니 보수 전, 미닫이 교정 전, 알파룸 보수 전, 실외기실 보수 전, 현관 보강 전, 욕실 보강 전, 우드 바닥 보강 전, 유나방 변경 전, 유나방 기본 옵션 교정 전. |
| `assets/textures/`, `assets/textures_export/` | 목록 제외 | 기존 원본 텍스처와 웹 익스포트용 가공 텍스처. 위치를 유지한다. |

## 출처와 해석 주의

### 도면

원본은 `references/drawings/original/정보공개 파일(A76-2BL_도면)_1.pdf`다.
PDF 추출본과 CAD 확대는 실제 도면 계열이고, `84A.jpg`의 가구가 보이는 입체 평면 이미지는
시각 참고 자료다. 이 둘을 모델 렌더와 혼동하지 않는다.

`*_74*`의 74는 기존 파일명에서 페이지를 가리키는 표기이며, 74㎡형이라는 뜻으로 해석하지 않는다.
`*_flipped.png`는 좌우 반전한 파생본이다. 원본 방향과 모델 좌표를 대조한 뒤 사용한다.
도면의 방 번호·치수 표기는 전체 크기로 열어 확인해야 한다.

`page_*.png`의 번호는 기존 추출 파일명을 유지했다. 이번 정리에서 원본 PDF 전체를 다시 추출하거나
페이지 번호의 0/1 시작 규칙을 재검증하지는 않았다. 과거 설계서는 4·74페이지를 출처로 기록한다.
후속 Q4 보수에서 원본 PDF 100페이지 중 실제 4·74페이지를 다시 열었고 74페이지 도면을 대조했다.
외부 평면 이미지 두 장의 원 URL과 일부 수작업 크롭의 정확한 생성 과정은 저장소에서 확인되지 않았다.

### 모델하우스 사진

다운로드 스크립트에 기록된 원 출처는
`https://www.prugio.com/hb/2025/dongtan/assets/images/sub/display84a_XX.jpg`다.
이번에는 재다운로드하거나 현재 사이트의 내용을 검증하지 않았다.

| 파일 | 눈으로 확인한 내용 |
| --- | --- |
| `display84a_01.jpg` | 거실·TV 벽·창가 시점 묶음 |
| `display84a_03.jpg` | 식당·주방 시점 묶음 |
| `display84a_05.jpg` | 안방 시점 묶음 |
| `display84a_06.jpg` | 상단 침실2 서재, 하단 침실3 아이방. 공식 VR 012/013 메뉴 및 사진 표제로 대조 |
| `display84a_07.jpg` | 건식 세면대·습식 욕실 등 욕실 공간 묶음 |
| `display84a_08.jpg` | 공식 전시품목 분류와 VR로 재확인: 현관·신발장·현관창고 묶음. 드레스룸이 아님 |
| `display_03_part_1,2,3.jpg` | 식당 전체, 싱크대, 조리대·오븐 쪽 주방 부분 |
| `display84a_07_part_1,2,3,4.jpg` | 건식 세면대, 변기·샤워, 다른 세면대·욕실 부분 |

웹페이지 캡처에는 UI 표시와 여러 사진이 함께 들어 있다. 이미지 전체를 한 시점의 실내 사진으로
간주하지 않는다. 세부 방 이름이 불확실하면 파일명을 그대로 인용하고 추정이라고 표시한다.

### 최신 상태와 과거 자료

`renders/review/` 11·12번은 냉장고·김치냉장고·밥솥장 순서 변경 후 촬영됐고,
13·14·15번은 후속 안방 발코니·대피실 보수 후 촬영됐다.
16·17번은 Q5 알파룸 보수 후 촬영됐다. 17번은 벽 확인용 임시 보조광을 사용했으며 모델에는 저장하지 않았다.
`renders/presentation/`의 1~10번과 비교 시트·프리뷰·골조 검증본에는 이전 상태가 남아 있을 수 있다.
폴더명이나 수정일만으로 모든 이미지가 현재 모델과 일치한다고 단정하지 않는다.

초기 [설계서](superpowers/specs/2026-10-16-dongtan-84a-apartment-modeling-design.md)와
[실행 계획](superpowers/plans/2026-10-16-dongtan-84a-apartment-modeling.md)은 당시의 기록이다.
그 안의 좌우 배치·치수·출력 경로가 후속 교정 전 상태일 수 있으므로, 현재 모델을 이 문서 값으로
되돌리지 않는다. 현행 좌표와 검증 내용은 품질 보고서와 저장된 모델을 확인한다.

## 생성·갱신 경로

명령은 프로젝트 루트에서 실행한다. 렌더에 `RENDER_DIR`를 직접 지정하면 그 경로가 우선한다.

| 작업 | 스크립트 | 기본 입출력 |
| --- | --- | --- |
| 입체 평면도 부분 발췌 | `scripts/crop_ref.py` | `references/layout/original/84A.jpg` → `references/layout/crops/` |
| 모델하우스 자료 다운로드 | `scripts/download_refs.py`, `download_more_refs.py` | `references/modelhouse/original/` |
| 윤곽 기반 초기 골조 | `scripts/rebuild_exact_walls.py` | `assets/analysis/polys.json` → 골조·`renders/verification/structure/` |
| 냉장고장 구성 | `scripts/fix_fridge_option1.py` | 현행 Blender 파일 저장. 거실 → 냉장고 → 김치 → 밥솥 |
| 최신 가전 확인 렌더 | `scripts/render_fridge_pov.py` | `renders/review/` |
| 안방 발코니·대피실 보수 | `scripts/fix_master_balcony.py` | 현행 Blender 파일 저장. 과거 전체 생성 스크립트보다 뒤에 실행 |
| 알파룸 벽 복원·가구 제거 | `scripts/fix_alpha_room.py` | Q3/Q4 뒤 실행. 원본 저장 후 충돌·GLB 재생성 필요 |
| 알파룸 렌더·형상 검사 | `scripts/render_alpha_room.py`, `verify_alpha_room.py` | `renders/review/` 16·17번 / Blender 내부 검사 |
| 실외기실 보수·검증 | `scripts/fix_utility_room.py`, `verify_utility_room.py` | Q5 뒤 Q6 적용. Blender 내부 형상 검사 |
| 실외기실 렌더 | `scripts/render_alpha_room.py -- --utility` | `renders/review/` 18·19번. 모델에 저장하지 않는 검토용 보조광 사용 |
| 현관 디테일·검증 | `scripts/detail_foyer.py`, `verify_foyer.py` | Q6 뒤 Q7 적용. 중문·팬트리·신발장/Blender 검사 |
| 현관 확인 렌더 | `scripts/render_foyer_detail.py` | `renders/review/` 20~23번. 21번만 임시 닫힘 촬영, 원본 저장 안 함 |
| 거실 욕실 디테일·검증 | `scripts/detail_common_bath.py`, `verify_common_bath.py` | Q7 뒤 Q8 적용. 실제 세면볼 개구부·곡면 변기·샤프트 앞 샤워 부속·사진 타일 검사 |
| 거실 욕실 렌더 | `scripts/render_common_bath.py` | `renders/review/` 24~27번. 원본 저장 안 함 |
| 우드 바닥 개선·검증 | `scripts/improve_flooring.py`, `verify_flooring.py` | Q8 뒤 Q9 적용. 덧판 제거·공통 UV·2K PBR·타일 보존 검사 |
| 우드 바닥 렌더 | `scripts/render_flooring.py` | `renders/review/` 28·29번. 원본 저장 안 함 |
| 유나방 보강·검증·렌더 | `scripts/detail_yuna_room.py`, `verify_yuna_room.py`, `render_yuna_room.py` | Q9 뒤 Q10b. 방문 옆 기본장·도어 여유·일자 창 벽·통로 검사, 30~32번 렌더 |
| 침실2 서재·검증·렌더 | `scripts/detail_study_room.py`, `verify_study_room.py`, `render_study_room.py` | Q10b 뒤 Q11. 창 벽 마감·모션테이블 두 자리·검정/그레이 의자, 33~35번 렌더 |
| 발코니·대피실 렌더/보행 검증 | `scripts/render_master_balcony.py`, `verify_master_balcony.py` | `renders/review/` 13~15번 / 현행 충돌 JSON 검사 |
| 품질 v2 렌더 | `scripts/render_quality_v2.py` | `renders/presentation/` |
| 기존 10뷰 렌더 | `scripts/render_present_views.py` | `renders/presentation/`. 과거 조명 재설정 로직이 있어 품질 보고서를 먼저 확인 |
| 저샘플 프리뷰 | `scripts/run_preview_one.py`, `run_preview_pbr.py`, `run_plantop.py` | `renders/previews/` |
| 초기 단계 저장 | `scripts/task1_baseline.py`, `task6_verify_and_save.py`, `furnish_and_tour.py` | `models/archive/`, 해당 과거 렌더 폴더 |
| 웹 반영 | `scripts/bake_collision.py`, `export_glb_textured.py` | `web/public/colliders.json`, `house.glb` |

렌더 예:

```powershell
& "C:\Program Files\Blender Foundation\Blender 4.2\blender.exe" --background apt_84a_photoreal_tour.blend --python-exit-code 1 --python scripts/render_fridge_pov.py
```

`rebuild_exact_walls.py` 등 과거 생성 스크립트는 현재 수정된 벽·가구를 대체할 수 있다.
기존 변경을 이어갈 때는 현행 Blender 파일을 열고 필요한 부분만 수정한다.
모델 변경 후 웹 충돌 데이터와 GLB를 함께 갱신하고, 필요한 확인 렌더도 새로 찍는다.

이번 정리에서는 `.blend`의 내용도 보존했다. 현행 저장본 내부의 렌더 출력 설정은 여전히
루트의 `render_10_common_bath_dry_vanity_pov.png`를 가리킨다. 위 스크립트는 실행 시 새 경로를
설정하지만, Blender GUI에서 직접 저장할 때는 출력 폴더를 `renders/` 아래로 지정해야 한다.

## 정리 검증 기록

- 이동 파일 103개와 루트에 유지한 현행 모델까지 총 104개의 SHA-256이 정리 전과 일치한다.
- Python 스크립트 85개의 구문을 검사했고, 관련 Markdown의 로컬 파일 링크 136개가 존재한다.
- 실제 Blender 장면에서 렌더·저장 연산을 대체해 주요 렌더 스크립트 3개의 출력 폴더,
  `RENDER_DIR` 지정과 배치 필터 동작을 검사했다. 실제 재렌더나 모델 저장은 실행하지 않았다.
- 과거 모델을 이동하기 전 Blender 이미지 경로를 검사했다. 미패킹 이미지에 상대 경로를
  사용하는 모델은 없었다. 기존 텍스처 폴더와 현행 모델·웹 파일의 위치는 유지했다.
- 루트에 이미지·PDF가 남지 않았고, 이전 렌더 폴더 두 곳은 파일 이동 후 빈 폴더만 제거했다.

## 새 파일을 추가할 때

원본은 `references/`, 생성한 이미지는 `renders/`, 분석 중간물은 `assets/analysis/`에 둔다.
수정 전 모델은 `models/backups/`에 설명 가능한 이름으로 보관한다.
파일을 이동하면 생산·소비 스크립트, 이 안내와 [파일 목록](asset-inventory.md)의 경로를 함께 수정한다.
목록은 2026-10-20 정리 시점의 스냅샷이며 자동 갱신되지 않는다.

