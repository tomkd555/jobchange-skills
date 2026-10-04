# Section: Target companies and roles (targets)

Records the industries, roles, and companies the user aspires to. The first pass skips this section. It is done as a section update right before starting company research or job search. The section catalogue and the definition of reach stages are in `../sections.md`.

## Fields to fill

| Field | Format |
|---|---|
| `targets.industries`, `roles`, `companies` | Free text (their choices cannot be enumerated in advance) |

## Reach stages

| Stage | Condition |
|---|---|
| `skeleton` | At least one category has an item |
| `deep` | Same as skeleton |

## Procedure

Opening question:

- Are there industries, roles, or companies the user aspires to? A company name becomes the starting point for the company-research sub-skill.

When the user wants to move into a role outside their current experience, write the target role into `roles`. The `skills` section of `job-change-profile` reads this and, alongside it, presents candidate skills generally required for that target role (`job-change-profile`'s `references/sections/skills.md`).

Write company names in the user's own words. Normalizing the notation (replacing a name with its formal company name, slugifying it) is the job of the company-research sub-skill, done in `company_index.json`.

## Downstream

Company research (`job-change-company-research`) builds a per-company directory starting from `companies`. Job search (`job-change-job-search`) uses `industries` and `roles`, anonymized, as search conditions.
