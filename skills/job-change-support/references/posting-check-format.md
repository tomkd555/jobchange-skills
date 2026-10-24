# posting-check.json specification (posting-check-format)

The canonical specification of `posting-check.json`, the record of one job posting and the public figures of the company behind it. The posting researcher agent (`job-change-posting-researcher`) writes the `job` and `company` sections from the posting and from official sources; the main session adds the しょくばらぼ (shokuba labo) values it reads through Chrome. `scripts/validate_posting_check.py` checks a file against this specification. Field ids, the value shape, enumerations and the common rules come from `references/field-catalog.md`.

Location: `{DATA_ROOT}/companies/{company slug}/postings/{posting id}/posting-check.json`. The posting id is `{company slug}-{YYYYMMDD}-{NN}`: the slug, the fetch date, and a two-digit sequence number within that company and day, so a second posting or a scout mail from the same company gets its own file. The file holds no personal information: the user's conditions, the match against them and the unknowns go to `career-private/matches/{posting id}.json` (`matches-format.md`).

## Overall structure

```json
{
  "schema_version": "1.0",
  "posting_id": "S_アクメクラウド-20261025-01",
  "company_slug": "S_アクメクラウド",
  "source_type": "url",
  "source_url": "https://example.com/careers/123",
  "fetched_at": "2026-10-25",
  "job": {
    "company_name": {"value": "アクメクラウド株式会社", "unit": null, "source_url": "https://example.com/careers/123", "grade": "A", "as_of": "2026-10-25", "quote": "アクメクラウド株式会社"},
    "job_title": {"value": "インフラエンジニア", "unit": null, "source_url": "https://example.com/careers/123", "grade": "A", "as_of": "2026-10-25", "quote": "インフラエンジニア（AWS）"},
    "salary_min": {"value": 6500000, "unit": "円", "source_url": "https://example.com/careers/123", "grade": "A", "as_of": "2026-10-25", "quote": "年収 650 万〜900 万円"},
    "salary_max": {"value": 9000000, "unit": "円", "source_url": "https://example.com/careers/123", "grade": "A", "as_of": "2026-10-25", "quote": "年収 650 万〜900 万円"},
    "monthly_overtime_h": {"value": null, "unit": "時間", "source_url": null, "grade": null, "as_of": null, "quote": null},
    "scope_of_change_duties": {"value": "会社の定める業務", "unit": null, "source_url": "https://example.com/careers/123", "grade": "A", "as_of": "2026-10-25", "quote": "変更の範囲: 会社の定める業務"}
  },
  "company": {
    "legal_entity_name": {"value": "アクメクラウド株式会社", "unit": null, "source_url": "https://disclosure2.edinet-fsa.go.jp/...", "grade": "A", "as_of": "2026-03", "quote": "提出会社の名称"},
    "avg_tenure_years": [
      {"value": 4.2, "unit": "年", "source_url": "https://disclosure2.edinet-fsa.go.jp/...", "grade": "A", "as_of": "2026-03", "quote": "平均勤続年数 4.2 年"},
      {"value": 4.5, "unit": "年", "source_url": "https://shokuba.mhlw.go.jp/...", "grade": "A", "as_of": "2025", "quote": "平均勤続年数 4.5 年"}
    ],
    "labor_violation_listed": {"value": false, "unit": null, "source_url": "https://www.mhlw.go.jp/kinkyu/151106.html", "grade": "A", "as_of": "2026-09-30", "quote": null}
  },
  "open_questions": ["求人票に月平均残業時間の記載がない"]
}
```

## Root fields

| Field | Required | Rule |
|---|---|---|
| `schema_version` | Required | `"1.0"`. Another value is WARN |
| `posting_id` | Required | `{company slug}-{YYYYMMDD}-{NN}`. The slug part must match the slug form in `company-index-format.md`, and the date part must equal `fetched_at` with the hyphens removed |
| `company_slug` | Required | Equal to the slug part of `posting_id` |
| `source_type` | Required | `url` (a posting page), `text` (pasted text), `scout` (a scout mail) or `search` (picked from a job search result) |
| `source_url` | Conditional | Required and starting with `http` when `source_type` is `url` or `search`; `null` allowed otherwise |
| `fetched_at` | Required | `YYYY-MM-DD` |
| `job` | Required | An object keyed by field id. Every key must be a posting field in the catalog |
| `company` | Required | An object keyed by field id. Every key must be a company field in the catalog |
| `open_questions` | Required | An array of strings. An empty array is fine |

## job and company

Each key is a field id from the catalog, and each value is one value object in the catalog's value shape. In `company` a value may instead be an array of value objects when the same field was found in more than one source (the 有価証券報告書 and しょくばらぼ both give average tenure); the entries are kept side by side and never merged. In `job` a value is always one object, because a posting is one source.

A field the source does not state is written with `value: null` and the other keys `null` (`unit` keeps the catalog unit). Writing a key with `null` says the source was read and the item was absent; leaving the key out says the item was never looked for. The researcher writes every key in the "always write" list below, so a `null` there is a finding.

Always write in `job`: `company_name`, `job_title`, `industry`, `employment_type`, `work_location`, `remote_policy`, `salary_min`, `salary_max`, `salary_basis`, `fixed_overtime_included`, `fixed_overtime_hours`, `scheduled_hours`, `annual_holidays`, `monthly_overtime_h`, `paid_leave_rate`, `scope_of_change_duties`, `scope_of_change_location`, `contract_renewal_cap`, `requirements_must`, `requirements_want`, `selection_process`, `posted_at`.

Always write in `company`: `legal_entity_name`, `employee_count`, `avg_age`, `avg_tenure_years`, `avg_annual_salary`, `revenue_growth`, `operating_margin`, `equity_ratio`, `labor_violation_listed`, `labor_violation_date`.

`monthly_overtime_h`, `paid_leave_rate` and `avg_tenure_years` from しょくばらぼ are added by the main session as further entries under `company` (an array), each with the しょくばらぼ page as `source_url`. The `job` entries for the same fields stay as the posting stated them.

Only official sources are used: the posting page itself, the company's own site, EDINET and the company's IR pages, the 厚生労働省 violation list and しょくばらぼ. Every value therefore carries grade `A`. News, certification schemes, review sites and the gender-related disclosure figures are out of scope by the user's instruction.

## Validation (validate_posting_check.py)

```
python validate_posting_check.py <posting-check.json> [--json]
```

Exit code 0 is PASS (WARN alone counts as PASS), 1 is FAIL.

ERROR:

- the file does not parse as JSON, or the root is not an object
- a required root field is missing or has the wrong type
- `posting_id` is malformed, its slug part differs from `company_slug`, or its date part differs from `fetched_at`
- `source_type` is outside its four values; `source_url` is missing or does not start with `http` when the type requires it
- a key in `job` or `company` is absent from the catalog, or sits in the wrong section (a company field under `job`, a posting field under `company`)
- a value in `job` is an array
- a value object lacks one of `value`, `unit`, `source_url`, `grade`, `as_of`
- `value` is not `null` and does not match the catalog type (an integer field holding a string, an enumeration field holding a value outside the enumeration, a date field holding a malformed date, a `string_list` holding a non-string)
- `unit` differs from the catalog unit
- `value` is not `null` while `source_url` does not start with `http`, `grade` is outside `A` to `D`, or `as_of` is malformed
- `open_questions` contains a non-string

WARN:

- `schema_version` is outside the known versions
- a field in the "always write" lists is missing from `job` or `company`
- `scope_of_change_duties`, `scope_of_change_location` or `posted_at` has `value: null` (the posting lacks a legally required item; the main session shows it as 要確認)
- `employment_type` is `contract` or `temporary` while `contract_renewal_cap` has `value: null`
- a value carries a grade other than `A` (the posting check uses official sources only)
