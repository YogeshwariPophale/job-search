# Connector Refresh Setup

This folder turns the "fresh listings before LinkedIn" workflow into reusable system files.

## Files

- `apify_company_watchlist_seed.json` - generated seed input for an Apify job-listing actor or another connector workflow. It currently contains 133 sponsor-friendly company career URLs.

Regenerate it after editing `../watchlist_companies.csv` or `../tracker/sponsor_friendly_data_companies.csv`:

```text
python job_search_system/scripts/build_apify_watchlist.py
```

If `python` is not on PATH, ask Codex to run the generator with its bundled Python runtime.

## Workflow

1. Create or open an Apify account.
2. Choose a job-listing actor that can read company career pages, Greenhouse, Lever, Workday, Indeed, or Google Jobs.
3. Paste the `startUrls` from `apify_company_watchlist_seed.json` into the actor input.
4. Schedule the actor every 24 hours.
5. Filter for listings posted in the last 24-48 hours.
6. Export the dataset, or connect it to an LLM through an Apify connector/MCP.
7. Use `../prompts/connector_refresh_agent.md` to convert the fresh dataset into `../data/extracted_jobs.json`.
8. Run `python job_search_system/scripts/generate_tailored_resumes.py`.

## Live App

Run the local live server:

```text
powershell -ExecutionPolicy Bypass -File job_search_system/scripts/start_live_app.ps1
```

The server exposes:

- `http://127.0.0.1:8787/job_search_system/phone_app.html`
- `http://127.0.0.1:8787/job_search_system/job_board.html`
- `http://127.0.0.1:8787/api/jobs`
- `http://127.0.0.1:8787/api/status`

The pages poll `/api/jobs` every 60 seconds. To make the job data truly live, connect Apify or another source so it rewrites `../data/extracted_jobs.json` on a schedule.

Apify refresh options:

- Set `APIFY_TOKEN` plus `APIFY_ACTOR_ID` or `APIFY_TASK_ID` to run a scraper automatically.
- Or set `APIFY_TOKEN` and `APIFY_DATASET_ID` to read an existing dataset.
- Or save an Apify export to `apify_latest_dataset.json`, then run `python ../scripts/refresh_from_apify_dataset.py`.
- Start the live app with `-UseApifyRefresh` to rerun the refresh script in the background.

One-time Windows setup:

```text
powershell -ExecutionPolicy Bypass -File job_search_system/scripts/configure_apify_refresh.ps1 -ApifyToken "YOUR_TOKEN" -ActorId "ACTOR_OWNER/ACTOR_NAME"
```

Install the Windows startup task from the workspace root:

```text
powershell -ExecutionPolicy Bypass -File job_search_system/scripts/install_live_app_startup.ps1 -UseApifyRefresh
```

## Guardrails

- Prefer direct company links over reposted LinkedIn listings.
- Prefer companies marked with "Large H-1B employer signal" or "Known H-1B filing signal", while still checking each posting's sponsorship wording.
- Do not treat an old repost as fresh unless the company career page confirms it is still open.
- Keep the daily apply list small: no more than 5 high-fit roles per day.
- Do not submit applications or send recruiter messages without explicit approval.
