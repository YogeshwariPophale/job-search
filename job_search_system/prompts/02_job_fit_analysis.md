# Codex Prompt - Job Fit Analysis

Use this after a job listing is pasted or opened.

## Inputs

- Candidate profile: `job_search_system/profile/candidate_profile.md`
- Preferences: `job_search_system/profile/preferences.yml`
- Job listing text or URL

## Task

Analyze fit using only grounded candidate facts. Do not invent experience.

## Output

1. Fit score from 0-100.
2. Apply / Save / Network / Skip recommendation.
3. Matched requirements.
4. Gaps or risks.
5. Resume tailoring strategy.
6. Suggested top resume keywords.
7. Suggested bullet rewrites grounded in the base resume.
8. Screening questions that need user confirmation.

