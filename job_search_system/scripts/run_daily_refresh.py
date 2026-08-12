from __future__ import annotations

import subprocess
import sys
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SYSTEM = ROOT / "job_search_system"
SCRIPTS = SYSTEM / "scripts"
LOCAL_ENV = SYSTEM / "connectors" / "apify_config.local.env"
APIFY_ENV_KEYS = [
    "APIFY_TOKEN",
    "APIFY_ACTOR_ID",
    "APIFY_TASK_ID",
    "APIFY_DATASET_ID",
    "APIFY_INPUT_FILE",
    "APIFY_RUN_TIMEOUT_SECONDS",
]


def load_windows_user_env() -> None:
    if os.name != "nt":
        return


def load_local_env() -> None:
    if not LOCAL_ENV.exists():
        return
    for line in LOCAL_ENV.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        name, value = stripped.split("=", 1)
        name = name.strip()
        value = value.strip().strip('"').strip("'")
        if name and value and not os.environ.get(name):
            os.environ[name] = value
    try:
        import winreg
    except ImportError:
        return
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
            for name in APIFY_ENV_KEYS:
                if os.environ.get(name):
                    continue
                try:
                    value, _ = winreg.QueryValueEx(key, name)
                except FileNotFoundError:
                    continue
                if isinstance(value, str) and value.strip():
                    os.environ[name] = value
    except OSError:
        return


def run_step(script: str, required: bool = True) -> tuple[int, str]:
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / script)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=420,
    )
    output = (result.stdout or result.stderr or "").strip()
    if required and result.returncode != 0:
        raise RuntimeError(f"{script} failed with {result.returncode}: {output}")
    return result.returncode, output


def main() -> int:
    load_local_env()
    load_windows_user_env()
    messages = []
    for script, required in [
        ("sync_apify_company_include.py", True),
        ("refresh_from_apify_dataset.py", False),
        ("merge_browser_session_jobs.py", True),
        ("enrich_sponsor_metadata.py", True),
        ("generate_tailored_resumes.py", True),
    ]:
        try:
            code, output = run_step(script, required=required)
            status = "ok" if code == 0 else f"skipped/nonfatal:{code}"
            messages.append(f"{script}: {status} {output}".strip())
        except Exception as exc:  # noqa: BLE001
            messages.append(f"{script}: error {exc}")
            if required:
                print("\n".join(messages))
                return 1
    print("\n".join(messages))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
