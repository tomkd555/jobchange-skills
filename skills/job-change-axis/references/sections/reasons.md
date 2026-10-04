# Section: Reasons for changing jobs (reasons)

Records, as an array of short sentences, what the user wants to achieve next by changing jobs. The first pass settles at least one item. Constructive rephrasing and grounding belong to `job-change-self-analysis`. That skill's Step 6 writes only the resulting values back into this section. The section catalogue and the definition of reach stages are in `../sections.md`.

## Fields to fill

| Field | First pass | Format |
|---|---|---|
| `job_change_axis.reasons` | First pass (at least one item required) | Free text (choices cannot be enumerated in advance) |

## Reach stages

| Stage | Condition |
|---|---|
| `skeleton` | `reasons` has at least one item |
| `deep` | Same as skeleton. The detailed pass belongs to `job-change-self-analysis` |

## Procedure

Opening question:

- What does the user want to achieve next by changing jobs? When the answer is framed as dissatisfaction with the current situation, record it as stated, then also ask for one sentence framed as what to achieve next.

In the detailed pass, keep the user from ruminating emotionally by directing questions toward facts: when, in what situation, what the user did. Do not repeat "why." Constructive rephrasing of reasons for leaving and grounding of strengths lie outside this skill's scope. Direct the user to `job-change-self-analysis` (the rationale is in the must/want section of `../axis-methods.md`).

`reasons` is the entry point to the `conditions` section. A condition mentioned within a reason for changing jobs (salary, work location, work style) stays as a sentence in this section; it is structured into an axis, operator, and threshold in the `conditions` section.

## Downstream

The statement of purpose in application documents (`job-change-documents`), the consistency perspective in job interview preparation (`job-change-interview-prep`), and `reason_for_change` in self-analysis (`job-change-self-analysis`) all read this section.
