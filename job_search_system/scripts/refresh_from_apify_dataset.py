from __future__ import annotations

import json
import os
import re
import sys
from datetime import date
from pathlib import Path
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[2]
SYSTEM = ROOT / "job_search_system"
OUTPUT = SYSTEM / "data" / "extracted_jobs.json"
LOCAL_EXPORT = SYSTEM / "connectors" / "apify_latest_dataset.json"
DEFAULT_INPUT = SYSTEM / "connectors" / "apify_linkedin_data_analyst_input.json"
LOCAL_ENV = SYSTEM / "connectors" / "apify_config.local.env"

ROLE_TERMS = [
    "data analyst",
    "business analyst",
    "business data analyst",
    "product analyst",
    "product data analyst",
    "bi analyst",
    "business intelligence",
    "business intelligence engineer",
    "operations analyst",
    "operations analytics",
    "supply chain analyst",
    "supply chain analytics",
    "manufacturing analyst",
    "manufacturing analytics",
    "risk analyst",
    "healthcare analyst",
    "healthcare analytics",
    "data science analyst",
    "data scientist",
    "analytics analyst",
    "insights analyst",
]

SKILL_TERMS = [
    "sql",
    "python",
    "dashboard",
    "analytics",
    "reporting",
    "data quality",
    "business intelligence",
    "tableau",
    "power bi",
    "statistics",
    "machine learning",
]

EXCLUDE_ROLE_TERMS = [
    "senior",
    "sr.",
    "staff",
    "principal",
    "lead analyst",
    "manager",
    "director",
    "cashier",
    "driver",
    "warehouse associate",
    "sales associate",
    "retail associate",
    "store associate",
    "customer service",
    "registered nurse",
    "security officer",
    "crew member",
    "barista",
    "cook",
    "mechanic",
    "financial analyst",
    "finops",
    "systems analyst",
    "solutions analyst",
    "applications",
]

US_LOCATION_MARKERS = [
    "united states",
    "remote",
    " al",
    " ak",
    " az",
    " ar",
    " ca",
    " co",
    " ct",
    " dc",
    " de",
    " fl",
    " ga",
    " hi",
    " ia",
    " id",
    " il",
    " in",
    " ks",
    " ky",
    " la",
    " ma",
    " md",
    " me",
    " mi",
    " mn",
    " mo",
    " ms",
    " mt",
    " nc",
    " nd",
    " ne",
    " nh",
    " nj",
    " nm",
    " nv",
    " ny",
    " oh",
    " ok",
    " or",
    " pa",
    " ri",
    " sc",
    " sd",
    " tn",
    " tx",
    " ut",
    " va",
    " vt",
    " wa",
    " wi",
    " wv",
    " wy",
]

NON_US_LOCATION_TERMS = [
    "canada",
    "india",
    "united kingdom",
    "england",
    "ireland",
    "dublin",
    "luxembourg",
    "germany",
    "france",
    "singapore",
    "australia",
]


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def first_value(item: dict, names: list[str], default: str = "") -> str:
    for name in names:
        value = item.get(name)
        if value not in (None, ""):
            return str(value).strip()
    return default


def load_local_env() -> None:
    if not LOCAL_ENV.exists():
        return
    for line in LOCAL_ENV.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        name, value = stripped.split("=", 1)
        name = name.strip()
        value = value.strip().strip('"').strip("'")
        if name and value and not os.getenv(name):
            os.environ[name] = value


def apify_request(url: str, payload: dict | None = None, token: str = "") -> object:
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "YogeshwariJobSearchSystem/1.0",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = Request(
        url,
        data=body,
        headers=headers,
        method="POST" if payload is not None else "GET",
    )
    with urlopen(request, timeout=360) as response:  # noqa: S310
        return json.loads(response.read().decode("utf-8"))


def actor_identifier() -> str:
    actor_id = os.getenv("APIFY_ACTOR_ID", "").strip()
    actor_task_id = os.getenv("APIFY_TASK_ID", "").strip()
    if actor_task_id:
        return f"actor-tasks/{actor_task_id}"
    if actor_id:
        return f"acts/{actor_id.replace('/', '~')}"
    return ""


def load_actor_input() -> dict:
    input_file = Path(os.getenv("APIFY_INPUT_FILE", str(DEFAULT_INPUT))).expanduser()
    if not input_file.is_absolute():
        input_file = ROOT / input_file
    return json.loads(input_file.read_text(encoding="utf-8"))


def run_apify_actor() -> list[dict]:
    token = os.getenv("APIFY_TOKEN", "").strip()
    identifier = actor_identifier()
    if not token or not identifier:
        return []

    timeout_seconds = int(os.getenv("APIFY_RUN_TIMEOUT_SECONDS", "300"))
    url = f"https://api.apify.com/v2/{identifier}/run-sync-get-dataset-items?clean=true&format=json&timeout={timeout_seconds}"
    result = apify_request(url, load_actor_input(), token)
    return result if isinstance(result, list) else []


def fetch_apify_dataset_items() -> list[dict]:
    token = os.getenv("APIFY_TOKEN", "").strip()
    dataset_id = os.getenv("APIFY_DATASET_ID", "").strip()
    if not token or not dataset_id:
        return []

    url = f"https://api.apify.com/v2/datasets/{dataset_id}/items?clean=true&format=json"
    result = apify_request(url, token=token)
    return result if isinstance(result, list) else []


def load_items() -> tuple[str, list[dict]]:
    actor_items = run_apify_actor()
    if actor_items:
        return "Apify actor run", actor_items

    dataset_items = fetch_apify_dataset_items()
    if dataset_items:
        return "Apify dataset API", dataset_items

    if LOCAL_EXPORT.exists():
        payload = json.loads(LOCAL_EXPORT.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            return "Apify local export", payload.get("items") or payload.get("jobs") or []
        return "Apify local export", payload

    return "Apify connector", []


def normalize_job(item: dict) -> dict:
    company = first_value(item, ["company", "companyName", "organization", "hiringOrganizationName"], "Unknown company")
    role = first_value(item, ["role", "title", "jobTitle", "positionName"], "Unknown role")
    location = first_value(item, ["location", "jobLocation", "formattedLocation", "address"], "United States")
    url = first_value(item, ["url", "jobUrl", "jobPostingUrl", "link"])
    apply_url = first_value(item, ["applyUrl", "apply_url", "applicationUrl", "directApplyUrl"], url)
    posted = first_value(item, ["posted", "postedAt", "datePosted", "publishedAt", "postedDate"], "Fresh connector result")
    salary = first_value(item, ["salary", "salaryText", "compensation"], "Not listed")
    description = first_value(item, ["description", "jobDescription", "summary", "text"], f"{role} at {company} in {location}")
    source = first_value(item, ["source", "site", "platform"], "LinkedIn via Apify")
    source_refresh_id = first_value(item, ["sourceRefreshId", "id", "jobId"])

    return {
        "sourceRefreshId": source_refresh_id or f"apify-{date.today().isoformat()}-{slug(company)}-{slug(role)}-{slug(location)}",
        "source": source,
        "company": company,
        "role": role,
        "location": location,
        "salary": salary,
        "posted": posted,
        "url": url,
        "applyUrl": apply_url,
        "description": description,
    }


def is_relevant_job(job: dict) -> bool:
    role = str(job.get("role", "")).lower()
    location = f" {str(job.get('location', '')).lower().replace(',', ' ')} "
    text = " ".join(str(job.get(key, "")) for key in ("role", "description", "company", "source")).lower()

    if any(term in role for term in EXCLUDE_ROLE_TERMS):
        return False
    if any(term in location for term in NON_US_LOCATION_TERMS):
        return False
    if not any(marker in location for marker in US_LOCATION_MARKERS):
        return False

    has_role_match = any(term in role for term in ROLE_TERMS)
    has_skill_match = any(term in text for term in SKILL_TERMS)
    return has_role_match and has_skill_match


def item_passes_actor_filters(item: dict) -> bool:
    dynamic_match = item.get("dynamicFilterMatch")
    if dynamic_match is False:
        return False
    return True


def preserved_non_apify_jobs() -> list[dict]:
    if not OUTPUT.exists():
        return []
    try:
        payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    jobs = payload.get("jobs", []) if isinstance(payload, dict) else []
    preserved = []
    for job in jobs:
        if not isinstance(job, dict):
            continue
        source = str(job.get("source", "")).lower()
        if "apify" not in source:
            preserved.append(job)
    return preserved


def merge_jobs(primary_jobs: list[dict], extra_jobs: list[dict]) -> list[dict]:
    merged: dict[str, dict] = {}
    for job in [*extra_jobs, *primary_jobs]:
        key = str(
            job.get("sourceRefreshId")
            or job.get("url")
            or "|".join(str(job.get(part, "")).lower() for part in ("company", "role", "location"))
        )
        merged[key] = {**merged.get(key, {}), **job}
    return list(merged.values())


def main() -> int:
    load_local_env()
    source, items = load_items()
    if not items:
        print("No Apify items found. Set APIFY_TOKEN plus APIFY_ACTOR_ID/APIFY_TASK_ID, set APIFY_DATASET_ID, or write connectors/apify_latest_dataset.json.")
        return 2

    normalized_jobs = [normalize_job(item) for item in items if isinstance(item, dict) and item_passes_actor_filters(item)]
    jobs = [job for job in normalized_jobs if is_relevant_job(job)]
    if not jobs:
        print(f"Apify returned {len(normalized_jobs)} items, but none matched the Data Analyst relevance filters. Keeping the previous job file.")
        return 3
    preserved_jobs = preserved_non_apify_jobs()
    merged_jobs = merge_jobs(jobs, preserved_jobs)
    payload = {
        "generatedAt": date.today().isoformat(),
        "sources": [source, *sorted({job.get("source", "Browser session import") for job in preserved_jobs})],
        "rawItemCount": len(normalized_jobs),
        "filteredOutCount": len(normalized_jobs) - len(jobs),
        "preservedNonApifyCount": len(preserved_jobs),
        "jobs": merged_jobs,
    }
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(merged_jobs)} jobs to {OUTPUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
