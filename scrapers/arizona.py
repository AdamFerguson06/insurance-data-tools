"""
Arizona Department of Insurance rate scraper.

The ADOI publishes rate comparison data as downloadable PDF reports
rather than an interactive tool. This scraper downloads and parses
the PDF to extract carrier rates.

Source: Arizona Department of Insurance and Financial Institutions
URL: https://difi.az.gov/insurance/consumers/auto-insurance-comparison
Tier: 1 (.gov)

Status: Implemented. Uses pdfplumber for table extraction from
        the published rate comparison PDF.

Usage:
    from scrapers.arizona import ArizonaScraper

    scraper = ArizonaScraper()
    result = scraper.scrape_from_pdf("path/to/az_rate_comparison.pdf")
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

from scrapers.models import DriverProfile, RateResult, CarrierRate, BASELINE


class ArizonaScraper:
    """
    Parser for Arizona DOI rate comparison PDFs.

    Unlike TX and AL, Arizona publishes static PDF reports rather than
    an interactive tool. This scraper extracts rate tables from those PDFs.
    """

    @property
    def state_code(self) -> str:
        return "AZ"

    @property
    def source_name(self) -> str:
        return "Arizona Dept. of Insurance and Financial Institutions"

    @property
    def source_url(self) -> str:
        return "https://difi.az.gov/insurance/consumers/auto-insurance-comparison"

    def scrape_from_pdf(
        self,
        pdf_path: str,
        county: Optional[str] = None,
        zip_code: Optional[str] = None,
    ) -> RateResult:
        """
        Extract carrier rates from an AZ DOI rate comparison PDF.

        Args:
            pdf_path: Path to the downloaded PDF
            county: County name (extracted from PDF if not provided)
            zip_code: ZIP code (extracted from PDF if not provided)

        Returns:
            RateResult with extracted carrier rates
        """
        if pdfplumber is None:
            raise ImportError(
                "pdfplumber is required for PDF parsing. "
                "Install it with: pip install pdfplumber"
            )

        carriers = []

        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    carriers.extend(self._parse_table(table))

                # Try to extract location from page text if not provided
                if not county or not zip_code:
                    text = page.extract_text() or ""
                    if not county:
                        county_match = re.search(r"County:\s*(\w+)", text)
                        if county_match:
                            county = county_match.group(1)
                    if not zip_code:
                        zip_match = re.search(r"ZIP:\s*(\d{5})", text)
                        if zip_match:
                            zip_code = zip_match.group(1)

        return RateResult(
            state="AZ",
            county=county or "Unknown",
            zip_code=zip_code or "00000",
            profile=BASELINE,
            carriers=carriers,
            source_url=self.source_url,
            source_name=self.source_name,
        )

    def _parse_table(self, table: list[list[str]]) -> list[CarrierRate]:
        """Parse a rate table from the PDF into CarrierRate objects."""
        results = []
        if not table or len(table) < 2:
            return results

        # Find column indices for carrier name and premium
        header = [str(cell).lower().strip() for cell in table[0] if cell]

        name_col = None
        rate_col = None
        for i, h in enumerate(header):
            if "company" in h or "carrier" in h or "insurer" in h:
                name_col = i
            elif "premium" in h or "rate" in h or "annual" in h:
                rate_col = i

        if name_col is None or rate_col is None:
            return results

        for row in table[1:]:
            if not row or len(row) <= max(name_col, rate_col):
                continue

            carrier = str(row[name_col] or "").strip()
            rate_text = str(row[rate_col] or "").strip()

            if not carrier or not rate_text:
                continue

            rate_match = re.search(r"\$?([0-9,]+(?:\.\d{2})?)", rate_text)
            if rate_match:
                rate_str = rate_match.group(1).replace(",", "")
                annual_rate = int(float(rate_str))
                if annual_rate > 0:
                    results.append(CarrierRate(
                        carrier=carrier,
                        annual_rate=annual_rate,
                    ))

        return results
