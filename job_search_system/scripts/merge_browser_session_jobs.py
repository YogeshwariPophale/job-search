from __future__ import annotations

import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SYSTEM = ROOT / "job_search_system"
BOARD_FILE = SYSTEM / "data" / "extracted_jobs.json"
BROWSER_FILE = SYSTEM / "data" / "browser_session_jobs.json"
SOURCE_FEEDS = SYSTEM / "data" / "source_feeds"


def job_key(job: dict) -> str:
    return str(
        job.get("sourceRefreshId")
        or job.get("url")
        or "|".join(str(job.get(part, "")).lower() for part in ("company", "role", "location"))
    )


def load_payload(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"jobs": []}


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
            if job.get("source") in refreshed_sources:
                continue
            merged[job_key(job)] = job
    imported_count = 0
    for feed in feeds:
        for job in feed.get("jobs", []):
            if isinstance(job, dict):
                imported_count += 1
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
