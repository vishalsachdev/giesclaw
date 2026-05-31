#!/usr/bin/env bash
# giesclaw VPS deploy — run ON the VPS:  ssh vps 'cd /opt/giesclaw && ./scripts/deploy.sh'
# Generalized from _meta-optimization/scripts/vps-deploy.sh for giesclaw's systemd setup.
# Improvements over the manual sequence in CLAUDE.md: lockfile-clean pull,
# build-before-restart enforced, post-deploy health check, heartbeat sentinel.
set -euo pipefail

REPO="/opt/giesclaw"
PLATFORM="$REPO/platform"
HEALTH_URL="http://localhost:3004/"          # business-infinite.service listens here
BRANCH="main"

log()  { printf '\033[1;34m[deploy]\033[0m %s\n' "$*"; }
fail() { printf '\033[1;31m[deploy:FAIL]\033[0m %s\n' "$*" >&2; exit 1; }

cd "$REPO"
log "Discarding lockfile churn so git pull won't conflict…"
git checkout -- platform/package-lock.json 2>/dev/null || true

log "Pulling $BRANCH…"
git fetch origin "$BRANCH" --quiet
git reset --hard "origin/$BRANCH"

log "Installing + building platform (build MUST precede restart)…"
cd "$PLATFORM"
npm ci --silent 2>/dev/null || npm install --silent
npm run build

log "Restarting services…"
sudo systemctl restart business-infinite
sudo systemctl restart giesclaw-daemon

log "Health check: $HEALTH_URL"
sleep 2
for i in 1 2 3 4 5; do
  if curl -fsS --max-time 5 "$HEALTH_URL" >/dev/null 2>&1; then
    log "Healthy ✓  Deploy complete."
    mkdir -p "$HOME/.deploy-sentinels"; touch "$HOME/.deploy-sentinels/giesclaw"
    exit 0
  fi
  log "  not healthy yet ($i/5)…"; sleep 3
done
systemctl status business-infinite --no-pager -n 20 2>/dev/null || true
journalctl -u business-infinite -n 30 --no-pager 2>/dev/null || true
fail "Health check never passed — business-infinite may have crashed. Logs above."
