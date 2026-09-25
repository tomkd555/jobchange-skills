# Canonical specification of job_posting.json (job-posting-format)

This is the canonical specification defining the field specification, entry criteria, and mechanical validation rules for `job_posting.json`, the structured data of an imported job posting. The job posting intake agent (job-change-posting-parser) assembles an object conforming to this specification, and `scripts/validate_job_posting.py` mechanically checks it against this specification.

The output location is `{DATA_ROOT}/companies/{company slug}/job_posting.json`. The calling skill (the job-change-company-research body itself) writes the file, and only after the slug is resolved. The posting-parser agent writes no file; it returns `{company_name, aliases, job_posting}` as JSON in its final message.

## Entry points for intake

A job posting is always built at the start of the per-company pipeline. There are four entry points, distinguished by `source_type`.

| `source_type` | Entry point | How it is taken in | `source_url` |
|---|---|---|---|
| `url` | The URL of the job posting page | Fetch the page and structure it | The URL (required) |
| `text` | The job posting's text | Structure the pasted text | null or omitted |
| `file` | A PDF or image of the job posting | Read the file the user provided and structure it | null or omitted |
| `dialogue` | The company name only | Ask through dialogue for the required items and structure them | null or omitted |

A URL may also be written for reference at any entry point besides `url`. `source_url` is checked only when `source_type` is `url`.

## Overall structure

```json
{
  "schema_version": "1.1",
  "source_type": "url",
  "source_url": "https://recruit.example.co.jp/jobs/1234",
  "fetched_at": "2026-07-17",
  "company_name": "架空クラウドワークス株式会社",
  "title": "バックエンドエンジニア（中途）",
  "employment_type": "正社員",
  "location": { "work_location": "東京都渋谷区", "remote_policy": "週3リモート可" },
  "salary": { "min": 6000000, "max": 9000000, "currency": "JPY", "basis": "年収", "notes": "" },
  "working_hours": { "scheduled_hours": 7.5, "break_minutes": 60, "discretionary": false, "overtime_notes": "" },
  "metrics": {
    "annual_holidays": { "value": 125, "quote": "年間休日125日" },
    "monthly_overtime_h": { "value": 20, "quote": "月平均残業20時間" },
    "paid_leave_rate": { "value": 71.0, "quote": "有給取得率71%" },
    "paid_leave_days_granted": { "value": 20, "quote": "有給付与20日" }
  },
  "scope_of_change": {
    "duties": { "stated": true, "unlimited": false, "quote": "変更の範囲: バックエンド開発およびこれに関連する業務" },
    "work_location": { "stated": true, "unlimited": true, "quote": "変更の範囲: 会社の定める場所" },
    "contract_renewal_cap": null
  },
  "requirements": { "must": [ "" ], "want": [ "" ] },
  "benefits": [ { "name": "書籍購入補助", "quote": "技術書は全額会社負担" } ],
  "selection_process": [ "書類選考", "適性検査", "一次面接", "最終面接" ],
  "open_questions": [ "" ]
}
```

## Field specification

### Required fields

| Field | Type | Entry criteria |
|---|---|---|
| `schema_version` | String | Currently `"1.1"`. `"1.0"` is also accepted as a known version. Anything else is a WARN |
| `source_type` | String | The intake entry point. One of `url` / `text` / `file` / `dialogue` |
| `fetched_at` | String | The fetch date (an actual date in `YYYY-MM-DD` form). When filled through dialogue, the date it was asked |
| `company_name` | String | The company name as the job posting states it |
| `title` | String | The job posting's job type or position name |

`source_url` is required only when `source_type` is `url`, and must be a string starting with `http`. It may be null or omitted at any other entry point.

An ERROR occurs when any field in the table above is missing or empty. In addition, it is an ERROR when `source_type` is none of the four values, when `source_type` is `url` but `source_url` does not start with `http`, or when `fetched_at` is not an actual date in `YYYY-MM-DD` form.

### Optional fields

| Field | Type | Content |
|---|---|---|
| `employment_type` | String | The employment type (正社員, 契約社員, and so on) — these are field values |
| `location` | Object | `work_location` (the place of work), `remote_policy` (the remote-work policy) |
| `salary` | Object | `min`, `max`, `currency`, `basis` (年収/月給 and so on) — field values, `notes` |
| `working_hours` | Object | `scheduled_hours` (scheduled working hours), `break_minutes` (break minutes), `discretionary` (whether discretionary work applies), `overtime_notes` |
| `metrics` | Object | The 4 metrics described below |
| `scope_of_change` | Object | The 3 items described below (schema_version 1.1 and later) |
| `requirements` | Object | `must` (an array of required qualifications), `want` (an array of preferred qualifications) |
| `benefits` | Array | Each element is `{name, quote}`. `name` is non-empty |
| `selection_process` | Array | An array of strings listing the selection stages in order |
| `open_questions` | Array | Items that could not be fetched, and points to confirm |

For an optional field, it is an ERROR when it is present and violates the type in the table above (an array or scalar where an object is expected, an object or scalar where an array is expected, and so on). It is not checked when it is absent.

### metrics (object, optional)

Holds, in machine-readable form, the numeric work-style figures the job posting states explicitly. It has 4 keys, and each value is an object `{value, quote}`, or `null`.

| Key | Content | Unit guideline |
|---|---|---|
| `annual_holidays` | Total annual holidays | Days |
| `monthly_overtime_h` | Average monthly overtime | Hours |
| `paid_leave_rate` | Paid-leave-taking rate | % (following the job posting's own notation) |
| `paid_leave_days_granted` | Expected paid-leave days granted | Days |

Each metric has the following fields.

| Field | Required | Entry criteria |
|---|---|---|
| `value` | Required | A number. A string or a boolean is not allowed |
| `quote` | Required | A quote from the job posting (non-empty). Transcribe the passage that grounds the number, verbatim |

**Rule**: enter `value` and a quote `quote` only when the job posting states them explicitly. Set it to `null` when there is no explicit statement (estimation or invention is prohibited). A missing `metrics` as a whole, and `null` for an individual metric, are both normal and raise neither an ERROR nor a WARN. It is an ERROR when `metrics` is present and is not an object, or when a metric is neither `null` nor `{value, quote}`, or when its `value` is not a number, or when its `quote` is empty.

### scope_of_change (object, optional. schema_version 1.1 and later)

Under the April 1, 2024 revision to the Enforcement Regulations of the Employment Security Act, a job posting must disclose the following three items (Ministry of Health, Labour and Welfare, https://www.mhlw.go.jp/stf/newpage_32105.html ). These give material for estimating the risk of a transfer, a change in duties, or non-renewal, and the downstream fit assessment uses them. It has 3 keys, and each value is an object `{stated, unlimited, quote}`, or `null`.

| Key | The corresponding mandatory-disclosure item |
|---|---|
| `duties` | The scope of change to the duties an employee is to perform |
| `work_location` | The scope of change to the place of work |
| `contract_renewal_cap` | The cap on renewing a fixed-term employment contract (a cap on the total contract period or the number of renewals) |

Each item has the following fields.

| Field | Type | Entry criteria |
|---|---|---|
| `stated` | Boolean | True when the job posting states this item, false when it does not |
| `unlimited` | Boolean | True when it is stated but the scope is not limited. Judgment criteria are described below |
| `quote` | String | A quote from the job posting. Required and non-empty when `stated` is true |

```json
"scope_of_change": {
  "duties": { "stated": true, "unlimited": false, "quote": "変更の範囲: バックエンド開発およびこれに関連する業務" },
  "work_location": { "stated": true, "unlimited": true, "quote": "変更の範囲: 会社の定める場所" },
  "contract_renewal_cap": { "stated": false, "unlimited": false, "quote": "無期雇用のため対象外" }
}
```

**Rule**: write only content you confirmed by reading the job posting. When you cannot find the item itself in the job posting, set that item to `null`. Set `stated` to false only when the job posting touches on the item but you can read that it discloses no scope (for example, a statement that a renewal cap does not apply because employment is unlimited-term). The difference between `null` and `stated: false` is the difference between "the job posting was read but no relevant passage was found" and "the job posting touches on it but does not state a scope."

**Judgment criteria for `unlimited`**: treat it as true when the stated scope is written so that the company can broaden it later at its own discretion.

| Example wording | `unlimited` |
|---|---|
| 「変更の範囲: 会社の定める業務」「会社の定める場所」「会社の指示する業務全般」 | True |
| 「変更の範囲: 会社内のすべての業務」「当社の全事業所（将来設置されるものを含む）」 | True |
| 「変更の範囲: バックエンド開発およびこれに関連する業務」 | False |
| 「変更の範囲: 本社および東京23区内の事業所」「変更なし」 | False |
| 「更新上限: 通算契約期間5年」「更新回数3回まで」 | False |

For wording that is hard to judge (for example, 「原則として現在の勤務地」, where the scope of an exception cannot be read), set `unlimited` to false and write that fact into `open_questions`. Route to `open_questions` only this kind of ambiguous wording. The stated content itself goes into `scope_of_change`, so do not write it into `open_questions` again.

All three items being `null` (including `scope_of_change` itself being absent) is a WARN. A job posting listed since April 2024 carries a disclosure obligation, and not having obtained all three items raises a suspicion that the intake was incomplete.

When `schema_version` is `1.0`, `scope_of_change` is not checked. Version 1.0 has no such field, so this keeps an existing deliverable readable as is. Only 1.0 is excluded from the check; every later version is checked.

## Handling a page that cannot be fetched

When the page cannot be fetched because it requires login, uses client-side rendering, or is a listing that has closed, fill in only what could be fetched. Set a missing item to `null` (for a metric) or omit it, and record in `open_questions` what could not be fetched. Do not fill in a number the job posting does not state, by estimation.

This handling applies regardless of the entry point. When `source_type` is `dialogue` and the user could not answer an item, treat it the same way. Do not fill it in by estimation; write it into `open_questions`.

## Mechanical validation rules (validate_job_posting.py)

`scripts/validate_job_posting.py` performs the mechanical check. Even a single ERROR is a FAIL (exit code 1); zero ERRORs is a PASS (exit code 0, even with WARNs present).

**ERROR (the deliverable does not hold together, or a type is violated)**

- It cannot be parsed as JSON
- The root is not an object
- Any of `schema_version`, `source_type`, `fetched_at`, `company_name`, or `title` is missing or empty
- `source_type` is none of `url` / `text` / `file` / `dialogue`
- `source_type` is `url` but `source_url` does not start with `http`
- `fetched_at` is not an actual date in `YYYY-MM-DD` form
- `metrics` is present and is not an object
- A metric in `metrics` is present (non-null), and is not a `{value, quote}` object, or its `value` is not a number, or its `quote` is empty
- `schema_version` is not `1.0`, and `scope_of_change` is present and is not an object
- `schema_version` is not `1.0`, and an item in `scope_of_change` is present (non-null), and is not an object, or its `stated` is not a boolean, or its `unlimited` is not a boolean, or `stated` is true while `quote` is empty, or `quote` is not a string
- `location`, `salary`, `working_hours`, or `requirements` is present and is not an object
- `selection_process`, `open_questions`, or `benefits` is present and is not an array
- An element of `benefits` is not an object, or its `name` is empty

**WARN (it holds together, but information is insufficient)**

- `schema_version` is not a known version (`1.0` / `1.1`)
- `schema_version` is not `1.0`, and all 3 items of `scope_of_change` are `null` (including `scope_of_change` itself being absent)
