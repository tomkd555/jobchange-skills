---
name: job-change-exam-prep
description: >-
  Sub-skill for written-test and aptitude-assessment preparation in Japanese mid-career hiring. It identifies
  the assessment type used by the target company (SPI3, 玉手箱 (Tamatebako), GAB/CAB, TG-WEB, TAL, 内田クレペリン検査 (Uchida-Kraepelin),
  personality tests, foreign-affiliated online assessments) through domain detection of the exam-invitation
  URL and investigation by the job-change-exam-scout agent, builds a preparation plan per assessment type
  (subject-level study items, time allocation, materials policy, schedule), and practices with self-made
  questions that mimic the question format. It distinguishes confirmed information from estimates, and
  follows the difference in preparation per assessment type: repeated practice for ability tests (能力検査), consistent
  honest answers for personality tests. It does not reproduce real exam questions. Used when routed from the
  hub (job-change-support).
  Use when the user prepares for a written test or aptitude assessment in a Japanese mid-career job change
  (including foreign-affiliated online assessments) — identifying which test a company uses, building a
  study plan, and practicing question formats.
  trigger words: 適性検査, 適性検査対策, 筆記試験, SPI, SPI3, 玉手箱, GAB, CAB, TG-WEB, TAL,
  内田クレペリン, WEBテスト, テストセンター, ケース面接, フェルミ推定。
allowed-tools: Read, Write, Glob, Grep, Bash, Agent, AskUserQuestion, Skill
---

# job-change-exam-prep

When preparing for a written test or aptitude assessment in mid-career hiring, this skill covers everything from identifying the assessment type through building a preparation plan and practicing. It focuses on assessments used in Japanese mid-career hiring and also handles foreign-affiliated online assessments.

Assessments differ in question format and in how well preparation works, depending on type. The skill proceeds in this order: identify the assessment type used by the target company, build a preparation plan matched to the type, then practice with self-made questions that mimic the question format. Investigating the assessment type is delegated to the dedicated agent `job-change-exam-scout`; this skill handles launching it, reconciling its results, building the plan, and running practice.

## Purpose and principles

1. **Identify the assessment type first.** Preparation depends on the assessment type, so study items are not decided before the type is settled. If an exam-invitation URL is available, the domain detection in `references/domain-detection.md` immediately narrows down the family, and investigation by `job-change-exam-scout` confirms and reinforces the type. Confirmed information (explicitly stated on the careers page, etc.) is distinguished from estimates (inferred from candidate write-ups); estimates are never written as if they were confirmed.

2. **Separate preparation by assessment type.** Ability tests (SPI3, 玉手箱 (Tamatebako), TG-WEB, GAB, CAB, etc.) are tests where scores rise with repeated practice. Personality tests, TAL, and 内田クレペリン検査 (Uchida-Kraepelin), by contrast, are tests where preparation has little effect; for personality tests specifically, consistent honest answers are recommended. Whether faking (distorting answers) affects validity is not academically settled. Both views are presented together in `references/prep-methods.md`.

3. **Do not reproduce real exam questions.** Practice is done with self-made questions that mimic the question formats shown in `references/assessment-catalog.md`. Reproducing real exam questions or copyrighted material, taking an exam on the user's behalf, or exam impersonation are not performed.

4. **Do not send personal information externally.** The user's personal information is never used in any external transmission, including search queries, fetches, or external APIs. The canonical definition of what this covers and which roles may or may not handle it lives in the hub's `{HUB_SKILL_DIR}/references/pii-boundary.md`. `job-change-exam-scout` has WebSearch and WebFetch. For this reason, paths and contents under `career-private/` and `profile.json` are not passed to this agent. The Step 1 instructions pass only the company name, applied role, and job posting. This skill does not require `profile.json` as a prerequisite. Even when it is consulted to understand the applied role, its contents are not passed to any procedure with web-sending capability.

5. **Vendor-published figures are treated as self-reported.** Numbers such as completion rates or sample sizes published by an assessment vendor or a preparation outlet are treated as self-reported figures that have not passed independent verification, and are not used as grounds for an assertion.

## Out of scope

The following are out of scope for this skill. When requested, the skill states that it cannot handle them.

- **Taking an exam on the user's behalf, exam impersonation, or misconduct.** Taking an assessment in place of the user, exam impersonation, and evading proctoring are not handled.
- **Rehearsing answers for the actual interview.** Preparation for the interview itself is handled by `job-change-interview-prep`. For case interviews and Fermi estimation, this skill covers the thinking pattern as part of written/online screening. Rehearsed answers for follow-up probing during an interview are delegated to `job-change-interview-prep`.
- **Company research and document creation.** These are handled by `job-change-company-research` and `job-change-documents` respectively.
- **Predicting or guaranteeing pass/fail or scores.** A preparation plan is a study policy; it does not predict or guarantee pass/fail or scores.

## Path resolution

Where the user's data is stored is decided solely by the configuration file. There is no default location. Wherever this document writes `{DATA_ROOT}`, read it as the `data_root` returned by the following command.

When routed from the hub (job-change-support), the hub passes the already-resolved `{DATA_ROOT}`. When launched standalone, run the following before any other step of the work.

```bash
python {HUB_SKILL_DIR}/scripts/jc_config.py --show
```

| Exit code | State | Action |
|---|---|---|
| 0 | Configured | The `paths` in the output hold the absolute path for each data item. Proceed with the work |
| 1 | Configuration exists but is invalid | Show the `errors` in the output to the user, and do not proceed until the user fixes the configuration |
| 2 | Not configured | Launch `job-change-support` with the Skill tool to create the configuration, resolve `{DATA_ROOT}`, then return |

`{SKILL_DIR}` refers to this skill's own absolute path, and `{HUB_SKILL_DIR}` refers to the absolute path of `job-change-support` in the same installation. The configuration file's specification, including its search order, lives in `docs/configuration.md`.

## Intermediate deliverables

Per-company deliverables are placed under `{DATA_ROOT}/companies/{company slug}/`. The company slug follows the same convention as the hub and is resolved via `career-private/company_index.json` (e.g., fictional CloudWorks Inc. → `kakuu-cloudworks`).

| Path | Content | Step that produces it |
|---|---|---|
| `companies/{company slug}/exam_assessment.json` | Investigation results on assessment type (type, stage, source URL, confidence, question format, recommended preparation) | Step 1 (written out by `job-change-exam-scout`) |
| `companies/{company slug}/exam-prep-plan.md` | Preparation plan (study items, time allocation, materials policy, schedule per assessment type) | Step 2 |

For a generic preparation request where no company can be identified, deliverables are placed under `_general/`, which takes the company slug's place in the path.

## Pipeline

Proceed through Step 0 to Step 3 in order.

### Step 0 Intake

Confirm the following. Confirmation is done mainly through multiple-choice questions via AskUserQuestion, at most 4 questions with 4 options each.

- Target company name (official name). Distinguish whether this is generic preparation with no company decided, or preparation for a specific company.
- Applied role (general track, engineering track, etc. This affects the CAB/GAB distinction and assessment-tendency judgment).
- Whether an exam-invitation URL exists. Whether there is an invitation email or a URL for the assessment page.

If an exam-invitation URL exists, check it against the domain-detection table in `references/domain-detection.md` to immediately determine the family, and state the confidence explicitly. Detection is done by matching the URL string only; it involves no external access to the URL and no external transmission of the profile. The detection result is provisional, and its confidence is set to `推定` (estimate). Also convey that the Japan SHL family (`e-exam`, `nsvs`, `tsvs`) can only be narrowed to one of 玉手箱 (Tamatebako), GAB, or CAB; that paper-format tests cannot be detected from a URL; and that an assessment vendor may change its domain. Confirmation happens through the investigation in Step 1.

For a specific-company request, before resolving the slug, validate the index with `validate_company_index.py`. On FAIL (1 or more ERRORs), show the findings to the user and do not proceed to resolution until the user fixes the index. Then resolve the company slug via `career-private/company_index.json`. If the company name matches an entry in the index, use that slug; if not, derive one once and register it. Details are in job-change-support's `references/company-index-format.md`.

Once the slug is resolved, check whether `companies/{company slug}/company_research.json` exists. If it does, judge that company's `_manifest.json` with `check_freshness.py`. If any topic is `stale`, show this fact and the affected topic names to the user, and propose an incremental re-investigation of the stale topics with `job-change-company-research`. If the user chooses to proceed without re-investigating, state clearly in the `exam-prep-plan.md` from Step 2 that the plan relies on outdated information, naming the affected topics. The canonical definition of the judgment rules and TTLs is in job-change-support's `references/freshness-policy.md`.

```bash
python {HUB_SKILL_DIR}/scripts/validate_company_index.py {DATA_ROOT}/career-private/company_index.json
python {HUB_SKILL_DIR}/scripts/check_freshness.py {DATA_ROOT}/companies/{company slug}/_manifest.json
```

`validate_company_index.py` exits 0 on PASS and 1 on FAIL (WARN only is treated as PASS). `check_freshness.py` always exits 0, and its output classifies each topic as `fresh`, `stale`, or `missing`.

`profile.json` is optional for this skill. It may be consulted to understand the applied role, but its content is not passed to the Step 1 agent (principle 4).

### Step 1 Investigating the assessment type

Launch the `job-change-exam-scout` agent (model: sonnet) with the Agent tool to investigate the assessment types used in the target company's mid-career hiring process.

- What the instructions pass: the company name (official name), the applied role (if known), and the job posting (if available). Also pass this skill's absolute path (`{SKILL_DIR}`, for the location of `references/exam-assessment-format.md` and `scripts/`), and job-change-company-research's absolute path (for the location of `references/evidence-grading.md`). If `companies/{company slug}/company_research.json` exists, also pass a summary of the claims under topic=selection_process. The summary carries three items: the claim, the source URL, and the evidence level. This summary is passed so that evidence already gathered is not discarded and re-investigated from scratch. Because this summary is public information about the company and contains no personal information, it may be passed to an investigation role that has web tools. `profile.json` is not passed (principle 4).
- When the investigation results conflict with the passed claims, the one with the higher evidence level is adopted. If the levels are equal, the more recently investigated one is adopted, and both claims plus the reason for the choice are recorded in `exam_assessment.json`'s `open_questions`.
- Output destination: the agent writes the results to `{DATA_ROOT}/companies/{company slug}/exam_assessment.json` and returns the same JSON.
- The canonical definition of the output JSON's format (field specification, entry criteria, mechanical validation rules) is in `references/exam-assessment-format.md`. A filled-in example (fictional data) is in `assets/exam_assessment_example.json`.

After receiving the agent's response, validate the deliverable it wrote. On FAIL (1 or more ERRORs), do not proceed to Step 2; send it back to the agent along with the findings.

```bash
python {SKILL_DIR}/scripts/validate_exam_assessment.py {DATA_ROOT}/companies/{company slug}/exam_assessment.json
```

Exit code 0 means PASS, 1 means FAIL (WARN only is treated as PASS). A WARN lets the deliverable proceed; reflect it in the preparation plan at Step 2 (e.g., a type backed by only a single piece of evidence, or an exam name not covered by `assessment-catalog.md`).

If the company cannot be identified and this is a generic preparation request, skip this step. Proceed to Step 2 using the provisional detection from `references/domain-detection.md` (if a URL exists) and basic preparation assuming the most common assessments (SPI3, 玉手箱 (Tamatebako)).

### Step 2 Building the preparation plan

Cross-reference `exam_assessment.json`'s `assessments` against `references/assessment-catalog.md` and `references/prep-methods.md`, and build a preparation plan per assessment type. The plan includes the following.

| Component | Content |
|---|---|
| Study items by subject | For each subject tested by the assessment type (verbal, non-verbal, quantitative, English, rule-inference, instruction tables, code-breaking, etc.), list the items to master. Base this on the question formats in `references/assessment-catalog.md`. |
| Time allocation | Based on the administration method and time-limit characteristics (for tests like 玉手箱 (Tamatebako) and TG-WEB, which present the same format in rapid succession under short time limits, time management is a key point), show a time allocation for study and practice by subject. |
| Materials policy | Show the standard family of materials matched to the assessment type (`references/prep-methods.md`). For assessments where preparation is difficult (TAL, etc.), state this explicitly and avoid over-investing in materials. |
| Schedule | Show a study sequence matched to the number of days until the exam. Prioritize ability tests where repeated practice is effective; for personality tests, limit the plan to confirming the answering approach. |

Following the difference in how well preparation works (`references/prep-methods.md`), do not recommend excessive preparation for personality tests, TAL, or 内田クレペリン検査 (Uchida-Kraepelin). For personality tests, recommend consistent honest answers.

Distinguish confirmed information from estimates. For a type whose `confidence` is `推定` (estimate), state in the preparation plan that it is an estimate, the number of supporting pieces of evidence, and the confidence level, and do not assert it with the same certainty as a confirmed type. When the provisional detection from Step 0 (based on the URL) conflicts with the Step 1 investigation results, show both and prioritize the one with higher confidence.

Write the plan to `companies/{company slug}/exam-prep-plan.md` (or `_general/exam-prep-plan.md` for the generic case). Both the plan and the final message state the conclusion first. Do not include empty sections, repeated content, or boilerplate preambles.

### Step 3 Practice and mock questions

Based on the question formats shown in `references/assessment-catalog.md`, present self-made questions that mimic the target assessment's format, then score and explain them.

- The focus is mainly on the ability-test family where repeated practice is effective (SPI3, 玉手箱 (Tamatebako), TG-WEB, GAB, CAB). Repeat the cycle: present a question → the user answers → score it → explain it → re-present questions on weak subjects.
- For personality tests, the practice consists solely of advice on the answering approach (consistency, honesty).
- Case interviews and Fermi estimation are practiced following the thinking pattern (confirm premises → decompose into elements → form a hypothesis → state the conclusion first). The evaluation weighs the thinking process (`references/prep-methods.md`).
- Do not reproduce real exam questions or copyrighted material (principle 3). Self-made questions mimic only the format.

## Pass/fail gates and send-backs

This skill does not have an independent audit agent. The gate is set against the validity of the Step 1 investigation results.

- The format gate (Step 1) is defined by a PASS from `validate_exam_assessment.py`. If there is even one ERROR, Step 2 is not entered. This validation script mechanically detects assertions with no source URL, out-of-range `grade` or `confidence` values, and a `確定` (confirmed) claim with no level-A evidence, and treats them as FAIL. The canonical definition of the judgment rules is in `references/exam-assessment-format.md`.
- The type-identification gate (Step 1) requires that `job-change-exam-scout` return a valid type.
  - If the agent returns `{"error": "企業名が指定されていない"}`, return to Step 0 and confirm the company name.
  - If `assessments` is empty with only `open_questions`, re-request the agent with instructions to broaden the search scope (other candidate-write-up outlets, checking the careers page). Re-requesting is capped at 2 attempts.
  - If the type still cannot be identified after 2 attempts, tell the user "type unknown" as an open item. It is then left to the user to choose between narrowing to basic preparation assuming the most common assessments (SPI3, 玉手箱 (Tamatebako)), or re-investigating once the exam invitation arrives.
- The confidence gate (Step 2) requires that for a type whose `confidence` is `推定` (estimate), the preparation plan states explicitly that it is an estimate, the number of supporting pieces of evidence, and the confidence level, without asserting it with the same certainty as a confirmed type.
  - What the mechanical check guarantees. That a `確定` (confirmed) claim has level-A evidence (if not, it fails the Step 1 format gate) is judged mechanically by `validate_exam_assessment.py`. Flagging a `推定` (estimate) backed by only a single piece of evidence as WARN is also done by `validate_exam_assessment.py`.
  - What requires human judgment. The following four points cannot be judged mechanically. In particular, for a type backed by only a single candidate write-up, its limitation is stated explicitly in the preparation plan.
    - Whether the quoted passage genuinely describes that assessment type
    - Whether the assignment of the evidence level itself is appropriate
    - Which side to follow when multiple sources conflict
    - How far a `推定` (estimate) type may be relied on in the preparation plan

## Role execution (by harness)

This skill's pipeline is written so that the work is delegated to specialized roles. The content of each role lives under `references/roles/`, which is its canonical definition.

| Agent name | Canonical role prompt |
|---|---|
| `job-change-exam-scout` | `{SKILL_DIR}/references/roles/exam-scout.md` |

The canonical definition of the execution procedure by harness, and how many instances to launch, is in the hub's `{HUB_SKILL_DIR}/references/role-execution.md`.

## Agent model policy

| Agent | model | Responsibility |
|---|---|---|
| `job-change-exam-scout` | sonnet | Investigating the target company's assessment types (type, stage, source URL, confidence, question format, recommended preparation) |

The `model` is fixed in the agent definition's frontmatter and is not overridden at launch time.

## References list

| File | What | When to read it |
|---|---|---|
| `references/assessment-catalog.md` | Providers, structure, administration method, question format, and sources for the major assessments (SPI3, 玉手箱 (Tamatebako), GAB/CAB, TG-WEB, TAL, 内田クレペリン検査 (Uchida-Kraepelin), personality tests, foreign-affiliated online assessments) | Interpreting Step 1's results, designing Step 2's study items, understanding Step 3's question formats |
| `references/domain-detection.md` | The advance detection table for assessment family by exam-invitation-URL domain, and its limitations | When a URL exists at Step 0; when cross-checking the provisional detection against the investigation results at Step 2 |
| `references/prep-methods.md` | The difference in preparation effectiveness by assessment type, academic findings on practice effects and faking, the standard family of materials, and the pattern for case interviews and Fermi estimation | Deciding the preparation policy at Step 2; the practice policy at Step 3 |
| `references/exam-assessment-format.md` | The field specification, entry criteria, and mechanical validation rules for `exam_assessment.json` | Writing the Step 1 instructions and validating its deliverable; reflecting WARNs into the plan at Step 2 |
