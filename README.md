A modular automation system designed to log into utility provider portals, download billing statements, extract key billing data, and compile structured reports for recurring processing.
# Utility Bill Automation System

> **Proposal Demo Repository**  
> A production-grade Python automation system for downloading, extracting, and reporting utility bills across multiple providers — built for maintainability at scale.

---

## Overview

This system automates the full lifecycle of utility bill management:

1. **Login** to each utility portal using securely stored credentials
2. **Download** the latest bill PDF automatically
3. **Extract** billing data (amount due, due date, usage, billing period) from the PDF
4. **Consolidate** all results into a structured report
5. **Export** to Google Sheets, Google Docs, CSV, and Excel
6. **Schedule** the entire process to run monthly (or at any interval)

The architecture is designed from the ground up for maintainability: when a utility provider changes its website layout, only a single isolated file needs to be updated.

---

## Key Features

| Feature | Details |
|---|---|
| Browser Automation | Playwright (Chromium, headless) |
| PDF Extraction | pdfplumber (primary) + pytesseract OCR (fallback) |
| Data Handling | pandas DataFrames |
| Google Integration | Sheets append + Docs report generation |
| Scheduling | APScheduler (cron or interval mode) |
| Cloud Deployment | Docker + GitHub Actions + Cloud Run ready |
| Secrets Management | Environment variables via `.env` (never hardcoded) |
| Error Handling | Per-provider isolation — one failure never breaks the run |
| Logging | Rotating file + console logs |
| Testing | pytest unit tests for parser, consolidation, registry |

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     main.py / scheduler.py               │
│                   (orchestration entry points)            │
└────────────────────────┬────────────────────────────────┘
                         │
         ┌───────────────▼──────────────────┐
         │     pipelines/run_all_providers   │
         │   (runs each enabled provider)    │
         └───────────────┬──────────────────┘
                         │
    ┌────────────────────▼────────────────────────┐
    │              providers/                      │
    │  base_provider.py  ←  shared browser logic   │
    │  electricity_provider.py  ←  login, nav, dl  │
    │  gas_provider.py          ←  login, nav, dl  │
    │  water_provider.py        ←  login, nav, dl  │
    └────────────────────┬────────────────────────┘
                         │ PDF path
    ┌────────────────────▼────────────────────────┐
    │              extraction/                     │
    │  pdf_extractor.py   ←  pdfplumber            │
    │  ocr_extractor.py   ←  pytesseract fallback  │
    │  bill_parser.py     ←  regex field parsing   │
    └────────────────────┬────────────────────────┘
                         │ BillRecord objects
    ┌────────────────────▼────────────────────────┐
    │              pipelines/                      │
    │  consolidate_data.py  ←  pandas DataFrame    │
    │  export_reports.py    ←  CSV / Excel / JSON  │
    └────────────────────┬────────────────────────┘
                         │
    ┌────────────────────▼────────────────────────┐
    │              integrations/                   │
    │  google_sheets.py  ←  append rows            │
    │  google_docs.py    ←  monthly report doc     │
    └─────────────────────────────────────────────┘
```

---

## Repository Structure

```
utility-bill-automation/
│
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── main.py                     ← Primary entry point
├── scheduler.py                ← APScheduler recurring runner
├── config.py                   ← All config from environment variables
├── logging_config.py           ← Console + rotating file logging
│
├── providers/
│   ├── __init__.py             ← Provider registry + dynamic loader
│   ├── base_provider.py        ← Shared browser automation base class
│   ├── electricity_provider.py ← Electricity portal automation
│   ├── gas_provider.py         ← Gas portal automation
│   └── water_provider.py       ← Water portal automation (+ MFA demo)
│
├── extraction/
│   ├── __init__.py
│   ├── pdf_extractor.py        ← pdfplumber text + table extraction
│   ├── ocr_extractor.py        ← pytesseract OCR fallback
│   └── bill_parser.py          ← Regex field parsing into BillRecord
│
├── pipelines/
│   ├── __init__.py
│   ├── run_all_providers.py    ← Orchestrates all provider runs
│   ├── consolidate_data.py     ← Builds pandas DataFrame + summary
│   └── export_reports.py       ← CSV, Excel, JSON, Sheets export
│
├── integrations/
│   ├── __init__.py
│   ├── google_sheets.py        ← Append rows to Google Sheet
│   └── google_docs.py          ← Create monthly report Google Doc
│
├── models/
│   ├── __init__.py
│   └── bill_record.py          ← BillRecord dataclass (canonical model)
│
├── utils/
│   ├── __init__.py
│   ├── file_utils.py           ← Path construction, PDF validation
│   ├── retry_utils.py          ← Retry decorator, safe_execute
│   ├── date_utils.py           ← Date parsing across bill formats
│   └── validation_utils.py     ← Amount/field validation + quality score
│
├── storage/
│   ├── bills/                  ← Downloaded PDFs (per provider/account)
│   ├── exports/                ← CSV, Excel, JSON reports
│   └── logs/                   ← Rotating log files
│
├── tests/
│   ├── test_bill_parser.py
│   ├── test_consolidation.py
│   └── test_provider_registry.py
│
└── .github/workflows/
    └── run-bills.yml           ← GitHub Actions scheduled workflow
```

---

## Setup Instructions

### 1. Clone and configure

```bash
git clone https://github.com/yourname/utility-bill-automation.git
cd utility-bill-automation
cp .env.example .env
# Edit .env with your real credentials
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Install Playwright browser

```bash
playwright install chromium
playwright install-deps chromium
```

### 4. (Optional) Install Tesseract OCR

Only needed if your utility providers use scanned/image PDFs:

```bash
# Ubuntu / Debian
sudo apt-get install tesseract-ocr tesseract-ocr-eng

# macOS
brew install tesseract

# Windows: download installer from https://github.com/UB-Mannheim/tesseract/wiki
```

---

## Environment Variable Reference

Copy `.env.example` to `.env` and fill in all values:

```dotenv
# Provider credentials (repeat pattern for each provider)
ELECTRICITY_USERNAME=your_username
ELECTRICITY_PASSWORD=your_password
ELECTRICITY_PORTAL_URL=https://your-electricity-portal.com
ELECTRICITY_ACCOUNT_NUMBER=EL-123456

# Google integrations
GOOGLE_SERVICE_ACCOUNT_JSON=credentials/service_account.json
GOOGLE_SHEETS_SPREADSHEET_ID=your_spreadsheet_id
GOOGLE_SHEETS_WORKSHEET_NAME=Bills
GOOGLE_DOCS_FOLDER_ID=your_drive_folder_id

# Browser settings
HEADLESS=true                         # false = watch automation (debug mode)

# Scheduler
SCHEDULE_MODE=cron
SCHEDULE_CRON_EXPRESSION=0 7 1 * *    # 7am on the 1st of each month
```

**Security**: Credentials are loaded from environment variables only. No secrets appear in code.  
For production, use a secrets manager (AWS Secrets Manager, GCP Secret Manager, GitHub Secrets).

---

## Running Locally

### Run all providers once

```bash
python main.py
```

### Run specific providers only

```bash
python main.py --providers electricity gas
```

### Dry run (validate config without automation)

```bash
python main.py --dry-run
```

### Extract from a local PDF (skip browser)

```bash
python main.py --extract-only storage/bills/my_bill.pdf --provider "Electricity Provider"
```

### Run tests

```bash
pytest tests/ -v
```

---

## Running with Docker

### Build and run once

```bash
docker compose up --build pipeline
```

### Run with the scheduler (long-running)

```bash
docker compose up scheduler
```

### Run tests inside Docker

```bash
docker compose run test
```

---

## Scheduling

The system supports two scheduling modes configured via `.env`:

**Cron mode** (recommended for monthly bills):
```dotenv
SCHEDULE_MODE=cron
SCHEDULE_CRON_EXPRESSION=0 7 1 * *    # 7:00 AM UTC on the 1st of every month
```

**Interval mode** (for frequent checks):
```dotenv
SCHEDULE_MODE=interval
SCHEDULE_INTERVAL_HOURS=24
```

Start the scheduler:
```bash
python scheduler.py          # Runs continuously, triggers on schedule
python scheduler.py --once   # Run immediately, then exit
```

---

## Google Sheets & Docs Setup

1. Create a Google Cloud project and enable the Sheets API and Drive API.
2. Create a **Service Account** and download the JSON key.
3. Save the JSON key to `credentials/service_account.json`.
4. Share your Google Sheet with the service account email address (Editor role).
5. Set `GOOGLE_SHEETS_SPREADSHEET_ID` and `GOOGLE_DOCS_FOLDER_ID` in `.env`.

The system will:
- Append one row per bill to the configured worksheet on each run.
- Create a new formatted Google Doc in the configured Drive folder each month.

If Google credentials are missing, the system falls back gracefully to CSV/Excel/JSON export only — the run does not fail.

---

## How to Add a New Provider

Adding a new utility provider requires editing **two files only**:

**Step 1** — Create `providers/new_provider.py`:

```python
from config import PROVIDERS
from providers.base_provider import BaseProvider

SELECTORS = {
    "login_username": "#username",
    "login_password": "#password",
    "login_submit":   "button[type='submit']",
    "login_success":  ".dashboard",
    "billing_nav":    "a:has-text('Bills')",
    "bill_row":       "table tbody tr:first-child",
    "download_btn":   "a.download-pdf",
}

class NewProvider(BaseProvider):
    def login(self):
        self._goto(f"{self.config.portal_url}/login")
        self._fill(SELECTORS["login_username"], self.config.username)
        self._fill(SELECTORS["login_password"], self.config.password)
        self._click(SELECTORS["login_submit"])
        self._wait_for(SELECTORS["login_success"])

    def navigate_to_billing(self):
        self._click(SELECTORS["billing_nav"])

    def find_latest_bill(self):
        return self._page.locator(SELECTORS["bill_row"]).inner_text()

    def download_bill(self):
        with self._page.expect_download() as dl:
            self._page.locator(SELECTORS["download_btn"]).click()
        target = self._download_dir / "bill.pdf"
        dl.value.save_as(str(target))
        return target

def create_provider():
    return NewProvider(config=PROVIDERS["new_provider"])
```

**Step 2** — Register in `providers/__init__.py`:

```python
PROVIDER_REGISTRY = {
    "electricity": "providers.electricity_provider",
    "gas":         "providers.gas_provider",
    "water":       "providers.water_provider",
    "new_provider": "providers.new_provider",   # ← add this line
}
```

**Step 3** — Add credentials to `config.py` and `.env`.

That's all. No other files need changing.

---

## When a Provider Changes Its Layout

Each provider module contains a clearly marked `SELECTORS` dictionary at the top of the file:

```python
# ============================================================
# SELECTORS — update this section when the portal changes its UI
# ============================================================
SELECTORS = {
    "login_username": "#username",      # ← update if field ID changes
    "login_submit":   "button[type='submit']",
    "bill_row":       "table tbody tr:first-child",  # ← update if table changes
    "download_btn":   "a.download-pdf",
}
```

**When a provider updates its website:**
1. Open the provider's `*_provider.py` file.
2. Update the relevant selector in the `SELECTORS` dictionary.
3. If the navigation flow changed, update the corresponding method (`login()`, `navigate_to_billing()`, etc.).
4. No other files need changing — all other providers are unaffected.

Selectors can be found using browser DevTools (F12 → inspect the element → copy selector).

---

## Sample Outputs

### Console log output

```
2024-05-01 07:00:12 | INFO     | provider.electricity_provider  | Logging in to https://electricity-portal.com
2024-05-01 07:00:18 | INFO     | provider.electricity_provider  | Login successful for Electricity Provider
2024-05-01 07:00:22 | INFO     | provider.electricity_provider  | Found latest bill: April 2024
2024-05-01 07:00:31 | INFO     | provider.electricity_provider  | Downloaded bill → storage/bills/electricity_provider/EL123456/April_2024_electricity_provider.pdf
2024-05-01 07:00:32 | INFO     | extraction.bill_parser         | Parsed bill for 'Electricity Provider': amount=$92.45, due=2024-05-15, status=success
2024-05-01 07:00:45 | INFO     | provider.gas_provider          | Login successful for Gas Provider
2024-05-01 07:01:03 | INFO     | pipelines.run_all_providers    | Run complete in 51.2s | Success: 2 | Partial: 1 | Failed: 0
```

### Exported CSV structure

```csv
provider_name,account_number,billing_period,amount_due,currency,due_date,usage,extraction_status,downloaded_at
Electricity Provider,EL-123456,April 2024,92.45,USD,2024-05-15,487 kWh,success,2024-05-01T07:00:32
Gas Provider,GS-789012,April 2024,67.20,USD,2024-04-30,28.5 CCF,success,2024-05-01T07:01:01
Water Provider,WA-345678,April 2024,38.90,USD,2024-05-20,4500 gal,partial,2024-05-01T07:01:28
```

### Sample parsed BillRecord object

```json
{
  "provider_name": "Electricity Provider",
  "account_number": "EL-123456",
  "billing_period": "April 2024",
  "amount_due": 92.45,
  "currency": "USD",
  "due_date": "2024-05-15",
  "usage": "487 kWh",
  "bill_file_path": "storage/bills/electricity_provider/EL123456/April_2024.pdf",
  "extraction_status": "success",
  "extraction_notes": "",
  "downloaded_at": "2024-05-01T07:00:32.145021"
}
```

---

## Scaling from 3 to 50 Providers

The architecture is designed specifically for this growth path:

| Scale | What changes |
|---|---|
| 3 providers (now) | 3 provider files, 3 entries in registry and config |
| 10 providers | Add 7 provider files + 7 config entries. Zero pipeline changes. |
| 50 providers | Add 47 more. Consider parallelising `run_all_providers()` with `concurrent.futures.ThreadPoolExecutor` for faster runs. |

**Parallelisation** (for 50 providers): each provider run is independent. A one-line change to `run_all_providers.py` can run all providers concurrently, cutting a 50-provider run from ~4 hours to ~15 minutes.

**Credentials at scale**: use a secrets manager (AWS Secrets Manager, GCP Secret Manager, HashiCorp Vault). The `config.py` file already reads all credentials from environment variables, so switching from `.env` to a secrets manager requires no code changes — only the secrets injection layer changes.

---

## Security Notes

- Credentials are stored as environment variables or GitHub Secrets — never in code.
- The `credentials/` directory is git-ignored.
- The Docker container runs as a non-root user.
- Browser automation runs headless with no persistent session storage.
- Downloaded PDFs are stored locally in `storage/bills/` — restrict filesystem access as appropriate.
- For production: rotate credentials regularly, use read-only portal accounts where possible.

---

## Cloud Deployment Options

### GitHub Actions (recommended for monthly runs)

Already included in `.github/workflows/run-bills.yml`. Configure GitHub Secrets with all provider credentials. The workflow runs automatically on the 1st of each month and uploads reports as artifacts.

### Google Cloud Run

```bash
gcloud builds submit --tag gcr.io/YOUR_PROJECT/ubill
gcloud run jobs create ubill-pipeline \
  --image gcr.io/YOUR_PROJECT/ubill \
  --command python,main.py \
  --set-env-vars="$(cat .env | tr '\n' ',')"
gcloud scheduler jobs create http ubill-monthly \
  --schedule="0 7 1 * *" \
  --uri="https://CLOUD_RUN_JOB_URL/run"
```

### DigitalOcean / VPS

```bash
# On the server:
git clone https://github.com/yourname/utility-bill-automation.git
cd utility-bill-automation
cp .env.example .env && nano .env
docker compose up -d scheduler
```

The scheduler container runs continuously and triggers the pipeline on schedule, with automatic restart on failure.

---

## Maintenance Notes

- **Provider selector changes**: edit only the relevant `providers/*_provider.py` SELECTORS dict.
- **New extraction patterns**: add regex patterns to `extraction/bill_parser.py` PATTERNS dict.
- **New export formats**: add a function to `pipelines/export_reports.py` and call it from `export_all()`.
- **New Google integration**: extend `integrations/google_docs.py` or add a new integration module.
- **Log rotation**: logs are automatically rotated at 5 MB with 10 backups kept.
- **Storage cleanup**: implement a periodic cleanup in `utils/file_utils.py` to archive old PDFs.

---

*Built with Playwright · pdfplumber · pandas · Google APIs · APScheduler · Docker*
