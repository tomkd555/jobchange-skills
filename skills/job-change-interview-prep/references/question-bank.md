# Canonical source for frequent questions (question categories, evaluation criteria, principles for answering)

This document organizes, by question category, the questions frequently asked in mid-career hiring interviews in Japan. For each category it gives the evaluation criterion the interviewer is checking with the question, the principle for answering, and its sources. The canonical source for foreign-affiliated behavioral interviews and case interviews is `foreign-interviews.md`; for answer-evaluation anchors, `evaluation-rubric.md`; and for the artifact holding company-specific interview information, `interview-intel-format.md`.

## Provenance and presentation of expected questions

An expected question has one of three provenances, distinguished by `interview_questions.json`'s `provenance` field.

| Provenance | Content | How it is presented to the user |
|---|---|---|
| `general` | A common question category from this document, independent of any particular company | Presented as is |
| `reported` | A question interview_intel.json reports as "asked" (`kind: reported`), or a question the user obtained from a job-change agency or a past selection process | Presented in its reported wording, with its source (review-site content is grade C) and posting period attached |
| `inferred` | A question inferred from company-research claims (a medium-term management plan, a desired candidate profile, a job posting's required qualifications) or from a review-site trend | Presented as one where "there is no guarantee it will be asked, but it is worth preparing for," with the basis for the inference attached |

Provenance and the confidence of the underlying evidence are separate things. A question reported through review-site content (C) is worth practicing as a record of the wording it was actually asked in. A question inferred from a securities report (A) rests on a certain fact, but there is no guarantee it will be asked. The two are never collapsed into a single confidence level.

How an inferred question is built follows this correspondence, depending on the kind of evidence.

| Basis (a claim's topic, or the kind of intel) | How the question is built |
|---|---|
| A job posting's required qualification | One achievement-drilling question per item (「〜の経験を具体的に教えてください」, "Please tell me specifically about your experience with ..."). The most mechanical to build and the least likely to miss the mark |
| A medium-term management plan's or securities report's priority initiative (`business`) | A motivation-for-applying or contribution-after-joining question (「〜の施策に、これまでの経験はどう活かせますか」, "How can your experience so far contribute to the ... initiative?") |
| A recruiting page's desired candidate profile or employee interviews (`philosophy`) | A culture-fit question (「〜な人物像とありますが、そう言える経験を教えてください」, "You describe wanting a ... kind of person — can you tell me about an experience that shows you fit that description?"). This is the company's own claim about itself, and even though the source is A, `confidence` is never set to high |
| A review site's stated reasons for considering leaving (`themes`) | A question phrased as the direction an interviewer is likely to probe (「〜という環境で、意欲をどう保ちますか」, "How do you sustain motivation in an environment like ...?") |
| A review site's stated post-hire gap (`themes`) | Material for a reverse question (「選考で聞いた話と入社後のずれを、どう見極めますか」, "How would you go about noticing a gap between what you heard in the selection process and what you find after joining?"). This fits a question the user asks better than one the interviewer asks |
| Recent news (a new venture, an M&A) | Material for motivation for applying or a reverse question. A scandal rarely becomes something an interviewer asks the candidate directly, so it is limited to material for a reverse question that checks on measures taken to prevent recurrence |

## The interviewer's overall evaluation criteria

These are the evaluation criteria that underlie mid-career hiring interviews generally, preceding any individual question category.

| Criterion | Content |
|---|---|
| 転職理由と志望動機の一貫性（中核） (Consistency between the reason for changing jobs and the motivation for applying, the core criterion) | Whether the reason for leaving / changing jobs connects to the reason for wanting to join this company without contradiction. This forms the core of the candidate assessment[E64]. |
| 再現性 (Reproducibility) | Whether the candidate has the behavioral traits to reproduce their prior achievements. What matters is the reproducibility of the behavior that produced the achievement[E63]. |
| カルチャーフィット (Culture fit) | Fit with the company's values and way of working. Job-change media commentary states that culture fit is emphasized alongside being immediately effective[E38] (grade C; no public data on how commonly this is actually applied could be confirmed). |
| 定着性 (Retention) | Whether the candidate is likely to stay after joining. This shows up most strongly as a concern about a high number of job changes[E65]. |
| 入社意欲 (Motivation to join) | Motivation to work at the company, and the specificity of the candidate's picture of life after joining[E67]. |

### Sub-items of the evaluation criteria (vocabulary for interviewer_intent)

An employer-facing question compilation divides 120 questions into five major categories — 16 on job aptitude, 6 on reason for leaving, 23 on motivation for applying / career vision / view of work, 71 on personality / character, and 4 on additional appeal / reverse questions — and further divides the personality / character category into 12 sub-items[E98]. When writing `interviewer_intent`, use these 12 sub-items as vocabulary alongside the five criteria above.

| Sub-item | Number of questions | What it checks |
|---|---|---|
| 社風との相性 (fit with company culture) | 3 | Fit with the company's values and way of working |
| 既存社員との相性 (fit with existing employees) | 4 | Ease of collaborating with colleagues in the assigned team |
| ストレス耐性 (stress tolerance) | 6 | What the candidate gained from a difficult experience |
| 強み・弱み (strengths and weaknesses) | 8 | Self-awareness and corrective action |
| 主体性・積極性 (initiative) | 4 | Experience acting without waiting for instructions |
| コミュニケーション力・協調性 (communication and cooperativeness) | 13 | How the candidate works with someone who disagrees |
| 分析力・論理思考力 (analytical and logical thinking) | 8 | How the candidate breaks down a problem and follows a line of reasoning |
| 向上心・成長意欲 (drive to grow) | 7 | An ongoing attitude toward learning |
| 学習意欲 (willingness to learn) | 4 | Taking on a new area |
| 責任感 (sense of responsibility) | 5 | Experience seeing an undertaken task through to completion |
| 柔軟性 (flexibility) | 3 | Response to change |
| 発想力 (creativity) | 4 | Experience proposing a new idea |

### Emphasis by age bracket

A survey of 7,206 job changers (conducted November 25 to December 22, 2021) found that the hardest question to answer was, for respondents in their 20s, 「今後のキャリアプラン」 (career plan going forward), and for respondents in their 30s and 40s and older, the reverse question (「何か質問はありますか」). Across all age brackets, the most common form of preparation was preparing answers to expected questions[E99]. When generating expected questions, the balance between career-plan and reverse-question preparation shifts according to the user's age bracket. A reverse question is one for which gathering company-specific information yields no answer; the answer lies in the user's own interests.

### Emphasis by selection stage

Domestic mid-career hiring is typically described as three stages — a first round with a frontline interviewer, a second round with a department head, and a final round with an executive — though the number of stages and the interviewers vary by company. The emphasis at each stage is as follows; this is an operational rule of thumb, and the target company's actual stages should be confirmed from `interview_intel.json`'s `format_facts`. When they cannot be confirmed, `stage` is set to `不明` (unknown).

| Stage | Interviewer (typical) | Emphasis |
|---|---|---|
| カジュアル面談 (casual meeting) | A recruiter or a frontline employee | Nominally a mutual exchange of information. The direction of questioning reverses (see below) |
| 一次面接 (first interview) | A frontline manager or colleague | Drilling into day-to-day work, skill fit, ease of collaboration |
| 二次面接 (second interview) | A department head | Management, organizational fit, career plan |
| 最終面接 (final interview) | An executive | Level of interest in the company, conditions, intent to join, culture fit |

## Question categories

Major job-change media outlets name self-introduction, reason for changing jobs, motivation for applying, self-PR, and reverse questions as the five that are always asked[E100]. This document lists categories including these five.

### Self-introduction

| Item | Content |
|---|---|
| Evaluation criterion | Whether the candidate can convey the essence of their career history briefly. This serves as the entry point for subsequent questions, giving the interviewer material for choosing where to drill down[E100]. |
| Principle for answering | Speak for about a minute, covering the flow of the candidate's career history and one achievement relevant to the applied role. Stay within the range of profile.json's `summary` and `career_history`, without overlapping with self-PR. |

### Reason for changing jobs / reason for leaving

| Item | Content |
|---|---|
| Evaluation criterion | An essential check that shapes matching accuracy and retention[E62]. Consistency between the reason for leaving and the motivation for applying forms the core of the candidate assessment[E64]. The interviewer watches for whether the explanation blames others. |
| Principle for answering | Never end the explanation by blaming others. Add a corrective action the candidate themselves took to the reason. Reframe a negative reason (dissatisfaction, conditions) as a positive aspiration for what the candidate wants to achieve once it is resolved[E64]. Keep the narrative consistent with the motivation for applying. |

### Motivation for applying

| Item | Content |
|---|---|
| Evaluation criterion | Motivation to join, company understanding, and consistency with the reason for changing jobs. Whether the reason is specific to "this company in particular." Content that would apply equally to a competitor is not well regarded[E97]. |
| Principle for answering | Connect the answer to a company-specific fact (a claim in company_research.json — philosophy, business, or desired candidate profile). Match the aspiration stated under reason for changing jobs to the basis for why this company can realize it[E97]. |

### Self-PR and achievements

| Item | Content |
|---|---|
| Evaluation criterion | Whether the candidate will be immediately effective, and reproducibility. A prior achievement is an item used to check whether the candidate will be immediately effective[E63]. The interviewer looks at whether the behavioral trait that produced the achievement can be reproduced at the new employer. |
| Principle for answering | Back the achievement with numbers. State the role and scope of responsibility accurately, within what profile.json records, without overstating the scale or the candidate's own part in it. |

### Drilling into achievements

| Item | Content |
|---|---|
| Evaluation criterion | Reproducibility, thinking and action, consistency, and self-reflection. A STAR-based interview evaluates, at each stage, the premise (Situation), the thinking and action (Task/Action), the presence of fabrication or inconsistency, and self-reflection (looking back on the Result)[E66]. |
| Principle for answering | Make the answer specific enough to withstand further drilling. Keep numbers, proper nouns, and the timeline consistent and fact-based. A contradiction between answers tends to surface under drilling, so prepare with facts (a report exists that over 90 percent of candidates engage in some form of impression management in an interview, and drilling serves as a means of detecting such inconsistency; see the academic evidence in `evaluation-rubric.md`)[E80]. |

### Weaknesses

| Item | Content |
|---|---|
| Evaluation criterion | Self-awareness, self-reflection, and corrective action. Whether the candidate recognizes a weakness and takes action to improve it. Evaluated on the same axis as the self-reflection check in a STAR-based interview[E66]. |
| Principle for answering | Admit the weakness candidly, then add a specific action being taken to improve it. Never end by blaming others[E64]. Never choose a weakness that would be fatal to performing the applied role. |

### Number of job changes

| Item | Content |
|---|---|
| Evaluation criterion | A retention concern (which shows up most strongly against a high number of job changes) and consistency in the candidate's career axis[E65]. |
| Principle for answering | Connect each job change through a career axis (a consistent direction), and show the intent to stay at the next employer[E65]. Respond with the consistency of the axis. |

### Employment gaps and short tenures

| Item | Content |
|---|---|
| Evaluation criterion | From the number of job changes, the interviewer looks for "a pattern of repetition." From an employment gap or a short tenure, the interviewer looks at "what happened in that one instance." This checks retention and whether the candidate can explain the fact candidly. |
| Principle for answering | State the fact briefly, and add what the candidate did during that period (relearning, caregiving, recovery after treatment, job-seeking activity) and the reason for returning to the applied role. Stay within the range of the candidate's own explanation recorded in profile.json's `career_history[].note` and `notes`, without fabricating a reason. Treatment, caregiving, or a family matter need not be described in more detail than the candidate themselves is willing to share. |

### Failure and setback

| Item | Content |
|---|---|
| Evaluation criterion | Stress tolerance (what the candidate gained from a difficult experience) and self-reflection[E98]. The interviewer looks at what the candidate changed after the failure. |
| Principle for answering | State, in order, the fact of the failure, the judgment made at the time, and the action changed afterward. Never end by blaming others. Choose from a behavioral episode in self_analysis.json's `episodes`. |

### Management

| Item | Content |
|---|---|
| Evaluation criterion | For a candidate with experience managing subordinates or juniors, this checks goal-setting, evaluation, development, and how disagreement was handled. Its weight increases from the second interview onward. |
| Principle for answering | State the number of people, the period, and the role accurately, within what profile.json's `career_history[].role` and `assignment` record. Never let a phrase such as "led" or "oversaw" exceed the level of role the candidate stated in the interview (the canonical source lives in job-change-profile's `references/answer-handling.md`). |

### Collaboration and conflict

| Item | Content |
|---|---|
| Evaluation criterion | Communication and cooperativeness (how the candidate works with someone who disagrees), and fit with existing employees[E98]. |
| Principle for answering | State the situation where opinions diverged, the candidate's understanding of the other party's position, the process that reached agreement, and the outcome. Never frame it as blaming the other party. |

### Career plan

| Item | Content |
|---|---|
| Evaluation criterion | Consistency with the motivation for applying, and the specificity of a realistic path at this company. This is reported as the hardest question to answer for respondents in their 20s[E99]. |
| Principle for answering | State a three- to five-year outlook as an extension of the applied role. If self_analysis.json has a `career_narrative`, use it as the axis. Connect it to the company's business plan (a `business` claim in company_research.json). |

### Contribution after joining

| Item | Content |
|---|---|
| Evaluation criterion | Whether the candidate will be immediately effective, and company understanding. Whether the candidate, having understood the job posting's duties, can picture what they will do in the first six months to a year. |
| Principle for answering | Match the job posting's required qualifications to the candidate's own achievements one to one, and name one task to tackle first. Never presuppose a business or a challenge absent from a claim in company_research.json. |

### Culture fit

| Item | Content |
|---|---|
| Evaluation criterion | Fit with company culture[E98]. Whether the company's values and way of working match the candidate's stated preferences for work style (profile.json's `work_character_preferences`). |
| Principle for answering | Against the desired candidate profile (a `philosophy` claim), give one experience that supports it. Where there is a mismatch, state it honestly and describe how the candidate would work with it. A self-reported personality trait (self_analysis.json's `personality`) is used only to the extent it is tied to an episode. |

### Confirming conditions

| Item | Content |
|---|---|
| Evaluation criterion | Desired salary, possible start date, the status of other companies' selection processes, and willingness to relocate. Its weight increases at the final interview. This is the company's own mandatory confirmation item. |
| Principle for answering | State the desired salary based on profile.json's `salary.desired`, with reasoning attached (the current amount and the market rate). State the possible start date including the time needed to resign from the current position. State the status of other selection processes as fact, never falsely. A `fit_assessment.json` `condition_fit` item with `met: "unknown"` is a candidate for something to confirm at this point. |

### Reverse questions

| Item | Content |
|---|---|
| Evaluation criterion | A place to gauge motivation to join and the specificity of the candidate's picture of life after joining[E67]. |
| Principle for answering | Prepare a specific, post-joining question that presupposes an understanding of the business, the organization, and the role. |

Two kinds of reverse question should be avoided.

- A question whose answer is easy to look up (company overview, already-published business content, or anything already established in company_research.json)[E67].
- A question about treatment (salary, benefits, leave — anything that suggests conditions matter more than motivation)[E67].

The reverse question is reported as the hardest to answer for respondents in their 30s and older[E99]. An `interview_intel.json` `themes` entry about a post-hire gap, and a `fit_assessment.json` `condition_fit` item marked `unknown`, both serve as material for a reverse question.

### Casual meeting

A meeting held before the selection process, nominally for mutual information exchange. The direction of questioning reverses, and the user becomes the one asking. The employer side often asks for a brief self-introduction and reason for changing jobs. This section is this skill's own operational organization and carries no source. Whether a casual meeting counts as part of the selection process is not settled in practice, and matters such as travel-expense handling or the disclosure of working conditions do not necessarily follow the same rules as the formal selection process. The user should not assume a casual meeting receives the same treatment as the selection process, and should confirm the employer's own treatment of it during the meeting if needed.

| Item | Content |
|---|---|
| Evaluation criterion | Nominally a mutual exchange of information, but the impression carries over into the selection process. What matters is the specificity of interest in the business and the role. |
| Principle for proceeding | Prepare around five reverse questions, asked in the order of business, role, team, and way of working. Raise the topic of treatment only if the employer side brings it up first. Keep the self-introduction to about a minute, and state the reason for changing jobs briefly, within a range consistent with the motivation for applying. Record the content of the meeting in `interview_notes_user.md`, as material for later expected questions. |

## Matters the user is not required to answer

The Ministry of Health, Labour and Welfare (厚生労働省) names 14 matters that, being unrelated to an applicant's aptitude or ability, risk leading to employment discrimination if asked about[E101]. Because an interviewer asking about these violates the basic principles of fair hiring selection, none of these is ever generated as an expected question. When a review reports that one of these was asked (`interview_intel.json`'s `category: 配慮事項`), it is presented to the user as "a matter you are not required to answer," and the user is never coached on how to answer it.

| Group | Matters |
|---|---|
| Matters outside the candidate's own responsibility | Permanent domicile and place of birth; family (occupation, relationship, health, medical history, standing, education, income, assets); housing situation (floor plan, number of rooms, type of housing, nearby facilities); living and family environment |
| Matters that should be a matter of free choice | Religion, political party supported, outlook on life and living philosophy, an admired figure, ideology, involvement in a labour union or student movement or other social movement, subscribed newspapers, magazines, or favorite books |
| Selection methods | A background check, application documents that include matters unrelated to the candidate's aptitude or ability, and a health examination at the time of selection whose necessity is not reasonably and objectively established |

"An admired figure" or "a favorite book" is sometimes asked in the form of small talk. Whether to answer is the user's own choice, and this skill never steers the user toward either answering or declining.

## Information obtained through a job-change agency

A job-change agency often passes a candidate the questions recently asked in interviews it handles and the trends in the selection process. This is more current than review-site content gathered from the web and connects directly to that company's selection process. When the user holds this information, this skill records it in `interview_notes_user.md` in Step 0 and uses it as material for expected questions with `provenance: reported`. Experience from a past selection process at the same company is treated the same way. This file contains the details of the user's own selection process and is never passed to a role with web transmission methods.

## Correspondence between question categories and job-change-interview-coach's categories

The `category` job-change-interview-coach attaches to an expected question connects to this document's question categories through the following correspondence. A question about the number of job changes is treated as belonging to the reason-for-changing-jobs category, carrying the intent (interviewer_intent) of checking retention. The canonical vocabulary for `category` lives in `interview-format.md`'s "The known question categories." This table shows the meaning of each `category` and its correspondence to this document's question categories.

| This document's question category | The coach's category |
|---|---|
| Self-introduction | 自己紹介 |
| Reason for changing jobs / reason for leaving | 転職理由 |
| Number of job changes | 転職理由（interviewer_intent = 定着性） |
| Employment gaps and short tenures | 空白期間・短期離職 |
| Motivation for applying | 志望動機 |
| Self-PR and achievements | 自己PR |
| Drilling into achievements | 実績深掘り |
| Weaknesses | 弱み |
| Failure and setback | 失敗・挫折 |
| Management | マネジメント |
| Collaboration and conflict | 協働・対立 |
| Career plan | キャリアプラン |
| Contribution after joining | 入社後の貢献 |
| Culture fit | カルチャーフィット |
| Confirming conditions | 条件確認 |
| Reverse questions | 逆質問 |
| Casual meeting | カジュアル面談 |
| Behavioral (foreign-affiliated companies, and domestic consulting firms and IT companies) | ビヘイビアラル（`foreign-interviews.md`） |
| Case / technical (same as above) | ケース（`foreign-interviews.md`） |
| Matters the user is not required to answer | Not present in `category`. A `配慮事項` report from `interview_intel.json` is listed in `notes` and never presented in the mock interview |

## Sources

<!-- textlint-disable -->
<!-- This section lists sources in a bibliographic format (publisher. title. year. level. URL). This rule is disabled for this section only, so that the separating periods and parts of company names are not judged as Japanese punctuation or synonyms. -->

- [E38] マイナビ転職 (Mynavi Job Change). 転職の適性検査とは？新卒と中途の違いや目的、種類、対策法. 2026. Level C. https://tenshoku.mynavi.jp/knowhow/caripedia/167/
- [E62] マイナビ（HUMAN CAPITAL サポネット）(Mynavi, HUMAN CAPITAL Saponet). 中途採用面接で聞くべき厳選質問集［50選］｜面接官の心得. 2022-11-09. Level B. https://saponet.mynavi.jp/column/detail/ty_saiyo_t03_50-interview-questions_210611.html
- [E63] マイナビ（HUMAN CAPITAL サポネット）. 中途採用面接で聞くべき厳選質問集［50選］｜面接官の心得. 2022-11-09. Level B. https://saponet.mynavi.jp/column/detail/ty_saiyo_t03_50-interview-questions_210611.html
- [E64] マイナビ転職. 面接での転職・退職理由の答え方 面接官も納得のポジティブな回答例文. 2026-02-25. Level B. https://tenshoku.mynavi.jp/knowhow/mensetsu/guide/35/
- [E65] リクルートエージェント (Recruit Agent). 転職回数が多い場合、面接で理由を聞かれたらどう答える？【回答例付き】. 2022-09-30. Level B. https://www.r-agent.com/guide/jobinterview/14550/
- [E66] エン・ジャパン (en Japan). 誰でも応募者を深掘りできる面接フレームワーク│STAR面接とは？. 2023-07-07. Level B. https://saiyo.employment.en-japan.com/blog/star-mensetsu
- [E67] エン転職 (en Tenshoku). 面接で使える逆質問45例！逆質問のコツや評価される立ち回りを紹介. 2026. Level B. https://employment.en-japan.com/tenshoku-daijiten/41419/
- [E80] Journal of Applied Psychology. Measuring faking in the employment interview: Development and validation of an interview faking behavior scale. 2007. Level A (single study). DOI:10.1037/0021-9010.92.6.1638 https://doi.org/10.1037/0021-9010.92.6.1638
- [E97] リクルートエージェント. 職務経歴書に志望動機は必要？履歴書との違いや書き方を解説. 2024. Level B. https://www.r-agent.com/guide/resume/article4402/
- [E98] エン・ジャパン（エン人事のミカタ）(en Japan, "En Jinji no Mikata"). 面接質問集120選. Level B (an employer-facing question compilation; the question counts for the five major categories and 12 sub-items were confirmed on the original page on 2026-09-04. The 12 sub-items sum to 69, which does not match the major category's 71 — a discrepancy that comes from how the original page counts). https://partners.en-japan.com/special/mensetsu_shitsumon/
- [E99] エン転職. アンケート集計結果「面接」について. 2022 (survey period 2021-11-25 to 2021-12-22, 7,206 valid responses). Level B. https://employment.en-japan.com/enquete/report-80/
- [E100] doda. 面接で必ず聞かれる5つの質問. Level B. https://doda.jp/guide/mensetsu/interview/
- [E101] 厚生労働省 (Ministry of Health, Labour and Welfare). 公正な採用選考の基本（就職差別につながるおそれがある14事項）. Level A. https://www.mhlw.go.jp/www2/topics/topics/saiyo/saiyo1.htm

<!-- textlint-enable -->
