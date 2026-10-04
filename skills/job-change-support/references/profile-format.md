# profile.json specification

This is the canonical definition of profile.json, the user profile, within the job-change-support family of skills. The code of `scripts/validate_profile.py` follows this specification exactly.

profile.json is the canonical source of the user's career record for the job-change support family of skills: basic information, career history, achievements, skills, and strengths. The job-change axis (reasons, conditions, work-character preferences, scoring axes, targets, salary) is in axis.json, defined in `references/axis-format.md`. Every downstream sub-skill (application-document writing, self-analysis, job search, fit assessment, interview preparation) refers to this profile.json. The same information is held in one place only. `job-change-profile` is the one skill that writes profile.json. `strengths` enters through it on the hand-off from `job-change-self-analysis`.

## Location

- Where the canonical file is stored: `{DATA_ROOT}/career-private/profile.json`
- User data is never placed in the skill's own folder (`skills/job-change-support/`). `assets/profile_example.json` is a fictitious filled-in example.

## Root structure

```json
{
  "schema_version": "3.0",
  "updated_at": "2026-07-12",
  "summary": "",
  "basic": { },
  "career_history": [ ],
  "career_gaps": [ ],
  "skills": { },
  "strengths": [ ],
  "notes": ""
}
```

| Field | Type | Required / optional | Meaning and entry guidance |
|---|---|---|---|
| `schema_version` | string | required | The specification version. The current version is `"3.0"`. `"1.0"`, `"1.1"` and `"2.0"` can also be read (see "Reading older versions" below). Missing is an ERROR |
| `updated_at` | string | optional | The date of the last update, in `YYYY-MM-DD` format. Rewrite it on every update. Missing is a WARN |
| `summary` | string | optional | A summary of the work history. Shows the overall picture of the experience in 3 to 4 sentences |
| `basic` | object | required | Basic information. See below |
| `career_history` | array | required | An array of work-history entries. At least one entry is required. See below |
| `career_gaps` | array | optional | An array of explanations for gap periods. See below |
| `skills` | object | optional | Skills held. A WARN occurs when every category is empty. See below |
| `strengths` | array | optional | A list of short statements of strength, used as material for self-promotion in application documents and job interviews. Deepening these with grounding in behavioural evidence and feedback from others can be done in `job-change-self-analysis` (the canonical definition is that skill's `self_analysis.json`; only the short statements are reflected back here) |
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

When the user held more than one job in the same period (a concurrent post, a secondment, a side business, self-employment), each one is recorded as its own entry. An overlap in `period` is allowed. An overlap is valid. The `role` field distinguishes which capacity the user held, such as 「バックエンドエンジニア」(Backend Engineer) and 「業務委託（副業）」(contract work, side business).

| Field | Type | Required / optional | Meaning and entry guidance |
|---|---|---|---|
| `company` | string | required | The name of the company the user worked for (the employer). Missing is an ERROR |
| `period` | string | required | The period of employment, in `YYYY-MM〜YYYY-MM` format. For a current job, use `〜現在` ("to present"). Missing is an ERROR |
| `role` | string | required | The role or title held. Missing is an ERROR |
| `employment_type` | string | optional | The employment type (regular employee, contract employee, temporary staffing, contract work, officer, self-employed, and so on). Write it in the user's own words. Leave it out when there is no record of it |
| `assignment` | string | optional | A place of work separate from the employer, such as an on-site client, a staffing placement, a secondment destination, a main client, or an overseas location. Used for temporary staffing, SES (system engineering service) contracts, contract work, and secondments. Write the employer in `company`, and separate the place of work into this field |
| `note` | string | optional | A supplementary note the user stated themselves, such as a leave period during employment or the circumstances of leaving. Never write anything the user did not state |
| `responsibilities` | array | optional | An array of strings describing the duties held |
| `achievements` | array | optional | An array of achievements. See below |

`employment_type`, `assignment`, and `note` fall outside what `validate_profile.py` checks. The canonical definition of how to record a non-standard career history (temporary staffing, contract work, secondment, a leave period, and so on) is in `references/answer-handling.md` of `job-change-profile`.

### achievements

Each entry represents one achievement.

| Field | Type | Required / optional | Meaning and entry guidance |
|---|---|---|---|
| `description` | string | optional | A description of the achievement |
| `metric` | string or null | optional | A quantitative value, shown as a number, a percentage, or a monetary amount, such as 「応答時間を40%短縮」(cut response time by 40%) or 「売上を年3000万円増」(increased sales by 30 million yen a year). An achievement that cannot be quantified is set to `null` |
| `project` | string | optional | The name of the project or engagement. Used to distinguish which project an achievement belongs to, when more than one project ran in parallel at the same job. Leave it out for a job with only one project |
| `period` | string | optional | The period of that project, in `YYYY-MM〜YYYY-MM` format. For an ongoing project, use `〜現在`. It falls within the employment period. Leave it out for a job with only one project |

Fill `metric` with a quantitative value wherever possible. `validate_profile.py` issues a WARN when no quantitative `metric` exists across the whole work history. Write the number the user stated, exactly as stated, into `metric`.

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

## Summary of the validation rules

`validate_profile.py` checks the following. A FAIL (exit code 1) occurs when even one ERROR is present. A PASS (exit code 0) occurs when there are zero ERRORs (a WARN is allowed).

```bash
python {HUB_SKILL_DIR}/scripts/validate_profile.py {PROFILE}
python {HUB_SKILL_DIR}/scripts/validate_profile.py {PROFILE} --json
```

### ERROR (the profile does not stand as valid)

- Cannot be parsed as JSON, or the root is something other than an object
- `schema_version` is missing or empty
- `basic.current_role` is missing or empty
- `career_history` is empty, or any entry is missing or has an empty `company`, `period`, or `role`

### WARN (the profile stands as valid, but a shortage of information lowers the quality of downstream output)

- No quantitative `metric` (the `metric` of an achievement) exists across the whole work history
- Every category of `skills` is empty
- `updated_at` is missing
- `schema_version` is a version other than the known ones (`1.0`, `1.1`, `2.0`, `3.0`)
- `career_history[].period` is not in `YYYY-MM〜YYYY-MM` or `YYYY-MM〜現在` format
- When every `career_history[].period` can be parsed, a gap of 6 months or longer falls outside every work-history entry's period, and no corresponding `career_gaps` entry (with an overlapping period) exists
- An entry in `skills.languages` is something other than an object holding `{"language","level"}`
- A format mismatch in `career_gaps[].period`, or `explanation` missing or empty
- `skills.portable[].category` is anything other than "対課題" or "対人"
- In a `3.0` file, an axis key (`job_change_axis`, `company_score_axes`, `targets`, `salary`) is present. Those keys belong in axis.json

## Reading older versions

| `schema_version` | What the file holds | Handling |
|---|---|---|
| `3.0` | The career record alone (the keys above) | The rules above apply |
| `1.0` / `1.1` / `2.0` | The career record and the job-change axis in one file | `validate_profile.py` validates the whole file: the rules above plus every axis rule of `references/axis-format.md` (an empty `job_change_axis.reasons` is then an ERROR). The file serves as both `{PROFILE}` and `{AXIS}` until it is split |

Skills read a 1.x/2.0 file as it stands. A skill that writes through a writer role splits it first with `split_profile.py`, which leaves a 3.0 profile.json and an axis.json beside it and keeps a backup. The procedure and the rule for an axis.json found beside a 1.x/2.0 profile.json are in "Splitting a 1.x/2.0 profile.json" and "Location" of `references/axis-format.md`.
