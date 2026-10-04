---
name: job-change-interview-prep
description: >-
  Sub-skill for job-change interview preparation. job-change-interview-scout (sonnet) researches review-site
  posts and recruiting pages for the target company's interviews and builds interview_intel.json; taking
  profile.json and, where available, company_research.json and interview_intel.json as input,
  job-change-interview-coach (opus) generates company-specific expected questions by question category, collects
  the user's answers one question at a time in a mock interview, gives feedback on four criteria (STAR,
  specificity, consistency, and company understanding) and summarizes strengths and priority
  improvements by criterion. Falls back to company-independent general preparation when neither
  company_research.json nor interview_intel.json exists.
  Covers mid-career hiring interviews in Japan, including casual meetings and the behavioral / case
  interviews used by foreign-affiliated companies.
  Personal information in profile.json is never used for outbound transmission.
  Use when the user prepares for a job-change interview in Japan (including foreign-affiliated company
  selection): researching what a company asks in interviews, generating expected questions, running a
  mock interview, getting answer feedback, or practicing behavioral / case interviews.
  trigger words: 面接対策, 想定問答, 想定質問, 逆質問, 行動面接, ビヘイビアラル面接, ケース面接, 模擬面接, カジュアル面談, 面接で聞かれること。
allowed-tools: Read, Write, Glob, Grep, Bash, Agent, AskUserQuestion, Skill
---

# job-change-interview-prep

This skill defines the procedure for job-change interview preparation, from generating expected questions through running a mock interview, evaluating answers, and summarizing results. It starts when the job-change support hub (job-change-support) routes a request here as interview preparation. It covers mid-career hiring interviews in Japan, including the behavioral and case interviews used by foreign-affiliated companies.

The dedicated agent job-change-interview-scout (sonnet) handles researching the target company's interviews (Step 0.9); the dedicated agent job-change-interview-coach (opus) handles generating expected questions (Step 1) and evaluating answers (Step 3). This skill handles launching both agents, running the mock interview, and summarizing results.

## Purpose and principles

1. **Company-specific questions rest on claims from company_research.json and on interview_intel.json.** Company-specific expected questions rest on claims from the target company's company research (company_research.json) and on the interview information gathered in interview_intel.json. From the former, the claims with topic=selection_process (selection-process reports, candidate write-ups) and topic=philosophy (company philosophy) are the main material. From the latter, the reported questions (`reported_questions`), interview-format facts (`format_facts`), and review-site trends (`themes`) are used. Each expected question records its provenance (`provenance`: `general`, `reported`, or `inferred`), showing reported questions in their reported wording and marking inferred questions as inferences. Provenance and the confidence of the underlying evidence are separate things and must not be merged into one confidence level (the canonical definition is in the "Provenance and presentation of expected questions" section of `references/question-bank.md`). When neither company_research.json nor interview_intel.json exists, no company-specific questions are generated; the skill falls back to company-independent general preparation (fallback mode). When company_research.json exists but has zero claims with topic=selection_process, and interview_intel.json's `format_facts` is also absent, no question that presupposes a selection process is generated. This covers any question that treats the number of interview rounds, their format, or the evaluation criteria of each stage as known. In this case, company-specific questions rest only on claims with topic=philosophy, and the user is told there is no evidence for the selection process (partial fallback). Zero claims is never treated as evidence that the selection process is simple. No expected question generated from any source touches a matter that could lead to employment discrimination (the canonical list is in the "Matters the user is not required to answer" section of `references/question-bank.md`). When `career-private/self_analysis.json` exists, it is added as input to question generation and answer evaluation. When `career-private/fit/{company slug}/fit_assessment.json` exists, it is added as input to question generation. Its `condition_fit` entries with `met: "unknown"` and its `overall.open_questions` are used as material for reverse questions (questions the candidate asks the interviewer) and confirmation items. When `companies/{company slug}/exam_assessment.json` exists, its identified exam type and selection-process arrangement are read and used as a premise for judging which selection stage the interview belongs to (optional input; the work proceeds without it).

2. **Answer evaluation is anchored.** Answers are evaluated on four criteria: STAR, specificity, consistency, and company understanding. Each criterion is judged on a three-level scale: `充足` (met), `一部` (partial), or `不足` (not met). The canonical anchors for each level are in `references/evaluation-rubric.md`. job-change-interview-coach reads this file in Step 3 and judges against it. Evaluation follows the canonical anchors exactly, applying them neither leniently nor harshly. For the consistency criterion, the reference set includes `job_change_axis` in `{AXIS}` (when it exists). When self_analysis.json exists, its `career_narrative` (the consistent motivation) and `reason_for_change` (the constructive reframing and its explanation of alignment with `job_change_axis.reasons`) are also added to the reference set.

3. **Personal information is never sent outbound.** The user's personal information is never used for any outbound transmission (search queries, fetches, or external APIs). The canonical list of covered items and role-by-role permissions is in the hub's `{HUB_SKILL_DIR}/references/pii-boundary.md`. Neither this skill's allowed-tools nor job-change-interview-coach's tools include a web transmission method (WebSearch, WebFetch), so profile.json may be passed to it as is. job-change-interview-scout has web transmission methods. It may receive only these inputs: the company name, the job title, the job posting URL, the output path, and the paths to `company_research.json` and `job_posting.json` under `companies/{company slug}/`. It never receives anything under `career-private/`, nor `interview_answers.json`, `interview_evaluation.json`, or `interview_notes_user.md` under `companies/{company slug}/`.

4. **An agent's model is fixed.** job-change-interview-coach's model is fixed to opus in that agent's frontmatter, and job-change-interview-scout's model is fixed to sonnet. Neither is overridden at launch.

5. **Information the user already holds takes priority over the web.** A list of questions from a job-change agency, or the user's experience from a past selection process at the same company, is more current than review-site posts from the web. It also connects directly to that company's selection process. Step 0 checks whether such information exists and, if so, records it in `interview_notes_user.md` as material for expected questions. This file contains the details of the user's own selection process and is never passed to a role with web transmission methods.

## Out of scope

- **Company research itself.** Researching a company's business, finances, reputation, and selection process belongs to `job-change-company-research`. This skill takes the researched company_research.json as input.
- **Producing application documents.** Producing a résumé, CV, or cover letter belongs to `job-change-documents`.
- **Preparation for written tests and aptitude tests.** Preparation for SPI, 玉手箱 (Tamatebako), and other online assessments belongs to `job-change-exam-prep`. This skill covers preparing answers to questions asked in a recorded online interview (such as HireVue); preparation for game-based assessments belongs to `job-change-exam-prep`.
- **Scheduling interviews and sending materials to the employer.** Scheduling interview dates and replying to or sending anything to the employer are out of scope. This skill supports expected questions and answer improvement; the user sends anything themselves.
- **Predicting the outcome.** This skill never predicts the probability of passing or being hired. Its scope stops at evaluating answers by criterion and suggesting improvements.

## Path resolution

The location of the user's data is determined entirely by the configuration file. There is no default location. Wherever this document writes `{DATA_ROOT}`, read it as the `data_root` returned by the following command.

When routed from the hub (job-change-support), the hub passes the already-resolved `{DATA_ROOT}`. When launched standalone, this skill runs the following before any other step of the work.

```bash
python {HUB_SKILL_DIR}/scripts/jc_config.py --show
```

| Exit code | State | Response |
|---|---|---|
| 0 | Configured | The absolute path to each data item is in the output's `paths`. Proceed with the work |
| 1 | Configured but invalid | Show the user the `errors` in the output; do not proceed until it is fixed |
| 2 | Not configured | Launch `job-change-support` with the Skill tool to create the configuration, resolve `{DATA_ROOT}`, then return here |

`{SKILL_DIR}` is this skill's absolute path; `{HUB_SKILL_DIR}` is the absolute path of `job-change-support`, located alongside it. The configuration file's specification, including its search order, is in `docs/configuration.md`.

## Intermediate artifacts

Each stage of the pipeline produces the following. When the work proceeds with an identified company (company mode, with a resolved company slug), these are saved under `{DATA_ROOT}/companies/{company slug}/`. When launched without a target company, there is no company slug, so results are presented in conversation and written out only when the user specifies a save location. Fallback mode (no company-specific evidence) is a distinction independent of whether a company slug exists; when a company slug exists, fallback-mode artifacts are still saved to the same location. `interview_notes_user.md`, `interview_answers.json`, and `interview_evaluation.json` contain the user's information and answers verbatim, and `interview_questions.json` and `interview-prep-report.md` contain content derived from the profile and the answers, so all of these are personal information. Neither this skill nor job-change-interview-coach has a web transmission method, however, and no role outside this skill reads these files. Role prompts also instruct every role with a web transmission method not to read these files. For this reason, they are placed in the same location as the other artifacts (the canonical definition of the boundary is in `{HUB_SKILL_DIR}/references/pii-boundary.md`).

| File | Content | Step that produces it |
|---|---|---|
| `interview_notes_user.md` | Information about the company's interviews that the user obtained from a job-change agency or a past selection process, in the user's own words | Step 0 |
| `interview_intel.json` | Reported questions, interview-format facts, and review-site trends gathered from review sites and recruiting pages about the target company's interviews (output JSON of job-change-interview-scout; non-personal information) | Step 0.9 |
| `interview_questions.json` | Expected questions by question category (the top-level Step 1 output JSON from job-change-interview-coach, saved as is) | Step 1 |
| `interview_answers.json` | Question ID / answer pairs (appended incrementally in Step 2; used to resume after an interruption) | Step 2 |
| `interview_evaluation.json` | Evaluation on the four criteria (the top-level Step 3 output JSON from job-change-interview-coach, saved as is) | Step 3 |
| `interview-prep-report.md` | Strengths and priority improvements by criterion, and suggestions for further practice | Step 4 |

The canonical specification for `interview_questions.json`, `interview_answers.json`, and `interview_evaluation.json` is in `references/interview-format.md`; the canonical specification for `interview_intel.json` is in `references/interview-intel-format.md`. `interview_questions.json` and `interview_evaluation.json` follow job-change-interview-coach's output JSON (Step 1 and Step 3) exactly. Every top-level key, including `degraded` and `degraded_reason`, is saved as is; the `questions` or `evaluations` array alone is never extracted and saved on its own. Dropping `degraded` would make it impossible to tell from the file alone whether a question set is company-specific or a company-independent fallback, which would make it impossible to recheck the pass gate when resuming after an interruption.

## Pipeline

Proceed through Step 0 to Step 4 in order. Read `{HUB_SKILL_DIR}` as the absolute path of the job-change support hub (job-change-support).

### Step 0: Load and gate

1. Check for the existence of `{DATA_ROOT}/career-private/profile.json` with Read / Glob. If it is missing, return to the hub (job-change-support) and have it create the profile first.
2. Pass the career gate (mandatory). profile.json (read as `{PROFILE}`, the career facts) is assumed to have passed (`python {HUB_SKILL_DIR}/scripts/validate_profile.py {PROFILE}`, a job-change-support script, returning zero ERRORs) before this step. When entering this skill through the hub, the hub has already confirmed a PASS before routing. When launched standalone, this skill runs `validate_profile.py` itself to confirm a PASS. On FAIL, show the user the ERROR contents and recommend completing the profile through `job-change-profile`. If the user still wants to proceed knowing the gaps, the work may continue on two conditions: no question directly quotes or presupposes the value of a missing field, and no evaluation rests on that field as evidence. The report then states plainly which fields remain missing. When the hub has already put this choice to the user before routing here, this skill does not ask it a second time. It follows the choice already made, so the hub and this skill never ask the user the same choice twice.
   The axis is optional input here. Resolve `{AXIS}` by the rule in `{HUB_SKILL_DIR}/references/axis-format.md`, section "Location". When it resolves to a file, confirm it with `python {HUB_SKILL_DIR}/scripts/validate_axis.py {AXIS}`; on FAIL, show the ERRORs, recommend fixing them through `job-change-axis`, and continue without `{AXIS}`. When no axis source exists, continue without it and tell the user once that questions about the reason for changing jobs and about work style rest on weaker grounds. The reason-for-change judgment then relies on `self_analysis.json` or the user's own interview notes.
3. Before resolving the company slug, validate the index with `validate_company_index.py` (a job-change-support script). On FAIL (one or more ERRORs), show the user the findings and do not proceed to resolution until it is fixed.
4. Resolve the target company's company slug from `career-private/company_index.json` (details in job-change-support's `references/company-index-format.md`). Then check whether company_research.json exists (`companies/{company slug}/company_research.json`). If `interview_answers.json` exists in the same folder, subtract the set of `interview_answers.json`'s `answers[].question_id` values from the set of `interview_questions.json`'s `questions[].id` values. Present the questions whose IDs remain as the "remaining questions" and offer to resume from there. This difference is determined solely from these two files. If `interview_questions.json` is missing, resumption is not possible, and the work restarts from Step 1. If company_research.json is missing, use AskUserQuestion to present the following choices explicitly and let the user pick.
   - (A) Run company research first. Return to the hub, launch `job-change-company-research` to obtain company_research.json, then come back to this skill.
   - (B) Skip company research and run only the Step 0.9 interview-information research. Proceed using `interview_intel.json` as the company-specific evidence.
   - (C) Choose fallback mode. Proceed as general preparation with no company-specific evidence; from here on, no company-specific expected question is generated, and the company-understanding criterion is excluded from evaluation.
5. When company_research.json exists, judge the company's `_manifest.json` with `check_freshness.py` (a job-change-support script). If any topic is `stale`, tell the user so, naming the affected topics, and suggest a differential re-research through `job-change-company-research`. If the user chooses to proceed without re-researching, that is fine, but Step 4's `interview-prep-report.md` must record that the information is stale and which topics are affected. The canonical judgment rules and TTLs are in job-change-support's `references/freshness-policy.md`.
6. Check whether `career-private/self_analysis.json` exists. If so, add it as input to Step 1 and Step 3. If it is absent, the work can proceed, but tell the user explicitly that running self-analysis (`job-change-self-analysis`) first would make two things available as evidence for the consistency criterion: the career narrative and the constructive reframing of the reason for leaving.
7. Check whether `career-private/fit/{company slug}/fit_assessment.json` exists. If so, add it as input to Step 1. When generating expected questions, use its `condition_fit` entries with `met: "unknown"` and its `overall.open_questions` as material for reverse questions and confirmation items. The work can proceed without it. fit_assessment.json is an artifact under career-private and is never passed to an agent with web tools.
8. Confirm the personal-information handling rules. The content of profile.json is never used for outbound transmission. Neither this skill nor job-change-interview-coach has a web transmission method, so profile.json (and, where present, `{AXIS}`, self_analysis.json and fit_assessment.json) may be passed as is.
9. Ask one AskUserQuestion to check whether the user holds a list of questions or selection-process trends from a job-change agency, experience from a past selection process at the same company, or anything heard in a casual meeting. If so, record it in the user's own words in `companies/{company slug}/interview_notes_user.md` (in company mode). Do not summarize or rephrase it. If not, do not create the file.
10. Confirm with the user which selection stage is the target (`カジュアル面談` (casual meeting), `一次面接` (first interview), `二次面接` (second interview), or `最終面接` (final interview)). If unclear, record `不明` (unknown) and supplement it later with Step 0.9's `format_facts`.

### Step 0.9: Interview-information research (job-change-interview-scout, sonnet)

Runs when a company slug has been resolved, gathering information from the web about the target company's interviews. It does not run when launched without a target company identified.

1. Check whether `companies/{company slug}/interview_intel.json` exists and how fresh it is. If `_manifest.json` records `artifacts.interview_intel`, `check_freshness.py` judges it (the canonical TTL and judgment rules are in `{HUB_SKILL_DIR}/references/freshness-policy.md`). If `fresh`, use the existing artifact without re-researching. If `stale` or not yet obtained, proceed.
2. Ask the user whether to research at all, noting that it takes about as long as one web-fetch research pass and that review sites can only be read within what is available without logging in. If the user declines, skip it and note this in the Step 4 report.
3. Launch job-change-interview-scout (sonnet) with the Agent tool. Pass it the following in the instructions.
   - The company name (the formal name and any aliases from `company_index.json`) and the job title (from `job_posting.json`; if absent, the job title the user specified).
   - The output path `{DATA_ROOT}/companies/{company slug}/interview_intel.json`.
   - This skill's absolute path (`{SKILL_DIR}`) and job-change-company-research's absolute path (the location of `references/evidence-grading.md` and `references/source-catalog.md`).
   - The paths to `companies/{company slug}/company_research.json` and `job_posting.json`, if they exist. Both are in the non-personal-information tree.
   - **Never pass**: any path or content under `career-private/`; `interview_notes_user.md`, `interview_answers.json`, `interview_evaluation.json`, `interview_questions.json`, `interview-prep-report.md`, or anything under `documents/`; or the user's name, career history, or salary.
4. Re-verify the `interview_intel.json` the scout wrote with `validate_interview_intel.py` (gate). On FAIL (one or more ERRORs), attach the ERROR contents to the instructions and relaunch the scout. Once PASS is confirmed, Read `_manifest.json`, replace only `artifacts.interview_intel` with `{"updated_at": "YYYY-MM-DD"}`, and Write the whole object back. Do not drop the records of other artifacts. If the file does not exist, create `{"schema_version": 1, "artifacts": {"interview_intel": {...}}}`.
5. If any `reported_questions[].category` is `配慮事項` (a matter requiring care), tell the user this is a matter they need not answer even if asked (「聞かれても答えなくてよい事項」) (the canonical list is in `references/question-bank.md`). If `open_questions` notes that a source is old or comes from a new-graduate hiring record, tell the user this too.

### Step 1: Generate expected questions

1. Launch job-change-interview-coach (opus) with the Agent tool, instructing it to run Step 1. Pass it the following in the instructions.
   - The step to run = 1.
   - The absolute path to profile.json, and `{AXIS}` (if present). The absolute paths to company_research.json (if present), interview_intel.json (if present), interview_notes_user.md (if present), self_analysis.json (if present), fit_assessment.json (if present), exam_assessment.json (if present), and the job posting (if present).
   - The target selection stage (as confirmed in Step 0, including `不明`).
   - This skill's absolute path (`{SKILL_DIR}`), as the location of the canonical output-format definition `references/interview-format.md`.
2. The coach generates expected questions by question category. Each question is returned with four fields. The interviewer_intent is the evaluation criterion the interviewer is checking. The basis is a claim ID from company_research, an ID from interview_intel, the relevant part of `interview_notes_user.md`, or the relevant part of the profile. The provenance is `general`, `reported`, or `inferred`. The stage is the selection stage the question is expected in. In fallback mode, degraded: true is set, and no question is generated from a company-specific claim. When company_research.json exists but has zero claims with topic=selection_process, and interview_intel.json's `format_facts` is also absent, this must be stated explicitly in the instructions, and no question that presupposes a selection process is generated (partial fallback). When fit_assessment.json exists, its `condition_fit` entries with `met: "unknown"` and its `overall.open_questions` are added. Both serve as material for reverse questions and confirmation items. When it is absent, only company_research.json, interview_intel.json, and profile.json serve as material. When the selection stage is `カジュアル面談` (casual meeting), only the `逆質問` (reverse questions) category and short `自己紹介` (self-introduction) / `転職理由` (reason for changing jobs) answers are generated.
3. Save the JSON the coach returns as `interview_questions.json` (in company mode), including every top-level key such as `degraded` and `degraded_reason`. Do not extract only the `questions` array. The canonical format definition is in `references/interview-format.md`; the canonical definitions for question categories, evaluation criteria, and foreign-affiliated-company question formats are in `references/question-bank.md`, `references/evaluation-rubric.md`, and `references/foreign-interviews.md` respectively.
4. Validate the saved `interview_questions.json` with `validate_interview_artifacts.py` (in company mode; a gate). On FAIL (one or more ERRORs), do not proceed to Step 2. Attach the ERROR contents to the instructions and relaunch the coach.

### Step 2: Mock interview

1. This skill (the orchestrator) presents the generated expected questions one at a time, collects the user's answer as text, and moves to the next question after each answer. Questions with `provenance: reported` are presented first; `inferred` questions are presented as marked inferences. A `配慮事項` (matter requiring care) is only ever written in `notes`; it is never used in the mock interview. A question whose `stage` differs from the target selection stage is deferred unless the user asks for it.
2. Not every question needs to be covered. The interview may be run over a range the user specifies (question category, number of questions). As each answer is received, append one entry `{"question_id": …, "answer": …, "answered_at": …}` to the `answers` array in `companies/{company slug}/interview_answers.json`. When there is no company slug, keep it in conversation instead. `question_id` is written exactly as the presented question's `id` in `interview_questions.json`. `answer` transcribes the user's answer verbatim, with no summarizing or rephrasing. The canonical format definition is in `references/interview-format.md`.
3. No evaluation, correction, or rephrasing happens at this stage (evaluation is Step 3). Answers are never led toward any direction.
4. Before proceeding to Step 3, validate `interview_answers.json` with `validate_interview_artifacts.py` (in company mode; a gate), passing `interview_questions.json` to `--questions` to confirm every `question_id` exists on the question side. On FAIL, resolve the ERRORs before proceeding to Step 3.

### Step 3: Evaluate answers and give feedback

1. Launch job-change-interview-coach (opus) with the Agent tool, instructing it to run Step 3. Pass it the following in the instructions.
   - The step to run = 3.
   - The absolute path to profile.json, and `{AXIS}` (if present). The absolute paths to company_research.json (if present), interview_intel.json (if present), and self_analysis.json (if present).
   - This skill's absolute path (`{SKILL_DIR}`), as the location of the canonical output-format definition `references/interview-format.md`.
   - The list of questions and answers to evaluate (read from `interview_answers.json` in company mode; the pairs kept in conversation when there is no company slug).
2. The coach evaluates each answer on four criteria: STAR (scores.star), specificity (scores.specificity), consistency (scores.consistency), and company understanding (scores.company_fit). Each criterion takes one of three levels: `充足` (met), `一部` (partial), or `不足` (not met). feedback and improvement always include an evidence reference (the relevant part of the profile, self_analysis.json's narrative or reason_for_change, or a claim ID). In fallback mode, the company-understanding criterion is excluded and degraded: true is set.
3. The canonical evaluation anchors are in `references/evaluation-rubric.md` (matching the coach's own judgment definitions). Save the JSON the coach returns as `interview_evaluation.json` (in company mode), including every top-level key such as `degraded` and `degraded_reason`. Do not extract only the `evaluations` array. The answers themselves remain in `interview_answers.json`, linked by `question_id`. The canonical format definition is in `references/interview-format.md`.
4. Validate the saved `interview_evaluation.json` with `validate_interview_artifacts.py` (in company mode; a gate), passing `interview_questions.json` to `--questions`. On FAIL, do not proceed to Step 4. Attach the ERROR contents to the instructions and relaunch the coach.

### Step 4: Summary

1. Aggregate every evaluation by criterion, organizing strengths (criteria largely met) and priority improvements (criteria not met, with specific ways to address them). Improvement suggestions follow the anchors in `references/evaluation-rubric.md` and include how to fill any missing STAR element and how to bring in company understanding.
2. Add a suggestion for further practice (a repeat mock interview focused on the weaker criteria or question categories).
3. Compile the strengths and priority improvements by criterion, and the practice suggestions, into `interview-prep-report.md` (saved to the company folder in company mode). Every judgment and improvement suggestion rests on the evaluation anchors and evidence references, never on facts absent from profile.json, company_research.json, or interview_intel.json. The report states the breakdown of expected-question provenance (the counts of `general`, `reported`, and `inferred`) and reproduces `interview_questions.json`'s `notes` (matters the user is not required to answer, premises about the selection stage, and notes on stale sources). If interview-information research was skipped, state this too.
4. Both the report and the final message state the conclusion first. Every section has content, each point appears once, and the text opens without a formulaic preamble.

## Pass gates and reruns

The pipeline has four gates.

- The Step 0.9 scout-output gate (when research ran in company mode) validates the saved `interview_intel.json` with `validate_interview_intel.py` and confirms PASS (zero ERRORs). On FAIL, attach the ERROR contents to the instructions and relaunch the scout. A returned `{"error": ...}` means an input was missing; fix the instructions and relaunch. This validation checks only format and the presence of sources; whether a question was actually asked is left to the user's judgment.
- The Step 0 career gate (mandatory) does not allow proceeding to Step 1 unless `validate_profile.py` returns PASS. The axis gate (`validate_axis.py`) is optional and never blocks. If profile.json does not exist, or if it FAILs (one or more ERRORs), have the hub (job-change-support) complete the profile through `job-change-profile` first and confirm PASS before returning; on FAIL, show the ERROR contents. If the user wants to proceed knowing the gaps, the work may continue on two conditions: no question directly quotes or presupposes the value of a missing field, and no evaluation rests on that field as evidence. The report states which fields remain missing. When the hub has already put this choice to the user, this skill does not ask it a second time and follows the choice already made.
- The coach-output gate (Step 1 and Step 3) confirms that the JSON job-change-interview-coach returns satisfies the following. If not, relaunch the coach with the shortfall attached to the instructions.
  - It is not `{"error": ...}` (a response caused by a missing input).
  - It conforms to the schema (`questions` for Step 1, `evaluations` for Step 3).
  - `degraded` and `degraded_reason` are consistent with whether company-specific evidence exists. The condition for setting `degraded` to `true` is defined in "Purpose and principles" item 1 and is not redefined here. When `true`, `degraded_reason` states the reason (no company-specific evidence, or no evidence for the selection process).
  - Each of Step 3's `scores` values is one of `充足` (met), `一部` (partial), or `不足` (not met).
  - Step 3's `feedback` and `improvement` include an evidence reference. An evidence reference means the relevant part of the profile, self_analysis.json's narrative or reason_for_change, or a claim ID.
- The artifact gate (Steps 1 to 3, in company mode) validates the saved `interview_questions.json`, `interview_answers.json`, and `interview_evaluation.json` with `validate_interview_artifacts.py` and confirms PASS (zero ERRORs). On FAIL, do not proceed to the next Step. This validation script checks only format, `degraded` consistency, `question_id` cross-references, and vocabulary. The soundness of a question or evaluation is outside what it checks. When there is no company slug, artifacts may not be written to a file at all. In that case this gate is skipped.

Reruns are capped at two per step. If the issue does not resolve within two reruns, present the question or evaluation in question as an open item to the user and proceed only after they decide.

## Executing roles (by harness)

This skill's pipeline is written as delegation of work to dedicated roles. Role content is in `references/roles/`, which is the canonical source.

| Agent name | Canonical role-prompt location |
|---|---|
| `job-change-interview-scout` | `{SKILL_DIR}/references/roles/interview-scout.md` |
| `job-change-interview-coach` | `{SKILL_DIR}/references/roles/interview-coach.md` |

The canonical execution procedure by harness, and the judgment for how many to launch, are in the hub's `{HUB_SKILL_DIR}/references/role-execution.md`. On a harness that cannot launch subagents, when the main body itself takes on the scout's role, it may have already read `career-private/`. Even then, while performing the scout's role, it brings no personal information into either its search terms or its output.

## Agent model policy

| Agent | model | Responsibility |
|---|---|---|
| `job-change-interview-scout` | sonnet | Step 0.9: web research on the target company's interviews → interview_intel.json |
| `job-change-interview-coach` | opus | Step 1: generate expected questions by category / Step 3: four-criterion answer evaluation and feedback |

The model is fixed in each agent's frontmatter and is not overridden at launch.

## Script CLI usage examples

This skill has two validation scripts: `validate_interview_intel.py` and `validate_interview_artifacts.py`. The former validates the `interview_intel.json` saved in Step 0.9. The latter validates the artifacts saved in Step 1, Step 2, and Step 3, as shown below. The script determines which kind of artifact it is checking from the top-level keys, so this is never given as an argument.

```bash
python {SKILL_DIR}/scripts/validate_interview_intel.py {DATA_ROOT}/companies/{company slug}/interview_intel.json --json
python {SKILL_DIR}/scripts/validate_interview_artifacts.py {DATA_ROOT}/companies/{company slug}/interview_questions.json
python {SKILL_DIR}/scripts/validate_interview_artifacts.py {DATA_ROOT}/companies/{company slug}/interview_answers.json --questions {DATA_ROOT}/companies/{company slug}/interview_questions.json
python {SKILL_DIR}/scripts/validate_interview_artifacts.py {DATA_ROOT}/companies/{company slug}/interview_evaluation.json --questions {DATA_ROOT}/companies/{company slug}/interview_questions.json --json
```

The scripts used in Step 0 all belong to the hub (job-change-support); when entering through the hub, the hub has already run them before routing. When launched standalone, this skill runs the following itself. Read `{HUB_SKILL_DIR}` as the hub skill's absolute path.

```bash
python {HUB_SKILL_DIR}/scripts/validate_profile.py {PROFILE} --json
python {HUB_SKILL_DIR}/scripts/validate_axis.py {AXIS} --json
python {HUB_SKILL_DIR}/scripts/validate_company_index.py {DATA_ROOT}/career-private/company_index.json
python {HUB_SKILL_DIR}/scripts/check_freshness.py {DATA_ROOT}/companies/{company slug}/_manifest.json
```

`validate_interview_intel.py`, `validate_interview_artifacts.py`, `validate_profile.py`, and `validate_company_index.py` exit 0 on PASS and 1 on FAIL (WARN alone counts as PASS). `check_freshness.py` always exits 0 and prints a classification of `fresh`, `stale`, or `missing`. The canonical specification and validation rules for profile.json are in job-change-support's `references/profile-format.md`.

## references index

| File | What it covers | When to read it |
|---|---|---|
| `references/interview-intel-format.md` | Field specification, entry criteria, and mechanical validation rules for `interview_intel.json`; the distinction between reported and inferred questions | The Step 0.9 research and validation, and Step 1 input |
| `references/interview-format.md` | Field specification, entry criteria, and mechanical validation rules for the three artifacts (`interview_questions.json`, `interview_answers.json`, `interview_evaluation.json`) | Saving and validating in Step 1 through Step 3 |
| `references/question-bank.md` | Provenance and presentation of expected questions; frequent question categories with interviewer evaluation criteria (sub-items, age bracket, selection stage), principles for answering, reverse questions to avoid, casual meetings, matters the user is not required to answer, and sourced information obtained through a job-change agency | The Step 0 interview, generating expected questions in Step 1, running Step 2 |
| `references/roles/interview-scout.md` | Role prompt for the interview-information research role | Step 0.9. Read by the main body on a harness that cannot use subagents |
| `references/roles/interview-coach.md` | Role prompt for generating expected questions and evaluating answers | Step 1 and Step 3. Read by the main body on a harness that cannot use subagents |
| `references/evaluation-rubric.md` | The four criteria (STAR, specificity, consistency, company understanding) and their three-level anchors; elements of a good answer; academic evidence (with DOIs) | Evaluation in Step 3, summary in Step 4 |
| `references/foreign-interviews.md` | How foreign-affiliated behavioral / competency interviews and case interviews proceed, and their evaluation criteria (sourced) | Step 1, Step 2, and Step 3 for a foreign-affiliated selection process |
