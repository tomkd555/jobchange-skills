# Canonical answer-evaluation source (four criteria, three-level anchors)

<!-- textlint-disable jtf-style/4.3.2.大かっこ［］ -->
<!-- The [E1]-style notation in the body is the source-id notation. To preserve the half-width square brackets, this rule is disabled for this file. -->

This is the canonical source for the anchors (explicit judging criteria for each level) used to evaluate answers collected in a mock interview. job-change-interview-coach reads this file in Step 3 and judges against the anchors it states. Evaluation covers four criteria, each judged on a three-level scale (`充足` (met), `一部` (partial), `不足` (not met)). In company-independent fallback mode, the company-understanding criterion is excluded from evaluation.

## The four criteria and their three-level anchors

The JSON key for each criterion (inside `scores`) is given alongside it.

### STAR (`scores.star`)

Judged by whether the four elements — Situation, Task, Action, Result — are present.

| Level | Judgment |
|---|---|
| `充足` (met) | All four elements are present. |
| `一部` (partial) | One or two elements are missing. |
| `不足` (not met) | Three or more elements are missing. |

### Specificity (`scores.specificity`)

Judged by whether the answer is backed by numbers or proper nouns.

| Level | Judgment |
|---|---|
| `充足` (met) | Backed by numbers or proper nouns. |
| `一部` (partial) | Backed only partially. |
| `不足` (not met) | Purely abstract, with no backing. |

### Consistency (`scores.consistency`)

Judged by whether there is a contradiction between the reason for changing jobs and the motivation for applying. The reference for this judgment is profile.json's `job_change_axis`. When `self_analysis.json` exists, its `career_narrative` (the consistent motivation) and `reason_for_change` (the constructive reframing and its explanation of alignment with `job_change_axis.reasons`) are also added to the reference set.

| Level | Judgment |
|---|---|
| `充足` (met) | No contradiction. |
| `一部` (partial) | A minor discrepancy. |
| `不足` (not met) | A clear contradiction. |

### Company understanding (`scores.company_fit`)

Judged by whether the answer connects to company-specific evidence (a claim in company_research.json, or an `RQ`, `FF`, or `TH` item in interview_intel.json). Excluded in fallback mode (when neither company_research.json nor interview_intel.json exists).

| Level | Judgment |
|---|---|
| `充足` (met) | A clear connection to a claim. |
| `一部` (partial) | The connection is fragmentary. |
| `不足` (not met) | No connection. |

## Elements of a good answer

The elements a highly rated answer has[E69].

| Element | Content |
|---|---|
| Specificity | Speaking through concrete situations and actions. |
| Quantification | Backing an achievement with numbers. |
| Ownership | Stating the role, judgment, and action the candidate themselves took, as the subject (distinguishing it from what others or the organization achieved). |
| Answer-first | Stating the conclusion first, followed by the supporting reasoning. |
| Time allocated to Action | Devoting 50 to 60 percent of the answer time to Action, and describing Action in the greatest detail among the STAR elements. This time allocation matters especially in a behavioral interview scored with a Behaviorally Anchored Rating Scale (BARS)[E69]. |

## Academic evidence

This section states the basis for recommending preparation aligned with structured and past-behavior interviews in interview preparation, its limits, and unsettled questions. Where a question cannot be settled, both sides of the debate are presented. Every source carries a DOI.

### Predictive validity of structured interviews

A structured interview (one with questions and evaluation criteria set in advance) has higher predictive validity than an unstructured interview. McDaniel et al. (1994), a meta-analysis of 245 coefficients across N = 86,311, concluded that structured interviews have higher validity than unstructured interviews[E74]. Conway et al. (1995) estimated the validity ceiling implied by reliability at .67 for highly structured interviews and .34 for unstructured interviews[E79].

Two estimates of the absolute level of validity coexist and neither can be treated as settled (both sides presented).

| Estimate | Content |
|---|---|
| Classical estimate (Schmidt & Hunter, 1998) | Summarizing 85 years of research on the predictive validity of selection methods, it reported .51 for general mental ability (GMA) alone and .63 for GMA plus a structured interview, among other figures[E73]. This figure of around .51 has long served as the standard. |
| Downward revision (Sackett et al., 2022) | Arguing that earlier estimates over-corrected for range restriction (the shrinkage of variance caused by selection), this work revised validity downward and placed structured interviews at the top of the relative ranking. The validity of structured interviews is estimated at approximately .42[E75]. This downward revision (over whether the range-restriction correction is warranted) remains contested between Sackett and colleagues and Oh, Le & Roth (2023), so neither coefficient is settled[E82]. The relative ranking (structured interviews, work samples, and GMA at the top) remains largely unchanged. |

Implication: preparing STAR answers on the premise of a structured, behavioral interview is academically supported. The absolute level of validity has, however, been revised downward. This skill treats interview technique as one tool with known limits.

### Past-behavior versus situational interviews (unsettled)

Interview questions fall into two forms: the past-behavior interview, which asks about actual past behavior ("what did you actually do when ..."), and the situational interview, which asks about a hypothetical response ("what would you do if ..."). Which is superior remains academically unsettled. The user needs to prepare for both forms (both sides presented).

- McDaniel et al. (1994) ranked situational interviews highest[E74].
- Taylor & Small (2002) reported that past-behavior (behavior-description) questions show higher validity than situational questions (.63 versus .47)[E78].

### Verification status in Japanese hiring interviews (a limitation)

Every validity estimate above rests on meta-analyses of Western samples. Research verifying the validity and reliability of hiring interviews in Japan is limited to a small number of case studies, and none of them confirms validity at the level the Western meta-analyses show.

Suzuki (2013) analyzed interview data from one Japanese company. The reliability coefficient for behavioral evaluation was 0.63 to 0.73, and the predictive validity from behavioral evaluation to performance evaluation was a negative coefficient of −.34 to −.20. From this, Suzuki concluded that the company's hiring interview had no predictive validity[E105]. Suzuki (2016) showed inter-rater reliability rank correlations of only 0.04 to 0.41[E106]. Takeda (2004) reported designing an interview with a deliberately low degree of structure, prioritizing building trust with the candidate on the premise of long-term employment[E107].

Implication: expected questions and evaluation anchors are tools that help prepare answers. The "never predicting the outcome" scope exclusion in SKILL.md rests on this verification status. With no evidence for what level of validity Japanese interview evaluation has, the quality of preparation cannot be used to infer the likelihood of success.

Limitation: all of the above are single-company case studies of new-graduate hiring, and none examines the effect of range restriction from observing performance only for hired candidates. No peer-reviewed Japanese paper verifying the predictive validity of mid-career hiring selection could be identified. The discrepancy from the Western meta-analyses is therefore never treated as a general rule for Japan, nor is it treated as grounds for asserting that Japanese hiring interviews have no validity.

### Impression management, and the implication for fact-based preparation

Levashina & Campion (2007) reported that over 90 percent of candidates engage in some form of impression management during an interview[E80]. This finding rests on a single study, however, and no independent study has reproduced a result at the same level, so this document avoids asserting it as settled. The implication is as follows: because embellishment can surface as a contradiction under further questioning, fact-based, specific preparation is the best approach. This implication is consistent with the evaluation anchors above (backing specificity and consistency with numbers and proper nouns).

## Sources

- [E69] CareerTestPrep. Behavioural Interview Questions: The Complete STAR Method Guide 2026. 2026-05-31. Level B. https://www.careertestprep.com/blog/behavioural-interview-questions-star-method
- [E73] Psychological Bulletin. The validity and utility of selection methods in personnel psychology: Practical and theoretical implications of 85 years of research findings. 1998. Level A. DOI:10.1037/0033-2909.124.2.262 https://doi.org/10.1037/0033-2909.124.2.262
- [E74] Journal of Applied Psychology. The validity of employment interviews: A comprehensive review and meta-analysis. 1994. Level A. DOI:10.1037/0021-9010.79.4.599 https://doi.org/10.1037/0021-9010.79.4.599
- [E75] Journal of Applied Psychology. Revisiting meta-analytic estimates of validity in personnel selection: Addressing systematic overcorrection for restriction of range. 2022. Level A. DOI:10.1037/apl0000994 https://doi.org/10.1037/apl0000994
- [E78] Journal of Occupational and Organizational Psychology. Asking applicants what they would do versus what they did do: A meta-analytic comparison of situational and past behaviour employment interview questions. 2002. Level A. DOI:10.1348/096317902320369712 https://doi.org/10.1348/096317902320369712
- [E79] Journal of Applied Psychology. A meta-analysis of interrater and internal consistency reliability of selection interviews. 1995. Level A. DOI:10.1037/0021-9010.80.5.565 https://doi.org/10.1037/0021-9010.80.5.565
- [E80] Journal of Applied Psychology. Measuring faking in the employment interview: Development and validation of an interview faking behavior scale. 2007. Level A (single study). DOI:10.1037/0021-9010.92.6.1638 https://doi.org/10.1037/0021-9010.92.6.1638
- [E82] Journal of Applied Psychology. Correcting for range restriction in meta-analysis: A reply to Oh et al. (2023). 2023. Level A. DOI:10.1037/apl0001116 https://doi.org/10.1037/apl0001116
- [E105] Suzuki 2013. Level A. DOI:10.24592/jshrm.14.2_4 https://doi.org/10.24592/jshrm.14.2_4
- [E106] Suzuki 2016. Level A. DOI:10.24592/jshrm.17.1_69 https://doi.org/10.24592/jshrm.17.1_69
- [E107] Takeda 2004. Level A. DOI:10.4992/jjpsy.75.339 https://doi.org/10.4992/jjpsy.75.339
