"""
main.py
=======
Primary entry point for the Utility Bill Automation system.

Usage:
    python main.py                          # Run all enabled providers
    python main.py --providers electricity  # Run specific provider(s)
    python main.py --providers electricity gas
    python main.py --dry-run               # Validate config without running
    python main.py --extract-only path/to/bill.pdf --provider "Electricity Provider"
"""

import argparse
import logging
import sys
from pathlib import Path

from config import PROVIDERS
from integrations.google_docs import create_monthly_report_doc
from logging_config import setup_logging
from pipelines.consolidate_data import generate_summary, log_summary_table, records_to_dataframe
from pipelines.export_reports import export_all
from pipelines.run_all_providers import run_all_providers

logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Utility Bill Automation — download, extract, and report utility bills."
    )
    parser.add_argument(
        "--providers",
        nargs="*",
        default=None,
        help="Provider keys to run (e.g. electricity gas water). Default: all enabled.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate configuration and print enabled providers without running automation.",
    )
    parser.add_argument(
        "--extract-only",
        metavar="PDF_PATH",
        help="Skip browser automation; extract data from a local PDF file only.",
    )
    parser.add_argument(
        "--provider",
        metavar="PROVIDER_NAME",
        default="Unknown",
        help="Provider name to use with --extract-only.",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging verbosity.",
    )
    parser.add_argument(
        "--no-google-doc",
        action="store_true",
        help="Skip Google Doc creation even if credentials are configured.",
    )
    return parser.parse_args()


def dry_run() -> None:
    """Print config summary without running any automation."""
    logger.info("DRY RUN — configuration check")
    logger.info("Enabled providers:")
    for key, cfg in PROVIDERS.items():
        status = "✓ enabled" if cfg.enabled else "✗ disabled"
        cred_ok = "✓ credentials set" if cfg.username and cfg.password else "✗ MISSING credentials"
        logger.info("  [%s] %s | %s | %s", key, cfg.name, status, cred_ok)

    from config import GOOGLE_CONFIG
    logger.info("Google Sheets: %s", "configured" if GOOGLE_CONFIG.available else "not configured")
    logger.info("Dry run complete — no automation executed.")


def extract_only_mode(pdf_path: str, provider_name: str) -> None:
    """Extract bill data from a local PDF without browser automation."""
    from extraction.bill_parser import extract_bill_record
    path = Path(pdf_path)
    if not path.exists():
        logger.error("PDF not found: %s", pdf_path)
        sys.exit(1)

    logger.info("Extract-only mode: %s", path)
    record = extract_bill_record(path, provider_name=provider_name)
    logger.info("Extracted record:\n%s", record.to_json())


def main() -> None:
    args = parse_args()
    setup_logging(log_level=args.log_level)
    logger.info("=" * 60)
    logger.info("Utility Bill Automation — starting run")
    logger.info("=" * 60)

    if args.dry_run:
        dry_run()
        return

    if args.extract_only:
        extract_only_mode(args.extract_only, args.provider)
        return

    # --- Full pipeline run ---
    records = run_all_providers(provider_keys=args.providers)

    if not records:
        logger.warning("No records returned — nothing to export.")
        return

    df = records_to_dataframe(records)
    summary = generate_summary(df)
    log_summary_table(df)

    output_paths = export_all(df, summary)
    for fmt, path in output_paths.items():
        logger.info("Output [%s]: %s", fmt.upper(), path)

    # Create Google Doc report
    if not args.no_google_doc:
        try:
            doc_url = create_monthly_report_doc(df, summary)
            if doc_url:
                logger.info("Google Doc report: %s", doc_url)
        except Exception as exc:
            logger.warning("Google Doc creation failed (non-fatal): %s", exc)

    logger.info("=" * 60)
    logger.info("Run complete.")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
