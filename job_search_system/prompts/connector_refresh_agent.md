# Connector Refresh Agent

Use this prompt after a connector run from Apify or another live job-listing source.

```text
Run my connector refresh.

Inputs:
- Connector seed: job_search_system/connectors/apify_company_watchlist_seed.json
- Optional Apify export: job_search_system/connectors/apify_latest_dataset.json
- Watchlist: job_search_system/watchlist_companies.csv
- Sponsor-friendly tracking database: job_search_system/tracker/sponsor_friendly_data_companies.csv
- Candidate profile: job_search_system/profile/candidate_profile.md
- Preferences: job_search_system/profile/preferences.yml
- Current board import file: job_search_system/data/extracted_jobs.json

Use the connector dataset if available. If a connector is not available, use the watchlist career URLs directly.

Target freshness:
- Prefer jobs posted in the last 24 hours.
- Accept jobs posted in the last 48 hours if fit is strong.
- Keep older jobs only when the company career page confirms the listing is still open and the role is highly aligned.

Target roles:
- Data Analyst
- Business Data Analyst
- Data Science Intern
- Machine Learning Intern
- Manufacturing Data Analyst
- Operations Analyst
- Supply Chain Analytics Intern
- Business Intelligence Analyst
- Data Engineer Intern

For each job, extract:
- company
- role
- location
- salary, if visible
- posted age/date
- source
- job URL
- direct apply URL, if visible
- short description
- freshness note, such as "posted today", "posted 1 day ago", or "company page confirms open"

Ranking rules:
1. Prioritize fresh direct company postings over LinkedIn Easy Apply reposts.
2. Prefer internships, new-grad, entry-level, junior, analyst, BI, operations, manufacturing, supply-chain analytics, data science, and data engineering roles.
3. Prefer companies marked with "Large H-1B employer signal" or "Known H-1B filing signal"; still verify sponsorship wording on each posting.
4. Flag senior/principal/staff/manager roles or roles requiring 5+ years of experience.
5. De-duplicate by company, role, location, and URL.
6. Keep the top roles that clear the normal fit threshold, then write them to job_search_system/data/extracted_jobs.json.
7. If using an Apify export or dataset API, run python job_search_system/scripts/refresh_from_apify_dataset.py first.
8. Run python job_search_system/scripts/generate_tailored_resumes.py.
9. Do not apply or send outreach during refresh.

After the import file and tailored resumes are updated, open job_search_system/job_board.html and click Import Daily Refresh if needed.
```

## Output Shape

Write `job_search_system/data/extracted_jobs.json` with this shape:

```json
{
  "generatedAt": "YYYY-MM-DD",
  "source": "connector refresh",
  "jobs": [
    {
      "sourceRefreshId": "connector-YYYY-MM-DD-company-role-location",
      "company": "Company",
      "role": "Role",
      "location": "Location",
      "salary": "",
      "posted": "posted today",
      "source": "Apify connector - company career page",
      "url": "https://...",
      "applyUrl": "https://...",
      "description": "Short but specific job description."
    }
  ]
}
```
