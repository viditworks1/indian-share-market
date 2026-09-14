# Quick Start: Local Mac Execution

## What's Ready

- ✓ `run-refresh.sh` — Fully configured execution wrapper
- ✓ Scripts compile without errors
- ✓ Python 3.11+ verified available
- ✓ All project dependencies present

## 1. First Run (Test)

On your Mac:

```bash
cd ~/indian-share-market
./run-refresh.sh
```

This runs both:
1. Confluence-100 technical scan
2. Paper-trading daily refresh

Output goes to console + `logs/refresh_YYYYMMDD_HHMMSS.log`

**Expected time:** 2-5 minutes depending on network/data availability

## 2. Verify Yahoo Finance Access

```bash
curl -I https://query1.finance.yahoo.com/v8/finance/chart/AAPL
```

Should return `HTTP/1.1 200 OK` (or redirect). If `403 Forbidden`, your Mac is going through a proxy that blocks Yahoo.

## 3. Schedule on macOS Cron (Recommended)

Edit your crontab:
```bash
crontab -e
```

Add ONE line (choose your timezone):

**EST (4:30 PM):**
```
30 16 * * 1-5 cd ~/indian-share-market && ./run-refresh.sh
```

**CST (3:30 PM):**
```
30 15 * * 1-5 cd ~/indian-share-market && ./run-refresh.sh
```

**PST (1:30 PM):**
```
30 13 * * 1-5 cd ~/indian-share-market && ./run-refresh.sh
```

**IST (1:00 AM next day, Tue-Sat):**
```
00 01 * * 2-6 cd ~/indian-share-market && ./run-refresh.sh
```

Save and exit (Ctrl+X then Y in nano, :wq in vi).

## 4. Verify Cron Is Active

```bash
crontab -l | grep run-refresh
```

Should show your line.

## 5. Monitor Execution

Check logs anytime:
```bash
tail -f ~/indian-share-market/logs/refresh_*.log
```

Or list all logs:
```bash
ls -lt ~/indian-share-market/logs/
```

## Done

Your trading refresh is now automated. Cron will run it every weekday at market close.

---

## Optional: Use Claude Code Trigger

If you prefer Claude Code's trigger system instead of cron:

From Claude Code on your Mac:

```bash
claude
```

Then create a trigger:
```
I want a scheduled routine that runs every weekday at 16:30 UTC (market close). 
The routine should execute: cd ~/indian-share-market && ./run-refresh.sh
Name it "Market Close Refresh"
```

Claude Code will set up the local trigger for you.

---

## Removing Remote Cloud Execution

The remote scheduled routine that was failing is no longer needed. To clean it up:

1. Log into https://claude.ai/code
2. Find and delete the old "Daily market-close refresh" routine
3. Keep only the new local one (cron or Claude trigger)

---

## Troubleshooting

### "Permission denied" when running script
```bash
chmod +x ~/indian-share-market/run-refresh.sh
```

### "No such file" error in cron
- Use absolute path: `/Users/YOUR_USERNAME/indian-share-market/run-refresh.sh`
- Or: `$HOME/indian-share-market/run-refresh.sh`

### Yahoo Finance 403 Forbidden
- Your Mac is behind a proxy/firewall that blocks Yahoo
- Test: `curl -v https://query1.finance.yahoo.com` (check response headers)
- Solution: Talk to your network administrator or use a different data source

### Script runs but no log file
- Check permissions: `ls -la ~/indian-share-market/logs/`
- Make sure logs directory is writable: `chmod 755 ~/indian-share-market/logs/`

### Cron never runs
- Check that cron daemon is running: `ps aux | grep cron`
- Verify macOS privacy settings allow cron (System Prefs → Security & Privacy → Full Disk Access → add Terminal.app)
- Check system log: `log stream --predicate 'process == "cron"'`

---

## Next Steps

1. **Right now:** Run `./run-refresh.sh` manually to test
2. **If successful:** Add to crontab (Step 3 above)
3. **Verify:** Check logs after first automatic run tomorrow
4. **Done:** Monitor weekly for any issues

No remote cloud execution needed anymore. Direct local execution is faster and more reliable.
