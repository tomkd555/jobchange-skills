# wishes.json specification (wishes-format)

The canonical specification of `wishes.json`, the user's condition sheet. `job-change-job-search` creates it from the user's one-line wish, `job-change-decision` adds work values to it, and both read it. `scripts/validate_wishes.py` checks a file against this specification. Field ids, enumerations and the common rules come from `field-catalog.md`.

Location: `{DATA_ROOT}/career-private/wishes.json`. The file holds the user's own conditions, so it stays inside the personal-information boundary (`pii-boundary.md`). An agent with web tools never receives its path or its content; the job search passes an anonymised copy of the active conditions (id, kind, text, level) instead.

The file never records the name of the user's current employer or the current salary. Neither is asked for.

## Overall structure

```json
{
  "schema_version": "1.0",
  "updated": "2026-10-25",
  "conditions": [
    {
      "id": "c001",
      "kind": "salary_min",
      "field_id": "salary_min",
      "operator": ">=",
      "text": "年収 600 万円以上",
      "value": 6000000,
      "unit": "円",
      "level": "must",
      "source": "user",
      "how_to_judge": null,
      "created": "2026-10-25",
      "updated": "2026-10-25",
      "active": true
    },
    {
      "id": "c002",
      "kind": "remote",
      "field_id": "remote_policy",
      "operator": "in",
      "text": "リモート中心",
      "value": ["full_remote", "hybrid"],
      "unit": null,
      "level": "must",
      "source": "user",
      "how_to_judge": null,
      "created": "2026-10-25",
      "updated": "2026-10-25",
      "active": true
    },
    {
      "id": "c003",
      "kind": "value",
      "field_id": "custom",
      "operator": null,
      "text": "知的な挑戦",
      "value": null,
      "unit": null,
      "level": "want",
      "source": "intellectual_challenge",
      "how_to_judge": "業務内容に新しい技術の導入や設計の判断が含まれるか",
      "created": "2026-11-01",
      "updated": "2026-11-01",
      "active": true
    }
  ],
  "history": [
    {"date": "2026-11-01", "condition_id": "c001", "field": "value", "before": 5500000, "after": 6000000, "reason": "提示された求人の下限がそろって 600 万円を超えていた"}
  ],
  "used_in": ["20261115-infra-2sha"]
}
```

## Root fields

| Field | Required | Rule |
|---|---|---|
| `schema_version` | Required | `"1.0"`. Another value is WARN |
| `updated` | Required | The date of the last change, `YYYY-MM-DD` |
| `conditions` | Required | The array of conditions. An empty array is WARN |
| `history` | Required | The array of changes. An empty array is fine |
| `used_in` | Required | The array of decision ids (`{YYYYMMDD}-{subject slug}`) that used this file. An empty array is fine |

## A condition

| Field | Required | Rule |
|---|---|---|
| `id` | Required | `c` plus three digits. Unique within the file. Ids are never reused |
| `kind` | Required | One of `condition_kind` in the catalog |
| `field_id` | Required | A field id in the catalog. `custom` for a condition in the user's own words (`kind` is `value` or `other`) |
| `operator` | Conditional | One of `operator` in the catalog. Required when `value` is not `null`; `null` when `value` is `null` |
| `text` | Required | The condition in the user's words, shown back to the user |
| `value` | Optional | The threshold or the allowed set, typed as the catalog field: a number for a numeric field, a string or an array of strings for a string or enum field, `null` for a `custom` condition |
| `unit` | Conditional | The catalog unit of `field_id`; `null` when the field has none |
| `level` | Required | `must` or `want` |
| `source` | Required | `user` when the user wrote the condition, or the id of a work value from `job-change-decision/references/work-values.md` |
| `how_to_judge` | Conditional | One sentence saying what to look at in a candidate when rating. Required and non-empty when `field_id` is `custom` |
| `created` | Required | `YYYY-MM-DD` |
| `updated` | Required | `YYYY-MM-DD`, on or after `created` |
| `active` | Required | Boolean. A condition is never deleted; it is switched off |

The `kind` to `field_id` correspondence for the six sheet items of the job search is: `role` to `job_title`, `industry` to `industry`, `salary_min` to `salary_min`, `location` to `work_location`, `remote` to `remote_policy` or `remote_days_per_week`, `employment_type` to `employment_type`. `value` and `other` map to `custom`.

## A history entry

| Field | Required | Rule |
|---|---|---|
| `date` | Required | `YYYY-MM-DD` |
| `condition_id` | Required | An id present in `conditions` |
| `field` | Required | The name of the condition field that changed (`value`, `level`, `active`, `text`, `how_to_judge`, `operator`) |
| `before` | Required | The value before the change (`null` allowed) |
| `after` | Required | The value after the change (`null` allowed) |
| `reason` | Required | Why it changed, in the user's words. Non-empty |

Every change to a condition appends one entry and bumps the condition's `updated` and the root `updated`. Adding a condition appends an entry whose `field` is `active`, `before` is `null` and `after` is `true`.

## Validation (validate_wishes.py)

```
python validate_wishes.py <wishes.json> [--json]
```

Exit code 0 is PASS (WARN alone counts as PASS), 1 is FAIL.

ERROR:

- the file does not parse as JSON, or the root is not an object
- a required root field is missing or has the wrong type
- a condition is missing a required field, or `id` is malformed or duplicated
- `kind`, `level` or `operator` is outside its enumeration
- `field_id` is absent from the catalog
- `value` is not `null` while `operator` is `null`, or `value` is `null` while `operator` is not `null`
- `value` does not match the catalog type of `field_id` (a string for an integer field, a value outside an enumeration, and so on)
- `unit` differs from the catalog unit of `field_id`
- `field_id` is `custom` while `how_to_judge` is empty
- `created` or `updated` is not a real date, or `updated` is before `created`
- a history entry references an unknown `condition_id`, or has an empty `reason`
- an element of `used_in` does not match the decision id form

WARN:

- `schema_version` is outside the known versions
- `conditions` is empty
- a `must` condition has `active` false (the user may have switched off a required condition by mistake)
- a `kind` of `salary_min` or `remote` is absent among the active conditions (the job search records both as required)
