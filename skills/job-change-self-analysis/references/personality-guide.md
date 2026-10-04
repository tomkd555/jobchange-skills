# Handling of personality and behavioural tendencies (personality-guide)

<!-- textlint-disable jtf-style/4.3.2.大かっこ［］ -->
<!-- The [E1] form in the body is the notation for a source id. This file disables that rule to keep the half-width square brackets. -->

This is the canonical definition, in the job-change-self-analysis skill, for collecting personality and behavioural tendencies as self-reports, mapping them to behavioural evidence and feedback from others, and carrying them into the deliverable. The entry criteria for `personality` in `self_analysis.json`, the Step 3.5 questions (`question-bank.md`), and the judgment of the two agents (writer / auditor) all treat this file as canonical. The grounds for the limits of introspection and for preventing rumination are in `self-analysis-methods.md`, and are not duplicated here. Evidence levels are marked on a four-level A-D scale, and academic research carries a DOI.

## Position

Self-reported personality is the third material, after behavioural episodes and feedback from others. A self-report shows the person's own self-image, and does not show the trait itself ("Introspection alone is unreliable" in `self-analysis-methods.md`). So the items in a self-report are limited to the following three roles.

1. A prompt that draws out an episode. After the person answers an item, have them name one episode where that tendency showed up, and map it with `linked_episode_ids`.
2. Material that makes the agreement and disagreement between self-image and feedback from others visible (the Johari window). A disagreement is recorded as it stands, without leaning toward the more favourable side.
3. Material that gives behaviour-grounded language to work-characteristic preferences (`work_character_preferences`), orientation, and the description of strengths and weaknesses in a job interview.

A self-report alone never builds a strength. A self-report that maps to neither an episode nor feedback from others stays in `personality.markers`, and grounds no entry in `strengths`.

## Instruments used and not used

For a personality assessment, whether it is public and the terms of its use differ by instrument. This skill may ask only items that are public and permit redistribution and modification.

| Instrument | Terms of use | Handling in this skill |
|---|---|---|
| IPIP (International Personality Item Pool) | Public domain. Copying, editing, translating, and using it does not require permission or a fee [E1] | The Big Five framework and the intent of its items, and honesty-humility (the IPIP version derived from HEXACO), may be used. Items are rewritten into this skill's forced-choice form before being asked |
| HEXACO-PI-R (the original version) | Free for non-commercial academic research only. Any other use requires contacting the author [E2] | The original items are not used. Only the honesty-humility framework is used, in the sense of the IPIP version |
| Short Grit Scale (Grit-S) | Free for non-commercial research and education only. The author's terms exclude commercial use, wide public distribution, and use in a setting with a stake, such as hiring [E3] | The scale is not used. Only the construct of grit is referenced, and it is asked through a forced-choice item this skill wrote on its own |
| General Self-Efficacy Scale (GSE) | The original (English) version is free for research purposes. The standard Japanese scale (一般性セルフ・エフィカシー尺度, the General Self-Efficacy Scale) is a paid assessment [E4] | The scale is not used. Only the construct of self-efficacy is referenced, and it is asked through an item this skill wrote on its own |
| O*NET Interest Profiler | CC BY 4.0. Modification, including translation, is allowed when the source is credited [E5] | This skill does not offer a scored assessment, so its items are not used. Only the name of the interests (RIASEC) framework is used |
| The content of the O*NET Work Importance Profiler and the other Career Exploration Tools | CC BY-ND 4.0. Using the items unchanged is allowed, and modifying them (including rewriting into Japanese) requires a separate developer licence and verification obligation [E5] | Items are not rewritten into Japanese and offered. Only the name of the work-values framework is used |
| VPI Vocational Interest Inventory (Japanese version) | A paid assessment kit, and JILPT does not sell it [E6] | Not used. RIASEC is used only as the name of the framework |
| The self-diagnosis tool on the Ministry of Health, Labour and Welfare's job tag site, JILPT Career Insight, the VRT card, and the GATB | Provided by public institutions, and the user can take them independently. Some are available at a Hello Work office (ハローワーク, the public employment service) | Not offered by this skill. When the user brings in a result they took elsewhere, treat it as a prompt, never as a settled judgment |
| Schein's Career Anchor questionnaire | A paid publication | Used only as a prompt for the eight categories (`question-bank.md`) |
| Career Construction Interview (Savickas) | An open-ended interview framework described in an academic paper | Questions written in this skill's own words, carrying the intent of the five questions, are used (the five CCI-style questions in `question-bank.md`). The original questions are never reproduced as they stand |
| VIA Character Strengths | The official survey is the intellectual property of the VIA Institute. The public research versions (GACS, SSS) are also limited to research on groups [E7]. Whether reproducing the names of the 24 strengths is allowed has not been confirmed against the terms of use | The survey is not offered. The names of the 24 strengths are shown in conversation only as candidates for putting a strength into words, and are never reproduced as a list in the deliverable |
| CliftonStrengths (Gallup) | Protected by trademark and copyright, and reproducing its theme names and descriptions is prohibited [E8] | Not offered. Its names are not reproduced either |
| MBTI, 16Personalities | Sorts a person into a four-letter type. The subscales' retest reliability is uneven, and the thinking-feeling scale reaches only .61 [E9]. 16Personalities has not published its scoring model, and no independent validity study has been confirmed [E10] | Not offered. When the user names a type, such as 「私は INFP です」 ("I'm an INFP"), the type is neither denied nor affirmed; the conversation moves to an episode by asking, 「その型で言うと、どんな行動が思い当たりますか」 ("In terms of that type, what behaviour comes to mind?") |
| Employer-side aptitude tests such as SPI3, 玉手箱 (Tamatebako; its 性格検査 part is OPQ), and TAL | Commercial tests for the hiring side's decision-making. Items are not public, and the result is never returned to the test-taker | Not offered. The description stays at what the test measures, and preparation is referred to `job-change-exam-prep` |
| Miidas, GOOD POINT diagnosis, doda's Career Type diagnosis, and en-japan's diagnosis | Free diagnostics each company built from its own data. No independent validity study has been published | Not offered. Their items are not reproduced either. The 18 published names from GOOD POINT diagnosis are listed in the vocabulary table as candidate names for a strength |
| The Dark Triad (such as the SD3) | Research scales are public | Not offered. It is a scale for judging risk in others, has no constructive use in self-analysis, and can be harmful as a label a person applies to themselves |

## Construct vocabulary

The identifiers usable in `personality.markers[].construct` are limited to the following table. `validate_self_analysis.py` holds the same vocabulary as this table, and reports an identifier absent from the table as an ERROR. The table's first column (the string in backticks) is the identifier.

| Identifier | Name | Origin | What it observes |
|---|---|---|---|
| `conscientiousness` | Conscientiousness | Big Five (IPIP) | The tendency to plan, arrange steps, and follow through |
| `emotional_stability` | Emotional stability | Big Five (IPIP) | Calm and recovery under a demanding situation |
| `extraversion` | Extraversion | Big Five (IPIP) | The direction of energy in a situation involving other people |
| `agreeableness` | Agreeableness | Big Five (IPIP) | How the person settles a conflict |
| `openness` | Openness | Big Five (IPIP) | How the person approaches an unfamiliar method or field |
| `honesty_humility` | Honesty-humility | HEXACO (IPIP version) | How credit for a result is attributed, and candour |
| `grit` | Grit | Construct referenced only (no scale used) | Persistence toward a long-term goal |
| `self_efficacy` | Self-efficacy | Construct referenced only (no scale used) | The expectation of getting through a difficulty by one's own approach |
| `planning_style` | Approach | This skill's own framework | Whether planning comes first, or adjustment happens on the fly |
| `collaboration_style` | Collaboration style | This skill's own framework | Whether the person concentrates alone or moves forward through dialogue |
| `change_orientation` | Orientation toward change | This skill's own framework | Whether a stable environment or a highly changeable one suits the person |
| `decision_style` | Decision style | This skill's own framework | Whether numbers and measurement come first, or hypothesis and intuition come first |
| `feedback_timing` | Interval for receiving evaluation | This skill's own framework | Whether the person wants results at short intervals, or gathered at milestones |
| `stress_trigger` | Source of strain | This skill's own framework | Which of ambiguity, a deadline, interpersonal friction, or monotonous work drains the person most |
| `recovery_style` | Recovery style | This skill's own framework | Whether the person recovers alone or by talking with someone |

The Big Five factors and honesty-humility are the framework whose link to job performance has been confirmed most repeatedly [E11][E12]. The seven items in this skill's own framework exist to check against work-characteristic preferences (the hub's `screening-axes.md`) and against culture fit in fit assessment. This skill wrote the wording of all 15 items itself, and reproduces no item from another assessment. The Big Five items, too, are rewritten by this skill around a situation and a behaviour, in keeping with the intent of each factor.

## How to ask

A self-report is asked as a behaviour-grounded forced choice. Two behaviours whose desirability is balanced are set side by side, and the person picks which is closer to them. This produces less bias toward the more desirable side than a format where the person rates one sentence with 「当てはまる／当てはまらない」 (applies / does not apply) [E13][E14]. AskUserQuestion's choice form (up to 4 options) suits a forced choice.

Rules to keep.

- Write both options so each works as a strength in some situation. Never build a pair where one side is clearly more desirable, as in 「計画的」 (planned) against 「場当たり的」 (haphazard).
- Write a situation and a behaviour, as in 「締切が迫ったとき、まず残りの作業を書き出す」 (when a deadline is close, first list the remaining work).
- Each time an item is answered, have the person name one episode where that tendency showed up. Have them choose from the existing `behavioral_episodes`, and when none fits, ask immediately for one episode in STAR form. When none comes up, leave `linked_episode_ids` empty. An item that maps to neither an episode nor feedback from others produces a WARN, and the deliverable still stands.
- 「どちらも同じくらい」 (both about equally) and 「場面による」 (it depends on the situation) are accepted as answers too. Never force the person toward one side.
- The questions asked in one Step are limited to 16 (covering 15 constructs; `stress_trigger` alone gets 2 questions; the breakdown is in `question-bank.md`), and no further "why" is layered on top (to prevent rumination).
- When feedback from others (`others_feedback`) describes the same tendency, map it with `feedback_ids`. When a self-report disagrees with feedback from others, write the disagreement as it stands in `note`.

The settled wording is in Step 3.5 of `question-bank.md`.

## How to write the result

- Never sort a person by the name of a type or category. Never write 「〜型です」, 「〜タイプです」 or 「あなたは内向型です」. When `personality.presentation` contains the name of a type or category, the validation script reports a WARN.
- Write a descriptive passage. Write it in the past tense, mapped to an episode, as in 「事前に計画を固めてから着手する行動が、ep-1 と ep-2 で繰り返し見られた」 (the behaviour of settling a plan before starting showed up repeatedly, in ep-1 and ep-2).
- Attach no number, percentile, or five-point score. A number looks like a measured value, so a reader gives it more weight than the evidence supports.
- Write it as a self-image at one point in time. It states 「現時点でこう自己申告している」 (what the person reports about themselves at this point), and stays open to revision as a trait.
- Never write a sentence that fits anyone (「慎重なときもあれば大胆なときもある」). When a sentence could move unchanged into another person's set of episodes, it has no grounding (the Barnum effect [E15]). The auditor checks from this perspective.
- Write a disagreement between a self-report and feedback from others as it stands.

## Connection downstream

| Destination | How it is used |
|---|---|
| `job_change_axis.work_character_preferences` (`{AXIS}`, owned by `job-change-axis`; skipped when no `{AXIS}` exists) | `planning_style` is checked against the preference level for `clear_completion`, `collaboration_style` against `solo_completable`, and `feedback_timing` against `short_feedback`. A disagreement is written in `notes`, and the skill never decides which side is true |
| `culture_fit` and `work_character_fit` in `job-change-fit-assessment` | `change_orientation`, `stress_trigger`, and `recovery_style` become material for checking against the facts about working style and reputation from company research. A self-report alone never raises a `score` |
| Self-promotion and weaknesses in `job-change-interview-prep` | The grounds for `strengths` (episodes, feedback from others) and the description in `personality.markers` become material for the answer to a question about weaknesses. From "source of strain" and "recovery style," the user can talk about a weakness while naming the improving behaviour that goes with it |
| The personality test in `job-change-exam-prep` | For a personality test, a consistent, honest answer is recommended (`prep-methods.md` of that skill). The self-image organised here is material for keeping that consistency |
| The Ministry of Health, Labour and Welfare's Job Card (ジョブ・カード) | The content of `behavioral_episodes` and `career_narrative` overlaps with the self-understanding section of the Job Card's Career Plan Sheet. For a user who separately needs a Job Card, tell them this deliverable can be reused for it [E16] |

## Limits

- Personality explains only a small share of job performance. In a study that integrated 54 meta-analyses, the correlation between conscientiousness and overall job performance is ρ=.19, extraversion .10, agreeableness .10, neuroticism -.12, and openness .13 [E11]. Conscientiousness alone explains under 4% of the variance, and the five factors together stay at a few percent. These are correlations after statistical correction, and a position that doubts the correction's validity estimates them lower still [E18]. In fit assessment, personality fit is never weighted more heavily than closeness of experience or skill fit.
- Step 3.5 exists despite this small explanatory share because describing a weakness and a strength in a job interview, answering a personality test consistently, and checking against work-characteristic preferences all need behaviour-grounded language. For this purpose, 15 items is a ceiling, and the whole of Step 3.5 may be skipped when the user wants to omit it.
- How personality operates changes by occupation. Conscientiousness holds validity across every occupational group, and extraversion holds higher validity for management and sales roles [E12].
- A self-report and feedback from others tend to disagree on conscientiousness and emotional stability. When either of these two constructs grounds a `strengths` entry, mapping it to feedback from others is strongly recommended.
- The correlation between interest fit and job satisfaction is weak (ρ=.19; [E11] in `self-analysis-methods.md`). Interest fit is never treated as a guarantee of satisfaction.
- Fit with a supervisor relates to satisfaction and retention, and its relation to job performance is weak [E17]. It cannot be judged from a job posting or company research, so it stays as a matter to confirm at the job interview (`fit-criteria.md` in `job-change-fit-assessment`).

## Sources

<!-- textlint-disable -->
<!-- This section lists sources in bibliographic form (publisher. title. year. level. URL). This section alone disables the rule, so the linter does not judge the separating periods and parts of organisation names as Japanese punctuation or as synonyms. -->

- [E1] International Personality Item Pool (Oregon Research Institute). IPIP Home — public domain statement. Level A. https://ipip.ori.org/
- [E2] HEXACO Personality Inventory-Revised (Lee & Ashton). Download terms. Level A. https://hexaco.org/hexaco-inventory
- [E3] Angela Duckworth. Research — measures and terms of use. Level A. https://www.angeladuckworth.com/measures (original work: Duckworth, A. L. & Quinn, P. D. Journal of Personality Assessment. 2009. DOI:10.1080/00223890802634290)
- [E4] Schwarzer, R. & Jerusalem, M. Generalized Self-Efficacy scale. In Measures in health psychology: A user's portfolio. 1995. Level B (secondary distribution of a version the author published). https://www.researchgate.net/publication/311570532_The_general_self-efficacy_scale_GSE
- [E5] O*NET Resource Center. O*NET Career Exploration Tools Content License. Level A. https://www.onetcenter.org/license_tools.html
- [E6] The Japan Institute for Labour Policy and Training (労働政策研究・研修機構, JILPT). VPI Vocational Interest Inventory. Level A. https://www.jil.go.jp/institute/seika/tools/VPI.html
- [E7] VIA Institute on Character. Public Domain Surveys. Level A. https://www.viacharacter.org/researchers/assessments/noregistration
- [E8] Gallup, Inc. Product Terms of Use. Level A. https://login.gallup.com/Home/ProductTerms
- [E9] Journal of Best Practices in Health Professions Diversity. Randall, K., Isaacson, M. & Ciro, C. Validity and Reliability of the Myers-Briggs Personality Type Indicator: A Systematic Review and Meta-Analysis. 2017. Level A. https://gwern.net/doc/psychology/personality/2017-randall.pdf
- [E10] Medical News Today. Myers-Briggs: 16 personality types and their accuracy. Level C. https://www.medicalnewstoday.com/articles/myers-briggs-16-personality-types
- [E11] Journal of Personality (Wiley). Zell, E. & Lesick, T. L. Big Five Personality Traits and Performance: A Quantitative Synthesis of 50+ Meta-Analyses. 2022. Level A. DOI:10.1111/jopy.12683. https://doi.org/10.1111/jopy.12683
- [E12] Personnel Psychology (Wiley). Barrick, M. R. & Mount, M. K. The Big Five Personality Dimensions and Job Performance: A Meta-Analysis. 1991. Level A. DOI:10.1111/j.1744-6570.1991.tb00688.x. https://doi.org/10.1111/j.1744-6570.1991.tb00688.x
- [E13] Frontiers in Psychology. A Meta-Analysis of the Faking Resistance of Forced-Choice Personality Inventories. 2021. Level A. https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2021.732241/full
- [E14] Frontiers in Psychology. Controlling for Response Biases in Self-Report Scales: Forced-Choice vs. Psychometric Modeling of Likert Items. 2019. Level A. https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2019.02309/full
- [E15] Current Psychology (Springer). Accepting personality test feedback: A review of the Barnum effect. Level A. https://link.springer.com/article/10.1007/BF02686623
- [E16] Ministry of Health, Labour and Welfare (厚生労働省). The Job Card system (ジョブ・カード制度). Level A. https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/koyou_roudou/jinzaikaihatsu/jobcard_system.html
- [E17] Personnel Psychology (Wiley). Kristof-Brown, A. L., Zimmerman, R. D. & Johnson, E. C. Consequences of Individuals' Fit at Work: A Meta-Analysis. 2005. Level A. DOI:10.1111/j.1744-6570.2005.00672.x. https://doi.org/10.1111/j.1744-6570.2005.00672.x
- [E18] Journal of Applied Psychology (APA). Sackett, P. R. et al. Revisiting meta-analytic estimates of validity in personnel selection: Addressing systematic overcorrection for restriction of range. 2022. Level A. DOI:10.1037/apl0000994. https://doi.org/10.1037/apl0000994

<!-- textlint-enable -->
