from __future__ import annotations

import argparse
import csv
import random
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import List

from faker import Faker
from openpyxl import Workbook
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


fake = Faker()


@dataclass
class PurchaseOrderLineItem:
    item_description: str
    quantity: int
    unit_price: float
    line_total: float


@dataclass
class PurchaseOrderRecord:
    po_id: str
    requester: str
    approver: str
    line_items: List[PurchaseOrderLineItem] = field(default_factory=list)
    total_amount: float = 0.0
    cost_center: str = ""
    ship_to_address: str = ""
    contract_reference: str = ""


def _sanitize_filename(value: str) -> str:
    sanitized = re.sub(r"[^A-Za-z0-9]+", "_", value).strip("_")
    return sanitized.lower() or "po"


def _po_id() -> str:
    year = fake.date_this_year().year
    return f"PO-{year}-{random.randint(1, 99999):05d}"


def _cost_center() -> str:
    return f"CC-{random.randint(1000, 9999)}"


def _contract_reference() -> str:
    year = fake.date_this_decade().year
    return f"CTR-{year}-{random.randint(1, 99999):05d}"


def _line_items() -> List[PurchaseOrderLineItem]:
    items: List[PurchaseOrderLineItem] = []
    item_count = random.randint(2, 6)

    for _ in range(item_count):
        quantity = random.randint(1, 25)
        unit_price = round(random.uniform(25, 2500), 2)
        line_total = round(quantity * unit_price, 2)
        items.append(
            PurchaseOrderLineItem(
                item_description=fake.bs().capitalize(),
                quantity=quantity,
                unit_price=unit_price,
                line_total=line_total,
            )
        )

    return items


def generate_fake_purchase_orders(count: int) -> List[PurchaseOrderRecord]:
    """Generate fake purchase order records with realistic procurement fields."""
    records: List[PurchaseOrderRecord] = []

    for _ in range(count):
        line_items = _line_items()
        total = round(sum(item.line_total for item in line_items), 2)

        record = PurchaseOrderRecord(
            po_id=_po_id(),
            requester=fake.name(),
            approver=fake.name(),
            line_items=line_items,
            total_amount=total,
            cost_center=_cost_center(),
            ship_to_address=fake.address().replace("\n", ", "),
            contract_reference=_contract_reference(),
        )
        records.append(record)

    return records


def export_to_csv(records: List[PurchaseOrderRecord], output_path: Path) -> None:
    """Export purchase order records to CSV."""
    if not records:
        raise ValueError("No purchase order records provided for CSV export.")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    headers = [
        "po_id",
        "requester",
        "approver",
        "line_items",
        "unit_price",
        "cost_center",
        "ship_to_address",
        "contract_reference",
        "total_amount",
    ]

    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=headers)
        writer.writeheader()

        for record in records:
            item_names = "; ".join(item.item_description for item in record.line_items)
            unit_prices = "; ".join(f"{item.unit_price:.2f}" for item in record.line_items)
            writer.writerow(
                {
                    "po_id": record.po_id,
                    "requester": record.requester,
                    "approver": record.approver,
                    "line_items": item_names,
                    "unit_price": unit_prices,
                    "cost_center": record.cost_center,
                    "ship_to_address": record.ship_to_address,
                    "contract_reference": record.contract_reference,
                    "total_amount": f"{record.total_amount:.2f}",
                }
            )


def export_to_xlsx(records: List[PurchaseOrderRecord], output_path: Path) -> None:
    """Export purchase order records to XLSX."""
    if not records:
        raise ValueError("No purchase order records provided for XLSX export.")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Purchase Orders"

    headers = [
        "po_id",
        "requester",
        "approver",
        "line_items",
        "unit_price",
        "cost_center",
        "ship_to_address",
        "contract_reference",
        "total_amount",
    ]
    sheet.append(headers)

    for record in records:
        item_names = "; ".join(item.item_description for item in record.line_items)
        unit_prices = "; ".join(f"{item.unit_price:.2f}" for item in record.line_items)
        sheet.append(
            [
                record.po_id,
                record.requester,
                record.approver,
                item_names,
                unit_prices,
                record.cost_center,
                record.ship_to_address,
                record.contract_reference,
                record.total_amount,
            ]
        )

    workbook.save(output_path)


def export_to_individual_pdfs(records: List[PurchaseOrderRecord], output_dir: Path) -> List[Path]:
    """Create one PDF file per purchase order record."""
    if not records:
        raise ValueError("No purchase order records provided for PDF export.")

    output_dir.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()
    generated_files: List[Path] = []

    for idx, record in enumerate(records, start=1):
        filename = f"{_sanitize_filename(record.po_id)}_{idx:03d}.pdf"
        output_path = output_dir / filename
        doc = SimpleDocTemplate(str(output_path), pagesize=LETTER)

        elements = [
            Paragraph("Purchase Order", styles["Title"]),
            Spacer(1, 10),
            Paragraph(f"PO ID: {record.po_id}", styles["Normal"]),
            Paragraph(f"Requester: {record.requester}", styles["Normal"]),
            Paragraph(f"Approver: {record.approver}", styles["Normal"]),
            Paragraph(f"Cost Center: {record.cost_center}", styles["Normal"]),
            Paragraph(f"Ship-To Address: {record.ship_to_address}", styles["Normal"]),
            Paragraph(f"Contract Reference: {record.contract_reference}", styles["Normal"]),
            Spacer(1, 8),
            Paragraph("Line Items", styles["Heading3"]),
        ]

        for item in record.line_items:
            elements.append(
                Paragraph(
                    f"- {item.item_description} | Qty: {item.quantity} | Unit Price: ${item.unit_price:,.2f} | Line Total: ${item.line_total:,.2f}",
                    styles["Normal"],
                )
            )

        elements.extend(
            [
                Spacer(1, 8),
                Paragraph(f"Total Amount: ${record.total_amount:,.2f}", styles["Heading3"]),
            ]
        )

        doc.build(elements)
        generated_files.append(output_path)

    return generated_files


def generate_and_export_purchase_orders(
    count: int,
    output_dir: str | Path,
) -> List[PurchaseOrderRecord]:
    """Reusable helper to generate purchase orders and export PDF, CSV, and XLSX."""
    output_path = Path(output_dir)
    records = generate_fake_purchase_orders(count=count)

    export_to_csv(records, output_path / "purchase_orders.csv")
    export_to_xlsx(records, output_path / "purchase_orders.xlsx")
    export_to_individual_pdfs(records, output_path / "pdfs")

    return records


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate fake purchase orders in PDF, CSV, and XLSX formats."
    )
    parser.add_argument("--count", type=int, default=10, help="Number of purchase orders to generate")
    parser.add_argument("--output-root", default="output", help="Base output directory")
    parser.add_argument("--category", default="purchase_orders", help="Output category folder name")

    args = parser.parse_args()

    output_dir = Path(args.output_root) / args.category
    records = generate_and_export_purchase_orders(count=args.count, output_dir=output_dir)

    print(f"Generated {len(records)} purchase order records.")
    print(f"CSV: {(output_dir / 'purchase_orders.csv').resolve()}")
    print(f"XLSX: {(output_dir / 'purchase_orders.xlsx').resolve()}")
    print(f"PDF directory: {(output_dir / 'pdfs').resolve()}")


if __name__ == "__main__":
    main()
