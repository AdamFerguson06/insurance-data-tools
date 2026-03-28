# Auto Insurance Data Tools

Open-source tools for collecting and analyzing auto insurance rate data directly from state Department of Insurance websites.

**Live site:** [adamferguson06.github.io/insurance-data-tools](https://adamferguson06.github.io/insurance-data-tools)

## What This Is

Most auto insurance rate data published online comes from a single commercial data vendor, relicensed by dozens of publisher sites. These tools go directly to the source: state DOIs, which publish rate comparison data derived from regulatory filings.

Every data point is sourced from .gov websites (Tier 1 sources).

## Quick Start

```bash
# Clone and install
git clone https://github.com/AdamFerguson06/insurance-data-tools.git
cd insurance-data-tools
pip install -r requirements.txt
python -m playwright install chromium

# Scrape Texas DOI rates (baseline profile)
python scrape.py --state TX --county Dallas --zip 75007

# Run all profiles and compute factor multipliers
python scrape.py --state TX --county Dallas --zip 75007 --factors

# Save results to JSON
python scrape.py --state TX --county Dallas --zip 75007 --factors --output data/
```

## Tools

### State DOI Rate Scraper

Python scrapers that query state DOI rate comparison tools with standardized driver profiles. Each scraper automates the state's official tool using Playwright.

**Supported states:**

| State | DOI Tool | Method |
|-------|----------|--------|
| TX | [HelpInsure](https://www.helpinsure.com) | Interactive SPA (Playwright) |
| AL | [Compare Premiums](https://www.aldoi.gov/ConsumerServices/ComparePremiums.aspx) | ASP.NET form (Playwright) |
| AZ | [ADOI Rate Comparison](https://difi.az.gov/insurance/consumers/auto-insurance-comparison) | PDF download + parsing |

**Usage as a library:**

```python
from scrapers.texas import TexasScraper

scraper = TexasScraper()

# Single profile
result = scraper.scrape_profile(county="Dallas", zip_code="75007", profile=BASELINE)
for carrier in result.carriers:
    print(f"{carrier.carrier}: ${carrier.annual_rate}/yr")

# Factor analysis (all profiles)
report = scraper.compute_factors(county="Dallas", zip_code="75007")
report.print_summary()
```

### Factor Isolation Methodology

To measure how individual factors affect rates, we query each DOI tool with profiles that vary exactly one factor from a baseline:

| Profile | What Changes | Everything Else |
|---------|-------------|----------------|
| baseline | nothing | age 25-64, good credit, clean record |
| age_young | age 16-24 | good credit, clean record |
| age_senior | age 65+ | good credit, clean record |
| credit_poor | poor credit | age 25-64, clean record |
| credit_average | average credit | age 25-64, clean record |
| accident | at-fault accident | age 25-64, good credit |
| violation | speeding ticket | age 25-64, good credit |

The multiplier for each factor is the median ratio of variant rates to baseline rates across all carriers that appear in both queries.

See [examples/tx_dallas_75007.json](examples/tx_dallas_75007.json) for sample output.

### Source Integrity Checker

A git pre-commit hook that blocks commits where source citations change without corresponding data value changes. This prevents the error of swapping attribution (citing Source B) while keeping Source A's numbers.

```bash
# Install the hook
./hooks/install.sh

# Or copy manually
cp hooks/source-integrity-check.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

Configure the file paths by setting environment variables:

```bash
export SOURCES_FILE="src/data/sources.ts"
export DATA_FILE="src/data/rates.ts"
```

## Adding a New State

Each state DOI has a different tool (interactive form, PDF, API). To add a state:

1. Create `scrapers/{state}.py` with a class that extends `BaseScraper`
2. Implement `_query_rates()` to handle that state's specific tool
3. Add the scraper to `SCRAPERS` dict in `scrape.py`
4. Test with `python scrape.py --state XX --county ... --zip ...`

See `scrapers/texas.py` for a complete example (interactive SPA) or `scrapers/arizona.py` for PDF parsing.

## Project Structure

```
├── scrape.py              # CLI entry point
├── scrapers/
│   ├── models.py          # DriverProfile, RateResult, FactorReport
│   ├── base.py            # BaseScraper abstract class
│   ├── texas.py           # TX HelpInsure scraper
│   ├── alabama.py         # AL Compare Premiums scraper
│   └── arizona.py         # AZ PDF parser
├── hooks/
│   ├── source-integrity-check.sh  # Pre-commit hook
│   └── install.sh         # Hook installer
├── examples/              # Sample output data
├── index.html             # GitHub Pages site
└── pyproject.toml         # Python package config
```

## Requirements

- Python 3.9+
- Playwright (for browser automation)
- pdfplumber (optional, for PDF-based states like AZ)

## Built By

[QuoteFii](https://blog.quotefii.com?utm_source=github&utm_medium=readme&utm_content=insurance-data-tools) builds auto insurance data analysis using .gov sources. See our [data tables](https://blog.quotefii.com/data?utm_source=github&utm_medium=readme&utm_content=insurance-data-tools) and [rate guides](https://blog.quotefii.com/guides?utm_source=github&utm_medium=readme&utm_content=insurance-data-tools).

## License

MIT
