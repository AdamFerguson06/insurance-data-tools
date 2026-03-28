---
status: planned
pr: null
completed: null
---
# PRD: Rate Claim Fact-Checker (Chrome Extension)

## Introduction

A Chrome extension that highlights dollar amounts on insurance content pages and lets users compare them against QuoteFii's .gov-sourced research. When a user clicks a highlighted figure, a popup shows what QuoteFii's data suggests, with full source links and clear disclaimers that figures are estimates for informational purposes only.

This is the most differentiated of three planned extensions and the most on-brand for QuoteFii's ".gov data" positioning. It is also the highest legal risk, so disclaimers and framing are critical. QuoteFii is not a licensed insurance provider. We do not claim our figures are "correct" or that other sources are "wrong." We present our research alongside the page's claim and let the user decide.

The Chrome Web Store listing provides a DR 99 dofollow backlink.

## Legal Framework (CRITICAL)

This extension compares third-party claims against QuoteFii's estimates. The legal risk is implying that QuoteFii's figures are authoritative or that the page's figures are wrong. To mitigate:

### Language Rules

**Never use:**
- "This site is wrong"
- "The correct figure is..."
- "This is inaccurate"
- "You should expect to pay..."
- "The real cost is..."
- "This is misleading"

**Always use:**
- "QuoteFii's research suggests a different estimate"
- "Based on our analysis of government data, the average may differ"
- "Our sources show a different figure"
- "See how this compares to government data"

### Required Disclaimers

Every comparison popup MUST include:

1. **Context line**: "This page shows [their figure]. QuoteFii's research, based on [source names], estimates [our figure]."
2. **Methodology link**: "See our sources and methodology" (links to blog.quotefii.com/data)
3. **Disclaimer**: "QuoteFii is not a licensed insurance provider. All figures are estimates for informational purposes only. Actual rates vary by carrier, coverage, location, driving history, and other factors. Differences between sources may reflect different methodologies, coverage levels, or time periods. Always consult a qualified insurance provider for personalized quotes."
4. **No judgment**: The popup presents both numbers side by side without declaring either right or wrong.

## Goals

- Help consumers see how insurance cost claims compare to government-sourced data
- Present comparisons neutrally without implying either source is right or wrong
- Maintain full legal compliance with clear disclaimers and source attribution
- Drive traffic to blog.quotefii.com methodology and data pages
- Secure DR 99 dofollow backlink from Chrome Web Store listing

## User Stories

### US-001: Highlight cost claims on insurance pages
**Description:** As a consumer reading insurance content, I want dollar amounts highlighted so I can quickly check them against independent data.

**Acceptance Criteria:**
- [ ] On insurance-related sites (URL pattern matching), extension scans for dollar amounts in text (e.g., "$1,500", "$200/month", "$2,400 per year")
- [ ] Recognized cost patterns are underlined with a subtle QuoteFii-branded indicator (small icon or colored underline)
- [ ] Only highlights figures that plausibly relate to insurance costs (filter out prices for products, phone numbers, etc. by context: look for nearby keywords like "premium", "rate", "cost", "average", "per month", "per year", "annually")
- [ ] Does not highlight amounts inside forms, inputs, or interactive elements
- [ ] Can be toggled on/off via extension icon
- [ ] Verified visually in browser on at least 3 insurance content sites

### US-002: Comparison popup
**Description:** As a consumer, I want to click a highlighted figure and see how it compares to QuoteFii's research, with full context about both numbers.

**Acceptance Criteria:**
- [ ] Clicking a highlighted figure opens a popup showing:
  - The page's figure: "This page says: $X/[period]"
  - QuoteFii's estimate: "QuoteFii's research estimates: $Y/[period]"
  - Difference: shown as dollar amount and percentage, labeled "Difference" (not "savings" or "error")
  - Source attribution: "Based on [NAIC + BLS CPI / specific source]"
  - "See our methodology" link to blog.quotefii.com/data (UTM params)
- [ ] Full disclaimer visible in popup (see Legal Framework)
- [ ] If QuoteFii has no comparable data for the specific claim, popup says: "We don't have a direct comparison for this figure. Browse our data." with link
- [ ] Popup dismisses on click outside or Escape
- [ ] Verified visually in browser

### US-003: Matching logic
**Description:** As a developer, the extension needs to intelligently match page claims to the right QuoteFii data point so comparisons are meaningful.

**Acceptance Criteria:**
- [ ] Extension attempts to determine context of each dollar amount: is it monthly or annual? Full coverage or minimum? State-specific or national?
- [ ] Context detection uses nearby text keywords (e.g., "per month", "annual", "full coverage", "minimum", state names)
- [ ] If context is ambiguous, popup shows: "We're not sure what this figure represents. Here's QuoteFii's national average for reference." with caveats
- [ ] Never compares a monthly figure to an annual figure or full coverage to minimum coverage without conversion and labeling
- [ ] Matching logic documented in code comments for maintainability

### US-004: Chrome Web Store listing
**Description:** As an SEO, I want the store listing to include backlinks and proper legal framing.

**Acceptance Criteria:**
- [ ] Store description includes links to blog.quotefii.com and quotefii.com
- [ ] Description prominently states: "For informational purposes only. QuoteFii is not a licensed insurance provider."
- [ ] Description frames the extension as "see how claims compare to government data" (not "find errors" or "fact-check")
- [ ] Privacy: extension reads page content to find dollar amounts, collects no personal data

## Functional Requirements

- FR-1: Detect insurance-related pages by URL pattern matching (same list as Jargon Decoder, shared across extensions)
- FR-2: Scan visible DOM text for dollar amount patterns using regex: `\$[\d,]+(?:\.\d{2})?(?:\s*(?:\/|per)\s*(?:mo(?:nth)?|yr|year|annually))?`
- FR-3: Filter dollar amounts by proximity to insurance-related keywords within the same paragraph or sentence
- FR-4: Match detected figures against bundled QuoteFii data (national average, state averages, coverage type breakdowns)
- FR-5: Display comparison popup with both figures, difference, sources, and full legal disclaimer
- FR-6: All outbound links use UTM params: utm_source=chrome_extension, utm_medium=popup, utm_content=rate-factchecker
- FR-7: Toggle highlighting on/off via extension icon click, persisted in chrome.storage.sync
- FR-8: No external network requests. All data bundled. No analytics.
- FR-9: Manifest V3

## Non-Goals

- No claim that QuoteFii's data is "correct" or that the page's data is "wrong"
- No automated reporting or scoring of pages ("this page has 3 inaccurate claims")
- No carrier-specific rate comparisons
- No personalized rate estimates
- No social sharing ("share this fact-check")
- No browser notifications or alerts about cost claims
- No modification of page content beyond subtle highlighting

## Technical Considerations

- **Data bundle**: Same static JSON as the Cost Checker (national avg, state avgs, coverage type breakdowns), with source names and last-updated dates
- **Context detection**: Use proximity search (scan +-100 characters around the dollar amount for keywords like "monthly", "annual", "full coverage", "minimum", state names). This is heuristic, not perfect; when unsure, say so in the popup.
- **Period normalization**: If page says "$200/month" and QuoteFii data is annual, convert before comparing. Always show both periods in the popup.
- **False positive handling**: Better to skip a figure than to show a misleading comparison. When in doubt, don't highlight.
- **Repo**: Separate repo (e.g., AdamFerguson06/quotefii-rate-checker)
- **No build step**: Plain HTML/CSS/JS

## Success Metrics

- Chrome Web Store listing live with dofollow backlinks
- Zero legal complaints or cease-and-desist letters (most critical metric)
- Click-through rate on methodology link > 3%
- Store rating >= 4.0 stars
- No Chrome Web Store policy violations

## Open Questions

- Should we name this "Rate Comparison Tool" instead of "Fact-Checker"? "Fact-checker" implies judgment and could attract legal scrutiny. "Comparison tool" is more neutral. (Recommendation: use "Insurance Rate Comparison" or "Insurance Data Companion" in the store listing, avoid "fact-checker" entirely in public-facing copy)
- How aggressively should we highlight? Conservative (only amounts with clear "per month/year" context) vs. liberal (any dollar amount on an insurance page). (Recommendation: conservative, with a "Check this figure" right-click option for anything we didn't auto-detect)
- Should the popup show a visual (bar chart comparing the two figures) or just text? (Recommendation: text only in v1; a bar chart could imply one figure is "better" than the other)
