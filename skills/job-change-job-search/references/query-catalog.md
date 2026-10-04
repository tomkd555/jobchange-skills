# Catalog of free public web search for job discovery (query-catalog)

A catalog for finding job postings using free public web search alone. Each listed site is one whose search-results page has actually been confirmed to be viewable without login, and whose robots.txt has actually been confirmed not to forbid fetching the search-results page. A site that could not be confirmed, or one this skill has decided as a matter of policy not to use, is recorded with its reason under "Sites excluded from scope". The job searcher agent (job-change-job-searcher) follows these with WebSearch and WebFetch, and gathers results with a quotation from and the source URL of the listing page attached.

**Confirmation dates**: 2026-08-21 (求人ボックス (Kyujin Box), マイナビ転職エンジニア (Mynavi Tenshoku Engineer), type, Wantedly, and the initial excluded sites), 2026-09-04 (HERP Careers, family C, additional excluded sites, and unconfirmed sites). Each site's login requirement, URL structure, and robots.txt were confirmed as of that date. A site's own specification changes can cause this catalog's record to drift from actuality. An item that could not be retrieved is recorded in the deliverable's `coverage_notes`. For a site whose confirmation date is more than 180 days old, re-read its robots.txt before use (the rule is in "The rule for deciding whether retrieval is permitted").

**Common constraints**
- "Non-public postings" that require member registration or login are outside the scope of free public search. Being placed outside scope is recorded in `coverage_notes`.
- A listing page's wording is transcribed verbatim into `quote`. A posting that cannot be retrieved is never fabricated.
- A posting whose salary reads 「応相談」 (negotiable) or similar, with no readable number, has `salary_range` set to `null`.
- A path forbidden by robots.txt is never fetched. Each site's forbidden paths are recorded in its own section.

## There are 3 families of ways to open a job listing page

Sites differ in whether a search result can be reached directly by constructing a URL. Confusing the families results in constructing a nonexistent URL and collecting 404s.

| Family | Content | Sites it applies to |
|---|---|---|
| A. Constructing URL syntax | Conditions appear in the structure of the URL in a regular way, so a URL can be assembled to obtain a result even for an untried combination. The syntax is recorded in this catalog. | 求人ボックス (Kyujin Box), マイナビ転職エンジニア (Mynavi Tenshoku Engineer), HERP Careers |
| B. Discovering the results URL via a `site:` search | The search conditions appear in the URL as an internal ID, so a URL cannot be assembled. `WebSearch` is used to search `site:{domain} {occupation} {region} {condition}`, and the resulting results page or individual posting page URL is read with `WebFetch`. | type, Wantedly |
| C. Opening the careers page from a known company slug | There is no entry point for cross-site search. Only each company's own careers page exists. Only when the company slug is already known (found through company research, HERP Careers, or a `site:` search), that page is read with `WebFetch`. | HRMOS, Findy |

A guessed ID points to another company's posting or a 404, so **a URL must never be constructed for a family-B site**. For family C, a company slug is also never guessed and assembled.

## 1. 求人ボックス (Kyujin Box) (family A)

A job search engine operated by Kakaku.com, Inc. It aggregates postings across Japan. It is this catalog's only large-scale source whose URL can be constructed from conditions.

| Aspect | Content |
|---|---|
| Domain | `https://xn--pckua2a7gp15o89zb.com` (the Punycode form of "求人ボックス.com"; pass it to `WebFetch` in this form) |
| Login requirement | Browsing the search and listing pages does not require login (confirmed) |
| URL shape | Conditions are embedded in the URL path as URL-encoded Japanese. A query string is not used |
| robots.txt | `/api/`, `/suggest/`, `/rd/`, `/map/`, `/my/`, `/apply*`, `/pdf/`, and so on are Disallow. The search-results page (`/{keyword}の仕事…`) is not among the forbidden targets |

### URL syntax

| Purpose | Path | Example |
|---|---|---|
| Occupation listing | `/{keyword}の仕事` | `/データサイエンティストの仕事` |
| Narrow by region | `/{keyword}の仕事-{prefecture}` | `/データサイエンティストの仕事-東京都` |
| Add a condition | `/{keyword}-{condition}の仕事-{prefecture}` | `/データサイエンティスト-年収500万円の仕事-東京都` |
| Salary market rate | `/{occupation}の年収・時給` (Salary Navi) | `/データサイエンティストの年収・時給` |

Conditions can be joined with `-` to specify more than one at once. The confirmed condition tokens are `年収500万円` (replaced in 1-million-yen increments), `フルリモート`, `上場企業`, and `大手企業`.

Measured (2026-08-21): `/データサイエンティスト-年収500万円の仕事-東京都` returned 1,098 hits, and `/データサイエンティスト-フルリモートの仕事` returned 1,461 hits.

| Aspect | Content |
|---|---|
| Retrievable fields | Posting title, company name, work location, salary, employment type, and other fields shown in the listing |
| Constraint | Because it reproduces the aggregation source's own record as is, the same posting appears repeatedly from multiple aggregation sources. Deduplicate using the "Deduplication" rule. For a posting whose detail is not readable, confirm via the source link with `WebFetch` |

## 2. マイナビ転職エンジニア (Mynavi Tenshoku Engineer) (family A)

The engineering segment of the job-change site operated by Mynavi. URL segments are expressed as codes, and can be assembled even for a combination not yet observed.

| Aspect | Content |
|---|---|
| Login requirement | Browsing the search-results listing does not require login (confirmed) |
| robots.txt | There is no entry naming an AI crawler (ClaudeBot, anthropic-ai, GPTBot, CCBot) as a User-agent (confirmed 2026-08-21). The `User-agent: *` Disallow entries are centred on application and member functions. `/engineer/list/` and the individual posting page `/jobinfo-{ID}-…/` are not among the forbidden targets. `/job/`, `/entry/`, `/mypage/`, and `/ajax/*` are Disallow, and are never followed |

### URL syntax

```
https://tenshoku.mynavi.jp/engineer/list/p{prefecture}/e{employment type}/min{salary}/f{preference}/o{occupation}/i{industry}/kw{keyword}/pg{page}/
```

Each segment may be omitted, and the order is fixed as above. The known codes are as follows.

| Segment | Meaning | Known values |
|---|---|---|
| `p` | Prefecture | `p13` = Tokyo |
| `e` | Employment type | `e01` = permanent employee |
| `min` | Salary floor for the first year (in units of 10,000 yen, 4 digits) | `min0550`, `min0600`, `min0700`, `min0800` |
| `f` | Preference condition | `f618` = remote work allowed |
| `o` | Occupation | `o16` = IT engineer |
| `i` | Industry | Not confirmed |
| `kw` | Free keyword | Place the Japanese term as is |

An unknown code is never filled in by guesswork. When one is needed, run `site:tenshoku.mynavi.jp {condition term}` with `WebSearch` to find a real URL and read the code from it.

Measured (2026-08-21): a combination that does not appear in the actual narrowing UI, `p13/e01/min0700/f618/kwデータサイエンティスト/`, returned 29 hits. This confirmed that segments can be assembled to search.

| Aspect | Content |
|---|---|
| Retrievable fields | Posting title, company name, work location, first-year salary, employment type, preference conditions |
| Constraint | The `min` narrowing can sometimes be judged against the upper bound of the offered range. Confirm again against the body of the posting, following the "Re-judging the salary floor" rule |

## 2.5 HERP Careers (family A)

The public posting listing of the recruitment management service operated by HERP, Inc. It searches across the postings of companies using this service. It skews toward startups and IT-sector occupations.

| Aspect | Content |
|---|---|
| Domain | `https://herp.careers` |
| Login requirement | Browsing the cross-site listing does not require login (confirmed 2026-09-04; `/careers/jobs?parent-job-role-ids=engineer&remote-work-type-ids=FULL_REMOTEWORK` returned 「20/242 企業を表示中」 (showing 20 of 242 companies)) |
| URL shape | `/careers/jobs` with conditions attached as a query string. A per-company page is `/v1/{company slug}` |
| robots.txt | There is no entry naming an AI crawler as a User-agent. The `User-agent: *` Disallow covers only `/ref/`, `/*?viaCareers=`, and `/apply$`; the listing and individual postings are not among the forbidden targets (confirmed 2026-09-04) |
| Terms of service | Whether automated retrieval is permitted has not been read in this catalog's confirmation. Confirm it in the first search session that uses this site, following "The rule for deciding whether retrieval is permitted" |

### URL syntax

| Parameter | Meaning | Value confirmed to exist |
|---|---|---|
| `parent-job-role-ids` | Occupation, top-level category | `engineer` |
| `job-role-ids` | Occupation, sub-category | Not confirmed |
| `employment-type-id` | Employment type | Not confirmed |
| `city-codes` | Work location | Not confirmed |
| `remote-work-type-ids` | Remote-work category | `FULL_REMOTEWORK` |

The listing page has narrowing by occupation, employment type, work location, salary, remote-work category, and company size, plus free-word search. For an unconfirmed parameter's value, read the listing page's narrowing controls with `WebFetch` to confirm a value that actually exists, before using it. A value is never filled in by guesswork. When a value cannot be read, search using only the free word and `parent-job-role-ids`.

| Aspect | Content |
|---|---|
| Retrievable fields | Posting title, company name, work location, salary, employment type, remote-work category |
| Constraint | Listed companies are limited to users of this service. The same posting appears on both the company page (`/v1/{company slug}`) and the cross-site listing, so under "Deduplication," the company-page side is kept |

## 3. Sites found via a `site:` search (family B)

The following sites express search conditions as a numeric ID or numeric code in the URL, so a URL cannot be assembled from conditions. Use only the path of running `WebSearch` for `site:{domain} {occupation} {region} {condition}` and reading the returned URL with `WebFetch`. Each robots.txt was fetched and confirmed in its original form on 2026-08-21.

| Site | Domain | robots.txt | Characteristics |
|---|---|---|---|
| type | `type.jp` | Only one `User-agent: *` block. There is no entry naming an AI crawler. Disallow covers `/skillsheet/`, `/experience/`, `/maintenance_user/`, and so on; the occupation category and individual posting pages are not among the forbidden targets | Occupation and area are expressed as a numeric category (e.g. `/job-1/1001/`). No public table maps the numbers |
| Wantedly | `www.wantedly.com` | Only one `User-agent: *` block. There is no entry naming an AI crawler. Disallow is centred on member functions and `.js` fragments; the listing page `/projects/{ID}` is not among the forbidden targets | A listing page is expressed with a numeric ID. Many listings do not state a salary explicitly, so `salary_range` is often `null` |

## 3.5 Sites where a careers page is opened from a company slug (family C)

The following sites each have a careers page per company, but have no entry point for cross-site search. Only when a company slug or ID is already known is that page read with `WebFetch`. The source of the slug is a HERP Careers company page, or a `site:` search result. Since the job searcher agent is not given `company_research.json`, when a careers-page URL learned through company research is to be used, the calling skill writes only the URL into the instructions and passes it that way. A slug is never guessed and assembled. Each robots.txt was confirmed on 2026-09-04.

| Site | URL shape | robots.txt | Characteristics |
|---|---|---|---|
| HRMOS careers page | `https://hrmos.co/pages/{company slug}/jobs` (`?category={ID}` narrows by occupation) | `/robots.txt` returns 404 (the file is absent). This is read as expressing no intent to forbid ("The rule for deciding whether retrieval is permitted," on the handling of 404) | The listing does not require login (`hrmos.co/pages/hrmos/jobs` returned 「全 82 件中 82 件を表示」 (showing 82 of 82)). Narrowing by employment type, occupation, work location, and department exists |
| Findy | `https://findy-code.io/companies/{ID}/jobs` | The `User-agent: *` Disallow covers only member functions (`/home/`, `/likes/`, `/matches/`, `/settings/`, `/users/`, and others) and blog drafts. There is no entry naming an AI crawler | Only a per-company posting listing exists. There is no cross-site search. The same posting often also appears on HERP Careers |

## 4. Sites excluded from scope

| Site | Reason |
|---|---|
| Indeed Japan (`jp.indeed.com`) | robots.txt is a large file, and this catalog's tools have not been able to read its full text consistently (the summary obtained differed between the 2026-08-21 and 2026-09-04 retrievals). What agreed across multiple retrievals is that Indeed names `ClaudeBot`, `anthropic-ai`, `GPTBot`, and `CCBot` as a group of training crawlers and forbids the paths for job search and browsing. This is a prohibition the site itself expresses, and this skill does not use it as a matter of policy. The `site:jp.indeed.com` search route is also not used |
| Green (`www.green-japan.com`) | robots.txt has a `User-agent: GPTBot` / `Disallow: /` block, forbidding a generative-AI crawler entirely, by name (confirmed 2026-08-21). `ClaudeBot` and `anthropic-ai` are absent from the list, though the expressed refusal is read as directed at crawlers of the same kind, and this site is treated the same as Indeed and not used. Also, `User-agent: *` has `/search?` as Disallow, so the search-results page itself cannot be followed |
| Stanby (`jp.stanby.com`) | robots.txt's `User-agent: *` has `/search`, `/jobs/`, and `/*?*` as Disallow (confirmed 2026-08-21). The search-results page, individual posting pages, and any URL with a query string are all among the forbidden targets. Every route that public search could use is among them |
| Hello Work Internet Service | A URL with the conditions already specified cannot be opened directly. Search state is held through screen transitions and a session, by design, so a search result cannot be opened by URL alone (re-confirmed 2026-09-04 that opening a `GECA110010.do`-style URL directly produces a system error). Not used except when the posting number is already known. The mechanism the Ministry of Health, Labour and Welfare provides for private job-placement businesses to receive posting information has not been investigated |
| en-japan (`employment.en-japan.com`) | robots.txt has a `User-agent: ClaudeBot` / `Disallow: /` block, forbidding the entire site by name (confirmed 2026-09-04). `GPTBot` has `Crawl-delay: 30` and a Disallow on the search listing. `OAI-SearchBot` has Disallow on `/comp*/list*` and `/apply*`. Treated the same as Indeed and not used |
| engage (`en-gage.net`) | robots.txt has a `User-agent: ClaudeBot` / `Disallow: /` block, forbidding the entire site (confirmed 2026-09-04). `/search/` and `/search2/` are also Disallow for `GPTBot`, `OAI-SearchBot`, `PerplexityBot`, and others. **Many companies' own careers pages (`en-gage.net/{company name}/…`) are placed under the same domain, and they receive the same prohibition.** Even when a careers-page URL learned through company research falls under this domain, it is not fetched |
| LinkedIn Jobs (`www.linkedin.com`) | robots.txt does not name any AI crawler, yet it forbids `/jobs-guest/` (the only path for viewing postings without login) along with `/jobs?runSearch*`, `/jsearch*`, and `/api/jobPostings/jobs*`, for every User-agent other than `LinkedInBot` (confirmed 2026-09-04). Also, the company's own terms of service forbid automated collection. Even absent a refusal naming this crawler, it is not used as a matter of policy |
| doda (`doda.jp`) job search | robots.txt's `User-agent: *` has `/DodaFront/View/JobSearchList.action*` and `/DodaFront/View/JobSearchList/*?*` as Disallow, forbidding the search-listing mechanism itself for every User-agent (confirmed 2026-09-04). There is no entry naming an AI crawler. The format of the individual posting page's URL has not been confirmed. The doda average-annual-income ranking in `{HUB_SKILL_DIR}/references/market-data-sources.md` is a separate page group and is unaffected by this exclusion |
| Talentio careers page (`talentio.co.jp`) | `/robots.txt` returns 403 (confirmed 2026-09-04). The policy cannot be read, and a 403 also shows a mechanism exists to block automated access. A site whose policy cannot be read is not treated as permitted |

## 5. Unconfirmed sites

The following sites have had their robots.txt confirmed, but the format of a URL for a listing readable without login has not been confirmed, or the investigation itself has not been done. They are not included in this catalog and will be added with a family assigned once confirmed. Their absence here does not mean they have been excluded.

| Site | What was confirmed | What remains unconfirmed |
|---|---|---|
| paiza tenshoku (`paiza.jp`) | robots.txt is `User-agent: *` / `Disallow:` (empty), fully open (2026-09-04). The listing entry point is `/career/job_offers` | How narrowing by occupation, work location, and salary appears in the URL |
| BizReach public postings (`www.bizreach.jp`) | robots.txt has no entry naming an AI crawler. The path `/job/j/` is not among the forbidden targets (2026-09-04) | Whether an individual posting's body can be read without member registration. Only a keyword-based listing page has been confirmed readable |
| LAPRAS (`lapras.com`) | robots.txt forbids only `PetalBot` | Whether a posting listing exists that is readable without login. It is a scouting-type product, and may not have a listing |
| YOUTRUST (`youtrust.jp`) | robots.txt has no Disallow | Whether a posting listing exists. It is a networking-type product, and may not have a posting listing |
| Jobcan Recruitment Management careers pages (`ats.jobcan.ne.jp`) | robots.txt's only Disallow is `/wp-admin/` | An example of an actual company's careers-page URL. `ats.jobcan.jp` is a different domain and is easily confused with this one |
| Airwork Recruitment Management careers pages | The product's domain is under `airregi.jp/work/recruitment`. `airwork.net` does not resolve | An example of an actual company's careers-page URL, and its robots.txt |
| `hellowork.careers` | robots.txt is open | The operator. Whether this is an official Ministry of Health, Labour and Welfare service, an authorised reproduction, or an unrelated collection site has not been confirmed. Not used until confirmed |
| Rikunabi NEXT, Mynavi Tenshoku (outside the engineer edition), doda X, AMBI, Miidas, 日経転職版 (Nikkei Tenshokuban), Forkwell Jobs, Offers, Levtech Career | Not investigated | Everything |

## The rule for deciding whether retrieval is permitted

This catalog's "excluded" and "unconfirmed" entries are decided by the following rule. When a site absent from this catalog is found during a search session, judge it by the same rule, and record the content of the judgement in `coverage_notes`.

| Rule | Content |
|---|---|
| Crawler name | Which User-agent `WebFetch` identifies itself as has not been confirmed. So a site is not used when its robots.txt names and forbids any of `ClaudeBot`, `anthropic-ai`, `Claude-User`, or `Claude-SearchBot`. Such a site is treated as one that sees this crawler under that name. A site that forbids only another company's generative-AI crawler, such as `GPTBot` or `CCBot`, is also read as expressing a refusal directed at crawlers of the same kind. It is not used either |
| Terms of service | Terms of service factor into whether retrieval is permitted, together with robots.txt. A domestic job site or recruitment management service sometimes forbids automated retrieval in its terms of service, and that clause can also cover a company's own careers page placed on the same domain. For a site whose terms of service have not been read in this catalog (HERP Careers, HRMOS, Findy), read the terms-of-service page with `WebFetch` the first time it is used in a search session. If a clause forbids automated retrieval or scraping, do not use the site for that session, and record this in `coverage_notes`. The same treatment applies when the terms could not be read |
| The difference between 404 and 403 | A site whose robots.txt returns 404 (the file is absent) is treated as a site that expresses no intent to forbid. A site that returns 403 is not treated as permitted, since its policy cannot be read and a 403 also shows a mechanism exists to block automated access. RFC 9309 classifies both the same way, as "unable to fetch," but a 403 is an active block by the site, from which consent cannot be inferred |
| Confirmation date and re-reading | For both included and excluded sites, this catalog keeps the date it was confirmed. For a site whose confirmation date is more than 180 days old, re-read its robots.txt before use, and correct this catalog if it has changed. Record the result of re-reading in `coverage_notes` |
| Refused at runtime | When a site treated as in scope by this catalog becomes unreadable during a search session (a robots.txt change, a 403, or a redirect to a login screen), do not use it for that session. Record it in `coverage_notes` with the date. Do not repeat the retry within the same session |

## Query expansion rules

The queries run in one search are built from a combination of occupation-name rephrasing, region, and conditions, and increasing the number of rephrasings does not necessarily make results better.

**The occupation-name variants are, as a base, the three of the user's original wording plus 2 rephrasings.** In a study verifying LLM-based query expansion, growing from 1 variant to 3 variants showed the most consistent improvement. Going to 5 variants increased noise (https://arxiv.org/abs/2510.10009, grade B). This is a preprint that has not been peer-reviewed, and is a primary report by its authors. It has also been reported that, for an ambiguous query, expansion itself can lower recall (https://arxiv.org/abs/2505.12694, grade B, also a non-peer-reviewed preprint and a primary report by its authors). The canonical definition of the evidence-grade scale is in `job-change-company-research/references/evidence-grading.md`.

Searching by rephrasing alone misses postings for the occupation the user explicitly named. **The occupation name the user explicitly stated is run as is, unexpanded, as one query.**

The query cap is **12 per search session**. The breakdown is as follows.

| Count | Composition |
|---|---|
| 9 | 3 occupation-name variants (original + 2 rephrasings) × 1 first-choice region × 3 condition patterns (no condition / salary floor / remote) |
| 2 | 1 strongest variant × 2 next-choice regions |
| 1 | Reserve. Used for the pairing of that seniority level's title with the occupation's broad category, when a seniority level is specified, or for the katakana spelling (described below) when a tool or technology is specified. Not run when neither applies |

12 is a ceiling. Stopping once enough postings meeting the required conditions have been gathered is acceptable (the basis is "Search volume does not predict employment quality" in `search-methods.md`).

Separate from these 12 (the primary set), queries for the derivation lanes the user chose are run. Up to 3 queries per lane. Even choosing all 10 lanes adds at most 30 more. The canonical definition of how lanes are built is `derivation-lanes.md`. The reason the primary set's query count is not reduced to make room for the lanes is in `search-methods.md`. A lane's queries are also recorded one by one in `search_log`, with `search_set` set to `derived` and `lane` set to the lane name. The same `search_set` and `lane` are written for the postings adopted. Whoever handles the primary set does not search the lanes, and whoever handles a lane searches only the lane assigned to them.

Retrieval in `company_profile` mode is capped at 6 per company (the sources are described below in "Sources for company information").

### How to build synonyms

An occupation listed in the table below is used as is. For an occupation absent from the table, search `{occupation name} とは 別の呼び方` with `WebSearch`, obtain 2 to 3 names that job sites actually use, and **never invent an unconfirmed rephrasing**.

The table has two sources. One is the Ministry of Health, Labour and Welfare's Occupational Classification, Reiwa 4 edition (18,725 occupation names are tied to its minor categories; the classification table: https://www.mhlw.go.jp/content/11650000/001030651.pdf, grade A, a classification edited by a public institution). The other is doda's Occupation Encyclopedia (https://doda.jp/guide/zukan/, grade B, secondary information edited by a private job-placement outlet). The occupation-information site jobtag is a single-page application and cannot be read with `WebFetch` (confirmed 2026-08-21). There is no need to consult the sources at runtime. Consulting the table alone is enough.

Rephrasings 1 and 2 are other names for the same occupation, and are used in the primary set. An adjacent occupation is a different occupation whose duties overlap, and is used only in the exploration set (`bias-checklist.md`). A posting's `role_match` is `same` when it matches rephrasing 1 or 2, and `adjacent` when it matches an adjacent occupation (the canonical definition is `job-search-format.md`).

| Occupation | Rephrasing 1 | Rephrasing 2 | Adjacent occupation | Note |
|---|---|---|---|---|
| バックエンドエンジニア (backend engineer) | サーバーサイドエンジニア | Webアプリケーションエンジニア | フルスタックエンジニア | |
| フロントエンドエンジニア (frontend engineer) | Webフロントエンドエンジニア | UIエンジニア | フルスタックエンジニア | |
| インフラエンジニア (infrastructure engineer) | サーバーエンジニア | クラウドエンジニア | SRE | |
| SRE | サイトリライアビリティエンジニア | インフラエンジニア | DevOpsエンジニア | |
| データサイエンティスト (data scientist) | 機械学習エンジニア | データアナリスト | データエンジニア | Rephrasings 1 and 2 are often listed as separate occupations. The market rate and duties differ, so confirm from the posting's own description |
| データエンジニア (data engineer) | データ基盤エンジニア | ETLエンジニア | データアナリスト | |
| モバイルアプリエンジニア (mobile app engineer) | iOSエンジニア | Androidエンジニア | フロントエンドエンジニア | |
| 社内SE (in-house SE) | 情報システム担当 | 情シス | IT企画 | |
| プロジェクトマネージャー (project manager) | PM | ITプロジェクトマネージャー | プロダクトマネージャー | |
| プロダクトマネージャー (product manager) | PdM | プロダクトオーナー | プロジェクトマネージャー | |
| QAエンジニア (QA engineer) | テストエンジニア | 品質保証エンジニア | テスト自動化エンジニア | |
| セキュリティエンジニア (security engineer) | 情報セキュリティエンジニア | SOCアナリスト | ネットワークエンジニア | SOC analyst leans toward a monitoring/operations title |
| ITコンサルタント (IT consultant) | 業務コンサルタント | 業務システムコンサルタント | PMO | |
| 経理 (accounting) | 財務経理 | 会計スタッフ | 経営企画 | |
| 人事 (HR) | 人事労務 | 採用担当 | 総務 | |
| 法人営業 (corporate sales) | 法人向け営業 | BtoB営業 | インサイドセールス | |
| カスタマーサクセス (customer success) | カスタマーサポート | テクニカルサポート | インサイドセールス | The support side has different duties. Confirm from the posting's description of duties |

Before relying on `WebSearch` for an occupation absent from the table, consult the minor categories of the Ministry of Health, Labour and Welfare's Occupational Classification. A minor category ties in multiple alternate names for the occupation. Much of the wording job sites use appears there. The jobtag CSV contains the same vocabulary, but is not used at runtime because `WebFetch` cannot read it.

### Seniority level

An occupation-name rephrasing changes the occupation, and keeps the seniority level as it is. A managerial posting is sometimes listed under the title alone, with the occupation name dropped (e.g. 「エンジニアリング部門 部長」 (head of the engineering department)), and an occupation-name-only query misses it.

| Level | Form of the title | Note |
|---|---|---|
| Senior individual contributor | シニア{occupation}, リード{occupation}, {occupation}リード | Often a prefixed form |
| First-line manager | {occupation}マネージャー, {occupation}課長, チームリーダー, {occupation}主任 | IT tends toward マネージャー; other industries tend toward 課長/主任 |
| Middle manager | 部長, グループマネージャー, ユニットリーダー | Sometimes listed under the title alone, with the occupation name dropped |
| Unmodified | {occupation} | Default |

When the condition sheet specifies a seniority level (such as 「マネージャー」 or 「リーダー」 under `other`), the reserve query pairs that level's title with the occupation's broad category (「エンジニア」, 「営業」). When no such level is specified, search unmodified, and shift the seniority level one step up and one step down in the `seniority_shift` lane (`derivation-lanes.md`).

### English and katakana spellings

When `other` names a tool or technology, job sites split between using the English spelling (Salesforce, Machine Learning) and the katakana spelling (セールスフォース, 機械学習). Only when a well-established katakana spelling exists, run the reserve query with the katakana spelling. A katakana spelling is never invented (an unsettled spelling, such as クバネティス, is not used).

### Exclusion terms (site: search only)

A family-A site's URL syntax has no exclusion operator. `WebSearch`'s `site:` search can exclude with `-{term to exclude}`. Use it only in the following 2 cases.

- Excluding an adjacent occupation that shares the same occupation name. Example: `カスタマーサクセス -カスタマーサポート`.
- When `employment_type` is permanent employment, excluding dispatch and contractor postings. Example: `-派遣 -業務委託`. A family-A site has an employment-type token, so the exclusion term is unnecessary there.

A posting removed by an exclusion term does not appear in `search_log`. A query that used an exclusion term is recorded in `query` with the exclusion term included as typed.

### Expressions of remote work

The `remote_policy` condition token on 求人ボックス (Kyujin Box) is "フルリモート" (full remote) only, but a posting's own wording varies. Searching for full remote alone misses a posting whose main wording is "一部リモート" (partial remote) or "週2日出社" (2 office days a week). One of the 3 condition patterns for remote work uses the following wording, depending on the user's `remote_policy`.

| A posting's wording | Corresponding value in the observation layer (`remote_certainty`) |
|---|---|
| フルリモート, 完全リモート (full remote, fully remote) | `guaranteed` or `full_remote_possible` (decided from the posting's body, whichever applies) |
| リモートワーク可, 在宅勤務可 (remote work allowed, work-from-home allowed) | `full_remote_possible` |
| 一部リモート, ハイブリッド, 週◯日出社 (partial remote, hybrid, N office days a week) | `hybrid` |

Even when the user requires full remote as a must, when the `remote_widen` lane is chosen, the hybrid wording is used for the query ("Fixation on full remote work" in `bias-checklist.md`, `derivation-lanes.md`). The judgement layer decides on this, using the user's own requirement level.

### Expressions of salary

A job posting's salary is written in one of 4 forms: 年収 (annual salary), 想定年収 (expected annual salary), モデル年収 (model annual salary), 月給 (monthly salary). A `site:` search is also run with 想定年収 as well as 年収. モデル年収 is an example for one tenure, separate from the offered amount, so it is not used as `value` in the observation layer (the canonical definition is `salary_condition` in `{HUB_SKILL_DIR}/references/screening-axes.md`). A posting stated only as a monthly salary is one whose floor simply cannot be confirmed. It is not necessarily below `salary_min`. Following the "Re-judging the salary floor" rule, keep it with `salary_range` set to `null`.

### Rail lines and commuting range

求人ボックス (Kyujin Box) is said to have a screen for narrowing by rail line, but this has not been confirmed as URL syntax. A rail line or station name is used as a search term only when the user has written a line or station name themselves into the condition sheet's `location`. A station name must never be derived from `career-private/commute.json` for use as a search term. The nearest station is residential information more specific than a municipality, and cannot be passed to a role holding a means of sending data to the web (the canonical definition of the boundary is `{HUB_SKILL_DIR}/references/pii-boundary.md`).

## Re-judging the salary floor

A site's salary filter can sometimes judge against the **upper bound** of the offered range. In a measurement (2026-08-21), specifying `min0700` on マイナビ転職エンジニア (Mynavi Tenshoku Engineer) returned a posting reading 「初年度年収 350万円～800万円」 (first-year salary 3.5 to 8 million yen).

**When the salary floor (`salary_min`) was used to narrow the search, do not trust the filter's result. Always re-judge using the floor value written in the posting's own body**. A posting whose floor value is under `salary_min` is not placed in the results. A posting whose range cannot be read (「応相談」 (negotiable) or similar) is kept in the results with `salary_range` set to `null`, and `match_notes` states that the floor could not be confirmed.

This re-judging is observation-layer work that corrects for what the search route missed and over-collected. Matching against the user's own conditions stays in the judgement layer. This is possible because `salary_min` is the one condition of the user's own that may be passed to the job searcher (the canonical definition of the boundary is `{HUB_SKILL_DIR}/references/pii-boundary.md`). Since no threshold is passed for the overtime ceiling, the annual-holidays floor, or work-characteristic preferences, the same narrowing is not done for them. Only the observation is recorded.

## Deduplication

An aggregator pulls the same posting in from multiple aggregation sources, so an identical posting can appear repeatedly under different URLs. A posting whose following composite key matches another's is treated as identical, and only one is kept.

```
normalised company name ∥ first 12 characters of the occupation name ∥ work location (municipality) ∥ salary range
```

The normalised company name is obtained by converting full-width alphanumerics to half-width, removing whitespace, stripping a corporate-form notation ("株式会社," "（株）," "(株)," "有限会社," "合同会社") from the leading and trailing positions, and lowercasing letters. The canonical definition of the rule is in the `results[].company_key` section of `job-search-format.md`, and its implementation is `normalize_company_key` in `scripts/validate_job_search_results.py`.

When the key matches, the one kept is chosen by the following priority, so that the listing closest to primary information is retained.

1. The company's own careers page (including a company page on HRMOS, Findy, or HERP Careers)
2. A single-source job site (the マイナビ転職エンジニア (Mynavi Tenshoku Engineer), type, or Wantedly listing, or the HERP Careers cross-site listing)
3. An aggregator (求人ボックス (Kyujin Box))

The count removed is recorded in `coverage_notes`.

### Second stage: matching close candidates

An exact match on the composite key misses the following 2 cases.

- The first 12 characters of the occupation name differ due to a site-specific prefix (such as "【急募】" (urgent) or "【リモート可】" (remote allowed), or a company brand name).
- The salary range renders as a different string between a site that shows base salary alone and one that includes bonus.

So a second stage follows the exact match. A pair whose normalised company name and work location (municipality) match, and whose occupation-name similarity is 0.8 or higher, is listed in `coverage_notes` as "a posting that may be identical". It is not merged automatically, since merging risks dropping a different posting whose conditions truly differ. The occupation-name normalisation and similarity are as follows.

| Step | Content |
|---|---|
| Normalisation | Convert full-width alphanumerics to half-width, remove a prefix or suffix enclosed in 【】, （）, or ［］, remove whitespace, remove "株式会社," "（株）," "㈱" |
| Similarity | Compare the normalised occupation names with `difflib.SequenceMatcher`'s `ratio()` (computable from the standard library alone) |
| Threshold | 0.8 or higher is a candidate. This value is an operational convention chosen without measurement |

The salary range is not included as a matching condition in the second stage; when it does match, it is appended to `coverage_notes` as corroboration of identity.

## Market-rate benchmark

Whether a posting's offered amount is high or low is decided by comparison against a market rate. The canonical definition of the source of market-rate data and its handling rules is in `{HUB_SKILL_DIR}/references/market-data-sources.md`, and is not transcribed here. What job search uses is the following 2 points.

The median returned by 求人ボックス (Kyujin Box) Salary Navi (`/{occupation}の年収・時給`) is used as the benchmark. **This is grade C, and `market-data-sources.md`'s rule requires stating alongside it that this is a reference value from the site's own independent estimate.** So it never settles a fact on its own, and is shown as a reference value.

**The occupation name used to draw the benchmark must be the same as the one the candidate posting itself uses.** In a measurement (2026-08-21), "データアナリスト" (data analyst) came to 7.23 million yen. "データサイエンティスト" (data scientist) came to 5.53 million yen. In this measurement, changing the occupation name alone moved the benchmark by 1.7 million yen. If a posting calls itself "データサイエンティスト," the benchmark is also drawn under "データサイエンティスト."

The obtained benchmark's value, source URL, and retrieval year and month are recorded in `coverage_notes` as a set of three, and for each posting, in `related_info.salary_benchmark` (the specification is in `job-search-format.md`).

Comparison against the user's own current salary belongs to the judgement layer (the calling skill), because the job searcher does not know the user's own salary.

## Sources for related information

For a posting's own related information, under 2.3 the 2 per-posting keys are gathered into `related_info` (the specification is "Exploration set and related information" in `job-search-format.md`). Per-company information is gathered under "Sources for company information" below, and written into `company_profiles`. A key that could not be retrieved is either omitted, or has its `value` set to `null`.

| Key | Source | Grade | Note |
|---|---|---|---|
| `posting_age` | The listing or update date shown on the posting page | A (the listing page's own display) | Omitted when not shown. Age is never treated as evidence the listing has ended |
| `salary_benchmark` | The median from 求人ボックス (Kyujin Box) Salary Navi ("Market-rate benchmark") | C | Drawn under the same occupation name the candidate posting itself uses |

## Sources for company information (company_profile mode)

For every company appearing in the results, one `company_profiles` element is gathered (the specification is "Derivation lanes and company information (2.3)" in `job-search-format.md`). Only what can be read without login is gathered, and company research is still carried out separately. Retrieval is capped at 6 per company, and an item that could not be retrieved has its `value` set to `null` with the reason written in `note`.

| Item → recorded to | Source | Grade | Agent retrieves |
|---|---|---|---|
| Average annual compensation → `metrics.compensation_level`; number of employees → `basics.employee_count`; average age and average tenure → `open_questions` or `note` | The 「従業員の状況」 (state of employees) section of the 有価証券報告書 (securities report). Since EDINET's viewing screen is rendered with JavaScript and its API requires an authentication key, read the securities-report PDF placed on the company's own IR page (search "{company name} 有価証券報告書" with `WebSearch`) | A | Yes. EDINET directly is tried only once; if unreadable, this is written in `note` |
| Revenue growth rate, operating margin, equity ratio → `metrics.revenue_growth`, `operating_margin`, `equity_ratio` | The 「主要な経営指標等の推移」 (key management indicators over time) section of the securities report (the calculation rule is in `job-change-company-research/references/source-catalog.md`) | A | Yes |
| Male childcare-leave utilisation rate → `metrics.male_childcare_leave_rate` | The human-capital disclosure in the securities report | A | Yes |
| 「労働基準関係法令違反に係る公表事案」 (published cases of labour-law violations) → `negative_checks.labor_law_violation_list` | The latest nationwide PDF from the Ministry of Health, Labour and Welfare, https://www.mhlw.go.jp/kinkyu/151106.html | A | Yes. Retrieved once per batch, and cross-checked against every company in the batch. An absence from the list is never treated as evidence of an absence of violations. The published period covers roughly one year; a case outside that period does not appear |
| Eruboshi certification → `basics.certifications` | The Ministry of Health, Labour and Welfare's list page of Eruboshi-certified companies | A | Yes |
| Kurumin certification, the Database of Companies Promoting Women's Active Participation, Shokuba Rabo | — | A | No. These cannot be retrieved because they return 403 or require operating a search form ("Sources that cannot be fetched automatically" in `job-change-company-research/references/source-catalog.md`). What the user has looked up is received instead. For this reason `turnover_rate`, `monthly_overtime`, and `paid_leave_rate` are often `null` |
| Health and Productivity Management Outstanding Organization, Youth Yell certification | Each program's list of certified companies | A | Tried once. Whether retrieval is possible is unconfirmed; failure to read it is never treated as evidence the certification is absent |
| Overall review score → `basics.review_aggregate` | OpenWork's company page (the overall score and response count, readable without login) | C | Yes. The review text requires login and is not read. When the response count is small, this is written in `note` |
| Company overview → `name`, `official_url`, `hq_location`, `industry`, `basics.founded_year`, `capital_yen`, `listed`, `business_summary` | The company overview page on the company's own official site | A (for the factual part; a company's own evaluative claim about itself is never used as grounds) | Yes. The figures in a company overview are the company's own self-reported figures, and can disagree with a securities report's or a registration's date. When they disagree, note both in `note` |
| Careers page → `careers_url` | The company's own official site, or a company page on HRMOS or HERP Careers (only when the slug is known) | A | Yes |
| `basics.edinet_code` | An EDINET document search | A | Tried once. Only a listed company, or one obligated to file a securities report, has one |
| Recent reporting and announcements → `recent_news` | A company's own press release (A), major reporting outlets such as Nikkei (B) | A/B | Yes. The last 12 months, up to 3 items |

When running `WebSearch` under a company name, the search terms are limited to the company name and the item name ("従業員数" (employee count), "有価証券報告書" (securities report)). The content of the condition sheet or the user's own information is never mixed in. A securities report's average annual compensation is an average across all employees, and is never read as the salary for the posting's occupation. A number is never inferred from a review's text and written into `metrics`.

## Confirming listing closure and re-listing

Whether a posting is still open cannot be told from its wording alone. Perform the following 2 checks, in ascending order of cost.

| Check | Content | Recorded to |
|---|---|---|
| Re-fetching the URL | Just before delivery, open each adopted posting's `url` again with `WebFetch`, one by one. If it shows a 404, a redirect to a listing page, or wording such as "掲載終了" (listing ended) or "募集を終了しました" (recruitment has ended), remove that posting from `results`, and write the URL and date into `coverage_notes` | `coverage_notes` |
| Matching against past searches | The calling skill reads past deliverables under `{DATA_ROOT}/job-search/`; if a posting with the same normalised company name and occupation name also appears in a different `search_id` more than 60 days apart, this is written into `open_questions`. A posting that keeps appearing over a long span is either a posting that never gets filled, or a standing-recruitment posting, and the two cannot be told apart from the posting alone | `open_questions` |

Matching against past searches is done locally by the calling skill. A past deliverable includes the judgement layer (matching against the user's own thresholds), so it is never passed to the job searcher agent, which holds a means of sending data to the web. These checks are never grounds for classifying a posting as `excluded`. The grounds for classification are the 8-axis judgement alone.

## Common fallback measures

Even a family-A site can, on occasion, become unreachable directly because of a specification change, dynamic rendering, or a temporary outage. In that case, fall back as follows.

| Measure | Content |
|---|---|
| The search engine's `site:` operator | Search `site:{domain} {occupation} {work location} {condition term}` with `WebSearch`, obtain the results page or individual posting page's URL, and then read the content with `WebFetch`. Example: `site:type.jp バックエンドエンジニア 東京 リモート`. Even on a dynamically rendered site, an individual posting page is often indexed. This measure is also never used to reach an excluded site |
| Substituting a different site | A condition that cannot be retrieved from one site is substituted from another site in this catalog. The site of retrieval is always recorded in each result's `source_site` |
| Stating the retrieval's limits | States which range of which site was covered, and what was placed out of scope (member-only non-public postings, a narrowing that could not be read due to dynamic rendering, a site excluded under robots.txt), in `coverage_notes` |

Under every measure, the principle of attaching a quotation `quote` and a URL from the listing page, and never fabricating a posting that could not be retrieved, is preserved.
