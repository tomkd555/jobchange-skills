# Section: Responsibilities and achievements (achievements)

For each position, deep-dives in the order responsibilities → key projects → achievements, and supports quantifying the achievements. The first pass skips this section; it is done as a section update right before writing the application documents. The `skills` section uses what comes up while discussing this section as its material, so do that section immediately afterward. The section catalogue and the definition of reach stages live in `../sections.md`.

## Fields to fill

| Field | Format |
|---|---|
| `career_history[].responsibilities` | Free text |
| `career_history[].achievements[].description` | Free text |
| `career_history[].achievements[].metric` | Free text (numeric; `null` when it cannot be expressed) |
| `career_history[].achievements[].project` | Free text (only when concurrent projects were run) |
| `career_history[].achievements[].period` | Free text (period; same condition as above) |

`responsibilities` is asked as free text because it is asked at a point when nothing is yet known about that position. Building candidates in advance would mean presenting a task name the interviewer imagined.

## Reach stages

| Stage | Condition |
|---|---|
| `skeleton` | Some career-history entry has `responsibilities` or `achievements` |
| `deep` | Every career-history entry has `responsibilities`, and at least one achievement carries a quantitative `metric` |

## Procedure

For each position, ask in the order responsibilities → key projects → achievements. Ask about achievements situated within the period of employment. For each achievement, ask what changed, at what scale, and how. Support quantification using the patterns in `../quantification-guide.md`. Do not force a number onto an achievement that yields none; make the ingenuity or the recognized point concrete instead, and set `metric` to `null`. Record any figure the user states exactly as given, regardless of its source. Record a range or an estimate the user gives as a range or an estimate, unchanged.

Opening questions:

- What kind of work did you mainly handle at this position (free text)?
- Among that work, which key project stood out? What changed, at what scale, and how?
- (When multiple projects were run concurrently) Which project does this achievement belong to? When did that project run, from and to (`project`, `period`; skip this question when the position involved only one project)?
- Can this achievement be expressed as a number (year-over-year comparison, count, frequency, scale, number of people handled, process-reduction rate, and so on; use the patterns in `../quantification-guide.md` as a guide)? When it cannot, do not force a number; make the ingenuity or the recognized point concrete instead (`metric` set to `null`).

Record a stated figure into `metric` as given. Do not ask where the figure came from. Note the figure's uncertainty only when the user volunteers it themselves.

The wording for the quantification question lives in "Supporting quantification" in `../answer-handling.md`.

For a colloquial or vague phrase (「手伝った」「作った」「いろいろやった」), show a candidate phrasing that would read well in an application document, following the substitution table in `../answer-handling.md`, and record in the elicitation notes, under a `言い換え（本人了承）:` (reworded, user-approved) line, only the sentence the user approved. Do not raise the description of a role's involvement above the scope the user themselves reported.

When a single position involved multiple concurrent projects, ask, for each achievement, for the project's name (`project`) and that project's period (`period`), so that which project produced which result, and when, stays distinguishable. Skip these two questions for a position that involved only one project.

### Update operation

Add to this section whenever a new achievement appears, and review it at least once a quarter. A section that has reached `deep` returns to being a target for additions as more achievements come in ("Update practice" in `../elicitation-guide.md`).

## Downstream

Application documents (`job-change-documents`) use this section as the core of the shokumu-keirekisho. Self-analysis (`job-change-self-analysis`) uses `achievements` as material for behavioral episodes, and matches `metric` exactly.
