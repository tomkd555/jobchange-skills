# The canonical definition of the personal information boundary (pii-boundary)

This is the canonical definition of the boundary that keeps the user's personal information from reaching a role that has a means of sending data to the web. The hub and every sub-skill refer to this file.

| Referrer | What it is used for |
|---|---|
| `job-change-support` | Routing and what the hub passes to a sub-skill |
| `job-change-job-search` | What the anonymised condition sheet may hold; what the searcher agent may read |
| `job-change-posting-check` | What the researcher agent may receive; where the match record is written |
| `job-change-decision` | Confirms that the comparison runs in the main session with no agent |

The enumeration of targets, the exceptions and the permission for each role live here alone. The role prompts (`agents/*.md` and `skills/*/references/roles/*.md`) repeat the substance of the principle verbatim, because a role prompt travels alone to a sub-agent that may not open this file. When this file changes, update both role prompts in the same change.

## Boundary principle

Treat the following as personal information, and never use any of it for external transmission of any kind, including search queries, fetches and external API calls.

### What the skills never record

The name of the user's current employer and the user's current salary are never asked for and never written to any file. No role, with or without web tools, holds them.

### Files under career-private/

Everything under `{DATA_ROOT}/career-private/` is personal information, both its path and its content.

| File | Why it is personal information |
|---|---|
| `wishes.json` | The user's conditions and work values, their history and the decisions they fed |
| `company_index.json` | The list of companies the user considers reveals the user's preferences |
| `matches/{posting id}.json` | Which conditions a posting meets, fails or leaves unknown for this user |
| `decisions/{decision id}.json` | The candidates compared, the weights, the chosen option and the follow-up |
| Older files from version 1.x (`profile.json`, `axis.json`, `profile_interview_notes.md`, `documents/`) | The career record and the interview notes; left in place, never read by this version |

A derived value stays inside the boundary of its source. A match result is derived from the conditions and is personal information even though the posting check it was derived from is not.

### Files outside career-private/

`companies/{company slug}/postings/{posting id}/posting-check.json` and `job-search/{search id}/job_search_results.json` hold facts about postings and companies. The roles with web tools write there and read there. Two fields in the search result are written by the main session and are about the user: `must_match` (the match against the required conditions, which the searcher also writes from the anonymised sheet) and `considering` (the user's mark). Both are allowed outside `career-private/` because the anonymised sheet is the one exception below, and a mark on a posting identifies nobody.

## The exception: the anonymised condition sheet

The job search passes the searcher agent an anonymised copy of the active conditions, one element per condition with `condition_id`, `kind`, `text` and `level`. The sheet may hold:

- the occupation, the industry, the employment type
- the work location at the level of a prefecture or municipality, plus any rail line or station the user wrote in their own words
- the remote arrangement
- the floor of the desired salary
- for `similar_better`, the baseline posting's published values (these come from a posting check, which holds no personal information)
- the text of a work value or free condition, as the user wrote it

The sheet never holds: the current salary, the current employer, the user's name, the `how_to_judge` sentences, the `history`, the `used_in` list, or the path of `wishes.json`. This range of information alone cannot identify the individual. `job-change-job-search` is the one skill that uses this exception.

The posting researcher receives no part of the sheet. It receives the company name as the posting spells it and the posting URL or text, which are public.

## Permission by role

Whether a role may read under `career-private/` is decided by whether that role has a means of sending data to the web (WebSearch, WebFetch). Each role's `tools` is fixed in the frontmatter of `agents/*.md`.

| Role | Means of sending data to the web | Reading under `career-private/` |
|---|---|---|
| `job-change-job-searcher` | Yes (WebSearch, WebFetch) | Never. Does not open a file there even when given the path. Reads no other search's directory and never the main session's `partial-chrome` file |
| `job-change-posting-researcher` | Yes (WebSearch, WebFetch) | Never. Does not open a file there even when given the path. Reads no `job-search/` file and no other posting's directory |
| The main session (`job-change-decision`, and the matching step of `job-change-posting-check`) | Holds web tools but uses none while doing this work | May read and write |

Adding one web tool to a role is enough to make that role unable to receive personal information. When a role's `tools` changes, update this table and the role prompt in the same change.

The main session reads pages in the user's Chrome (しょくばらぼ, Indeed, Green, pages WebFetch cannot open). It does so with the company name or the search conditions only; it never types a personal detail into a web form while doing so.

On a harness that cannot launch a sub-agent (Codex), the main body reads the role prompt and takes on the role itself. While it works as a role with web tools, it does not open `career-private/`; while it works as the main session, it does not use web search or fetch on personal information.

## What a machine can check

No mechanical lint for leaked personal information remains in this version: the two items it used to detect (the current employer's name and the current salary) are no longer recorded anywhere, so there is nothing to extract them from. The protection rests on what is passed before any material leaves the main session. A validator PASS is no evidence that the boundary was honoured.
