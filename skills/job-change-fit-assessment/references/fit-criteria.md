# Fit-assessment judgement criteria (fit-criteria)

This defines the judgement criteria for `fit_assessment.json`'s seven dimensions (experience_proximity / aspiration_alignment / work_character_fit / condition_fit / culture_fit / compensation_fit / time_fit). The canonical definition of the data structure and validation rules is in `references/fit-format.md`, and of evidence levels A–D in the `job-change-company-research` skill's `references/evidence-grading.md`.

## Rules common to every dimension

1. **Do not write a claim with no evidence.** Ground each dimension's verdict in evidence (one or more items), and do not reflect an unsupported impression or guess into the score or verdict.
2. **Do not assert a verdict from level C or D evidence alone.** Do not assert a dimension high or low on word-of-mouth or hearsay (a claim inside company_research graded C or D) alone. When grounding a verdict in C or D evidence, hedge the wording (「口コミでは〜という声がある。傍証にとどめる」). Follow evidence-grading.md for the level definitions and how to hedge.
3. **Do not treat a company's self-flattering claim as established.** A recruiting-site claim such as 「風通しが良い」 (an open culture) does not have its confidence marked high by the company_research side, even at level A. Do not use this as grounds for asserting culture_fit.
4. **Set the score to null (hold judgement) when material is lacking.** Do not fill in a number by guesswork. Keep to the policy of preferring unknown.
5. **Do not invent a fact absent from profile, the axis or self_analysis.** Ground the person's career, strengths, and conditions in what profile.json, `{AXIS}` and self_analysis.json record.

## General guidance for the score of 1–5

| score | Meaning |
|---|---|
| 5 | Requirements, conditions, and aspiration nearly all match. Grounds are complete |
| 4 | Broadly matches. A minor gap or unconfirmed point exists |
| 3 | Partially matches. Strengths and weaknesses roughly balance |
| 2 | Mismatch predominates. A commensurate concern exists |
| 1 | Clearly mismatched. A serious obstacle exists |
| null | Judgement material is insufficient; no number can be attached (hold judgement) |

## Criteria by dimension

### experience_proximity (experience proximity)

Cross-check job_posting's `requirements.must[]` and `requirements.want[]` against profile's `career_history` and `skills`, and measure the **distance from current experience**.

- Place must-have requirement fulfilment at the centre. Do not give a high score when a must-have requirement is unmet.
- Treat fulfilment of a nice-to-have requirement (want) as a plus.
- Use years of experience and achievements (the `metric` of profile's achievements) as evidence.
- Write each missing requirement into `skill_gap_items`, and express `skill_gap` in three stages (plus `none` and `unknown`). The criteria for the stages are as follows.

| Stage | Criterion |
|---|---|
| `complementable_within_3m` | Has hands-on experience with an adjacent technology, and the learning need is limited to the specific gap. Reachable within three months through self-study and applying it on the job |
| `needs_6_12m_study` | Adjacent experience is thin and systematic study is needed. Or a separate opportunity to apply it on the job must be created |
| `not_applicable_now` | The core of a must-have requirement (years of experience, hands-on work in a specific area) is unmet, and short-term study will not fill it |

- **This dimension does not include "do they want to."** Do not use closeness of experience as grounds for wanting that job. Evaluate aspiration separately, in `aspiration_alignment`.
- Evidence sources are mainly `job_posting` and `profile`.

### aspiration_alignment (aspiration alignment)

Evaluate whether the job's duties are close to "the work they want to do going forward," **independently of experience proximity**.

- Treat self_analysis's `career_narrative.future_direction` as the primary source, and look at the overlap between `interests.domains` (RIASEC domain names) and `interests.concrete_topics` and the job's technical and product areas.
- Treat `job_change_axis.reasons` in `{AXIS}` (what they want to achieve next through the job change) as a supporting source.
- **Do not divert experience proximity into grounds for aspiration.** The inference "they have experience, so it must match their aspiration too" is explicitly prohibited.
- When there is no self-analysis (`inputs.self_analysis=false`), do not raise the score. A score of 4 or higher is not allowed.
- Evidence must always include `self_analysis` or `profile`. Do not assert aspiration from the job posting alone.
- Write evidence's `ref` as a field path, such as `interests.domains[0]` or `career_narrative.future_direction`.

### work_character_fit (work-character match)

Cross-check `{AXIS}`'s `work_character_preferences[]` (the desired degree for eight work characteristics) against the job and company's reality. The characteristic definitions are in job-change-support's `references/screening-axes.md`.

- When the job has gone through job search (`inputs.job_search_screening=true`), use `job_search_results.json`'s `axis_observations` (the ratio of hands-on work, the ratio of coordination work, remote-work confidence, night-time response) as evidence.
- When it has not, read the same points from job_posting's duty description and company_research's working style.
- **Do not fill in the three characteristics that cannot be judged from the job posting by guessing.** The three are `clear_completion` (clarity of completion criteria), `solo_completable` (ease of completing work solo), and `short_feedback` (how soon results can be confirmed). The job posting and the company research almost never mention them. State plainly in the verdict 「求人票・企業研究からは判定できない」 (cannot be judged from the job posting or company research), and raise it in `overall.open_questions` as an interview-confirmation item.
- Do not raise the score when a characteristic whose desired degree is `must` is unmet. That characteristic also becomes `met=no` in `must_condition_results`.
- Evidence sources are mainly `job_search_screening`, `job_posting`, `company_research`, and `profile`.

### condition_fit (condition match)

Cross-check job_posting's working conditions (`location`, `employment_type`, `working_hours`, etc.) against `{AXIS}`'s `conditions[level=want]` and `targets`. Since fulfilment of must-have conditions is judged separately in `must_condition_results`, this dimension covers alignment with desirable conditions and the target areas (`targets`).

- Look at how well conditions such as remote eligibility, work location, employment type, and discretionary work arrangements match the person's desired conditions.
- Add job_posting's `scope_of_change` as material when looking at work-location and job-type conditions (described below).
- Evidence sources are mainly `job_posting` and `profile`.

#### Handling scope_of_change (the scope of change)

job_posting's `scope_of_change` structures the three items whose disclosure in job postings became mandatory from April 2024 (the scope of change in duties, the scope of change in work location, and the cap on fixed-term contract renewal). Its canonical format is in `job-change-company-research`'s `references/job-posting-format.md`.

| State | Handling |
|---|---|
| `work_location.unlimited` is true | Include as a relocation risk in `condition_fit`'s evidence. Write into the verdict that the work location is not guaranteed to stay at the location assigned at hiring |
| `duties.unlimited` is true | Handle the same way, as a job-transfer risk. Write that the current duties are not guaranteed to continue |
| `contract_renewal_cap.stated` is true and a cap exists | Treat as the upper limit on a fixed-term contract's duration, as material for judging the employment-type condition |
| Either is `null` | Leave as unknown. **Do not treat failing to find a mention as evidence that the scope is limited.** Put the confirmation item into `overall.open_questions` |

Write evidence in the form `{"source": "job_posting", "ref": "scope_of_change.work_location.unlimited", "note": "…"}`, with `ref` as the field path and `note` transcribing the `quote` (the job posting's wording).

`unlimited` being true records only that the company may order relocation or a job transfer at its discretion. Write the verdict so it keeps this discretion apart from a confirmed relocation or job transfer.

When `job_posting.json`'s `schema_version` is `1.0`, `scope_of_change` is absent, since the scope of change in duties and in work location was not looked at when the posting was taken in. Do not change the judgement. Put 「求人票の取り込みが旧形式であり、業務・就業場所の変更の範囲を確認していない」 into `overall.open_questions`.

### culture_fit (culture match)

Cross-check company_research's philosophy, workstyle, and reputation topics against self_analysis's behavioural evidence and values.

- **Do not place heavy weight on introspection alone.** Do not assert from self_analysis's subjective self-report alone. Prioritise correspondence with the behavioural evidence recorded in self_analysis (specific past actions and achievements).
- Treat the company's own self-flattering claims (level A ones whose confidence is not high) as separate from facts (the existence of a system, a disclosed figure, a certification), and do not use the former as grounds for an assertion.
- Keep word-of-mouth sources (level C) hedged.
- When there is no self-analysis (inputs.self_analysis=false), do not raise the score, since behavioural evidence is lacking; write that into the verdict, or set it to null.
- Evidence sources are mainly `company_research` and `self_analysis`.

### compensation_fit (compensation match)

Cross-check desired annual salary against the offered range and the industry average.

- Cross-check job_posting's `salary` (the offered range) against `{AXIS}`'s `salary.desired` (desired annual salary).
- Add company_research's `company_metrics.compensation_level` (the average annual salary from the securities report, etc.) as a reference point. However, this value is a company-wide average with no breakdown by job type. Write that limit into the verdict or overall.open_questions.
- Do not raise the score when the offered range's lower bound falls below the desired amount. Also factor in the gap to the upper bound and the uncertainty of room for raises.
- If time_analysis.json has `comparison`, ground the verdict in the difference in effective hourly wage from the current job (`comparison.delta.hourly_wage_binding_basis` and the same for `labor_basis`). Do not raise the score on the increase in nominal annual salary alone.
- Evidence sources are mainly `job_posting`, `profile`, `company_research`, and `time_analysis`.

### time_fit (time match)

Cross-check time_analysis.json's annual committed time and effective hourly wage against the must/want conditions concerning overtime, commute, and working hours.

- Treat time_analysis.json's `annual.binding_hours` (annual committed time), `annual.labor_hours` (annual working hours), and `effective_hourly_wage` (effective hourly wage, on a committed-time basis and a labor basis) as the primary material.
- The effective hourly wage is computed only when a leveled basis for the expected annual salary exists (otherwise it is null on the time_analysis side). When it is null, do not use an amount comparison to assert.
- For an item in time_analysis's input where a statistical fallback was used (`fallbacks_used`), reflect in the verdict that it is not measured, and do not overstate confidence.
- Look at alignment with must/want conditions concerning overtime, commute, and working hours.
- If time_analysis.json has `comparison`, ground the verdict in the difference in annual committed time from the current job (`comparison.delta.annual_binding_hours`). If `comparison` is absent, write into the verdict that a comparison with the current job could not be made.
- Do not represent commute burden by time alone. If commute.json has `transfers` (number of transfers) or `crowding` (degree of crowding), touch on them in the verdict. Write into the verdict, when the one-way commute is long, that a longer commute cuts into sleep and exercise time, so it does not necessarily offset against a difference in salary (grounds in `references/fit-methods.md`).
- Evidence sources are mainly `time_analysis` and `job_posting`.

## Judging must_condition_results

Cross-check each of the must-have conditions in `{AXIS}` (`conditions[level=must]` and `work_character_preferences[desire=must]`) against the facts in job_posting and company_research, judge each `yes`, `no`, or `unknown`, and match them one-to-one by `ref` (a condition ID or a characteristic ID).

- Mark `yes` or `no` only when the job posting or company research carries clear grounds, and always attach that evidence.
- Mark `unknown` for a condition where grounds cannot be found (do not guess yes/no). An `unknown` condition may leave evidence empty.
- **For a must-have condition about work location or remote work, also look at `scope_of_change.work_location` when judging.** Even when the job posting's work location satisfies the condition, if `work_location.unlimited` is true, the condition is fulfilled only as of hiring. In this case, do not set `met` to `unknown`; set it to `yes`, add `scope_of_change.work_location.unlimited` to evidence, and write into `note` that fulfilment could be lost through a change of work location. When the job posting's work location does not satisfy the condition and `unlimited` is true, leave `met=no`. Handle the relationship between a must-have condition about job type or duties and `duties.unlimited` the same way.
- When the corresponding `scope_of_change` item is `null`, do not use that item as grounds. Do not treat failing to find a mention as grounds that the scope is limited.
- Set `negotiable` to `true` only when a `met=no` condition can be resolved through negotiation or how a system is run. Attach grounds (a past negotiation example, a system's stated rule) to evidence. Do not attach `true` without grounds.
- Marking the overall verdict `推奨` while a must-have condition has `no` is not allowed (ERROR).

## overall (overall verdict)

Combine the seven dimensions' scores and must_condition_results, and attach one of `推奨`, `条件付き推奨`, `非推奨`, or `判断保留`.

| Situation | Verdict |
|---|---|
| Every must-have condition is met, and the main dimensions score high | `推奨` |
| The main fit holds but an unconfirmed condition remains. Or every `met=no` item has `negotiable=true` (with grounds) | `条件付き推奨` |
| Mismatch predominates. Or a must-have condition that negotiation cannot resolve remains | `非推奨` |
| Input is thin (most of `inputs` is false) and judgement material is insufficient | `判断保留` |

- **Do not recommend on closeness of experience alone.** Even when `experience_proximity` scores high, if `aspiration_alignment` or `work_character_fit` scores low, state that plainly in the rationale, and do not let the high `experience_proximity` score cancel it out. A job centred on coordination, management, or client negotiation can be close to the person's experience while running against their aspiration.
- Do not mark `推奨` or `条件付き推奨` when `skill_gap` is `not_applicable_now`.
- In rationale, write what tipped the verdict, and, when conditional, what condition must be resolved. List unconfirmed points under `open_questions`. Always put a work characteristic that cannot be judged from the job posting (clarity of completion criteria, ease of completing work solo, how soon results can be confirmed) into `open_questions` as an interview-confirmation item.
- **Always put how the direct manager is involved into `open_questions`.** In the Japanese employee sample, manager fit shapes retention and satisfaction, but it cannot be judged from the job posting and company research. Do not create an eighth dimension for it, and do not add it to `culture_fit`'s score; raise it as an interview-confirmation item (grounds in `references/fit-methods.md`).
- **State clearly in rationale that the verdict is based on the material at that point.** The verdict is based on the material available at this point, and high satisfaction right after joining does not necessarily last. Place this note at the end of rationale (grounds in `references/fit-methods.md`).
