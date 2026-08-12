# LinkedIn Deep Audit Prompt

Use this for a full line-by-line LinkedIn teardown.

```text
Run a LinkedIn Deep Audit using my job_search_system.

Use:
- job_search_system/profile/candidate_profile.md
- job_search_system/profile/job_search_profile.md
- job_search_system/profile/preferences.yml
- job_search_system/templates/linkedin_profile_intake.md

Input:
[upload LinkedIn PDF or paste the complete profile]

Audit through two lenses:
- Recruiter lens: would this profile make a recruiter shortlist Yogeshwari for data analyst, data science intern, BI analyst, operations analytics, manufacturing analytics, supply-chain analytics, or data engineering intern roles?
- Algorithm lens: would LinkedIn surface this profile for the right searches?

For each section, provide:
- Current state
- Issues identified
- Recommended fix
- Rewrite where useful

Scorecard out of 60:
- Profile completeness /10
- Headline strength /10
- About summary /10
- Experience descriptions /10
- Keywords and discoverability /10
- Visual first impression and proof assets /10

Keyword gap analysis:
- List the top 10 recruiter search terms for Yogeshwari's target roles.
- Mark each as present, weak, or missing.
- Suggest where to add each missing term truthfully.

End with:
- The one-paragraph diagnosis of what is holding the profile back most
- A 7-day fix plan
- A 30-day activity plan for posts, comments, featured work, and recruiter visibility

Rules:
- Do not invent achievements, dates, tools, certifications, publications, or endorsements.
- Rewrites must stay grounded in the candidate profile.
- Ask before recommending any public statement about work authorization or sponsorship.
```
