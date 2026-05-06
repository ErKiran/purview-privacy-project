# Fake Financial Statement Generator

Reusable Python function to generate fake financial statement data and export it to CSV plus one PDF per record.

Each PDF is named with the company name slug, for example `acme_corp_001.pdf`.

## What it generates

- Company name, fiscal year, date range, statement date
- Revenue, expenses, net income (with GL/account codes)
- Bank account number and routing number
- Fake Tax ID / EIN
- Auditor name and signature block
- Credit card number for expense reporting

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
python financial_statement_generator.py --count 10 --year 2026
```

Default output layout is category-based:

- `output/financial/statements.csv`
- `output/financial/pdfs/*.pdf`

You can change category (for future datasets) with:

```bash
python financial_statement_generator.py --category financial --output-root output
```

You can still override exact paths with `--csv` and `--pdf-dir`.

## Reusable function

Import and call:

```python
from financial_statement_generator import generate_and_export

rows = generate_and_export(
    count=10,
    fiscal_year=2026,
    csv_path="output/financial/statements.csv",
    pdf_output_dir="output/financial/pdfs",
)
```

`rows` is a list of generated records if you want to post-process the data.

## Employee Resume PDFs

Use the employee resume generator to create one PDF per record.

Important: SSN is intentionally excluded.

### Run

```bash
python employee_resume_generator.py --count 10
```

Default output layout:

- `output/employee_resumes/pdfs/*.pdf`

### Reusable function

```python
from employee_resume_generator import generate_and_export_employee_resumes

files = generate_and_export_employee_resumes(
    count=10,
    pdf_output_dir="output/employee_resumes/pdfs",
)
```

## Customer Complaints

Generate customer complaint datasets with these fields:

- Customer full name, email, phone number
- Account/order ID and case number
- Complaint date
- Issue type and description
- Payment method mention text
- Home address
- Resolution notes and agent name

### Run

```bash
python customer_complaint_generator.py --count 10
```

Default output layout:

- `output/customer_complaints/complaints.csv`
- `output/customer_complaints/complaints.xlsx`
- `output/customer_complaints/complaints.txt`
- `output/customer_complaints/emails/*.eml`
- `output/customer_complaints/email_bodies/*.txt`

### Reusable function

```python
from customer_complaint_generator import generate_and_export_customer_complaints

records = generate_and_export_customer_complaints(
    count=10,
    output_dir="output/customer_complaints",
)
```

## Vendor Details

Generate vendor onboarding/procurement records with these fields:

- Vendor company name, contact person, and title
- Business address, phone, email
- Federal Tax ID and W-9 reference
- ACH routing/account details
- Contract value and payment terms
- Service category
- Vendor ID and onboarding date

### Run

```bash
python vendor_details_generator.py --count 10
```

Default output layout:

- `output/vendor_details/vendor_details.csv`
- `output/vendor_details/vendor_details.xlsx`
- `output/vendor_details/pdfs/*.pdf`

### Reusable function

```python
from vendor_details_generator import generate_and_export_vendor_details

records = generate_and_export_vendor_details(
    count=10,
    output_dir="output/vendor_details",
)
```

## Payroll and Compensation

Generate payroll records with these fields:

- Employee ID and full name
- Bank account number and routing number
- Gross pay, tax withholding, bonus, net pay
- Pay period

### Run

```bash
python payroll_compensation_generator.py --count 10
```

Default output layout:

- `output/payroll_compensation/payroll_compensation.csv`
- `output/payroll_compensation/payroll_compensation.xlsx`
- `output/payroll_compensation/pdfs/*.pdf`

### Reusable function

```python
from payroll_compensation_generator import generate_and_export_payroll_compensation

records = generate_and_export_payroll_compensation(
    count=10,
    output_dir="output/payroll_compensation",
)
```

## Purchase Orders

Generate purchase order records with these fields:

- PO ID
- Requester and approver
- Line items and unit price
- Cost center
- Ship-to address
- Contract reference

### Run

```bash
python purchase_order_generator.py --count 10
```

Default output layout:

- `output/purchase_orders/purchase_orders.csv`
- `output/purchase_orders/purchase_orders.xlsx`
- `output/purchase_orders/pdfs/*.pdf`

### Reusable function

```python
from purchase_order_generator import generate_and_export_purchase_orders

records = generate_and_export_purchase_orders(
    count=10,
    output_dir="output/purchase_orders",
)
```
# purview-privacy-project
