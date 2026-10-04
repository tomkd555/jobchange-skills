# Section: Career skeleton (career)

Settles the chronology of companies, periods, and roles the user has held. This is the core of profile.json. Every other section and every downstream process is built on this frame. Responsibilities and achievements get a detailed pass later as the `achievements.md` section, and skills as the `skills.md` section. The section catalogue and the definition of reach stages are in `../sections.md`.

## Fields to fill

| Field | First pass | Format |
|---|---|---|
| `career_history[].company`, `period`, `role` | First pass | Free text (confirmation only when imported from a document) |
| Concurrent `career_history[]` entries | First pass | Multiple choice plus free text |
| `career_history[].employment_type`, `assignment`, `note` | First pass (only where applicable) | Free text |
| `career_gaps[].period`, `explanation`, `activities` | First pass (only where detected) | Multiple choice (activity type) plus free text |

`role` is asked as free text because it is asked at a point when nothing is yet known about that position. Building candidates in advance would mean presenting a job title the interviewer imagined.

## Reach stages

| Stage | Condition |
|---|---|
| `skeleton` | At least one career-history entry has `company`, `period`, and `role` filled |
| `deep` | Every entry is filled, and every entry's `period` reads in the form `YYYY-MM〜YYYY-MM` or `YYYY-MM〜現在` (YYYY-MM to present) |

## Procedure

### Importing an existing document

Before starting the elicitation, ask in one question whether the user has a shokumu-keirekisho, rirekisho, or resume file on hand (Word, PDF, text, or Markdown). **Do not ask the user to submit one.** When the answer is no, proceed straight into the dialogue. Only when the answer is yes should a path be accepted and read.

Read PDF, text, and Markdown files with Read. Read does not handle `.docx`, so read its body with Python's standard library through Bash. A `.docx` file is a ZIP archive, and its body is at `word/document.xml`. Replace each paragraph terminator `</w:p>` with a newline before stripping tags, to preserve the paragraph breaks. Pass the result through `html.unescape` after stripping tags, because XML writes `&`, `<`, and `>` as entities. Skipping that step leaves "A&amp;B株式会社" written into profile.json as `A&amp;amp;B株式会社`.

```bash
python -c "import zipfile,re,html,sys; xml=zipfile.ZipFile(sys.argv[1]).read('word/document.xml').decode('utf-8'); xml=re.sub(r'</w:p>','\n',xml); print(html.unescape(re.sub(r'<[^>]+>','',xml)))" {path to the document}
```

Table cells also come out as paragraphs, so a shokumu-keirekisho written as a table still yields its company name, employment period, and job title. The correspondence between rows and columns is lost, though, so for a document built mainly as tables, confirm the extracted order with the user. `.doc` (the legacy format) has no ZIP structure, so this method cannot read it; recommend a PDF or text version, and fall back to the dialogue when that is not practical. A PDF made only of scanned images may leave Read unable to extract any text. The PDF-export feature of a LinkedIn profile supports only Latin characters, so a Japanese-language profile comes out with its body missing. Do not fill an unreadable field by guessing. Ask about that field alone through the dialogue.

In the SES (systems engineering services) industry, a skill sheet often records the phase of involvement as an abbreviation code. Confirm the meaning of each code with the user before transcribing it into `responsibilities`.

Once read, transcribe the extracted company names, employment periods, job titles, and responsibilities into the elicitation notes. Show the extracted list to the user and ask 「違うところだけ教えてください」 (please point out only what is wrong). Ask the user to report only the incorrect items, and do not ask for agreement on every item. Add only the corrected items to the notes, under a `訂正:` (correction) line.

Long text such as a description of duties or an achievement extracts less accurately than a company name, employment period, or job title. Mark such long text with `（要確認）` (needs confirmation) at the point it is transcribed into the notes, and remove the mark once the user has confirmed it.

Treat a fact read from a file on the same footing as a fact stated in the dialogue (SKILL.md Principle 8). Do not treat it as documentary proof, and do not use it to corroborate other items.

#### Settled wording: document on hand

| Item | Wording |
|---|---|
| `header` | 手元の書類 (Document on hand) |
| `question` | 職務経歴書・履歴書・レジュメのファイルはお手元にありますか。あれば読み込んで、伺う項目を減らせます。 (Do you have a shokumu-keirekisho, rirekisho, or resume file on hand? If so, reading it can reduce the number of questions asked.) |
| Choice 1 | **ファイルがあります**：続けて置き場所をお知らせください。Word・PDF・テキスト・Markdown のいずれでも読めます。 (I have a file: please tell me where it is. Word, PDF, text, and Markdown can all be read.) |
| Choice 2 | **対話で答えます**：ファイルは使わず、伺いながら進めます。 (I will answer through dialogue: proceeding through questions without a file.) |

When the user selects 「対話で答えます」, do not raise the subject of a document again, and do not recommend preparing one.

#### Settled wording: confirming the extracted result

Show the company names, employment periods, job titles, and responsibilities extracted from the document as a list, and confirm with the following text. Since no set of choices can be built for this, AskUserQuestion is not used. Write it as text accompanying the list.

| Item | Wording |
|---|---|
| Lead-in | 読み込んだ書類から、次のように読み取りました。**違うところだけ**お知らせください。合っている項目についてのお返事は要りません。 (From the document read, the following was extracted. Please point out only what is wrong. No reply is needed for items that are correct.) |
| Note on long text | 担当業務の記述は読み違いが起きやすいため、`（要確認）` を付けています。ここだけは目を通していただけますか。 (The description of duties is prone to misreading, so it is marked `(needs confirmation)`. Could you look over just that part?) |
| Item that could not be read | 書類から読み取れなかった項目は `未取得` と書いています。後ほど伺います。 (An item that could not be extracted from the document is marked `未取得` [not yet obtained]. It will be asked about later.) |

Do not ask for agreement on every item. Ask 「どこが違いますか」 (this avoids a phrasing whose default answer is agreement). Add only the corrected items to the elicitation notes, under a `訂正:` line.

### Settling the skeleton

First settle the list of company × employment period × role, in chronological or reverse-chronological order. When it was imported from a document, that list is the skeleton, and it becomes settled once corrections have been reported. Do not ask the user about an imported item again through the dialogue. Use a transition such as a job change, a transfer, or a promotion as a chronological landmark. The rationale is in `../elicitation-guide.md`. For a position currently held, write the period as `〜現在` (to present).

Opening questions:

- Ask the user to list the companies held, in chronological or reverse-chronological order. What was the employment period at each company, from and to (in the form `YYYY-MM〜YYYY-MM`; `〜現在` [to present] while still employed)?
- What was the role or title at each company (free text)?
- Where were the turning points, such as a job change, a transfer, or a promotion (used as a chronological landmark)?

Once the skeleton is laid out, confirm in one question whether there was a period of holding multiple positions at the same time (concurrent duty, secondment, side work, self-employment). When there was, ask about that position too as one more `career_history` entry (company, period, and role). Record within `role` which capacity it was held in (such as 「業務委託（副業）」, contract work, side job). Record the overlap in employment periods as it stands, as a record of concurrent employment.

When the employer and the place of work differ (dispatch work, SES, being stationed at a client site, contract work, or secondment), write the employer into `company` and the place of work into `assignment`. Write the employment type in the user's own words into `employment_type`. Record a non-standard career history (a leave of absence, starting a business, civil-service work, overseas assignment, and the like) following the table in "A career history with an atypical shape" in `../answer-handling.md`, and keep it in its own form.

#### Settled wording: concurrent employment

| Item | Wording |
|---|---|
| `header` | 並行の有無 (Whether there was concurrent employment) |
| `question` | いま挙げていただいた職のうち、同じ時期に2つ以上に在籍していた期間はありますか。 (Among the positions just listed, was there a period of holding two or more of them at the same time?) |
| `multiSelect` | true |
| Choice 1 | **副業・業務委託**：本業と並行して、別の会社や個人で仕事を受けていました。 (Side work or contract work: taking on work from another company or as an individual, alongside the main job.) |
| Choice 2 | **出向・兼務**：籍を置いたまま、別の会社や部門でも働いていました。 (Secondment or dual appointment: working at another company or department while remaining on the payroll of the original one.) |
| Choice 3 | **自営・法人の経営**：勤めのかたわら、自分の事業や会社を持っていました。 (Self-employment or running a company: holding one's own business or company alongside employment.) |
| Choice 4 | **なし**：どの時期も職は1つだけでした。 (None: only one position was held at any time.) |

### Employment gaps

Once the skeleton (including concurrent positions) is settled, mechanically detect any period (6 months or longer) not covered by any career-history entry's employment period. Immediately ask about its explanation and the activity during it, and record it in `career_gaps`. Perform the detection against the union of every career-history entry's period. Checking only adjacent career-history entries would detect an employment gap that does not exist, when side work overlaps with a main job. The rationale for how gaps are handled is in "Handling an employment gap" in `../elicitation-guide.md`.

#### Settled wording: activity during the gap

Replace `{期間}` (the period) with the detected period (such as "2019-04〜2019-12").

| Item | Wording |
|---|---|
| `header` | 期間中の活動 (Activity during the period) |
| `question` | {期間} は、どのように過ごされましたか。当てはまるものが無ければ Other でお聞かせください。 (How did you spend {period}? If none of these apply, please tell us through Other.) |
| `multiSelect` | true |
| Choice 1 | **学習・資格取得**：勉強や資格の取得に充てていました。 (Study or obtaining a certification: spent on study or working toward a certification.) |
| Choice 2 | **療養**：ご自身の治療や休養に充てていました。 (Medical treatment or rest: spent on one's own treatment or recovery.) |
| Choice 3 | **家庭の事情・介護**：ご家族の事情や介護に充てていました。 (Family circumstances or caregiving: spent on a family matter or caregiving.) |
| Choice 4 | **転職活動**：次の勤め先を探していました。 (Job search: spent looking for the next position.) |

The one-sentence explanation (`career_gaps[].explanation`) is then asked as free text, based on the activity chosen.

## Downstream

Every process reads this section. Application-document writing gives priority to the most recent 7 to 10 years. `job-change-documents` applies that priority, and profile.json itself keeps the full history.
