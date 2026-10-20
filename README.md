# 동탄 84A 아파트 3D 모델·웹 투어

현재 작업 모델은 [apt_84a_photoreal_tour.blend](apt_84a_photoreal_tour.blend)다.
Blender 모델을 GLB로 내보내 [웹 투어](web/README.md)에서 사용한다.

- [자료 안내](docs/asset-guide.md): 도면·참고 사진·렌더 구분, 최신 상태, 생성 경로
- [파일별 목록과 이동표](docs/asset-inventory.md): 기존 위치 → 정리된 위치
- [품질 보고서](docs/quality-v2-report.md): 최근 배치 변경과 검증 결과
- [에이전트 작업 안내](AGENTS.md): 다른 작업자가 이어갈 때 먼저 읽을 내용

```text
references/     원본 도면·평면 참고도·모델하우스 자료와 크롭
renders/        발표용·최근 검토·비교·프리뷰·과거 검증 이미지
models/         과거 모델과 복원용 백업
assets/         텍스처와 분석 중간 데이터
scripts/        Blender 생성·렌더·익스포트·검사 스크립트
web/            Three.js 투어와 웹용 GLB·충돌 데이터
docs/           자료 목록·검증 기록·과거 설계와 계획
```

최근 가전 배치의 확인 이미지는 [냉장고 POV](renders/review/render_11_fridge_pov.png)와
[싱크 옆 문 POV](renders/review/render_12_sink_door_pov.png)다.
다른 렌더에는 이전 배치가 남아 있을 수 있다.

안방 발코니·대피실 보수본은 [평면 검토](renders/review/render_13_master_balcony_plan.png),
[발코니 입구](renders/review/render_14_master_balcony_pov.png),
[대피실 입구](renders/review/render_15_refuge_pov.png)를 참고한다. 두 문은 통행 가능한 열린 상태다.

알파룸 벽 복구·책상/의자 제거 후 상태는 [평면 검토](renders/review/render_16_alpha_plan.png)와
[실내 확인](renders/review/render_17_alpha_pov.png)을 참고한다.

후속 실외기실 정리본은 [평면](renders/review/render_18_utility_plan.png)과
[실내 확인](renders/review/render_19_utility_pov.png)을 참고한다.

공식 84A VR에 맞춰 보강한 현관은 [열린 모습](renders/review/render_23_foyer_open.png),
[팬트리 내부](renders/review/render_22_entry_pantry.png),
[중문 디테일](renders/review/render_21_middle_door_detail.png)을 참고한다. 중문 디테일 컷만 임시 닫힘 촬영이다.

