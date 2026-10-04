---
name: job-change-company-research
description: >-
  Sub-skill for company research in a job change. It takes a company name and areas of focus, collects
  information from official materials, news reports, review sites and other sources, and builds a
  company_research.json in which every claim carries a source URL and an evidence level (A = primary/official,
  B = reliable secondary, C = aggregated review-site posts, D = personal blog/hearsay). It runs the result
  through mechanical validation and an independent audit before delivering a topic-organized company research
  report. When given a job posting URL, it imports the job posting into job_posting.json before starting
  research. It covers collecting published figures for the axis metrics it is instructed to cover, and does
  not score, weight, or rate the company (independent of profile). It runs when dispatched by
  job-change-support (the hub).
  Use when the user researches a target company for a job change in Japan (including foreign-affiliated
  selection): its philosophy, business, financials, compensation, benefits, work style, reputation, and
  selection process; or imports a job posting from a URL, and needs sourced, evidence-graded findings.
  trigger words: 企業研究, 会社を調べる, 企業分析, 事業内容, 財務, 平均年収, 有価証券報告書, 評判, 口コミ,
  選考プロセス, 理念, パーパス, 求人URL, 求人票の取り込み, この求人を調べて。
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Agent, AskUserQuestion, Skill
---

# job-change-company-research

This one skill provides the complete procedure for company research in a job change, from collection through delivery. It attaches a source URL and an evidence level to every piece of company information, secures validity through mechanical validation and an independent audit, and delivers a topic-organized company research report.

This skill runs when dispatched by the hub (job-change-support). The company researcher agent (job-change-company-researcher) handles collection and drafting; the research auditor agent (job-change-research-auditor) handles the independent audit. The judgment criteria are self-contained in `references/`.

## Purpose and principles

1. **Attach a source and an evidence level to every claim.** Each claim about a company has a source URL, a quote, an evidence level, and a confidence value. The evidence levels are A = primary/official, B = reliable secondary, C = aggregated review-site posts, and D = personal blog/hearsay/unconfirmed. The canonical definition of the levels, the criteria for assigning them, and the operating rules are in `references/evidence-grading.md`. The hub and each agent treat this file as canonical too.

2. **Do not assert a fact on C or D alone.** Do not assert a fact on review-site posts or hearsay (C or D) alone. Write a statement based on C or D with a hedge (「口コミでは〜という声がある。選択バイアスがあり傍証にとどめる」). Use review-site posts as a supporting signal only under three conditions: the figure is an aggregated overall score, it rests on a sufficient number of responses, and it can be corroborated across multiple sources. Do not use individual posts, aggregates with few responses, or per-facet scores to assert a fact.

3. **Do not give a company's own claim about itself a confidence of high.** A company's claim that presents itself favorably, such as a "good communication culture" statement on its recruiting site, may be untrue even when the source is level A. State in the source that the claim comes from a page the company itself owns, and do not set confidence to high (treat it as B-equivalent). Separate the fact (what the company states, a disclosed figure, whether a certification exists) from the evaluation (whether the culture is actually good) into different claims.

4. **A primary source has limits too.** Even a level-A primary source has limits on representativeness and comparability (the average annual salary in a securities report is a company-wide average and lacks a breakdown by job type). State these limits in the statement or in open_questions.

5. **Do not send personal information externally.** Do not use the user's personal information in any external transmission, including search queries, fetches, and external API calls. The canonical list of what this covers and its exceptions is in the hub's `{HUB_SKILL_DIR}/references/pii-boundary.md`. This skill's job-change-company-researcher and job-change-posting-parser, and the auditor job-change-research-auditor, all hold WebSearch and WebFetch, so none of them receives paths or content under `profile.json`, `axis.json` or `career-private/`. They may receive only the array of axis identifiers from `{AXIS}`'s `company_score_axes` whose `kind` is `quantitative` (the hub reads `{AXIS}`, resolved by the rule in `{HUB_SKILL_DIR}/references/axis-format.md`, section "Location") (the exception this canonical file allows). Areas of focus are given from the user's own instructions.

6. **Collect published figures, with sources, for the metrics of the instructed axes. Do not evaluate or rate.** Company research collects published figures for the quantitative metrics of the axis identifiers given in the instruction, such as `["compensation_level", "annual_holidays"]`. It writes `value`, `unit`, `source_url`, `grade`, and `as_of` into `company_metrics`. When no axes are specified, it collects `compensation_level`. A published figure is a fact about the company and does not depend on the user's profile (desired salary, skills, criteria for changing jobs). This step does not need profile.json or `{AXIS}`; the hub reads `{AXIS}` only to pick the quantitative axis IDs. Scoring, weighting, and the overall score depend on how much weight the user gives each axis, so the fit assessment (job-change-fit-assessment) computes them. The canonical definition of the nine quantitative candidate axes (axis key, metric, unit, direction, source) and the entry format are in `references/company-score-rubric.md`. Set `value` to `null` for an item that cannot be confirmed, and do not enter an estimate or an approximation.

## Out of scope

- **Creating and managing the user's profile and axis.** `job-change-profile` and `job-change-axis` (through the hub, job-change-support) create, update, and validate profile.json and axis.json. This skill does not take either file as input (per principle 5, neither is given to a role with web access).
- **Generating application documents, interview preparation, or exam preparation.** Downstream sub-skills (job-change-documents / job-change-interview-prep / job-change-exam-prep) use the company research result (company_research.json) as grounding; this skill does not run them.
- **Detailed investigation of the selection exam type.** An overview of the selection process (its stages, whether a written test or aptitude test exists) is handled as topic=selection_process. Identifying the exam type (SPI3, 玉手箱 (Tamatebako), and so on) and preparing for it belong to job-change-exam-prep (job-change-exam-scout).
- **Investment advice or ranking companies as better or worse.** Financial information is organized as fact, but this skill does not make a stock-trading judgment or a "good company / bad company" determination.

## Resolving paths

Where the user's data lives is determined solely by the configuration file. There is no default location. Wherever this document writes `{DATA_ROOT}`, read it as the `data_root` value returned by the following command.

When dispatched by the hub (job-change-support), the hub passes in the already-resolved `{DATA_ROOT}`. When started standalone, run the following before any other step of the work.

```bash
python {HUB_SKILL_DIR}/scripts/jc_config.py --show
```

| Exit code | State | Action |
|---|---|---|
| 0 | Configured | The `paths` in the output contains the absolute path for each piece of data. Proceed with the work. |
| 1 | Configured but invalid | Show the user the `errors` in the output and do not proceed until it is fixed. |
| 2 | Not configured | Start `job-change-support` with the Skill tool to have it create the configuration, resolve `{DATA_ROOT}`, then return here. |

`{SKILL_DIR}` refers to this skill's own absolute path; `{HUB_SKILL_DIR}` refers to the absolute path of `job-change-support`, located alongside it. The canonical specification of the configuration file, including its lookup order, is in `docs/configuration.md`.

## Intermediate artifact: company_research.json

All company research judgments are gathered into `company_research.json`. Its output location is `{DATA_ROOT}/companies/{company slug}/company_research.json`. The company slug is the identifier used as the per-company directory name; its canonical format is defined in job-change-support's `references/company-index-format.md`. Step 0 resolves it by looking it up in `career-private/company_index.json`, and it is never re-derived afterward (example: a fictional company 架空クラウドワークス株式会社 → `kakuu-cloudworks`, `S_アクメクラウド`).

```json
{
  "company": { "name": "", "securities_code": "", "edinet_code": "" },
  "research_date": "YYYY-MM-DD",
  "claims": [
    { "id": "C001", "topic": "philosophy", "statement": "反証可能な命題",
      "evidence": [ { "source_url": "https://...", "source_name": "", "grade": "A", "quote": "引用", "accessed": "YYYY-MM-DD" } ],
      "confidence": "medium" }
  ],
  "company_metrics": {
    "compensation_level": { "value": 6120000, "unit": "円", "source_url": "https://...", "grade": "A", "as_of": "2026-03" },
    "annual_holidays": { "value": null, "unit": "日", "source_url": null, "grade": null, "as_of": null }
  },
  "open_questions": [ "" ]
}
```

There are eight kinds of `topic`: `philosophy`, `business`, `financials`, `compensation`, `benefits`, `workstyle`, `reputation`, and `selection_process`. `company_metrics` holds the measured figures for the quantitative candidate axes (principle 6, above). The canonical definition of the complete field specification, entry criteria, and validation rules is in `references/company-research-format.md`; a worked example (a fictional company) is in `assets/company_research_example.json`.

## Pipeline

As a sub-skill, proceed through Step 0 through Step 4 below in order. Read `{SKILL_DIR}` as this skill's own absolute path, and `{company_research.json}` as the artifact's path (`companies/{company slug}/company_research.json`).

### Step 0: Intake

Confirm the following. Ask about anything unclear mainly through multiple-choice questions with AskUserQuestion, up to 4 questions with up to 4 choices each.

- The target company's name (its formal name). When it is ambiguous (a group company, a holding company, or another company sharing the name exists), list the candidates and confirm.
- Areas of focus, if any: which of philosophy, business, financials, compensation, benefits, work style, reputation, or selection process to weight more heavily. When none is specified, treat all eight topics equally.
- How the job posting will be obtained. Accept a job posting URL, the pasted text of the job posting, or a PDF or image file. When none of these is available, confirm only that fact, since Step 0.5 fills the gaps through dialogue.

Resolve the company slug in `career-private/company_index.json`. When the company name matches `name` or `aliases` in the index, use that slug; only when there is no match, derive one exactly once, register it in the index, and create `companies/{company slug}/` (see job-change-support's `references/company-index-format.md` for details).

### Step 0.5: Job posting intake (required)

Job posting intake is the first stage of the per-company pipeline. The `job_posting.json` built here is read as input by the company research and fit assessment that follow. Do not skip intake and move ahead.

There are four entry points. This skill selects an entry point according to what material the user can provide, and builds the same `job_posting.json` in every case. The specification is in `references/job-posting-format.md`.

| Entry point | `source_type` | Handler |
|---|---|---|
| A job posting URL | `url` | job-change-posting-parser |
| The pasted text of the job posting | `text` | This skill |
| A PDF or image of the job posting | `file` | This skill |
| Company name only (the job posting cannot be identified) | `dialogue` | This skill |

**When the entry point is a job posting URL (job-change-posting-parser, sonnet).** Launch the job posting intake agent with the Agent tool, passing it the job posting URL and `{SKILL_DIR}` (the location of `references/job-posting-format.md`). The agent fetches the page with WebFetch and returns a JSON of `{company_name, aliases, job_posting}` (it does not write a file). **Do not pass it the user's personal information (the items listed in principle 5)**, since posting-parser holds WebFetch. Use the returned `company_name` and `aliases` to resolve the slug through the same procedure as Step 0 (deriving and registering one exactly once, only when there is no match).

**When the entry point is the pasted text or a file of the job posting.** This skill assembles the `job_posting` object according to the specification. It reads the pasted text as the user gave it, and reads a file with Read. It sets `source_type` to `text` or `file`, and sets `source_url` to null. It uses the company name and slug already confirmed and resolved in Step 0. It fills `scope_of_change` with the scope of change to duties and work location and the cap on contract renewal. The entry criteria are in the section of the same name in `references/job-posting-format.md`.

**When only the company name is available.** Confirm the applied position (`title`) through dialogue, and fill only the items among salary, location, employment type, and requirements that the user can answer. Set `source_type` to `dialogue` and `source_url` to null. Fill `scope_of_change` (the scope of change to duties and work location, and the cap on contract renewal) as far as the user can answer by looking at the job posting. The entry criteria are in the section of the same name in `references/job-posting-format.md`. Do not fill an item the user could not answer with an estimate; write what remains unconfirmed into `open_questions`. Accept a job posting with sparse content as it stands. Carry unconfirmed items forward as items to confirm in the company research and interview that follow.

**Common follow-up.**

1. This skill writes the assembled `job_posting` object to `companies/{company slug}/job_posting.json` with Write (only after the slug is resolved).
2. Validate it with the following command and confirm a PASS (zero ERRORs). If there is an ERROR, send it back to posting-parser for the URL entry point, or have this skill fill it in again for any other entry point, and leave a gap that cannot be filled in `open_questions`.

   ```bash
   python {SKILL_DIR}/scripts/validate_job_posting.py {job_posting.json} --json
   ```

3. Update `artifacts.job_posting` in `companies/{企業スラッグ}/_manifest.json` to `{updated_at: 取得日, source_url: 取り込んだ求人URL}` (see "Updating _manifest.json" below). Set `source_url` to null for any entry point other than a URL.

The imported job posting is used in the Step 1 collection to cross-check the selection process and the desired candidate profile. `job_posting.metrics` (annual holidays, overtime, paid-leave-taking rate, and days granted) provides supporting material for company_research's `company_metrics`.

### Step 1: Collection and drafting (job-change-company-researcher, opus)

Launch the company researcher agent (job-change-company-researcher) with the Agent tool and have it build company_research.json. Pass the following in the brief.

- The company name (its formal name), areas of focus (if any), the output directory, and the location of the job posting (if any).
- The array of axis identifiers for which to collect measured figures (such as `["compensation_level", "annual_holidays"]`; the hub takes them from the `quantitative` axes of `{AXIS}`). When the caller specifies no axes, pass `["compensation_level"]`. Do not pass the description of a qualitative axis the user defined, since it reflects the user's own situation and the fit assessment makes that judgment. When something related to a qualitative axis needs investigating, the user gives it as an area of focus in their own words.
- This skill's absolute path `{SKILL_DIR}` (the location of references and scripts).

Normalize areas of focus into a weight-of-emphasis specification across the eight topics (philosophy, business, financials, compensation, benefits, work style, reputation, selection) before passing them. Rephrase personal information from the user's free-form description as a weight-of-emphasis specification for the relevant topic (principle 5; the canonical definition is in `{HUB_SKILL_DIR}/references/pii-boundary.md`), and pass only that specification in the brief.

**Do not pass profile.json or axis.json** (principle 5; the researcher holds WebSearch and WebFetch). When job_posting.json was built in Step 0.5, pass its location in the brief and have the agent use it to cross-check the selection process and the desired candidate profile. The agent treats `references/evidence-grading.md`, `references/company-research-format.md`, `references/source-catalog.md`, `references/philosophy-analysis.md`, `references/compensation-benefits.md`, and `references/company-score-rubric.md` as canonical, and follows them to gather the collected claims into the claims array. Store figures such as average annual salary, annual holidays, average monthly overtime, paid-leave-taking rate, and turnover rate both in a prose claim and in structured form in `company_metrics`. Note the unit, source URL, and level with each figure, and set value to null when it cannot be confirmed.

Give priority to collecting the metrics for the axes given in the brief, and write the measured figure and its source into each item of `company_metrics` (principle 6: a fact about the company, which does not depend on the profile). Attach no score and no rating. For anything given as an area of focus, write into claims the facts and sources that could be confirmed. Have the agent run `validate_company_research.py` itself and get a PASS before returning (a missing or malformed `company_metrics` is an ERROR). This is the extent of this agent's responsibility.

### Step 2: Mechanical validation

Validate the company_research.json the researcher returned, on the orchestrator side as well.

```bash
python {SKILL_DIR}/scripts/validate_company_research.py {company_research.json} --json
```

Send it back to Step 1 when there is even one ERROR. Do not proceed until it reaches a PASS (zero ERRORs). A WARN alone counts as a PASS, but record its content and prompt for additional supporting evidence on the topic when needed.

### Step 3: Independent audit (job-change-research-auditor, opus)

Launch the research auditor agent (job-change-research-auditor) in a new context that withholds the researcher's rationale. Pass the brief the absolute path of company_research.json, the array of axis identifiers whose collection was instructed in Step 1, and `{SKILL_DIR}`.

The audit does the following. The verdict returns as `BLOCK` / `CONCERNS` / `CLEAN`.

- Rerunning `validate_company_research.py` (recording the result as `validation_rerun`: PASS when there are zero ERRORs, FAIL otherwise). When `validation_rerun` is FAIL, the verdict is unconditionally BLOCK.
- Stratified sampling of claims, confirming that each source URL exists and that its quote matches the original text (the sample must always include level-A financial claims and claims with confidence=high).
- The validity of the assigned levels (whether a review-site post has been upgraded to A or B, or a primary source downgraded to C).
- Whether a fact is asserted on level C or D alone, and whether confidence high has been given to a claim in which the company presents itself favorably.
- Coverage of the seven required topics (`philosophy`, `business`, `financials`, `compensation`, `benefits`, `workstyle`, `reputation`), and how well `selection_process` is filled in (zero items counts as a WARN-level issue, and collecting it is recommended). Do not treat a missing `selection_process` as critical.
- The validity of `company_metrics` (against the standard in `references/company-score-rubric.md`). Check whether each measured figure matches what its source states, whether the assigned evidence level is appropriate, and whether the metrics for the instructed axes have been collected, with nothing missing and nothing extra.

Send it back to Step 1 when the verdict is `BLOCK`, or when there is a finding with severity=重大. When sending it back, pass the researcher the audit's findings (target, evidence, fix) as they are.

### Step 4: Delivery

Format company_research.json into the human-readable company research report `companies/{company slug}/company-research-report.md` and deliver it.

- At the top, show the measured figure, unit, source, evidence level, and point in time for each axis. For an axis that could not be confirmed, write 「確認できず」. Add, one sentence each, that this is a fact about the company, separate from the user's fit, and that the fit assessment is responsible for scoring and computing the overall score.
- Arrange claims by topic (philosophy, business, financials, compensation, benefits, work style, reputation, selection process), presenting the claim, its source, its level, and its confidence in a readable form.
- State the open_questions explicitly (points that could not be corroborated, discrepancies between sources, and the limits of a primary source's representativeness).
- Keep the hedge in place, in the report too, for anything based on C or D (「口コミでは〜という声がある。傍証にとどめる」).

At delivery, update `artifacts.company_research` in `companies/{company slug}/_manifest.json` (see "Updating _manifest.json" below). Set `updated_at` to the research date, and set `last_researched` to the research date for each topic that was researched. Also write the verdict obtained from the Step 3 audit into `audit_verdict`, and the date it was audited into `audited_at`. When it was sent back and re-audited, write the verdict and date of the last audit.

Do not change the company slug prefix (the directory name). Do not write a company's score or rating into the classification or listing fields of `career-private/company_index.json`, because the fit assessment is what computes the score.

Summarize the following in the final message.

- The key points of the measured figures and sources for each axis
- The key points of the main topics
- The validation result (the validate PASS and the audit verdict)
- Any remaining open items (a point not resolved after two rounds of sending back)

Both the report and the final message state their conclusion first. Leave out empty sections, repeated content, and boilerplate preambles.

## Updating _manifest.json

`companies/{company slug}/_manifest.json` is a record holding the last-updated date of each per-company artifact and the last-researched date of each company_research topic. This skill writes this record; determining whether re-research is needed is the hub's responsibility, and this skill does not make that determination.

The structure is as follows. Use the existing company_research topic names (`philosophy`, `business`, `financials`, `compensation`, `benefits`, `workstyle`, `reputation`, `selection_process`) as topic names.

```json
{
  "schema_version": 1,
  "artifacts": {
    "job_posting": { "updated_at": "YYYY-MM-DD", "source_url": "https://..." },
    "company_research": {
      "updated_at": "YYYY-MM-DD",
      "audit_verdict": "CLEAN",
      "audited_at": "YYYY-MM-DD",
      "topics": { "financials": { "last_researched": "YYYY-MM-DD" } }
    }
  }
}
```

- Create `_manifest.json` if it does not exist. When it exists, update only the relevant part and preserve the record of other artifacts (such as `fit_assessment`).
- Update `artifacts.job_posting` when job_posting.json was built in Step 0.5.
- At Step 4 delivery, update `artifacts.company_research.updated_at` and `topics.<topic name>.last_researched` for each topic that was researched. In the same update, also write `audit_verdict` (the Step 3 verdict, one of `CLEAN`, `CONCERNS`, or `BLOCK`) and `audited_at` (the date it was audited). When it was sent back and re-audited, overwrite these with the result of the last audit.

### Topic-scoped incremental re-research

When the caller (the hub) specifies a target topic, re-research only that topic.

1. Launch the Step 1 researcher with only the specified topic as the area of focus, and obtain the claims for that topic.
2. Read the existing company_research.json, replace (merge) only the specified topic's claims, and leave the claims of every other topic unchanged.
3. Re-fetch the `company_metrics` items that correspond to the specified topic, and update their value, source URL, level, and point in time (`as_of`). Leave items outside the scope of re-fetching unchanged. Reset `value` to `null` for an item that can no longer be confirmed.
4. Run the Step 2 mechanical validation again and confirm a PASS.
5. Update only `artifacts.company_research.topics.<specified topic>.last_researched` in `_manifest.json` (leave `last_researched` for every other topic unchanged). Set `updated_at` to this research date.

The hub determines which topic needs re-research and instructs it; this skill handles re-researching the specified topic and updating the record.

## Pass/fail gates and send-backs

The pipeline has two gates.

| Gate | Passing condition and send-back destination |
|---|---|
| The Step 2 mechanical validation gate | Do not proceed to Step 3 or any later step unless `validate_company_research.py` reaches a PASS (zero ERRORs). Send an ERROR back to Step 1. |
| The Step 3 independent audit gate | Send it back to Step 1 when `job-change-research-auditor`'s verdict is `BLOCK`, or when there is a finding with severity=重大. |

Send a company's research back at most twice. Record a finding not resolved after two rounds into company-research-report.md's open items, and deliver only after leaving the judgment to the user. Resolve a mechanical-validation ERROR before delivery regardless of the send-back limit; delivery is allowed, with the item stated explicitly as an open item, only when what remains unresolved is solely an audit finding. When sending back, pass the researcher the mechanical validation's ERROR content or the audit's findings as they are, and run it through Step 2 again after the fix.

## Executing the role (by harness)

This skill's pipeline is written to delegate the work to specialized roles. The content of each role is in `references/roles/`, which is canonical.

| Agent name | Canonical role prompt |
|---|---|
| `job-change-company-researcher` | `{SKILL_DIR}/references/roles/company-researcher.md` |
| `job-change-research-auditor` | `{SKILL_DIR}/references/roles/research-auditor.md` |
| `job-change-posting-parser` | `{SKILL_DIR}/references/roles/posting-parser.md` |

The canonical definition of the execution procedure by harness, how to decide how many to launch, and the reason for separating drafting from auditing is in the hub's `{HUB_SKILL_DIR}/references/role-execution.md`.

## Agent model policy

| Agent | model | Responsibility |
|---|---|---|
| `job-change-company-researcher` | opus | Collecting primary and secondary-or-lower information → building company_research.json with sources and assigned levels |
| `job-change-research-auditor` | opus | Auditing source existence, quote agreement, level validity, and topic coverage, in an independent context |
| `job-change-posting-parser` | sonnet | Fetching the job posting URL → assembling an object conforming to the job_posting.json specification (does not write a file) |

This policy is fixed in each agent's frontmatter, and `model` is never overridden at launch.

## Script CLI usage examples

Validating company research data (the exit code is 0 for a PASS, 1 for a FAIL; a WARN alone counts as a PASS). Read `{SKILL_DIR}` as this skill's own absolute path, and `{company_research.json}` as the path of the target being validated.

```bash
python {SKILL_DIR}/scripts/validate_company_research.py {company_research.json}
python {SKILL_DIR}/scripts/validate_company_research.py {company_research.json} --json
python {SKILL_DIR}/scripts/validate_job_posting.py {job_posting.json}
python {SKILL_DIR}/scripts/validate_job_posting.py {job_posting.json} --json
```

`--json` outputs the result in JSON form (`status`, `error_count`, `warning_count`, `errors`, `warnings`). A worked example is in `assets/company_research_example.json`. The canonical field specification and validation rules are in `references/company-research-format.md` (company research) and `references/job-posting-format.md` (job posting intake). Run the unit tests with the following.

```bash
cd {SKILL_DIR} && python -m unittest discover -s scripts/tests
```

## References list

| File | What it covers | When to read it |
|---|---|---|
| `references/evidence-grading.md` | The definitions of evidence levels A through D, the criteria for assigning them, the prohibition on asserting a fact from C/D alone, the confidence limit on a claim in which a company presents itself favorably, cross-checking sources, and corroborating findings (review-site selection bias, the validity of an aggregated score, the limits of a securities report) | Every stage that assigns or checks a level and a confidence |
| `references/company-research-format.md` | The field specification, entry criteria, and mechanical validation rules for company_research.json | Every stage that writes, reads, or validates company_research.json |
| `references/source-catalog.md` | The source catalog (EDINET securities reports, IR disclosures, Shushoku Shikiho, Shokuba Labo, certification schemes, review sites) and each source's content, limits, and source URL | The Step 1 collection, the Step 3 audit |
| `references/philosophy-analysis.md` | The collection sources and analysis procedure for philosophy, corporate creed, and purpose analysis (explicit statement → behavioral guidelines → HR systems → consistency check against disclosures), and its relationship with the confidence limit on a claim in which a company presents itself favorably | Collecting and analyzing topic=philosophy |
| `references/compensation-benefits.md` | The investigation perspectives and source catalog for compensation, benefits, and work style (securities reports, Shokuba Labo, certification schemes, Shushoku Shikiho, OpenWork, public statistics), and the rule for storing figures into company_metrics | Collecting topic=compensation/benefits/workstyle |
| `references/company-score-rubric.md` | The definition of the nine quantitative candidate axes (axis key, metric, unit, direction, source), the entry format for `company_metrics`, and the division of labor by which the fit assessment handles scoring, weighting, and the overall score | Collecting measured figures in Step 1, auditing company_metrics in Step 3 |
| `references/job-posting-format.md` | The field specification, entry criteria, and mechanical validation rules for job_posting.json (including the four entry points and `source_type`) | The stage of importing and validating a job posting in Step 0.5 |
