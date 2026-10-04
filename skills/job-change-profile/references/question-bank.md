# Structured question set (question-bank)

This is the canonical definition of the common rules for the pre-set structured questions job-change-profile's
elicitation uses, and the correspondence table between questions and sections/fields. Each section's procedure, its
opening question, and the settled wording passed to AskUserQuestion are in each section's own `sections/{id}.md`
(the catalogue is `sections.md`). Only Step 0's wording (choosing the mode and the sections) belongs to no section,
so it is placed in this document. The grounding for recall cues and the choice-format operation is in
`elicitation-guide.md`, and the canonical definition of the field specification is in the hub's
`references/profile-format.md`.

The two common-rule sections below ("The register of the question text" and "Rules for use") also govern
`job-change-axis`'s elicitation, together with `answer-handling.md` and `elicitation-guide.md`. That skill keeps its
own correspondence table and Step 0 wording in its `references/question-bank.md`.

## The register of the question text

- The running text (this document's own description, SKILL.md's procedure) is written in plain Japanese (常体). A
  question addressed to the user, and a choice's label and description, are written in polite Japanese (敬体). Only
  text addressed to the other party is polite, and the two registers are never mixed.
- Confirmation is never phrased as a request for agreement. It is asked as 「この理解のどこが違いますか」 (where does
  this understanding differ), which avoids a question shaped so that agreement becomes the default answer.
- A choice never leads the user. The desired answer is never placed first, and a neutral or negative choice such as
  「どちらでもよい」 (either is fine) or 「不要である」 (not needed) is never dropped.
- A question never asks the user to corroborate their own statement. A form such as "can that figure be confirmed,"
  "can you prove it," or "is that really true" is never used (see "Never corroborate a user's statement" in
  `elicitation-guide.md`; the list of question types never placed is in `answer-handling.md`).
- The choice format is the form of the question, and it never constrains how the user answers. When an answer
  comes back in free text or covering several items at once, what comes in is sorted into its items, and only the
  items still unanswered are asked next (see "Handling each answer format" in `answer-handling.md`).
- Colloquial or vague phrasing is put into document-ready wording only after a reworded candidate is shown to the
  user and the user approves it. The wording for presenting a candidate is in `answer-handling.md`.

## Rules for use

- A question is run centered on AskUserQuestion's choice format. At most 4 questions per AskUserQuestion call, with
  up to 4 choices per question. When one question should take several answers, use `multiSelect: true` and keep it
  as one question.
- For a question whose choices can be enumerated in advance, use the section file's settled wording as it stands,
  never improvising the phrasing when asking. An item that cannot be enumerated (a company name, a tenure period,
  responsibilities, a project name, an achievement, a figure) is asked in free text. **No candidate is presented
  for an item whose candidates are unknown.**
- "Choice format + free text" in the correspondence table denotes receiving an answer outside the choices through
  AskUserQuestion's Other. A format that has the user pick a choice and then requires a separate free-text addition
  is never used.
- A detailed pass never leads the user into ruminating on feelings; the question is aimed at fact (when, in what
  situation, what was done). Constructive rewording of a reason for leaving, and grounding a strength, fall outside
  this skill's scope and are directed to `job-change-self-analysis`.
- The main session appends the elicitation's results to `career-private/profile_interview_notes.md` as elicitation
  proceeds.
- Eliciting one section reads only this document's common rules and that section's own `sections/{id}.md`. Another
  section's file is never read ahead of time.

## Correspondence table between questions and sections/fields

The "First pass" column marks a question asked within the first-pass scope (`sections.md`'s "Scope of the first
pass") as `初回` (first pass). A question skipped there and asked later, at a section update just before the
downstream process needs it, is marked `深掘り` (detailed pass).

| Step | Section | Question | Field it fills | Format | First pass |
|---|---|---|---|---|---|
| 1 | `career` | Whether a shokumu-keirekisho (career history document), rirekisho (résumé form), or résumé file is available | (transcribe what could be read into the elicitation notes) | Choice format | First pass |
| 1 | `career` | Where the company name, tenure period, job title, and responsibilities extracted from the document differ | Correction of each field in `career_history[]` | Free text (only for an item that differed) | First pass |
| 1 | `career` | Listing the companies worked at and their tenure periods, from oldest (or most recent) | `career_history[].company`, `career_history[].period` | Free text (company name, period) | First pass |
| 1 | `career` | The role and job title at each company | `career_history[].role` | Free text | First pass |
| 1 | `career` | Whether a period existed with 2 or more concurrent jobs, and its breakdown | Concurrent `career_history[]` elements | Choice format + free text | First pass |
| 1 | `career` | The employment type at each company, and whether a place of work exists apart from the employer (a client site, a place of dispatch, a place of secondment) | `career_history[].employment_type`, `career_history[].assignment`, `career_history[].note` | Free text (only where applicable; the canonical definition of how to record it is in "A career history with an atypical shape" in `answer-handling.md`) | First pass |
| 1 | `career` | The reason for a detected employment gap (6 months or more) and the activity during it | `career_gaps[].period`, `career_gaps[].explanation`, `career_gaps[].activities` | Choice format (activity type) + free text | First pass |
| 1 | `basic` | Basic information (current role, years of experience, place of residence, education) | `basic.current_role`, `basic.years_of_experience`, `basic.location`, `basic.education` | Free text (the choices cannot be enumerated in advance) | First pass for the current role only; the rest is a detailed pass |
| 2 | `achievements` | Responsibilities at each job | `career_history[].responsibilities` | Free text | Detailed pass |
| 2 | `achievements` | A key project and its achievement (what changed, at what scale, and how) | `career_history[].achievements[].description` | Free text | Detailed pass |
| 2 | `achievements` | (When a concurrent project exists) which project this achievement belongs to | `career_history[].achievements[].project` | Free text | Detailed pass |
| 2 | `achievements` | (Same as above) that project's period | `career_history[].achievements[].period` | Free text (period) | Detailed pass |
| 2 | `achievements` | Whether that achievement can be expressed as a figure (year-on-year change, a count, a scale) | `career_history[].achievements[].metric` | Free text (a figure; null when it cannot be expressed) | Detailed pass |
| 3 | `skills` | Skills held, worked out in reverse from the career history (languages, frameworks, cloud platforms / business skills / languages / certifications) | `skills.technical`, `skills.business`, `skills.languages`, `skills.certifications` | Choice format (candidates built from what came up in `achievements`) + free text | Detailed pass |
| 3 | `skills` | Which of the 9 portable-skill elements the user has experience exercising | `skills.portable[].skill`, `skills.portable[].category` | Choice format | Detailed pass |

`career_history[].role` and `career_history[].responsibilities` are asked in free text because both are asked
about before anything is yet known of that job. Building a candidate in advance would mean presenting a job title
or a task name that elicitation itself imagined. `skills.technical` and the like may use the choice format because
a candidate can be built from what came up in `achievements`.

## Step 0: Confirming the mode and the sections

### Settled wording: mode

| Item | Wording |
|---|---|
| `header` | モード (Mode) |
| `question` | 今回は職歴のプロファイルをどのように扱いますか。 (How would you like to handle the career profile this time?) |
| Choice 1 | **初回作成**: まだ profile.json がありません。基本情報と職歴の骨格を伺います。 (First creation: profile.json does not exist yet. We will ask for your basic information and career skeleton.) |
| Choice 2 | **節の更新**: 既にある profile.json の一部だけを作る、または直します。次にどの節かを伺います。 (Section update: part of an existing profile.json will be built or corrected. Next, we will ask which section.) |
| Choice 3 | **全面点検**: 既にある profile.json を最初から見直します。 (Full review: an existing profile.json will be reviewed from the start.) |

Only when "section update" is chosen, go on to ask which sections are the target, in one question with
`multiSelect: true`. Attach the current stage `profile_sections.py` returned to the end of each choice's
description, in the form 「いまは {段階}」 (currently: {stage}) (write `missing` as 「まだ無い」, `skeleton` as
「骨格まで」, and `deep` as 「深掘り済み」).

| Item | Wording |
|---|---|
| `header` | 経歴 (Career) |
| `question` | どの節を更新しますか。 (Which section will you update?) |
| `multiSelect` | true |
| Choices | **基本情報**: 現職の役割・経験年数・居住地・学歴です。／ **職歴の骨格**: 在籍した企業・期間・役割と、空白期間です。／ **担当業務と実績**: 各職での担当業務・主要プロジェクト・実績の数値です。／ **スキル**: 技術・業務スキル・語学・資格・ポータブルスキルです。 (Basic information: current role, years of experience, place of residence, and education. / Career skeleton: the companies worked at, their periods, roles, and any employment gap. / Responsibilities and achievements: responsibilities, key projects, and achievement figures at each job. / Skills: technical and business skills, languages, certifications, and portable skills.) |

The choices correspond in order to `basic`, `career`, `achievements`, `skills`.

When a downstream sub-skill dispatches this skill naming a section it needs, this question is skipped, and the
named section becomes the target directly. A request about the job-change axis (reasons, conditions,
work-character preferences, scoring axes, targets, salary) goes to `job-change-axis`.

Introspective work (constructive rewording of a reason for leaving, grounding a strength) belongs to
`job-change-self-analysis`.

For the details of source notation (DOI, URL), see the sources sections in `elicitation-guide.md`,
`quantification-guide.md`, and `profile-methods.md`.
