#!/usr/bin/env bash
set -euo pipefail
network=board-verify
database=board-verify-db
backend=board-verify-api
frontend=board-verify-web
cleanup() { docker rm -f "$frontend" "$backend" "$database" >/dev/null 2>&1 || true; docker network rm "$network" >/dev/null 2>&1 || true; }
trap cleanup EXIT
docker network create "$network" >/dev/null
docker run -d --name "$database" --network "$network" --network-alias board-db -e POSTGRES_DB=board -e POSTGRES_USER=board -e POSTGRES_PASSWORD=local-test-only postgres:16-alpine >/dev/null
for attempt in $(seq 1 45); do
  if docker exec "$database" pg_isready -U board -d board >/dev/null 2>&1; then break; fi
  sleep 2
done
docker run --rm --network "$network" -e DATABASE_URL=postgresql+psycopg2://board:local-test-only@board-db:5432/board final-board-backend:initial flask --app 'app:create_app()' init-db
docker run -d --name "$backend" --network "$network" --network-alias board-backend -e DATABASE_URL=postgresql+psycopg2://board:local-test-only@board-db:5432/board final-board-backend:initial >/dev/null
docker run -d --name "$frontend" --network "$network" -p 127.0.0.1:18080:80 final-board-frontend:initial >/dev/null
for attempt in $(seq 1 30); do
  if curl -fsS http://127.0.0.1:18080/api/health >/dev/null; then break; fi
  sleep 2
done
python3 scripts/smoke.py http://127.0.0.1:18080
