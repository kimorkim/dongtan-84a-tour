# 에이전트 공통 작업 안내

- 거실은 Q15 마감본이다. Q14 소파 뒤 `scripts/detail_living_finish.py`를 적용했다.
  중앙 `Q2_Coffee*`/`Q2_Pouf*`/거실 러그와 도형 덧판은 사용자 요청으로 제거했다.
  아트월은 y.92~4.75 전체 높이와 북쪽 안방 문 상부만 마감한다. 출입구를 막지 않는다.
  거실 창 외곽 3600×2000mm·하부270mm는 유지하며, 가운데 넓은 분할과 양끝 커튼은
  모델하우스 `display84a_01.jpg`를 참고한 추정이다. 난간 상단은 주바닥 기준830mm다.
  `Q2_Landscape`는 손상된 픽셀·거꾸로 된 UV를 복구해 패킹한 예시 배경이며 실제 조망이 아니다.
  `verify_living_finish.py`와 기존 치수/방/보행 검사 뒤 충돌·GLB를 갱신한다.
  확인 렌더는 40번 창가·41번 아트월이며 29·38·39·36번도 갱신했다.

## 이어서 작업하기

1. [자료 안내](docs/asset-guide.md)를 읽어 도면·실물 참고 사진·생성 렌더를 구별한다.
2. [품질 보고서](docs/quality-v2-report.md)에서 최근 변경과 검증 범위를 확인한다.
3. 개별 파일은 [자료 목록과 이동표](docs/asset-inventory.md)에서 찾는다.

현재 원본은 루트의 `apt_84a_photoreal_tour.blend`다.
`models/archive/`는 과거 단계, `models/backups/`는 복원용이며 현행 원본이 아니다.
웹은 `web/public/house.glb`와 `web/public/colliders.json`을 사용한다.

## 현행 배치와 자료 해석

- **Q14 거실 소파:** 사용자 지정 시트앤모어 브레스트 아이보리 4인으로 교체했다.
  공식 닫힌 규격 2850×1000×950mm, 거실 동쪽 벽을 등지고 TV 방향이다.
  뒤쪽 x8.655/앞쪽 x7.655이며 벽과 150mm를 띄웠다. 리클라이너는 접힘, 중앙 홈바는 내려온 모습이다.
  옛 `Sofa_Living_*`와 `Q2_Sofa*` 쿠션을 되살리지 않는다. `scripts/replace_living_sofa.py`는 현재 모델에 적용한다.
  `verify_brest_sofa.py`, 기존 치수/방별/보행 검사 뒤 충돌·GLB·렌더를 갱신한다.
  38번 소파/29번 거실/39번 평면이 현재 확인 이미지다. 전개 궤적·모터 작동은 미검증이다.
  공식 출처와 가정은 `references/furniture/seatandmore-brest/README.md`를 본다.

- **Q13 서재 책장:** 거실과 공유하는 서쪽 벽에 검정 몸체·우드색 단면의 까사미아 포에타 6단
  800+600mm 두 개를 붙였다. x9.095~9.395/y1.35~2.75이며 북쪽 방문 앞은 비운다.
  `scripts/add_study_bookcases.py`는 현재 Q12 이후 모델에 추가하는 스크립트다.
  과거 전체 생성·Q12 백업 마이그레이션을 재실행해 책장을 없애지 않는다.
  `verify_study_bookcases.py`, 기존 방별/치수/보행 검사 뒤 충돌·GLB·렌더를 갱신한다.
  현재 확인 이미지는 37번 책장/33번 서재/34번 평면이며, 제품 규격·가정은
  `references/furniture/casamia-poeta/README.md`를 본다. 600형 깊이·높이는 같은 제품군 가정이다.

- **Q12 치수 교정이 아래 Q4~Q11의 옛 절대 좌표보다 우선한다.**
  `docs/dimension-correction-q12.md`와 `scripts/plan_dimensions.py`를 먼저 읽는다.
  서재 2700×3410/유나방 3000×3410, 사이 벽 130mm로 교정했다. 창과 전체 외곽도 갱신했다.
  일반 천장 2300/거실 우물천장 안쪽 2400mm는 사용자 확인값이며 형상에 반영했다.
  실외기실·알파룸 깊이·낮은 바닥 구역의 문/천장 상세 등 남긴 가정은 확정 치수로 제시하지 않는다.
  `calibrate_dimensions.py`는 Q11b 백업을 여는 일회성 마이그레이션이다. 후속 수정 뒤 재실행하면 안 된다.
  Q12 검사는 `verify_dimensions.py` 및 기존 방별 검사, 충돌/보행, 웹 실제 GLB 검사다.
  전체 현재 형상은 `renders/review/render_36_dimensioned_plan.png`를 본다.
- Blender는 m 단위, x=동쪽, y=북쪽, z=높이. 웹은 (x,y,z) → (x,z,-y).
- 냉장고장 순서: 남쪽 거실 → 냉장고 → 김치냉장고 → 밥솥장 → 북쪽 부엌.
  장 전체는 y5.64~8.05이며 북쪽 문 공간을 침범하지 않는다.
- 이 배치가 반영된 확인 이미지는 `renders/review/render_11_fridge_pov.png`와
  `render_12_sink_door_pov.png`다. 다른 렌더는 이전 상태일 수 있다.
- 도면 원본·추출은 `references/drawings/`, 입체·평면 참고도는 `references/layout/`,
  모델하우스 사진은 `references/modelhouse/`다. Blender 렌더는 `renders/`에 있다.
- `*_flipped.png`는 좌우 반전본이다. `*_74*`는 페이지 표기이며 74㎡형으로 해석하지 않는다.
- 초기 `docs/superpowers/` 문서는 후속 배치·치수 교정 이전의 기록이다.
  현재 모델을 초기 계획 값으로 되돌리거나 과거 전체 생성 스크립트를 무작정 재실행하지 않는다.
- 출처·실측·추정값과 검증 완료 범위를 구별해 기록한다. 가전 문 열림 간섭은 아직 미검증이다.
- 안방 발코니·대피실은 Q4 보수본이다. `scripts/fix_master_balcony.py`로 두 출입문을 열린 상태로
  만들었고 외창·외벽은 보행을 막는다. `scripts/verify_master_balcony.py`로 현관부터의 경로를 검사한다.
  **안방→발코니는 미닫이문**이다. 동쪽 문짝이 서쪽으로 겹쳐 열리며 여닫이 회전축을 만들지 않는다.
  최신 형태는 `renders/review/render_13_master_balcony_plan.png`, 14·15번 POV를 본다.
  과거 `fix_openings_pro.py`·`enhance_photoreal_details.py`를 재실행했다면 Q4를 마지막에 다시 적용한다.

## 저장과 검증

- 침실2는 Q11 2인 서재다. Q10b 이후 `scripts/detail_study_room.py`를 적용한다.
  구조벽을 보존하고 창 벽 마감선을 y=.85/창틀 중심을 y=.80으로 맞췄다.
  옛 `Bed2_*` 침대를 되살리지 않는다. 동쪽 문 없는 벽에 화이트 에렉투스 비스포크 모션테이블
  1800×800(남쪽)·1400×700mm(북쪽), 검정·그레이 에어론 형태 의자를 배치했다.
  제품 판매 규격은 공식 페이지 근거이며 하드웨어·의자 형상은 사진 기반 근사다.
  `verify_study_room.py`와 Q5~Q10 검사, `verify_master_balcony.py`의 서재 경로를 검사한 뒤
  충돌·GLB·33/34/35번 확인 렌더 및 웹 갤러리 '서재'를 갱신한다.
  의자와 책상은 정지 배치다. 실제 승강·의자 이동 중 간섭은 검증하지 않았다.
  Q11b에서는 큰 책상에 델 27인치 듀얼 암·세로 클램쉘 맥북·키보드/마우스·A2 스피커 2개,
  작은 책상에 받침대 위 32인치 모니터·키보드/마우스·하부 본체를 추가했다.
  의자는 큰 쪽 220mm/작은 쪽 270mm 동쪽으로 넣었다. 장비는 `Q11_Equipment_*`다.
  재현은 같은 `detail_study_room.py`를 쓰고 `references/furniture/workstation.md`에서 근거/가정을 구분한다.

- 침실3(거실 욕실 옆 동쪽 작은방)은 Q10b 유나방이다. Q9 뒤 `scripts/detail_yuna_room.py`를 적용한다.
  **사용자 옵션은 방문 옆 북쪽 기본 붙박이장**이다. 공식 VR 013의 창 옆 장은 다른 옵션이므로 복제하지 않는다.
  기본장 폭 1.82m/깊이 약 .60m는 임시 가정이며 천장까지 닫힌 4도어·필러 마감을 사용한다.
  CAD 구조 외곽·창 폭/높이는 유지하며, 창 벽의 실내 마감선은 y=.85로 일자로 보완했다.
  창틀 중심은 y=.80으로 옮겼다. 옛 y=.385 창틀과 y=.51 창 하부벽을 되살리지 않는다.
  창·문틀 면 방향과 방문 손잡이의 이중 좌표 변환도 고쳤다.
  이 방 창은 `Mat_Q10_Glass`(알파 .06)를 사용한다. 굴절 유리가 어둡게 나와 기존 투어와 같은
  알파 유리 방식을 사용하며 다른 방 유리는 미변경이다. 실제 광학 성능을 재현하는 모델은 아니다.
  방문은 손잡이가 서쪽 벽에 박히지 않게 85도 열려 있다. 서쪽 낮은 침대, 동쪽 낮은 그림책 수납과
  놀이 테이블, 중앙 꽃 러그를 사용하며 북쪽 장 문 앞 y3.15~3.59는 비운다.
  `Bed3_*`/`Wardrobe_Bed3_*` 성인 가구와 바닥 덧판을 되살리지 않는다.
  `verify_yuna_room.py`(Blender), 기존 Q5~Q9 검사, `verify_master_balcony.py`(현관→유나방 포함) 뒤
  충돌·GLB를 갱신한다. 갱신된 렌더 30번 POV·31번 평면·32번 기본장, 웹 갤러리 '아이방'을 본다.
  캐릭터 제품을 복제한 모델이 아니며 가구 치수·마감색은 제안값이다. 실제 아동 안전 인증은 별도다.

- 우드 바닥은 Q9 보수본이다. Q4~Q8 뒤 `scripts/improve_flooring.py`를 마지막에 적용한다.
  `Exact_Floor` 상면 하나(z=0)에 `Mat_Q9_LightOak`·명시적 `FloorUV`를 사용한다.
  안방/드레스룸/침실2·3/알파룸의 옛 사각 우드 덧판 5개는 제거했다. 다시 겹쳐 만들지 않는다.
  결은 x축(복도의 긴 방향), UV는 `(x/3, y/1.04)`로 방 사이 위상을 공유한다.
  판 폭 약 130mm와 밝은 오크 색은 사진 기반 가정이다. 현관·욕실·발코니·실외기실 타일은 보존한다.
  `verify_flooring.py`(Blender), Q5~Q8 및 보행 검사 뒤 충돌·GLB를 갱신한다.
  새 확인 이미지는 28번 복도·29번 거실과 `web_floor_before/after.jpg`다.

- 거실 욕실은 Q8 보수본이다. Q7 뒤 `scripts/detail_common_bath.py`를 적용하고 충돌·GLB를 갱신한다.
  근거는 공식 VR 015/016이며, `016_f.jpg`의 깨끗한 타일 부분을 UV로 사용한다.
  벽 300×600/바닥 300×300mm와 별도 줄눈을 유지한다. 사진은 제조사 PBR 스캔이 아니다.
  `ExactWall_5`의 샤프트 실내 면(x14.456~14.475)과 그 뒤 `ExactWall_6`를 철거하지 않는다.
  샤워 부속은 이 면 서쪽에 있고, 욕실문·샤워문은 열린 상태다.
  `verify_common_bath.py`(Blender)와 기존 Q5/Q6/Q7·보행 검사를 실행한다.
  새 확인 렌더는 24번 평면, 25번 건식 세면대, 26번 변기·거울장, 27번 샤워실이다.

- 알파룸은 Q5 보수본이다. 범위 x7.987~10.387/y5.737~7.931이며 동쪽 현관 팬트리와 구분한다.
  책상·의자와 `Office_*` 소품은 제거했다. `ExactWall_8`은 원래 윤곽으로 재생성한 닫힌 메시다.
  남쪽 출입구 x9.412~10.35, 북쪽 실외기실 문 x9.00~9.731을 사용한다.
  과거 Q3의 x8.05~8.85 추가 구멍과 문 앞 `Vent_ACRoom_*` 판을 되살리지 않는다.
  전체 생성/Q3/Q4 뒤 `scripts/fix_alpha_room.py`를 마지막으로 적용하고 충돌·GLB를 갱신한다.
  `verify_alpha_room.py`는 Blender 내부, `verify_master_balcony.py`는 일반 Python으로 검사한다.
  최신 확인 이미지는 `renders/review/` 16번 평면과 17번 POV다.
  식탁 러그 `Q2_Dining_Rug`는 중심 x6.85/y6.70, 크기 1.90×1.75m다.
  동쪽 끝 x7.80은 알파룸 벽면 x7.856보다 56mm 서쪽이어야 한다. 옛 2.35m 폭으로 되돌리지 않는다.
- 실외기실은 Q6 보수본이다. Q5 뒤 `scripts/fix_utility_room.py`를 적용한 다음 충돌·GLB를 갱신한다.
  방 내부는 대략 x8.662~10.181/y8.175~9.30이며 원래 두꺼운 서쪽 벽을 절개하지 않는다.
  `Floor_KitchenBalcony`/`Floor_ACOutdoor` 중복 바닥 대신 `Q6_UtilityFloor`를 사용한다.
  실외기는 서쪽 벽을 따라 놓이고 북쪽 x8.963~9.90에 루버가 있다. 환기 성능을 검증한 모델은 아니다.
  `verify_utility_room.py`(Blender), `verify_master_balcony.py`(보행)를 검사한다.
  최신 실외기실 이미지는 `renders/review/` 18번 평면·19번 POV다. 16·17번보다 후속 상태다.
- 현관은 Q7 보수본이다. 공식 84A VR의 017(현관)/018(현관창고) 장면을 기준으로 했다.
  근거 JPG와 출처는 `references/modelhouse/vr84a/README.md`를 본다.
  Q4/Q5/Q6 뒤 `scripts/detail_foyer.py`를 마지막에 실행하고 충돌·GLB를 갱신한다.
  팬트리 개구부를 가리던 `Foyer_Mirror_*`를 되살리지 않는다. 팬트리는 밝은색 양개문과 ㄷ자 선반이다.
  중문은 반투명 미닫이이며 투어에서는 서쪽으로 열린 상태다. `FrostedGlass` 재질을 일반 투명유리로 바꾸지 않는다.
  20번 평면·22번 팬트리·23번 열린 현관이 저장 상태다. 21번은 재질 확인용 임시 닫힘 촬영이다.
  `verify_foyer.py`(Blender) 및 기존 Q5/Q6·보행 검사를 실행한다.


- 새 원본은 `references/`, 생성 이미지는 `renders/`, 분석 중간물은 `assets/analysis/`에 둔다.
  이미지·도면을 프로젝트 루트에 새로 생성하지 않는다.
- 기존 변경 사항을 보존한다. Blender를 크게 수정하기 전 `models/backups/`에 백업한다.
- 스크립트는 프로젝트 루트에서 실행한다. `RENDER_DIR`를 지정하면 기본 출력 폴더보다 우선한다.
  Blender 저장본 내부의 과거 출력 설정은 유지했으므로 GUI 직접 저장 시에도 `renders/`를 지정한다.
- 모델을 변경하면 필요한 충돌 재베이크·GLB 익스포트·확인 렌더까지 갱신한다.
  웹 코드 검사는 `web/`에서 `npm run typecheck`, `npm run build`를 사용한다.
- 파일 이동 시 생산·소비 스크립트와 문서 경로도 수정한다.
  `docs/asset-inventory.md`는 수동 관리 목록이므로 새 자료의 목적·상태를 함께 남긴다.


## Q16 주방 싱크대 복구

- 현행 Q15 이후 `scripts/detail_kitchen_finish.py`를 적용했다. 부품별 Q12 변형으로 어긋난 상판/하부장/식기세척기와 수전을 복구했다.
- 서쪽 발코니2(다용도실) 가벽 `ExactWall_10`의 주방 쪽 마감면(`x=5.075`)을 침범하지 않도록 북측 상판·좌측 상부장·좌측 타일·마감판 시작점을 `x=5.080`으로 맞추고, 식기세척기(`x=5.095~5.685`)와 싱크볼(`x=5.715~6.555`, 창 구간 `x=5.455~6.655` 내)을 도면에 맞춰 정렬했다.
- 인덕션 위 중복 냄비(`Q2_Pot*`)를 제거해 단일 냄비(`KitchenProp_Pot_*`)만 남기고, 사용자 옵션에서 제외된 인덕션 하부 빌트인 오븐(`ProK_Oven_*`, `Q16_Oven*`)을 제거해 싱크대 하부장과 동일한 캐시미어 마감 양개 수납장(`Kitchen_Base_East`, `ProK_DoorE_L/R`)으로 교체했다.
- Q12 창 1200×1150/하부1120mm 및 구조벽·냉장고장 순서를 유지한다. 옛 전체 주방 생성/Q12 마이그레이션을 재실행하지 않는다.
- 싱크볼·가전 세부는 Q12 전 백업에서 해당 조립체만 복원해 강체 이동한다. 백업 파일 전체를 현행 원본으로 되돌리지 않는다.
- `verify_kitchen_finish.py`, 기존 치수/방/보행 검사 뒤 충돌·GLB·웹 주방 갤러리를 갱신한다.
- 현재 확인 렌더는 42~45번이다. 12/36번 및 갤러리용 주방 3/9번도 갱신했다.
- 장 깊이/문 분할·밝은 석재는 사진 기반 제안값이다. 가전 문 개폐·실제 배관·제작 치수는 미검증이다.


## Q17 거실 TV장 및 스탠드형 TV 교체

- 현행 Q16 이후 `scripts/replace_living_tv_stand.py`를 적용했다. 사용자 지정 `references/furniture/living-tv-stand/model.glb`(2000×450×513mm)로 기존 거실 TV장(`MediaUnit_Living`, `ProK_MediaTop`)과 상부 소품(`Q2_Console*`)을 교체하고, 기존 벽걸이 TV(`Living_TV_OLED_*`)를 제거한 뒤 사용자 지정 스탠드형 TV `references/furniture/living-tv/tv.glb`(1225×270×765mm, `Q17_TV_*`)를 TV장 상판 중앙(`x=4.420~4.690`, `y=2.6735~3.8985`, `z=0.513~1.278`)에 올려놓았다.
- TV장은 서쪽 아트월 마감면(`x=4.330`)에 뒷면을 밀착(`x=4.330~4.780`, `y=2.286~4.286`, `z=0.000~0.513`)했고, TV장 도어와 TV 화면 모두 동쪽 소파(`+X`)를 향한다.
- `verify_living_tv_stand.py`, `verify_living_finish.py`, 기존 치수/방/보행 검사 뒤 충돌·GLB·거실 확인 렌더(41·39·40·38·29·36번)와 웹 갤러리를 갱신한다.


## Q18 냉장고장 밥솥칸 상부 LG 광파오븐 추가 및 실사용 높이·도어 틈새 마감 교정

- 현행 Q17 이후 `scripts/add_lg_lightwave_oven.py`를 적용했다. 냉장고장 가장 북쪽 칸(밥솥장, `y=7.5033~8.1359`)을 실사용 인체공학 높이에 맞춰 하부 2단 서랍(`z=0.040~0.560`), 밥솥 오픈칸(`z=0.582~0.940`, 선반 `Q3_Niche_Shelf` `z=0.562~0.582`), 광파오븐 오픈칸(`z=0.960~1.400`, 하판 `Q3_Niche_Top` `z=0.940~0.960`, 상판 `Q3_OvenNiche_Top` `z=1.400~1.420`), 중상부 수납문(`Q3_OvenUpper_Door` `z=1.422~1.8095`)으로 재구성했다.
- 냉장고장 상부장 4도어(`Q3_TopDoor1..3, 0`, `z=1.812~2.260`)와 중상부 도어(`Q3_OvenUpper_Door`), 하부 서랍 2단(`Q3_Drawer_Front1/2`, 손잡이 `Q3_Drawer_Handle0/1`), 가전 좌우 필러(`Q3_FillerS/N`)·수직 칸막이(`Q3_Divider`, `Q3_Divider2`, `Q3_Drawer_SideS/N`)·상부 몰딩(`Q3_TopPanel` `z=2.262~2.300`)을 빈틈없이 2mm 줄눈(내부 몸통 백업 포함)으로 정밀 정렬했다.
- 사용자 지정 LG 디오스 오브제컬렉션 광파오븐 `MLJ32EWSO`(공식 외형 527×480×394mm, `Q18_LightwaveOven_*`)를 모델링하여 밥솥 위 상부 오픈칸 중앙(`x=4.420~4.900`, `y=7.5715~8.0985`, `z=0.960~1.354`, 전면 `+X`)에 배치했다. 공식 규격·출처는 `references/furniture/lg-lightwave-oven/README.md`를 본다.
- `verify_lg_lightwave_oven.py`, `verify_kitchen_finish.py`, 기존 치수/방/보행 검사 뒤 충돌·GLB·냉장고장 확인 렌더(11·12번)와 웹 갤러리를 갱신한다.


## Q19 거실 사운드바 및 무선 서브우퍼 추가

- 현행 Q18 이후 `scripts/add_living_soundbar.py`를 적용했다. 사용자 지정 삼성 2.1채널 사운드바(`HW-C450/B450` 계열, `references/furniture/living-soundbar/README.md`)를 모델링해 추가했다.
- 사운드바 본체(공식 외형 858.8×75.0×59.0mm, `Q19_Soundbar_*`)는 거실 TV장 상판(`z=0.513`) 위 TV 스탠드 다리 사이 전면 중앙(`x=4.680~4.755`, `y=2.8566~3.7154`, `z=0.513~0.572`, 전면 `+X`)에 배치했고, 무선 서브우퍼(공식 외형 184.0×295.0×343.0mm, `Q19_Subwoofer_*`)는 브레스트 소파의 남쪽(창가 쪽) 팔걸이 옆 바닥(`x=8.360~8.655`, `y=1.373~1.557`, `z=0.000~0.343`, 전면 `-X`)에 배치했다.
- `verify_living_soundbar.py`, `verify_living_finish.py`, 기존 치수/방/보행 검사 뒤 충돌·GLB·거실 확인 렌더(41·40·39·38·29·36번)와 웹 갤러리를 갱신한다.


## Q20 냉장고장-다용도실 가벽 틈새 마감 및 다용도실 터닝도어 교체

- 현행 Q19 이후 `scripts/fix_utility_turning_door.py`를 적용했다. 냉장고장 우측 마감판(`Q3_SideN`, `y=8.176`)과 다용도실 가벽(`ExactWall_11`) 사이의 사선 단차(`y=8.185~8.280`) 및 돌출 걸레받이(`ProBaseboards`)를 제거하고 가벽 남단(`y=8.176`)을 냉장고장 측판에 0mm로 밀착했다.
- 다용도실 출입구(`y=8.360~9.015`) 상부 인방벽(`Q20_UtilityDoor_Header`, `x=4.975~5.075`, `z=2.150~2.300`)을 채우고, 벽면에서 떠 있던 기존 목문 틀(`Q3_SinkTrim*`)과 불투명 방문짝(`ProDoorLeaf_UtilitySink`)을 제거한 뒤 벽 두께 전체를 감싸는 일체형 화이트 uPVC 터닝도어 프레임(`Q20_TurningDoor_Frame_S/N/Top/Bot/Gasket`, `x=4.963~5.087`)과 투명 복층유리 터닝도어 문짝(`ProDoorLeaf_UtilitySink_Frame/Glass/Gasket/Handle`, 다용도실 안쪽 90° 개방)으로 교체했다.
- `verify_utility_turning_door.py`, `verify_kitchen_finish.py`, 기존 치수/방/보행 검사 뒤 충돌·GLB·다용도실 문 확인 렌더(11·12번)와 웹 갤러리를 갱신한다.



## Q21 다용도실 세탁기 홈 치수 교정, LG 워시타워 및 타일 바닥

- 현행 Q20 이후 `scripts/add_lg_washtower.py`를 적용했다. 도면(`A02-102`, `dimension_north.png`의 `1,010 / 1,115` 치수선)과 달리 `y=8.995~9.015`(폭 635mm)로 좁아져 있던 다용도실 남서쪽 세탁기 홈의 북쪽 PS 가벽(`ExactWall_11`, `ExactWall_12`, `ProBaseboards`)을 도면 치수인 `y=9.270`(실내 순폭 `910mm`, `y=8.360~9.270`, 단차 깊이 `600mm`, `x=3.175~3.775`)으로 교정했다.
- 사용자 지정 LG 트롬 오브제컬렉션 워시타워 `WL21EGZU`(공식 700×1890×830mm, 상단 네이처 그린 건조기/하단 네이처 베이지 세탁기, `Q21_WashTower_*`)를 모델하우스와 동일하게 다용도실 남서쪽 세탁기 홈 안쪽 서쪽 벽(`x=3.175`)에서 호스 여유 40mm를 띄우고 정면이 터닝도어(`+X`)를 향하게 배치했다(`x=3.215~4.045`, `y=8.500~9.200`, `z=0.014~1.904`).
- 다용도실 바닥은 우드 위에 300×300 회색 타일·2mm 줄눈(`Q21_UtilityTile_Floor/Grout`, 상면 z=0.014)과 사각 배수구(`Q21_UtilityTile_Drain`)로 마감했다. 범위는 남쪽(세탁기 홈~출입구) x3.175~4.975/y8.360~9.270, 북쪽(창문 앞) x3.775~4.975/y9.270~10.145다.
- 정면 비례는 `references/furniture/lg-washtower/wl21egzu_front.png` 기반 근사다. 급배수 위치, 도어 열림(1410mm) 간섭, 바닥 물매는 미검증이다.
- `verify_lg_washtower.py`, `verify_utility_turning_door.py`, `verify_kitchen_finish.py`, 기존 치수/방/보행 검사 뒤 충돌·GLB·확인 렌더(46·47번, 11·12번)를 갱신한다.
