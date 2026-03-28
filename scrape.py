#!/usr/bin/env python3
"""
CLI entry point for the insurance rate scraper.

Usage:
    # Scrape Texas rates for a single baseline profile
    python scrape.py --state TX --county Dallas --zip 75007

    # Run all 7 profiles to compute factor multipliers
    python scrape.py --state TX --county Dallas --zip 75007 --factors

    # Alabama
    python scrape.py --state AL --county Shelby --zip 35242 --factors

    # Save results to JSON
    python scrape.py --state TX --county Dallas --zip 75007 --factors --output data/
"""

import argparse
import sys

from scrapers.models import FACTOR_PROFILES, BASELINE
from scrapers.texas import TexasScraper
from scrapers.alabama import AlabamaScraper


SCRAPERS = {
    "TX": TexasScraper,
    "AL": AlabamaScraper,
}


def main():
    parser = argparse.ArgumentParser(
        description="Scrape state DOI rate comparison tools for auto insurance data"
    )
    parser.add_argument(
        "--state", required=True, choices=list(SCRAPERS.keys()),
        help="State to scrape (e.g., TX, AL)"
    )
    parser.add_argument("--county", required=True, help="County name")
    parser.add_argument("--zip", required=True, help="ZIP code")
    parser.add_argument(
        "--factors", action="store_true",
        help="Run all profiles and compute factor multipliers"
    )
    parser.add_argument(
        "--output", default=None,
        help="Directory to save JSON results (default: print to stdout)"
    )

    args = parser.parse_args()

    scraper_cls = SCRAPERS.get(args.state)
    if not scraper_cls:
        print(f"No scraper implemented for {args.state}")
        print(f"Available: {', '.join(SCRAPERS.keys())}")
        sys.exit(1)

    scraper = scraper_cls()

    print(f"Scraping {scraper.source_name}")
    print(f"Location: {args.county} county, ZIP {args.zip}")
    print()

    if args.factors:
        report = scraper.compute_factors(args.county, args.zip)
        report.print_summary()

        if args.output:
            from pathlib import Path
            out_dir = Path(args.output) / args.state.lower()
            out_dir.mkdir(parents=True, exist_ok=True)
            filepath = out_dir / f"{args.county.lower()}_{args.zip}_factors.json"
            with open(filepath, "w") as f:
                f.write(report.to_json())
            print(f"\nSaved to {filepath}")
    else:
        result = scraper.scrape_profile(args.county, args.zip, BASELINE)
        print(f"Got {result.carrier_count} carriers (median: ${result.median_rate}/yr)")
        print()
        for c in sorted(result.carriers, key=lambda x: x.annual_rate):
            print(f"  {c.carrier:<40} ${c.annual_rate:>6}/yr  (${c.monthly_rate}/mo)")

        if args.output:
            results = {"baseline": result}
            scraper.save_results(results, args.output)


if __name__ == "__main__":
    main()
