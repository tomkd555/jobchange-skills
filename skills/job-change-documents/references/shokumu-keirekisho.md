# Shokumu-keirekisho writing standard

This is the canonical definition for writing a shokumu-keirekisho (career history document) in
mid-career hiring in Japan. The writer (`job-change-document-writer`) uses it for selecting the
format and writing the summary section and the achievements. The auditor
(`job-change-document-auditor`) uses it for checking length, correspondence with the requirements,
and quantification.

厚生労働省 (the Ministry of Health, Labour and Welfare) and ハローワーク (Hello Work) position the
shokumu-keirekisho as a document 「履歴書では書ききれない具体的なキャリアとやる気をアピールするためのもの」 (for
presenting the concrete career and motivation a rirekisho cannot fully convey). They distribute format
examples free of charge (source: 厚生労働省
ハローワークインターネットサービス "履歴書・職務経歴書の書き方"
https://www.hellowork.mhlw.go.jp/member/career_doc01.html, primary/official). Where the rirekisho
fills in fixed fields, the shokumu-keirekisho shows experience and achievement in free-form prose.

## The three formats and when to use each

The shokumu-keirekisho has three basic formats. Choose among them by the relationship between the
target occupation and the career history, and by which point deserves emphasis (source: マイナビ転職エージェント
"『編年体式』『逆編年体式』の職務経歴書の書き方やポイントを紹介！" https://mynavi-agent.jp/knowledge/prepare/683.html,
reliable secondary).

| Format | Ordering | Where it fits |
|---|---|---|
| Chronological (編年体式) | From the start of working life to the present, in time order (oldest first) | A consistent career in the same industry and occupation, when the applicant wants to show a process of growth |
| Reverse-chronological (逆編年体式) | From the present back to the past, in reverse time order (newest first) | The current role's content is close to the target job, or the applicant wants to emphasize the most recent experience |
| Career style (キャリア式) | Grouped by field of work | Frequent job changes, or a technical role where the applicant wants to emphasize skill by field |

- In the **chronological** format, the applicant writes their work experience in time order from the
  start of their working life to the present. It conveys continuity and growth in their work.
- In the **reverse-chronological** format, the applicant writes from the present back toward the past.
  Because the most recent role comes first, a hiring manager reads the experience closest to the
  target job first. It fits a case where the current role and the target job resemble each other, or
  where the applicant wants to foreground their most recent achievement.
- In the **career style**, the career history is organized by the field of work the applicant handled.
  Because "what I have done" and "my
  strong field" come across by field, it fits a case with frequent job changes, where a
  chronological account would look fragmented, or a technical role where the applicant wants to show
  depth of skill.

The writer chooses a format from the relationship between the career history and the target job, and
states the reason for the choice. When the choice is not clear-cut, prefer the
reverse-chronological format when recent experience matters most, and the career style when
field-specific skill deserves emphasis.

## The summary section (職務要約)

Open with a short summary of the career history and strengths so far. A hiring manager reads this
part first, and it becomes the material for deciding whether to keep reading.

- Show years of experience, the main area of work, and an achievement relevant to the target job in a
  few lines.
- State the connection to the target occupation first. Do not write at length about career history
  unrelated to the target job.
- An achievement written in the summary section also follows the quantification principle below and
  the principle of staying within `profile.json`'s achievements.

## Quantifying achievements

Show an achievement with a number, a percentage, or an amount wherever possible. A quantified
achievement creates the difference from other applicants.

- Write in the form "Action (what was done) + object + Result," and quantify the result as
  「◯%改善」「◯%増加」「年◯万円」 (◯% improvement, ◯% increase, ◯ ten-thousand yen per year) (source: Yale
  Office of Career Strategy "Writing
  Impactful Resume Bullets" https://ocs.yale.edu/resources/writing-impactful-resume-bullets/, reliable
  secondary).
- Write the applicant's own contribution (same source).
- Match a quantified value exactly to `profile.json`'s `achievements[].metric`. Do not write a number
  absent from `metric`. Do not round or inflate it.
- For an item whose `metric` is `null` (an achievement that cannot be quantified), do not invent a
  number; show the scope of responsibility, the role, and the effort with a concrete fact instead.

## Length

The canonical definition of the numeric guide for length and for the summary section's length is in
`references/templates.md`. It sets one to two A4 pages for roughly seven years of work experience or
less, two to three pages beyond that, and 200 to 300 characters for the summary. The points below give
its background.

- The page count splits across sources between one to two pages and two to three pages (the full list
  is in `templates.md`). Treat this as a guide for measuring conciseness and relevance. The English
  resume's "one to two A4 or letter pages" is a separate
  standard grounded in `references/english-resume.md`'s length criterion (with its own source), and
  does not extend to the Japanese-language shokumu-keirekisho.
- Even with a long career history, select the achievements relevant to the target job and avoid a
  redundant listing. The auditor flags a case where the length greatly exceeds the guide and an
  excessive listing of achievements unrelated to the target job appears together.

## What a hiring manager looks for

A hiring manager reads a shokumu-keirekisho for the following points. Write a structure that answers
them.

| Point | Content |
|---|---|
| Fit with the target occupation | Whether an experience or an achievement corresponds to the posting requirements. The appeal mapping (`references/tailoring.md`) maps the requirements against the achievements. |
| Reproducibility of the achievement | Whether a past result can be reproduced at the target company. Show the action and the effort that led to the result. |
| Stability | For frequent job changes, whether a consistent axis in the career comes through. Show that axis through the format (the career style) and the summary section. |
| Concreteness | Whether the document is written with fact and number. |

## The scope and limits of this standard

- The distinction among the three formats rests on a major recruiting agency's practical guide
  (reliable secondary). A hiring manager's evaluation varies by company and occupation, and the
  right choice differs from case to case.
- The character-count guide for the summary section differs by practical media outlet (some count
  characters, others lines). This document states the principle "the connection to the target job
  first, an achievement in quantified form," and places the numeric guide (200 to 300 characters) in
  `templates.md`.
