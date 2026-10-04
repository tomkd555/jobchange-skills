# English resume writing standard

<!-- textlint-disable @textlint-ja/no-synonyms -->
<!-- The source cites the company name "エンワールド・ジャパン," so this keeps the linter from flagging "ジャパン" and "日本" as inconsistent spelling. -->

This is the canonical definition for the English resume used when applying to a foreign-affiliated or
global company. The writer (`job-change-document-writer`) uses it for structure, wording, and ATS
handling. The auditor (`job-change-document-auditor`) uses it for checking the correctness of English
grammar and tense, the fitness of action verbs, quantification, ATS fitness, and length. The English
resume is a separate document from the Japanese-language rirekisho, and Japanese grammar and
orthography checks do not cover it.

## Basic format

The English resume's standard format is as follows (source: エンワールド・ジャパン "英文レジュメの書き方ガイド"
https://www.enworld.com/candidates/career-advices/foreign-job-change/resume/how-to-write-english-resume.html,
reliable secondary).

| Aspect | Content |
|---|---|
| Length | One to two pages, in A4 or letter size. |
| Ordering | List the work history and education in newest-first (reverse chronological) order. |
| Register | Open each item with an action verb, and omit an unnecessary subject such as "I." Example: "Led a team of 5 engineers ...", "Reduced response time by 40% ...". |

## Structure

An English resume is built mainly from the following sections (source: same エンワールド・ジャパン,
reliable secondary).

| Item | Content |
|---|---|
| PERSONAL INFORMATION | Name and contact information. Note the "Personal information to omit" section below. |
| OBJECTIVE | A short statement of what the applicant seeks in the target role. |
| SUMMARY | A summary of the career history and strengths. |
| WORK EXPERIENCE | The work history, newest first. Write each role as bullet points opening with an action verb. |
| EDUCATION | Education, newest first. |
| QUALIFICATIONS (SPECIAL SKILLS) | Qualifications and skills. |
| ADDITIONAL INFORMATION | Supplementary information. |

The table above reflects one company, エンワールド. The structure this skill uses (SUMMARY
required, OBJECTIVE optional, and three styles: Reverse-chronological, Combination, and
Functional) and its grounds are in `references/templates.md`.

## Personal information to omit

Do not state sex, age, date of birth, or a photograph in an English resume (source: same
エンワールド・ジャパン, reliable secondary). Western countries set strict laws against discrimination
in hiring, which makes this the largest difference from the Japanese-language rirekisho. Do not carry
over the rirekisho's sense of what to include.

## Quantifying achievements

- Write each bullet point in the form "Action (verb) + Project (object, context) + Result," and
  quantify the result as "◯% improvement" or "◯% increase" (source: Yale Office of Career Strategy
  "Writing Impactful Resume Bullets" https://ocs.yale.edu/resources/writing-impactful-resume-bullets/,
  reliable secondary). Write the applicant's own contribution.
- Match a quantified value exactly to `profile.json`'s `achievements[].metric`. Do not invent a number
  absent from `metric`.

## ATS handling

Many companies process an application document through an ATS (Applicant Tracking System). An ATS
scans a document by keyword and ranks it (source: Indeed "Get Your Resume Seen With ATS Keywords"
https://www.indeed.com/career-advice/resumes-cover-letters/ats-resume-keywords, reliable secondary).

| Guideline | Content |
|---|---|
| Contextual match with the job posting | Reflect the language the job posting (job description) uses, in a form that fits the context of the experience. Use the posting's keywords naturally, within a description of the actual work and result. |
| Avoid keyword stuffing | A modern NLP-based ATS scores keywords by their context and relevance. Repeating the same word unnaturally is judged as low quality and lowers the score, and it also reads as unnatural to a human reviewer. Reflecting the posting's language works only when it comes with accurate extraction and quantified backing. Aim for contextual match with the job posting. |
| Avoid a table, an image, or graphics | An ATS can fail to parse a table, an image, or graphics (including a graph or a chart) correctly. Build the résumé with plain text formatting. |

### The problem of an ATS turning away a capable candidate

An ATS can screen out a capable candidate in error. ATS handling serves two ends: getting through,
and guarding against a wrongful rejection. (Source: Harvard Business School / Accenture "Hidden
Workers: Untapped Talent," 2021. A secondary article reports it at
https://jobcannon.io/research/stats/hbs-accenture-hidden-workers-2021, word of mouth/aggregated grade.
The primary source is the HBS/Accenture report by Fuller, Raman, and others.)

The following two statistics are separate; do not state them as causally linked.

| Statistic | Content |
|---|---|
| 88% of employers | The share of employers who acknowledged that a capable, highly skilled candidate is being vetted out during the selection process. This reflects the employers' own self-awareness that a selection mechanism, including an ATS, can screen out a capable candidate. This figure comes from one survey report (HBS/Accenture 2021) (grade C). |
| About 27 million people (hidden workers) | The total number of hidden workers, defined by employment status. Do not causally link this total with the 88% figure, as in a claim that "an ATS excluded 27 million people." |

The practical response to this problem is a contextual match with the job posting, a simplified
format, and company-specific tailoring.

### The state of foreign-affiliated ATS use inside Japan

The following concrete ATS vendors used in mid-career hiring by foreign-affiliated companies in Japan
are confirmed (as of July 2026).

| Vendor | Confirmed fact |
|---|---|
| Workday | NCR, a US-based multinational, runs its external Japan hiring site on Workday (the URL is `ncr.wd1.myworkdayjobs.com/ext_jp`, including a posting in the `ja-JP` Japanese locale. The pattern `subdomain.wdN.myworkdayjobs.com` is Workday Recruiting's definitive URL structure. Source: the NCR hiring page URL, grade B). |
| Greenhouse | Foreign-affiliated tech companies (Anthropic, Databricks, and others) publish and accept applications for their Japan-based positions on a Greenhouse job board (`job-boards.greenhouse.io`). Confirmed for a Japan-based role at Anthropic and a Tokyo-based role at Databricks. The pattern `job-boards.greenhouse.io` is Greenhouse's definitive URL structure. Source: each company's Greenhouse job board URL, grade B. |

Greenhouse states "full parsing capabilities" for a résumé in a language including Japanese in its
official support documentation (source: Greenhouse Support "Resume parsing with non-English
languages" https://support.greenhouse.io/hc/en-us/articles/205019689-Resume-parsing-with-non-English-languages,
grade A). This is the vendor's own claim, however, unverified by any third party. Japanese
appears on the list of supported languages, but that states only that it falls within the spec's
parsing scope. The same document does not give a figure showing the actual extraction accuracy for
Japanese (CJK text, with no word segmentation, in full-width characters).

Japan-based recruiting agencies also offer practical ATS-related advice for foreign-affiliated
hiring. Morgan McKinley (a recruiting agency strong in foreign-affiliated hiring) states that
companies manage application information through an ATS. It advises that editing a résumé to include
the keywords in the job posting raises the likelihood of passing the ATS screening. It also states
that a PDF file format is preferable, since a complex layout can be more than an ATS can process
(source: Morgan McKinley "英文レジュメの書き方：DX対応編," 2023-10-05,
https://www.morganmckinley.com/jp-ja/article/%E8%8B%B1%E6%96%87%E3%83%AC%E3%82%B8%E3%83%A5%E3%83%A1%E3%81%AE%E6%9B%B8%E3%81%8D%E6%96%B9%EF%BC%9ADX%E5%AF%BE%E5%BF%9C%E7%B7%A8,
grade B). The publisher, however, is a recruiting agency that offers resume-editing and job-placement
services and has an interest in stressing ATS handling (one source only).

## The scope and limits of this standard

- The format, structure, information to omit, and quantification rest on a normative guide from a
  foreign-affiliated specialist agency and a US university career center (reliable secondary).
- Two facts are confirmed (see "The state of foreign-affiliated ATS use inside Japan" above): the
  concrete ATS vendors used inside Japan (Workday, Greenhouse), and that a Japanese-language document
  falls within their parsing scope by specification (Greenhouse's own documentation). Two items
  remain unconfirmed even after additional search as of July 2026: primary quantitative data on the
  adoption rate of a foreign-affiliated ATS, and a figure showing the actual parsing accuracy for a
  Japanese resume. The search covered IMARC's Japan ATS market report, Greenhouse's own parsing
  documentation, and explanatory articles from recruiting agencies serving foreign-affiliated hiring.
  IMARC's market report is one source that does not disclose its methodology (grade C), so its
  individual figures cannot be independently confirmed, and Greenhouse's own documentation gives no
  figure on actual parsing accuracy either. Confirming with the target company or the agency directly is the
  reliable way to learn how much a domestic foreign-affiliated posting relies on an ATS.
- The 88% and 27-million figures for hidden workers come from one survey report (HBS/Accenture
  2021, grade C). Do not use them in an assertively causal statement.

<!-- textlint-enable @textlint-ja/no-synonyms -->
