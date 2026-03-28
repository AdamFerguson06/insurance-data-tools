"""
Texas Department of Insurance rate scraper.

Scrapes HelpInsure (helpinsure.com), the official TDI rate comparison
tool. Queries the SPA form directly for reliable automation.

Source: Texas Department of Insurance
URL: https://www.helpinsure.com
Tier: 1 (.gov partner site)

Usage:
    from scrapers.texas import TexasScraper

    scraper = TexasScraper()
    report = scraper.compute_factors(county="Dallas", zip_code="75007")
    report.print_summary()
"""

from __future__ import annotations

import re
import time

from playwright.sync_api import Page

from scrapers.base import BaseScraper
from scrapers.models import DriverProfile, RateResult, CarrierRate


# Map standardized profile fields to HelpInsure form labels
AGE_MAP = {
    "16-24": "16 to 24",
    "25-64": "25 to 64",
    "65+": "65 and older",
}

CREDIT_MAP = {
    "poor": "Poor",
    "average": "Average",
    "good": "Good",
    "excellent": "Good",  # HelpInsure only has 3 tiers
}


class TexasScraper(BaseScraper):
    """Scraper for Texas HelpInsure rate comparison tool."""

    @property
    def state_code(self) -> str:
        return "TX"

    @property
    def source_name(self) -> str:
        return "Texas Department of Insurance (HelpInsure)"

    @property
    def source_url(self) -> str:
        return "https://www.helpinsure.com"

    def _query_rates(
        self, page: Page, profile: DriverProfile, county: str, zip_code: str
    ) -> RateResult:
        """Query HelpInsure with a driver profile and extract carrier rates."""

        # Navigate to the SPA form (bypass iframe wrapper)
        page.goto("https://www.helpinsure.com/app/auto/form")
        page.wait_for_load_state("networkidle")
        time.sleep(2)

        # County: Choices.js dropdown
        county_dropdown = page.locator(".choices").first
        county_dropdown.click()
        time.sleep(0.5)
        page.locator(".choices__input--cloned").fill(county)
        time.sleep(1)
        page.get_by_role("option", name=county, exact=True).click()
        time.sleep(0.5)

        # ZIP code
        page.get_by_label("ZIP code").select_option(zip_code)
        time.sleep(0.3)

        # Gender (constant: male)
        page.locator('label:has-text("Male")').first.click()

        # Marital status (constant: married)
        page.locator('label:has-text("Married")').first.click()

        # Age (variable)
        age_label = AGE_MAP.get(profile.age_group, "25 to 64")
        page.locator(f'label:has-text("{age_label}")').click()

        # Credit (variable)
        credit_label = CREDIT_MAP.get(profile.credit_tier, "Good")
        credit_group = page.locator("fieldset").filter(has_text="credit score")
        credit_group.locator(f'label:has-text("{credit_label}")').click()

        # Vehicle type (constant: car)
        vehicle_group = page.locator("fieldset").filter(has_text="Vehicle type")
        vehicle_group.locator('label:has-text("Car")').click()

        # Vehicle usage (constant: commute)
        page.locator('label:has-text("Mostly for going to work")').click()

        # Accident (variable)
        accident_label = "Yes" if profile.has_accident else "No"
        accident_group = page.locator("fieldset").filter(has_text="caused an accident")
        accident_group.locator(f'label:has-text("{accident_label}")').click()

        # Speeding ticket (variable, may not appear)
        time.sleep(0.5)
        ticket_group = page.locator("fieldset").filter(has_text="speeding ticket")
        if ticket_group.count() > 0:
            ticket_label = "Yes" if profile.has_violation else "No"
            ticket_group.locator(f'label:has-text("{ticket_label}")').click()

        # Coverage: minimum (first option)
        page.locator('label[for="coverage_limit_1"]').click()

        # Submit
        page.get_by_role("button", name="View rates").click()
        page.wait_for_url("**/results/**", timeout=15000)
        time.sleep(2)

        # Extract carrier names and rates from results page
        carriers = self._parse_results(page)

        return RateResult(
            state="TX",
            county=county,
            zip_code=zip_code,
            profile=profile,
            carriers=carriers,
            source_url="https://www.helpinsure.com",
            source_name="Texas Department of Insurance (HelpInsure)",
        )

    def _parse_results(self, page: Page) -> list[CarrierRate]:
        """Extract carrier names and annual rates from the HelpInsure results page."""
        body_text = page.evaluate("() => document.body.innerText")
        results = []
        current_carrier = None

        # Lines we know are NOT carrier names
        skip_prefixes = (
            "$", "Tooltip", "Estimated", "Annual", "To get", "View",
            "Complaints", "Compared", "Fewer", "More", "Complaint",
            "AM Best", "Financial", "Select", "No data", "Policy type",
            "Sort", "Sample", "Your search", "Search", "How do", "Choose",
            "Compare", "0 of", "Skip", "HelpInsure", "Brought", "Looking",
            "Visit", "Toggle", "Home", "Auto insurance", "Policy search",
            "Download",
        )

        for line in body_text.split("\n"):
            line = line.strip()

            # Rate line: contains "a year" and a dollar amount
            if "a year" in line and "$" in line:
                rate_match = re.search(r"\$([0-9,]+)", line)
                if rate_match and current_carrier:
                    annual_rate = int(rate_match.group(1).replace(",", ""))
                    results.append(CarrierRate(
                        carrier=current_carrier,
                        annual_rate=annual_rate,
                    ))
                    current_carrier = None
                continue

            # Candidate carrier name: text line that isn't a known UI element
            if (
                line
                and not any(line.startswith(p) for p in skip_prefixes)
                and "a year" not in line
                and 3 < len(line) < 80
                and any(c.isalpha() for c in line)
            ):
                current_carrier = line

        return results
