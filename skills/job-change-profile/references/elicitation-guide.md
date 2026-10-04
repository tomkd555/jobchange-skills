# Elicitation methodology (grounding for recall cues and handling a statement)

<!-- textlint-disable jtf-style/4.3.2.大かっこ［］ -->
<!-- The [E1]-style notation in this text is the citation-id notation. This file disables the rule so the half-width square brackets are kept. -->

This is the canonical definition of job-change-profile's elicitation design. SKILL.md's principles,
question-bank.md's question design, and both agents (writer / auditor) reference this file. Evidence level is
written on a 4-step scale, A through D (A = primary/official, B = a reliable secondary source, C = word-of-mouth or
an aggregator site, D = a personal blog, hearsay, or unconfirmed). A piece of academic research also has a DOI.
The canonical definition is in `job-change-company-research/references/evidence-grading.md`, and a peer-reviewed
academic study falls under Level A. The notation format maps to the "Sources" section at the end.

## Elicit with structured recall cues

Recall of career history and achievements is fuller and more accurate when elicitation follows a frame with
its items and order fixed in advance than when it is left to free text. The evidence favoring this outweighs the
evidence against it (confidence: likely, 65%-80%).

- In meta-analyses of the validity of selection methods, a structured interview lands in the top tier [E17], and an
  interview's content and structure determine its validity [E18]. A structured interview's validity is about twice
  that of an unstructured one [E19].
- Autobiographical memory is a hierarchical network, and an event-history calendar (a cue that combines
  chronology with a cross-cutting theme) raises the completeness and accuracy of recall in line with this
  structure [E20]. A calendar-based method raises the completeness and consistency of retrospective data [E24].

Operation: elicitation proceeds along the chronological frame "company → tenure period → role → project →
achievement" (`sections/career.md`, `sections/achievements.md`). A turning point (a job change, a transfer, a
promotion) is used as a chronological cue. An individual achievement is asked about placed within its tenure
period.

**Evidence that lowers confidence (a limit)**: a structured technique (an event-history calendar) can increase
over-reporting for things such as household size or number of employers to a statistically significant degree
[E21]. Structure supplies a frame for recall; it does not by itself guarantee the answer is correct.

## Never corroborate a user's statement

The career history, achievement, and figure obtained through elicitation are recorded as fact, as stated.
Elicitation never asks for supporting documents, and never places a question shaped like "can that figure be
confirmed" or "can you prove it." A question that doubts what the other party states turns elicitation into an
interrogation, and it shortens the answers it draws out.

Operation: only a value the user themselves called uncertain gets `（本人が不確かとした）` (the user called it
uncertain) attached in the notes (see "The elicitation notes' recording format" below). Elicitation never presses
for confidence on its own. Elicitation never asks for a cross-check against evidence for a qualification's or a
language skill's name, a possessed skill, a role held, a tenure period, an annual salary, or an achievement figure.
Nor does it write, in the deliverable or a handover note, that this cross-check is "not yet done," as an unresolved
issue. The canonical definition of the scope of operations elicitation may perform, the types of question never
asked, handling each answer format, and how to record a career history with an atypical shape is in
`answer-handling.md`.

One exception: a value elicitation itself produces by calculation (such as a qualification's year obtained, back-calculated
from the graduation year) is marked explicitly as an estimate (SKILL.md Principle 6). This is a
distinction that keeps a value the user did not state from being mistaken for the user's own statement.

Fabrication is held in check at a different stage. The writer uses only facts in the elicitation notes, and the
auditor checks the deliverable against those notes. Elicitation itself has no need to turn the user into a
verifier.

## Handling concurrent employment

Holding more than one job during the same period (a concurrent role, secondment, side work, self-employment) is
an ordinary occurrence. An overlap in tenure periods is never treated as an inconsistency.

Operation: once the career skeleton is laid out, confirm with one question whether the user held more than one job
during the same period. Each job that did exist becomes its own `career_history` entry, and the overlap in
`period` is kept as it stands. Which standing applied is written into `role` (such as 「業務委託（副業）」 (contract
work, side job)). When more than one project was handled concurrently within one job, attach `project` (the project's name) and
`period` (that project's period) to each achievement, so which project's outcome and when it occurred can be told
apart. A job with only one project leaves both fields out.

## Handling an employment gap

Once the career skeleton is settled, mechanically detect a period (6 months or more) covered by no career-history
entry's tenure period, and ask for an explanation and the activity during it (confidence: likely, 65%-80%).

- A gap of 3 months or less draws little scrutiny, while one of 6 months or more requires an explanation and a
  sense of planning [E100].
- An employment gap still works against a hiring decision and against pay on its own. The strong claim that "a gap
  is harmless" does not hold [E99].

Operation: judge a gap against the union of every career-history entry's tenure period. Looking only at adjacent
entries would detect a gap that does not exist whenever a side job overlaps the main job, and would ask the user
to explain a period that is not in fact a gap. A gap is never hidden. Record its period, an explanation, and the
activity during it (study, obtaining a qualification, caregiving, medical treatment, and the like) in
`career_gaps`, so it can be explained. This field exists to keep accuracy and completeness without resorting
to falsification. It is never a place to fabricate an account that makes the gap look favorable.

**Evidence that lowers confidence (a limit)**: for the HBR study on employment gaps, an effect-size figure could
not be obtained from the article's own text. How large an employment gap's effect on a selection outcome is stays
unsettled for this skill (an evidence gap).

## Importing an existing document and lightening the first pass

There are two ways to shorten elicitation: asking about fewer items, and importing from a document already on
hand. A conversational format does not by itself make data entry faster (confidence: likely, 65%-80%).

- A chatbot-format survey takes longer than a web-form format (26 minutes 44 seconds versus 17 minutes 30 seconds).
  It also increases variance in answers and reduces satisficing (a low-effort answer) [E105]. A conversational
  format is used for the quality of the answer and for letting the user resume after an interruption.
- An application form's completion rate depends strongly on time taken. It is 12.47% under 5 minutes and 3.61% at
  15 minutes or more [E106]. The number of items asked on the first pass has a direct effect on the completion rate.
- Automated extraction from a résumé reaches an F1 of 0.963 for a tenure period, 0.932 for a company name or job
  title, and 0.838 for a long-form job description [E107]. The skeleton (company name, tenure period, job title)
  can be imported from a document and just confirmed; only the long-form description needs a human eye.
- A sensitive item is pushed to a later stage. Among the principles for reducing a form's cognitive load is
  starting with non-sensitive information and pushing an item such as career history or desired salary to a later
  stage [E108].

Operation: the first pass builds profile.json to validity with the career skeleton and current role alone, and
`job-change-axis` builds axis.json to validity with reasons for changing jobs, key conditions, and the 8
work-character preferences alone. Quantifying achievements and taking stock of skills here are deferred until just
before the process that needs them. In `job-change-axis`, building the company scoring axes, covering conditions
and putting them in priority order, and the actual figure for current salary are deferred the same way (the section
catalogues and the first-pass scopes are in `sections.md` of each skill). Elicitation first asks with one question only whether a document exists,
without requiring its submission. When one exists, it is read and the skeleton is transcribed into the elicitation
notes. The extracted result is presented as a list, and the user is asked only "where it is different" about
it. How to read a `.docx` is in `sections/career.md`. Consent to every item is never sought, to avoid a question shaped so
that consent becomes the default answer. A long-form description is marked `（要確認）` (needs confirmation). A
fact read from a document counts the same as the user's own statement, and is never treated as documentary proof (the previous section, "Never corroborate a user's
statement").

**Evidence that lowers confidence (a limit)**: both the application form's completion rate and the résumé
extraction's F1 come from a different population and task than this skill's elicitation. Neither the relationship
between time taken and completion rate, nor the extraction accuracy from a document, has been measured for this
elicitation.

## Operating elicitation centered on the choice format

- Elicitation is run centered on AskUserQuestion's choice format. At most 4 questions per AskUserQuestion call,
  with up to 4 choices per question. Free text is asked only for an item that cannot be put into choices, such as a
  company name, a tenure period, or an achievement figure.
- For a question whose choices can be enumerated in advance (the 8 work-character traits, the 9 elements of
  portable skills, a condition's axis, a company scoring axis's quantitative candidates, and the like), the wording
  is settled per section in `sections/{id}.md`. The phrasing is never composed anew each time elicitation runs.
  For an item asked about before anything is yet known of that job (a role, responsibilities), elicitation does
  not present a candidate, because such a candidate would be one elicitation itself imagined.
- A question addressed to the user, and its choice labels, are written in polite Japanese (敬体); the running text
  (this skill's internal procedure, this document) is written in plain Japanese (常体). Confirmation is asked as
  「どこが違いますか」 (where does this differ), which avoids a question shaped so that agreement becomes the default
  answer.
- A detailed pass never leads the user into ruminating on feelings; the question is aimed at fact (when, in what
  situation, what was done). A detailed pass on introspection (constructive rewording of a reason for leaving,
  grounding a strength) belongs to `job-change-self-analysis`; direct the user there.
- The main session appends the elicitation's results to `career-private/profile_interview_notes.md` as elicitation
  proceeds. This supports resuming after an interruption. The writer uses only the facts in these notes.

## The elicitation notes' recording format

`profile_interview_notes.md` grows only by appending. The writer looks to these notes alone for the support behind
each statement in profile.json, and the auditor checks the deliverable against these notes. The notes are
written so that a fact elicited and when it was elicited can be told apart.

- Raise a `## YYYY-MM-DD` heading for each round of elicitation, and append what was elicited that round beneath
  it. The content under a past heading is never rewritten. When a past round's content turns out to have been
  wrong, add a line starting with `訂正:` (correction) under the latest heading, stating which statement is being
  revised to what.
- Write one item as one bullet line, in the form `- {item}: {the user's answer}`. For `{item}`, use the question
  item's name in the `references/question-bank.md` of the skill eliciting it, or the field name in profile.json or
  axis.json.
- Transcribe a company name, a tenure period, a job title, and an achievement figure in the user's own words. Never
  drop the unit or the point in time (when the figure applies).
- An item the user did not answer is written as `- {item}: 未回答` (unanswered), and the line is never dropped.
  Attach `（本人が不確かとした）` (the user called it uncertain) to a value the user called uncertain. Write
  `未回答（本人の意向）` (unanswered, at the user's own wish) for an item the user said they would rather not
  answer, and `本人が不明とした` (the user called it unknown) for an item the user said they do not remember.
- For an item reworded into document-ready phrasing, keep the original line and add a
  `言い換え（本人了承）:` (reworded, user-approved) line directly beneath it. A rewording without approval is never
  written. The list of line formats and the canonical definition of the permissible scope of a rewording are in
  `answer-handling.md`.
- Mark a statement imported from an existing document that the user has not yet confirmed with `（要確認）` (needs
  confirmation), and remove the mark once confirmed. Being document-sourced never changes how an item is handled;
  imported content counts the same as the user's own statement, and a confirmed statement is handled the
  same as any other answer.
- Elicitation's own interpretation, summary, or guess is never written. The writer uses only the facts in the
  notes to write profile.json, so an interpretation or a guess added to the notes becomes fabrication as it stands.

## Update practice

profile.json is kept current (confidence: likely, 65%-80%).

- Leaving information to go stale, and a lack of completeness, are typical failures; when writing an
  application document, give priority to the most recent 7-10 years and cut work no longer relevant [E103]. A
  quarterly update, and keeping career-history data as a running document, are recommended in common by
  English-language and Japanese-language sources alike [E104].

Operation: append whenever a new achievement comes in, at least once a quarter. Keep profile.json itself
complete (narrowing to the most recent 7-10 years is done by the application-documents sub-skill at the stage
of writing an application document), and rewrite `updated_at` with every update.

## Sources

<!-- textlint-disable -->
<!-- This section lists sources in a bibliographic format (publisher. Title. Year. Level. URL). This section alone disables the rule so the separating periods and part of a company name are not judged as Japanese punctuation or a synonym. -->

- [E17] Psychological Bulletin (APA). The validity and utility of selection methods in personnel psychology. 1998. Level A. DOI:10.1037/0033-2909.124.2.262. https://doi.org/10.1037/0033-2909.124.2.262
- [E18] Journal of Applied Psychology (APA). The validity of employment interviews: A comprehensive review and meta-analysis. 1994. Level A. DOI:10.1037/0021-9010.79.4.599. https://doi.org/10.1037/0021-9010.79.4.599
- [E19] Journal of Occupational Psychology. A meta-analytic investigation of the impact of interview format and degree of structure. 1988. Level A. DOI:10.1111/j.2044-8325.1988.tb00467.x. https://doi.org/10.1111/j.2044-8325.1988.tb00467.x
- [E20] Memory. The structure of autobiographical memory and the event history calendar. 1998-07. Level A. DOI:10.1080/741942610. https://doi.org/10.1080/741942610
- [E21] Public Opinion Quarterly. Event history calendars and question list surveys: a direct comparison of interviewing methods. 2001. Level A. DOI:10.1086/320037. https://doi.org/10.1086/320037
- [E24] Quality & Quantity. Applications of calendar instruments in social surveys: a review. 2009. Level A. DOI:10.1007/s11135-007-9129-8. https://doi.org/10.1007/s11135-007-9129-8
- [E99] Harvard Business Review (Groysberg, Lin). Research: Resume Gaps Still Matter. 2024-07-31. Level B. https://hbr.org/2024/07/research-resume-gaps-still-matter
- [E100] JAC Recruitment. 面接での経歴の空白期間の好印象な答え方は？. 2024-06-12. Level C. https://www.jac-recruitment.jp/market/knowhow/interview/interview-blank-period/
- [E103] Forbes JAPAN. 2026年の採用市場で差がつく「職務経歴書」5つの更新ポイント. 2026-03-15. Level C. https://forbesjapan.com/articles/detail/93818
- [E104] Indeed / ResumeGenius 他. Guide To Updating Your Resume. 2024. Level C. https://www.indeed.com/career-advice/resumes-cover-letters/guide-to-updating-your-resume
- [E105] ACM CHI (Kim, Lee, Gweon). Comparing Data from Chatbot and Web Surveys: Effects of Platform and Conversational Style on Survey Response Quality. 2019-05. Level A. DOI:10.1145/3290605.3300316. https://doi.org/10.1145/3290605.3300316
- [E106] Appcast. Recruitment Marketing Benchmark Report. 2025. Level B. https://info.appcast.io/whitepaper/2025-recruitment-marketing-benchmark-report
- [E107] arXiv (Zhu ほか). Layout-Aware Parsing Meets Efficient LLMs: A Unified, Scalable Framework for Resume Information Extraction and Evaluation. 2025-10. Level B. arXiv:2510.09722. https://arxiv.org/abs/2510.09722
- [E108] Nielsen Norman Group. Four Principles to Reduce Cognitive Load in Forms. Level B. https://www.nngroup.com/articles/4-principles-reduce-cognitive-load/

<!-- textlint-enable -->
