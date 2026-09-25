# Section: Annual salary (salary)

Records the current annual salary and the desired annual salary, in yen. The first pass skips this section; it is done as a section update right before fit assessment. This also keeps a question as sensitive as current salary out of the first pass (see "Importing an existing document and lightening the first pass" in `../elicitation-guide.md`). The section catalogue and the definition of reach stages live in `../sections.md`.

## Fields to fill

| Field | Format |
|---|---|
| `salary.current`, `desired` | Free text (numeric, in yen) |

## Reach stages

| Stage | Condition |
|---|---|
| `skeleton` | `desired` is numeric |
| `deep` | `current` is also numeric |

## Procedure

The wording for the salary question lives in "Supporting quantification" in `../answer-handling.md`. Ask for the gross figure over the most recent year (including bonuses and overtime pay); when the user answers using a different counting method, note that method alongside the figure. The interviewer does not convert it.

Place the non-negotiable salary floor in the `conditions` section (`axis=salary_condition`), and the desired figure in this section's `desired`. When the floor exceeds the desired figure, `validate_profile.py` raises a WARN, so cross-check the two immediately whenever both are asked.

When deciding the standard for the compensation level (`compensation_level`) in the `score_axes` section, the default approach places the current annual salary at `zero` and the desired annual salary at `full`. Filling in this section beforehand shortens that later question.

## Downstream

The compensation dimension of fit assessment (`job-change-fit-assessment`), and its computation of the difference in binding hours against the current job, read `current` and `desired`. Job search (`job-change-job-search`) receives only the salary floor from `conditions`; `current` is never passed to it (the canonical definition lives in the hub's `references/pii-boundary.md`).
