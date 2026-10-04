---
name: job-change-axis
description: >-
  Sub-skill of the job-change support skill group, dedicated to creating and updating axis.json, the user's
  job-change axis: reasons for changing jobs, structured must/want conditions, work-character preferences, company
  scoring axes, target companies and roles, and annual salary. It elicits each section through its own single-file
  procedure and judges each section's reach stage (missing / skeleton / deep) with a script. The first pass settles
  the reasons, the key conditions and the 8 work-character preferences; the other sections follow just before the
  process that needs them. Elicitation centers on AskUserQuestion's choice format, at most 4 questions per call with
  up to 4 choices each. Writing and independent audit are each handled by a dedicated agent
  (job-change-axis-writer / job-change-axis-auditor). It splits a 1.x/2.0 profile.json into profile.json and
  axis.json before its first write, and holds the conversation that moves a 1.x axis to 2.0. The career record
  (profile.json) is optional input. It runs when dispatched from job-change-support (the hub). The career record
  belongs to job-change-profile; grounding reasons and strengths belongs to job-change-self-analysis.
  Use when the user wants to settle or revise what they want from a job change in Japan: reasons for changing jobs,
  non-negotiable and desirable conditions, work-style preferences, how to score companies, target companies and
  roles, or current and desired salary.
  trigger words: 転職の軸を登録, 転職の軸を決めたい, 転職の軸を見直したい, 希望条件の整理, 必須条件, 譲れない条件,
  企業の採点軸, 希望年収, job-change axis, must-have conditions, job preferences, desired salary。
allowed-tools: Read, Write, Glob, Grep, Bash, AskUserQuestion, Agent, Skill
---

# job-change-axis

This skill holds the complete procedure, from elicitation through delivery, for creating or updating axis.json,
the user's job-change axis. axis.json is built in sections, and each section has one file,
`references/sections/{id}.md`, holding its procedure and settled wording (the catalogue is `references/sections.md`).
axis.json is settled through writing, mechanical validation, and independent audit. Job search, fit assessment and
company research need it; application documents, self-analysis and job interview preparation read it when it
exists.

## Purpose and principles

1. **Keep must-have conditions to a small number, and treat the axis as open to reassessment.** The separation
   between conditions that cannot be given up and conditions that are merely desirable is kept. Must-have
   conditions (the sum of `conditions[level=must]` and `work_character_preferences[desire=must]`) are narrowed to
   about 3 items, with their priority and the time for reassessment kept as metadata. A user's preferences settle
   over the course of elicitation and change over time, so the axis stays a working answer
   (`references/axis-methods.md`).

2. **Record the user's own statements as stated.** Elicitation asks for facts and preferences and records them in
   the user's words. It never assigns a free-text condition to an axis, an operator or a threshold on its own
   judgment: an unsettled condition stays qualitative until the user settles it. The shared rules for handling
   answers and rewording are in `job-change-profile`'s `references/answer-handling.md`.

3. **Build section by section.** On first creation, the first pass fills `reasons`, `conditions` (key conditions
   only) and `work_character` to `skeleton`, which makes axis.json valid. The other sections, and the detailed pass on
   the first-pass sections, are each done as a "section update" once a downstream process needs that section.
   `scripts/axis_sections.py` judges each section's stage from `{AXIS}` alone, without the memory of the
   conversation (the rationale is in "Importing an existing document and lightening the first pass" in
   `job-change-profile`'s `references/elicitation-guide.md`).

4. **Leave the user's judgment with the user.** When the scoring axes conflict with a must-have condition, the skill
   presents both sides and the user chooses. Introspective work (constructive rewording of a reason, grounding a
   preference) is directed to `job-change-self-analysis`.

5. **Personal information is never sent outward.** The personal information axis.json holds (salary, conditions,
   reasons) is never used in any outward transmission, including a search query, a fetch, or an external API. The
   canonical listing of what falls inside the boundary and which role may access it is in the hub's
   `{HUB_SKILL_DIR}/references/pii-boundary.md`. This skill builds `axis.json` and appends to
   `profile_interview_notes.md`, both inside that boundary. Neither the writer (job-change-axis-writer) nor the
   auditor (job-change-axis-auditor) has a means to send data to the web, so these paths may be passed to them.

## Scope

This skill handles the six axis sections. Requests outside them go to:

- Career history, achievements, skills, basic information, strengths: `job-change-profile`.
- Grounding reasons and strengths, a career narrative, constructive rewording of reasons for leaving:
  `job-change-self-analysis`. Its Step 6 hands `reasons` and a `work_character` correction back here as a section
  update.
- Application documents: `job-change-documents`.
- Company research: `job-change-company-research`.

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
`job-change-support` at the same install location. The configuration file's specification is in
`docs/configuration.md`.

## Data layout

| Path | Role | Input/output |
|---|---|---|
| `career-private/axis.json` | The canonical source of the job-change axis | Output (this skill creates and updates it) |
| `career-private/profile_interview_notes.md` | Elicitation notes, shared with `job-change-profile`. The recording format is in `job-change-profile`'s `references/elicitation-guide.md` | Output (the main session appends to it as elicitation proceeds) |
| `career-private/profile.json` | The career record | Optional input. A 1.x/2.0 file is split in Step 0 before the first write |

- `{PROFILE}` denotes the absolute path of `career-private/profile.json`, `{AXIS}` the axis source, and `{NOTES}`
  the absolute path of `profile_interview_notes.md`. The resolution order of `{AXIS}`, and the stop state when
  axis.json sits beside a 1.x/2.0 profile.json, are in "Location" of the hub's `references/axis-format.md`.
- The canonical definition of axis.json's fields and validation rules is in the hub's
  `references/axis-format.md`. A filled-in example is in the hub's `assets/axis_example.json` (a fictitious
  person).
- No user data is placed in the skill's own folder (`skills/job-change-axis/`). When `career-private/` does not yet
  exist, this skill creates it once it is needed.

## Sections and reach stages

The canonical definition of the section list, the fields each fills, the first-pass scope, the process that needs
each section, the order of asking, and the criteria for each reach stage (`missing` / `skeleton` / `deep`) is in
`references/sections.md`. Each section's procedure and settled wording is in `references/sections/{id}.md`.

| Section ID | Name | First pass |
|---|---|---|
| `reasons` | Reasons for changing jobs | At least one item |
| `conditions` | Structured conditions | Key conditions only |
| `work_character` | Work-character preferences | All 8 items |
| `score_axes` | Company scoring axes | skip |
| `targets` | Target companies and roles | skip |
| `salary` | Annual salary | skip |

An axis.json that fills only the first-pass scope passes `validate_axis.py`. The WARNs expected within that scope
are listed under "Scope of the first pass" in `references/sections.md`, and are never grounds for sending Step 5
back.

## Pipeline

Steps 0 through 6 run in order. The main session performs elicitation with AskUserQuestion (a sub-agent cannot
converse with the user). The question format, the register of question text, and the handling of each answer
format follow the common rules named at the top of `references/question-bank.md`. For a question whose choices can
be enumerated in advance, the section file's settled wording is used as it stands.

### Step 0: Resolving the axis source and checking the premises

1. Resolve `{AXIS}` by "Location" in the hub's `references/axis-format.md`. In the stop state (axis.json beside a
   1.x/2.0 profile.json), show the paths and stop until the user settles which file holds the axis.
2. When `{PROFILE}` is a 1.0, 1.1 or 2.0 file, this skill will write through its writer, so split it first:

   ```bash
   python {HUB_SKILL_DIR}/scripts/split_profile.py {PROFILE}
   ```

   Tell the user the backup path the report gives (`backup`). On exit 1, show the report's `errors` and stop. After
   the split, `{AXIS}` is `career-private/axis.json`.
3. When `{AXIS}` exists, validate it with the axis gate and grasp each section's stage:

   ```bash
   python {HUB_SKILL_DIR}/scripts/validate_axis.py {AXIS}
   python {SKILL_DIR}/scripts/axis_sections.py {AXIS}
   ```

4. When axis.json has `schema_version` `1.0` or `1.1`, ask whether the user wants to move the axis to 2.0 now. The
   move is a conversation held in the `conditions` section ("Migration from 1.x" in
   `references/sections/conditions.md`). A free-text condition is never assigned to an axis mechanically. When the
   user declines, the axis stays at 1.x and the skill states once which downstream judgments stay unavailable (the
   fallback table in "Version and migration" of the hub's `references/axis-format.md`).
5. Check the mode with AskUserQuestion: 「初回作成」, 「節の更新」, 「全面点検」 (the wording is in
   `references/question-bank.md`'s Step 0). For "section update," have the user choose the target sections, with
   each section's current stage attached to its choice. When a downstream sub-skill dispatches this skill naming a
   section it needs, that section is treated as a "section update" regardless of the mode.

profile.json is optional input. When it exists, the writer may read it for context (such as the current role
when targets are discussed). The axis is settled the same way when it does not exist.

### Steps 1-4: Elicitation by section

For each target section, read `references/sections/{id}.md` and ask with the procedure and settled wording it
holds. Append each answer to `{NOTES}` as it comes in, under the date heading the notes format prescribes. The
order between sections follows "Section order" in `references/sections.md`. The Step numbers match the column in
`references/question-bank.md`'s correspondence table.

| Step | Section | First pass | Canonical procedure |
|---|---|---|---|
| 1 | `reasons` | At least one item | `references/sections/reasons.md` |
| 2 | `conditions` | Key conditions only | `references/sections/conditions.md` |
| 3 | `work_character` | All 8 items | `references/sections/work_character.md` |
| 4 | `score_axes`, `targets`, `salary` | skip | `references/sections/score_axes.md`, `references/sections/targets.md`, `references/sections/salary.md` |

The section files hold the following matters, and SKILL.md does not repeat them.

- `conditions`: the 4 items of a condition (axis, operator, threshold, verification method), handling a qualitative condition,
  the count and priority of must-have conditions, and migration from 1.x.
- `work_character`: the desired level for each of the 8 traits, the `statement` for `desire=must`, and the 3 traits
  a job posting cannot settle.
- `score_axes`: choosing a quantitative axis, building a qualitative axis, weight and criteria, a check against two
  fictitious companies, and a mismatch between a scoring axis and a must-have condition.
- `salary`: the settled wording for the salary question and the pairing with the salary floor in `conditions`.

### Step 5: Writing, mechanical validation, independent audit

Launch the `job-change-axis-writer` agent (model: opus). Pass it the step to run, `{NOTES}`, the existing `{AXIS}`
(when updating), `{PROFILE}` when it exists, the hub's `references/axis-format.md`, the target sections, and the
output destination `{DATA_ROOT}/career-private/axis.json`. The writer creates or updates axis.json from the facts in
the notes alone. On its return, run the axis gate and confirm ERROR 0:

```bash
python {HUB_SKILL_DIR}/scripts/validate_axis.py {DATA_ROOT}/career-private/axis.json
```

Then launch the `job-change-axis-auditor` agent (model: opus) in a new context that withholds the writer's
reasoning. Pass it axis.json, `{NOTES}`, and the path of `validate_axis.py`. When `verdict` is BLOCK, or a finding
carries `severity` = must_fix, the work returns to the writing step of Step 5 (at most twice; after that, the user
decides).

A WARN for a section outside the first pass is expected; that section stays `missing` and is presented to the user
as a section still ahead.

### Step 6: Delivery

Rewrite `updated_at` to today's date. Attach the output of `scripts/axis_sections.py`, and summarize for the user
what was written: the reasons, the must-have conditions and their priority, the work-character traits marked
`must` or `important`, the company scoring axes, targets, and salary. Name each section still `missing` or
`skeleton` once, with the process that needs it (the "Section list" in `references/sections.md`). Then guide the
user to the downstream work that reads axis.json: job search in `job-change-job-search`, fit assessment in
`job-change-fit-assessment`, and company research in `job-change-company-research`. The final message opens with
its conclusion and states each point once. It omits empty sections and formulaic preambles.

## Pass/fail gate and send-back

| Gate | Passing condition and where a send-back returns to |
|---|---|
| Step 5's validation-and-audit gate | The work returns to Step 5's writing step when `validate_axis.py` FAILs (1 or more ERRORs), when `job-change-axis-auditor`'s `verdict` is BLOCK, or when a finding has `severity` = must_fix. A send-back happens at most twice for the same deliverable. |

On a send-back, the audit's findings (`target`, `evidence`, `fix`) are passed to the writer as they stand, and the
work runs again from Step 5's mechanical validation. A finding that two send-backs fail to resolve is delivered
only after the user has settled it as an open item. A mechanical validation ERROR is resolved before delivery
regardless of the send-back limit.

## Role execution (by harness)

The content of each role is in `references/roles/`, which is the canonical definition.

| Agent name | model | Canonical role prompt | Responsibility |
|---|---|---|---|
| `job-change-axis-writer` | opus | `{SKILL_DIR}/references/roles/axis-writer.md` | Creates and updates axis.json from the elicitation notes (Step 5) and reflects audit findings |
| `job-change-axis-auditor` | opus | `{SKILL_DIR}/references/roles/axis-auditor.md` | In an independent context, checks axis.json against the notes and reruns `validate_axis.py` (Step 5) |

Each agent's model is fixed in its own frontmatter and is never overridden at launch. The execution procedure by
harness and the reason for separating writing from auditing are in the hub's
`{HUB_SKILL_DIR}/references/role-execution.md`.

## Script CLI usage

`validate_axis.py` (the hub's) exits 0 for PASS and 1 for FAIL; WARN alone counts as PASS. `--json` outputs
`status`, `error_count`, `warning_count`, `errors`, and `warnings`. `axis_sections.py` (this skill's) always exits 0
and reports each section's stage; its output format is in "How to use the script" in `references/sections.md`.
`split_profile.py` (the hub's) is described in "Splitting a 1.x/2.0 profile.json" of the hub's
`references/axis-format.md`.

```bash
python {HUB_SKILL_DIR}/scripts/validate_axis.py {AXIS} --json
python {SKILL_DIR}/scripts/axis_sections.py {AXIS} --json
python {HUB_SKILL_DIR}/scripts/split_profile.py {PROFILE} --json
```

## References list

| File | What it holds | When to read it |
|---|---|---|
| `references/sections.md` | The section catalogue, the first-pass scope, the reach-stage criteria, and how to use `axis_sections.py` | When choosing a section in Step 0, when reporting a remaining section at delivery |
| `references/sections/{id}.md` | Each section's procedure, opening question, settled wording, and the downstream process it serves | When eliciting that section |
| `references/question-bank.md` | The pointers to the shared elicitation rules, the correspondence table between questions and fields, and the Step 0 wording | When starting elicitation, when asking the mode and the sections |
| `references/axis-methods.md` | The grounding and limits of must/want and of narrowing must-have conditions, with sources | When confirming the grounding for a design decision, when settling an audit perspective |
| The hub's `references/axis-format.md` | axis.json's fields, validation rules, `{AXIS}` resolution, versions, and the split procedure | When writing, validating, or resolving the axis source |
