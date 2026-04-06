#!/usr/bin/env bash
# Nightly backup of memory/, people/, MEMORY.md to a private git remote.
# Configure BACKUP_REMOTE in .env (e.g. git@github.com:you/cos-backup.git).

set -euo pipefail

cd "$(dirname "$0")/.."
[ -f .env ] && set -a && . ./.env && set +a

if [ -z "${BACKUP_REMOTE:-}" ]; then
  echo "[backup] BACKUP_REMOTE not set; skipping"
  exit 0
fi

BRANCH="main"
DIR=".backup-repo"

if [ ! -d "$DIR/.git" ]; then
  git clone "$BACKUP_REMOTE" "$DIR"
fi

rsync -a --delete memory/ "$DIR/memory/"
rsync -a --delete people/ "$DIR/people/"
cp MEMORY.md "$DIR/MEMORY.md"

cd "$DIR"
git add -A
if git diff --cached --quiet; then
  echo "[backup] no changes"
  exit 0
fi
git commit -m "backup $(date -u +%Y-%m-%dT%H:%M:%SZ)"
git push origin "$BRANCH"
