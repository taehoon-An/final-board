# 검증 기록

- 코드 작성: 완료.
- 로컬 CRUD 테스트: 통과 (2026-11-27). 작성→목록 조회→수정→삭제, 빈 값/잘못된 JSON/긴 제목 거부, 없는 글 404, DB health 확인. SQLite 메모리 DB 기반이므로 실제 PostgreSQL 배포 검증은 별도 필요.
- VM SSH 연결: 성공. 임시 키의 잘못된 암호 설정을 수정하여 접속 확인.
- VM Docker 통합 테스트: 통과. nginx 프론트 프록시 → Flask 백엔드 → 실제 PostgreSQL 16 경로로 health·작성·조회·수정·삭제 확인. 테스트용 컨테이너는 종료 후 정리.
- Kubernetes 배포 파일: kubectl client dry-run 통과. board namespace, DB Secret, DB Deployment, PV/PVC 생성 완료. PVC Bound 확인. 전체 배포 검증은 진행 중.
- GitHub Actions 실제 실행: GitHub 재인증 대기.
- Argo CD Synced/Healthy 및 화면 시연: 배포 후 확인 필요.

아직 배포 완료 상태가 아닙니다.
