# 검증 기록

2026-11-27 실제 환경에서 확인했습니다.

- 단위 테스트 및 VM Docker PostgreSQL 통합 CRUD 통과.
- main push Actions 성공: https://github.com/taehoon-An/final-board/actions/runs/45940003861
- 테스트, 이미지 빌드, PostgreSQL CRUD, GHCR 게시, 배포 태그 커밋 모두 성공.
- 배포 이미지 소스: 3280ce60830827cbba457d843f53ea45ff950ba7.
- Argo CD final-board: Synced / Healthy.
- frontend/backend/DB 별도 Deployment: 모두 1/1 Running. PVC Bound, 2Gi.
- Windows http://127.0.0.1:2000 경유 실제 배포 health·작성·조회·수정·삭제 통과.
- DB Pod 재생성 후 테스트 글 유지 확인. 해당 테스트 글은 삭제.
- 브라우저 한글 글 작성·목록·수정 확인. 시연용 글 1개 유지.
- 공개 GHCR 이미지를 사용하며 임시 registry credential Secret 제거.

기존 myserver3 Calico 및 다른 일부 실습 애드온 오류는 별도입니다. 게시판은 myserver2에 고정하여 검증했습니다.
모니터링/서버리스는 구현하지 않았습니다. 목표는 게시판 70점 + CI/CD 30점 항목이며 실제 점수는 교수자 평가에 따릅니다.
