# Re-investigation deadline policy (freshness-policy)

The canonical reference defining the policy for judging whether a per-company deliverable needs re-investigation (fresh, stale, or missing). The judgment is grounded in `companies/{company slug}/_manifest.json`, whose specification and TTL table also live here. The tool that performs the judgment is `scripts/check_freshness.py`.

## Policy

- `companies/{company slug}/` is a storage location that keeps everything without deleting it; a deliverable file is never deleted or moved even after its TTL has elapsed.
- A TTL that has elapsed gives the hub (job-change-support) grounds to instruct `job-change-company-research` to "investigate only the topics judged stale." A topic that is not stale, and a deliverable that is fresh, is never re-investigated. The existing deliverable is reused as is.
- The skill that creates each deliverable writes `_manifest.json` itself. `job-change-company-research` updates the `job_posting` field when it obtains the job posting, and updates the `company_research` field when it finishes investigating a topic. `check_freshness.py` only judges; it never rewrites `_manifest.json`.

## `_manifest.json` specification

```json
{
  "schema_version": 1,
  "artifacts": {
    "job_posting": {
      "updated_at": "2026-07-01",
      "source_url": "https://example.com/jobs/123"
    },
    "company_research": {
      "updated_at": "2026-07-10",
      "audit_verdict": "CLEAN",
      "audited_at": "2026-07-10",
      "topics": {
        "philosophy": {"last_researched": "2026-06-01"},
        "workstyle": {"last_researched": "2026-07-10"}
      }
    }
  }
}
```

| Field | Type | Meaning |
|---|---|---|
| `schema_version` | number | The specification version. Currently `1` |
| `artifacts` | object | An object keyed by deliverable name |
| `artifacts.job_posting` | object \| null | The state of obtaining the job posting. Holds `updated_at` (`YYYY-MM-DD`) and `source_url`. `source_url` holds a value only when the posting was ingested from a URL; it is `null` when built from body text, a file, or dialogue. `null` when not yet obtained |
| `artifacts.company_research` | object \| null | The state of carrying out company research. Holds `updated_at` (the last update date), a `topics` object keyed by topic name whose value holds `last_researched` (`YYYY-MM-DD`), and `audit_verdict` and `audited_at`. `null` when not yet carried out |
| `artifacts.company_research.audit_verdict` | string | The independent audit's verdict. One of `CLEAN`, `CONCERNS`, or `BLOCK`. `job-change-company-research` writes it |
| `artifacts.company_research.audited_at` | string | The date the audit was carried out (`YYYY-MM-DD`) |

`artifacts` may freely add a deliverable such as `exam_assessment` in the form `{updated_at: "YYYY-MM-DD"}`, beyond the two above. Only a deliverable name and a date may be recorded; personal information and any value derived from it are never written (canonical definition: `pii-boundary.md`). `check_freshness.py` always judges the two deliverables `job_posting` and `company_research`.

Beyond these, the following optional deliverable is judged only when `artifacts` holds a record for it. When there is no record, and when the value is explicitly `null` (stating it has not been obtained), it is never treated as `missing` and never appears in the judgment result. When a record exists but `updated_at` is missing or invalid, or the value is of an invalid type, it is treated as `missing`. Any key other than the ones above is skipped without judgment.

| Optional deliverable | Writer | TTL (days) |
|---|---|---|
| `interview_intel` | `job-change-interview-prep` (writes `{updated_at: "YYYY-MM-DD"}` when Step 0.9's job-interview information investigation finishes) | 180 |

When an optional deliverable is judged `stale` or `missing`, the hub hands the re-investigation to the skill that writes that deliverable (the Writer column above).

## Topic names and the TTL table

The keys of `company_research.topics` match the eight topic names defined by the `job-change-company-research` skill's `references/company-research-format.md`. The TTL (in days) is decided by the nature of the topic. Topics fall into three groups by nature: news and reporting; compensation, benefits, and work style; and philosophy and business. The table below gives the assignment for each topic.

| topic | Category | TTL (days) |
|---|---|---|
| `philosophy` | Philosophy/business | 365 |
| `business` | Philosophy/business | 365 |
| `financials` | Compensation/benefits/work style | 180 |
| `compensation` | Compensation/benefits/work style | 180 |
| `benefits` | Compensation/benefits/work style | 180 |
| `workstyle` | Compensation/benefits/work style | 180 |
| `reputation` | News/reporting | 90 |
| `selection_process` | Default | 180 |

For a topic name in `company_research.topics` that is not in the table above, apply the default TTL (180 days). `job_posting`'s TTL is a separate bracket from `topics`, set at 30 days.

## Judgment rules

The reference date for the judgment is the date given to `--today`, or the date at execution time when it is omitted. `check_freshness.py` computes the number of days elapsed between this reference date and each deliverable's last update date, and returns `fresh` when the elapsed days are within the TTL, `stale` when they exceed it. Exactly the TTL counts as `fresh`.

- `job_posting`: when `artifacts.job_posting` is absent or `null`, or `updated_at` is missing or in an invalid date format, it is `missing`. Otherwise it is judged from `updated_at` with a TTL of 30 days.
- `company_research`: when `artifacts.company_research` is absent or `null`, the whole `company_research` is `missing`, with no per-topic judgment. When it exists, check the presence and format of `last_researched` for each topic under `topics`. A topic that is missing or invalid is `missing`; otherwise it is judged `fresh`/`stale` with the table's TTL. When `topics` is absent, `null`, or of an invalid type, the whole `company_research` is `missing`, with no per-topic judgment. When `topics` is an empty object, it is treated as having no topics at all and is excluded from the judgment.
- When `_manifest.json` does not exist, or cannot be loaded as JSON, both `job_posting` and `company_research` are reported as `missing`. The exit code stays 0. This tool's role is to report whether re-investigation is needed, so a missing manifest still exits with 0.
