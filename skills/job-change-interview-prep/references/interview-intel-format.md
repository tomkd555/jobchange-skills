# Canonical specification for interview_intel.json (interview-intel-format)

This is the canonical source defining the field specification, entry criteria, and mechanical validation rules for `interview_intel.json`, the interview-information research artifact. The interview-information research role (job-change-interview-scout) produces the artifact to this specification, and `scripts/validate_interview_intel.py` checks it mechanically against this specification. The interview preparation role (job-change-interview-coach) reads this artifact as material for expected questions.

The output path is `{DATA_ROOT}/companies/{company slug}/interview_intel.json`, in the per-company non-personal-information tree. It is written by a role with web transmission methods, and the user's personal information and anything derived from it is never written to this file (the canonical definition of the boundary is in `{HUB_SKILL_DIR}/references/pii-boundary.md`).

## Positioning

Company-specific expected questions previously rested solely on company_research.json's claims with `topic=selection_process`. The company research role gathers that as one of eight topics, so the collection of interview questions themselves tended to stay shallow. `interview_intel.json` is an artifact built by re-collecting information specifically about the target company's interviews from review sites, recruiting pages, and candidate write-ups.

It gathers three kinds of content, each a hypothesis about what might be asked in an interview.

| Kind | Content | How it is used |
|---|---|---|
| Reported questions (`reported_questions`) | Question text a review or write-up reports as "asked," or question text inferred from a description | Candidate expected questions. `kind` shows the nature of the provenance |
| Facts about interview format (`format_facts`) | The number of selection stages, interviewer seniority, whether online or in person, duration, whether there is a written test or aptitude test | The premise for expected questions matched to a stage. Where this overlaps `exam_assessment.json`, the two are cross-checked |
| Trends readable from review-site posts (`themes`) | What interviewers repeatedly try to confirm, and the resulting likely direction of follow-up | The basis for an inferred question (`kind: inferred`) |

Whether a question was "reported" or "inferred" is distinguished by `kind`; the confidence of the source is distinguished by `grade`. `kind` and `grade` are never merged into one confidence level. A reported question is worth practicing in its reported wording; an inferred question is presented to the user as one where "there is no guarantee it will be asked, but it is worth preparing for." Which frame is used is decided by `kind`; `grade` decides the confidence of the underlying fact.

## Overall structure

```json
{
  "schema_version": "1.0",
  "company": "架空クラウドワークス株式会社",
  "role_title": "バックエンドエンジニア",
  "researched_at": "2026-09-04",
  "reported_questions": [
    {
      "id": "RQ001",
      "question": "現職を離れようと考えた理由を教えてください",
      "kind": "reported",
      "category": "転職理由",
      "stage": "一次面接",
      "source_url": "https://example.com/reviews/kuraudo-works/interview/1",
      "source_name": "転職会議",
      "grade": "C",
      "quote": "「現職を離れようと考えた理由を教えてください」と一次面接で聞かれた",
      "posted_at": "2025-11",
      "accessed": "2026-09-04"
    }
  ],
  "format_facts": [ ],
  "themes": [ ],
  "search_log": [ ],
  "coverage_notes": "",
  "open_questions": [ ]
}
```

A fully filled-in example (fictional data) is in `assets/interview_intel_example.json`.

## Field specification

### Top level

| Field | Required | Entry criteria |
|---|---|---|
| `schema_version` | Required | Currently `"1.0"`. An absence or an empty value is an ERROR. A value outside the known set is a WARN |
| `company` | Required | The company name. An absence or an empty value is an ERROR |
| `role_title` | Optional | The target job title. A string or `null`; anything else is an ERROR |
| `researched_at` | Required | The date the research was done (`YYYY-MM-DD`). An absence, a format mismatch, or a non-existent date is an ERROR |
| `reported_questions` | Required | An array. A non-array value is an ERROR. An empty array is a WARN |
| `format_facts` | Required | An array. A non-array value is an ERROR. An empty array is a WARN |
| `themes` | Required | An array. A non-array value is an ERROR. An empty array is a WARN |
| `search_log` | Required | An array. An absence, a non-array value, or an empty array is an ERROR |
| `coverage_notes` | Optional | The scope and limits of the research. Not writing it is a WARN |
| `open_questions` | Optional | An array of points that could not be corroborated. A non-array value, or any element other than a non-empty string, is an ERROR |

An artifact where all three arrays are empty and `open_questions` is also empty is an ERROR (an artifact with zero content makes it impossible to tell whether the research failed or the target simply has none). When nothing at all can be found, write this fact and the path taken in `open_questions` and `coverage_notes`.

### Evidence fields common to the three arrays

Each element of `reported_questions`, `format_facts`, and `themes` has the following fields.

| Field | Required | Entry criteria |
|---|---|---|
| `source_url` | Required | The source URL. Not starting with `http` is an ERROR |
| `source_name` | Optional | The source's name (転職会議, キャリコネ, 採用ページ, and so on). These are the values written into `source_name` |
| `grade` | Required | An evidence level, A through D. A value outside these four is an ERROR. `D` is a WARN. The canonical definition is in `job-change-company-research/references/evidence-grading.md` |
| `quote` | Required | The quote from the source. An absence or an empty value is an ERROR. Kept to the minimal length needed to identify the question |
| `posted_at` | Optional | The source's posting or publication date (`YYYY-MM` or `YYYY-MM-DD`), written when it can be read |
| `accessed` | Required (nullable) | The access date (`YYYY-MM-DD`). Not writing it, or `null`, is a WARN. A format mismatch or a non-existent date is an ERROR |

The level is determined by the source. A company's own recruiting page is A; a survey or explanatory article published by a major job-change media outlet is B; a review-site or candidate-write-up aggregation site is C; a personal blog, social media, or anonymous forum is D. A former employee's blog is D. Never assert a fact about the company's interviews on the basis of C or D alone.

### reported_questions[]

| Field | Required | Entry criteria |
|---|---|---|
| `id` | Required | `RQ` followed by three or more digits (the `RQ001` format). An absence, a format mismatch, or a duplicate is an ERROR |
| `question` | Required | The question text. **Always phrase it as a question.** Never write it as a prediction such as 「〜を聞かれる可能性が高い」 ("... is likely to be asked"), because `kind` already indicates whether it is an inference. An absence or an empty value is an ERROR |
| `kind` | Required | `reported` (the source itself reports the question text) or `inferred` (the question text is inferred from the source's description). A value outside these two is an ERROR |
| `category` | Optional | The question category. The canonical vocabulary is in `question-bank.md`'s "Correspondence between question categories and job-change-interview-coach's categories" |
| `stage` | Optional | The selection stage at which it was asked: one of `カジュアル面談`, `一次面接`, `二次面接`, `最終面接`, or `不明`. `不明` when the source does not state the stage |

When `kind` is `reported`, `quote` must contain the question text. If `question` and `quote` do not overlap, this is a WARN (a question labeled reported with no question in the quote). When `kind` is `inferred`, `quote` is the description that grounds the inference.

When a source reports a question touching a matter that could lead to employment discrimination (listed in `question-bank.md`'s "Matters the user is not required to answer"), record it with `kind: reported` and `category: 配慮事項` (a matter requiring care). Examples are 「家族構成を聞かれた」 and 「持ち家か賃貸かを聞かれた」 (asked about family composition / whether one owns or rents). It is recorded as a fact about the selection process. The interview-preparation role never presents this category in the mock interview and instead shows it in the report as "a matter you are not required to answer."

### format_facts[]

| Field | Required | Entry criteria |
|---|---|---|
| `id` | Required | `FF` followed by three or more digits. An absence, a format mismatch, or a duplicate is an ERROR |
| `statement` | Required | One fact about the interview format (number of stages, interviewer seniority, online or in person, duration, whether there is a written test or aptitude test, whether a casual meeting is included). An absence or an empty value is an ERROR |

When the recruiting page describes the selection process, record it first as grade A. When a review's description (grade C) conflicts with the recruiting page, list both and show which is newer via `posted_at`. Since the exam type overlaps with `exam_assessment.json` (from `job-change-exam-prep`), record only its presence and stage here, and leave the type inference to that skill.

### themes[]

| Field | Required | Entry criteria |
|---|---|---|
| `id` | Required | `TH` followed by three or more digits. An absence, a format mismatch, or a duplicate is an ERROR |
| `theme` | Required | What interviewers repeatedly try to confirm. An absence or an empty value is an ERROR |
| `likely_probe` | Required | The likely direction of follow-up suggested by the trend. Phrased in the form 「〜と考えられる」 ("... is considered likely"). An absence or an empty value is an ERROR |
| `count_note` | Optional | The number of answers underlying the trend (such as 「回答12件中5件」 (5 of 12 answers)). Written when the count can be read |

A trend is grounded in "the same content appearing across multiple answers." Never build a trend from one answer. When the count is small, state this in `count_note`.

### search_log[]

Records every search run, one entry at a time. Any claim about the scope of the research rests solely on this log.

| Field | Required | Entry criteria |
|---|---|---|
| `query` | Required | The search terms run, or the path of the URL opened. An absence or an empty value is an ERROR |
| `source` | Required | The name of the source fetched from (the site name, or `WebSearch`). An absence or an empty value is an ERROR |
| `url` | Required (nullable) | The URL actually opened. A string not starting with `http` is an ERROR |
| `fetched_at` | Required (nullable) | The fetch date/time (`YYYY-MM-DD`, or ISO 8601 starting with a date). A format mismatch is an ERROR |
| `hit_count` | Required (nullable) | The number of search results or answers. A negative value or a non-integer is an ERROR |
| `adopted_count` | Required (nullable) | The number of items adopted from that query into the three arrays. A negative value or a non-integer is an ERROR |

All four nullable keys must be present (setting the value to `null` explicitly records that it could not be obtained). A search that could not be read because it was redirected to a login screen is still recorded, with `hit_count` set to `null`. This is never interpreted as "no information exists."

## Entry rules

- Keep the span of source text transcribed into `quote` to the minimum needed to identify the question or fact. Never transcribe the entirety of a review's body. The artifact exists for the user's own interview preparation and is never redistributed.
- The older a source, the lower its value as evidence. When a question or fact rests solely on a source whose `posted_at` predates the research date by more than five years, write in `open_questions`: 「古い選考の記録であり、現在の選考と異なりうる」 (a record from an old selection process; may differ from the current one).
- New-graduate-hiring candidate write-ups (such as new-graduate pages on Shukatsu Kaigi or ONE CAREER) are used only for facts of format, such as the number of selection stages or interviewer seniority. They are never evidence for a mid-career-specific question such as one about the reason for changing jobs or drilling into achievements. When used this way, write in `open_questions`: 「新卒選考の記録であり、中途の選考体系と異なりうる」 (a new-graduate record; may differ from the mid-career selection structure).
- A company recruiting page's "desired candidate profile" or "employee interviews" is a grade-A source, but it is the company's own evaluative claim about itself. It can support an inference (`themes`) about what might be probed in an interview, but it never becomes a "question that was asked" (`kind: reported`).
- A review site's "reasons for considering leaving" or "gaps after joining" records employees' views of the company. When building a trend (`themes`) from this content, write `likely_probe` as the direction an interviewer is likely to probe, never as an assertion that the company has a problem.
- Never place the user's own information (name, career history, current employer, salary) in a search term or in the artifact. Research using only the company name, job title, job posting URL, and output path given in the instructions.

## Mechanical validation rules (validate_interview_intel.py)

`scripts/validate_interview_intel.py` performs the mechanical checks. One or more ERRORs is a FAIL (exit code 1); zero ERRORs is a PASS (exit code 0, even with WARNs present).

```
python validate_interview_intel.py <interview_intel.json> [--json]
```

**ERROR (the artifact does not hold together, or a rule is violated)**

- The JSON cannot be parsed, or the root element is a non-object value
- An absence or an empty value in `schema_version`, `company`, or `researched_at`; `researched_at` a format mismatch with `YYYY-MM-DD` or a non-existent date
- `role_title` is neither a string nor null
- Any of `reported_questions`, `format_facts`, or `themes` is a non-array value, or has a non-object element
- An absence, a format mismatch, or a duplicate within the same array in any element's `id`
- `reported_questions[].question` is empty, or `kind` is a value outside the two allowed
- `format_facts[].statement` is empty
- `themes[].theme` or `likely_probe` is empty
- Any element's `source_url` not starting with `http`, `grade` a value outside the four allowed, `quote` empty, or `accessed` a format mismatch or a non-existent date
- An absence, a non-array value, or an empty array in `search_log`; a non-object element in it; `query` or `source` empty
- In a `search_log` element: a missing key for `url`, `fetched_at`, `hit_count`, or `adopted_count`; `url` not starting with `http`; `fetched_at` a format mismatch; `hit_count` or `adopted_count` neither a non-negative integer nor null
- `open_questions` is a non-array value, or contains an element other than a non-empty string
- All three arrays empty and `open_questions` also empty

**WARN (the artifact holds together, but something is short or an inconsistency is noted)**

- `schema_version` is a value outside the known set
- Any of the three arrays is empty
- `grade` is D
- `accessed` is not written, or is null
- `kind` is `reported` but `question` and `quote` do not overlap
- `coverage_notes` is not written

The validation script checks only format and the presence of sources. It never checks whether a question was actually asked, or whether a trend's reading is sound. `category`, `stage`, `posted_at`, `source_name`, and `count_note` are not checked.
