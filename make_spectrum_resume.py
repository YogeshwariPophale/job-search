from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.pdfbase.pdfmetrics import stringWidth


OUTPUT = "output/pdf/yogeshwari_pophale_spectrum_ats_resume.pdf"
CONTACT_DISPLAY = (
    "+1 (951) 830-2153 | yspophale@gmail.com | ypoph001@ucr.edu | "
    "linkedin.com/in/yogeshwari-pophale-281b80206 | github.com/YogeshwariPophale"
)


def esc(text):
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def fit_style(base_name, font_name, font_size, leading, available_width, text, min_size=6.5):
    size = font_size
    while size > min_size and stringWidth(text, font_name, size) > available_width:
        size -= 0.25
    return ParagraphStyle(
        base_name,
        fontName=font_name,
        fontSize=size,
        leading=max(leading - (font_size - size), size + 1),
        textColor=colors.HexColor("#202020"),
        alignment=1,
        spaceAfter=0,
    )


doc = SimpleDocTemplate(
    OUTPUT,
    pagesize=letter,
    rightMargin=0.32 * inch,
    leftMargin=0.32 * inch,
    topMargin=0.25 * inch,
    bottomMargin=0.24 * inch,
)

usable_width = letter[0] - doc.leftMargin - doc.rightMargin

styles = {
    "name": ParagraphStyle(
        "Name",
        fontName="Helvetica-Bold",
        fontSize=13.5,
        leading=14.2,
        alignment=1,
        textColor=colors.HexColor("#1f1f1f"),
        spaceAfter=2,
    ),
    "contact": fit_style(
        "Contact",
        "Helvetica",
        7.7,
        8.4,
        usable_width,
        CONTACT_DISPLAY,
    ),
    "section": ParagraphStyle(
        "Section",
        fontName="Helvetica-Bold",
        fontSize=9.1,
        leading=9.5,
        textColor=colors.HexColor("#1f1f1f"),
        uppercase=True,
        borderWidth=0,
        borderPadding=0,
        spaceBefore=4,
        spaceAfter=1,
    ),
    "body": ParagraphStyle(
        "Body",
        fontName="Helvetica",
        fontSize=7.75,
        leading=8.45,
        textColor=colors.HexColor("#202020"),
        spaceAfter=1.2,
    ),
    "small": ParagraphStyle(
        "Small",
        fontName="Helvetica",
        fontSize=7.35,
        leading=8.05,
        textColor=colors.HexColor("#202020"),
        spaceAfter=1,
    ),
    "job": ParagraphStyle(
        "Job",
        fontName="Helvetica-Bold",
        fontSize=8.25,
        leading=8.75,
        textColor=colors.HexColor("#1f1f1f"),
        spaceBefore=2,
        spaceAfter=0.4,
    ),
    "right": ParagraphStyle(
        "Right",
        fontName="Helvetica",
        fontSize=7.35,
        leading=8.05,
        alignment=2,
        textColor=colors.HexColor("#404040"),
        spaceAfter=0,
    ),
    "bullet": ParagraphStyle(
        "Bullet",
        fontName="Helvetica",
        fontSize=7.35,
        leading=8.1,
        leftIndent=8,
        firstLineIndent=-5,
        bulletIndent=0,
        textColor=colors.HexColor("#202020"),
        spaceAfter=0.25,
    ),
}


def section(title):
    return [
        Paragraph(title.upper(), styles["section"]),
        Table([[""]], colWidths=[usable_width], rowHeights=[0.8], style=TableStyle([
            ("LINEABOVE", (0, 0), (-1, -1), 0.5, colors.HexColor("#bdbdbd")),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ])),
    ]


def two_col(left, right, style_left="job"):
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


def bullet(text):
    return Paragraph(esc(text), styles["bullet"], bulletText="-")


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
story.append(Paragraph(
    esc("Computational Data Science M.S. candidate with analytics experience across manufacturing, operations, business, and engineering datasets. Skilled in SQL, Python, Excel, Tableau, Power BI, SAP, ETL/data quality pipelines, metrics design, dashboard development, data visualization, statistical analysis, anomaly detection, reporting design, and hypothesis-driven problem solving. Translate raw and complex data into actionable recommendations, customer-readable reports, and performance insights for cross-functional stakeholders."),
    styles["body"],
))

story += section("Education")
story.append(two_col("University of California, Riverside - M.S. Computational Data Science | GPA: 3.78/4.00", "Expected Mar 2027"))
story.append(Paragraph(esc("Coursework: Machine Learning, Data Analytics and Exploration, Databases, Artificial Intelligence, NLP, Data Mining, Data Ethics"), styles["small"]))
story.append(two_col("College of Engineering Pune (COEP) - B.Tech. Electrical Engineering | GPA: 7.86/10", "Graduated Aug 2024"))
story.append(Paragraph(esc("Coursework: DSA, Probability & Statistics, Embedded Systems, Analog/Digital Electronics, PCB Design, Circuit Integration, System Validation"), styles["small"]))

story += section("Technical Skills")
skills = [
    ("Programming & Databases", "SQL, PostgreSQL, MySQL, SQL Server, Python, PySpark, R, MATLAB, C/C++"),
    ("Analytics & Reporting", "ETL Pipelines, Data Extraction, Data Cleaning, Data Engineering, Data Quality Analysis, Exploratory Data Analysis, Statistical Analysis, Variance Analysis, Outlier Detection, Anomaly Detection, Metrics Design, KPI Reporting, Dashboard Development, Tableau, Power BI, Excel Reporting, Data Visualization, Reporting Design, Business Intelligence Workflows"),
    ("Business Analytics", "Business Requirements, Strategic Objectives, Hypothesis Development, Actionable Recommendations, Cross-functional Collaboration, Root Cause Analysis, Process Improvement, Production Analytics, Supply Chain Analytics, Manufacturing Operations, Data Governance"),
    ("Tools & Platforms", "Excel, Tableau, Power BI, SAP, Flask, Docker, Hadoop, Pandas, NumPy, Scikit-learn, Matplotlib, Git, Gemini API, Large Language Models, NLP Workflows"),
]
for label, value in skills:
    story.append(Paragraph(f"<b>{esc(label)}:</b> {esc(value)}", styles["small"]))

story += section("Professional Experience")
story.append(two_col("Bajaj Auto Limited | Graduate Trainee Engineer", "Aug 2024 - Aug 2025"))
for item in [
    "Developed Python-based ETL, reporting, validation, and data quality pipelines for manufacturing operations, reducing manual reporting effort by 40% while improving standardized analytics and reporting reliability.",
    "Extracted, cleaned, engineered, and analyzed SAP BOM, procurement, inventory, and production datasets using SQL and Python to support production planning, capacity visibility, and decision making across 200+ components.",
    "Designed KPI metrics, reporting logic, and dashboard views for production throughput, quality metrics, process deviations, and operational efficiency, enabling faster identification of corrective actions.",
    "Performed exploratory, statistical, and anomaly analysis for AMR deployment; developed hypotheses around bottlenecks, operational deviations, process variance, and optimization opportunities.",
    "Collaborated with production, planning, and procurement stakeholders to define business requirements, interpret complex datasets, and communicate actionable recommendations for manufacturing performance improvement.",
]:
    story.append(bullet(item))

story.append(two_col("Rolls-Royce Power Systems AG | Engineering Intern", "Jan 2024 - Jun 2024"))
for item in [
    "Automated Python engineering analysis workflows and simulation tooling for mtu S1600 engine validation, reducing validation cycle time by 85%.",
    "Analyzed engineering test, validation, and simulation datasets to identify anomaly patterns, failure trends, overheating indicators, quality risks, and system performance drivers.",
    "Applied statistical analysis and data profiling to investigate performance deviations, support root cause analysis, and translate findings into technical documentation, white papers, and optimization recommendations.",
]:
    story.append(bullet(item))

story.append(two_col("APTIV | Summer Intern", "May 2023 - Jul 2023"))
story.append(bullet("Designed vehicle wire harnesses with CATIA and LDorado for Volkswagen and BMW; supported validation, technical documentation, and change management activities."))

story += section("Campus Experience")
story.append(two_col("BUS173: Introduction to Databases for Management | Grader, UCR", "Winter 2026"))
story.append(bullet("Evaluated SQL assignments involving relational databases, joins, aggregations, query optimization, database design concepts, and structured query development for management analytics use cases."))
story.append(two_col("BUS175: Business Data Communications | Grader, UCR", "Spring 2026"))
story.append(bullet("Supported instruction in Python-based analytics, data transformation, visualization, business intelligence workflows, and customer-readable communication of analytical results."))

story += section("Projects")
story.append(two_col("AI-Powered Research Proposal Workflow Agent | Python, Gemini API, LLMs, NLP", "In Progress"))
story.append(bullet("Built a Gemini-powered workflow assistant for proposal planning, drafting, revision, evaluation, recommendation generation, structured quality assessment, automated feedback workflows, and repeatable review summaries."))
story.append(two_col("Hotel Reservation Analytics Platform | SQL, PostgreSQL, Flask, Hadoop, Docker", ""))
story.append(bullet("Built a PostgreSQL-Flask analytics platform for querying and visualizing reservation data with dynamic SQL filtering, scalable Hadoop/Docker processing, and analysis across pricing, booking, and customer dimensions."))

doc.build(story)
