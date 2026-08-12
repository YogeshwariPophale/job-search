from __future__ import annotations

import argparse
import json
import mimetypes
import os
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse


ROOT = Path(__file__).resolve().parents[2]
SYSTEM = ROOT / "job_search_system"
DATA_FILE = SYSTEM / "data" / "extracted_jobs.json"
WATCHLIST_FILE = SYSTEM / "tracker" / "sponsor_friendly_data_companies.csv"
LOG_FILE = SYSTEM / "tmp" / "live_server.log"


class RefreshState:
    def __init__(self, command: str | None, interval: int) -> None:
        self.command = command
        self.interval = interval
        self.last_run = ""
        self.last_status = "idle"
        self.last_message = "No live refresh command configured."
        self.lock = threading.Lock()

    def snapshot(self) -> dict:
        with self.lock:
            return {
                "lastRun": self.last_run,
                "lastStatus": self.last_status,
                "lastMessage": self.last_message,
                "refreshIntervalSeconds": self.interval,
                "hasRefreshCommand": bool(self.command),
            }

    def update(self, status: str, message: str) -> None:
        with self.lock:
            self.last_run = datetime.now(timezone.utc).isoformat()
            self.last_status = status
            self.last_message = message


def log(message: str) -> None:
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with LOG_FILE.open("a", encoding="utf-8") as handle:
        handle.write(f"[{stamp}] {message}\n")


def load_jobs_payload() -> dict:
    payload = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    jobs = payload.get("jobs", []) if isinstance(payload, dict) else payload
    source_mtime = datetime.fromtimestamp(DATA_FILE.stat().st_mtime).isoformat()
    response = {
        "generatedAt": payload.get("generatedAt") if isinstance(payload, dict) else "",
        "sourceUpdatedAt": source_mtime,
        "servedAt": datetime.now(timezone.utc).isoformat(),
        "jobs": jobs,
    }
    if isinstance(payload, dict):
        for key in [
            "sources",
            "browserImportedAt",
            "sponsorEnrichedAt",
            "sponsorWatchlistCount",
            "sponsorMatchedJobCount",
            "rawItemCount",
            "filteredOutCount",
            "preservedNonApifyCount",
        ]:
            if key in payload:
                response[key] = payload[key]
    return response


def run_refresh_command(state: RefreshState) -> None:
    if not state.command:
        state.update("idle", "No live refresh command configured.")
        return

    try:
        result = subprocess.run(
            state.command,
            cwd=ROOT,
            shell=True,
            capture_output=True,
            text=True,
            timeout=max(state.interval - 5, 30),
        )
        output = (result.stdout or result.stderr or "").strip()
        if result.returncode == 0:
            state.update("ok", output[-500:] or "Refresh command completed.")
        else:
            state.update("error", (output[-500:] or f"Refresh exited with {result.returncode}."))
    except Exception as exc:  # noqa: BLE001
        state.update("error", str(exc))


def refresh_loop(state: RefreshState) -> None:
    if not state.command:
        return
    while True:
        run_refresh_command(state)
        time.sleep(max(state.interval, 60))


def safe_static_path(raw_path: str) -> Path | None:
    parsed_path = unquote(urlparse(raw_path).path)
    if parsed_path == "/":
        parsed_path = "/job_search_system/phone_app.html"
    candidate = (ROOT / parsed_path.lstrip("/")).resolve()
    try:
        candidate.relative_to(ROOT.resolve())
    except ValueError:
        return None
    if candidate.is_dir():
        candidate = candidate / "index.html"
    return candidate


def make_handler(state: RefreshState):
    class Handler(BaseHTTPRequestHandler):
        server_version = "YogeshwariJobLive/1.0"

        def do_GET(self) -> None:  # noqa: N802
            path = urlparse(self.path).path
            if path == "/api/jobs":
                self.send_json(load_jobs_payload())
                return
            if path == "/api/status":
                self.send_json({
                    "ok": True,
                    "dataFile": str(DATA_FILE),
                    "watchlistFile": str(WATCHLIST_FILE),
                    **state.snapshot(),
                })
                return

            static_path = safe_static_path(self.path)
            if not static_path or not static_path.exists():
                self.send_error(404, "Not found")
                return

            content_type = mimetypes.guess_type(static_path.name)[0] or "application/octet-stream"
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(static_path.read_bytes())

        def do_POST(self) -> None:  # noqa: N802
            if urlparse(self.path).path != "/api/refresh":
                self.send_error(404, "Not found")
                return
            run_refresh_command(state)
            self.send_json(state.snapshot())

        def send_json(self, payload: dict) -> None:
            body = json.dumps(payload, indent=2).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format: str, *args) -> None:  # noqa: A002
            log(format % args)

    return Handler


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve the job search app with live JSON refresh endpoints.")
    parser.add_argument("--host", default=os.getenv("JOB_APP_HOST", "0.0.0.0"))
    parser.add_argument("--port", type=int, default=int(os.getenv("JOB_APP_PORT", "8787")))
    parser.add_argument("--refresh-command", default=os.getenv("JOB_REFRESH_COMMAND", ""))
    parser.add_argument("--use-apify-refresh", action="store_true")
    parser.add_argument("--refresh-interval", type=int, default=int(os.getenv("JOB_REFRESH_INTERVAL_SECONDS", "900")))
    args = parser.parse_args()

    if args.use_apify_refresh and not args.refresh_command.strip():
        refresh_script = SYSTEM / "scripts" / "run_daily_refresh.py"
        args.refresh_command = f'"{sys.executable}" "{refresh_script}"'

    state = RefreshState(args.refresh_command.strip() or None, args.refresh_interval)
    if state.command:
        threading.Thread(target=refresh_loop, args=(state,), daemon=True).start()

    server = ThreadingHTTPServer((args.host, args.port), make_handler(state))
    log(f"Serving {ROOT} on http://{args.host}:{args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
