# The canonical definition of screening axes and work characteristics (screening-axes)

This is the canonical definition of the vocabulary used to match a job posting against the user's preferences. The following skills refer to this file.

| Referrer | What it is used for |
|---|---|
| `job-change-axis` / `job-change-support` | The value range of `job_change_axis.conditions[].axis` and `work_character_preferences[].trait` in `{AXIS}` (`axis.json`, or a 1.x/2.0 `profile.json`; resolved by "Location" in `axis-format.md`) |
| `job-change-job-search` | The value range of `axis_observations[]`, `duty_items[]`, and `axis_judgements[]` in `job_search_results.json` |
| `job-change-fit-assessment` | What the `work_character_fit` dimension evaluates |

The vocabulary is defined here alone, and is never duplicated into a referrer.

## Design premise

Facts read from a job posting (observation) are kept separate from the comparison against the user's own conditions (judgement). A role that carries out web search writes the observation; the skill body, which can read the user profile, writes the judgement. Keeping observation and judgement apart lets condition judgement happen without passing personal information to a role that has a means of sending data to the web.

Never fill in what cannot be observed by guessing. An axis with no statement in the posting is marked `stated: false`, and its judgement becomes `unknown`. A posting whose `unknown` values reach the thresholds is classified as `needs_more_research`（追加調査候補）. The thresholds and the order in which they apply are in job-change-job-search's `references/job-search-format.md`. The absence of a statement is never used as evidence that a condition is met, nor as evidence that it is not met.

## The eight screening axes

| Axis id | Name | Observed-value type | Enumeration / unit |
|---|---|---|---|
| `remote_certainty` | Remote-work certainty | enum | `guaranteed` / `full_remote_possible` / `hybrid` / `onsite` |
| `overtime_hours` | Overtime hours | number | monthly average hours |
| `annual_holidays` | Annual holidays | number | days / year |
| `oncall_load` | Night and holiday response | enum | `none_stated` / `exists` |
| `hands_on_ratio` | Hands-on work ratio | number | 0.0-1.0 (derived from `duty_items`) |
| `coordination_ratio` | Coordination and management ratio | number | 0.0-1.0 (derived from `duty_items`) |
| `experience_distance` | Experience distance | enum | `near` / `adjacent` / `far` (decided only at judgement) |
| `salary_condition` | Salary condition | number | salary floor (yen) |

### remote_certainty (remote-work certainty)

| Value | Judgement basis |
|---|---|
| `guaranteed` | Full remote work is stated explicitly as part of the work rules or a personnel policy. Wording such as 「フルリモート制度あり」(a full-remote system is in place) or 「リモートワーク規程」(a remote-work policy) shows that a policy exists |
| `full_remote_possible` | Only wording such as 「フルリモート可」(full remote possible) or 「在宅勤務可」(work from home possible) appears. No backing by a policy can be read |
| `hybrid` | A number of office days or an office-attendance frequency is specified, such as 「週2日出社」(2 office days a week) or 「月数回の出社あり」(a few office days a month) |
| `onsite` | Constant office attendance, or no mention of remote work with a fixed work location |

「リモート可」 (remote work possible) and 「リモートが制度として保証されている」 (remote work guaranteed as a policy) are two different statements. Never judge `guaranteed` from the wording alone. When no statement of a policy can be read, keep the judgement at `full_remote_possible`.

### overtime_hours (overtime hours)

Observe the monthly average overtime hours as a number. 「月平均20時間」(monthly average 20 hours) becomes `20`. When wording such as 「みなし残業30時間分を含む」(includes 30 hours of deemed overtime pay) appears, treat the deemed hours as a ceiling estimate, use `30` as the observed value, and record in `note` that it is deemed overtime.

When only a qualitative expression appears, such as 「残業少なめ」(low overtime) or 「残業ほぼなし」(almost no overtime), set `stated: true` and `value: null`, and transcribe the wording into `value_text`. Never infer a number from a qualitative expression.

### annual_holidays (annual holidays)

Observe the number of annual holiday days as a number. 「年間休日125日」(125 annual holidays) becomes `125`. A statement of only 「完全週休2日制」(a complete five-day work week) leaves the day count unsettled, so set `stated: true` and `value: null`, and transcribe the wording into `value_text`.

### oncall_load (night and holiday response)

| Value | Judgement basis |
|---|---|
| `none_stated` | States explicitly 「夜間対応なし」(no night response) or 「オンコールなし」(no on-call) |
| `exists` | States any of: duty rotation, on-call, shift work, incident response, or 24/7 operation |

When there is no statement, `stated: false`. The absence of a statement is never used as grounds for 「夜間対応なし」 (no night response). A posting for operations, maintenance, or infrastructure work can include night or holiday response even with no statement of it.

### hands_on_ratio / coordination_ratio (work-content ratios)

Transcribe each quoted phrase of job content into `duty_items[]`, one item at a time, and give each one exactly one category. The ratio is calculated from the count of items in each category.

| category | Meaning | Example | Counts toward |
|---|---|---|---|
| `build` | Construction / implementation | 「システムの設計・構築」「アプリケーション開発」 | hands-on |
| `operate` | Configuration / operation | 「サーバーの設定変更」「監視基盤の運用」 | hands-on |
| `verify` | Verification / testing | 「検証環境での動作確認」「テスト計画の実施」 | hands-on |
| `automate` | Automation / tooling | 「運用自動化スクリプトの作成」「CI/CD の整備」 | hands-on |
| `coordinate` | Internal coordination / negotiation | 「関係部署との調整」「ベンダーコントロール」 | coordination / management |
| `manage` | Management / progress / staffing | 「プロジェクトの進捗管理」「メンバーの育成」 | coordination / management |
| `customer_facing` | Customer interaction / proposals | 「顧客への提案」「要件のヒアリング」 | coordination / management |
| `other` | None of the above | 「その他付随業務」 | counted only in the denominator |

```
hands_on_ratio     = (build + operate + verify + automate) / duty_items の全件数
coordination_ratio = (coordinate + manage + customer_facing) / duty_items の全件数
```

When `duty_items` has fewer than 3 entries, the denominator is too small and the ratio swings by chance. In this case, set both axes to `stated: false` and `value: null`.

The following shows boundary examples for classification.

| Quoted phrase | Category | Reason |
|---|---|---|
| 「要件定義から設計・構築まで一貫して担当」 | `build` | The hands-on process is the primary content |
| 「要件定義および関係部署との合意形成」 | `coordinate` | Building agreement is the primary content |
| 「インフラ構築の外部委託先管理」 | `manage` | Management is the primary content; the outside vendor carries out the construction |
| 「障害発生時の一次対応」 | `operate` | A hands-on response (whether it happens at night is judged separately, under `oncall_load`) |
| 「技術選定と PoC の実施」 | `verify` | A PoC is verification |
| 「セキュリティポリシーの策定」 | `coordinate` | Drafting a policy involves reaching agreement among stakeholders |
| 「チームリードとして5名を統括」 | `manage` | Leading the team is the primary content |

When one quoted phrase contains both construction and coordination, decide by which one the sentence's subject and predicate treat as primary. When in doubt, never fall back to `other`: decide by the primary predicate, and keep the quoted phrase in `duty_items`. As long as the quoted phrase remains, a person can revisit the judgement later.

### experience_distance (experience distance)

This axis alone never has its value decided at the observation layer. A job posting shows the requirement. The distance is settled only once it is compared against the user's own career history.

The observation layer holds `required_experience[]` (an array of quoted phrases stating the must-have requirements) and `job_family` (a broad job-type category, such as 「インフラエンジニア」(infrastructure engineer) or 「バックエンドエンジニア」(backend engineer)). `value` is fixed at `null`.

The judgement layer decides the distance by the following standard.

| Value | Judgement basis |
|---|---|
| `near` | The must-have requirements are met by current hands-on experience. The broad job-type category matches the current job or is adjacent to it |
| `adjacent` | Some of the must-have requirements are met. The shortfall can be covered by experience in an adjacent technology |
| `far` | Most of the must-have requirements are not met. The broad job-type category differs from the current job |

**Experience distance is separate from alignment with the user's own aspiration.** Closeness of experience is never used as evidence that the user wants that job. Evaluating aspiration belongs to the `aspiration_alignment` dimension of `job-change-fit-assessment`.

### salary_condition (salary condition)

Observe the floor of the stated annual salary as a number in yen. 「年収600万〜900万円」(annual salary 6 million to 9 million yen) becomes `6000000`.

「応相談」(negotiable) or 「経験・能力を考慮のうえ決定」(decided based on experience and ability) is set to `stated: true` and `value: null`. Set `stated: true` and `value: null` as well when only a monthly salary is stated, the existence of a bonus cannot be read, and the figure cannot be converted to an annual salary. Never convert to an annual salary by estimation.

Never decide `value` from a statement of a 「モデル年収」(model annual salary) alone, such as 「入社3年目のモデル年収600万円」(a model annual salary of 6 million yen in the third year of employment). It is an example for a different length of service. A 「想定年収」(expected annual salary) may be treated as the offered figure; when the floor is left open with a dash, read the floor alone. When the stated figure includes a fixed overtime allowance, record that fact in `value_text`, and write the hour count into the observation for the `overtime_hours` axis.

## The eight work characteristics

This is the vocabulary that expresses how the user wants to work. In `{AXIS}`, `work_character_preferences[]` gives each one a desire level.

| Trait id | Meaning | Observable from a job posting | Corresponding axis |
|---|---|---|---|
| `hands_on` | Able to do hands-on work | yes | `hands_on_ratio` |
| `build_ops_ratio` | A high ratio of construction, configuration, verification, and automation | yes | `hands_on_ratio` |
| `low_coordination` | Little customer negotiation, internal coordination, or management work | yes | `coordination_ratio` |
| `full_remote_guaranteed` | Full remote work is guaranteed as a policy | partial | `remote_certainty` |
| `no_oncall` | In principle, no night or holiday response | partial | `oncall_load` |
| `clear_completion` | Completion conditions are clear | no | none |
| `solo_completable` | Able to decide the work's procedure and approach and see it through | no | none |
| `short_feedback` | Results can be confirmed within a short period | no | none |

### Handling the three unobservable traits

`clear_completion`, `solo_completable`, and `short_feedback` cannot be judged from the wording of a job posting. They differ by organisation even under the same job title, and a job posting essentially never states them.

These traits never affect the classification judgement in a job search. Never mark "met" or "not met" by guessing. They are handled as follows.

- In a job search, these traits have no corresponding axis, so they play no part in classification.
- In fit assessment, the `verdict` of the `work_character_fit` dimension states 「求人票・企業研究からは判定できない」 (cannot be judged from the job posting or company research). It is also listed in `overall.open_questions` as an item to confirm at the job interview.
- In interview preparation, it is treated as material for a question the candidate asks the interviewer (such as 「このポジションで、着任後3か月の成果として何が期待されるか」 (what results are expected from this position within three months of joining)).

### Desire level (desire)

| Value | Meaning | Effect on judgement |
|---|---|---|
| `must` | Rules out the posting if not met | Treated as a must-have condition. A posting that fails to meet it becomes a candidate for exclusion |
| `important` | Given weight | Affects the evaluation, but never excludes a posting by itself |
| `neutral` | No preference either way | Not used in judgement |
| `not_required` | Not needed | Not used in judgement |

Give a desire level to all 8 traits. This distinguishes "left blank" from "no preference either way." Leaving one blank leaves room for a downstream sub-skill to fill it in by guessing.

## The academic basis for the work characteristics

The three traits that cannot be observed from a job posting correspond to dimensions of the job characteristics model. This mapping lets the three traits be treated as constructs with a demonstrated link to job satisfaction and motivation.

Humphrey and colleagues (2007) integrated 259 studies and 219,625 people. They showed that 14 job characteristics explain an average of 43% of the variance in 19 worker attitudes and behaviours, and that motivational characteristics explain 34% of the variance in job satisfaction. The validation of the job characteristics model itself is in Fried and Ferris (1987). Morgeson and Humphrey (2006) presented a framework that decomposes autonomy into three parts: work scheduling, decision-making, and work methods.

| Trait id | Corresponding job characteristic | What the mapping states |
|---|---|---|
| `clear_completion` | Task identity | The work is carried out as one whole piece from start to finish, and its completed state can be identified |
| `solo_completable` | Autonomy, in its work-methods form | The person can choose the work's procedure and approach, and carry it through to completion without waiting on another person's decision |
| `short_feedback` | Feedback | The work itself lets the good or bad of the result be known at short intervals |

The scale's item wording is not reproduced here. What is shown here is only the mapping between the traits and the job-characteristic dimensions. Having the user answer the scale itself falls outside the purpose of this vocabulary.

<!-- textlint-disable jtf-style/2.1.2.漢字 -->
<!-- This is where author names are shown exactly as in the original. Non-standard kanji in personal names are permitted only here. -->

### Confirmation in Japanese samples

Komagata and colleagues (2021) validated the Japanese-language version of the job characteristics scale on 240 nursing staff at an acute-care hospital. Every subscale's reliability coefficient was 0.7 or above, and the correlation with job satisfaction ranged from 0.23 to 0.53. Ishibashi (2016) worked with 832 Japanese respondents and reported that job design with task significance, feedback, and autonomy raises job satisfaction. It also showed that the direct effect on organisational citizenship behaviour is stronger than the indirect effect mediated through job satisfaction. Arimoto and Kumagai (2021), working with 258 operating-room nurses, showed that higher control over one's work is tied to better mental health.

### Limits of the mapping

The effect of a job characteristic can depend on the workplace context. Masaki and Muramoto (2018) showed, across two studies, that task interdependence raises affective commitment only where gender diversity in the workplace is relatively low. Meeting a work-characteristic preference does not always lead to a good outcome. Matching a preference is one piece of judgement material, and is never treated by itself as a conclusion of good or bad.

The validation of the Japanese-language scale covered 240 nursing staff at one facility, so the representativeness across job types is limited. Its exploratory factor analysis also extracted 4 factors, where the original version has 5 (skill variety, task significance, task identity, autonomy, and feedback). The mapping above cannot assume that the original factor structure holds, as it stands, in Japanese workplaces.

### Sources

- Humphrey and colleagues (2007), DOI:10.1037/0021-9010.92.5.1332
- Fried and Ferris (1987), DOI:10.1111/j.1744-6570.1987.tb00605.x
- Morgeson and Humphrey (2006), DOI:10.1037/0021-9010.91.6.1321
- Komagata and colleagues (2021), DOI:10.19012/janap.25.1_12
- Ishibashi (2016), DOI:10.11221/jima.66.309
- Arimoto and Kumagai (2021), DOI:10.3861/kenko.87.5_229
- Masaki and Muramoto (2018), DOI:10.5651/jaas.30.133

<!-- textlint-enable jtf-style/2.1.2.漢字 -->

## Correspondence between axes and conditions

In `{AXIS}`, `job_change_axis.conditions[]` takes, for `axis`, either one of these 8 axes or `null`. `null` represents "a qualitative condition that fits none of the 8 axes" (such as 「モダンな技術スタックが整備されていること」: "a modern technology stack is in place").

A condition whose `axis` is `null` cannot be judged mechanically from a job posting. Set `operator` to `qualitative`, and set `verification` to `research` (confirmed through company research) or `interview` (confirmed at the job interview). This kind of condition is never used in job-search classification; it is passed on to fit assessment and to confirmation at the job interview.

Only a condition that has an `axis` is used in the 8-axis judgement and threshold comparison of a job search.
