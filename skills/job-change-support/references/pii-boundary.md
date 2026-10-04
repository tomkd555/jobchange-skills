# The canonical definition of the personal information boundary (pii-boundary)

This is the canonical definition of the boundary that keeps the user's personal information from reaching a role that has a means of sending data to the web. The hub and every sub-skill refer to this file.

| Referrer | What it is used for |
|---|---|
| `job-change-support` | Routing to each sub-skill, and narrowing the axes passed to company research |
| `job-change-profile` / `job-change-axis` / `job-change-self-analysis` | Deciding which role may create or update files under `career-private/` |
| `job-change-company-research` / `job-change-job-search` / `job-change-exam-prep` | Deciding what material may be passed to a role that has a means of sending data to the web |
| `job-change-documents` / `job-change-interview-prep` / `job-change-fit-assessment` | Deciding where personal information and its derived values are stored, and to whom they are passed |

The enumeration of targets, the exceptions, and the permission for each role live here alone, and are never duplicated into a referrer. A referrer's SKILL.md states only the principle (personal information is never used for external transmission) and the consequences specific to that skill.

The role prompts (`agents/*.md` and `skills/*/references/roles/*.md`) are the one exception: they contain the substance of the principle verbatim. A role prompt travels alone to a sub-agent, and the sub-agent may not be able to open this file. `job-change-posting-parser`, for one, holds only `WebFetch` and `WebSearch` in its `tools`, has no `Read`, and cannot open a reference. This duplication is intentional; when this file changes, update every role prompt in the same change.

## Boundary principle (the wide enumeration)

Treat the following as personal information, and never use any of it for external transmission of any kind, including search queries, fetches, and external API calls.

### Fields of profile.json and axis.json

- `profile.json` (the career record): the name, place of residence and education. The name of the company where the user works or has worked (`career_history[].company`) and the achievements (including the quantitative values in `career_history[].achievements`) are covered too.
- `axis.json` (the job-change axis): the current salary (`salary.current`), the desired salary (`salary.desired`), the conditions in `job_change_axis`, and the `weight`, `thresholds`, and qualitative axes of `company_score_axes`. These represent the user's own judgement and circumstances.

A 1.x or 2.0 `profile.json` holds both sets of fields in one file. Every field in both lists is covered there.

### Files under career-private/

Everything under `{DATA_ROOT}/career-private/` is treated as personal information, both its path and its content.

| File | Why it is personal information |
|---|---|
| `profile.json` | The canonical record of career history and name |
| `axis.json` | The canonical job-change axis: reasons, conditions, salary, and scoring axes |
| `profile.json.bak-{version}` | The backup of a 1.x or 2.0 profile that `split_profile.py` leaves; it holds both the career record and the axis |
| `profile_interview_notes.md` | The raw record of the elicitation interview for both the career record and the axis |
| `documents/` | Generic application documents written before a target company exists; their body text draws on `profile.json` |
| `self_analysis.json` | Behavioural episodes, feedback from others, and values |
| `company_index.json` | The list of target companies reveals the user's own preferences |
| `commute.json` | Commute time implies place of residence |
| `fit/{company slug}/fit_assessment.json` | A value derived from the profile, self-analysis, and commute |
| `fit/{company slug}/time_analysis.json` | A value derived from salary, working hours, and commute time |
| `fit/{company slug}/sources.json` | Source metadata for the figures used to calculate a derived value |
| `fit/{company slug}/qualitative_judgment.json` | The result of applying the judgement conditions the user wrote in their own words |
| `fit/current/time_analysis.json` | Committed time and effective hourly wage at the current job |

A derived value stays inside the same boundary as the source it came from. A value calculated from personal information is personal information, even though it is the result of a calculation.

### The boundary is defined by the role's web tools

Splitting the world into "`career-private/` holds personal information, `companies/` and `job-search/` do not" fails to describe reality. The substance of the boundary is that a role with a means of sending data to the web never receives the path or the content of personal information. The name of a tree is only a rough guide for that judgement.

Under `companies/{company slug}/`, the following artifacts contain personal information. Every one stays inside the boundary, because neither the role that writes it nor the role that reads it has a means of sending data to the web.

| File | Why it is personal information | Role that reads and writes it |
|---|---|---|
| Application documents under `documents/` | The body text draws career history and achievements from `profile.json` | `job-change-document-writer` / `job-change-document-auditor` |
| `documents/appeal-mapping.md` | A mapping between job requirements and the achievements in `profile.json` | same as above |
| `documents/tailoring-rationale.md` | Which achievements were chosen, and why | same as above |
| `interview_answers.json` | A verbatim transcript of the user's answers, with no summarising or paraphrasing | `job-change-interview-coach` |
| `interview_evaluation.json` | An evaluation of the answers, with references to its basis | same as above |
| `interview_notes_user.md` | What the user learned about that company's job interview from a recruiting agent or a past selection process, including the course of the user's own selection process | same as above |
| `interview_questions.json` | Anticipated questions built from the profile and `interview_notes_user.md`; `basis` points to the relevant part of the profile | same as above |
| `interview-prep-report.md` | A summary evaluation of the answers | same as above |

`companies/{company slug}/company_research.json`, `companies/{company slug}/exam_assessment.json`, `companies/{company slug}/interview_intel.json`, and everything under `job-search/{search ID}/` are read and written by roles that have a means of sending data to the web: `job-change-company-researcher`, `job-change-research-auditor`, `job-change-exam-scout`, `job-change-interview-scout`, and `job-change-job-searcher`. Personal information and its derived values are never written there. For the files with personal information that sit in the same `companies/{company slug}/` tree (the table above), the role prompts for these roles list the files and instruct the role not to read them. The same reasoning limits where a fit-assessment derived value is stored, to under `career-private/fit/{company slug}/` alone.

`_manifest.json` never contains personal information or its derived values either. The specification for the items it records is in `freshness-policy.md`.

## Exceptions

Only the following two cases may cross the boundary to a role with a means of sending data to the web. These two cases are the only exceptions.

### An anonymised condition sheet (including the floor of the desired salary)

An anonymised condition sheet may be passed as the search condition for a job search. The condition sheet may hold the following items.

- job type
- industry
- the work location at the level of a prefecture or municipality, plus any rail line or station name the user wrote in their own words
- remote-work policy
- employment type
- the floor of the desired salary (`salary_min`)
- the ID of the improvement axis the user chose in similar_better (`improvement_axes`)
- the key names and reasons for any condition excluded from the exploration set

A job search is a procedure built on these as its axes, and this range of information alone cannot identify the individual.

The condition sheet never holds the following items.

- the current salary (`salary.current`)
- a threshold such as an overtime ceiling, a floor on annual holidays, or a preference on work characteristics
- the station name derived from `commute.json`
- the assessment tier of a past search result

Once both the current salary and the desired salary are present, there is enough information to infer the company the user works for. A threshold is the user's own condition, and by itself represents the individual.

`job-change-job-search` is the one that uses this exception. The paths and contents of `profile.json` and `axis.json` stay with the caller.

### The identifiers of the quantitative axes in company_score_axes

When starting company research (`job-change-company-research`), only the array of identifiers for the axes in `company_score_axes` whose `kind` is `quantitative` may be passed, such as `["compensation_level", "monthly_overtime", "annual_holidays"]`. The caller reads `company_score_axes` from `{AXIS}` (resolved by "Location" in `axis-format.md`) and passes the array alone. The path of the axis file stays with the caller. This array contains no personal name, no name of the user's employer, and no current salary. `weight` and `thresholds` are never passed: the weight and the standard are the user's own judgement, and gathering facts on the company side does not need them. When there is no `company_score_axes`, the caller does not pass any axis when starting research.

A qualitative axis (`kind` is `qualitative`) is never passed, because it holds a `label`, `definition`, and `judgment` the user wrote in their own words. Judgement on a qualitative axis is made by fit assessment, which does not have a web tool, working from the facts company research has gathered and from the job posting. When a qualitative axis needs further investigation from company research, the caller gives it to company research as a focus point, in the user's own words.

## The three items a machine can detect (the narrow definition)

The wide enumeration above is the standard used for judging what to pass, before any material is passed. Separately from it, a mechanical check looks for personal information that has leaked into a finished artifact. That check covers only the three items a plain string match can detect with certainty: the name of the current employer, a value that looks like a name, and the current salary. The canonical definition of the extraction source and the detection rule is under "PII lint" in `references/job-search-format.md` of `job-change-job-search`. The code of `scripts/validate_job_search_results.py` (`_SALARY_MIN_FOR_LINT`, `_NAME_KEYS`) matches this definition.

The floor of the desired salary is excluded from this check, because the exception above permits its use as a search condition.

The narrow definition never replaces the wide enumeration. A machine can detect only these three items. Everything else is protected by the judgement made before material is passed. A PASS on the check is no evidence that the wide enumeration was honoured.

## Permission by role

Whether a role may read under `career-private/` is decided by whether that role has a means of sending data to the web (WebSearch, WebFetch). Each role's `tools` is fixed in the frontmatter of `agents/*.md`.

| Role | Means of sending data to the web | Reading under `career-private/` |
|---|---|---|
| `job-change-company-researcher` | Yes (WebSearch, WebFetch) | Never reads it. Does not open it even when given a path. Also never reads the personal-information files under `companies/{company slug}/` |
| `job-change-posting-parser` | Yes (WebSearch, WebFetch) | Never reads it. Does not open it even when given a path (does not have `Read`) |
| `job-change-job-searcher` | Yes (WebSearch, WebFetch) | Never reads it. Does not open it even when given a path. Also never reads the personal-information files under `companies/{company slug}/`, nor past results under `job-search/` |
| `job-change-exam-scout` | Yes (WebSearch, WebFetch) | Never reads it. Does not open it even when given a path. Also never reads the personal-information files under `companies/{company slug}/` |
| `job-change-interview-scout` | Yes (WebSearch, WebFetch) | Never reads it. Does not open it even when given a path. Also never reads the personal-information files under `companies/{company slug}/` |
| `job-change-research-auditor` | Yes (WebSearch, WebFetch) | Never reads it. Does not open it even when given a path. Also never reads the personal-information files under `companies/{company slug}/` |
| `job-change-fit-assessor` | None | May read it. Writes derived values only under `career-private/fit/{company slug}/` |
| `job-change-profile-writer` | None | May read it |
| `job-change-profile-auditor` | None | May read it |
| `job-change-axis-writer` | None | May read it |
| `job-change-axis-auditor` | None | May read it |
| `job-change-self-analysis-writer` | None | May read it |
| `job-change-self-analysis-auditor` | None | May read it |
| `job-change-document-writer` | None | May read it |
| `job-change-document-auditor` | None | May read it |
| `job-change-interview-coach` | None | May read it |

Whenever a role's `tools` changes, check this table. Adding one web tool is enough to make that role unable to receive personal information.

On a harness that cannot launch a sub-agent (Codex and others), the main body reads the role prompt and takes on that role itself. The main body may hold a means of sending data to the web; while it works as a role without that means, it never uses it.
