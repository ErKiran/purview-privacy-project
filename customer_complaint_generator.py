from __future__ import annotations

import argparse
import csv
import random
import re
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import List

from faker import Faker
from openpyxl import Workbook


fake = Faker()


ISSUE_TYPES = [
    "billing dispute",
    "product defect",
    "service failure",
]


@dataclass
class CustomerComplaint:
    customer_full_name: str
    customer_email: str
    customer_phone: str
    account_or_order_id: str
    complaint_date: str
    case_number: str
    issue_type: str
    issue_description: str
    payment_method_mentioned: str
    home_address: str
    resolution_notes: str
    agent_name: str


def _sanitize_filename(value: str) -> str:
    sanitized = re.sub(r"[^A-Za-z0-9]+", "_", value).strip("_")
    return sanitized.lower() or "complaint"


def _order_id(complaint_year: int) -> str:
    return f"ORD-{complaint_year}-{random.randint(1, 99999):05d}"


def _case_number(complaint_year: int) -> str:
    return f"CASE-{complaint_year}-{random.randint(1, 99999):05d}"


def _payment_mention() -> str:
    card_brand = random.choice(["Visa", "Mastercard", "Amex", "Discover"])
    last4 = random.randint(1000, 9999)
    return f"I paid with my {card_brand} ending in {last4}"


def _issue_description(issue_type: str) -> str:
    templates = {
        "billing dispute": [
            "I was charged twice for the same order and need a refund.",
            "The invoice total does not match the checkout amount.",
            "I see an unauthorized fee on my monthly statement.",
        ],
        "product defect": [
            "The item stopped working after two days of use.",
            "The product arrived damaged and unusable.",
            "A key component is missing from the package.",
        ],
        "service failure": [
            "Support never followed up after opening the ticket.",
            "Delivery was delayed and no status updates were provided.",
            "The service appointment was canceled without notice.",
        ],
    }
    return random.choice(templates[issue_type])


def _resolution_notes(issue_type: str) -> str:
    notes = {
        "billing dispute": [
            "Validated duplicate charge; initiated refund within 5 business days.",
            "Adjusted invoice and sent corrected statement to customer.",
        ],
        "product defect": [
            "Approved replacement shipment and provided return label.",
            "Issued full refund after defect verification.",
        ],
        "service failure": [
            "Escalated to operations and applied courtesy account credit.",
            "Rescheduled service with priority handling and waived fee.",
        ],
    }
    return random.choice(notes[issue_type])


def generate_fake_customer_complaints(count: int) -> List[CustomerComplaint]:
    """Generate fake customer complaint records with realistic support-case details."""
    complaints: List[CustomerComplaint] = []

    for _ in range(count):
        complaint_dt = fake.date_between(start_date="-2y", end_date="today")
        issue_type = random.choice(ISSUE_TYPES)

        complaint = CustomerComplaint(
            customer_full_name=fake.name(),
            customer_email=fake.email(),
            customer_phone=fake.phone_number(),
            account_or_order_id=_order_id(complaint_dt.year),
            complaint_date=complaint_dt.isoformat(),
            case_number=_case_number(complaint_dt.year),
            issue_type=issue_type,
            issue_description=_issue_description(issue_type),
            payment_method_mentioned=_payment_mention(),
            home_address=fake.address().replace("\n", ", "),
            resolution_notes=_resolution_notes(issue_type),
            agent_name=f"{fake.first_name()} {fake.last_name()}",
        )
        complaints.append(complaint)

    return complaints


def export_to_csv(complaints: List[CustomerComplaint], output_path: Path) -> None:
    """Export complaints to CSV format."""
    if not complaints:
        raise ValueError("No complaints provided for CSV export.")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=list(asdict(complaints[0]).keys()))
        writer.writeheader()
        for complaint in complaints:
            writer.writerow(asdict(complaint))


def export_to_xlsx(complaints: List[CustomerComplaint], output_path: Path) -> None:
    """Export complaints to XLSX format."""
    if not complaints:
        raise ValueError("No complaints provided for XLSX export.")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Customer Complaints"

    headers = list(asdict(complaints[0]).keys())
    sheet.append(headers)

    for complaint in complaints:
        row = [asdict(complaint)[header] for header in headers]
        sheet.append(row)

    workbook.save(output_path)


def export_to_txt(complaints: List[CustomerComplaint], output_path: Path) -> None:
    """Export complaints to a plain-text report format."""
    if not complaints:
        raise ValueError("No complaints provided for TXT export.")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as txt_file:
        for idx, complaint in enumerate(complaints, start=1):
            txt_file.write(f"Complaint #{idx}\n")
            txt_file.write(f"Customer: {complaint.customer_full_name}\n")
            txt_file.write(f"Email: {complaint.customer_email}\n")
            txt_file.write(f"Phone: {complaint.customer_phone}\n")
            txt_file.write(f"Order ID: {complaint.account_or_order_id}\n")
            txt_file.write(f"Complaint Date: {complaint.complaint_date}\n")
            txt_file.write(f"Case Number: {complaint.case_number}\n")
            txt_file.write(f"Issue Type: {complaint.issue_type}\n")
            txt_file.write(f"Issue Description: {complaint.issue_description}\n")
            txt_file.write(f"Payment Mentioned: {complaint.payment_method_mentioned}\n")
            txt_file.write(f"Home Address: {complaint.home_address}\n")
            txt_file.write(f"Resolution Notes: {complaint.resolution_notes}\n")
            txt_file.write(f"Agent Name: {complaint.agent_name}\n")
            txt_file.write("\n" + "-" * 72 + "\n\n")


def _build_email_body(complaint: CustomerComplaint) -> str:
    return (
        f"Dear Support Team,\n\n"
        f"I am writing to report an issue regarding order/account {complaint.account_or_order_id}.\n"
        f"Case Number: {complaint.case_number}\n"
        f"Complaint Date: {complaint.complaint_date}\n\n"
        f"Issue Type: {complaint.issue_type}\n"
        f"Issue Details: {complaint.issue_description}\n"
        f"Payment Information: {complaint.payment_method_mentioned}\n"
        f"Return/Refund Address: {complaint.home_address}\n\n"
        f"Please contact me at {complaint.customer_email} or {complaint.customer_phone}.\n\n"
        f"Regards,\n"
        f"{complaint.customer_full_name}\n"
    )


def export_to_eml_and_email_text(
    complaints: List[CustomerComplaint],
    eml_dir: Path,
    body_text_dir: Path,
) -> List[Path]:
    """Export each complaint as both .eml and body text files."""
    if not complaints:
        raise ValueError("No complaints provided for email export.")

    eml_dir.mkdir(parents=True, exist_ok=True)
    body_text_dir.mkdir(parents=True, exist_ok=True)

    generated_files: List[Path] = []

    for idx, complaint in enumerate(complaints, start=1):
        base_name = f"{_sanitize_filename(complaint.customer_full_name)}_{idx:03d}"
        body = _build_email_body(complaint)

        eml_content = (
            f"From: {complaint.customer_email}\n"
            f"To: support@example.com\n"
            f"Subject: Complaint {complaint.case_number} - {complaint.issue_type}\n"
            f"Date: {date.fromisoformat(complaint.complaint_date).strftime('%a, %d %b %Y 09:00:00 -0000')}\n"
            f"MIME-Version: 1.0\n"
            f"Content-Type: text/plain; charset=\"utf-8\"\n"
            f"\n"
            f"{body}"
        )

        eml_path = eml_dir / f"{base_name}.eml"
        body_text_path = body_text_dir / f"{base_name}.txt"

        eml_path.write_text(eml_content, encoding="utf-8")
        body_text_path.write_text(body, encoding="utf-8")

        generated_files.extend([eml_path, body_text_path])

    return generated_files


def generate_and_export_customer_complaints(
    count: int,
    output_dir: str | Path,
) -> List[CustomerComplaint]:
    """Reusable helper to generate complaints and export CSV, XLSX, TXT, and EML/body text files."""
    output_path = Path(output_dir)
    complaints = generate_fake_customer_complaints(count=count)

    export_to_csv(complaints, output_path / "complaints.csv")
    export_to_xlsx(complaints, output_path / "complaints.xlsx")
    export_to_txt(complaints, output_path / "complaints.txt")
    export_to_eml_and_email_text(
        complaints,
        eml_dir=output_path / "emails",
        body_text_dir=output_path / "email_bodies",
    )

    return complaints


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate fake customer complaints in CSV, XLSX, TXT, and EML/body text formats."
    )
    parser.add_argument("--count", type=int, default=10, help="Number of complaints to generate")
    parser.add_argument("--output-root", default="output", help="Base output directory")
    parser.add_argument("--category", default="customer_complaints", help="Output category folder name")

    args = parser.parse_args()

    output_dir = Path(args.output_root) / args.category
    generate_and_export_customer_complaints(count=args.count, output_dir=output_dir)

    print(f"Generated {args.count} customer complaints.")
    print(f"CSV: {(output_dir / 'complaints.csv').resolve()}")
    print(f"XLSX: {(output_dir / 'complaints.xlsx').resolve()}")
    print(f"TXT: {(output_dir / 'complaints.txt').resolve()}")
    print(f"EML directory: {(output_dir / 'emails').resolve()}")
    print(f"Email body text directory: {(output_dir / 'email_bodies').resolve()}")


if __name__ == "__main__":
    main()
