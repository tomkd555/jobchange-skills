# Decision record specification (decision-format)

The canonical specification of a decision record, the file `job-change-decision` writes while the user compares two to five postings or offers. `scripts/validate_decision.py` checks a file against this specification and, with `--fill`, computes the derived parts (scaled values, the ROC and equal weights, the four rankings and the sensitivity check) from the user's inputs, so that no arithmetic is done by hand.

Location: `{DATA_ROOT}/career-private/decisions/{decision id}.json`. The decision id is `{YYYYMMDD}-{subject slug}`; the slug is lowercase letters, digits and hyphens. The record names the user's conditions and choices, so it is personal information and lives under `career-private/`.

## Overall structure

```json
{
  "schema_version": "1.0",
  "id": "20261115-infra-2sha",
  "date": "2026-11-15",
  "subject": "インフラ職 2 社の比較",
  "candidates": [
    {
      "posting_id": "S_アクメクラウド-20261025-01",
      "company_slug": "S_アクメクラウド",
      "label": "A"
    },
    {
      "posting_id": "B_ベータシステムズ-20261028-01",
      "company_slug": "B_ベータシステムズ",
      "label": "B"
    }
  ],
  "criteria": [
    {
      "id": "k01",
      "field_id": "salary_min",
      "condition_id": "c001",
      "direction": "higher",
      "values": {
        "S_アクメクラウド-20261025-01": 6500000,
        "B_ベータシステムズ-20261028-01": 7000000
      },
      "ratings": null,
      "scaled": {
        "S_アクメクラウド-20261025-01": 0.0,
        "B_ベータシステムズ-20261028-01": 1.0
      }
    },
    {
      "id": "k02",
      "field_id": "monthly_overtime_h",
      "condition_id": null,
      "direction": "lower",
      "values": {
        "S_アクメクラウド-20261025-01": 25,
        "B_ベータシステムズ-20261028-01": null
      },
      "ratings": null,
      "scaled": {
        "S_アクメクラウド-20261025-01": 1.0,
        "B_ベータシステムズ-20261028-01": null
      }
    },
    {
      "id": "k03",
      "field_id": "custom",
      "condition_id": "c003",
      "direction": "higher",
      "values": null,
      "ratings": {
        "S_アクメクラウド-20261025-01": 4,
        "B_ベータシステムズ-20261028-01": 2
      },
      "scaled": {
        "S_アクメクラウド-20261025-01": 0.75,
        "B_ベータシステムズ-20261028-01": 0.25
      }
    }
  ],
  "swing_order": [
    "k01",
    "k03",
    "k02"
  ],
  "swing_points": {
    "k01": 100,
    "k03": 60,
    "k02": 40
  },
  "chosen": "B_ベータシステムズ-20261028-01",
  "decisive_fields": [
    "k01"
  ],
  "compromised_fields": [
    "k02",
    "k03"
  ],
  "follow_up": [
    {
      "at": "3m",
      "date": null,
      "satisfaction": null,
      "notes": {}
    },
    {
      "at": "1y",
      "date": null,
      "satisfaction": null,
      "notes": {}
    }
  ],
  "weights": {
    "swing": {
      "k01": 0.5,
      "k03": 0.3,
      "k02": 0.2
    },
    "roc": {
      "k01": 0.6111,
      "k03": 0.2778,
      "k02": 0.1111
    },
    "equal": {
      "k01": 0.3333,
      "k02": 0.3333,
      "k03": 0.3333
    }
  },
  "scores": {
    "swing": {
      "S_アクメクラウド-20261025-01": 0.425,
      "B_ベータシステムズ-20261028-01": 0.7187
    },
    "roc": {
      "S_アクメクラウド-20261025-01": 0.3194,
      "B_ベータシステムズ-20261028-01": 0.7656
    },
    "equal": {
      "S_アクメクラウド-20261025-01": 0.5833,
      "B_ベータシステムズ-20261028-01": 0.625
    },
    "want_count": {
      "S_アクメクラウド-20261025-01": 0,
      "B_ベータシステムズ-20261028-01": 0
    }
  },
  "rankings": {
    "swing": [
      "B_ベータシステムズ-20261028-01",
      "S_アクメクラウド-20261025-01"
    ],
    "roc": [
      "B_ベータシステムズ-20261028-01",
      "S_アクメクラウド-20261025-01"
    ],
    "equal": [
      "B_ベータシステムズ-20261028-01",
      "S_アクメクラウド-20261025-01"
    ],
    "want_count": [
      "S_アクメクラウド-20261025-01",
      "B_ベータシステムズ-20261028-01"
    ]
  },
  "sensitivity": {
    "delta": 0.2,
    "top_changes": false,
    "details": [
      {
        "criterion_id": "k01",
        "change": "-20%",
        "top": "B_ベータシステムズ-20261028-01"
      },
      {
        "criterion_id": "k01",
        "change": "+20%",
        "top": "B_ベータシステムズ-20261028-01"
      },
      {
        "criterion_id": "k02",
        "change": "-20%",
        "top": "B_ベータシステムズ-20261028-01"
      },
      {
        "criterion_id": "k02",
        "change": "+20%",
        "top": "B_ベータシステムズ-20261028-01"
      },
      {
        "criterion_id": "k03",
        "change": "-20%",
        "top": "B_ベータシステムズ-20261028-01"
      },
      {
        "criterion_id": "k03",
        "change": "+20%",
        "top": "B_ベータシステムズ-20261028-01"
      }
    ]
  }
}
```

## Root fields

| Field | Required | Rule |
|---|---|---|
| `schema_version` | Required | `"1.0"`. Another value is WARN |
| `id` | Required | `{YYYYMMDD}-{subject slug}`; the date part equals `date` with the hyphens removed. The file name is `{id}.json` |
| `date` | Required | `YYYY-MM-DD` |
| `subject` | Required | A short Japanese title. Non-empty |
| `candidates` | Required | Two to five elements with distinct `posting_id` |
| `criteria` | Required | One or more elements with distinct `id` |
| `swing_order` | Required | The criterion ids in the order the swing questions ranked them. A permutation of the criterion ids |
| `swing_points` | Required | The 0 to 100 points the user gave each criterion, keyed by criterion id; the first of `swing_order` is 100 |
| `weights` | Required | Keys `swing`, `roc`, `equal`, each an object keyed by criterion id whose values sum to 1 (tolerance 0.001) |
| `scores` | Required | Keys `swing`, `roc`, `equal`, `want_count`, each keyed by `posting_id` |
| `rankings` | Required | Keys `swing`, `roc`, `equal`, `want_count`, each a permutation of the candidate posting ids, best first |
| `sensitivity` | Required | `delta` (0.2), `top_changes` (boolean), `details` (one element per criterion and direction) |
| `chosen` | Required | A candidate `posting_id`, or `null` while the user has not decided |
| `decisive_fields` | Required | Criterion ids the user named as the deciding items. Empty allowed while `chosen` is `null` |
| `compromised_fields` | Required | Criterion ids on which the chosen candidate is below another candidate or below the user's condition. Empty allowed while `chosen` is `null` |
| `follow_up` | Required | Exactly two elements, `at` `3m` and `1y`, created empty |

### A candidate

| Field | Required | Rule |
|---|---|---|
| `posting_id` | Required | `{company slug}-{YYYYMMDD}-{NN}`; its posting check and match record exist |
| `company_slug` | Required | Equal to the slug part of `posting_id` |
| `label` | Required | A one- or two-character label used in the tables shown to the user (`A`, `B`, ...) |

### A criterion

| Field | Required | Rule |
|---|---|---|
| `id` | Required | `k` plus two digits, unique |
| `field_id` | Required | A field id in the catalog |
| `condition_id` | Optional | The `wishes.json` condition this criterion comes from, or `null` for a posting-check field with no condition. Required when `field_id` is `custom` |
| `direction` | Required | `higher` or `lower`. For a catalog field with a direction it equals the catalog's; for `custom` it is `higher` (a higher rating is better) |
| `values` | Conditional | The raw value per candidate, keyed by `posting_id`, `null` for an unknown value. Required for a numeric catalog field; `null` for `custom` |
| `ratings` | Conditional | The user's 1 to 5 rating per candidate. Required for `custom` and for a non-numeric catalog field; `null` for a numeric field |
| `scaled` | Derived | The 0 to 1 value per candidate. Computed by `--fill` |

## Derived values (computed by --fill)

- `scaled` for a numeric criterion: the worst value among the candidates becomes 0 and the best becomes 1, linearly, after the direction is applied; a `null` value stays `null`. When all known values are equal every known candidate gets 1. For a rated criterion: `(rating - 1) / 4`.
- `weights.swing`: `swing_points` normalised to sum 1.
- `weights.roc`: for the criterion at position `i` of `n` in `swing_order`, `(1/n) × Σ(k=i..n) 1/k`.
- `weights.equal`: `1/n` each.
- `scores.<method>`: for each candidate the sum over criteria of `weight × scaled`, skipping criteria whose `scaled` is `null` for that candidate and renormalising the remaining weights to 1. A candidate with every `scaled` `null` gets `null`.
- `scores.want_count`: the number of criteria with a `condition_id` whose condition is `want` in `wishes.json` and whose `scaled` is 1.0 for that candidate (the top of the candidates). It needs `--wishes`; without it `--fill` keeps the recorded value (0 for a new record) and the validator skips the check with a WARN.
- `rankings.<method>`: candidates sorted by the method's score, highest first; a `null` score sorts last; ties keep the order of `candidates`.
- `sensitivity`: for each criterion, the swing weight is multiplied by `1 - delta` and by `1 + delta` (capped at 1), the other weights are scaled proportionally so the total stays 1, and the first of the recomputed swing ranking is recorded as `top`. `top_changes` is true when any `top` differs from the first of `rankings.swing`.

Values are rounded to four decimals when written.

## Validation (validate_decision.py)

```
python validate_decision.py <decision.json> [--wishes <wishes.json>] [--json]
python validate_decision.py <decision.json> --fill [--wishes <wishes.json>]
```

Exit code 0 is PASS (WARN alone counts as PASS), 1 is FAIL. `--fill` rewrites the derived fields in place and then validates. Without `--fill` the derived fields are recomputed and compared; a difference is ERROR. Run both with `--wishes`; without it `want_count` and its ranking are left unchecked.

ERROR:

- the file does not parse as JSON, or the root is not an object
- a required field is missing or has the wrong type
- `id` is malformed, or its date part differs from `date`
- fewer than two or more than five candidates, a duplicated `posting_id`, a malformed `posting_id`, or `company_slug` not equal to the slug part
- a criterion `id` is malformed or duplicated; `field_id` is absent from the catalog; `direction` is outside `higher`/`lower` or differs from the catalog direction of a directed field
- `field_id` is `custom` while `condition_id` is `null`
- `values` or `ratings` is present for the wrong kind of criterion, has keys that differ from the candidate ids, or holds a value of the wrong type (a rating outside 1 to 5)
- `swing_order` is not a permutation of the criterion ids; `swing_points` has different keys, a value outside 0 to 100, or the first criterion's points differ from 100
- a `weights` method is missing or its values do not sum to 1 within 0.001
- a `rankings` method is missing or is not a permutation of the candidate ids
- a derived field differs from the recomputed value by more than 0.0005
- `chosen` is not `null` and not a candidate; a `decisive_fields` or `compromised_fields` element is not a criterion id
- `follow_up` is not exactly the two elements `3m` and `1y`; `satisfaction` is not `null` and not an integer 1 to 5
- (with `--wishes`) a `condition_id` is absent from `wishes.json`

WARN:

- `schema_version` is outside the known versions
- a criterion has `scaled` `null` for some candidates (an unknown value stays visible in the table)
- `chosen` is not `null` while `decisive_fields` is empty
- `sensitivity.top_changes` is true (the first place depends on one weight; the main session says so to the user)
- `--wishes` was not given (`want_count` and its ranking were not checked)
