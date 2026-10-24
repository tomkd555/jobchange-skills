---
name: job-change-decision
description: >-
  Decision support for a job change in Japan: the user compares two to five postings or offers that
  have a posting check, and the skill writes out the options so the user can decide. It records the
  user's work values as conditions in wishes.json (a twelve-item list plus free input, each marked
  must or want with a one-line judging guide), filters by the required conditions, builds the
  comparison items from the active conditions and the posting-check fields that differ, elicits
  weights by swing weighting, shows five rankings side by side (swing, rank-order centroid, equal
  weights, want count, and a ±20% sensitivity check), checks the user's preferred option on three
  tables, and records the decision with the deciding and compromised items and empty follow-up
  slots for three months and one year. The skill never ranks for the user. trigger words: 2 社で迷っ
  ている, 内定をどちらにする, 比較したい, 何を重視するか, 価値観, 意思決定, 条件の重み.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, AskUserQuestion
---

# job-change-decision

Runs in the main session only, with no agent, so nothing personal reaches a web tool. It writes options out, asks about trade-offs and shows the arithmetic; the user decides.

## Principles

1. **Write out, then compare.** The steps follow the counselling components with an effect size behind them (writing out each option, individual feedback, attention to what blocks action) and the pre-screening, in-depth exploration and choice sequence of the PIC model.
2. **The user's conditions are the rows.** No fixed scoring table. The items come from the active conditions in `wishes.json` and from the posting-check fields on which the candidates differ.
3. **Weights come from the candidates' spread.** Swing weighting asks which item the user would move from worst to best first, so the weights reflect the differences on the table. One level of items only; splitting an item inflates its weight.
4. **Never one ranking.** Weighting methods disagree, so five views are shown together and the user reads them.
5. **Record the reasons and the compromises.** A decision made on written grounds leaves less regret, and the follow-up slots show later which compromise mattered.
6. **No lecture on method, no verdict.** A bias note is one sentence, only where it applies: salary anchoring, the focusing illusion on one condition, deadline pressure.

## Path resolution

When dispatched from the hub, `{DATA_ROOT}` is already resolved. Otherwise run `python {HUB_SKILL_DIR}/scripts/jc_config.py --show`; on exit code 2 start `job-change-support` first.

## Data layout

| Path | Contents |
|---|---|
| `career-private/wishes.json` | The conditions, including work values. `{HUB_SKILL_DIR}/references/wishes-format.md` |
| `career-private/matches/{posting id}.json` | Match per condition for each candidate |
| `companies/{slug}/postings/{posting id}/posting-check.json` | The candidates' values |
| `career-private/decisions/{decision id}.json` | The record of one comparison. `references/decision-format.md` |

## Part 1 Work values (before the first comparison)

1. **Start.** When `wishes.json` does not exist, go to item 2 without asking. When it exists, show its active conditions in one table (text, must/want) and ask once whether to update them. When the user keeps them, go to Part 2.
2. **The list.** Show the twelve work values of `references/work-values.md` in one AskUserQuestion of three questions with four options each, multi-select, Japanese labels. The user picks any number.
3. **Free input.** Ask once, in one sentence, for anything the user values that the list lacks.
4. **Must or want.** For each chosen and written item, one question: 必須か希望か.
5. **How to judge.** For each item, propose one sentence saying what to look at in a posting check (`how_to_judge`); the user corrects it.
6. **Record.** Append each item to `wishes.json` as a condition with `kind: "value"` (or `"other"` for free input), `field_id: "custom"`, `source` the work-value id or `user`, `level`, `how_to_judge`, and one `history` entry. Validate with `python {HUB_SKILL_DIR}/scripts/validate_wishes.py`.

Every question text is a complete Japanese sentence with a concrete example, one decision per question, run through the reply lint before asking.

## Part 2 The comparison

### Step 1 Confirm the levels

For each active condition whose `level` the user has not set in this or an earlier session, ask must or want. Conditions set in the job search or Part 1 are not asked again.

### Step 2 Filter by the required conditions

Read each candidate's `matches/{posting id}.json`. A candidate with `not_meets` on a `must` condition leaves the table; say which condition. A candidate with `unknown` stays, marked 不明. Fix the candidates here; none is added later.

### Step 3 Build the items

- One row per active condition (`condition_id`, with its `field_id`).
- One row per posting-check field with a value for at least one candidate and differing values among the candidates (`field_id`, no `condition_id`). Fields equal across all candidates, or `null` for all, are left out.
- A field `null` for some candidates keeps the row; the cell shows 不明 and goes into Step 7.

### Step 4 Values

For a numeric row, take each candidate's value from its posting check (the first entry when a field has two or more sources; say which). For a `custom` row and for a non-numeric field, show the candidates' relevant posting-check passages next to the `how_to_judge` sentence and ask the user to rate each candidate 1 to 5. Write `values` or `ratings` into the decision record.

### Step 5 Weights (swing weighting)

Ask: 「すべての項目が候補の中で最も低い値だとして、1 つだけ最も高い値に変えられるならどの項目ですか」. Remove the answer and repeat until one item remains; the questions number one less than the items. Then ask for 0 to 100 points per item with the first at 100. Record `swing_order` and `swing_points`. When an earlier decision record has the same `field_id` or `condition_id`, propose its points as the default and ask only about new items.

### Step 6 Compute and show

```bash
python {SKILL_DIR}/scripts/validate_decision.py {DATA_ROOT}/career-private/decisions/{decision id}.json --fill --wishes {DATA_ROOT}/career-private/wishes.json
```

Show one table with the five views side by side: the swing ranking, the rank-order centroid ranking, the equal-weight ranking, the want-count ranking, and whether the first place changes when any one weight moves ±20% (`sensitivity.top_changes`, with the items that flip it). Show the weights next to the items. Then the item table: rows are items, columns are candidates, cells the value with unit or 不明.

### Step 7 Check the preferred candidate

Ask which candidate the user leans to. For that candidate show three tables: conditions it does not meet, items on which it is last among the candidates, and its unknown items. Add the one-sentence bias note where it applies.

### Step 8 Record

Write `chosen`, `decisive_fields` (the items the user names as deciding) and `compromised_fields` (the items from Step 7's first two tables), keep `follow_up` empty, run the validator without `--fill` and with `--wishes`, and append the decision id to `wishes.json`'s `used_in`. Tell the user the file path and that the follow-up slots are for 3 か月後 and 1 年後.

## Reply rules

- Conclusion first; the five rankings before any explanation.
- Never say which candidate to take. Never collapse the five views into one score.
- 不明 stays 不明. The absence of a figure is never 0 and never a point against.

## Scripts

| Script | Use |
|---|---|
| `scripts/validate_decision.py` | `{file} [--wishes {wishes.json}] [--json]` validates; `--fill` computes scaled values, weights, scores, rankings and sensitivity in place. Exit 0 PASS, 1 FAIL |

Unit tests: `cd {SKILL_DIR} && python -m unittest discover -s scripts/tests`. A fictitious example is `assets/decision_example.json`.

## References

| File | Holds | Read at |
|---|---|---|
| `references/decision-format.md` | The record, the derived values and the validator | Steps 4 to 8 |
| `references/work-values.md` | The twelve work values with ids, Japanese labels and the O*NET mapping | Part 1 |
| `{HUB_SKILL_DIR}/references/wishes-format.md` | `wishes.json` | Part 1, Step 1 |
| `{HUB_SKILL_DIR}/references/field-catalog.md` | Field ids, directions, labels | Steps 3 and 4 |
