# Guide to quantifying an achievement (patterns, alternative phrasing, and limits)

<!-- textlint-disable jtf-style/4.3.2.大かっこ［］ -->
<!-- The [E1]-style notation in this text is the citation-id notation. This file disables the rule so the half-width square brackets are kept. -->

This is the canonical definition referenced when eliciting, writing, and auditing an achievement in
job-change-profile's `achievements` section. SKILL.md's Principle 3, `sections/achievements.md`, and both agents
reference this file. Evidence level is written on a 4-step scale, and a piece of academic research carries a DOI.

## Recommend quantification, without mechanically forcing a number

Quantifying an achievement is strongly recommended in practice. A figure's relevance to the requirement matters
more than its mere quantity, and attaching a number to every achievement mechanically can backfire (confidence:
likely, 65%-80%).

- A recruiting agency recommends expressing an achievement in a quantitative figure, shown against the prior year
  and the like [E25].
- Academically, adding competency statements (a description of ability or achievement) to an application document
  raises its evaluation and the probability of passing document screening. This effect, however, does not depend
  on where the statement sits; it "arises even from ordinary phrasing" [E34]. **A large part of this effect comes
  from the statement's mere presence.**
- An excessive or inaccurate figure backfires. Attaching a number mechanically to every bullet point, and a figure
  that departs from fact, invite the hiring side's distrust. An article written from the hiring side's viewpoint
  notes that a single inaccurate figure damages the credibility of the whole document [E29].

Operation: write to `metric` the figure the user states, as it stands. Elicitation never asks for an explanation
of its source, and never manufactures a figure itself. When no figure is available for an achievement, it is never
forced into a number; `metric` is set to `null`, and the point worked on and the point evaluated are made concrete
in `description`. The danger E29 names lies mainly in elicitation itself inflating a figure while trying to fit it
into a quantification pattern.

## Patterns for quantification

The patterns for expressing an achievement as a figure are as follows. During elicitation, proceed by checking
together with the user which pattern applies.

| Pattern | How to show it |
|---|---|
| Year-on-year change, a rate of change | Show a change in sales, cost, or workload as a proportion (for example, 「前年度比で処理件数を1.4倍」, processing count up 1.4× year on year) [E25]. |
| A count or a scale | Show an absolute quantity such as the number of projects or clients handled, the data volume, or the system's scale [E28]. |
| Frequency | Show the frequency or the number of times a routine task was carried out [E28]. |
| The number of people or the scope handled | Show the number of people managed or negotiated with, or the department or region handled [E28]. |
| A reduction rate or an efficiency gain | For operations and maintenance or routine work, show a process reduction rate, a processing-time cut, or a reduction in errors [E32][E26]. |
| Linking a qualitative outcome | For an outcome that resists quantification, show it linked to a later quantitative outcome (an order won, a renewed contract) [E32]. |
| A comparison against a benchmark | Show it against the prior year, the prior period, or a team's or department's average (for example, 「達成率80%から90%へ」, achievement rate up from 80% to 90%; 「チーム平均95%に対して98%」, 98% against a team average of 95%) [E38]. |
| An approximation from an activity volume | When no record is on hand, have the user approximate it from an activity volume they recall (a daily call count × days worked, a weekly visit count × weeks) [E39]. Elicitation notes that it is an approximation and records the value in the user's own words. |

## Alternative phrasing for a hard-to-quantify task

For work in an indirect department, routine work, or operations and maintenance, where a direct figure is hard to
produce, use the following alternative phrasing (confidence: likely, 65%-80%).

- Even routine work can be expressed through a point worked on, a reduction in errors, or an efficiency gain [E26].
  When quantification is difficult, writing the point worked on and the point evaluated concretely is enough [E27].
- Operations and maintenance can be shown through a process reduction rate, the system's scale, and a qualitative
  outcome linked to an order won [E32].
- Even work that resists a direct figure can be quantified through frequency, scope, the number of people handled,
  or an approximate range [E28].

Operation: even when using alternative phrasing, a word denoting scale, scope, or the acting subject (大規模
[large-scale], 全社 [company-wide], 主導 [led], and the like) is never used beyond the range the elicitation notes
support. An exaggeration
without support becomes a target for the auditor's finding.

## The limits of quantification's effect (an evidence gap)

- No peer-reviewed field experiment isolating and measuring the effect of quantification itself has been confirmed,
  in any language (an evidence gap). Many of the claimed effect sizes rest on a staffing provider's own
  self-reported figures. A statement's mere presence is shown to raise evaluation [E34], but no monotonic
  relationship — "the more figures, the higher the evaluation" — has been demonstrated.
- The persuasive effect of a figure or a specific detail depends on context. In a probability statement, whether a
  figure or a word raises trust more depends on the context [E37]. A figure that is too fine-grained can itself
  invite suspicion [E36].

## Dependency on occupation

The weight an achievement figure carries depends on the occupation (confidence: very likely, 80%-90%).

- For an IT role, the item weighed most heavily in an application document was "skills and usable tools" (48.4% in a
  survey of 150 hiring staff) [E2][E31]. **This figure comes from a single survey.**

Operation: for some occupations, a clear skill inventory (Step 3) settles a hiring outcome more than quantifying
achievements does, so elicitation adjusts its emphasis to suit the occupation.

## Sources

<!-- textlint-disable -->
<!-- This section lists sources in a bibliographic format (publisher. Title. Year. Level. URL). This section alone disables the rule so the separating periods and part of a company name are not judged as Japanese punctuation or a synonym. -->

- [E2] Geekly（ギークリー）. 【採用担当150名に聞いた】応募書類で重視するポイントとは？. 2021-12. Level C (single source, self-reported). https://www.geekly.co.jp/column/cat-jobsearch/resume_point_byrecruiter/
- [E25] JAC Recruitment. 職務経歴書「実績」の書き方とは？職種別の記入例も解説. 2022-11-25. Level C. https://www.jac-recruitment.jp/market/knowhow/resume/achievements/
- [E26] JAC Recruitment. 職務経歴書「実績」の書き方とは？職種別の記入例も解説. 2022-11-25. Level C. https://www.jac-recruitment.jp/market/knowhow/resume/achievements/
- [E27] エン・ジャパン（エン転職）. 転職Q&A「【職務経歴書】数字で示せる実績がない。何を書けば良い？」. 2023. Level C. https://employment.en-japan.com/qa_1199_2040/
- [E28] The Muse. How to Quantify Your Resume Bullets (When You Don't Work With Numbers). 2020-06-19. Level C. https://www.themuse.com/advice/how-to-quantify-your-resume-bullets-when-you-dont-work-with-numbers
- [E29] The Resume Writers (AU). The Metric Mirage: How Overusing Resume Numbers Is Undermining Their Impact. 2025-08-28. Level C. https://theresumewriters.com.au/the-metric-mirage-how-overusing-resume-numbers-is-undermining-their-impact/
- [E31] Geekly（ギークリー）. 【採用担当150名に聞いた】応募書類で重視するポイントとは？. 2021-12. Level C (single source, self-reported). https://www.geekly.co.jp/column/cat-jobsearch/resume_point_byrecruiter/
- [E32] type転職エージェント. インフラエンジニアの職務経歴書｜職務経歴書の書き方. 2023. Level C. https://type.career-agent.jp/knowhow/documents/keirekisho/network.html
- [E34] International Journal of Selection and Assessment. The Impact of Competency Statements on Resumes for Short-listing Decisions. 2000. Level A. DOI:10.1111/1468-2389.00132. https://doi.org/10.1111/1468-2389.00132
- [E36] Strategic Management Journal. Give it to us straight (most of the time). 2018. Level A. DOI:10.1002/smj.2733. https://doi.org/10.1002/smj.2733
- [E37] Judgment and Decision Making. Cultivating credibility with probability words and numbers. 2019. Level A. DOI:10.1017/S1930297500005404. https://doi.org/10.1017/S1930297500005404
- [E38] リクルートダイレクトスカウト. 職務経歴書での実績の書き方とは？効果的なアピール方法を紹介. 2025. Level C. https://directscout.recruit.co.jp/contents/article/3627/
- [E39] jobree（履歴書・職務経歴書の書き方）. 職務経歴書の営業実績が覚えてない｜採用担当者が教える書き方と例文. 2025. Level C. https://rirekisho.jobree.co.jp/how/職務経歴書-営業-実績-覚えてない/

<!-- textlint-enable -->
