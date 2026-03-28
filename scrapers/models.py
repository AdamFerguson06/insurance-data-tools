"""
Data models for insurance rate scraping.

These models define the standardized schema for driver profiles,
rate results, and factor multiplier reports.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional
import json


@dataclass
class DriverProfile:
    """
    A standardized driver profile for querying DOI rate tools.

    To isolate rate factors, create profiles that vary exactly ONE field
    from a baseline. The ratio between variant and baseline rates gives
    the factor multiplier.
    """
    name: str
    description: str

    # Variable fields (change one at a time)
    age_group: str = "25-64"       # "16-24", "25-64", "65+"
    credit_tier: str = "good"      # "poor", "average", "good", "excellent"
    has_accident: bool = False     # at-fault accident in past 3 years
    has_violation: bool = False    # speeding ticket in past 3 years

    # Constant fields (same across all profiles)
    gender: str = "male"
    marital_status: str = "married"
    vehicle_type: str = "car"
    vehicle_usage: str = "commute"
    coverage_type: str = "minimum"  # "minimum" or "full"

    def to_dict(self) -> dict:
        return asdict(self)


# Standard profiles for factor isolation.
# Each varies exactly ONE field from baseline.
BASELINE = DriverProfile(
    name="baseline",
    description="Baseline: age 25-64, good credit, clean record",
)

FACTOR_PROFILES = {
    "baseline": BASELINE,
    "age_young": DriverProfile(
        name="age_young",
        description="Young driver: age 16-24",
        age_group="16-24",
    ),
    "age_senior": DriverProfile(
        name="age_senior",
        description="Senior driver: age 65+",
        age_group="65+",
    ),
    "credit_poor": DriverProfile(
        name="credit_poor",
        description="Poor credit score",
        credit_tier="poor",
    ),
    "credit_average": DriverProfile(
        name="credit_average",
        description="Average credit score",
        credit_tier="average",
    ),
    "accident": DriverProfile(
        name="accident",
        description="At-fault accident in past 3 years",
        has_accident=True,
    ),
    "violation": DriverProfile(
        name="violation",
        description="Speeding ticket in past 3 years",
        has_violation=True,
    ),
}


@dataclass
class CarrierRate:
    """A single carrier's rate from a DOI tool query."""
    carrier: str
    annual_rate: int
    monthly_rate: Optional[int] = None

    def __post_init__(self):
        if self.monthly_rate is None:
            self.monthly_rate = round(self.annual_rate / 12)


@dataclass
class RateResult:
    """
    Complete result from a single DOI tool query.
    Contains the profile used, location, and all carrier rates returned.
    """
    state: str
    county: str
    zip_code: str
    profile: DriverProfile
    carriers: list[CarrierRate] = field(default_factory=list)
    source_url: str = ""
    source_name: str = ""
    query_date: str = field(default_factory=lambda: datetime.now().isoformat())

    @property
    def carrier_count(self) -> int:
        return len(self.carriers)

    @property
    def median_rate(self) -> Optional[int]:
        if not self.carriers:
            return None
        rates = sorted(c.annual_rate for c in self.carriers)
        mid = len(rates) // 2
        if len(rates) % 2 == 0:
            return (rates[mid - 1] + rates[mid]) // 2
        return rates[mid]

    @property
    def mean_rate(self) -> Optional[int]:
        if not self.carriers:
            return None
        return round(sum(c.annual_rate for c in self.carriers) / len(self.carriers))

    def to_dict(self) -> dict:
        return {
            "state": self.state,
            "county": self.county,
            "zip_code": self.zip_code,
            "profile": self.profile.to_dict(),
            "source_url": self.source_url,
            "source_name": self.source_name,
            "query_date": self.query_date,
            "carrier_count": self.carrier_count,
            "median_rate": self.median_rate,
            "mean_rate": self.mean_rate,
            "carriers": [asdict(c) for c in self.carriers],
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)


@dataclass
class FactorMultiplier:
    """
    A single factor multiplier computed from variant vs baseline rates.
    """
    factor_name: str
    factor_description: str
    multiplier: float
    carriers_matched: int
    baseline_median: int
    variant_median: int


@dataclass
class FactorReport:
    """
    Complete factor analysis for a location, showing how each factor
    (age, credit, driving record) affects rates relative to baseline.
    """
    state: str
    county: str
    zip_code: str
    source_name: str
    source_url: str
    query_date: str
    baseline: RateResult
    factors: list[FactorMultiplier] = field(default_factory=list)

    @classmethod
    def compute(cls, baseline: RateResult, variants: dict[str, RateResult]) -> "FactorReport":
        """
        Compute factor multipliers by comparing each variant to the baseline.

        For each carrier that appears in both baseline and variant results,
        compute the ratio. The reported multiplier is the median across
        all matched carriers.
        """
        baseline_rates = {c.carrier: c.annual_rate for c in baseline.carriers}
        factors = []

        for name, variant in variants.items():
            ratios = []
            for carrier in variant.carriers:
                if carrier.carrier in baseline_rates:
                    base_rate = baseline_rates[carrier.carrier]
                    if base_rate > 0:
                        ratios.append(carrier.annual_rate / base_rate)

            if ratios:
                ratios.sort()
                mid = len(ratios) // 2
                if len(ratios) % 2 == 0:
                    median_ratio = (ratios[mid - 1] + ratios[mid]) / 2
                else:
                    median_ratio = ratios[mid]

                factors.append(FactorMultiplier(
                    factor_name=name,
                    factor_description=variant.profile.description,
                    multiplier=round(median_ratio, 2),
                    carriers_matched=len(ratios),
                    baseline_median=baseline.median_rate or 0,
                    variant_median=variant.median_rate or 0,
                ))

        return cls(
            state=baseline.state,
            county=baseline.county,
            zip_code=baseline.zip_code,
            source_name=baseline.source_name,
            source_url=baseline.source_url,
            query_date=baseline.query_date,
            baseline=baseline,
            factors=factors,
        )

    def to_dict(self) -> dict:
        return {
            "state": self.state,
            "county": self.county,
            "zip_code": self.zip_code,
            "source_name": self.source_name,
            "source_url": self.source_url,
            "query_date": self.query_date,
            "baseline_carrier_count": self.baseline.carrier_count,
            "baseline_median_rate": self.baseline.median_rate,
            "factors": [asdict(f) for f in self.factors],
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    def print_summary(self):
        print(f"\nFactor Analysis: {self.state} ({self.county} county, ZIP {self.zip_code})")
        print(f"Source: {self.source_name}")
        print(f"Baseline: {self.baseline.carrier_count} carriers, "
              f"median ${self.baseline.median_rate}/yr")
        print()
        print(f"{'Factor':<40} {'Multiplier':>10} {'Carriers':>10}")
        print("-" * 62)
        for f in self.factors:
            print(f"{f.factor_description:<40} {f.multiplier:>9.2f}x {f.carriers_matched:>9}")
