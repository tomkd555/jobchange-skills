# Job-change market data sources (market-data-sources)

The canonical reference defining the list of public data drawn on to research job-market supply and demand, wages, and job-changer trends, and how to use each. The canonical source for a company-level source is in the `job-change-company-research` skill's `references/source-catalog.md`. This file covers only aggregate figures for an occupation, an industry, or the market as a whole. The definition of evidence levels (A through D) follows that same skill's `references/evidence-grading.md`.

The URLs and update frequencies were confirmed as of August 2026.

## Supply, demand, and the market as a whole

| Name | URL | Update frequency | Where to use it | Level |
|---|---|---|---|---|
| MHLW General Employment Placement Status (一般職業紹介状況) | https://www.mhlw.go.jp/toukei/list/114-1.html | Monthly | Market-wide supply and demand (the Hello Work job-openings-to-applicants ratio) | A |
| MIC Labour Force Survey, detailed tabulation (労働力調査 詳細集計) | https://www.stat.go.jp/data/roudou/sokuhou/nen/dt/index.html | Quarterly/annual | The number of job changers and of those wanting to change jobs | A |
| doda Job-Change Job-Openings-Ratio Report | https://www.saiyo-doda.jp/report/ | Monthly | The job-openings ratio by occupation, industry, and region | B |
| Recruit JBRC Job-Change Market Insight | https://jbrc.recruit.co.jp/ | Quarterly | The year-on-year change in decided wages | B |
| Recruit Works Institute Mid-Career Hiring Survey | https://www.works-i.com/surveys/ | Twice a year | The corporate hiring-outlook diffusion index | B |
| Mynavi Career Research Lab | https://career-research.mynavi.jp/ | Annual/monthly | Reasons for changing jobs, changes in annual salary, hiring criteria | B |
| JILPT Business Labor Trend | https://www.jil.go.jp/kokunai/blt/ | Monthly | Support for interpreting the statistics | B |

## Wages and treatment

| Name | URL | Update frequency | Where to use it | Level |
|---|---|---|---|---|
| MHLW Basic Survey on Wage Structure (賃金構造基本統計調査) | https://www.e-stat.go.jp/stat-search/files?tstat=000001011429 | Annual | The wage distribution by occupation × age × region. The official baseline for judging whether an offered salary is at the going rate | A |
| MHLW Employment Trend Survey (雇用動向調査) | https://www.mhlw.go.jp/toukei/list/9-23-1.html | Annual | The change in wages for those who changed jobs (the share that increased, stayed the same, or decreased) | A |
| MHLW Survey on Employment Trends of Job Changers (転職者実態調査) | https://www.e-stat.go.jp/surveyplan/p00450074001 | Roughly every 5 years | The structure of reasons for leaving and post-change satisfaction | A |
| doda Average Annual Salary Ranking | https://doda.jp/guide/heikin/syokusyu/ | Annual | The average by occupation, based on registrants' actual annual salary | B |
| Kyujin Box Salary Navi | https://xn--pckua2a7gp15o89zb.com/ | As available | The median offered amount by occupation | C |
| OpenWork Salary and Pay Reviews | https://www.openwork.jp/ | As available | The annual-salary distribution by company, based on self-reported figures from current and former employees | C |

The latest edition of the Survey on Employment Trends of Job Changers is the Reiwa 2 survey. The results of the Reiwa 7 survey are not yet published as of August 2026. Kyujin Box Salary Navi itself states that its figures are "a reference value from its own independent estimate," so this alone does not settle the going rate. OpenWork's annual-salary figures are an aggregate of self-reported values and, like Salary Navi, are cited alongside it as a reference value. Because the review text itself requires a login, only the aggregate figures readable without one are used. The robots.txt check on 2026-09-04 showed that company pages are allowed and some paths with a query string are disallowed.

## Public databases that compare companies

These hold company-level values, but each can also be read as a distribution by occupation or industry. For research into one company, follow the `job-change-company-research` skill's `references/source-catalog.md`.

| Name | URL | Update frequency | Where to use it | Level |
|---|---|---|---|---|
| EDINET | https://disclosure2.edinet-fsa.go.jp/ | As available | Human-capital disclosure in the Annual Securities Report (有価証券報告書) | A |
| Shokubaraboo (職場情報総合サイト しょくばらぼ) | https://shokuba.mhlw.go.jp/ | As available | Cross-company comparison of years of continuous employment, overtime hours, and paid-leave uptake | A |
| Database of Companies Advancing Women's Participation | https://positive-ryouritsu.mhlw.go.jp/positivedb/ | As available | The share of female managers, and the average years of continuous employment by gender | A |
| Eruboshi (えるぼし) certification status | https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/0000129028.html | As available | The list of companies certified under the Act on Promotion of Women's Active Engagement | A |
| Kurumin (くるみん, Work-Life Balance Support Plaza) | https://ryouritsu.mhlw.go.jp/ | As available | The list of companies certified under the Act on Advancement of Measures to Support Raising Next-Generation Children | A |
| Job Tag (職業情報提供サイト job tag) | https://shigoto.mhlw.go.jp/User/ | As available | Job decomposition and skill vocabulary | A |
| National Tax Agency Corporate Number Publication Site | https://www.houjin-bangou.nta.go.jp/ | As available | Looking up the registered address and the corporate-number assignment date from a corporate name | A |
| Excellent Health and Productivity Management Corporation (ACTION! 健康経営) | https://kenko-keiei.jp/ | Annual | The list of certified corporations | A |
| Youth Yell (ユースエール) certified companies | The listing page of each prefectural labour bureau | As available | The list of companies certified under the Act on Promotion of Employment of Young People | A |

The assignment date obtainable from the Corporate Number Publication Site is the date the corporate number was assigned. It does not always match the founding year stated in the company profile (for a company that went through a holding-company reorganization or a trade-name change). Do not treat the two as the same; when they diverge, state both. Whether the Excellent Health and Productivity Management Corporation list and the Youth Yell certification list can be obtained with this skill group's tools has not been confirmed (as of 2026-09-04). The Youth Yell certification list is published only as separate PDFs per prefectural labour bureau. Both are treated as a source the user checks themselves and hands over the result for. Failing to obtain one is never read as "not certified."

Four sources in this table cannot be obtained through web fetching (WebFetch, WebSearch): Shokubaraboo, the Database of Companies Advancing Women's Participation, the Work-Life Balance Support Plaza, and Job Tag. The reason and the measurement are canonically defined in the `job-change-company-research` skill's `references/source-catalog.md`, under "Sources that cannot be fetched automatically," and are not duplicated here. Each is a source whose result the user checks themselves and hands over. None of them enter an agent's investigation procedure. **Failing to obtain one is never read as "not listed."**

## Rules of use

1. **A job-openings ratio is a different indicator depending on its source.** The Hello Work basis (General Employment Placement Status, 1.18x in June 2026; https://www.mhlw.go.jp/toukei/list/114-1.html) and the doda basis (2.55x in the same month; https://www.saiyo-doda.jp/report/) draw from different populations. The former counts only the postings and job seekers Hello Work handles; the latter counts only the postings and registrants of that one company's service. Do not compare or mix the two. Always state the source alongside a ratio.

2. **Do not read a high job-openings ratio as "easy to pass."** Companies keep a quality-focused, selective hiring stance. In Mynavi's 2026 Mid-Career Hiring Status Survey, 62.1% of companies (up 7.7 points year on year) answered that they "do not hire" a candidate who does not meet the requirements (https://career-research.mynavi.jp/reserch/20260327_109053/). A large number of postings does not mean an applicant who does not meet the requirements gets through.

3. **Use the Basic Survey on Wage Structure as the official baseline for placing an offered salary against the going rate.** This public statistic can cross-tabulate wages by occupation against factors such as age bracket and company size. This skill group uses it as the baseline. The National Tax Agency's Statistical Survey of Actual Status for Salary is an aggregate by industry and age. It does not give a distribution by occupation, so it is never used as the baseline. The axes actually obtainable differ by e-Stat table, so cite the name of the table drawn from alongside the source. Kyujin Box Salary Navi remains an auxiliary only; when it is cited, state alongside it that it is "that site's own independent-estimate reference value."

4. **Whether a job change raises annual salary depends on age.** Across job changers as a whole, more see it rise than fall. In the Reiwa 6 Employment Trend Survey, the share of job changers whose wage "increased" against their previous job was 40.5%, "decreased" 29.4%, and "unchanged" 28.4% (Summary of Results, Table 6, https://www.mhlw.go.jp/toukei/itiran/roudou/koyou/doukou/25-2/dl/kekka_gaiyo-03.pdf). Reading the same table by age bracket, however, the margin by which "increased" exceeds "decreased" is largest at 36.9 points for age 19 and under, and generally narrows as age rises. The margin fluctuates in between (17.1 points at ages 25 to 29, 22.6 points at ages 45 to 49). At ages 50 to 54 it is 10.8 points, and at ages 55 to 59 the sign reverses to -9.2 points. The amounts show the same tendency. In Mynavi's 2026 Job-Change Trend Survey (surveyed December 2025, 1,446 valid responses), the average annual salary before and after changing jobs moved from 5.145 million yen to 5.337 million yen (+192,000 yen). By age bracket, however, the increase is largest in the thirties at +324,000 yen, while only those in their fifties see a decrease, of -45,000 yen (https://career-research.mynavi.jp/reserch/20260323_108572/).

   Do not place "a job change raises annual salary" as a default premise regardless of age. The boundary differs by survey, however, so treat each age bracket separately. By share, "increased" falls below "decreased" only from ages 55 to 59; at ages 50 to 54, "increased" remains the largest category at 39.0%. By amount, in Mynavi's breakdown by age bracket, only those in their fifties see a decrease. When telling a user in their fifties about the rise or fall in annual salary, present the difference in where this boundary falls across surveys as well. The Employment Trend Survey and the Mynavi survey draw from different populations and measure differently. The Employment Trend Survey is a nationwide survey through establishments, measuring the distribution of increase and decrease. Mynavi surveys job changers themselves, measuring the amount. Do not mix a share and an amount into one claim.
