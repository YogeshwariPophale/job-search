from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SYSTEM = ROOT / "job_search_system"
WATCHLIST_FILE = SYSTEM / "tracker" / "sponsor_friendly_data_companies.csv"
APIFY_INPUT_FILE = SYSTEM / "connectors" / "apify_linkedin_data_analyst_input.json"


def main() -> int:
    with WATCHLIST_FILE.open(newline="", encoding="utf-8") as handle:
        companies = [row["company"] for row in csv.DictReader(handle)]

    payload = json.loads(APIFY_INPUT_FILE.read_text(encoding="utf-8"))
    existing = payload.get("companyInclude", [])
    merged = []
    for company in [*existing, *companies]:
        if company and company not in merged:
            merged.append(company)
    payload["companyInclude"] = merged
    payload["companyIncludeSource"] = "job_search_system/tracker/sponsor_friendly_data_companies.csv"
    payload["companyIncludeCount"] = len(merged)
    APIFY_INPUT_FILE.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Synced {len(merged)} H-1B sponsor/watchlist companies into Apify companyInclude.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
