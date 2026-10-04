# Criteria for selecting application-document templates

Multiple style templates for each document type are placed under `assets/templates/`. This document is the canonical definition of which template to choose for which situation, what each template's structure is based on, and how a conflict between sources was resolved. The writer (`job-change-document-writer`) chooses one template from the table below at Step 1's format selection, and fills it in without breaking the chosen template's structure. The auditor (`job-change-document-auditor`) uses it to check whether a document has the required items of its selected template.

A template is the canonical definition of structure. The standard for quantification, the ban on exaggeration, and per-company tailoring is in `shokumu-keirekisho.md`, `rirekisho.md`, `english-resume.md`, and `tailoring.md`.

## Template notation

- `{profile.…}` refers to a field of `profile.json`. The writer fills it in with that value alone, and for an item with no value either omits the line or writes "特になし" (none in particular); each template specifies which.
- `{axis.…}` is a key path inside `{AXIS}`, the axis source resolved by "Location" in the hub's `references/axis-format.md` (such as `{axis.job_change_axis.reasons[]}` and `{axis.targets.industries}`). When the key has no value, or `{AXIS}` resolves to no file, the writer does not use any wording drawn from it and follows the template's instruction for a missing value.
- The generic 履歴書 (generic mode, used without a target company) leaves the 志望動機 field with the note （応募先ごとに記入）.
- `{…}` without a `profile.` or `axis.` prefix is a value filled in from something other than `profile.json` and `{AXIS}`: the job posting, company research, the drafting date, and so on.
- `<!-- -->` is a writing instruction for the writer, and is never left in the deliverable.
- A heading's wording follows the source's own notation as is. When the employer specifies its own format, follow that format and leave the template unused.
- A template is written in Markdown. Right-alignment and centring (for a date, a name, "以上" [the end]) cannot be expressed in Markdown. Wherever the instructions say "right-align," adjust for it when exporting to Word, PDF, or another format. No positioning is fixed while the document stays in Markdown.
- A date may be rewritten from `profile.json`'s `period` (`2022-04〜2024-03`) into a Japanese-style date such as "2022年4月から2024年3月まで" (from April 2022 to March 2024). A string in `achievements[].metric` is copied verbatim, character for character. The auditor checks this same distinction by the same standard.
- Register is split by section. The career summary, career history, and skills sections are written in the plain style (常体, the である form). The self-PR and statement-of-motivation sections, being addressed to the hiring manager, are written in the polite style (敬体, the です・ます form). Mixing the plain and polite styles within one document is acceptable as long as it follows this rule of splitting register by section.

## Template list

| File | Document type | Style | Where it fits |
|---|---|---|---|
| `shokumu-keirekisho-chronological.md` | shokumu-keirekisho (career history document) | Chronological (編年体式) | A consistent career in the same industry and occupation, wanting to show a process of growth |
| `shokumu-keirekisho-reverse.md` | shokumu-keirekisho | Reverse-chronological (逆編年体式) | The most recent role is close to the target job |
| `shokumu-keirekisho-career.md` | shokumu-keirekisho | Career style (キャリア式) | Frequent job changes, or wanting to show cross-field experience organized by field |
| `shokumu-keirekisho-engineer.md` | shokumu-keirekisho | IT engineer style (ITエンジニア式) | A technical role. Needs a technical-skills section and a project-by-project career history |
| `rirekisho-mhlw.md` | rirekisho (résumé form) | MHLW format example (厚労省様式例) | The default when the employer specifies no format |
| `rirekisho-conventional.md` | rirekisho | Conventional format (従来様式, former JIS-equivalent) | The employer specified a format with fields for spouse, dependants, and commute time |
| `english-resume-reverse-chronological.md` | English résumé | Reverse-chronological | The default. A job change within the same field |
| `english-resume-combination.md` | English résumé | Combination | A job change across industry or occupation, wanting to show skills first |
| `english-resume-functional.md` | English résumé | Functional | A large gap or discontinuity in the career history. Weak against ATS |
| `motivation-rirekisho-field.md` | Statement of motivation | 履歴書の志望動機欄 (the rirekisho's motivation field) | 200 to 300 characters, written into the rirekisho or shokumu-keirekisho field |
| `motivation-letter.md` | Statement of motivation | A standalone motivation letter (志望動機書, one A4 page) | The employer asked for a submitted motivation letter |
| `self-pr.md` | 自己PR (self-PR) | 結論→証明→貢献 (conclusion → proof → contribution) | The self-PR field of the shokumu-keirekisho or rirekisho |

## Shokumu-keirekisho

### The skeleton common to every style

Across the fifteen sources surveyed (below), the shokumu-keirekisho has the following seven items: five required, one recommended and one optional. The difference among the three formats is only in how "職務経歴" (career history) is ordered internally and by what unit. The section structure itself is the same (sources S3 and S4 show the same section structure for the chronological and reverse-chronological formats).

| Order | Heading | Required | Source |
|---|---|---|---|
| 1 | The title "職務経歴書" (Shokumu-keirekisho), with a right-aligned date and name | Required | S2, S3, S6, S8 |
| 2 | 職務要約 (career summary) | Required | All sources |
| 3 | 職務経歴 (career history) | Required | All sources |
| 4 | 活かせる経験・知識・スキル (transferable experience, knowledge, and skills) | Recommended | S2, S3, S6, S8, S9, S13 |
| 5 | 資格・免許 (licences and qualifications) | Required (write "特になし" [none in particular] when there are none) | S1, S2, S3, S8, S10 |
| 6 | 自己PR (self-PR) | Required | S1 to S4, S6 to S10, S12 to S14 |
| 7 | 志望動機・転職理由 (statement of motivation / reason for changing jobs) | Optional | S9, S10, and S12 each state it is "not required" |

The company overview within 職務経歴 (career history) centres on four items: 会社名（正式名称） (company name, the formal name), 事業内容 (line of business), 資本金 (capital), and 従業員数 (employee count). It treats 売上高 (revenue), 設立年 (year founded), and 上場区分 (listing status) as optional (S3, S8, S9, S10, S12, S13, S14). Since `profile.json` records only the company name and period, fill in line of business, capital, and employee count from a claim in `company_research.json`, or omit the line entirely when there is none. Never invent one.

### Length

| Item | Standard adopted | Conflicts with sources |
|---|---|---|
| Total page count | One to two A4 pages for roughly seven years of work experience or less, two to three pages beyond that | S8. The other sources split between one to two pages (S1, S2) and two to three pages (S3, S6, S10). S7 rejects the constraint itself. This adopts the one source that splits the case by years of experience |
| 職務要約 (career summary) | 200 to 300 characters (three to five lines) | The character-count camp (S2 around 250 characters, S8 200 to 300 characters) and the line-count camp (S1 two to five lines, S3 three to four lines, S9 three to five lines, S10 within five lines). A value that fits both ranges |
| 自己PR (self-PR) | 200 to 400 characters | S8. S1 calls for three bullet points or prose within five lines; S10 calls for around 300 characters. The standalone self-PR (`self-pr.md`) follows M7: around 300 characters and 400 at most, a value that fits both ranges |

### How the three formats order the entries

| Format | How 職務経歴 (career history) is ordered | Note |
|---|---|---|
| Chronological (編年体式) | Oldest first. One block per company | S1 (リクルートエージェント) treats this as the default when nothing else is specified |
| Reverse-chronological (逆編年体式) | Newest first. One block per company | S8 (リクナビNEXT) calls this "the most common." S4 alone says "only an overview for anything but the most recent role," but since no other source says so, this is treated as an optional compression |
| Career style (キャリア式) | One block per field (or project) | Only S5 instructs a brief chronological list at the top, but this is adopted to make up for the drawback that the chronology becomes unreadable |

How to choose the default: when nothing is specified, sources split over which of the chronological and reverse-chronological formats is standard (S1 vs. S8). This skill uses the reverse-chronological format when the most recent role is close to the target job, and the chronological format otherwise. It uses the career style for frequent job changes or a career that spans multiple fields.

### Variation by occupation

- **IT engineer**: a separate technical-skills section (environment, languages used) is added (S7, S11, S12). 職務経歴 (career history) is written project by project (period, project, team structure and role, responsibility, outcome, technology used; S12, S15). Given its own template.
- **Sales**: the section list stays as it is. 職務経歴's achievements are written per fiscal year as an absolute value and a relative value for 「売上・目標達成率・社内順位」 (revenue, target-achievement rate, in-house ranking) (S13). Treated as the guidance for the achievements field of the chronological and reverse-chronological templates.
- **Management**: the section list stays as it is. The shokumu-keirekisho has no separate 「マネジメント経験欄」 (management experience section) (S6). The company block adds the department, title, and number of subordinates, and achievements are shown by headcount together with how organizational challenges were addressed (S6, S14). No source asks for budget scale.

## Rirekisho

### Choosing between the two formats

- The **MHLW format example** (厚労省様式例, published April 16, 2021) is the default. In July 2020, the Japanese Standards Association (日本規格協会) removed the rirekisho format example from its commentary on the JIS standard. 厚生労働省 (the Ministry of Health, Labour and Welfare, MHLW) then created a replacement format example (R3 to R5, primary/official).
- The **conventional format** (従来様式) is used only when the employer specifies a format with fields for spouse, dependants, and commute time (R29).

### The MHLW format example's items

| Order | Item | Handling |
|---|---|---|
| 1 | "　年　月　日現在" (as of [date]) | The submission date (for mail, the posting date). Use one calendar system, Western or Japanese era, across the whole document (R9, R14, R21) |
| 2 | ふりがな・氏名 (reading and name) | Hiragana when the label reads "ふりがな," katakana when it reads "フリガナ" (R14) |
| 3 | 生年月日（満　歳） (date of birth, age) | |
| 4 | 性別 (sex) | An optional field. It may be left blank, and is never turned into a 男・女 choice (R24, R26, R28; MHLW states 「性別の回答を強要することのないよう配慮」 (care not to compel an answer on sex)) |
| 5 | 写真 (photo) | Optional (R25). When attached, it is 4 cm by 3 cm and taken within the past three months (R9, R13, R14, R21) |
| 6 | ふりがな・現住所（〒）・電話・E-mail (reading, current address with postal code, phone, email) | The prefecture is never omitted (R14) |
| 7 | 連絡先 (contact address) | Only when it differs from the current address (R14) |
| 8 | 学歴・職歴 (education and work history, each grouped separately) | The entry rules below |
| 9 | 免許・資格 (licences and qualifications) | The year and month obtained, and the formal name |
| 10 | 志望の動機、特技、好きな学科、アピールポイントなど (motivation, special skills, favourite subjects, points to appeal, and so on) | 200 to 300 characters. `motivation-rirekisho-field.md` |
| 11 | 本人希望記入欄 (the applicant's-own-requests field) | Write "貴社規定に従います" (I will follow your company's policy) when there is no request (R17, R21, R22). Never write "特になし" (none in particular), leave it blank, or state a specific figure for compensation (R17, R22) |

An item absent from the MHLW format example (commute time, number of dependants, spouse, spousal support obligation) is never added. MHLW states that adding an item absent from the format example must be done with care not to run against the standard of fair hiring selection (R3).

### Entry rules for education and work history

| Rule | Wording adopted | Conflicts with sources |
|---|---|---|
| Where education starts | Starting from "○○高等学校 卒業" (graduated from ○○ High School) when the highest level of education is high school or above | R13, R21. R9 starts a high-school graduate from high-school entry, and R15 also allows a graduate-school completer to include university entry. This adopts the majority view |
| Order of work history | Oldest first. The company name is its formal name | R13 |
| Reason for leaving | "一身上の都合により退職" (resigned for personal reasons) / "会社都合により退職" (left due to company circumstances) | R15, R21 |
| Currently employed | "現在に至る" (to the present). When the leaving date is set: "現在に至る（○年○月○日退職予定）" (to the present, scheduled to leave on [date]) | R15. R13 and R21 also allow "在職中" (currently employed), but this fixes on "現在に至る" for consistency |
| Closing | "以上" (the end), right-aligned on the next line | R9, R15, R21 |
| A gap in work history | Never written on the rirekisho. Use `profile.career_gaps`'s explanation in the shokumu-keirekisho's career summary or self-PR instead | This skill's own organization of the point |

## English résumé

### Choosing among the three styles

| Style | Where it fits | Source |
|---|---|---|
| Reverse-chronological | The default. A continuous career in the same field | E8 (Indeed), E13 (Michael Page Japan), E15 (Japan Dev) |
| Combination | Changing industry or occupation. Shows skills and achievements first and keeps the work history in newest-first order | E9 (Indeed), E5 (JMU) |
| Functional | A large gap or discontinuity in the work history, wanting the reader to focus on ability | E7 (Indeed), E5 (JMU). Because the headings become field names, it fits poorly with the ATS standard-heading rule (E12) |

### Section structure

| Order | Heading | Required | Source |
|---|---|---|---|
| 1 | Name and contact information (placed in the body, never in a header/footer) | Required | E4, E8, E12 |
| 2 | Summary | Required | E10, E13, E15 |
| 3 | Objective | Optional | E10 |
| 4 | Work Experience (in Combination, Skills / Key Achievements comes first; in Functional, this is replaced by sections organized by field, with an Employment History list at the end) | Required | E8, E9, E13 |
| 5 | Education | Required | E8, E14, E15 |
| 6 | Skills (a licence or qualification is written as one line in this section) | Required | E12, E15 |
| 7 | Languages | Required | E15 |
| 8 | Additional Information | Optional | エンワールド (en world) (`english-resume.md`) |

### Decisions made

- **Summary is required; Objective is optional.** The existing `english-resume.md` follows エンワールド (en world) and includes OBJECTIVE in its structure. E15, however, calls "Objective" a mistaken label, E13 uses only Professional Summary / Career Profile, and E10 aims Objective at someone with little experience. Since this skill's users are mid-career, Summary is adopted.
- **Education follows Experience.** E8, E14, and E15, aimed at mid-career hires, place Experience first. E2 and E4, aimed at students, place Education first, but they target a different audience.
- **The Languages section is required.** For a foreign-affiliated employer in Japan, E15 requires this section and instructs writing speaking and reading/writing separately. Stating a JLPT level is optional.
- **Residence status is written as one line in Summary.** E15's instruction. No source giving a detailed format could be obtained, so this stays at one line.
- **Tense**: the present tense for the current role, the past tense for a past role (E4). E14 allows either as long as it is consistent across the whole document, but E4's rule is clearer.
- **Number of bullet points**: three to five for the most recent role, three for an earlier one (E4 gives three to four, E8 gives five for the most recent and three for earlier ones; a range that fits both). One to two lines per point.
- **Length**: one page. Two pages for more than ten years of experience (E8). E14 allows up to three A4 pages, but E2, E4, and E5 cap it at two pages.
- **ATS formatting** (E2, E11, E12, E15): one column with no tables, text boxes, images, or skill bars. Name and contact information go in the body, outside any header/footer. Use standard heading names (Work Experience / Education / Skills), a standard 10 to 12pt font, and a text-based PDF or .docx.
- **Personal information never included**: photo, age, date of birth, sex, marital status (E1, E4, E15). E14 calls for a date of birth, but this contradicts every other source and is not adopted.

## Statement of motivation and self-PR

### The three types and their length

| Type | Structure | Length | Source |
|---|---|---|---|
| The rirekisho's or shokumu-keirekisho's motivation field | 書き出し（結論） (opening: conclusion) → 根拠となるエピソード (grounding episode) → 締めくくり（入社後の貢献） (closing: contribution after joining) | 200 to 300 characters: about 100 for the opening, 60 to 100 for the middle, 60 to 100 for the closing | M1 (リクルートエージェント), M2 (マイナビ転職). The character allocation is from M2 |
| A standalone motivation letter (志望動機書, one A4 page) | Date, the title "志望動機書," and the name → 導入 (introduction) → 業界 (industry) → 企業 (company) → 職種 (occupation) → 貢献できること (what the applicant can contribute) | 800 to 1,000 characters, filling about 80% of the page. The per-paragraph allocation (about 100 characters for the introduction, 150 to 200 for the industry, about 200 each for the company, occupation, and contribution) is this skill's own organization of the point; the sources do not give this split | M12, M13. M18 gives around 800 characters |
| Self-PR | 結論（強み） (conclusion: a strength) → 証明（行動と結果） (proof: action and result) → 貢献 (contribution) | Around 300 characters, 400 at most. One strength, three at most | M7 (JAC). M9 allows up to 600 characters, but this matches M7's upper limit |

### Decisions made

- **A standalone motivation letter omits the opening/closing salutation (拝啓・敬具) and the seasonal greeting.** M11 alone calls for one; M12, M13, and M14 all call for none. This also avoids overlapping in role with a cover letter.
- **The motivation letter's header is the date, the title, and the name, with no addressee.** This follows M12 and M13. M14 adds an addressee, and M18 places the addressee at the top left, but this adopts the majority view.
- **The opening states a conclusion addressed to the company.** This follows M1's pattern, "貴社を志望する理由は◯◯だからです" (the reason I wish to join your company is ◯◯). M2's pattern, "私は○○に携わりたい" (I want to work on ○○), turns into a sentence facing the applicant, and is not adopted.
- **No fixed length is set for the shokumu-keirekisho's motivation field.** No obtained source gives a number. It follows the same structure as the rirekisho field, targeting 200 to 300 characters.
- **The self-PR's structure never uses the names PREP or STAR.** M3, M7, and M9 are all aimed at mid-career hires and do not use either name. M20 uses a name and is aimed at new graduates. The structure itself is the same (conclusion → proof → contribution); only the name is dropped.
- **Never written** (M1, M2, M6, M11, M14):
  - making compensation or working conditions the main reason;
  - dissatisfaction with a former employer;
  - praise for the company culture that could apply to any company;
  - the passive "学ばせていただく" (I would be allowed to learn) pattern;
  - motivation expressed only as "頑張ります" (I will do my best).

## Sources

The canonical definition of the evidence levels is in `references/evidence-grading.md` of `job-change-company-research`. A practical explainer from a staffing agency or job-change site is graded B (reliable secondary), and an individually run media site is graded C. The MHLW's PDF and Excel files could not be machine-extracted in their body text, so the item list was built from agreement between the official HTML page and multiple secondary sources. doda, レバテック (Levtech), and Robert Walters could not be retrieved, and are not included among the sources.

### Shokumu-keirekisho (S)

| id | Publisher | Title | URL | Level |
|---|---|---|---|---|
| S1 | リクルートエージェント | 職務経歴書の書き方まとめ | https://www.r-agent.com/guide/resume/ | B |
| S2 | マイナビ転職 | 職務経歴書（職歴書）の書き方マニュアル完全版・例文集 | https://tenshoku.mynavi.jp/knowhow/sample/ | B |
| S3 | マイナビ転職エージェント | 「編年体式」「逆編年体式」の職務経歴書の書き方やポイントを紹介！ | https://mynavi-agent.jp/knowledge/prepare/683.html | B |
| S4 | エン転職 | 「編年体式」「逆編年体式」の職務経歴書の書き方 | https://employment.en-japan.com/tenshoku-daijiten/9217/ | B |
| S5 | エン転職 | キャリア式の職務経歴書の書き方 | https://employment.en-japan.com/tenshoku-daijiten/8248/ | B |
| S6 | JAC Recruitment | 職務経歴書の書き方 完全ガイド | https://www.jac-recruitment.jp/market/knowhow/resume/ | B |
| S7 | type転職エージェント | 【職務経歴書の書き方】簡単に作れるテンプレート・フォーマット付き | https://type.career-agent.jp/knowhow/documents/keirekisho/ | B |
| S8 | リクナビNEXT | 職務経歴書の書き方完全ガイド | https://next.rikunabi.com/tenshokuknowhow/shokurekisho/ | B |
| S9 | リクルートダイレクトスカウト | 職務経歴書の書き方と職種別の書き方見本 | https://directscout.recruit.co.jp/contents/article/28759/ | B |
| S10 | LHH転職エージェント | 職務経歴書の書き方・職種別サンプルダウンロード | https://www.lhh.com/ja-jp/insights/career-credentials | B |
| S11 | Green | プロフィールテンプレートの確認 | https://www.green-japan.com/guide/profile/templates | B |
| S12 | マイナビクリエイター | 職務経歴書の書き方 | https://mynavi-creator.jp/knowhow/article/resume-free-download | B |
| S13 | 日経転職版 | 法人営業の職務経歴書テンプレート | https://career.nikkei.com/knowhow/shokureki/000273/ | B |
| S14 | ジャスネットキャリア | 一般事業会社の管理職の職務経歴書の書き方とサンプル | https://career.jusnet.co.jp/resume/sample/cv_company_management/ | B |
| S15 | きっかけエージェント | ITエンジニア転職用｜履歴書・職務経歴書のテンプレートと書き方 | https://kikkakeagent.co.jp/column/guide/898 | B |

### Rirekisho (R)

| id | Publisher | Title | URL | Level |
|---|---|---|---|---|
| R1 | 厚生労働省 ハローワークインターネットサービス | 履歴書・職務経歴書の書き方 | https://www.hellowork.mhlw.go.jp/member/career_doc01.html | A |
| R3 | 熊本労働局 | 厚生労働省履歴書様式例の作成について | https://jsite.mhlw.go.jp/kumamoto-roudoukyoku/newpage_00155.html | A |
| R4 | 石川労働局 | 履歴書様式例 | https://jsite.mhlw.go.jp/ishikawa-roudoukyoku/roudoukyoku/annai02/syokugyou_antei/job/rirekisyo_youshikirei.html | A |
| R5 | 栃木労働局 | 履歴書様式例（厚生労働省） | https://jsite.mhlw.go.jp/tochigi-roudoukyoku/newpage_01671.html | A |
| R9 | リクナビNEXT | 履歴書の書き方完全ガイド | https://next.rikunabi.com/tenshokuknowhow/rirekisho/ | B |
| R10 | リクナビNEXT | 転職活動の志望動機の文字数の目安は？ | https://next.rikunabi.com/tenshokuknowhow/rirekisho/douki/other01/ | B |
| R13 | マイナビ転職 | 履歴書の書き方【簡単作成】見本・記入例あり | https://tenshoku.mynavi.jp/knowhow/rirekisho/ | B |
| R14 | マイナビ転職 | 履歴書 基本情報欄の書き方 | https://tenshoku.mynavi.jp/knowhow/rirekisho/01/ | B |
| R15 | マイナビ転職 | 履歴書 学歴・職歴欄の書き方 | https://tenshoku.mynavi.jp/knowhow/rirekisho/02/ | B |
| R17 | マイナビ転職 | 【履歴書】本人希望記入欄の書き方と例文 | https://tenshoku.mynavi.jp/knowhow/rirekisho/05/ | B |
| R18 | マイナビ転職 | 【履歴書】配偶者・扶養家族とは？ | https://tenshoku.mynavi.jp/knowhow/rirekisho/09/ | B |
| R21 | タウンワークマガジン | 履歴書の書き方～転職編の基本ガイド | https://townwork.net/magazine/knowhow/resume/t_resume/ | B |
| R22 | エン転職 | 【本人希望記入欄】の書き方 | https://employment.en-japan.com/resume_guide/14204/ | B |
| R24 | laborblog.work | 履歴書のJIS規格様式は廃止、厚労省様式の性別欄は任意記載に | https://laborblog.work/resume/ | C |
| R25 | 日本法令 | 履歴書（厚生労働省履歴書様式例準拠） | https://www.horei.co.jp/iec/products/view/3155.html | B |
| R26 | keireki.net | 厚生労働省推奨の履歴書とは？JIS規格との違い | https://keireki.net/rkkksrds/ | C |
| R28 | Wikipedia 日本語版 | 履歴書 | https://ja.wikipedia.org/wiki/履歴書 | C |
| R29 | 履歴書Do | 履歴書の扶養家族と配偶者欄の書き方 | https://www.rirekisyodo.com/papers/rirekisho-dependent.html | C |

### English résumé (E)

| id | Publisher | Title | URL | Level |
|---|---|---|---|---|
| E1 | Harvard FAS Mignone Center for Career Success | Harvard College Guide to Creating a Strong Resume | https://careerservices.fas.harvard.edu/resources/create-a-strong-resume/ | B |
| E2 | MIT CAPD | Career toolkit: Crafting an effective resume | https://capd.mit.edu/resources/career-toolkit-crafting-an-effective-resume/ | B |
| E4 | Yale Office of Career Strategy | Resume Formatting and Common Errors | https://ocs.yale.edu/resources/resume-formatting/ | B |
| E5 | James Madison University Career Center | Choosing a Résumé Format | https://www.jmu.edu/career/students/career-prep/resumes/format.shtml | B |
| E7 | Indeed | Chronological vs Functional Resumes | https://www.indeed.com/career-advice/resumes-cover-letters/chronological-vs-functional-resume | B |
| E8 | Indeed | How to Write a Chronological Resume | https://www.indeed.com/career-advice/resumes-cover-letters/chronological-resume-tips-and-examples | B |
| E9 | Indeed | Combination Resume Tips and Examples | https://www.indeed.com/career-advice/resumes-cover-letters/combination-resume-tips-and-examples | B |
| E10 | Indeed | Resume Summary vs. Resume Objective | https://www.indeed.com/career-advice/resumes-cover-letters/resume-summary-vs-objective | B |
| E11 | Jobscan | Anatomy of an ATS Friendly Resume Format | https://www.jobscan.co/blog/20-ats-friendly-resume-templates/ | B |
| E12 | Jobscan | 5 Critical ATS Resume Formatting Mistakes to Avoid | https://www.jobscan.co/blog/ats-formatting-mistakes/ | B |
| E13 | Michael Page Japan | 3 impactful resume templates | https://www.michaelpage.co.jp/en/advice/career-advice/resume-and-cover-letter/resume-templates-writing | B |
| E14 | Daijob | CV | https://www.daijob.com/en/guide/tipsadvice/resume/cv/ | B |
| E15 | Japan Dev | How to write a perfect developer resume in Japan | https://japan-dev.com/blog/developer-english-resume-japan | B |

### Statement of motivation and self-PR (M)

| id | Publisher | Title | URL | Level |
|---|---|---|---|---|
| M1 | リクルートエージェント | 志望動機の書き方と例文54種 | https://www.r-agent.com/guide/motive/1672/ | B |
| M2 | マイナビ転職 | 履歴書の志望動機は「書き出し」と「締めくくり」で差を付ける！ | https://tenshoku.mynavi.jp/knowhow/shibodoki/01/ | B |
| M3 | マイナビ転職 | 自己PR例文・書き方・テンプレ | https://tenshoku.mynavi.jp/knowhow/pr_sample/ | B |
| M6 | type | 「魅力が伝わる」志望動機の書き方 | https://type.jp/tensyoku-knowhow/technique/reason/ | B |
| M7 | JAC Recruitment | 職務経歴書の自己PRの書き方 | https://www.jac-recruitment.jp/market/knowhow/resume/selfpr/ | B |
| M9 | エン転職 | 職務経歴書の自己PRの書き方 | https://employment.en-japan.com/tenshoku-daijiten/10181/ | B |
| M11 | ハタラクティブ＋ | 志望動機書の書き方とは？ | https://hataractive-plus.jp/article/resume/106/ | B |
| M12 | 40代 転職の極意 | 志望動機書のテンプレート | https://xn--u9j177ljjfdzyj6p.jp/siboudoukisyo/ | C |
| M13 | 転職エージェント総合ガイド | 志望動機書の書き方 | https://agent-guide.com/中谷充宏/志望動機書/ | C |
| M14 | ミライトーチResume | 志望動機書とは？書き方を解説 | https://miraitorch-career.com/service/motivation-letter/ | C |
| M18 | doda | 志望動機・志望理由の書き方 | https://doda.jp/guide/rireki/douki/ | B (from the search-result summary only; the body text could not be retrieved) |
| M20 | PORTキャリア | 自己PRの構成作成ガイド｜PREP・STAR法 | https://www.theport.jp/portcareer/article/60948/ | C (aimed at new graduates) |

## Scope and limits of this standard

- Every source is a web page as of August 2026. The MHLW format example itself could not have its body text extracted; the item list rests on agreement between the official HTML and secondary sources.
- The shokumu-keirekisho's length and the career summary's length vary by source. The values in this document were chosen to fit within the range of multiple sources, and no single value is the correct one.
- A cover letter (添え状/送付状) and an English cover letter are not among this skill's document types, so no template is provided for either.
