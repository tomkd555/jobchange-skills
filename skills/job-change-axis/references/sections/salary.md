# Section: Annual salary (salary)

Records the current annual salary and the desired annual salary, in yen. The first pass skips this section. It is done as a section update right before fit assessment. This also keeps a question as sensitive as current salary out of the first pass (see "Importing an existing document and lightening the first pass" in `job-change-profile`'s `references/elicitation-guide.md`). The section catalogue and the definition of reach stages are in `../sections.md`.

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

Ask with the settled wording below. Annual salary differs between gross and net, with and without bonus and overtime pay, and between a projection and an actual figure, so the question fixes one meaning: the gross figure over the most recent year, including bonuses and overtime pay. When the user answers using a different counting method, record the figure as given and note that method alongside it. The interviewer does not convert it. The general rules for recording a figure (a range, an approximation, 「未回答（本人の意向）」) are in "Supporting quantification" and "Handling each answer format" in `job-change-profile`'s `references/answer-handling.md`.

| Item | Wording |
|---|---|
| Annual salary question | 年収は、直近1年の額面（賞与を含み、残業代を含む）でお答えください。別の数え方であれば、その旨を添えてください。 (For annual salary, please answer with the gross figure for the most recent year, including bonus and overtime pay. If you count it a different way, please note that as well.) |

Place the non-negotiable salary floor in the `conditions` section (`axis=salary_condition`), and the desired figure in this section's `desired`. When the floor exceeds the desired figure, `validate_axis.py` raises a WARN, so cross-check the two immediately whenever both are asked.

When deciding the standard for the compensation level (`compensation_level`) in the `score_axes` section, the default approach places the current annual salary at `zero` and the desired annual salary at `full`. Filling in this section beforehand shortens that later question.

## Downstream

The compensation dimension of fit assessment (`job-change-fit-assessment`), and its computation of the difference in binding hours against the current job, read `current` and `desired`. Job search (`job-change-job-search`) receives only the salary floor from `conditions`. `current` is never passed to it (the canonical definition is in the hub's `references/pii-boundary.md`).
