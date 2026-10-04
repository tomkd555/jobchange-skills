# Axis design methodology (grounding and limits)

<!-- textlint-disable jtf-style/4.3.2.大かっこ［］ -->
<!-- The [E54]-style notation in this text is the citation-id notation. This file disables the rule so the half-width square brackets are kept. -->

This is the canonical definition of the grounding and limits behind job-change-axis's design decisions. SKILL.md's
principles and both agents' (writer / auditor) audit perspectives reference this file. Evidence level is written on
a 4-step scale, A through D (A = primary/official, B = a reliable secondary source, C = word-of-mouth or an
aggregator site, D = a personal blog, hearsay, or unconfirmed). A piece of academic research has a DOI. The
canonical definition is in `job-change-company-research/references/evidence-grading.md`, and a peer-reviewed
academic study falls under Level A. The citation IDs keep the numbers they had in `job-change-profile`'s
`references/profile-methods.md`, so an ID means the same source in both files.

## The grounding and limits of must/want

Separating must from want has the same structure as the requirements-engineering practice MoSCoW, and is a
practical standard. Separating the two alone, however, does not by itself improve a decision. It is reasonable to
keep must-have conditions to a small number while treating them as open to reassessment (confidence: likely,
65%-80%).

- A major Japanese agency presents dividing desired conditions into MUST/WANT and prioritizing them as how to build
  a job-change axis [E54], and holds narrowing the axes to about 3 as the ideal [E55]. A job-search textbook also
  narrows must-haves to a small number [E56]. Requirements engineering's MoSCoW (Must/Should/Could/Won't) carries
  the same structure [E60].

Implication for the design: `job_change_axis` keeps the separation between conditions that cannot be given up and
conditions that are merely desirable, while narrowing must-have conditions to about 3 items and keeping a ranking
and a reassessment time in `priority_note`. This holds back an arbitrary bias toward MUST and a fixed set of axes.

**Evidence that lowers confidence (a limit)**: MoSCoW lacks an objective method for ranking requirements against
each other, and which item becomes MUST is left to subjective judgment [E61]. A meta-analysis of choice overload
found the average effect size for the benefit of narrowing choices close to zero [E69]. A preference is constructed
over the course of elicitation and shifts over time [E71][E66]. No level-A or level-B empirical study verifying the
effect of a must/want split or a decision matrix has been obtained (an evidence gap).

Because of this gap, this skill treats improved decision-making from a must/want split as a point whose effect size
is small, and holds narrowing to about 3 items as a practice with a reservation attached.

## Sources

<!-- textlint-disable -->
<!-- This section lists sources in a bibliographic format (publisher. Title. Year. Level. URL). This section alone disables the rule so the separating periods and part of a company name are not judged as Japanese punctuation or a synonym. -->

- [E54] リクルートエージェント. 転職の軸とは？転職の軸の作り方や譲れない条件一覧. 2023-12-22. Level C. https://www.r-agent.com/guide/start/21312/
- [E55] JAC Recruitment. 転職先の選び方｜キャリアを実現する業界・企業選びのポイントと具体例. 2024-12-02. Level C. https://www.jac-recruitment.jp/market/knowhow/preparation/points-to-select/
- [E56] Saylor Academy (open textbook). Personal Decision Criteria When Considering Possible Job Targets. 2020. Level B. https://saylordotorg.github.io/text_six-steps-to-job-search-success/s07-03-personal-decision-criteria-whe.html
- [E60] ProductPlan. MoSCoW Prioritization | Glossary. 2024. Level B. https://www.productplan.com/glossary/moscow-prioritization/
- [E61] ProductPlan. MoSCoW Prioritization | Glossary. 2024. Level B. https://www.productplan.com/glossary/moscow-prioritization/
- [E66] Vero Recruitment. Shifting Priorities. 2024. Level C. https://verorecruitment.com/blog/shifting-priorities-career-advancement-tips
- [E69] Journal of Consumer Research. Can There Ever Be Too Many Options? A Meta-Analytic Review of Choice Overload. 2010. Level A. DOI:10.1086/651235. https://doi.org/10.1086/651235
- [E71] American Psychologist. The construction of preference. 1995. Level A. DOI:10.1037/0003-066x.50.5.364. https://doi.org/10.1037/0003-066x.50.5.364

<!-- textlint-enable -->
