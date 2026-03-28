"""
Auto insurance rate scrapers for state Department of Insurance websites.

Each scraper module targets a specific state's DOI rate comparison tool
and extracts carrier-specific rates for standardized driver profiles.
"""

from scrapers.models import DriverProfile, RateResult, FactorReport
from scrapers.base import BaseScraper

__all__ = ["DriverProfile", "RateResult", "FactorReport", "BaseScraper"]
