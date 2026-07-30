# Codex Prompt - Job Search Agent

Use this when Yogeshwari asks Codex to find roles.

## Objective

Find high-fit roles for Yogeshwari Pophale using the candidate profile and preferences in `job_search_system/profile/`.

## Search Targets

Prioritize:

- Data Analyst
- Business Data Analyst
- Data Science Intern
- Machine Learning Intern
- Manufacturing Data Analyst
- Operations Analyst
- Supply Chain Analytics Intern
- Business Intelligence Analyst
- Data Engineer Intern

Strong keywords:

- SQL
- Python
- data quality
- dashboard
- KPI
- manufacturing analytics
- operations analytics
- supply chain analytics
- anomaly detection
- statistical analysis
- SAP
- PostgreSQL
- data visualization
- machine learning
- NLP
- LLM

## Search Process

1. Search current listings on job boards and company career pages.
2. Prefer roles posted recently and roles open to students, interns, recent graduates, or early-career candidates.
3. Avoid senior-only roles unless the requirements are clearly flexible.
4. For each role, capture company, title, location, URL, date found, employment type, and important requirements.
5. Score each role before recommending application.

## Output Format

Return a short ranked list:

| Rank | Company | Role | Location | Fit | Why it fits | Concern | URL |
| --- | --- | --- | --- | --- | --- | --- | --- |

Then recommend the top 3 to tailor for first.

