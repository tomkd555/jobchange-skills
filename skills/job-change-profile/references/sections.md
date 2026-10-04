# Section catalogue (sections)

profile.json (`schema_version` 3.0) holds the career record and is built in the sections below. A section is the unit of elicitation and update. The canonical definition of the schema is in the hub's `references/profile-format.md`. This document groups its fields into units that get asked together and completed together. The document to read for building one section is confined to that section's single file (`sections/{id}.md`). The job-change axis (reasons, conditions, work-character preferences, scoring axes, targets, salary) is stored in axis.json, and its sections belong to `job-change-axis`.

`scripts/profile_sections.py` encodes the section IDs in this catalogue and the judgment of reach stage. When a section is added to or removed from this catalogue, the script and its unit tests receive the same change.

## Section list

| Section ID | Name | Fields it fills | First pass | Process that needs it | Canonical procedure |
|---|---|---|---|---|---|
| `basic` | Basic information | `basic.*` | Current role only | Rirekisho (`job-change-documents`) | `sections/basic.md` |
| `career` | Career skeleton | `company`, `period`, `role`, `employment_type`, `assignment`, `note` of `career_history[]`, and `career_gaps[]` | Skeleton | Every process | `sections/career.md` |
| `achievements` | Responsibilities and achievements | `career_history[].responsibilities`, `career_history[].achievements[]` | skip | Application documents (`job-change-documents`), self-analysis (`job-change-self-analysis`) | `sections/achievements.md` |
| `skills` | Skill inventory | `skills.*` | skip | Application documents, fit assessment (`job-change-fit-assessment`) | `sections/skills.md` |

`summary`, `strengths`, `notes`, and `updated_at` belong to no section. The writer summarizes `summary` from the elicitation notes. `strengths` is written on the hand-off from `job-change-self-analysis`: that skill's Step 6 passes its short statements of strength to this skill, and they enter profile.json through a profile update. The main session writes `updated_at` at delivery time.

## Section order

Some sections depend on others for the order in which they are asked. Sections with no dependency can be taken in whatever order the user chooses.

- `career` → `achievements` → `skills`. Achievements are asked for within the frame of the career history, and skill candidates are built from what comes up while discussing achievements.
- `basic` can be asked on its own.

## Reach stages

Each section has three stages: `missing`, `skeleton`, and `deep`. The stage is decided from the content of profile.json alone, without the memory of the conversation or the elicitation notes. The judgment is implemented in `scripts/profile_sections.py`, under the conditions in the table below.

| Section ID | `skeleton` (a skeleton exists) | `deep` (the detailed pass is done) |
|---|---|---|
| `basic` | `current_role` exists | `years_of_experience`, `location`, and `education` also exist |
| `career` | At least one career-history entry has `company`, `period`, and `role` filled | Every entry is filled, and every entry's `period` reads in the prescribed format |
| `achievements` | Some career-history entry has `responsibilities` or `achievements` | Every career-history entry has `responsibilities`, and at least one achievement has a quantitative `metric` |
| `skills` | At least one category has an item | `technical` or `business` exists, and `portable` also exists |

`deep` marks that the level of detail a downstream process needs has been reached; as more achievements come in, `achievements` returns to being a target for additions even after reaching `deep` (the canonical definition for update operation is in `elicitation-guide.md`).

## Scope of the first pass

On first creation, the first pass fills every section whose "First pass" column holds a value other than `skip`, up to `skeleton`, so that profile.json becomes valid: `basic` (current role) and `career`. The remaining sections are each built later, one at a time, as a "section update," once a downstream process needs it. The rationale is in "Importing an existing document and lightening the first pass" in `elicitation-guide.md`.

A profile.json that fills only the first-pass scope passes `validate_profile.py`. The following 2 WARNs are expected within the first-pass scope and are never grounds for sending the work back.

- No achievement has a quantitative `metric`
- `skills` is empty

## How to use the script

```bash
python {SKILL_DIR}/scripts/profile_sections.py {PROFILE}
python {SKILL_DIR}/scripts/profile_sections.py {PROFILE} --json
```

The exit code is always 0. Pass/fail is decided by `validate_profile.py`. This script only reports each section's stage. The `--json` output has `sections[]` and `initial_complete`. Each element of `sections[]` has `id`, `state`, `initial`, and `needed_by`. `initial_complete` states whether every section in the first-pass scope has reached `skeleton` or beyond.

Step 0 shows this output alongside the section choices, in the form given in `question-bank.md`'s Step 0.
