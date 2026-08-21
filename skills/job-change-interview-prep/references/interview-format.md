# 面接対策の成果物の原本仕様（interview-format）

面接対策の成果物 `interview_questions.json`・`interview_answers.json`・`interview_evaluation.json` のフィールド仕様・記入基準・機械的な検証の規則を定める原本である。`scripts/validate_interview_artifacts.py` がこの仕様に照らして機械的に検査する。

出力先は company モードでは `{DATA_ROOT}/companies/{企業スラッグ}/` である。企業非依存のフォールバックモードでは企業スラッグが無いため、利用者が保存先を指定した場合にのみ書き出す。

`interview_questions.json` と `interview_evaluation.json` は、job-change-interview-coach が返した JSON をトップレベルごと保存したものである。`questions`・`evaluations` の配列だけを取り出して保存してはならない。`degraded`・`degraded_reason` が落ちると、その質問群が企業固有のものか企業非依存のフォールバックかをファイルから判別できなくなり、中断からの再開時に合否ゲートを再確認できない。

`interview_answers.json` はコーチの出力ではなく、スキル本体が模擬面接（Step 2）で1問ずつ書き足す。

## degraded と degraded_reason（`interview_questions.json`・`interview_evaluation.json` 共通）

```json
{
  "degraded": false,
  "degraded_reason": null
}
```

| フィールド | 必須 | 記入基準 |
|---|---|---|
| `degraded` | 必須 | 真偽値。企業固有の根拠を用いずに生成・評価した場合に `true`。真偽値でない、または欠落は ERROR |
| `degraded_reason` | 必須 | `degraded` が `true` のときは理由の文字列（空は ERROR）。`false` のときは `null`（`null` 以外は ERROR） |

`degraded` を `true` にする条件は SKILL.md の「目的と原則」と「合否ゲートと差し戻し」が定める。company_research.json が無い場合、company_research.json はあるが topic=selection_process の claims が0件の場合、および Step 3 で企業理解の観点を評価対象外とする場合である。

## interview_questions.json

```json
{
  "degraded": false,
  "degraded_reason": null,
  "questions": [
    {
      "id": "Q001",
      "category": "転職理由",
      "question": "現職を離れようと考えた理由を聞かせてください。",
      "interviewer_intent": "定着性と、転職で解こうとしている課題の一貫性を確認する。",
      "basis": "profile.job_change_axis.reasons[0]"
    }
  ]
}
```

### questions（配列・必須）

配列でない場合は ERROR。空配列は WARN（想定質問が1件も無い成果物は Step 2 で使えない）。

| フィールド | 必須 | 記入基準 |
|---|---|---|
| `id` | 必須 | 質問の識別子。`Q` に続く3桁以上の数字（`Q001` 形式）。欠落・空・形式不一致は ERROR。同一ファイル内での重複は ERROR |
| `category` | 必須 | 質問類型。欠落・空は ERROR。既知の類型でない値は WARN |
| `question` | 必須 | 利用者へ提示する質問文。欠落・空は ERROR |
| `interviewer_intent` | 必須 | 面接官がその質問で確認する評価観点。欠落・空は ERROR |
| `basis` | 必須 | 根拠。company_research の claim id、または profile の該当箇所を指す。欠落・空は ERROR |

`id` は `interview_answers.json` の `question_id` と `interview_evaluation.json` の `question_id` が指す先である。3ファイルを結ぶ唯一の連結キーである。

既知の質問類型は `転職理由`・`志望動機`・`自己PR`・`実績深掘り`・`弱み`・`逆質問`・`ビヘイビアラル`・`ケース` である。この対応の原本は `question-bank.md` の「質問類型と job-change-interview-coach のカテゴリの対応」（外資系の2類型は `foreign-interviews.md`）にある。既知の8値以外を ERROR ではなく WARN とするのは、類型が増えても成果物としては成立するためである。

## interview_answers.json

```json
{
  "answers": [
    {
      "question_id": "Q001",
      "answer": "基盤の設計から運用までを一貫して担いたいと考えたためです。",
      "answered_at": "2026-08-15"
    }
  ]
}
```

模擬面接（Step 2）で、回答を受け取るごとに1件ずつ追記する。途中で中断した場合、`interview_questions.json` の `questions[].id` から本ファイルの `answers[].question_id` を差し引いた集合が「残りの質問」である。再開はこの差分だけで決まり、会話の記憶に依存しない。

### answers（配列・必須）

配列でない場合は ERROR。空配列は WARN（1問も回答していない段階の保存を許容する）。

| フィールド | 必須 | 記入基準 |
|---|---|---|
| `question_id` | 必須 | `interview_questions.json` の `questions[].id` と同じ値。欠落・空・形式不一致は ERROR。重複は ERROR |
| `answer` | 必須 | 利用者の回答をそのまま転記する。要約・言い換え・添削をしない。欠落・空は ERROR |
| `answered_at` | 必須 | 回答した日付（`YYYY-MM-DD`）。欠落・形式不一致は ERROR |

## interview_evaluation.json

```json
{
  "degraded": false,
  "degraded_reason": null,
  "evaluations": [
    {
      "question_id": "Q001",
      "scores": {
        "star": "一部",
        "specificity": "充足",
        "consistency": "充足",
        "company_fit": "一部"
      },
      "feedback": "profile.job_change_axis.reasons[0] と矛盾なく述べている。状況の説明が薄い。",
      "improvement": "claim-012 の開発体制へ触れ、STAR の状況（Situation）を1文足す。"
    }
  ]
}
```

### evaluations（配列・必須）

配列でない場合は ERROR。空配列は WARN。

| フィールド | 必須 | 記入基準 |
|---|---|---|
| `question_id` | 必須 | 評価対象の質問の `id`。欠落・空・形式不一致は ERROR。重複は ERROR |
| `scores` | 必須 | 4観点の判定。オブジェクトでない場合は ERROR。詳細は次節 |
| `feedback` | 必須 | 評価の説明。根拠参照（profile の該当箇所、self_analysis.json の `career_narrative`・`reason_for_change`、または claim id）を含める。欠落・空は ERROR |
| `improvement` | 必須 | 改善案。同じく根拠参照を含める。欠落・空は ERROR |

### scores（オブジェクト・必須）

| キー | 観点 | 値 |
|---|---|---|
| `star` | STAR | `充足` / `一部` / `不足` |
| `specificity` | 具体性 | `充足` / `一部` / `不足` |
| `consistency` | 一貫性 | `充足` / `一部` / `不足` |
| `company_fit` | 企業理解 | `充足` / `一部` / `不足`。`degraded` が `true` のときは `対象外` または欠落 |

`star`・`specificity`・`consistency` が3値のいずれでもない場合は ERROR。

`company_fit` は `degraded` と整合しなければならない。`degraded` が `true`（フォールバックモード）のときは企業理解を評価できないため、`対象外` か欠落のいずれかとし、3段階の値を入れると ERROR とする。`degraded` が `false` のときは3値のいずれかが必須であり、`対象外` は ERROR とする。company_research.json を読んだうえで評価を省いた成果物を、フォールバックと区別できるようにするためである。

各段階の判定基準（アンカー）の原本は `evaluation-rubric.md` にある。ここへは複製しない。検証スクリプトは値が語彙に収まるかだけを見て、判定の当否は見ない。

## 機械的な検証の規則（validate_interview_artifacts.py）

`scripts/validate_interview_artifacts.py` が機械的に検査する。ERROR が1件でもあれば FAIL（終了コード1）、ERROR 0件なら PASS（終了コード0。WARN があっても PASS）。

```
python validate_interview_artifacts.py <artifact.json> [--json] [--questions <interview_questions.json>]
```

検査する成果物の種別は、トップレベルのキーで判別する。`questions`・`answers`・`evaluations` のうち1つだけを持てばその種別とし、1つも持たない場合と2つ以上を持つ場合は ERROR とする。3ファイルは互いに素なキーを持つため、種別を引数で指定させる必要が無い。

`--questions` に `interview_questions.json` のパスを渡すと、`interview_answers.json`・`interview_evaluation.json` の `question_id` が質問側に実在するかを検査する。実在しない場合は ERROR とする。フォールバックモードでは質問ファイルを書き出さない場合があるため、`--questions` は任意とし、渡されないときは相互参照を検査しない。
