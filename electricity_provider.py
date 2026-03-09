"""
providers/electricity_provider.py
==================================
Automation for the demo electricity portal.
Real target: https://demo-electricity-portal.com

=============================================================================
MAINTENANCE GUIDE — When the electricity portal changes its layout:
=============================================================================
1. LOGIN selectors    → update SELECTORS["login_*"] constants below
2. BILLING navigation → update SELECTORS["billing_nav"] and navigate_to_billing()
3. BILL ROW detection → update SELECTORS["bill_row"] and find_latest_bill()
4. DOWNLOAD trigger   → update SELECTORS["download_btn"] and download_bill()
=============================================================================
"""

import logging
import tempfile
from pathlib import Path
from typing import Optional

from playwright.sync_api import Download

from config import PROVIDERS
from models.bill_record import BillRecord
from providers.base_provider import BaseProvider

logger = logging.getLogger(__name__)

# =============================================================================
# SELECTORS — update this section when the portal changes its UI
# =============================================================================
SELECTORS = {
    "login_username":    "#username",
    "login_password":    "#password",
    "login_submit":      "button[type='submit']",
    "login_success":     ".dashboard-welcome",          # element visible after login
    "billing_nav":       "a[href*='billing'], a:has-text('Billing')",
    "bill_row":          "table.billing-history tbody tr:first-child",
    "bill_period":       "td.billing-period",
    "bill_amount":       "td.amount-due",
    "bill_due_date":     "td.due-date",
    "bill_usage":        "td.usage",
    "download_btn":      "a.download-pdf, button:has-text('Download PDF')",
}
# =============================================================================


class ElectricityProvider(BaseProvider):
    """Automation for demo electricity portal."""

    def login(self) -> None:
        """
        Log in to the electricity portal.

        MAINTENANCE: Update selectors in SELECTORS dict above if login page changes.
        """
        self.logger.info("Logging in to %s", self.config.portal_url)
        self._goto(f"{self.config.portal_url}/login")

        self._fill(SELECTORS["login_username"], self.config.username)
        self._fill(SELECTORS["login_password"], self.config.password)
        self._click(SELECTORS["login_submit"])

        # Wait for post-login indicator
        self._wait_for(SELECTORS["login_success"], timeout=15_000)
        self.logger.info("Login successful for %s", self.config.name)

    def navigate_to_billing(self) -> None:
        """
        Navigate from dashboard to the billing/statements page.

        MAINTENANCE: Update "billing_nav" selector or URL path if navigation changes.
        """
        self.logger.info("Navigating to billing section")
        self._click(SELECTORS["billing_nav"])
        self._wait_for(SELECTORS["bill_row"], timeout=15_000)

    def find_latest_bill(self) -> Optional[str]:
        """
        Identify the most recent bill row in the billing table.
        Returns billing period text as a reference, or None.

        MAINTENANCE: Update row/cell selectors if table structure changes.
        """
        assert self._page is not None
        try:
            period = self._page.locator(
                f"{SELECTORS['bill_row']} {SELECTORS['bill_period']}"
            ).inner_text(timeout=5_000)
            self.logger.info("Found latest bill: %s", period.strip())
            return period.strip()
        except Exception as exc:
            self.logger.warning("Could not find latest bill row: %s", exc)
            return None

    def download_bill(self) -> Optional[Path]:
        """
        Click the download button on the latest bill row and capture the file.

        MAINTENANCE: Update "download_btn" selector if the download trigger changes.
        """
        assert self._page is not None
        assert self._download_dir is not None

        try:
            with self._page.expect_download(timeout=30_000) as download_info:
                self._page.locator(
                    f"{SELECTORS['bill_row']} {SELECTORS['download_btn']}"
                ).click()

            download: Download = download_info.value
            target = self._download_dir / (download.suggested_filename or "electricity_bill.pdf")
            download.save_as(str(target))
            self.logger.info("Downloaded bill to temp: %s", target)
            return target
        except Exception as exc:
            self.logger.error("Download failed: %s", exc)
            self._take_screenshot("download_error")
            return None

    def run(self) -> BillRecord:
        """
        Full run: login → billing → find → download → return record.
        Augments the base record with electricity-specific field extraction.
        """
        record = super().run()

        # If download succeeded, attempt live field extraction from the page
        # (extraction layer will also parse the PDF separately)
        if record.bill_file_path and self._page:
            try:
                record.billing_period = self._page.locator(
                    f"{SELECTORS['bill_row']} {SELECTORS['bill_period']}"
                ).inner_text(timeout=3_000).strip()

                raw_amount = self._page.locator(
                    f"{SELECTORS['bill_row']} {SELECTORS['bill_amount']}"
                ).inner_text(timeout=3_000).strip()

                raw_due = self._page.locator(
                    f"{SELECTORS['bill_row']} {SELECTORS['bill_due_date']}"
                ).inner_text(timeout=3_000).strip()

                raw_usage = self._page.locator(
                    f"{SELECTORS['bill_row']} {SELECTORS['bill_usage']}"
                ).inner_text(timeout=3_000).strip()

                from utils.validation_utils import validate_amount
                from utils.date_utils import parse_date

                record.amount_due = validate_amount(raw_amount)
                record.due_date = parse_date(raw_due) or raw_due
                record.usage = raw_usage
                record.currency = "USD"

            except Exception as exc:
                self.logger.debug("Live field extraction skipped: %s", exc)

        return record


def create_provider() -> ElectricityProvider:
    """Factory function — returns a configured ElectricityProvider instance."""
    return ElectricityProvider(config=PROVIDERS["electricity"])
