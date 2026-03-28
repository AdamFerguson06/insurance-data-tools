---
status: planned
pr: null
completed: null
---
# PRD: Insurance Cost Checker (Chrome Extension)

## Introduction

A Chrome extension that provides a quick-reference toolbar popup showing average auto insurance costs by state and age group, powered by QuoteFii's .gov-sourced data. Users pick their state and age to see benchmark figures, with prominent CTAs linking to the full calculator and data tables on blog.quotefii.com.

All data is presented with clear disclaimers that figures are estimates for informational purposes only, sourced from government data with linked methodology. QuoteFii is not a licensed insurance provider.

This is the second-priority extension of three planned. The Chrome Web Store listing provides a DR 99 dofollow backlink.

## Legal Framework (CRITICAL)

Every screen that displays cost data MUST include:

1. **Inline disclaimer** (visible without scrolling): "Estimates based on publicly available government data. For informational purposes only."
2. **Methodology link**: "See our sources and methodology" linking to blog.quotefii.com/data (UTM params)
3. **Footer disclaimer** (present on every popup view): "QuoteFii is not a licensed insurance provider or agent. These figures are estimates that may not reflect your actual costs. Rates vary by carrier, coverage level, driving history, and other factors. Always speak with a qualified insurance provider for personalized quotes."
4. **No language that implies guarantees**: Never use "you will pay", "your rate is", "you should expect". Always use "the average may be", "estimates suggest", "based on our research".

## Goals

- Let users quickly check average auto insurance costs for their state and age group
- Present data transparently with full source attribution and legal disclaimers
- Drive traffic to blog.quotefii.com calculator and data pages
- Secure DR 99 dofollow backlink from Chrome Web Store listing
- Zero backend, zero API keys; all data bundled in the extension

## User Stories

### US-001: State and age selector
**Description:** As a consumer, I want to pick my state and age group so I can see average insurance costs for someone like me.

**Acceptance Criteria:**
- [ ] Toolbar popup shows two dropdowns: State (50 states + DC) and Age Group (e.g., 16-24, 25-34, 35-44, 45-54, 55-64, 65+)
- [ ] Default: no state selected (prompt "Select your state")
- [ ] Selection persists across popup opens via chrome.storage.sync
- [ ] Verified visually in browser

### US-002: Cost display with disclaimers
**Description:** As a consumer, I want to see estimated average costs with clear context about where the numbers come from.

**Acceptance Criteria:**
- [ ] After selecting state and age, shows: estimated monthly and annual average
- [ ] Label reads "Estimated average" (never "Your rate" or "You will pay")
- [ ] Below the figure: "Based on [source names] data. See sources and methodology." with link to blog.quotefii.com/data (UTM params)
- [ ] Footer disclaimer always visible (see Legal Framework above)
- [ ] Verified visually in browser

### US-003: CTA to full tools
**Description:** As a user, I want to easily access QuoteFii's full calculator and data tables for deeper analysis.

**Acceptance Criteria:**
- [ ] Primary CTA button: "Check if you're overpaying" linking to blog.quotefii.com/tools/overpaying-calculator (UTM params)
- [ ] Secondary link: "View all state data" linking to blog.quotefii.com/data (UTM params)
- [ ] All links use utm_source=chrome_extension&utm_medium=popup&utm_content=cost-checker
- [ ] Verified visually in browser

### US-004: Chrome Web Store listing
**Description:** As an SEO, I want the store listing to include dofollow backlinks to QuoteFii.

**Acceptance Criteria:**
- [ ] Store description includes links to blog.quotefii.com and quotefii.com
- [ ] Description clearly states "informational purposes only" and "not a licensed insurance provider"
- [ ] Privacy policy: extension stores user's state/age preference locally, collects no personal data, makes no network requests

## Functional Requirements

- FR-1: Bundle state-level and age-group cost data as a static JSON file in the extension (sourced from blog's canonical data files at build time)
- FR-2: Display cost data with mandatory disclaimer text on every view
- FR-3: All cost figures labeled as "estimated averages" with source attribution
- FR-4: Methodology link points to blog.quotefii.com/data with UTM params
- FR-5: No external network requests. All data bundled. No analytics.
- FR-6: Manifest V3, toolbar popup only (no content script needed)
- FR-7: State/age selection stored in chrome.storage.sync

## Non-Goals

- No personalized quotes or rate calculations based on individual factors (credit, driving record, etc.)
- No carrier-specific rates or carrier names
- No rate comparison between states (that's what the blog data tables are for)
- No financial advice or recommendations
- No integration with insurance APIs or third-party data
- No content script or page modification

## Technical Considerations

- **Data source**: At extension build/update time, export the relevant subset from blog-quotefii-auto's `src/data/insurance-rates.ts` and `src/data/state-guides.ts` into a static JSON
- **Data freshness**: Bundle the "last updated" date in the JSON. Display it in the popup: "Data last updated: [Month Year]"
- **Update cadence**: Republish the extension when canonical data updates (monthly CPI, annual NAIC). This is manual but infrequent.
- **Repo**: Separate repo (e.g., AdamFerguson06/quotefii-cost-checker)
- **No build step**: Plain HTML/CSS/JS

## Success Metrics

- Chrome Web Store listing live with dofollow backlinks
- Backlink visible in Ahrefs within 30 days
- Click-through rate on CTA to calculator > 5%
- Zero legal complaints or Chrome Web Store policy violations
- Store rating >= 4.0 stars

## Open Questions

- What age group granularity to use? The blog has data by specific ages (25, 30, 40, 50, 60) from one source. May need to bucket into ranges for a simpler UX.
- Should we show the national average alongside the state average for comparison context? (Recommendation: yes, as a small "National avg: $X/mo" reference line)
