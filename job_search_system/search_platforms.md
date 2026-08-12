# Search Platforms

Use these as starting points for job searches. For logged-in or personalized results, Yogeshwari can provide the exact URL after opening the platform in her browser.

## General Platforms

- LinkedIn Jobs: https://www.linkedin.com/jobs/
- Handshake: https://app.joinhandshake.com/
- Indeed: https://www.indeed.com/
- Simplify: https://simplify.jobs/
- Simplify Dashboard: https://simplify.jobs/dashboard
- Jobot: https://jobot.com/find/full-time-data-analytics-jobs
- Wellfound: https://wellfound.com/jobs
- RippleMatch: https://ripplematch.com/
- Google Jobs search: https://www.google.com/search?q=data+analyst+intern+jobs
- Jobright recommendations: https://jobright.ai/jobs/recommend
- Rewriting the Code / GradLeaders jobs: https://candidate.gradleaders.com/RewritingTheCode/Candidates/Authenticated/Jobs/SearchJobs.aspx

## Priority Login Platforms

Tracked in `tracker/job_platform_sources.csv`:

| Platform | URL | Login Needed | How To Use |
| --- | --- | --- | --- |
| Simplify | https://simplify.jobs/dashboard | Yes | Logged-in dashboard/recommended jobs for fresh matched postings |
| Jobot | https://jobot.com/find/full-time-data-analytics-jobs | Usually no | Public job search for recruiter-posted data analytics roles |
| Handshake | https://app.joinhandshake.com/stu/postings | Yes | UCR/student jobs, internships, and early-career roles |
| LinkedIn | https://www.linkedin.com/jobs/search/?keywords=Data%20Analyst%20visa%20sponsorship&location=United%20States | Yes | Logged-in search; prefer company apply links over Easy Apply |

## Company Watchlist

The full sponsor-friendly Data Analyst target database lives in:

```text
job_search_system/watchlist_companies.csv
job_search_system/tracker/sponsor_friendly_data_companies.csv
```

It currently includes 133 large companies across big tech, fintech, banking, consulting, IT services, healthcare, pharma, retail, logistics, automotive, manufacturing, semiconductors, media, and consumer goods. These companies have public H-1B filing/sponsorship signals, but sponsorship must still be verified for each specific role.

Sample high-priority targets:

| Company | Careers URL | Priority Queries |
| --- | --- | --- |
| Microsoft | https://careers.microsoft.com/v2/global/en/home.html | Data Analyst, Data Science, Business Analytics, Program Manager - Data, Operations Analyst |
| Google / Alphabet | https://www.google.com/about/careers/applications/jobs/results/?hl=en_US | Data Analyst, Business Analyst, Data Science, Early Career, Intern |
| NVIDIA | https://www.nvidia.com/en-us/about-nvidia/careers/ | Data Science, Data Analyst, Operations Analyst, Supply Chain, AI |
| OpenAI | https://openai.com/careers/ | Data, Analytics, Applied AI, Operations, Emerging Talent, Residency |
| X / xAI | https://x.ai/careers | Data, Operations, AI, Product Analytics, Business Operations |
| Netflix | https://www.jobs.netflix.com/ | Data Science, Analytics, Data Engineering, Operations |
| Disney | https://www.disneycareers.com/en/search_jobs/search-results?c=US | Data Science and Analytics, Technology, Operations, Internships |
| Meta | https://www.metacareers.com/jobs/ | Data Analyst, Data Science, Product Analytics, University Grad, Internship |
| Amazon | https://www.amazon.jobs/en/ | Business Analyst, Data Analyst, Data Engineer, Operations, Supply Chain |
| Apple | https://jobs.apple.com/en-us/search?location=united-states-USA | Data Science, AIML, Operations, Business Analytics, New Grad |
| JPMorgan Chase | https://careers.jpmorgan.com/us/en/students/programs | Data Analyst, Business Analyst, Data Science, Operations Analyst, Risk Analyst |
| Accenture | https://www.accenture.com/us-en/careers/jobsearch | Data Analyst, Business Analyst, Data Science Analyst, Analytics Consultant, BI |
| UnitedHealth Group / Optum | https://careers.unitedhealthgroup.com/ | Data Analyst, Business Analyst, Data Science, Healthcare Analytics |
| Walmart | https://careers.walmart.com/ | Data Analyst, Business Analyst, Data Science, BI, Supply Chain Analytics |
| General Motors | https://search-careers.gm.com/en/jobs/ | Data Analyst, Business Analyst, Data Science, Manufacturing Analytics |

## Direct Company Applications

Prefer company career pages when a role is high fit. Direct applications are usually cleaner than third-party reposts.

Search examples:

- `site:jobs.lever.co "Data Analyst Intern" "United States"`
- `site:greenhouse.io "Data Science Intern" "United States"`
- `site:workdayjobs.com "Business Intelligence Analyst" "United States"`
- `site:myworkdayjobs.com "Machine Learning Intern" "United States"`

## University And Local

- UCR Career Center: https://careers.ucr.edu/
- UCR Handshake access is usually through the university or Handshake account login.

## Recommended Query Templates

- `"Data Analyst Intern" "SQL" "Python" "United States"`
- `"Business Data Analyst" "SQL" "Python" "entry level"`
- `"Data Science Intern" "machine learning" "Python" "Summer 2027"`
- `"Manufacturing Data Analyst" "SQL" "Python"`
- `"Operations Analyst" "data quality" "dashboard"`
- `"Supply Chain Analytics Intern" "SQL" "Python"`
- `"Business Intelligence Analyst" "new grad" "SQL"`
- `"Data Engineer Intern" "PostgreSQL" "Python" "Docker"`
