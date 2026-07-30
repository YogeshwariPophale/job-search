# Daily Refresh Agent

Use this prompt when you want Codex to refresh the job board from logged-in platforms and watchlist companies.

```text
Run my daily job refresh.

Use the logged-in in-app browser tabs for:
- Jobright recommendations: https://jobright.ai/jobs/recommend
- Rewriting the Code / GradLeaders jobs: https://candidate.gradleaders.com/RewritingTheCode/Candidates/Authenticated/Jobs/SearchJobs.aspx

Also check the watchlist in:
- job_search_system/watchlist_companies.csv
- job_search_system/search_platforms.md

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
1. Extract current role title, company, location, salary if visible, posted age/date, source URL, and short description.
2. Prefer internships, new-grad, entry-level, junior, analyst, data science, data engineering, BI, operations, manufacturing, and supply chain analytics roles.
3. Keep senior/principal/manager roles only if they are from a high-priority company, but let the board score them lower.
4. Write the merged result to `job_search_system/data/extracted_jobs.json`.
5. Run `job_search_system/scripts/generate_tailored_resumes.py`.
6. Confirm that the top 15 roles have ATS-friendly tailored PDF resumes under `output/pdf/tailored_resumes/`.
7. Do not submit applications or send messages during refresh.
8. After writing the file and generating resumes, reload `job_search_system/job_board.html`; the board will auto-import new jobs, update resume links, and de-duplicate old ones.
```

## How Daily Import Works

The job board fetches `data/extracted_jobs.json` on page load and when you click `Import Daily Refresh`. It saves new jobs into browser local storage, updates existing jobs with new tailored resume links, and skips duplicates by company, role, location, and URL.

The resume generator selects the top 15 jobs by fit score, extracts supported keywords, avoids ungrounded claims, and creates one-page ATS-friendly PDFs. Unsupported tools such as Tableau, Power BI, AWS, Azure, GCP, Airflow, dbt, Kubernetes, Snowflake, and Looker are flagged in the tailoring notes instead of being claimed as experience.
