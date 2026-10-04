# Structured question set (question-bank)

This is the canonical definition of the correspondence table between job-change-axis's questions and its
sections/fields, and of the Step 0 wording (choosing the mode and the sections). Each section's procedure, its
opening question, and the settled wording passed to AskUserQuestion are in that section's own `sections/{id}.md`
(the catalogue is `sections.md`). The canonical definition of the field specification is in the hub's
`references/axis-format.md`.

The common rules for elicitation are in `job-change-profile` and apply to this skill as they stand:

- the register of the question text and the rules for choice-format operation: "The register of the question text"
  and "Rules for use" in `job-change-profile`'s `references/question-bank.md`;
- handling each answer format, the question types that never doubt a statement, and the notes' line formats:
  `job-change-profile`'s `references/answer-handling.md`;
- the choice-format operation and the elicitation notes' recording format: `job-change-profile`'s
  `references/elicitation-guide.md`.

Eliciting one section reads those common rules and that section's own `sections/{id}.md`, and leaves other
sections' files unread until their turn.

## Correspondence table between questions and sections/fields

The "First pass" column marks a question asked within the first-pass scope (`sections.md`'s "Scope of the first
pass") as `初回` (first pass), and a question asked later, at a section update just before the downstream process
needs it, as `深掘り` (detailed pass).

| Step | Section | Question | Field it fills | Format | First pass |
|---|---|---|---|---|---|
| 1 | `reasons` | What the user wants to achieve next by changing jobs (reasons for changing jobs) | `job_change_axis.reasons` | Free text (the choices cannot be enumerated in advance) | 初回 |
| 2 | `conditions` | A condition that cannot be given up, a condition that is desirable, and its axis, threshold, and means of verification | `job_change_axis.conditions[]` | Choice format + free text | 初回 for key conditions only; full coverage is 深掘り |
| 2 | `conditions` | The priority and reassessment time of a must-have condition | `job_change_axis.conditions[].priority`, `job_change_axis.priority_note` | Choice format + free text | 深掘り |
| 3 | `work_character` | The desired level for each of the 8 work-character traits | `job_change_axis.work_character_preferences[]` | Choice format | 初回 |
| 4 | `score_axes` | Which of the 9 quantitative candidate axes for scoring a company matter, and which non-numeric matter the user wants scored (a qualitative axis's name, definition, and judgment conditions) | `company_score_axes[].axis`, `company_score_axes[].kind`, `company_score_axes[].label`, `company_score_axes[].definition`, `company_score_axes[].judgment[]` | Choice format + free text | 深掘り |
| 4 | `score_axes` | The weight assigned to each chosen axis (summing to 100), and the criteria used for a quantitative axis (asked together in one AskUserQuestion call) | `company_score_axes[].weight`, `company_score_axes[].thresholds` | Choice format (an allocation candidate, a choice of criteria) + free text (figures) + choice format (a check against 2 companies) | 深掘り |
| 4 | `targets` | The desired industry, occupation, and company | `targets.industries`, `targets.roles`, `targets.companies` | Free text (the choices cannot be enumerated in advance) | 深掘り |
| 4 | `salary` | Current and desired annual salary | `salary.current`, `salary.desired` | Free text (a figure) | 深掘り |

## Step 0: Confirming the mode and the sections

### Settled wording: mode

| Item | Wording |
|---|---|
| `header` | モード (Mode) |
| `question` | 今回は転職の軸をどのように扱いますか。 (How would you like to handle your job-change axis this time?) |
| Choice 1 | **初回作成**: まだ転職の軸がありません。転職理由・主な条件・作業特性を伺います。 (First creation: no job-change axis exists yet. We will ask for your reasons for changing jobs, key conditions, and work-character preferences.) |
| Choice 2 | **節の更新**: 既にある転職の軸の一部だけを作る、または直します。次にどの節かを伺います。 (Section update: part of the existing job-change axis will be built or corrected. Next, we will ask which section.) |
| Choice 3 | **全面点検**: 既にある転職の軸を最初から見直します。 (Full review: the existing job-change axis will be reviewed from the start.) |

Only when "section update" is chosen, go on to ask which sections are the target. The sections are split across 2
questions, asked in one AskUserQuestion call with `multiSelect: true`. Attach the current stage `axis_sections.py`
returned to the end of each choice's description, in the form 「いまは {段階}」 (currently: {stage}) (write `missing`
as 「まだ無い」, `skeleton` as 「骨格まで」, and `deep` as 「深掘り済み」).

| Item | Wording |
|---|---|
| Question 1 `header` | 転職の軸 (Job-change axis) |
| Question 1 `question` | どの節を更新しますか。転職の軸に関する節から選んでください。 (Which section will you update? Choose from the sections about your job-change axis.) |
| `multiSelect` | true |
| Choices | **転職理由**: 転職で次に実現したいことです。／ **条件**: 譲れない条件・望ましい条件と、その優先順位です。／ **作業特性**: 8つの作業特性それぞれの希望度です。／ **企業スコアの採点軸**: 企業を採点する軸と重みです。 (Reasons for changing jobs: what you want to achieve next by changing jobs. / Conditions: a condition you cannot give up, one that is desirable, and their priority. / Work-character preferences: the desired level for each of the 8 work-character traits. / Company scoring axes: the axes and weights for scoring a company.) |
| Question 2 `header` | 志望と年収 (Targets and salary) |
| Question 2 `question` | 同じく、志望と年収に関する節から選んでください。 (Likewise, choose from the sections about targets and salary.) |
| `multiSelect` | true |
| Choices | **志望対象**: 志望する業界・職種・企業です。／ **年収**: 現年収と希望年収です。 (Target companies and roles: the desired industry, occupation, and company. / Annual salary: current and desired annual salary.) |

Question 1's choices correspond in order to `reasons`, `conditions`, `work_character`, `score_axes`; Question 2's to
`targets`, `salary`.

When a downstream sub-skill dispatches this skill naming a section it needs, this question is skipped, and the
named section becomes the target directly.

Introspective work (constructive rewording of a reason, grounding a value in reasons) belongs to
`job-change-self-analysis`. The grounding for keeping must-have conditions to a small number and treating them as
open to reassessment is in `axis-methods.md`.
