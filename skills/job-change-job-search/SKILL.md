---
name: job-change-job-search
description: >-
  Job search for a job change in Japan, started from one line of the user's wishes ("リモート中心、
  年収 600 万円以上、SaaS 業界"). It turns the line into a condition sheet (wishes.json), asks only
  about the vague items, searches free public job pages with one searcher agent, reads the pages
  WebFetch cannot open (Indeed, Green, login or dynamic pages) in the user's Chrome, checks each
  posting for the legally required items, matches it against the required conditions and returns a
  list with a source URL and a quotation per posting. No career record and no employer or salary
  question. Use when the user wants postings found, or better postings than a baseline posting
  (similar_better). trigger words: 求人を探して, 求人検索, 求人を見つけたい, もっと良い条件,
  似た求人でより良い待遇, リモートの求人, 年収.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, AskUserQuestion, Agent, Skill, ToolSearch, mcp__claude-in-chrome__tabs_context_mcp, mcp__claude-in-chrome__tabs_create_mcp, mcp__claude-in-chrome__navigate, mcp__claude-in-chrome__get_page_text, mcp__claude-in-chrome__read_page, mcp__claude-in-chrome__find, mcp__claude-in-chrome__computer, mcp__claude-in-chrome__form_input, mcp__claude-in-chrome__tabs_close_mcp
---

# job-change-job-search

Finds job postings from the user's wishes with free public web search and the user's own browser, and returns a list the user can act on in the first reply.

## Principles

1. **Start from one line.** The user writes their wish in one sentence. The skill builds the condition sheet and asks at most two questions, about the items it cannot settle from the line (the salary floor, the remote arrangement). The sheet is saved in `{DATA_ROOT}/career-private/wishes.json` and is reused on the next run without asking again.
2. **Never ask for, and never record, the current employer's name or the current salary.** The desired salary floor is a condition; the current salary is nothing this skill needs.
3. **Three routes to postings.** Sites whose result URL can be built (求人ボックス, マイナビ転職エンジニア, HERP Careers), `site:` search for the others, and company careers pages. The catalog with each site's URL grammar and robots.txt status is `references/query-catalog.md`. Indeed and Green refuse automated fetching in robots.txt; the searcher agent never opens them. The main session opens them in the user's Chrome (Step 3).
4. **Every posting carries a quotation and a URL.** A page that could not be read is never written as a result. A salary with no figure is `salary_range: null`.
5. **The legal items are checked per posting.** Since 2024-04-01 a posting must state the scope of change of duties and of work location and the renewal cap of a fixed-term contract; the research also found the posting date and the salary range width often missing. Each is recorded as `stated`, `missing` or `not_applicable` and a missing item is shown as 要確認.
6. **Counts are facts about the queries, never about the market.** The reply states which query returned how many hits, from `search_log`, and never claims completeness. The share of agency-only postings is shown as 不明.
7. **The searcher writes observations; the main session writes everything personal.** The agent receives the anonymised sheet (condition id, kind, text, level) and writes the postings and `must_match`. The main session writes `wishes.json`, the Chrome results and the user's `considering` marks.

## Path resolution

When dispatched from the hub, `{DATA_ROOT}` is already resolved. When started on its own:

```bash
python {HUB_SKILL_DIR}/scripts/jc_config.py --show
```

Exit code 0: use `paths`. Exit code 2: start `job-change-support` with the Skill tool, let it build the configuration, then return. `{SKILL_DIR}` is this skill's absolute path; `{HUB_SKILL_DIR}` is the hub's.

## Data layout

| Path | Contents |
|---|---|
| `career-private/wishes.json` | The condition sheet (`{HUB_SKILL_DIR}/references/wishes-format.md`). Personal information |
| `job-search/{search id}/job_search_results.json` | The search result (`references/job-search-format.md`). `{search id}` is `{YYYYMMDD}-{condition slug}`, for example `20261025-remote-infra` |
| `job-search/{search id}/job_search_results.partial-searcher.json` | The searcher agent's partial file |
| `job-search/{search id}/job_search_results.partial-chrome.json` | The main session's partial file for pages read in Chrome |

## Procedure

### Step 1 The condition sheet

1. When `wishes.json` exists and validates (`python {HUB_SKILL_DIR}/scripts/validate_wishes.py`), show its active conditions in one table (id, text, must/want) and ask once whether to use them as they are or change something. Skip to Step 2 when the user keeps them.
2. Otherwise take the user's one line and map it to the six sheet items: 職種 (`role`), 業界 (`industry`), 年収の下限 (`salary_min`), 勤務地とリモート (`location`, `remote`), 雇用形態 (`employment_type`), その他 (`other`). Each item becomes one condition with `kind`, `field_id`, `operator`, `value`, `text`, `level` as `wishes-format.md` defines.
3. Ask at most two AskUserQuestion questions, only for items the line leaves open. The usual two are the salary floor (offer four amounts around any figure in the line) and the remote arrangement (フルリモートのみ / 週 3 日以上 / 週 1 日以上 / 問わない). Write the question text as a complete Japanese sentence with a concrete example, one decision per question, and run it through the reply lint before asking.
4. Record `salary_min` and `remote` as `must`; `role` as `must`; `industry`, `location`, `employment_type`, `other` as `want` unless the user's words make one a requirement. Write `wishes.json` with the hub's validator passing, and append one `history` entry per new condition.
5. Build the anonymised sheet for the searcher: `[{condition_id, kind, text, level}, ...]` for the active conditions. Nothing else from `wishes.json` leaves the main session.

For `similar_better`, the baseline is a posting that has a posting check (`companies/{slug}/postings/{posting id}/posting-check.json`). Read its `job` values, show them, and ask one question: which items the search should beat (salary floor, annual holidays, remote days, overtime). Add the chosen items as conditions on top of the sheet, and record `baseline.posting_id`.

### Step 2 The searcher agent

Launch one `job-change-job-searcher` (Agent tool; `model` is fixed in its definition). Pass:

- the mode (`fuzzy` or `similar_better`) and, for `similar_better`, the baseline's `job` values as plain text (no personal information is in a posting check);
- the anonymised sheet from Step 1;
- the output directory `{DATA_ROOT}/job-search/{search id}/`, the partial file name `job_search_results.partial-searcher.json`, the `search_id` and `executed_at`;
- `{SKILL_DIR}` (for `references/query-catalog.md`, `references/job-search-format.md`, `references/derivation-lanes.md`);
- the derivation lanes to run, if any. The default is none; offer lanes only when the user asks for a wider search. The ten lanes are in `references/derivation-lanes.md`; pass at most three.

The agent writes the partial file and returns `{"written": ..., "result_count": N, "query_count": M}`. On a harness without sub-agents, read `references/roles/job-searcher.md` and perform the role in the main session.

### Step 3 Pages the agent cannot read (Chrome)

While the agent runs, the main session reads in the user's Chrome the pages WebFetch cannot open: Indeed Japan and Green searches for the same conditions, and any posting URL the user pasted that failed in WebFetch (login, dynamic rendering).

1. Load the tools with one ToolSearch call: `select:mcp__claude-in-chrome__tabs_context_mcp,mcp__claude-in-chrome__tabs_create_mcp,mcp__claude-in-chrome__navigate,mcp__claude-in-chrome__get_page_text,mcp__claude-in-chrome__read_page,mcp__claude-in-chrome__find,mcp__claude-in-chrome__computer,mcp__claude-in-chrome__tabs_close_mcp`. Call `tabs_context_mcp` first, then open a new tab.
2. Open the site's search page, enter the occupation, region and salary floor in its form, and read the first page of results with `get_page_text`. Open each posting that fits the sheet and copy its wording.
3. Write the postings as results with `read_via: "chrome"` and the query as a `search_log` element with `source: "chrome"`, into `job_search_results.partial-chrome.json`, in the same form as the searcher's file. The legal check and `must_match` follow the same rules.
4. Reading a site that refuses automated crawlers in the user's own browser is the user's decision under that site's terms. Say so in one line the first time in a session, and stop if the user declines.

When Chrome is unavailable, skip this step and write in `coverage_notes` that Indeed and Green were not read.

### Step 4 Merge and validate

```bash
python {SKILL_DIR}/scripts/merge_search_results.py {DATA_ROOT}/job-search/{search id} --json
python {SKILL_DIR}/scripts/validate_job_search_results.py {DATA_ROOT}/job-search/{search id}/job_search_results.json
```

Fix any ERROR in the merged file and validate again; a FAIL is never delivered. After PASS: `merge_search_results.py {dir} --cleanup`.

### Step 5 Reply

Reply in Japanese, conclusion first, from `job_search_results.json` alone.

- One table, one row per posting: title, company, site, salary range as published, location and remote wording, `must_match` per required condition (満たす・満たさない・不明), the `missing` legal items as 要確認, and the URL. Derived postings sit below the primary ones under their lane name.
- Below the table: the queries run and their hit counts from `search_log`, in one short table. State that the counts describe the queries and that the share of postings held by agencies is unknown.
- `open_questions` and `coverage_notes` as they stand.
- Ask the user to mark the postings they want to consider (応募を検討したい). Write `true` or `false` into each result's `considering`, validate again, and offer `job-change-posting-check` for the marked postings. Add the search id to the user's record of baselines when the run is the measurement the plan calls for.

Never write 「網羅的に調べた」. Never present the number of results as the size of the market. Never rank the postings; ranking belongs to `job-change-decision`.

## Role execution and model

| Agent | Role prompt | model |
|---|---|---|
| `job-change-job-searcher` | `references/roles/job-searcher.md` | sonnet |

The procedure without sub-agents is the hub's `references/role-execution.md`.

## Scripts

| Script | Use |
|---|---|
| `scripts/merge_search_results.py` | `{dir} [--json]` merges the partial files; `{dir} --cleanup` deletes them. Exit 0 success, 1 failure |
| `scripts/validate_job_search_results.py` | `{file} [--json]`. Exit 0 PASS (WARN only counts as PASS), 1 FAIL |

Unit tests: `cd {SKILL_DIR} && python -m unittest discover -s scripts/tests`. A fictitious example is `assets/job_search_results_example.json`.

## References

| File | Holds | Read at |
|---|---|---|
| `references/job-search-format.md` | The deliverable, the legal check, `must_match`, the merge, the validator | Steps 3 to 5 |
| `references/query-catalog.md` | Sites, URL grammar, robots.txt status, excluded sites, query expansion, dedup, listing closure | Step 2 instructions, Step 3 |
| `references/derivation-lanes.md` | The ten optional lanes that widen or improve the search | Step 2 when the user asks for a wider search |
| `references/search-methods.md` | Why volume is never the goal and why the reply shows the method before the result | Writing Step 5 |
| `{HUB_SKILL_DIR}/references/wishes-format.md` | `wishes.json` | Step 1 |
| `{HUB_SKILL_DIR}/references/pii-boundary.md` | What may be passed to the searcher | Steps 1 and 2 |
| `references/roles/job-searcher.md` | The searcher's role prompt | Step 2 |
