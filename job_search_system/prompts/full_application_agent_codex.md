# Full Application Agent Prompt - Codex Version

Paste this into Codex when applying to a specific role.

```text
I want to apply to this role using my job_search_system.

ROLE: [job title]
COMPANY: [company name]
JD LINK OR TEXT: [paste URL or full job description]

Use:
- job_search_system/profile/candidate_profile.md
- job_search_system/profile/job_search_profile.md
- job_search_system/profile/preferences.yml
- base/yogeshwari_resume_UCR_base_profile.md

STEP 1 - RESEARCH
Search the web for current information about the company:
- What they do and who their customers are
- Recent news, funding, product launches, or business updates
- The likely hiring manager, recruiter, or relevant team lead
- Company values or culture signals that can personalize outreach

STEP 2 - FIT ANALYSIS
Score my fit for this role from 0 to 100 and explain:
- Top 3 reasons I am a strong fit
- Gaps or risks I should address
- The single strongest hook I should lead with

STEP 3 - CONTACT RESEARCH
Find a relevant contact if possible:
- Name and title
- LinkedIn URL
- Public email only if it is clearly available or follows a confirmed company pattern
- One personal detail I can use respectfully in outreach

STEP 4 - TAILORED RESUME
Create a tailored resume package:
- New resume headline or summary
- Keywords to add or emphasize
- Bullet points to move up or rewrite
- Anything to remove or de-emphasize
- Final ATS-friendly tailored resume PDF and source file

Use only grounded claims from my profile. Do not invent tools, projects, dates, certifications, work authorization, or metrics.

STEP 5 - COVER LETTER IF NEEDED
Write a cover letter under 300 words:
- Open with a specific hook about the company
- Include my strongest relevant proof point
- Use first person
- Casual-professional tone
- Short sentences
- No em-dashes
- Do not use "I look forward to hearing from you"

STEP 6 - COLD EMAIL AND LINKEDIN MESSAGE
Draft:
- A cold email under 150 words with subject line
- A LinkedIn connection request under 280 characters

Rules:
- Warm, direct, not formal
- No em-dashes
- Do not reference the JD directly
- Use my hook: reduced manual manufacturing reporting effort by 40% through Python reporting, validation, and data quality pipelines
- Ask me before mentioning work authorization or sponsorship

STEP 7 - APPLICATION ANSWERS
If there are form questions, draft answers in my voice:
- Specific
- First person
- Metric-led where truthful
- No AI cliches
- Ask me before answering sponsorship, salary, relocation, availability, disability, veteran status, demographic, or legal attestation questions

STEP 8 - SEND SEQUENCE
Tell me the exact order:
- What to upload
- What to send
- When to submit
- When to follow up
- What to update in tracker/applications.csv

STEP 9 - COACH FOLLOW-UPS
Recommend whether to run:
- Module 2 LinkedIn Quick Feedback if my LinkedIn profile needs fast recruiter-facing cleanup for this role family
- Module 3 LinkedIn Deep Audit if I am targeting this company or role family repeatedly
- Module 4 Interview Prep Planner if this role is high-fit or if I get a screen

Stop before final submission or sending any message. Ask for my explicit approval.
```
