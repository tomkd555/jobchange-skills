# How to receive an answer (handling a statement, making it concrete, quantification, rewording)

This is the canonical definition of how job-change-profile's elicitation receives a user's answer, and how far it
may go in shaping it. SKILL.md's Principles 2 and 3, question-bank.md's question design, and both agents (writer
and auditor) reference this file. The grounding for recall cues and the elicitation notes' recording format lives
in `elicitation-guide.md`, and the patterns for quantification live in `quantification-guide.md`; neither is
duplicated here.

## A statement is a fact

The career history, role, achievement, figure, and period a user states are recorded as fact, as stated.
Elicitation never places a question that doubts them. Elicitation may perform only the three operations described
below — making a statement concrete, supporting quantification, and rewording into language the job market
accepts.

The following types of question are never placed, whatever their content.

| Question never placed | Reason |
|---|---|
| "Is that really the case?" "Isn't it actually...?" | It questions the truth of the statement |
| "Can you confirm that?" "Can you prove it?" "Do you have grounds for that?" | It demands documentary proof |
| "Where did that figure come from?" "Is that an internal company figure?" | It questions the figure's source |
| "It should be..." "Generally speaking..." | It overwrites the statement with elicitation's own knowledge |
| 「珍しいですね」「本当ですか、すごいですね」 (That's unusual. / Really? That's impressive.) | Voicing surprise reads as doubt |

A figure's source is never asked. Only when the user has said on their own "roughly," "approximately," or "I'm not
sure," is that noted in the elicitation notes as `（本人が不確かとした）` (the recording format's canonical
definition is in `elicitation-guide.md`). Elicitation never presses for confidence on its own.

When statements appear to conflict (an overlap in tenure periods, a job title out of order, a different figure for
the same achievement), this is never treated as an error to point out. The two conflicting points are laid out as
they stand, and the user decides which is correct. Only the two points are presented, with no guess of elicitation's
own added. An overlap in tenure periods can be concurrent employment (`elicitation-guide.md`), so it is not even
treated as a conflict.

## The three operations elicitation may perform

### Making a statement concrete

Of the elements "what, when, where, at what scale, and how something changed," ask about one missing element at a
time. Never place an open-ended question such as "could you tell me more" — name the missing element explicitly
when asking. Leave an element with no answer empty; elicitation never fills it in.

| Missing element | Example question (polite form) |
|---|---|
| Object | 「その改善は、どのシステム（または業務）に対するものでしたか」 (Which system (or task) was that improvement for?) |
| Time | 「それはいつごろのことでしたか。年と、分かれば月をお願いします」 (Roughly when was that? A year, and a month if you recall it, please.) |
| Scale | 「関わった人数、扱った件数、金額のうち、覚えているものはありますか」 (Do you recall the number of people involved, the number of cases handled, or the amount of money?) |
| Role | 「その中でご自身が受け持ったのは、どの部分でしたか」 (Which part of it did you personally handle?) |
| Change | 「それを行う前と後で、何がどう変わりましたか」 (What changed, and how, before and after you did this?) |
| Method | 「そのとき、具体的にはどのような手を打ちましたか」 (Specifically, what steps did you take at that time?) |
| Period/budget | 「その取り組みはどれくらいの期間でしたか。予算の規模は分かりますか」 (About how long did that effort take? Do you know the scale of the budget?) |
| The user's own share | 「そのプロジェクトのうち、ご自身が受け持った部分はどこでしたか」 (Of that project, which part did you personally handle?) |

When an answer is phrased with a subject other than the user themselves — "we," "the team," "it was done" — ask
once about the user's own share. This question separates the scope of the user's involvement. When the answer is "I
did the whole thing myself," record it as stated.

Making a statement concrete only breaks down what the user said into a granularity the downstream processes
(application documents, job interview preparation) can use.

### Supporting quantification

Present the patterns in `quantification-guide.md` as choices and let the user pick whichever pattern fits.
Elicitation never proposes a figure itself. A leading question such as "would that be around 20%?" or "about 10
cases?" replaces the user's own statement with elicitation's own guess.

| How the user answers | Recording |
|---|---|
| A single figure ("cut it by 40%") | Write it to `metric` as it stands. Add the unit and the point in time |
| A range ("10-15 cases," "2 or 3 times a month") | Record the range as it stands. Never round it to a median |
| An approximation ("roughly half," "felt like about 30%") | Record the user's own words as stated, with `（本人が概算とした）` (the user called it an approximation) attached |
| No record, but an activity volume is remembered ("I was making about 30 calls a day") | Record the value the user approximates from the activity volume, with a note that it is an approximation. Leave the multiplication to the user; elicitation never computes it and presents the result |
| No figure available | Set `metric` to `null`, and make the point that was worked on and the point that was evaluated concrete in `description` |
| A comparison in place of a figure ("it used to mean working through the night, but now it finishes on time") | Record the comparison as stated. Never convert it into a number of hours |

When no figure is available, keep the question to the wording below, and never ask as if a number were assumed.

| Item | Wording |
|---|---|
| Quantification question | その成果は数字で表せそうですか。難しければ、前後の変化や、覚えている活動量（1日の件数など）からの概算でも構いません。 (Can that result be expressed as a number? If that is difficult, an approximation from the change before and after, or from an activity volume you recall, such as a daily count, is fine too.) |
| Annual salary question | 年収は、直近1年の額面（賞与を含み、残業代を含む）でお答えください。別の数え方であれば、その旨を添えてください。 (For annual salary, please answer with the gross figure for the most recent year, including bonus and overtime pay. If you count it a different way, please note that as well.) |

Annual salary changes in value depending on whether it is gross or net, whether it includes bonus or overtime pay,
and whether it is a projection or an actual figure. Ask with the definition fixed on the question's side to one
meaning, and when the user answers by a different reckoning, add that reckoning to the notes. Elicitation never
converts it itself.

A value elicitation places by calculation (a qualification's year obtained, back-calculated from the graduation
year, for example) is marked as distinct from the user's own statement, as an estimate (`elicitation-guide.md`).

### Rewording into language the job market accepts

Colloquial or vague phrasing is reworded into language that reads well in an application document and a job
interview. A reworded candidate is always shown to the user, and only a sentence the user approves is kept in the
notes with a `言い換え（本人了承）:` (reworded, user-approved) line. The original line is never deleted. When the
user wants to keep the original wording, the original wording stands.

What to keep in mind when rewording:

- Never raise a role's phrasing above the scope of involvement the user stated. The correspondence between the
  scope of involvement and the phrasing follows "The scale of role phrasing" below.
- Never add a figure, a scale, a scope, or an acting subject in the course of rewording. Never turn "was in charge
  of" into "led the company-wide 〜."
- An evaluative word (worked hard, put in effort, it was tough) is never placed in the document. Write the fact of
  what was done instead.
- A negative fact (a dismissal, a demotion, a failure) is never hidden. It is put into document-ready phrasing
  within the range the user stated. A reason the user did not state is never filled in.

The wording for presenting a reworded candidate is as follows.

| Item | Wording |
|---|---|
| Preamble | 書類で通る言い方に直すと、次のようになります。**違うところ**があれば元の言い方のままにします。 (Put into language that reads well in a document, this becomes as follows. If anything is different, it stays as originally phrased.) |
| Confirmation | 「{原文}」→「{言い換え}」。この言い方で合っていますか。関与の範囲が実際より広く見えるなら、そのままお知らせください。 ("{original}" → "{reworded}". Does this phrasing match? If the scope of involvement looks wider than it actually was, please say so.) |

## The scale of role phrasing

The word for a role is decided by the scope of involvement in the user's own statement. Elicitation never adds
involvement the statement lacks through phrasing.

| Involvement in the user's statement | Phrasing that may be used | Phrasing not used without a corresponding statement |
|---|---|---|
| Took on part of the work under instruction | 担当、参画、従事 (in charge of, participated in, engaged in) | 主導、推進、リード、統括 (led, drove, headed, oversaw) |
| Took on one area at their own discretion | 主担当、〜を一貫して担当、専任 (principal owner, consistently in charge of 〜, sole owner) | 統括、責任者 (oversaw, responsible for) |
| Assigned work to several people and managed progress | リード、進行管理、取りまとめ (led, managed progress of, coordinated) | 責任者（決裁権の申告が無い場合）(responsible for, with no statement of decision-making authority) |
| Was the starting point from planning through execution | 企画、立ち上げ、推進 (planned, launched, drove) | 統括（他の担当者の管理を申告していない場合）(oversaw, when not stating management of other staff) |
| Held decision-making, personnel, or budget authority | 責任者、統括、マネジメント (responsible for, oversaw, managed) | — |

The same word carries a different weight depending on the company or occupation (for example, 「リード」 (lead)
points to the center of hands-on work at a small team, and to a title at a large company). Which rung a user's own word falls on
is decided by asking about the scope of involvement, never by the sound of the word.

## Verb and noun replacement table

Rewording changes only the phrasing, never adding a fact. The "Caution" column lists what to confirm with the user
before making the replacement.

| The user's own wording | Document-ready phrasing | Caution |
|---|---|---|
| helped out (手伝った) | 〜の一部を担当した、サポートした (took on part of 〜, supported) | first make concrete what was helped with |
| did it (やった, やりました) | 担当した、実施した、実行した (was in charge of, carried out, executed) | |
| made (作った) | 開発した、構築した、作成した、設計した (developed, built, created, designed) | confirm whether design was included |
| fixed (直した) | 改修した、修正した、改善した (improved, corrected, resolved) | what was fixed |
| watched, was watching (見た, 見ていた) | 監視した、レビューした、管理した (monitored, reviewed, managed) | what was watched |
| pulled together (まとめた) | 取りまとめた、整理した、集約した (consolidated, organized, aggregated) | |
| talked, negotiated (話した, 話をつけた) | 折衝した、調整した、提案した (negotiated, coordinated, proposed) | the other party (client, in-house, executives) |
| taught (教えた) | 指導した、育成した、OJT を担当した (instructed, trained, provided OJT, on-the-job training) | number of people and duration |
| sold (売った) | 販売した、受注した、獲得した (sold, took orders for, won) | amount and count within the user's own statement |
| decided (決めた) | 選定した、決定した、策定した (selected, decided, formulated) | whether decision-making authority existed |
| thought about (考えた) | 企画した、立案した、設計した (planned, drafted, designed) | |
| did it by hand (手を動かした) | 実装した、構築した、運用した (implemented, built, operated) | |
| alone (一人で) | 単独で、専任で (solo, as the sole owner) | |
| all together, as a team (みんなで, チームで) | チーム（N名）で (as a team, of N members) | headcount within the user's own statement |
| the higher-ups, the person above (偉い人, 上の人) | 経営層、部門長、上長 (executives, department head, superior) | confirm the party's title |
| the customer (お客さん) | 顧客、取引先、エンドユーザー (client, business partner, end user) | |
| part-time, temp job (バイト, パート) | アルバイト、パートタイム（雇用形態として記録）(part-time work, recorded as an employment type) | |
| was let go, was laid off (クビになった, リストラ) | 会社都合により退職 (left for reasons on the company's side) | write within the range the user stated. Never ask the reason |
| quit (辞めた) | 退職した、退任した、契約満了 (resigned, retired from the position, contract completed) | whether it was a completed contract or a personal choice, in the user's own words |
| worked hard, gave it my all (頑張った, しっかりやった) | （削る）(cut) | replace with the fact of what was done |
| various things, and so on (いろいろ, とか) | （列挙する）(enumerate) | cut it when it cannot be enumerated |

## Handling each answer format

The user decides the form of the answer. Elicitation never corrects how the user answers — whether the user
answers a choice-format question in free text, or answers several questions at once.

| Answer format | Response |
|---|---|
| Answering several questions at once | Sort what comes in by item into the notes, and ask next only about the items still unanswered. Never ask again about an item already answered |
| Narrating a career history in one long stretch of free text | Never return to the choice format. Present the list of items read off (company, period, role, responsibilities, achievements) and ask only "where it is different." This is the same handling as when reading from a document (`elicitation-guide.md`) |
| Answering out of order | The notes may be reordered chronologically. The content is never changed |
| Correcting a later answer | Add a `訂正:` (correction) line under the latest heading. Never ask the reason for the correction |
| "I don't remember" | Record it as `本人が不明とした` (the user called it unknown). Ask once whether a range or a rough time can be given, and leave it empty if none comes, without asking again |
| Answering with a range or an approximation | Record it as stated. Never round it to a single value |
| "I'd rather not say" | Record it as `未回答（本人の意向）` (unanswered, at the user's own wish). Never ask the reason, and never return to that item. This handling is kept especially for annual salary, reasons for leaving, and the circumstances of an employment gap |
| "That's not important" | Follow the user's own judgment and do not deep-dive. When said about a work-character preference or a condition, this is itself the answer, and is recorded as a desired level of `not_required`. This holds except for profile.json's required items (current role, company name, tenure period, job title, reasons for changing jobs); for those alone, state once that the item is required and what a downstream process cannot do without it |
| Asking back what a question is for | Answer in one sentence which downstream process uses it and for what |
| An answer outside the choices | Take it as stated through Other. Never round it to the nearest choice |
| Asking to change the order of questions | Follow it. Because the elicitation notes' headings and item names allow the answers to be matched up regardless of order, the order does not affect the result |

## A career history with an atypical shape

None of the following career histories are treated as unusual; each is recorded as the table below states. An
item in the "Never ask" column is recorded only when the user brings it up unprompted.

| Type of career history | How to record it | Never ask |
|---|---|---|
| Temporary staffing, SES (system engineering service), client-site assignment | `company` is the employer (the staffing agency or the employing company), `assignment` is the client site or place of dispatch, `employment_type` is 「派遣」「正社員（客先常駐）」(temporary staffing, permanent employee — client-site assignment), and the like | When the user would rather not name the client site, a description such as 「大手製造業」 (a major manufacturer) is fine |
| Contract employee, advisory position, part-time work | Write the employment type into `employment_type`. Treat it as one entry, the same as a permanent position | Why the user did not become a permanent employee |
| Contract work, freelance, sole proprietorship | `company` is the trade name or 「個人事業」 (sole proprietorship); write the main client into `assignment` or `responsibilities` | The breakdown of income |
| Secondment, transfer | For a secondment, make the seconding company and the receiving company two separate entries and keep the overlap in periods (concurrent employment). For a transfer, make the destination company a new entry | The circumstances of the secondment |
| Founding a company, management, a family business | Write `role` in the user's own words, such as 「代表取締役」 (representative director) or 「共同創業者」 (co-founder). Record revenue and headcount within the user's own statement | Why the business was closed |
| Public servant, teacher, medical, licensed professional | Write the official or professional title in the user's own words. Never reword it into a private-sector title | |
| Childcare leave, family-care leave, medical leave of absence | A leave taken while still employed counts within the tenure period (it stays part of employment). Write the leave's period into `career_history[].note` only when the user brings it up | The reason for the leave, the diagnosis |
| Returning to study (graduate school, vocational training, study abroad) | For a period not employed, write it into `career_gaps[].activities`; for a degree, also write it into `basic.education` | |
| Working overseas, a foreign company | The company name and job title may stand in the original language. Write the location into `assignment` or `note` | |
| Wanting to move into an unfamiliar occupation | Write the career history as fact, as it stands. Write the desired occupation into `targets.roles`, without bending the career history toward it | |
| A short tenure (a few months) | Write it as fact, as one entry | The reason for leaving (write it to `note` only if the user states it) |
| Many job changes | No special handling. Never merge career-history entries to reduce the count | |
| A side job, holding multiple jobs | Follow `elicitation-guide.md`'s rule for concurrent employment | The income from the side job |
| Re-employment after retirement, a senior job change | Re-employment is a new entry at the same company; write the user's own words, such as 「再雇用（嘱託）」 (re-employment, advisory position), into `employment_type` | Age |
| Foreign nationality, residence status | Write the type of residence status into `notes` (root) only when the user brings it up. Elicitation never asks about nationality | Details of nationality or residence status |
| A disability certificate, a request for accommodation | Write the requested accommodation into `notes` (root) only when the user brings it up. Elicitation never asks whether a certificate exists | The diagnosis or its grade |

`assignment`, `employment_type`, and `note` are optional fields of `career_history[]` (the specification is in the
hub's `references/profile-format.md`). An item absent from the user's statement is never written.

For a matter that calls for particular legal care, such as medical treatment, caregiving, disability, or
nationality, only what the user states is recorded. When asking a choice-format question about
activities during a gap period, add one sentence on what it is for (to decide how the document will explain the
gap), and show that declining to answer is an option.

## Prohibitions for elicitation

- Questioning the truth, source, or grounds of a statement.
- Proposing a figure, a time, a job title, or a scale from elicitation's own guess and having the user affirm it.
- Writing a reworded candidate into the notes without showing it to the user.
- Using, in a rewording, a role's phrasing stronger than the scope of involvement the user stated. Adding a figure,
  a scale, a scope, or an acting subject.
- Returning to an item the user said they would rather not answer. Asking the reason.
- Deep-diving into an item the user called "not important," when it is not a required item.
- Reshaping a career history with an atypical shape into a typical form (writing the place of assignment as the
  employer, writing a leave of absence as a gap, merging several career-history entries into one).

## Recording in the elicitation notes

The recording format of `profile_interview_notes.md` is set by `elicitation-guide.md`. What this file adds is the
following line formats.

| Line type | How to write it |
|---|---|
| Original statement | `- {item}: {the user's own words, as stated}` |
| Rewording | Directly under the original, `  - 言い換え（本人了承）: {the approved sentence}` |
| An uncertain or approximate statement | `（本人が不確かとした）` appended after the figure (the same mark as `elicitation-guide.md`) |
| A statement of "unknown" | `- {item}: 本人が不明とした` |
| Declining to answer | `- {item}: 未回答（本人の意向）` |
| Presenting a conflict | `- 確認: {statement A}／{statement B} → 本人の選択: {A or B}` |

The writer uses the reworded sentence for an item that carries a rewording line, and confirms that it never
exceeds the original's role or scale. The auditor checks whether an item with no rewording line carries
document-ready phrasing, and whether a rewording exceeds the original's scope of involvement. Neither checks the
truth of the statement itself.

## Grounding and limits

"The scale of role phrasing" and the "Verb and noun replacement table" are this skill's own operating convention;
citations cover the two failure types below, and the individual replacement words carry none. The two types are writing
"project leader experience" for work that was in fact only supporting [E1], and writing a team's achievement as an
individual's achievement [E2]. The latter source names, as a countermeasure, making the role and the degree of
involvement explicit ("as team leader," "was in charge of 〜, and 〜"). "The scale of role phrasing" is that
countermeasure broken into rungs in the user's own words. Both sources are level-C practitioner articles, and no
study measuring a rewording's effect on a selection outcome could be identified.

## Sources

<!-- textlint-disable -->
<!-- This section lists sources in a bibliographic format (publisher. Title. Level. URL). This section alone disables the rule so the separating periods are not judged as Japanese punctuation. -->

- [E1] 応募書類マスター（keireki.net）. 【履歴書の「盛る」はNG？】適切なアピール方法と注意点を解説！. Level C. https://keireki.net/rrsmoru/
- [E2] lekky.jp. 職務経歴書の「営業成績」は盛るとバレる？リスクと正しい書き方を解説. Level C (this skill's tools returned 403; content was confirmed from the search result's own index text). https://lekky.jp/articles/1030/

<!-- textlint-enable -->
