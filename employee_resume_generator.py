from __future__ import annotations

import argparse
import random
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List

from faker import Faker
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


fake = Faker()


@dataclass
class EmploymentEntry:
    company_name: str
    title: str
    start_date: str
    end_date: str


@dataclass
class EmployeeResume:
    full_name: str
    address: str
    phone: str
    personal_email: str
    date_of_birth: str
    employment_history: List[EmploymentEntry]
    education: str
    gpa: float
    certifications: List[str]
    emergency_contact_name: str
    emergency_contact_relationship: str
    emergency_contact_phone: str
    salary_expectation: int
    salary_history: List[int]


def _sanitize_filename(value: str) -> str:
    sanitized = re.sub(r"[^A-Za-z0-9]+", "_", value).strip("_")
    return sanitized.lower() or "resume"


def _employment_history() -> List[EmploymentEntry]:
    entries: List[EmploymentEntry] = []
    years = sorted(random.sample(range(2012, 2025), k=3))
    for idx, start_year in enumerate(years):
        end_year = years[idx + 1] - 1 if idx < len(years) - 1 else 2026
        entries.append(
            EmploymentEntry(
                company_name=fake.company(),
                title=fake.job(),
                start_date=f"{start_year}-01-01",
                end_date=f"{end_year}-12-31",
            )
        )
    return entries


def _certifications() -> List[str]:
    pool = [
        "PMP",
        "AWS Certified Solutions Architect",
        "Certified ScrumMaster",
        "CompTIA Security+",
        "Google Data Analytics Certificate",
        "Six Sigma Green Belt",
    ]
    return random.sample(pool, k=3)


def _salary_history(base: int) -> List[int]:
    first = int(base * random.uniform(0.62, 0.72))
    second = int(base * random.uniform(0.78, 0.9))
    third = int(base * random.uniform(0.9, 1.0))
    return [first, second, third]


def generate_fake_employee_resumes(count: int) -> List[EmployeeResume]:
    """Generate fake employee resume records with sensitive-looking fields except SSN."""
    resumes: List[EmployeeResume] = []

    for _ in range(count):
        salary_expectation = random.randrange(70_000, 240_001, 1_000)

        resume = EmployeeResume(
            full_name=fake.name(),
            address=fake.address().replace("\n", ", "),
            phone=fake.phone_number(),
            personal_email=fake.email(),
            date_of_birth=fake.date_of_birth(minimum_age=22, maximum_age=65).isoformat(),
            employment_history=_employment_history(),
            education=f"{fake.random_element(elements=['B.S.', 'B.A.', 'M.S.', 'MBA'])} in {fake.random_element(elements=['Computer Science', 'Finance', 'Business Administration', 'Data Analytics', 'Information Systems'])}, {fake.company()} University",
            gpa=round(random.uniform(2.7, 4.0), 2),
            certifications=_certifications(),
            emergency_contact_name=fake.name(),
            emergency_contact_relationship=fake.random_element(elements=['Spouse', 'Sibling', 'Parent', 'Partner', 'Friend']),
            emergency_contact_phone=fake.phone_number(),
            salary_expectation=salary_expectation,
            salary_history=_salary_history(salary_expectation),
        )
        resumes.append(resume)

    return resumes


def export_employee_resumes_to_pdfs(resumes: List[EmployeeResume], output_dir: Path) -> List[Path]:
    """Create one PDF resume file per employee record."""
    if not resumes:
        raise ValueError("No resume records provided for PDF export.")

    output_dir.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()
    section_style = ParagraphStyle(
        name="SectionHeader",
        parent=styles["Heading3"],
        spaceBefore=8,
        spaceAfter=4,
    )

    generated: List[Path] = []

    for idx, resume in enumerate(resumes, start=1):
        filename = f"{_sanitize_filename(resume.full_name)}_{idx:03d}.pdf"
        output_path = output_dir / filename
        doc = SimpleDocTemplate(str(output_path), pagesize=LETTER)

        elements = [
            Paragraph("Employee Resume", styles["Title"]),
            Spacer(1, 8),
            Paragraph(f"Full Name: {resume.full_name}", styles["Normal"]),
            Paragraph(f"Address: {resume.address}", styles["Normal"]),
            Paragraph(f"Phone: {resume.phone}", styles["Normal"]),
            Paragraph(f"Personal Email: {resume.personal_email}", styles["Normal"]),
            Paragraph(f"Date of Birth: {resume.date_of_birth}", styles["Normal"]),
            Spacer(1, 8),
            Paragraph("Employment History", section_style),
        ]

        for job in resume.employment_history:
            elements.append(
                Paragraph(
                    f"{job.title} at {job.company_name} ({job.start_date} to {job.end_date})",
                    styles["Normal"],
                )
            )

        certs = ", ".join(resume.certifications)
        history_text = ", ".join(f"${amount:,.0f}" for amount in resume.salary_history)

        elements.extend(
            [
                Spacer(1, 8),
                Paragraph("Education", section_style),
                Paragraph(f"{resume.education}", styles["Normal"]),
                Paragraph(f"GPA: {resume.gpa}", styles["Normal"]),
                Paragraph(f"Certifications: {certs}", styles["Normal"]),
                Spacer(1, 8),
                Paragraph("Emergency Contact", section_style),
                Paragraph(f"Name: {resume.emergency_contact_name}", styles["Normal"]),
                Paragraph(f"Relationship: {resume.emergency_contact_relationship}", styles["Normal"]),
                Paragraph(f"Phone: {resume.emergency_contact_phone}", styles["Normal"]),
                Spacer(1, 8),
                Paragraph("Compensation", section_style),
                Paragraph(f"Salary Expectation: ${resume.salary_expectation:,.0f}", styles["Normal"]),
                Paragraph(f"Salary History: {history_text}", styles["Normal"]),
            ]
        )

        doc.build(elements)
        generated.append(output_path)

    return generated


def generate_and_export_employee_resumes(
    count: int,
    pdf_output_dir: str | Path,
) -> List[Path]:
    """Reusable one-call helper: generate fake employee resumes and export to PDFs."""
    resumes = generate_fake_employee_resumes(count=count)
    return export_employee_resumes_to_pdfs(resumes=resumes, output_dir=Path(pdf_output_dir))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate fake employee resumes and export individual PDF files."
    )
    parser.add_argument("--count", type=int, default=10, help="Number of employee resumes to generate")
    parser.add_argument("--output-root", default="output", help="Base output directory")
    parser.add_argument("--category", default="employee_resumes", help="Output category folder name")
    parser.add_argument(
        "--pdf-dir",
        default=None,
        help="Directory for individual resume PDF files (optional override)",
    )

    args = parser.parse_args()

    category_dir = Path(args.output_root) / args.category
    pdf_output_dir = Path(args.pdf_dir) if args.pdf_dir else category_dir / "pdfs"

    files = generate_and_export_employee_resumes(count=args.count, pdf_output_dir=pdf_output_dir)

    print(f"Generated {len(files)} employee resume PDF files.")
    print(f"PDF directory: {pdf_output_dir.resolve()}")


if __name__ == "__main__":
    main()
