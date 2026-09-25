# Company-specific tailoring and the anti-exaggeration standard

This is the canonical definition for the procedure that adjusts an application document to the target
company and the target posting, and for the standard that keeps that adjustment from turning into
exaggeration or fabrication. The writer (`job-change-document-writer`) uses it for the statement of
motivation's structure and the appeal mapping; the auditor (`job-change-document-auditor`) uses it for
detecting exaggeration and fabrication. The standard for checking exaggeration across every document
type is consolidated here.

## Appeal mapping

Before writing, build a table that maps the posting requirements against `profile.json`'s
achievements. This becomes the grounding for every selling point.

| Column | Content |
|---|---|
| Posting requirement | An experience, a skill, or a result the posting asks for. One requirement per row. |
| Corresponding achievement | The career history or achievement in `profile.json` that corresponds to that requirement. Points to the relevant entry in `career_history[].achievements`. |
| Supporting evidence | The concrete fact that grounds the correspondence (the scope of responsibility, a quantified value in `metric`, a qualification, and the like). |

- Every selling point maps to a posting requirement. Do not line up a self-PR statement that connects
  to no requirement.
- When `profile.json` has no achievement that corresponds to a posting requirement, leave that row
  blank. Do not fill it with fabrication. When many rows are blank, show the user the resulting gap
  between the target job and the career history (whether to apply, and whether to strengthen the
  career history, are the user's decisions).

## The statement of motivation's structure

Write the statement of motivation in three parts (source: リクルートエージェント "職務経歴書に志望動機は必要？"
https://www.r-agent.com/guide/resume/article4402/, reliable secondary).

1. State the conclusion first: why the applicant wants this company.
2. Follow with the background and the reasoning behind that conclusion, backed by a concrete episode
   (the applicant's own experience or achievement).
3. Close with a prospect for how the applicant will contribute and perform after joining.

- Write what only this company makes possible. When a statement of motivation would read equally well
  for a competitor, a hiring manager may judge that it need not be this company (同 リクルートエージェント).
  Tie it to an element specific to the target company's philosophy and business.
- Connect the company research to the achievements. Map `company_research.json`'s philosophy (claims
  with `topic=philosophy`), business, and the profile of the person it wants against `profile.json`'s
  achievements. Ground any element about the company cited in the statement of motivation in a
  `company_research.json` claim; do not build a picture of the company from hearsay or guesswork.
- When `company_research.json` does not exist, a company-specific statement of motivation cannot be
  written. Limit it to a generic skeleton (the axis of the applicant's own career change, an
  organization of their strengths), and tell the user explicitly that company-specific tailoring
  follows after company research.
- When `career-private/self_analysis.json` (the output of `job-change-self-analysis`) exists, use it
  as follows. Use `career_narrative` (the life theme, a turning point, the consistent motivation) for
  the 「背景」 (background) paragraph of the statement of motivation and the self-PR. Use `strengths`
  grounded in evidence (a strength mapped to an `episode_id` or a `feedback_id`) to support the
  「結論」 (conclusion) and 「入社後の貢献」 (contribution after joining) parts. Base any passage touching the reason for changing jobs on
  `reason_for_change.constructive_version` (a reframing centered on the value the applicant wants to
  bring). Confirm it does not conflict with profile.json's `job_change_axis.reasons`. When
  self_analysis.json does not exist, use only profile.json's `strengths` and `job_change_axis` as
  material.

## The anti-exaggeration standard

While adjusting the wording for a company, the writer strictly holds the description within what
`profile.json` supports, following the standard below. The auditor detects exaggeration and
fabrication against this same standard.

- Match a number, a percentage, or an amount in the document exactly to `profile.json`'s
  `achievements[].metric`. Do not round it (「38%」→「約40%」) or inflate it (「40%」→「50%近く」).
  Do not invent a number absent from `metric`. Do not attach a quantified value to an
  achievement whose `metric` is `null`.
- Limit a word for scale, scope, or ownership to what the evidence supports. Do not use a word such as
  「大規模」「全社」「主導」「立ち上げ」「責任者」 (large-scale, company-wide, led, launched, responsible for) beyond
  what `profile.json`'s description supports. The canonical definition of where a role-describing word
  (担当・主担当・リード・統括・責任者) falls on the scale of the applicant's actual involvement lives in
  `job-change-profile`'s `references/answer-handling.md` ("The scale of role phrasing"). Do not
  rewrite a role on the document's side into stronger wording than profile.json supports.
  - Use a word for scale (大規模 large-scale, 多数 numerous, and the like) only when profile.json has a
    description that shows that scale.
  - Use a word for scope (全社 company-wide, 全部門 across all departments, グローバル global, and the like)
    only when profile.json shows that scope. Do not write a single department's initiative as
    「全社の」.
  - Use a word for ownership (主導 led, 統括 oversaw, 立ち上げ launched, and the like) only when
    profile.json shows the applicant's own leading involvement. Do not write an involvement limited to
    participation or support as 「主導」.
- Do not invent a career history entry or an achievement absent from the record. Do not add a career
  history entry, an achievement, or a skill absent from `profile.json` for the purpose of matching a
  posting requirement (fabrication is prohibited).

## The scope and limits of this standard

- The statement of motivation's three-part structure and the "only this company" principle rest on a
  major recruiting agency's practical guide (reliable secondary). The wording's detail varies by
  company and occupation.
- The anti-exaggeration standard rests on this skill family's design, which treats `profile.json` as
  the sole canonical source of grounding. When profile.json's description is inaccurate or incomplete,
  the document's precision is constrained accordingly. Strengthening an achievement runs through
  updating profile.json via `job-change-profile`'s section update (`achievements`).
