# Career narrative and constructive reframing of the reason for leaving

<!-- textlint-disable jtf-style/4.3.2.大かっこ［］ -->
<!-- The [E1] form in the body is the notation for a source ID. This file disables that rule to preserve the half-width square brackets. -->

This is the canonical definition of the criteria the job-change-self-analysis skill uses when integrating self-analysis material into a "consistent career narrative" and a "constructive reframing of the reason for leaving." The material refers to episodes, testimony from others, interests, values, and career adaptability. The writer agent references this file when creating career_narrative and reason_for_change. Job interview preparation and the deepening of statements of motivation (interview-prep / documents) also read it as the grounds for consistency. The evidence-level and DOI notation follow the same convention as self-analysis-methods.md.

## Why connect to a narrative

The result of self-analysis connects to how a candidate is evaluated in the selection process, through consistency across the job interview and the statement of motivation (confidence: likely, 65% or higher and under 80%).

- The Career Construction Interview (CCI) is a framework that elicits a life theme through five to seven questions [E43]. The interviewer and the counselee jointly build a consistent career story (a narrative identity) that connects the self-concept to a professional role. CCI is the academic framework that connects the result of self-analysis to consistency between the statement of motivation and interview answers.
- Employers include the reason for changing jobs and the statement of motivation among the interview's evaluation criteria, and judge the reproducibility of the candidate's behaviour [E42]. Because employers see the lack of an objective standard for evaluating ability as a challenge [E24][E25], a consistent explanation from the candidate can become a point of contact for that evaluation.

**Reservation**: no domestic empirical study confirms that the consistency of a narrative raises the selection outcome (a pass, or the offer rate). This skill keeps this connection at the level of "consistency can become a point of contact for evaluation." It never treats consistency as a guarantee of a pass.

## The components of the career narrative

Build career_narrative along the CCI framework (the life theme, turning points, consistent motivation).

| Element | Content |
|---|---|
| life_theme (the life theme) | The theme of interest running through multiple episodes. Express in one sentence the direction that appears in common across multiple episodes. Use the answers to question-bank.md's five CCI-style questions (an admired figure, a magazine or programme, a favourite story, a motto, an early childhood memory) as material. |
| turning_points (turning points) | The junctures where interest or behaviour changed. Select, from behavioral_episodes, the events that set the direction. |
| consistent_motivation (the consistent motivation) | The motivation that recurs across multiple situations. Extract, from the episodes and the values, the motivation that has been at work consistently. |
| future_direction (the future direction) | Where the consistent motivation heads next. Align it with reason_for_change's constructive_version. |

Rules for building it:

1. Write each element of the narrative only within the range corroborated by material from behavioral_episodes, others_feedback, or values. Never invent a fact not found in the material.
2. Never ground the narrative in an affective forecast ("I would be fulfilled if I took this job") [E55]. Extract motivation from past behaviour, and never substitute a forecast of future feeling for it.

## Constructive reframing of the reason for leaving

In reason_for_change, convert a list of complaints (raw_reasons) into an explanation built around the value the person wants to bring to bear (constructive_version).

The conversion procedure:

1. Record raw_reasons without processing them. List, without dressing them up, the present complaints and the original reasons behind considering leaving. This is the starting point of the conversion and is kept internal.
2. Identify the "value the person wants to bring to bear" behind each complaint. For each complaint, ask "then what do I want to achieve," and map it to values and to career_narrative's consistent_motivation. Reframe the complaint (what to avoid) into what the person wants to achieve (what to move toward).
3. Write constructive_version with what the person wants to achieve as its subject, built around the value the person wants to bring to bear. constructive_version must be a different sentence from raw_reasons (the validation script issues a WARN when it remains the identical string).
4. Check the alignment with the axis in consistency_note. Check whether the axis of constructive_version agrees with `job_change_axis.reasons` in `{AXIS}` (the reason for changing jobs, written as what the person wants to achieve next). Explain any divergence. When no `{AXIS}` exists, leave consistency_note out; the constructive_version waits as the proposed answer for `reasons` until the user starts the `job-change-axis` track.

The example below shows the conversion's structure only; the actual data comes from the user's own material.

- raw_reason (the complaint): 「今の環境では、運用の設計まで踏み込めない」 (In my current environment, I cannot get involved as far as designing operations)
- The value identified: 「個人の対応を仕組みへ残して再現性を上げたい」 (I want to raise reproducibility by turning individual responses into a system)
- constructive_version (what the person wants to achieve): 「個人の対応を仕組みへ残す働き方を、運用の設計まで担える範囲で発揮したい」 (I want to bring to bear a way of working that turns individual responses into a system, in a role that reaches as far as designing operations)

Rule: never hide a complaint. Even so, never let it end as a list of complaints. A constructive reframing is "the value the person wants to bring to bear," backed by fact (an episode, a value), and describes the present situation as it is.

## Connecting to how a company evaluates

Connect the result of self-analysis to the perspective a company evaluates from. This connection comes with the reservation that the weight given to the statement of motivation varies by company.

- In interviews for experienced-hire recruitment aimed at people in their twenties, the point HR staff look at most often is character and fit with the company culture (86.2%). Experience and achievements (60.8%), the reason for changing jobs (55.3%), and the statement of motivation (49.4%) follow [E40]. **This figure comes from one survey whose population was limited to people in their twenties.** The reason for changing jobs and the statement of motivation rank high, yet character and achievements rank above them. That fact shows both the value and the limit of connecting self-analysis to the selection process.
- The weight given to the statement of motivation varies by company. At a company that emphasises skill and experience, the statement of motivation has lower priority, and the interview may not even ask about it [E41].
- A mid-career hiring interview pays attention to the behavioural process leading to a result (in which situation the candidate thought and acted, and how), and judges the reproducibility that keeps functioning when the environment changes [E42]. behavioral_episodes's reproducibility corresponds directly to this perspective on reproducibility.

Operating this connection:

1. STAR material (behavioral_episodes), once it includes a metric (a quantitative value) and reproducibility, becomes a point of contact for the employer's challenge of "lacking an objective standard for evaluating ability" [E25].
2. Pass career_narrative and reason_for_change.constructive_version on as grounds for the interview's "consistency" perspective (which interview-prep evaluates), and as grounds for the statement of motivation (which documents writes).
3. Never treat the statement of motivation as the top deciding factor. Because its weight varies by company, prepare corroboration for character, fit, and achievements (episodes, testimony from others) alongside it.

## Sources

<!-- textlint-disable -->
<!-- This section lists sources in bibliographic form (publisher. title. year. level. URL). This section alone disables the rule, so its separating periods and the parts of company names are not judged as Japanese punctuation or synonyms. -->

- [E24] Ministry of Health, Labour and Welfare (厚生労働省). Summary of the FY2020 Survey on the Actual Situation of Job Changers (令和2年転職者実態調査の概況), on problems at the time of hiring (84.1%). 2021-12. Level A. https://www.mhlw.go.jp/toukei/list/dl/6-18c-r02-gaikyo.pdf
- [E25] Ministry of Health, Labour and Welfare (厚生労働省). Summary of the FY2020 Survey on the Actual Situation of Job Changers (令和2年転職者実態調査の概況), breakdown of the problems. 2021-12. Level A. https://www.mhlw.go.jp/toukei/list/6-18c-r02.html
- [E40] Gakujo Co., Ltd. (株式会社学情). What HR staff look at in interviews when hiring experienced candidates in their twenties (an HR-staff survey of 421 companies). 2023-05. Level B. https://prtimes.jp/main/html/rd/p/000001051.000013485.html
- [E41] Geekly (ギークリー). Why wasn't I asked about my statement of motivation in the interview? 2024-08-30. Level C. https://www.geekly.co.jp/column/cat-jobsearch/interview/jobinterview_reasons_for_application/
- [E42] Humanage, Inc. (i-note). Interview techniques for identifying candidates who thrive in mid-career hiring (reproducibility). 2025-05-30. Level C. https://www.i-note.jp/assessment/tekisei-kensa/articles/028.html
- [E43] PMC (primary source: Savickas 2011, APA Career Counseling). Career construction theory: tools, interventions (CCI). 2024. Level A. https://pmc.ncbi.nlm.nih.gov/articles/PMC11026660/
- [E55] Current Directions in Psychological Science. Affective forecasting: Knowing what to want. 2005. Level A. DOI:10.1111/j.0963-7214.2005.00355.x. https://doi.org/10.1111/j.0963-7214.2005.00355.x

<!-- textlint-enable -->
