from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path
from textwrap import shorten

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.pdfbase.pdfmetrics import stringWidth


ROOT = Path(__file__).resolve().parents[2]
SYSTEM = ROOT / "job_search_system"
DATA_FILE = SYSTEM / "data" / "extracted_jobs.json"
MANIFEST_FILE = SYSTEM / "data" / "tailored_resumes.json"
BASE_PROFILE_FILE = ROOT / "base" / "yogeshwari_resume_UCR_base_profile.md"
OUTPUT_DIR = ROOT / "output" / "pdf" / "tailored_resumes" / str(date.today())
SOURCE_DIR = SYSTEM / "outputs" / "tailored_resumes" / str(date.today())

CONTACT_DISPLAY = (
    "+1 (951) 830-2153 | yspophale@gmail.com | ypoph001@ucr.edu | "
    "linkedin.com/in/yogeshwari-pophale-281b80206 | github.com/YogeshwariPophale"
)

SUPPORTED_KEYWORDS = {
    "sql": "SQL",
    "python": "Python",
    "postgresql": "PostgreSQL",
    "mysql": "MySQL",
    "sql server": "SQL Server",
    "pyspark": "PySpark",
    "r": "R",
    "matlab": "MATLAB",
    "c++": "C/C++",
    "data quality": "Data Quality Analysis",
    "data validation": "Data Validation",
    "reporting": "Reporting",
    "dashboard": "Dashboard Development",
    "dashboards": "Dashboard Development",
    "kpi": "KPI Reporting",
    "business intelligence": "Business Intelligence",
    "statistical analysis": "Statistical Analysis",
    "statistics": "Statistical Analysis",
    "exploratory data analysis": "Exploratory Data Analysis",
    "eda": "Exploratory Data Analysis",
    "variance analysis": "Variance Analysis",
    "outlier": "Outlier Detection",
    "anomaly": "Anomaly Detection",
    "feature engineering": "Feature Engineering",
    "machine learning": "Machine Learning",
    "model evaluation": "Model Evaluation",
    "pca": "PCA",
    "root cause": "Root Cause Analysis",
    "process improvement": "Process Improvement",
    "operations": "Operations Analytics",
    "manufacturing": "Manufacturing Analytics",
    "production": "Production Analytics",
    "supply chain": "Supply Chain Analytics",
    "inventory": "Inventory Analytics",
    "procurement": "Procurement Analytics",
    "sap": "SAP",
    "pandas": "Pandas",
    "numpy": "NumPy",
    "scikit-learn": "Scikit-learn",
    "docker": "Docker",
    "hadoop": "Hadoop",
    "flask": "Flask",
    "git": "Git",
    "matplotlib": "Matplotlib",
    "nlp": "NLP",
    "llm": "Large Language Models",
    "large language model": "Large Language Models",
    "gemini": "Gemini API",
}

UNSUPPORTED_HARD_REQUIREMENTS = {
    "tableau": "Tableau",
    "power bi": "Power BI",
    "aws": "AWS",
    "azure": "Azure",
    "gcp": "GCP",
    "airflow": "Airflow",
    "dbt": "dbt",
    "kubernetes": "Kubernetes",
    "snowflake": "Snowflake",
    "looker": "Looker",
}

SENIORITY_RISKS = ("senior", "sr.", "principal", "manager", "lead", "staff", "5+ years", "7+ years", "10+ years")


def esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def slug(text: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", text.lower()).strip("-")
    return value[:70] or "tailored-resume"


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower())


def contains_keyword(text: str, key: str) -> bool:
    if key in {"r", "c++"}:
        return re.search(rf"(?<![a-z0-9+#]){re.escape(key)}(?![a-z0-9+#])", text) is not None
    return key in text


def extract_supported_keywords(job: dict) -> list[str]:
    found = extract_job_supported_keywords(job)
    defaults = ["SQL", "Python", "Data Quality Analysis", "Statistical Analysis", "Dashboard Development"]
    for item in defaults:
        if item not in found:
            found.append(item)
    return found[:18]


def extract_job_supported_keywords(job: dict) -> list[str]:
    text = normalize(" ".join(str(job.get(key, "")) for key in ("role", "company", "location", "description")))
    found = []
    for raw, label in SUPPORTED_KEYWORDS.items():
        if contains_keyword(text, raw) and label not in found:
            found.append(label)
    return found[:18]


def extract_unconfirmed_keywords(job: dict) -> list[str]:
    text = normalize(" ".join(str(job.get(key, "")) for key in ("role", "description")))
    return [label for raw, label in UNSUPPORTED_HARD_REQUIREMENTS.items() if raw in text]


def role_family(job: dict) -> str:
    text = normalize(f"{job.get('role', '')} {job.get('description', '')}")
    if any(word in text for word in ("data engineer", "pipeline", "etl", "spark")):
        return "data_engineering"
    if any(word in text for word in ("data scientist", "machine learning", "model", "nlp", "llm")):
        return "data_science"
    if any(word in text for word in ("supply chain", "manufacturing", "operations", "production", "inventory", "procurement")):
        return "operations"
    return "analytics"


def fit_score(job: dict) -> int:
    if job.get("fitScore") is not None:
        try:
            return int(job["fitScore"])
        except (TypeError, ValueError):
            pass
    return 0


def has_seniority_risk(job: dict) -> bool:
    role_text = normalize(str(job.get("role", "")))
    full_text = normalize(f"{job.get('role', '')} {job.get('description', '')}")
    title_terms = ("senior", "sr.", "principal", "manager", "staff", "lead")
    for item in title_terms:
        pattern = r"(?<![a-z0-9])" + re.escape(item).replace(r"\ ", r"\s+") + r"(?![a-z0-9])"
        if re.search(pattern, role_text):
            return True
    for item in ("5+ years", "7+ years", "10+ years"):
        pattern = r"(?<![a-z0-9])" + re.escape(item).replace(r"\ ", r"\s+") + r"(?![a-z0-9])"
        if re.search(pattern, full_text):
            return True
    return False


def summary_for(job: dict, keywords: list[str]) -> str:
    family = role_family(job)
    company = job.get("company", "the company")
    role = job.get("role", "this role")
    keyword_phrase = ", ".join(keywords[:7])
    if family == "data_science":
        return (
            f"Computational Data Science M.S. candidate targeting {role} at {company}, with hands-on Python, "
            f"statistical analysis, anomaly detection, machine learning coursework, and NLP/LLM workflow experience. "
            f"Brings manufacturing and engineering analytics experience translating complex datasets into reliable insights."
        )
    if family == "data_engineering":
        return (
            f"Computational Data Science M.S. candidate targeting {role} at {company}, with experience building Python "
            f"reporting, validation, and data quality pipelines across manufacturing operations. Skilled in {keyword_phrase}, "
            f"with project experience in PostgreSQL, Flask, Hadoop, and Docker analytics workflows."
        )
    if family == "operations":
        return (
            f"Computational Data Science M.S. candidate targeting {role} at {company}, with manufacturing, operations, "
            f"production, procurement, inventory, and SAP analytics experience. Skilled in {keyword_phrase}, with a record "
            f"of turning operational data into process improvements and KPI visibility."
        )
    return (
        f"Computational Data Science M.S. candidate targeting {role} at {company}, with experience in SQL, Python, "
        f"data quality, KPI reporting, dashboards, statistical analysis, and business intelligence. Proven ability to "
        f"transform operational and engineering datasets into actionable insights."
    )


def prioritized_skills(keywords: list[str]) -> list[tuple[str, str]]:
    keyword_set = set(keywords)
    programming = ["SQL", "Python", "PostgreSQL", "MySQL", "SQL Server", "PySpark", "R", "MATLAB", "C/C++"]
    analytics = [
        "Data Quality Analysis",
        "Data Validation",
        "Exploratory Data Analysis",
        "Statistical Analysis",
        "Dashboard Development",
        "KPI Reporting",
        "Business Intelligence",
        "Anomaly Detection",
        "Feature Engineering",
        "Machine Learning",
        "Model Evaluation",
        "Root Cause Analysis",
    ]
    operations = [
        "Manufacturing Analytics",
        "Operations Analytics",
        "Production Analytics",
        "Supply Chain Analytics",
        "Inventory Analytics",
        "Procurement Analytics",
        "Process Improvement",
        "SAP",
    ]
    tools = ["Pandas", "NumPy", "Scikit-learn", "Docker", "Hadoop", "Flask", "Git", "Matplotlib", "Gemini API", "NLP", "Large Language Models"]

    def ordered(items: list[str]) -> str:
        promoted = [item for item in items if item in keyword_set]
        rest = [item for item in items if item not in keyword_set]
        return ", ".join(promoted + rest)

    return [
        ("Programming & Databases", ordered(programming)),
        ("Analytics & Statistics", ordered(analytics)),
        ("Business & Operations", ordered(operations)),
        ("Tools & AI", ordered(tools)),
    ]


def bullets_for(job: dict, keywords: list[str]) -> dict[str, list[str]]:
    family = role_family(job)
    bajaj = [
        "Developed Python-based reporting, validation, and data quality pipelines for manufacturing operations, reducing manual reporting effort by 40% and improving standardized analytics reliability.",
        "Queried and analyzed SAP BOM, procurement, inventory, and production datasets using SQL and Python to support production planning across 200+ components.",
        "Built KPI dashboards tracking production throughput, quality metrics, process deviations, and operational efficiency, enabling faster identification of corrective actions.",
        "Performed exploratory, statistical, and anomaly analysis for AMR deployment, identifying process bottlenecks, operational deviations, and optimization opportunities.",
    ]
    rr = [
        "Automated Python engineering analysis workflows and simulation tooling for mtu S1600 engine validation, reducing validation cycle time by 85%.",
        "Analyzed engineering test, validation, and simulation datasets to identify anomaly patterns, failure trends, quality risks, and system performance drivers.",
        "Applied statistical analysis and data profiling to investigate performance deviations, support root cause analysis, and translate findings into technical documentation and optimization recommendations.",
    ]
    projects = [
        "Built a Gemini-powered workflow assistant for proposal planning, drafting, revision, evaluation, structured quality assessment, automated feedback, and recommendation generation.",
        "Built a PostgreSQL-Flask analytics platform for querying and visualizing reservation data with dynamic SQL filtering across pricing, booking, and customer dimensions.",
    ]
    if family == "data_engineering":
        bajaj = [bajaj[0], bajaj[1], bajaj[2], bajaj[3]]
        projects = [projects[1], projects[0]]
    elif family == "data_science":
        rr = [rr[1], rr[0], rr[2]]
        projects = [projects[0], projects[1]]
    elif family == "operations":
        bajaj = [bajaj[1], bajaj[2], bajaj[3], bajaj[0]]
    return {"bajaj": bajaj, "rr": rr, "projects": projects}


def matching_aliases(label: str) -> list[str]:
    aliases = {
        "Data Quality Analysis": ["data quality", "data quality analysis", "data validation"],
        "Dashboard Development": ["dashboard", "dashboards", "dashboard development"],
        "KPI Reporting": ["kpi", "kpi reporting"],
        "Business Intelligence": ["business intelligence", "bi"],
        "Statistical Analysis": ["statistical analysis", "statistics"],
        "Exploratory Data Analysis": ["exploratory data analysis", "eda"],
        "Anomaly Detection": ["anomaly", "anomaly detection"],
        "Outlier Detection": ["outlier", "outlier detection"],
        "Feature Engineering": ["feature engineering"],
        "Machine Learning": ["machine learning", "ml"],
        "Model Evaluation": ["model evaluation"],
        "Root Cause Analysis": ["root cause", "root cause analysis"],
        "Manufacturing Analytics": ["manufacturing", "manufacturing analytics"],
        "Operations Analytics": ["operations", "operations analytics", "operational"],
        "Production Analytics": ["production", "production analytics"],
        "Supply Chain Analytics": ["supply chain", "supply chain analytics"],
        "Inventory Analytics": ["inventory", "inventory analytics"],
        "Procurement Analytics": ["procurement", "procurement analytics"],
        "Large Language Models": ["large language models", "llm", "llms"],
        "Gemini API": ["gemini", "gemini api"],
        "Scikit-learn": ["scikit-learn", "sklearn"],
    }
    return aliases.get(label, [label.lower()])


def keyword_present(text: str, label: str) -> bool:
    normalized = normalize(text)
    return any(alias in normalized for alias in matching_aliases(label))


def tailored_resume_text(job: dict, keywords: list[str]) -> str:
    selected = bullets_for(job, keywords)
    skill_text = " ".join(value for _, value in prioritized_skills(keywords))
    return " ".join([
        summary_for(job, keywords),
        skill_text,
        " ".join(selected["bajaj"]),
        " ".join(selected["rr"]),
        " ".join(selected["projects"]),
        "SQL Python PostgreSQL Flask Hadoop Docker Gemini API NLP Large Language Models",
    ])


def match_score_for_text(job: dict, text: str, essential_keywords: list[str], unconfirmed: list[str]) -> dict:
    covered = [keyword for keyword in essential_keywords if keyword_present(text, keyword)]
    missing = [keyword for keyword in essential_keywords if keyword not in covered]
    coverage = round((len(covered) / len(essential_keywords)) * 100) if essential_keywords else 55

    score = coverage
    role = normalize(str(job.get("role", "")))
    if any(term in role for term in ("intern", "junior", "jr", "analyst i", "entry")):
        score += 8
    if any(term in role for term in ("data analyst", "business/data analyst", "operations analyst", "supply chain")):
        score += 6
    if any(term in role for term in ("senior", "sr.", "principal", "manager")):
        score -= 18
    if unconfirmed:
        score -= min(12, len(unconfirmed) * 4)
    if "sql" in normalize(text) and "python" in normalize(text):
        score += 4
    score = max(0, min(100, score))

    return {
        "score": score,
        "coveredKeywords": covered,
        "missingKeywords": missing,
        "coveragePercent": coverage,
    }


def action_plan(job: dict, tailored_score: int, base_score: int, unconfirmed: list[str], seniority_risk: bool) -> dict:
    delta = tailored_score - base_score
    company = job.get("company", "the company")
    role = job.get("role", "the role")
    if tailored_score >= 78 and not seniority_risk:
        priority = "Apply today"
        next_action = "Use the tailored resume, apply directly, and send a short recruiter or hiring-team note."
    elif tailored_score >= 65 and not seniority_risk:
        priority = "Apply with networking"
        next_action = "Apply with the tailored resume, then find one recruiter or team member for a warm outreach note."
    elif seniority_risk:
        priority = "Network first"
        next_action = "Do not lead with a cold application. Ask a recruiter whether early-career candidates are considered for this opening or adjacent roles."
    else:
        priority = "Save or research"
        next_action = "Save the role, look for an adjacent entry-level or intern opening, and apply only if the requirements are flexible."

    interview_hook = (
        "Lead with the 40% reporting-effort reduction at Bajaj Auto, then connect it to SQL/Python data quality, "
        "KPI visibility, and cross-functional manufacturing or operations decisions."
    )
    if role_family(job) == "data_science":
        interview_hook = (
            "Lead with Python analytics and anomaly detection from Rolls-Royce and Bajaj Auto, then connect it to ML coursework "
            "and the Gemini-powered proposal workflow project."
        )
    elif role_family(job) == "data_engineering":
        interview_hook = (
            "Lead with Python reporting and validation pipelines, SAP production datasets, and the PostgreSQL-Flask-Hadoop-Docker analytics platform."
        )
    elif role_family(job) == "operations":
        interview_hook = (
            "Lead with SAP BOM, procurement, inventory, and production analytics across 200+ components, plus KPI dashboards and process optimization."
        )

    cautions = []
    if unconfirmed:
        cautions.append("Do not claim " + ", ".join(unconfirmed) + " unless Yogeshwari confirms hands-on experience.")
    if seniority_risk:
        cautions.append("Seniority appears above target. Treat this as a networking or adjacent-role opportunity.")
    if delta < 5:
        cautions.append("Tailoring has limited lift because the base resume already covers most supported keywords or the JD is sparse.")

    return {
        "priority": priority,
        "nextAction": next_action,
        "interviewHook": interview_hook,
        "cautions": cautions,
        "outreachSubject": f"{role} at {company} - data analytics background",
    }


def resume_match_scores(job: dict, base_keyword_match: dict, tailored_keyword_match: dict, unconfirmed: list[str], seniority_risk: bool) -> tuple[int, int, int]:
    source_score = fit_score(job) or 50
    base_score = source_score
    if seniority_risk:
        base_score -= 15
    if unconfirmed:
        base_score -= min(9, len(unconfirmed) * 3)
    base_score = max(0, min(100, base_score))

    coverage_gain = max(0, tailored_keyword_match["coveragePercent"] - base_keyword_match["coveragePercent"])
    tailoring_lift = 6
    tailoring_lift += min(5, len(tailored_keyword_match["coveredKeywords"]))
    tailoring_lift += min(4, round(coverage_gain / 10))
    if role_family(job) in {"operations", "data_engineering", "data_science"}:
        tailoring_lift += 2
    if unconfirmed:
        tailoring_lift -= min(5, len(unconfirmed) * 2)
    if seniority_risk:
        tailoring_lift = min(tailoring_lift, 4)
    tailoring_lift = max(0, min(15, tailoring_lift))

    tailored_score = min(100, base_score + tailoring_lift)
    if seniority_risk:
        tailored_score = min(tailored_score, 64)

    return base_score, tailored_score, tailored_score - base_score


def fit_style(base_name: str, font_name: str, font_size: float, leading: float, available_width: float, text: str, min_size: float = 6.3) -> ParagraphStyle:
    size = font_size
    while size > min_size and stringWidth(text, font_name, size) > available_width:
        size -= 0.25
    return ParagraphStyle(
        base_name,
        fontName=font_name,
        fontSize=size,
        leading=max(leading - (font_size - size), size + 1),
        alignment=1,
        textColor=colors.HexColor("#202020"),
        spaceAfter=0,
    )


def build_pdf(job: dict, keywords: list[str], output_pdf: Path) -> None:
    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(output_pdf),
        pagesize=letter,
        rightMargin=0.32 * inch,
        leftMargin=0.32 * inch,
        topMargin=0.25 * inch,
        bottomMargin=0.24 * inch,
    )
    usable_width = letter[0] - doc.leftMargin - doc.rightMargin
    styles = {
        "name": ParagraphStyle("Name", fontName="Helvetica-Bold", fontSize=13.5, leading=14.2, alignment=1, textColor=colors.HexColor("#1f1f1f"), spaceAfter=2),
        "contact": fit_style("Contact", "Helvetica", 7.7, 8.4, usable_width, CONTACT_DISPLAY),
        "section": ParagraphStyle("Section", fontName="Helvetica-Bold", fontSize=9.1, leading=9.5, textColor=colors.HexColor("#1f1f1f"), spaceBefore=4, spaceAfter=1),
        "body": ParagraphStyle("Body", fontName="Helvetica", fontSize=7.65, leading=8.3, textColor=colors.HexColor("#202020"), spaceAfter=1.1),
        "small": ParagraphStyle("Small", fontName="Helvetica", fontSize=7.25, leading=7.95, textColor=colors.HexColor("#202020"), spaceAfter=0.8),
        "job": ParagraphStyle("Job", fontName="Helvetica-Bold", fontSize=8.15, leading=8.65, textColor=colors.HexColor("#1f1f1f"), spaceBefore=1.8, spaceAfter=0.25),
        "right": ParagraphStyle("Right", fontName="Helvetica", fontSize=7.25, leading=7.95, alignment=2, textColor=colors.HexColor("#404040"), spaceAfter=0),
        "bullet": ParagraphStyle("Bullet", fontName="Helvetica", fontSize=7.2, leading=7.85, leftIndent=8, firstLineIndent=-5, bulletIndent=0, textColor=colors.HexColor("#202020"), spaceAfter=0.15),
    }

    def section(title: str) -> list:
        return [
            Paragraph(title.upper(), styles["section"]),
            Table([[""]], colWidths=[usable_width], rowHeights=[0.8], style=TableStyle([
                ("LINEABOVE", (0, 0), (-1, -1), 0.5, colors.HexColor("#bdbdbd")),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ])),
        ]

    def two_col(left: str, right: str, style_left: str = "job") -> Table:
        return Table(
            [[Paragraph(left, styles[style_left]), Paragraph(right, styles["right"])]],
            colWidths=[usable_width * 0.73, usable_width * 0.27],
            style=TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]),
        )

    def bullet(text: str) -> Paragraph:
        return Paragraph(esc(text), styles["bullet"], bulletText="-")

    selected = bullets_for(job, keywords)
    story = [
        Paragraph("Yogeshwari Pophale", styles["name"]),
        Paragraph(
            '+1 (951) 830-2153 | '
            '<a href="mailto:yspophale@gmail.com" color="#202020">yspophale@gmail.com</a> | '
            '<a href="mailto:ypoph001@ucr.edu" color="#202020">ypoph001@ucr.edu</a> | '
            '<a href="https://www.linkedin.com/in/yogeshwari-pophale-281b80206" color="#202020">linkedin.com/in/yogeshwari-pophale-281b80206</a> | '
            '<a href="https://github.com/YogeshwariPophale" color="#202020">github.com/YogeshwariPophale</a>',
            styles["contact"],
        ),
    ]

    story += section("Professional Summary")
    story.append(Paragraph(esc(summary_for(job, keywords)), styles["body"]))

    story += section("Education")
    story.append(two_col("University of California, Riverside - M.S. Computational Data Science | GPA: 3.78/4.00", "Expected Jan 2027"))
    story.append(Paragraph(esc("Coursework: Machine Learning, Data Analytics and Exploration, Databases, Artificial Intelligence, NLP, Data Mining, Data Ethics"), styles["small"]))
    story.append(two_col("College of Engineering Pune (COEP) - B.Tech. Electrical Engineering | GPA: 7.86/10", "Graduated Aug 2024"))
    story.append(Paragraph(esc("Coursework: DSA, Probability & Statistics, Embedded Systems, Analog/Digital Electronics, PCB Design, Circuit Integration, System Validation"), styles["small"]))

    story += section("Technical Skills")
    for label, value in prioritized_skills(keywords):
        story.append(Paragraph(f"<b>{esc(label)}:</b> {esc(value)}", styles["small"]))

    story += section("Professional Experience")
    story.append(two_col("Bajaj Auto Limited | Graduate Trainee Engineer", "Aug 2024 - Aug 2025"))
    for item in selected["bajaj"]:
        story.append(bullet(item))

    story.append(two_col("Rolls-Royce Power Systems AG | Engineering Intern", "Jan 2024 - Jun 2024"))
    for item in selected["rr"]:
        story.append(bullet(item))

    story.append(two_col("APTIV | Summer Intern", "May 2023 - Jul 2023"))
    story.append(bullet("Designed vehicle wire harnesses with CATIA and LDorado for Volkswagen and BMW; supported validation, technical documentation, and change management activities."))

    story += section("Campus Experience")
    story.append(two_col("BUS173: Introduction to Databases for Management | Grader, UCR", "Winter 2026"))
    story.append(bullet("Evaluated SQL assignments involving relational databases, joins, aggregations, query optimization, database design concepts, and structured query development."))
    story.append(two_col("BUS175: Business Data Communications | Grader, UCR", "Spring 2026"))
    story.append(bullet("Supported instruction in Python-based analytics, data transformation, visualization, and business intelligence workflows."))

    story += section("Projects")
    story.append(two_col("AI-Powered Research Proposal Workflow Agent | Python, Gemini API, LLMs, NLP", "In Progress"))
    story.append(bullet(selected["projects"][0]))
    story.append(two_col("Hotel Reservation Analytics Platform | SQL, PostgreSQL, Flask, Hadoop, Docker", ""))
    story.append(bullet(selected["projects"][1]))

    doc.build(story)


def write_source(job: dict, keywords: list[str], unconfirmed: list[str], pdf_rel: str, metrics: dict) -> Path:
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    path = SOURCE_DIR / f"{slug(job.get('company', 'company'))}_{slug(job.get('role', 'role'))}.md"
    lines = [
        f"# Tailored Resume Notes - {job.get('company')} - {job.get('role')}",
        "",
        f"PDF: `{pdf_rel}`",
        f"Fit score: {fit_score(job)}",
        f"Source: {job.get('source', 'Unknown')}",
        f"Location: {job.get('location', 'Unknown')}",
        f"Base resume match: {metrics['baseResumeMatch']}",
        f"Tailored resume match: {metrics['tailoredResumeMatch']}",
        f"Match lift: +{metrics['matchDelta']}",
        f"Recommended action: {metrics['recommendedAction']['priority']}",
        "",
        "## Supported Keywords Used",
        "",
    ]
    lines.extend(f"- {item}" for item in keywords)
    lines.extend(["", "## Unconfirmed Keywords Not Added As Claims", ""])
    lines.extend(f"- {item}" for item in unconfirmed)
    if not unconfirmed:
        lines.append("- None detected.")
    lines.extend([
        "",
        "## Match Analysis",
        "",
        f"- Base keyword coverage: {metrics['baseCoveragePercent']}%",
        f"- Tailored keyword coverage: {metrics['tailoredCoveragePercent']}%",
        f"- Covered by tailored resume: {', '.join(metrics['tailoredCoveredKeywords']) if metrics['tailoredCoveredKeywords'] else 'None'}",
        f"- Still missing or unconfirmed: {', '.join(metrics['tailoredMissingKeywords'] + unconfirmed) if (metrics['tailoredMissingKeywords'] or unconfirmed) else 'None'}",
        "",
        "## Interview Strategy",
        "",
        f"- Priority: {metrics['recommendedAction']['priority']}",
        f"- Next action: {metrics['recommendedAction']['nextAction']}",
        f"- Interview hook: {metrics['recommendedAction']['interviewHook']}",
        f"- Outreach subject: {metrics['recommendedAction']['outreachSubject']}",
    ])
    if metrics["recommendedAction"]["cautions"]:
        lines.extend(["", "## Cautions", ""])
        lines.extend(f"- {item}" for item in metrics["recommendedAction"]["cautions"])
    lines.extend([
        "",
        "## Moral Tailoring Guardrail",
        "",
        "This tailored resume only uses skills, tools, dates, metrics, and experience grounded in the base resume/profile. Unsupported tools are not claimed as experience.",
        "",
        "## Job Summary Used",
        "",
        shorten(str(job.get("description", "")), width=1200, placeholder="..."),
    ])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def main() -> None:
    payload = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    jobs = payload.get("jobs", [])
    top_jobs = sorted(jobs, key=fit_score, reverse=True)[:15]
    base_text = BASE_PROFILE_FILE.read_text(encoding="utf-8")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest = {"generatedAt": str(date.today()), "resumes": []}

    for rank, job in enumerate(top_jobs, start=1):
        keywords = extract_supported_keywords(job)
        job_keywords = extract_job_supported_keywords(job)
        unconfirmed = extract_unconfirmed_keywords(job)
        essential_keywords = job_keywords or keywords[:5]
        base_match = match_score_for_text(job, base_text, essential_keywords, unconfirmed)
        tailored_text = tailored_resume_text(job, keywords)
        tailored_match = match_score_for_text(job, tailored_text, essential_keywords, unconfirmed)
        seniority_risk = has_seniority_risk(job)
        base_resume_score, tailored_resume_score, match_delta = resume_match_scores(
            job, base_match, tailored_match, unconfirmed, seniority_risk
        )
        metrics = {
            "baseResumeMatch": base_resume_score,
            "tailoredResumeMatch": tailored_resume_score,
            "matchDelta": match_delta,
            "baseCoveragePercent": base_match["coveragePercent"],
            "tailoredCoveragePercent": tailored_match["coveragePercent"],
            "baseCoveredKeywords": base_match["coveredKeywords"],
            "baseMissingKeywords": base_match["missingKeywords"],
            "tailoredCoveredKeywords": tailored_match["coveredKeywords"],
            "tailoredMissingKeywords": tailored_match["missingKeywords"],
            "essentialKeywords": essential_keywords,
            "recommendedAction": action_plan(job, tailored_match["score"], base_match["score"], unconfirmed, seniority_risk),
        }
        file_stem = f"{rank:02d}_{slug(job.get('company', 'company'))}_{slug(job.get('role', 'role'))}"
        output_pdf = OUTPUT_DIR / f"{file_stem}.pdf"
        build_pdf(job, keywords, output_pdf)
        pdf_rel_from_board = "../" + output_pdf.relative_to(ROOT).as_posix()
        source_path = write_source(job, keywords, unconfirmed, pdf_rel_from_board, metrics)
        source_rel_from_board = "../" + source_path.relative_to(ROOT).as_posix()

        job["tailoredResumePdf"] = pdf_rel_from_board
        job["tailoredResumeSource"] = source_rel_from_board
        job["tailoredKeywords"] = keywords
        job["essentialKeywords"] = essential_keywords
        job["unconfirmedKeywords"] = unconfirmed
        job["tailoredRank"] = rank
        job["tailoredGeneratedAt"] = str(date.today())
        job.update(metrics)

        manifest["resumes"].append({
            "rank": rank,
            "company": job.get("company"),
            "role": job.get("role"),
            "fitScore": fit_score(job),
            "baseResumeMatch": metrics["baseResumeMatch"],
            "tailoredResumeMatch": metrics["tailoredResumeMatch"],
            "matchDelta": metrics["matchDelta"],
            "baseCoveragePercent": metrics["baseCoveragePercent"],
            "tailoredCoveragePercent": metrics["tailoredCoveragePercent"],
            "pdf": pdf_rel_from_board,
            "source": source_rel_from_board,
            "keywords": keywords,
            "essentialKeywords": essential_keywords,
            "unconfirmedKeywords": unconfirmed,
            "seniorityRisk": seniority_risk,
            "recommendedAction": metrics["recommendedAction"],
        })

    payload["jobs"] = jobs
    payload["tailoredGeneratedAt"] = str(date.today())
    DATA_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    MANIFEST_FILE.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps({"generated": len(manifest["resumes"]), "output": str(OUTPUT_DIR), "manifest": str(MANIFEST_FILE)}, indent=2))


if __name__ == "__main__":
    main()
