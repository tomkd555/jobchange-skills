# profile.json specification

This is the canonical definition of profile.json, the user profile, within the job-change-support family of skills. The implementation of `scripts/validate_profile.py` follows this specification exactly.

profile.json is the "single canonical source of user data" for the job-change support family of skills. It gathers career history, skills, job-change axes, and target companies into one place. Every downstream sub-skill (company research, application-document writing, interview preparation, exam preparation) refers to this profile.json. The same information is never held in more than one place.

## Location

- Where the canonical file lives: `{DATA_ROOT}/career-private/profile.json`
- User data is never placed in the skill's own folder (`skills/job-change-support/`). `assets/profile_example.json` is a fictitious filled-in example.

## Root structure

```json
{
  "schema_version": "2.0",
  "updated_at": "2026-07-12",
  "summary": "",
  "basic": { },
  "career_history": [ ],
  "career_gaps": [ ],
  "skills": { },
  "strengths": [ ],
  "job_change_axis": { },
  "company_score_axes": [ ],
  "targets": { },
  "salary": { },
  "notes": ""
}
```

| Field | Type | Required / optional | Meaning and entry guidance |
|---|---|---|---|
| `schema_version` | string | required | The specification version. The current version is `"2.0"`. `"1.0"` and `"1.1"` can also be read (see "Version and migration" below). Missing is an ERROR |
| `updated_at` | string | optional | The date of the last update, in `YYYY-MM-DD` format. Rewrite it on every update. Missing is a WARN |
| `summary` | string | optional | A summary of the work history. Shows the overall picture of the experience in 3 to 4 sentences |
| `basic` | object | required | Basic information. See below |
| `career_history` | array | required | An array of work-history entries. At least one entry is required. See below |
| `career_gaps` | array | optional | An array of explanations for gap periods. See below |
| `skills` | object | optional | Skills held. A WARN occurs when every category is empty. See below |
| `strengths` | array | optional | A list of short statements of strength, used as material for self-promotion in application documents and job interviews. Deepening these with grounding in behavioural evidence and feedback from others can be done in `job-change-self-analysis` (the canonical definition is that skill's `self_analysis.json`; only the short statements are reflected back here) |
| `job_change_axis` | object | required | The job-change axes. See below |
| `company_score_axes` | array | optional, 2.0 only | A declaration of the axes and weights used to score a company. Valid only when `schema_version` is `2.0`. See below |
| `targets` | object | optional | Target companies and roles. A WARN occurs when every category is empty. See below |
| `salary` | object | optional | Salary. See below |
| `notes` | string | optional | Supplementary notes, such as points to watch during the selection process |

## basic

Basic information.

| Field | Type | Required / optional | Meaning and entry guidance |
|---|---|---|---|
| `current_role` | string | required | The role or title at the current job. Missing is an ERROR |
| `years_of_experience` | number | optional | Total years of hands-on work experience |
| `location` | string | optional | Place of residence (prefecture-level detail is sufficient) |
| `education` | array | optional | An array of education strings, ordered most recent first |

## career_history

An array of work-history entries. At least one entry is required. Put the most recent job first. Each entry has the following fields.

When the user held more than one job at the same time (a concurrent post, a secondment, a side business, self-employment), each one is held as its own entry, and an overlap in `period` is allowed. An overlap is valid. Which capacity the user held is distinguished in `role` — for example, 「バックエンドエンジニア」(Backend Engineer) and 「業務委託（副業）」(contract work, side business).

| Field | Type | Required / optional | Meaning and entry guidance |
|---|---|---|---|
| `company` | string | required | The name of the company the user worked for (the employer). Missing is an ERROR |
| `period` | string | required | The period of employment, in `YYYY-MM〜YYYY-MM` format. For a current job, use `〜現在` ("to present"). Missing is an ERROR |
| `role` | string | required | The role or title held. Missing is an ERROR |
| `employment_type` | string | optional | The employment type (regular employee, contract employee, temporary staffing, contract work, officer, self-employed, and so on). Write it in the user's own words. Leave it out when there is no record of it |
| `assignment` | string | optional | A place of work separate from the employer — an on-site client, a staffing placement, a secondment destination, a main client, an overseas location, and so on. Used for temporary staffing, SES (system engineering service) contracts, contract work, and secondments. Write the employer in `company`, and separate the place of work into this field |
| `note` | string | optional | A supplementary note the user stated themselves, such as a leave period during employment or the circumstances of leaving. Never write anything the user did not state |
| `responsibilities` | array | optional | An array of strings describing the duties held |
| `achievements` | array | optional | An array of achievements. See below |

`employment_type`, `assignment`, and `note` fall outside what `validate_profile.py` checks. The canonical definition of how to record a non-standard career history (temporary staffing, contract work, secondment, a leave period, and so on) lives in `references/answer-handling.md` of `job-change-profile`.

### achievements

Each entry represents one achievement.

| Field | Type | Required / optional | Meaning and entry guidance |
|---|---|---|---|
| `description` | string | optional | A description of the achievement |
| `metric` | string or null | optional | A quantitative value, shown as a number, a percentage, or a monetary amount, such as 「応答時間を40%短縮」(cut response time by 40%) or 「売上を年3000万円増」(increased sales by 30 million yen a year). An achievement that cannot be quantified is set to `null` |
| `project` | string | optional | The name of the project or engagement. Used to distinguish which project an achievement belongs to, when more than one project ran in parallel at the same job. Leave it out for a job with only one project |
| `period` | string | optional | The period of that project, in `YYYY-MM〜YYYY-MM` format. For an ongoing project, use `〜現在`. It falls within the employment period. Leave it out for a job with only one project |

Fill `metric` with a quantitative value wherever possible. `validate_profile.py` issues a WARN when not a single quantitative `metric` exists across the whole work history. Write the number the user stated, exactly as stated, into `metric`.

`project` and `period` are optional, and `validate_profile.py` does not check them. Matching them against the interview notes is confirmed by the auditor (`job-change-profile-auditor`).

## career_gaps

An array of explanations for gap periods (6 months or longer, and not covered by any work-history entry's period). Each entry has the following fields.

| Field | Type | Required / optional | Meaning and entry guidance |
|---|---|---|---|
| `period` | string | required | The gap period, in `YYYY-MM〜YYYY-MM` format. A format mismatch or a missing value is a WARN |
| `explanation` | string | required | The reason for the gap period. Missing or empty is a WARN |
| `activities` | array | optional | An array of strings describing activities carried out during the period |

`validate_profile.py` issues a WARN when a period of 6 months or longer falls outside every work-history entry's period, and no corresponding `career_gaps` entry states it. This check runs only when every `career_history[].period` can be parsed. The judgement runs against the union of every work-history period, so an overlap between work-history entries never causes a false gap detection.

## skills

Skills held, grouped by category. A WARN occurs when every category is empty.

| Field | Type | Meaning and entry guidance |
|---|---|---|
| `technical` | array | An array of technical-skill strings (languages, frameworks, cloud platforms, and so on) |
| `business` | array | An array of business-skill strings (management, requirements definition, and so on) |
| `languages` | array | An array of languages. Each entry has the form `{"language": "英語", "level": "TOEIC 850"}`. A format mismatch is a WARN |
| `certifications` | array | An array of strings listing certifications held |
| `portable` | array | An array of portable skills. Each entry has the form `{"skill": string, "category": "対課題" または "対人", "note": string（任意）}`. The Ministry of Health, Labour and Welfare's 9 elements of portable skill (5 for how the work is done, 4 for how the person relates to others) are used as an auxiliary classification. A `category` other than "対課題" or "対人" is a WARN |

## job_change_axis

The job-change axes. Holds the reason for changing jobs, the must-have conditions, and the nice-to-have conditions separately. This is the foundation for consistency between the statement of motivation in the application documents and the job interview.

| Field | Type | Required / optional | Meaning and entry guidance |
|---|---|---|---|
| `reasons` | array | required | An array of strings giving the reasons for the job change. At least one entry is required (empty is an ERROR). Write these as what the user wants to achieve next. Deepening these into a constructive rephrasing can be done in `job-change-self-analysis` (the canonical definition is `reason_for_change` in that skill's `self_analysis.json`; only the short statements are reflected back here) |
| `conditions` | array | **required in 2.0** | An array of conditions. Holds must-have and nice-to-have conditions structured as an axis, an operator, and a threshold. See below |
| `work_character_preferences` | array | **required in 2.0** | The desire level for each of the 8 work characteristics. Holds exactly 8 entries, no more and no fewer. See below |
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
| `axis` | string or null | required | Either one of the 8 axis ids in `references/screening-axes.md`, or `null` (a qualitative condition that fits none of the 8 axes). Any other value is an ERROR |
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

Gives each of the 8 work characteristics a desire level. **Exactly 8 entries** are required, no more and no fewer (a missing or duplicate entry is an ERROR). Requiring "not needed" to be stated explicitly distinguishes a blank entry from indifference. The definition of the trait ids lives in `references/screening-axes.md`.

| Field | Type | Required / optional | Meaning and entry guidance |
|---|---|---|---|
| `trait` | string | required | One of the 8 trait ids. A value outside the defined set, a duplicate, or a missing value is an ERROR |
| `desire` | string | required | `must` (passes on the job if not met), `important` (given weight), `neutral` (no preference either way), or `not_required` (not needed). Any other value is an ERROR |
| `statement` | string | conditionally required | A supplementary note in the user's own words. Required when `desire=must`, because fit assessment surfaces the wording as a must-have condition |
| `note` | string | optional | A supplementary note |

A trait with `desire=must` is treated as a must-have condition, on equal footing with `conditions[level=must]`. Fit assessment's `must_condition_results` covers both, so the same condition is never registered twice, in two places.

### The count of must-have conditions

The rule "must-have conditions should stay to around 3" counts the **sum** of `conditions[level=must]` and `work_character_preferences[desire=must]`. A sum of 4 or more is a WARN.

### Handling of salary

A non-negotiable salary floor is placed in `conditions` (`axis=salary_condition`); the desired figure is placed in `salary.desired`. The former is used as a threshold by job search; the latter is used by fit assessment's compensation dimension. A WARN occurs when the floor exceeds the desired figure.

## company_score_axes (2.0)

A declaration of the axes and weights used to score a company (0 to 100 points). It is an optional array at the top level, valid only when `schema_version` is `2.0`. `1.0` and `1.1` have no such field, and it is never checked even when present.

The canonical definition of the 9 candidate quantitative axes, the conversion to a score, and the rule for distributing weight lives in `job-change-company-research/references/company-score-rubric.md`. What is passed to company research is only the array of identifiers for axes whose `kind` is `quantitative`. `weight`, `thresholds`, and a qualitative axis's `label`, `definition`, and `judgment` are never passed. A qualitative axis's description is written by the user in their own words, and is never passed to an agent that holds a web tool.

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
| `thresholds` | object | optional, quantitative axes only | An override for the scoring standard. Holds both `zero` (the level equivalent to a score of 0) and `full` (the level equivalent to a score of 100) as numbers. Attaching it to a qualitative axis is an ERROR. An ERROR also occurs when `zero` or `full` is not a number, or when the two are equal |
| `label` | string | required for a qualitative axis | The name in the user's own words. Empty is an ERROR |
| `definition` | string | required for a qualitative axis | The definition of what counts as satisfying it, made concrete enough to judge. Empty is an ERROR |
| `judgment` | array | required for a qualitative axis | An array of judgement conditions. At least one entry is required. See below |
| `note` | string | optional | The reason the axis was chosen, written in the user's own words |

A quantitative axis with no `thresholds` uses a statistics-based default. The canonical definition of the default lives in a constant in `job-change-fit-assessment/scripts/calculate_company_score.py`; this document holds no number. An axis with no default is never scored until `thresholds` is written. The compensation level (`compensation_level`) has no default; the standard for this axis is decided from the user's current and desired salary.

### judgment (a qualitative axis)

Each entry represents one judgement condition.

| Field | Type | Required / optional | Meaning and entry guidance |
|---|---|---|---|
| `score` | integer | required | The score when the condition is met, an integer from 0 to 100. Any other value is an ERROR |
| `condition` | string | required | States what must be confirmed to earn that score. Empty is an ERROR |

List the entries in descending order of `score`, apply the conditions from the top, and take the first one that is met. A WARN occurs when the list is not in descending order. When no condition is met, the score is `null` (cannot be judged); never place a guessed intermediate score.

A qualitative axis enters scoring only once `label`, `definition`, and `judgment` are all present. A matter for which a judgement condition cannot be written is never brought into scoring; it is passed on as an item to confirm at the job interview.

After distributing the weights, check the result by comparing two hypothetical companies. Score the two companies with the distributed weights, and confirm that the side with the higher score matches the answer to "which would actually be chosen?" (the procedure lives in company-score-rubric.md).

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

`validate_profile.py` checks the following. A FAIL (exit code 1) occurs when even one ERROR is present; a PASS (exit code 0) occurs when there are zero ERRORs (a WARN is allowed).

### ERROR (the profile does not stand as valid)

- Cannot be parsed as JSON
- `schema_version` is missing or empty
- `basic.current_role` is missing or empty
- `career_history` is empty, or any entry is missing or has an empty `company`, `period`, or `role`
- `job_change_axis.reasons` is empty (not a single valid reason is present)

When `schema_version` is `2.0`, the following are also ERRORs.

- `conditions` is not an array, or is missing
- In `conditions[]`: a format mismatch or a duplicate in `id`, a `level` outside its value range, an empty `statement`, an `axis` outside its value range, an `operator` outside its value range, or a `verification` outside its value range
- `operator` is anything other than `qualitative` while `value` is `null`
- `unit` is present but is none of `yen`, `h_month`, `days_year`, `ratio`, or `none`
- `work_character_preferences` is not an array, or is missing
- `work_character_preferences` does not hold exactly the 8 traits (a missing entry, a duplicate, or an unknown `trait`)
- `desire` is outside its value range, or `desire=must` while `statement` is empty
- `company_score_axes` is present but is not an array, or an entry in it is not an object
- `company_score_axes[].axis` is empty or duplicated, `kind` is outside its value range, or the `axis` of an entry whose `kind` is `quantitative` is not one of the 9 candidate quantitative axes
- The `axis` of an entry whose `kind` is `qualitative` contains a character other than a lowercase ASCII letter, a digit, or an underscore
- `weight` is not an integer from 1 to 100, or the sum of `weight` is not 100
- An entry whose `kind` is `qualitative` has `thresholds`, `zero` or `full` is not a number, or `zero` and `full` are equal
- For an entry whose `kind` is `qualitative`: `label` or `definition` is empty, `judgment` is not an array of at least one entry, `judgment[].score` is outside its value range, or `judgment[].condition` is empty

### WARN (the profile stands as valid, but a shortage of information lowers the quality of downstream output)

- Not a single quantitative `metric` (the `metric` of an achievement) exists across the whole work history
- Every category of `skills` is empty
- Every category of `targets` is empty
- `updated_at` is missing
- `schema_version` is a version other than the known ones (`1.0`, `1.1`, `2.0`)
- `schema_version` is `1.0` or `1.1` (migration to 2.0 is recommended)
- `career_history[].period` is not in `YYYY-MM〜YYYY-MM` or `YYYY-MM〜現在` format
- When every `career_history[].period` can be parsed, a gap of 6 months or longer falls outside every work-history entry's period, and no corresponding `career_gaps` entry (with an overlapping period) exists
- An entry in `skills.languages` is not an object holding `{"language","level"}`
- `salary.current` or `salary.desired` is neither a number nor null
- The count of must-have conditions is 4 or more (the count of `must_conditions` in 1.x; the sum of `conditions[level=must]` and `work_character_preferences[desire=must]` in 2.0)
- A format mismatch in `career_gaps[].period`, or `explanation` missing or empty
- `skills.portable[].category` is anything other than "対課題" or "対人"

When `schema_version` is `2.0`, the following are also WARNs.

- Not a single `level=must` entry exists in `conditions` (with no must-have condition, job-search filtering has nothing to work from)
- More than one `level=must` condition exists for the same `axis` (judgement adopts the strictest threshold)
- A `level=must` condition has no `priority`, or `priority` values are duplicated
- `must_conditions` or `want_conditions` remains non-empty (a migration was missed)
- The must-have salary floor exceeds `salary.desired`
- `company_score_axes` is an empty array (not a single scoring axis has been chosen)
- `company_score_axes` has no `compensation_level` (an axis that is selected by default)
- `judgment` is not sorted in descending order of `score`

## Version and migration

| `schema_version` | Handling |
|---|---|
| `1.0` / `1.1` | Only the legacy validation rules apply. The absence of `conditions` or `work_character_preferences` is never checked, and `company_score_axes` is never checked either. One WARN urging migration is issued |
| `2.0` | The 2.0 rules above apply in addition to the legacy rules |

**A 1.x profile passes validation as it stands.** Staying on 1.x, however, puts downstream sub-skills into fallback behaviour.

| Skill | Behaviour under 1.x |
|---|---|
| `job-change-job-search` | Job observation proceeds as normal, but with the 8-axis judgement unavailable, every posting is classified as `needs_more_research`（追加調査候補）, and the overall judgement is set to 「判定不能」 (cannot be judged) |
| `job-change-fit-assessment` | Sets the score for work-characteristic match and aspiration match to `null` (「判断保留」, judgement withheld), and writes the reason into `verdict`. With no declared scoring axis, no company score is calculated either |

**No automatic migration is performed.** Mechanically mapping a free-text condition (for example, 「モダンな技術スタックが整備されていること」— "a modern technology stack is in place") onto an axis, an operator, and a threshold is a guess, and runs against the principle of never fabricating a fact. Migration happens through a conversation in `job-change-profile` (the "Structured conditions" (`conditions`) section; match the label in job-change-profile/references/sections.md).
