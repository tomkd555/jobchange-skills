# English Resume Template (Reverse-Chronological)

## How to use

- Choose this style by default, for a move within the same field where the work history runs without breaks (sources E8, E13, E15).
- Keep the resume to one page; go to two only past ten years of experience (source E8). Give 3 to 5 bullets to the most recent role where the profile supports it; never pad with invented bullets. Give each earlier role 3, at one or two lines per bullet (sources E4, E8).
- Write the current role in the present tense and every past role in the past tense (source E4). Start each bullet with an action verb and drop the subject "I".
- Keep the file ATS-readable: one column, no tables, text boxes, images or skill bars, name and contact details in the body rather than a header or footer, the standard headings below, a standard 10 to 12 point font, and a text-based PDF or .docx (sources E2, E11, E12, E15).
- Never include a photo, age, date of birth, gender or marital status (sources E1, E4, E15).
- `{profile.…}` marks a field of profile.json, `{…}` marks input from elsewhere (the job posting, company research, the date of writing). `<!-- -->` lines are notes to the writer and never appear in the finished resume.

## Structure

```markdown
{Full name}
{profile.basic.location} | {phone} | {email} | {LinkedIn URL}
<!-- Required. Only the location comes from profile.json; ask the user for the name and contact details. Keep them in the body, never in a header or footer (sources E11, E12). Drop any line the user does not supply. -->

## Summary
<!-- Required (sources E10, E13, E15). Three or four lines built from {profile.summary}, {profile.basic.years_of_experience} and {profile.basic.current_role}, opening with the point of contact with {job posting}. Close with a single line on work authorisation in Japan (source E15); ask the user for it and leave the line out if the user does not supply it. Never drop this section. -->

## Objective
<!-- Optional. Include only when the user asks for it: a mid-career applicant is served by the Summary alone, and E15 treats "Objective" as the wrong label for an experienced candidate. Drop the whole section when it is not used. -->

## Work Experience
<!-- Required. List {profile.career_history[]} newest first by the start month in period. Concurrent roles each get their own entry. -->

### {profile.career_history[].role} - {profile.career_history[].company}
{profile.career_history[].period} | {location}
<!-- Ask the user for the company's own English name rather than translating it yourself. Write the period as month and year. Drop the location when the user does not supply it. -->

- {action verb} … {profile.career_history[].achievements[].description}, {profile.career_history[].achievements[].metric}
- {action verb} … {profile.career_history[].responsibilities[]}
<!-- Carry every figure across from metric exactly as written; do not round it and do not invent one. An achievement whose metric is null gets a bullet with scope and role and no number. Write fewer bullets rather than filling the count with something profile.json does not support. -->

## Education
<!-- Required, and placed after Work Experience for a mid-career applicant (sources E8, E14, E15). One line per entry in {profile.basic.education[]}, newest first. Name the institution and the field of study, and give the graduation month and year. Do not state a degree title that profile.json does not record. -->

## Skills
<!-- Required. Group {profile.skills.technical[]} and {profile.skills.business[]} under short labels. Close with a Certifications line drawn from {profile.skills.certifications[]}, using each certification's official English name; ask the user when the English name is unclear. Do not claim years of experience or proficiency levels, which profile.json does not record. Drop the Certifications line when the array is empty. -->

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

Backend engineer and team lead with 8 years building e-commerce core systems in Python on AWS. Led the staged migration of a payment platform from a monolith to microservices, cutting peak API response time from an average of 820ms to 310ms (about 62% improvement). Rebuilt the release pipeline, raising deployment frequency from weekly to daily (about 5x). Managed a team of 5 engineers, including technical interviewing. {Work authorisation in Japan}

## Work Experience

### Backend Engineer (Contract, Concurrent) - Kakuu Healthcare Lab Co., Ltd.
April 2023 - June 2026 | Tokyo, Japan

- Implemented the booking system API in Python on GCP.
- Moved slot inventory calculation to real time, cutting the average wait before a booking is confirmed from 12 seconds to 2 seconds.

### Backend Engineer / Team Lead - Kakuu RetailTech Co., Ltd.
October 2021 - June 2026 | Tokyo, Japan

- Led the staged migration of the payment platform from a monolith to microservices, cutting peak API response time from an average of 820ms to 310ms (about 62% improvement).
- Rebuilt the release process around CI/CD, raising deployment frequency from weekly to daily (about 5x) and cutting mean incident recovery time from 4 hours to 40 minutes.
- Designed and implemented the core e-commerce API in Python on AWS.
- Managed a team of 5 engineers and ran technical interviews.

### Software Engineer - Kakuu System Solutions Co., Ltd.
April 2018 - March 2021 | Tokyo, Japan

- Built business systems on contract in Java and Oracle.
- Gathered client requirements and produced the basic design documents.
- Optimised the inventory management batch, cutting its overnight run time from 6 hours to 2.5 hours.

## Education

Kakuu Institute of Technology, Faculty of Information Engineering - graduated March 2018

## Skills

- Languages: Python, Java
- Cloud and infrastructure: AWS (ECS, Lambda, RDS), Terraform, Docker
- Databases: PostgreSQL
- Practices: requirements definition, agile development (Scrum), technical interviewing, team management
- Certifications: Applied Information Technology Engineer; AWS Certified Solutions Architect - Associate

## Languages

- Japanese: native
- English: TOEIC 850; reads technical documentation and holds simple conversation
```
