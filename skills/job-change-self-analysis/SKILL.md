---
name: job-change-self-analysis
description: >-
  Sub-skill for self-analysis in a job change. Building on profile.json, it collects behavioural
  episodes (STAR material) and feedback from others as required elements on equal footing with
  introspection, structures them along interests, values, the four dimensions of career adaptability,
  and four axes of past behaviour, and produces a self_analysis.json holding three elements: grounded
  strengths, a career narrative, and a constructive reframing of the reason for leaving. It makes a
  deliverable that job interview preparation (job-change-interview-prep) and the deepening of statements
  of motivation (job-change-documents) can read. A strength must map to behavioural evidence or feedback
  from others; weight is never placed on introspection alone. Questions are limited to a fixed set of structured
  questions to prevent rumination, diagnostic results are never treated as a final verdict, facts are
  never fabricated or exaggerated, and metric values match exactly. A dedicated agent handles writing,
  and a separate dedicated agent handles independent auditing (job-change-self-analysis-writer /
  job-change-self-analysis-auditor). It runs when routed from job-change-support (the hub).
  Use when the user does self-analysis for a job change in Japan — organizing strengths, taking stock of
  their career, deepening their reasons for changing jobs, or building a consistent career narrative for
  interviews and statements of motivation.
  trigger words: 自己分析, 強みの整理, キャリアの棚卸し, 転職の軸を深めたい, 自己PRの根拠, キャリア・ナラティブ,
  他己分析, モチベーショングラフ, 退職理由の言語化。
allowed-tools: Read, Write, Glob, Grep, Bash, AskUserQuestion, Agent, Skill
---

# job-change-self-analysis

When working on self-analysis for a job change, this single skill covers every step from taking stock to delivering the finished output. Building on profile.json, it collects behavioural episodes (STAR material) and feedback from others on equal footing with introspection, and structures them along interests, values, the four dimensions of career adaptability, and four axes of past behaviour. From there, it produces a self_analysis.json holding three elements: grounded strengths, a career narrative, and a constructive reframing of the reason for leaving. Job interview preparation (job-change-interview-prep) and the deepening of statements of motivation (job-change-documents) read the deliverable as input.

This skill uses behavioural evidence and the perspective of others alongside introspection (the grounds are in `references/self-analysis-methods.md`). A dedicated agent handles writing, and a separate dedicated agent handles independent auditing (`job-change-self-analysis-writer` and `job-change-self-analysis-auditor`). This skill oversees launching writing and independent auditing, sending work back for revision, and delivering the result.

## Purpose and principles

1. **Use the perspective of others and behavioural evidence alongside introspection.** Every strength must map to a behavioural episode (behavioral_episodes) or feedback from others (others_feedback). A strength grounded in introspection alone is not accepted (the validation script reports it as an ERROR). Take in feedback from others with a task-oriented focus, and record it as a mapping between actions and results.

2. **Limit questions to a fixed set of structured questions (to prevent rumination).** Questions are limited to the fixed set in `references/question-bank.md`, and unlimited repetition of "why" is never encouraged. When probing further, questions always map to an action or a fact (an episode) and never lead the user into an emotional rumination. An affective forecast ("changing jobs will make me happy") is never used as grounds for a firm conclusion.

3. **Never treat a diagnostic result as a final verdict.** Frameworks with weak validity (Schein's career anchors, commercial strengths tools, RIASEC self-diagnosis tools) are used only in a limited way, as a prompt for introspection. A result is never treated as a settled picture of the self. Practical methods (Will-Can-Must, the motivation graph, feedback from others, the Johari window) are used to move the elicitation interview forward, and any result obtained through them is corroborated with introspection, behaviour and testimony from others before it enters the deliverable.

3-2. **Ask about personality and behavioural tendencies as a forced choice between options drawn from published frameworks, and never sort a person into a type.** Self-reported personality is limited to published item sets (the Big Five and honesty-humility from IPIP), two whose construct alone is borrowed (grit and self-efficacy; their scales are not used), and this skill's own seven behavioural-tendency items, asked as a forced choice grounded in behaviour. MBTI, 16Personalities, employer-side aptitude tests, and any company's free diagnostic tool are never offered. A self-report records the person's self-image, so it counts toward a strength only once it maps to an episode or feedback from others. Write the result as a descriptive passage, and attach no numeric score (`references/personality-guide.md`).

4. **Never fabricate or exaggerate a fact.** The career history, achievements, and figures that enter the deliverable stay within the range profile.json records. Match a behavioral_episodes `metric` (a quantitative value) exactly to profile.json's achievements, with no rounding or inflating. Keep a word denoting scale, scope, or agency (large-scale, company-wide, led, and the like) within the range profile.json's description corroborates.

5. **Never send personal information outward.** Never use the personal information held in `profile.json` or `self_analysis.json` in any external transmission, including a search query, a fetch, or an external API. The canonical enumeration of the scope and each role's permission is in the hub's `{HUB_SKILL_DIR}/references/pii-boundary.md`. This skill sits inside that boundary, building `self_analysis.json`. Because neither the writer (`job-change-self-analysis-writer`) nor the auditor (`job-change-self-analysis-auditor`) holds a means of sending data to the web, the paths of `profile.json` and `self_analysis.json` may be passed to them.

## Out of scope

The following fall outside this skill's scope. When asked for one of these, state that the skill cannot handle it and name the alternative owner or action.

- **Taking an aptitude test on the user's behalf.** This skill never sits a psychological or aptitude test in the user's place. Test preparation is handled by `job-change-exam-prep`.
- **Psychotherapeutic support for introspection, and mental-health counselling.** This skill is limited to self-analysis for a job change. A mental-health condition such as depression or severe anxiety falls outside its scope, and the skill encourages consulting a professional (a physician, a clinical psychologist, a counsellor, and the like). Because excessive introspection (rumination) is harmful, questions stay limited to the fixed set of structured questions. When uncertainty remains about the direction of the person's career itself, the skill points to a nationally certified career consultant (国家資格のキャリアコンサルタント). Free or low-cost consultation is available at a Hello Work office (ハローワーク, the public employment service), a regional youth support station (地域若者サポートステーション), or a job café (ジョブカフェ) (Ministry of Health, Labour and Welfare, https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/koyou_roudou/jinzaikaihatsu/career_consultant01.html).
- **Company research.** Research into a company's philosophy, business and reputation is handled by `job-change-company-research`. This skill is limited to analysis of the user.
- **Writing application documents.** Writing a work history document, a statement of motivation, and the like is handled by `job-change-documents`. This skill produces the material for application documents — grounded strengths, the narrative, and the reason for leaving — and hands it to `job-change-documents`.

## Path resolution

Where user data is stored is decided solely by what the configuration file states. There is no default location. Wherever this document writes `{DATA_ROOT}`, read it as the `data_root` that the following command returns.

When routed from the hub (job-change-support), this skill receives an already-resolved `{DATA_ROOT}` from the hub. When launched standalone, run the following before any other step of the work.

```bash
python {HUB_SKILL_DIR}/scripts/jc_config.py --show
```

| Exit code | State | Response |
|---|---|---|
| 0 | Configured | The `paths` field in the output holds the absolute path for each data item. Proceed with the work as is. |
| 1 | Configuration exists but is invalid | Show the user the `errors` field in the output, and do not proceed until it is fixed. |
| 2 | Not configured | Launch `job-change-support` with the Skill tool to have it create the configuration, resolve `{DATA_ROOT}`, and then return. |

`{SKILL_DIR}` refers to this skill's own absolute path, and `{HUB_SKILL_DIR}` refers to the absolute path of `job-change-support`, installed alongside it. The configuration file's specification, including its lookup order, is in `docs/configuration.md`.

## Data layout

User data lives in the private directory `{DATA_ROOT}/career-private/`. The paths this skill reads and writes are as follows.

| Path | Role | I/O |
|---|---|---|
| `career-private/profile.json` | The canonical definition of the user profile (managed by the hub) | Input (read as the starting values; only values are reflected back in Step 6) |
| `career-private/self_analysis.json` | The canonical self-analysis deliverable | Output (the material sections are appended incrementally in Steps 1–3, and the integrated sections are written in Step 4) |

- The material sections refer to `behavioral_episodes`, `others_feedback`, `interests`, `values`, `career_adaptability`, and `personality.markers`. The integrated sections refer to `strengths`, `career_narrative`, `reason_for_change`, and `personality.presentation`. `validate_self_analysis.py` fails while the integrated sections remain unwritten, so validation happens in Step 5.
- The canonical definition of `self_analysis.json`'s field specification, entry criteria, and validation rules is in `references/self-analysis-format.md`. A worked example (a fictional person) is in `assets/self_analysis_example.json`.
- Never place user data inside the skill's own folder (`skills/job-change-self-analysis/`).
- When `career-private/` does not yet exist, this skill creates it once it is needed.

## Pipeline

Proceed through Steps 0–6 in order, from intake to delivery. In Steps 1–3, write what was elicited to `{SELF}` at the end of each step. This lets the work resume, after an interruption, without asking again about a step already completed. Read `{SKILL_DIR}` as this skill's own absolute path, `{PROFILE}` as the absolute path of `profile.json`, and `{SELF}` as the absolute path of `self_analysis.json`.

### Step 0: Preconditions

- Check whether `profile.json` exists. If it does not, direct the user first to the `job-change-profile` sub-skill through the hub (`job-change-support`), since self-analysis builds on profile.json.
- Validate `profile.json` with the hub's `validate_profile.py`. When it fails (one or more ERRORs), follow the table under "Pass/fail gates and rework" for how to proceed.
- When a `self_analysis.json` already exists, treat this as an update: read its existing content as the starting values, and append or revise the difference.
- When the material sections of an existing `self_analysis.json` are only partly filled in, treat this as resuming from an interruption. Propose to the user that the already-completed steps (whichever of Steps 1–3 are filled in) be skipped and the work continue from there, and let the user decide whether to be asked again.

### Step 1: Taking stock of behavioural episodes

Present `career_history` and `achievements` from `profile.json` as material. Use AskUserQuestion mainly in its choice form (at most 4 questions per call, at most 4 options each; free text is limited to concrete values), and structure the answers into the STAR format (Situation / Task / Action / Result). Use the Step 1 questions in `references/question-bank.md`. Treat the idea of a motivation graph (a timeline plus the rise and fall of feelings) as an optional aid. Attach a `metric` (a quantitative value, matching profile.json's achievements exactly) and a `reproducibility` note to each episode where possible. At the end of this step, write what was elicited to `behavioral_episodes` in `{SELF}` (the canonical definition of the format is in `references/self-analysis-format.md`).

### Step 2: Incorporating feedback from others

Record points raised in past performance reviews, and things others have said, as `others_feedback` (feedback from others, and the Johari window). Use the Step 2 questions in question-bank.md. Take in feedback with a task-oriented focus, and record it in the form of which action led to which result. Map it to an episode with `linked_episode_ids`. When feedback from others cannot be obtained on the spot, proceed with the deliverable left in a WARN state, and show the user that collecting feedback from others remains an open task. Use `assets/feedback_request_template.md` for the request text. At the end of this step, write what was elicited to `others_feedback` in `{SELF}`.

### Step 3: Structured questions on interests, values, and career adaptability

Use only the fixed set of Step 3 questions in `references/question-bank.md`. Structure interests (the RIASEC framework), values (mapped to episodes), and the four dimensions of career adaptability (concern / control / curiosity / confidence). Unlimited repetition of "why" is forbidden, and probing further always maps to an episode (a fact). Use Schein's eight categories and the five CCI-style questions as a prompt, and never treat the result as a final verdict. At the end of this step, write what was elicited to `interests`, `values`, and `career_adaptability` in `{SELF}`.

### Step 3.5: Self-reported personality and behavioural tendencies

Ask the 16 Step 3.5 questions in `references/question-bank.md` (covering 15 constructs; the breakdown of question counts is in that file) as a forced choice grounded in behaviour (4 questions per AskUserQuestion call, across 4 calls). After each item is answered, have the user pick one episode where that tendency showed up, and map it with `linked_episode_ids`. When feedback from others describes the same tendency, map it with `feedback_ids`. When no episode comes to mind, leave `linked_episode_ids` empty. When the user wants to skip this, the whole of Step 3.5 may be skipped, in which case `personality` is not written. At the end of this step, write what was elicited to `personality.markers` in `{SELF}`. The canonical definition of the vocabulary, the way of asking, and the way of writing is in `references/personality-guide.md`.

### Step 4: Integration (writing)

Launch the `job-change-self-analysis-writer` agent (model: opus). Pass it `{SELF}`, with its material sections written in Steps 1–3.5, along with `{PROFILE}` and the output destination `{SELF}`, and have it read the material sections. The writer grounds the strengths (a mapping to an episode or feedback is mandatory), creates the career_narrative (the life theme, turning points, consistent motivation), and creates reason_for_change.constructive_version (built around the value the user wants to bring to bear). When `personality.markers` exists, the writer describes, in prose, the agreement and disagreement between the self-report and the episodes and feedback from others, in `personality.presentation` (attaching no name of a type or category and no numeric score). Present the returned result to the user, and confirm the points to revise through AskUserQuestion's choice form.

### Step 5: Mechanical validation and independent audit

Validate `{SELF}` with `validate_self_analysis.py` and confirm it PASSes (zero ERRORs). Then launch the `job-change-self-analysis-auditor` agent (model: opus, in a fresh context that withholds the writer's rationale). It audits for exaggeration and fabrication, consistency of the description, a firm claim grounded in introspection alone, a description that relies on rumination or an affective forecast, the name of a type or category, a description that fits anyone, and a strength grounded in a self-report alone. Send its findings back to Step 4 (at most twice; beyond that, the decision belongs to the user).

### Step 6: Reflecting values back and pointing to what connects downstream

Reflect only the values of `strengths` (a short sentence drawn from self_analysis's strengths.statement) and `job_change_axis.reasons` (wording based on constructive_version) back into `profile.json`. Never change profile.json's schema. When a `personality.markers` self-report disagrees with the preference level in profile.json's `work_character_preferences` (the canonical definition of how they correspond is in "Connecting downstream" in `references/personality-guide.md`), show the user the disagreement and let the user decide which one to correct — this skill never decides on its own. Make the reflection through the update of `job-change-profile`'s section (`reasons`, `work_character`). After reflecting, re-run the hub's `validate_profile.py` and confirm it PASSes. Rewrite profile.json's `updated_at` to today's date. `self_analysis.json` is input for downstream sub-skills, so this step never produces a separately formatted file. Instead, show the user a summary of what was written — the strengths, values, interests, career narrative, and the constructive reframing of the reason for changing jobs. Finally, point to the downstream work that can use `self_analysis.json` as input: the deepening of the statement of motivation (`job-change-documents`) and consistent answers in job interview preparation (`job-change-interview-prep`). Open the final message with the conclusion. Never include an empty section, a repetition of the same content, or a stock preamble.

## Pass/fail gates and rework

The pipeline has two gates.

| Gate | Passing condition and where it is sent back |
|---|---|
| The profile gate in Step 0 | Do not start unless `profile.json` PASSes `validate_profile.py`. When it is missing or FAILs, send it back to the `job-change-profile` sub-skill through the hub (`job-change-support`). When it FAILs, show the content of the ERROR. When the user wants to proceed while accepting the gap, proceeding is allowed on the condition that no description directly quotes the value of a missing item and no description assumes that value. State plainly, in the deliverable, which items remain missing. |
| The validation and audit gate in Step 5 | Send it back to the writer at Step 4 when `validate_self_analysis.py` FAILs (one or more ERRORs), when `job-change-self-analysis-auditor`'s `verdict` is BLOCK, or when a finding has `severity` = must_fix. Rework happens at most twice for the same deliverable. |

When sending work back, pass the audit's findings (target, evidence, fix) to the writer as they are, and run it through Step 5 again once they have been reflected. A finding that two rounds of rework fail to resolve is left as an open item, delivered only after the user's judgment has been sought. For example, a finding that profile.json's achievements alone do not sufficiently ground a strength is left to the user's judgment, because it calls for collecting more feedback from others or reconsidering how the strength is presented. An ERROR from mechanical validation is always resolved before delivery, regardless of the rework limit. Delivery with an open item is allowed only when the sole thing left unresolved is a finding from the audit, and only once that item has been clearly stated.

## Running the role (by harness)

This skill's pipeline is written as work delegated to specialised roles. The content of each role lives in `references/roles/`, and the file placed there is the canonical definition.

| Agent name | Canonical definition of the role prompt |
|---|---|
| `job-change-self-analysis-writer` | `{SKILL_DIR}/references/roles/self-analysis-writer.md` |
| `job-change-self-analysis-auditor` | `{SKILL_DIR}/references/roles/self-analysis-auditor.md` |

The canonical definition of the execution procedure per harness, the judgment of how many instances to launch, and the reason for separating writing from auditing is in the hub's `{HUB_SKILL_DIR}/references/role-execution.md`.

## Agent model policy

| Agent | model | Responsibility |
|---|---|---|
| `job-change-self-analysis-writer` | opus | Grounding the strengths, creating the career_narrative, and the constructive reframing of reason_for_change (Step 4), and reflecting audit findings |
| `job-change-self-analysis-auditor` | opus | Auditing, in an independent context, for exaggeration, consistency, weight given to introspection alone, and a description that relies on rumination or an affective forecast, and re-running the validation script (Step 5) |

Mechanical validation is handled by `validate_self_analysis.py`. Each agent's `model` is fixed in its frontmatter, and it is never overridden at launch.

## Script CLI usage examples

Validating the self-analysis deliverable (the exit code is 0 on PASS, 1 on FAIL; a result with only WARNs counts as a PASS). Read `{SKILL_DIR}` as this skill's own absolute path, and the trailing path as the path of the self_analysis.json under validation.

```bash
python {SKILL_DIR}/scripts/validate_self_analysis.py {DATA_ROOT}/career-private/self_analysis.json
python {SKILL_DIR}/scripts/validate_self_analysis.py {DATA_ROOT}/career-private/self_analysis.json --json
```

`--json` outputs the result in JSON form (`status`, `error_count`, `warning_count`, `errors`, `warnings`). A worked example is in `assets/self_analysis_example.json`, and the canonical definition of the field specification and validation rules is in `references/self-analysis-format.md`. `validate_profile.py`, used at the profile gate in Step 0, is a script belonging to the hub (`job-change-support`).

## References list

| File | What it holds | When to read it |
|---|---|---|
| `references/self-analysis-methods.md` | The empirical grounding and limits of the four analytical axes adopted, the limits of introspection and the grounds for using the perspective of others alongside it, the operating rules for preventing rumination, both sides of contested points, and sources with DOIs | When checking the grounds for a principle, when setting the audit's perspective |
| `references/self-analysis-format.md` | self_analysis.json's field specification, entry criteria, and validation rules (the list of ERRORs/WARNs) | At every stage of creating, updating, or validating the deliverable |
| `references/question-bank.md` | The fixed structured questions used in Steps 1–3.5 (the STAR stock-taking, feedback from others, interests/values/adaptability, the forced choice on personality and behavioural tendencies, candidate names for a strength, Schein as a prompt, the five CCI-style questions) | When selecting a question at each step of the elicitation interview |
| `references/personality-guide.md` | The place of self-reported personality and behavioural tendencies, which instruments may and may not be used for questions (with conditions of use), the construct vocabulary, how to ask a forced choice, how to write without the name of a type or category, the connection downstream, the limits of effect size, and sources with DOIs | The Step 3.5 elicitation, creating Step 4's `personality.presentation`, the Step 5 audit, and matching against work characteristics in Step 6 |
| `references/narrative-guide.md` | The structure of the career narrative, the procedure for a constructive reframing of the reason for leaving, the connection to and reservations about how a company evaluates it, and sources with DOIs | When creating or auditing career_narrative and reason_for_change |
