# Section catalogue (sections)

axis.json is built in the sections below. A section is the unit of elicitation and update. The canonical definition of the schema is in the hub's `references/axis-format.md`. This document groups its fields into units that get asked together and completed together. The document to read for building one section is confined to that section's single file (`sections/{id}.md`).

`scripts/axis_sections.py` contains the section IDs in this catalogue and the code that judges the reach stage. When a section is added to or removed from this catalogue, the script and its unit tests receive the same change.

## Section list

| Section ID | Name | Fields it fills | First pass | Process that needs it | Canonical procedure |
|---|---|---|---|---|---|
| `reasons` | Reasons for changing jobs | `job_change_axis.reasons` | At least one item | Application documents (`job-change-documents`), job interview preparation (`job-change-interview-prep`), self-analysis (`job-change-self-analysis`) | `sections/reasons.md` |
| `conditions` | Structured conditions | `job_change_axis.conditions[]`, `job_change_axis.priority_note` | Key conditions only | Job search (`job-change-job-search`), fit assessment (`job-change-fit-assessment`) | `sections/conditions.md` |
| `work_character` | Work-character preferences | `job_change_axis.work_character_preferences[]` | All 8 items | Job search, fit assessment | `sections/work_character.md` |
| `score_axes` | Company scoring axes | `company_score_axes[]` | skip | Fit assessment, company research (`job-change-company-research`) | `sections/score_axes.md` |
| `targets` | Target companies and roles | `targets.*` | skip | Company research, job search | `sections/targets.md` |
| `salary` | Annual salary | `salary.*` | skip | Fit assessment | `sections/salary.md` |

`schema_version` and `updated_at` belong to no section. `job-change-self-analysis` writes its values for `job_change_axis.reasons` and its `work_character` correction back through a section update of this skill. The main session writes `updated_at` at delivery time.

## Section order

Some sections depend on others for the order in which they are asked. Sections with no dependency can be taken in whatever order the user chooses.

- `reasons` → `conditions` → `work_character` → `score_axes`. Conditions are structured after the reasons for changing jobs are heard, and scoring axes are decided while watching for mismatches against the must-have conditions.
- `targets` and `salary` can each be asked on their own. `salary` is handled as a pair with the annual-salary floor in `conditions`, so asking them together leaves less to redo later.

## Reach stages

Each section has three stages: `missing`, `skeleton`, and `deep`. The stage is decided from the content of `{AXIS}` alone, without the memory of the conversation or the elicitation notes. The judgment is implemented in `scripts/axis_sections.py`, under the conditions in the table below. A 1.x/2.0 `profile.json` passed as `{AXIS}` is judged the same way.

| Section ID | `skeleton` (a skeleton exists) | `deep` (the detailed pass is done) |
|---|---|---|
| `reasons` | `reasons` has at least one item | Same as skeleton. Grounding the reasons belongs to `job-change-self-analysis` |
| `conditions` | Under 2.0, `conditions` has at least one item. Under 1.x, `must_conditions` or `want_conditions` exists | Under 2.0, at least one item has `level=must`, and every such item has `priority`. Under 1.x, the section stays at `skeleton` until the migration is complete |
| `work_character` | All 8 traits are present, no more and no fewer | Same as skeleton |
| `score_axes` | `company_score_axes` has at least one item | Same as skeleton |
| `targets` | At least one category has an item | Same as skeleton |
| `salary` | `desired` is numeric | `current` is also numeric |

`deep` marks that the level of detail a downstream process needs has been reached.

## Scope of the first pass

On first creation, the first pass fills every section whose "First pass" column holds a value other than `skip`, up to `skeleton`, so that axis.json becomes valid. These sections are `reasons`, `conditions` (key conditions only), and `work_character`. The remaining sections are each built later, one at a time, as a "section update," once a downstream process needs it. The rationale is in "Importing an existing document and lightening the first pass" in `job-change-profile`'s `references/elicitation-guide.md`.

An axis.json that fills only the first-pass scope passes `validate_axis.py`. The following 2 WARNs are expected within the first-pass scope and are never grounds for sending the work back.

- `targets` is empty
- A `level=must` condition has no `priority`

## How to use the script

```bash
python {SKILL_DIR}/scripts/axis_sections.py {AXIS}
python {SKILL_DIR}/scripts/axis_sections.py {AXIS} --json
```

The exit code is always 0. Pass/fail is decided by `validate_axis.py`. This script only reports each section's stage. The `--json` output has `sections[]` and `initial_complete`. Each element of `sections[]` has `id`, `state`, `initial`, and `needed_by`. `initial_complete` states whether every section in the first-pass scope has reached `skeleton` or beyond.

Step 0 shows this output alongside the section choices, in the form given in `question-bank.md`'s Step 0.
