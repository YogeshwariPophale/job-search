# Daily Refresh Agent

Use this prompt when you want Codex to refresh the job board from logged-in platforms, connector datasets, and watchlist companies.

```text
Run my daily job refresh.

Use the logged-in in-app browser tabs for:
- Simplify dashboard: https://simplify.jobs/dashboard
- Handshake jobs: https://app.joinhandshake.com/stu/postings
- LinkedIn jobs: https://www.linkedin.com/jobs/search/?keywords=Data%20Analyst%20visa%20sponsorship&location=United%20States
- Jobright recommendations: https://jobright.ai/jobs/recommend
- Rewriting the Code / GradLeaders jobs: https://candidate.gradleaders.com/RewritingTheCode/Candidates/Authenticated/Jobs/SearchJobs.aspx

Use public/non-login job boards:
- Jobot Data Analytics jobs: https://jobot.com/find/full-time-data-analytics-jobs

Use connector inputs when available:
- job_search_system/connectors/apify_company_watchlist_seed.json
- Any exported Apify or connector dataset the user provides

Also check the watchlist in:
- job_search_system/watchlist_companies.csv
- job_search_system/search_platforms.md
- job_search_system/tracker/sponsor_friendly_data_companies.csv
- job_search_system/tracker/job_platform_sources.csv

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

For each source:
1. Extract current role title, company, location, salary if visible, posted age/date, source URL, direct apply URL when visible, and short description.
2. Prefer roles posted in the last 24 hours; accept 48-hour-old roles when fit is strong.
3. Prefer direct company career-page listings over LinkedIn Easy Apply reposts.
4. Prefer internships, new-grad, entry-level, junior, analyst, data science, data engineering, BI, operations, manufacturing, and supply chain analytics roles.
5. Prefer companies marked with "Large H-1B employer signal" or "Known H-1B filing signal"; still verify sponsorship wording on each posting.
6. Keep senior/principal/manager roles only if they are from a high-priority company, but let the board score them lower.
7. Write the merged result to `job_search_system/data/extracted_jobs.json`.
8. Run `job_search_system/scripts/generate_tailored_resumes.py`.
9. Confirm that the top 15 roles have ATS-friendly tailored PDF resumes under `output/pdf/tailored_resumes/`.
10. Do not submit applications or send messages during refresh.
11. If a platform is logged out, report exactly which platform needs sign-in and continue with the sources that are accessible.
12. After writing the file and generating resumes, reload `job_search_system/job_board.html`; the board will auto-import new jobs, update resume and apply links, and de-duplicate old ones.
```

## How Daily Import Works

The job board fetches `data/extracted_jobs.json` on page load and when you click `Import Daily Refresh`. It saves new jobs into browser local storage, updates existing jobs with new tailored resume and direct apply links, and skips duplicates by company, role, location, and URL.

The resume generator selects the top 15 jobs by fit score, extracts supported keywords, avoids ungrounded claims, and creates one-page ATS-friendly PDFs. Unsupported tools such as Tableau, Power BI, AWS, Azure, GCP, Airflow, dbt, Kubernetes, Snowflake, and Looker are flagged in the tailoring notes instead of being claimed as experience.

Scoring standards:

- Do not lower standards to make a role appear stronger than it is.
- Non-seniority, target-family roles should clear 85+ tailored ATS match when truthful keyword coverage supports it.
- Senior, principal, manager, staff, or high-years-experience roles must remain capped and flagged for networking first.
- Role fit and tailored ATS match are different metrics. Do not use keyword alignment to hide seniority or eligibility risk.
