# Section: Structured conditions (conditions)

Places non-negotiable and preferred conditions into `job_change_axis.conditions[]` in the form of an axis, an operator, and a threshold. They are never left as free-text sentences. The first pass asks only about the key conditions (the non-negotiable annual-salary floor, plus any constraint on work location or remote work, are enough). Full coverage and prioritization of conditions are done as a section update right before fit assessment. The field specification is in the hub's `references/axis-format.md`, and the vocabulary of axes is in the hub's `references/screening-axes.md`. The section catalogue and the definition of reach stages are in `../sections.md`.

## Fields to fill

| Field | First pass | Format |
|---|---|---|
| `job_change_axis.conditions[]` | First pass covers key conditions only; full coverage is a detailed pass | Multiple choice (`level`, `axis`, `verification`) plus free text (`operator`, `value`, `unit`) |
| `job_change_axis.conditions[].priority` | Detailed pass | Multiple choice plus free text |
| `job_change_axis.priority_note` | Detailed pass | Multiple choice plus free text |

## Reach stages

| Stage | Condition |
|---|---|
| `skeleton` | Under 2.0, `conditions` has at least one item. Under 1.x, `must_conditions` or `want_conditions` exists |
| `deep` | Under 2.0, at least one item has `level=must`, and every such item has `priority`. Under 1.x, the section stays at `skeleton` until the migration is complete |

## Procedure

Opening question:

- What are the non-negotiable conditions (work location, work style, technology, salary, and so on)? If any, what are the preferred conditions?

For each condition, settle the following with AskUserQuestion (one question may cover multiple conditions together).

| Item to settle | Question |
|---|---|
| `level` | Is this a non-negotiable condition, or one that is desirable if present? |
| `axis` | Does it fall under remote-work certainty, overtime, annual holidays, night duty, ratio of hands-on work, ratio of coordination work, closeness to experience, or salary? Or does it fall under none of these? |
| `operator`, `value`, `unit` | (When it falls under an axis) At what value can the condition be said to be met? For overtime, the monthly cap; for annual holidays, the yearly floor on the number of days; for salary, the floor amount. |
| `verification` | Can this be judged from what a job posting states, does it need company research, or can it only be confirmed at the job interview? |

Some qualitative conditions fit none of the axes, such as 「モダンな技術スタックが整備されていること」 (a modern technology stack is in place). For such a condition, set `axis` to `null`, `operator` to `qualitative`, and `value` to `null`. Set `verification` to `research` or `interview`. Tell the user that this kind of condition is handed off for confirmation through company research and at the job interview.

Place the non-negotiable annual-salary floor in this section (`axis=salary_condition`). Place the desired figure in the `salary` section. The former is used by job search as a threshold. The latter is used by the compensation dimension of fit assessment.

### Settled wording: condition level

| Item | Wording |
|---|---|
| `header` | 譲れるか (Negotiable?) |
| `question` | この条件は、満たさないなら見送る条件ですか。 (Is this a condition you would pass on an offer for not meeting?) |
| Choice 1 | **譲れない**：満たさない求人は見送ります。 (Non-negotiable: I will pass on an offer that does not meet this.) |
| Choice 2 | **あれば望ましい**：満たしていれば加点しますが、単独では見送りません。 (Preferred if available: it counts in the offer's favor if met, but does not by itself cause a pass.) |

### Settled wording: condition axis

Ask about the 8 axes across 2 questions in one round of AskUserQuestion. Take a qualitative condition that fits none of the axes through Other, and set `axis` to `null`, `operator` to `qualitative`, and `value` to `null`.

| Item | Wording |
|---|---|
| Q1 `header` | 条件の軸（働き方） (Condition axis: work style) |
| Q1 `question` | この条件は、次のどれに当たりますか。当てはまるものが無ければ、第2問を見てからお答えください。 (Which of these does this condition fall under? If none apply, please answer after seeing Q2.) |
| Choices | **リモート確度**：出社の要否や、リモートが制度として保証されているかどうかです。／ **残業時間**：1か月あたりの平均残業時間です。／ **年間休日**：1年あたりの休日日数です。／ **夜間・休日対応**：当番・オンコール・障害対応の有無です。 (Remote-work certainty: whether coming into the office is required, or whether remote work is guaranteed as a matter of policy. / Overtime hours: the average monthly overtime hours. / Annual holidays: the number of holiday days per year. / Night or holiday duty: whether there is on-call or incident-response duty.) |
| Q2 `header` | 条件の軸（仕事の中身） (Condition axis: content of the work) |
| Q2 `question` | 第1問に当てはまらない場合、次のどれに当たりますか。どれにも当たらなければ Other で条件をそのままお書きください。 (If Q1 did not apply, which of these does it fall under? If none apply, use Other and write the condition as it stands.) |
| Choices | **手を動かす業務の比率**：構築・設定・検証・自動化が占める割合です。／ **調整・管理業務の比率**：折衝・進捗管理・要員管理が占める割合です。／ **経験との距離**：いまの経験でどこまで対応できるかです。／ **年収条件**：譲れない年収の下限です。 (Ratio of hands-on work: the share taken up by construction, configuration, verification, and automation. / Ratio of coordination and management work: the share taken up by negotiation, progress management, and staff management. / Closeness to experience: how far the user's current experience can carry them. / Salary condition: the non-negotiable salary floor.) |

### Settled wording: verification method

| Item | Wording |
|---|---|
| `header` | 確認手段 (Means of confirmation) |
| `question` | この条件は、どこで確かめられそうですか。 (Where could this condition likely be confirmed?) |
| Choice 1 | **求人票で分かる**：募集要項の記載だけで判定できます。 (From the job posting: judged from the listing's stated requirements alone.) |
| Choice 2 | **企業研究が要る**：有価証券報告書・決算資料・公式サイトなどを調べて判定します。 (Company research is needed: judged by researching sources such as securities reports, financial results, or the official site.) |
| Choice 3 | **面接で聞くしかない**：公開情報には出ないため、選考の場で確かめます。 (Only confirmable at the job interview: confirmed during the selection process, since it does not appear in public information.) |
| Choice 4 | **確かめようがない**：入社するまで分かりません。 (Not confirmable at all: this will not be known until after joining.) |

Choices 1 through 4 correspond, in order, to `verification` values `posting`, `research`, `interview`, and `unverifiable` (the canonical definition of the value domain is in the hub's `references/axis-format.md`).

### Number of must-have conditions and their priority

Once the combined total of `conditions[level=must]` and `work_character_preferences[desire=must]` reaches 4 or more, insert a dialogue to rank and narrow them down. Ask which 3, in order of what is truly non-negotiable, the user would choose among the must-have conditions. Move anything not chosen into the preferred conditions. Record the ranking, and when to revisit the axes next, in `priority_note`. The rationale for narrowing must-have conditions to a small number, on the premise of later re-evaluation, is in the must/want section of `../axis-methods.md`.

In the detailed pass, assign `priority` to every `level=must` item even when the total is 3 or fewer, since fit assessment uses the ranking.

### Migration from 1.x

When the axis source `{AXIS}` has `schema_version` `1.0` or `1.1`, free-text sentences remain under `must_conditions` / `want_conditions`. **Do not assign them mechanically to an axis.** Guessing a threshold from free text amounts to fabricating a fact. A 1.x `profile.json` is split first (Step 0 of `../../SKILL.md`), so the migration always writes to `axis.json`.

In migration mode, present the existing free-text sentences one at a time, and settle the 4 items above through dialogue for each. Once every item has been migrated, set `must_conditions` / `want_conditions` to empty arrays, then continue to check the `work_character` section and the `score_axes` section. Finally, rewrite the `schema_version` of `axis.json` to `2.0` and `updated_at` to the current date.

When the user does not want to migrate, leave `axis.json` at 1.x. In that case, state once that the 8-axis judgment in job search and the work-character dimension of fit assessment will be unavailable.

## Downstream

Job search (`job-change-job-search`) uses `level=must` conditions as thresholds. Fit assessment (`job-change-fit-assessment`) references `id` through `must_condition_results[].ref`, and orders its judgments by `priority`.
