# 자료 파일 목록과 이동표

2026-10-20 정리 시점의 목록이다. [분류 기준과 사용법](asset-guide.md)을 먼저 읽는다.
총 104개 자료 중 103개를 이동했고, 작업용 모델 1개는 루트에 유지했다.
파일명·바이트 내용은 변경하지 않았으며 이동 전후 SHA-256 일치를 검사했다.
수정 시각은 정리 전 파일의 로컬 시각(Asia/Seoul)이다. 최신성 판단은 안내 문서의 상태 설명을 우선한다.
`*.blend1`, 텍스처·코드·웹 산출물은 목록에서 제외했다.

## 정리 후 추가 — Q4 안방 발코니·대피실 보수

아래 5개는 최초 104개 자료 목록 이후 추가됐다. 현행 원본 Blender 파일과 웹 데이터도 Q4 보수로
변경됐으므로 아래 과거 이동표의 원본 크기·수정 시각을 현행 파일 값으로 해석하지 않는다.
새 생성·검증 스크립트는 `scripts/fix_master_balcony.py`, `render_master_balcony.py`,
`verify_master_balcony.py`다. 근거와 가정은 [품질 보고서](quality-v2-report.md)의 Q4 항목을 본다.

| 현재 파일 | 바이트 | 용도 |
| --- | ---: | --- |
| [발코니 보수 전 원본](../models/backups/apt_84a_photoreal_tour_before_master_balcony.blend) | 8902932 | 보수 이전 전체 모델 백업 |
| [미닫이 교정 전 원본](../models/backups/apt_84a_photoreal_tour_before_sliding_correction.blend) | 8627184 | 초기 여닫이 해석이 남은 보수본. 현행 원본으로 사용하지 않음 |
| [13번 평면 검토](../renders/review/render_13_master_balcony_plan.png) | 1073835 | Workbench 위쪽 시점: 방 경계·미닫이문 확인 |
| [14번 발코니 POV](../renders/review/render_14_master_balcony_pov.png) | 1031669 | 안방에서 열린 미닫이문·외창 확인 |
| [15번 대피실 POV](../renders/review/render_15_refuge_pov.png) | 976751 | 발코니에서 대피실 문·창·바닥 확인 |

## 정리 후 추가 — Q5 알파룸 보수

최초 목록 이후 백업과 확인 이미지 3개를 추가했다. 현재 모델·웹 데이터도 함께 갱신했다.
생성/검증은 `scripts/fix_alpha_room.py`, `verify_alpha_room.py`, `render_alpha_room.py`를 사용한다.

| 현재 파일 | 용도 |
| --- | --- |
| [알파룸 보수 전 원본](../models/backups/apt_84a_photoreal_tour_before_alpha_cleanup.blend) | 벽·가구 변경 전 전체 모델. 제거한 책상·의자 복원 가능 |
| [16번 평면 검토](../renders/review/render_16_alpha_plan.png) | 복원한 벽·출입구와 빈 알파룸. 식탁 러그 침범 수정 후 식탁까지 넓혀 재촬영 |
| [17번 실내 POV](../renders/review/render_17_alpha_pov.png) | 벽면·실외기실 문 확인. 검토용 임시 보조광 사용 |

## 정리 후 추가 — Q6 실외기실 보수
Q6 실외기실 보수에서 아래 자료 3개를 추가했다. 현행 모델·웹 데이터도 Q6 상태다.

| 현재 파일 | 용도 |
| --- | --- |
| [실외기실 보수 전 원본](../models/backups/apt_84a_photoreal_tour_before_utility_cleanup.blend) | Q5 및 식탁 러그 교정까지 반영된 복원용 모델 |
| [18번 실외기실 평면](../renders/review/render_18_utility_plan.png) | 방 경계·바닥·문·실외기 배치 확인 |
| [19번 실외기실 POV](../renders/review/render_19_utility_pov.png) | 벽면과 북쪽 루버, 실외기 확인. 검토용 임시 보조광 사용 |

## 정리 후 추가 — Q7 현관 디테일
Q7 현관 보강에서 참고 JPG 8장·백업 1개·렌더 4개를 추가했다. 사진 출처/용도는
[VR 이미지 안내](../references/modelhouse/vr84a/README.md)에 기록했다.

| 현재 파일 | 용도 |
| --- | --- |
| [017_f](../references/modelhouse/vr84a/017_f.jpg), [017_r](../references/modelhouse/vr84a/017_r.jpg), [017_b](../references/modelhouse/vr84a/017_b.jpg), [017_l](../references/modelhouse/vr84a/017_l.jpg) | 공식 VR 현관: 중문·면재·신발장 참고 |
| [018_f](../references/modelhouse/vr84a/018_f.jpg), [018_r](../references/modelhouse/vr84a/018_r.jpg), [018_l](../references/modelhouse/vr84a/018_l.jpg), [018_b](../references/modelhouse/vr84a/018_b.jpg) | 공식 VR 현관창고: 선반·기둥·양개문 참고 |
| [현관 보강 전 원본](../models/backups/apt_84a_photoreal_tour_before_foyer_detail.blend) | Q6까지 반영된 복원용 모델 |
| [20번 평면](../renders/review/render_20_foyer_plan.png) | 현관·팬트리·중문 열린 배치 |
| [21번 중문 디테일](../renders/review/render_21_middle_door_detail.png) | 임시 닫힘 촬영. 실제 투어는 열린 상태 |
| [22번 현관 팬트리](../renders/review/render_22_entry_pantry.png) | 열린 양개문·ㄷ자 선반·금속 기둥 |
| [23번 현관 열린 모습](../renders/review/render_23_foyer_open.png) | 실제 투어의 열린 중문·현관·신발장 |

## 정리 후 추가 — Q8 거실 욕실 디테일

공식 VR 015/016 JPG 8장·백업 1개·확인 렌더 4개를 추가했다.
사진별 용도와 출처는 [VR 안내](../references/modelhouse/vr84a/README.md)의 욕실 조사 항목을 본다.

| 현재 파일 | 용도 |
| --- | --- |
| `references/modelhouse/vr84a/015_{f,r,b,l}.jpg` | 공식 원본: 건식 세면대·욕실 입구·복도 |
| `references/modelhouse/vr84a/016_{f,r,b,l}.jpg` | 공식 원본: 타일·샤워·변기·거울장. 016_f의 타일 부분을 UV로 사용 |
| [욕실 보강 전 원본](../models/backups/apt_84a_photoreal_tour_before_common_bath_detail.blend) | Q7 및 웹 시작점 교정 후, Q8 이전 전체 모델 |
| [24번 평면](../renders/review/render_24_common_bath_plan.png) | 실제 샤프트·변기·열린 샤워문·건식 공간 배치 |
| [25번 세면대](../renders/review/render_25_dry_vanity_detail.png) | 파인 볼·수전·양개 하부장·직사각 거울 |
| [26번 변기](../renders/review/render_26_common_toilet_detail.png) | 곡면 도기·물탱크·거울장·위생 샤워기·휴지걸이 |
| [27번 샤워실](../renders/review/render_27_shower_detail.png) | 유리·프레임·레인/핸드 샤워·호스·선반·배수구 |
| [웹 욕실 갤러리](../renders/review/web_common_bath_gallery.jpg) | 실제 브라우저에서 새 욕실 이미지와 설명 표시 확인 |

## 웹 안내 아이콘 음영 교정 증빙

- [수정 전](../renders/review/web_hotspot_ao_before.jpg): 실제 욕실 모델에서 안내 아이콘의 투명 영역에 사각 AO가 생김.
- [수정 후](../renders/review/web_hotspot_ao_after.jpg): 같은 카메라에서 사각 음영 제거, 아이콘과 벽 유지.
  개발용 고정 카메라 검사 화면의 브라우저 캡처이며 Blender 렌더가 아니다.

## 정리 후 추가 — Q9 우드 바닥

| 현재 파일 | 용도 |
| --- | --- |
| [바닥 보강 전 모델](../models/backups/apt_84a_photoreal_tour_before_flooring.blend) | 제거한 방별 우드 덧판 5개와 이전 재질을 복원할 수 있는 전체 백업 |
| [28번 복도](../renders/review/render_28_oak_corridor.png) | 복도와 방문 경계, 밝은 오크 결/연결 확인 |
| [29번 거실](../renders/review/render_29_oak_living.png) | 거실·복도 공통 마감과 가까운 나뭇결 확인 |
| [웹 바닥 수정 전](../renders/review/web_floor_before.jpg) | 기존 바닥의 고정 카메라 브라우저 캡처 |
| [웹 바닥 수정 후](../renders/review/web_floor_after.jpg) | 같은 카메라에서 새 바닥 비교 |

`assets/textures_export/q9_oak_albedo.jpg`, `q9_oak_normal.jpg`, `q9_oak_roughness.jpg`는
기존 `assets/textures/laminate_floor_02`에서 생성한 2K 파생 재질이다. 제조사 원본이 아니다.
원본 텍스처는 보존한다. 생성/검사는 `scripts/improve_flooring.py`와 `verify_flooring.py`다.

## 루트 — 현행 작업 모델

추가 검증 이미지: [web_start_view.jpg](../renders/review/web_start_view.jpg).
시작점을 현관문 안쪽 x12.33/y7.40으로 교정한 뒤 실제 브라우저에서 캡처했다.
처음 접속·초기화 버튼·R 키의 방향 확인용이며 Blender 렌더가 아니다.

| 파일 (현재 경로 링크) | 이전 상대 경로 | 바이트 | 원래 수정 시각 |
| --- | --- | ---: | --- |
| [apt_84a_photoreal_tour.blend](<../apt_84a_photoreal_tour.blend>) | `apt_84a_photoreal_tour.blend` | 8902932 | 2026-10-20 09:37:24 |

## assets/analysis

| 파일 (현재 경로 링크) | 이전 상대 경로 | 바이트 | 원래 수정 시각 |
| --- | --- | ---: | --- |
| [blueprint_grid.png](<../assets/analysis/blueprint_grid.png>) | `blueprint_grid.png` | 26054 | 2026-10-18 22:15:03 |
| [contours_overlay.png](<../assets/analysis/contours_overlay.png>) | `contours_overlay.png` | 22956 | 2026-10-16 14:00:24 |
| [polys.json](<../assets/analysis/polys.json>) | `polys.json` | 3158 | 2026-10-16 14:01:18 |
| [wall_mask_crop.png](<../assets/analysis/wall_mask_crop.png>) | `wall_mask_crop.png` | 924 | 2026-10-18 22:17:53 |
| [wall_mask.png](<../assets/analysis/wall_mask.png>) | `wall_mask.png` | 2106 | 2026-10-16 13:59:17 |

## models/archive

| 파일 (현재 경로 링크) | 이전 상대 경로 | 바이트 | 원래 수정 시각 |
| --- | --- | ---: | --- |
| [apt_84a_furnished_tour.blend](<../models/archive/apt_84a_furnished_tour.blend>) | `apt_84a_furnished_tour.blend` | 1924620 | 2026-10-16 14:07:44 |
| [apt_84a.blend](<../models/archive/apt_84a.blend>) | `apt_84a.blend` | 1291580 | 2026-10-16 14:04:33 |
| [apt_v00_initial.blend](<../models/archive/apt_v00_initial.blend>) | `apt_v00_initial.blend` | 934724 | 2026-10-16 12:14:16 |
| [apt_v01_structure.blend](<../models/archive/apt_v01_structure.blend>) | `apt_v01_structure.blend` | 1203180 | 2026-10-16 12:39:04 |

## models/backups

| 파일 (현재 경로 링크) | 이전 상대 경로 | 바이트 | 원래 수정 시각 |
| --- | --- | ---: | --- |
| [apt_84a_photoreal_tour_before_bay_reorder.blend](<../models/backups/apt_84a_photoreal_tour_before_bay_reorder.blend>) | `apt_84a_photoreal_tour_before_bay_reorder.blend` | 8690612 | 2026-10-19 21:54:49 |
| [apt_84a_photoreal_tour_before_quality_v2.blend](<../models/backups/apt_84a_photoreal_tour_before_quality_v2.blend>) | `apt_84a_photoreal_tour_before_quality_v2.blend` | 5544517 | 2026-10-18 23:38:23 |

## references/drawings/crops

| 파일 (현재 경로 링크) | 이전 상대 경로 | 바이트 | 원래 수정 시각 |
| --- | --- | ---: | --- |
| [cad_entry_detail_flipped.png](<../references/drawings/crops/cad_entry_detail_flipped.png>) | `cad_entry_detail_flipped.png` | 66742 | 2026-10-18 22:13:23 |
| [cad_entry_detail.png](<../references/drawings/crops/cad_entry_detail.png>) | `cad_entry_detail.png` | 66362 | 2026-10-18 22:12:51 |
| [crop_cad_entry_foyer.png](<../references/drawings/crops/crop_cad_entry_foyer.png>) | `crop_cad_entry_foyer.png` | 138346 | 2026-10-18 18:16:43 |
| [crop_cad_kitchen_full.png](<../references/drawings/crops/crop_cad_kitchen_full.png>) | `crop_cad_kitchen_full.png` | 72590 | 2026-10-17 23:09:36 |
| [crop_cad_kitchen.png](<../references/drawings/crops/crop_cad_kitchen.png>) | `crop_cad_kitchen.png` | 67287 | 2026-10-17 23:09:02 |
| [dim_left_74.png](<../references/drawings/crops/dim_left_74.png>) | `dim_left_74.png` | 28310 | 2026-10-16 12:02:53 |
| [dim_top_74.png](<../references/drawings/crops/dim_top_74.png>) | `dim_top_74.png` | 10664 | 2026-10-16 12:02:53 |
| [left_unit_74.png](<../references/drawings/crops/left_unit_74.png>) | `left_unit_74.png` | 125778 | 2026-10-16 13:57:52 |
| [top_dim_context.png](<../references/drawings/crops/top_dim_context.png>) | `top_dim_context.png` | 35419 | 2026-10-16 13:58:52 |
| [unit_crop_74_flipped.png](<../references/drawings/crops/unit_crop_74_flipped.png>) | `unit_crop_74_flipped.png` | 170381 | 2026-10-16 13:57:27 |
| [unit_crop_74.png](<../references/drawings/crops/unit_crop_74.png>) | `unit_crop_74.png` | 169558 | 2026-10-16 12:02:53 |

## references/drawings/original

| 파일 (현재 경로 링크) | 이전 상대 경로 | 바이트 | 원래 수정 시각 |
| --- | --- | ---: | --- |
| [정보공개 파일(A76-2BL_도면)_1.pdf](<../references/drawings/original/정보공개 파일(A76-2BL_도면)_1.pdf>) | `정보공개 파일(A76-2BL_도면)_1.pdf` | 16879768 | 2026-10-16 11:52:40 |

## references/drawings/pages

| 파일 (현재 경로 링크) | 이전 상대 경로 | 바이트 | 원래 수정 시각 |
| --- | --- | ---: | --- |
| [page_1.png](<../references/drawings/pages/page_1.png>) | `page_1.png` | 516955 | 2026-10-16 11:58:22 |
| [page_17.png](<../references/drawings/pages/page_17.png>) | `page_17.png` | 367643 | 2026-10-16 11:57:17 |
| [page_18.png](<../references/drawings/pages/page_18.png>) | `page_18.png` | 386555 | 2026-10-16 11:57:17 |
| [page_2.png](<../references/drawings/pages/page_2.png>) | `page_2.png` | 601883 | 2026-10-16 11:58:23 |
| [page_3.png](<../references/drawings/pages/page_3.png>) | `page_3.png` | 454338 | 2026-10-16 11:57:16 |
| [page_32.png](<../references/drawings/pages/page_32.png>) | `page_32.png` | 452601 | 2026-10-16 11:57:57 |
| [page_4.png](<../references/drawings/pages/page_4.png>) | `page_4.png` | 472481 | 2026-10-16 11:57:17 |
| [page_46.png](<../references/drawings/pages/page_46.png>) | `page_46.png` | 370785 | 2026-10-16 11:57:58 |
| [page_60.png](<../references/drawings/pages/page_60.png>) | `page_60.png` | 320959 | 2026-10-16 11:57:58 |
| [page_74.png](<../references/drawings/pages/page_74.png>) | `page_74.png` | 307337 | 2026-10-16 11:57:58 |

## references/layout/crops

| 파일 (현재 경로 링크) | 이전 상대 경로 | 바이트 | 원래 수정 시각 |
| --- | --- | ---: | --- |
| [blueprint_bath1_detail.png](<../references/layout/crops/blueprint_bath1_detail.png>) | `blueprint_bath1_detail.png` | 9848 | 2026-10-18 23:30:16 |
| [crop_84a_kitchen_dining.png](<../references/layout/crops/crop_84a_kitchen_dining.png>) | `crop_84a_kitchen_dining.png` | 139449 | 2026-10-17 22:25:12 |
| [crop_center_zone.png](<../references/layout/crops/crop_center_zone.png>) | `crop_center_zone.png` | 37111 | 2026-10-17 22:26:30 |
| [crop_kitchen_context.png](<../references/layout/crops/crop_kitchen_context.png>) | `crop_kitchen_context.png` | 17556 | 2026-10-17 22:24:19 |
| [crop_kitchen_top.png](<../references/layout/crops/crop_kitchen_top.png>) | `crop_kitchen_top.png` | 21930 | 2026-10-17 22:24:43 |
| [crop_ref_alpha.png](<../references/layout/crops/crop_ref_alpha.png>) | `crop_ref_alpha.png` | 15512 | 2026-10-17 09:24:53 |
| [crop_ref_entry_blueprint.png](<../references/layout/crops/crop_ref_entry_blueprint.png>) | `crop_ref_entry_blueprint.png` | 24906 | 2026-10-18 22:10:35 |
| [crop_ref_kitchen.png](<../references/layout/crops/crop_ref_kitchen.png>) | `crop_ref_kitchen.png` | 80568 | 2026-10-16 14:34:57 |
| [crop_ref_living.png](<../references/layout/crops/crop_ref_living.png>) | `crop_ref_living.png` | 82660 | 2026-10-16 14:34:57 |
| [crop_ref_master.png](<../references/layout/crops/crop_ref_master.png>) | `crop_ref_master.png` | 174226 | 2026-10-16 14:34:57 |
| [crop_ref_right.png](<../references/layout/crops/crop_ref_right.png>) | `crop_ref_right.png` | 204757 | 2026-10-16 14:34:57 |

## references/layout/original

| 파일 (현재 경로 링크) | 이전 상대 경로 | 바이트 | 원래 수정 시각 |
| --- | --- | ---: | --- |
| [84A.jpg](<../references/layout/original/84A.jpg>) | `84A.jpg` | 74511 | 2026-10-16 13:55:41 |
| [unit_84a.png](<../references/layout/original/unit_84a.png>) | `unit_84a.png` | 89134 | 2026-10-16 13:55:07 |

## references/materials

| 파일 (현재 경로 링크) | 이전 상대 경로 | 바이트 | 원래 수정 시각 |
| --- | --- | ---: | --- |
| [prugio_84a_finishes.jpg](<../references/materials/prugio_84a_finishes.jpg>) | `prugio_84a_finishes.jpg` | 1129061 | 2026-10-16 14:42:44 |

## references/modelhouse/crops

| 파일 (현재 경로 링크) | 이전 상대 경로 | 바이트 | 원래 수정 시각 |
| --- | --- | ---: | --- |
| [display_03_part_1.jpg](<../references/modelhouse/crops/display_03_part_1.jpg>) | `display_03_part_1.jpg` | 92831 | 2026-10-17 23:07:06 |
| [display_03_part_2.jpg](<../references/modelhouse/crops/display_03_part_2.jpg>) | `display_03_part_2.jpg` | 103711 | 2026-10-17 23:07:06 |
| [display_03_part_3.jpg](<../references/modelhouse/crops/display_03_part_3.jpg>) | `display_03_part_3.jpg` | 111514 | 2026-10-17 23:07:06 |
| [display84a_07_part_1.jpg](<../references/modelhouse/crops/display84a_07_part_1.jpg>) | `display84a_07_part_1.jpg` | 109555 | 2026-10-18 23:28:19 |
| [display84a_07_part_2.jpg](<../references/modelhouse/crops/display84a_07_part_2.jpg>) | `display84a_07_part_2.jpg` | 125397 | 2026-10-18 23:28:19 |
| [display84a_07_part_3.jpg](<../references/modelhouse/crops/display84a_07_part_3.jpg>) | `display84a_07_part_3.jpg` | 126566 | 2026-10-18 23:28:19 |
| [display84a_07_part_4.jpg](<../references/modelhouse/crops/display84a_07_part_4.jpg>) | `display84a_07_part_4.jpg` | 128861 | 2026-10-18 23:28:19 |

## references/modelhouse/original

| 파일 (현재 경로 링크) | 이전 상대 경로 | 바이트 | 원래 수정 시각 |
| --- | --- | ---: | --- |
| [display84a_01.jpg](<../references/modelhouse/original/display84a_01.jpg>) | `display84a_01.jpg` | 1027646 | 2026-10-16 14:44:05 |
| [display84a_03.jpg](<../references/modelhouse/original/display84a_03.jpg>) | `display84a_03.jpg` | 1292228 | 2026-10-16 14:44:05 |
| [display84a_05.jpg](<../references/modelhouse/original/display84a_05.jpg>) | `display84a_05.jpg` | 913049 | 2026-10-16 14:44:05 |
| [display84a_06.jpg](<../references/modelhouse/original/display84a_06.jpg>) | `display84a_06.jpg` | 1359709 | 2026-10-16 14:44:47 |
| [display84a_07.jpg](<../references/modelhouse/original/display84a_07.jpg>) | `display84a_07.jpg` | 2149118 | 2026-10-16 14:44:48 |
| [display84a_08.jpg](<../references/modelhouse/original/display84a_08.jpg>) | `display84a_08.jpg` | 1721528 | 2026-10-16 14:44:48 |

## renders/archive/before-quality-v2

| 파일 (현재 경로 링크) | 이전 상대 경로 | 바이트 | 원래 수정 시각 |
| --- | --- | ---: | --- |
| [render_1_isometric_topdown.png](<../renders/archive/before-quality-v2/render_1_isometric_topdown.png>) | `renders_prev/render_1_isometric_topdown.png` | 2026426 | 2026-10-16 18:38:39 |
| [render_2_living_room_pov.png](<../renders/archive/before-quality-v2/render_2_living_room_pov.png>) | `renders_prev/render_2_living_room_pov.png` | 2008498 | 2026-10-16 17:26:03 |
| [render_3_kitchen_dining_pov.png](<../renders/archive/before-quality-v2/render_3_kitchen_dining_pov.png>) | `renders_prev/render_3_kitchen_dining_pov.png` | 2133408 | 2026-10-16 18:39:37 |
| [render_4_master_bedroom_pov.png](<../renders/archive/before-quality-v2/render_4_master_bedroom_pov.png>) | `renders_prev/render_4_master_bedroom_pov.png` | 1942840 | 2026-10-16 17:31:08 |
| [render_5_foyer_corridor_pov.png](<../renders/archive/before-quality-v2/render_5_foyer_corridor_pov.png>) | `renders_prev/render_5_foyer_corridor_pov.png` | 1984480 | 2026-10-16 17:37:30 |
| [render_6_kitchen_reverse.png](<../renders/archive/before-quality-v2/render_6_kitchen_reverse.png>) | `renders_prev/render_6_kitchen_reverse.png` | 1967813 | 2026-10-16 18:41:51 |
| [render_7_dress_pov.png](<../renders/archive/before-quality-v2/render_7_dress_pov.png>) | `renders_prev/render_7_dress_pov.png` | 2057459 | 2026-10-16 17:42:05 |
| [render_8_bath_pov.png](<../renders/archive/before-quality-v2/render_8_bath_pov.png>) | `renders_prev/render_8_bath_pov.png` | 1912336 | 2026-10-16 17:45:33 |

## renders/archive/early-tour

| 파일 (현재 경로 링크) | 이전 상대 경로 | 바이트 | 원래 수정 시각 |
| --- | --- | ---: | --- |
| [tour_1_entrance_foyer.png](<../renders/archive/early-tour/tour_1_entrance_foyer.png>) | `tour_1_entrance_foyer.png` | 1085290 | 2026-10-16 14:07:42 |
| [tour_2_living_kitchen.png](<../renders/archive/early-tour/tour_2_living_kitchen.png>) | `tour_2_living_kitchen.png` | 1137798 | 2026-10-16 14:07:42 |
| [tour_3_master_bedroom.png](<../renders/archive/early-tour/tour_3_master_bedroom.png>) | `tour_3_master_bedroom.png` | 1172703 | 2026-10-16 14:07:43 |
| [tour_topdown_furnished.png](<../renders/archive/early-tour/tour_topdown_furnished.png>) | `tour_topdown_furnished.png` | 1149816 | 2026-10-16 14:07:44 |

## renders/comparisons

| 파일 (현재 경로 링크) | 이전 상대 경로 | 바이트 | 원래 수정 시각 |
| --- | --- | ---: | --- |
| [compare_kitchen.jpg](<../renders/comparisons/compare_kitchen.jpg>) | `compare_kitchen.jpg` | 87512 | 2026-10-19 12:41:31 |
| [compare_living.jpg](<../renders/comparisons/compare_living.jpg>) | `compare_living.jpg` | 81571 | 2026-10-19 12:41:31 |
| [compare_master.jpg](<../renders/comparisons/compare_master.jpg>) | `compare_master.jpg` | 66800 | 2026-10-19 12:41:31 |

## renders/presentation

| 파일 (현재 경로 링크) | 이전 상대 경로 | 바이트 | 원래 수정 시각 |
| --- | --- | ---: | --- |
| [render_1_isometric_topdown.png](<../renders/presentation/render_1_isometric_topdown.png>) | `render_1_isometric_topdown.png` | 2260230 | 2026-10-19 21:40:46 |
| [render_10_common_bath_dry_vanity_pov.png](<../renders/presentation/render_10_common_bath_dry_vanity_pov.png>) | `render_10_common_bath_dry_vanity_pov.png` | 1940909 | 2026-10-18 23:38:23 |
| [render_2_living_room_pov.png](<../renders/presentation/render_2_living_room_pov.png>) | `render_2_living_room_pov.png` | 2419593 | 2026-10-19 22:01:37 |
| [render_3_kitchen_dining_pov.png](<../renders/presentation/render_3_kitchen_dining_pov.png>) | `render_3_kitchen_dining_pov.png` | 2333979 | 2026-10-19 22:23:30 |
| [render_4_master_bedroom_pov.png](<../renders/presentation/render_4_master_bedroom_pov.png>) | `render_4_master_bedroom_pov.png` | 2141388 | 2026-10-19 22:38:59 |
| [render_5_foyer_corridor_pov.png](<../renders/presentation/render_5_foyer_corridor_pov.png>) | `render_5_foyer_corridor_pov.png` | 1934590 | 2026-10-18 22:24:29 |
| [render_6_kitchen_reverse.png](<../renders/presentation/render_6_kitchen_reverse.png>) | `render_6_kitchen_reverse.png` | 2300087 | 2026-10-19 16:27:17 |
| [render_7_dress_pov.png](<../renders/presentation/render_7_dress_pov.png>) | `render_7_dress_pov.png` | 2161523 | 2026-10-17 09:45:05 |
| [render_8_bath_pov.png](<../renders/presentation/render_8_bath_pov.png>) | `render_8_bath_pov.png` | 1840284 | 2026-10-17 10:01:09 |
| [render_9_kitchen_prep_pov.png](<../renders/presentation/render_9_kitchen_prep_pov.png>) | `render_9_kitchen_prep_pov.png` | 2018888 | 2026-10-18 12:20:52 |

## renders/previews

| 파일 (현재 경로 링크) | 이전 상대 경로 | 바이트 | 원래 수정 시각 |
| --- | --- | ---: | --- |
| [plan_topdown.png](<../renders/previews/plan_topdown.png>) | `previews_pbr/plan_topdown.png` | 966914 | 2026-10-16 22:19:11 |
| [render_1_isometric_topdown.png](<../renders/previews/render_1_isometric_topdown.png>) | `previews_pbr/render_1_isometric_topdown.png` | 812005 | 2026-10-16 22:37:19 |
| [render_2_living_room_pov.png](<../renders/previews/render_2_living_room_pov.png>) | `previews_pbr/render_2_living_room_pov.png` | 856851 | 2026-10-16 22:37:23 |
| [render_3_kitchen_dining_pov.png](<../renders/previews/render_3_kitchen_dining_pov.png>) | `previews_pbr/render_3_kitchen_dining_pov.png` | 879314 | 2026-10-16 22:29:52 |
| [render_4_master_bedroom_pov.png](<../renders/previews/render_4_master_bedroom_pov.png>) | `previews_pbr/render_4_master_bedroom_pov.png` | 770902 | 2026-10-16 22:29:56 |
| [render_5_foyer_corridor_pov.png](<../renders/previews/render_5_foyer_corridor_pov.png>) | `previews_pbr/render_5_foyer_corridor_pov.png` | 850141 | 2026-10-16 22:30:00 |
| [render_6_kitchen_reverse.png](<../renders/previews/render_6_kitchen_reverse.png>) | `previews_pbr/render_6_kitchen_reverse.png` | 835838 | 2026-10-16 22:30:04 |
| [render_7_dress_pov.png](<../renders/previews/render_7_dress_pov.png>) | `previews_pbr/render_7_dress_pov.png` | 777086 | 2026-10-16 22:30:08 |
| [render_8_bath_pov.png](<../renders/previews/render_8_bath_pov.png>) | `previews_pbr/render_8_bath_pov.png` | 917306 | 2026-10-16 22:30:11 |

## renders/review

### 84A 치수 대조 자료 (2026-10-21)

- `references/drawings/original/84a 평면도.pdf`: 사용자가 지정한 수치가 있는 확장형 평면도 원본, A02-102.
- `assets/analysis/dimensioned_plan_1.png`, `dimensioned_bedrooms.png`: 위 PDF를 회전/확대 추출한 도면 파생본. Blender 렌더가 아니다.
- `assets/analysis/audit_plan_dimensions.py`: 저장된 실제 벽 메시의 대표 치수 읽기 전용 검사.
- `docs/dimension-audit-84a.md`: 도면 표기와 메시 차이, 기준선/깊이 미검증 범위. 현행은 치수 완전 일치 모델이 아니다.

### Q11 침실2 서재 추가 자료 (2026-10-21)

- Q11b: 33·34·35번과 서재 WebP를 장비 추가 상태로 갱신했다.
  `references/furniture/workstation.md`는 장비 출처/가정이며,
  `models/backups/apt_84a_photoreal_tour_before_study_equipment.blend`는 장비 추가 전 복원본이다.
- `references/furniture/erectus/product_136.html`·`product_136.jpg`·`README.md`: 공식 제품 페이지/대표 사진/출처 및 가정 기록.
- `models/backups/apt_84a_photoreal_tour_before_study_room.blend`: 침실2 변경 전 Q10b 복원본.
- `assets/analysis/probe_bed2.py`: 변경 전 창 벽 단차·가구/손잡이 위치를 확인한 Blender 탐색 스크립트.
- `renders/review/render_33_study_pov.png`, `render_34_study_plan.png`, `render_35_study_desks.png`:
  Q11의 벽 마감·동쪽 화이트 책상 두 자리·검정/그레이 의자 확인용 생성 렌더.
- `web/public/gallery/study-room.webp`, `study-desks.webp`와 각 `thumbs/` 파생본:
  위 33·35번을 사용하는 웹 갤러리 '서재'. 생산 목록은 `scripts/optimize_gallery.py`다.

### Q10 유나방 추가 자료 (2026-10-20)

Q10b 교정: 사용자 기본 옵션은 방문 옆 장이다. 기존 30·31번 렌더와 `web_yuna_after.jpg`,
`yuna-room.webp`를 새 배치로 갱신했다. 추가 파일은 다음과 같다.

- `models/backups/apt_84a_photoreal_tour_before_yuna_basic_correction.blend`: 옵션 교정 전 Q10 복원본.
- `renders/review/render_32_yuna_basic_builtin.png`: 창 쪽에서 방문 옆 기본장을 보는 최종 확인 렌더.
- `web/public/gallery/yuna-builtin.webp` 및 `thumbs/yuna-builtin.webp`: 위 32번의 웹용 파생본.
  `yuna-room`과 함께 갤러리 아이방 탭에서 볼 수 있다.

- 공식 원본: `references/modelhouse/vr84a/013_f.jpg`, `013_r.jpg`, `013_b.jpg`, `013_l.jpg`.
  출처와 해석은 해당 폴더 README. Blender 생성 이미지가 아니다.
- 변경 전 복원본: `models/backups/apt_84a_photoreal_tour_before_yuna_room.blend`.
  Q9까지의 현행 모델을 보존하며, 초기 전체 모델로 되돌리는 용도가 아니다.
- 현행 확인 렌더: `renders/review/render_30_yuna_pov.png`, `render_31_yuna_plan.png`.
  CAD 외곽 유지·가구 재배치·투과 유리·아이방 마감을 확인한다. 가구 치수는 제안값이다.
- 실제 웹 캡처: `renders/review/web_yuna_after.jpg`.
- 파생 웹 갤러리: `web/public/gallery/yuna-room.webp`와 `thumbs/yuna-room.webp`.
  생산 스크립트는 `scripts/optimize_gallery.py`, 소비 목록은 `web/src/gallery-data.ts`다.

| 파일 (현재 경로 링크) | 이전 상대 경로 | 바이트 | 원래 수정 시각 |
| --- | --- | ---: | --- |
| [render_11_fridge_pov.png](<../renders/review/render_11_fridge_pov.png>) | `render_11_fridge_pov.png` | 1482900 | 2026-10-20 09:41:35 |
| [render_12_sink_door_pov.png](<../renders/review/render_12_sink_door_pov.png>) | `render_12_sink_door_pov.png` | 1450808 | 2026-10-20 09:45:07 |

## Q14 거실 소파 교체 자료 (2026-10-21)

| 경로 | 목적·상태 |
| --- | --- |
| `references/furniture/seatandmore-brest/` | 공식 제품 페이지 사본·대표/상세 사진·출처/가정 README, 렌더 아님 |
| `models/backups/apt_84a_photoreal_tour_before_brest_sofa.blend` | 교체 전 Q13 포함 복원본 |
| `renders/review/render_38_brest_sofa.png` | 새 브레스트 소파 확인 렌더, 웹 갤러리 |
| `renders/review/render_39_brest_living_plan.png` | 닫힌 소파/기존 거실 가구의 정지 배치 평면 |
| `renders/review/` 29/36번 | 새 소파가 반영된 거실 및 전체 평면으로 갱신 |

## Q13 서재 책장 추가 자료 (2026-10-21)

| 경로 | 목적·상태 |
| --- | --- |
| `references/furniture/casamia-poeta/poeta-800.jpg` 및 `README.md` | 상품 참고 사진/치수 출처·추정 구분, 렌더 아님 |
| `models/backups/apt_84a_photoreal_tour_before_study_bookcases.blend` | Q13 전 현행 치수 교정본 복원용 |
| `renders/review/render_37_study_bookcases.png` | 검정·우드색 800+600 6단 책장 확인 렌더, 웹 서재 갤러리 |
| `renders/review/` 33/34/35/36번 | Q13 배치가 반영된 서재 및 전체 확인 렌더로 갱신 |

## Q12 치수 교정 추가 자료 (2026-10-21)

| 경로 | 목적·상태 |
| --- | --- |
| `references/drawings/original/84a 평면도.pdf` | A02-102 확장형 치수 원본, Q12 기준 |
| `assets/analysis/dimensioned_plan_1.png` 및 `dimension_*.png` | 원본 PDF에서 추출·확대한 판독용 파생 이미지, 렌더 아님 |
| `assets/analysis/calibration_objects.json` | 교정 전 Q11b 객체 경계 기록, 현행 치수 아님 |
| `assets/analysis/q12_dimensions.json` | Q12 축·실내 범위·창 치수 결과, 해석 한계는 Q12 기록 참조 |
| `models/backups/apt_84a_photoreal_tour_before_dimensions.blend` | 치수 교정 전 복원본, 현행 원본 아님 |
| `renders/review/render_36_dimensioned_plan.png` | Q12 전체 형상 확인용 평면 렌더, 웹 갤러리 전체 뷰 |
| `scripts/render_calibrated_gallery.py` 출력 | 기존 갤러리 입력 및 18/19/31/34번을 Q12로 갱신, 기존 파일 경로 유지 |
| `docs/dimension-correction-q12.md` | 직접 표기 치수·추정·검증·미해결 높이의 현행 기록 |
| `docs/dimension-audit-84a.md` | 교정 전 조사 이력, 현행 치수로 사용하지 않음 |

## renders/verification/crops

| 파일 (현재 경로 링크) | 이전 상대 경로 | 바이트 | 원래 수정 시각 |
| --- | --- | ---: | --- |
| [crop_render_bath1_after.png](<../renders/verification/crops/crop_render_bath1_after.png>) | `crop_render_bath1_after.png` | 68155 | 2026-10-18 23:36:20 |
| [crop_render_foyer_after.png](<../renders/verification/crops/crop_render_foyer_after.png>) | `crop_render_foyer_after.png` | 68733 | 2026-10-18 22:22:09 |
| [crop_render_foyer_zoom.png](<../renders/verification/crops/crop_render_foyer_zoom.png>) | `crop_render_foyer_zoom.png` | 176274 | 2026-10-18 22:11:52 |

## renders/verification/structure

| 파일 (현재 경로 링크) | 이전 상대 경로 | 바이트 | 원래 수정 시각 |
| --- | --- | ---: | --- |
| [exact_structure_preview.png](<../renders/verification/structure/exact_structure_preview.png>) | `exact_structure_preview.png` | 1034362 | 2026-10-16 14:01:46 |
| [verification_alpha_pov.png](<../renders/verification/structure/verification_alpha_pov.png>) | `verification_alpha_pov.png` | 1081843 | 2026-10-16 12:39:04 |
| [verification_living_pov.png](<../renders/verification/structure/verification_living_pov.png>) | `verification_living_pov.png` | 1071293 | 2026-10-16 12:39:04 |
| [verification_topdown.png](<../renders/verification/structure/verification_topdown.png>) | `verification_topdown.png` | 1025130 | 2026-10-16 12:39:03 |


# Q15 추가 자료

| 경로 | 목적 / 상태 |
|---|---|
| `models/backups/apt_84a_photoreal_tour_before_living_finish.blend` | Q14 상태 복원용, 현행 원본 아님 |
| `renders/review/render_40_living_window.png` | Q15 창틀·양끝 커튼·외부 철제 난간 확인 |
| `renders/review/render_41_living_artwall.png` | Q15 벽 끝·문 상부 마감과 열린 안방 출입구 확인 |
| `assets/textures_export/q2_landscape.jpg` | 픽셀 복구 및 UV 방향 교정한 생성 배경, 실제 현장 조망 아님 |
| `assets/analysis/q15_living_objects.json` | 수정 전 거실 객체 범위 조사, 현행 배치로 해석하지 않음 |
| `scripts/detail_living_finish.py`, `scripts/verify_living_finish.py`, `scripts/render_living_finish.py` | 현행 거실 마감·검사·렌더 |


# Q16 주방 복구 자료

| 경로 | 목적 / 상태 |
|---|---|
| `models/backups/apt_84a_photoreal_tour_before_kitchen_finish.blend` | Q15 복원용 백업, 현행 원본 아님 |
| `assets/analysis/q16_kitchen_before.json`, `probe_kitchen_q16.py` | 수정 전 주방 부품 범위와 재현 렌더 스크립트 |
| `renders/review/q16_kitchen_before.png` | 수정 전 생성 렌더, 모델하우스 사진 아님 |
| `renders/review/render_42_kitchen_sink.png` | Q16 싱크대·식기세척기·수전 정렬 확인 렌더 |
| `renders/review/render_43_kitchen_corner.png` | Q16 싱크-오븐-반도형 조리대 연결, 웹 주방 상세 원본 |
| `renders/review/render_44_kitchen_plan.png` | Q16 주방 ㄷ자 평면과 통로 확인 |
| `renders/review/render_45_kitchen_dining.png` | 식당에서 본 Q16 주방, 웹 주방 전체 원본 |
| `assets/textures_export/q16_stone_diff.jpg` | 밝게 보정한 주방 전용 웹 석재 표현, 실제 제조사 스캔 아님 |
| `scripts/detail_kitchen_finish.py`, `verify_kitchen_finish.py`, `render_kitchen_finish.py` | 현행 모델에만 주방 복구·회귀 검사·확인 렌더 |

기존 12/36번 및 발표용 주방 3/9번 경로도 Q16으로 갱신했다. 신규 도면·사진 원본은 추가하지 않았다.


# Q17 거실 TV장 및 스탠드형 TV 교체 자료 (2026-10-22)

| 경로 | 목적 / 상태 |
|---|---|
| `references/furniture/living-tv-stand/model.glb` | 사용자 지정 거실 TV장 원본 GLB (2000×450×513mm) |
| `references/furniture/living-tv/tv.glb` | 사용자 지정 거실 스탠드형 TV 원본 GLB (1225×270×765mm) |
| `models/backups/apt_84a_photoreal_tour_before_tv_stand.blend` | Q16 상태 복원용 백업, 현행 원본 아님 |
| `scripts/replace_living_tv_stand.py`, `scripts/verify_living_tv_stand.py` | 거실 TV장 및 스탠드 TV 교체·치수·정렬·방향 검증 스크립트 |
| `renders/review/` 41/39/40/38/29/36번 | Q17 TV장 및 스탠드 TV가 반영된 거실 및 전체 확인 렌더로 갱신 |


# Q18 냉장고장 LG 광파오븐 추가 자료 (2026-10-23)

| 경로 | 목적 / 상태 |
|---|---|
| `references/furniture/lg-lightwave-oven/mlj32ewso.png`, `README.md` | LG 디오스 오브제컬렉션 광파오븐 `MLJ32EWSO` 정면 참고 이미지 및 공식 규격(527×480×394mm)/출처 |
| `assets/textures_export/q18_lg_lightwave_front.jpg` | `mlj32ewso.png`에서 추출한 전면 도어 텍스처 파생본 |
| `models/backups/apt_84a_photoreal_tour_before_lightwave_oven.blend` | Q17 상태 복원용 백업, 현행 원본 아님 |
| `scripts/add_lg_lightwave_oven.py`, `scripts/verify_lg_lightwave_oven.py` | 밥솥장 상부 오픈칸 추가 및 광파오븐 모델링·검증 스크립트 |
| `renders/review/render_11_fridge_pov.png`, `render_12_sink_door_pov.png` | 광파오븐이 반영된 냉장고장 확인 렌더 |


# Q19 거실 사운드바 및 무선 서브우퍼 추가 자료 (2026-10-23)

| 경로 | 목적 / 상태 |
|---|---|
| `references/furniture/living-soundbar/soundbar_angled.png`, `soundbar_front.png`, `README.md` | 삼성 2.1채널 사운드바 및 무선 서브우퍼 참고 이미지·공식 규격(858.8×75×59mm / 184×295×343mm) |
| `models/backups/apt_84a_photoreal_tour_before_soundbar.blend` | Q18 상태 복원용 백업, 현행 원본 아님 |
| `scripts/add_living_soundbar.py`, `scripts/verify_living_soundbar.py` | 거실 사운드바·서브우퍼 모델링 및 치수·배치·간섭 검증 스크립트 |
| `renders/review/render_41_living_artwall.png`, `render_38_brest_sofa.png`, `render_39_brest_living_plan.png` | 사운드바와 서브우퍼가 반영된 거실 확인 렌더 |


# Q20 다용도실 가벽 틈새 및 터닝도어 교체 자료 (2026-10-23)

| 경로 | 목적 / 상태 |
|---|---|
| `models/backups/apt_84a_photoreal_tour_before_turning_door.blend` | Q19 상태 복원용 백업, 현행 원본 아님 |
| `scripts/fix_utility_turning_door.py`, `scripts/verify_utility_turning_door.py` | 냉장고장-다용도실 가벽 틈새 교정, 상부 인방벽 및 유리 터닝도어 교체·검증 스크립트 |
| `renders/review/render_12_sink_door_pov.png`, `render_11_fridge_pov.png` | 가벽 밀착 및 터닝도어가 반영된 다용도실 입구·냉장고장 확인 렌더 |



# Q21 다용도실 LG 워시타워 및 타일 바닥 자료 (2026-10-23)

| 경로 | 목적 / 상태 |
|---|---|
| `references/furniture/lg-washtower/wl21egzu_front.png`, `modelhouse_utility_washtower.png`, `README.md` | 워시타워 정면 제품 사진, 모델하우스 다용도실 VR 캡처, 공식 규격(700×1890×830mm)·가정 |
| `models/backups/apt_84a_photoreal_tour_before_washtower.blend` | Q20 상태 복원용 백업, 현행 원본 아님 |
| `scripts/add_lg_washtower.py`, `verify_lg_washtower.py`, `render_lg_washtower.py` | 워시타워·타일 바닥 모델링, 검증, 확인 렌더 |
| `renders/review/render_46_utility_washtower.png`, `render_47_utility_washtower_side.png` | 다용도실 워시타워·타일 바닥 확인 렌더 |
# Q22 안방 리스탠다드 킹 자료 (2026-10-24)

후속 Q22b: `scripts/fix_master_bed_wall.py`는 연출용 벽패널/띠조명 제거와 실제벽 밀착을 재현한다.
`models/backups/apt_84a_photoreal_tour_before_master_wall_cleanup.blend`는 이 수정 직전 복원본이다.
아래 Q22 확인 렌더와 파생 갤러리는 Q22b 배치로 갱신한다.
Q22c에서는 `scripts/clear_master_bedside.py`로 러그·협탁/조명을 제거하고 마루에 침대를 놓았다.
백업은 `models/backups/apt_84a_photoreal_tour_before_master_bedside_cleanup.blend`이며,
같은 48~50번/발표4번/전체평면36번과 갤러리가 최신 Q22c 상태를 보여 준다.

| 경로 | 목적·상태 |
| --- | --- |
| `references/furniture/60s-restandard/README.md` | 사용자 옵션·공식 규격·출처 및 사진 기반 가정 |
| 같은 폴더 `product-1968.html`, `removebg-01.jpg`~`04.jpg`, `size-RBA-GR02-2.jpg` | 공식 페이지/제품 형태/115mm 다리 치수 원본 참고자료, 생성 렌더 아님 |
| `models/backups/apt_84a_photoreal_tour_before_restandard_bed.blend` | Q22 직전 복원용; 현행 원본 아님 |
| `assets/textures_export/q22_grey.png`, `q22_white.png`, `q22_wood.png` | 코드 생성 원단/목재 표현, blend에 패킹/GLB 포함; 제품 스캔 아님 |
| `renders/review/render_48_restandard_master.png` | 현행 안방 POV |
| `renders/review/render_49_restandard_detail.png` | 현행 침대 퀼팅/다리 확인 |
| `renders/review/render_50_restandard_plan.png` | 현행 안방 배치 평면 |
| `renders/presentation/render_4_master_bedroom_pov.png`, `renders/review/render_36_dimensioned_plan.png` | Q22 반영 안방·전체 평면 갱신 |
| `web/public/gallery/master-bed.webp`, `topdown.webp`, 각 `thumbs/` | 갱신 렌더의 웹 파생본 |
| `assets/analysis/inspect_master_bed.py`, `q22_validation_runner.py` | 기존 배치 읽기/저장모델18개 회귀검사 도구 |
| `docs/superpowers/specs/2026-10-24-restandard-master-bed-design.md`, `docs/superpowers/plans/2026-10-24-restandard-master-bed.md` | Q22 설계·실행 기록. 다른 방의 현행 교정을 대체하지 않음 |
