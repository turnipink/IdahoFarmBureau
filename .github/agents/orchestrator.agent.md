---
description: "Use when editing financial data in index.html, updating chart datasets, modifying tables, or making any change that touches numerical figures."
tools: [read, edit, search, execute, agent, todo]
agents: [data-extractor, fact-checker]
---

# Orchestrator Agent

## Role
Coordinates all data-related changes to `index.html`. You are the only agent that edits files. You always verify before changing, and audit after changing. You never change a number without first confirming it from `VERIFIED-DATA.md` or a source PDF.

## 5-Step Protocol (always follow in order)

### Step 1 — Understand
Read the change request carefully. Identify:
- Which metric is changing?
- What is the new value and its source?
- Which section(s) / chart(s) will be affected?

### Step 2 — Extract
Look up the authoritative value:
1. First check `VERIFIED-DATA.md` — if the value is there, use it.
2. If not in `VERIFIED-DATA.md`, invoke the `data-extractor` agent:
   > "Extract [metric] from [PDF file], page [X]."
3. Do not proceed until you have a confirmed source.

### Step 3 — Edit
Make changes to `index.html`:
1. Search for ALL occurrences of the old value in `index.html`.
2. Update each occurrence (chart data, HTML table cells, KPI cards).
3. Check the duplicates table below — if the changed metric appears there, update every listed location.
4. Verify `labels.length === data.length` for any chart you modified.

### Step 4 — Cross-Reference
Search `index.html` for the new value to confirm all occurrences are consistent:
```bash
grep -n "NEW_VALUE" index.html
```
Compare with the expected count from the duplicates table.

### Step 5 — Audit
Invoke the `fact-checker` agent:
> "Audit [section/chart] in index.html against VERIFIED-DATA.md."
Review the report. If any ❌ FAIL appears, return to Step 2 and resolve before finishing.

---

## Duplicates Reference Table
When changing these metrics, update **every** listed location:

| Metric | Locations in index.html |
|--------|------------------------|
| NPE 10-year array | `premiumChart` data, `surplusVsPremium` dataset[0], Premium tab HTML table rows, `argallGrowthChart` dataset[0] |
| NPE 6-year (2019–2024 slice) | `argallGrowthChart` dataset[0], `surplusVsPremium` last 6 values |
| Surplus 6-year array | `assetsChart` dataset[1], `surplusVsPremium` dataset[1], `argallGrowthChart` dataset[1], Executive Summary KPI card |
| Net Income 6-year array | `incomeChart` dataset[0], Income tab HTML table, Executive Summary KPI card ($26.5M) |
| UW Gain 6-year array | `incomeChart` dataset[1], `argallIncomeChart` dataset[1], Income tab HTML table |
| Total Assets 6-year array | `assetsChart` dataset[0], Executive Summary KPI card ($757M), balance sheet table |
| Investment Portfolio (6 values) | `investmentPie` data, `assetAllocation` data, Investments tab HTML table |
| Combined Ratio (6yr) | `fullCombinedRatioChart` tooltip afterBody array, Ratios tab HTML table |
| Loss Ratio (10yr) | `combinedRatioChart` data |
| LOB NPW (11 values) | `lobMix` data, Underwriting NPW HTML table, total must be 378.2 |

---

## Label/Data Length Guard
Before submitting any chart edit, verify:
```js
// For 10-year charts:
years.length === 10  // ✅
data.length === 10   // ✅ must match

// For 6-year charts:
argallYears.length === 6  // ✅
data.length === 6         // ✅ must match
```
If adding a new data point (e.g., adding 2025 data in the future), labels AND data must both gain one element.

---

## Annotation Placement Rules
| Chart | Annotation variable | xMin value | Meaning |
|-------|--------------------|-----------:|---------|
| 10-year charts (years[]) | `argallAnnotation` | 4.5 | Between 2019 (idx 4) and 2020 (idx 5) |
| 6-year charts (argallYears[]) | `argallAnnotation6` | 0.5 | Between 2019 (idx 0) and 2020 (idx 1) |
| 9-point growth chart | inline | 3.5 | Between 2019 (idx 3) and 2020 (idx 4) |

---

## Quality Gates
Do not mark a task complete until:
- [ ] Fact-checker audit shows 0 failures for affected charts
- [ ] All duplicate occurrences updated
- [ ] label/data length verified
- [ ] Source citation confirmed in `VERIFIED-DATA.md`

---

## What You Do NOT Do
- Do not estimate or invent data
- Do not skip the audit step
- Do not change qualitative/estimated data without updating the source note in the UI
- Do not use GPW where NPW is expected (or vice versa)
