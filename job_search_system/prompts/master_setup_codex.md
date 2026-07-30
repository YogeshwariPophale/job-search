# Codex Master Setup Prompt

Use this prompt when you want Codex to rebuild or update the full system.

```text
I want to build or update my personal job search system in this workspace.

Use these source files:
- base/yogeshwari_resume_UCR_base_profile.md
- job_search_system/profile/candidate_profile.md
- job_search_system/profile/job_search_profile.md
- job_search_system/profile/preferences.yml

Create or update:
- A self-contained job board HTML dashboard at job_search_system/job_board.html
- A tracker at job_search_system/tracker/applications.csv
- A networking tracker at job_search_system/tracker/networking.csv
- Reusable application prompts under job_search_system/prompts/
- Templates under job_search_system/templates/

The dashboard should include:
- Job cards with company, role, location, work arrangement, salary if known, source, fit score, posted age, status, and positioning notes
- Filters by status
- A fit score 70+ toggle
- Search by company, role, keyword, or location
- Stats for total roles, applied roles, highest fit score, and average fit score
- An Add Job form where I can paste a JD and save it locally in the browser
- An Apply Now button that copies a prefilled Codex application workflow prompt
- My name in the header
- Mobile-friendly styling

Use my resume facts only. Do not invent experience, credentials, tools, dates, work authorization, salary expectations, or visa information.

Keep the workflow Codex-compatible:
- Codex can search, score, tailor, draft, track, and help fill forms.
- Codex must stop for my explicit approval before submitting applications, sending messages, answering sponsorship questions, or entering salary expectations.
```

