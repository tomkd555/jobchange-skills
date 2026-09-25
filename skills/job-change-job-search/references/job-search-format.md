# Canonical specification for job_search_results.json (job-search-format)

This is the canonical definition of the field specification, entry criteria, and mechanical validation rules for `job_search_results.json`, the job search deliverable. The job searcher agent (job-change-job-searcher) builds the deliverable to this specification. `scripts/validate_job_search_results.py` checks it mechanically against this specification.

The output path is `{DATA_ROOT}/job-search/{YYYYMMDD}-{short slug for the conditions}/job_search_results.json`. Separate from the per-company deliverable tree (`companies/{company slug}/`), a directory is created under `job-search/` for each search run.

## Overall structure

```json
{
  "schema_version": "2.3",
  "search_id": "20260725-remote-infra",
  "mode": "fuzzy",
  "executed_at": "YYYY-MM-DD",
  "conditions": {
    "roles": ["バックエンドエンジニア"],
    "industries": ["SaaS"],
    "salary_min": 6000000,
    "location": "東京都",
    "remote_policy": "リモート中心",
    "employment_type": "正社員"
  },
  "search_sets": {
    "primary": {
      "roles": ["バックエンドエンジニア"],
      "industries": ["SaaS"],
      "salary_min": 6000000,
      "location": "東京都",
      "remote_policy": "リモート中心",
      "employment_type": "正社員"
    },
    "derivations": [
      {
        "lane": "better_salary",
        "roles": ["バックエンドエンジニア"],
        "industries": ["SaaS"],
        "salary_min": 7000000,
        "location": "東京都",
        "remote_policy": "リモート中心",
        "employment_type": "正社員",
        "changed_conditions": ["salary_min"],
        "rationale": "年収下限を主集合の600万円から700万円へ上げて検索した"
      }
    ],
    "exploration": null
  },
  "baseline": { "slug": "kakuu-cloudworks" },
  "improvement_axes": ["salary_condition", "annual_holidays"],
  "results": [
    {
      "title": "バックエンドエンジニア（SaaS・自社開発）",
      "company_name": "架空アトラス株式会社",
      "url": "https://example.com/jobs/atlas-backend",
      "source_site": "求人ボックス",
      "salary_range": "650万〜900万円",
      "location": "東京都渋谷区（フルリモート可）",
      "remote_policy": "フルリモート可",
      "annual_holidays": 125,
      "match_notes": "年収下限・リモート・自社SaaSの3条件に合致する。",
      "better_points": [],
      "quote": "年収650万〜900万円／フルリモート可／年間休日125日",
      "search_set": "primary",
      "lane": null,
      "company_key": "架空アトラス",
      "role_match": "same",
      "related_info": { "posting_age": { }, "salary_benchmark": { } },
      "duty_items": [ ],
      "axis_observations": [ ],
      "axis_judgements": [ ],
      "classification": "apply_candidate",
      "classification_reasons": [
        {"axis": "remote_certainty", "reason": "フルリモート可の記載があり、必須条件を満たす"},
        {"axis": "annual_holidays", "reason": "年間休日125日で必須条件を満たす"},
        {"axis": "salary_condition", "reason": "提示下限650万円が希望する下限を満たす"}
      ],
      "baseline_comparison": { }
    },
    {
      "title": "シニアバックエンドエンジニア",
      "company_name": "架空ノーチラス株式会社",
      "url": "https://example.com/jobs/nautilus-senior-backend",
      "source_site": "マイナビ転職エンジニア",
      "salary_range": "750万〜1000万円",
      "location": "東京都港区",
      "remote_policy": "週3日リモート",
      "annual_holidays": 120,
      "match_notes": "better_salary: 下限を700万円に上げて検索。提示下限750万円。",
      "better_points": [],
      "quote": "年収750万〜1000万円／週3日リモート／年間休日120日",
      "search_set": "derived",
      "lane": "better_salary",
      "company_key": "架空ノーチラス",
      "role_match": "same",
      "related_info": { },
      "duty_items": [ ],
      "axis_observations": [ ],
      "axis_judgements": [ ],
      "classification": "needs_more_research",
      "classification_reasons": [
        {"axis": "overtime_hours", "reason": "残業時間の記載が無く判定できない"}
      ],
      "baseline_comparison": { }
    }
  ],
  "search_log": [
    {
      "query": "サーバーサイドエンジニア-フルリモートの仕事-東京都",
      "url": "https://xn--pckua2a7gp15o89zb.com/...",
      "fetched_at": "2026-07-25",
      "hit_count": 312,
      "adopted_count": 1,
      "source": "求人ボックス",
      "search_set": "primary",
      "lane": null
    },
    {
      "query": "/engineer/list/p13/min0700/o1/kwバックエンドエンジニア/",
      "url": "https://tenshoku.mynavi.jp/engineer/list/p13/min0700/o1/kwバックエンドエンジニア/",
      "fetched_at": "2026-07-25",
      "hit_count": 48,
      "adopted_count": 1,
      "source": "マイナビ転職エンジニア",
      "search_set": "derived",
      "lane": "better_salary"
    }
  ],
  "company_profiles": {
    "架空アトラス": {
      "name": "架空アトラス株式会社",
      "aliases": ["架空アトラス（株）"],
      "official_url": "https://example.com/atlas",
      "careers_url": "https://example.com/atlas/careers",
      "hq_location": "東京都渋谷区",
      "industry": "SaaS",
      "business_summary": {
        "text": "中小企業向けの人事労務 SaaS を自社開発し、サブスクリプションで提供する。",
        "quote": "人事労務クラウドを中小企業向けに提供しています",
        "source_url": "https://example.com/atlas/company",
        "grade": "A"
      },
      "basics": {
        "employee_count": {"value": 320, "source_url": "https://example.com/atlas/company", "grade": "A", "as_of": "2026-03", "note": null},
        "listed": {"value": true, "source_url": "https://example.com/atlas/ir", "grade": "A", "as_of": "2026", "note": null}
      },
      "metrics": {
        "compensation_level": {"value": 6820000, "unit": "円", "source_url": "https://example.com/atlas/ir/yuho2025.pdf", "grade": "A", "as_of": "2025-12", "note": "有価証券報告書「従業員の状況」の平均年間給与"},
        "annual_holidays": {"value": 125, "unit": "日", "source_url": "https://example.com/atlas/careers", "grade": "A", "as_of": "2026", "note": null},
        "monthly_overtime": {"value": null, "unit": "時間", "source_url": null, "grade": null, "as_of": null, "note": "公表値を確認できなかった（しょくばらぼは取得できない）"},
        "paid_leave_rate": {"value": null, "unit": "%", "source_url": null, "grade": null, "as_of": null, "note": "公表値を確認できなかった"},
        "turnover_rate": {"value": null, "unit": "%", "source_url": null, "grade": null, "as_of": null, "note": "公表値を確認できなかった"},
        "male_childcare_leave_rate": {"value": 42.0, "unit": "%", "source_url": "https://example.com/atlas/ir/yuho2025.pdf", "grade": "A", "as_of": "2025-12", "note": null},
        "revenue_growth": {"value": 18.5, "unit": "%", "source_url": "https://example.com/atlas/ir/yuho2025.pdf", "grade": "A", "as_of": "2025-12", "note": null},
        "operating_margin": {"value": -3.2, "unit": "%", "source_url": "https://example.com/atlas/ir/yuho2025.pdf", "grade": "A", "as_of": "2025-12", "note": null},
        "equity_ratio": {"value": 61.0, "unit": "%", "source_url": "https://example.com/atlas/ir/yuho2025.pdf", "grade": "A", "as_of": "2025-12", "note": null}
      },
      "negative_checks": {
        "labor_law_violation_list": {"checked": true, "hit": false, "source_url": "https://www.mhlw.go.jp/kinkyu/151106.html", "as_of": "2026-06-30", "note": "公表事案に掲載が無い。違反が無い証拠にはならない"}
      },
      "recent_news": [
        {"headline": "架空アトラス、シリーズCで30億円を調達", "date": "2026-04-10", "source_url": "https://example.com/atlas/news/2026-04", "grade": "A"}
      ],
      "open_questions": []
    },
    "架空ノーチラス": { }
  },
  "screening": { },
  "coverage_notes": "求人ボックスの検索結果1ページ目を対象とした。",
  "open_questions": [ "" ]
}
```

`duty_items`, `axis_observations`, `axis_judgements`, `related_info`, `screening`, and the second `company_profiles` entry are left empty above, to show the skeleton. `baseline`, `improvement_axes`, and `baseline_comparison` are also placed only to show position, and are used only in `similar_better` mode. Writing them as above under `fuzzy` produces a WARN. `search_sets.exploration` is the 2.2 exploration set; under 2.3 it is `null` (2.3 uses `derivations` instead). The later sections define the actual content. A fully filled fuzzy example is in `assets/job_search_results_example.json`. A fully filled similar_better example is in `assets/job_search_results_similar_better_example.json`, which includes `improvement_axes` and `baseline_comparison`.

## Field specification

### schema_version (string, required)

The current value is `"2.3"`. `"2.2"`, `"2.1"`, `"2.0"`, and `"1.0"` are also readable. Missing or empty is ERROR. A value outside these five known values is WARN.

| Version | What it adds |
|---|---|
| `"1.0"` | Basic job fields, quotation, source URL |
| `"2.0"` | Observation layer (`axis_observations`, `duty_items`), judgement layer (`axis_judgements`, `classification`), summary (`screening`) |
| `"2.1"` | Search log (`search_log`), improvement axes (`improvement_axes`), per-axis comparison (`results[].baseline_comparison`) |
| `"2.2"` | Exploration set (`search_sets`, `results[].search_set`, `results[].role_match`, `screening.exploration`), related information (`results[].related_info`) |
| `"2.3"` | Derivation lanes (`search_sets.derivations`, `results[].lane`, `search_log[].lane`, `screening.derivations`), company information (`company_profiles`, `results[].company_key`) |

A check added in a newer version does not apply to a deliverable written in an older version. A `"1.0"` deliverable is not checked against the observation layer, a `"2.0"` deliverable is not required to have `search_log`, a `"2.1"` deliverable is not required to have `search_sets`, and a `"2.2"` deliverable is not required to have `company_profiles`. A newly created deliverable is written as `"2.3"`.

### search_id (string, required)

The identifier for this search run. Write the same value as the directory name that holds the deliverable (for `job-search/20260725-remote-infra/`, write `"20260725-remote-infra"`). Missing or empty is ERROR. The directory name sits outside the deliverable, so reading the file alone would not tell which search run it belongs to; the same value is written inside the file for that reason. Fit assessment identifies the search run from this value written in `screening_source.search_id`. The canonical specification for `screening_source` lives in job-change-fit-assessment's `references/fit-format.md`.

The format must match the following regular expression (a mismatch is ERROR).

```
^[0-9]{8}-[0-9a-z][0-9a-z-]*$
```

This is the 8-digit run date (`YYYYMMDD`), a hyphen, and a short slug for the conditions (lowercase letters, digits, and hyphens; it cannot start with a hyphen). The date part must be the same day as `executed_at`.

### mode (string, required)

The search mode. It must be one of the following two values. Missing, empty, or a value outside these two is ERROR.

| Value | Meaning |
|---|---|
| `fuzzy` | Fuzzy search. A search based on a condition sheet that structures the user's wishes |
| `similar_better` | A search for postings that beat a reference posting. A search for postings that exceed the conditions of a reference posting (`baseline`) |

### executed_at (string, required)

The date the search was run (`YYYY-MM-DD`). Missing or empty is ERROR. This records the date the search was run, so it can be confirmed later.

### conditions (object, required)

The conditions used for the search. These must be anonymised, and **must not include the current employer's name, the user's name, or the current salary**. A salary floor for the desired range (such as `salary_min`) may be included in the conditions. A non-object value is ERROR; an empty object is WARN.

The keys are free-form, but `roles`, `industries`, `salary_min`, `location`, `remote_policy`, `employment_type`, and `other` are recommended. `salary_min` is written as a number in yen.

### baseline (object, optional)

A reference to the reference posting used in `similar_better` mode. It carries either `url` (the posting's page URL) or `slug` (the slug under `companies/{company slug}/`).

- If `baseline` is missing under `similar_better`, it is WARN (recording the reference posting is recommended).
- If `baseline` is present under `fuzzy`, it is WARN (it is not used under fuzzy).
- If neither `url` nor `slug` is present, it is ERROR. `slug` must match the company slug format (a mismatch is ERROR). The canonical definition of the format lives in job-change-support's `references/company-index-format.md`.

### results (array, required)

The array of postings obtained by the search. A non-array value is ERROR. An empty array is WARN (recording the circumstances that prevented retrieval in `coverage_notes` is recommended). Each element carries the following fields.

| Field | Required | Entry criteria |
|---|---|---|
| `title` | Required | The posting's title. Missing or empty is ERROR |
| `company_name` | Required | The name of the company that placed the listing. Missing or empty is ERROR |
| `url` | Required | The URL of the listing page. It must be a string starting with `http` (a mismatch is ERROR) |
| `source_site` | Required | The name of the listing site (求人ボックス, マイナビ転職エンジニア, type, Wantedly, etc. The canonical definition of covered sites is `query-catalog.md`). Missing or empty is ERROR |
| `match_notes` | Required | A summary of the fit against, and gaps from, the conditions. Missing or empty is ERROR |
| `quote` | Required | A quotation from the listing page. Missing or empty is ERROR |
| `salary_range` | Optional | The salary range as a string. `null` when the listing reads 「応相談」 (negotiable) or similar and the value cannot be determined. A value that is neither a string nor null is ERROR |
| `location` | Optional | The work location as a string, or `null`. A value that is neither a string nor null is ERROR |
| `remote_policy` | Optional | The remote-work policy as a string, or `null`. A value that is neither a string nor null is ERROR |
| `annual_holidays` | Optional | The number of annual holidays. A number, a string, or `null` (a boolean is ERROR) |
| `better_points` | Conditional | An array of points on which this posting improves on the reference posting. Only for `similar_better`. A non-array value, or an element that is not a non-empty string, is ERROR |
| `baseline_comparison` | Conditional | A per-axis comparison against the reference posting. Only for `similar_better`. The specification follows below |

`quote` must transcribe the wording of the listing page verbatim. A posting that could not be retrieved must not be fabricated. When the salary reads 「応相談」 (negotiable), 「経験を考慮」 (commensurate with experience), or the like and no number can be read, `salary_range` is `null`.

#### Consistency between better_points and the mode

- Under `similar_better` mode, a result that has no `better_points`, or an empty one, is WARN (recording the points on which it improves on the reference posting is recommended).
- Under `fuzzy` mode, a `better_points` with any elements is WARN (it is reserved for `similar_better`).

### search_log (array, required since 2.1)

Records each search that was run, one entry per search. **Any claim of search coverage rests on this log alone.** A search absent from the log is a search that was not run. A statement not backed by this log, such as 「網羅的に調べた」 (researched exhaustively) or 「主要な求人サイトを一通り確認した」 (went through all the major job sites), must not appear in `coverage_notes` or in a report. What can be written is only 「このクエリでこの件数を見た」 (this query returned this many hits).

Missing, an empty array, or a non-array value is ERROR (2.1). It is not required for a `"2.0"` or earlier deliverable.

The four keys that allow `null` still cannot be omitted as keys (a failed retrieval is made explicit with `null`).

| Field | Required | Entry criteria |
|---|---|---|
| `query` | Required | The query string that was run. When built from URL syntax, its path; for a `site:` search, the search terms transcribed as typed. Missing or empty is ERROR |
| `source` | Required | The name of the source (a site name, or `WebSearch`). Missing or empty is ERROR |
| `url` | Required (null allowed) | The URL that was actually fetched. `null` when a `site:` search does not settle on a fixed results-page URL. A string not starting with `http` is ERROR |
| `fetched_at` | Required (null allowed) | The retrieval date (an actual `YYYY-MM-DD` date, or ISO 8601 starting with a date). A malformed or non-existent date is ERROR |
| `hit_count` | Required (null allowed) | The total number of hits for the search. `null` when the page shows no count. A negative value or a non-integer is ERROR |
| `adopted_count` | Required (null allowed) | The number of postings adopted into `results` from that query. A negative value or a non-integer is ERROR |
| `search_set` | Required since 2.2 | The set this query belongs to. Under 2.2, `primary` or `exploration`; under 2.3, `primary` or `derived`. Anything else is ERROR |
| `lane` | Conditionally required since 2.3 | The lane name when `search_set` is `derived`. A lane absent from `search_sets.derivations` is ERROR. A `lane` on a `primary` query is ERROR (`null` is allowed) |

If one or more results have `results[].search_set` equal to `exploration` while no `search_log` element has `search_set` equal to `exploration`, that is ERROR (2.2). A posting in the exploration set can only have been adopted from an exploration-set query. Under 2.3 the same rule applies per lane: if a result has `lane` X while no `search_log` element has `lane` X, that is ERROR. More than 3 `search_log` elements for one lane is WARN.

After merging the partial files from job searchers who ran in parallel, `adopted_count` can end up larger than the actual adopted count, by however much deduplication removed. The validation script does not check this difference.

`query` is part of the deliverable and falls within the scope of the PII lint (described below). Placing the user's name, current employer's name, or current salary into a search query makes this check ERROR.

## Observation layer (2.0)

The layer that records the facts read from a job posting; **it is written by the job searcher agent**. It is limited to what can be filled in from the posting's own content alone, without knowing the user's own conditions. The canonical definition of the axes and classification vocabulary lives in job-change-support's `references/screening-axes.md`.

### results[].duty_items (array, required)

Transcribes each quoted line from the posting's description of duties and assigns it a category. An empty array when there is no such description.

| Field | Required | Entry criteria |
|---|---|---|
| `quote` | Required | A quotation of a duty description. Empty is ERROR |
| `category` | Required | One of `build` / `operate` / `verify` / `automate` / `coordinate` / `manage` / `customer_facing` / `other`. Any other value is ERROR |

### results[].axis_observations (array, required)

Carries exactly the 8 axes, one each, no more and no fewer (missing, duplicate, or an unknown `axis` is ERROR).

| Field | Required | Entry criteria |
|---|---|---|
| `axis` | Required | One of the 8 axis ids |
| `stated` | Required | Whether the posting states anything on this axis (boolean) |
| `value` | Required | The type per axis follows the table below (the value range and unit are defined by `screening-axes.md`). `null` when there is no statement, or when only a qualitative expression exists that cannot be reduced to a value |
| `value_text` | Conditionally required | A summary of the qualitative expression. Required when `stated=true` and `value` is `null` |
| `quote` | Conditionally required | A quotation from the listing page. Required and non-empty when `stated=true` |
| `note` | Optional | Supplementary remarks |

When `value` is not `null`, the validation script checks the following per axis. The enumeration values, value ranges, and units themselves live in job-change-support's `references/screening-axes.md`, and are not duplicated here.

| Axis id | Type | Check |
|---|---|---|
| `remote_certainty` | Enumeration | A value outside the enumeration for this axis in `screening-axes.md` is ERROR |
| `oncall_load` | Enumeration | A value outside the enumeration for this axis in `screening-axes.md` is ERROR |
| `overtime_hours` | Number | A non-number, or a negative value, is ERROR |
| `annual_holidays` | Number | A non-number, or a negative value, is ERROR |
| `hands_on_ratio` | Number | A non-number, or a value outside the range in `screening-axes.md`, is ERROR |
| `coordination_ratio` | Number | A non-number, or a value outside the range in `screening-axes.md`, is ERROR |
| `salary_condition` | Number | A non-number, or a negative value, is ERROR. A value under 10,000 yen is WARN, on suspicion of confusing yen with man-yen units |
| `experience_distance` | — | `value` is fixed at `null`. A non-null value is ERROR |

The validation script does not treat a boolean as a number (`true` is ERROR).

`hands_on_ratio` and `coordination_ratio` are calculated from the category counts in `duty_items`. When `duty_items` has fewer than 3 entries, the sample is too small, so `stated` is set to `false` and `value` to `null`. The validation script recalculates the ratio from `duty_items` and treats a mismatch with `value` as ERROR (tolerance 0.01).

The structure of the `experience_distance` observation is defined by `screening-axes.md`. The validation script treats a non-null `value` as ERROR. When `stated=true`, it is also ERROR if `required_experience` is not an array of non-empty strings, or if `job_family` is not a non-empty string. The three values for distance are the vocabulary of the judgement layer (`axis_judgements`) and do not appear in the observation layer.

### improvement_axes (array, similar_better only, since 2.1)

Lists the ids of the improvement axes the user has decided to target. The values are the five: `salary_condition`, `remote_certainty`, `annual_holidays`, `overtime_hours`, `scope_of_change`. These are anonymised conditions and may be passed to the job searcher agent.

This axis has no fixed direction on its own scale; whether `different` counts as an improvement or a worsening is not determined by the axis itself (a change from permanent to fixed-term employment also comes out as `different`). Therefore **`employment_type` cannot be taken as an improvement axis**. A wish about employment type is handled as a required condition in `conditions.employment_type`. `employment_type` present in `improvement_axes` is ERROR.

Missing or empty under `similar_better` is WARN; present under `fuzzy` is WARN. A non-array value, an unknown axis id, `employment_type`, or a duplicate is ERROR.

This array is used to derive `baseline_comparison.overall`. **Which axis the user wants to beat is the user's own preference and is not determined by the per-axis observation**, so the preference is gathered into this one array alone, and the observation layer carries no judgement of better or worse.

### results[].baseline_comparison (object, similar_better only, since 2.1)

Records the result of comparing the reference posting and the candidate posting axis by axis. The free-text `better_points` is kept as is, and `baseline_comparison` holds the same comparison in a mechanically checkable form. It is the only field that crosses layers.

| Part | Layer | Written by |
|---|---|---|
| `axes[]` | Observation layer | The job searcher agent. Both sides being compared are postings, and none of the user's own information is needed |
| `overall` | Judgement layer | The skill itself. It needs `improvement_axes` (the user's own preference) |

Missing under `similar_better` is WARN (since 2.1); present under `fuzzy` is WARN. This follows the same treatment as `better_points`.

```json
"baseline_comparison": {
  "axes": [
    {
      "axis": "salary_condition",
      "relation": "higher",
      "baseline_value": "600万〜800万円（下限600万円）",
      "candidate_value": "700万〜950万円（下限700万円）",
      "quote": "年収700万〜950万円",
      "note": null
    }
  ],
  "overall": "better"
}
```

`axes` carries exactly the following 6 axes, one each, no more and no fewer (missing, duplicate, or an unknown `axis` is ERROR). The upper 4 axes use the axis ids from job-change-support's `references/screening-axes.md` as they are. The lower 2 axes are **additional axes reserved for the baseline comparison**, and are not among the 8 axes in `screening-axes.md` (they do not appear in the 8-axis judgement or in `screening.unmet_axis_summary`).

| axis | Scale of the fact | Side that `higher` refers to |
|---|---|---|
| `salary_condition` | Annualised lower bound of the offered range (yen) | The larger amount |
| `remote_certainty` | Degree of remote work (full remote > partial remote > no remote) | The greater degree of remote work |
| `annual_holidays` | Number of annual holiday days | The greater number of days |
| `overtime_hours` | Hours of fixed or deemed overtime (`unknown` when unstated) | The greater number of hours |
| `employment_type` (additional axis) | Whether the employment type is the same as the reference posting | Has no ordering, so `higher`/`lower` are not used |
| `scope_of_change` (additional axis) | Breadth of the scope of changes to work location and duties (limited < unlimited) | The broader scope |

`scope_of_change` comes from statute. The April 2024 amendment to the Employment Security Act made it mandatory for job listings to state three items: 「従事すべき業務の変更の範囲」 (scope of changes to duties), 「就業場所の変更の範囲」 (scope of changes to work location), and 「有期労働契約を更新する場合の基準」 (criteria for renewing a fixed-term contract) (Ministry of Health, Labour and Welfare, https://www.mhlw.go.jp/content/001114166.pdf, grade A). A posting that states none of these three items may not be meeting its statutory disclosure obligation. The observation layer leaves it as `unknown`, and the absence of the statement is written into `open_questions`.

**`relation` states only the factual relationship; it carries no judgement of good or bad.** Which side is which on the scale is decided from the two job postings alone. Which side is desirable is the user's own preference, and cannot be decided in the observation layer (the basis for this separation is in "Separating observation from judgment" in `search-methods.md`).

| Field | Required | Entry criteria |
|---|---|---|
| `axis` | Required | One of the 6 axis ids above |
| `relation` | Required | `higher` / `lower` / `same` / `unknown`. `employment_type` alone takes the three values `same` / `different` / `unknown` |
| `baseline_value` | Conditionally required | The reference posting's value. Required and non-empty when `relation` is anything other than `unknown` |
| `candidate_value` | Conditionally required | The candidate posting's value. Required and non-empty when `relation` is anything other than `unknown` |
| `quote` | Conditionally required | A quotation from the candidate posting's listing page. Required and non-empty when `relation` is anything other than `unknown` |
| `note` | Optional | Supplementary remarks |

**An axis absent from either posting is `unknown`. An absent statement must not be treated as `same`.** The absence of a statement does not mean "the same condition as the reference posting" (the basis is "The absence of a statement is never used as evidence" in `search-methods.md`). The validation script requires both sides' values and a quotation for any relation other than `unknown`, mechanically enforcing this rule. A comparison that cannot be quoted cannot be written.

When the reference posting's `job_posting.json` has `schema_version` `1.0`, `scope_of_change` does not exist in that file. This axis is then `unknown` (the absence is not read as "the scope of change is the same").

#### Deriving overall

`overall` takes one of two values, `better` / `not_better`. It looks only at **the axes listed in `improvement_axes`**. An axis that was not chosen is recorded only for display. Whether an untargeted axis went up or down has no determinable good or bad for the user, so it is not reflected in the overall judgement.

Each axis has the following direction of improvement.

| axis | Direction of improvement | Opposite direction |
|---|---|---|
| `salary_condition` | `higher` | `lower` |
| `annual_holidays` | `higher` | `lower` |
| `remote_certainty` | `higher` | `lower` |
| `overtime_hours` | `lower` | `higher` |
| `scope_of_change` | `lower` | `higher` |

`employment_type` is not in this table. The observation (`same` / `different` / `unknown`) is recorded and used in the report, but is not reflected in the overall judgement. A directional wish such as converting from fixed-term to permanent employment is also handled as a required condition in `conditions`.

| Condition | overall |
|---|---|
| One or more of `improvement_axes` is in the improving direction, and none of `improvement_axes` is in the opposite direction | `better` |
| Anything else | `not_better` |

The validation script recalculates from this table and treats a mismatch with `overall` as ERROR (it does not cross-check when the 6 axes are not all present). When it is not decided which axis the user wants to beat, whether something is better cannot be derived. For this reason, **it is also ERROR when `overall` is written while `improvement_axes` is empty or missing under `similar_better`**. `unknown` counts toward neither improvement nor worsening. Since `better` can result while an axis remains unconfirmed, the report must state the `unknown` axes explicitly.

## Exploration set and related information (2.2)

Records a search on the conditions the user specified (the primary set) separately from a broadened search run to check for bias in those conditions (the exploration set). The canonical definition of why the exploration set exists and how to build it lives in `bias-checklist.md`. This section defines only the recording on the deliverable's side.

### search_sets (object, required since 2.2)

| Field | Required | Entry criteria |
|---|---|---|
| `primary` | Required | The user's specified conditions. The same content as `conditions`, placed as is. A non-object value is ERROR |
| `exploration` | Required since 2.2 (null allowed) | The exploration set's conditions. `null` when it was not built. A value that is neither an object nor null is ERROR. Under 2.3 it is `null` (an object is ERROR) |
| `derivations` | Required since 2.3 | The array of derivation lanes. Specified in the "Derivation lanes and company information (2.3)" section |

When `exploration` is an object, it carries the following.

| Field | Required | Entry criteria |
|---|---|---|
| `roles` | Required | The array of occupation names searched in the exploration set. Lists adjacent occupations and titles at a shifted seniority level. An empty array when none apply. A non-array of non-empty strings is ERROR |
| `industries` | Required (null allowed) | `null` when the industry restriction was dropped. An array when kept. Anything else is ERROR |
| `dropped_conditions` | Required | The array of condition key names dropped from the primary set (e.g. `["industries"]`). An empty array when none apply. A non-array of non-empty strings is ERROR |
| `rationale` | Required | The reason for dropping it. States that the user answered that the condition was not required. Missing or empty is ERROR |

`exploration` being `null` under `fuzzy` is WARN (it skips the check for bias). `exploration` being an object under `similar_better` is WARN (it is reserved for fuzzy). `salary_min` is not dropped even in the exploration set, so `salary_min` is not written into `dropped_conditions`.

### results[].search_set (string, required since 2.2)

| Value | Meaning |
|---|---|
| `primary` | A posting obtained from a primary-set (the user's specified conditions) query |
| `exploration` | A posting obtained from an exploration-set query (2.2) |
| `derived` | A posting obtained from a derivation-lane query (2.3) |

Under 2.2 there are two values, `primary` and `exploration`; under 2.3 there are two values, `primary` and `derived`; anything else is ERROR. `exploration` while `search_sets.exploration` is `null` is ERROR (a state where exploration results exist without an exploration set having been built). It is written by the job searcher agent, and carries the same value as the adopted query's `search_log[].search_set`.

### results[].role_match (string, required since 2.2)

States the relationship between the posting's occupation and the primary set's `roles`.

| Value | Meaning |
|---|---|
| `same` | Matches the primary set's occupation name, or one of its synonyms (rephrasing 1 or 2 in the synonym table in `query-catalog.md`) |
| `adjacent` | An occupation falling under the "adjacent occupation" column of the synonym table, or an occupation differing only in seniority level |
| `different` | Neither of the above |

A value outside these three is ERROR. A `primary` posting with `different` is WARN (the query may have drifted from the conditions). `role_match` states the relationship between occupation names only; the distance from the user's own experience (`experience_distance`) is judged in the judgement layer, against the user's own career.

### results[].related_info (object, optional)

Records a company's related facts that lie outside the job posting, when they could be retrieved without logging in. It is written by the job searcher agent, and is gathered as supporting material for axes that could not be judged from the posting alone (the axes behind a `needs_more_research` reason). The targets to gather and their sources are in "Sources for related information" in `query-catalog.md`. A key may simply be omitted when it was not retrieved.

| Key | Meaning | Type of `value` |
|---|---|---|
| `employee_count` | Number of employees | Number |
| `founded_year` | Year founded | Number |
| `listed` | Whether listed | Boolean (the only key that may use a boolean) |
| `capital_yen` | Capital (yen) | Number |
| `edinet_code` | EDINET code | String |
| `certifications` | Certifications held (くるみん (Kurumin), えるぼし (Eruboshi), 健康経営優良法人 (Health and Productivity Management Outstanding Organization), etc.) | Array of strings |
| `review_aggregate` | Overall score and number of responses on a review-aggregation site | String (e.g. `"3.4（回答42件）"`) |
| `posting_age` | The posting's listing or update date | String (`YYYY-MM-DD`) |
| `salary_benchmark` | A benchmark market rate looked up under the same occupation name | String (e.g. `"中央値553万円（求人ボックス給料ナビ）"`) |

Any key outside the above 9 is ERROR. Under 2.3, only the per-posting keys (`posting_age`, `salary_benchmark`) are written here. The 7 per-company keys (`employee_count` through `review_aggregate`) are placed in `company_profiles[].basics`; their presence in `related_info` under 2.3 is WARN.

#### Each value in related_info

Each key's value is the following object.

| Field | Required | Entry criteria |
|---|---|---|
| `value` | Required | The type from the table above. `null` when retrieval was attempted but failed |
| `source_url` | Required | The source URL. When `value` is present, a URL without the `http` prefix is ERROR |
| `grade` | Required | An evidence grade, A through D. When `value` is not `null`, a value outside these four is ERROR. The canonical definition lives in `job-change-company-research/references/evidence-grading.md` |
| `as_of` | Required (null allowed) | The point in time for the value. `YYYY` or `YYYY-MM`. A malformed value is ERROR |
| `note` | Optional | Supplementary remarks (e.g. the registered founding date differs from the founding year in the company profile, only the count could be read for a review because the text requires login) |

`related_info` holds only supporting facts; company research (`company_research.json`) remains a separate step. What it captures is only what was learned in the course of reading the job posting; it has been through neither the 8-topic coverage nor the audit that company research undergoes. `review_aggregate` is grade C and does not settle a fact on its own.

### screening.exploration (object, required since 2.2)

The record of whether the exploration set was carried out. Placed inside `screening`.

| Field | Required | Entry criteria |
|---|---|---|
| `performed` | Required | Whether the exploration set was carried out (boolean) |
| `result_count` | Required (null allowed) | The count of results with `search_set` equal to `exploration`. `null` when not carried out |
| `apply_candidate_count` | Required (null allowed) | The count among those that are `apply_candidate`. `null` when not carried out |

Missing any of the 3 keys is ERROR. When `performed` is `true`, both counts must be integers matching the actual tally, or it is ERROR. When `performed` is `false`, both counts must be `null`, and `search_sets.exploration` being an object is ERROR (an exploration set exists but is recorded as not carried out).

## Derivation lanes and company information (2.3)

Generalises the 2.2 exploration set into 10 lanes, in the direction of improving conditions and the direction of broadening scope, and records the company information for every company that appears in the results, into the same deliverable. The canonical definition of the purpose and construction of the lanes is `derivation-lanes.md`; the canonical definition of the sources for company information is "Sources for company information" in `query-catalog.md`. This section defines only the recording on the deliverable's side.

### search_sets.derivations (array, required since 2.3)

Places one element per chosen lane. An empty array when no lane was chosen (WARN under fuzzy). A non-array value is ERROR. Under 2.3, `search_sets.exploration` is `null`; an object is ERROR.

| Field | Required | Entry criteria |
|---|---|---|
| `lane` | Required | The lane name. A value outside the 10 in `derivation-lanes.md`, or a duplicate within the array, is ERROR |
| `roles` | Required | The array of occupation names searched in this lane. An empty array when none apply. A non-array of non-empty strings is ERROR |
| `industries` | Required (null allowed) | `null` when the industry restriction was dropped. An array of non-empty strings when kept. Anything else is ERROR |
| `salary_min` | Required (null allowed) | This lane's salary floor (yen). A value that is neither a number nor null is ERROR. A value lower than `search_sets.primary.salary_min` is ERROR |
| `location` | Required (null allowed) | The work location. A string or null |
| `remote_policy` | Required (null allowed) | The remote-work policy. A string or null |
| `employment_type` | Required (null allowed) | The employment type. A string or null |
| `changed_conditions` | Required | The array of condition key names moved from the primary set (e.g. `["salary_min"]`). An empty array, or anything other than an array of non-empty strings, is ERROR |
| `rationale` | Required | The reason for moving it. Missing or empty is ERROR |

### results[].lane (string, conditionally required since 2.3)

For a posting with `search_set` equal to `derived`, states the lane name of the adopted query. `derived` while missing, or a lane name absent from `search_sets.derivations`, is ERROR. A `lane` on a `primary` posting is ERROR (`null` is allowed).

### results[].company_key (string, required since 2.3)

The key into `company_profiles`. Missing, empty, or a key absent from `company_profiles` is ERROR. Company-name normalisation follows the rule below, and `normalize_company_key` in `scripts/validate_job_search_results.py` is its sole implementation. The merge script (`scripts/merge_search_results.py`) uses the same function.

1. Apply Unicode NFKC normalisation (full-width alphanumerics to half-width, `（株）` and `㈱` unified to `(株)`).
2. Strip all whitespace.
3. Strip corporate-form notations (株式会社, 有限会社, 合同会社, 合資会社, 合名会社, 一般社団法人, 一般財団法人, 公益社団法人, 公益財団法人, `(株)`, `(有)`, `(同)`) from the leading and trailing positions, repeatedly, until none remain. A notation in the middle of the name is kept.
4. Lowercase ASCII characters.

When the normalised value of `company_name` differs from `company_key`, and matches neither the normalised `name` nor any normalised `aliases` value in the profile, it is WARN. A name that is only a corporate-form notation becomes an empty string, which is ERROR.

### company_profiles (object, required since 2.3)

Company information for each company appearing in the results. The key is `company_key`, and the value is the following object. It is written by the job searcher agent (`company_profile` mode), and belongs to the observation layer. A non-object value is ERROR. An element that no posting references is WARN.

| Field | Required | Entry criteria |
|---|---|---|
| `name` | Required | The company name (the formal name from the company profile). Empty is ERROR. The key must match the normalised value of either `name` or `aliases`, or it is ERROR |
| `aliases` | Required | The array of alternate spellings that appeared in job postings. When the formal name differs from the posting's spelling, the posting's spelling must be included here (since the key is derived from the posting's spelling). An empty array when none apply. A non-array of non-empty strings is ERROR |
| `official_url` | Required (null allowed) | The official site's URL. A string not starting with `http` is ERROR |
| `careers_url` | Required (null allowed) | The careers page's URL. A string not starting with `http` is ERROR |
| `hq_location` | Required (null allowed) | The headquarters location (string) |
| `industry` | Required (null allowed) | The industry (string) |
| `business_summary` | Required (null allowed) | A summary of the business. When an object, it carries `text` (the summary, empty is ERROR), `quote` (a quotation of the source, empty is ERROR), `source_url` (not starting with `http` is ERROR), and `grade` (outside A through D is ERROR) |
| `basics` | Required | The company's basic information. The keys are limited to the following 7; anything else is ERROR. Each value is checked with the same format and rules as each value in `related_info`. Missing any of the 7 keys is WARN |
| `metrics` | Required | The published values for the 9 quantitative axes. Described below |
| `negative_checks` | Required | The record of checking for negative information. Described below |
| `recent_news` | Required | The array of reporting and announcements from the last 12 months (up to 3 items). An empty array when none apply. Described below |
| `open_questions` | Required | The array of points that could not be confirmed (strings). An empty array when none apply |

#### Keys in basics

Uses the 7 per-company keys from `related_info` as they are.

| Key | Meaning | Type of `value` |
|---|---|---|
| `employee_count` | Number of employees | Number |
| `founded_year` | Year founded | Number |
| `listed` | Whether listed | Boolean |
| `capital_yen` | Capital (yen) | Number |
| `edinet_code` | EDINET code | String |
| `certifications` | Certifications held | Array of strings |
| `review_aggregate` | Overall score and number of responses on a review-aggregation site | String |

#### Axis keys in metrics

Carries the same 9 axes, in the same units, as `company_metrics` in `job-change-company-research`. Missing or containing an unknown key among the 9 keys is ERROR. The canonical definition of the vocabulary is "Quantitative candidate axes" in `job-change-company-research/references/company-score-rubric.md`, and the hub's `test_vocabulary_sync.py` cross-checks it down to the unit.

| Key | Metric | Unit |
|---|---|---|
| `compensation_level` | Average annual compensation | `円` (yen) |
| `annual_holidays` | Total annual holidays | `日` (days) |
| `monthly_overtime` | Average monthly overtime hours | `時間` (hours) |
| `paid_leave_rate` | Paid-leave utilisation rate | % |
| `turnover_rate` | Turnover rate | % |
| `male_childcare_leave_rate` | Male childcare-leave utilisation rate | % |
| `revenue_growth` | Revenue growth rate (annualised) | % |
| `operating_margin` | Operating margin | % |
| `equity_ratio` | Equity ratio | % |

Each axis's value is the following object.

| Field | Required | Entry criteria |
|---|---|---|
| `value` | Required | A number, or `null` when retrieval was attempted but failed. A boolean is ERROR. A negative value other than for `revenue_growth` or `operating_margin` is ERROR. `paid_leave_rate`, `turnover_rate`, `male_childcare_leave_rate`, and `equity_ratio` outside the range 0-100 is ERROR |
| `unit` | Required | A mismatch with the unit in the table above is ERROR |
| `source_url` | Required | When `value` is present, a URL without the `http` prefix is ERROR |
| `grade` | Required | When `value` is not `null`, a value outside A through D is ERROR |
| `as_of` | Required | The point in time for the value (`YYYY` or `YYYY-MM`). When `value` is not `null`, a malformed value is ERROR |
| `note` | Optional | Supplementary remarks. When `value` is `null` and `note` is empty, it is WARN (a reason for the failed retrieval should be left) |

`compensation_level.value` under 10,000 yen is WARN (on suspicion of confusing man-yen units). The average annual compensation in a securities report is an average across all employees, and must not be read as the salary for the posting's occupation.

#### negative_checks.labor_law_violation_list

Records whether the company appears on the Ministry of Health, Labour and Welfare's 「労働基準関係法令違反に係る公表事案」 (published cases of labour-law violations).

| Field | Required | Entry criteria |
|---|---|---|
| `checked` | Required | Whether it was checked (boolean) |
| `hit` | Required | Whether it appeared on the list (boolean). `null` when `checked` is `false` (anything else is ERROR) |
| `source_url` | Required | The URL of the published material checked. When `checked` is `true`, a URL without the `http` prefix is ERROR |
| `as_of` | Required | The point in time of the published material (`YYYY-MM-DD` or `YYYY-MM`). When `checked` is `true`, a malformed value is ERROR |
| `note` | Conditional | When `hit` is `true`, states the content of the listing (the violated statute, the publication date). Empty is ERROR |

An absence from the list says nothing about whether violations occurred. A report states 「掲載なし」 (not on the list), and never 「違反なし」 (no violations).

#### recent_news

| Field | Required | Entry criteria |
|---|---|---|
| `headline` | Required | The headline. Empty is ERROR |
| `date` | Required | The date (`YYYY-MM-DD` or `YYYY-MM`). A malformed value is ERROR |
| `source_url` | Required | Not starting with `http` is ERROR |
| `grade` | Required | A value outside A through D is ERROR |

`company_profiles` is a preliminary record; company research (`company_research.json`) is still carried out separately. It has been through neither the 8-topic coverage nor the audit that company research undergoes, and company research must be done again once an application target is chosen. `review_aggregate` is grade C and does not settle a fact on its own.

### screening.derivations (object, required since 2.3)

The record of whether derivation lanes were carried out. Placed inside `screening`.

| Field | Required | Entry criteria |
|---|---|---|
| `performed` | Required | Whether one or more lanes were carried out (boolean) |
| `lanes` | Required | An array of `{lane, result_count, apply_candidate_count}` per lane. An empty array when not carried out |

The set of lanes in `lanes` must match the set of lanes in `search_sets.derivations`, or it is ERROR (missing, extra, or duplicate). `result_count` is the count of results with `search_set` equal to `derived` for that lane, `apply_candidate_count` is the count among those that are `apply_candidate`, and a non-integer value or a mismatch with the actual tally is ERROR. It is ERROR when `performed` is `true` while `derivations` is empty, or when `performed` is `false` while `derivations` or `lanes` is non-empty.

## Judgement layer (2.0)

Records the result of matching the observations against the user's own conditions. **The skill itself writes this locally.** Since it needs to read `profile.json`, an agent with a means of sending data to the web must not write it.

### results[].axis_judgements (array, required)

Carries exactly the 8 axes, one each, no more and no fewer (missing, duplicate, or an unknown `axis` is ERROR).

| Field | Required | Entry criteria |
|---|---|---|
| `axis` | Required | One of the 8 axis ids |
| `level` | Required | `must` / `want` / `none`. Decided from the profile's condition and work-characteristic requirement levels by the following correspondence. A condition (`conditions[].level`) of `must` becomes `must`, `want` becomes `want`. A work characteristic (`work_character_preferences[].desire`) of `must` becomes `must`, `important` becomes `want`, and `neutral`/`not_required` becomes `none`. An axis with neither a condition nor a characteristic in the profile is `none` |
| `judgement` | Required | `meets` / `not_meets` / `unknown` |
| `threshold_ref` | Conditionally required | The `conditions[].id` or `work_character_preferences[].trait` from the profile used for the judgement. Required when `level` is `must` or `want` |
| `rationale` | Required | The basis for the judgement. States it as a comparison between the observed value and the threshold. Does not write the user's own career history or current salary |

**Guessing is forbidden.** Each of the following is ERROR.

- Judging `meets` or `not_meets` while the corresponding observation has `stated=false` (judging an unstated axis by guesswork).
- Judging `meets` or `not_meets` while the corresponding observation's `value` is `null` (asserting a conclusion from a qualitative expression alone).

### results[].classification (string, required)

One of `apply_candidate` (a candidate to apply to), `needs_more_research` (a candidate needing further research), or `excluded` (an excluded candidate). Any other value is ERROR.

The classification is derived mechanically from the axis judgements. Evaluate in order from the top, and adopt the first match.

| Condition | Classification |
|---|---|
| One or more axes with `level=must` have `not_meets` | `excluded` |
| One or more axes with `level=must` have `unknown` | `needs_more_research` |
| 4 or more of the 8 axes have `unknown` | `needs_more_research` |
| None of the above apply | `apply_candidate` |

The validation script recalculates from this table and treats a mismatch with `classification` as ERROR.

### results[].classification_reasons (array, required)

At least one element is required (empty is ERROR). Each element carries `axis` (one of the 8 axis ids) and `reason` (a non-empty string).

### results[].classification_override (object or null, optional)

Written only when the derived result was changed by hand. It carries `from` (the derived result), `to` (the actual classification), and `reason` (non-empty).

**A change is permitted only in the stricter direction.** Only the direction `apply_candidate` → `needs_more_research` → `excluded` is permitted; the reverse direction is ERROR. This prevents fabricating a single candidate without grounds when there are zero candidates to apply to.

### results[].slug (string or null, optional)

Once the decision is made to proceed to company research, appends the company slug resolved in `company_index.json`. This is the sole linking key between the job search deliverable and the per-company tree.

## screening (object, required since 2.0)

The summary of screening. Missing or a non-object value is ERROR.

| Field | Required | Entry criteria |
|---|---|---|
| `screened_at` | Required | The judgement date (`YYYY-MM-DD`) |
| `profile_schema_version` | Required | The `schema_version` of the profile used for judgement. Allows later verification of whether a fallback was used |
| `axes_source` | Required | `job_change_axis.conditions` (the normal case) / `degraded` (the profile is 1.x and axis judgement is not possible) |
| `counts` | Required | Integers for `apply_candidate`, `needs_more_research`, `excluded`, and `total`. A mismatch with the actual tally is ERROR |
| `recommendation` | Required | `応募推奨あり` (recommended to apply) / `応募推奨なし` (not recommended to apply) / `判定不能` (unable to judge) |
| `rationale` | Required | The basis for the judgement (non-empty) |
| `unmet_axis_summary` | Required | The `{axis, not_meets, unknown}` counts for each of the 8 axes. A mismatch with the actual tally is ERROR |
| `current_employer_exclusion` | Required | The record of whether current-employer postings were excluded. Described below |
| `exploration` | Required since 2.2 | The record of whether the exploration set was carried out. Specified in the "Exploration set and related information" section. WARN if present under 2.3 (it is not read) |
| `derivations` | Required since 2.3 | The record of whether derivation lanes were carried out. Specified in the "Derivation lanes and company information (2.3)" section |

`recommendation` is also a derived value.

| Condition | Value |
|---|---|
| `axes_source` is `degraded` | `判定不能` |
| `counts.apply_candidate` is 1 or more | `応募推奨あり` |
| `counts.apply_candidate` is 0 | `応募推奨なし` |

**When there are zero candidates to apply to, do not pick the strongest candidate anyway; state `応募推奨なし` explicitly.** The validation script treats `応募推奨あり` with zero apply candidates as ERROR.

### current_employer_exclusion

| Field | Required | Entry criteria |
|---|---|---|
| `performed` | Required | Whether the exclusion process was carried out (boolean) |
| `excluded_count` | Conditional | An integer when carried out. `null` when not carried out. An integer while not carried out is ERROR |
| `method` | Required | The judgement method (the fields checked). When not carried out, states the reason |

This field exists to structurally prevent reporting 「除外0件」 (0 excluded) without ever having checked. The skill itself does not report as an outcome something it has not verified.

### coverage_notes (string, optional)

Records the scope and limits of the search (the sites covered, the number of pages covered, postings excluded from scope because they required registration, fields that could not be retrieved due to dynamic rendering, and so on).

### open_questions (array, optional)

Records points that could not be corroborated, and points that should be confirmed before applying because of a gap from the conditions.

## Mechanical validation rules (validate_job_search_results.py)

`scripts/validate_job_search_results.py` performs the mechanical checks. One or more ERROR results in FAIL (exit code 1); zero ERROR results in PASS (exit code 0, even with WARNs present).

```
python validate_job_search_results.py <job_search_results.json> [--json] [--profile <profile.json>]
```

**ERROR (the deliverable does not stand as valid, or a rule is violated)**

- Cannot be parsed as JSON
- `schema_version` missing or empty
- `search_id` missing or empty, or not matching the directory-name format (`{YYYYMMDD}-{short slug for the conditions}`)
- `mode` missing or empty, or other than `fuzzy`/`similar_better`
- `executed_at` missing or empty
- `conditions` is not an object
- `results` is not an array
- A result's `title`, `company_name`, `source_site`, `match_notes`, or `quote` is missing or empty
- A result's `url` does not start with `http`
- A result's `salary_range`, `location`, or `remote_policy` is neither a string nor null
- A result's `annual_holidays` is none of a number, a string, or null
- A result's `better_points` is not an array, or contains an element that is not a non-empty string
- `baseline` is present and carries neither `url` nor `slug`, or `slug` does not match the format
- `search_log` is not an array, or one of its elements is not an object
- A `search_log` element's `query` or `source` is empty, or the keys `url`, `fetched_at`, `hit_count`, or `adopted_count` are missing
- A `search_log` element's `url` does not start with `http`, `fetched_at` is malformed or a non-existent date, or `hit_count`/`adopted_count` is neither a non-negative integer nor null
- `improvement_axes` is not an array, contains an unknown axis id, contains `employment_type`, or has a duplicate axis
- `baseline_comparison.overall` is written under `similar_better` while `improvement_axes` is empty or missing
- `baseline_comparison` is not an object, `axes` is not an array, it does not carry exactly the 6 axes (missing, unknown id, or duplicate), or `relation` is outside its per-axis fixed values
- A `baseline_comparison` element has `relation` other than `unknown` while `baseline_value`, `candidate_value`, or `quote` is empty
- `baseline_comparison.overall` is other than `better`/`not_better`, or does not match the result derived from `improvement_axes` and `relation`
- **PII contamination** (only when `--profile` is given): a value derived from the profile — the current employer's name, a value that looks like a name, or the current salary (`salary.current`) — has leaked into the deliverable

When `schema_version` is `"2.1"`, the following is also ERROR.

- `search_log` missing, or an empty array

When `schema_version` is `"2.2"`, the following is also ERROR.

- `search_sets` is not an object, `primary` is not an object, or `exploration` is neither an object nor null
- `search_sets.exploration`'s `roles` or `dropped_conditions` is not an array of non-empty strings, `industries` is neither an array nor null, or `rationale` is empty
- A result's `search_set` is outside the two values, or is `exploration` while `search_sets.exploration` is null
- A `search_log` element's `search_set` is missing, or outside the two values
- A result has `search_set` equal to `exploration` while no `search_log` element has `search_set` equal to `exploration`
- When `--profile` is given: `level` does not match the value determined from the profile's requirement level by the correspondence above
- A result's `role_match` is outside the three values
- A result's `related_info` is not an object, has a key outside the 9 keys, an element value that is not an object, or the keys `value`, `source_url`, `grade`, or `as_of` are missing
- In a result's `related_info`, `value` is not null while `source_url` does not start with `http`, or `grade` is outside the four values. A `value` other than for `listed` is a boolean. `as_of` is malformed
- `screening.exploration` is not an object, one of the 3 keys is missing, or `performed` is not a boolean
- `screening.exploration.performed` is `true` while the two counts are not integers, or do not match the actual tally
- `screening.exploration.performed` is `false` while the two counts are not null, or `search_sets.exploration` is an object

When `schema_version` is `"2.3"`, the following is also ERROR.

- `search_sets` is not an object, `primary` is not an object, `derivations` is not an array, or `exploration` is an object
- A `search_sets.derivations` element is not an object, `lane` is outside the 10 values or duplicated, `roles` is not an array of non-empty strings, `industries` is neither an array nor null, `salary_min` is neither a number nor null, `salary_min` is lower than `primary.salary_min`, `changed_conditions` is empty or not an array of non-empty strings, or `rationale` is empty
- A result's `search_set` is other than `primary`/`derived`
- A result's `search_set` is `derived` while `lane` is missing, or is a lane name absent from `search_sets.derivations`. `lane` is other than null while `search_set` is `primary`
- A `search_log` element's `search_set` is other than `primary`/`derived`. It is `derived` while `lane` is missing or absent from `derivations`. It is `primary` while `lane` is other than null
- A result has `lane` X while no `search_log` element has `lane` X
- A result's `company_key` is missing, empty, or absent from `company_profiles`
- `company_profiles` is not an object. A key matches neither the normalised `name` nor `aliases`. `name` is empty. `aliases` is not an array of non-empty strings. `official_url`/`careers_url` is a string not starting with `http`. `hq_location`/`industry` is neither a string nor null
- `business_summary` is neither an object nor null. When an object, `text`/`quote` is empty, `source_url` does not start with `http`, or `grade` is outside the four values
- `basics` is not an object, has a key outside the 7 keys, or an element value violates the rule for the corresponding value in `related_info`
- `metrics` is not an object, does not carry exactly the 9 keys, an element value is not an object, the keys `value`, `unit`, `source_url`, `grade`, or `as_of` are missing, `unit` differs from the axis's unit, `value` is a boolean or is not a number, a negative value appears other than for `revenue_growth`/`operating_margin`, one of the 4 ratio axes is outside the range 0-100, or `value` is not null while `source_url` does not start with `http`, `grade` is outside the four values, or `as_of` is malformed
- `negative_checks.labor_law_violation_list` is missing or not an object, `checked` is not a boolean, `checked` is `true` while `hit` is not a boolean, `source_url` does not start with `http`, or `as_of` is malformed, `checked` is `false` while `hit` is other than null, or `hit` is `true` while `note` is empty
- `recent_news` is not an array, an element's `headline` is empty, `date` is malformed, `source_url` does not start with `http`, or `grade` is outside the four values
- A company profile's (`company_profiles[]`) `open_questions` is not an array of strings
- `screening.derivations` is not an object, `performed`/`lanes` is missing, or `performed` is not a boolean
- `screening.derivations.performed` is `true` while `search_sets.derivations` is empty, or is `false` while `derivations` or `lanes` is non-empty
- The set of lanes in `screening.derivations.lanes` does not match `search_sets.derivations` (missing, extra, or duplicate), a count is not an integer, or does not match the actual tally

When `schema_version` is `"2.0"`, `"2.1"`, `"2.2"`, or `"2.3"`, the following is also ERROR.

- `screening` missing, or not an object
- `axis_observations` / `axis_judgements` does not carry exactly the 8 axes (missing, unknown id, or duplicate)
- `duty_items` is not an array, `duty_items[].quote` is empty, or `category` is outside the 8 fixed values
- `stated=true` while `quote` is empty
- `stated=true` and `value` is `null` while `value_text` is empty
- `value` falls outside the type or range per axis (the canonical definition is `screening-axes.md`) — a value outside the enumeration, a non-number, a negative value, or a value outside a ratio's range
- The `experience_distance` observation's `value` is not `null`
- `experience_distance` has `stated=true` while `required_experience`/`job_family` does not meet the required form
- An axis with `stated=false` is judged `meets`/`not_meets`
- An axis with `value` equal to `null` is judged `meets`/`not_meets`
- `level` is `must`/`want` while `threshold_ref` is empty, or `rationale` is empty
- One of the two ratio axes has `stated=true` while `duty_items` has fewer than 3 elements, or the recalculated ratio does not match `value`
- `classification` is outside the 3 fixed values, or `classification_reasons` is empty
- `classification` does not match the derived result, and no valid `classification_override` is present
- `classification_override` moves the classification in the looser direction
- `screening.counts` / `unmet_axis_summary` does not match the actual tally
- `recommendation` is `応募推奨あり` with zero apply candidates, or `応募推奨なし` with one or more
- `axes_source` is `degraded` while `recommendation` is other than `判定不能`
- `current_employer_exclusion.performed` is `false` while `excluded_count` is an integer, or is `true` while it is not an integer
- When `--profile` is given: `threshold_ref` does not exist among the profile's condition ids or characteristic ids, or `level` does not match the profile's requirement level

**WARN (it stands as valid, but something is missing or a consistency point needs attention)**

- `schema_version` is outside the 5 known values
- `--profile` was not given (the PII lint and the threshold cross-check were not performed)
- `search_sets.exploration` is null under `fuzzy` (2.2) (skipping the check for bias)
- `search_sets.exploration` is an object under `similar_better` (2.2)
- `search_sets.derivations` is empty under `fuzzy` (2.3) (no derivation lane was carried out)
- More than 3 `search_log` elements for one lane (2.3)
- `related_info` under 2.3 has one of the 7 per-company keys (`employee_count` through `review_aggregate`) (place these in `company_profiles[].basics`)
- The normalised value of `company_name` differs from `company_key`, and matches neither the profile's `name` nor `aliases` (2.3)
- A `company_profiles` element that no result references exists (2.3)
- One of the 7 keys in `basics` is missing (2.3)
- `basics`/`metrics` has `value` equal to null while `note` is empty (2.3)
- `metrics.compensation_level.value` is under 10,000 yen (2.3; suspicion of confusing man-yen units)
- `screening` under 2.3 has `exploration` (it is not read)
- A `primary` result's `role_match` is `different`
- Every result is `excluded` (the required conditions may be too strict)
- More than half the judgements are `unknown` (the posting's information density is low)
- The observed value for `salary_condition` is under 10,000 yen (suspicion of confusing man-yen units)
- `conditions` is an empty object
- `results` is an empty array
- `baseline` is absent under `similar_better`
- `baseline` is present under `fuzzy`
- A `similar_better` result has no `better_points`, or an empty one
- A `fuzzy` result has an element in `better_points`
- `improvement_axes` is absent or empty under `similar_better` (2.1)
- `fuzzy` has an element in `improvement_axes`
- A `similar_better` (2.1) result has no `baseline_comparison`
- A `fuzzy` result has `baseline_comparison`

## PII lint (when --profile is given)

When `--profile <profile.json>` is given, the PII lint runs in addition to the schema check. It extracts the following from `profile.json`, stringifies the entire deliverable JSON, and detects contamination. Contamination is ERROR.

These 3 items are the range that can be mechanically detected by string matching. The canonical definition of the personal-information boundary itself (what may be passed, and what the exceptions are) lives in the hub's `references/pii-boundary.md`; a PASS on this lint is not evidence that the boundary was honoured.

| Extraction target | Extracted from |
|---|---|
| Current employer's name | The `company` of the entry in `career_history` that is currently held (`period` is `〜現在`). When the currently-held entry cannot be identified, the `company` of the first entry. |
| A value that looks like a name | The 5 keys `name`, `full_name`, `氏名`, `kana`, `name_kana` inside `basic`. |
| Current salary | `salary.current` (a number). A value under 10000 is not extracted, to avoid a false match against a non-salary number. The floor of the desired salary is not within the scope of this check (it may be written as a condition). |

profile.json is read only locally and is never sent externally. Every example is fictitious data, found in `assets/job_search_results_example.json` and `assets/job_search_results_similar_better_example.json`.
