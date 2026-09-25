# Fit-assessment methodology (grounds and limits)

<!-- textlint-disable jtf-style/4.3.2.大かっこ［］ -->
<!-- The [E1]-style notation in this document is the citation-id notation. To keep the half-width square brackets, this rule is disabled for this file. -->

This is the canonical definition of the grounds and limits behind the judgement design of the job-change-fit-assessment skill. The scoring of the seven dimensions (experience_proximity / aspiration_alignment / work_character_fit / condition_fit / culture_fit / compensation_fit / time_fit), the one-to-one judgement of must-have conditions, and how the overall verdict is decided are themselves defined by `references/fit-criteria.md`. This file presents the findings behind those judgement criteria, and separates what is supported by evidence from what is an operational convention. The agent (fit-assessor) consults it as grounds when writing the verdict and `overall.open_questions`.

The scope is employment within Japan. The grounds for judgement place priority on evidence sampled from Japanese workers. A finding based on Western samples alone serves only as material for designing confirmation items or for a caveat until its validity in Japan is confirmed. Evidence levels are shown in four grades, A through D (A = primary/official, B = reliable secondary, C = word-of-mouth/aggregate sites, D = personal blog/hearsay/unconfirmed), and academic research carries its DOI. The canonical definition lives in `job-change-company-research/references/evidence-grading.md`, and peer-reviewed academic research is included in Level A.

## Why manager fit is not turned into a score

Fit with the direct manager is an independent factor shaping retention and satisfaction for Japanese workers. At the same time, it cannot be judged from the job posting and company research. It is therefore handled as a confirmation item, outside all seven dimensions' scores (confidence: likely, 65% or more but less than 80%).

- A comparison of Japanese and US employee samples found that the path from manager fit to affective organisational commitment runs both directly and indirectly (via organisation fit) in Japan, while in the US it runs only indirectly. That link was stronger in Japan than in the US[E1].
- A Japan–Korea comparison (138 Japanese, 144 Korean) found a significant three-way interaction of organisation fit and leader–member exchange on both job satisfaction and organisational commitment; the complementary effect of the two was pronounced in Japan and was not found in Korea[E2].
- A covariance structure analysis of 400 Japanese non-manufacturing white-collar workers found that leader–member exchange fully mediated the relationship between interactional justice and turnover intention, and that only leader–member exchange related directly to turnover intention[E3].
- A Japanese-language scale of manager support, targeting 1,946 Japanese workers, shows the expected correlations with work engagement, affective organisational commitment, and turnover intention[E4].

Implication for the design: fit with the direct manager is not made an eighth dimension, and is not included in `culture_fit`'s score either. This skill takes the same structure `fit-criteria.md` uses for the three work characteristics that cannot be judged from the job posting, and raises how the direct manager is involved as a required confirmation item in `overall.open_questions`, feeding it into material for a reverse question at interview. It carries no score because the job posting and company research hold no material for it, and attaching a number would be a guess.

**Evidence lowering confidence (limits)**: no study using a Japanese sample with fit with the assigned team as an independent variable has been identified (an evidence gap). This text covers manager fit only. An international meta-analysis reporting that the effect of relational fit is stronger in East Asia than in North America[E5] is not used as grounds for Japan, since whether the East Asian sample it covers includes Japan could not be confirmed in the original text.

## Why the current job is placed as a comparison point

Measuring the target's fit alone is not enough material for the application decision. Staying at the current job is also a choice under comparison (confidence: very likely, 80% or more but less than 90%).

- A meta-analysis of the determinants of voluntary turnover estimates the corrected correlation for perceived alternative employment at ρ=.23 (k=79, N=58,512), positioning perceived alternative employment as an important determinant of turnover[E6]. This revises the earlier meta-analysis's ρ=.12[E7] upward, on a sample roughly four times as large.
- A meta-analysis of 65 independent samples, N=42,907, shows that organisational and community embeddedness relate negatively to turnover intention and actual turnover even after controlling for job satisfaction, affective commitment, and alternatives[E8]. The factors that keep someone at their current job operate independently of dissatisfaction and alternatives.

Looking at the situation in Japan, a job change does not necessarily improve pay. In the Reiwa 6 (2024) Survey on Employment Trends, the share of job changers whose wages increased over their previous job was 40.5%, the share whose wages decreased was 29.4%, and the share unchanged was 28.4%. Within the increase, 29.4% were a rise of 10% or more and 11.2% a rise under 10%; within the decrease, 21.7% were a fall of 10% or more and 7.6% a fall under 10%[E9]. In the Reiwa 2 (2020) Survey on Job Changers, the satisfaction index for overall working life at the current employer (satisfied minus dissatisfied) is 42.0 points, while the equivalent index for the change in wages is positive for ages 20 through 49 and negative for ages 19 and under and 50 and over — the sign flips with age[E10]. A tendency has also been reported for a smaller task distance — the change in job content across the move — to hold down the post-change drop in income[E11].

Implication for the design: `calculate_time_analysis.py` also runs for the current job, and the target's `time_analysis.json` carries in `comparison` the current job's committed time and effective hourly wage and the difference from it. The `time_fit` and `compensation_fit` verdicts are written on the difference from the current job. The current job's working hours and commute time are taken as user input, using the same lane as `commute.json`.

**Evidence lowering confidence (limits)**: the turnover meta-analyses are centred on English-language settings. The Japanese statistics are cross-sectional surveys; each captures different individuals at a single point in time before and after a job change. The Reiwa 2 Survey on Job Changers' figures could not be confirmed against the primary source's body text, since the summary PDF's text could not be extracted, and rest on a reprinted press-release article.

## Why commute is not treated as a linear time cost

Adding commute time to the committed time alone is not enough. That long commutes cut into sleep and exercise, and relate to physical-health indicators, has been repeatedly observed in Japanese samples. This burden does not necessarily offset against a difference in salary (confidence: likely, 65% or more but less than 80%).

- A nationwide survey of 11,390 Japanese public elementary- and middle-school teachers found long working hours, a long commute, and the urbanity of the school significantly related to insomnia[E12].
- A study of 146 school teachers in Tokyo found that, with an average commute of 42.1 minutes (SD 22.5), a long commute significantly related to less exercise (`p<0.001`) and shorter sleep (`p=0.001`)[E13].
- Among 4,854 people undergoing a comprehensive health checkup, a commute of 60 minutes or more independently correlated positively with body mass index after adjusting for other lifestyle factors[E14].
- An in-vehicle experiment on major commuter lines in the Tokyo metropolitan area quantified commute stress from heart-rate variability, showing the load's trajectory differs between rapid and local services[E15].
- Aversion to a longer commute is reported to be stronger than aversion to longer working hours, pronounced among women and non-regular employees, and a wage premium for a long commute is reported to exist. This is treated as a report from a public research institute that has not undergone peer review[E16].

As international grounds, there is a panel-data test of the equilibrium hypothesis that commute burden is compensated for in the labour market or the housing market, and subjective well-being is systematically lower for people with a longer commute[E17]. A UK panel study also shows that commute time worsens women's psychological health even after controlling for income, job satisfaction, and housing quality, with no equivalent effect for men[E19].

Implication for the design: the `time_fit` judgement criteria carry a note that a long commute does not necessarily offset against a difference in salary. Since the Japanese grounds concentrate on sleep, exercise, and physical-health indicators, the note takes the form "a long commute cuts into sleep and exercise," and does not include a direct assertion about subjective well-being. `commute.json` carries the number of transfers and the degree of crowding as optional items, so that commute burden is not represented by time alone.

**Evidence lowering confidence (limits)**: the widely circulated figure that "compensating for a one-hour one-way commute needs roughly a 40% increase in income" does not exist in the published journal version[E17]. What the published version reports is about EUR 470 per month for a 22-minute one-way commute (35.4% of average monthly labour income); the authors themselves state they do not commit to a specific figure. The 40% figure exists only in footnote 14 on page 17 of the 2004 working-paper version[E18], and has been replaced and dropped in the published version. Cite it with this history attached when using it. No peer-reviewed Japanese paper treating commute time as the independent variable and subjective well-being or life satisfaction as the dependent variable has been identified, other than the one already cited in existing references (Kitagawa et al., 2011) (an evidence gap). In the study of 146 teachers in Tokyo[E13], a direct relationship between commute time and a mental-stress indicator was not reported as significant. A review also exists reporting that, while a longer commute lowers commute satisfaction, a consistent relationship between commute and overall life satisfaction has not been established[E20]; keep the discussion of commute on commute itself, without turning it into a discussion of life satisfaction.

## Why the change in post-move satisfaction over time is noted

<!-- textlint-disable jtf-style/2.1.2.漢字 -->
<!-- This section shows an author's name as it appears in the original. A non-joyo kanji in a personal name is allowed only here. -->

The fit assessment gives a recommend/do-not-recommend verdict from the material available at the time of judgement alone. Since high satisfaction right after joining does not necessarily last, the report states that the verdict is based on the material at that point (confidence: somewhat likely, over 50% but less than 65%).

- A within-person longitudinal analysis of a managerial sample supports a trajectory in which job satisfaction falls before a voluntary job change, rises right after the change, and then falls again[E21].
- In German panel data, a voluntary job changer's satisfaction with the new job is markedly high but short-lived, and an exogenous test using plant closures found no effect of a job change raising satisfaction[E22].
- A Japanese sample shows that, after controlling for tenure, a job changer's intention to stay is not lower than a non-changer's; the appearance of a lower intention to stay among job changers is interpreted as arising from their shorter tenure[E23]. This finding grounds not treating job-change experience itself as a sign of weaker retention.

Implication for the design: the fit-assessment report carries a note that the verdict is based on the material available at this point, and that high satisfaction right after joining does not mean it will last. This note corresponds to the rule the job-change-self-analysis skill holds, that a forecast of future emotion is not treated as grounds for confidence.

**Evidence lowering confidence (limits)**: the grounds on the trajectory of satisfaction rest on a US managerial sample and German panel data. No Japanese longitudinal study tracking the same individuals before and after a job change and measuring the change in job satisfaction has been identified, other than the one already cited in existing references (Watanabe et al., 2023) (an evidence gap). On the error in affective forecasting, a rebuttal exists[E24] arguing that overestimation occurs only when the event is left unspecified and a general mood is forecast instead, and that part of the intensity bias is an apparent effect arising from the measurement procedure; a counter-rebuttal to this has also been published. Both sides are presented.

<!-- textlint-enable jtf-style/2.1.2.漢字 -->

## Why the axes and weights for company quality are decided per user

Which aspect measures a company's quality differs by user. There is no grounds for applying the same axes and the same weights to every user (confidence: likely, 65% or more but less than 80%).

- Ogawa and Osato (2011) used policy-capturing (a method that back-calculates attribute weights from actual choices) to have 154 social-science students at a private university in the Tokyo metropolitan area evaluate fictional companies, and estimated the weight of company-selection criteria. Overall, the order was job content (β=0.48), pay level (0.38), culture fit (0.36), and company size (0.12). In the high-self-efficacy group, however, culture (0.39) exceeded pay (0.37) and the order flipped; the same reversal — culture (0.40) exceeding pay (0.37) — appeared in the female sample (for men, pay was 0.38 and culture 0.33)[E25].
- A policy-capturing study of 400 employed people in Australia considering a job change found that 40% of the variance in company-attractiveness ratings was attributable to differences between respondents[E26].
- A stated-preference experiment on a US national sample (1,815 employed people) found willingness to pay for a work-from-home option split by education level at 0%, 4%, and 7%. The value of discretion also differed by group, at 0.1% of wages in the lowest-education group and 5.8% in the highest-education group. The same study also shows that, for most attributes other than physical burden and paid leave, men's and women's ratings broadly agree[E27].

A common part also exists. A meta-analysis of 71 studies and 667 coefficients reports that job and organisation characteristics and perceived fit consistently predict how much an applicant is attracted to a company[E28]. A meta-analysis of 242 samples and 638,514 people found a significant gender difference in the weight placed on job attributes for 33 of 40 attributes, but 26 of those had an effect size of 0.20 or under[E29]. An individual difference shows up mainly in how that weight is allocated across attributes.

A stated weight does not, as it stands, match actual judgement. Ogawa and Osato (2011) also ran a direct-question method on the same sample, and found that while the ranking of job content and company size agreed, pay level and culture fit disagreed in ranking. The subgroup difference by self-efficacy could be detected only through the estimate from the choice task[E25]. In the context of hiring — evaluating application documents — the correlation between a subject's self-reported influencing factor and the experimentally manipulated true influence was low, at -0.31, 0.14, and 0.11[E30]. A stated weight is therefore not fixed without cross-checking it.

Implication for the design: the axes for scoring a company are chosen from a list of candidates, with only the compensation level pre-selected by default. A publicly reported numeric indicator is listed as a quantitative-axis candidate; a matter with no number attached enters scoring as a qualitative axis only when the user has decided its label, definition, and judgement conditions. The weight is declared as an allocation summing to 100, and that weight is then used to score two fictional companies, checking whether "which one they would actually choose" agrees with which one scores higher. If they disagree, the allocation is revisited, or both the stated allocation and the actual choice are presented. When the declared axes disagree with the must-have conditions, the desired degree of a work characteristic, or the jobs actually kept from job search, both are likewise presented to the user without deciding which is the true judgement. The canonical definition of the axes, scoring, and weighting lives in `job-change-company-research/references/company-score-rubric.md`.

**Evidence lowering confidence (limits)**: direct evidence from a Japanese sample is limited to the study of 154 university students[E25]; no choice experiment with a general job-seeker sample in the job-change market has been identified. No Japanese study reporting latent preference classes and their composition has been found either, so this skill does not pre-build a typology of weighting patterns. For [E28], the original text could not be reached, and attribute-level effect sizes were not obtained. As a counter-report, one exists arguing that, under a compensatory decision-making assumption, a directly stated weight better predicts job choice[E31]. The sample size and country for this study could not be confirmed.

## Research limits and evidence gaps (this skill's premises)

- No study using a Japanese sample with fit with the assigned team as an independent variable has been identified.
- No peer-reviewed Japanese paper treating the relationship between commute time and subjective well-being has been identified, other than the one already cited in existing references.
- No Japanese longitudinal study tracking the same individuals before and after a job change and measuring the change in job satisfaction has been identified, other than the one already cited in existing references.
- The seven-dimension breakdown itself, the guidance for a score of 1–5, and the decision table for the overall verdict are operational conventions; no empirical study validating the framework itself has been obtained.
- On the axes weighted for company quality, no Japanese choice experiment with a general job-seeker sample and no Japanese study reporting the composition of latent preference classes have been identified.

Because these gaps exist, this skill treats two kinds of point differently. A point supported by a Japanese sample (raising manager fit as a confirmation item, placing the current job as a comparison point, noting commute from the angle of sleep and exercise) is treated as settled, while a point based on a Western sample alone (the trajectory of satisfaction over time) carries a caveat in the form of a note.

## Sources

<!-- textlint-disable -->
<!-- This section lists sources in bibliographic form (publisher or author. title. year. level. URL). This section is disabled entirely so that the separating periods and part of the personal names are not judged as Japanese punctuation or non-joyo kanji. A source whose title could not be confirmed is shown by author name, year, and DOI. -->

- [E1] Astakhova. 2016. Level A. DOI:10.1016/j.jbusres.2015.08.039. https://doi.org/10.1016/j.jbusres.2015.08.039
- [E2] Jung, Takeuchi. 2014. Level A. DOI:10.1080/09585192.2013.778163. https://doi.org/10.1080/09585192.2013.778163
- [E3] 山口. 2026. Level A. DOI:10.20698/comm.54.2_121. https://doi.org/10.20698/comm.54.2_121
- [E4] 森ほか. 2025. Level A. DOI:10.7888/juoeh.47.125. https://doi.org/10.7888/juoeh.47.125
- [E5] Oh ほか. 2014. Level A (whether the East Asian sample's composition includes Japan could not be confirmed in the original text). DOI:10.1111/peps.12026. https://doi.org/10.1111/peps.12026
- [E6] Rubenstein ほか. 2018. Level A. DOI:10.1111/peps.12226. https://doi.org/10.1111/peps.12226
- [E7] Griffeth ほか. 2000. Level A. DOI:10.1177/014920630002600305. https://doi.org/10.1177/014920630002600305
- [E8] Jiang ほか. 2012. Level A. DOI:10.1037/a0028610. https://doi.org/10.1037/a0028610
- [E9] Ministry of Health, Labour and Welfare. Overview of the Reiwa 6 (2024) Survey on Employment Trends. 2025-08-26. Level A. https://www.mhlw.go.jp/toukei/list/9-23-1.html
- [E10] Ministry of Health, Labour and Welfare. Overview of the Reiwa 2 (2020) Survey on Job Changers. 2021. Level A (the summary PDF's text could not be extracted; confirmed via a reprinted press-release article). https://www.mhlw.go.jp/toukei/list/6-21c.html
- [E11] 小松. 2024. Level A. DOI:10.24592/jshrm.25.1_9. https://doi.org/10.24592/jshrm.25.1_9
- [E12] Hori ほか. 2020. Level A. DOI:10.1016/j.sleep.2019.09.017. https://doi.org/10.1016/j.sleep.2019.09.017
- [E13] Journal of Human Ergology 44(1) 1-9. A study of commute time and lifestyle habits among 146 school teachers in Tokyo. Level A. PMID:27281916. https://pubmed.ncbi.nlm.nih.gov/27281916/
- [E14] 早坂ほか. 2003. Level A. DOI:10.15064/jjpm.43.3_203_2. https://doi.org/10.15064/jjpm.43.3_203_2
- [E15] 鹿島, 武田. 2009. Level A. DOI:10.24639/tpsr.TPSR_11R_16. https://doi.org/10.24639/tpsr.TPSR_11R_16
- [E16] 森川. Research Institute of Economy, Trade and Industry Discussion Paper 18-J-009. 2018. Level B (a report from a public research institute that has not undergone peer review). https://www.rieti.go.jp/jp/publications/dp/18j009.pdf
- [E17] Stutzer, Frey. 2008. Level A. DOI:10.1111/j.1467-9442.2008.00542.x. https://doi.org/10.1111/j.1467-9442.2008.00542.x
- [E18] Stutzer, Frey. IZA Discussion Paper No. 1278 (the working-paper version of [E17]; footnote 14, page 17). 2004. Level B (contains a passage replaced in the published version). https://docs.iza.org/dp1278.pdf
- [E19] Roberts ほか. 2011. Level A. DOI:10.1016/j.jhealeco.2011.07.006. https://doi.org/10.1016/j.jhealeco.2011.07.006
- [E20] Chatterjee ほか. 2020. Level A. DOI:10.1080/01441647.2019.1649317. https://doi.org/10.1080/01441647.2019.1649317
- [E21] Boswell ほか. 2005. Level A. DOI:10.1037/0021-9010.90.5.882. https://doi.org/10.1037/0021-9010.90.5.882
- [E22] Chadi, Hetschko. 2018. Level A. DOI:10.1111/jems.12217. https://doi.org/10.1111/jems.12217
- [E23] 吉澤, 宮地. 2009. Level A. DOI:10.32222/jaiop.23.1_3. https://doi.org/10.32222/jaiop.23.1_3
- [E24] Levine ほか. 2012. Level A. DOI:10.1037/a0029544. https://doi.org/10.1037/a0029544
- [E25] 小川, 大里. 2011. Level A. DOI:10.32222/jaiop.25.1_25. https://doi.org/10.32222/jaiop.25.1_25
- [E26] Hicklenton ほか. 2021. Level A. DOI:10.1371/journal.pone.0254646. https://doi.org/10.1371/journal.pone.0254646
- [E27] Maestas ほか. 2023. Level A. DOI:10.1257/aer.20190846. https://doi.org/10.1257/aer.20190846
- [E28] Chapman ほか. 2005. Level A (the original text could not be reached; attribute-level effect sizes not obtained). DOI:10.1037/0021-9010.90.5.928. https://doi.org/10.1037/0021-9010.90.5.928
- [E29] Konrad ほか. 2000. Level A. DOI:10.1037/0033-2909.126.4.593. https://doi.org/10.1037/0033-2909.126.4.593
- [E30] Nisbett, Wilson. 1977. Level A. DOI:10.1037/0033-295X.84.3.231. https://doi.org/10.1037/0033-295X.84.3.231
- [E31] Slaughter ほか. 2006. Level A (the sample size and country could not be confirmed). DOI:10.1177/1094428105279936. https://doi.org/10.1177/1094428105279936

<!-- textlint-enable -->
