from __future__ import annotations

import argparse
import csv
import random
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import List

from faker import Faker
from openpyxl import Workbook
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


fake = Faker()


@dataclass
class PayrollCompensationRecord:
    employee_id: str
    full_name: str
    bank_account_number: str
    routing_number: str
    gross_pay: float
    tax_withholding: float
    bonus: float
    net_pay: float
    pay_period: str


def _sanitize_filename(value: str) -> str:
    sanitized = re.sub(r"[^A-Za-z0-9]+", "_", value).strip("_")
    return sanitized.lower() or "employee"


def _employee_id() -> str:
    return f"EMP-{random.randint(1, 99999):05d}"


def _bank_account_number() -> str:
    return "".join(str(random.randint(0, 9)) for _ in range(12))


def _routing_number() -> str:
    return f"{random.randint(100000000, 999999999)}"


def _pay_period() -> str:
    start = fake.date_between(start_date="-1y", end_date="today")
    end = fake.date_between_dates(date_start=start, date_end=start)
    # Bi-weekly style period for realistic payroll records.
    end = start.fromordinal(start.toordinal() + 13)
    return f"{start.isoformat()} to {end.isoformat()}"


def generate_fake_payroll_compensation_records(count: int) -> List[PayrollCompensationRecord]:
    """Generate fake payroll and compensation records."""
    records: List[PayrollCompensationRecord] = []

    for _ in range(count):
        gross_pay = round(random.uniform(2_500, 12_000), 2)
        tax_withholding = round(gross_pay * random.uniform(0.12, 0.32), 2)
        bonus = round(random.uniform(0, 2_500), 2)
        net_pay = round(gross_pay - tax_withholding + bonus, 2)

        record = PayrollCompensationRecord(
            employee_id=_employee_id(),
            full_name=fake.name(),
            bank_account_number=_bank_account_number(),
            routing_number=_routing_number(),
            gross_pay=gross_pay,
            tax_withholding=tax_withholding,
            bonus=bonus,
            net_pay=net_pay,
            pay_period=_pay_period(),
        )
        records.append(record)

    return records


def export_to_csv(records: List[PayrollCompensationRecord], output_path: Path) -> None:
    """Export payroll records to CSV."""
    if not records:
        raise ValueError("No payroll records provided for CSV export.")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=list(asdict(records[0]).keys()))
        writer.writeheader()
        for record in records:
            writer.writerow(asdict(record))


def export_to_xlsx(records: List[PayrollCompensationRecord], output_path: Path) -> None:
    """Export payroll records to XLSX."""
    if not records:
        raise ValueError("No payroll records provided for XLSX export.")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Payroll Compensation"

    headers = list(asdict(records[0]).keys())
    sheet.append(headers)

    for record in records:
        row = [asdict(record)[header] for header in headers]
        sheet.append(row)

    workbook.save(output_path)


def export_to_payslip_pdfs(records: List[PayrollCompensationRecord], output_dir: Path) -> List[Path]:
    """Create one PDF payslip per employee payroll record."""
    if not records:
        raise ValueError("No payroll records provided for PDF export.")

    output_dir.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()
    generated_files: List[Path] = []

    for idx, record in enumerate(records, start=1):
        filename = f"{_sanitize_filename(record.full_name)}_{idx:03d}.pdf"
        output_path = output_dir / filename
        doc = SimpleDocTemplate(str(output_path), pagesize=LETTER)

        elements = [
            Paragraph("Payroll Payslip", styles["Title"]),
            Spacer(1, 10),
            Paragraph(f"Employee ID: {record.employee_id}", styles["Normal"]),
            Paragraph(f"Employee Name: {record.full_name}", styles["Normal"]),
            Paragraph(f"Pay Period: {record.pay_period}", styles["Normal"]),
            Spacer(1, 8),
            Paragraph(f"Bank Account Number: {record.bank_account_number}", styles["Normal"]),
            Paragraph(f"Routing Number: {record.routing_number}", styles["Normal"]),
            Spacer(1, 8),
            Paragraph(f"Gross Pay: ${record.gross_pay:,.2f}", styles["Normal"]),
            Paragraph(f"Tax Withholding: ${record.tax_withholding:,.2f}", styles["Normal"]),
            Paragraph(f"Bonus: ${record.bonus:,.2f}", styles["Normal"]),
            Paragraph(f"Net Pay: ${record.net_pay:,.2f}", styles["Normal"]),
        ]

        doc.build(elements)
        generated_files.append(output_path)

    return generated_files


def generate_and_export_payroll_compensation(
    count: int,
    output_dir: str | Path,
) -> List[PayrollCompensationRecord]:
    """Reusable helper to generate payroll data and export CSV, XLSX, and PDF payslips."""
    output_path = Path(output_dir)
    records = generate_fake_payroll_compensation_records(count=count)

    export_to_csv(records, output_path / "payroll_compensation.csv")
    export_to_xlsx(records, output_path / "payroll_compensation.xlsx")
    export_to_payslip_pdfs(records, output_path / "pdfs")

    return records


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate fake payroll and compensation records in CSV, XLSX, and PDF payslip formats."
    )
    parser.add_argument("--count", type=int, default=10, help="Number of payroll records to generate")
    parser.add_argument("--output-root", default="output", help="Base output directory")
    parser.add_argument("--category", default="payroll_compensation", help="Output category folder name")

    args = parser.parse_args()

    output_dir = Path(args.output_root) / args.category
    records = generate_and_export_payroll_compensation(count=args.count, output_dir=output_dir)

    print(f"Generated {len(records)} payroll compensation records.")
    print(f"CSV: {(output_dir / 'payroll_compensation.csv').resolve()}")
    print(f"XLSX: {(output_dir / 'payroll_compensation.xlsx').resolve()}")
    print(f"PDF directory: {(output_dir / 'pdfs').resolve()}")


if __name__ == "__main__":
    main()
