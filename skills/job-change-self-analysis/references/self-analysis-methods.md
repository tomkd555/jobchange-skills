# Self-analysis methodology (the grounds and limits of the adopted theory)

<!-- textlint-disable jtf-style/4.3.2.大かっこ［］ -->
<!-- The [E1] form in the body is the notation for a source id. This file disables that rule to keep the half-width square brackets. -->

This is the canonical definition setting the empirical grounding and the limits of the analytical axes the job-change-self-analysis skill adopts. SKILL.md's principles, question-bank.md's question design, and the two agents (writer / auditor) all reference this file. Evidence levels are marked on a four-level A-D scale (A = primary or official, B = a reliable secondary source, C = word of mouth or an aggregation site, D = a personal blog, hearsay, or unconfirmed). Academic research carries a DOI. The canonical definition is in `job-change-company-research/references/evidence-grading.md`, and peer-reviewed academic research is included in Level A. The citation format is `[E-number] title (year) level DOI:xxx https://doi.org/xxx`, matched to the "Sources" list at the end.

## The core constraint: introspection alone is unreliable

Self-analysis is never done through introspection alone. This skill's design treats this constraint as central, as the one with the strongest support (confidence: near-certain, above 90%).

- A person can barely grasp a higher-order cognitive process directly through introspection, and a verbal report of a mental process comes from an implicit causal theory [E45]. Introspection is no means of directly knowing an unconscious mental process. The effective routes to greater self-knowledge are self-observation through the eyes of others, and observation of one's own behaviour [E44]. A person readily assumes that their own mental workings are visible to themselves (the introspection illusion) [E51].
- Evaluation by others (an observer's rating) has higher predictive validity than self-evaluation in predicting academic performance and job performance, and holds incremental validity over self-evaluation (a meta-analysis of 263 samples and 44,178 people) [E49]. **This figure comes from one large-scale meta-analysis.**
- Feedback, though, is no cure-all. A feedback intervention raises performance on average (d=.41), and over a third of interventions lower performance. Effectiveness falls the more attention turns from the task to the self (character) [E50]. **This d=.41 comes from one large-scale meta-analysis.**

From this constraint, this skill sets the following as its operating rules.

1. A strength (`strengths`) requires mapping to behavioural evidence (`behavioral_episodes`) or feedback from others (`others_feedback`). A strength grounded in introspection alone is never accepted in the deliverable (the validation script reports it as an ERROR).
2. Feedback from others is taken in with a task-oriented focus. It is recorded as a mapping between an action and a result: "which action led to which result" [E50].
3. A value or an interest reached through introspection is backed up, wherever possible, by mapping it to a past behavioural episode.

## The four adopted analytical axes and their empirical grounding

The analytical axes are set at four: interests, values, the four dimensions of career adaptability, and past behaviour. The frameworks adopted are the ones whose support for validity and effect is relatively strong (confidence: very likely, 80% to under 90%).

### Interests and interest fit (Holland's framework)

- Vocational interest correlates with job performance (r=.14) and training performance (r=.26), and a performance-focused interest scale raises the validity for performance to .23 [E1]. In a meta-analysis integrating 60 studies and about 568 correlations, an interest-environment congruence index predicts performance better than an individual interest score [E2].
- Interest fit, though, relates weakly to "overall job satisfaction." In a meta-analysis spanning 65 years and 105 studies (N=39,602), the correlation stayed at ρ=0.19, and fit relates more strongly to achievement and career satisfaction than to overall job satisfaction [E11].
- Application: interests use the six-domain RIASEC framework (Realistic, Investigative, Artistic, Social, Enterprising, Conventional) as axis names. A high fit is never treated as a guarantee of satisfaction. The result of an interest diagnosis is never a settled judgment, and is combined with the support of introspection and behaviour.

### The four dimensions of career adaptability

- The Japanese-language Career Adapt-Abilities Scale (CAAS-J) showed a high fit for a four-factor, 24-item model targeting young workers, with internal consistency of α=.97 [E8]. **This α=.97 comes from that one study.** It runs somewhat higher than the typical value for versions in other languages (α≈.93), and the reservation stands that it rests on one validity study.
- The four dimensions (concern, control, curiosity, and confidence) form the analytical framework. Only the framework of dimension names is used, and no scale item text is reproduced (a copyrighted scale item is never reproduced as it stands).

### Past behaviour (behavioural evidence)

- A mid-career hiring interview attends to the behavioural process leading to a result (how the person thought and acted in a situation), and judges whether the same behaviour reproduces even when the environment changes [E42]. This is the point where the result of self-analysis (a concrete past behaviour) connects with the STAR/behavioural interview.
- Given the limits of introspection cited above [E44], observing behaviour is a more reliable route to self-knowledge than introspection. This is the ground for placing `behavioral_episodes` as a required element of the deliverable.

### Values

- A value is put into words through introspection. Grounding it in introspection alone, though, has the same limits described above. The operating rule is to back it up by mapping it to a past behavioural episode (`values` maps to an episode with `evidence_episode_ids`).

### A supplementary point: strengths interventions (the well-being side)

- A meta-analysis of signature-strengths interventions (14 papers, 29 effect sizes) found g=0.32 for positive affect, g=0.42 for life satisfaction, and g=0.21 for reduced depression [E12]. **This is a small-to-medium effect on the well-being (subjective well-being) side, and says nothing about job performance.**
- Application: a strength is put into words through self-description, and this skill does not depend on a commercial diagnostic tool (see the limits described below).

## Limited use of frameworks with weak validity

The following frameworks are never used as a diagnosis that gives a settled judgment, and are used only as a prompt (a set of questions) for introspection.

- Schein's career anchors have weak construct validity. Even the Career Orientations Inventory's best-fitting model, built from seven studies' data, fits poorly [E7]. Even among 1,083 employees at large Japanese companies, the conceptual reality of the creativity factor was found to need reconsideration [E6]. The eight categories may be listed as a prompt in question-bank.md, and their result is never treated as a settled "your anchor."
- A commercial strengths tool has limited independent validity. The claim that psychological strengths and interpersonal resources buffer the effect of symptoms on subjective well-being was not confirmed in a meta-analysis of 223 studies and N=127,587 [E10]. **This result comes from one large-scale meta-analysis.** Dependence on a commercial tool such as CliftonStrengths is avoided, and a free self-description substitutes for it. No item text is reproduced as it stands.
- For a RIASEC self-diagnosis tool, a peer-reviewed paper points out that the existing evidence for its effectiveness as a career intervention is dated and geographically limited, and not yet at a stage where a decisive conclusion can be drawn [E23]. RIASEC is used as the framework for interests, and an intervention effect claimed for a diagnostic tool never grounds anything here.
- MBTI and 16Personalities are not used. A format that sorts a person into a four-letter type splits a person near the midpoint in two, so the type itself is unstable. The sources for this reason and how to handle a result the user brings in are in `personality-guide.md`. That file also gives the distinction and terms of use between a framework that may be used for the self-report of personality and a framework whose construct alone is borrowed.
- A Dark Triad scale (Machiavellianism, narcissism, psychopathy) is not used. It is a scale for judging risk in others, and has no constructive use in self-analysis. It can be harmful as a label a person applies to themselves.

## Operating rules for preventing rumination

Excessive introspection is harmful (confidence: very likely, 80% to under 90%).

- Rumination worsens depression, impairs problem-solving, and forfeits support from those around a person. It is distinguished from adaptive self-reflection [E52]. In a longitudinal study of Japanese speakers too, self-rumination predicted an increase in fear while self-reflection predicted a decrease in avoidance behaviour, and the kind of self-focus divides the effect [E54]. Practitioners, too, point out that introspection can become counterproductive once excessive, and that relationships with and observation by those around a person should be weighted [E22].
- People systematically misread a future feeling: they overestimate the intensity and duration of a future emotional reaction (the impact bias, caused by focalism) [E55]. An affective forecast such as "taking this job will make me happy" or "I will regret changing jobs" never grounds a firm conclusion in self-analysis.

Operating rules:

1. Self-analysis is limited to the fixed, structured questions in question-bank.md, and never encourages unlimited introspection.
2. Probing further with "why" never leads to emotional rumination, and always maps to a behaviour or a fact (an episode).
3. An affective forecast never grounds a judgment or a firm conclusion. `emotion_note` is a record of the motivation and feeling at the time, and does not contain a forecast of the future.

## A contested point (both sides stated)

The mechanism behind the Dunning-Kruger effect remains unsettled. The phenomenon of a low performer overestimating themselves (a bottom quartile that measured at the 12th percentile estimated itself at the 62nd) [E46] is confirmed as a figure, and the interpretation that explains its mechanism as "a lack of metacognitive ability" is contested. A counterargument states that the asymmetric error can be explained by regression to the mean and the better-than-average heuristic, and disappears once the two are removed [E47]. A reanalysis using a test suited to individual-difference data, however, finds the effect could be far smaller than previously reported [E48]. **This skill does not assert a settled mechanism for overconfidence in self-evaluation.** This dispute reinforces the operating rule stated above, of never treating a self-evaluation grounded in introspection alone as settled.

## The place of practical methods

Practical methods (Will-Can-Must, the motivation graph, a personal history or a career stock-take, evaluation by others, the Johari window) are useful as a basis for moving the process forward. Most of the claims of their effectiveness, though, are self-reports by staffing-service providers themselves [E14][E17][E19], and the evidence itself for the intervention effect of an interest-diagnosis tool is weak [E23].

Application: a practical method is adopted as a basis for question design and moving the process forward. The user is never led to treat "a diagnostic result" as "the settled self." A result obtained through a method is taken into the deliverable only once backed up by introspection, behaviour, and testimony from others.

## Sources

<!-- textlint-disable -->
<!-- This section lists sources in bibliographic form (publisher. title. year. level. URL). This section alone disables the rule, so the linter does not judge the separating periods and parts of organisation names as Japanese punctuation or as synonyms. -->

- [E1] Journal of Applied Psychology (APA). Are you interested? A meta-analysis of relations between vocational interests and performance/turnover. 2011. Level A. DOI:10.1037/a0024343. https://doi.org/10.1037/a0024343
- [E2] Perspectives on Psychological Science (SAGE/APS). Vocational Interests and Performance: A Quantitative Summary. 2012. Level A. DOI:10.1177/1745691612449021. https://doi.org/10.1177/1745691612449021
- [E6] Soshiki Kagaku (組織科学, Organizational Science; published by the Academic Association for Organizational Science). Verifying the fit of the nine-factor model of career anchors (キャリア・アンカー9因子モデルの適合性の検証). 2024. Level A. DOI:10.11207/soshikikagaku.20240702-4. https://doi.org/10.11207/soshikikagaku.20240702-4
- [E7] Journal of Career Assessment (SAGE). Underlying Factor Structure of Schein's Career Anchor Model. 2013. Level A. DOI:10.1177/1069072712475179. https://doi.org/10.1177/1069072712475179
- [E8] Career Counseling Studies (キャリア・カウンセリング研究, published by the Japanese Society for the Study of Career Counseling). Development of the Japanese-language Career Adapt-Abilities Scale (日本語版キャリア・アダプタビリティ尺度の開発). 2024. Level A. DOI:10.34512/careercounseling.26.1_1. https://doi.org/10.34512/careercounseling.26.1_1
- [E10] Journal of Affective Disorders (Elsevier). Internalising symptoms and wellbeing: Meta-analysis of buffering. 2025. Level A. DOI:10.1016/j.jad.2025.119809. https://doi.org/10.1016/j.jad.2025.119809
- [E11] Journal of Vocational Behavior (Elsevier). Interest fit and job satisfaction: A systematic review and meta-analysis. 2020. Level A. DOI:10.1016/j.jvb.2020.103503. https://doi.org/10.1016/j.jvb.2020.103503
- [E12] Journal of Happiness Studies (Springer). The Impact of Signature Character Strengths Interventions: A Meta-Analysis. 2019. Level A. DOI:10.1007/s10902-018-9990-2. https://doi.org/10.1007/s10902-018-9990-2
- [E14] Recruit (リクルート, Rikunabi NEXT). Eleven self-analysis frameworks and methods, including Will-Can-Must (自己分析のフレームワーク＆手法11種（Will-Can-Must）). 2021-05-28. Level B (a self-report). https://next.rikunabi.com/tenshokuknowhow/archives/25424/
- [E17] Recruit (リクルート, Rikunabi NEXT). A list of eleven self-analysis methods (自己分析手法11種の一覧). 2021-05-28. Level B (a self-report). https://next.rikunabi.com/tenshokuknowhow/archives/25424/
- [E19] Career Consul Study (キャリコンスタディ, LIFE&CAREER LLC). [Career counselling] Support for self-understanding (【キャリコン】自己理解の支援). 2020-09-24. Level C. https://careerconsultant-study.com/jikorikai-support/
- [E22] THE CAREER STORY (Job-Hunting Textbook, 就活の教科書). An interview with Professor Koichiro Komikawa of Hosei University (法政大学 児美川孝一郎教授インタビュー). 2024-08-20. Level C. https://reashu.com/story/professor-interview-komikawa/
- [E23] Frontiers in Organizational Psychology. RIASEC self-assessment tools as career interventions. 2026-04-24. Level A. https://www.frontiersin.org/journals/organizational-psychology/articles/10.3389/forgp.2026.1792707/full
- [E42] Humanage, Inc. (i-note). Interview techniques for identifying candidates who will thrive in mid-career hiring (reproducibility) (中途採用で活躍する人材を見極める面接術（再現性）). 2025-05-30. Level C. https://www.i-note.jp/assessment/tekisei-kensa/articles/028.html
- [E44] Annual Review of Psychology. Self-knowledge: its limits, value, and potential for improvement. 2004. Level A. DOI:10.1146/annurev.psych.55.090902.141954. https://doi.org/10.1146/annurev.psych.55.090902.141954
- [E45] Psychological Review (APA). Telling more than we can know: Verbal reports on mental processes. 1977. Level A. DOI:10.1037/0033-295X.84.3.231. https://doi.org/10.1037/0033-295X.84.3.231
- [E46] Journal of Personality and Social Psychology (APA). Unskilled and unaware of it. 1999. Level A. DOI:10.1037/0022-3514.77.6.1121. https://doi.org/10.1037/0022-3514.77.6.1121
- [E47] Journal of Personality and Social Psychology (APA). Unskilled, unaware, or both? The better-than-average heuristic. 2002. Level A. DOI:10.1037/0022-3514.82.2.180. https://doi.org/10.1037/0022-3514.82.2.180
- [E48] Intelligence (Elsevier). The Dunning-Kruger effect is (mostly) a statistical artefact. 2020. Level A. DOI:10.1016/j.intell.2020.101449. https://doi.org/10.1016/j.intell.2020.101449
- [E49] Psychological Bulletin (APA). An other perspective on personality: Meta-analytic integration of observers' accuracy. 2010. Level A. DOI:10.1037/a0021212. https://doi.org/10.1037/a0021212
- [E50] Psychological Bulletin (APA). The effects of feedback interventions on performance. 1996. Level A. DOI:10.1037/0033-2909.119.2.254. https://doi.org/10.1037/0033-2909.119.2.254
- [E51] Advances in Experimental Social Psychology (Elsevier). The Introspection Illusion. 2009. Level A. DOI:10.1016/s0065-2601(08)00401-2. https://doi.org/10.1016/s0065-2601(08)00401-2
- [E52] Perspectives on Psychological Science. Rethinking Rumination. 2008. Level A. DOI:10.1111/j.1745-6924.2008.00088.x. https://doi.org/10.1111/j.1745-6924.2008.00088.x
- [E54] Japanese Journal of Emotional Psychology (感情心理学研究, published by the Japanese Society of Research on Emotions). The effects of self-rumination and self-reflection on social anxiety (自己反すうと自己内省が社交不安に及ぼす影響). 2017. Level A. DOI:10.4092/jsre.25.1_17. https://doi.org/10.4092/jsre.25.1_17
- [E55] Current Directions in Psychological Science. Affective forecasting: Knowing what to want. 2005. Level A. DOI:10.1111/j.0963-7214.2005.00355.x. https://doi.org/10.1111/j.0963-7214.2005.00355.x

<!-- textlint-enable -->
