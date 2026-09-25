# Canonical specification of company_research.json (company-research-format)

This is the canonical specification defining the field specification, entry criteria, and mechanical validation rules for `company_research.json`, the structured data of company research. The company researcher agent (job-change-company-researcher) builds its deliverable to this specification, and `scripts/validate_company_research.py` mechanically checks it against this specification.

The output location is `{DATA_ROOT}/companies/{company slug}/company_research.json`.

## Overall structure

```json
{
  "company": { "name": "", "securities_code": "", "edinet_code": "" },
  "research_date": "YYYY-MM-DD",
  "claims": [
    {
      "id": "C001",
      "topic": "philosophy",
      "statement": "反証可能な命題を1文で書く。",
      "evidence": [
        {
          "source_url": "https://...",
          "source_name": "",
          "grade": "A",
          "quote": "根拠となる引用。",
          "accessed": "YYYY-MM-DD"
        }
      ],
      "confidence": "medium"
    }
  ],
  "company_metrics": {
    "compensation_level": { "value": 6120000, "unit": "円", "source_url": "https://...", "grade": "A", "as_of": "2026-03" },
    "annual_holidays":    { "value": null,    "unit": "日", "source_url": null,          "grade": null, "as_of": null }
  },
  "open_questions": [ "" ]
}
```

## Field specification

### company (object, required)

| Field | Required | Entry criteria |
|---|---|---|
| `name` | Required | The company's formal name. Write it in its full registered form, including the entity-type suffix such as 株式会社 |
| `securities_code` | Optional | A listed company's securities code (4 digits). May be omitted for an unlisted or overseas company |
| `edinet_code` | Optional | The EDINET code (E + 5 digits). Enter it when a securities report was used as a source; may be omitted otherwise |

An empty `name` is an ERROR in mechanical validation. `securities_code` and `edinet_code` may be absent; validation passes without them.

### research_date (string, recommended)

The date the research was performed (`YYYY-MM-DD`). Leaving it unset is a WARN in mechanical validation. It records when the research happened and is used to judge whether re-research is needed.

### claims (array, required, at least 1 item)

An array of claims about the company. At least 1 item is required; an empty array is an ERROR. Each claim has the following fields.

| Field | Required | Entry criteria |
|---|---|---|
| `id` | Required | The claim's identifier. A sequence starting from `C001` is recommended (mechanical validation does not require strict sequencing) |
| `topic` | Required | One of the 8 kinds described below |
| `statement` | Required | A falsifiable proposition, written in one sentence (described below) |
| `evidence` | Required | An array of sources. At least 1 item is required |
| `confidence` | Required | One of `high` / `medium` / `low` |

#### topic (8 kinds)

| topic | Covers |
|---|---|
| `philosophy` | Corporate philosophy, creed, purpose, and behavioral guidelines (canonically defined in `references/philosophy-analysis.md`) |
| `business` | Business description, segments, products/services, market position |
| `financials` | Results, financials, average annual salary, average years of service, employee count |
| `compensation` | Compensation system, bonuses, grades, compensation level |
| `benefits` | Benefits, leave, certification schemes (Kurumin, Eruboshi, Health and Productivity Management Outstanding Organization, and so on) |
| `workstyle` | Work style, overtime, paid-leave-taking rate, remote/flex arrangements, retention |
| `reputation` | Reputation from outside the company and from employees (aggregated review-site posts, reporting, and so on) |
| `selection_process` | Selection process, its stages, whether a written test or aptitude test exists, interview accounts |

**The required topics** are the 7 kinds `philosophy`, `business`, `financials`, `compensation`, `benefits`, `workstyle`, and `reputation`; having zero claims for any of these is an ERROR. `selection_process` is optional; 0 items is a WARN (collecting it is recommended, because the interview preparation that follows uses it as grounding).

#### statement (a falsifiable proposition)

Write the statement as a "falsifiable proposition." Put it in a form whose truth a source can confirm.

- Good example: 「第10期の平均年間給与は6,120千円である。」「健康経営優良法人2026に認定されている。」「選考は書類→適性検査→一次面接→最終面接の4段階である。」
- Bad example: 「良い会社である。」「働きやすい。」（真偽を出典で確認できない評価。企業が自社を良く見せる主張はこの形になりやすい）

When handling evaluative content, make the proposition state "who is making that evaluation." Example: 「口コミ集計サイトの総合評価は3.6である（回答87件）。」

#### evidence (an array of sources, at least 1 item)

| Field | Required | Entry criteria |
|---|---|---|
| `source_url` | Required | The source's URL. Must be a string starting with `http` |
| `source_name` | Recommended | The source's name (the outlet or document name) |
| `grade` | Required | `A` / `B` / `C` / `D`. Assignment criteria are in `references/evidence-grading.md` |
| `quote` | Required | A quote from the source (non-empty). Transcribe the passage that grounds the proposition, verbatim |
| `accessed` | Recommended | The date it was accessed (`YYYY-MM-DD`) |

Each of the following is an ERROR: `source_url` not starting with `http`, `grade` outside A through D, and an empty `quote`.

#### confidence

| Value | Guideline |
|---|---|
| `high` | A fact backed by primary/official (A) or reliable secondary (B) evidence, that agrees across multiple sources |
| `medium` | Backed by A or B, but from a single source, or with some limit remaining |
| `low` | Centered on C or D, staying a supporting signal for a trend |

**Rule**: do not give `high` to a claim based on level C or D alone (ERROR). Do not give `high` to a company's own evaluative claim about itself, even when the source is level A (treat it as B-equivalent; mechanical validation cannot judge this, and it is the audit agent's territory).

### open_questions (array, recommended)

Record a point that could not be corroborated, a discrepancy between sources, and the limits of a primary source's representativeness. Example: 「有報の平均年間給与は全従業員平均であり、応募職種の給与水準は判別できない。」

### company_metrics (object, required)

`company_metrics` is a required top-level field that structures the measured figures for the quantitative candidate axes into machine-readable numbers. It is kept independent of the prose `claims`, and downstream processing (calculating the company score, estimating effective hourly pay) uses the numbers directly. The canonical definition of the axes, units, and directions is in `references/company-score-rubric.md`.

Company research only collects measured figures; it neither scores nor rates. Prioritize collecting the metrics for the instructed axes, and set `value` to `null` for an item that could not be confirmed. Do not enter an estimate.

Use the same keys as the quantitative candidate axes' axis keys. The only key allowed besides an axis key is the auxiliary metric `avg_paid_leave_days_taken` (the average number of paid-leave days taken, used to calculate binding hours; unit: 日).

| Axis key | Metric | Unit |
|---|---|---|
| `compensation_level` | Average annual salary | 円 |
| `annual_holidays` | Total annual holidays | 日 |
| `monthly_overtime` | Average monthly overtime | 時間 |
| `paid_leave_rate` | Annual paid-leave-taking rate | % |
| `turnover_rate` | Turnover rate | % |
| `male_childcare_leave_rate` | Male childcare-leave-taking rate | % |
| `revenue_growth` | Revenue growth rate (annualized) | % |
| `operating_margin` | Operating margin | % |
| `equity_ratio` | Equity ratio | % |

Each item has the following fields.

| Field | Required | Entry criteria |
|---|---|---|
| `value` | Required | A number, or `null` to represent that it could not be confirmed. A string or a boolean is not allowed |
| `unit` | Required | The same string as the unit in the table above |
| `source_url` | Required when `value` is non-null | The source's URL. A string starting with `http` |
| `grade` | Required when `value` is non-null | `A` through `D`. Defined in `references/evidence-grading.md` |
| `as_of` | Recommended | The point in time the value refers to (`YYYY-MM` or `YYYY`). Missing is a WARN |

**Rule**: when you collect a figure such as annual holidays, overtime, paid-leave-taking rate, or average annual salary, do not stop at embedding it in a prose claim — always structure it into this company_metrics as well (noting the unit, source URL, and level together). Leave `value` as `null` when it cannot be confirmed.

## Mechanical validation rules (validate_company_research.py)

`scripts/validate_company_research.py` performs the mechanical check. Even a single ERROR is a FAIL (exit code 1); zero ERRORs is a PASS (exit code 0, even with WARNs present).

**ERROR (the deliverable does not hold together, or a rule is violated)**

- It cannot be parsed as JSON
- `company` is not an object, or `company.name` is empty
- `claims` is not an array, or is empty
- A claim is missing a required field (`id`, `topic`, `statement`, `evidence`, or `confidence`)
- `topic` is outside the 8 kinds
- `confidence` is outside `high`/`medium`/`low`
- `evidence` is empty
- `source_url` does not start with `http`
- `grade` is outside A through D
- `quote` is empty
- Any of the 7 required topics (`philosophy`, `business`, `financials`, `compensation`, `benefits`, `workstyle`, `reputation`) has zero claims
- A claim based on level C or D alone has `confidence=high`
- `company_metrics` is missing, or `company_metrics` is not an object
- A `company_metrics` key is neither one of the 9 quantitative candidate axes' axis keys nor `avg_paid_leave_days_taken`
- A `company_metrics` item is not an object
- `value` is neither a number nor `null`
- `unit` differs from the unit defined for the axis
- For an item whose `value` is non-null, `source_url` is not a string starting with `http`
- For an item whose `value` is non-null, `grade` is outside A through D

**WARN (it holds together, but the grounds are weak)**

- A topic's claims rest entirely on level C or D
- `selection_process` has 0 claims
- `research_date` is unset
- An item whose `value` is non-null has no `as_of`
- All 9 quantitative candidate axes have a null `value`

A worked example is in `assets/company_research_example.json` (a fictional company).
