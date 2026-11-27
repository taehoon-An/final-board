#!/usr/bin/env bash
set -euo pipefail
kubectl get namespace board >/dev/null 2>&1 || kubectl create namespace board
if ! kubectl -n board get secret board-db-secret >/dev/null 2>&1; then
  umask 077
  secret_file=$(mktemp)
  trap 'rm -f "$secret_file"' EXIT
  password=$(openssl rand -hex 24)
  printf 'password=%s\ndatabase-url=postgresql+psycopg2://board:%s@board-db:5432/board\n' "$password" "$password" > "$secret_file"
  kubectl -n board create secret generic board-db-secret --from-env-file="$secret_file"
  unset password
fi
