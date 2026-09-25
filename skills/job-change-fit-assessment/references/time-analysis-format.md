# Canonical specification of time_analysis.json (time-analysis-format)

This is the canonical definition of `time_analysis.json`'s specification and of the computation `scripts/calculate_time_analysis.py` performs. From the candidate company's job posting, company research, and user input, it mechanically computes the daily and annual committed time, the working hours, and the effective hourly wage, and uses these as grounds for the time_fit (time match) evaluation.

## Placement and handling

The generated artifact is placed at `career-private/fit/{company slug}/time_analysis.json`. The current job's computation result, which serves as the comparison baseline, does not correspond to any target company, so it is placed at `career-private/fit/current/time_analysis.json` and reused across every company. Since committed time and effective hourly wage are values derived from personal information such as annual salary and commute time, they are isolated under `career-private/`, and are never handed to an agent holding a web transmission means (WebSearch, WebFetch).

## Formulas

`calculate_time_analysis.py` computes with the following formulas. The denominator is unified to "the annual number of actual working days."

- Monthly working days = `(365 − annual holidays) ÷ 12`
- Daily overtime = `average monthly overtime ÷ monthly working days`
- Daily committed time = `scheduled working hours + break + daily overtime + one-way commute × 2`
- Paid-leave days taken = `actual days taken (if available) / otherwise, expected days granted × taken rate (%) ÷ 100`
- Annual number of actual working days = `365 − annual holidays − paid-leave days taken`
- Annual committed time = `annual number of actual working days × daily committed time`
- Annual working hours = `annual number of actual working days × (scheduled working hours + daily overtime)`
- Effective hourly wage (binding_basis) = `expected annual salary ÷ annual committed time`
- Effective hourly wage (labor_basis) = `expected annual salary ÷ annual working hours`

When there is no leveled expected annual salary, set `effective_hourly_wage` to `null`. Do not invent an effective hourly wage.

The internal computation does not round. Rounding happens only at output time: hours to one decimal place, days and yen to integers.

## Sensitivity analysis

`sensitivity` holds the increase or decrease (in hours) of the annual committed time when a single item is moved, with the other inputs held fixed.

- `overtime_plus10h` / `overtime_minus10h`: the change from moving average monthly overtime by ±10 hours
- `commute_plus15min` / `commute_minus15min`: the change from moving one-way commute by ±15 minutes

The annual number of actual working days is unaffected by overtime and commute. The increase and decrease therefore come out as symmetric values with the sign reversed between the plus side and the minus side, unchanged by the baseline level.

## Comparison with the current job

The target company's committed time and effective hourly wage cannot be judged good or bad from the absolute value alone. Compute the current job with the same formula, and use the difference as material for time_fit and compensation_fit.

Passing the current job's computation result to `--baseline-json` adds `comparison` to the output. Without it, `comparison` is not added.

| Key | Content |
|---|---|
| `current` | The current job's value. Holds the four items `annual_binding_hours`, `annual_labor_hours`, `hourly_wage_binding_basis`, `hourly_wage_labor_basis`. |
| `delta` | The "target − current" difference. Same items as `current`. |

If either side cannot be taken as a number for an item, set both `current` and `delta` to `null` for it. Round hours to one decimal place, yen to an integer.

The salary, working hours, and commute time used for the current job's computation are taken as user input (`user`), and the commute time uses the same lane as "Handling when commute time is not entered" below.

## Input priority

Each input's value is decided in the following priority order. The value fixed at the higher level is used; confidence falls as the level drops. Record the decided source in each input's `source` (`posting` / `research` / `user` / `fallback`).

| Priority | Source | Content |
|---|---|---|
| 1 | Job posting (`posting`) | A value in `job_posting.json`'s `working_hours` / `metrics`, carrying a quote. Given top priority. |
| 2 | Company-research indicators (`research`) | `company_research.json`'s `company_metrics` (average monthly overtime is `monthly_overtime`, annual holidays is `annual_holidays`, paid-leave-taken rate is `paid_leave_rate`, paid-leave days taken is `avg_paid_leave_days_taken`). When multiple candidates exist for the same item, adopt the one with the highest evidence level (A → B → C → D). The canonical definition of evidence levels lives in `job-change-company-research`'s `references/evidence-grading.md`. Avoid asserting from level C or D alone, and treat an adopted value at lower confidence even then. |
| 3 | User input (`user`) | A value the user reports directly, such as commute time. |
| 4 | Statistical fallback (`fallback`) | A default value based on a primary government statistic, applied to an item left unfilled at the levels above. |

The caller (the fit-assessment skill body) decides the value in priority order, passing the fixed value as a CLI argument and each value's source metadata to `--sources-json`. The script itself does not read `job_posting.json` or `company_research.json`; it only computes from the values passed to it and applies the fallback to unspecified items.

## Handling when commute time is not entered

The one-way commute time is handled through this single lane only.

1. If `career-private/commute.json`'s `one_way_minutes` for the slug exists, use it.
2. If not, ask once through AskUserQuestion.
3. If still unknown, apply the statistical fallback, and note it explicitly in `fallbacks_used` and `assumptions`.

No address geocoding or web route search is performed.

## Canonical definition of the fallback constants

The canonical definition of the statistical fallback's values, survey name, survey year, and source URL is the constants `FALLBACKS` (statistical values) and `STATUTORY_DEFAULTS` (the statutory defaults for scheduled working hours and break) inside `calculate_time_analysis.py`. This document does not duplicate the numbers. To change a constant, edit that constant in the script directly.

Each item of `FALLBACKS` is set after checking the latest published value of a primary statistic (a government domain) from either the Ministry of Health, Labour and Welfare or the Ministry of Internal Affairs and Communications, and holds `{value, survey, survey_year, source_url}`. Whenever a fallback is applied to an item, it is always left in both the generated artifact's `fallbacks_used` (a structured record) and `assumptions` (a sentence including the value, survey name, survey year, and URL).

## Output structure

```
{
  "inputs": { "<input key>": {"value", "source", "source_url"|null, "grade"|null}, ... },
  "daily": {"scheduled_hours", "break_h", "daily_overtime_h", "commute_oneway_h", "binding_hours"},
  "annual": {"working_days", "paid_leave_taken_days", "binding_hours", "labor_hours"},
  "effective_hourly_wage": {"binding_basis", "labor_basis"} | null,
  "sensitivity": {"overtime_plus10h", "overtime_minus10h", "commute_plus15min", "commute_minus15min"},
  "comparison": {"current": {...}, "delta": {...}},
  "assumptions": [ ... ],
  "fallbacks_used": [ {"field", "value", ...}, ... ]
}
```

`inputs` holds only the values used in the computation. When the actual paid-leave-days-taken value (`paid_leave_taken`) is given, that value is loaded into `inputs`, and the days granted and taken rate are not loaded, since they are not used in the computation. When the actual value is not given, the days granted (`paid_leave_granted`) and taken rate (`paid_leave_rate`; in %, on the same scale as company research's `company_metrics.paid_leave_rate`) are loaded, and days taken is estimated as days granted × taken rate ÷ 100.

The example lives in `assets/time_analysis_example.json` (fictional data).

## CLI

```bash
python scripts/calculate_time_analysis.py \
    [--scheduled-hours H] [--break-minutes M] [--overtime-h-month H] \
    [--annual-holidays D] [--paid-leave-rate R] [--paid-leave-granted D] \
    [--paid-leave-taken D] [--commute-oneway-min M] [--salary YEN] \
    [--sources-json PATH] [--baseline-json PATH] [--out PATH] [--json]
```

`--baseline-json` takes the current job's `time_analysis.json` path. Any item not specified receives the fallback. `--out` writes to the given path (creating the parent directory if it does not exist), and `--json` writes the result to standard output. When the input is contradictory — annual holidays of 365 or more, a paid-leave-taken rate outside 0–100 (%), and the like — it returns exit code 2 with a clear message.
