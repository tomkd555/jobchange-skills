# Structured question set (question-bank)

This is the canonical definition of the common rules for the pre-set structured questions job-change-profile's
elicitation uses, and the correspondence table between questions and sections/fields. Each section's procedure, its
opening question, and the settled wording passed to AskUserQuestion live in each section's own `sections/{id}.md`
(the catalogue is `sections.md`). Only Step 0's wording (choosing the mode and the sections) belongs to no section,
so it is placed in this document. The grounding for recall cues and the choice-format operation lives in
`elicitation-guide.md`, and the canonical definition of the field specification lives in the hub's
`references/profile-format.md`.

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
  `elicitation-guide.md`; the list of question types never placed lives in `answer-handling.md`).
- The choice format is the shape of the question, and it never constrains how the user answers. When an answer
  comes back in free text or covering several items at once, what comes in is sorted into its items, and only the
  items still unanswered are asked next (see "Handling each answer format" in `answer-handling.md`).
- Colloquial or vague phrasing is put into document-ready wording only after a reworded candidate is shown to the
  user and the user approves it. The wording for presenting a candidate lives in `answer-handling.md`.

## Rules for use

- A question is run centered on AskUserQuestion's choice format. At most 4 questions per AskUserQuestion call, with
  up to 4 choices per question. When one question should take several answers, use `multiSelect: true` and keep it
  as one question.
- For a question whose choices can be enumerated in advance, use the section file's settled wording as it stands,
  never composing the phrasing on the spot. An item that cannot be enumerated (a company name, a tenure period,
  responsibilities, a project name, an achievement, a figure) is asked in free text. **No candidate is presented
  for an item whose candidates are unknown.**
- "Choice format + free text" in the correspondence table denotes receiving an answer outside the choices through
  AskUserQuestion's Other. A format that has the user pick a choice and then requires a separate free-text addition
  is never used.
- A deep dive never drives the user into ruminating on feelings; the question is aimed at fact (when, in what
  situation, what was done). Constructive rewording of a reason for leaving, and grounding a strength, fall outside
  this skill's scope and are directed to `job-change-self-analysis`.
- The main session appends the elicitation's results to `career-private/profile_interview_notes.md` as elicitation
  proceeds.
- Eliciting one section reads only this document's common rules and that section's own `sections/{id}.md`. Another
  section's file is never read ahead of time.

## Correspondence table between questions and sections/fields

The "First pass" column marks a question asked within the first-pass scope (`sections.md`'s "Scope of the first
pass") as `初回` (first pass), and a question skipped there and asked later, at a section update just before the
downstream process needs it, as `深掘り` (deep dive).

| Step | Section | Question | Field it fills | Format | First pass |
|---|---|---|---|---|---|
| 1 | `career` | Whether a shokumu-keirekisho (career history document), rirekisho (résumé form), or résumé file is on hand | (transcribe what could be read into the elicitation notes) | Choice format | First pass |
| 1 | `career` | Where the company name, tenure period, job title, and responsibilities extracted from the document differ | Correction of each field in `career_history[]` | Free text (only for an item that differed) | First pass |
| 1 | `career` | Listing the companies worked at and their tenure periods, from oldest (or most recent) | `career_history[].company`, `career_history[].period` | Free text (company name, period) | First pass |
| 1 | `career` | The role and job title at each company | `career_history[].role` | Free text | First pass |
| 1 | `career` | Whether a period existed with 2 or more concurrent jobs, and its breakdown | Concurrent `career_history[]` elements | Choice format + free text | First pass |
| 1 | `career` | The employment type at each company, and whether a place of work exists apart from the employer (a client site, a place of dispatch, a place of secondment) | `career_history[].employment_type`, `career_history[].assignment`, `career_history[].note` | Free text (only where applicable; the canonical definition of how to record it is in "A career history with an atypical shape" in `answer-handling.md`) | First pass |
| 1 | `career` | The reason for a detected employment gap (6 months or more) and the activity during it | `career_gaps[].period`, `career_gaps[].explanation`, `career_gaps[].activities` | Choice format (activity type) + free text | First pass |
| 1 | `basic` | Basic information (current role, years of experience, place of residence, education) | `basic.current_role`, `basic.years_of_experience`, `basic.location`, `basic.education` | Free text (the choices cannot be enumerated in advance) | First pass for the current role only; the rest is a deep dive |
| 2 | `achievements` | Responsibilities at each job | `career_history[].responsibilities` | Free text | Deep dive |
| 2 | `achievements` | A key project and its achievement (what changed, at what scale, and how) | `career_history[].achievements[].description` | Free text | Deep dive |
| 2 | `achievements` | (When a concurrent project exists) which project this achievement belongs to | `career_history[].achievements[].project` | Free text | Deep dive |
| 2 | `achievements` | (Same as above) that project's period | `career_history[].achievements[].period` | Free text (period) | Deep dive |
| 2 | `achievements` | Whether that achievement can be expressed as a figure (year-on-year change, a count, a scale) | `career_history[].achievements[].metric` | Free text (a figure; null when it cannot be expressed) | Deep dive |
| 3 | `skills` | Skills held, worked out in reverse from the career history (languages, frameworks, cloud platforms / business skills / languages / certifications) | `skills.technical`, `skills.business`, `skills.languages`, `skills.certifications` | Choice format (candidates built from what came up in `achievements`) + free text | Deep dive |
| 3 | `skills` | Which of the 9 portable-skill elements the user has experience exercising | `skills.portable[].skill`, `skills.portable[].category` | Choice format | Deep dive |
| 4 | `reasons` | What the user wants to achieve next by changing jobs (reasons for changing jobs) | `job_change_axis.reasons` | Free text (the choices cannot be enumerated in advance) | First pass |
| 4 | `conditions` | A condition that cannot be given up, a condition that is desirable, and its axis, threshold, and means of verification | `job_change_axis.conditions[]` | Choice format + free text | First pass for key conditions only; full coverage is a deep dive |
| 4 | `conditions` | The priority and reassessment time of a must-have condition | `job_change_axis.conditions[].priority`, `job_change_axis.priority_note` | Choice format + free text | Deep dive |
| 4 | `work_character` | The desired level for each of the 8 work-character traits | `job_change_axis.work_character_preferences[]` | Choice format | First pass |
| 4 | `score_axes` | Which of the 9 quantitative candidate axes for scoring a company matter, and which non-numeric matter carries weight (a qualitative axis's name, definition, and judgment conditions) | `company_score_axes[].axis`, `company_score_axes[].kind`, `company_score_axes[].label`, `company_score_axes[].definition`, `company_score_axes[].judgment[]` | Choice format + free text | Deep dive |
| 4 | `score_axes` | The weight assigned to each chosen axis (summing to 100), and the criteria used for a quantitative axis (asked together in one AskUserQuestion call) | `company_score_axes[].weight`, `company_score_axes[].thresholds` | Choice format (an allocation candidate, a choice of criteria) + free text (figures) + choice format (a check against 2 companies) | Deep dive |
| 4 | `targets` | The desired industry, occupation, and company | `targets.industries`, `targets.roles`, `targets.companies` | Free text (the choices cannot be enumerated in advance) | Deep dive |
| 4 | `salary` | Current and desired annual salary | `salary.current`, `salary.desired` | Free text (a figure) | Deep dive |

`career_history[].role` and `career_history[].responsibilities` are asked in free text because both are asked
about before anything is yet known of that job. Building a candidate in advance would mean presenting a job title
or a task name that elicitation itself imagined. `skills.technical` and the like may use the choice format because
a candidate can be built from what came up in `achievements`.

## Step 0: Confirming the mode and the sections

### Settled wording — mode

| Item | Wording |
|---|---|
| `header` | モード (Mode) |
| `question` | 今回はプロファイルをどのように扱いますか。 (How would you like to handle the profile this time?) |
| Choice 1 | **初回作成** — まだ profile.json がありません。職歴の骨格から転職の軸まで、まず骨格を伺います。 (First creation — profile.json does not exist yet. We will go through everything from the career skeleton to the job-change axes, starting with the skeleton.) |
| Choice 2 | **節の更新** — 既にある profile.json の一部だけを作る、または直します。次にどの節かを伺います。 (Section update — Part of an existing profile.json will be built or corrected. Next, we will ask which section.) |
| Choice 3 | **全面点検** — 既にある profile.json を最初から見直します。 (Full review — An existing profile.json will be reviewed from the start.) |

Only when "section update" is chosen, go on to ask which sections are the target. The 10 sections are split
across 3 questions, asked in one AskUserQuestion call. Attach the current stage `profile_sections.py` returned to
the end of each choice's description, in the form 「いまは {段階}」 (currently: {stage}) (write `missing` as 「まだ無い」,
`skeleton` as 「骨格まで」, and `deep` as 「深掘り済み」).

| Item | Wording |
|---|---|
| Question 1 `header` | 経歴 (Career) |
| Question 1 `question` | どの節を更新しますか。経歴に関する節から選んでください。 (Which section will you update? Choose from the sections about career history.) |
| `multiSelect` | true |
| Choices | **基本情報** — 現職の役割・経験年数・居住地・学歴です。／ **職歴の骨格** — 在籍した企業・期間・役割と、空白期間です。／ **担当業務と実績** — 各職での担当業務・主要プロジェクト・実績の数値です。／ **スキル** — 技術・業務スキル・語学・資格・ポータブルスキルです。 (Basic information — current role, years of experience, place of residence, and education. / Career skeleton — the companies worked at, their periods, roles, and any employment gap. / Responsibilities and achievements — responsibilities, key projects, and achievement figures at each job. / Skills — technical and business skills, languages, certifications, and portable skills.) |
| Question 2 `header` | 転職の軸 (Job-change axes) |
| Question 2 `question` | 同じく、転職の軸に関する節から選んでください。 (Likewise, choose from the sections about your job-change axes.) |
| `multiSelect` | true |
| Choices | **転職理由** — 転職で次に実現したいことです。／ **条件** — 譲れない条件・望ましい条件と、その優先順位です。／ **作業特性** — 8つの作業特性それぞれの希望度です。／ **企業スコアの採点軸** — 企業を採点する軸と重みです。 (Reasons for changing jobs — what you want to achieve next by changing jobs. / Conditions — a condition you cannot give up, one that is desirable, and their priority. / Work-character preferences — the desired level for each of the 8 work-character traits. / Company scoring axes — the axes and weights for scoring a company.) |
| Question 3 `header` | 志望と年収 (Targets and salary) |
| Question 3 `question` | 同じく、志望と年収に関する節から選んでください。 (Likewise, choose from the sections about targets and salary.) |
| `multiSelect` | true |
| Choices | **志望対象** — 志望する業界・職種・企業です。／ **年収** — 現年収と希望年収です。 (Target companies and roles — the desired industry, occupation, and company. / Annual salary — current and desired annual salary.) |

Question 1's choices correspond in order to `basic`, `career`, `achievements`, `skills`; Question 2's to `reasons`,
`conditions`, `work_character`, `score_axes`; Question 3's to `targets`, `salary`.

When a downstream sub-skill dispatches this skill naming a section it needs, this question is never placed, and
the named section becomes the target directly.

A deep dive into introspection — constructive rewording of an axis, grounding a value in reasons — falls outside
this skill's scope and is directed to `job-change-self-analysis`. The grounding for keeping must-have conditions to
a small number and treating them as open to reassessment lives in the must/want section of `profile-methods.md`.

For the details of source notation (DOI, URL), see the sources sections in `elicitation-guide.md`,
`quantification-guide.md`, and `profile-methods.md`.
