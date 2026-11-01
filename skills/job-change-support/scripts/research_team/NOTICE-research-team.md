# Scripts copied from research-team

The scripts in this directory come from research-team
(https://github.com/tomkd555/research-skill, `plugins/research-team/skills/research-team/scripts/`,
commit 2d3a84d). Their tests live in that repository. `screen_claims.py` and the literature-review
scripts were left out: the company research procedure has neither a screening wave nor an academic
route.

| File | Changes |
|---|---|
| `check.py` | the grade enumeration is `A`, `B`, `C`, `D` (this skill's `references/evidence-grading.md`); an item with `paper` set is rejected; the `paper_search` import and the abstract check are removed |
| the other six | copied unchanged |

`scripts/tests/test_research_check.py` covers the two changes. To update the copies, copy the files
again, re-apply the two changes to `check.py`, and run that test.

MIT License

Copyright (c) 2026 tomkd555

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
