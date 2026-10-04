# axis.json specification

This is the canonical definition of axis.json, the user's job-change axis, within the job-change-support family of skills. The code of `scripts/validate_axis.py` (whose checks are in `check_axis` of `scripts/validate_profile.py`) and `scripts/split_profile.py` follows this specification exactly.

axis.json holds the job-change axis: the reasons for changing jobs, the structured conditions, the work-character preferences, the company scoring axes, the target companies and roles, and the salary. The career record is stored in profile.json (`references/profile-format.md`). `job-change-axis` is the one skill that writes axis.json.

## Location

- Where the canonical file is stored: `{DATA_ROOT}/career-private/axis.json` (the `axis` key in the `paths` that `jc_config.py --show` returns).
- User data is never placed in the skill's own folder (`skills/job-change-support/`). `assets/axis_example.json` is a fictitious filled-in example.

Every skill refers to the axis source as `{AXIS}` and resolves it in this order:

1. `career-private/axis.json`, when it exists.
2. Otherwise, a `career-private/profile.json` whose `schema_version` is `1.0`, `1.1` or `2.0`. Such a file holds the axis keys itself.
3. When neither applies, the axis is absent. A skill that needs the axis routes the user to `job-change-axis`. A skill for which the axis is optional proceeds without it and says so.

**Stop state.** When `axis.json` exists and `profile.json` is still at `1.0`, `1.1` or `2.0`, the two files each claim the axis. The skill stops, shows both paths and the backup path `career-private/profile.json.bak-{version}` when that file exists, and asks the user to settle which file holds the axis. The skill proceeds once the user has resolved it, such as by moving the stale file aside.

The axis gate is:

```bash
python {HUB_SKILL_DIR}/scripts/validate_axis.py {AXIS}
python {HUB_SKILL_DIR}/scripts/validate_axis.py {AXIS} --json
```

The exit code is 0 for PASS and 1 for FAIL; WARN alone counts as PASS. `validate_axis.py` accepts axis.json at `1.0`, `1.1` or `2.0`, and a `1.0`, `1.1` or `2.0` profile.json (it checks only the axis keys of that file). A `3.0` profile.json is an ERROR, since it does not hold the axis.

## Root structure

```json
{
  "schema_version": "2.0",
  "updated_at": "2026-07-12",
  "job_change_axis": { },
  "company_score_axes": [ ],
  "targets": { },
  "salary": { }
}
```

| Field | Type | Required / optional | Meaning and entry guidance |
|---|---|---|---|
| `schema_version` | string | required | The specification version. The current version is `"2.0"`. `"1.0"` and `"1.1"` can also be read (an axis.json split from a 1.x profile keeps that version; see "Version and migration" below). Missing is an ERROR; `"3.0"` is an ERROR |
| `updated_at` | string | optional | The date of the last update, in `YYYY-MM-DD` format. Rewrite it on every update. Missing is a WARN |
| `job_change_axis` | object | required | The job-change axes. See below |
| `company_score_axes` | array | optional, 2.0 only | A declaration of the axes and weights used to score a company. Valid only when `schema_version` is `2.0`. See below |
| `targets` | object | optional | Target companies and roles. A WARN occurs when every category is empty. See below |
| `salary` | object | optional | Salary. See below |

The key names equal those of a 2.0 profile.json, so a consumer that reads `data["job_change_axis"]` works with either file as `{AXIS}`.

## job_change_axis

The job-change axes. Holds the reason for changing jobs, the must-have conditions, and the nice-to-have conditions separately. This is the foundation for consistency between the statement of motivation in the application documents and the job interview.

| Field | Type | Required / optional | Meaning and entry guidance |
|---|---|---|---|
| `reasons` | array | required | An array of strings giving the reasons for the job change. At least one entry is required (empty is an ERROR). Write these as what the user wants to achieve next. Deepening these into a constructive rephrasing can be done in `job-change-self-analysis` (the canonical definition is `reason_for_change` in that skill's `self_analysis.json`; only the short statements are reflected back here) |
| `conditions` | array | **required in 2.0** | An array of conditions. Holds must-have and nice-to-have conditions structured as an axis, an operator, and a threshold. See below |
| `work_character_preferences` | array | **required in 2.0** | The desire level for each of the 8 work characteristics. Holds exactly 8 entries. See below |
| `must_conditions` | array | 1.x only | An array of free-text strings for must-have conditions. Moved into `conditions` in 2.0. Non-empty in 2.0 is a WARN |
| `want_conditions` | array | 1.x only | An array of free-text strings for nice-to-have conditions. Moved into `conditions` in 2.0. Non-empty in 2.0 is a WARN |
| `priority_note` | string | optional | A note on the priority among must-have conditions, and when to next re-evaluate the axes |

### conditions (2.0)

This is the one place conditions are held. Letting free text and structured data coexist would put the same condition in two places, so the wording from 1.x's `must_conditions` / `want_conditions` is moved into `statement`, and the original arrays are emptied.

| Field | Type | Required / optional | Meaning and entry guidance |
|---|---|---|---|
| `id` | string | required | The condition's identifier, matching `^[a-z0-9][a-z0-9-]*$`. A duplicate is an ERROR. This is the target that `must_condition_results[].ref` in fit assessment refers to |
| `level` | string | required | `must` (non-negotiable) or `want` (nice to have). Any other value is an ERROR |
| `statement` | string | required | The wording of the condition. Write it in the words used at a job interview or in condition negotiation. Empty is an ERROR |
| `axis` | string or null | required | Either one of the 8 axis IDs in `references/screening-axes.md`, or `null` (a qualitative condition that fits none of the 8 axes). Any other value is an ERROR |
| `operator` | string | required | `>=` / `<=` / `==` / `in` / `qualitative`. Any other value is an ERROR |
| `value` | number / string / array / null | conditionally required | The value to compare against. An ERROR occurs when `operator` is anything other than `qualitative` and `value` is `null` |
| `unit` | string | optional | `yen` / `h_month` / `days_year` / `ratio` / `none`. Any other value is an ERROR |
| `verification` | string | required | Where it can be confirmed: `posting` (the job posting), `research` (company research), `interview` (the job interview), or `unverifiable`. Any other value is an ERROR |
| `priority` | integer | optional | 1 is the highest priority. The ranking within `level=must`. A missing or duplicate value is a WARN |
| `note` | string | optional | A supplementary note |

```json
{
  "id": "cond-remote",
  "level": "must",
  "statement": "フルリモートが制度として保証されていること",
  "axis": "remote_certainty",
  "operator": "==",
  "value": "guaranteed",
  "unit": "none",
  "verification": "posting",
  "priority": 1
}
```

A condition whose `axis` is `null` cannot be judged mechanically from a job posting. Set `operator` to `qualitative`, and set `verification` to `research` or `interview`. This kind of condition is never used in job-search classification; it is passed on to fit assessment and to confirmation at the job interview.

### work_character_preferences (2.0)

Gives each of the 8 work characteristics a desire level. **Exactly 8 entries** are required (a missing or duplicate entry is an ERROR). Requiring "not needed" to be stated explicitly distinguishes a blank entry from indifference. The definition of the trait IDs is in `references/screening-axes.md`.

| Field | Type | Required / optional | Meaning and entry guidance |
|---|---|---|---|
| `trait` | string | required | One of the 8 trait IDs. A value outside the defined set, a duplicate, or a missing value is an ERROR |
| `desire` | string | required | `must` (passes on the job if not met), `important` (given weight), `neutral` (no preference either way), or `not_required` (not needed). Any other value is an ERROR |
| `statement` | string | conditionally required | A supplementary note in the user's own words. Required when `desire=must`, because fit assessment shows the wording as a must-have condition |
| `note` | string | optional | A supplementary note |

A trait with `desire=must` is treated as a must-have condition, on equal footing with `conditions[level=must]`. Fit assessment's `must_condition_results` covers both, so the same condition is never registered twice, in two places.

### The count of must-have conditions

The rule "must-have conditions should stay to around 3" counts the **sum** of `conditions[level=must]` and `work_character_preferences[desire=must]`. A sum of 4 or more is a WARN.

### Handling of salary

A non-negotiable salary floor is placed in `conditions` (`axis=salary_condition`). The desired figure is placed in `salary.desired`. Job search uses the former as a threshold, and fit assessment's compensation dimension uses the latter. A WARN occurs when the floor exceeds the desired figure.

## company_score_axes (2.0)

A declaration of the axes and weights used to score a company (0 to 100 points). It is an optional array at the top level, valid only when `schema_version` is `2.0`. `1.0` and `1.1` have no such field, and it is never checked even when present.

The canonical definition of the 9 candidate quantitative axes, the conversion to a score, and the rule for distributing weight are in `job-change-company-research/references/company-score-rubric.md`. What is passed to company research is only the array of identifiers for axes whose `kind` is `quantitative`. `weight`, `thresholds`, and a qualitative axis's `label`, `definition`, and `judgment` are never passed. A qualitative axis's description is written by the user in their own words, and is never passed to an agent that has a web tool.

```json
"company_score_axes": [
  {
    "axis": "compensation_level",
    "kind": "quantitative",
    "weight": 40,
    "thresholds": {"zero": 4500000, "full": 7000000}
  },
  {"axis": "annual_holidays", "kind": "quantitative", "weight": 25},
  {
    "axis": "discretion",
    "kind": "qualitative",
    "weight": 35,
    "label": "裁量の大きさ",
    "definition": "設計方針を自分で決められること",
    "judgment": [
      {"score": 100, "condition": "求人票に設計裁量の記載があり、面接でも確認できた"},
      {"score": 50, "condition": "求人票に記載があるが未確認"},
      {"score": 0, "condition": "上位者の承認が必要と明記されている"}
    ]
  }
]
```

| Field | Type | Required / optional | Meaning and entry guidance |
|---|---|---|---|
| `axis` | string | required | The axis's identifier. Empty is an ERROR. The same axis appearing twice or more is also an ERROR. For a quantitative axis, it must be one of the 9 candidate quantitative axis keys in company-score-rubric.md; any other value is an ERROR. For a qualitative axis, it is an identifier the user assigns (lowercase ASCII letters, digits, underscores); any other character is an ERROR |
| `kind` | string | required | `quantitative` (an axis that converts a published number into a score with a linear formula) or `qualitative` (an axis whose judgement condition the user decides). Any other value is an ERROR |
| `weight` | integer | required | The weight, an integer from 1 to 100. Any other value is an ERROR. An ERROR occurs when the sum across every axis is not 100 |
| `thresholds` | object | optional, quantitative axes only | An override for the scoring standard. Holds both `zero` (the level equivalent to a score of 0) and `full` (the level equivalent to a score of 100) as numbers. Attaching it to a qualitative axis is an ERROR. An ERROR also occurs when `zero` or `full` is something other than a number, or when the two are equal |
| `label` | string | required for a qualitative axis | The name in the user's own words. Empty is an ERROR |
| `definition` | string | required for a qualitative axis | The definition of what counts as satisfying it, made concrete enough to judge. Empty is an ERROR |
| `judgment` | array | required for a qualitative axis | An array of judgement conditions. At least one entry is required. See below |
| `note` | string | optional | The reason the axis was chosen, written in the user's own words |

A quantitative axis with no `thresholds` uses a statistics-based default. The canonical definition of the default is a constant in `job-change-fit-assessment/scripts/calculate_company_score.py`, and this document does not repeat the number. An axis with no default is never scored until `thresholds` is written. The compensation level (`compensation_level`) has no default. The standard for this axis is decided from the user's current and desired salary.

### judgment (a qualitative axis)

Each entry represents one judgement condition.

| Field | Type | Required / optional | Meaning and entry guidance |
|---|---|---|---|
| `score` | integer | required | The score when the condition is met, an integer from 0 to 100. Any other value is an ERROR |
| `condition` | string | required | States what must be confirmed for the axis to receive that score. Empty is an ERROR |

List the entries in descending order of `score`, apply the conditions from the top, and take the first one that is met. A WARN occurs when the list is not in descending order. When no condition is met, the score is `null` (cannot be judged). Never place a guessed intermediate score.

A qualitative axis enters scoring only once `label`, `definition`, and `judgment` are all present. A matter for which a judgement condition cannot be written is never brought into scoring; it is passed on as an item to confirm at the job interview.

After distributing the weights, check the result by comparing two hypothetical companies. Score the two companies with the distributed weights, and confirm that the side with the higher score matches the answer to "which would actually be chosen?" (the procedure is in company-score-rubric.md).

A declared axis can conflict with a must-have condition in `job_change_axis` (`conditions[level=must]`) or with a work-characteristic desire level (`work_character_preferences`). When this happens, the skill never decides which one is true. Both are presented to the user, and the user chooses.

When the array is absent, it is treated as no declared scoring axis. No company score is calculated, and scoring never assumes an axis or a weight.

## targets

Target companies and roles. A WARN occurs when every category is empty.

| Field | Type | Meaning and entry guidance |
|---|---|---|
| `industries` | array | An array of strings naming the target industries |
| `roles` | array | An array of strings naming the target job types and positions |
| `companies` | array | An array of strings naming the target companies. The company-research sub-skill uses this as the starting point for creating a per-company directory |

## salary

Salary. The unit is yen.

| Field | Type | Meaning and entry guidance |
|---|---|---|
| `current` | number or null | Current salary |
| `desired` | number or null | Desired salary |

## Summary of the validation rules

`validate_axis.py` checks the following. A FAIL (exit code 1) occurs when even one ERROR is present. A PASS (exit code 0) occurs when there are zero ERRORs (a WARN is allowed). For a 1.x/2.0 profile.json, `validate_profile.py` runs these same checks as well as the career rules.

### ERROR (the axis does not stand as valid)

- Cannot be parsed as JSON, or the root is something other than an object
- `schema_version` is missing or empty, or is `3.0`
- `job_change_axis` is something other than an object
- `job_change_axis.reasons` is empty (no valid reason is present)

When `schema_version` is `2.0`, the following are also ERRORs.

- `conditions` is something other than an array, or is missing
- In `conditions[]`: a format mismatch or a duplicate in `id`, a `level` outside its value range, an empty `statement`, an `axis` outside its value range, an `operator` outside its value range, or a `verification` outside its value range
- `operator` is anything other than `qualitative` while `value` is `null`
- `unit` is present but is none of `yen`, `h_month`, `days_year`, `ratio`, or `none`
- `work_character_preferences` is something other than an array, or is missing
- `work_character_preferences` does not hold exactly the 8 traits (a missing entry, a duplicate, or an unknown `trait`)
- `desire` is outside its value range, or `desire=must` while `statement` is empty
- `company_score_axes` is present but is something other than an array, or an entry in it is something other than an object
- `company_score_axes[].axis` is empty or duplicated, `kind` is outside its value range, or the `axis` of an entry whose `kind` is `quantitative` is not one of the 9 candidate quantitative axes
- The `axis` of an entry whose `kind` is `qualitative` contains a character other than a lowercase ASCII letter, a digit, or an underscore
- `weight` is something other than an integer from 1 to 100, or the sum of `weight` is not 100
- An entry whose `kind` is `qualitative` has `thresholds`, `zero` or `full` is something other than a number, or `zero` and `full` are equal
- For an entry whose `kind` is `qualitative`: `label` or `definition` is empty, `judgment` is something other than an array of at least one entry, `judgment[].score` is outside its value range, or `judgment[].condition` is empty

### WARN (the axis stands as valid, but a shortage of information lowers the quality of downstream output)

- `targets` is missing, or every category of `targets` is empty
- `updated_at` is missing
- `schema_version` is a version other than the known axis versions (`1.0`, `1.1`, `2.0`)
- `schema_version` is `1.0` or `1.1` (migration to 2.0 is recommended)
- `salary.current` or `salary.desired` is neither a number nor null
- The count of must-have conditions is 4 or more (the count of `must_conditions` in 1.x; the sum of `conditions[level=must]` and `work_character_preferences[desire=must]` in 2.0)

When `schema_version` is `2.0`, the following are also WARNs.

- No `level=must` entry exists in `conditions` (with no must-have condition, job-search filtering has nothing to work from)
- More than one `level=must` condition exists for the same `axis` (judgement adopts the strictest threshold)
- A `level=must` condition has no `priority`, or `priority` values are duplicated
- `must_conditions` or `want_conditions` remains non-empty (a migration was missed)
- The must-have salary floor exceeds `salary.desired`
- `company_score_axes` is an empty array (no scoring axis has been chosen)
- `company_score_axes` has no `compensation_level` (an axis that is selected by default)
- `judgment` is not sorted in descending order of `score`

## Version and migration

The axis has its own version line (`1.0`, `1.1`, `2.0`). Only profile.json moves to `3.0`; axis.json never carries `3.0`.

| `schema_version` | Handling |
|---|---|
| `1.0` / `1.1` | Only the legacy validation rules apply. The absence of `conditions` or `work_character_preferences` is never checked, and `company_score_axes` is never checked either. One WARN urging migration is issued |
| `2.0` | The 2.0 rules above apply together with the legacy rules |

**A 1.x axis passes validation as it stands.** Staying on 1.x, however, puts downstream sub-skills into fallback behaviour.

| Skill | Behaviour under 1.x |
|---|---|
| `job-change-job-search` | Job observation proceeds as normal, but with the 8-axis judgement unavailable, every posting is classified as `needs_more_research`（追加調査候補）, and the overall judgement is set to 「判定不能」 (cannot be judged) |
| `job-change-fit-assessment` | Sets the score for work-characteristic match and aspiration match to `null` (「判断保留」, judgement withheld), and writes the reason into `verdict`. Without a declared scoring axis, the company score is not calculated either |

**Moving a 1.x axis to 2.0 is a conversation with the user.** Mechanically mapping a free-text condition such as 「モダンな技術スタックが整備されていること」 ("a modern technology stack is in place") onto an axis, an operator, and a threshold is a guess. Such a guess runs against the principle of never fabricating a fact. The conversation happens in `job-change-axis` ("Migration from 1.x" in its `references/sections/conditions.md`), and only then is `schema_version` of axis.json rewritten to `2.0`.

## Splitting a 1.x/2.0 profile.json

A profile.json at `1.0`, `1.1` or `2.0` holds the career record and the axis together. Skills read such a file as it stands (it serves as both `{PROFILE}` and `{AXIS}`, and each validator checks its own part). A skill that writes through a writer role splits it first and then writes to the new layout:

```bash
python {HUB_SKILL_DIR}/scripts/split_profile.py {PROFILE}
python {HUB_SKILL_DIR}/scripts/split_profile.py {PROFILE} --json
```

- The script accepts a profile.json whose `schema_version` is the string `1.0`, `1.1` or `2.0`, and refuses every other value (exit 1), a `3.0` file included. It also refuses when `axis.json`, the backup `profile.json.bak-{version}` or the work file `profile.json.tmp` already exists beside the input.
- It writes, in order: the backup `profile.json.bak-{version}`, then `axis.json`, then profile.json replaced atomically. When a write fails, it removes the files it created and leaves profile.json as it was.
- axis.json receives `job_change_axis`, `company_score_axes`, `targets`, `salary`, the source `schema_version` and `updated_at`. Every other key stays in profile.json, whose `schema_version` becomes `3.0`. A key outside the known lists is named in the report (`unknown_keys`).
- The move copies values unchanged, so validator findings on either output are reported (`profile_validation`, `axis_validation`) and the split still completes. An unfinished axis can be split and completed afterwards in `job-change-axis`.

After the split, the skill tells the user the backup path from the report (`backup`). The split leaves the axis version as it was; moving a 1.x axis to 2.0 stays the conversation described above.
