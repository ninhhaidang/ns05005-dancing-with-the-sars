#!/bin/bash
# Mirror this repo (code, docs, data, outputs) to the home server, then rebuild and restart the web stack.
#   deploy/sync.sh            sync + docker compose up -d --build
#   deploy/sync.sh --no-build sync only
# Secrets never leave this machine: .earthdata_token is excluded; the server keeps its own ~/.config/dwts/web.env.
set -euo pipefail
HOST="${DWTS_HOST:-ninhhaidang@100.103.170.97}"
DEST="${DWTS_DEST:-workspace/ns05005-dancing-with-the-sars}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

rsync -az --delete --stats \
  --exclude '.earthdata_token' --exclude '.DS_Store' --exclude '__pycache__' --exclude 'catboost_info' \
  --exclude '.claude/' --exclude 'data/tmp/' \
  --exclude 'web/node_modules/' --exclude 'web/dist/' --exclude 'web/.astro/' --exclude 'web/.cache/' \
  --exclude 'web/public/figures/' --exclude 'web/src/generated/' \
  "$ROOT/" "$HOST:$DEST/"

if [[ "${1:-}" != "--no-build" ]]; then
  ssh "$HOST" "cd $DEST/deploy && docker compose up -d --build && docker compose ps"
fi
