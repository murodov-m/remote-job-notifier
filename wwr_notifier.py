import argparse
import json
import os
from pathlib import Path

import feedparser
import requests
from dotenv import load_dotenv


def load_seen(path: Path) -> set:
    if path.exists():
        try:
            return set(json.loads(path.read_text(encoding="utf-8")))
        except Exception:
            return set()
    return set()


def save_seen(path: Path, seen: set) -> None:
    path.write_text(json.dumps(sorted(seen), ensure_ascii=False, indent=2), encoding="utf-8")


def matches_keywords(entry, keywords):
    if not keywords:
        return True
    haystack = " ".join([
        entry.get("title", ""),
        entry.get("summary", ""),
        entry.get("description", ""),
        " ".join(tag.get("term", "") for tag in entry.get("tags", [])),
    ]).lower()
    return any(k.lower() in haystack for k in keywords)


def extract_company(entry):
    for key in ("author", "wwr_company", "company"):
        value = entry.get(key)
        if value:
            return value
    return "Unknown company"


def format_message(entry):
    title = entry.get("title", "Untitled job")
    link = entry.get("link", "")
    company = extract_company(entry)
    published = entry.get("published", "Unknown date")
    categories = ", ".join(tag.get("term", "") for tag in entry.get("tags", [])) or "Unknown category"
    return (
        f"📢 New WWR job\n"
        f"Title: {title}\n"
        f"Company: {company}\n"
        f"Category: {categories}\n"
        f"Posted: {published}\n"
        f"Link: {link}"
    )


def send_telegram(bot_token, chat_id, text):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    r = requests.post(url, json={"chat_id": chat_id, "text": text, "disable_web_page_preview": True}, timeout=30)
    r.raise_for_status()


parser = argparse.ArgumentParser()
parser.add_argument("--dry-run", action="store_true")
parser.add_argument("--bootstrap", action="store_true")
parser.add_argument("--limit", type=int, default=20)
args = parser.parse_args()

load_dotenv()
feed_url = os.getenv("FEED_URL", "https://weworkremotely.com/remote-jobs.rss")
keywords = [k.strip() for k in os.getenv("KEYWORDS", "").split(",") if k.strip()]
seen_file = Path(os.getenv("SEEN_FILE", "seen_jobs.json"))
bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
chat_id = os.getenv("TELEGRAM_CHAT_ID", "")

feed = feedparser.parse(feed_url)
entries = list(feed.entries)[: args.limit]
seen = load_seen(seen_file)

new_entries = [e for e in entries if e.get("link") not in seen and matches_keywords(e, keywords)]

if args.bootstrap:
    for e in entries:
        if e.get("link"):
            seen.add(e.get("link"))
    save_seen(seen_file, seen)
    print(f"Bootstrapped {len(entries)} jobs into {seen_file}")
    raise SystemExit(0)

for entry in reversed(new_entries):
    text = format_message(entry)
    if args.dry_run:
        print(text)
        print("-" * 60)
    else:
        if not bot_token or not chat_id:
            raise RuntimeError("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set unless using --dry-run")
        send_telegram(bot_token, chat_id, text)
    if entry.get("link"):
        seen.add(entry.get("link"))

save_seen(seen_file, seen)
print(f"Processed {len(entries)} entries, found {len(new_entries)} new matching jobs")