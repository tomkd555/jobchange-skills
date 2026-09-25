# Canonical investigation procedure for compensation, benefits, and work style (compensation-benefits)

This is the canonical procedure defining the investigation perspectives and source catalog for investigating compensation (topic=compensation), benefits (topic=benefits), and work style (topic=workstyle). Follow `references/evidence-grading.md` for the definition, assignment criteria, and operating rules of evidence levels (A through D); this file does not duplicate that definition. Each source below carries a rough indication of its level.

Collected figures (annual holidays, average monthly overtime, paid-leave-taking rate, average number of paid-leave days taken, average annual salary) must be structured into `company_metrics` in `company_research.json`, in addition to being embedded in a prose claim. The format is in `references/company-research-format.md`, noting the unit, source URL, and level together. Set value to null when it cannot be confirmed.

## Investigation perspectives

### Compensation

| Perspective | Content |
|---|---|
| Compensation structure | Whether a grade system exists, salary ranges, the frequency and basis of bonuses (performance-linked or fixed), the raise mechanism, and various allowances. The recruiting site's compensation-system page and the job posting are primary sources (level A, though an evaluative expression does not guarantee its truth). |
| Average annual salary level | The average annual salary in the securities report's "Status of Employees" section (level A). State in the statement or open_questions that it is a company-wide average lacking a breakdown by job type or employment type (the limits are in `references/source-catalog.md` and `references/evidence-grading.md`). |
| Cross-checking against the job posting's range | Cross-check the range the job posting (job_posting.json) states against the securities report's average annual salary and public statistics' job-type-level figures. Leave a discrepancy in open_questions. |
| Aggregated annual-salary figures from review sites | Use an aggregated annual-salary figure from a review-aggregation site (level C) as supporting evidence, limited to an aggregate resting on a sufficient number of responses. Do not use an individual post or a small-sample aggregate to assert a fact. |

### Benefits

| Perspective | Content |
|---|---|
| Whether a program exists (fact) | Social insurance, retirement benefits, housing assistance, childcare/caregiving support, a cafeteria plan, and so on. The recruiting site and the benefits page are primary sources (level A). |
| Whether a certification exists (fact) | Certifications such as Kurumin, Eruboshi, Health and Productivity Management Outstanding Organization, and Youth Yell are primary information with a clear basis in law and a clear supervising authority (level A). A certification shows only that a minimum standard is met and does not guarantee overall ease of working. Do not assert "an easy place to work" on the grounds of a certification alone. |
| Distinguishing a program from its use | A program's "existing" and its "being used" are different things. Cross-check it against actual-use figures (workstyle) such as the childcare-leave-taking rate and the paid-leave-taking rate. |

### Work style

| Perspective | Content |
|---|---|
| Working hours and overtime | Scheduled working hours, average monthly hours of overtime, and the policy on discretionary work, flextime, and remote work. Shokuba Labo's voluntary disclosure (level A), the job posting, Shushoku Shikiho (level B). |
| Leave | Annual holidays, paid-leave-taking rate, average number of paid-leave days taken. Shokuba Labo, Shushoku Shikiho, the job posting. |
| Retention | The 3-year retention rate, average years of service. Shushoku Shikiho (level B), the securities report's average years of service (level A). |
| Review-site evaluations of work style | Reviews of actual overtime and ease of taking leave (level C) are usable as conditional supporting evidence, limited to an aggregated overall score. An individual post is not used to assert a fact, because it is skewed to the extreme by selection bias. |

## Source catalog

### Primary and official (level A)

| Source | Mainly reveals | topic | Source URL |
|---|---|---|---|
| EDINET securities report, "Status of Employees" | Average annual salary, average years of service, average age, employee count | compensation/financials/workstyle | Viewing site https://disclosure2.edinet-fsa.go.jp/WEEK0010.aspx (About EDINET https://www.fsa.go.jp/search/20130917.html ) |
| Ministry of Health, Labour and Welfare's "Shokuba Labo" | Mid-career hiring ratio, retention rate, average monthly hours of scheduled-outside labour, paid-leave-taking rate (the company's own voluntary disclosure) | workstyle/benefits | https://shokuba.mhlw.go.jp/ |
| The recruiting site's compensation-system and benefits pages | Grade system, salary range, bonus formula, allowances, benefit programs | compensation/benefits | Each company's own domain (a page the company itself owns; do not set confidence to high for an evaluative expression) |
| Kurumin / Platinum Kurumin / Try Kurumin | Certification for next-generation child-rearing support | benefits | https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/kodomo/shokuba_kosodate/kurumin/index.html |
| Eruboshi / Platinum Eruboshi | Certification for promoting women's active participation (5 criteria) | benefits/workstyle | https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/0000091025_00002.html |
| Health and Productivity Management Outstanding Organization (White 500) | Recognition for health and productivity management | benefits | https://www.meti.go.jp/policy/mono_info_service/healthcare/kenkoukeiei_yuryouhouzin.html |
| Youth Yell | Certification for small and mid-sized enterprises active in hiring and developing young workers | benefits/workstyle | https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/0000100266.html |

Whether a certification exists is a fact (level A), but a certification shows only that a minimum standard is met and does not guarantee the company's overall ease of working.

### Reliable secondary (level B)

| Source | Mainly reveals | topic | Source URL |
|---|---|---|---|
| Shushoku Shikiho (Toyo Keizai Inc.) | 3-year retention rate, average annual salary, overtime hours, paid-leave-taking (an independent survey published free of charge) | workstyle/compensation/reputation | https://str.toyokeizai.net/magazine/shushoku_all/ |

A major news outlet's reporting and an industry association's report are also treated as level-B secondary information, being secondary information edited from primary material.

### Review and aggregation sites (level C)

| Source | Mainly reveals | topic | Source URL |
|---|---|---|---|
| OpenWork | Aggregated annual-salary figures, actual overtime, paid-leave-taking, and an overall evaluation of treatment (submission of proof of employment and manual screening required) | compensation/workstyle/reputation | https://www.openwork.jp/ |

Use a review-site post as supporting evidence on three conditions: it is an aggregated overall score across many respondents, it rests on a sufficient number of responses, and it can be corroborated across multiple sources. Do not use an individual post, a small-sample aggregate, or a per-facet score to assert a fact (the grounds and limits are in "The conditional validity of an aggregated overall score" and "The selection bias of review-site posts" in `references/evidence-grading.md`).

## Public statistics for comparing salary levels (a reference point)

Public statistics serve as a reference point for placing a single company's average annual salary (from its securities report) against industry, occupation, and age-group levels. Both are public statistics and are treated as fact at level A.

| Statistic | Supervising authority | Mainly reveals | Source URL |
|---|---|---|---|
| Basic Survey on Wage Structure | Ministry of Health, Labour and Welfare | Wages by occupation, age group, company size, and industry (scheduled cash earnings, annual special cash earnings) | Overview https://www.mhlw.go.jp/toukei/list/chinginkouzou.html / Data (e-Stat) https://www.e-stat.go.jp/statistics/00450091 |
| Statistical Survey of Actual Status for Salary in the Private Sector | National Tax Agency | Average salary of salaried workers (by sex, employment type, company size, industry) | https://www.nta.go.jp/publication/statistics/kokuzeicho/minkan/top.htm |

Limits of the comparison: a securities report's average annual salary is a company-wide average lacking a breakdown by job type, so a comparison against public statistics' job-type-level and age-group-level figures is an approximate comparison across differing conditions. Keep the comparison to grasping a level, and do not assert a simple ranking of superiority. Leave this limit in open_questions.

## Reflecting this in claims and company_metrics

- Once you collect a figure (annual holidays, overtime, paid-leave-taking rate, average number of paid-leave days taken, average annual salary), build the corresponding claim, and in addition structure it into `company_metrics` (value, unit, source_url, grade, as_of).
- Make a program's "existence" a factual claim (example: 「健康経営優良法人2026に認定されている」 grade=A; a certification scheme's published data is primary information from the certifying body). A program's "merit" is an evaluation; do not assert it.
- Leave a discrepancy between the job posting's range and the securities report's average annual salary or public statistics in open_questions.
