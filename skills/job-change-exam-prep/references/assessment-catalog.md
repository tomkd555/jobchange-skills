# Aptitude test catalog

This summarizes the providers, structure, administration method, and question format of the major written tests and aptitude tests used in mid-career hiring. It is used to interpret Step 1's investigation results (`exam_assessment.json`), design Step 2's study items, and understand Step 3's question formats.

## How to read this

- Each item carries a source URL. Evidence levels are A = primary/official, B = reliable secondary, C = review-site aggregation/preparation outlet, D = personal blog/hearsay/unconfirmed. Including preparation outlets under C is how this applies in the context of selection exams; the canonical definition lives in `job-change-company-research/references/evidence-grading.md`.
- Figures such as completion rates or sample sizes published by a provider or preparation outlet are treated as self-reported figures that have not passed independent verification. They are not used as grounds for an assertion.
- A peer-reviewed study in which an independent third party verified the predictive validity of an individual commercial test (SPI3, 玉手箱, etc.) itself, on a Japanese sample, has not been found even in the additional search as of July 2026. Peer-reviewed meta-analyses verifying cognitive-ability tests in general and the managerial-aptitude test NMAT on Japanese samples do exist (see "Note on the absolute level of validity" in `references/prep-methods.md`). Because the validity of individual commercial tests is likely to rest on non-peer-reviewed material from their providers, a provider's own validity claims are not used as grounds for an assertion.
- The details of subjects, time, and method can vary by test version and by the settings the adopting company chooses. What is shown here is the representative structure.
- The names to write into `exam_assessment.json`'s `type` field follow the notation in the two listing tables below exactly. `references/exam-assessment-format.md` and `scripts/validate_exam_assessment.py` reference this vocabulary.

## Catalog of major domestic assessments

| Assessment | Provider | Ability-test subjects | Personality test | Main administration methods |
|---|---|---|---|---|
| SPI3 | Recruit Management Solutions | Verbal, non-verbal | Yes | Test Center / Web Testing / Paper Testing / In-house CBT |
| 玉手箱 | Nihon SHL (Japan SHL) | Verbal, quantitative, English | Yes | Mainly the take-at-home web format |
| GAB | Nihon SHL | Verbal, quantitative (logical reasoning) | Yes | Paper / Web |
| CAB | Nihon SHL | Four arithmetic operations, rule inference, instruction tables, code-breaking | Yes | Paper / Web |
| TG-WEB | Humanage | Quantitative, verbal (classic / new type) | Yes | Web / Test Center |
| TAL | Jinsouken | 36 text questions plus 1 figure-placement question | Measuring personality traits is the main focus | Web |
| 内田クレペリン検査 | Japan Institute for Psychotechnology | Single-digit continuous addition | Judged from work characteristics | Mainly paper |

## Catalog of other types

This lists types that do not fit the table above. A personality test is built into many aptitude tests. The name "性格検査" (personality test) is used when only the fact that a personality test is administered is known, without the assessment's brand being identified. Case interviews and Fermi estimation are interview formats, but because they are given as part of written/online selection, they are listed here, distinguished by the "Category" column.

| Type | Category | Provider | Content | Direction of preparation |
|---|---|---|---|---|
| 性格検査 | Questionnaire | Built into each aptitude test (also administered standalone) | Numerous questions asking about behavior and inclinations | No answer meant to look favorable; consistent, honest answers (`references/prep-methods.md`) |
| HireVue | Recorded interview | HireVue | Recorded answers to questions presented on video. May include game-format tasks | Practice stating the conclusion first, within the time limit. Checking equipment and connectivity |
| pymetrics | Game-based assessment | pymetrics (Harver) | Measures cognitive and behavioral traits from responses to a series of game tasks | Preparation through knowledge has little effect. Limit to checking the operation beforehand |
| 英語オンラインテスト | Ability test | Nihon SHL / IBM Kenexa, etc. | Verbal, quantitative, and logical reasoning in English | Become accustomed to taking the test in English |
| ケース面接 | Interview format | The hiring company (consulting firms, etc.) | Analyzing a presented issue aloud and stating a conclusion | Practicing the thinking pattern (confirm premises → structural decomposition → hypothesis → conclusion) |
| フェルミ推定 | Interview format | The hiring company (consulting firms, etc.) | Estimating an unknown quantity by setting premises and decomposing it | Same as above. Organizing the thinking process |

Details and sources for each type are in the "Position of the personality test" and "Foreign-affiliated online assessments" sections.

## Details of each assessment

### SPI3

SPI3 is an aptitude test provided by Recruit Management Solutions. It is composed of an ability test (verbal, non-verbal) and a personality test. There are four administration methods: "Test Center," taken at a dedicated venue; "Web Testing," taken at home or elsewhere; "Paper Testing," taken on paper at the applicant company's venue; and "In-house CBT," taken on a computer at the applicant company. The questions and time-limit handling differ by method.

- Source: Recruit Management Solutions, 「適性検査『SPI』とは？」 ("What Is the Aptitude Test 'SPI'?") https://www.recruit-ms.co.jp/freshers/spi-001.html (Level B. Explanation from the provider)

### 玉手箱

玉手箱 is a web-based aptitude test provided by Nihon SHL (Japan SHL), composed of an ability test (verbal, quantitative, English) and a personality test. It is characterized by presenting many questions of the same format in rapid succession over a short time; the time available per question is short, so time management is key.

- Source: Nihon SHL, 「SHL の適性検査（玉手箱 III・GAB・CAB・RAB）を徹底比較」 ("A Thorough Comparison of SHL's Aptitude Tests (Tamatebako III, GAB, CAB, RAB)") https://www.shl.co.jp/column/perspective/220617ysato/ (Level B. Explanation from the provider)
- Source (supplement on the question subjects): unistyle, 「【玉手箱の完全対策】言語・計数・英語の例題や出題企業を掲載」 ("The Complete Guide to Tamatebako: Verbal, Quantitative, and English Example Questions and Companies That Use It") https://unistyleinc.com/techniques/962 (Level C. Preparation outlet)

### GAB・CAB

Both are provided by Nihon SHL. GAB is aimed at the general career track and measures logical reasoning through verbal and quantitative sections; CAB is aimed at computer-related roles (systems engineers, programmers, etc.) and measures aptitude for information processing through subjects covering four arithmetic operations, rule inference, instruction tables, and code-breaking.

- Source (GAB): Nihon SHL, "A Thorough Comparison of SHL's Aptitude Tests (Tamatebako III, GAB, CAB, RAB)" https://www.shl.co.jp/column/perspective/220617ysato/ (Level B)
- Source (CAB): Nihon SHL, "CAB" https://www.shl.co.jp/service/assessment/cab/ (Level B. Explanation from the provider)

### TG-WEB

TG-WEB is an aptitude test provided by Humanage. Its ability test, covering quantitative and verbal sections, has two lines: a classic type and a new type. The classic type includes higher-difficulty questions such as figures and code-breaking. The new type is said to tend toward processing a large number of questions in a short time. Preparation outlets describe the classic type's quantitative section as about 18 minutes and the new type's as about 8 minutes. For mid-career hiring, TG-WEB CAREER is offered.

- Source: Humanage, 「ヒューマネージの適性検査 TG-WEB」 ("Humanage's Aptitude Test TG-WEB") https://tg-web.humanage.co.jp/ (Level B. Explanation from the provider. The classic/new distinction and TG-WEB CAREER)
- Source (time estimates for classic/new type): DYM, 「TG-WEB 対策とは？新型と旧型の見分け方や例題と練習方法」 ("What Is TG-WEB Preparation? How to Tell New from Old Type, with Example Questions and Practice Methods") https://dym.asia/media/recruiting/tgweb/ (Level C. Preparation outlet. The time figures come from this outlet's explanation)

### TAL

TAL is an aptitude test provided by Jinsouken. It is composed of 36 text-based questions and 1 question involving placing figures. There are almost no official practice questions or preparation books, so preparation aimed at a clear correct answer does not hold well. Because its main focus is measuring personality and latent tendencies, this skill treats it as an assessment where preparation is difficult.

- Source: OneCareer, 「適性検査 TAL とは？特徴や対策方法、例題と解答のポイントを解説」 ("What Is the TAL Aptitude Test? Its Characteristics, How to Prepare, and Points on Example Questions and Answers") https://www.onecareer.jp/articles/5364 (Level C. Preparation outlet)

### 内田クレペリン検査

内田クレペリン検査 is a work-sample test provided by the Japan Institute for Psychotechnology. It involves continuous single-digit addition for a first 15-minute session and a second 15-minute session, 30 minutes in total, and judges processing ability and work-related traits from three factors: the work volume (total amount calculated), the work curve (the minute-by-minute change in work volume), and errors. Because the assessment measures work-sample performance, preparation through memorizing knowledge has little effect.

- Source: Japan Institute for Psychotechnology, 「内田クレペリン検査 〜検査について」 ("About the Uchida-Kraepelin Test") https://www.nsgk.co.jp/uk/whatis (Level B. Explanation from the provider)

## Position of the personality test

Many aptitude tests are composed of an ability test and a personality test. In mid-career hiring, companies place weight on fit with the existing organization (culture fit), so the personality test tends to carry more weight. The canonical definition of the personality test's preparation policy is `references/prep-methods.md` (in short: consistent, honest answers).

- Source: Mynavi Tenshoku (Mynavi Job Change), 「転職の適性検査とは？新卒と中途の違いや目的、種類、対策法」 ("What Is the Aptitude Test for Job Changes? Differences Between New-Graduate and Mid-Career Hiring, Its Purpose, Types, and How to Prepare") https://tenshoku.mynavi.jp/knowhow/caripedia/167/ (Level C. Preparation outlet. The tendency for personality tests to carry more weight in mid-career hiring)

## Foreign-affiliated online assessments

Foreign-affiliated selection processes sometimes use a different family of online assessments from Japan's domestic aptitude tests.

### HireVue (recorded interview plus game tasks)

HireVue is an asynchronous recorded interview in which the applicant records answers to questions presented on video. It may include game-format tasks. AI-based facial-expression analysis was removed by HireVue from new assessments in early 2021. Before the removal, the Electronic Privacy Information Center (EPIC) had filed a complaint with the U.S. Federal Trade Commission (FTC) alleging that HireVue's facial-expression analysis was unfair and deceptive. Figures such as completion rates published by the vendor are treated as self-reported.

- Source (overview): TechTarget, "What Is HireVue?" https://www.techtarget.com/searchhrsoftware/definition/HireVue (Level C)
- Source (withdrawal of facial analysis): Fortune, "HireVue stops using facial expressions to assess job candidates amid audit of its A.I. algorithms," 2021-01-19, https://fortune.com/2021/01/19/hirevue-drops-facial-monitoring-amid-a-i-algorithm-audit/ (Level C)

### pymetrics (game-based behavioral assessment)

pymetrics is an assessment that measures cognitive and behavioral traits from responses to a series of game tasks. A peer-reviewed study reports that the convergent validity of game-based assessments in general remains moderate (correlation r≈0.5).

- Source (overview): Harver / pymetrics, "Game-Based Behavioral Assessments" https://harver.com/gamified-assessments/ (Level C)
- Source (validity): "Game based assessments of cognitive ability in recruitment: Validity, fairness and test-taking experience," 2023, https://pmc.ncbi.nlm.nih.gov/articles/PMC9891208/ (Level A. Peer-reviewed paper)

### SHL / Kenexa English online tests

Foreign-affiliated selection processes may include an English-language online aptitude test (verbal, quantitative, logical, etc.) from SHL or IBM Kenexa. Applicants need to become accustomed to taking the test in English.

- Source: GraduatesFirst, "IBM Kenexa Assessments — Complete Practice Guide" https://www.graduatesfirst.com/aptitude-tests-publishers/ibm-kenexa (Level C. Preparation outlet)

### Case interviews and Fermi estimation

Consulting firms and similar companies give case interviews and Fermi estimation, weighting the thinking process (how premises are set, how the problem is decomposed, and how the hypothesis and conclusion are explained) above numerical accuracy. The canonical definition of this thinking pattern is `references/prep-methods.md`. Rehearsed answers for follow-up probing during the interview are handled by `job-change-interview-prep`.

- Source (case interviews): Management Consulted, "BCG Case Interview" https://managementconsulted.com/bcg-case-interview/ (Level C)
- Source (Fermi estimation): OneCareer, 「フェルミ推定・ケース面接を対策！」 ("Preparing for Fermi Estimation and Case Interviews!") https://www.onecareer.jp/articles/298 (Level C)
