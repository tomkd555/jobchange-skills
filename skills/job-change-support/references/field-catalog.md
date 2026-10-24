# Field catalog (field-catalog)

The canonical list of the fields that `wishes.json`, `posting-check.json`, `matches/{posting id}.json` and the decision records share. Every `field_id` written in any of the four files must appear in the tables below. `scripts/field_catalog.py` reads this file at run time, so the tables are the only copy; the validators of all four files import that module.

The common value shape, the common rules and the enumerations also live here. Each file's own structure is in its format reference (`wishes-format.md`, `job-change-posting-check/references/posting-check-format.md`, `job-change-posting-check/references/matches-format.md`, `job-change-decision/references/decision-format.md`).

## Fields

The columns are the field id, the Japanese label shown to the user, the type, the unit, the direction and the sources that supply the value. The direction is `higher` when a larger value is better, `lower` when a smaller value is better and `none` when the field has no direction. A `type` of `enum:<name>` refers to the enumeration tables below.

### Job posting fields (source `posting`)

| field_id | label | type | unit | direction | sources |
|---|---|---|---|---|---|
| `company_name` | 会社名 | string | | none | posting |
| `job_title` | 職種名 | string | | none | posting |
| `industry` | 業界 | string | | none | posting, user |
| `employment_type` | 雇用形態 | enum:employment_type | | none | posting |
| `work_location` | 勤務地 | string | | none | posting |
| `remote_policy` | リモートの方針 | enum:remote_policy | | none | posting |
| `remote_days_per_week` | 週のリモート日数 | integer | 日 | higher | posting |
| `salary_min` | 年収の下限 | integer | 円 | higher | posting, user |
| `salary_max` | 年収の上限 | integer | 円 | higher | posting |
| `salary_basis` | 給与の基準 | enum:salary_basis | | none | posting |
| `fixed_overtime_included` | 固定残業代の有無 | boolean | | none | posting |
| `fixed_overtime_hours` | 固定残業代の時間数 | number | 時間 | lower | posting |
| `scheduled_hours` | 所定労働時間 | number | 時間 | lower | posting |
| `annual_holidays` | 年間休日 | integer | 日 | higher | posting |
| `monthly_overtime_h` | 月平均残業時間 | number | 時間 | lower | posting, shokuba_labo |
| `paid_leave_rate` | 有給休暇の取得率 | number | % | higher | posting, shokuba_labo |
| `scope_of_change_duties` | 業務の変更の範囲 | string | | none | posting |
| `scope_of_change_location` | 勤務地の変更の範囲 | string | | none | posting |
| `contract_renewal_cap` | 有期契約の更新上限 | string | | none | posting |
| `requirements_must` | 必須要件 | string_list | | none | posting |
| `requirements_want` | 歓迎要件 | string_list | | none | posting |
| `selection_process` | 選考の流れ | string_list | | none | posting |
| `posted_at` | 掲載日 | date | | none | posting |

### Company fields (sources `yuho` = 有価証券報告書, `mhlw` = 厚生労働省, `shokuba_labo` = しょくばらぼ)

| field_id | label | type | unit | direction | sources |
|---|---|---|---|---|---|
| `legal_entity_name` | 法人名 | string | | none | yuho |
| `employee_count` | 従業員数 | integer | 人 | none | yuho |
| `avg_age` | 平均年齢 | number | 歳 | none | yuho |
| `avg_tenure_years` | 平均勤続年数 | number | 年 | higher | yuho, shokuba_labo |
| `avg_annual_salary` | 平均年間給与 | integer | 円 | higher | yuho |
| `revenue_growth` | 売上高成長率 | number | % | higher | yuho |
| `operating_margin` | 営業利益率 | number | % | higher | yuho |
| `equity_ratio` | 自己資本比率 | number | % | higher | yuho |
| `labor_violation_listed` | 労働基準関係法令違反の公表 | boolean | | none | mhlw |
| `labor_violation_date` | 公表日 | date | | none | mhlw |

### User fields (source `user`)

| field_id | label | type | unit | direction | sources |
|---|---|---|---|---|---|
| `custom` | 利用者が書いた条件 | string | | none | user |

`custom` is the field id of a condition the user wrote in their own words, including every work value chosen from `job-change-decision/references/work-values.md`. Such a condition has no posting field to compare against; `how_to_judge` in `wishes.json` says what to look at, and the user rates each candidate 1 to 5 in the decision record.

## Value shape

A measured value is written in the same shape in every file.

```json
{"value": 25, "unit": "時間", "source_url": "https://example.com/ir/yuho.pdf", "grade": "A", "as_of": "2026-03", "quote": "月平均所定外労働時間 25.0 時間"}
```

| Key | Required | Rule |
|---|---|---|
| `value` | Required | A value of the field's type, or `null` when the source does not state it. A string value never carries a unit |
| `unit` | Required | The unit from the tables above (`null` for a field without a unit). A mismatch is ERROR |
| `source_url` | Required | The page the value was read from. Must start with `http` when `value` is not `null` and the source is a web page; `null` when `value` is `null` or the source is the user |
| `grade` | Required | The evidence grade (see `grade` below). Required when `value` is not `null` |
| `as_of` | Required | The point in time of the value: `YYYY`, `YYYY-MM` or `YYYY-MM-DD`. Required when `value` is not `null` |
| `quote` | Optional | The passage of the source that states the value, verbatim |

## Common rules

- A date is `YYYY-MM-DD`. A point in time is `YYYY`, `YYYY-MM` or `YYYY-MM-DD`.
- Money is written as an integer in yen per year. A percentage runs from 0 to 100. Hours are written in hours.
- Enumeration values are English `snake_case`; the Japanese labels live in the tables below and nowhere else.
- Identifiers are stable. A company slug follows `company-index-format.md`. A posting id is `{company slug}-{YYYYMMDD}-{NN}` (the fetch date and a two-digit sequence number within that company and day). A condition id is `c` plus three digits, from `c001`. A decision id is `{YYYYMMDD}-{subject slug}` (lowercase letters, digits and hyphens).
- Every file carries `schema_version`. A reader accepts the current version and the one before it.
- A cross-file reference (`condition_id`, `posting_id`, `field_id`, a decision id in `used_in`) must point at an existing record. The validators check it when the referenced file is passed on the command line.

## Enumerations

### employment_type

| value | label |
|---|---|
| `full_time` | 正社員 |
| `contract` | 契約社員 |
| `temporary` | 派遣社員 |
| `part_time` | パート・アルバイト |
| `outsourcing` | 業務委託 |
| `other` | その他 |

### remote_policy

| value | label |
|---|---|
| `full_remote` | フルリモート |
| `hybrid` | 一部リモート |
| `onsite` | 出社 |

### salary_basis

| value | label |
|---|---|
| `annual` | 年収 |
| `monthly` | 月給 |

### grade

| value | label |
|---|---|
| `A` | 公式（有価証券報告書、厚生労働省、求人票、企業の公式サイト） |
| `B` | 報道・信頼できる二次資料 |
| `C` | 口コミ・集計サイト |
| `D` | 個人ブログ・伝聞 |

The grade is decided by who published the information, as `evidence-grading.md` defines. The posting check uses grade A sources only; B to D stay in the table so an older or a hand-written value can be labelled.

### direction

| value | label |
|---|---|
| `higher` | 大きいほど良い |
| `lower` | 小さいほど良い |
| `none` | 向きなし |

### level

| value | label |
|---|---|
| `must` | 必須 |
| `want` | 希望 |

### condition_kind

| value | label |
|---|---|
| `role` | 職種 |
| `industry` | 業界 |
| `salary_min` | 年収の下限 |
| `location` | 勤務地 |
| `remote` | リモート |
| `employment_type` | 雇用形態 |
| `value` | 価値観 |
| `other` | その他 |

### operator

| value | label |
|---|---|
| `>=` | 以上 |
| `<=` | 以下 |
| `==` | 一致 |
| `in` | いずれかに一致 |

### match_result

| value | label |
|---|---|
| `meets` | 満たす |
| `not_meets` | 満たさない |
| `unknown` | 不明 |

### legal_check_result

| value | label |
|---|---|
| `stated` | 記載あり |
| `missing` | 記載なし（要確認） |
| `not_applicable` | 対象外 |

### weight_method

| value | label |
|---|---|
| `swing` | スイング法の重み |
| `roc` | 順位重心法の重み |
| `equal` | 等重み |
| `want_count` | 希望条件を満たす数 |

### follow_up_at

| value | label |
|---|---|
| `3m` | 入社 3 か月後 |
| `1y` | 入社 1 年後 |
