"""
Base scraper class for state DOI rate comparison tools.

Each state implements a subclass that handles the specific DOI tool's
form fields, navigation, and result extraction.
"""

from __future__ import annotations

import json
import time
from abc import ABC, abstractmethod
from pathlib import Path

from scrapers.models import (
    DriverProfile,
    RateResult,
    FactorReport,
    FACTOR_PROFILES,
)

try:
    from playwright.sync_api import sync_playwright, Page, Browser
except ImportError:
    raise ImportError(
        "Playwright is required. Install it with:\n"
        "  pip install playwright && python -m playwright install chromium"
    )


# Minimum delay between queries (seconds). Be respectful to .gov servers.
REQUEST_DELAY = 2.0

# Browser user agent
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)


class BaseScraper(ABC):
    """
    Base class for state DOI scrapers.

    Subclasses must implement:
        - state_code: str property
        - source_name: str property
        - source_url: str property
        - _query_rates(page, profile, county, zip_code) -> RateResult
    """

    @property
    @abstractmethod
    def state_code(self) -> str:
        """Two-letter state code (e.g., 'TX')."""
        ...

    @property
    @abstractmethod
    def source_name(self) -> str:
        """Human-readable name of the DOI tool (e.g., 'Texas HelpInsure')."""
        ...

    @property
    @abstractmethod
    def source_url(self) -> str:
        """Base URL of the DOI tool."""
        ...

    @abstractmethod
    def _query_rates(
        self, page: Page, profile: DriverProfile, county: str, zip_code: str
    ) -> RateResult:
        """
        Query the DOI tool with a specific profile and return carrier rates.

        This is the core method each state scraper implements. It should:
        1. Navigate to the rate comparison form
        2. Fill in the form fields based on the profile
        3. Submit and wait for results
        4. Extract carrier names and annual rates
        5. Return a RateResult
        """
        ...

    def scrape_profile(
        self, county: str, zip_code: str, profile: DriverProfile
    ) -> RateResult:
        """Scrape rates for a single profile. Opens and closes browser."""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(user_agent=USER_AGENT)
            page = context.new_page()

            try:
                result = self._query_rates(page, profile, county, zip_code)
            finally:
                browser.close()

        return result

    def scrape_all_profiles(
        self,
        county: str,
        zip_code: str,
        profiles: dict[str, DriverProfile] | None = None,
    ) -> dict[str, RateResult]:
        """
        Scrape rates for all factor-isolation profiles.

        Uses a single browser session for efficiency, with respectful
        delays between queries.

        Returns dict mapping profile name to RateResult.
        """
        if profiles is None:
            profiles = FACTOR_PROFILES

        results = {}

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(user_agent=USER_AGENT)
            page = context.new_page()

            for name, profile in profiles.items():
                print(f"  [{self.state_code}] Querying {name}: {profile.description}")

                try:
                    result = self._query_rates(page, profile, county, zip_code)
                    results[name] = result
                    print(f"    Got {result.carrier_count} carriers")
                except Exception as e:
                    print(f"    ERROR: {e}")

                time.sleep(REQUEST_DELAY)

            browser.close()

        return results

    def compute_factors(
        self, county: str, zip_code: str
    ) -> FactorReport:
        """
        Run all profiles and compute factor multipliers vs baseline.

        This is the main entry point for factor analysis.
        """
        results = self.scrape_all_profiles(county, zip_code)

        if "baseline" not in results:
            raise RuntimeError("Baseline query failed; cannot compute factors")

        baseline = results.pop("baseline")
        return FactorReport.compute(baseline, results)

    def save_results(
        self, results: dict[str, RateResult], output_dir: str = "data"
    ) -> Path:
        """Save scrape results to a JSON file."""
        out = Path(output_dir) / self.state_code.lower()
        out.mkdir(parents=True, exist_ok=True)

        # Use first result for location info
        first = next(iter(results.values()))
        filename = f"{first.county.lower()}_{first.zip_code}.json"
        filepath = out / filename

        data = {name: r.to_dict() for name, r in results.items()}
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        print(f"Saved to {filepath}")
        return filepath
