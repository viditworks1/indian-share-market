# Local macOS Setup: Trading Refresh Automation

This guide sets up automated daily market-close refresh on your local Mac using Claude Code and macOS cron.

## Prerequisites

- Claude Code CLI installed locally (`brew install claude-code` or from https://claude.ai/download)
- Python 3.11+ installed (`python3 --version`)
- This repository cloned locally at `~/indian-share-market` (or adjust paths below)

## Option 1: Direct Cron (Recommended for Stability)

### 1. Set up the shell wrapper

The `run-refresh.sh` script is already created and executable. It:
- Runs confluence-100 technical scan
- Runs paper-trading daily refresh
- Logs all output to `logs/refresh_YYYYMMDD_HHMMSS.log`
- Cleans up logs older than 7 days

### 2. Add to your local macOS crontab

Edit your crontab:
```bash
crontab -e
```

Add this line to run at 4:30 PM EST on weekdays (market close is 4 PM EST):
```cron
30 16 * * 1-5 cd ~/indian-share-market && ./run-refresh.sh
```

For 4:30 PM in your timezone:
- **PST**: `30 13 * * 1-5` 
- **CST**: `30 14 * * 1-5`
- **EST**: `30 16 * * 1-5`
- **IST**: `00 02 * * 2-6` (Tuesday-Saturday, 1 AM IST next day)

### 3. Verify the cron is installed

```bash
crontab -l | grep run-refresh
```

### 4. Monitor logs

```bash
# View latest log
tail -f ~/indian-share-market/logs/refresh_*.log

# View all logs
ls -lt ~/indian-share-market/logs/
```

---

## Option 2: Claude Code Local Trigger (Option B)

If you prefer to run through Claude Code's trigger system:

### 1. On your local Mac, open Claude Code

```bash
claude
```

### 2. Create a local trigger

Use Claude Code's trigger feature to run on schedule. From Claude Code terminal:

```
/trigger create --name "Market Close Refresh" --schedule "30 16 * * 1-5" --script "cd ~/indian-share-market && ./run-refresh.sh"
```

Or use Claude's interactive interface to set up a scheduled routine.

### 3. View active triggers

```bash
/trigger list
```

---

## Testing

### Run manually (before scheduling)

```bash
cd ~/indian-share-market
./run-refresh.sh
```

This will:
1. Output progress to console
2. Create a log file in `logs/`
3. Run both refresh scripts
4. Report success/failure

### Verify Yahoo Finance access

Before scheduling, confirm direct access works:

```bash
curl -I https://query1.finance.yahoo.com/v8/finance/chart/AAPL
```

Should return HTTP 200 (not 403). If you get 403, your Mac's network is still going through a proxy/firewall.

---

## Switching Back to Remote Execution

If you need to return to remote Claude Code execution:

```bash
# Stop local cron
crontab -r

# Switch back to remote trigger in Claude Code web UI
```

---

## Troubleshooting

### Script permission denied
```bash
chmod +x ~/indian-share-market/run-refresh.sh
```

### Python not found
```bash
# Check Python path
which python3

# Update crontab to use full path if needed
/usr/local/bin/python3 ~/indian-share-market/projects/paper-trading/scripts/refresh.py
```

### Yahoo Finance still returning 403
- Verify: `curl -I https://query1.finance.yahoo.com/v8/finance/chart/AAPL`
- Check if Mac is behind a corporate proxy/firewall
- Check System Preferences → Network → Proxy settings
- Run `env | grep -i proxy` in Terminal — should be empty for local execution

### Logs location
```bash
# View latest 50 lines
tail -50 ~/indian-share-market/logs/refresh_$(ls -t logs | head -1)
```

---

## Files Modified/Created

- ✓ `run-refresh.sh` — Main execution wrapper
- ✓ `LOCAL_SETUP.md` — This file
- ✓ `logs/` — Auto-created, stores daily refresh logs

All Python scripts (refresh.py, build_confluence100.py) remain unchanged.
