# Canonical specification for exam_assessment.json (exam-assessment-format)

This is the canonical definition of the field specification, entry criteria, and mechanical validation rules for `exam_assessment.json`, the investigation result on assessment type. The selection-exam investigator agent (job-change-exam-scout) builds the deliverable to this specification. `scripts/validate_exam_assessment.py` checks it mechanically against this specification.

The output destination is `{DATA_ROOT}/companies/{company slug}/exam_assessment.json`. For a generic preparation request where no company can be identified, `_general/` is used in place of a company slug.

## Overall structure

```json
{
  "company": "架空クラウドワークス株式会社",
  "assessments": [
    {
      "type": "SPI3",
      "stage": "書類選考通過後・一次面接前",
      "evidence": [
        {
          "source_url": "https://example.com/careers/process",
          "grade": "A",
          "quote": "書類選考の通過者には、一次面接の前に SPI3（テストセンター）の受検を案内します。"
        }
      ],
      "confidence": "確定",
      "format_notes": "テストセンター方式。言語・非言語の能力検査と性格検査で構成される。",
      "prep_recommendations": ["非言語の頻出分野を反復練習する", "テストセンター方式の操作に慣れておく"]
    }
  ],
  "open_questions": ["性格検査の実施が同一日程かどうかは確認できていない。"]
}
```

A fully filled-in example (fictional data) is at `assets/exam_assessment_example.json`.

## Field specification

### company (string, required)

The name of the company under investigation (official name). Missing or empty is an ERROR.

### assessments (array, required)

The array of identified assessment types. Not being an array is an ERROR. An empty array is a WARN (it is recommended to record, in `open_questions`, why no type could be identified). If `assessments` is empty and `open_questions` is also empty, this is an ERROR, because the deliverable states nothing at all.

### assessments[].type (string, required)

The name of the assessment. Missing or empty is an ERROR. The canonical definition of this vocabulary is `references/assessment-catalog.md`; it is not duplicated here. An assessment name not covered by the catalog stays at WARN, because a company may use an assessment the catalog does not cover.

### assessments[].stage (string, required)

The stage in the selection process at which the assessment is administered (e.g., 「書類選考の通過後」, 「一次面接前」). Missing or empty is a WARN: the deliverable still stands even when the stage is unknown.

### assessments[].evidence (array, required)

The evidence used to identify this type. Not being an array is an ERROR. An empty array is an ERROR (this prohibits asserting a claim with no source URL). Each element carries the following.

| Field | Required | Entry criteria |
|---|---|---|
| `source_url` | Required | The URL of the source page. Must be a string starting with `http` (missing or non-matching is an ERROR) |
| `grade` | Required | One of the evidence levels `A` / `B` / `C` / `D`. Any other value, or missing, is an ERROR |
| `quote` | Required | A quotation from the source page. Missing or empty is an ERROR |

The canonical definition and assignment rules for `grade` are in `job-change-company-research/references/evidence-grading.md`. How this is applied in the context of selection exams is written in the role prompt `references/roles/exam-scout.md`.

### assessments[].confidence (string, required)

The confidence for this type. Must be one of the following two values. Missing, empty, or any value other than these two is an ERROR.

| Value | Meaning |
|---|---|
| `確定` (confirmed) | The type is explicitly stated by a level-A source, such as a careers page or an official company selection notice |
| `推定` (estimate) | Inferred from a source below level A, such as a candidate write-up |

`確定` (confirmed) requires that `evidence` contain at least one element with `grade` equal to `A`. If it does not, this is an ERROR (this mechanically prevents setting `確定` (confirmed) on the basis of a single piece of hearsay alone).

When `confidence` is `推定` (estimate) and `evidence` has only one element, this is a WARN, because the type is backed by only a single write-up, and this limitation needs to be made explicit in the preparation plan.

### assessments[].format_notes (string, required)

A summary of the question format (subject composition, time, administration-method characteristics). Missing or empty is a WARN.

### assessments[].prep_recommendations (array, required)

The general direction of recommended preparation. Must be an array of non-empty strings. Not being an array, or containing an element that is not a non-empty string, is an ERROR. An empty array is a WARN.

### open_questions (array, required)

Records points that could not be verified, points to confirm once the exam invitation arrives, and so on. When the claims passed in the instructions conflict with the investigation results, both claims and the reason for the choice are also recorded here. Not being an array, or containing an element that is not a non-empty string, is an ERROR.

## Mechanical validation rules (validate_exam_assessment.py)

`scripts/validate_exam_assessment.py` performs the mechanical check. One or more ERRORs means FAIL (exit code 1); zero ERRORs means PASS (exit code 0, even with WARNs present).

```
python validate_exam_assessment.py <exam_assessment.json> [--json]
```

**ERROR (the deliverable does not stand, or a rule is violated)**

- Cannot be parsed as JSON, or the root element is not an object
- `company` is missing or empty
- `assessments` is not an array
- `assessments` is empty and `open_questions` is also empty
- `type` is missing or empty
- `evidence` is not an array, or is an empty array
- `source_url` is missing, or does not start with `http`
- `grade` is not one of `A` / `B` / `C` / `D`
- `quote` is missing or empty
- `confidence` is not one of `確定` / `推定`
- `confidence` is `確定` but `evidence` has no level-A element
- `prep_recommendations` or `open_questions` is not an array, or contains a non-empty-string element

**WARN (the deliverable stands, but there is a shortfall or a confidence-related note)**

- `assessments` is an empty array
- `type` is not a name covered by `assessment-catalog.md`
- `stage` is missing or empty
- `confidence` is `推定` and `evidence` has only one element
- `format_notes` is missing or empty
- `prep_recommendations` is an empty array

## Scope beyond mechanical checking

The following cannot be judged mechanically and require human judgment.

- Whether the source's content genuinely describes that assessment type (the correspondence between `quote` and `type`).
- Whether the assignment of the evidence level itself is appropriate (whether a review has been upgraded to A, or a careers page downgraded to C).
- Which side to adopt when multiple sources conflict.
- Where to draw the line on how far a `推定` (estimate) type may be relied on in the preparation plan.
