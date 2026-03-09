"""
providers/base_provider.py
==========================
Abstract base class for all utility provider automations.

Every provider subclass must implement:
    - login()
    - navigate_to_billing()
    - find_latest_bill()
    - download_bill() -> Path

Shared logic for browser lifecycle, retries, and normalisation lives here.
When a provider changes its layout, only that provider's file needs editing.
"""

from __future__ import annotations

import logging
import tempfile
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from playwright.sync_api import Browser, BrowserContext, Page, Playwright, sync_playwright

from config import BROWSER_CONFIG, RETRY_CONFIG, ProviderConfig
from logging_config import get_provider_logger
from models.bill_record import BillRecord
from utils.file_utils import build_bill_path, get_latest_download, is_valid_pdf, move_downloaded_file
from utils.retry_utils import retry_on_exception
from utils.validation_utils import classify_extraction


class BaseProvider(ABC):
    """
    Abstract base for utility portal automation.

    Lifecycle per run:
        __init__ → open_browser → login → navigate_to_billing
        → find_latest_bill → download_bill → close_browser → BillRecord

    Subclasses override the abstract methods only.
    Shared plumbing (browser management, retries, record building) stays here.
    """

    def __init__(self, config: ProviderConfig) -> None:
        self.config = config
        self.logger: logging.Logger = get_provider_logger(config.name)

        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None
        self._download_dir: Optional[Path] = None

    # ------------------------------------------------------------------
    # Abstract interface — each provider implements these
    # ------------------------------------------------------------------

    @abstractmethod
    def login(self) -> None:
        """
        Perform portal login.
        Use self._page to interact with the browser.
        Raise an exception if login fails so the run is flagged.

        MAINTENANCE NOTE:
            When a provider updates its login page selectors, only this
            method in the provider's file needs updating.
        """

    @abstractmethod
    def navigate_to_billing(self) -> None:
        """
        Navigate from post-login landing page to the billing/statements section.

        MAINTENANCE NOTE:
            Update selectors/URLs here when billing navigation changes.
        """

    @abstractmethod
    def find_latest_bill(self) -> Optional[str]:
        """
        Locate the most recent bill on the billing page.
        Return a URL or identifier for the download step,
        or None if no bill is found.

        MAINTENANCE NOTE:
            Update row-selection logic or table selectors here.
        """

    @abstractmethod
    def download_bill(self) -> Optional[Path]:
        """
        Trigger the bill download and return the Path to the downloaded PDF.
        Return None if download fails.

        MAINTENANCE NOTE:
            Update download trigger selectors here.
        """

    # ------------------------------------------------------------------
    # Browser lifecycle (shared — do not override unless necessary)
    # ------------------------------------------------------------------

    def open_browser(self) -> None:
        """Launch Playwright browser and set up download directory."""
        self._download_dir = Path(tempfile.mkdtemp(prefix="ubill_"))
        self.logger.info("Opening browser (headless=%s)", BROWSER_CONFIG.headless)

        self._playwright = sync_playwright().start()
        self._browser = self._playwright.chromium.launch(
            headless=BROWSER_CONFIG.headless,
            slow_mo=BROWSER_CONFIG.slow_mo_ms,
        )
        self._context = self._browser.new_context(
            accept_downloads=True,
            viewport={"width": 1280, "height": 900},
        )
        self._page = self._context.new_page()
        self._page.set_default_timeout(BROWSER_CONFIG.timeout_ms)

    def close_browser(self) -> None:
        """Cleanly shut down browser resources."""
        try:
            if self._context:
                self._context.close()
            if self._browser:
                self._browser.close()
            if self._playwright:
                self._playwright.stop()
        except Exception as exc:
            self.logger.warning("Error during browser teardown: %s", exc)
        finally:
            self._page = None
            self._context = None
            self._browser = None
            self._playwright = None

    # ------------------------------------------------------------------
    # Main run entrypoint
    # ------------------------------------------------------------------

    def run(self) -> BillRecord:
        """
        Execute the full automation flow for this provider.
        Returns a BillRecord regardless of success/failure.
        One failed provider never breaks the overall pipeline.
        """
        record = BillRecord(
            provider_name=self.config.name,
            account_number=self.config.account_number,
        )

        try:
            self.open_browser()
            self._retry_login()
            self.navigate_to_billing()
            bill_ref = self.find_latest_bill()

            if not bill_ref:
                self.logger.warning("No bill found for %s", self.config.name)
                record.mark_failed("No bill found on billing page")
                return record

            raw_path = self.download_bill()
            if not raw_path or not is_valid_pdf(raw_path):
                record.mark_failed("Download failed or file is not a valid PDF")
                return record

            # Move to canonical storage location
            dest = build_bill_path(
                self.config.name,
                self.config.account_number,
                "pending",   # will be updated after extraction
            )
            move_downloaded_file(raw_path, dest)
            record.bill_file_path = str(dest)

            self.logger.info("Bill downloaded → %s", dest)

        except Exception as exc:
            self.logger.exception("Unhandled error during run for %s: %s", self.config.name, exc)
            record.mark_failed(str(exc))
        finally:
            self.close_browser()

        return record

    # ------------------------------------------------------------------
    # Retry wrapper for login
    # ------------------------------------------------------------------

    @retry_on_exception(exceptions=(Exception,), max_attempts=RETRY_CONFIG.max_retries)
    def _retry_login(self) -> None:
        self.login()

    # ------------------------------------------------------------------
    # Shared browser helpers available to all providers
    # ------------------------------------------------------------------

    def _goto(self, url: str) -> None:
        """Navigate to URL and wait for load."""
        assert self._page is not None
        self.logger.debug("Navigating to: %s", url)
        self._page.goto(url, wait_until="networkidle")

    def _fill(self, selector: str, value: str) -> None:
        """Clear and fill an input field."""
        assert self._page is not None
        self._page.locator(selector).fill(value)

    def _click(self, selector: str) -> None:
        """Click an element."""
        assert self._page is not None
        self._page.locator(selector).click()

    def _wait_for(self, selector: str, timeout: int = 10_000) -> None:
        """Wait for a selector to become visible."""
        assert self._page is not None
        self._page.locator(selector).wait_for(state="visible", timeout=timeout)

    def _take_screenshot(self, label: str = "debug") -> None:
        """Save a debug screenshot to the logs directory."""
        if self._page:
            from config import LOGS_DIR
            path = LOGS_DIR / f"{self.config.name.lower().replace(' ', '_')}_{label}.png"
            self._page.screenshot(path=str(path))
            self.logger.debug("Screenshot saved: %s", path)

    def _wait_for_download(self) -> Optional[Path]:
        """
        Trigger a download via context and return saved path.
        Usage: call within a `with self._page.expect_download() as dl:` block.
        This helper is illustrative; use Playwright's download API in subclasses.
        """
        assert self._download_dir is not None
        return get_latest_download(self._download_dir)
