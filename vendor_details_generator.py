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


SERVICE_CATEGORIES = [
    "IT Services",
    "Logistics",
    "Catering",
    "Facilities",
    "Marketing",
    "Security",
    "Consulting",
]

PAYMENT_TERMS = [
    "Net 15",
    "Net 30",
    "Net 45",
    "Net 60",
]


@dataclass
class VendorDetail:
    vendor_company_name: str
    contact_person: str
    contact_title: str
    business_address: str
    phone: str
    email: str
    federal_tax_id: str
    w9_reference: str
    ach_routing_number: str
    ach_account_number: str
    contract_value: float
    payment_terms: str
    service_category: str
    vendor_id: str
    onboarding_date: str


def _sanitize_filename(value: str) -> str:
    sanitized = re.sub(r"[^A-Za-z0-9]+", "_", value).strip("_")
    return sanitized.lower() or "vendor"


def _federal_tax_id() -> str:
    return f"{random.randint(10, 99)}-{random.randint(1000000, 9999999)}"


def _routing_number() -> str:
    return f"{random.randint(100000000, 999999999)}"


def _account_number() -> str:
    return "".join(str(random.randint(0, 9)) for _ in range(12))


def _vendor_id() -> str:
    return f"VND-{random.randint(1, 99999):05d}"


def _w9_reference(vendor_id: str) -> str:
    return f"W9-{vendor_id}-{random.randint(100, 999)}"


def generate_fake_vendor_details(count: int) -> List[VendorDetail]:
    """Generate fake vendor detail records for procurement/onboarding scenarios."""
    records: List[VendorDetail] = []

    for _ in range(count):
        vendor_id = _vendor_id()
        contract_value = round(random.uniform(10_000, 3_000_000), 2)

        record = VendorDetail(
            vendor_company_name=fake.company(),
            contact_person=fake.name(),
            contact_title=fake.job(),
            business_address=fake.address().replace("\n", ", "),
            phone=fake.phone_number(),
            email=fake.company_email(),
            federal_tax_id=_federal_tax_id(),
            w9_reference=_w9_reference(vendor_id),
            ach_routing_number=_routing_number(),
            ach_account_number=_account_number(),
            contract_value=contract_value,
            payment_terms=random.choice(PAYMENT_TERMS),
            service_category=random.choice(SERVICE_CATEGORIES),
            vendor_id=vendor_id,
            onboarding_date=fake.date_between(start_date="-3y", end_date="today").isoformat(),
        )
        records.append(record)

    return records


def export_to_csv(records: List[VendorDetail], output_path: Path) -> None:
    """Export vendor details to CSV."""
    if not records:
        raise ValueError("No vendor records provided for CSV export.")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=list(asdict(records[0]).keys()))
        writer.writeheader()
        for record in records:
            writer.writerow(asdict(record))


def export_to_xlsx(records: List[VendorDetail], output_path: Path) -> None:
    """Export vendor details to XLSX."""
    if not records:
        raise ValueError("No vendor records provided for XLSX export.")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Vendor Details"

    headers = list(asdict(records[0]).keys())
    sheet.append(headers)

    for record in records:
        row = [asdict(record)[header] for header in headers]
        sheet.append(row)

    workbook.save(output_path)


def export_to_individual_pdfs(records: List[VendorDetail], output_dir: Path) -> List[Path]:
    """Create one PDF file per vendor record."""
    if not records:
        raise ValueError("No vendor records provided for PDF export.")

    output_dir.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()
    generated_files: List[Path] = []

    for idx, record in enumerate(records, start=1):
        filename = f"{_sanitize_filename(record.vendor_company_name)}_{idx:03d}.pdf"
        output_path = output_dir / filename
        doc = SimpleDocTemplate(str(output_path), pagesize=LETTER)

        elements = [
            Paragraph("Vendor Detail Record", styles["Title"]),
            Spacer(1, 10),
            Paragraph(f"Vendor Company Name: {record.vendor_company_name}", styles["Normal"]),
            Paragraph(f"Vendor ID: {record.vendor_id}", styles["Normal"]),
            Paragraph(f"Onboarding Date: {record.onboarding_date}", styles["Normal"]),
            Spacer(1, 8),
            Paragraph(f"Contact Person: {record.contact_person}", styles["Normal"]),
            Paragraph(f"Contact Title: {record.contact_title}", styles["Normal"]),
            Paragraph(f"Business Address: {record.business_address}", styles["Normal"]),
            Paragraph(f"Phone: {record.phone}", styles["Normal"]),
            Paragraph(f"Email: {record.email}", styles["Normal"]),
            Spacer(1, 8),
            Paragraph(f"Federal Tax ID: {record.federal_tax_id}", styles["Normal"]),
            Paragraph(f"W-9 Reference: {record.w9_reference}", styles["Normal"]),
            Paragraph(f"ACH Routing Number: {record.ach_routing_number}", styles["Normal"]),
            Paragraph(f"ACH Account Number: {record.ach_account_number}", styles["Normal"]),
            Spacer(1, 8),
            Paragraph(f"Service Category: {record.service_category}", styles["Normal"]),
            Paragraph(f"Payment Terms: {record.payment_terms}", styles["Normal"]),
            Paragraph(f"Contract Value: ${record.contract_value:,.2f}", styles["Normal"]),
        ]

        doc.build(elements)
        generated_files.append(output_path)

    return generated_files


def generate_and_export_vendor_details(
    count: int,
    output_dir: str | Path,
) -> List[VendorDetail]:
    """Reusable helper to generate vendor details and export CSV, XLSX, and PDF files."""
    output_path = Path(output_dir)
    records = generate_fake_vendor_details(count=count)

    export_to_csv(records, output_path / "vendor_details.csv")
    export_to_xlsx(records, output_path / "vendor_details.xlsx")
    export_to_individual_pdfs(records, output_path / "pdfs")

    return records


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate fake vendor details in CSV, XLSX, and PDF formats."
    )
    parser.add_argument("--count", type=int, default=10, help="Number of vendor records to generate")
    parser.add_argument("--output-root", default="output", help="Base output directory")
    parser.add_argument("--category", default="vendor_details", help="Output category folder name")

    args = parser.parse_args()

    output_dir = Path(args.output_root) / args.category
    records = generate_and_export_vendor_details(count=args.count, output_dir=output_dir)

    print(f"Generated {len(records)} vendor detail records.")
    print(f"CSV: {(output_dir / 'vendor_details.csv').resolve()}")
    print(f"XLSX: {(output_dir / 'vendor_details.xlsx').resolve()}")
    print(f"PDF directory: {(output_dir / 'pdfs').resolve()}")


if __name__ == "__main__":
    main()
