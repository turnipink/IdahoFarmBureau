# Copilot Instructions — FBMIC Dashboard

## Mission
This project is a single-file interactive HTML dashboard (`index.html`) presenting Idaho Farm Bureau Insurance Company of Idaho (FBICI) financial data extracted from publicly filed annual statements. It is used for a job application and demonstrates AI/prompt engineering skills. **Data accuracy is non-negotiable.**

## Source PDFs
All verified numbers live in `VERIFIED-DATA.md` at the project root. If you need raw extraction, use the `data-extractor` agent. If you need to validate accuracy, use the `fact-checker` agent.

| PDF File | Content |
|----------|---------|
| `YE24-FBICI-Annual-Statement.pdf` | 2024 full annual statement — primary source for all 2024 data |
| `YE24-WCIC-Annual-Statement.pdf` | 2024 WCIC subsidiary statement |
| `YE20-FBMIC-Annual-Statement.pdf` | 2020 abbreviated filing (SCANNED — must render as image to read) |

## Architecture of index.html

### Key JavaScript Variables (do not rename)
| Variable | Contents | Array Length |
|----------|----------|-------------|
| `years` | `['2015','2016',…,'2024']` | **10** |
| `argallYears` | `['2019','2020',…,'2024']` | **6** |
| `argallAnnotation` | Vertical line at `xMin: 4.5` (between 2019 and 2020 on 10-year charts) | — |
| `argallAnnotation6` | Vertical line at `xMin: 0.5` (between 2019 and 2020 on 6-year charts) | — |

### Sections (in navlink order)
1. `#executive-summary` — KPI cards + CEO scorecard + argallGrowthChart + argallIncomeChart
2. `#merger` — Mountain West merger details + synergyChart + riskDiversification + mergerCompare
3. `#financials` — Tabbed: Premium / Income / Assets / Ratios
4. `#underwriting` — lobMix + lossVsPremium + NPW table
5. `#investments` — investmentPie + investIncomeChart + portfolio table
6. `#structure` — Org chart of holding company
7. `#history` — Timeline + historicGrowth bar chart
8. `#pension` — Plan details (no chart, KPI cards and tables only)
9. `#ai-vision` — AI integration narrative (no charts)
10. `#sources` — Data sources table + methodology disclaimer

### CDN Libraries
- Chart.js 4.4.7: `https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js`
- chartjs-plugin-annotation 3.0.1: `https://cdn.jsdelivr.net/npm/chartjs-plugin-annotation@3.0.1/dist/chartjs-plugin-annotation.min.js`

## Data Integrity Rules

1. **Every number must trace to `VERIFIED-DATA.md` or a source PDF.** Never invent or interpolate figures.
2. **Label/data length parity:** `labels.length === data.length` for every dataset. Chart.js silently misrenders if mismatched.
3. **10-year charts use `years` (length 10) + `argallAnnotation`.**
4. **6-year charts use `argallYears` (length 6) + `argallAnnotation6`.**
5. **Duplicates must be identical:** NPE appears in `premiumChart`, `surplusVsPremium`, the premium data table, and `argallGrowthChart`. All must show identical values.
6. **Use `null` with `spanGaps: true`** for data points that don't exist in a given series — never omit or guess.
7. **Qualitative estimates** (synergy scores, historic milestones pre-2020, Mountain West estimated premium) must carry a source note or badge in the UI.
8. **Surplus value:** Balance sheet shows 376.8; some rounded displays show 377.0. Both are correct for their context. Do not mix them.

## Common Mistakes to Avoid
- Using `years` (10 elements) as labels for a chart that only has 6 data points.
- Changing a number in a chart but forgetting to update the matching HTML table.
- Adding a new chart canvas without a corresponding `new Chart(...)` call in the script block.
- Using `fill: true` on a stacked area chart without checking `fill: '-1'` stacking order.
- Assuming the annotation plugin auto-loads — it must be registered via CDN script tag.

## Workflow for Editing Financial Data
Always follow the orchestrator agent's 5-step protocol:
1. **Understand** what changed and why.
2. **Extract** the authoritative value from `VERIFIED-DATA.md` or source PDF.
3. **Edit** `index.html` (change all occurrences of that metric).
4. **Cross-reference** — search for duplicate occurrences of the same value.
5. **Audit** — run the fact-checker agent against the changed section.
