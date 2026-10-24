# Job search methodology (grounds and limitations)

<!-- textlint-disable jtf-style/4.3.2.大かっこ［］ -->
<!-- The [E1] form in the body text is the notation for a source id. This file disables that rule to keep the half-width square brackets. -->

The grounds behind the design decisions of `job-change-job-search`: how far to widen a search, what the reply states first, and why the searcher writes observations while the main session writes everything about the user. SKILL.md's Steps 2 and 5 and the searcher's role prompt refer to this file.

Grades follow the hub's `references/evidence-grading.md` (A = primary or peer-reviewed, B = reliable secondary). Every academic study cited here rests on a US or European sample; no replication on a Japanese sample was found. The findings set how the search is run and reported. They never decide a posting's pass or fail.

## Search volume does not predict employment quality

Increasing the number of results never raises the quality of the job obtained on its own. The skill stops at a list that meets the required conditions and offers wider lanes only when the user asks (confidence: high).

- A meta-analysis of 378 independent samples (N=165,933) found that search intensity predicted the number of interviews (rc=.23), offers (rc=.14) and employment status (rc=.19), and did not predict employment quality. Search quality and self-regulation did [E1].

Implication: the default run is the primary set alone. Derivation lanes are optional and never replace the primary set. When the list is short, the reply proposes checking the conditions before widening them. The reply never asks the user to confirm that no better posting exists elsewhere.

Limitation: the meta-analysis did not manipulate where a search is cut off, so no threshold is empirically supported.

## The cost of always searching for the best

A stance of always searching for the best posting lowers satisfaction even when the outcome on paper is strong (confidence: likely).

- Job seekers who kept searching for the best obtained a starting salary 20% higher, reported lower satisfaction with that job and more negative emotion during the search [E2].
- Across seven samples (1,747 people) the maximising-tendency scale correlated negatively with happiness, optimism, self-esteem and life satisfaction, and positively with depression, perfectionism and regret [E3].

Implication: the search result is a list with the match against the required conditions, never a ranking. Ranking belongs to `job-change-decision`, where the user sets the weights. In `similar_better` the items to beat are confirmed before the search, which confines the search to postings that beat the baseline on those items.

Limitation: [E2] is one longitudinal study of US new graduates (11 universities, 548 respondents); [E3] is cross-sectional. Neither applies directly to Japan's mid-career market.

## The reply states the method before the result

Stating the queries and how the postings were narrowed comes before any statement about which posting looks good (confidence: likely).

- A meta-analysis of 108 papers (683 effect sizes, 47,245 people) found that the decline in well-being after a choice was mitigated when attention was directed toward the choice process over the outcome [E4].

Implication: the reply shows the posting table with `must_match` and the missing legal items, then the queries and hit counts from `search_log`. It never claims completeness and never presents the count as the size of the market. The research behind the rebuild found 18–22% of postings estimated as ghost jobs by one vendor and 45% of job changers using job sites, so the count on a site says little about what exists.

Limitation: [E4] covers consumer choice in general; no effect size for job search alone was obtained.

## The searcher observes; the main session judges

The searcher agent holds WebSearch and WebFetch, so it never receives `wishes.json`. It receives the anonymised sheet (condition id, kind, text, level) and writes what the page states and the match against the required conditions on that basis. Everything else about the user (the sheet itself, the `considering` marks, the decision) stays in the main session (confidence: an operational rule derived from the personal-information boundary in the hub's `pii-boundary.md`).

Implication: `must_match` may carry `unknown`. The absence of a statement is never read as `meets` and never as `not_meets`. A posting is a selective document: a missing item can mean the condition does not exist or that it was left unwritten, and the page does not say which.

Limitation: the searcher cannot drop a posting that fails a `want` condition, so the list holds postings the user will reject. The design accepts that cost to keep the boundary.

## The legal items are a checklist, never a verdict

Since 2024-04-01 the Employment Security Act enforcement regulations require a posting to state the scope of change of duties and of work location and the renewal cap of a fixed-term contract (MHLW, https://www.mhlw.go.jp/stf/newpage_32105.html , grade A). The posting date and the range of the salary are the two items the rebuild research found most often missing. `legal_check` records each as `stated`, `missing` or `not_applicable`, and the reply shows a missing item as 要確認. A missing item is a question for the company, never a point against it.

## Source list

<!-- textlint-disable -->
<!-- This section lists sources in bibliographic form (publisher. author and year. grade. DOI. URL). -->

- [E1] Journal of Applied Psychology. van Hooft et al. 2021. Grade A (a meta-analysis of 378 independent samples, N=165,933). DOI:10.1037/apl0000675. https://doi.org/10.1037/apl0000675
- [E2] Psychological Science. Iyengar et al. 2006. Grade A (a longitudinal study of US new-graduate undergraduates, 11 universities, 548 respondents). DOI:10.1111/j.1467-9280.2006.01677.x. https://doi.org/10.1111/j.1467-9280.2006.01677.x
- [E3] Journal of Personality and Social Psychology. Schwartz et al. 2002. Grade A (seven samples, 1,747 people total). DOI:10.1037/0022-3514.83.5.1178. https://doi.org/10.1037/0022-3514.83.5.1178
- [E4] Journal of Consumer Psychology. Belli et al. 2022. Grade A (a meta-analysis of 108 papers, 683 effect sizes, 47,245 people after removing duplicates). DOI:10.1002/jcpy.1283. https://doi.org/10.1002/jcpy.1283

<!-- textlint-enable -->
