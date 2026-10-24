---
name: job-change-support
description: >-
  The hub skill and entry point for a mid-career job change in Japan. It settles where the user's
  data lives (the configuration gate), resolves company slugs, and routes a request to one of three
  sub-skills: job-change-job-search (find postings from a one-line wish), job-change-posting-check
  (record one posting and the official figures of its company) and job-change-decision (compare two
  to five postings or offers and record the decision). It asks for neither a career record nor the
  user's current employer or salary. Use when the user works on a job change in Japan and the
  request spans the process (where to start, what to do next, several steps at once) or names no
  sub-skill. trigger words: 転職, 転職支援, 転職活動, キャリアチェンジ, 転職の進め方, 何から始めればいい,
  次に何をすればいい。
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, AskUserQuestion, Skill
---

# job-change-support

The entry point of the job-change skill group. It does three things and nothing else: it settles the configuration, it resolves company slugs, and it routes the request to a sub-skill through the Skill tool.

## Principles

1. **The first reply carries a deliverable.** No registration comes before the first search result or the first posting check. The only thing the hub settles first is where the data lives.
2. **The user decides.** The skills list options, state the facts with their sources and ask about trade-offs. Ranking and choosing stay with the user (`job-change-decision`).
3. **Every fact carries a source URL and a grade.** The grade is A (official), B (reliable secondary), C (review sites), D (hearsay); the canonical definition is `references/evidence-grading.md`. The posting check uses grade A sources only.
4. **Personal information never leaves the main session.** The two agents with web tools (`job-change-job-searcher`, `job-change-posting-researcher`) receive the anonymised condition sheet or the company name and posting text, and nothing under `career-private/`. The canonical definition is `references/pii-boundary.md`.
5. **The user's data is JSON with one field catalog.** Four files share the field ids, value shape and enumerations of `references/field-catalog.md`: `wishes.json`, `posting-check.json`, `matches/{posting id}.json` and the decision records. `scripts/export_flat.py` writes them to one CSV.
6. **The hub never asks for the current employer's name or the current salary.** No file records either.

## Out of scope

- Applying, registering with an agency, replying to a scout. The skills prepare material; the user sends.
- Negotiating salary on the user's behalf.
- Legal and visa advice. Point the user to a lawyer, 行政書士 or 社会保険労務士.
- Benefit and training procedures. Point the user to the MHLW page https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/koyou_roudou/koyou/kyushokusha_shien/index.html and to Hello Work.
- New-graduate hiring. The skills assume mid-career hiring.
- Application documents, interview and exam preparation. These return in a later plan.

## Path resolution

Only the configuration file decides where the user's data lives. Wherever a skill writes `{DATA_ROOT}`, read it as the `data_root` that this command returns:

```bash
python {SKILL_DIR}/scripts/jc_config.py --show
```

| Exit code | State | Action |
|---|---|---|
| 0 | Configured | Carry `data_root` forward as `{DATA_ROOT}`; `paths` gives every directory and file |
| 1 | Invalid configuration | Show the `errors` and stop until the file is fixed |
| 2 | Not configured | Build the configuration (next section) |

`{SKILL_DIR}` is this skill's absolute path and `{HUB_SKILL_DIR}` is the same path seen from a sub-skill. The configuration file is specified in `docs/configuration.md`.

## Configuration gate

Before any routing, run `jc_config.py --show`. On exit code 2, ask one AskUserQuestion: where the data should live. Say in the question that the location will hold the user's conditions, the postings they consider and their decisions, and that a folder outside any sync or sharing scope is safer. Offer `~/job-change-data`, `~/Documents/job-change-data` and `./job-change-data`, with any absolute path as the other option. Then:

```bash
python {SKILL_DIR}/scripts/jc_config.py --init --data-root <absolute path>
```

Tell the user the path of the configuration file that was created, and continue.

## Data layout

| Path | Contents | Written by |
|---|---|---|
| `career-private/wishes.json` | The condition sheet: conditions with `must`/`want`, their history, the decisions that used them. Specification `references/wishes-format.md` | job search, decision |
| `career-private/company_index.json` | Company name to slug mapping. Specification `references/company-index-format.md` | hub, posting check |
| `career-private/matches/{posting id}.json` | The match of one posting against the conditions, and its unknown fields. Specification `job-change-posting-check/references/matches-format.md` | posting check (main session) |
| `career-private/decisions/{decision id}.json` | One comparison and its outcome. Specification `job-change-decision/references/decision-format.md` | decision |
| `companies/{company slug}/postings/{posting id}/posting-check.json` | One posting and the company's official figures. Specification `job-change-posting-check/references/posting-check-format.md` | posting researcher, main session |
| `job-search/{search id}/job_search_results.json` | One search run. Specification `job-change-job-search/references/job-search-format.md` | job searcher, main session |
| `export/flat.csv` | Every value of the four JSON types as one row per candidate and field. `scripts/export_flat.py` | hub on request |

Everything under `career-private/` is personal information. `companies/` and `job-search/` hold no personal information; the agents with web tools write only there. Older files from version 1.x (`profile.json`, `axis.json`, `profile_interview_notes.md`, `documents/`) are left where they are and are neither read nor deleted by this version.

## Company slug resolution

A company slug is an optional prefix (one uppercase letter plus `_`) and a body in alphanumerics, hyphens or Japanese characters, for example `S_アクメクラウド`. `company_index.json` maps every name and alias to one slug. Before any per-company work:

```bash
python {SKILL_DIR}/scripts/validate_company_index.py {DATA_ROOT}/career-private/company_index.json
```

On FAIL, repair the list with the user following "Repairing a broken list" in `references/company-index-format.md`. When the list does not exist, create `{"schema_version": 1, "companies": {}}`. Resolve the name in the request against `name` and `aliases`; when there is no match, derive a slug once, register it, and create `companies/{slug}/`. Pass an agent with web tools only the slug, never the list.

## Routing

| Request | Sub-skill | Examples |
|---|---|---|
| Find postings | `job-change-job-search` | 「求人を探したい」「リモート中心で年収 600 万円以上の求人」「もっと良い条件を探したい」 |
| Check one posting or company | `job-change-posting-check` | 「この求人を調べて」「この URL の求人を読んで」「スカウトメールが来た」「この会社の残業と年収の実態は」 |
| Compare and decide | `job-change-decision` | 「2 社で迷っている」「内定をどちらにするか」「何を重視するか整理したい」「価値観を記録したい」 |

A request that names none of these gets the recommended order in one line: search, then check the postings the user wants to consider, then compare. Hand off through the Skill tool with `{DATA_ROOT}` resolved. State the reply from the conclusion; no empty section, no preamble.

## Harness without sub-agents

On a harness that cannot launch sub-agents (Codex), the sub-skill reads the role prompt under its `references/roles/` and performs the role itself. The procedure is `references/role-execution.md`.

## Scripts

| Script | Use |
|---|---|
| `scripts/jc_config.py` | `--show`, `--init --data-root <path>`, `--path <key>`. Exit 0 configured, 1 invalid, 2 unconfigured |
| `scripts/validate_company_index.py` | Validates `company_index.json`. Exit 0 PASS, 1 FAIL |
| `scripts/validate_wishes.py` | Validates `wishes.json`. Exit 0 PASS, 1 FAIL |
| `scripts/field_catalog.py` | Loads `references/field-catalog.md`; imported by every validator |
| `scripts/export_flat.py` | `--data-root {DATA_ROOT} [--out <csv>]`. Writes the four JSON types as one CSV |

Unit tests: `cd {SKILL_DIR} && python -m unittest discover -s scripts/tests`.

## References

| File | Holds |
|---|---|
| `references/field-catalog.md` | Field ids, value shape, common rules, enumerations and their Japanese labels |
| `references/wishes-format.md` | `wishes.json` |
| `references/company-index-format.md` | `company_index.json` and the slug form |
| `references/pii-boundary.md` | The personal-information boundary and each agent's permission |
| `references/evidence-grading.md` | Grades A to D and how to word a claim on each |
| `references/role-execution.md` | Running a role without sub-agents |
