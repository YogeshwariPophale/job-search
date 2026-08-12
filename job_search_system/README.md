# Yogeshwari's Codex Job Search System

This is a Codex-compatible version of the "AI Job Search System" guide, personalized from the base resume in `base/yogeshwari_resume_UCR_base_profile.md`.

It is designed for this workflow:

1. Use `job_board.html` as the personal job board dashboard.
2. Add roles manually, ask Codex to search current openings, or run a connector refresh from company career pages.
3. Score each role against Yogeshwari's profile.
4. Use `Apply Now` to open the listing or company application page.
5. Generate a tailored resume, cover letter, outreach, and screening answers.
6. Track the application, follow-ups, interview steps, and outcomes.

Codex can help search, tailor, fill forms, and draft messages. Codex should not submit an application without explicit approval from Yogeshwari.

## Quick Start

Open the compiled overview site:

```text
job_search_system/index.html
```

Open the working job board:

```text
job_search_system/job_board.html
```

Open the phone-friendly app:

```text
job_search_system/phone_app.html
```

For phone access and automatic refresh, run the live server:

```text
powershell -ExecutionPolicy Bypass -File job_search_system/scripts/start_live_app.ps1
```

Then open the phone URL printed by the script. Keep the computer awake and on the same Wi-Fi. The desktop board and phone app poll for updates every 60 seconds.

When you find a job listing, paste the listing or send the URL and ask:

```text
Use my job_search_system to score this role and create a tailored resume package.
```

Codex will:

- Read `profile/candidate_profile.md`
- Read `profile/job_search_profile.md`
- Check `profile/preferences.yml`
- Score the job with `scripts/score_job.py`
- Write application notes into `outputs/`
- Update `tracker/applications.csv` if you approve tracking it

You can also open `job_board.html` directly in a browser. It is self-contained and stores jobs in the browser's local storage.

## GitHub Pages Deploy

This repository includes a GitHub Actions workflow at `.github/workflows/deploy-pages.yml`.
When the repository is pushed to GitHub on the `master` branch, GitHub Pages publishes
the static site from `job_search_system/` and includes generated files from `output/`
so the resume PDF download links continue to work.

After pushing, enable GitHub Pages in the repository settings with source set to
`GitHub Actions`. The live site will open at the Pages URL shown by the workflow run.

## Folder Map

- `profile/` - resume-derived profile, career preferences, and missing info
- `prompts/` - reusable Codex prompts for search, tailoring, applying, and follow-up
- `templates/` - copy/paste templates for job listings, screening answers, and outreach
- `tracker/` - application and networking trackers
- `scripts/` - lightweight helper scripts
- `connectors/` - Apify/connector refresh setup for fresh company career-page jobs
- `outputs/` - generated job-specific materials
- `index.html` - compiled overview site showing what has been built
- `job_board.html` - self-contained job board dashboard with filters, stats, scoring, local save, CSV export, direct Apply Now links, and Agent Prompt copying
- `data/extracted_jobs.json` - latest daily refresh payload imported by the board
- `data/tailored_resumes.json` - manifest of generated role-specific resume PDFs
- `tracker/sponsor_friendly_data_companies.csv` - 133-company sponsor-friendly tracking database for Data Analyst and adjacent analytics roles
- `tracker/job_platform_sources.csv` - priority job boards, including Simplify, Jobot, Handshake, and LinkedIn

## Operating Rules

- Keep every resume claim grounded in the base profile or confirmed by Yogeshwari.
- Tailor keywords and ordering, but do not invent degrees, employers, tools, projects, dates, publications, certifications, or metrics.
- Ask before using sensitive personal details not already in the profile.
- Ask before submitting applications, sending emails, messaging recruiters, or accepting terms.
- Save each tailored package under `outputs/company_role_date/`.

## Guide Mapping

- Step 0 assets: resume copied into `base/`; LinkedIn/GitHub captured in profile.
- Step 1 job search profile: `profile/job_search_profile.md`.
- Step 2 personal job board: `job_board.html`.
- Step 3 adding jobs: use the dashboard Add Job form or `prompts/01_search_agent.md`.
- Step 4 application agent: `prompts/full_application_agent_codex.md`.
- Step 5 tracker: `tracker/applications.csv`, with a Notion-compatible column shape.
- Job Search Coach modules: `prompts/job_search_coach_router.md`.
- Weekly refresh: `prompts/01_search_agent.md` and `prompts/05_follow_up_agent.md`.

## Daily Refresh

Ask Codex:

```text
Run my daily job refresh.
```

Codex will use `prompts/daily_refresh_agent.md` to extract roles from logged-in Jobright and GradLeaders pages, then check watchlist company career pages. Results are written to `data/extracted_jobs.json`.

After extraction, Codex runs `scripts/generate_tailored_resumes.py`. The script selects the top 15 jobs, extracts essential supported keywords, generates one-page ATS-friendly tailored PDFs, writes tailoring notes, and updates the board data with `Resume PDF` download links.

The job board imports that file every time it loads and when you click `Import Daily Refresh`. It de-duplicates by company, role, location, and URL, re-scores jobs against Yogeshwari's profile, and updates existing jobs with new resume links, direct apply links, base-vs-tailored match scores, keyword coverage, missing keyword notes, and recommended actions.

When served with `scripts/live_server.py`, the board and phone app read from `/api/jobs` first, then fall back to `data/extracted_jobs.json`. This keeps the site online locally and makes new connector results appear without reopening the page.

`Apply Now` opens the direct application URL when available, otherwise the job listing URL, otherwise the mapped career page for watchlist companies. `Agent Prompt` copies the Codex application workflow for resume tailoring, outreach, and application-answer drafting.

The tailoring rule is "highest truthful match": keywords are incorporated only when they are supported by Yogeshwari's actual resume, coursework, projects, or experience. Unsupported tools are flagged in notes instead of being claimed.

## Connector Refresh

The article workflow has been added as a connector-first path:

```text
Run my connector refresh.
```

Use `connectors/apify_company_watchlist_seed.json` as the seed input for an Apify job-listing actor or any connector that can read company career pages, Greenhouse, Lever, Workday, Indeed, or Google Jobs. It is generated from `watchlist_companies.csv` by:

```text
python job_search_system/scripts/build_apify_watchlist.py
```

If `python` is not on PATH, ask Codex to regenerate the seed; Codex can use its bundled Python runtime.

Connector refreshes prioritize postings from the last 24-48 hours, direct company career-page links, and early-career data roles. The output still lands in `data/extracted_jobs.json`, so the existing board import and tailored resume generation flow stays the same.

For automatic background refresh, start the live server with a command that updates `data/extracted_jobs.json`:

```text
powershell -ExecutionPolicy Bypass -File job_search_system/scripts/start_live_app.ps1 -UseApifyRefresh
```

`refresh_from_apify_dataset.py` supports either:

- environment variables `APIFY_TOKEN` plus `APIFY_ACTOR_ID` or `APIFY_TASK_ID` to run the scraper automatically
- environment variables `APIFY_TOKEN` and `APIFY_DATASET_ID` to read an existing dataset
- a local Apify export at `job_search_system/connectors/apify_latest_dataset.json`

Without a configured connector/API command, the app refreshes the displayed data from disk but cannot discover brand-new jobs by itself.

Configure Apify once with:

```text
powershell -ExecutionPolicy Bypass -File job_search_system/scripts/configure_apify_refresh.ps1 -ApifyToken "YOUR_TOKEN" -ActorId "ACTOR_OWNER/ACTOR_NAME"
```

Or use `-TaskId "YOUR_TASK_ID"` if you create an Apify task in the Apify console.

To keep the app online after Windows login, install the startup task:

```text
powershell -ExecutionPolicy Bypass -File job_search_system/scripts/install_live_app_startup.ps1 -UseApifyRefresh
```

If Task Scheduler is blocked, copy `job_search_system/scripts/start_job_search_live_app.cmd` into the Windows Startup folder. That fallback has been used on this machine.

Remove it with:

```text
powershell -ExecutionPolicy Bypass -File job_search_system/scripts/uninstall_live_app_startup.ps1
```

## Sponsor-Friendly Company Database

`watchlist_companies.csv` and `tracker/sponsor_friendly_data_companies.csv` now track 133 large companies with public H-1B filing/sponsorship signals and plausible Data Analyst or adjacent analytics openings.

Use this prompt:

```text
Search the sponsor-friendly company database for fresh Data Analyst roles.
```

Prioritize direct career pages and these title families:

- Data Analyst
- Business Analyst
- Business Data Analyst
- Product Analyst
- Business Intelligence Analyst
- Operations Analyst
- Supply Chain Analytics
- Manufacturing Analytics
- Risk Analyst
- Healthcare Analytics
- Data Science Analyst

Important: past H-1B filing history is a signal, not a promise. Always check each job posting's sponsorship language before applying.

## Job Search Coach Modules

The second guide has been adapted into Codex prompts:

- Module 1 - ATS Resume Optimizer: use the existing `prompts/03_tailor_resume.md` and `prompts/full_application_agent_codex.md`.
- Module 2 - LinkedIn Quick Feedback: use `prompts/linkedin_quick_feedback.md`.
- Module 3 - LinkedIn Deep Audit: use `prompts/linkedin_deep_audit.md`.
- Module 4 - Interview Prep Planner: use `prompts/interview_prep_planner.md`.

For broad requests, start with:

```text
Use my Job Search Coach.
```

Codex should route the request through `prompts/job_search_coach_router.md`, then use the right intake template from `templates/`.

## Interview-Landing Metrics

Each tailored job now tracks:

- Base resume match score
- Tailored resume match score
- Match lift after tailoring
- Base keyword coverage
- Tailored keyword coverage
- Covered keywords
- Missing or unconfirmed keywords
- Seniority risk
- Recommended next action
- Interview hook
- Outreach subject line

Scoring standards:

- Do not lower standards to make a role look better.
- Keep senior/principal/manager roles flagged even if the keywords match.
- Push tailored ATS resume match to 85+ only when the job is in a target family and the resume can truthfully support the keywords.
- Keep unsupported tools in the caution/missing-keyword notes instead of claiming them.
- Treat `role fit` and `tailored ATS match` as separate signals.

The job board also supports:

- Sorting by highest tailored match
- Sorting by highest role fit
- Sorting by recently added
- Sorting by highest base match
- Sorting by company
- Recording applied/interview/offer jobs into a separate browser-side applied log
- Exporting the applied log as CSV

## Recommended Search Focus

Initial role families from the resume:

- Data Analyst
- Business Data Analyst
- Data Science Intern
- Machine Learning Intern
- Manufacturing Data Analyst
- Operations Analyst
- Supply Chain Analytics Intern
- Data Engineer Intern
- Business Intelligence Analyst

Best-fit domains:

- Manufacturing analytics
- Operations analytics
- Supply chain analytics
- Data quality and reporting
- SQL/Python analytics
- Applied ML / anomaly detection
- AI workflow tooling
