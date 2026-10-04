# Section: Basic information (basic)

Records the current role, years of experience, place of residence, and educational background. The first pass asks only about the current role. The rest is filled in just before building the rirekisho. The section catalogue and the definition of reach stages are in `../sections.md`.

## Fields to fill

| Field | First pass | Format |
|---|---|---|
| `basic.current_role` | First pass | Free text |
| `basic.years_of_experience` | Detailed pass | Free text (numeric) |
| `basic.location` | Detailed pass | Free text (a prefecture is enough) |
| `basic.education` | Detailed pass | Free text (newest first) |

None of these can have their choices enumerated in advance, so all are asked as free text.

## Reach stages

| Stage | Condition |
|---|---|
| `skeleton` | `current_role` exists |
| `deep` | `years_of_experience`, `location`, and `education` also exist |

## Procedure

1. Ask for the current role and title. When the person does not hold a position at present, ask for the role at the most recent position and record that fact in the elicitation notes.
2. In the detailed pass, ask for total years of practical work experience, place of residence, and educational background. Record the educational background in the person's own words: school name, department, and graduation month and year.
3. Record years of experience exactly as the person states them. When the interviewer computes a value from the career-history periods instead, mark that value explicitly as an estimate in the notes (`../elicitation-guide.md`).

## Downstream

The rirekisho (`job-change-documents`) uses every field of `basic`.
