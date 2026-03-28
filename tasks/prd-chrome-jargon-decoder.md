---
status: planned
pr: null
completed: null
---
# PRD: Insurance Jargon Decoder (Chrome Extension)

## Introduction

A Chrome extension that helps consumers understand auto insurance terminology while browsing. On insurance-related sites, the extension automatically highlights recognized terms and shows plain-English definitions on hover/click. On all other sites, users can select any term and right-click to look it up. Every definition popup includes a link to QuoteFii, creating a natural funnel from the Chrome Web Store (DR 99 dofollow backlink) to the blog.

This is the highest-priority extension of three planned (see also: prd-chrome-cost-checker.md, prd-chrome-rate-factchecker.md) because it has the broadest appeal, the lowest legal risk (definitions are factual, not rate claims), and the highest organic install potential.

## Goals

- Provide clear, plain-English definitions for ~50 common auto insurance terms
- Auto-highlight terms on insurance-related websites for maximum discoverability
- Offer right-click context menu lookup on all other sites
- Drive traffic to blog.quotefii.com through natural, helpful CTA links in every popup
- Secure a DR 99 dofollow backlink from the Chrome Web Store listing page
- Zero backend, zero API keys, zero ongoing maintenance cost

## User Stories

### US-001: Auto-highlight on insurance sites
**Description:** As a consumer browsing an insurance website, I want insurance jargon automatically highlighted so I can quickly understand terms without leaving the page.

**Acceptance Criteria:**
- [ ] Extension detects insurance-related sites by URL pattern matching (e.g., domains containing "insurance", "geico", "progressive", "statefarm", "allstate", "usaa", known .gov DOI domains, etc.)
- [ ] On detected sites, recognized insurance terms in page text are underlined with a subtle dotted style (not disruptive to reading)
- [ ] Clicking or hovering on a highlighted term opens a definition popup
- [ ] Highlighting does not break page layout, forms, buttons, or interactive elements
- [ ] Highlighting skips text inside `<script>`, `<style>`, `<input>`, `<textarea>`, and `<select>` elements
- [ ] Performance: page scan completes in under 500ms on typical insurance pages
- [ ] Verified visually in browser on at least 3 insurance sites

### US-002: Right-click context menu on all sites
**Description:** As a user on any website, I want to select an insurance term and right-click to get its definition so I can look things up anywhere.

**Acceptance Criteria:**
- [ ] Context menu item "Define Insurance Term" appears when text is selected
- [ ] Clicking it opens the same definition popup used by auto-highlight
- [ ] If the selected text is not a recognized term, popup says "Term not found. Browse our insurance glossary." with a link to blog.quotefii.com/glossary
- [ ] Context menu item includes the QuoteFii icon
- [ ] Works on all sites (not just insurance sites)

### US-003: Definition popup design
**Description:** As a user, I want the definition popup to be clean, readable, and helpful so I can quickly understand a term and optionally learn more.

**Acceptance Criteria:**
- [ ] Popup shows: term name (bold), definition (2-3 sentences, plain English), and a "Learn more" link
- [ ] "Learn more" links to the most relevant blog.quotefii.com article with UTM params (utm_source=chrome_extension&utm_medium=popup&utm_content=jargon-decoder)
- [ ] Popup footer: small QuoteFii logo + "Compare auto insurance quotes" linking to quotefii.com with UTM params
- [ ] Popup is styled consistently with QuoteFii brand (#1B3A6D primary, Inter font)
- [ ] Popup dismisses on click outside or Escape key
- [ ] Popup positions intelligently (doesn't overflow viewport edges)
- [ ] Verified visually in browser

### US-004: Extension popup (toolbar icon)
**Description:** As a user, I want to click the extension icon in the toolbar to browse all terms so I can use it as a quick reference.

**Acceptance Criteria:**
- [ ] Toolbar popup shows a searchable A-Z glossary of all terms
- [ ] Search/filter box at top narrows the list as user types
- [ ] Clicking any term expands its definition inline
- [ ] Footer: "Powered by QuoteFii" with link to blog.quotefii.com (UTM params)
- [ ] Popup width: 360px, max height: 500px with scroll
- [ ] Verified visually in browser

### US-005: Settings and toggle
**Description:** As a user, I want to toggle auto-highlighting on/off so the extension doesn't interfere when I don't want it.

**Acceptance Criteria:**
- [ ] Toggle switch in toolbar popup: "Auto-highlight insurance terms"
- [ ] Default: ON
- [ ] Setting persists via chrome.storage.sync
- [ ] When OFF, only right-click context menu works
- [ ] Extension icon badge shows "OFF" indicator when highlighting is disabled

### US-006: Chrome Web Store listing
**Description:** As an SEO, I want the Chrome Web Store listing to include dofollow backlinks to QuoteFii so we gain DR 99 link equity.

**Acceptance Criteria:**
- [ ] Store listing description includes links to blog.quotefii.com and quotefii.com
- [ ] Description is compelling, not spammy (focuses on user value)
- [ ] Screenshots show the extension in action (auto-highlight, popup, glossary)
- [ ] Category: "Shopping" or "Productivity"
- [ ] Privacy: extension reads page content but collects no user data (important for store approval)

## Functional Requirements

- FR-1: Maintain a static dictionary of ~50 insurance terms with plain-English definitions (stored as JSON in the extension bundle)
- FR-2: Detect insurance-related sites using a URL pattern list (configurable, stored in extension)
- FR-3: On detected sites, scan visible DOM text nodes for dictionary matches using case-insensitive whole-word matching
- FR-4: Wrap matched terms in a styled `<span>` with click/hover handler (must not break existing page functionality)
- FR-5: On right-click with text selected, add "Define Insurance Term" to context menu via chrome.contextMenus API
- FR-6: Display definition popup as an injected DOM element (not a new window/tab) positioned near the term
- FR-7: Toolbar popup renders a searchable glossary using the same dictionary data
- FR-8: All outbound links include UTM parameters: utm_source=chrome_extension, utm_medium=popup, utm_content=jargon-decoder
- FR-9: No external network requests. All data is bundled. No analytics, no tracking pixels, no third-party scripts.
- FR-10: Extension manifest v3 (required by Chrome Web Store as of 2024)

## Non-Goals

- No rate data, cost estimates, or financial advice (that's the Cost Checker extension)
- No page modification beyond term highlighting (no ads, no banners, no injected content blocks)
- No user accounts or sign-in
- No analytics or usage tracking (keeps the privacy policy simple for store approval)
- No Firefox/Safari/Edge ports in v1
- No AI-powered definitions or dynamic content; all definitions are static and human-written
- No affiliate links or monetization beyond CTA to QuoteFii

## Technical Considerations

- **Manifest V3**: Required by Chrome Web Store. Use service workers (not background pages), chrome.contextMenus, chrome.storage.sync
- **Content script**: Injected on all pages but only auto-highlights on URL-matched insurance sites
- **Dictionary format**: Single JSON file (~50 terms), each entry has: term, aliases (e.g., "BI" for "bodily injury"), definition, learn_more_url
- **Term matching**: Use word boundary regex to avoid partial matches (e.g., "car" inside "cardinal"). Match the term and all its aliases.
- **Popup positioning**: Calculate based on clicked element's bounding rect + viewport bounds. Flip above/below/left/right to stay in view.
- **No build step**: Plain HTML/CSS/JS. The extension is the source code.
- **Repo**: Separate repo (e.g., AdamFerguson06/quotefii-jargon-decoder)

## Sample Dictionary Entry

```json
{
  "term": "Deductible",
  "aliases": ["deductibles"],
  "definition": "The amount you pay out of pocket before your insurance coverage kicks in. For example, with a $500 deductible, you pay the first $500 of a covered claim and your insurer pays the rest.",
  "learn_more_url": "https://blog.quotefii.com/blog/understanding-auto-insurance-coverage-types"
}
```

## Success Metrics

- Chrome Web Store listing live with dofollow backlinks to quotefii.com and blog.quotefii.com
- Backlink visible in Ahrefs/DataForSEO within 30 days of publishing
- 100+ installs within first 90 days (organic, no paid promotion)
- Click-through rate on "Learn more" and "Compare quotes" links > 2%
- Store rating >= 4.0 stars
- Zero privacy policy issues during Chrome Web Store review

## Open Questions

- Should we create a /glossary page on blog.quotefii.com to serve as the landing page for "term not found" cases?
- Which ~50 terms to include in v1? (Recommendation: start with the terms that appear most frequently on state DOI sites, since that's our audience overlap)
- Should highlighted terms use a tooltip (hover) or a click-to-open popup? Tooltip is faster but harder to interact with on mobile. Click is more deliberate. (Recommendation: click on mobile, hover on desktop)
