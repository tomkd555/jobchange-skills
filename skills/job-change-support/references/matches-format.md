# matches/{posting id}.json specification (matches-format)

The canonical specification of the match record that pairs one posting check with the user's conditions. The main session writes it in the posting check after the researcher returns, and the decision procedure reads it. `scripts/validate_matches.py` checks a file against this specification.

Location: `{DATA_ROOT}/career-private/matches/{posting id}.json`. The record names the user's conditions, so it is personal information and lives under `career-private/`. An agent with web tools never receives its path or its content.

## Overall structure

```json
{
  "schema_version": "1.0",
  "posting_id": "S_アクメクラウド-20261025-01",
  "checked_at": "2026-10-25",
  "match": [
    {"condition_id": "c001", "result": "meets", "basis_field_id": "salary_min", "note": "下限 650 万円が条件の 600 万円以上"},
    {"condition_id": "c002", "result": "unknown", "basis_field_id": "remote_policy", "note": "求人票にリモートの記載がない"},
    {"condition_id": "c003", "result": "unknown", "basis_field_id": null, "note": "価値観の条件は意思決定の支援で評点する"}
  ],
  "unknowns": ["monthly_overtime_h", "paid_leave_rate", "remote_policy"]
}
```

## Fields

| Field | Required | Rule |
|---|---|---|
| `schema_version` | Required | `"1.0"`. Another value is WARN |
| `posting_id` | Required | The id of the posting check this record belongs to, in the form `{company slug}-{YYYYMMDD}-{NN}`. The file name is `{posting_id}.json` |
| `checked_at` | Required | `YYYY-MM-DD` |
| `match` | Required | One element per active condition in `wishes.json` at the time of the check |
| `unknowns` | Required | The field ids whose value is `null` in every entry of the posting check. An empty array is fine |

### A match element

| Field | Required | Rule |
|---|---|---|
| `condition_id` | Required | A condition id (`c` plus three digits). Unique within `match` |
| `result` | Required | `meets`, `not_meets` or `unknown` (`match_result` in the catalog) |
| `basis_field_id` | Conditional | The posting-check field the result was read from. Required when `result` is `meets` or `not_meets`; `null` allowed when `result` is `unknown` |
| `note` | Required | One sentence giving the value compared and the threshold, in Japanese. Non-empty |

A condition whose `field_id` is `custom` always gets `result: unknown` here; the user rates it in the decision record.

The absence of a statement is never read as `meets` and never as `not_meets`. A field with `value: null` makes the result `unknown`.

## Validation (validate_matches.py)

```
python validate_matches.py <matches.json> --wishes <wishes.json> [--posting-check <posting-check.json>] [--json]
```

Exit code 0 is PASS (WARN alone counts as PASS), 1 is FAIL. `--wishes` is required so that every `condition_id` can be checked against the condition sheet.

ERROR:

- the file does not parse as JSON, or the root is not an object
- a required field is missing or has the wrong type
- `posting_id` is malformed, or (with `--posting-check`) differs from the posting check's `posting_id`
- `checked_at` is not a real date
- a `condition_id` is malformed, duplicated, or absent from `wishes.json`
- `result` is outside its three values
- `result` is `meets` or `not_meets` while `basis_field_id` is `null` or absent from the catalog
- `note` is empty
- an element of `unknowns` is absent from the catalog
- (with `--posting-check`) an element of `unknowns` names a field that has a non-null value in the posting check, or a field with only null values is missing from `unknowns`

WARN:

- `schema_version` is outside the known versions
- an active `must` or `want` condition in `wishes.json` has no element in `match`
- a `condition_id` in `match` points at a condition whose `active` is false
