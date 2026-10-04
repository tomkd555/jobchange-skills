# English Resume Template (Functional)

## How to use

- Choose this style when the work history has large gaps or breaks in continuity and the reader has to be led by ability first and chronology second (sources E7, E5).
- Weigh the cost first: the section headings become functional area names, which fits poorly with the standard-heading rule that applicant tracking systems rely on (source E12). Where the employer screens through an ATS, prefer `english-resume-combination.md`, which puts skills first while keeping the standard headings.
- Keep the resume to one page; go to two only past ten years of experience (source E8). Give each functional area 3 to 5 bullets where the profile supports it; never pad with invented bullets. Keep each bullet to one or two lines (sources E4, E8). The employment history below lists dates and titles only, with no bullets.
- Write the current role in the present tense and every past role in the past tense (source E4). Start each bullet with an action verb and drop the subject "I".
- Keep the file ATS-readable (sources E2, E11, E12, E15). Use one column with no tables, text boxes, images or skill bars. Put the name and contact details in the body, outside the header and footer. Use a standard 10 to 12 point font and a text-based PDF or .docx. The standard-heading part of that rule is the one this style gives up, for the reason given above.
- Never include a photo, age, date of birth, gender or marital status (sources E1, E4, E15). Never adjust dates to shorten or hide a gap; the employment history states the real months.
- `{profile.…}` marks a field of profile.json, `{…}` marks input from elsewhere (the job posting, company research, the date of writing). `<!-- -->` lines are notes to the writer and never appear in the finished resume.

## Structure

```markdown
{Full name}
{profile.basic.location} | {phone} | {email} | {LinkedIn URL}
<!-- Required. Only the location comes from profile.json; ask the user for the name and contact details. Keep them in the body, never in a header or footer (sources E11, E12). Drop any line the user does not supply. -->

## Summary
<!-- Required (sources E10, E13, E15). Three or four lines built from {profile.summary}, {profile.basic.years_of_experience} and {profile.basic.current_role}, stating the abilities the functional areas below will evidence. Close with a single line on work authorisation in Japan (source E15); ask the user for it and leave the line out if the user does not supply it. Never drop this section. -->

## Objective
<!-- Optional. Include only when the user asks for it: a mid-career applicant is served by the Summary alone, and E15 treats "Objective" as the wrong label for an experienced candidate. Drop the whole section when it is not used. -->

## Skills
<!-- Required, and the centre of this style. Build 3 to 4 functional areas out of {profile.skills.technical[]}, {profile.skills.business[]}, {profile.skills.portable[].skill} and {profile.career_history[].responsibilities[]}, ordered by how close each is to {job posting}. Under each area put the matching bullets from {profile.career_history[].achievements[]}. Close with a Certifications line drawn from {profile.skills.certifications[]}, using each certification's official English name. Do not put one achievement under two areas. -->

### {Functional area name}
- {action verb} … {profile.career_history[].achievements[].description}, {profile.career_history[].achievements[].metric}
<!-- Carry every figure across from metric exactly as written; do not round it and do not invent one. This style does not name the employer in the bullet, so keep every claim inside what profile.json supports. An area whose achievements all have a null metric gets bullets that state scope and role with no number. -->

## Work Experience
<!-- Required. One line per entry in {profile.career_history[]}, newest first by the start month in period: title, employer, and the months. No bullets here: the evidence sits under Skills. Concurrent roles each get their own line. -->

- {profile.career_history[].role}, {profile.career_history[].company}, {profile.career_history[].period}
<!-- Show the real months. A gap recorded in {profile.career_gaps[]} is left as a gap: do not write it into this list, do not stretch a period to cover it, and do not fill it with an entry profile.json does not record. If the employer asks about it, the explanation in career_gaps[].explanation is the answer to give in conversation, kept off the resume. -->

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

Backend engineer with 8 years of experience whose work has centred on three abilities: taking a large system migration from plan to completion, showing the effect of a change in measured numbers, and building a team, including hiring and technical interviewing. Worked in Python on AWS and in Java on Oracle. Managed a team of 5 engineers. {Work authorisation in Japan}

## Skills

### System Migration and Delivery

- Led the staged migration of a payment platform from a monolith to microservices as technical lead, cutting peak API response time from an average of 820ms to 310ms (about 62% improvement).
- Rebuilt a release process around CI/CD, raising deployment frequency from weekly to daily (about 5x) and cutting mean incident recovery time from 4 hours to 40 minutes.
- Structured and prioritised the work of the migration, planning the order in which services were split out.

### Backend Design and Performance

- Designed and implemented core e-commerce APIs in Python on AWS (ECS, Lambda, RDS).
- Moved slot inventory calculation to real time, cutting the average wait before a booking is confirmed from 12 seconds to 2 seconds.
- Optimised an inventory management batch, cutting its overnight run time from 6 hours to 2.5 hours.
- Built business systems on contract in Java and Oracle, gathering client requirements and producing the basic design.

### Team Leadership and Hiring

- Managed a team of 5 engineers, running technical interviews and giving feedback.
- Ran development to an agile (Scrum) cadence and led requirements definition with stakeholders.

Certifications: Applied Information Technology Engineer; AWS Certified Solutions Architect - Associate

## Work Experience

- Backend Engineer (contract, concurrent), Kakuu Healthcare Lab Co., Ltd., April 2023 - June 2026
- Backend Engineer / Team Lead, Kakuu RetailTech Co., Ltd., October 2021 - June 2026
- Software Engineer, Kakuu System Solutions Co., Ltd., April 2018 - March 2021

## Education

Kakuu Institute of Technology, Faculty of Information Engineering - graduated March 2018

## Languages

- Japanese: native
- English: TOEIC 850; reads technical documentation and holds simple conversation
```
