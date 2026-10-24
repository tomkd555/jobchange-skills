---
name: job-change-posting-check
description: >-
  Posting check for a job change in Japan: records one job posting (from a search result, a URL,
  pasted text or a scout mail) and the official figures of the company behind it in one JSON
  (posting-check.json), then matches it against the user's conditions in a separate personal file
  (matches/{posting id}.json). The researcher agent reads the posting, the company's site, the
  有価証券報告書 on EDINET and the MHLW violation list; the main session reads しょくばらぼ and any page
  WebFetch cannot open in the user's Chrome. Official sources only; no news, certifications or
  reviews. Use when the user presents a posting, a company or a scout mail, or asks about a
  company's overtime, salary or results. trigger words: この求人を調べて, 求人票を読んで, 求人チェック,
  この会社を調べて, スカウトメール, 残業と年収の実態, 有価証券報告書.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, AskUserQuestion, Agent, Skill, ToolSearch, mcp__claude-in-chrome__tabs_context_mcp, mcp__claude-in-chrome__tabs_create_mcp, mcp__claude-in-chrome__navigate, mcp__claude-in-chrome__get_page_text, mcp__claude-in-chrome__read_page, mcp__claude-in-chrome__find, mcp__claude-in-chrome__computer, mcp__claude-in-chrome__form_input, mcp__claude-in-chrome__tabs_close_mcp
---

# job-change-posting-check

Turns one posting into the material the user needs to decide whether to apply: the posting's own terms, the company's official figures, the legally required items that are missing, and the match against the user's conditions.

## Principles

1. **One posting, one file.** Each posting gets a posting id `{company slug}-{YYYYMMDD}-{NN}` and its own `posting-check.json` under `companies/{slug}/postings/{posting id}/`. A second posting or a scout mail from the same company is a second file.
2. **Official sources only.** The posting page, the company's own site, EDINET and the IR pages (有価証券報告書), the MHLW list of published 労働基準関係法令違反 and しょくばらぼ. Every value carries the source URL, grade A, the point in time and a quotation. News, certification schemes, review sites and the gender-related disclosure figures are out of scope.
3. **Side by side, never merged.** The same figure from two sources (average tenure in the 有価証券報告書 and in しょくばらぼ) is kept as two entries.
4. **The researcher sees no personal information.** It receives the company name and the posting text or URL. The user's conditions, the match and the unknowns are written by the main session into `career-private/matches/`.
5. **Absence is a finding, never a verdict.** A legally required item the posting lacks is shown as 要確認. A figure no source states is `null` and listed in `unknowns`.
6. **Caveats travel with the figures.** The 有価証券報告書 average salary is the whole legal entity's average and never the posting's salary; the violation list keeps an entry for about one year; a company's claim about itself stays a claim.

## Path resolution

When dispatched from the hub, `{DATA_ROOT}` is already resolved. Otherwise run `python {HUB_SKILL_DIR}/scripts/jc_config.py --show`; on exit code 2 start `job-change-support` first. `{SKILL_DIR}` is this skill's absolute path; `{HUB_SKILL_DIR}` is the hub's.

## Data layout

| Path | Contents | Written by |
|---|---|---|
| `companies/{slug}/postings/{posting id}/posting-check.json` | The posting and the company figures. `references/posting-check-format.md` | researcher agent, then the main session for しょくばらぼ |
| `career-private/matches/{posting id}.json` | Match per condition and the unknown fields. `references/matches-format.md` | main session |
| `career-private/company_index.json` | Name to slug. Hub's `references/company-index-format.md` | main session |

## Procedure

### Step 1 Intake and ids

1. Identify the posting: a result marked `considering: true` in a `job_search_results.json`, a URL, pasted text, or a scout mail. Record `source_type` (`search`, `url`, `text`, `scout`).
2. Resolve the company slug through the hub's procedure ("Company slug resolution" in the hub's SKILL.md; validate `company_index.json` first). Register a new company with its name and the posting's spelling as an alias.
3. Assign the posting id: the slug, today's date as `YYYYMMDD`, and the next two-digit number among `companies/{slug}/postings/` for that date (`01` when none exists). Create the directory.
4. When WebFetch cannot open the posting URL (Indeed, Green, login, dynamic rendering), read it in Chrome first (Step 3, item 2) and pass the text to the researcher as pasted text.

### Step 2 The researcher agent

Launch one `job-change-posting-researcher` (Agent tool). Pass:

- the company name as the posting spells it, and the posting URL or the posting text;
- the output path `{DATA_ROOT}/companies/{slug}/postings/{posting id}/posting-check.json`, the `posting_id`, the `company_slug`, the `source_type` and `source_url`, and `fetched_at`;
- `{SKILL_DIR}` (for `references/posting-check-format.md`) and `{HUB_SKILL_DIR}` (for `references/field-catalog.md` and `references/evidence-grading.md`).

The agent splits the work into four questions (the posting's terms, the legally required items, the 有価証券報告書 figures, the violation list), spends at most eight tool calls per question, and writes the file with every "always write" field present. It returns `{"written": ..., "null_fields": [...]}`. On a harness without sub-agents, read `references/roles/posting-researcher.md` and perform the role in the main session.

### Step 3 しょくばらぼ and unreadable pages (Chrome)

1. Load the Chrome tools with one ToolSearch call (`select:mcp__claude-in-chrome__tabs_context_mcp,mcp__claude-in-chrome__tabs_create_mcp,mcp__claude-in-chrome__navigate,mcp__claude-in-chrome__get_page_text,mcp__claude-in-chrome__read_page,mcp__claude-in-chrome__find,mcp__claude-in-chrome__computer,mcp__claude-in-chrome__form_input,mcp__claude-in-chrome__tabs_close_mcp`), call `tabs_context_mcp`, and open a new tab.
2. For a posting page WebFetch could not open: navigate to the URL, read it with `get_page_text`, and keep the text for Step 2. Reading a site that refuses crawlers in the user's own browser is the user's decision under that site's terms; say so once per session.
3. しょくばらぼ (https://shokuba.mhlw.go.jp/): enter the legal entity name (from the posting check's `legal_entity_name`, or the company name) in the search form, open the company's page, and read three figures: 月平均所定外労働時間 (`monthly_overtime_h`), 有給休暇取得率 (`paid_leave_rate`), 平均勤続年数 (`avg_tenure_years`). Append each as a further entry of the `company` field (an array when the field already has a value), with the しょくばらぼ page URL, grade `A`, the year shown as `as_of` and the figure's wording as `quote`. When the company is absent from しょくばらぼ, add 「しょくばらぼに掲載なし」 to `open_questions`.
4. Close the tab. Validate:

```bash
python {SKILL_DIR}/scripts/validate_posting_check.py {DATA_ROOT}/companies/{slug}/postings/{posting id}/posting-check.json
```

Fix any ERROR and validate again before Step 4.

### Step 4 The match (main session)

1. Read `wishes.json` (validate it with the hub's `validate_wishes.py`). When it does not exist, skip this step, tell the user that `job-change-job-search` or `job-change-decision` creates the condition sheet, and write the match record the next time this posting is checked or when the decision skill starts.
2. For each active condition, compare its `field_id`, `operator` and `value` with the posting check's value of that field: `meets`, `not_meets`, or `unknown` when the value is `null`. A `custom` condition is `unknown` here. Write `note` as one sentence with the two values compared.
3. List in `unknowns` every field id whose value is `null` in every entry of `job` and `company`.
4. Write `career-private/matches/{posting id}.json` and validate:

```bash
python {SKILL_DIR}/scripts/validate_matches.py {DATA_ROOT}/career-private/matches/{posting id}.json --wishes {DATA_ROOT}/career-private/wishes.json --posting-check {DATA_ROOT}/companies/{slug}/postings/{posting id}/posting-check.json
```

### Step 5 Reply

Reply in Japanese, conclusion first. Three tables, built from the two files alone:

1. **求人情報:** the `job` fields with a value, in catalog order, each with its value and unit. The legally required items with `null` are listed as 要確認 under the table.
2. **企業情報:** the `company` fields with a value, one row per entry when a field has two or more sources, with the source name and the point in time. One line under the table: the 有価証券報告書 figures are the whole legal entity's averages, and a violation-list entry stays listed for about one year.
3. **希望条件との照合:** one row per condition: text, must/want, result, note. Then the `unknowns` as 未確認の項目.

End with the next step: another posting to check, or `job-change-decision` once two or more postings have a check. Never state whether the user should apply.

## Role execution and model

| Agent | Role prompt | model |
|---|---|---|
| `job-change-posting-researcher` | `references/roles/posting-researcher.md` | sonnet |

The procedure without sub-agents is the hub's `references/role-execution.md`.

## Scripts

| Script | Use |
|---|---|
| `scripts/validate_posting_check.py` | `{file} [--json]`. Exit 0 PASS (WARN only counts as PASS), 1 FAIL |
| `scripts/validate_matches.py` | `{file} --wishes {wishes.json} [--posting-check {file}] [--json]`. Exit 0 PASS, 1 FAIL |

Unit tests: `cd {SKILL_DIR} && python -m unittest discover -s scripts/tests`. Fictitious examples are under `assets/`.

## References

| File | Holds | Read at |
|---|---|---|
| `references/posting-check-format.md` | `posting-check.json`, the always-write lists, the validator | Steps 2 to 5 |
| `references/matches-format.md` | `matches/{posting id}.json` and its validator | Steps 4 and 5 |
| `{HUB_SKILL_DIR}/references/field-catalog.md` | Field ids, value shape, enumerations and labels | Every step |
| `{HUB_SKILL_DIR}/references/evidence-grading.md` | Grades and the limits of 有価証券報告書 figures | Step 5 |
| `{HUB_SKILL_DIR}/references/pii-boundary.md` | What the researcher may receive | Step 2 |
| `references/roles/posting-researcher.md` | The researcher's role prompt | Step 2 |
