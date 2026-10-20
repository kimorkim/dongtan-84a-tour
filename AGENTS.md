# 에이전트 공통 작업 안내

## 이어서 작업하기

1. [자료 안내](docs/asset-guide.md)를 읽어 도면·실물 참고 사진·생성 렌더를 구별한다.
2. [품질 보고서](docs/quality-v2-report.md)에서 최근 변경과 검증 범위를 확인한다.
3. 개별 파일은 [자료 목록과 이동표](docs/asset-inventory.md)에서 찾는다.

현재 원본은 루트의 `apt_84a_photoreal_tour.blend`다.
`models/archive/`는 과거 단계, `models/backups/`는 복원용이며 현행 원본이 아니다.
웹은 `web/public/house.glb`와 `web/public/colliders.json`을 사용한다.

## 현행 배치와 자료 해석

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

