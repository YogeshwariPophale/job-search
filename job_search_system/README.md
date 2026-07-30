# Yogeshwari's Codex Job Search System

This is a Codex-compatible version of the "AI Job Search System" guide, personalized from the base resume in `base/yogeshwari_resume_UCR_base_profile.md`.

It is designed for this workflow:

1. Use `job_board.html` as the personal job board dashboard.
2. Add roles manually or ask Codex to search current openings.
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

## Folder Map

- `profile/` - resume-derived profile, career preferences, and missing info
- `prompts/` - reusable Codex prompts for search, tailoring, applying, and follow-up
- `templates/` - copy/paste templates for job listings, screening answers, and outreach
- `tracker/` - application and networking trackers
- `scripts/` - lightweight helper scripts
- `outputs/` - generated job-specific materials
- `index.html` - compiled overview site showing what has been built
- `job_board.html` - self-contained job board dashboard with filters, stats, scoring, local save, CSV export, direct Apply Now links, and Agent Prompt copying
- `data/extracted_jobs.json` - latest daily refresh payload imported by the board
- `data/tailored_resumes.json` - manifest of generated role-specific resume PDFs

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
- Weekly refresh: `prompts/01_search_agent.md` and `prompts/05_follow_up_agent.md`.

## Daily Refresh

Ask Codex:

```text
Run my daily job refresh.
```

Codex will use `prompts/daily_refresh_agent.md` to extract roles from logged-in Jobright and GradLeaders pages, then check watchlist company career pages. Results are written to `data/extracted_jobs.json`.

After extraction, Codex runs `scripts/generate_tailored_resumes.py`. The script selects the top 15 jobs, extracts essential supported keywords, generates one-page ATS-friendly tailored PDFs, writes tailoring notes, and updates the board data with `Resume PDF` download links.

The job board imports that file every time it loads and when you click `Import Daily Refresh`. It de-duplicates by company, role, location, and URL, re-scores jobs against Yogeshwari's profile, and updates existing jobs with new resume links, direct apply links, base-vs-tailored match scores, keyword coverage, missing keyword notes, and recommended actions.

`Apply Now` opens the direct application URL when available, otherwise the job listing URL, otherwise the mapped career page for watchlist companies. `Agent Prompt` copies the Codex application workflow for resume tailoring, outreach, and application-answer drafting.

The tailoring rule is "highest truthful match": keywords are incorporated only when they are supported by Yogeshwari's actual resume, coursework, projects, or experience. Unsupported tools are flagged in notes instead of being claimed.

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
