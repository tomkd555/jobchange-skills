# Source catalog (source-catalog)

This is the canonical catalog organizing the sources used in researching a Japanese company, together with their category, content, limits, and source URL. Follow `references/evidence-grading.md` for the definition of evidence levels (A through D). Each source's content corresponds to a claim's topic.

## Primary and official (level A)

### EDINET securities report, "Status of Employees"

| Perspective | Content |
|---|---|
| Location | Viewable at the Financial Services Agency's EDINET (no charge). https://www.fsa.go.jp/search/20130917.html (About EDINET). |
| Content | "Part I: Company Information / 1. Company Overview / 5. Status of Employees" states the filing company's employee count, average age, average years of service, and average annual salary (topic=financials). This is the source of the quantitative candidate axis `compensation_level`. |
| Definition and limits of the average annual salary | Under the disclosure ordinance, it is uniformly defined by law to include bonuses and exclude officers and temporary employees. Non-scheduled wages (overtime pay, allowances), however, and the treatment of part-time workers are each company's own discretion, and the figure is a company-wide average lacking a breakdown by job type or employment type. A simple comparison between companies has limits, so state this fact in the statement or in open_questions (a commentary on the calculation method: Kabushiki Soumu 2023, level C https://kabushikisoumu.com/annual-income-4 ). |
| The 3 human-capital indicators | Starting with securities reports for fiscal years ending March 2023 and later, under the revised disclosure ordinance, a filing company subject to a publication obligation under the Act on Promotion of Women's Active Engagement in Professional Life or the Child Care and Family Care Leave Act states the female-manager ratio, the male childcare-leave-taking rate, and the gender wage gap in "Status of Employees" (Financial Services Agency https://www.fsa.go.jp/policy/kaiji/sustainability-kaiji.html ). This is the source of the quantitative candidate axis `male_childcare_leave_rate` (topic=workstyle/benefits). |
| Items added from fiscal years ending March 2026 and later | Under the disclosure-ordinance revision promulgated February 20, 2026, a securities report for a fiscal year ending March 2026 or later (to be filed from around June 2026) adds a human-resources strategy, the policy for determining employee compensation and similar, and the filing company's year-over-year rate of change in average employee compensation (Financial Services Agency https://www.fsa.go.jp/news/r7/shouken/20260220/20260220.html ). The rate of change in average compensation supports the trend of `compensation_level`; the determination policy supports topic=compensation; the human-resources strategy supports topic=business/philosophy. |
| How to identify a document | An EDINET document can be uniquely identified by its document management number. For a claim sourced from a securities report, recording the document management number and the filing date makes it easier to cross-check at audit time. |

When researching a listed company, include the human-capital disclosures above among what you check. All are statutory disclosures and can be treated as level-A figures, and can later be corroborated by opening the same securities report again. When you cannot find the disclosure, you cannot distinguish between the filing company being exempt from the publication obligation and a simple oversight, so record in `open_questions` that "the relevant part of the securities report was checked but the disclosure could not be found."

### The obligation to publish the mid-career hiring ratio

Under the Act on Comprehensive Promotion of Labor Measures, a company that regularly employs 301 or more workers has an obligation to publish its mid-career hiring ratio (the share of mid-career hires among the hires of regular employees) for the most recent 3 fiscal years, roughly once a year (effective April 2021. Ministry of Health, Labour and Welfare https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/koyou_roudou/koyou/jakunen/index_00003.html ). The publication location may be either the company's own site or Shokuba Labo.

When you find a published figure, make it a level-A factual claim (topic=workstyle). When the company has 301 or more employees but you could not find a published figure, record that fact itself in `open_questions`. **Do not assert that it is unpublished.** The law does not fix a single publication location, and this means the search's completeness cannot be guaranteed.

The securities report's "Part I: Company Information / 1. Company Overview / 1. Trends in Major Management Indicators" lists revenue and the equity ratio across the most recent 5 fiscal years side by side. The quantitative candidate axis `revenue_growth` is calculated from this revenue trend, and `equity_ratio` uses the value in this table directly. `operating_margin` is calculated from the consolidated income statement's operating profit and revenue in "Status of Accounting." For a calculated value, write the fiscal period and figures used in the calculation into the statement, and set the source to the relevant part of the securities report.

### Earnings briefing materials, integrated reports, medium-term management plans, corporate governance reports

A company's disclosure falls into three categories: statutory disclosure, timely disclosure, and voluntary disclosure (Funda Navi 2024, level C https://navi.funda.jp/article/disclosure ).

| Material | Content |
|---|---|
| Earnings briefing materials, integrated reports, medium-term management plans, annual reports | Voluntary disclosure (IR information). Grounds for the business description, results, strategy, and philosophy (topic=business/financials/philosophy). Note that, because the speaker is the party itself, the description can be biased toward presenting the company favorably. |
| Corporate governance report | A listed company submits this to the Tokyo Stock Exchange on a comply-or-explain basis (Japan Exchange Group, level B https://www.jpx.co.jp/equities/listing/cg/index.html ). Grounds for board composition and the governance structure. |

These are primary information from the company itself, and a fact (a number, a structure, whether a program exists) is treated as level A. On the other hand, how far a philosophy or purpose has been "realized," and self-praise about company culture, are evaluative claims, and confidence is not set to high on them (see `references/evidence-grading.md`).

### Ministry of Health, Labour and Welfare's "Shokuba Labo"

| Perspective | Content |
|---|---|
| Location | https://shokuba.mhlw.go.jp/ (the Comprehensive Workplace Information Site). |
| Content | The mid-career hiring ratio, retention rate, overtime hours, paid-leave-taking rate, and similar (topic=workstyle). This is the source of the quantitative candidate axes `turnover_rate`, `monthly_overtime`, and `paid_leave_rate`. |
| Limits | The listed content depends on the company's own voluntary disclosure. An undisclosed item cannot be determined. A disclosed figure is treated as primary information. |
| How to obtain it | It requires operating a search form, so it cannot be pulled by a web fetch alone (see "Sources that cannot be fetched automatically" below). The result is received from the user, who consulted it themselves. |

### Certification schemes (primary information with a clear basis in law and a clear supervising authority)

Every one has a clear basis in law and a clear supervising authority, and whether a certification exists is itself a level-A fact (topic=benefits/workstyle).

<!-- textlint-disable ja-technical-writing/max-kanji-continuous-len -->
<!-- This table carries law names in their original Japanese; the long kanji run in "次世代育成支援対策推進法" (Act on Advancement of Measures to Support Raising Next-Generation Children) is allowed only in this table. -->

| Certification | Legal basis and supervising authority | Source URL |
|---|---|---|
| Kurumin / Platinum Kurumin / Try Kurumin | Act on Advancement of Measures to Support Raising Next-Generation Children, Ministry of Health, Labour and Welfare | https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/kodomo/shokuba_kosodate/kurumin/index.html |
| Eruboshi / Platinum Eruboshi | Act on Promotion of Women's Active Engagement in Professional Life (5 criteria), Ministry of Health, Labour and Welfare | https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/0000091025_00002.html |
| Health and Productivity Management Outstanding Organization (White 500) | Ministry of Economy, Trade and Industry and the Japan Health Council (established fiscal 2016; the top 500 in the large-enterprise category are "White 500") | https://www.meti.go.jp/policy/mono_info_service/healthcare/kenkoukeiei_yuryouhouzin.html |
| Youth Yell | Act on Promotion of Employment of Young People, Ministry of Health, Labour and Welfare (for small and mid-sized enterprises) | https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/0000100266.html |

<!-- textlint-enable ja-technical-writing/max-kanji-continuous-len -->

Whether a certification exists is a fact, but a certification shows only that a minimum standard is met; it does not guarantee the company's overall ease of working. Do not assert "an easy place to work" on the grounds of a certification alone.

The following databases hold whether an individual company is certified, and the figures behind the certification. Among these, "Ryoritsu Support Plaza" and the "Database of Companies Promoting Women's Active Participation" cannot be pulled by an agent through a web fetch alone (see "Sources that cannot be fetched automatically" below). They are sources whose result the user consults themselves and hands over, and they are not included in the investigation procedure.

| Database | Content | Source URL |
|---|---|---|
| Eruboshi certification status | A list of companies certified Eruboshi or Platinum Eruboshi (topic=workstyle/benefits) | https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/0000129028.html |
| Ryoritsu Support Plaza | Kurumin-certified companies and each company's general employer action plan for work-life balance support (topic=benefits) | https://ryouritsu.mhlw.go.jp/ |
| Database of Companies Promoting Women's Active Participation | The female-manager ratio, average years of service by sex, and the female share among new hires (topic=workstyle) | https://positive-ryouritsu.mhlw.go.jp/positivedb/ |

The Eruboshi certification status page is an ordinary Ministry of Health, Labour and Welfare page, and it can be pulled by a web fetch.

### Why negative information is sought

Collecting only a company's self-disclosure and recruiting communications produces a picture skewed toward the favorable. A study of Japanese job changers, too, confirms that a gap between pre-hire expectations and post-hire reality undermines retention. 片山と藤 (2023), in a survey of 412 job changers, showed that a reality shock at the time of a job change lowers work engagement and raises turnover intention (DOI:10.4992/jjpsy.93.20062). On the company-side measure of a realistic job preview, there is a meta-analysis by Phillips (1998), but this addresses the scene where a company gives information to an applicant, and does not directly transfer to the applicant's own side of information-gathering. The original text's effect size could not be obtained, and this catalog relies on a secondary source for it.

Negative information is therefore sought through the same procedure as positive information. The following sources serve that purpose.

### Ministry of Health, Labour and Welfare's "Published cases of violations of labor-standards laws"

| Perspective | Content |
|---|---|
| Location | Published by the prefectural labour bureaus, and compiled nationally on a monthly basis by the ministry. The starting page is https://www.mhlw.go.jp/kinkyu/151106.html . The ministry's compilation is published as a PDF. |
| Content | The company or workplace's name, its location, the publication date, the violated provision, and a summary of the case (topic=workstyle/reputation). Covers cases referred for prosecution and cases with a director's instruction. |
| Limit on the listing period | Under the governing notice (基発0330第11号), the listing period is roughly 1 year from the publication date, and a case is removed at the end of the first month after 1 year has passed. A case from more than 1 year ago is not listed. |
| Limit on searching | Neither the site nor the PDF has a function to filter by company name. You must fetch the monthly national PDF and search it. There is no table data in the HTML, and fetching the PDF is required. |
| How to use it | When a match is found, treat it as a level-A fact. **Do not use the absence of a match as evidence that no legal violation exists.** Because of the two limits above, a violation can exist even when the company is unlisted. |

### Public statistics (Basic Survey on Wage Structure, Employment Trend Survey, job tag)

These sources give aggregate values by occupation and by industry. Use them as a reference point for seeing how far an individual company's offered terms are from the level for the same occupation or industry. The canonical source for their origin, update frequency, whether they can be fetched, and their usage rules is the hub's `{HUB_SKILL_DIR}/references/market-data-sources.md`; it is not duplicated here.

These are occupation-level and industry-level statistics, so they stay out of `claims`. Use them within a statement as the baseline for comparison when evaluating a level of compensation or work style. Because job tag shows the same annual-salary figure for several IT occupations, do not evaluate an individual job posting's offered amount on the grounds of a matching occupation name alone.

## Sources that cannot be fetched automatically

Some sources hold company-level information but cannot be pulled by a web fetch alone. What was actually confirmed is as follows.

| Source | Why it cannot be pulled |
|---|---|
| Shokuba Labo | Its search form does not work with GET parameters. It also forbids direct access to an individual company's page. |
| Database of Companies Promoting Women's Active Participation | Every path returns 403, and the body cannot be fetched. |
| Ryoritsu Support Plaza | Same as above. |
| job tag (the Occupational Information Provision Site) | Both the body and the download page are rendered with JavaScript, and the fetch result comes back empty. Obtaining the CSV requires a manual download by the user. |

Treat these as sources the user consults personally and hands to the agent, and leave them out of the agent's investigation procedure. **Do not interpret an inability to fetch as "nothing is listed."**

## Reliable secondary (level B)

### Shushoku Shikiho

| Perspective | Content |
|---|---|
| Location | Toyo Keizai Inc. https://str.toyokeizai.net/magazine/shushoku_all/ . |
| Character | Covers roughly 1,300 companies through its own survey, charging no listing fee (3-year retention rate, average annual salary, overtime hours, paid-leave-taking, and so on). Its editorial policy of a free listing fee and its own independent survey lead to treating it as secondary information independent of the company's own public relations (topic=reputation/workstyle/financials). |
| Limits | A company may decline to answer a survey item, leaving it blank. The number of companies listed is limited, and an unlisted company cannot be supplemented. |

Total annual holidays (the quantitative candidate axis `annual_holidays`) is mainly sourced from the job posting, and can also be confirmed in Shushoku Shikiho's holidays-and-leave column. State in the statement that the job posting's value is the condition for the recruited job type alone.

### Major reporting, industry reports

An article from a major news outlet, and a report from an industry association or a research firm, are treated as level-B secondary information, being secondary information edited from primary material. A personal blog or an anonymous repost is treated as level D, distinguished from these.

## Review-aggregation sites (level C)

| Perspective | Content |
|---|---|
| Representative examples | OpenWork, Glassdoor, and sites aggregating selection-process accounts. |
| Character and limits | Because whether to post is the poster's own decision, an extreme opinion is more likely to be posted (selection bias). An individual post, a metric with a small response count, or a facet-level metric is not used to assert a fact. An overall score aggregated across many respondents can be used as supporting evidence for a trend, on the condition that it rests on a sufficient number of responses and can be cross-checked against another source (see "The conditional validity of an aggregated overall score" in `references/evidence-grading.md`; the r=.516 figure comes from the single study by Landers 2019). |
| Quality differences among sites | OpenWork requires submission of proof of employment and manual screening, so a poster's authenticity is comparatively higher, though a leaver bias remains. Treat every aggregation site as level C, and keep the principle of using the overall score as supporting evidence (Job-Hunting Handbook 2024 https://jo-katsu.com/campus/10412/ ). |
| How to write it | Write a statement based on C with a hedge. 「口コミでは〜という声がある（回答 N 件）。選択バイアスがあり傍証にとどめる。」 |

## Personal blog, hearsay, unconfirmed (level D)

A personal blog, hearsay on social media, a repost of unknown origin, and a single anonymous post are level D. Do not assert a fact on D alone. Mention it only as a supplement, limited to cases where another level-A or level-B source corroborates it.

## Correspondence between topic and source

| topic | Main primary and secondary sources |
|---|---|
| `philosophy` | The company's official-site philosophy page, the integrated report, messages from the president (`references/philosophy-analysis.md`) |
| `business` | The securities report, earnings briefing materials, the integrated report |
| `financials` | The securities report's "Status of Employees," earnings materials |
| `compensation` | The recruiting site's compensation system, the securities report's average annual salary, review-site aggregates (supporting evidence) |
| `benefits` | Certification-scheme databases, Shokuba Labo, the benefits page |
| `workstyle` | The securities report's human-capital disclosures, the published mid-career hiring ratio, Shokuba Labo, Shushoku Shikiho, the Database of Companies Promoting Women's Active Participation, the corporate governance report, published cases of labour-standards violations |
| `reputation` | Shushoku Shikiho, major reporting, published cases of labour-standards violations, review-site aggregates (supporting evidence) |
| `selection_process` | The recruiting site's selection flow, aggregated selection-process accounts, reviews (whether each site can be fetched is in the next section) |

## Sources for the selection process (selection_process)

Among sites that collect the questions asked at interview and the selection format, the range readable without login and the range robots.txt allows to be fetched automatically differ greatly. The company research role's Step 4 and the interview-information investigator (`job-change-interview-scout`) follow the same table. It was checked on 2026-09-04, and robots.txt should be re-read once 180 days have passed.

| Site | Whether interview questions exist | Range readable without login | robots.txt (as of 2026-09-04) | Level | Fetching |
|---|---|---|---|---|---|
| Tenshoku Kaigi (`jobtalk.jp`) | Yes. `/companies/{ID}/answers?question_codes=examination` is the interview/exam category | Fragments of question text can be read. The body on interview atmosphere, preparation, and outcome requires registration | `User-agent: *` has `Allow: /`. Disallow covers only `/company_archives/`, `/jobs/p*`, and the image proxy paths. No mention of naming an AI crawler | C | Allowed |
| Careerconnection (`careerconnection.jp`) | Yes. `/review/{ID}/interview/` | About 1 item per company is readable; the rest requires registration. Many posts are old (2010s) | `User-agent: ClaudeBot` has only `Crawl-delay: 3`; no Disallow. `User-agent: *`'s Disallow covers paths such as voting, reporting, and job details | C | Allowed (space fetches at least 3 seconds apart) |
| OpenWork (`openwork.jp`) | **None**. Of its 9 categories (組織体制・企業文化／年収・給与／入社理由と入社後ギャップ／働きがい・成長／女性の働きやすさ／ワーク・ライフ・バランス／退職検討理由／企業分析／経営者への提言), none is an interview category | Category names and the count per category. The body requires registration | Company pages are not among the disallowed. Some paths with a query string and `/landing/` are disallowed. No mention of naming an AI crawler | C (the Institute for Job Satisfaction's aggregated reports are B) | Allowed. Limited to the grounds for `themes` (trends) and the counts for post-join gap and reasons considered for leaving |
| en Lighthouse (`en-hyouban.com`) | Yes (inferred from search-result fragments; the body is unconfirmed) | Unconfirmed | **`User-agent: ClaudeBot` / `Disallow: /`**. Names the crawler and refuses the entire site | C | **Not allowed**. Do not fetch it even via a `site:` search |
| Glassdoor Japan (`glassdoor.co.jp`) | Yes, though the count for domestic companies is small | Unconfirmed | `/robots.txt` returns HTTP 530 and cannot be read | C | Not allowed (do not treat a site whose policy cannot be read as permitted) |
| Indeed Company Reviews (`jp.indeed.com/cmp/`) | Yes, though the count is small | Unconfirmed | The file is large, and the tool could not confirm its content. `ClaudeBot` is on the list of crawlers used for training | C | Not allowed (until the content can be confirmed) |
| Shukatsu Kaigi (`syukatsu-kaigi.jp`), ONE CAREER (`onecareer.jp`) | Yes. Accounts from **new-graduate** hiring | A summary is readable. The body requires registration | ONE CAREER's `User-agent: *` has essentially no restriction. Shukatsu Kaigi is unconfirmed | C | Allowed. Limited, however, to facts about the selection format, such as the number of selection stages and interviewers' titles; do not use it as grounds for a question specific to mid-career hiring. ONE CAREER PLUS (for mid-career hiring, `plus.onecareer.jp`) is unconfirmed |
| JobQ Town, selection-process accounts on note and Hatena Blog, posts on X | Single, anonymous | Readable | Various | D | Not included in the procedure. Limited to a supplement when corroborated by another source |
| YouTube interview-preparation videos | Mostly a general explanation of how to answer; almost no company-specific questions | Readable | — | C (a recruitment agency's (転職エージェント) official channel is B) | Not used as a company-specific source. Kept as a candidate source for the canonical general question-type reference (`job-change-interview-prep`'s `question-bank.md`) |

The canonical rule that decides whether fetching is allowed (the crawler's name, the terms of service, the difference between a 404 and a 403, the check date and re-reading, and being refused at fetch time) is in `job-change-job-search`'s `references/query-catalog.md`, "The rule for deciding whether retrieval is permitted." The table above is the result of applying that rule to sources for the selection process, and when a site not in the table is found during an investigation, judge it by the same rule. Do not transcribe a review's body wholly into the deliverable; keep a quote to the minimum needed to identify a question or a fact. When redirected to a login screen, do not read that page again within that session. Do not interpret an inability to read as "no information exists."

Some users receive a list of questions for their target company through a recruitment agency (転職エージェント). That is information from outside the web, so do not pass it to a role holding a web-transmission tool; `job-change-interview-prep` receives it directly from the user.
