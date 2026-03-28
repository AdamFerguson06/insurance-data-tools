---
status: planned
pr: null
completed: null
---
# PRD: GitHub Pages Site Redesign

## Introduction

The insurance-data-tools GitHub Pages site (adamferguson06.github.io/insurance-data-tools) is a public page that serves two purposes: (1) showcase our open-source data tools and methodology, and (2) provide a DR96 dofollow backlink to blog.quotefii.com. The current site is a single HTML file with inline CSS that looks amateurish. It needs a professional redesign that matches the quality of blog.quotefii.com.

## Goals

- Professional, modern design that builds credibility for QuoteFii as a data-driven brand
- Mobile-responsive
- Fast loading (no framework, minimal dependencies)
- Maintain all existing backlinks to blog.quotefii.com with UTM params
- Look like a real open-source project page, not a link farm

## User Stories

### US-001: Visual design overhaul
**Description:** As a visitor, I want the page to look professional and modern so I trust the data and tools being presented.

**Acceptance Criteria:**
- [ ] Design matches blog.quotefii.com's brand: same color palette (#1B3A6D primary, warm/approachable feel)
- [ ] Clean typography: system font stack or a single Google Font (Inter or similar)
- [ ] Proper spacing, visual hierarchy, and section breaks
- [ ] Hero section with clear value proposition
- [ ] Cards for tools have visual polish (subtle shadows, hover states, icons or illustrations)
- [ ] Data tables are clean and readable
- [ ] CTA section is visually distinct but not aggressive
- [ ] Footer is minimal and professional
- [ ] Verified visually in browser (desktop and mobile)

### US-002: Mobile responsiveness
**Description:** As a mobile visitor, I want the page to work well on my phone.

**Acceptance Criteria:**
- [ ] Single-column layout on mobile
- [ ] Readable text without horizontal scrolling
- [ ] Tables scroll horizontally if needed
- [ ] Touch-friendly spacing on links and buttons
- [ ] Verified on mobile viewport (375px width)

### US-003: Content refinement
**Description:** As a visitor, I want the content to be concise, credible, and useful.

**Acceptance Criteria:**
- [ ] Hero: one clear sentence about what this is ("Open-source auto insurance data tools")
- [ ] Remove any content that looks like it's trying too hard to sell
- [ ] Tools section: show status clearly (live vs in-progress)
- [ ] Data methodology section: keep it, this is the credibility builder
- [ ] Rate factor table: keep with source attribution
- [ ] Contributing section: brief, links to GitHub issues
- [ ] No em dashes or double hyphens in any content

### US-004: SEO and backlink optimization
**Description:** As an SEO, I want the page to be properly optimized for search and backlink value.

**Acceptance Criteria:**
- [ ] Proper meta tags (title, description, OG tags)
- [ ] All links to blog.quotefii.com use UTM params (utm_source=github, utm_medium=pages, utm_content=insurance-data-tools)
- [ ] Links are dofollow (default for GitHub Pages)
- [ ] Canonical URL set
- [ ] Page loads fast (no heavy assets, no JavaScript frameworks)

## Non-Goals

- No JavaScript frameworks (React, Vue, etc.). Plain HTML/CSS only.
- No build step. The HTML file is the deployment.
- No multi-page site. Single page is fine.
- No blog or dynamic content on this page.

## Technical Considerations

- **Deployment:** GitHub Pages from the main branch, root directory
- **Repo:** github.com/AdamFerguson06/insurance-data-tools (public)
- **URL:** adamferguson06.github.io/insurance-data-tools
- **Files:** index.html, README.md, possibly a CSS file and a few SVG icons
- **No custom domain** (the whole point is the github.io domain authority)

## Design Inspiration

- Match blog.quotefii.com's visual language
- Clean open-source project pages: Astro's site, Tailwind's landing page, Vercel's project pages
- Data-focused: lots of white space, clean tables, subtle color accents

## Success Metrics

- Page indexed by Google
- Dofollow backlinks visible in Ahrefs/DataForSEO
- Page looks professional enough that someone would share it or link to it organically
