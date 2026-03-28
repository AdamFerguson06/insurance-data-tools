"""
Alabama Department of Insurance rate scraper.

Scrapes the ALDOI Compare Premiums tool for auto insurance rate data.

Source: Alabama Department of Insurance
URL: https://www.aldoi.gov/ConsumerServices/ComparePremiums.aspx
Tier: 1 (.gov)

Status: Implemented, tested with Shelby County profiles.

Usage:
    from scrapers.alabama import AlabamaScraper

    scraper = AlabamaScraper()
    report = scraper.compute_factors(county="Shelby", zip_code="35242")
    report.print_summary()
"""

from __future__ import annotations

import re
import time

from playwright.sync_api import Page

from scrapers.base import BaseScraper
from scrapers.models import DriverProfile, RateResult, CarrierRate


class AlabamaScraper(BaseScraper):
    """Scraper for Alabama DOI Compare Premiums tool."""

    @property
    def state_code(self) -> str:
        return "AL"

    @property
    def source_name(self) -> str:
        return "Alabama Department of Insurance (Compare Premiums)"

    @property
    def source_url(self) -> str:
        return "https://www.aldoi.gov/ConsumerServices/ComparePremiums.aspx"

    def _query_rates(
        self, page: Page, profile: DriverProfile, county: str, zip_code: str
    ) -> RateResult:
        """
        Query the ALDOI Compare Premiums tool.

        The AL tool uses ASP.NET postbacks with ViewState, so we must
        interact with the form sequentially (each dropdown triggers a
        partial postback that populates the next).
        """
        page.goto(self.source_url)
        page.wait_for_load_state("networkidle")
        time.sleep(2)

        # Select county (triggers postback to populate ZIP dropdown)
        county_select = page.locator("#ContentPlaceHolder1_ddlCounty")
        county_select.select_option(label=county)
        page.wait_for_load_state("networkidle")
        time.sleep(1)

        # Select ZIP code
        zip_select = page.locator("#ContentPlaceHolder1_ddlZipCode")
        zip_select.select_option(label=zip_code)
        time.sleep(0.5)

        # Age group
        age_map = {
            "16-24": "16-24",
            "25-64": "25-64",
            "65+": "65+",
        }
        age_select = page.locator("#ContentPlaceHolder1_ddlAge")
        age_select.select_option(label=age_map.get(profile.age_group, "25-64"))
        time.sleep(0.5)

        # Driving record
        record_select = page.locator("#ContentPlaceHolder1_ddlRecord")
        if profile.has_accident:
            record_select.select_option(label="At-Fault Accident")
        elif profile.has_violation:
            record_select.select_option(label="Minor Violation")
        else:
            record_select.select_option(label="Clean")
        time.sleep(0.5)

        # Submit
        page.locator("#ContentPlaceHolder1_btnSubmit").click()
        page.wait_for_load_state("networkidle")
        time.sleep(2)

        # Extract results from the comparison table
        carriers = self._parse_results(page)

        return RateResult(
            state="AL",
            county=county,
            zip_code=zip_code,
            profile=profile,
            carriers=carriers,
            source_url=self.source_url,
            source_name=self.source_name,
        )

    def _parse_results(self, page: Page) -> list[CarrierRate]:
        """Extract carrier rates from the ALDOI results table."""
        results = []

        # The results appear in a GridView table
        rows = page.locator("#ContentPlaceHolder1_gvResults tr").all()

        for row in rows[1:]:  # Skip header row
            cells = row.locator("td").all()
            if len(cells) >= 2:
                carrier = cells[0].inner_text().strip()
                rate_text = cells[1].inner_text().strip()

                rate_match = re.search(r"\$?([0-9,]+)", rate_text)
                if rate_match and carrier:
                    annual_rate = int(rate_match.group(1).replace(",", ""))
                    results.append(CarrierRate(
                        carrier=carrier,
                        annual_rate=annual_rate,
                    ))

        return results
