from __future__ import annotations

import csv
import json
import re
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SYSTEM = ROOT / "job_search_system"
BOARD_FILE = SYSTEM / "data" / "extracted_jobs.json"
WATCHLIST_FILE = SYSTEM / "tracker" / "sponsor_friendly_data_companies.csv"
SPONSOR_SOURCE = "USCIS/H-1B sponsor watchlist"


def normalize(value: str) -> str:
    value = value.lower()
    value = re.sub(r"\b(incorporated|inc|llc|ltd|corp|corporation|company|co|plc)\b", "", value)
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def company_aliases(company: str) -> set[str]:
    values = {company}
    values.update(part.strip() for part in re.split(r"/|\(|\)", company) if part.strip())
    if "Alphabet" in company:
        values.update({"Google", "Alphabet"})
    if "NBCUniversal" in company:
        values.update({"Comcast", "NBCUniversal"})
    return {normalize(value) for value in values if normalize(value)}


def load_watchlist() -> list[dict]:
    with WATCHLIST_FILE.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        row["_aliases"] = company_aliases(row["company"])
    return rows


def find_sponsor(company: str, watchlist: list[dict]) -> dict | None:
    normalized_company = normalize(company)
    if not normalized_company:
        return None
    for row in watchlist:
        if normalized_company in row["_aliases"] or any(alias and alias in normalized_company for alias in row["_aliases"]):
            return row
    return None


def merge_signal(existing: str, signal: str) -> str:
    parts = [part.strip() for part in [existing, signal] if part and part.strip()]
    merged = []
    for part in parts:
        if part not in merged:
            merged.append(part)
    return " | ".join(merged)


def enrich_job(job: dict, watchlist: list[dict]) -> bool:
    row = find_sponsor(str(job.get("company", "")), watchlist)
    if not row:
        return False
    job["h1bSponsorSignal"] = merge_signal(
        str(job.get("h1bSponsorSignal", "")),
        f"{SPONSOR_SOURCE}: {row['sponsorship_signal']}",
    )
    job["sponsorWatchlistMatch"] = row["company"]
    job["sponsorCareerUrl"] = row["careers_url"]
    job["sponsorCategory"] = row["category"]
    job["sponsorNotes"] = row["notes"]
    return True


def main() -> int:
    payload = json.loads(BOARD_FILE.read_text(encoding="utf-8"))
    jobs = payload.get("jobs", []) if isinstance(payload, dict) else []
    watchlist = load_watchlist()
    matched = sum(1 for job in jobs if isinstance(job, dict) and enrich_job(job, watchlist))
    sources = payload.get("sources", [])
    if matched and SPONSOR_SOURCE not in sources:
        sources.append(SPONSOR_SOURCE)
    payload["sources"] = sources
    payload["sponsorEnrichedAt"] = date.today().isoformat()
    payload["sponsorWatchlistCount"] = len(watchlist)
    payload["sponsorMatchedJobCount"] = matched
    BOARD_FILE.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Enriched {matched} jobs with sponsor metadata from {len(watchlist)} watchlist companies.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
