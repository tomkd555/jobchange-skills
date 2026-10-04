---
name: job-change-job-search
description: >-
  Sub-skill for job search in a job change. It finds job postings using only free public web search, and produces
  job_search_results.json with a quotation from the listing page and a source URL for every posting. It has two
  modes. fuzzy (fuzzy search) converts the user's vague wishes (for example, "mostly remote, salary 6 million yen
  or more, SaaS industry") into a structured condition sheet, confirms it with AskUserQuestion, and then searches.
  similar_better (search to beat a reference posting) extracts conditions from a reference posting
  (job_posting.json or a URL), confirms which axis (salary, remote work, annual holidays, fixed overtime pay,
  scope of change) the search should improve on, and then searches. In both modes, it searches derivation lanes
  in parallel alongside the primary set (raising the salary, increasing holidays, work style, adjacent
  occupations, widening industry or region, company type, and company career pages) and gathers company profiles
  (the nine axes of disclosed figures, published labor-law violation cases, and recent news) for every company
  that appears in the results into the same deliverable. It anonymises the conditions passed to search: it
  excludes the current employer's name, the user's name, and the current salary (a desired salary floor may be
  included). Once the user picks a company from the results, this hands off to job posting intake in company
  research. It runs when dispatched from job-change-support (the hub).
  Use when the user wants to search for job openings for a job change in Japan using only free public web search,
  either from a vague wish list (fuzzy mode) or by finding roles that beat a baseline posting (similar_better mode),
  with derived lanes for better conditions and wider scope, a sourced company profile for every company found,
  with every posting backed by a verbatim quote from the listing page, and their current employer, name and
  current salary kept out of the query.
  trigger words: 求人検索, 求人を探す, 求人を探して, 転職先を探す, リモートの求人, 年収600万以上の求人,
  似た求人でもっと良い条件, 今より良い条件の求人, この求人より良いところ, 求人を絞り込む, 求人と企業情報, 幅広く求人を探す。
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Agent, AskUserQuestion, Skill
---

# job-change-job-search

When searching for job postings in a job change, this skill covers the whole procedure, from building conditions through search, validation, and delivery. It finds job postings using only free public web search, and attaches a quotation from the listing page and a source URL to every posting.

This skill runs when dispatched from the hub (job-change-support). The job searcher agent (job-change-job-searcher) carries out the search execution (web research). The judgment criteria are self-contained in `references/`.

## Purpose and principles

1. **Search using only free public web search.** It does not depend on paid job-posting APIs or member-only private postings. The catalog of search methods is in `references/query-catalog.md`. It covers the three families of opening job pages, the URL grammar and constraints per site, and the sites excluded from scope with the reasons. It also covers the rules for deciding whether fetching is allowed, the query-expansion rules, re-checking the salary floor, deduplication, market-rate baselines, where to obtain related information, and confirming listing expiry. When a job posting that requires membership registration is placed out of scope, this is recorded in the deliverable's `coverage_notes`. A site whose robots.txt explicitly refuses AI-crawler fetching is out of scope even when fetching it is technically possible.

2. **Attach a quotation from the listing page and a source URL.** Every posting must include a quotation from the listing page (`quote`), a source URL (`url`), and the listing site name (`source_site`). Postings that cannot be fetched are never fabricated. When the salary reads 「応相談」 (negotiable) or similar and no number can be read, `salary_range` is set to `null`.

3. **Enforce anonymisation.** The conditions passed to the searcher agent exclude the current employer's name, the user's name, and the current salary. A desired salary floor may be included in the conditions. This is the only exception to the personal-information boundary that applies to this skill. The reasoning and the rule are in `{HUB_SKILL_DIR}/references/pii-boundary.md`. The paths and content of `profile.json` and `axis.json` are never passed to an agent that holds web tools. The skill body builds the conditions and passes them only as anonymised strings.

4. **Exclude postings from the current employer.** Search results can include postings from the current employer. The skill body performs the exclusion locally (since `profile.json` is never passed to a web tool, the exclusion judgment happens outside the agent).

5. **Never send personal information outward.** The user's personal information is never used in any outward transmission, including search queries, fetches, or external APIs. The canonical enumeration of covered items and the exceptions is in the hub's `{HUB_SKILL_DIR}/references/pii-boundary.md`. Because job-change-job-searcher holds WebSearch and WebFetch, `profile.json`, `axis.json` and paths and content under `career-private/` are never passed to it. The only exception for this skill is the desired salary floor, which may be passed as `salary_min` in the anonymised condition sheet (principle 3). The current salary (`salary.current`) is not among the exceptions and is never passed. Station names derived from `commute.json` are never passed either.

6. **Search the user's conditions as given, and run derivations in a separate track.** The user's wishes are searched as they stand, as the primary set (`search_sets.primary`), with twelve queries. On top of this, both modes build derivation lanes (`search_sets.derivations`), each with up to three additional queries. Some lanes improve conditions (salary, annual holidays, work style, company type), and others widen scope (adjacent occupation, industry, seniority level, remote-work phrasing, region, company career pages). When the way a condition is worded conceals a narrowing the user did not choose themselves, Step 1 confirms with one question whether it is required or a preference, and only conditions answered as preferences are moved by a lane. Lanes never replace the primary set, and never reduce the number of queries in the primary set. The default is to select every lane that fits the mode; lanes the user opts out of are not run. The canonical definition of lanes is in `references/derivation-lanes.md`, and the list of biases is in `references/bias-checklist.md`.

7. **Gather company profiles for every company that appears in the results.** After the search, this gathers company information into `company_profiles` for each company that appears in the results, with a source URL and evidence level on each value. The information covers the nine axes of disclosed figures (average annual salary, annual holidays, overtime, paid-leave-use rate, turnover rate, male childcare-leave-use rate, revenue growth rate, operating margin, equity ratio), basic information, listing in published labor-law violation cases, and recent news. The searcher agent collects it in `company_profile` mode. The result belongs to the observation layer and does not include any judgment. A company profile does not substitute for company research, and company research after a candidate company is chosen is still carried out separately. The canonical source list is in "Sources for company information (company_profile mode)" in `references/query-catalog.md`.

## Out of scope

- **Applying to postings, registering with agencies, and other outward transmission.** This does not submit application forms, reply to scouts, or register with job-change agencies. It supports work up through gathering postings; the user applies.
- **Company research, and structured intake of job postings.** Company research for the chosen company, and structuring the job posting, are handled by job-change-company-research. Its deliverables are `company_research.json` and `job_posting.json`. This skill gathers search results and hands off to company research after selection.
- **Fit assessment.** Effective hourly wage, binding hours, and the seven-dimension fit assessment are handled by job-change-fit-assessment. This skill stays within the eight-axis screening that can be judged from the posting text alone, and does not perform assessment that requires company research, self-analysis, or commute time.
- **Creating and managing the user profile and the axis.** Creating, updating, and validating profile.json is handled by the hub (job-change-support) and `job-change-profile`. axis.json belongs to `job-change-axis`. This skill only reads them locally, and never passes their content outward or to an agent holding web tools. It reads profile.json for the current employer and the PII lint, and `{AXIS}` for the axis judgment in Step 3.5 and the current salary in Step 4.

## Path resolution

Where the user's data is placed is determined solely by what the configuration file states. There is no default location. Wherever this document writes `{DATA_ROOT}`, read it as the `data_root` that the following command returns.

When dispatched from the hub (job-change-support), the hub passes an already-resolved `{DATA_ROOT}`. When started standalone, run the following before any stage of the work.

```bash
python {HUB_SKILL_DIR}/scripts/jc_config.py --show
```

| Exit code | State | Response |
|---|---|---|
| 0 | Configured | The output's `paths` holds the absolute path for each piece of data. Proceed with the work as is |
| 1 | Configured but the content is invalid | Show the output's `errors` to the user, and do not proceed until it is fixed |
| 2 | Not configured | Start `job-change-support` with the Skill tool to have it create the configuration, resolve `{DATA_ROOT}`, and then return |

`{SKILL_DIR}` denotes this skill's absolute path, and `{HUB_SKILL_DIR}` denotes the absolute path of `job-change-support` installed alongside it. The configuration file's specification, including the lookup order, is in `docs/configuration.md`.

## Data layout

For each search run, create `job-search/{YYYYMMDD}-{short condition slug}/` and place `job_search_results.json` there. This is separate from the per-company deliverable tree (`companies/{company slug}/`).

| Path | Content |
|---|---|
| `job-search/{YYYYMMDD}-{short condition slug}/job_search_results.json` | The job search deliverable. Specification in `references/job-search-format.md` |
| `job-search/{YYYYMMDD}-{short condition slug}/job-search-report.md` | A report formatting the search results into human-readable form. The skill body writes it in Step 5 |
| `job-search/{YYYYMMDD}-{short condition slug}/job_search_results.partial-*.json` | Partial files that the searcher writes in parallel (the primary set and the lane groups). Deleted after Step 4 passes |
| `job-search/{YYYYMMDD}-{short condition slug}/company_profiles.batch-*.json` | Batch files of company information. Deleted after Step 4 passes |

- The short condition slug is a concise identifier expressing the main conditions in romaji or alphanumerics (such as `remote-saas-be`). The date matches the search execution date (`executed_at`).
- Real data is never placed in the skill's own folder (`skills/job-change-job-search/`). The two sample entries under `assets/` are fictitious.

## Intermediate deliverable: job_search_results.json

Search results are aggregated into `job_search_results.json` (`schema_version` is `2.3`). The structure has three layers.

| Layer | Fields | Writer |
|---|---|---|
| Observation layer | In `results[]`: title, company_name, url, source_site, salary_range, location, remote_policy, annual_holidays, match_notes, quote, better_points, `search_set`, `lane`, `role_match`, `related_info`, `duty_items`, `axis_observations`, `baseline_comparison.axes`; at the top level: `search_sets`, `search_log`, `improvement_axes`, `company_profiles` | The searcher agent (holds web tools; never reads profile) |
| Merge | Combining partial files, deduplication, excluding the current employer, assigning `results[].company_key` | The skill body (`scripts/merge_search_results.py`; reads profile locally) |
| Judgment layer | In `results[]`: `axis_judgements`, `classification`, `classification_reasons`, `classification_override`, `slug`, `baseline_comparison.overall` | The skill body (local; reads `{AXIS}`) |
| Summary | `screening` (counts per classification, overall verdict, unmet-condition counts per axis, the record of whether current-employer exclusion ran, the record of whether derivation lanes ran) | The skill body |

Splitting the observation layer from the judgment layer makes condition judgment possible without passing personal information to an agent holding web tools. The full specification, entry criteria, and validation rules are canonically defined in `references/job-search-format.md`.

## Modes

### mode=fuzzy (fuzzy search)

Converts the user's vague wishes into a structured condition sheet, confirms it, and then searches.

1. Structure the user's wish (such as "mostly remote, salary 6 million yen or more, SaaS industry") into a condition sheet along the following axes.
   - Occupation (`roles`), industry (`industries`), salary floor (`salary_min`, a numeric value in yen), work location/remote work (`location`, `remote_policy`), employment type (`employment_type`), other conditions (`other`).
   - The current employer's name, the user's name, and the current salary are excluded from the conditions (principle 3). A desired salary floor may be included as `salary_min`.
2. Confirm the structured condition sheet with AskUserQuestion. Center it on multiple-choice questions, up to four questions with up to four options each. Prioritise confirming the axes that are vague (remote-work frequency, salary floor, occupation range, and so on).
3. Check the condition sheet against the "List of user-side biases" in `references/bias-checklist.md`, and for any matching condition, include "is it required, or a preference?" as one of the confirmation questions. Only conditions answered as a preference are moved by a lane. The salary floor is never lowered by any lane.
3.5. Confirm derivation lanes with a multiple-choice selection in AskUserQuestion. Split it into three questions (improving conditions / widening scope / location and entry point), with the options for each question following the "How to choose" table in `references/derivation-lanes.md`. The default is to select every lane that fits the mode and the condition sheet. Mark the options 「（推奨）」 (recommended), and add the cost (the expected number of additional queries and the number of companies for company-profile collection) to each question's description. When the user does not answer a question, every lane in that question's group is treated as selected. For each lane chosen, build a lane condition sheet writing which condition it moves, its value, and the reason.
4. Pass the confirmed conditions (the primary set) and the lane condition sheets, both as anonymised strings, to the job searcher agent (job-change-job-searcher), and have it search under `mode=fuzzy` (how launches are split is in Step 2).

### mode=similar_better (search to beat a reference posting)

Extracts conditions from a reference posting, confirms which axis the search should improve on, and then searches.

1. Receive the reference posting. Its location is either `companies/{company slug}/job_posting.json` (an already-ingested posting) or a URL. When given a URL, this skill cannot extract conditions since it does not hold WebFetch. First start `job-change-company-research` with the Skill tool and run Step 0.5's posting intake. Use the resulting `job_posting.json` as the reference posting.
2. Extract occupation, salary, annual holidays, remote-work policy, overtime, **employment type**, and **scope of change in work location and duties** from the reference posting. The latter two are among the six axes of the per-axis comparison, so omitting either leaves that axis `unknown`. When `job_posting.json`'s `schema_version` is `1.0`, that file has no `scope_of_change`. In that case, treat the axis as `unknown` and confirm with the user whether to re-ingest the posting. During extraction too, the current employer's name, the user's name, and the current salary are never carried into the conditions.
3. Confirm with AskUserQuestion which axis the search should improve on. The five options are salary, remote work, annual holidays, fixed overtime pay, and scope of change. Record the chosen axes' IDs as `improvement_axes`. Employment type is not among the options (it has no direction on a scale, so it cannot be taken as an improvement axis; if there is a wish for it, treat it as a required condition in `conditions.employment_type`). The canonical definition of axis IDs and improvement direction is in `references/job-search-format.md`.
3.5. Confirm derivation lanes with the same procedure as fuzzy's 3.5. In similar_better, keep each lane's `salary_min` at or above the reference posting's floor, and drop `industry_widen` from the options when the reference posting's industry is a required condition. Have `baseline_comparison.axes` written for derived postings too.
4. Pass the extracted baseline conditions, `improvement_axes`, and the lane condition sheets, as anonymised strings, to the job searcher agent, and have it search under `mode=similar_better` (how launches are split is in Step 2). Instruct it to record `baseline` (the reference posting's URL or company slug) in the deliverable. For each posting, the agent lists in `better_points` the points where it beats the reference posting's conditions. It also writes the six-axis `baseline_comparison.axes`.

## Pipeline

`{SKILL_DIR}` denotes this skill's absolute path. `{results.json}` is read as the deliverable's path (`job-search/{YYYYMMDD}-{slug}/job_search_results.json`).

### Step 0 Intake and mode determination

Determine whether the request is fuzzy (a search from a vague wish) or similar_better (a search to beat a reference posting). Treat it as similar_better when a reference posting or URL is given, and as fuzzy when it is a vague wish. When the determination is unclear, confirm with AskUserQuestion.

This skill needs both gates to pass before Step 1. Read `{PROFILE}` as the absolute path of `career-private/profile.json`, and `{AXIS}` as the axis source resolved by the rule in `{HUB_SKILL_DIR}/references/axis-format.md`, section "Location".

```bash
python {HUB_SKILL_DIR}/scripts/validate_profile.py {PROFILE}
python {HUB_SKILL_DIR}/scripts/validate_axis.py {AXIS}
```

When `profile.json` is missing or FAILs, send the work to `job-change-profile` through the hub. When no axis source exists or `{AXIS}` FAILs, send the work to `job-change-axis` through the hub.

### Step 1 Building and confirming conditions

Build conditions according to the mode (the procedure in "Modes" above), and confirm them with AskUserQuestion. The conditions built here must already be anonymised (they exclude the current employer's name, the user's name, and the current salary).

### Step 2 Executing the search (job-change-job-searcher, sonnet)

Launch multiple job searcher agents (job-change-job-searcher) in one message: one for the primary set, and one per every three lanes (for seven lanes, one for the primary set plus three lane handlers). Each handler's coverage never overlaps: the primary-set handler searches only the primary set's twelve queries, and a lane handler searches only its assigned lanes. The canonical rule against passing the same work to multiple roles is in "How many to launch" in the hub's `{HUB_SKILL_DIR}/references/role-execution.md`. Each handler writes to a partial file and does not return the deliverable's body. The instructions pass the following.

- The mode (`fuzzy` or `similar_better`) and the assignment ("primary-set handler" or the list of lane names).
- The anonymised search conditions (a string, excluding the current employer's name, the user's name, and the current salary). For a lane handler, attach the condition sheet of its assigned lane (the lane name, the condition it moves and its value, and the reason).
- The output directory (`job-search/{YYYYMMDD}-{slug}/`), the name of the partial file to write (`job_search_results.partial-primary.json` for the primary-set handler, `job_search_results.partial-lanes-{N}.json` for a lane handler), and the value to write into `search_id`. `search_id` takes the same `{YYYYMMDD}-{slug}` as the directory name.
- For similar_better, pass the baseline conditions, `improvement_axes` (an array of improvement axis IDs), and `baseline` (a URL or company slug). Also pass the reference posting's path, `{DATA_ROOT}/companies/{company slug}/job_posting.json`. This file is in the per-company non-personal-information tree and does not contain any information about the user, so it may be passed to an agent holding web tools. When the reference posting originates from a URL and `job_posting.json` does not yet exist, first have job-change-company-research create it in Step 0.5 (posting intake), then pass its path.
- This skill's absolute path `{SKILL_DIR}` (where `references/query-catalog.md`, `references/job-search-format.md`, `references/bias-checklist.md`, and `references/derivation-lanes.md` live).
- The hub's absolute path `{HUB_SKILL_DIR}` (where `references/screening-axes.md` and `references/market-data-sources.md` live).
- An instruction to write **through the observation layer only**. The observation layer covers the quotations and classification of `duty_items`, the eight-axis `axis_observations`, the `search_log` of executed queries (with `search_set` and `lane`), each posting's `search_set`, `lane`, `role_match`, `related_info` (the two per-posting keys), and the top-level `search_sets`. In similar_better, this also includes the six-axis `baseline_comparison.axes` and copying through `improvement_axes`. It never writes the judgment layer (including `baseline_comparison.overall`), `screening`, or `company_key`.

**`profile.json` and `axis.json` are never passed** (principle 5; the searcher holds WebSearch and WebFetch). Thresholds such as an overtime ceiling, an annual-holidays floor, or work-characteristic preferences are never passed either. These are the user's own conditions, and the skill body performs the judgment in Step 3.5. The one exception is `salary_min`, already allowed as an anonymised condition, which may be included in the search conditions.

The agent gathers postings following the search methods in `references/query-catalog.md`. It builds the partial file in the format of `references/job-search-format.md`. It reads the eight-axis and duty-classification vocabulary from `{HUB_SKILL_DIR}/references/screening-axes.md`. On a harness that cannot launch subagents, the skill body reads the role prompt and runs each assignment in sequence itself, writing the same partial files.

### Step 2.5 Merging and gathering company information (the skill body plus job-change-job-searcher)

1. Build a list of companies from the partial files. Run the following and receive `companies` from `--json`. With `--profile`, postings from the current employer are excluded locally at this stage, and never enter the list.

   ```bash
   python {SKILL_DIR}/scripts/merge_search_results.py {DATA_ROOT}/job-search/{search_id} --list-companies --profile {DATA_ROOT}/career-private/profile.json --json
   ```

2. Gather company information. Split the company list into batches of eight, and launch one job searcher agent per batch under `mode=company_profile`, up to three at a time. The instructions pass the batch's companies (`company_key`, `name`, the job-listing page URL), the filename to write (`company_profiles.batch-{N}.json`), the output directory, and `{SKILL_DIR}`. Search conditions, profile, and lane information are never passed. Any batch beyond three waits for the previous group to finish before launching.
3. Merge. Run the following and confirm exit code 0. Pass every lane chosen in Step 1 to `--lanes`.

   ```bash
   python {SKILL_DIR}/scripts/merge_search_results.py {DATA_ROOT}/job-search/{search_id} --profile {DATA_ROOT}/career-private/profile.json --lanes better_salary,adjacent_role --json
   ```

   The merge script combines the partial files, removes duplicates, excludes postings from the current employer, combines `company_profiles`, assigns `company_key` to each result, and writes `job_search_results.json`. The partial files and batch files are kept, and deleted with `--cleanup` after Step 4's validation passes. When a company is missing its company information, it stops with an ERROR, so relaunch the `company_profile` batch once, for the missing companies only. If it is still missing after the relaunch, merge with `--stub-missing`, and leave the missing companies in `open_questions`. When a lane was chosen but its partial file is missing, this is recorded in `coverage_notes` as not run.

### Step 3 Excluding postings from the current employer (the skill body)

Exclusion of postings from the current employer already happens in Step 2.5's merge. The current entry is the one in `career-private/profile.json`'s `career_history` whose `period` ends with `〜現在` (to present); the merge script removes any result whose `company_name` matches its `company` after normalisation. The excluded count is in `--json`'s `excluded_count`, and Step 3.5 records it in `screening.current_employer_exclusion` as `performed: true`・`excluded_count`・`method: "merge_search_results.py（正規化企業名の一致）"`. The excluded company name counts as the current employer's name, so it never appears in the deliverable or the merge script's output, and is conveyed only in the chat reply to the user.

### Step 3.5 Eight-axis judgment and three-way classification (the skill body)

The searcher agent writes only through the observation layer (the facts readable from the posting). Matching against the user's own conditions is done locally by the skill body, which can read `{AXIS}`. This division of labor makes condition judgment possible without passing personal information to an agent holding web tools.

1. Read `{AXIS}` with Read, and check its `schema_version`.
2. Read the requirement level and threshold per axis from `job_change_axis.conditions[]` and `work_character_preferences[]` in `{AXIS}`. The requirement level is one of three values: `must` / `want` / `none`. When the same axis has multiple required conditions, adopt the strictest threshold.
3. Match each result's `axis_observations` against the threshold, and write `axis_judgements`. An axis whose observation is `stated=false`, or whose `value` is `null`, becomes `unknown`. **The absence of a statement is never used as evidence that a condition is met, and never as evidence that it is not met.**
4. Derive `classification` from the decision table in `references/job-search-format.md`, and write `classification_reasons`. When manually changing the derived result, attach `classification_override` only in the direction that makes it stricter.
5. In similar_better, write each posting's `baseline_comparison.overall`. Looking only at the axes listed in `improvement_axes`, it is `better` when at least one is in the improving direction and none is in the opposite direction, and `not_better` otherwise. The mapping table for improvement direction is in `references/job-search-format.md`. This is the only stage that assigns good or bad to the `relation` (the factual relationship) the agent wrote.
6. Write `screening` as a derived value. Make `counts` and `unmet_axis_summary` match the actual tally. Record Step 3's execution result in `current_employer_exclusion` (`performed: false` and `excluded_count: null` when not run). In `derivations`, write whether lanes ran, and, per lane, the count of postings whose `search_set` is `derived` and how many of those are application candidates (`performed: false` and an empty array when no lane was chosen). Derived postings are judged and classified under the same rules as the primary set. Classification never depends on how a posting was found, and never depends on the content of `company_profiles`.

When `{AXIS}`'s `schema_version` is `1.0` or `1.1`, fall back. Leave the observation layer as is. Set every axis to `level: none`, `judgement: unknown`, and every result to `needs_more_research`. Set `screening.axes_source` to `degraded` and `recommendation` to `判定不能`. Never present the classification result as an "application candidate", and guide the user toward structuring their conditions in `job-change-axis`.

The canonical vocabulary used in judgment (the eight axes, eight work characteristics, duty classification) is in `references/screening-axes.md` in the hub (`job-change-support`).

### Step 4 Mechanical validation and PII lint (the skill body)

Validate the job_search_results.json after exclusion, with `--profile` and `--axis`.

```bash
python {SKILL_DIR}/scripts/validate_job_search_results.py {results.json} --profile {PROFILE} --axis {AXIS}
```

With `--profile` and `--axis`, this also runs the PII lint (detecting a leaked current-employer name, the user's name, or the current salary) alongside the schema check. `--profile` supplies the current employer and the name from `career_history` and `basic`; `--axis` supplies `salary.current` and the thresholds. When `{AXIS}` is a 1.x/2.0 `profile.json` that holds both, `--profile` alone covers both. Even one ERROR is a FAIL. When a PII-leak ERROR appears, remove the leaked part from the deliverable and validate again (it is an anonymisation leak, and is never delivered as is). Confirm PASS (zero ERRORs) before delivering. Reading profile.json and `{AXIS}` stays confined to this local validation process and is never sent outward.

Once PASS is confirmed, delete Step 2.5's partial files and batch files. On FAIL, keep them, and redo from the merge (Step 2.5's step 3).

```bash
python {SKILL_DIR}/scripts/merge_search_results.py {DATA_ROOT}/job-search/{search_id} --cleanup
```

### Step 5 Delivery and hand-off

Deliver the validated, PASSing job_search_results.json. Organise the report by classification, and state `screening.recommendation` first. Never include an empty section, a repeated statement, or a boilerplate preamble.

Before delivery, the skill body formats job_search_results.json into a human-readable job search report. The output goes to `job-search/{search_id}/job-search-report.md`. `search_id` is the deliverable's top-level value, the same `{YYYYMMDD}-{slug}` as the directory name. Since this report is in the non-personal-information tree, it never writes the current employer's name, the user's name, or the current salary (the canonical boundary is defined in `{HUB_SKILL_DIR}/references/pii-boundary.md`).

- Place `screening.recommendation`, `rationale`, and the count per classification (`screening.counts`) at the top.
- Tabulate postings by classification (`apply_candidate`, `needs_more_research`, `excluded`) with these columns: job title, company name, listing site, source URL, salary range, work location/remote policy, and the unmet-`want` count. Keep a separate table per classification; never list `excluded` postings in the same table as application candidates. The unmet-`want` count is the number of axes in `axis_judgements` whose `level` is `want` and whose `judgement` is `not_meets`; it exists only as a report column, and the deliverable schema has no such field. Never sort by this count to make a ranking table.
- Place derived postings (`search_set` is `derived`) within each classification's table, split by lane, under a 「派生レーン: {lane}」 (derivation lane) subsection. Never place them above the primary set's table. Attach, from `match_notes`, which lane and which condition produced the posting. When application candidates exist only among derived postings, state this in `rationale`, and never present them as the top candidate in place of the primary set's application candidates. When no lane was chosen at all, write in one line that none was created and why. When `coverage_notes` lists a lane that did not run, write that lane as not run.
- Tabulate the eight-axis judgment per posting (axis, requirement level, threshold, observed value, `yes`/`no`/`unknown`). Attach `classification_reasons` as the screening's basis, and for a posting that has `classification_override`, state this along with the reason. Write an axis with no observation as `unknown`, and never use it as evidence that the condition is met or as evidence that it is not met.
- Place one table of company information, one row per element of `company_profiles`. Its columns are company name, employee count, average annual salary, annual holidays, average monthly overtime, turnover rate, whether it is listed, published labor-law violation cases, and the lowest evidence level in that row. Write the violation-case column as 「掲載あり」 (listed), 「掲載なし（違反が無い証拠にはならない）」 (not listed; no evidence of absence), or 「未確認」 (unconfirmed). Never write an item whose `value` is `null` as 0; write it as 「未取得」 (not obtained). Add one line below the table noting that the average annual salary in a securities report is an average across all employees, and is never read as the salary for the posting's occupation. Note that level-C values (an overall word-of-mouth score, a median from a salary-navigator site) are reference values. Continue `recent_news` and `open_questions` per company as bullet lists.
- Write `related_info`'s listing date and market-rate baseline as one column in the posting table.
- `company_profiles` does not substitute for company research, and is never carried over into company research. Company research after choosing where to apply is done separately, and the company information from the search stage serves only as material for judging whether to advance a `needs_more_research` posting into company research.
- The skill body performs matching against past search results locally. It reads past deliverables under `{DATA_ROOT}/job-search/`, and when a posting with the same normalised company name and occupation name also appears in a different `search_id` 60 or more days apart, writes this into `open_questions`. The rule is in "Confirming listing closure and re-listing" in `references/query-catalog.md`. Since a past deliverable includes the judgment layer, it is never passed to the searcher agent.
- Write the suspected listing expiries recorded in `open_questions` (a posting that became unreadable on re-fetching the URL), and the postings that also appeared in a past search, into the report as they stand.
- Tabulate the unmet and undecidable count per axis (`screening.unmet_axis_summary`).
- Write current-employer exclusion exactly as `screening.current_employer_exclusion` gives it. When `performed` is `false`, write 「未検証」 (not verified), never 「0件」. The excluded company name counts as the current employer's name, so it is never written into job-search-report.md, and is conveyed only in the chat reply to the user.

1. Convey `screening.recommendation` and `rationale` first, as the overall verdict. When it is `応募推奨なし` (no recommendation to apply), state this plainly, and never force a top candidate to be chosen.
2. List postings whose `classification` is `apply_candidate`, along with the required conditions they meet.
3. List `needs_more_research` postings, along with the axes that could not be judged (the `unknown` axes) and the means to confirm them (company research or interviewing).
4. List `excluded` postings briefly, along with the required condition they failed to meet. Attach a note, and never list them in the same table as application candidates.
5. Once the user picks a company, register the company slug in `career-private/company_index.json` following the hub's (job-change-support's) Step 0 procedure. Create `companies/{company slug}/`, and append it to that result's `slug`. After appending, re-run Step 4's validation and confirm PASS (zero ERRORs). Then hand off to job-change-company-research's Step 0.5 (posting intake). Use the job-listing page URL as the entry point when there is one; otherwise, pass the listing content copied into the search result as the body.

In similar_better, also give each posting's `better_points` (the points that improve on the reference posting). Tabulate the six axes of `baseline_comparison.axes` with these columns: axis, whether it was chosen as an improvement axis, `relation`, the reference posting's value, and the candidate posting's value. Show postings whose `overall` is `better` separately from those that are `not_better`, and attach which of the axes listed in `improvement_axes` it beat. Write an `unknown` axis as "unconfirmed", never as the same as the reference posting.

#### Reporting rules

**Never report an unverified matter as an accomplishment.** The only figures allowed in the report are the following.

| Figure allowed in the report | Source |
|---|---|
| Count per classification | `screening.counts` |
| Unmet/undecidable count per axis | `screening.unmet_axis_summary` |
| Count per lane, and how many of those are application candidates | `screening.derivations.lanes` (only when `performed` is `true`) |
| Each value in the company-information table | `company_profiles` (attach `grade` to each value; `null` is "not obtained") |
| Unmet-`want` count per posting | Counted from `results[].axis_judgements` |
| Excluded-current-employer-posting count | `screening.current_employer_exclusion.excluded_count` (only when `performed` is `true`) |
| Number of queries executed, hit count, adopted count | `search_log` |

The report may state only as much as the queries and their counts recorded in `search_log`, and **never claims that the search was exhaustive**. It never writes 「網羅的に調べた」 (researched exhaustively) or 「主要な求人サイトを一通り確認した」 (checked through the major job-listing sites).

Write an item where `current_employer_exclusion.performed` is `false` as 「未検証」 (not verified), never as 「0件」. A PASS on mechanical validation shows only three things: the format is in order, no PII has leaked, and the classification and overall verdict agree with the axis judgments. Whether a posting suits the user is a separate question. Reflect this distinction in the report.

## Pass/fail gates

| Gate | Passing condition and where it sends work back |
|---|---|
| Step 2.5's merge | Do not proceed to Step 3.5 unless `merge_search_results.py` exits with code 0. When company information is missing, relaunch the `company_profile` batch once; if it is still missing, merge with `--stub-missing` and leave it in `open_questions`. |
| Step 4's mechanical validation and PII lint | Never deliver unless `validate_job_search_results.py --profile --axis` PASSes (zero ERRORs). A PII-leak ERROR is an anonymisation leak; remove it from the deliverable and validate again. |
| Recommendation to apply | When `screening.recommendation` is `応募推奨なし` (no recommendation to apply), this does not hand off to company research or fit assessment by default. It sends the work back to reviewing the required conditions (updating conditions in `job-change-axis`), or to reviewing the search conditions or search approach. When there are zero application candidates, it never dresses up an excluded or a needs-more-research posting as the top candidate. **Exception**: after listing every unmet required condition for a posting, when the user explicitly wishes to proceed with that specific posting, this may hand it off to company research. The material for this judgment is only what the posting states, and the judgment itself can be overturned by company research or interviewing. When handing off, state plainly in the handover which required conditions remain unmet. When the user has not expressed a wish, this skill never proposes the hand-off on its own. |
| Stating the fallback plainly | When `screening.recommendation` is `判定不能` (undecidable; the axis source is 1.x), state plainly that judgment could not be made. Never present the classification result as an "application candidate", and guide the user toward structuring their conditions in `job-change-axis`. |

## Role execution (by harness)

This skill's pipeline is written to delegate work to specialised roles. The role content is under `references/roles/`, which is the canonical source.

| Agent name | Canonical role prompt |
|---|---|
| `job-change-job-searcher` | `{SKILL_DIR}/references/roles/job-searcher.md` |

The canonical execution procedure by harness, and the judgment for how many to launch, are in the hub's `{HUB_SKILL_DIR}/references/role-execution.md`.

## Agent model policy

| Agent | model | Responsibility |
|---|---|---|
| `job-change-job-searcher` | sonnet | Public web search from anonymised conditions (primary-set handler, lane handler) → partial file, with quotations and source URLs attached. In `company_profile` mode, a batch file of company information |

`model` is fixed in the agent's frontmatter and is never overridden at launch. The primary-set handler, lane handlers, and company-information batches all launch the same agent multiple times with different assignments.

## Script CLI usage examples

Merging partial files (exit code 0 on success, 1 on ERROR; `--list-companies` does not write a file and only returns the company list).

```bash
python {SKILL_DIR}/scripts/merge_search_results.py {search_dir} --list-companies --profile {DATA_ROOT}/career-private/profile.json --json
python {SKILL_DIR}/scripts/merge_search_results.py {search_dir} --profile {DATA_ROOT}/career-private/profile.json --lanes better_salary,adjacent_role --json
python {SKILL_DIR}/scripts/merge_search_results.py {search_dir} --profile {DATA_ROOT}/career-private/profile.json --stub-missing
python {SKILL_DIR}/scripts/merge_search_results.py {search_dir} --cleanup
```

`--json` outputs `status`, `errors`, `warnings`, `excluded_count`, `companies`, `missing_lanes`, and `output_path`. `--stub-missing` creates an element with every field `null` for a company missing its company information. Merging keeps the partial files, and `--cleanup` deletes them after Step 4's PASS.

Validating the job search results (exit code 0 on PASS, 1 on FAIL; WARN-only counts as PASS). `{SKILL_DIR}` is this skill's absolute path, and `{results.json}` is read as the path under validation.

```bash
python {SKILL_DIR}/scripts/validate_job_search_results.py {results.json}
python {SKILL_DIR}/scripts/validate_job_search_results.py {results.json} --json
python {SKILL_DIR}/scripts/validate_job_search_results.py {results.json} --profile {PROFILE} --axis {AXIS}
```

`--json` outputs the result in JSON form (`status`, `error_count`, `warning_count`, `errors`, `warnings`). With `--profile` and `--axis`, this adds the PII lint (detecting a leaked current-employer name, the user's name, or the current salary). It also checks whether `threshold_ref` actually exists among the conditions and characteristics in `{AXIS}`, and whether `level` matches the requirement level in `{AXIS}`. Running without `--profile` and `--axis` gives a WARN stating that the PII lint and the threshold cross-check were not run. Sample entries live under `assets/`: `job_search_results_example.json` for fuzzy, and `job_search_results_similar_better_example.json` for similar_better. The canonical field specification and validation rules are in `references/job-search-format.md`. Run the unit tests (for both the validation script and the merge script) with the following.

```bash
cd {SKILL_DIR} && python -m unittest discover -s scripts/tests
```

## References list

| File | What it holds | When to read it |
|---|---|---|
| `references/job-search-format.md` | The field specification, entry criteria, mechanical validation rules, and PII lint for job_search_results.json | Every stage of creating, reading, or validating the deliverable |
| `references/query-catalog.md` | The methods for finding postings via free public web search (the three families of opening job pages, the URL grammar and constraints per site, sites out of scope or unconfirmed, the rules for deciding whether fetching is allowed, the query-expansion rules, re-checking the salary floor, deduplication, market-rate baselines, where to obtain related information, where to obtain company information, confirming listing expiry) | Step 2's search, Step 2.5's gathering of company information, instructions to the searcher agent |
| `references/derivation-lanes.md` | The purpose, the condition moved, the query-building method, the mode, and the corresponding bias for each of the ten derivation lanes; how to choose lanes (the three-question split); recording and how results are handled | Step 1's lane selection, Step 2's instructions, Step 5's report |
| `references/bias-checklist.md` | The list of user-side condition biases and the checking questions, how biases map to derivation lanes, and the unmet-condition count attached to the report | Step 1's confirming of conditions, Step 5's report |
| `references/search-methods.md` | The relation between search volume and employment quality, the practice of satisficing, the reason for separating observation from judgment, and the sourced grounds for keeping derivation lanes in a separate track and keeping company information at the observation level | The stage of deciding how to report, the stage of building the proposal when there is no recommendation to apply |
| `{HUB_SKILL_DIR}/references/screening-axes.md` | The vocabulary and boundary examples for the eight screening axes, eight work characteristics, and duty classification | Step 2's observation, Step 3.5's judgment |
| `{HUB_SKILL_DIR}/references/market-data-sources.md` | The source of market-rate data and the rules for handling it | Step 2's market-rate baseline and related information |
| `{HUB_SKILL_DIR}/references/pii-boundary.md` | The canonical personal-information boundary and its exceptions | Every stage of building conditions and passing them to an agent |
| `references/roles/job-searcher.md` | The searcher's role prompt (covering through the observation layer) | Step 2. On a harness that cannot use subagents, the skill body reads it |
