#!/bin/bash
# Hourly refresh: regenerate feeds, commit, push (GitHub Pages serves them).
set -euo pipefail
cd "$(dirname "$0")"
/usr/bin/python3 fetch.py >> logs/fetch.log 2>&1 || true
if [ -n "$(git status --porcelain feeds)" ]; then
  git add feeds
  git -c user.name=doi -c user.email=doi@local commit -q -m "feeds: $(date '+%Y-%m-%d %H:%M')"
  git push -q origin main
  echo "$(date '+%F %T') pushed $(ls feeds | wc -l | tr -d ' ') feeds" >> logs/push.log
fi
