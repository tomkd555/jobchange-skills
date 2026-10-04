# Checking search-condition bias (bias-checklist)

<!-- textlint-disable jtf-style/4.3.2.大かっこ［］ -->
<!-- The [E1] form in the body text is the notation for a source id. This file disables that rule to keep the half-width square brackets. -->

This is the canonical procedure for checking, before the search, the biases the user brings into the conditions, and compensating for them with derivation lanes (`derivation-lanes.md`). It is referenced by SKILL.md's Step 1 (building conditions), Step 2 (executing the search), Step 5 (delivery), and the searcher agent's (job-change-job-searcher's) role prompt. The specification for the deliverable-side records (`search_sets`, `results[].search_set`, `results[].lane`, `screening.derivations`) is in `job-search-format.md`.

The evidence level is expressed on a four-step scale, A through D. The canonical definition is in `job-change-company-research/references/evidence-grading.md`. This file's list of biases lays out, as an operational convention, the ones that tend to appear in a user's conditions in Japan's mid-career market. No Japanese study demonstrating each bias's effect on job-search outcomes could be identified. Only a matter with supporting evidence cites a source.

## Position

The user's wishes are searched as they stand, as the condition sheet (`search_sets.primary`). This file establishes one visibility check: surfacing, once, a narrowing concealed in how a wish is worded that the user did not choose, and creating a chance for the user to choose again.

- The primary set (`primary`) is the user's specified conditions, and a derivation lane never replaces it. Even when a derived posting becomes an application candidate, it never substitutes for the primary set's application candidates.
- A derivation lane is built from additional queries in a track separate from the primary set's twelve. The primary set's query count is never cut down to feed a lane (the grounds are in "Derivation lanes are never traded against the primary set" in `search-methods.md`).
- When the user chooses no lane at all, none is built. That none was built stays on record in the deliverable (`search_sets.derivations` is an empty array; this is a WARN in fuzzy).

## List of user-side biases

When building the condition sheet, check whether the following biases have crept into the conditions. When one matches, ask "is that condition required, or a preference?" as one question in Step 1's confirmation. The condition itself is never rewritten. A condition answered as not required becomes a candidate for the corresponding lane to move. The purpose and building method of the lanes are in `derivation-lanes.md`.

| Bias | How it appears in the conditions | Checking question | Corresponding lane |
|---|---|---|---|
| Fixation on the occupation name | Writing the current job's occupation name into `roles` as the only one, unchanged | May another occupation whose duties overlap also be a target? | `adjacent_role` (the "Adjacent occupation" column of the synonym table in `query-catalog.md`; paraphrases 1 and 2 are already used in the primary set) |
| Fixation on the industry | Writing only the current or most recent industry into `industries` | Is the industry a required condition? | `industry_widen` |
| Bias toward large, well-known companies | Writing 「大手」 (major company) or 「上場」 (listed) into `other`. Describing the condition through example companies | Which of the eight axes does the wish for scale and name recognition correspond to? | `company_type` (drops the scale condition, keeps the eight-axis wishes, and searches by each type: foreign-affiliated, startup, listed) |
| Anchoring to the current salary | Setting `salary_min` at the same amount as the current salary, or higher | Is the floor "the lowest acceptable amount", or "the current amount"? | `better_salary` (moves only in the direction of raising the floor; there is no lane in the lowering direction, only the question) |
| Fixation on full remote work | Writing only full remote work into `remote_policy` | If the goal is cutting commute time, does a posting with fewer office days per week also become a target? | `remote_widen` (`query-catalog.md`'s "Expressions of remote work") |
| Fixation on the job title | Narrowing the occupation name by whether 「マネージャー」 (manager) or 「リーダー」 (leader) appears | Is the seniority level required? | `seniority_shift` (`query-catalog.md`'s "Seniority level") |
| The work-location assumption | Writing only one prefecture, excluding an adjacent prefecture within commuting range | If deciding by a commute-time ceiling, does a posting in an adjacent prefecture also become a target? | `region_widen` (the next-choice region is already part of the primary set's twelve queries; the lane widens beyond it) |
| Excluding generalist roles that presuppose relocation | Setting 「転勤なし」 (no relocation) as required | Is it enough that the scope of change in work location is limited? | No lane. Scope of change in work location is not among the eight axes, and fuzzy does not observe it. Copy the posting's statement into `match_notes`, and send confirmation to `open_questions`. |
| Self-limiting by job-change count or employment gaps | Lowering the condition on the reasoning "I have changed jobs several times, so I lower my target" | Is the reason the condition was lowered a requirement in the posting, or the user's own assumption? | No lane. Restore the condition and place it in the primary set. Judge whether to apply by the posting's required qualifications. |
| Self-limiting by age | Lowering the occupation or salary on the reasoning "I am over 35" | Is there a basis for lowering it on account of age? | No lane. Restore the condition and place it in the primary set. The salary trend by age is handled in rule 4 of `{HUB_SKILL_DIR}/references/market-data-sources.md`. |
| Self-limiting by education | Narrowing the target on the reasoning "my education will get me rejected" | Does the posting's required qualifications include education? | No lane. Restore the condition and place it in the primary set. |
| Influence from a recently seen posting | Writing the condition based on a posting seen in a scout email or an advertisement | Did the user decide that condition themselves? | No lane. Tie every posting to a query in `search_log`. Never write that a posting was "seen" when it is absent from the log. |
| Dependence on agent recommendations | Keeping a posting on the reasoning "it was recommended", even when it does not fit the conditions | Which of the user's eight axes does the reason for the recommendation correspond to? | `direct_careers` (enters through a company's own careers page directly). Classification runs on the eight-axis judgment alone; the recommendation itself plays no part. |

The current salary, the number of job changes, age, education, and residential detail and commute time (`commute.json`) are personal information. The checking question is completed entirely between the user and the hub, and only the condition sheet's values are passed to the searcher agent. A rail line name or station name is treated as a condition only when the user wrote it into the condition sheet in their own words, and is never derived from `commute.json`. The rule is in "Rail lines and commuting range" in `query-catalog.md`, and the canonical boundary is defined in `{HUB_SKILL_DIR}/references/pii-boundary.md`.

## On the bias to hesitate before applying

The line "men apply once they meet 60% of the requirements, and women wait until they meet 100%" is widely quoted, but its origin is only said to be an internal report at a U.S. company, and no primary source has been confirmed. This skill's documents never write that figure.

The primary source that can be confirmed is an online experiment the UK's Behavioural Insights Team published in 2022 (10,468 respondents, three conditions using fictitious job postings) [E1]. It reports that men apply once they meet 52.1% of the requirements, and women once they meet 55.7%, and states that in every one of the three conditions, men were more inclined to apply than equally qualified women. The team's own blog explains, citing a journalist's investigation, the course of events behind the 60%-versus-100% figure [E2].

The implication for this skill is reading a posting's required qualifications separately from its preferred qualifications. In the eight-axis judgment, only an unmet `must` grounds exclusion, and an unmet `want` never excludes a posting (the decision table is in `job-search-format.md`). When a user tries to exclude an application candidate themselves on the reasoning that "I do not meet every requirement," confirm from the posting's own wording which requirements are required and which are preferred. An analysis of about 77,000 UK job postings found that postings for senior roles used more words coded masculine (such as "lead"), and postings for support roles used more words coded feminine (such as "support") [E3]. That a posting's choice of words can influence an applicant's self-selection is a reason to read requirements as required and preferred separately. Both are UK samples, and no replication in Japan's mid-career market could be identified.

## Correspondence with derivation lanes

In 2.3, the search widened by the bias check is built as derivation lanes (`derivation-lanes.md`). A lane is a query added on top of the primary set (the user's specified conditions, twelve or fewer queries), up to three per lane. It is used in both fuzzy and similar_better. In similar_better, each lane's `salary_min` is kept at or above the reference posting's floor, and `baseline_comparison.axes` is written for derived postings too.

The primary set's query count is never cut down to feed a lane. The reason and the limitations are in "Derivation lanes are never traded against the primary set" in `search-methods.md`.

2.2's exploration set (up to six queries, fuzzy only) corresponds to the following four lanes. Read 2.2's deliverable through this correspondence.

| 2.2's query count | How it is built | Corresponding lane |
|---|---|---|
| 2 | Two adjacent occupations × the first-choice region × no condition | `adjacent_role` |
| 1 | Main occupation × the first-choice region × dropping `industries` | `industry_widen` |
| 2 | Main occupation × the first-choice region × one level up and one level down in seniority | `seniority_shift` |
| 1 | Main occupation × the first-choice region × widening remote-work phrasing | `remote_widen` |

`salary_min` is never lowered in any lane. The salary floor is the minimum amount the user decides on, and it is a condition.

List the condition a lane moves in `search_sets.derivations[].changed_conditions`, and write the reason it was moved in `rationale`. The only condition ever dropped is one the user answered as not required. A condition answered as required in Step 1 is never dropped by any lane.

## How a derived posting is handled

The recording and reporting rules for a derived posting are in "How results are handled" in `derivation-lanes.md`.

## The unmet count attached to the report

Classification takes three values, and does not rank postings within `apply_candidate` ("The cost of always searching for the best" in `search-methods.md`). The count of unmet `want` conditions can only be known by reading `axis_judgements`, though, so attach one column to Step 5's per-posting table counting the axes whose `level` is `want` and whose `judgement` is `not_meets`. This column belongs only to the report; the deliverable schema omits it. Never sort by this count to make a ranking table.

## Source list

<!-- textlint-disable -->
<!-- This section lists sources in bibliographic form (publisher. title. year. level. URL). This section alone disables the rule, so the separating periods are never judged as Japanese punctuation. -->

- [E1] Behavioural Insights Team. Gender differences in response to requirements in job adverts. 2022-03. Level A (an online experiment by a UK government-affiliated behavioral science research body; 10,468 respondents; three conditions using fictitious job postings). https://www.bi.team/wp-content/uploads/2022/03/Gender-differences-in-response-to-requirements-in-job-adverts-March-2022.pdf
- [E2] Behavioural Insights Team. Women Only Apply When 100% Qualified. Fact or Fake News?. Level B (a blog reporting the absence of a primary source; explains the origin of the 60%-versus-100% figure based on a journalist's investigation). https://www.bi.team/blogs/women-only-apply-when-100-qualified-fact-or-fake-news/
- [E3] Totaljobs. How UK job ads bias applicants by gender. 2017. Level B (an analysis of about 77,000 job postings by the job board itself; the original page returns a 403 from this skill's tools and cannot be read, so its content was confirmed through the company's own Gender Bias Decoder explainer page and trade-press coverage). https://www.totaljobs.com/media-centre/how-uk-job-ads-bias-applicants-by-gender/

<!-- textlint-enable -->
