# Canonical definition of fit-assessment data (fit-format)

This is the canonical definition of the field specification, validation rules, and sample entries for `fit_assessment.json`, the fit-assessment deliverable. The `job-change-fit-assessment` skill body and the `job-change-fit-assessor` agent both refer to this file. The canonical definition of the judgement criteria (score guidance for each dimension, how to attach evidence) is in `references/fit-criteria.md`.

## Placement

`fit_assessment.json` is written to the following location.

```
{DATA_ROOT}/career-private/fit/{company slug}/fit_assessment.json
```

It contains values derived from the user's profile, axis and self-analysis, so it is placed under the non-public directory `career-private/`. It is never handed to an agent holding a web transmission means (WebSearch, WebFetch). The company slug uses the value already resolved in `career-private/company_index.json` as is. The canonical definition of the format is in job-change-support's `references/company-index-format.md`.

## Top-level structure

```json
{
  "schema_version": "2.0",
  "slug": "kakuu-cloudworks",
  "assessed_at": "2026-07-25",
  "inputs": { "job_posting": true, "company_research": true, "self_analysis": true, "time_analysis": true, "job_search_screening": true },
  "dimensions": [ /* 7次元。後述 */ ],
  "must_condition_results": [ /* axis の必須条件と ref で1対1。後述 */ ],
  "company_score": { /* 企業スコア（0〜100点）。任意。後述 */ },
  "overall": { "recommendation": "条件付き推奨", "rationale": "…", "open_questions": ["…"] }
}
```

| Field | Type | Required | Content |
|---|---|---|---|
| `schema_version` | string | required | The current version is `"2.0"`. `"1.0"` can also be read (see "Versions and migration" below) |
| `slug` | string | required | The company slug. The canonical definition of the format is in job-change-support's `references/company-index-format.md` |
| `assessed_at` | string | required | Assessment date, in `YYYY-MM-DD` |
| `inputs` | object | required | Records whether each input is present, as a boolean. In 2.0 there are five keys: `job_posting`, `company_research`, `self_analysis`, `time_analysis`, `job_search_screening` |
| `screening_source` | object | optional | A reference to the job-search screening result. `{search_id, result_index, classification, screened_at}`. See below |
| `dimensions` | array | required | The evaluation of each dimension. In 2.0 there are exactly seven, no more and no fewer |
| `must_condition_results` | array | required | The judgement of the must-have conditions, one-to-one with the must-have conditions in `{AXIS}` |
| `company_score` | object | optional | The company score (0–100 points). `{total, coverage, provisional, axes, rationale}` |
| `overall` | object | required | The overall verdict |

## dimensions (seven dimensions)

Each dimension has the following structure. In 2.0, there are seven `id` values, and each one is present exactly once.

| id | What is evaluated | Main input source |
|---|---|---|
| `experience_proximity` | The distance between the posting's requirements and job content, and the person's actual work experience. Missing technical requirements are shown in three stages by `skill_gap` | job_posting / profile |
| `aspiration_alignment` | Whether the job content is close to "the work the person wants to do going forward." Evaluated independently of experience proximity | self_analysis / profile / job_posting |
| `work_character_fit` | The match between the eight work-characteristic preferences and the actual conditions at the posting/company | profile / job_posting / company_research / job_search_screening |
| `condition_fit` | The match between the desired conditions (`level=want`) and the working conditions | job_posting / profile |
| `culture_fit` | The match between the company's philosophy, way of working, and reputation, and the person's behavioural evidence and values | company_research / self_analysis |
| `compensation_fit` | The match between the offered range and the desired annual salary / industry level | job_posting / profile / company_research |
| `time_fit` | The match between the annual committed time / effective hourly wage and the time-related conditions | time_analysis / job_posting |

**Experience proximity and aspiration match are treated as separate axes.** This keeps a job centred on coordination, management, or client negotiation from being pushed up to "推奨" (recommend) on close experience alone when it does not match the person's orientation.

```json
{
  "id": "experience_proximity",
  "score": 4,
  "verdict": "判定の要約。1〜数文",
  "skill_gap": "complementable_within_3m",
  "skill_gap_items": [ /* 後述 */ ],
  "evidence": [
    { "source": "job_posting", "ref": "requirements.must[0]", "note": "根拠の説明" }
  ]
}
```

| Field | Type | Content |
|---|---|---|
| `id` | string | One of the seven values above |
| `score` | integer \| null | An integer from 1 to 5. `null` when there is not enough material to judge (hold judgement) |
| `verdict` | string | A summary of the judgement (non-empty) |
| `evidence` | array | One or more items. Each element is described below |
| `skill_gap` | string | Only for `experience_proximity`. See below |
| `skill_gap_items` | array | Only for `experience_proximity`. See below |

Each element of `evidence`:

| Field | Type | Content |
|---|---|---|
| `source` | string | One of `company_research`, `job_posting`, `profile`, `self_analysis`, `time_analysis`, `job_search_screening` (`job_search_screening` only in 2.0). The value `profile` covers evidence that comes from `{AXIS}` as well as from profile.json |
| `ref` | string | Points to the evidence, such as a company_research claim ID (e.g. `C012`), a job_posting field path (e.g. `salary.min`), or a time_analysis field path (e.g. `annual.binding_hours`) |
| `note` | string | An explanation of what this piece of evidence shows |

### skill_gap (the three stages of missing technical requirements)

A breakdown of `experience_proximity` (experience proximity).

| Value | Meaning |
|---|---|
| `none` | No shortfall |
| `complementable_within_3m` | Fillable within three months |
| `needs_6_12m_study` | Needs six to twelve months of study |
| `not_applicable_now` | Hard to apply for at present |
| `unknown` | Not enough material to judge |

`skill_gap_items[]` is the breakdown per missing requirement. It may be an empty array when the value is `none` or `unknown`.

| Field | Type | Content |
|---|---|---|
| `requirement` | string | A quoted passage from the posting's must-have or preferred requirements (non-empty) |
| `gap_level` | string | One of `complementable_within_3m`, `needs_6_12m_study`, `not_applicable_now` |
| `basis` | string | The grounds for choosing this stage (non-empty), such as holding an adjacent skill or an estimate of the study load |
| `evidence` | array | One or more items |

`skill_gap` **must match the heaviest stage among** `skill_gap_items[].gap_level` (a mismatch is an ERROR). Lightening the overall stage alone, to make the total look better, is not allowed.

## must_condition_results

Corresponds one-to-one, by `ref`, with the must-have conditions in `{AXIS}` (`conditions[level=must]` and `work_character_preferences[desire=must]`). Checked by matching the set of IDs. A condition with no material is not set to `yes` or `no` by guesswork. `unknown` takes priority.

```json
{
  "ref": "cond-remote",
  "condition": "リモート勤務が可能であること",
  "met": "yes",
  "negotiable": false,
  "evidence": [ { "source": "job_posting", "ref": "location.remote_policy", "note": "フルリモート可と明記" } ]
}
```

| Field | Type | Content |
|---|---|---|
| `ref` | string | `{AXIS}`'s `conditions[].id` or `work_character_preferences[].trait` (required in 2.0; a duplicate is an ERROR) |
| `condition` | string | The wording of the condition (non-empty). A copy of `statement`, used for display to the user |
| `met` | string | One of `yes`, `no`, `unknown` |
| `negotiable` | boolean | Optional. Whether a condition with `met=no` could be resolved through negotiation or how a policy is operated. Defaults to `false`. Setting it to `true` requires one or more items of evidence |
| `evidence` | array | Grounds. Required with one or more items when `met` is `yes` or `no`. May be empty when `unknown` |

## company_score

The result of scoring the target company from 0 to 100 points. The measured value for each axis is written into `company_research.json`'s `company_metrics` by the company-research role. The fit-assessment role (fit-assessor), which can read `{AXIS}`, then scores that measured value against the axes and weights the user declared in `{AXIS}`'s `company_score_axes`, and writes the result into `company_score`.

`scripts/calculate_company_score.py` performs the calculation mechanically. The canonical definition of the nine candidate quantitative axes, the conversion to points, how criteria are decided, weight allocation, and the overall-score rule is in job-change-company-research's `references/company-score-rubric.md`. The canonical definition of the statistics-derived default criteria is the constant `DEFAULT_THRESHOLDS` in `scripts/calculate_company_score.py`.

The overall score is based on the axes the user chose and the weights they assigned. It measures the company only against that user's own axes and weights. Scores from different users are never compared against each other. The only valid comparison is between companies the same user scored with the same axes and weights.

```json
"company_score": {
  "total": 72,
  "coverage": 85,
  "provisional": false,
  "axes": [
    {
      "axis": "compensation_level", "kind": "quantitative", "weight": 40,
      "value": 6480000, "unit": "円", "score": 65,
      "threshold_source": "user", "thresholds": { "zero": 4500000, "full": 7000000 },
      "grade": "A", "source_url": "https://..."
    },
    {
      "axis": "tech_discretion", "kind": "qualitative", "weight": 35,
      "value": null, "unit": null, "score": 50,
      "threshold_source": null, "thresholds": null,
      "grade": null, "source_url": null,
      "evidence": "求人票の『設計から関与』の記載に合致した"
    },
    {
      "axis": "annual_holidays", "kind": "quantitative", "weight": 25,
      "value": null, "unit": "日", "score": null,
      "threshold_source": null, "thresholds": null,
      "grade": null, "source_url": null,
      "reason": "企業研究に実測値が無い"
    }
  ],
  "rationale": "点数に効いた軸と、判定できなかった軸を書く"
}
```

| Field | Type | Content |
|---|---|---|
| `total` | integer \| null | The overall score, computed as the weighted average of only the axes that could be judged and rounded to a 0–100 integer. `null` when no axis could be judged. The score is never produced by assuming axes or weights |
| `coverage` | integer | The sum of `weight` over the axes that could be judged (0–100). Because the weights sum to 100, this is directly the proportion of the overall score that is backed by evidence |
| `provisional` | boolean | Whether the score is provisional. `true` when `coverage` falls below `calculate_company_score.py`'s constant `COVERAGE_THRESHOLD`, and when `total` is `null` |
| `axes` | array | Lists the axes the user declared, in declaration order. An axis that could not be judged is still listed, with `score` set to `null` |
| `rationale` | string | States which axes drove the score and which axes could not be judged, with the reason (non-empty). Assembled mechanically by the script |

Each element of `axes`:

| Field | Type | Content |
|---|---|---|
| `axis` | string | The axis identifier (non-empty). Copied directly from `{AXIS}`'s `company_score_axes[].axis` |
| `kind` | string | One of `quantitative` (an axis that converts a published figure to points by a linear formula) or `qualitative` (an axis whose judgement conditions the user sets) |
| `weight` | integer | The weight, an integer from 1 to 100. Copied directly from the declaration in `{AXIS}` |
| `value` | number \| null | The measured value for a quantitative axis: the `value` of that axis in `company_metrics`. `null` for a qualitative axis or an axis with no measured value |
| `unit` | string \| null | The unit of the measured value. `null` for a qualitative axis |
| `score` | integer \| null | The score for that axis (a 0–100 integer). `null` for a quantitative axis lacking a measured value or a criterion, or a qualitative axis with no judgement result |
| `threshold_source` | string \| null | The origin of the score's criterion: `user` (`{AXIS}`'s `thresholds`) or `statistic` (`DEFAULT_THRESHOLDS`). `null` for an axis with no criterion or a qualitative axis |
| `thresholds` | object \| null | The applied criterion, `{zero, full}`. `null` for an axis with no criterion or a qualitative axis |
| `grade` | string \| null | The evidence level (A–D) of the measured value. Copied from that axis's `grade` in `company_metrics`. `null` for a qualitative axis |
| `source_url` | string \| null | The source URL of the measured value. Copied from that axis's `source_url` in `company_metrics`. `null` for a qualitative axis |
| `evidence` | string \| null | Only for a qualitative axis. An explanation of which judgement condition was matched. Copied directly from fit-assessor's judgement result |
| `reason` | string | Only for an axis that could not be judged. States whether the measured value, the criterion, or the judgement result is missing |

A quantitative axis's criterion prefers `{AXIS}`'s `thresholds` (`threshold_source` is `user`) over the statistics-derived default (`statistic`). An axis with neither sets `score` to `null`. A score is never produced from a guessed criterion. An axis with no measured value is also set to `null`. A score of 0 means "confirmed to be at a low level," and is kept distinct from having no material.

A qualitative axis's score is the result of fit-assessor applying the facts in the job posting and company research to the judgement conditions (`{AXIS}`'s `judgment`). An axis matching no condition has `score` set to `null`. A midpoint score is never placed by guesswork.

## overall

```json
{
  "recommendation": "条件付き推奨",
  "rationale": "判定の根拠を数文で",
  "open_questions": ["未確認の論点"]
}
```

| Field | Type | Content |
|---|---|---|
| `recommendation` | string | One of `推奨`, `条件付き推奨`, `非推奨`, `判断保留` |
| `rationale` | string | The grounds for the overall verdict (non-empty) |
| `open_questions` | array | Unconfirmed or unsettled points. May be an empty array |

## screening_source

Written when this assessment was reached through job-search (`job-change-job-search`) screening. It gives the source of that judgement. Not written when the case entered from company research without going through job search.

```json
{
  "search_id": "20260725-remote-infra",
  "result_index": 0,
  "classification": "apply_candidate",
  "screened_at": "2026-07-25"
}
```

| Field | Type | Content |
|---|---|---|
| `search_id` | string | The identifier of the referenced search run. Copied directly from the top-level `search_id` in `{DATA_ROOT}/job-search/{search ID}/job_search_results.json`. The value is the same as the directory name `{search ID}`. The canonical definition of the format and the writing criteria is in job-change-job-search's `references/job-search-format.md` |
| `result_index` | integer | The index (0-based) into the referenced `results[]` that points to the job in question |
| `classification` | string | The value of the referenced `results[result_index].classification` |
| `screened_at` | string | The referenced `screening.screened_at` (the judgement date, `YYYY-MM-DD`) |

`search_id` and `result_index` together fix which job in which file the judgement looked at. An axis on which the job-search judgement and the fit-assessment judgement disagree is one the validation script looks up by `result_index` and reports as a WARN.

## Intermediate artifacts (sources.json, qualitative_judgment.json)

These are the two files fit-assessor creates in Step 2. Both are placed under the same `{DATA_ROOT}/career-private/fit/{company slug}/` directory as `fit_assessment.json`. The qualitative axes' judgement conditions are written by the user in their own words, and the judgement result built from them is also a personal-information derived value, so neither file is placed in the non-personal-information tree (under `companies/`). Neither is left as a temporary file with no fixed location, since, when work resumes after an interruption, the presence of these files determines how far Step 2 has progressed.

### sources.json

The source metadata for each figure used to compute committed time. Passed to `calculate_time_analysis.py`'s `--sources-json`, and the script copies each key's metadata into `time_analysis.json`'s `inputs`.

```
{DATA_ROOT}/career-private/fit/{company slug}/sources.json
```

```json
{
  "monthly_overtime_h": { "value": 18, "source": "research", "source_url": "https://...", "grade": "B" },
  "annual_holidays": { "value": 125, "source": "posting", "source_url": "https://...", "grade": "A" },
  "commute_oneway_min": { "value": 45, "source": "user", "source_url": null, "grade": null }
}
```

The keys are `calculate_time_analysis.py`'s input identifiers, and can take `scheduled_hours`, `break_minutes`, `monthly_overtime_h`, `annual_holidays`, `paid_leave_rate`, `paid_leave_granted`, `paid_leave_taken`, `commute_oneway_min`, `salary`. Only an item whose value was passed as a CLI argument is written here. An item left unpassed, deferred to the statistical fallback, is not written here (the script fills `source` in as `fallback`).

| Field | Type | Content |
|---|---|---|
| `value` | number | The extracted value. Written as a record identical to the value passed as the CLI argument. The score calculation uses the CLI argument's value |
| `source` | string | One of `posting` (job-posting metrics), `research` (company-research indicators), `user` (the user's declaration), `fallback`. A value other than the defaults is treated as `user` |
| `source_url` | string \| null | The source URL. `null` when there is no URL, as with the user's own declaration |
| `grade` | string \| null | The evidence level of the source (A–D). The canonical definition is in job-change-company-research's `references/evidence-grading.md`. `null` when a level cannot be assigned, as with the user's own declaration |

### qualitative_judgment.json

The result of applying facts to the judgement conditions (`judgment`) for each axis in `{AXIS}`'s `company_score_axes` whose `kind` is `qualitative`. Passed to `calculate_company_score.py`'s `--qualitative-json`, and the script copies `matched_score` directly into `company_score.axes[].score`, and `evidence` into its own `evidence`.

```
{DATA_ROOT}/career-private/fit/{company slug}/qualitative_judgment.json
```

```json
{
  "tech_discretion": { "matched_score": 50, "evidence": "求人票の『設計から関与』の記載に合致した" },
  "team_autonomy": { "matched_score": null, "evidence": null }
}
```

The keys are `{AXIS}`'s `company_score_axes[].axis` (qualitative axes only).

| Field | Type | Content |
|---|---|---|
| `matched_score` | integer \| null | The `score` of the first judgement condition matched. Writing a value absent from that axis's `judgment[].score` in `{AXIS}` makes `calculate_company_score.py` reject it with exit code 2. An axis matching no condition is `null`; a midpoint score is never placed by guesswork |
| `evidence` | string \| null | An explanation of which statement matched the condition. May be `null` when `matched_score` is `null` |

## Validation rules (validate_fit_assessment.py)

The canonical definition of the mechanical validation is `scripts/validate_fit_assessment.py`. The exit code is 0 for PASS (0 ERRORs) and 1 for FAIL (1 or more ERRORs). WARN alone still counts as PASS.

### ERROR (fails to hold)

- The root is something other than an object.
- `schema_version`, `slug`, or `assessed_at` is missing or empty. `slug` does not match the company-slug format (canonical definition in job-change-support's `references/company-index-format.md`).
- `inputs` is something other than an object. One of the version's keys (four in 1.0, five in 2.0) is missing, or is something other than a boolean.
- `dimensions` is something other than an array. The version's IDs (five in 1.0, seven in 2.0) are not exactly matched (missing, an unknown ID, or a duplicate).
- A dimension's `score` is neither an integer from 1 to 5 nor `null`. `verdict` is missing or empty.
- A dimension's `evidence` is empty, or `source` is outside the defined values (five values in 1.0, six in 2.0).
- `must_condition_results` is something other than an array. `condition` is missing or empty. `met` is other than `yes`, `no`, `unknown`. `met` is `yes` or `no` while `evidence` is empty.
- `overall.recommendation` is outside the four defined values. `overall.rationale` is missing or empty. `overall.open_questions` is something other than an array.
- `company_score` is present and is something other than an object. `total` is neither a 0–100 integer nor `null`. `coverage` is something other than a 0–100 integer. `provisional` is something other than a boolean. `axes` is something other than an array. In `axes[]`: `axis` is empty, `kind` is other than `quantitative`/`qualitative`, `weight` is something other than a 1–100 integer, or `score` is neither a 0–100 integer nor `null`. `rationale` is missing or empty.

When `schema_version` is `2.0`, the following are also ERRORs.

- `dimensions`' IDs do not match the seven values (including the case of using 1.0's `skill_fit`).
- `inputs` lacks `job_search_screening`, or it is something other than a boolean.
- `experience_proximity`'s `skill_gap` is outside the five defined values, or `skill_gap_items` is something other than an array.
- In `skill_gap_items[]`: `requirement` or `basis` is empty, `gap_level` is outside the three defined values, or `evidence` is empty.
- `skill_gap` does not match the heaviest stage among `skill_gap_items[].gap_level`.
- `must_condition_results[].ref` is missing, empty, or duplicated.
- `negotiable` is something other than a boolean, or `negotiable=true` while `evidence` is empty.
- **An unmet must-have condition (`met=no`) exists while `recommendation` is `推奨`.**
- A `met=no` condition whose `negotiable` is not `true` still remains, while `recommendation` is `条件付き推奨`.
- `skill_gap` is `not_applicable_now` while `recommendation` is `推奨` or `条件付き推奨`.
- `aspiration_alignment`'s `score` is non-null, but its evidence contains neither `self_analysis` nor `profile`.
- `inputs.self_analysis` is `false` while `aspiration_alignment.score` is 4 or higher.
- When `--axis` is given: the set of `ref` in `must_condition_results` does not match the set of must-have conditions in `{AXIS}`.
- When `--axis` is given: its root is something other than an object, or it is a career-only `profile.json` (`schema_version` 3.0).

### WARN (holds, but lowers quality)

- `schema_version` is a version other than the known ones (`1.0` / `2.0`).
- `assessed_at` is not in `YYYY-MM-DD` format.
- A dimension's `score` is `null` (an explicit hold on judgement).
- An `evidence` item's `ref` is missing or empty.
- Every key in `inputs` is `false` (the grounds for the assessment are thin).
- An unmet must-have condition (`met=no`) exists while `recommendation` is `推奨` (1.0 only; an ERROR in 2.0).
- `--axis` is not given (the one-to-one correspondence with the must-have conditions is unverified).
- `--axis` is given and its axis is at `schema_version` 1.x (the one-to-one correspondence is verified for a 2.0 axis only).
- Three or more keys in `inputs` are `false` while `recommendation` is `推奨`.
- `inputs.self_analysis` is `false` (the grounds for aspiration are weak).
- `company_score.total` is `null` (no axis could be judged, so the overall score could not be computed).
- `company_score.provisional` is `true` (the total weight of the judged axes is below `COVERAGE_THRESHOLD`, so the score is pulled by a small number of axes).
- When `--screening` is given: a job that job-search judged as meeting a must-have condition has become `met=no` after the job posting was taken in.

## Versions and migration

| `schema_version` | Handling |
|---|---|
| `1.0` | Five dimensions (`skill_fit`, `condition_fit`, `culture_fit`, `compensation_fit`, `time_fit`). `inputs` has four keys. `must_condition_results` does not require `ref`. Only the legacy rules apply |
| `2.0` | Seven dimensions. `inputs` has five keys. The 2.0 rules above also apply |

A 1.0 deliverable passes validation as it stands. This keeps consistency with the policy of storing each company's directory permanently, and never leaves a past assessment unreadable. Mixing versions, such as using the seven-dimension IDs under 1.0 or using `skill_fit` under 2.0, is an ERROR.

## Sample entry

A complete sample entry for a fictional company is in `assets/fit_assessment_example.json`. The unit tests confirm that this sample passes validation.
