# Section: Skill inventory (skills)

Inventories specialized skills and transferable skills separately. The entry categories are technical / business / languages / certifications; the supplementary classification is the Ministry of Health, Labour and Welfare's 9 elements of portable skills (5 対課題 [task-facing], 4 対人 [people-facing]). The first pass skips this section. It is done together with the `achievements` section right before writing the application documents. The rationale is in the skill-classification section of `../profile-methods.md`. The section catalogue and the definition of reach stages are in `../sections.md`.

## Fields to fill

| Field | Format |
|---|---|
| `skills.technical`, `business`, `languages`, `certifications` | Multiple choice (candidates built from what came up in `achievements`) plus free text |
| `skills.portable[].skill`, `category` | Multiple choice |

## Reach stages

| Stage | Condition |
|---|---|
| `skeleton` | At least one category has an item |
| `deep` | `technical` or `business` exists, and `portable` also exists |

## Procedure

Confirm technical / business / languages / certifications by working backward from what came up in `achievements` (present candidates as choices and have the user select). Then confirm the 9 elements of portable skills by multiple choice and place them in `skills.portable` (`category` is either `対課題` [task-facing] or `対人` [people-facing]). Tell the user that matching these against job requirements is done later, at application time, by the application-documents sub-skill.

Opening questions:

- Among the work that came up in `achievements`, which technologies (languages, frameworks, cloud platforms, and so on) were used (present candidates built from what came up, as choices)?
- Which business skills (management, requirements definition, negotiation, and so on) apply?
- Any language ability (in the form `{"language","level"}`) or certifications held? Record the name and the year obtained exactly as the user reports them. Confirm currency only for a score or certification that has an expiry.
- Among the 9 elements of portable skills, which has the user actually exercised (use the settled wording below; split the 9 elements across 3 questions asked in one round of AskUserQuestion)?

When the user wants to move into a role outside their current experience, the candidates built from what came up in `achievements` will not overlap with the target role. In this case, also present candidate skills generally required for the target role (`targets.roles` in axis.json when present; otherwise the role the user names), and have the user select only the ones they actually hold. A candidate list exists only to be chosen from. Write down as held only the items the user selects.

### Settled wording: the 9 elements of portable skills

| Item | Wording |
|---|---|
| Q1 `header` | 対課題（1） (Task-facing (1)) |
| Q1 `question` | 仕事の進め方のうち、実際に発揮した経験があるものを選んでください。 (Among these ways of doing work, select the ones you have actually practiced.) |
| `multiSelect` | true |
| Choices | **現状の把握**：課題を見つけるために状況や情報を集めた経験です。／ **課題の設定**：何を解くべき問題として立てるかを決めた経験です。／ **計画の立案**：解決までの段取りと進め方を組み立てた経験です。 (Grasping the current state: gathering the situation and information to find a problem. / Setting the problem: deciding what to treat as the problem to solve. / Planning: building the steps and approach toward a solution.) |
| Q2 `header` | 対課題（2） (Task-facing (2)) |
| Q2 `question` | 同じく仕事の進め方のうち、発揮した経験があるものを選んでください。 (Likewise, among ways of doing work, select the ones you have practiced.) |
| `multiSelect` | true |
| Choices | **課題の遂行**：立てた計画を実行し、やり切った経験です。／ **状況への対応**：想定が外れたときに、進め方を組み替えた経験です。 (Carrying out the task: executing a plan you set and seeing it through. / Adapting to circumstances: reworking your approach when things did not go as expected.) |
| Q3 `header` | 対人 (People-facing) |
| Q3 `question` | 人との関わり方のうち、発揮した経験があるものを選んでください。 (Among these ways of dealing with people, select the ones you have practiced.) |
| `multiSelect` | true |
| Choices | **社内対応**：上司や経営層に働きかけた経験です。／ **社外対応**：顧客やパートナーと向き合った経験です。／ **上司・部下との連携**：縦の関係で仕事を回した経験です。／ **部門横断・社外との連携**：部門や会社をまたいで巻き込んだ経験です。 (Working within the company: influencing a manager or executives. / Working outside the company: dealing directly with clients or partners. / Working with superiors and subordinates: running work through a vertical relationship. / Working across departments or organizations: pulling in people across departments or companies.) |

Record each element in `skills.portable[]` as `{"skill": element name, "category": "対課題"|"対人"}`. A choice from Q1 or Q2 becomes `対課題`; a choice from Q3 becomes `対人`.

Matching against job requirements is done later, at application time, by the application-documents sub-skill. Here, the work stops at inventorying the facts of what the user holds.

## Downstream

Application documents (`job-change-documents`) use this as material for building the requirements-match table (the appeal map). Fit assessment (`job-change-fit-assessment`) uses it to judge closeness of experience and to identify missing technical requirements.
