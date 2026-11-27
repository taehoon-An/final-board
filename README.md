# Cloud Board — 클라우드 네이티브 기말 프로젝트

## 구현 목표와 현재 검증 범위

게시글 조회·작성·수정·삭제, 프론트엔드/백엔드 별도 이미지 및 Deployment,
PostgreSQL 영구 저장, GitHub Actions 이미지 빌드 및 GitOps 배포 구성을 제공합니다.
실제 배포 여부와 테스트 결과는 VALIDATION.md에 기록합니다. 구성 파일이 있다는 것만으로
배포가 성공한 것은 아닙니다.

## 구조

브라우저 → Windows 2000 → 기존 nginx Ingress → board-frontend Service → nginx 프론트 Pod
→ /api/ 프록시 → board-backend Service → Flask/Gunicorn 백엔드 Pod → board-db → PostgreSQL.
각 서비스는 별도 Deployment입니다. 모든 프로젝트 Pod는 myserver2에 배치합니다.

## 수업 자료 대응

- 11주차 36~44쪽: GitHub Actions. 게시판 단위 테스트와 실제 PostgreSQL 컨테이너 CRUD 테스트로 확장.
- 11주차 51~55쪽: 기존 Argo CD 로그인 환경 재사용.
- 11주차 57~62쪽: nginx 예제를 이 저장소의 k8s/로 대체.
- 11주차 63~70쪽: Application 생성 및 동기화. 이 프로젝트는 자동 동기화 사용.
- 75~76쪽 삭제 실습은 제출용 배포에 수행하지 않음.

## 최초 설치

1. 저장소 이름은 예시 `taehoon-An/final-board`. 실제 이름이 다르면 argocd/application.yaml의 repoURL을 수정합니다.
2. main에 push하면 Actions가 테스트 후 GHCR에 frontend/backend 이미지를 올립니다.
3. GHCR의 두 프로젝트 이미지는 공개 패키지이며 클러스터에서 인증 없이 읽습니다. 클러스터에 GitHub 토큰을 보관하지 않습니다.
4. server01에서 `bash scripts/bootstrap.sh`로 namespace와 DB Secret을 생성합니다. 기존 Secret은 덮어쓰지 않습니다.
5. Actions 성공 및 k8s/kustomization.yaml의 bootstrap 태그가 실제 커밋 태그로 변경됐는지 확인합니다.
6. `kubectl apply -f argocd/application.yaml`을 실행합니다.
7. `kubectl get applications -n myargocd`, `kubectl get pods,svc,ingress,pvc -n board`로 확인합니다.

별도 Argo CD 관리 비밀번호나 DB 비밀번호는 Git에 기록하지 않습니다. DB Secret 생성은 명령 출력에 비밀번호를 표시하지 않습니다.

## 재시작

서버01·02를 켜고 `kubectl get nodes`, `kubectl get pods -n board`로 확인합니다.
저장된 Kubernetes 리소스는 유지되므로 helm install을 반복하지 않습니다.
Ingress IP가 기존 Windows 2000 포워딩 목적지와 맞아야 합니다.

## 테스트

```bash
cd backend
pip install -r requirements.txt
python -m unittest -v
```

배포 후 프로젝트 루트에서:

```bash
python3 scripts/smoke.py http://127.0.0.1:2000
```

주의: 위 주소는 Windows에서 실행할 때의 주소입니다. VM에서 실행할 때에는 실제 Ingress External IP를 지정합니다.
테스트는 고유한 테스트 글을 만들고 그 글만 삭제합니다.

## 5분 시연 흐름

1. 게시판 접속 및 목록 조회, 글 작성, 새로고침으로 저장 확인.
2. 글 수정 후 삭제, 화면 반영 확인.
3. `kubectl get deploy,pods,svc,pvc -n board`로 프론트/백엔드 분리와 DB 저장 공간 확인.
4. frontend/index.html의 화면 문구 변경 후 main push.
5. Actions의 테스트/빌드/업로드 성공과 GitOps 이미지 태그 커밋 확인.
6. Argo CD에서 Synced/Healthy 확인 후 게시판 새로고침으로 변경 반영 시연.

## 제한사항

- 교육용 공개 게시판으로 로그인·글 소유자 권한·첨부파일은 구현하지 않음. 모든 방문자가 CRUD 가능.
- PostgreSQL 데이터는 server02의 /var/lib/cloud-board-postgres에 저장. Pod 재생성에는 유지되지만 VM 디스크 손실이나 다른 노드로의 이동을 자동 복구하지 못함. 고가용성 아님.
- PV reclaimPolicy는 Retain. 앱 삭제 시에도 데이터를 자동 삭제하지 않음.
- 테스트는 기능 검증용이며 부하·보안 검증 전체를 대신하지 않음.
- 컨테이너 기반 이미지의 패치 버전은 재빌드 시 바뀔 수 있음. 프로젝트 이미지는 Git 커밋 SHA 태그로 구분.
- 모니터링과 서버리스는 이번 제출 범위에 포함하지 않음.
- 점수는 교수자의 실제 채점에 따름. 목표는 게시판 및 CI/CD 항목의 동작 증빙.
