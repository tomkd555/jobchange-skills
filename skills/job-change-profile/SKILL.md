---
name: job-change-profile
description: >-
  Sub-skill of the job-change support skill group, dedicated to creating and updating profile.json, the user's
  career record. It divides profile.json into sections (basic information, career skeleton, responsibilities and
  achievements, skills), elicits each section through its own single-file procedure, and judges each section's
  reach stage (missing / skeleton / deep) with a script. The first pass settles the basic information and the
  career skeleton, which is enough to start application documents. It elicits information through structured
  recall cues (chronological × project unit), and supports quantification of achievements and a skill inventory,
  building the result through writing, mechanical validation, and independent audit. It splits a 1.x/2.0
  profile.json into profile.json and axis.json before its first write. Elicitation centers on AskUserQuestion's choice format, at most 4
  questions per call with up to 4 choices each; free text is limited to items that cannot be put into choices, such
  as company names, periods, and achievement figures. It can record both concurrent employment at the same time
  (concurrent roles, secondment, side work) and multiple concurrent projects handled within a single job. Writing
  and independent audit are each handled by a dedicated agent (job-change-profile-writer / job-change-profile-auditor).
  It runs when dispatched from job-change-support (the hub). The job-change axis (reasons, conditions,
  work-character preferences, scoring axes, targets, salary) belongs to job-change-axis; grounding strengths and
  building a career narrative belong to job-change-self-analysis; wording of application documents belongs to
  job-change-documents.
  Use when the user creates or updates their career record for a job change in Japan: registering career history,
  taking stock of skills, or quantifying achievements.
  trigger words: プロファイルを作りたい, 経歴を登録, 職務経歴の棚卸し, プロファイルを更新, 職歴の登録,
  実績の定量化, スキルの棚卸し, career history, skill inventory。
allowed-tools: Read, Write, Glob, Grep, Bash, AskUserQuestion, Agent, Skill
---

# job-change-profile

This skill holds the complete procedure, from elicitation through delivery, for creating or updating profile.json,
the canonical source of the user's career record in the job-change support skill group. profile.json is built in
sections, and each section has one file, `references/sections/{id}.md`, holding its procedure and settled wording
(the catalogue is `references/sections.md`). Elicitation uses structured recall cues (a chronological frame of
company → tenure period → role → project → outcome) and supports quantification of achievements and a skill
inventory. profile.json is settled through writing, mechanical validation, and independent audit. Application
documents, self-analysis, job search, fit assessment, and job interview preparation read the result as an input.
The job-change axis is stored in axis.json and is built by `job-change-axis`.

The core of profile.json is the content of career history, achievements, and skills, and how that content maps to
job requirements (relevance). The grounding for this is in `references/profile-methods.md`. Relevance to job
requirements changes with each application, so profile.json does not hold it as a fixed value; the
application-documents sub-skill reconstructs it at application time. Each application reconstructs its own
relevance from the job-level detail (career history, achievements, quantified values). This skill keeps that detail
accurate, complete, and current.

## Purpose and principles

1. **Elicit with structured recall cues.** Elicitation follows a fixed frame of tenure period × project unit. A
   structured interview carries about twice the validity of an unstructured one.
   A method that uses calendar events as cues across time and theme also raises the completeness and consistency of
   recall, in line with the structure of autobiographical memory (`references/elicitation-guide.md`).

2. **Record the user's own statements as fact, without doubting them.** The career history, achievements, and
   figures the user states are recorded as fact, as stated. Elicitation never asks for supporting documents and
   never asks a question shaped like "can you prove that" or "is that really true." Only a value the user
   themselves called uncertain gets that note in the elicitation notes (`references/elicitation-guide.md`).
   Elicitation permits exactly three operations (making a statement concrete, supporting quantification, and
   rewording into language the job market accepts), and none of them adds a fact the user did not state. A reworded
   sentence is used only after it is shown to the user and the user accepts it (`references/answer-handling.md`).
   Fabrication is held in check elsewhere: the writer uses only facts recorded in the elicitation notes, and the
   auditor checks the deliverable against those notes (Principle 6).

3. **Recommend quantifying achievements, without forcing a number onto every one.** For work that resists
   quantification, a set of alternative phrasing patterns is available (the canonical list of patterns is in
   `references/quantification-guide.md`). Attaching a number to every achievement mechanically is never required. A
   figure is used only when the user states it; elicitation never proposes a candidate value. An excess of figures
   damages the credibility of the whole document (`references/quantification-guide.md`).

3-2. **The user decides the form of the answer.** Elicitation never corrects how the user answers, whether the
   user answers a choice-format question in free text, answers several questions at once, or narrates a whole
   career history in one go. What comes in is sorted into its items, and only the items still unanswered get asked
   next. A career history with an atypical shape (temporary staffing, contract work, secondment, a leave of
   absence, running a business) is recorded as it is, without reshaping it into a typical form
   (`references/answer-handling.md`).

4. **Separate specialized skills from transferable skills.** The entry point is technical / business / languages /
   certifications. A secondary classification holds the 9 elements of the MHLW's (Ministry of Health, Labour and
   Welfare) portable skills (5 対課題 (task-facing), 4 対人 (people-facing)). These two layers take stock of specialized and
   transferable skills separately, without depending on a uniform application of a generic taxonomy
   (`references/profile-methods.md`).

5. **The career record is complete without the job-change axis.** profile.json holds career facts only, so
   application documents can be produced once the career record exists. The job-change axis (reasons, conditions, work-character preferences,
   scoring axes, targets, salary) is settled in `job-change-axis` and written to axis.json.

6. **Do not fabricate or fill in facts.** The career history, achievements, and figures placed in profile.json stay
   within what the elicitation notes record. An achievement figure, a period, or a job title is never filled in by
   inference. Falsifying a career history leads to disciplinary action or a withdrawn offer, and cross-checking
   against social insurance and similar records exposes it with high probability (`references/profile-methods.md`).

7. **Build section by section: settle the skeleton on the first pass, and defer a detailed pass until just before the
   process that needs it.** profile.json is built in sections (the catalogue is `references/sections.md`). On
   first creation, the current role (`basic`) and the career skeleton (`career`) are filled to `skeleton` to make
   profile.json valid. Responsibilities and achievements, skills, and the detailed pass on the first-pass sections are
   each done one section at a time, as a "section update," once a downstream process needs that section. `scripts/profile_sections.py` judges which stage each section has
   reached from profile.json alone, never from the memory of the conversation. Sections are deferred because the
   dropout rate rises as elicitation runs longer, and a conversational format does not by itself make data entry faster
   (`references/elicitation-guide.md`).

8. **Read a document the user already has when one is available, without requiring it.** When a shokumu-keirekisho
   (career history document), rirekisho (résumé form), or résumé is available, the career skeleton is imported from
   it and only needs confirming. Submitting a file is never a condition; elicitation asks through conversation as
   before when none is available. A fact read from a file counts the same as the user's own statement, and is
   never treated as documentary proof (Principle 2).

9. **Personal information is never sent outward.** The personal information profile.json holds is never used in
   any outward transmission, including a search query, a fetch, or an external API. The canonical listing of what
   falls inside the boundary and which role may access it is in the hub's
   `{HUB_SKILL_DIR}/references/pii-boundary.md`. This skill builds `profile.json` and `profile_interview_notes.md`,
   both inside that boundary. Neither the writer (job-change-profile-writer) nor the auditor
   (job-change-profile-auditor) has a means to send data to the web, so these paths may be passed to them.

## Out of scope

The following fall outside this skill's scope. When asked for one of these, this skill states that it cannot
handle the request and names the sub-skill or action to use instead.

- **The job-change axis** (reasons for changing jobs, conditions, work-character preferences, company scoring axes,
  target companies and roles, annual salary). `job-change-axis` handles these and writes axis.json.
- **Grounding strengths, building a career narrative, and constructive rewording of reasons for leaving.**
  `job-change-self-analysis` handles these. Its short statements of strength come back to this skill as a
  `strengths` update (Step 5).
- **Writing the wording of application documents.** `job-change-documents` handles drafting the shokumu-keirekisho,
  rirekisho, English résumé, and statement of motivation. This skill builds the underlying data (profile.json) and
  hands it over.
- **Mapping requirements to the profile for a specific company (an appeal map).** Relevance changes with each
  application and is never held fixed in the profile. `job-change-documents` reconstructs it from profile.json's
  job-level data at application time.
- **Company research.** Researching a company's philosophy, business, and reputation belongs to
  `job-change-company-research`.

## Path resolution

Where the user's data is placed is decided solely by what the configuration file states. There is no default
location. Wherever this document writes `{DATA_ROOT}`, read it as the `data_root` the following command returns.

When dispatched from the hub (job-change-support), the hub passes an already-resolved `{DATA_ROOT}`. When launched
on its own, this skill runs the following before any other step of the work.

```bash
python {HUB_SKILL_DIR}/scripts/jc_config.py --show
```

| Exit code | State | Response |
|---|---|---|
| 0 | Configured | The output's `paths` holds the absolute path for each piece of data. Proceed with the work as it stands. |
| 1 | Configured but invalid | Show the output's `errors` to the user, and do not proceed until it is fixed. |
| 2 | Not configured | Launch `job-change-support` with the Skill tool to have it create the configuration, resolve `{DATA_ROOT}`, and return. |

`{SKILL_DIR}` denotes this skill's own absolute path, and `{HUB_SKILL_DIR}` denotes the absolute path of
`job-change-support` at the same install location. The configuration file's specification, including its search
order, is in `docs/configuration.md`.

## Data layout

The user's data is stored in the private directory `{DATA_ROOT}/career-private/`. The paths this skill reads and
writes are as follows.

| Path | Role | Input/output |
|---|---|---|
| `career-private/profile.json` | The canonical source of the user's career record (`schema_version` 3.0) | Output (this skill creates and updates it) |
| `career-private/profile_interview_notes.md` | Elicitation notes, shared with `job-change-axis`. The canonical definition of the recording format is in `references/elicitation-guide.md` | Output (the main session appends to it as elicitation proceeds; supports resuming after an interruption) |
| `career-private/axis.json` | The job-change axis, written by `job-change-axis` | Created by the split in Step 0 only; this skill leaves its content to `job-change-axis` |

- The canonical definition of profile.json's field specification, entry criteria, and validation rules is in the
  hub's (`job-change-support`) `references/profile-format.md`. This skill does not edit it.
- A filled-in example is in the hub's `assets/profile_example.json` (a fictitious person). This skill does not keep
  a copy of it.
- No user data is placed in the skill's own folder (`skills/job-change-profile/`).
- When `career-private/` does not yet exist, this skill creates it once it is needed.

## Sections and reach stages

profile.json is built in sections. `references/sections.md` is the canonical definition of the section list and
the fields each fills. It also defines the first-pass scope, the process that needs each section, the dependency in
the order of asking, and the criteria for judging the reach stage (`missing` / `skeleton` / `deep`). Each section's
procedure and settled wording are in `references/sections/{id}.md`, and building one section reads only that file
and the common rules (`references/question-bank.md`).

| Section ID | Name | First pass |
|---|---|---|
| `basic` | Basic information | Current role only |
| `career` | Career skeleton | Skeleton |
| `achievements` | Responsibilities and achievements | skip |
| `skills` | Skill inventory | skip |

`scripts/profile_sections.py` judges the reach stage from the content of profile.json alone. Resuming after an
interruption, and deciding which section gets a detailed pass next, are both decided from this output, never from
the memory of the conversation. A skipped section, and the detailed pass on a first-pass section, are each done as
a "section update," just before the process that needs it. When the user states during the session a wish to
continue, elicitation may continue as asked.

A profile.json that fills only the first-pass scope passes `validate_profile.py`. The WARNs expected within the
first-pass scope are listed under "Scope of the first pass" in `references/sections.md`, and are never grounds for
sending Step 5 back.

## Pipeline

Steps 0 through 6 run in order, from intake to delivery. Read `{SKILL_DIR}` as this skill's own absolute path, and
`{HUB_SKILL_DIR}` as the hub's (`job-change-support`) absolute path. `{PROFILE}` denotes the absolute path of
`profile.json`, and `{NOTES}` denotes the absolute path of `profile_interview_notes.md`.

The main session performs elicitation with AskUserQuestion (a sub-agent cannot converse with the user). Elicitation
centers on the choice format, at most 4 questions per AskUserQuestion call with up to 4 choices per question. When
one question should take several answers, use `multiSelect: true` and keep it as one question.
Free text is asked only for an item that cannot be put into choices, such as a company name, a tenure period, or an
achievement figure. Questions use the structured questions set in advance in `references/question-bank.md`, never
an open-ended question that invites rumination. A question addressed to the user, and its choice labels, are
written in polite Japanese (敬体). For a question whose choices can be enumerated in advance,
`references/question-bank.md` holds the settled wording, and that wording is used as it stands, never improvised at
the moment of asking.

The choice format is the form of elicitation's own question, and it never constrains how the user answers. When
the user answers in free text or answers several things at once, what comes in is sorted into its items and written
to `{NOTES}`, and only the items still unanswered are asked next. The same item is never asked again in choice
format. The canonical definition of how to handle each answer format, and the types of question that never doubt a
statement, is in `references/answer-handling.md`.

### Step 0: Checking the premises

- Check whether `profile.json` exists. When axis.json exists beside a 1.x/2.0 profile.json, follow the stop state
  in "Location" of the hub's `references/axis-format.md` and wait for the user to settle it.
- When `profile.json` has `schema_version` 1.0, 1.1 or 2.0, split it before any write, and tell the user the
  backup path the report gives (`backup`); on exit 1, show the report's `errors` and stop. The procedure is in
  "Splitting a 1.x/2.0 profile.json" of the hub's `references/axis-format.md`.

  ```bash
  python {HUB_SKILL_DIR}/scripts/split_profile.py {PROFILE}
  ```

  The axis moved into axis.json keeps its version; moving a 1.x axis to 2.0 is handled by `job-change-axis`.
- When `profile.json` exists, validate it with the career gate, then grasp each section's reach stage with
  `scripts/profile_sections.py`.

  ```bash
  python {HUB_SKILL_DIR}/scripts/validate_profile.py {PROFILE}
  ```
- Check the mode with AskUserQuestion. The choices are 「初回作成」 (first creation), 「節の更新」 (section update),
  and 「全面点検」 (full review) (the wording is in `references/question-bank.md`'s Step 0).
- For "section update," have the user go on to choose the target sections (one question, taken with
  `multiSelect: true`). Attach each section's current stage to its choice description. Read
  the existing profile.json and elicit only the chosen sections.
- For "first creation," proceed within the first-pass scope described above under "Sections and reach stages."
  Only when the user states a wish to finish the detailed pass in the same sitting does elicitation continue directly
  into the skipped sections.
- When a downstream sub-skill dispatches this skill naming a section it needs, that section is treated as a
  "section update" regardless of the chosen mode.

### Steps 1-4: Elicitation by section

For each target section, read `references/sections/{id}.md` and ask with the procedure and settled wording it
holds. What comes back is appended to `{NOTES}` immediately. The dependency in the order between sections (`career`
→ `achievements` → `skills`) follows "Section order" in `references/sections.md`. A section with no dependency may be taken in whatever order the user chooses.
The Step numbers match the column in `references/question-bank.md`'s correspondence table.

| Step | Section | First pass | Canonical procedure |
|---|---|---|---|
| 1 | `career`, `basic` | Skeleton and current role | `references/sections/career.md`, `references/sections/basic.md` |
| 2 | `achievements` | skip | `references/sections/achievements.md` |
| 3 | `skills` | skip | `references/sections/skills.md` |

Step 4 is handled by `job-change-axis`: after the first pass, name it once as the next step for job search and fit
assessment, and launch it with the Skill tool when the user wants to continue.

The section files hold the following matters, and SKILL.md does not repeat them.

- `career`: importing an existing document (including reading a `.docx`), settling the skeleton, concurrent
  employment, separating the employer from the place of work, and detecting and recording a gap in employment.
- `achievements`: a detailed pass in the order responsibilities → key projects → achievements, support for
  quantification, presenting a reworded candidate, and `project`/`period` for a concurrent project.
- `skills`: reverse lookup from what the user says, the 9 elements of portable skills, and how to present
  candidates when converting into an unfamiliar occupation.

### Step 5: Writing, mechanical validation, independent audit

As elicitation proceeds, the main session appends its results to `{NOTES}` (`profile_interview_notes.md`) and keeps
them collected there (this supports resuming after an interruption). The `job-change-profile-writer` agent (model:
opus) is launched. It is passed `{NOTES}`, the existing `{PROFILE}` (when updating), the hub's
`references/profile-format.md`, and the output destination `{PROFILE}`. The writer creates or updates profile.json
from the facts in the notes alone. On the hand-off from `job-change-self-analysis`, the main session appends the
short statements of strength it receives to `{NOTES}` under the day's heading and passes the same statements in
the writer's brief. The writer updates `strengths` from them with `strengths` as the target. On receiving its return value, the main session runs the hub's
`validate_profile.py` and confirms ERROR 0. The `job-change-profile-auditor` agent (model: opus, in a new context
that is not given the writer's reasoning) is then launched to audit the result. When `verdict` is BLOCK, or a
finding carries `severity` = must_fix, the work is sent back to the writing step of Step 5 (at most twice; after
that, it is the user's decision).

This step runs as usual even within the first-pass scope. A profile.json that fills only the first-pass scope
produces a WARN for each skipped section. Such a section stays `missing`, which is expected, and is never grounds
for sending the work back. It is presented to the user as a section whose detailed pass is still ahead.

### Step 6: Guidance on update practice and delivery

Guide the user on update practice: append whenever a new achievement comes in, review at least once a quarter,
and give priority to the most recent 7-10 years when writing it into an application document. Also rewrite
`updated_at` to today's date. profile.json is an input for downstream sub-skills, so no formatted file is
produced from it. Instead, attach the output of `scripts/profile_sections.py` and summarize for the user what was
written: the job summary, the number of career-history entries and their tenure periods, achievements, and
skills. Finally, guide the user to the downstream work that can take profile.json as input: application-document
writing in `job-change-documents`, self-analysis in `job-change-self-analysis`, and the job-change axis in
`job-change-axis` (needed for job search and fit assessment). When a section remains
`missing` or `skeleton`, name that section and the process that needs it (the "Section list" table in
`references/sections.md`) once, without urging a detailed pass right away. The final message states its conclusion
first and states each point once. It omits empty sections and formulaic preambles.

## Pass/fail gate and send-back

The pipeline has one validation-and-audit gate.

| Gate | Passing condition and where a send-back returns to |
|---|---|
| Step 5's validation-and-audit gate | The work returns to Step 5's writing step when the hub's `validate_profile.py` FAILs (1 or more ERRORs), when `job-change-profile-auditor`'s `verdict` is BLOCK, or when a finding has `severity` = must_fix. A send-back happens at most twice for the same deliverable. |

On a send-back, the audit's findings (`target`, `evidence`, `fix`) are passed to the writer as they stand. Once
they are reflected, the work runs again from Step 5's mechanical validation. A finding that two send-backs fail to
resolve is delivered only after the user has settled it as an open item. For example, when the finding is a figure in
profile.json with no record in the elicitation notes, the user chooses between asking again and removing it. A
mechanical validation ERROR is resolved before delivery regardless of the send-back limit. Delivery may proceed
with an open item noted explicitly only when what remains unresolved is an audit finding.

## Role execution (by harness)

This skill's pipeline is written as delegating work to specialized roles. The content of each role is in
`references/roles/`, which is the canonical definition.

| Agent name | Canonical role prompt |
|---|---|
| `job-change-profile-writer` | `{SKILL_DIR}/references/roles/profile-writer.md` |
| `job-change-profile-auditor` | `{SKILL_DIR}/references/roles/profile-auditor.md` |

The canonical definition of the execution procedure by harness, the judgment of how many agents to launch, and the
reason for separating writing from auditing are in the hub's `{HUB_SKILL_DIR}/references/role-execution.md`.

## Agent model policy

| Agent | model | Responsibility |
|---|---|---|
| `job-change-profile-writer` | opus | Creates and updates profile.json from the elicitation notes (Step 5) and reflects audit findings. Never fabricates a fact the notes lack |
| `job-change-profile-auditor` | opus | In an independent context, audits fabrication and exaggeration, chronological consistency, and concurrent employment, and reruns the validation script (Step 5) |

Mechanical checking is handled by the hub's `validate_profile.py`. Each agent's model is fixed in its own
frontmatter, and it is never overridden at launch.

## Script CLI usage examples

Validating profile.json uses the hub's (`job-change-support`) `validate_profile.py` (this skill holds no
validation script of its own, to avoid managing the same thing in two places). The exit code is 0 for PASS, 1 for
FAIL; WARN alone counts as PASS. Read `{HUB_SKILL_DIR}` as the hub's absolute path, and the trailing path as the
path of the profile.json under validation.

```bash
python {HUB_SKILL_DIR}/scripts/validate_profile.py {DATA_ROOT}/career-private/profile.json
python {HUB_SKILL_DIR}/scripts/validate_profile.py {DATA_ROOT}/career-private/profile.json --json
```

`--json` outputs the result in JSON form (`status`, `error_count`, `warning_count`, `errors`, `warnings`). The
canonical definition of profile.json's field specification and validation rules is in the hub's
`references/profile-format.md`. See the hub's `assets/profile_example.json` for a filled-in example.

This skill's `profile_sections.py` reports each section's reach stage. Its exit code is always 0, and it never
decides pass or fail. The output format is in "How to use the script" in `references/sections.md`.

```bash
python {SKILL_DIR}/scripts/profile_sections.py {DATA_ROOT}/career-private/profile.json
python {SKILL_DIR}/scripts/profile_sections.py {DATA_ROOT}/career-private/profile.json --json
```

## References list

| File | What it holds | When to read it |
|---|---|---|
| `references/sections.md` | The section catalogue (the sections, the fields each fills, the first-pass scope, the process that needs each section, the dependency in the order of asking, the criteria for judging reach stage), and how to use `profile_sections.py` | When choosing a section in Step 0, when reporting a remaining section at delivery, when adding or removing a section |
| `references/sections/{id}.md` | Each section's procedure, its opening question, the settled wording passed to AskUserQuestion, and the downstream process it serves | When eliciting that section (reading only this file and `question-bank.md`'s common rules per section) |
| `references/elicitation-guide.md` | The grounding for chronological × project-unit recall cues, handling concurrent employment and an employment gap, the grounding for importing an existing document and lightening the first pass, the operation of preferring the choice format, the elicitation notes' recording format, update practice, and sources with a DOI or URL | When settling the elicitation policy, when confirming an audit perspective |
| `references/answer-handling.md` | The types of question that never doubt a statement, the 3 operations elicitation may perform (making a statement concrete, supporting quantification, rewording), the scale of role phrasing and its replacement table, handling each answer format, how to record a career history with an atypical shape, and the notes' line formats | Whenever an answer comes in, when presenting a reworded candidate, when eliciting a career history with an atypical shape, when the audit checks the scope of a reworded sentence |
| `references/question-bank.md` | The common rules for the register of question text and the choice-format operation (shared with `job-change-axis`), the settled wording for Step 0 (choosing the mode and the sections), and the correspondence table between questions and sections/fields | When starting elicitation, when asking the mode and the sections in Step 0 |
| `references/quantification-guide.md` | Patterns for quantification and alternative phrasing, the risk of a figure that departs from fact, the limits of quantification's effect, dependency on occupation, and sources with a DOI or URL | When judging a quantitative expression during elicitation, writing, or audit of an achievement |
| `references/profile-methods.md` | The information the hiring side looks at, skill classification, the real picture of ATS (applicant tracking systems), the consequences of falsifying a career history, the limits of the design and its evidence gaps, and sources with a DOI or URL | When confirming the grounding for a design decision, when settling an audit perspective |
