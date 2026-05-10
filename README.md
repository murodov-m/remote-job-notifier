# We Work Remotely notifier prototype

This prototype watches the **all jobs** We Work Remotely RSS feed and sends Telegram alerts for newly seen jobs.

Feed used:

- All jobs: `https://weworkremotely.com/remote-jobs.rss`

## Files

- `wwr_notifier.py` — main script
- `.env.example` — environment variables template
- `requirements.txt` — Python dependencies
- `github-actions-example.yml` — optional scheduled workflow example
- `seen_jobs.json` — created automatically after first run

## Features

- Checks the WWR **all jobs** feed
- Sends a Telegram message for each newly seen posting
- Stores seen links locally to avoid duplicates
- Supports optional keyword filtering, but defaults to **all jobs**
- Supports `--dry-run` for testing without Telegram messages

## Setup

1. Create a Telegram bot with [@BotFather](https://t.me/BotFather).
2. Get your personal chat ID by messaging your bot, then visiting:
   `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
3. Copy `.env.example` to `.env` and fill in values.
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Run:
   ```bash
   python wwr_notifier.py --bootstrap
   ```
   This saves current jobs as already seen, so you only get future alerts.
6. Later run normally:
   ```bash
   python wwr_notifier.py
   ```

## Optional flags

- `--dry-run` — print new jobs without sending Telegram messages
- `--bootstrap` — mark current feed items as seen without alerting
- `--limit 5` — only process the latest N items

## GitHub Actions

You can use the included workflow as a starting point for running every 15 minutes.

## Notes

- By default the script monitors **all categories** through WWR's public all-jobs RSS feed.
- Optional keyword filtering is off by default. Leave `KEYWORDS=` empty to get alerts for all jobs.
