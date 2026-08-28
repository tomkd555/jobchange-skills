# English Resume Template (Combination)

## How to use

- Choose this style for a move that changes industry or job function, where the skills and results have to be read before the job titles (sources E9, E5). Skills and achievements come first; the work history stays and is listed newest first.
- Keep the resume to one page; go to two only past ten years of experience (source E8). Give each skill group 2 to 4 achievement bullets and each role in the work history one or two lines, at one or two lines per bullet (sources E4, E8).
- Write the current role in the present tense and every past role in the past tense (source E4). Start each bullet with an action verb and drop the subject "I".
- Keep the file ATS-readable: one column, no tables, text boxes, images or skill bars, name and contact details in the body rather than a header or footer, the standard headings below, a standard 10 to 12 point font, and a text-based PDF or .docx (sources E2, E11, E12, E15). Name the skill groups after terms the job posting itself uses, so the standard "Skills" heading still carries the keywords.
- Never include a photo, age, date of birth, gender or marital status (sources E1, E4, E15).
- `{profile.…}` marks a field of profile.json, `{…}` marks input from elsewhere (the job posting, company research, the date of writing). `<!-- -->` lines are notes to the writer and never appear in the finished resume.

## Structure

```markdown
{Full name}
{profile.basic.location} | {phone} | {email} | {LinkedIn URL}
<!-- Required. Only the location comes from profile.json; ask the user for the name and contact details. Keep them in the body, never in a header or footer (sources E11, E12). Drop any line the user does not supply. -->

## Summary
<!-- Required (sources E10, E13, E15). Three or four lines built from {profile.summary}, {profile.basic.years_of_experience} and {profile.basic.current_role}. Because the target function differs from the current one, open with what carries across rather than with the current job title. Close with a single line on work authorisation in Japan (source E15); ask the user for it and leave the line out if the user does not supply it. Never drop this section. -->

## Objective
<!-- Optional. Include only when the user asks for it: a mid-career applicant is served by the Summary alone, and E15 treats "Objective" as the wrong label for an experienced candidate. Drop the whole section when it is not used. -->

## Skills
<!-- Required, and placed before Work Experience in this style. Build 3 to 4 groups out of {profile.skills.technical[]}, {profile.skills.business[]} and {profile.skills.portable[].skill}, ordered by how close each is to {job posting}. Under each group put the achievement bullets from {profile.career_history[].achievements[]} that belong to it, naming the employer in the bullet so the reader can tie the result to a job. Close with a Certifications line drawn from {profile.skills.certifications[]}, using each certification's official English name. Do not put one achievement under two groups. -->

### {Skill group name}
- {action verb} … {profile.career_history[].achievements[].description}, {profile.career_history[].achievements[].metric} ({profile.career_history[].company})
<!-- Carry every figure across from metric exactly as written; do not round it and do not invent one. A group whose achievements all have a null metric gets bullets that state scope and role with no number. -->

## Work Experience
<!-- Required. List {profile.career_history[]} newest first by the start month in period, one entry per role. Keep each entry to the title, employer, dates and one line of scope; the results have already been given under Skills, so do not repeat them here. Concurrent roles each get their own entry. -->

### {profile.career_history[].role} - {profile.career_history[].company}
{profile.career_history[].period} | {location}
<!-- Ask the user for the company's own English name rather than translating it yourself. Write the period as month and year. Drop the location when the user does not supply it. -->

- {one line from profile.career_history[].responsibilities[]}

## Education
<!-- Required, and placed after Work Experience for a mid-career applicant (sources E8, E14, E15). One line per entry in {profile.basic.education[]}, newest first. Name the institution and the field of study, and give the graduation month and year. Do not state a degree title that profile.json does not record. -->

## Languages
<!-- Required for applications to foreign-affiliated employers in Japan (source E15). One line per entry in {profile.skills.languages[]}, splitting speaking from reading and writing where the level says so. A JLPT level is optional. -->

## Additional Information
<!-- Optional. Use it only for material the sections above cannot hold and the job posting asks for. Drop the whole section when there is nothing to put in it. -->
```

## Example

```markdown
<!-- English company and school names below were supplied by the user; do not translate names yourself. -->

{Full name}
Tokyo, Japan | {phone} | {email} | {LinkedIn URL}

## Summary

Backend engineer with 8 years of system design, most recently as a team lead, moving from e-commerce into payments infrastructure. Data-driven: shows the effect of every improvement in measured numbers. Led a staged monolith-to-microservices migration and rebuilt a release pipeline, with the results below. Managed a team of 5 engineers, including hiring and technical interviewing. {Work authorisation in Japan}

## Skills

### Platform Migration and Modernisation

- Led the staged migration of the payment platform from a monolith to microservices, cutting peak API response time from an average of 820ms to 310ms (about 62% improvement) (Kakuu RetailTech Co., Ltd.).
- Rebuilt the release process around CI/CD, raising deployment frequency from weekly to daily (about 5x) and cutting mean incident recovery time from 4 hours to 40 minutes (Kakuu RetailTech Co., Ltd.).

### Backend API Design and Performance

- Moved slot inventory calculation to real time, cutting the average wait before a booking is confirmed from 12 seconds to 2 seconds (Kakuu Healthcare Lab Co., Ltd.).
- Optimised the inventory management batch, cutting its overnight run time from 6 hours to 2.5 hours (Kakuu System Solutions Co., Ltd.).
- Designed and implemented core e-commerce APIs in Python on AWS (ECS, Lambda, RDS).

### Team Leadership and Hiring

- Managed a team of 5 engineers and ran technical interviews (Kakuu RetailTech Co., Ltd.).
- Gathered client requirements and produced basic design documents for contracted business systems (Kakuu System Solutions Co., Ltd.).

Certifications: Applied Information Technology Engineer; AWS Certified Solutions Architect - Associate

## Work Experience

### Backend Engineer (Contract, Concurrent) - Kakuu Healthcare Lab Co., Ltd.
April 2023 - June 2026 | Tokyo, Japan

- Booking system API implementation in Python on GCP.

### Backend Engineer / Team Lead - Kakuu RetailTech Co., Ltd.
October 2021 - June 2026 | Tokyo, Japan

- Core e-commerce API design and implementation; technical lead for the payment platform migration.

### Software Engineer - Kakuu System Solutions Co., Ltd.
April 2018 - March 2021 | Tokyo, Japan

- Contracted business system development in Java and Oracle.

## Education

Kakuu Institute of Technology, Faculty of Information Engineering - graduated March 2018

## Languages

- Japanese: native
- English: TOEIC 850; reads technical documentation and holds simple conversation
```
