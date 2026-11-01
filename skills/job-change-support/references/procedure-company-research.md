# Company research procedure

Turns one company into a sourced report on what the company is (its business, history, group, sites and stated philosophy) and on the four things a job seeker wants to know before applying: the work in the posted role, overtime and pay as they are, the latest results and risks, and the points to verify in the interview. The procedure is research-team's (parallel collectors with a fixed tool budget, one writer, one verification wave in a fresh context), specialised to one company: the sub-questions are fixed, the sources are graded A to D by `references/evidence-grading.md`, and the scripts are copies under `scripts/research_team/`.

## Principles

1. **One company, one run.** A run lives in `companies/{slug}/research/{YYYYMMDD}/`. A later run on the same company is a new directory; the reply names the earlier one.
2. **Every factual sentence cites evidence a script has checked.** `check.py` matches each quote against the cached page; a sentence cites only items that passed. The key sentences then go to a verifier that sees the sentence and its sources alone.
3. **Grades A to D travel with every item, and C or D never asserts a fact.** A sentence that rests on a review site or hearsay names the source, the response count and the bias (`evidence-grading.md`, "How to write a statement based on C or D"). A statement from the company's own page is presented as a quotation from the company with the page as its source.
4. **The agents see no personal information.** The collectors and the verifier receive the company name, the legal entity, the job title, the run directory and the posting checks under `companies/`. The brief names no person and no condition of the user. The canonical definition is `references/pii-boundary.md`.
5. **Absence is a finding.** What no source states becomes a point to verify in the interview, never a guess.
6. **No verdict on applying.** The report states facts, their sources and their limits. Whether to apply, and how to weigh the findings, stays with the user (the decision procedure).

Out of scope: the gender pay gap, the share of women managers and the male childcare-leave rate; investment advice; the posting's own terms, which the posting check records.

## Data layout

Everything below `{RUN}` = `{DATA_ROOT}/companies/{slug}/research/{YYYYMMDD}/` is written in English, except verbatim quotes and `report.ja.md`. `{SCRIPTS}` = `{SKILL_DIR}/scripts/research_team`.

| Path | Contents | Written by |
|---|---|---|
| `brief.md` | the decision, the sub-questions, the hypotheses, the local materials, notes | main session |
| `collect/{SQ}_web.jsonl`, `collect/searches_{SQ}_web.jsonl` | one collector's evidence items and search log | collector |
| `pages/` | cached page texts (`fetch_page.py`) | collector, verifier |
| `evidence.jsonl`, `digests/{SQ}.md`, `gaps.json` | the merged items with their check, the passing items with context, the gaps | `check.py` |
| `outline.md`, `report.md` | the headings with their evidence ids; the English report | main session |
| `claims/`, `verdicts.json` | the sentences sent to the verifiers and their verdicts | `select_claims.py`, verifier, `apply_verdicts.py` |
| `sources.md` | each cited source with its check result, the gaps, the search log | `report_check.py` |
| `report.ja.md` | the Japanese translation the reply quotes from | main session |

Nothing in `{RUN}` is personal information; the collectors and the verifier read and write there.

## Procedure

Your context is the run's scarcest resource. Read the scripts' summaries, the digests and the agents' return lines; leave raw pages, `evidence.jsonl` and verdict files to the scripts. Run each step's scripts in one Bash call and keep each command under 7,000 characters. While agents run, do the work that does not depend on them; when nothing is left, end the turn with one line on what is running, and resume when their notifications arrive.

### Step 1 Intake and ids

1. Identify the company: a name, a posting id, or a posting check already on disk. Resolve the slug through "Company slug resolution" in SKILL.md.
2. Collect the local materials: every `{DATA_ROOT}/companies/{slug}/postings/*/posting-check.json`. Take `legal_entity_name` and `job_title` from the latest one; when there is none, ask the user for the job title in one line, or write `unknown`.
3. Ask for a focus only when the request names one (「特に残業を」「海外展開を」). It becomes SQ5; otherwise the run has four sub-questions.
4. Get the as-of date with Bash and create `{RUN}`. Write nothing outside it.

### Step 2 Brief

Write `{RUN}/brief.md`:

```markdown
# Brief: {company name}

As of {YYYY-MM-DD}. Legal entity: {legal entity or unknown}. Job title: {job title or unknown}.

## Decision

The user decides whether to apply to {company name} for {job title}, and what to verify in the interview.

## Sub-questions

- SQ1: What is {company name}: its business segments and main products, founding and history, group and parent, sites, employee count, and its stated philosophy as a quotation (有価証券報告書 「事業の内容」「沿革」, the company's 会社概要)?
- SQ2: What is the work in the posted role like at {company name}: the unit's business, products and customers, the workload and the turnover signals?
- SQ3: What are overtime, pay and leave like at {legal entity}, in the official figures (有価証券報告書, しょくばらぼ, the posting) and in secondary sources (news, review aggregates)?
- SQ4: What are the latest results and risks of {legal entity}: revenue and profit trend, 自己資本比率, 事業等のリスク, restructuring, 行政処分, lawsuits, the MHLW violation list?
- SQ5: {the user's focus, when given}

## Hypotheses

- H1: {what the posting or the company's page states, as the posting check quotes it}
- H2: {the opposing reading}

## Local materials

{the posting-check.json paths, or none}

## Notes

{defaults adopted, shortfalls found during the run}
```

### Step 3 Collect (wait 1)

Launch one `job-change-company-collector` per sub-question in one message, `model: sonnet`. Each launch prompt:

```text
Collect evidence for one sub-question, following your agent definition.

- Company: {company name}; legal entity: {legal entity or unknown}; job title: {job title or unknown}
- As-of date: {AS_OF}
- Run directory: {RUN}
- Scripts directory: {SCRIPTS}
- Local materials: {posting-check.json paths, or none}

<assignment>
- Sub-question {SQ}: {text}
- Tool budget: 12
- Evidence path: {RUN}/collect/{SQ}_web.jsonl
- Searches path: {RUN}/collect/searches_{SQ}_web.jsonl
</assignment>
```

Wait for every collector. A collector that returns no files is relaunched once; after a second failure, record the sub-question as a gap in the brief's Notes.

### Step 4 Check and outline

1. `python {SCRIPTS}/check.py --run-dir {RUN}`. Read its summary only.
2. Read `{RUN}/digests/SQ*.md`. Write `{RUN}/outline.md`: the Findings headings in order and, under each, the evidence ids it will use. Put opposing items under the heading they oppose.

### Step 5 Write the report

Write the report once with the Write tool to `{RUN}/draft.md`, then run `mv {RUN}/draft.md {RUN}/report.md && python {SCRIPTS}/report_check.py --run-dir {RUN}` and fix it to 0 failures.

```markdown
# {Company name}: company research

As of {YYYY-MM-DD}. Legal entity: {legal entity}. Job title: {job title}.

## Answer

{One sentence on what the company is, then 3-6 sentences on the four points, each fact with its ids [E3]. Then "Points to verify in the interview:" and a list derived from the gaps and the disagreements, with no ids.}

## Findings

### The company

### The work in the posted role

### Overtime, pay and leave

### Results and risks

### {The user's focus, when SQ5 exists}

## Disagreements and limits

{Opposing evidence the Answer had to weigh; sub-questions with no passing evidence (gaps.json); figures quoted from the company's own pages and single-cluster figures; what the run could not reach.}

Sources, the gaps and the search log: `sources.md`.
```

Rules for the text:

- Every sentence that states a fact ends with the ids it rests on, `[E3]` or `[E3, E7]`. Write each cited sentence from the quote and its context in the digest; the item's claim line points to the passage and is never the source of the wording.
- Cite only items in the digests. Cite a `warn` item only where no `pass` item says the same.
- A sentence resting on a C or D item names the source, the response count and the bias, as `evidence-grading.md` prescribes; it never asserts the fact. A sentence resting on the company's own page quotes the page and cites it.
- Keep the source's scope words and conditions, and name the legal entity, the period and the population a figure holds for. The 有価証券報告書 average salary is the whole legal entity's average; the violation list keeps an entry for about one year.
- Where passing items disagree, present both values and why they differ (definition, period, population).
- The report's own reading goes in a sentence of its own after the facts it rests on, worded as the report's reading, with no ids. The interview points are such readings.
- Write every date as `YYYY-MM-DD` or `YYYY-MM` and every count in Arabic digits, so the translation carries the same numbers.

### Step 6 Verify (wait 2)

1. `python {SCRIPTS}/select_claims.py --run-dir {RUN} --cap 10`.
2. Launch one `job-change-research-verifier` per batch, all in one message, `model: opus`. Pass the paths only; never the report, the brief or any reasoning:

```text
Judge the claims in the batch below, following your agent definition.

- Run directory: {RUN}
- Scripts directory: {SCRIPTS}

<assignment>
- Batch: {RUN}/claims/batch_{k}.json
- Write verdicts to: {RUN}/claims/verdicts_{k}.json
</assignment>
```

3. `python {SCRIPTS}/apply_verdicts.py --run-dir {RUN}`. Resolve any error it lists by relaunching that verifier once. When it fails again, delete its `batch_{k}.json`, re-run the script, and list that batch's sentences under Disagreements and limits as unverified.

### Step 7 Patch and check

1. For each `contradicted` patch whose source is not yet in `evidence.jsonl`: run `python {SCRIPTS}/fetch_page.py --run-dir {RUN} {source} --json`, then Write one evidence item for the found passage (the claim's sub-question, `stance: opposes`, the quote copied from the cached page) to `{RUN}/claims/opposing.jsonl`. Run `python {SCRIPTS}/check.py --run-dir {RUN} --append {RUN}/claims/opposing.jsonl` once for all of them, fix any item it fails, and cite the ids it prints when the sentence states both values.
2. Edit each sentence in the patch list, one Edit per sentence, as its action and the found passage say. Leave every other sentence as it is.
3. `python {SCRIPTS}/report_check.py --run-dir {RUN}`. Fix each failure at its line and re-run until it passes.

### Step 8 Translate

Translate `report.md` in one pass with the Write tool into `{RUN}/draft.ja.md`: keep every heading, every marker `[E..]` in place and every number in Arabic digits exactly as in English (no 万, no kanji numerals, dates stay `YYYY-MM-DD`); keep verbatim quotes and proper names as they are; write in the register of a Japanese business report, with the terms the posting check uses. Then `mv {RUN}/draft.ja.md {RUN}/report.ja.md && python {SCRIPTS}/report_check.py --run-dir {RUN} --translation {RUN}/report.ja.md` and fix each mismatch.

### Step 9 Reply

Reply in Japanese, from `report.ja.md` alone, conclusion first:

1. **結論:** the Answer's sentences on what the company is and on the four points, with their ids.
2. **面接で確かめる点:** the list from the Answer.
3. **異論と限界:** the opposing evidence and the gaps, in up to five lines.
4. **検証:** claims verified, supported, patched (from `apply_verdicts.py`), and one line on the grades used (how many A to D items are cited, from `sources.md`).
5. The paths of `report.ja.md`, `report.md`, `sources.md` and `brief.md`.

Never state whether the user should apply. End with the next step: the posting check for a posting of this company, or the decision procedure once two or more companies have a check.

## Role execution and model

| Agent | Role prompt | model |
|---|---|---|
| `job-change-company-collector` | `references/roles/company-collector.md` | sonnet |
| `job-change-research-verifier` | `references/roles/research-verifier.md` | opus |

The procedure without sub-agents is `references/role-execution.md`. While performing the verifier's role there, read only `claims/` and `pages/` of the run.

## Scripts

All under `{SCRIPTS}` = `scripts/research_team/`, copied from research-team (`NOTICE-research-team.md` beside them). Standard library only; `fetch_page.py` reads PDFs when `pypdf` is installed.

| Script | Use |
|---|---|
| `triage_sources.py` | `--prefix {SQ} {urls} --json`. Orders candidate URLs, one per publisher. Exit 0 something to fetch, 1 nothing |
| `fetch_page.py` | `--run-dir {RUN} {urls} --json`. Caches page text in `pages/`. Exit 0 all cached, 1 some failed |
| `check.py` | `--run-dir {RUN} [--lint FILE | --only SQn | --append FILE]`. Lints items, merges them into `evidence.jsonl`, writes the digests and `gaps.json`. Exit 0 done, 1 failing items (`--lint`, `--append`), 2 usage |
| `select_claims.py` | `--run-dir {RUN} --cap 10`. Writes `claims/batch_*.json`. Exit 0, 2 usage |
| `apply_verdicts.py` | `--run-dir {RUN}`. Merges the verdicts into `verdicts.json` and prints the patch list. Exit 0, 1 verdict errors, 2 usage |
| `report_check.py` | `--run-dir {RUN} [--translation FILE]`. Checks the headings, the markers and the patches; writes `sources.md`. Exit 0 pass, 1 failures, 2 usage |

| Situation | Action |
|---|---|
| WebSearch returns a budget-exceeded string | record it in the brief's Notes; raise `CLAUDE_CODE_MAX_WEB_SEARCHES_PER_SESSION` next time |
| A script exits 2 | read its message, fix the input, re-run once |
| `report_check.py` still fails after two fixes | deliver with the failure stated under Disagreements and limits |
| The run stopped early | resume at the first missing file of `brief.md`, the collect files, `evidence.jsonl`, `outline.md`, `report.md`, `verdicts.json`, `report.ja.md` |

## References

| File | Holds | Read at |
|---|---|---|
| `references/evidence-grading.md` | Grades A to D, the hedged form for C and D, the limits of A | Steps 5 and 9 |
| `references/pii-boundary.md` | What the collectors and the verifier may receive | Steps 3 and 6 |
| `references/company-index-format.md` | The slug | Step 1 |
| `references/posting-check-format.md` | `legal_entity_name`, `job_title` and the figures the collectors read as local material | Step 1 |
| `references/roles/company-collector.md`, `references/roles/research-verifier.md` | The role prompts | Steps 3 and 6 |
