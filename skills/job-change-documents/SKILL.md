---
name: job-change-documents
description: >-
  A sub-skill that writes job application documents for a career change (shokumu-keirekisho,
  rirekisho, English resume, statement of motivation) from the achievements in profile.json, the
  posting requirements, and the results of company research. It builds a correspondence table
  between the posting requirements and the achievements (an appeal mapping), writes each document
  type in its standard format, and delivers it only after it passes an independent audit (Japanese
  grammar, detection of exaggeration and fabrication, correspondence with the requirements, English
  resume criteria, length). It holds to the principle that a quantified value matches profile.json's
  metric exactly and that no achievement without a record in the profile is fabricated. It runs when
  dispatched from job-change-support (the hub). Dedicated agents (job-change-document-writer /
  job-change-document-auditor) handle the writing and the audit.
  Use when the user writes job application documents for a career change in Japan (including
  foreign-affiliated selection) — a shokumu-keirekisho (work-history CV), rirekisho (resume), English
  resume, or statement of motivation — based on their profile and the target company's requirements.
  trigger words: 職務経歴書, 履歴書, 応募書類, 志望動機, レジュメ, 英文レジュメ, 職務要約, 自己PR。
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Agent, AskUserQuestion, Skill
---

# job-change-documents

This single skill covers the full procedure, from intake to delivery, for writing job application
documents for a career change. It maps posting requirements to the user's achievements, writes each
document in its standard format by document type, and delivers it only after it passes an audit
independent of the writer. It centers on mid-career hiring in Japan and also supports the English
resume used for foreign-affiliated company selection.

Dedicated agents (`job-change-document-writer` and `job-change-document-auditor`) handle the writing
and the audit respectively. This skill governs their launch, rework, and delivery. The writing
standards for each document type are self-contained in `references/`.

## Purpose and principles

1. **Write achievements only within what profile.json records.** Every career history entry,
   achievement, and figure that appears in a document is limited to what `profile.json` records. Do
   not fabricate an achievement or a career history entry it does not record (fabrication is
   prohibited). Match every quantified value exactly to `profile.json`'s `achievements[].metric`; do
   not round or inflate it. Do not use a word for scale, scope, or ownership (大規模 large-scale, 全社
   company-wide, 主導 led, and the like) beyond what `profile.json`'s description supports.

2. **Map the posting requirements to the achievements before writing.** Before writing, build an
   appeal mapping (a requirement-to-profile map) that matches the posting requirements against
   `profile.json`'s achievements, listing each requirement, its corresponding achievement, and the
   supporting evidence. Every selling point maps to a posting requirement. Treat a requirement with
   no corresponding achievement in profile.json as unmatched, and do not fill it with fabrication.

3. **Separate the writer from the auditor.** Launch the auditor in a new context that withholds the
   writer's rationale, so it judges the deliverable on its own terms. The auditor does not rewrite the
   document; it returns findings only. The writer applies them.

4. **Use company research for company-specific tailoring.** Base the statement of motivation and any
   company-specific tailoring on the target company's `company_research.json` (its philosophy, the
   profile of the person it wants, and the like). When `company_research.json` does not exist, skip
   company-specific tailoring and tell the user explicitly that the output is a reduced version — a
   generic format and a skeleton self-PR that do not depend on the company.

5. **Do not send personal information outside the system.** Do not use the user's personal
   information in any outbound transmission, including a search query, a fetch, or an external API
   call. The canonical definition of what counts as personal information and which role may handle it
   lives in the hub's `{HUB_SKILL_DIR}/references/pii-boundary.md`. Neither `job-change-document-writer`
   nor `job-change-document-auditor` in this skill holds a web transmission tool, so `profile.json`,
   `self_analysis.json`, and `fit_assessment.json` may be passed to them as they are. This rule holds
   throughout this skill and every downstream step.

## Out of scope

- **Submitting an application or sending documents outside the system.** This skill does not perform
  an operation that sends anything outside the system on the user's behalf, such as submitting an
  application form, delivering documents to a recruiting agency, or replying to a scout. It supports
  the work through document creation; the user sends the documents.
- **Creating a new profile.** The hub (`job-change-support`) handles creating and validating
  `profile.json`. This skill takes an existing `profile.json` as input.
- **Company research itself.** `job-change-company-research` handles researching a company's
  philosophy, business, and reputation. This skill references its output (`company_research.json`).

## Path resolution

The user data location is determined solely by what the configuration file states; there is no
default location. Wherever this document writes `{DATA_ROOT}`, read it as the `data_root` the
following command returns.

When dispatched from the hub (job-change-support), this skill receives the `{DATA_ROOT}` the hub has
already resolved. When launched standalone, run the following before any other step.

```bash
python {HUB_SKILL_DIR}/scripts/jc_config.py --show
```

| Exit code | State | Action |
|---|---|---|
| 0 | configured | The output's `paths` holds the absolute path to each data file. Proceed with the work as is. |
| 1 | configuration exists but is invalid | Show the user the output's `errors`, and do not proceed until the user fixes it. |
| 2 | unconfigured | Launch `job-change-support` with the Skill tool to have it create the configuration, resolve `{DATA_ROOT}`, and then return. |

`{SKILL_DIR}` denotes this skill's own absolute path, and `{HUB_SKILL_DIR}` denotes the absolute path
of `job-change-support` in the same installation. The configuration file's specification, including
the search order, lives in `docs/configuration.md`.

## Data layout

User data is split across two locations. The private directory `{DATA_ROOT}/career-private/` holds
personal information such as profile.json. The project root outside it, `{DATA_ROOT}/`, holds
non-personal information such as per-company outputs. This skill reads and writes the following
paths.

| Path | Role | I/O |
|---|---|---|
| `career-private/profile.json` | Canonical user profile | Input (read only) |
| `career-private/self_analysis.json` | Self-analysis output (canonical definition: `job-change-self-analysis`) | Input (optional; when present, add it to the input for the statement of motivation and the self-PR; the pipeline proceeds without it) |
| `career-private/fit/{company slug}/fit_assessment.json` | Fit-assessment output (canonical definition: `job-change-fit-assessment`) | Input (optional; when present, add it to selecting the appeal mapping's selling points; the pipeline proceeds without it) |
| `companies/{company slug}/company_research.json` | Company research's structured data | Input (optional; a fallback applies when absent) |
| `companies/{company slug}/documents/` | Output location for the application documents produced | Output |
| `companies/{company slug}/documents/appeal-mapping.md` | Appeal mapping table | Output |
| `companies/{company slug}/documents/tailoring-rationale.md` | Explanation of the tailoring rationale | Output |

- The company slug follows the same convention as the hub and resolves through
  `career-private/company_index.json` (example: the fictional Kakuu Cloudworks →
  `kakuu-cloudworks`).
- A company-independent generic document (when the target company is undecided) is placed under
  `documents/`.
- Document files are named separately by type (for example: `shokumu-keirekisho.md`,
  `rirekisho.md`, `english-resume.md`, `motivation.md`).
- Write the appeal mapping table to `documents/appeal-mapping.md` and the tailoring rationale to
  `documents/tailoring-rationale.md`. Both cite achievements from `profile.json` and so contain
  personal information, but they are placed alongside the application documents themselves. Neither
  of this skill's two roles holds a web transmission tool, and no role outside this skill reads
  `companies/{company slug}/documents/`.

## Intermediate outputs

The pipeline produces the following along the way. Both are included in the final delivery.

| Intermediate output | Content |
|---|---|
| Appeal mapping | A three-column table of posting requirement, corresponding achievement, and supporting evidence. The writer builds it in Step 1 and carries it into the output JSON (`appeal_mapping`) and the deliverable. It grounds every selling point without exaggeration, and the auditor uses it to check correspondence with the posting requirements. |
| Format selection record | Which template from `references/templates.md` was chosen for each document type, and why (the writer's output JSON field `format`). |

## Pipeline

Proceed through Step 0 to Step 4 in order, from intake to delivery. Read `{PROFILE}` as the absolute
path to `profile.json`, and `{COMPANY_RESEARCH}` as the absolute path to the target company's
`company_research.json`. `{SELF_ANALYSIS}` is the absolute path to `career-private/self_analysis.json`
(when present). `{FIT_ASSESSMENT}` is the absolute path to
`career-private/fit/{company slug}/fit_assessment.json` (when present). Read `{OUT_DIR}` as the
document output directory.

### Step 0: Intake

Confirm the following. Ask any unclear point with AskUserQuestion, as a multiple-choice question in
principle, at most 4 questions per round with up to 4 options each.

| Item to confirm | Content |
|---|---|
| Document type | One of shokumu-keirekisho (career history document), rirekisho (résumé form), English résumé, or statement of motivation (multiple allowed). |
| Job posting | The target posting's requirements, received as text or a file. Without it, limit the scope to producing a generic format. |
| Target company | The subject of company-specific tailoring. Before resolving the slug, validate the index with `validate_company_index.py` (a hub script); on FAIL (one or more ERROR), show the finding to the user and do not proceed to resolution until the user fixes it. Then resolve the company slug through `career-private/company_index.json` (details in the hub's `references/company-index-format.md`) and set `{OUT_DIR}`. |

The profile.json gate is mandatory.

- This skill assumes `profile.json` PASSes `validate_profile.py` (a hub script), meaning zero ERROR.
  When entered through the hub, the hub has already confirmed this before routing. When this skill is
  launched standalone, it runs `validate_profile.py` itself and confirms the PASS.
- When `profile.json` does not exist, do not proceed. Send the user back to the hub's
  (`job-change-support`) profile setup, and resume once it is created (creating the profile is the
  responsibility of the hub and `job-change-profile`).
- When validation FAILs (one or more ERROR), show the user the ERROR content and recommend fixing it
  in `job-change-profile`. When the user knowingly accepts the gap and wants to proceed anyway, this
  skill may proceed, on the condition that it writes no statement that directly quotes or presupposes
  the value of a missing field. In that case, state clearly at delivery which fields remain missing.
  When dispatched from the hub and the hub has already asked the user this same question, follow that
  choice without asking again, so the hub and this skill do not ask the user the same question twice.

When `profile.json`'s `career_history[].achievements` and `skills` are empty, guide the user to return
to `job-change-profile`'s section update (`achievements`, `skills`) to elicit them in depth, then come
back. Achievements and skills are fields that become necessary only at this stage, and the profile's
initial scope skips them by default. Since validation still PASSes, treat this as guidance to the
user. When the user chooses to proceed anyway, write only what the bare career-history skeleton
supports, and state clearly at delivery that no achievement is recorded.

Checking company_research.json is optional, and when it is absent, state the fallback explicitly.

- Check whether the target company's `company_research.json` exists. When it is absent, proceed with
  a fallback behavior that applies no company-specific tailoring, and tell the user so explicitly.
  Also tell them that running company research (`job-change-company-research`) first would raise the
  precision of the statement of motivation and the company-specific tailoring.
- When `company_research.json` exists, judge that company's `_manifest.json` with `check_freshness.py`
  (a hub script). When a topic is `stale`, show the user that fact and the topic's name, and suggest a
  differential re-investigation in `job-change-company-research`. When the user chooses to proceed
  without re-investigating, state clearly in Step 4's tailoring rationale that the document relies on
  stale information, naming the topic, and proceed. The canonical definition of the judgment rule and
  the TTL lives in the hub's `references/freshness-policy.md`.

self_analysis.json is likewise an optional input.

- Check whether `career-private/self_analysis.json` exists. When present, add it to the input for the
  statement of motivation and the self-PR. The pipeline proceeds without it, but tell the user
  explicitly that running self-analysis (`job-change-self-analysis`) first would let the document
  reflect the career narrative and a constructive framing of the reason for changing jobs.

fit_assessment.json is likewise not mandatory.

- Check whether `career-private/fit/{company slug}/fit_assessment.json` exists. When present, add
  `dimensions`' `evidence` and `must_condition_results` as judgment material for selecting the appeal
  mapping's selling points. The pipeline proceeds without it, matching only the posting requirements
  against `profile.json`'s achievements. fit_assessment.json is an output under career-private, and it
  is not passed to an agent holding a web tool.

### Step 1: Writing

Launch the `job-change-document-writer` agent (model: opus) and instruct it to perform Step 1
(writing). Pass it the following in its brief.

- The step to run (= 1), the document type, `{PROFILE}`, `{COMPANY_RESEARCH}` (when present),
  `{SELF_ANALYSIS}` (when present), `{FIT_ASSESSMENT}` (when present), the job posting (when present),
  and the output location `{OUT_DIR}`.

The writer has the following responsibilities. Extract the posting requirements and, when company
research exists, its philosophy and the profile of the person it wants, and match them against
`profile.json`'s achievements to build the appeal mapping. Then select a template from the list in
`references/templates.md`, with a reason, and write within its structure. Write the document under
`{OUT_DIR}`. When `company_research.json` does not exist, skip company-specific tailoring and state
this clearly in the deliverable and the output JSON (`company_research_used: false`,
`degraded_reason`). When `fit_assessment.json` exists, add `dimensions`' `evidence` and
`must_condition_results` as judgment material for selecting the appeal mapping's selling points. When
it does not exist, proceed by matching only the posting requirements against `profile.json`'s
achievements.

For the statement of motivation and the self-PR, when `self_analysis.json` exists, use
`career_narrative` (the life theme, the consistent motivation) as material. Add `strengths` grounded
in evidence (a strength mapped to an `episode_id` or a `feedback_id`) and
`reason_for_change.constructive_version` (a reframing of the reason for changing jobs around the
value the user wants to bring) as material as well. Use both together with `profile.json`'s
achievements. When `self_analysis.json` does not exist, use only `profile.json`'s `strengths` and
`job_change_axis.reasons` as material. In this case, unlike company-specific tailoring, there is no
need to state explicitly that a fallback occurred.

### Step 2: Independent audit

Launch the `job-change-document-auditor` agent (model: sonnet) in a new context that withholds the
writer's rationale, and instruct it to perform Step 2 (audit). Pass it the absolute path to the
document file under audit, the document type, the file name of the template the writer selected,
`{PROFILE}`, and the job posting (when present).

The auditor checks the following four points.

- **Japanese grammar and orthography.** For the shokumu-keirekisho, the rirekisho, and the statement
  of motivation, check against the criteria the role prompt's "Canonical judgment reference" lists
  (particle usage, subject-predicate agreement, modifier attachment, parallel structure, redundant
  phrasing, spelling inconsistency, and typos and omissions).
- **Exaggeration and fabrication.** Cross-check against `profile.json` and detect an achievement or a
  figure it does not record, a mismatch with `metric`, and a word for scale, scope, or ownership that
  exceeds what it supports.
- **Correspondence with the posting requirements, quantification, length, and conformance to the
  template's structure.**
- **English resume.** Check English grammar and tense, the fitness of action verbs (opening with a
  verb, omitting the subject), quantification, ATS fitness (avoiding tables, images, and graphics;
  matching the posting's keywords in context), and length (one to two pages). Japanese grammar and
  orthography checks do not cover it.

The judgment returns as `verdict` (BLOCK / CONCERNS / CLEAN) and `findings` (each finding carrying
`severity` = 重大 / 警告 / 軽微).

### Step 3: Applying audit findings

When `verdict` is not CLEAN, pass the findings to `job-change-document-writer` and instruct it to
perform Step 3 (applying audit findings). Pass it the same input as Step 1, plus the auditor's
findings.

The writer reviews the findings one by one and applies to the document whichever finding it can
address within what `profile.json` supports. For a finding it leaves unapplied, it states the reason
clearly (for example, when the requested addition would be fabrication because profile.json provides
no support).

- When `verdict` is BLOCK, or a finding carries `severity` = 重大, return to Step 2 for a re-audit
  after applying the findings (this counts as one round of rework).
- When `verdict` is CONCERNS with no 重大 finding (only 警告 or 軽微), apply the findings, and a
  re-audit is optional. Proceed to Step 4 once the findings are applied, or once any finding that
  could not be applied is recorded in the tailoring rationale.

### Step 4: Delivery

Deliver once `verdict` becomes CLEAN, or once every 重大 finding is resolved. The final delivery
consists of the following three items.

1. **The application documents** (the files under `{OUT_DIR}`).
2. **The appeal mapping table** (posting requirement, corresponding achievement, supporting
   evidence). Written to `{OUT_DIR}/appeal-mapping.md`.
3. **The tailoring rationale** (the format selected and why, what was tailored in the
   company-specific customization and which `company_research.json` claim it rests on, and the audit
   result). In a fallback, state that no company-specific tailoring was applied. The audit result
   includes the final verdict and, for any finding left unapplied, the reason. Written to
   `{OUT_DIR}/tailoring-rationale.md`.

The final message summarizes the type and file path of each document produced, the format selected,
the audit's final verdict, and any open issue. Both the tailoring rationale and the final message
state the conclusion first. Neither contains an empty section, a repeated statement, or a formulaic
preamble.

## Pass/fail gates and rework

The pipeline has two gates.

| Gate | Passing condition and where it sends rework |
|---|---|
| Step 0's profile gate | Writing does not proceed unless `profile.json` PASSes `validate_profile.py`. When it does not exist, or FAILs, send the user back to the hub's profile setup. On FAIL, however, show the ERROR content, and when the user knowingly accepts the gap and wants to proceed, this may proceed, on the condition that it writes no statement that directly quotes or presupposes the value of a missing field. State clearly in the deliverable which fields remain missing. When the hub has already asked the user this same question, follow that choice without asking again. |
| Step 2's independent audit gate | When `job-change-document-auditor`'s `verdict` is BLOCK, or a finding carries `severity` = 重大, send it back to the writer at Step 3. Rework runs at most twice for the same document. |

On rework, pass the audit's findings (target, evidence, fix) to the writer as they are, and run it
through Step 2 again once applied. A finding that two rounds of rework do not resolve is stated
clearly as an open issue in the tailoring rationale, and delivery follows only after the user has been
given the decision. For example, a finding such as "profile.json's achievements alone do not
sufficiently meet the posting requirements" calls for either strengthening the career history or
reconsidering whether to apply, so it is left to the user's decision. Resolve every ERROR from
mechanical validation before delivery regardless of the rework limit; delivery is permitted only when
what remains unresolved is an audit finding, and only after that finding is stated clearly as an open
issue.

## Role execution (by harness)

This skill's pipeline is written to delegate work to dedicated roles. Each role's content lives in
`references/roles/`, which is its canonical definition.

| Agent name | Canonical role prompt |
|---|---|
| `job-change-document-writer` | `{SKILL_DIR}/references/roles/document-writer.md` |
| `job-change-document-auditor` | `{SKILL_DIR}/references/roles/document-auditor.md` |

The canonical definition of the per-harness execution procedure, how many instances to launch, and
the reason for separating the writer from the auditor lives in the hub's
`{HUB_SKILL_DIR}/references/role-execution.md`.

## Agent model policy

| Agent | model | Responsibility |
|---|---|---|
| `job-change-document-writer` | opus | Appeal mapping, format selection, and writing (Step 1); applying audit findings (Step 3) |
| `job-change-document-auditor` | sonnet | Auditing the document in an independent context (Step 2). It checks Japanese grammar and orthography itself as well. |

The model is fixed in each agent's frontmatter. This skill does not override it at launch.

## Script CLI usage examples

This skill has no scripts of its own. All three scripts used in Step 0 belong to the hub
(`job-change-support`); when entered through the hub, the hub has already run them before routing.
When launched standalone, this skill runs the following.

```bash
python {HUB_SKILL_DIR}/scripts/validate_profile.py {DATA_ROOT}/career-private/profile.json
python {HUB_SKILL_DIR}/scripts/validate_profile.py {DATA_ROOT}/career-private/profile.json --json
python {HUB_SKILL_DIR}/scripts/validate_company_index.py {DATA_ROOT}/career-private/company_index.json
python {HUB_SKILL_DIR}/scripts/check_freshness.py {DATA_ROOT}/companies/{company slug}/_manifest.json
```

`validate_profile.py` and `validate_company_index.py` exit 0 on PASS and 1 on FAIL (WARN alone counts
as PASS). `--json` outputs the result in JSON form (`status`, `error_count`, `warning_count`,
`errors`, `warnings`). `check_freshness.py` always exits 0 and outputs a classification of `fresh`,
`stale`, or `missing`. The canonical definition of profile.json's field specification lives in the
hub's `references/profile-format.md`.

## references index

| File | What it covers | When to read it |
|---|---|---|
| `references/shokumu-keirekisho.md` | The shokumu-keirekisho's three formats and when to use each, the summary section, quantifying achievements, length, and the hiring manager's perspective | When writing or auditing a shokumu-keirekisho |
| `references/rirekisho.md` | The current state of the rirekisho form (the MHLW's format example), handwritten versus typed, and avoiding reuse | When writing or auditing a rirekisho |
| `references/english-resume.md` | The English resume's standard structure, the personal information to omit, quantification, and ATS handling | When writing or auditing an English resume |
| `references/tailoring.md` | Company-specific tailoring, the statement of motivation's structure, the appeal mapping, and the anti-exaggeration standard | When working on the statement of motivation or company-specific tailoring, and as the standard for the exaggeration check across every document |
| `references/templates.md` | The list of multiple-style templates for each document type, how to choose among them, length, and the decisions made where sources disagree | When selecting a format, and when auditing conformance to the structure |

The templates themselves live in `assets/templates/` (four for the shokumu-keirekisho, two for the
rirekisho, three for the English resume, two for the statement of motivation, and one for the
self-PR). The writer selects one from the list in `references/templates.md` and writes within its
structure.
