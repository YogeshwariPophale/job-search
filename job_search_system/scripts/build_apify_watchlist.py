from __future__ import annotations

import csv
import json
from datetime import date
from pathlib import Path


SYSTEM = Path(__file__).resolve().parents[1]
WATCHLIST = SYSTEM / "watchlist_companies.csv"
OUTPUT = SYSTEM / "connectors" / "apify_company_watchlist_seed.json"

TARGET_ROLES = [
    "Data Analyst",
    "Business Data Analyst",
    "Data Science Intern",
    "Machine Learning Intern",
    "Manufacturing Data Analyst",
    "Operations Analyst",
    "Supply Chain Analytics Intern",
    "Business Intelligence Analyst",
    "Data Engineer Intern",
]

PREFERRED_LOCATIONS = [
    "United States",
    "Remote",
    "California",
    "Riverside, CA",
]


def split_queries(value: str) -> list[str]:
    return [item.strip() for item in value.split(";") if item.strip()]


def build_seed() -> dict:
    with WATCHLIST.open(newline="", encoding="utf-8") as handle:
        companies = list(csv.DictReader(handle))

    start_urls = []
    for company in companies:
        start_urls.append(
            {
                "url": company["careers_url"].strip(),
                "userData": {
                    "company": company["company"].strip(),
                    "priorityQueries": split_queries(company.get("priority_queries", "")),
                    "category": company.get("category", "").strip(),
                    "sponsorshipSignal": company.get("sponsorship_signal", "").strip(),
                    "notes": company.get("notes", "").strip(),
                },
            }
        )

    return {
        "generatedAt": date.today().isoformat(),
        "purpose": "Seed input for an Apify job-listing actor or connector workflow.",
        "freshnessWindowHours": 48,
        "schedule": "Run every 24 hours, then import only jobs posted in the last 24-48 hours.",
        "targetRoles": TARGET_ROLES,
        "preferredLocations": PREFERRED_LOCATIONS,
        "startUrls": start_urls,
        "rankingRules": [
            "Prefer direct company career-page listings over reposted boards.",
            "Prefer internship, new-grad, entry-level, junior, analyst, BI, operations, supply-chain, manufacturing analytics, data science, and data engineering roles.",
            "Keep senior, principal, staff, and manager roles only for strategic watchlist companies and flag them for networking first.",
            "Discard roles with unclear posting dates unless they are from a high-priority company and still open on the company site.",
        ],
        "expectedFields": [
            "company",
            "role",
            "location",
            "salary",
            "posted",
            "source",
            "url",
            "applyUrl",
            "description",
        ],
        "jobBoardOutput": "job_search_system/data/extracted_jobs.json",
    }


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(build_seed(), indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
