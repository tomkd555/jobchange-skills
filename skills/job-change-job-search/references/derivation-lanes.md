# Derivation lanes (derivation-lanes)

This is the canonical definition of the lanes that derive the search, in a track separate from the primary set (the user's specified conditions), toward improving conditions and toward widening scope. It is referenced by SKILL.md's Step 1 (choosing lanes), Step 2 (executing the search), Step 5 (delivery), and the searcher agent's (job-change-job-searcher's) role prompt. The specification for the deliverable-side records (`search_sets.derivations`, `results[].lane`, `search_log[].lane`, `screening.derivations`) is in `job-search-format.md`. The canonical list of biases and their checking questions is in `bias-checklist.md`.

## Position

- The primary set (`primary`) is the user's specified conditions, run as twelve queries just as given. A lane is a search added on top of the primary set, and never replaces it. The primary set's query count is never cut down to feed a lane (the grounds are in "Derivation lanes are never traded against the primary set" in `search-methods.md`).
- Lanes are used in both fuzzy and similar_better. In similar_better, each lane's `salary_min` is kept at or above the reference posting's floor, and `baseline_comparison.axes` is written for derived postings too.
- `salary_min` is never lowered in any lane. The salary floor is the minimum amount the user decides on, and it is a condition.
- A lane's queries are capped at three. Even selecting all ten lanes adds at most thirty queries.
- A condition answered as required in Step 1 is never dropped by any lane. The conditions a lane moves are limited to conditions answered as a preference, and conditions a lane moves in the improving direction.

## Lane list

| `lane` | Purpose | Condition moved | How to build the queries (up to 3) | Mode | Corresponding bias (`bias-checklist.md`) |
|---|---|---|---|---|---|
| `adjacent_role` | Target another occupation whose duties overlap | Replace `roles` with an adjacent occupation (the "Adjacent occupation" column of the synonym table in `query-catalog.md`) | Two adjacent occupations × the first-choice region. Add one more query if there is a third adjacent occupation | fuzzy, similar_better | Fixation on the occupation name |
| `industry_widen` | Remove the industry specification | Set `industries` to `null`. Replace it with a close industry if one exists | Main occupation × the first-choice region × no industry. One query each for up to two close industries | fuzzy, similar_better (not used when the reference posting's industry is a required condition) | Fixation on the industry |
| `seniority_shift` | Shift the seniority level | Move the title in `roles` one level up and one level down (`query-catalog.md`'s "Seniority level") | One query one level up, one query one level down | fuzzy, similar_better | Fixation on the job title |
| `remote_widen` | Widen the remote-work phrasing | Broaden `remote_policy`'s phrasing (`query-catalog.md`'s "Expressions of remote work") | One or two queries with the broadened phrasing | fuzzy, similar_better. Not used when the primary set has no remote-work condition | Fixation on full remote work |
| `region_widen` | Widen beyond the primary set's next two regions | Set `location` to an adjacent prefecture, or to 「全国＋フルリモート」 (nationwide plus full remote) | Up to two queries for adjacent prefectures, one query for nationwide plus full remote | fuzzy, similar_better. Only when `location` exists | The work-location assumption |
| `better_salary` | Raise the salary floor | Raise `salary_min`. The raise is whichever is larger of the primary set's floor plus 1 million yen, or the primary set's floor times 1.15 (rounded up to the nearest 500,000 yen). In similar_better, this starts from the reference posting's floor | One query with the original occupation × the first-choice region × the new floor, one with the strongest paraphrase × the same, one adding remote work | fuzzy, similar_better. Only when `salary_min` exists | Anchoring to the current salary (only the question is posed; the floor is moved only in the raising direction) |
| `better_holidays` | Increase annual holidays | Add `annual_holidays_min: 120` | One query for 「年間休日120日以上」, one for 「完全週休2日 土日祝」, one for both | fuzzy, similar_better | No corresponding bias (a lane that improves conditions) |
| `better_workstyle` | Reduce overtime and widen discretion over work style | Add `overtime_max: 20`, 「フレックス」, and 「固定残業なし」 | One query for 「残業20時間以内」, one for 「フレックスタイム」, one for 「固定残業代なし」 | fuzzy, similar_better | No corresponding bias (a lane that improves conditions) |
| `company_type` | Change the company type | Place 「外資系」 (foreign-affiliated), 「スタートアップ」 (startup) and 「上場」 (listed) respectively into `other` | One query per type | fuzzy, similar_better | Bias toward large, well-known companies (both a bias favoring large companies and a bias avoiding them) |
| `direct_careers` | Use a company's own careers page as the entry point | Route the search through company-page-family sites | One query each for `site:hrmos.co/pages {職種}`・`site:herp.careers {職種}`・`site:findy-code.io/companies {職種}`. Never guess the company slug (family C in `query-catalog.md`) | fuzzy, similar_better | Dependence on agent recommendations (a bias toward what job-listing sites carry) |

2.2's exploration set (up to six queries, fuzzy only) corresponds to the four lanes `adjacent_role` (2 queries), `industry_widen` (1 query), `seniority_shift` (2 queries), `remote_widen` (1 query). Read 2.2's deliverable through this correspondence.

The count (three queries each) and the salary raise are operational conventions set without measurement. The limitations are in "Research limitations and evidence gaps" in `search-methods.md`.

## How to choose

Step 1 confirms lanes with a multiple-choice selection in AskUserQuestion. Since one question allows up to four options, this is split into three questions.

| Question | Heading | Options |
|---|---|---|
| 1 | Improving conditions | `better_salary`, `better_holidays`, `better_workstyle`, `company_type` |
| 2 | Widening scope | `adjacent_role`, `industry_widen`, `seniority_shift`, `remote_widen` |
| 3 | Location and entry point | `region_widen`, `direct_careers` |

The default is to select every lane that fits the mode and the condition sheet. Mark the options 「（推奨）」 (recommended), and add the cost (the number of additional queries and the count for company-profile collection) to each question's description. When the user does not answer a question, every lane in that question's group is treated as selected. A lane whose condition the table above marks "not used" is dropped from the options.

## Recording

- Write one element of `search_sets.derivations` for each lane chosen. List the key names of the moved conditions (`roles`, `industries`, `salary_min`, `location`, `remote_policy`, `other`) in `changed_conditions`, and write the reason it was moved in `rationale`.
- Record each lane query into `search_log` one at a time, with `search_set` set to `derived` and `lane` set to the lane name.
- For a posting adopted from a lane, set `results[].search_set` to `derived` and `results[].lane` to the lane name.
- When a lane was chosen but the searcher did not respond, the merge (`merge_search_results.py`) records it in `coverage_notes` as not run, and drops that lane from `search_sets.derivations`.

## How results are handled

- A derived posting has the same observation layer and judgment layer as a primary-set posting, and the eight-axis judgment and three-way classification follow the same rules. Classification never depends on how a posting was found.
- Write `results[].role_match` as its relation to the primary set's occupation (`same`, `adjacent`, `different`). A `derived` posting being `different` never triggers a WARN.
- In the report (Step 5), split derived postings within each classification's table into 「派生レーン: {lane}」 (derivation lane) subsections, and place them below the primary set's table. Never dress up a derived application candidate as the top candidate when the primary set has zero application candidates. Since `screening.recommendation` is derived from the count of `apply_candidate` across the primary set and derivations combined, state in `rationale` when application candidates exist only among derived postings.
- Write, in a derived posting's `match_notes`, which lane and which condition produced it (such as 「better_salary: 下限を700万円に上げて検索」). This is so the user can judge by the duties and the conditions.
- Record, in `screening.derivations`, the count per lane and the count of those that are application candidates. When no lane was chosen at all, set `performed: false`, and make `lanes` an empty array.
