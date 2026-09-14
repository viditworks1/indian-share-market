#!/bin/bash
#
# Local trading refresh runner for macOS
# Runs daily market-close update: confluence-100 technicals + paper-trading ledger
# Designed to be called from local cron or Claude Code trigger
#

set -e  # exit on any error

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="${ROOT}/logs"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="${LOG_DIR}/refresh_${TIMESTAMP}.log"

# Create logs directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Log start
{
  echo "=== Trading Refresh Started: $(date) ==="
  echo "Root: $ROOT"
  echo ""
} | tee -a "$LOG_FILE"

# Function to run a Python script and log output
run_script() {
  local script_name="$1"
  local script_path="$2"

  echo "--- Running: $script_name ---" | tee -a "$LOG_FILE"

  if [[ ! -f "$script_path" ]]; then
    echo "ERROR: Script not found: $script_path" | tee -a "$LOG_FILE"
    return 1
  fi

  if python3 "$script_path" 2>&1 | tee -a "$LOG_FILE"; then
    echo "✓ $script_name completed successfully" | tee -a "$LOG_FILE"
    return 0
  else
    echo "✗ $script_name failed (see log above)" | tee -a "$LOG_FILE"
    return 1
  fi
}

# Run both refresh scripts
cd "$ROOT"

echo ""
run_script "Confluence-100 Technical Scan" \
  "$ROOT/projects/valuepickr-open-screen/scripts/build_confluence100.py"

echo ""
run_script "Paper-Trading Daily Refresh" \
  "$ROOT/projects/paper-trading/scripts/refresh.py"

# Log completion
echo "" | tee -a "$LOG_FILE"
echo "=== Trading Refresh Completed: $(date) ===" | tee -a "$LOG_FILE"
echo "Log: $LOG_FILE" | tee -a "$LOG_FILE"

# Keep last 7 days of logs
find "$LOG_DIR" -name "refresh_*.log" -mtime +7 -delete

exit 0
