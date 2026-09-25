# Canonical specification for interview-preparation artifacts (interview-format)

This is the canonical source defining the field specification, entry criteria, and mechanical validation rules for the interview-preparation artifacts `interview_questions.json`, `interview_answers.json`, and `interview_evaluation.json`. `scripts/validate_interview_artifacts.py` checks them mechanically against this specification.

In company mode, the output path is `{DATA_ROOT}/companies/{company slug}/`. In company-independent fallback mode, there is no company slug, so files are written out only when the user specifies a save location.

`interview_questions.json` and `interview_evaluation.json` are the JSON returned by job-change-interview-coach, saved with every top-level key intact. Never extract and save only the `questions` or `evaluations` array. Dropping `degraded` or `degraded_reason` would make it impossible to tell from the file alone whether a question set is company-specific or a company-independent fallback, which would in turn make it impossible to recheck the pass gate when resuming after an interruption.

The skill's main body writes `interview_answers.json`, appending one question at a time during the mock interview (Step 2).

## degraded and degraded_reason (common to `interview_questions.json` and `interview_evaluation.json`)

```json
{
  "degraded": false,
  "degraded_reason": null
}
```

| Field | Required | Entry criteria |
|---|---|---|
| `degraded` | Required | Boolean. `true` when generated or evaluated without company-specific evidence. A non-boolean value or an absence is an ERROR |
| `degraded_reason` | Required | When `degraded` is `true`, a non-empty string reason (an empty string is an ERROR). When `false`, `null` (anything other than `null` is an ERROR) |

The condition for setting `degraded` to `true` is defined in "Purpose and principles" item 1 of SKILL.md and is not duplicated here.

## interview_questions.json

```json
{
  "degraded": false,
  "degraded_reason": null,
  "questions": [
    {
      "id": "Q001",
      "category": "転職理由",
      "question": "現職を離れようと考えた理由を聞かせてください。",
      "interviewer_intent": "定着性と、転職で解こうとしている課題の一貫性を確認する。",
      "basis": "profile.job_change_axis.reasons[0]",
      "provenance": "general",
      "stage": "一次面接"
    }
  ],
  "notes": []
}
```

### questions (array, required)

An ERROR if not an array. An empty array is a WARN (an artifact with zero expected questions cannot be used in Step 2).

| Field | Required | Entry criteria |
|---|---|---|
| `id` | Required | The question's identifier: `Q` followed by three or more digits (the `Q001` format). An absence, an empty value, or a format mismatch is an ERROR. A duplicate within the same file is an ERROR |
| `category` | Required | The question category. An absence or an empty value is an ERROR. A value outside the known categories is a WARN |
| `question` | Required | The question text presented to the user. An absence or an empty value is an ERROR |
| `interviewer_intent` | Required | The evaluation criterion the interviewer is checking with this question. An absence or an empty value is an ERROR |
| `basis` | Required | The basis: a claim id from company_research, an id from interview_intel (`RQ`, `FF`, or `TH`), the relevant part of `interview_notes_user.md`, or the relevant part of the profile. An absence or an empty value is an ERROR |
| `provenance` | Optional (the coach always attaches it) | The provenance: one of `general` (a common general-purpose question), `reported` (a question reported as having been asked at this company), or `inferred` (a question inferred from company research or review-site trends). An absence is a WARN, and a value other than these three is also a WARN. Never an ERROR, to preserve compatibility with older artifacts |
| `stage` | Optional (the coach always attaches it) | The expected selection stage: one of `カジュアル面談`, `一次面接`, `二次面接`, `最終面接`, or `不明`. An absence is a WARN, and a value other than these five is also a WARN |

`id` is what `interview_answers.json`'s `question_id` and `interview_evaluation.json`'s `question_id` point to. It is the only key linking the three files.

Provenance and the confidence of the underlying evidence are separate things. A `reported` question is often backed by review-site content (grade C), while an `inferred` question may be backed by a securities report (grade A). A `reported` question is a record of the wording as it was actually asked; an `inferred` question is a guess with no guarantee of being asked. In the mock interview, `reported` questions are presented first, and `inferred` questions are presented marked as inferences.

The known question categories are `自己紹介`, `転職理由`, `志望動機`, `自己PR`, `実績深掘り`, `弱み`, `失敗・挫折`, `マネジメント`, `協働・対立`, `キャリアプラン`, `入社後の貢献`, `カルチャーフィット`, `条件確認`, `空白期間・短期離職`, `逆質問`, `カジュアル面談`, `ビヘイビアラル`, `ケース`. This list is the canonical vocabulary. `validate_interview_artifacts.py`'s set of known categories matches this list exactly. The meaning of each category, and its correspondence to `question-bank.md`'s question categories, live in that file's "Correspondence between question categories and job-change-interview-coach's categories" section (the two foreign-affiliated categories live in `foreign-interviews.md`). A value outside the known set is a WARN, because the artifact still holds together even as categories are added. A report interview_intel.json classifies as `配慮事項` is never placed in `questions[]`; it is listed in `notes` instead.

### notes (array, optional)

An array of matters to convey to the user alongside the expected questions. It is an array of strings; a non-array value is an ERROR. It records the following.

- Matters the user is not required to answer (if interview_intel.json reports anything classified as `配慮事項`, that fact).
- Premises about the selection stage (the number of stages and the interviewers, read from `format_facts`).
- If any question rests on a stale source or a new-graduate-hiring record, that fact.

## interview_answers.json

```json
{
  "answers": [
    {
      "question_id": "Q001",
      "answer": "基盤の設計から運用までを一貫して担いたいと考えたためです。",
      "answered_at": "2026-08-15"
    }
  ]
}
```

During the mock interview (Step 2), one entry is appended each time an answer is received. If the interview is interrupted partway through, the set obtained by subtracting this file's `answers[].question_id` values from `interview_questions.json`'s `questions[].id` values is the "remaining questions." Resumption is determined solely by this difference.

### answers (array, required)

An ERROR if not an array. An empty array is a WARN (saving a stage where zero questions have been answered is allowed).

| Field | Required | Entry criteria |
|---|---|---|
| `question_id` | Required | The same value as one of `interview_questions.json`'s `questions[].id`. An absence, an empty value, or a format mismatch is an ERROR. A duplicate is an ERROR |
| `answer` | Required | The user's answer, transcribed verbatim. Never summarized, rephrased, or corrected. An absence or an empty value is an ERROR |
| `answered_at` | Required | The date the answer was given (`YYYY-MM-DD`). An absence or a format mismatch is an ERROR |

## interview_evaluation.json

```json
{
  "degraded": false,
  "degraded_reason": null,
  "evaluations": [
    {
      "question_id": "Q001",
      "scores": {
        "star": "一部",
        "specificity": "充足",
        "consistency": "充足",
        "company_fit": "一部"
      },
      "feedback": "profile.job_change_axis.reasons[0] と矛盾なく述べている。状況の説明が薄い。",
      "improvement": "claim-012 の開発体制へ触れ、STAR の状況（Situation）を1文足す。"
    }
  ]
}
```

### evaluations (array, required)

An ERROR if not an array. An empty array is a WARN.

| Field | Required | Entry criteria |
|---|---|---|
| `question_id` | Required | The `id` of the question being evaluated. An absence, an empty value, or a format mismatch is an ERROR. A duplicate is an ERROR |
| `scores` | Required | The judgment on the four criteria. A non-object value is an ERROR. Details in the next section |
| `feedback` | Required | The explanation of the evaluation. Includes an evidence reference (the relevant part of the profile, self_analysis.json's `career_narrative` or `reason_for_change`, or a claim id). An absence or an empty value is an ERROR |
| `improvement` | Required | The improvement suggestion. Also includes an evidence reference. An absence or an empty value is an ERROR |

### scores (object, required)

| Key | Criterion | Value |
|---|---|---|
| `star` | STAR | `充足` (met) / `一部` (partial) / `不足` (not met) |
| `specificity` | Specificity | `充足` / `一部` / `不足` |
| `consistency` | Consistency | `充足` / `一部` / `不足` |
| `company_fit` | Company understanding | `充足` / `一部` / `不足`. When `degraded` is `true`, `対象外` (excluded from evaluation) or an absence |

If `star`, `specificity`, or `consistency` is not one of the three values, it is an ERROR.

`company_fit` must be consistent with `degraded`. When `degraded` is `true` (fallback mode), company understanding cannot be evaluated, so the value must be either `対象外` or absent; entering one of the three-level values is an ERROR. When `degraded` is `false`, one of the three values is required, and `対象外` is an ERROR. This distinguishes an artifact that read company_research.json but omitted the evaluation from an artifact produced under fallback.

The canonical judging anchors for each level live in `evaluation-rubric.md` and are not duplicated here. The validation script checks only that a value falls within the vocabulary.

## Mechanical validation rules (validate_interview_artifacts.py)

`scripts/validate_interview_artifacts.py` performs the mechanical checks. One or more ERRORs is a FAIL (exit code 1); zero ERRORs is a PASS (exit code 0, even with WARNs present).

```
python validate_interview_artifacts.py <artifact.json> [--json] [--questions <interview_questions.json>]
```

The kind of artifact being checked is determined from its top-level keys. Having exactly one of `questions`, `answers`, or `evaluations` determines the kind; having none of them, or having two or more, is an ERROR. Because the three files use mutually exclusive keys, there is no need to specify the kind as an argument.

Passing the path to `interview_questions.json` in `--questions` checks that every `question_id` in `interview_answers.json` or `interview_evaluation.json` exists on the question side. A `question_id` that does not exist is an ERROR. In fallback mode, a questions file may not be written at all, so `--questions` is optional; when it is not passed, the cross-reference is not checked.
