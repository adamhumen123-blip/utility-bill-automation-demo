from pathlib import Path
import re

BASE_DIR = Path(__file__).resolve().parent
BILL_FILE = BASE_DIR / "sample_bill.txt"

def parse_bill_text(text: str) -> dict:
    patterns = {
        "provider_name": r"Provider Name:\s*(.*)",
        "account_number": r"Account Number:\s*(.*)",
        "billing_period": r"Billing Period:\s*(.*)",
        "amount_due": r"Amount Due:\s*(.*)",
        "due_date": r"Due Date:\s*(.*)",
        "usage": r"Usage:\s*(.*)",
        "bill_download_date": r"Bill Download Date:\s*(.*)",
    }

    result = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, text)
        result[key] = match.group(1).strip() if match else ""

    return result

def run_simulation():
    if not BILL_FILE.exists():
        raise FileNotFoundError(f"Sample bill not found: {BILL_FILE}")

    text = BILL_FILE.read_text(encoding="utf-8")
    bill_data = parse_bill_text(text)

    print("=== SIMULATED AUTOMATION OUTPUT ===")
    for key, value in bill_data.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    run_simulation()
