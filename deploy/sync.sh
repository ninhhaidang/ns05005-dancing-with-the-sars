#!/bin/bash
# Mirror this repo (code, docs, data, outputs) to the home server, then rebuild and restart the web stack.
#   deploy/sync.sh            sync + docker compose up -d --build
#   deploy/sync.sh --no-build sync only
# Secrets never leave this machine: .earthdata_token is excluded; the server keeps its own ~/.config/dwts/web.env.
set -euo pipefail
# Server address lives in deploy/sync.local.env (gitignored): DWTS_HOST=user@host
[[ -f "$(dirname "$0")/sync.local.env" ]] && source "$(dirname "$0")/sync.local.env"
HOST="${DWTS_HOST:?set DWTS_HOST=user@host (or put it in deploy/sync.local.env)}"
DEST="${DWTS_DEST:-workspace/ns05005-dancing-with-the-sars}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

rsync -az --delete --stats \
  --exclude '.earthdata_token' --exclude '.DS_Store' --exclude '__pycache__' --exclude 'catboost_info' \
  --exclude '.claude/settings.local.json' --exclude 'deploy/sync.local.env' --exclude 'deploy/SERVER.local.md' --exclude 'data/tmp/' \
  --exclude 'web/node_modules/' --exclude 'web/dist/' --exclude 'web/.astro/' --exclude 'web/.cache/' \
  --exclude 'web/public/figures/' --exclude 'web/src/generated/' \
  "$ROOT/" "$HOST:$DEST/"

if [[ "${1:-}" != "--no-build" ]]; then
  ssh "$HOST" "cd $DEST/deploy && docker compose up -d --build && docker compose ps"
fi
