# Canonical company score specification (company-score-rubric)

This is the canonical specification of the system that scores a target company on a 0-to-100 scale. It defines the axes used for scoring, their conversion to a score, how weight is assigned, and the rule for calculating the overall score. The company researcher agent (job-change-company-researcher) writes the measured figure for each axis, with its source, into `company_metrics` in `company_research.json`. The fit assessment skill (job-change-fit-assessment) mechanically calculates the overall score with `scripts/calculate_company_score.py`.

## Why scoring is built per user

Which aspect of a company matters most differs by user. In a policy-capturing study on a Japanese sample, the ranking between salary and workplace culture flips depending on the level of self-efficacy and on sex, and a discrete-choice experiment on hospital physicians finds a stronger tendency to avoid night duty among married women and those aged 50 and over. In an Australian policy-capturing study, 40% of the variance in ratings of company attractiveness is attributable to differences between respondents. There is no basis for applying the same axes and the same weights to every user (the grounds and limits are in `job-change-fit-assessment/references/fit-methods.md`).

The work is therefore divided as follows.

| Object | Content | Owner |
|---|---|---|
| An axis's measured figure | A fact about the company. The same for anyone who looks | Company research (`company_metrics` in `company_research.json`) |
| The choice of axes, their weights, and scoring criteria | The user's judgment | The profile (`company_score_axes` in `profile.json`) |
| The overall score | Determined from the two items above | Fit assessment (`company_score` in `fit_assessment.json`) |

The company research role holds WebSearch and WebFetch, so `profile.json` must never be passed to it. What is passed is only the array of identifiers for the quantitative axes whose measured figures are to be collected. A qualitative axis's `label`, `definition`, and `judgment` are written by the user in their own words and reflect their own situation, so they are not passed. Judging a qualitative axis is the work of the fit assessment, which holds no web tool, using the facts company research has collected and the job posting as material.

## The two kinds of axis

| Kind | `kind` | Content |
|---|---|---|
| Quantitative axis | `quantitative` | A metric published as a number, traceable to its source. The user picks it from a list of candidates |
| Qualitative axis | `qualitative` | Something that does not become a number. The user decides its label, definition, and judgment criteria entirely, through an interview |

Of the quantitative axes, `compensation_level` (compensation level) is the only one selected by default. Another axis becomes a scoring target only when the user selects it.

## Quantitative candidate axes

Every one of these is numeric, and its source is one of a securities report, a public-statistics site, Shushoku Shikiho, or a job posting. "Direction" states whether a higher value scores higher (`higher_is_better`) or a lower value scores higher (`lower_is_better`).

| Axis key | Metric | Unit | Direction | Main source |
|---|---|---|---|---|
| `compensation_level` | Average annual salary | 円 | Higher is better | The securities report's "Status of Employees" |
| `annual_holidays` | Total annual holidays | 日 | Higher is better | The job posting, Shokuba Labo, Shushoku Shikiho |
| `monthly_overtime` | Average monthly overtime | 時間 | Lower is better | Shokuba Labo, Shushoku Shikiho, the job posting |
| `paid_leave_rate` | Annual paid-leave-taking rate | % | Higher is better | Shokuba Labo, Shushoku Shikiho |
| `turnover_rate` | Turnover rate | % | Lower is better | Shokuba Labo, Shushoku Shikiho |
| `male_childcare_leave_rate` | Male childcare-leave-taking rate | % | Higher is better | The securities report, Shokuba Labo |
| `revenue_growth` | Revenue growth rate (annualized) | % | Higher is better | The securities report, earnings materials |
| `operating_margin` | Operating margin | % | Higher is better | The securities report, earnings materials |
| `equity_ratio` | Equity ratio | % | Higher is better | The securities report, earnings materials |

Adding an axis is conditioned on satisfying all three of the following: it is published as a number, its source is a primary source or a reliable secondary source, and the direction of high versus low is uniquely determined. A word whose measurement target is unsettled, such as "growth potential" or "technical sophistication," does not become an axis. When what should be measured cannot be expressed as a quantitative metric, the user defines it as a qualitative axis.

## Conversion to a score

Each axis's measured figure is converted to a 0-to-100 score by the following linear formula.

```
score = 100 × (実測値 − p0) ÷ (p100 − p0)
```

`p0` is the level corresponding to a score of 0, and `p100` is the level corresponding to a score of 100. For an axis whose direction is `lower_is_better`, `p0 > p100` (a longer overtime level sits closer to a score of 0). Clamp the computed value to 0 when it falls below 0 and to 100 when it exceeds 100, and round it to an integer.

Set `score` to `null` (undeterminable) for an axis with no measured figure. A score of 0 means "confirmed to be at a low level," which is distinguished from having no material at all.

## How the thresholds (p0, p100) are decided

The thresholds are decided in the following priority order. Record the decided source, per axis, as `threshold_source` (`user` / `statistic`).

| Priority | Source | Content |
|---|---|---|
| 1 | The user (`user`) | Use `zero` and `full` from `profile.json`'s `company_score_axes[].thresholds`, when they are written |
| 2 | The statistical default (`statistic`) | When there is no override, use the default based on the distribution of public statistics |

The canonical source for the default values is the constant `DEFAULT_THRESHOLDS` in `job-change-fit-assessment/scripts/calculate_company_score.py`. This document does not duplicate the numbers. Each entry holds `{p0, p100, unit, direction, survey, survey_year, source_url, coverage}`, and its values are set after being corroborated against a primary statistic from a government domain.

An axis with no statistical default is not scored until the user states a threshold. Set `score` to `null` and prompt the user to state a threshold. Do not manufacture a score from a guessed threshold. An axis has no default when applying a statistical distribution to the company's value would shift its level. Compensation level falls under this, because no public statistic gives a company-level annual-salary distribution; its threshold is decided from the user's current salary and desired salary.

Record, in the report, when the user has overridden an axis's threshold. Because the threshold is itself the user's own judgment there, that axis's score cannot be compared against another person's score.

## How to build a qualitative axis

For a qualitative axis, the user decides the label, definition, and judgment criteria in full. An undecided qualitative axis is not included in scoring.

| Item | Content |
|---|---|
| `axis` | The axis's identifier. The user assigns it, in lowercase ASCII letters, digits, and underscores. It must not duplicate a quantitative candidate axis's key |
| `label` | A name in the user's own words. Example: 「裁量の大きさ」 |
| `definition` | The definition of what grounds that label. Make it concrete enough to be judged. Example: 「設計方針を自分で決められること」 |
| `judgment` | An array of judgment criteria. Each element holds `{score, condition}`; `score` is an integer from 0 to 100, and `condition` states "what must be confirmed for that score" |

Sort `judgment` from the highest score down, and apply the conditions from the top, adopting the first one that matches. When no condition matches, set `score` to `null` (undeterminable). Do not place a guessed value in between.

Build a qualitative axis's label and definition through an interview. Do not stop at a granularity where a judgment condition cannot be written, such as "ease of working" or "openness of communication." When a judgment condition cannot be written for something, leave that matter out of scoring, and route it to `overall.open_questions` as a point to confirm at interview.

## Weight allocation

The user allocates weight, in integers summing to 100, across the axes chosen. An axis with a weight of 0 is not placed (to leave an axis out of scoring, remove the axis entirely).

After the allocation, check it with a comparison between two fictional companies. Score the two companies with the allocated weights, and check whether the answer to "which would actually be chosen" agrees with the side that scores higher. When there is a mismatch, either revisit the allocation, or record both the allocation and the actual choice and present them to the user. The skill itself does not decide which one is the true judgment. Multiple empirical studies repeatedly confirm that a self-reported weight diverges from a weight inferred from an actual choice. This check is therefore never skipped.

## Calculating the overall score

Take the weighted average using only the axes that could be judged (whose `score` is not `null`).

```
total = Σ(score × weight) ÷ Σ(weight)      （judged な軸のみ）
coverage = Σ(judged な軸の weight)          （申告した重みの合計は 100 のため、そのまま割合になる）
```

Round `total` to an integer. When not one axis could be judged, set `total` to `null`.

When `coverage` falls below `COVERAGE_THRESHOLD` (a constant in `calculate_company_score.py`), set `provisional` to `true`. The larger the weight of the axes that could not be judged, the more the overall score is determined by only a small number of axes.

The overall score reflects the axes the user chose and the weights they allocated, and holds only relative to that user's own choices. Do not compare overall scores between different users. Compare only companies the same user scored with the same axes and weights.

## Entry format

### `company_metrics` in company_research.json

Company research writes the measured figure for each quantitative candidate axis, with its source, here. Prioritize collecting the metrics for the instructed axes, and set an item that could not be confirmed to `null`.

Use the same keys as the quantitative candidate axes' axis keys. The only key allowed besides an axis key is the auxiliary metric needed for calculating binding hours (`avg_paid_leave_days_taken`), which is not used in scoring.

```json
"company_metrics": {
  "compensation_level": {"value": 6480000, "unit": "円", "source_url": "https://...", "grade": "A", "as_of": "2026-03"},
  "annual_holidays": {"value": 125, "unit": "日", "source_url": "https://...", "grade": "B", "as_of": "2026-04"},
  "monthly_overtime": {"value": null, "unit": "時間", "source_url": null, "grade": null, "as_of": null},
  "avg_paid_leave_days_taken": {"value": 12.4, "unit": "日", "source_url": "https://...", "grade": "B", "as_of": "2026-03"}
}
```

| Field | Required | Entry criteria |
|---|---|---|
| `value` | Required | A number. `null` when it could not be confirmed. Do not enter an estimate |
| `unit` | Required | Matches the unit in the candidate-axis table above |
| `source_url` | Required when `value` is non-null | An existing source URL |
| `grade` | Required when `value` is non-null | The evidence level (A through D). Canonically defined in `references/evidence-grading.md` |
| `as_of` | Recommended | The point in time the value refers to (`YYYY-MM` or `YYYY`) |

For a qualitative axis, company research assigns no score. It writes the confirmed facts and their sources into `claims` for whatever the user instructed as an area of emphasis, and the fit assessment makes the judgment.

### `company_score_axes` in profile.json

Holds the choice of axes, the weights, threshold overrides, and qualitative-axis definitions. The canonical format is in `job-change-support/references/profile-format.md`.

### `company_score` in fit_assessment.json

Holds the overall score, the breakdown per axis, `coverage`, `provisional`, and the grounds. The canonical format is in `job-change-fit-assessment/references/fit-format.md`.

## Division of labor between mechanical validation and audit

| Owner | Scope of check |
|---|---|
| Mechanical validation (validate_company_research.py) | Checks `company_metrics`'s structure, units, whether `value` is a number or `null`, and whether `source_url` and `grade` are present when `value` is non-null. It does not judge the correctness of the value itself. |
| Independent audit (job-change-research-auditor) | Checks whether the measured figure agrees with what its source states, whether the assigned evidence level is appropriate, and whether the metrics for the instructed axes have been collected completely, with nothing missing and nothing extra. |
| Mechanical calculation (calculate_company_score.py) | Mechanically calculates the scoring, the weighted average, `coverage`, and `provisional`, following this document's rules. |

When changing a rule, change this document, `calculate_company_score.py`, the unit tests, and the worked example together.
