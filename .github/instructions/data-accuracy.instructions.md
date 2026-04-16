---
description: "Use when editing financial data in index.html, modifying chart datasets, changing table values, or updating any numerical figure."
applyTo: "index.html"
---

# Data Accuracy Rules for index.html

## Golden Rule
**Every number in index.html must be traceable to `VERIFIED-DATA.md`.** If you cannot find a number there, do NOT guess — invoke the `data-extractor` agent to pull it from the source PDF.

## Before Editing Any Number
1. Look up the authoritative value in `VERIFIED-DATA.md`.
2. Identify **all** places that number appears in `index.html` (search for the exact value).
3. Change every occurrence simultaneously — never leave partial updates.
4. After editing, run the `fact-checker` agent against the changed section.

## Label/Data Length Parity (CRITICAL)
Chart.js silently misrenders when `labels.length !== data.length`. Always verify:
```js
// CORRECT — lengths match
labels: years,           // 10 elements
data: [166.4, 177.9, 192.8, 210.4, 224.1, 239.0, 249.6, 269.3, 299.4, 341.4]  // 10 elements

// WRONG — will silently clip or pad with undefined
labels: years,           // 10 elements
data: [239.0, 249.6, 269.3, 299.4, 341.4]  // 5 elements
```

## Variable Scope
| Chart type | Use labels | Use annotation |
|------------|-----------|----------------|
| 10-year charts | `years` (len 10) | `argallAnnotation` (xMin: 4.5) |
| 6-year charts | `argallYears` (len 6) | `argallAnnotation6` (xMin: 0.5) |
| Growth rate chart (9-point) | `['2016',...,'2024']` inline | Custom `xMin: 3.5` |

## Metrics That Appear in Multiple Places
If you change any of these, you must update **everywhere**:

| Metric | Appears in |
|--------|-----------|
| NPE (10yr array) | `premiumChart`, `surplusVsPremium`, premium tab HTML table, `argallGrowthChart` |
| Surplus (6yr array) | `assetsChart`, `surplusVsPremium`, `argallGrowthChart`, executive summary KPI card |
| Net Income (6yr) | `incomeChart`, income tab HTML table, executive summary KPI card |
| Combined Ratio (6yr) | `fullCombinedRatioChart` tooltip afterBody, ratios tab HTML table, executive summary KPI card |
| Total Assets (6yr) | `assetsChart`, executive summary KPI card, balance sheet table |

## Qualitative Data Markers
Estimated or qualitative figures must be marked in the UI with one of:
- `<span class="estimated-badge">EST</span>` or similar badge
- `<p class="source-note">` with explicit disclaimer
- Language: "from FBICI press release", "directional estimate", "historic estimate"

## Surplus Rounding Convention
- Balance sheet detail: use **376.8** (exact from SEC statutory filing)
- KPI card / headline: use **377.0** (rounded for display)
- Do NOT mix contexts — a balance sheet table must show 376.8

## Common Bugs to Avoid
- `fill: '-1'` stacking in line charts requires datasets in correct order (loss → LAE → expense)
- The annotation plugin requires the CDN `<script>` tag — it does NOT auto-register
- Doughnut charts with negative values (e.g., realized losses of -0.9) may render unexpectedly — use a bar chart or exclude negatives with a note
- `spanGaps: true` must be set on any dataset that uses `null` placeholder values
