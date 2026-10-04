# Section: Work-character preferences (work_character)

Records how strongly the user prefers each of 8 work characteristics. The schema requires this section, and the first pass fills it through two rounds of multiple choice. The definitions of the characteristics are in the hub's `references/screening-axes.md`. The section catalogue and the definition of reach stages are in `../sections.md`.

## Fields to fill

| Field | First pass | Format |
|---|---|---|
| `job_change_axis.work_character_preferences[]` (8 items) | First pass | Multiple choice |
| `job_change_axis.work_character_preferences[].statement` | First pass (only when `desire=must`) | Free text |

## Reach stages

| Stage | Condition |
|---|---|
| `skeleton` | All 8 traits are present, no more and no fewer |
| `deep` | Same as skeleton |

## Procedure

For each of the 8 work characteristics, confirm the strength of preference (`must` / `important` / `neutral` / `not_required`). Two rounds of AskUserQuestion (4 characteristics per round) fill the section.

Make the user choose 「どちらでもよい」 or 「不要である」 explicitly as well, to distinguish between something left unanswered and actual indifference. For any characteristic where the user chooses `desire=must`, ask for a one-sentence condition statement (`statement`) in the user's own words.

The three characteristics `clear_completion`, `solo_completable`, and `short_feedback` cannot be judged from a job posting. When the user chooses `must` or `important` for one of these, state immediately that it becomes a matter to confirm at the job interview.

A characteristic with `desire=must` is treated as a must-have condition, on the same footing as `conditions[level=must]`. Do not register the same condition twice, once here and once in the `conditions` section. When the total number of must-have conditions reaches 4 or more, the narrowing described in "Number of must-have conditions and their priority" in `conditions.md` applies.

### Settled wording: preference strength for the 8 work characteristics

Ask about the 8 characteristics, 4 per question, in two rounds of AskUserQuestion. The 4 choices are the same across every question.

| Choice | Wording |
|---|---|
| Choice 1 | **必須**：満たさないなら見送ります。 (Must-have: I will pass on an offer that does not meet this.) |
| Choice 2 | **重視する**：評価に影響しますが、単独では見送りません。 (Important: it affects the evaluation, but does not by itself cause a pass.) |
| Choice 3 | **どちらでもよい**：判定に使いません。 (Either is fine: not used in the judgment.) |
| Choice 4 | **不要である**：判定に使いません。 (Not required: not used in the judgment.) |

| Round | `header` | `question` | `trait` |
|---|---|---|---|
| Round 1, Q1 | 手を動かせるか (Hands-on work) | 自分で手を動かせることは、次の職場でどれくらい大事ですか。 (How important is it to you that you personally do hands-on work at your next job?) | `hands_on` |
| Round 1, Q2 | 構築の比率 (Ratio of building work) | 構築・設定・検証・自動化が業務の中心であることは、どれくらい大事ですか。 (How important is it that construction, configuration, verification, and automation form the core of the work?) | `build_ops_ratio` |
| Round 1, Q3 | 調整の少なさ (Low coordination load) | 顧客折衝・社内調整・管理業務が少ないことは、どれくらい大事ですか。 (How important is it that client negotiation, internal coordination, and management duties are minimal?) | `low_coordination` |
| Round 1, Q4 | リモートの保証 (Guaranteed remote work) | フルリモートが制度として保証されていることは、どれくらい大事ですか。 (How important is it that full remote work is guaranteed as a matter of policy?) | `full_remote_guaranteed` |
| Round 2, Q1 | 夜間対応の無さ (No night duty) | 夜間・休日の対応が原則ないことは、どれくらい大事ですか。 (How important is it that there is, in principle, no night or holiday duty?) | `no_oncall` |
| Round 2, Q2 | 完了条件の明確さ (Clear completion criteria) | 何をもって終わりとするかが明確であることは、どれくらい大事ですか。 (How important is it that what counts as "done" is clearly defined?) | `clear_completion` |
| Round 2, Q3 | 自分で完結できるか (Solo completability) | 手順や進め方を自分で決めて完結させられることは、どれくらい大事ですか。 (How important is it that you can decide the procedure and approach yourself and carry the work through to completion?) | `solo_completable` |
| Round 2, Q4 | 結果の見えやすさ (Visibility of results) | 結果が短期間で確認できることは、どれくらい大事ですか。 (How important is it that results can be confirmed within a short period?) | `short_feedback` |

## Downstream

The 8-axis judgment in job search (`job-change-job-search`) and the work-character dimension of fit assessment (`job-change-fit-assessment`) read this section. When this section disagrees with `personality.markers` from self-analysis (`job-change-self-analysis`), that skill's Step 6 has the user choose between them, and the choice is reflected here through a section update.
