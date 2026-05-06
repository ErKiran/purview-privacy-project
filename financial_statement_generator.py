from __future__ import annotations

import argparse
import csv
import random
import re
from dataclasses import dataclass, asdict
from datetime import date, timedelta
from pathlib import Path
from typing import Iterable, List

from faker import Faker
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


fake = Faker()


@dataclass
class FinancialStatementRow:
    company_name: str
    fiscal_year: int
    start_date: str
    end_date: str
    statement_date: str
    revenue_gl_code: int
    revenue: float
    expenses_gl_code: int
    expenses: float
    net_income_gl_code: int
    net_income: float
    bank_account_number: str
    routing_number: str
    tax_id_ein: str
    auditor_name: str
    auditor_signature_block: str
    credit_card_number: str


def _random_date_range(fiscal_year: int) -> tuple[date, date, date]:
    start = date(fiscal_year, 1, 1)
    end = date(fiscal_year, 12, 31)
    statement = start + timedelta(days=random.randint(30, 364))
    return start, end, statement


def _bank_account_number() -> str:
    return "".join(str(random.randint(0, 9)) for _ in range(12))


def _routing_number() -> str:
    return f"{random.randint(100000000, 999999999)}"


def _ein() -> str:
    return f"{random.randint(10, 99)}-{random.randint(1000000, 9999999)}"


def _credit_card_number() -> str:
    return fake.credit_card_number()


def _sanitize_filename(value: str) -> str:
    sanitized = re.sub(r"[^A-Za-z0-9]+", "_", value).strip("_")
    return sanitized.lower() or "company"


def generate_fake_financial_statements(count: int, fiscal_year: int) -> List[FinancialStatementRow]:
    """Generate fake financial statement rows with realistic finance-sensitive fields."""
    rows: List[FinancialStatementRow] = []

    for _ in range(count):
        company_name = fake.company()
        start_date, end_date, statement_date = _random_date_range(fiscal_year)

        revenue = round(random.uniform(150_000, 8_000_000), 2)
        expenses = round(random.uniform(80_000, revenue * 0.92), 2)
        net_income = round(revenue - expenses, 2)

        auditor = f"{fake.first_name()} {fake.last_name()}, CPA"

        row = FinancialStatementRow(
            company_name=company_name,
            fiscal_year=fiscal_year,
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
            statement_date=statement_date.isoformat(),
            revenue_gl_code=1001,
            revenue=revenue,
            expenses_gl_code=2045,
            expenses=expenses,
            net_income_gl_code=3001,
            net_income=net_income,
            bank_account_number=_bank_account_number(),
            routing_number=_routing_number(),
            tax_id_ein=_ein(),
            auditor_name=auditor,
            auditor_signature_block=f"Signed electronically by {auditor}",
            credit_card_number=_credit_card_number(),
        )

        rows.append(row)

    return rows


def export_to_csv(rows: Iterable[FinancialStatementRow], output_path: Path) -> None:
    """Write generated statement rows to a CSV file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    rows_list = list(rows)
    if not rows_list:
        raise ValueError("No rows provided for CSV export.")

    with output_path.open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=list(asdict(rows_list[0]).keys()))
        writer.writeheader()
        for row in rows_list:
            writer.writerow(asdict(row))


def export_to_individual_pdfs(rows: Iterable[FinancialStatementRow], output_dir: Path) -> List[Path]:
    """Write one generic financial statement PDF per generated record."""
    output_dir.mkdir(parents=True, exist_ok=True)
    rows_list = list(rows)
    if not rows_list:
        raise ValueError("No rows provided for PDF export.")

    styles = getSampleStyleSheet()
    generated_files: List[Path] = []

    for idx, row in enumerate(rows_list, start=1):
        company_slug = _sanitize_filename(row.company_name)
        output_path = output_dir / f"{company_slug}_{idx:03d}.pdf"
        doc = SimpleDocTemplate(str(output_path), pagesize=LETTER)
        elements = [
            Paragraph("Financial Statement", styles["Title"]),
            Spacer(1, 10),
            Paragraph(f"Company: {row.company_name}", styles["Normal"]),
            Paragraph(f"Fiscal Year: {row.fiscal_year}", styles["Normal"]),
            Paragraph(f"Date Range: {row.start_date} to {row.end_date}", styles["Normal"]),
            Paragraph(f"Statement Date: {row.statement_date}", styles["Normal"]),
            Spacer(1, 8),
            Paragraph(f"Revenue (GL {row.revenue_gl_code}): ${row.revenue:,.2f}", styles["Normal"]),
            Paragraph(f"Expenses (GL {row.expenses_gl_code}): ${row.expenses:,.2f}", styles["Normal"]),
            Paragraph(f"Net Income (GL {row.net_income_gl_code}): ${row.net_income:,.2f}", styles["Normal"]),
            Spacer(1, 8),
            Paragraph(f"Bank Account Number: {row.bank_account_number}", styles["Normal"]),
            Paragraph(f"Routing Number: {row.routing_number}", styles["Normal"]),
            Paragraph(f"Tax ID / EIN: {row.tax_id_ein}", styles["Normal"]),
            Paragraph(f"Credit Card Number: {row.credit_card_number}", styles["Normal"]),
            Spacer(1, 12),
            Paragraph(f"Auditor: {row.auditor_name}", styles["Normal"]),
            Paragraph(row.auditor_signature_block, styles["Normal"]),
        ]

        doc.build(elements)
        generated_files.append(output_path)

    return generated_files


def generate_and_export(
    count: int,
    fiscal_year: int,
    csv_path: str | Path,
    pdf_output_dir: str | Path,
) -> List[FinancialStatementRow]:
    """Reusable one-call helper: generate rows and export CSV + individual PDFs."""
    rows = generate_fake_financial_statements(count=count, fiscal_year=fiscal_year)
    export_to_csv(rows, Path(csv_path))
    export_to_individual_pdfs(rows, Path(pdf_output_dir))
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate fake financial statements and export to CSV and PDF."
    )
    parser.add_argument("--count", type=int, default=10, help="Number of statements to generate")
    parser.add_argument("--year", type=int, default=date.today().year, help="Fiscal year")
    parser.add_argument(
        "--output-root",
        default="output",
        help="Base output directory",
    )
    parser.add_argument(
        "--category",
        default="financial",
        help="Output category folder name",
    )
    parser.add_argument("--csv", default=None, help="CSV output path (optional override)")
    parser.add_argument(
        "--pdf-dir",
        default=None,
        help="Directory for individual PDF files (optional override)",
    )

    args = parser.parse_args()

    category_dir = Path(args.output_root) / args.category
    csv_path = Path(args.csv) if args.csv else category_dir / "statements.csv"
    pdf_output_dir = Path(args.pdf_dir) if args.pdf_dir else category_dir / "pdfs"

    generate_and_export(
        count=args.count,
        fiscal_year=args.year,
        csv_path=csv_path,
        pdf_output_dir=pdf_output_dir,
    )

    print(f"Generated {args.count} fake financial statements.")
    print(f"CSV: {csv_path.resolve()}")
    print(f"PDF directory: {pdf_output_dir.resolve()}")


if __name__ == "__main__":
    main()
