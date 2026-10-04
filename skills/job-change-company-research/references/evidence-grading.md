# Canonical definition of evidence levels (evidence-grading)

This is the canonical definition of the definition, assignment criteria, and operating rules for evidence levels (A through D) on company information. Among the job-change support skills, the hub (job-change-support), the company researcher agent (job-change-company-researcher), the research auditor agent (job-change-research-auditor), and the selection-exam investigator agent (job-change-exam-scout) reference this file.

## Definition of the levels

Every piece of evidence about a company has one of the following four grades, according to the nature of its source.

| Level | Category | Examples |
|---|---|---|
| **A** | Primary/official | EDINET securities reports, earnings briefing materials, the company's official site, integrated reports, public statistics and government certification-scheme databases, peer-reviewed academic research |
| **B** | Reliable secondary | Major news outlets, Shushoku Shikiho, industry reports, explanatory pages from public institutions (secondary information edited from primary material) |
| **C** | Review-aggregation sites | Aggregated posts from OpenWork, Glassdoor, and similar sites; sites that aggregate selection-process accounts |
| **D** | Personal blog, hearsay, unconfirmed | Personal blogs, hearsay on social media, reposts of unknown origin, one anonymous post |

## Assignment criteria

- **Judge by whether the source is primary.** Decide by who sent the information out. Information a government, an exchange, or the company itself sends out under a law or a scheme is A; information a news outlet or a publication's own survey has edited is B.
- **Within A, a claim that presents the company favorably does not have its truth guaranteed.** A company sends out some claims to present itself favorably, such as "open communication," "an easy place to work," or "an environment for growth" on its recruiting site. The truth of such a claim is not guaranteed, even when the source is primary/official. State in the source that this kind of claim comes from a page the company itself owns, and do not set confidence to high (treat it as B-equivalent). Treat the fact (whether a certification exists, a disclosed figure, whether a program exists) separately from the evaluation (whether the culture is good or bad).
- **Do not use C or D to assert a fact.** Do not assert a fact on review-site posts or hearsay alone. Write a statement based on C or D with a hedge (described below).
- **Distinguish an aggregation site's overall score from an individual post.** A review-aggregation site differs in reliability between a multi-response aggregated overall score and an individual post (described below in "The conditional validity of an aggregated overall score").

## How to write a statement based on C or D

Write a statement based on C or D without an assertive form, stating the source and its limits explicitly.

- Bad example (an assertion): 「この企業は残業が多い。」
- Good example (hedged): 「口コミ集計サイトでは、残業が多いという声がある（回答 N 件）。在籍者の自己選択による偏りがあり、傾向の傍証にとどめる。」

A hedged statement has three elements: (1) it states the source (「口コミでは」「選考体験記では」), (2) it states the quantity behind it, such as a response count, and (3) it adds the limit from bias.

## The principle of cross-checking sources

For one point, cross-check multiple sources in the hierarchy A > B > C.

- Center on primary information at level A, and use B and C as supporting evidence to confirm agreement with it.
- When A and C disagree, go with A. Record the discrepancy on the C side in open_questions.
- Do not set confidence to high for a point backed by C alone, with no support from A or B. When an entire topic is made up of only C and D, consider adding primary or secondary backing (`validate_company_research.py` detects this state as a WARN).

## Corroborated findings (grounds)

The grounds for the evidence-level hierarchy and the treatment of review-site posts, with their sources. A DOI is given for academic research.

### The selection bias of review-site posts (an individual post skews to the extreme)

An online review has a self-selection bias. A person holding a more extreme opinion is more likely to post, so the distribution of ratings skews toward the extremes (Marinescu, Klein, Chamberlain & Smart 2021, a combination of observational research and a randomized experiment, peer-reviewed. DOI:10.1037/xap0000342 https://doi.org/10.1037/xap0000342 ). This selection bias is the grounds for not using an individual review-site post, a small-sample aggregate, or a facet-level metric (an individual item) to assert a fact.

As reinforcing evidence, an online review's average rating becomes a biased estimator of quality because of acquisition bias and underreporting bias, and its distribution becomes J-shaped (positively skewed, asymmetric, bimodal) (MIS Quarterly 2017, DOI:10.25300/misq/2017/41.2.06 https://doi.org/10.25300/misq/2017/41.2.06 ). A company also has an incentive to artificially manufacture biased reviews (American Economic Review 2014, DOI:10.1257/aer.104.8.2421 https://doi.org/10.1257/aer.104.8.2421 ).

### The conditional validity of an aggregated overall score (both sides stated)

Even with selection bias present, review posts have a usable range. An overall score aggregated across a large number of responses has a conditional validity that correlates moderately with an external measure. At the aggregate level of US federal agencies, Glassdoor's overall satisfaction score correlates moderately with the overall rating from a government employee survey (FEVS). The correlation is **r=.516, a figure from one study (Landers 2019)** (Personnel Assessment and Decisions 2019, DOI:10.25035/pad.2019.03.006 https://doi.org/10.25035/pad.2019.03.006 ). The same study, however, does not sufficiently support the validity of facet-level (individual-item) metrics. A company with a higher employee-satisfaction score also had better stock market performance under COVID-19, and satisfaction predicts future operating performance as well (Review of Finance 2022, DOI:10.1093/rof/rfac055 https://doi.org/10.1093/rof/rfac055 ).

<!-- textlint-disable jtf-style/2.1.2.漢字 -->
<!-- This source's author names contain characters outside the joyo kanji list, so this rule is disabled for this range only. -->

There is peer-reviewed research in the Japanese-language sphere too, showing that a score generated from aggregated review text predicts a company's indicators. The study generated a time series of "job satisfaction" and "ease of working" scores from 306,392 reviews (July 2007 to March 2019) on the employee review site OpenWork. The time series relates to company performance and stock performance. An "improved x improved" portfolio shows a statistically significant excess return of an annualized 8.481% on a market-cap-weighted basis about 12 months later (西家宏典・長尾智晴「従業員口コミを用いた働きがいと働きやすさの企業業績との関係」ジャフィー・ジャーナル 19:79-96, 2021, DOI:10.32212/jafee.19.0_79 https://doi.org/10.32212/jafee.19.0_79 , level A, peer-reviewed). The response count and the excess-return figure come from this one study. This study demonstrates the aggregated score's predictive validity (its information value) in the Japanese-language sphere, but it does not negate the size of the selection bias toward posters who have left or are considering leaving. One author was also involved in an index OpenWork co-developed. This leaves a reservation about the study's independence.

<!-- textlint-enable jtf-style/2.1.2.漢字 -->

The conclusion is: "a review post is useful as supporting evidence on the conditions of an aggregated overall score, a sufficient response count, and cross-corroboration." A small-sample aggregate or a per-item score skews to the extreme and becomes J-shaped from selection bias, and the company also has an incentive to manipulate it, so do not use either to assert a fact. Note that this r=.516 comes from one study, and reproduction of the same value by an independent study remains unconfirmed.

### OpenWork's proof-of-employment requirement and manual screening (a quality difference among review sites)

There is a quality difference among review sites as well. OpenWork requires proof of employment (an employee ID, a company email, and so on) to post or view a review, and a dedicated staff screens it manually (there is primary-source backing for this). However, a "leaver bias," in which a dissatisfied former employee is more likely to post, affects the score (Job-Hunting Handbook 2024, level C. https://jo-katsu.com/campus/10412/ ). This proof-of-employment requirement and manual screening make a poster's authenticity comparatively higher than on other sites. A leaver bias and a selection bias still remain. So treat OpenWork as level C as long as it is an aggregation site, and keep the principle of using the overall score as supporting evidence.

An additional search in July 2026 cross-searched J-STAGE, CiNii, and OpenAlex. It did not find a peer-reviewed study that directly measures the size of the leaver bias and selection bias on a Japanese-language review site (OpenWork, 転職会議 (Tenshoku Kaigi), and so on). A pointer to bias in the Japanese-language sphere stays at the level of level-C HR and job-change blogs. In the English-language sphere, research exists that addresses the validity of Glassdoor's aggregated rating (the Landers 2019 study cited above, Personnel Assessment and Decisions 2019), but it does not use a Japanese sample. So note that in the Japanese-language sphere, Nishiie and Nagao 2021 (cited above) demonstrates the aggregated score's predictive validity, while the size of the bias remains unquantified at the peer-reviewed level.

### The discretion in calculating a securities report's average annual salary, and the limits of comparability (even A has limits)

Primary information (level A) has limits too. A securities report's average annual salary is uniformly defined by law under the disclosure ordinance to include bonuses and exclude officers and temporary employees. Non-scheduled wages (overtime pay, allowances) and the treatment of part-time workers, however, are each company's own discretion, and the figure is a company-wide average lacking a breakdown by job type or employment type. So a simple comparison between companies has limits (primary source: the Financial Services Agency's EDINET https://www.fsa.go.jp/search/20130917.html ; a commentary on the calculation method: Kabushiki Soumu 2023, level C https://kabushikisoumu.com/annual-income-4 ). Even for a level-A figure, state its limits on representativeness and comparability in the statement or in open_questions.

## Relationship with the agents and the script

- The company researcher (job-change-company-researcher) assigns a level and a confidence to each claim, following this file's rules.
- The research auditor (job-change-research-auditor) checks the validity of the assigned levels against this file's rules. It also checks whether a fact is asserted on C or D alone, and whether confidence high has been given to a claim that presents the company favorably.
- `scripts/validate_company_research.py` mechanically checks the legitimacy of level values (A through D), confidence=high on a claim based on C or D alone, and a topic made up entirely of C and D. The validity of a level assignment itself (such as whether a review-site post has been upgraded to A or B, or a primary source downgraded to C) cannot be judged mechanically; it is the audit agent's territory.
