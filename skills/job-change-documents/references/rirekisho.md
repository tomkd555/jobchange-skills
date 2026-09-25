# Rirekisho writing standard

This is the canonical definition for writing a rirekisho (résumé form) in mid-career hiring in Japan.
The writer (`job-change-document-writer`) uses it to fill the form's fixed fields, and the auditor
(`job-change-document-auditor`) uses it to check conformance with the current format and to check for
signs of reuse across applications.

The rirekisho is a document that fills in fixed fields — 学歴・職歴 (education and career history), 資格
(qualifications), 志望動機 (motivation), and the like. Its role is separate from the shokumu-keirekisho (career
history document), which shows experience and achievement in free-form prose.

## The current state of the format

The rirekisho's standard format changed at a boundary in July 2020 (Reiwa 2).

- 日本規格協会 (the Japanese Standards Association) removed the rirekisho format example it had
  carried in its commentary on the JIS standard in July 2020 (source: 厚生労働省 青森労働局 "厚生労働省が新たに作成した『履歴書様式例』を掲載しました。"
  https://jsite.mhlw.go.jp/aomori-roudoukyoku/news_topics/topics/_00051.html, primary/official).
  Since then, no official standard format called "the JIS-standard rirekisho" exists.
- In response, 厚生労働省 (the Ministry of Health, Labour and Welfare) created and now distributes a
  new rirekisho format example (a PDF version and an Excel version), from the standpoint of ensuring
  fair hiring selection (source: 厚生労働省 ハローワークインターネットサービス "履歴書・職務経歴書の書き方"
  https://www.hellowork.mhlw.go.jp/member/career_doc01.html, primary/official).

This skill uses the 厚生労働省 (MHLW) new format example as the current reference standard.

### Features of the MHLW format example

The MHLW format example reflects consideration for the applicant's privacy (source:
社会保険労務士法人アドバンス・行政書士法人アドバンス "厚生労働省の履歴書様式例 性別欄を任意記載欄に変更"
https://van.gr.jp/news/2021_0526/, word of mouth/aggregated — a secondary commentary quoting 厚生労働省's
own primary statement).

- The sex field is optional. It is an optional free-entry field, replacing the 〔男・女〕 selection; an
  applicant who does not wish to state it may leave it blank.
- 厚生労働省 does not provide a field for four items — commute time, the number of dependent family
  members excluding a spouse, a spouse, and a spouse's dependent obligation — because these touch
  privacy to a high degree. Where the employer needs them, the premise is that it asks the applicant
  directly at a later stage, such as an interview.

The writer follows the MHLW format example and writes on the premise that these four items are not
required. When the target company specifies its own format, it follows that format.

## Handwritten versus typed

- Without an instruction from the target company, the pass/fail decision treats a handwritten
  document and one typed on a computer as equivalent. A neatly typed rirekisho can itself serve as
  evidence of basic business skill.
  - Grounds and limits: this rests on this skill's own background research. Searching for
    disconfirmation of the hypothesis "handwriting is favored," this skill cross-checked that doda's
    and マイナビ転職's practical guides state that, absent an instruction from the target company,
    neither handwriting nor typing is a pass/fail criterion. The grade is word of mouth/aggregated (C);
    no primary source establishing the method of preparation as a pass/fail factor was confirmed, and
    no single citable URL remains in this skill's evidence record. This skill therefore treats it as
    support for an operating policy that gives priority to content and company-specific optimization
    over the method of preparation.
- This skill accordingly does not treat the method of preparation as a pass/fail factor. It gives
  priority to the accuracy of the content and its company-specific optimization over the choice of
  method.

## Avoiding reuse

Reusing a rirekisho or a statement of motivation across multiple companies invites a mistake where
wording aimed at an earlier target company remains.

- A mismatch — a previous company's name or business left in the 志望動機欄 (motivation field), or a self-PR that
  does not fit the target job — can read to a hiring manager as low interest in their own company.
- The writer revisits the statement of motivation and the self-PR for each company. The auditor checks
  for a proper noun or a selling point left over that does not match the target company or the target
  posting.
- The standard for company-specific tailoring of the statement of motivation lives in
  `references/tailoring.md`.

## The scope and limits of this standard

- The current format's background (the removal of the JIS format example, the MHLW format example)
  rests on 厚生労働省's primary/official information. The citations for making the sex field optional
  and for not providing the four fields come from a secondary commentary (word of mouth/aggregated
  grade) quoting 厚生労働省's own statement, but multiple independent sources agree.
- The finding that handwriting versus typing has no bearing on the pass/fail decision rests on
  practical guides from major career-change media. Because companies differ in the format and the
  submission method they specify, the target company's own instruction takes priority above all.
