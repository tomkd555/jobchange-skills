# Job search methodology (grounds and limitations)

<!-- textlint-disable jtf-style/4.3.2.大かっこ［］ -->
<!-- The [E1] form in the body text is the notation for a source id. This file disables that rule to keep the half-width square brackets. -->

This is the canonical source defining the grounds and limitations behind the job-change-job-search skill's design decisions. The judgment for how far to increase the volume of search, and what to state first in the report, rests on this file. The division of labor between observation and judgment, and the handling of an axis with no statement, rest on this file too. It is referenced by SKILL.md's pipeline (Step 2's search, Step 3.5's eight-axis judgment, Step 5's delivery and hand-off) and its pass/fail gates. The searcher agent's (job-change-job-searcher's) role prompt references it too.

The evidence level is expressed on a four-step scale (A = primary/official, B = reliable secondary, C = word-of-mouth/aggregator sites, D = personal blogs/hearsay/unconfirmed), and academic research carries a DOI. The canonical definition is in `job-change-company-research/references/evidence-grading.md`, and peer-reviewed academic research is included in level A. The scope is employment within Japan. Every academic study this file cites is based on a US or European sample, and no replication on a Japanese sample could be identified. These findings are used as grounds for setting how to conduct the search and how to report it. They are never used as grounds for mechanically deciding a posting's pass or fail.

## Search volume does not predict employment quality

Increasing the number of search results, on its own, never raises the quality of the job obtained. This skill's default behavior is to encourage stopping the search (satisficing) once a posting meeting the required conditions set in advance is found (confidence: very likely, 80% to under 90%).

- A meta-analysis of 378 independent samples (N=165,933) found that job-search quantity (search intensity) predicted the number of interviews at rc=.23, the number of offers at rc=.14, and employment status at rc=.19, while it did not predict employment quality. What predicts employment quality is search quality and self-regulation [E1].

Implication for the design: this skill's default proposal, when there are few application candidates, avoids adding search routes to increase the candidate count. When `screening.recommendation` is `応募推奨なし`, it proposes reconfirming the conditions before loosening them (SKILL.md's pass/fail gate "Recommendation to apply"). It presents a posting meeting the required conditions as an application candidate, and never asks for confirmation that no better posting exists elsewhere.

**Evidence that lowers confidence (limitations)**: the meta-analysis above deals with the relation between search intensity and employment quality, without experimentally manipulating the point at which search is cut off. The threshold itself, of "where to satisfice," is not empirically supported.

## The cost of always searching for the best

With a stance of always searching for the best posting, satisfaction fails to follow even when the outcome on paper is strong. This skill is a tool for finding a posting that meets conditions decided in advance (confidence: likely, 65% to under 80%).

- Job seekers who kept searching for the best obtained a starting salary 20% higher, yet reported lower satisfaction with that job, and experienced more negative emotion throughout the job-search process [E2].
- Across seven samples (1,747 people total), the maximizing-tendency scale correlated negatively with happiness, optimism, self-esteem, and life satisfaction, and positively with depression, perfectionism, and regret [E3].

Implication for the design: classification takes three values, `apply_candidate` / `needs_more_research` / `excluded`. The deliverable does not include a ranking table that orders postings by the strength of their conditions. In similar_better mode, the improvement axis (salary, holidays, remote work, overtime, scope of change) is confirmed before the search. That confirmation confines the search's target to "a posting that beats the reference on the specified axis." When there are zero application candidates, this never dresses up an excluded posting or a needs-more-research posting as the top candidate.

**Evidence that lowers confidence (limitations)**: the maximizing-tendency research is one longitudinal study of US new graduate undergraduates (11 universities, 548 respondents) [E2], and a cross-sectional study dealing with scale correlations [E3]. There are no grounds for applying it directly to Japan's mid-career market, where new-graduate mass hiring and mid-career hiring are institutionally separate. In [E3]'s seven samples, self-esteem and perfectionism were also measured only in some of the samples.

## The report states the selection method plainly

In the deliverable's report, stating the criteria and how the postings were narrowed comes before stating which posting is best (confidence: likely, 65% to under 80%).

- A meta-analysis of 108 papers, 683 effect sizes, and 47,245 people after removing duplicates found that the decline in well-being was mitigated when the decision maker's attention was directed toward the choice process over the outcome [E4].

Implication for the design: the report begins with `screening.recommendation` and `rationale` (the overall verdict and its reason), then shows the count per classification and the unmet/undecidable count per axis. Each posting is listed individually, along with the required conditions it meets, the axes that could not be judged, and the required conditions it fails to meet. Every entry includes `classification_reasons` so the user retains the path to the classification, alongside its result.

**Evidence that lowers confidence (limitations)**: in [E4]'s meta-analysis, some of the moderating variables concerning choice complexity received weaker support than predicted. The analysis also targets consumer choice in general, and no effect size for the job-search subset specifically could be obtained.

## Separating observation from judgment

The facts readable from a posting (observation) are separated from the matching against the user's conditions (judgment). The role carrying out web search writes the observation, and the skill body that can read the user profile writes the judgment (confidence: not grounded in evidence; this is an operational convention derived from the personal-information boundary).

Separating observation from judgment makes condition judgment possible without passing personal information to a role holding means of outward web transmission. Since the searcher agent holds WebSearch and WebFetch, `profile.json`, `axis.json` and everything under `career-private/` must never be passed to it. For the same reason, thresholds such as an overtime ceiling, an annual-holidays floor, or work-characteristic preferences are never passed either. A threshold is the user's own condition, and it can itself be information that identifies the individual. The salary floor (`salary_min`), already allowed as an anonymised condition, is the one exception.

Implication for the design: `job_search_results.json` has a three-layer structure: observation, judgment, and summary. The searcher agent writes the observation layer (`axis_observations`, `duty_items`, and the rest). The skill body writes the judgment layer (`axis_judgements`, `classification`) and `screening` locally in Step 3.5. This boundary reaches beyond a documented promise. `validate_job_search_results.py`'s PII lint builds "words that must never go outward" from `profile.json` and the axis source (`axis.json`), and mechanically inspects the deliverable's body against them. The canonical source of the PII lint's extraction and detection rules is "PII lint" in `job-search-format.md`, and the canonical vocabulary for the eight axes and duty classification is in `{HUB_SKILL_DIR}/references/screening-axes.md`.

**Evidence that lowers confidence (limitations)**: as the cost of this separation, the searcher agent cannot discard a posting that fails the conditions while it searches, and every judgment moves to a later stage. The ratio of application candidates to postings fetched drops under this design. This design gives priority to guarding the personal-information boundary over search efficiency.

## The absence of a statement is never used as evidence

An axis a posting does not state is set to `stated: false`, and its judgment becomes `unknown`. The absence of a statement is never used as evidence that a condition is met, and never as evidence that it is not met (confidence: not grounded in evidence; an operational convention against filling a missing observation by guesswork).

A posting is a selective document: it contains only the items the lister chose to place in it. A missing statement can mean the condition does not exist, and it can equally mean the condition exists but was left unwritten. Since the posting itself does not show which case applies, its absence is evidence for neither case. This holds especially for `oncall_load` (night and holiday response duty): in operations, maintenance, and infrastructure postings, the duty can exist even when the posting never states it.

Implication for the design: a posting with a high count of `unknown` axes is automatically classified as `needs_more_research` (a needs-further-research candidate). The report attaches the axes that could not be judged, and the means to confirm them (company research or interviewing). The three characteristics `clear_completion`, `solo_completable`, and `short_feedback` cannot be judged from a posting's own text, so they play no part whatsoever in the job-search classification decision. An axis with only a qualitative expression (such as 「残業少なめ」 (light overtime)) is set to `value: null`, with its wording copied into `value_text`, without estimating a number.

**Evidence that lowers confidence (limitations)**: under this rule, a posting with a thinner statement leans further toward `needs_more_research`. The volume of listed information depends on the company's own listing policy, so this classification never represents the quality of the posting itself. The classification represents the sufficiency of the information. Reflect this point in the report.

## Derivation lanes are never traded against the primary set

Derivation lanes toward improving conditions and toward widening scope (`derivation-lanes.md`) are built from additional queries in a track separate from the primary set's twelve. The primary set's query count is never cut down to feed a lane (confidence: not grounded in evidence; this is an operational convention derived from the findings of the two sections above).

What the finding that search volume does not predict employment quality [E1] shows extends only as far as this: increasing volume never raises quality. Whether shifting queries from the primary set to a lane would raise quality falls outside this finding's scope. Cutting the primary set only increases the postings missed within the conditions the user specified. A lane's value lies in confirming whether an application candidate exists in the scope the user did not specify, and in the range of better conditions than specified. That confirmation happens without cutting the primary set's coverage.

Lanes are recorded separately from the primary set for two reasons. First, the deliverable's own structure keeps the primary set's coverage from being traded against a lane. Second, the user can see the yield per lane (`screening.derivations`) and judge which direction held an application candidate.

Implication for the design: lanes are the default in both modes, and none is built when the user says they are unneeded. A derived posting is judged and classified under the same rules as the primary set, and the report places it below the primary set, split by lane. A derived application candidate is never presented as the top candidate when the primary set has zero application candidates (the same implication as in "The cost of always searching for the best").

**Evidence that lowers confidence (limitations)**: no study verifying whether adding a lane improves application outcomes could be identified. The count of lanes (three queries each) and the salary raise are also operational conventions, set without measurement.

## Company information stays at the observation level

`company_profiles` is the observation layer the searcher writes, and it does not include any judgment. Classification is decided solely by the posting's eight-axis judgment, and company information plays no part in it. Company information never substitutes for company research. It passes through neither the eight-topic coverage nor the audit that company research requires, and company research after choosing where to apply is still carried out separately. The purpose of gathering company information at the search stage is letting the user see, at an early stage, whether to advance a `needs_more_research` posting into company research, and whether any negative public information exists about an application candidate's company.

## Research limitations and evidence gaps (this skill's premises)

- All four studies this file cites are US or European samples. No study verifying the relation between search volume and employment quality in Japan's mid-career market could be identified.
- No meta-analysis of maximizing tendency specialised to job search exists. This file connects and uses a finding from the job-search context [E2] with findings from the general-choice context [E3][E4].
- No empirical verification of the satisficing threshold (how many required conditions, where to cut off the search) could be identified. This is the reason this skill leaves the count of required conditions to the user's own declaration.
- Separating observation from judgment, and the rule against using the absence of a statement as evidence, are operational conventions derived from the personal-information boundary and the handling of missing observations.
- The rule keeping derivation lanes in a separate track is also an operational convention. No study measuring, in Japan's mid-career market, the effect of user-side condition bias on job-search outcomes could be identified.

Given these gaps, this skill's design handles its points in two groups. A point with strong evidence (never using search volume as a proxy for outcome, keeping the selection method in the report) is treated as settled. A point with reservations on effect size or scope of application (generalising the cost of maximizing tendency to the mid-career market) is treated with those reservations attached. The judgment material for job search is only what a posting states, and the judgment itself can be overturned by company research or interviewing. Reflect this premise in both the pass/fail gate for recommending an application and in the report.

## Source list

<!-- textlint-disable -->
<!-- This section lists sources in bibliographic form (publisher. author and year. level. DOI. URL). This section alone disables the rule, so the separating periods are never judged as Japanese punctuation. -->

- [E1] Journal of Applied Psychology. van Hooft et al. 2021. Level A (a meta-analysis of 378 independent samples, N=165,933). DOI:10.1037/apl0000675. https://doi.org/10.1037/apl0000675
- [E2] Psychological Science. Iyengar et al. 2006. Level A (a longitudinal study of US new-graduate undergraduates, 11 universities, 548 respondents). DOI:10.1111/j.1467-9280.2006.01677.x. https://doi.org/10.1111/j.1467-9280.2006.01677.x
- [E3] Journal of Personality and Social Psychology. Schwartz et al. 2002. Level A (seven samples, 1,747 people total). DOI:10.1037/0022-3514.83.5.1178. https://doi.org/10.1037/0022-3514.83.5.1178
- [E4] Journal of Consumer Psychology. Belli et al. 2022. Level A (a meta-analysis of 108 papers, 683 effect sizes, 47,245 people after removing duplicates). DOI:10.1002/jcpy.1283. https://doi.org/10.1002/jcpy.1283

<!-- textlint-enable -->
