# Section catalogue (sections)

profile.json is built as 10 sections. A section is the unit of elicitation and update. The canonical definition of the schema lives in the hub's `references/profile-format.md`; this document groups its fields into units that get asked together and deep-dived together. The document to read for building one section is confined to that section's single file (`sections/{id}.md`).

`scripts/profile_sections.py` implements the section ids in this catalogue and the judgment of reach stage. When a section is added to or removed from this catalogue, the script and its unit tests receive the same change.

## Section list

| Section id | Name | Fields it fills | First pass | Process that needs it | Canonical procedure |
|---|---|---|---|---|---|
| `basic` | Basic information | `basic.*` | Current role only | Rirekisho (`job-change-documents`) | `sections/basic.md` |
| `career` | Career skeleton | `company`, `period`, `role`, `employment_type`, `assignment`, `note` of `career_history[]`, and `career_gaps[]` | Skeleton | Every process | `sections/career.md` |
| `achievements` | Responsibilities and achievements | `career_history[].responsibilities`, `career_history[].achievements[]` | skip | Application documents (`job-change-documents`), self-analysis (`job-change-self-analysis`) | `sections/achievements.md` |
| `skills` | Skill inventory | `skills.*` | skip | Application documents, fit assessment (`job-change-fit-assessment`) | `sections/skills.md` |
| `reasons` | Reasons for changing jobs | `job_change_axis.reasons` | At least one item | Application documents, job interview preparation (`job-change-interview-prep`), self-analysis | `sections/reasons.md` |
| `conditions` | Structured conditions | `job_change_axis.conditions[]`, `job_change_axis.priority_note` | Key conditions only | Job search (`job-change-job-search`), fit assessment | `sections/conditions.md` |
| `work_character` | Work-character preferences | `job_change_axis.work_character_preferences[]` | All 8 items | Job search, fit assessment | `sections/work_character.md` |
| `score_axes` | Company scoring axes | `company_score_axes[]` | skip | Fit assessment, company research (`job-change-company-research`) | `sections/score_axes.md` |
| `targets` | Target companies and roles | `targets.*` | skip | Company research, job search | `sections/targets.md` |
| `salary` | Annual salary | `salary.*` | skip | Fit assessment | `sections/salary.md` |

`summary`, `strengths`, `notes`, and `updated_at` belong to no section. `summary` is summarized by the writer from the elicitation notes; the deepening of `strengths` and `job_change_axis.reasons` is where `job-change-self-analysis` writes its values back. `updated_at` is written by the main session at delivery time.

## Section order

Some sections depend on others for the order in which they are asked. Sections with no dependency can be taken in whatever order the user chooses.

- `career` → `achievements` → `skills`. Achievements are asked for within the frame of the career history, and skill candidates are built from what comes up while discussing achievements.
- `reasons` → `conditions` → `work_character` → `score_axes`. Conditions are structured after the reasons for changing jobs are heard, and scoring axes are decided while watching for mismatches against the must-have conditions.
- `basic`, `targets`, and `salary` can each be asked on their own. `salary` is handled as a pair with the annual-salary floor in `conditions`, so asking them together leaves less to redo later.

## Reach stages

Each section has three stages: `missing`, `skeleton`, and `deep`. The stage is decided from the content of profile.json alone, never from the memory of the conversation or the elicitation notes. The judgment is implemented in `scripts/profile_sections.py`, under the conditions in the table below.

| Section id | `skeleton` (a skeleton exists) | `deep` (the deep dive is done) |
|---|---|---|
| `basic` | `current_role` exists | `years_of_experience`, `location`, and `education` also exist |
| `career` | At least one career-history entry has `company`, `period`, and `role` filled | Every entry is filled, and every entry's `period` reads in the prescribed format |
| `achievements` | Some career-history entry has `responsibilities` or `achievements` | Every career-history entry has `responsibilities`, and at least one achievement carries a quantitative `metric` |
| `skills` | At least one category has an item | `technical` or `business` exists, and `portable` also exists |
| `reasons` | `reasons` has at least one item | Same as skeleton. The deep dive belongs to `job-change-self-analysis` |
| `conditions` | Under 2.0, `conditions` has at least one item. Under 1.x, `must_conditions` or `want_conditions` exists | Under 2.0, at least one item has `level=must`, and every such item has `priority`. Under 1.x, the section stays at `skeleton` until the migration is complete |
| `work_character` | All 8 traits are present, no more and no fewer | Same as skeleton |
| `score_axes` | `company_score_axes` has at least one item | Same as skeleton |
| `targets` | At least one category has an item | Same as skeleton |
| `salary` | `desired` is numeric | `current` is also numeric |

`deep` is a marker that the granularity a downstream process needs has been reached; as more achievements come in, `achievements` returns to being a target for additions even after reaching `deep` (the canonical definition for update operation lives in `elicitation-guide.md`).

## Scope of the first pass

On first creation, the first pass fills every section whose "First pass" column is not `skip`, up to `skeleton`, so that profile.json becomes valid. That means the five sections `basic` (current role), `career`, `reasons`, `conditions` (key conditions only), and `work_character`. The remaining sections are each built later, one at a time, as a "section update," once a downstream process needs it. The rationale lives in "Importing an existing document and lightening the first pass" in `elicitation-guide.md`.

A profile.json that fills only the first-pass scope passes `validate_profile.py`. The following 4 WARNs are expected within the first-pass scope and are not grounds for sending the work back.

- No achievement carries a quantitative `metric`
- `skills` is empty
- `targets` is empty
- A `level=must` condition has no `priority`

## How to use the script

```bash
python {SKILL_DIR}/scripts/profile_sections.py {DATA_ROOT}/career-private/profile.json
python {SKILL_DIR}/scripts/profile_sections.py {DATA_ROOT}/career-private/profile.json --json
```

The exit code is always 0. Pass/fail is decided by `validate_profile.py`; this script only reports each section's stage. The `--json` output has `sections[]` and `initial_complete`. Each element of `sections[]` has `id`, `state`, `initial`, and `needed_by`; `initial_complete` states whether every section in the first-pass scope has reached `skeleton` or beyond.

Step 0 shows this output alongside the section choices. A `missing` section is shown as 「まだ無い」 (not yet started), a `skeleton` section as 「深掘りがこれから」 (the deep dive is still ahead), and a `deep` section as 「更新なら選ぶ」 (pick this one for an update).
