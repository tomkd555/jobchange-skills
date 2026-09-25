# Profile design methodology (grounding and limits)

<!-- textlint-disable jtf-style/4.3.2.大かっこ［］ -->
<!-- The [E1]-style notation in this text is the citation-id notation. This file disables the rule so the half-width square brackets are kept. -->

This is the canonical definition of the grounding and limits behind job-change-profile's design decisions.
SKILL.md's principles and both agents' (writer / auditor) audit perspectives reference this file. Evidence level is
written on a 4-step scale, A through D (A = primary/official, B = a reliable secondary source, C = word-of-mouth or
an aggregator site, D = a personal blog, hearsay, or unconfirmed), and a piece of academic research carries a DOI.
The canonical definition lives in `job-change-company-research/references/evidence-grading.md`, and a peer-reviewed
academic study falls under Level A.

## What the hiring side looks at in document screening

The core of what the hiring side evaluates in document screening for mid-career hiring is the content of career
history, achievements, and skills, and how that content maps to job requirements (relevance). A document's
readability and freedom from typos also weigh on whether it passes (confidence: very likely, 80%-90%).

- A survey of Japanese hiring staff names career history and job content as the item most heavily weighed (43.4% in
  a doda survey) [E1]. For IT roles alone, "skills and usable tools" is weighed most heavily (48.4%); the item
  weighed most heavily depends on the occupation [E2]. **Each of these two figures comes from a single survey.**
- Academically, person-job and person-organization fit correlate broadly with pre-hire outcomes such as hiring
  intent and an offer (a meta-analysis of 172 studies) [E13]. How a résumé's attributes are read depends on the
  target job [E12]. Eye-tracking shows that attention paid to the Experience section predicts a pass decision
  [E15].

Implication for the design: profile.json holds career history, achievements, and quantified values at the job
level, at a granularity that lets the application-documents sub-skill reconstruct relevance for each application.
Because relevance itself changes with each application, it is never held fixed in profile.json — this avoids an
old mapping lingering in the data.

**Evidence that lowers confidence (a limit)**: the sheer "volume" of a career history predicts an outcome very
little on its own. The corrected correlation between pre-hire work experience's amount, duration, and type and job
performance stays at .06 [E14]. Writing a career history in detail does not by itself guarantee a favorable
evaluation.

## Skill classification

The rough division into "technical / business / language / certification" exists in practice. Public
classification systems, by contrast, separate specialized skills from transferable skills and treat
transferability as a continuous degree that depends on context. A skill inventory does not function from simply
applying a generic taxonomy as it stands (confidence: very likely, 80%-90%).

- O*NET divides skills into basic skills and cross-functional (transferable) skills, and attaches an operational
  definition to each item [E40].
- Japan's Ministry of Health, Labour and Welfare (MHLW) officially defines portable skills as "skills in carrying
  out work that can be carried from one industry or occupation to another," made up of 9 elements: 5 in how one
  approaches tasks (対課題) and 4 in how one relates to people (対人) [E44].
- ESCO (European Skills, Competences, Qualifications and Occupations) classifies a skill's reusability into 4
  stages — transversal, cross-sectoral, sector-specific, and occupation-specific. ESCO also states explicitly that
  an abstract, cross-cutting skill becomes usable only once placed in an occupation's context [E47].

Implication for the design: profile.json takes technical / business / languages / certifications as its entry
point, and holds the 9 elements of portable skills (対課題 (task-facing) and 対人 (people-facing)) as a secondary classification
(`skills.portable`). These two layers give a structure that separates specialized skills from transferable skills
in the inventory. Mapping to a requirement is done by the application-documents sub-skill at application time.

**Evidence that lowers confidence (a limit)**: transferability is context-dependent and dynamic, and an
occupation-specific model is recommended over a generic one [E53]. No quantitative causal evidence
could be identified showing that a skill-classification framework predicts success at inventory-taking or at
changing jobs (an evidence gap).

## The grounding and limits of must/want

Separating must from want carries the same structure as the requirements-engineering practice MoSCoW, and is a
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

## The real picture of ATS and support for hiring abroad

A profile is enough once it holds job-level data that maps to standard headings, and the items an English résumé
needs (excluding gender, age, and photo). Excessive keyword optimization is unnecessary. The premise that "an ATS
(applicant tracking system) auto-rejects in bulk" is a myth (confidence: likely, 65%-80%).

- A leading ATS extracts name, contact information, a summary, each job's title/company/period/achievements,
  education, and a skills list as structured fields [E72]. Mapping to standard headings is the requirement for
  letting an ATS read the document [E73].
- An English résumé consolidates the Japanese rirekisho (résumé form) and shokumu-keirekisho (career history
  document) and lists them in reverse chronological order [E84]. It never states gender, age, date of birth, photo,
  or salary [E85]. An achievement is shown as action verb + figure + result [E86].

Implication for the design: the current career_history unit (each job's company, period, role, and achievements)
can be mapped to standard headings. profile.json holds no field for name, age, gender, or photo (these are items an
English résumé never states, and this also agrees with the policy of holding a minimum of personal information). No
ATS-keyword field or keyword-optimization field is provided.

**Evidence that lowers confidence (a limit; refuting a myth)**: the statistic "75% are auto-rejected by an ATS"
traces to 2012 corporate marketing with no supporting basis [E77]. A survey of 25 recruiters found 92% said their
own company's ATS does not auto-reject by format or content [E79]. Keyword stuffing is detected and penalized by a
modern ATS. **The decision not to provide a keyword-optimization field therefore rests on refuting the myth.**
That said, the effect size of structuring and organizing a document has no grounding beyond vendor claims, and
controlled studies remain scarce [E79].

## The consequences of falsifying a career history

Managing accuracy, comprehensiveness, and currency prevents the typical failure. The consequences of falsifying a
career history vary with severity, relevance to the job, and time elapsed. A falsehood, however, is exposed with
high probability in practice, and the consequences are severe (confidence: likely, 65%-80%).

- In Japan, for a disciplinary dismissal on grounds of falsifying a career history to hold, both requirements must
  be met: that the company would not have hired the person had it known beforehand, and that the dismissal has
  objective reasonableness [E92]. Court cases exist where a dismissal was held invalid on grounds such as no
  disruption to the work, an old criminal record, or a minor falsehood — not every falsehood is fatal [E94]. A
  falsehood that amounts to document forgery, fraud for financial gain, or falsifying a qualification is subject to
  criminal punishment [E101]. A falsehood is exposed by objective facts through cross-checking against social
  insurance, withholding tax, and a reference check [E102].
- A U.S. survey found that among people hired on a false statement, 41% had their offer withdrawn and 18% were
  dismissed; only 29% faced no consequence at all [E97].

Implication for the design: profile.json is created from facts in the elicitation notes alone. An achievement
figure, a period, or a job title is never filled in by inference (SKILL.md Principle 6). A gap in employment is
never hidden; it is recorded in `career_gaps` so it can be explained. A falsehood is held in check by elicitation
itself never manufacturing a fact (`elicitation-guide.md`).

## Disputed figures (both sides stated)

The following two figures are never used alone to assert a fact, because they come from different populations or
because conflicting surveys exist.

- **A 37.3% pass rate for document screening** [E7]: Mynavi states the pass rate for document screening in
  mid-career hiring as 37.3%, but this figure is limited to people who succeeded in changing jobs, and it conflicts
  with the general figure from independent outlets (20%-30%). As a representative figure for the pass rate in
  general, this is disputed.
- **An 81.4% detection rate for career-history falsification** [E95]: StandOutCV states that 81.4% is detected,
  while another survey states that about 79% goes undetected — the level is disputed. No settled representative
  figure for the detection rate exists.

## Limits of the research and evidence gaps (this skill's premises)

- No peer-reviewed field experiment isolating the effect of quantification alone has been obtained (see
  `quantification-guide.md`).
- No level-A or level-B empirical study verifying the effect of a must/want split and a decision matrix has been
  obtained.
- For Japanese mid-career hiring, a Level-A (MHLW survey) primary-source figure for the most-weighed items could not
  be obtained from that survey's own text; this skill relies instead on doda's and Geekly's Level-B/C surveys
  (single-source).
- The effect size of an employment gap on a selection outcome could not be obtained from the source text (see
  `elicitation-guide.md`).

Given these gaps, this skill's design treats as settled "the core backed by strong evidence" — structured
elicitation, elicitation itself never manufacturing a fact (the separation of writer and auditor), avoiding the
typical failures, and separating specialized skills from transferable skills. It treats "a point whose effect size
is small" — the effect of quantification itself, and improved decision-making from a must/want split — with a
reservation attached.

## Sources

<!-- textlint-disable -->
<!-- This section lists sources in a bibliographic format (publisher. Title. Year. Level. URL). This section alone disables the rule so the separating periods and part of a company name are not judged as Japanese punctuation or a synonym. -->

- [E1] doda（パーソルキャリア）. 中途採用の履歴書・職務経歴書で一番見られているのはどこ？. 2024. Level B (single source). https://doda.jp/guide/saiyo/007.html
- [E2] Geekly（ギークリー）. 【採用担当150名に聞いた】応募書類で重視するポイントとは？. 2021-12. Level C (single source, self-reported). https://www.geekly.co.jp/column/cat-jobsearch/resume_point_byrecruiter/
- [E7] マイナビ（マイナビ転職）. 書類選考とは？通過率は？突破する履歴書・職務経歴書の書き方を解説. 2025. Level B (disputed). https://tenshoku.mynavi.jp/knowhow/caripedia/276/
- [E12] Journal of Applied Psychology. Biodata phenomenology: Recruiters' perceptions and use of biographical information in resume screening. 1994. Level A. DOI:10.1037/0021-9010.79.6.897. https://doi.org/10.1037/0021-9010.79.6.897
- [E13] Personnel Psychology. Consequences of Individuals' Fit at Work: A Meta-Analysis. 2005. Level A. DOI:10.1111/j.1744-6570.2005.00672.x. https://doi.org/10.1111/j.1744-6570.2005.00672.x
- [E14] Personnel Psychology. A meta-analysis of the criterion-related validity of prehire work experience. 2019. Level A. DOI:10.1111/peps.12335. https://doi.org/10.1111/peps.12335
- [E15] Machine Learning and Knowledge Extraction (MDPI). Using Machine Learning with Eye-Tracking Data to Predict if a Recruiter Will Approve a Resume. 2023. Level A. DOI:10.3390/make5030038. https://doi.org/10.3390/make5030038
- [E40] O*NET Resource Center (U.S. Department of Labor). The O*NET Content Model. 2025. Level A. https://www.onetcenter.org/content.html
- [E44] 厚生労働省. ポータブルスキル見える化ツール（職業能力診断ツール）. 2021. Level A. https://www.mhlw.go.jp/stf/newpage_23112.html
- [E47] European Commission (ESCO). Skill contextualisation — ESCOpedia. 2025. Level A. https://esco.ec.europa.eu/en/about-esco/escopedia/escopedia/skill-contextualisation
- [E53] Workitect. The One-Size-Fits-All Competency Model. 2023. Level C. https://workitect.com/the-one-size-fits-all-competency-model/
- [E54] リクルートエージェント. 転職の軸とは？転職の軸の作り方や譲れない条件一覧. 2023-12-22. Level C. https://www.r-agent.com/guide/start/21312/
- [E55] JAC Recruitment. 転職先の選び方｜キャリアを実現する業界・企業選びのポイントと具体例. 2024-12-02. Level C. https://www.jac-recruitment.jp/market/knowhow/preparation/points-to-select/
- [E56] Saylor Academy (open textbook). Personal Decision Criteria When Considering Possible Job Targets. 2020. Level B. https://saylordotorg.github.io/text_six-steps-to-job-search-success/s07-03-personal-decision-criteria-whe.html
- [E60] ProductPlan. MoSCoW Prioritization | Glossary. 2024. Level B. https://www.productplan.com/glossary/moscow-prioritization/
- [E61] ProductPlan. MoSCoW Prioritization | Glossary. 2024. Level B. https://www.productplan.com/glossary/moscow-prioritization/
- [E66] Vero Recruitment. Shifting Priorities. 2024. Level C. https://verorecruitment.com/blog/shifting-priorities-career-advancement-tips
- [E69] Journal of Consumer Research. Can There Ever Be Too Many Options? A Meta-Analytic Review of Choice Overload. 2010. Level A. DOI:10.1086/651235. https://doi.org/10.1086/651235
- [E71] American Psychologist. The construction of preference. 1995. Level A. DOI:10.1037/0003-066x.50.5.364. https://doi.org/10.1037/0003-066x.50.5.364
- [E72] Resume Optimizer Pro. How Resume Parsers Actually Work: Inside Workday, Greenhouse, Lever, iCIMS, Taleo. 2026-04-22. Level C. https://resumeoptimizerpro.com/blog/how-resume-parsers-actually-work
- [E73] Resume Optimizer Pro. How Resume Parsers Actually Work. 2026-04-22. Level C. https://resumeoptimizerpro.com/blog/how-resume-parsers-actually-work
- [E77] UnchartedCareer. The '75% of resumes are auto-rejected' myth, traced to its source. 2026-07-04. Level C. https://unchartedcareer.com/blog/the-75-of-resumes-are-auto-rejected-myth-traced-to-its-source
- [E79] Enhancv. Does the ATS Reject Your Resume? 25 Recruiters Explain What Really Happens. 2025-11-03. Level C (single source, vendor survey). https://enhancv.com/blog/does-ats-reject-resumes/
- [E84] エンワールド・ジャパン. 英文レジュメの書き方ガイド. 2019-03-18. Level C. https://www.enworld.com/candidates/career-advices/foreign-job-change/resume/how-to-write-english-resume.html
- [E85] エンワールド・ジャパン. 英文レジュメの書き方ガイド. 2019-03-18. Level C. https://www.enworld.com/candidates/career-advices/foreign-job-change/resume/how-to-write-english-resume.html
- [E86] エンワールド・ジャパン. 英文レジュメの書き方ガイド. 2019-03-18. Level C. https://www.enworld.com/candidates/career-advices/foreign-job-change/resume/how-to-write-english-resume.html
- [E92] 咲くやこの花法律事務所. 経歴詐称を理由に懲戒解雇できる？注意点や対応方法を裁判例付きで解説. 2022-12. Level B. https://kigyobengo.com/media/useful/2984.html
- [E94] 咲くやこの花法律事務所. 経歴詐称を理由に懲戒解雇できる？. 2022-12. Level B. https://kigyobengo.com/media/useful/2984.html
- [E95] StandOutCV. How many people lie on their resume to get a job? [Study]. 2023-12. Level B (disputed). https://standout-cv.com/usa/stats-usa/study-fake-job-references-resume-lies
- [E97] ResumeBuilder.com. 1 in 3 Americans admit to lying on resume. 2021-07-16. Level B. https://www.resumebuilder.com/1-in-3-americans-admit-to-lying-on-resume/
- [E101] ベンナビ刑事事件（アシロ）. 経歴詐称とは｜成立要件と問われる罪. 2025. Level C. https://keiji-pro.com/columns/213/
- [E102] ASHIATO（エン・ジャパン）. バックグラウンドチェックで経歴詐称や転職活動はバレない？. 2024-09-19. Level C. https://ashiatohr.com/news/7ecucee-k

<!-- textlint-enable -->
