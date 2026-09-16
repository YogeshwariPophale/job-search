from __future__ import annotations

import json
import re
from datetime import date, datetime, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SYSTEM = ROOT / "job_search_system"
BOARD_FILE = SYSTEM / "data" / "extracted_jobs.json"
BROWSER_FILE = SYSTEM / "data" / "browser_session_jobs.json"
SOURCE_FEEDS = SYSTEM / "data" / "source_feeds"
MAX_POSTING_AGE_DAYS = 3


def job_key(job: dict) -> str:
    return str(
        job.get("sourceRefreshId")
        or job.get("url")
        or "|".join(str(job.get(part, "")).lower() for part in ("company", "role", "location"))
    )


def load_payload(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"jobs": []}


def parse_posted_date(value: object) -> date | None:
    if value in (None, ""):
        return None
    text = str(value).strip()
    if not text:
        return None

    lowered = text.lower()
    today = date.today()
    if lowered in {"today", "just posted"}:
        return today
    if lowered in {"yesterday", "1 day ago"}:
        return today - timedelta(days=1)

    match = re.search(r"(\d+)\s+(minute|minutes|hour|hours|day|days)\s+ago", lowered)
    if match:
        amount = int(match.group(1))
        unit = match.group(2)
        if unit.startswith(("minute", "hour")):
            return today
        return today - timedelta(days=amount)

    normalized = text.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(normalized).date()
    except ValueError:
        pass

    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%b %d, %Y", "%B %d, %Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


def is_recent_posting(job: dict) -> bool:
    posted_date = parse_posted_date(job.get("posted"))
    if posted_date is None:
        return False
    age = date.today() - posted_date
    return timedelta(days=0) <= age <= timedelta(days=MAX_POSTING_AGE_DAYS)


def source_payloads() -> list[dict]:
    payloads = [load_payload(BROWSER_FILE)]
    if SOURCE_FEEDS.exists():
        for path in sorted(SOURCE_FEEDS.glob("*.json")):
            payloads.append(load_payload(path))
    return payloads


def main() -> int:
    board = load_payload(BOARD_FILE)
    feeds = source_payloads()
    refreshed_sources = {
        source
        for feed in feeds
        for source in feed.get("sources", [])
        if source
    }

    merged: dict[str, dict] = {}
    for job in board.get("jobs", []):
        if isinstance(job, dict):
            if not is_recent_posting(job):
                continue
            if job.get("source") in refreshed_sources:
                continue
            merged[job_key(job)] = job
    imported_count = 0
    for feed in feeds:
        for job in feed.get("jobs", []):
            if isinstance(job, dict):
                imported_count += 1
                if not is_recent_posting(job):
                    continue
                merged[job_key(job)] = {**merged.get(job_key(job), {}), **job}

    sources = []
    for feed in [board, *feeds]:
        for source in feed.get("sources", []):
            if source and source not in sources:
                sources.append(source)

    output = {
        **board,
        "generatedAt": date.today().isoformat(),
        "sources": sources or ["Browser session import"],
        "browserImportedAt": date.today().isoformat(),
        "jobs": list(merged.values()),
    }
    BOARD_FILE.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"Merged {imported_count} source-feed jobs; board now has {len(output['jobs'])} jobs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
