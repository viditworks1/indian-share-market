#!/bin/bash
# git_sync.sh — shared end-of-run commit+push for every scheduled task in this repo.
#
# 2026-09-17 (user instruction): "all changes from all routines needs to be made in the
# local. Any git commit needs to just update. Maintain just one source of truth." This
# repo previously accumulated ~600 files of uncommitted scheduled-task output over 5 days
# (see PR #2) because no task ever committed its own work, AND a separate, now-removed
# clone at ~/indian-share-market (driven by a stale native-cron entry) was independently
# committing straight to origin — causing this checkout's local `main` to diverge from
# `origin/main`. Both problems are fixed by: (a) removing that second clone/cron entry,
# and (b) every task calling this script as its last step, so this ONE checkout is always
# the single source of truth and is never more than one run behind origin.
#
# Usage (from repo root, or anywhere — cd's to the repo root itself first):
#   ./scripts/git_sync.sh "<task-id>" "<one-line summary of what this run changed>" [path ...]
#
# If no [path ...] is given, stages everything under the repo (git add -A). Pass explicit
# paths when a task should only ever touch its own project's files (recommended — keeps
# one task's sync from accidentally sweeping up another task's uncommitted work-in-progress
# from a DIFFERENT, still-running task on the rare occasion two overlap).
#
# Safe to call even when there's nothing to commit (no-ops cleanly, exit 0). Always ends
# with a `git pull --rebase` + `git push` so the local commit becomes a plain fast-forward
# update on origin/main — never a merge, never a diverging branch.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

TASK_ID="${1:?usage: git_sync.sh <task-id> <summary> [path ...]}"
SUMMARY="${2:?usage: git_sync.sh <task-id> <summary> [path ...]}"
shift 2 || true
PATHS=("$@")

if [ ${#PATHS[@]} -eq 0 ]; then
  git add -A
else
  git add -- "${PATHS[@]}"
fi

if git diff --cached --quiet; then
  echo "git_sync[$TASK_ID]: nothing to commit, skipping."
  exit 0
fi

git commit -m "${TASK_ID}: ${SUMMARY}

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"

# Catch up on anything another task committed since this run started, then push as a
# plain fast-forward — never leave this checkout diverged from origin again.
git pull --rebase origin main
git push origin main

echo "git_sync[$TASK_ID]: committed and pushed."
