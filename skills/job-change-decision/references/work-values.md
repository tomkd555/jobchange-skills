# Work values list (work-values)

The twelve work values shown in Part 1 of `job-change-decision`. The ids are the `source` of a condition in `wishes.json`; the Japanese labels are what the user sees. The list is the scale set of Super's Work Values Inventory, revised (WVI-R, Zytowski 2006). The six values of O*NET's Work Importance Profiler are mapped onto it and add no item.

## The twelve values

| id | label | one-line gloss shown in the option description | O*NET value mapped here |
|---|---|---|---|
| `achievement` | 達成感 | 仕事の成果が目に見えて残ること | Achievement |
| `coworkers` | 同僚との関係 | 気の合う同僚と働くこと | Relationships |
| `creativity` | 創造性 | 新しいものを考え、形にすること | |
| `income` | 収入 | 高い報酬を得ること | |
| `independence` | 独立性 | 自分の判断で仕事を進めること | Independence |
| `lifestyle` | 生活との両立 | 仕事以外の時間を確保できること | |
| `intellectual_challenge` | 知的な挑戦 | 難しい問題に取り組むこと | |
| `prestige` | 社会的な評価 | 周囲から認められること | Recognition |
| `security` | 安定 | 雇用と収入が安定していること | |
| `supervision` | 上司との関係 | 公平で支えになる上司のもとで働くこと | Support |
| `variety` | 仕事の多様性 | 変化のある仕事をすること | |
| `workplace` | 職場環境 | 設備や立地など働く場所が快適であること | Working Conditions |

## How the list is shown

One AskUserQuestion with three multi-select questions of four options each, in this order:

| Question | Header | Options |
|---|---|---|
| 1 | 成果と報酬 | 達成感, 収入, 社会的な評価, 安定 |
| 2 | 仕事の中身 | 創造性, 知的な挑戦, 仕事の多様性, 独立性 |
| 3 | 人と環境 | 同僚との関係, 上司との関係, 職場環境, 生活との両立 |

The question text is 「次のうち、転職先で重視するものを選んでください。いくつでも選べます。」 with the gloss as each option's description. A value the user picks becomes a condition with `kind: "value"`, `field_id: "custom"`, `source` the id above, `text` the label, and a `how_to_judge` sentence the skill proposes and the user corrects. Examples of a judging sentence:

| id | proposed `how_to_judge` |
|---|---|
| `achievement` | 業務内容に、成果が数値や納品物として残る仕事が書かれているか |
| `income` | 年収の下限と上限、固定残業代の有無 |
| `lifestyle` | 月平均残業時間、年間休日、リモートの方針 |
| `intellectual_challenge` | 業務内容に新しい技術の導入や設計の判断が含まれるか |
| `security` | 雇用形態、平均勤続年数、自己資本比率 |
| `independence` | 業務内容に裁量や担当範囲の広さが書かれているか |

## Source

Zytowski, D. G. (2006). Super's Work Values Inventory-Revised: Technical manual. Kuder, Inc. O*NET Work Importance Profiler: https://www.onetcenter.org/WIP.html . The mapping follows the research report `research/20261025-jobchange-rebuild/report.md` (evidence E122, E123).
