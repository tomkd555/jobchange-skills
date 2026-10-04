# self_analysis.json specification

This is the canonical definition, in the job-change-self-analysis skill, of self_analysis.json, the deliverable of self-analysis. `scripts/validate_self_analysis.py` follows this specification exactly.

self_analysis.json is a deliverable that builds on profile.json (the canonical definition of the career facts, owned by `job-change-profile`) and on the job-change axis (`{AXIS}`, owned by `job-change-axis`). It deepens strengths and the career axis by grounding them in behavioural evidence and the perspective of others. Job interview preparation (job-change-interview-prep) and the deepening of the statement of motivation (job-change-documents) read it as input. The schema of neither file is changed. The result of self-analysis reflects only values: profile.json's `strengths` (a short sentence, through a `job-change-profile` update) and the axis's `job_change_axis.reasons` (wording based on constructive_version, through a `job-change-axis` section update).

## Placement

- The canonical file is placed at `{DATA_ROOT}/career-private/self_analysis.json` (a private directory).
- A path under career-private/ is never passed to an agent holding a means of sending to the web (WebSearch, WebFetch). This skill's writer and auditor do not have such a means, so it may be passed to them.
- User data is never placed inside the skill's own folder. `assets/self_analysis_example.json` is a worked example, and does not contain real data.

## Root structure

```json
{
  "schema_version": "1.1",
  "updated_at": "2026-07-16",
  "behavioral_episodes": [ ],
  "others_feedback": [ ],
  "interests": { },
  "values": [ ],
  "career_adaptability": { },
  "personality": { },
  "strengths": [ ],
  "career_narrative": { },
  "reason_for_change": { },
  "notes": ""
}
```

| Field | Type | Required/Optional | Meaning and entry criteria |
|---|---|---|---|
| `schema_version` | string | Required | The specification's version. The current one is `"1.1"`. `"1.0"` can also be read. A missing or empty value is an ERROR. A value other than these two known ones is a WARN |
| `updated_at` | string | Optional | The date last updated, in `YYYY-MM-DD` form. A missing value is a WARN |
| `behavioral_episodes` | array | Required | An array of behavioural episodes (STAR material). At least one entry is required. Described below |
| `others_feedback` | array | Optional | An array of feedback received from others. Zero entries is a WARN. Described below |
| `interests` | object | Optional | Interests. An empty value is a WARN. Described below |
| `values` | array | Optional | An array of values. An empty array is a WARN. Described below |
| `career_adaptability` | object | Optional | The four dimensions of career adaptability. Described below |
| `personality` | object or null | Optional (1.1) | The self-report of personality and behavioural tendencies, and its description. `null` is treated as not yet filled in. Described below. The canonical definition is in `references/personality-guide.md` |
| `strengths` | array | Optional | An array of grounded strengths. Described below |
| `career_narrative` | object | Required | The career narrative. Described below |
| `reason_for_change` | object | Required | The reason for leaving and for changing jobs. Described below |
| `notes` | string | Optional | A supplementary note |

## behavioral_episodes

An array of behavioural episodes (STAR material). At least one entry is required. Strengths, values, and career adaptability are all grounded by mapping to this array.

| Field | Type | Required/Optional | Meaning and entry criteria |
|---|---|---|---|
| `id` | string | Required | The episode's identifier (such as `ep-1`). It becomes the reference target of other fields |
| `period` | string | Optional | The period, in `YYYY-MM〜YYYY-MM` form |
| `situation` | string | Required | The situation. A missing or empty value is an ERROR |
| `task` | string | Optional | The task or role taken on |
| `action` | string | Required | The action actually taken. A missing or empty value is an ERROR |
| `result` | string | Required | The result. A missing or empty value is an ERROR |
| `metric` | string or null | Optional | A quantitative value (such as 「応答時間を62%短縮」). `null` when it cannot be quantified |
| `reproducibility` | string or null | Optional | The grounds for the approach working even when the environment changes (reproducibility). An employer judges whether a behavioural process reproduces, so this is written wherever possible |
| `emotion_note` | string or null | Optional | A record of the motivation and feeling at the time. Never write a forecast of a future feeling |

- `metric` is filled with a quantitative value wherever possible. When no episode across the whole array has a `metric`, the validation script reports a WARN.
- `situation`, `action`, and `result` form the skeleton of an episode; when one of them is missing, the episode does not stand, so this is an ERROR.

## others_feedback

An array of feedback received from others. Zero entries is a WARN (collecting the perspective of others is recommended).

| Field | Type | Required/Optional | Meaning and entry criteria |
|---|---|---|---|
| `id` | string | Required | The feedback's identifier (such as `fb-1`). It becomes a reference target for strengths |
| `source_type` | string | Optional | The source: one of `上司` (manager), `同僚` (colleague), `部下` (subordinate), `顧客` (client), `友人・家族` (friend or family), or `評価面談` (performance review) |
| `content` | string | Optional | The content received. Record it as a mapping between an action and a result |
| `context` | string | Optional | When and in what situation it was received |
| `linked_episode_ids` | array | Optional | An array of the IDs of related behavioral_episodes |

- Feedback is taken in with a task-oriented focus.

## interests

Interests. An empty value (both `domains` and `concrete_topics` empty) is a WARN.

| Field | Type | Meaning and entry criteria |
|---|---|---|
| `domains` | array | An array of interest-domain strings. The six RIASEC domain names (Realistic, Investigative, Artistic, Social, Enterprising, Conventional) are used as axis names |
| `concrete_topics` | array | An array of concrete interest strings |

## values

An array of values. An empty array is a WARN. Each element represents one value.

| Field | Type | Meaning and entry criteria |
|---|---|---|
| `value` | string | A description of the value |
| `evidence_episode_ids` | array | An array of the IDs of the supporting behavioral_episodes. To avoid resting weight on introspection alone, map it to an episode wherever possible |

## career_adaptability

The four dimensions of career adaptability. Only the framework of dimension names is used, and no scale item text is reproduced. Each dimension has the same structure.

| Dimension | Meaning |
|---|---|
| `concern` | Concern (interest in and preparation for the future career) |
| `control` | Control (directing one's career by one's own choice) |
| `curiosity` | Curiosity (exploring possibilities) |
| `confidence` | Confidence (self-efficacy for getting through a challenge) |

Each dimension's object contains the following fields.

| Field | Type | Meaning and entry criteria |
|---|---|---|
| `self_note` | string | A self-description for that dimension |
| `evidence_episode_ids` | array | An array of the IDs of the supporting behavioral_episodes |

## personality (1.1)

Holds the self-report of personality and behavioural tendencies, and its description. It is optional, and the deliverable stands without it. A self-report is a record of the person's own self-image, and does not show the trait itself, so it never counts as grounds for `strengths`. The canonical definition of how to ask, the vocabulary, and how to write is in `references/personality-guide.md`.

```json
"personality": {
  "markers": [
    {
      "id": "pm-1",
      "construct": "planning_style",
      "options": ["事前に段取りを固めてから着手する", "着手してから状況に合わせて組み替える", "場面による", "どちらも当てはまらない"],
      "response": "事前に段取りを固めてから着手する",
      "linked_episode_ids": ["ep-1"],
      "feedback_ids": ["fb-1"],
      "note": null
    }
  ],
  "presentation": "計測してから手を打ち、段取りを先に固める行動が ep-1 と ep-2 で繰り返し見られる。"
}
```

| Field | Type | Required/Optional | Meaning and entry criteria |
|---|---|---|---|
| `markers` | array | Required | An array of self-reports. Zero entries is allowed. Described below |
| `presentation` | string or null | Optional | A descriptive passage that checks the self-report against the evidence. Never sorted by the name of a type or category. Written in the past tense, mapped to an episode |

### markers

Each element represents one self-report.

| Field | Type | Required/Optional | Meaning and entry criteria |
|---|---|---|---|
| `id` | string | Required | The identifier (such as `pm-1`). A missing or empty value is an ERROR. A duplicate is a WARN |
| `construct` | string | Required | The construct's identifier. One of the identifiers in the "Construct vocabulary" table in `references/personality-guide.md`. Any other value is an ERROR |
| `options` | array | Optional | An array of strings recording the presented options as they stand (2-4 entries; a forced-choice question has 4, holding the full wording of every presented option). When present, `response` must be one of these (a mismatch is an ERROR). When Other is chosen and replaced with free text, `options` is omitted |
| `response` | string | Required | The sentence of the option the person chose. A missing or empty value is an ERROR |
| `linked_episode_ids` | array | Optional | An array of the IDs of the behavioral_episodes where that tendency showed up. An ID that does not exist is an ERROR |
| `feedback_ids` | array | Optional | An array of the IDs of the others_feedback about the same tendency. An ID that does not exist is an ERROR |
| `note` | string or null | Optional | A supplementary note, such as a disagreement between the self-report and feedback from others |

- When a self-report has both `linked_episode_ids` and `feedback_ids` empty, the validation script reports a WARN (a record grounded in the self-report alone). The deliverable still stands.
- When `presentation` contains the name of a type or category (such as 「〜型です」「〜タイプです」「〜型である」), this is a WARN.

## strengths

An array of grounded strengths. **A strength grounded in introspection alone is never accepted.** Each element maps to at least one of behavioural evidence (`episode_ids`) or feedback from others (`feedback_ids`).

| Field | Type | Required/Optional | Meaning and entry criteria |
|---|---|---|---|
| `statement` | string | Required | A short sentence stating the strength. A missing or empty value is an ERROR. It becomes the material for the short sentence reflected into profile.json's `strengths` |
| `episode_ids` | array | Conditionally required | An array of the IDs of the supporting behavioral_episodes |
| `feedback_ids` | array | Conditionally required | An array of the IDs of the supporting others_feedback |
| `constructs` | array | Optional (1.1) | An array of the identifiers of the constructs involved in that strength. The vocabulary is the same as `personality.markers[].construct`. An identifier absent from the table is an ERROR |

- When both `episode_ids` and `feedback_ids` are empty (no valid ID at all), this is an ERROR (a strength grounded in introspection alone). At least one of them must contain at least one existing ID.
- An ID referenced by `episode_ids` or `feedback_ids` must be an ID that exists in behavioral_episodes / others_feedback (referential integrity). A reference to an ID that does not exist is an ERROR.
- For a construct named in `constructs`, when the matching self-report in `personality.markers` maps to neither an episode nor feedback from others, this is a WARN (it checks whether a self-report is being used as grounds for a strength).

## career_narrative

The career narrative. It follows the framework of the Career Construction Interview (CCI): life theme, turning points, consistent motivation. See narrative-guide.md.

| Field | Type | Required/Optional | Meaning and entry criteria |
|---|---|---|---|
| `life_theme` | string | Required | The life theme. A missing or empty value is an ERROR |
| `turning_points` | array | Optional | An array of turning-point strings |
| `consistent_motivation` | string | Required | The consistent motivation. A missing or empty value is an ERROR |
| `future_direction` | string | Optional | The future direction |

## reason_for_change

The reason for leaving and for changing jobs. It converts a list of complaints into a constructive reframing built around the value the person wants to bring to bear. See narrative-guide.md.

| Field | Type | Required/Optional | Meaning and entry criteria |
|---|---|---|---|
| `raw_reasons` | array | Required | An array of the original reasons (unprocessed reasons, including complaints). At least one entry is required (an empty array is an ERROR) |
| `constructive_version` | string | Required | An explanation built around the value the person wants to bring to bear. A missing or empty value is an ERROR |
| `consistency_note` | string | Optional | An explanation of consistency with the axis's `job_change_axis.reasons` (in `{AXIS}`). Omitted when no `{AXIS}` exists |

- When `constructive_version` remains an identical string to one of the `raw_reasons`, this is a WARN (the constructive reframing has not been done).

## Summary of the validation rules

`validate_self_analysis.py` checks the following. Even one ERROR makes it FAIL (exit code 1); zero ERRORs makes it PASS (exit code 0; a WARN is allowed). Reading supports UTF-8 with a BOM (`utf-8-sig`).

### ERROR (the deliverable does not stand)

- Cannot be read as JSON
- `schema_version` is missing or empty
- `behavioral_episodes` is empty, or an element has `id`, `situation`, `action`, or `result` missing or empty
- An element of `others_feedback` has `id` missing or empty
- An element of `strengths` has `statement` missing or empty
- An element of `strengths` has both `episode_ids` and `feedback_ids` empty (a strength grounded in introspection alone)
- An `episode_id` / `feedback_id` referenced by `strengths`, `values`, `career_adaptability`, or `personality.markers` does not exist (a referential-integrity error)
- `personality` has a type other than object, `personality.markers` has a type other than array, or one of its elements has a type other than object
- An element of `personality.markers` has `id` or `response` missing or empty, `construct` absent from the vocabulary table, or `options` present while `response` is not among them
- An element of `personality.markers` has `options` present, but not as an array of 2-4 non-empty strings
- `personality.presentation` is neither a string nor null
- `strengths[].constructs` has a type other than array, or contains an identifier absent from the vocabulary table
- `career_narrative.life_theme` or `consistent_motivation` is missing or empty
- `reason_for_change.raw_reasons` is empty, or `constructive_version` is missing or empty

### WARN (the deliverable stands, but a lack of information lowers its quality)

- `others_feedback` has zero entries (the perspective of others is missing)
- An `id` is duplicated within `behavioral_episodes`, `others_feedback`, or `personality.markers`
- An element of `others_feedback` has a `source_type` outside the value domain in the table above
- No episode across the whole array has a `metric`
- `updated_at` is missing
- `schema_version` is other than the two known values (`1.0`, `1.1`)
- `interests` is empty (`domains` and `concrete_topics` both empty)
- `values` is empty
- An element of `personality.markers` has both `linked_episode_ids` and `feedback_ids` empty (a record grounded in the self-report alone)
- `personality.presentation` contains the name of a type or category
- A self-report for a construct named in `strengths[].constructs` maps to neither an episode nor feedback from others
- `constructive_version` remains an identical string to `raw_reasons`
