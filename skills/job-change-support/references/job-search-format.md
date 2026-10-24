# job_search_results.json specification (job-search-format)

The canonical specification of `job_search_results.json`, the job search deliverable. The job searcher agent (`job-change-job-searcher`) writes a partial file in this form for the postings it found; the main session writes a second partial file for the pages it read through Chrome; `scripts/merge_search_results.py` combines them and removes duplicates; `scripts/validate_job_search_results.py` checks the result against this specification.

Output path: `{DATA_ROOT}/job-search/{YYYYMMDD}-{condition slug}/job_search_results.json`. The directory name is the `search_id`.

`schema_version` is `"3.0"`. Deliverables at `"2.3"` and earlier were written by the previous design and are no longer read; no such deliverable exists in use.

## Overall structure

```json
{
  "schema_version": "3.0",
  "search_id": "20261025-remote-infra",
  "mode": "fuzzy",
  "executed_at": "2026-10-25",
  "conditions": [
    {"condition_id": "c001", "kind": "salary_min", "text": "年収 600 万円以上", "level": "must"},
    {"condition_id": "c002", "kind": "remote", "text": "リモート中心", "level": "must"},
    {"condition_id": "c004", "kind": "industry", "text": "SaaS 業界", "level": "want"}
  ],
  "baseline": null,
  "derivations": [],
  "results": [
    {
      "title": "インフラエンジニア（AWS）",
      "company_name": "架空アトラス株式会社",
      "url": "https://example.com/jobs/atlas-infra",
      "source_site": "求人ボックス",
      "read_via": "webfetch",
      "quote": "年収 650 万〜900 万円／フルリモート可／年間休日 125 日",
      "salary_range": "650万〜900万円",
      "location": "東京都渋谷区",
      "remote_policy": "フルリモート可",
      "employment_type": "正社員",
      "annual_holidays": 125,
      "posted_at": "2026-10-20",
      "lane": null,
      "legal_check": {
        "scope_of_change_duties": {"result": "stated", "quote": "変更の範囲: インフラ運用およびこれに関連する業務"},
        "scope_of_change_location": {"result": "missing", "quote": null},
        "contract_renewal_cap": {"result": "not_applicable", "quote": "雇用形態: 正社員"},
        "posted_at": {"result": "stated", "quote": "掲載日 2026/10/20"},
        "salary_range": {"result": "stated", "quote": "年収 650 万〜900 万円"}
      },
      "must_match": [
        {"condition_id": "c001", "result": "meets", "basis": "提示下限 650 万円"},
        {"condition_id": "c002", "result": "meets", "basis": "フルリモート可の記載"}
      ],
      "match_notes": "年収下限とリモートの 2 条件を満たす。勤務地の変更の範囲の記載がない。",
      "considering": null
    }
  ],
  "search_log": [
    {"query": "インフラエンジニア-フルリモートの仕事-東京都", "source": "求人ボックス", "url": "https://xn--pckua2a7gp15o89zb.com/...", "fetched_at": "2026-10-25", "hit_count": 312, "adopted_count": 1, "lane": null}
  ],
  "coverage_notes": "求人ボックスの検索結果 1 ページ目を対象とした。Indeed と Green は Chrome で 2 件読んだ。",
  "open_questions": []
}
```

## Root fields

| Field | Required | Rule |
|---|---|---|
| `schema_version` | Required | `"3.0"`. Another value is WARN |
| `search_id` | Required | `^[0-9]{8}-[0-9a-z][0-9a-z-]*$`; the date part equals `executed_at` with the hyphens removed |
| `mode` | Required | `fuzzy` (a search from the condition sheet) or `similar_better` (a search for postings that beat a baseline posting) |
| `executed_at` | Required | `YYYY-MM-DD` |
| `conditions` | Required | The anonymised condition sheet: one element per active condition passed to the searcher, with `condition_id`, `kind`, `text`, `level`. Never the current employer's name, the user's name or the current salary. An empty array is WARN |
| `baseline` | Conditional | `{"posting_id": "..."}` under `similar_better`; `null` under `fuzzy`. A `baseline` under `fuzzy` or a missing one under `similar_better` is WARN |
| `derivations` | Required | The derivation lanes that were run, each `{lane, changed_conditions, rationale}`. `lane` is one of the ten lanes in `derivation-lanes.md`; a duplicate is ERROR. An empty array when none was run |
| `results` | Required | The postings. An empty array is WARN |
| `search_log` | Required | One element per query that was run. An empty array is ERROR |
| `coverage_notes` | Optional | The sites and pages covered and what was left out, as a string |
| `open_questions` | Optional | An array of strings |

## A result

| Field | Required | Rule |
|---|---|---|
| `title` | Required | Non-empty |
| `company_name` | Required | Non-empty |
| `url` | Required | Starts with `http` |
| `source_site` | Required | The listing site's name (`query-catalog.md`). Non-empty |
| `read_via` | Required | `webfetch` (the searcher read it) or `chrome` (the main session read it in the user's browser) |
| `quote` | Required | A verbatim passage of the listing page. Non-empty |
| `salary_range` | Required (null allowed) | The published range as a string; `null` when the page gives no figure (応相談) |
| `location` | Required (null allowed) | String |
| `remote_policy` | Required (null allowed) | String, as the page words it |
| `employment_type` | Required (null allowed) | String, as the page words it |
| `annual_holidays` | Required (null allowed) | Integer |
| `posted_at` | Required (null allowed) | `YYYY-MM-DD` |
| `lane` | Required (null allowed) | `null` for the primary set; a lane name present in `derivations` for a derived posting |
| `legal_check` | Required | Exactly the five keys below, each `{result, quote}` with `result` in `legal_check_result` (`stated`, `missing`, `not_applicable`) and `quote` non-empty when `result` is `stated` |
| `must_match` | Required | One element per condition in `conditions` whose `level` is `must`: `{condition_id, result, basis}` with `result` in `match_result` and `basis` non-empty when `result` is `meets` or `not_meets`. A missing or extra `condition_id` is ERROR |
| `match_notes` | Required | One or two sentences on the fit and the gaps. Non-empty |
| `considering` | Required (null allowed) | The user's mark 応募を検討したい: `true`, `false`, or `null` before the user has marked it. Written by the main session only |

### legal_check keys

The items a job posting has had to state since 2024-04-01 under the Employment Security Act enforcement regulations, plus the two items the research found most often missing.

| Key | Item | `not_applicable` when |
|---|---|---|
| `scope_of_change_duties` | 業務の変更の範囲 | never |
| `scope_of_change_location` | 勤務地の変更の範囲 | never |
| `contract_renewal_cap` | 有期契約の更新上限 | the posting states an indefinite-term employment type (正社員) |
| `posted_at` | 掲載日 | never |
| `salary_range` | 給与レンジの幅（下限と上限） | never |

A `missing` result means the page was read and the item was absent. The absence is shown to the user as 要確認 and is never read as a fault of the company.

### Deciding must_match

The searcher compares the posting's wording with the condition text it received. `meets` and `not_meets` need a passage of the page as `basis`; when the page says nothing on the condition the result is `unknown`. A salary condition is judged on the floor of the published range, never on a site filter's result and never on a モデル年収 figure.

## A search_log element

| Field | Required | Rule |
|---|---|---|
| `query` | Required | The query string or the URL path that was run. Non-empty |
| `source` | Required | The site name, `WebSearch`, or `chrome`. Non-empty |
| `url` | Required (null allowed) | The URL fetched; starts with `http` |
| `fetched_at` | Required (null allowed) | `YYYY-MM-DD` |
| `hit_count` | Required (null allowed) | A non-negative integer; `null` when the page shows no count |
| `adopted_count` | Required (null allowed) | A non-negative integer |
| `lane` | Required (null allowed) | `null` for the primary set; a lane in `derivations` otherwise. A lane named by a result but by no search_log element is ERROR |

Any claim about how much was searched rests on this log. 「網羅的に調べた」 and similar claims never appear in `coverage_notes` or in the reply. The count of results is never presented as the size of the market.

## Partial files and the merge (merge_search_results.py)

The searcher writes `job_search_results.partial-searcher.json`, and the main session writes `job_search_results.partial-chrome.json` for the pages it read through Chrome. Both have the structure above; `conditions`, `mode`, `search_id` and `executed_at` are the same in both.

```
python merge_search_results.py <search dir> [--json]
python merge_search_results.py <search dir> --cleanup
```

The merge concatenates `results` and `search_log`, removes duplicates whose normalised `company_name` and `title` agree (the first occurrence is kept, and the removed count is appended to `coverage_notes`), joins `coverage_notes` and `open_questions`, and writes `job_search_results.json`. Exit code 0 on success, 1 when no partial file exists or a partial file does not parse. `--cleanup` deletes the partial files after the validation has passed.

## Validation (validate_job_search_results.py)

```
python validate_job_search_results.py <job_search_results.json> [--json]
```

Exit code 0 is PASS (WARN alone counts as PASS), 1 is FAIL.

ERROR:

- the file does not parse as JSON, or the root is not an object
- a required root field is missing or has the wrong type
- `search_id` is malformed or its date part differs from `executed_at`; `mode` is outside its two values; `executed_at` is not a real date
- `baseline` is present and is not an object with a `posting_id` string
- a `derivations` element is not an object, its `lane` is outside the ten lanes or duplicated, `changed_conditions` is not an array of non-empty strings, or `rationale` is empty
- a result is missing a required key, `url` does not start with `http`, `read_via` is outside its two values, a nullable field has the wrong type, `posted_at` is malformed, or `lane` names a lane absent from `derivations`
- `legal_check` lacks a key or has an extra key; an item's `result` is outside its three values, or `quote` is empty while `result` is `stated`
- `must_match` does not cover exactly the `must` conditions of `conditions`; an element's `result` is outside its three values, or `basis` is empty while `result` is `meets` or `not_meets`
- `considering` is outside `true`, `false`, `null`
- `search_log` is empty; an element lacks a key, `query` or `source` is empty, `url` does not start with `http`, `fetched_at` is malformed, a count is negative or not an integer, or `lane` is absent from `derivations`
- a result names a `lane` that no `search_log` element names

WARN:

- `schema_version` is outside the known versions
- `conditions` or `results` is empty
- `baseline` under `fuzzy`, or no `baseline` under `similar_better`
- more than three `search_log` elements for one lane
- a result's `legal_check` has two or more `missing` items (the posting leaves out several required items)
- `considering` is `null` on every result (the user has not marked any)
