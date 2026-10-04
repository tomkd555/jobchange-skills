# company_index.json specification

The canonical reference for company_index.json, the mapping between company names and company slugs, in the job-change-support skill group. The code of `scripts/validate_company_index.py` follows this specification exactly.

company_index.json is "the one canonical source for resolving a company name to a slug." Each sub-skill (company research, application document writing, job interview preparation, exam preparation) resolves the same company to the same slug every time, and uses that slug as the per-company directory name. Even when the user refers to the same company by a different name, each sub-skill converges on one slug through this list.

## Location

- Where the canonical copy is stored: `{DATA_ROOT}/career-private/company_index.json`
- Where the per-company directory lives: `{DATA_ROOT}/companies/{company slug}/`
- The list is never placed inside the skill's own folder (`skills/job-change-support/`). `assets/company_index_example.json` is a fictitious sample entry.

## Root structure

```json
{
  "schema_version": 1,
  "companies": {
    "acme-cloud": {
      "name": "アクメクラウド株式会社",
      "aliases": ["アクメクラウド", "Acme Cloud"],
      "created": "2026-07-12",
      "score": 72
    }
  }
}
```

| Field | Type | Required/optional | Meaning and entry criteria |
|---|---|---|---|
| `schema_version` | number | Required | The specification version. Currently `1`. Missing, or a non-numeric value, is an ERROR. A number other than `1` is a WARN |
| `companies` | object | Required | An object keyed by company slug, valued by a company entry. Missing, or of an invalid type, is an ERROR. An empty object is fine |

## The `companies` entry

The key is a company slug, and the value is a company entry. A slug must match the following form.

| Part | Rule |
|---|---|
| Prefix (optional) | "One uppercase letter plus an underscore." Used to group companies by priority or by an evaluation tier (example: `S_`). |
| Body (required) | Alphanumerics and hyphens, and Japanese characters (hiragana, katakana, kanji, and full-width alphanumerics and symbols). The first character cannot be a hyphen. A symbol such as whitespace or a path separator is not allowed. |

The body is decided for readability and may be the company's Japanese name (example: `S_アクメクラウド`). A romanized spelling also works (example: `S_acme-cloud`). Because the per-company directory name is identical to the slug, a prefix or Japanese text attached to the slug appears unchanged in the directory name.

`_general` is a reserved name. It is used to place general exam-preparation deliverables that are not specific to a company under `{DATA_ROOT}/companies/_general/` (its canonical use is described in `job-change-exam-prep`'s SKILL.md). The form above disallows a leading underscore. Registering `_general` as a company slug under `companies` is an ERROR from `validate_company_index.py`. A reserved name is never assigned to a company.

| Field | Type | Required/optional | Meaning and entry criteria |
|---|---|---|---|
| `name` | string | Required | The company's official name. Missing or empty is an ERROR |
| `aliases` | array | Required | An array of alternate-name strings. When there is no alternate name, use an empty array `[]`. Not an array, or containing a non-string, is an ERROR |
| `created` | string | Optional | The registration date, in `YYYY-MM-DD` form. Missing is a WARN |
| `status` | string | Optional | The selection-process status. Either `"active"` (in progress) or `"closed"` (ended, or passed over). Treated as `active` when missing. Deliverables are kept even after it becomes `closed`; they are never deleted or moved to an archive. An invalid type, or a value outside the allowed set, is an ERROR |
| `score` | integer | Optional | The company score. An integer from 0 through 100. A machine-readable value copied from `fit_assessment.json`'s `company_score.total`, whose canonical source is the `fit_assessment.json` side (this is a copy for listing and sorting). The fit-assessment skill (job-change-fit-assessment) copies and updates it. Not copied when `company_score.total` is `null` (no axis has been declared for scoring, or no axis could be judged). Missing is allowed (a company not yet investigated or scored). An invalid type or a value out of range is an ERROR. It is independent of the slug prefix (such as `A_`); when the score changes, the slug (the directory name) is unchanged. |

`name` and every entry's `aliases`, taken together, work as the identifier that uniquely points to a company across the whole list. The same string appearing under more than one slug is an ERROR, because each skill would then resolve different slugs from the same name.

## The company-slug resolution procedure (each skill's Step 0)

Each sub-skill fixes the slug with the following procedure before handling a company.

1. When the list exists, first validate it with `validate_company_index.py`. On FAIL (one or more ERROR), fix it following the next section, "Repairing a broken list," before proceeding to resolution. Never resolve against a broken list. When routed from the hub (job-change-support), the hub has already finished validating it before routing. When a sub-skill is launched on its own, that sub-skill runs `validate_company_index.py` itself.
2. Read `company_index.json`. When the list does not exist, create `{"schema_version":1,"companies":{}}` before proceeding.
3. When the company name in the request matches an entry's `name` or `aliases`, use that slug.
4. When there is no match, derive a slug once, register it in the list, and create `companies/{slug}/`.
5. When it later turns out that a different spelling refers to the same company, append that spelling to that entry's `aliases`. A slug is never re-derived.
6. Pass an agent with web tools only the resolved slug (or the directory path under `companies/`), never the list itself.

## Repairing a broken list

The hub (job-change-support) is the one who repairs the list. Writing to it is spread across company research, exam preparation, fit assessment, and job search, but only the hub fixes a broken list. When a sub-skill launched on its own detects a FAIL, it returns to the hub without fixing the list itself. After the repair, rerun `validate_company_index.py` and confirm PASS (zero ERROR) before proceeding to resolution.

The action for each kind of ERROR is as follows.

| ERROR | Action |
|---|---|
| Cannot be loaded as JSON | Show the user the content of the file that could not be loaded and the exception message, and let them choose between fixing it by hand or rebuilding it. The hub never rewrites it automatically (guessing at the structure and fixing it loses the existing registrations) |
| The same `name` or alias is assigned to more than one slug | Show the conflicting identifier and the slugs involved, and let the user choose the merge target with `AskUserQuestion`. The hub merges the entries, moving the merged-away entry's `name` and `aliases` into the target's `aliases`. When both slugs have deliverables under `companies/{company slug}/`, also ask in the same step whether to move them into the target or leave them |
| A malformed slug, a missing or mistyped `schema_version` / `companies` / `name` / `aliases`, an invalid `status` or `score` value, or a non-object entry | The hub shows the location and a proposed fix, and fixes it after the user approves. When the slug changes, also rename the `companies/{company slug}/` directory in the same step |

A WARN alone (such as a missing `created`) does not FAIL, so it is fine to proceed to resolution without fixing it.

## Summary of the validation rules

`validate_company_index.py` checks the following. One or more ERROR is a FAIL (exit code 1); zero ERROR is a PASS (exit code 0; WARN is allowed).

```
python validate_company_index.py <company_index.json> [--json]
```

### ERROR (the list does not stand as a list)

- Cannot be loaded as JSON
- `schema_version` is missing, or of an invalid type
- `companies` is missing, or of an invalid type
- A slug does not match the form "an optional prefix (one uppercase letter plus an underscore) plus a body (alphanumerics, hyphens, and Japanese characters; the first character cannot be a hyphen; whitespace and symbols are disallowed)"
- An entry is of an invalid type
- `name` is missing or empty
- `aliases` is of an invalid type, or contains a non-string
- The same `name` or alias is assigned to more than one slug (including a collision between a `name` and another company's alias)
- `status` is present and is of an invalid type, or is neither `"active"` nor `"closed"`
- `score` is present and is of an invalid type, or is outside the range 0 through 100

### WARN (stands as a list, but with incomplete information)

- `schema_version` is a number other than the known version (`1`)
- `created` is missing
- `aliases` has a duplicate within the same entry
- `name` overlaps with the entry's own alias
