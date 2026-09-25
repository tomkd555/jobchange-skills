# Section: Company scoring axes (score_axes)

Decides the axes and weights used to score a company from 0 to 100 points, and places them into `company_score_axes[]`. The first pass skips this section; it is done as a section update right before fit assessment. When the first pass skips it, leave the `company_score_axes` field unwritten entirely (do not set it to an empty array). The 9 quantitative candidate axes, the conversion into points, and the rules for allocating weight live in `job-change-company-research`'s `references/company-score-rubric.md`. The field specification lives in the hub's `references/profile-format.md`. The section catalogue and the definition of reach stages live in `../sections.md`.

## Fields to fill

| Field | Format |
|---|---|
| `company_score_axes[].axis`, `kind` | Multiple choice (9 quantitative candidate axes) plus free text (qualitative axes) |
| `company_score_axes[].label`, `definition`, `judgment[]` | Free text (qualitative axes only) |
| `company_score_axes[].weight`, `thresholds` | Multiple choice (allocation proposal, choice of standard) plus free text (numbers) plus multiple choice (cross-check by comparing two companies) |
| `company_score_axes[].note` | Free text |

## Reach stages

| Stage | Condition |
|---|---|
| `skeleton` | `company_score_axes` has at least one item |
| `deep` | Same as skeleton |

## Procedure

Decide in the following order.

1. Present the 9 quantitative candidate axes (compensation level, total annual holidays, average monthly overtime hours, paid-leave usage rate, turnover rate, men's rate of taking childcare leave, revenue growth rate, operating margin, and equity ratio), and have the user select the ones that matter to them. Split this into 3 questions in one round of AskUserQuestion, with each question taking 3 axes as `multiSelect: true` (a single question cannot hold all 9 axes, since it allows at most 4 choices). Treat compensation level (`compensation_level`) as selected by default, and confirm only whether to exclude it.
2. For a qualitative matter the user wants weighted anyway, build it as a qualitative axis. Decide, together with the user, its label (a name), its definition (what counts as meeting it), and its judgment criteria (what can be confirmed for what score, at roughly 3 levels). When judgment criteria cannot be pinned down, leave the matter out of the score and state immediately that it goes to the job interview for confirmation instead.
3. Ask, in one round of AskUserQuestion, for the weight allocation across the chosen axes (summing to 100) together with the standard to use for quantitative axes. The first question is the weight allocation: present allocation proposals as choices scaled to the number of chosen axes, and fall back to free text when none fit. The second question is whether to use the default standard, based on published statistics, or the user's own standard. Do not keep an axis whose weight comes to 0, and drop any axis that will not be scored.
4. For an axis where the user chose their own standard, ask, in free text, for the level that scores 100 points (`full`) and the level that scores 0 points (`zero`), and place them into `thresholds`. This is a numeric elicitation; AskUserQuestion is not used. Compensation level (`compensation_level`) has no default standard, so it must always be asked. The default approach places the current annual salary at `zero` and the desired annual salary (or a level above it) at `full`; follow a different placement if the user prefers one.
5. Score two hypothetical companies using the allocated weights, and check whether the higher-scoring one matches the answer to "which would you actually choose." Frame the comparison around company profiles, avoiding an abstract comparison of axis names (for example: 「A社は年収が現職より120万円高いが残業が月30時間、B社は年収が現職と同水準で残業が月5時間。どちらを選ぶか」, Company A pays 1.2 million yen more per year than your current job but averages 30 hours of overtime a month; Company B pays about the same as your current job but averages 5 hours of overtime a month. Which would you choose?).

When the cross-check disagrees with the allocation, either revise the allocation or record both the allocation and the actual choice and present them to the user. The skill does not decide, on its own, which one reflects the true judgment. When the user selects no axis at all, state immediately that no company score will be produced.

| Item to settle | Question |
|---|---|
| `axis`, `kind` | Among the 9 quantitative candidate axes, which matter when choosing a company (fixed wording below; compensation level is treated as selected by default)? |
| `label`, `definition`, `judgment` | (For a qualitative matter that matters to the user) What should it be called? What counts as meeting it? What can be confirmed for 100 points, and what for 0 points (roughly 3 levels)? |
| `weight`, `thresholds` | (Asked as 2 questions in one round of AskUserQuestion) How should the total of 100 be allocated across the chosen axes? Use the default standard based on published statistics, or the user's own standard? |
| Value of `thresholds` | (For an axis using the user's own standard only, in free text) Where is the level that scores 100 points, and where is the level that scores 0 points? |
| Cross-check | Under this allocated weighting, this side scores higher — but which would the user actually choose? |

### Fixed wording — the 9 quantitative candidate axes

Ask across 3 questions in one round of AskUserQuestion. The weight-allocation proposals change with the number of axes chosen, so no fixed wording is given for them; write them at that point in the conversation.

| Item | Wording |
|---|---|
| Q1 `header` | 処遇と休み (Compensation and time off) |
| Q1 `question` | 企業を採点するとき、次のうち重視するものを選んでください。 (When scoring a company, select the ones that matter to you.) |
| `multiSelect` | true |
| Choices | **処遇水準** — 年収の水準です（既定で選択済み。外す場合はここで外してください）。／ **年間休日総数** — 1年あたりの休日日数です。／ **月平均の残業時間** — 従業員1人あたりの、ひと月あたり平均の残業時間です。 (Compensation level — the level of annual salary, selected by default; deselect it here if you want it excluded. / Total annual holidays — the number of holiday days per year. / Average monthly overtime hours — the average overtime hours per employee per month.) |
| Q2 `header` | 働きやすさ (Ease of working) |
| Q2 `question` | 同じく、次のうち重視するものを選んでください。 (Likewise, select the ones that matter to you.) |
| `multiSelect` | true |
| Choices | **有給休暇の取得率** — 付与日数に対する取得日数の割合です。／ **離職率** — 1年あたりに辞めた人の割合です。／ **男性の育児休業取得率** — 男性従業員の育児休業の取得割合です。 (Paid-leave usage rate — the share of granted leave days actually taken. / Turnover rate — the share of employees who leave per year. / Men's rate of taking childcare leave — the share of male employees who take childcare leave.) |
| Q3 `header` | 経営の状態 (State of management) |
| Q3 `question` | 同じく、次のうち重視するものを選んでください。 (Likewise, select the ones that matter to you.) |
| `multiSelect` | true |
| Choices | **売上高の成長率** — 前年度からの売上の伸びです。／ **営業利益率** — 売上高に対する営業利益の割合です。／ **自己資本比率** — 総資産に占める自己資本の割合です。 (Revenue growth rate — the growth in revenue over the previous year. / Operating margin — operating profit as a share of revenue. / Equity ratio — equity as a share of total assets.) |

### Fixed wording — scoring standard

| Item | Wording |
|---|---|
| `header` | 採点の基準 (Scoring standard) |
| `question` | 定量軸を点数へ直すとき、どちらの基準を使いますか。 (When converting a quantitative axis into points, which standard should be used?) |
| Choice 1 | **統計に基づく既定の基準** — 公表統計をもとに決めた水準で採点します。 (Default standard based on published statistics — scores using a level decided from published statistics.) |
| Choice 2 | **自分の基準** — 100点と0点に当たる水準をご自身で決めます。処遇水準は既定の基準を持たないため、どちらを選んでも伺います。 (Your own standard — you decide, yourself, the levels that count as 100 points and 0 points. Compensation level has no default standard, so it is always asked regardless of which choice is made.) |

### Mismatch between scoring axes and must-have conditions

The chosen scoring axes and weights can disagree with the strength of preference set in `conditions[level=must]` or `work_character_preferences`. Example: a cap on overtime is set as a must-have condition, yet `monthly_overtime` was not chosen as an axis. Or the largest weight was placed on `compensation_level`, yet the salary condition is still set to `want`.

The interviewer does not decide which one reflects the true judgment. Present the mismatched combination to the user as it stands, and let the user choose how to handle it (revise the axis or weight, revise the must-have condition, or leave both as they are). Record, in the elicitation notes, both the mismatch presented and the handling the user chose.

## Downstream

`calculate_company_score.py` in fit assessment (`job-change-fit-assessment`) scores using this section. To company research (`job-change-company-research`), the hub passes only an array of identifiers for the axes whose `kind` is `quantitative` (`weight`, `thresholds`, and qualitative axes are never passed; the canonical definition lives in the hub's `references/pii-boundary.md`).
