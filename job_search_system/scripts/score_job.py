from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "profile" / "candidate_profile.md"


SKILL_KEYWORDS = {
    "sql": 8,
    "python": 8,
    "data analysis": 7,
    "data analyst": 7,
    "data science": 7,
    "machine learning": 6,
    "statistics": 6,
    "statistical analysis": 7,
    "dashboard": 6,
    "kpi": 6,
    "data quality": 7,
    "etl": 5,
    "reporting": 6,
    "business intelligence": 6,
    "analytics": 5,
    "anomaly detection": 7,
    "root cause": 5,
    "manufacturing": 7,
    "operations": 6,
    "supply chain": 5,
    "sap": 5,
    "postgresql": 5,
    "mysql": 4,
    "sql server": 4,
    "pandas": 4,
    "numpy": 4,
    "scikit-learn": 4,
    "flask": 3,
    "docker": 3,
    "hadoop": 3,
    "pyspark": 3,
    "nlp": 4,
    "llm": 4,
    "large language model": 4,
}

ROLE_KEYWORDS = {
    "intern": 10,
    "student": 6,
    "new grad": 8,
    "entry level": 8,
    "early career": 8,
    "data analyst": 10,
    "business analyst": 8,
    "business intelligence": 8,
    "data scientist": 8,
    "machine learning": 7,
    "data engineer": 6,
    "operations analyst": 8,
    "manufacturing analyst": 9,
    "supply chain analyst": 8,
}

RISK_KEYWORDS = {
    "senior": -12,
    "staff": -15,
    "principal": -18,
    "lead": -10,
    "manager": -8,
    "5+ years": -15,
    "7+ years": -20,
    "10+ years": -25,
    "active security clearance": -18,
    "citizenship required": -18,
}


@dataclass
class ScoreResult:
    score: int
    matched: list[str]
    risks: list[str]
    missing: list[str]


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower())


def find_keywords(text: str, weighted: dict[str, int]) -> tuple[int, list[str]]:
    total = 0
    found: list[str] = []
    for keyword, weight in weighted.items():
        pattern = r"\b" + re.escape(keyword).replace(r"\ ", r"\s+") + r"\b"
        if re.search(pattern, text):
            total += weight
            found.append(keyword)
    return total, found


def score_job(job_text: str) -> ScoreResult:
    text = normalize(job_text)
    skill_score, skills = find_keywords(text, SKILL_KEYWORDS)
    role_score, roles = find_keywords(text, ROLE_KEYWORDS)
    risk_score, risks = find_keywords(text, RISK_KEYWORDS)

    raw_score = skill_score + role_score + risk_score
    score = max(0, min(100, 35 + raw_score))

    profile_text = normalize(PROFILE.read_text(encoding="utf-8"))
    matched = [item for item in skills + roles if item in profile_text or item in ROLE_KEYWORDS]

    possible_missing = []
    for keyword in ["tableau", "power bi", "aws", "azure", "gcp", "airflow", "dbt", "kubernetes"]:
        if keyword in text and keyword not in profile_text:
            possible_missing.append(keyword)

    return ScoreResult(score=score, matched=matched, risks=risks, missing=possible_missing)


def recommendation(score: int) -> str:
    if score >= 78:
        return "Apply"
    if score >= 65:
        return "Apply after tailoring or networking"
    if score >= 50:
        return "Save or network first"
    return "Skip unless there is a strong personal reason"


def main() -> None:
    parser = argparse.ArgumentParser(description="Score a job listing against Yogeshwari's profile.")
    parser.add_argument("job_file", help="Path to a text or markdown file containing the job listing.")
    parser.add_argument("--output", help="Optional markdown output path.")
    args = parser.parse_args()

    job_path = Path(args.job_file)
    job_text = job_path.read_text(encoding="utf-8")
    result = score_job(job_text)

    lines = [
        "# Job Fit Score",
        "",
        f"Source: `{job_path}`",
        "",
        f"Score: {result.score}/100",
        f"Recommendation: {recommendation(result.score)}",
        "",
        "## Matched Signals",
        "",
    ]
    lines.extend(f"- {item}" for item in result.matched[:30])
    if not result.matched:
        lines.append("- No strong keyword matches found.")

    lines.extend(["", "## Risks", ""])
    lines.extend(f"- {item}" for item in result.risks)
    if not result.risks:
        lines.append("- No seniority or eligibility risk keywords detected.")

    lines.extend(["", "## Possible Missing Or Unconfirmed Requirements", ""])
    lines.extend(f"- {item}" for item in result.missing)
    if not result.missing:
        lines.append("- No common unsupported tool requirements detected by the lightweight scanner.")

    lines.extend([
        "",
        "## Tailoring Notes",
        "",
        "- Emphasize SQL, Python, data quality, statistical analysis, dashboards, and operational datasets when relevant.",
        "- Preserve grounded metrics: 40% manual reporting reduction, 200+ components, 85% validation cycle reduction.",
        "- Confirm work authorization, sponsorship, availability, salary, and relocation before form submission.",
    ])

    report = "\n".join(lines) + "\n"
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()

