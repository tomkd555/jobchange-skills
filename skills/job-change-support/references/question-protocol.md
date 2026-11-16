# Question protocol (question-protocol)

The canonical rules for every AskUserQuestion the skill puts to the user. The procedures under `references/` hold the wording of their questions; this file holds the shape of one call and the check that runs before it. The rules live here only and are not copied into the procedures.

## One question per call

One AskUserQuestion carries exactly one question. Two or more questions are never put in one call.

- A follow-up whose content depends on an answer is the next call, after the answer has arrived. Never "if the first question does not apply, see the second" inside one call.
- The question text names its subject: the condition, the candidate, the work value, the item. A call never points at the previous call's subject with 「この条件」 or 「同じく」 alone.
- Repeated items (one must/want question per condition, one swing-weighting round per item, one lane group) are one call each. Calls are never bundled to save a round trip.

## What the tool does

The question is shaped by the tool, not the other way round.

| Tool fact | What the question must do |
|---|---|
| Every question is answered | Never assume the user can leave it blank. Where "none of these" is a possible answer, including in a multi-select question, put it in as an option (「該当なし」, 「追加しない」) |
| No option is selected in advance | Never write 「既定で選択済み」 or "uncheck to remove". A yes/no is its own question |
| Other is always present and takes free text | Never add an option whose only content is "write it in Other". Every option means something when chosen |
| Two to four options | An item with five or more values is split over several calls, each with its neutral option |
| `header` is at most 12 characters | A short noun that names the subject |
| `multiSelect: true` accepts several answers | Use it when several answers are valid; never split one multi-valued question into several single-valued ones |

## Check before asking

Before every call, in this order. A question that fails a check is fixed before it is asked.

1. **Known answers.** Read the request line, `wishes.json`, the earlier decision records and this conversation. An item already answered is not asked, whether the answer came as a choice, as free text or inside a longer message. A value that follows from an earlier answer is not asked either: show it in the table and ask 「違うところだけ」.
2. **State.** Every option must be selectable now. Drop an option that the state rules out (a file that does not exist, a lane marked "not used" for this sheet, a candidate already filtered out). When one option remains, do not ask; say which one applies and continue.
3. **Earlier answers.** Never ask the same thing under another name. A level set in the job search is not asked again in the decision; a value picked from the work-values list is not asked again as free input.
4. **Options.** In a single-select question the options exclude each other; in a multi-select question they are independent. No two options share a description. The neutral option is present where "none" is a possible answer.

## Contradictory answers

- 「該当なし」 chosen together with other options in a multi-select question, or an answer that conflicts with an earlier one: show the two answers side by side and let the user choose. The skill never picks one.
- An answer the skill cannot map to its options is recorded as given, through Other. It is not bent toward the nearest option.

## Free text

A figure, a name, a sentence to correct (a `how_to_judge` proposal, a job title) is asked in a plain message, one item per message, never through the tool. The tool is for choices between options the skill can list.
