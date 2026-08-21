# profile.json 仕様

job-change-support スキル群における、利用者プロファイル profile.json の原本である。`scripts/validate_profile.py` の実装は、この仕様に厳密に従う。

profile.json は転職支援スキル群の「利用者データの単一の原本」である。経歴・スキル・転職の軸・志望対象を1か所に集約する。後続のサブスキル（企業研究・応募書類作成・面接対策・試験対策）は、すべてこの profile.json を参照する。同じ情報を複数の場所に持たない。

## 配置

- 原本の配置先: `{DATA_ROOT}/career-private/profile.json`
- スキル本体フォルダ（`skills/job-change-support/`）に利用者データを置かない。`assets/profile_example.json` は記入例であり、実データではない。

## ルート構造

```json
{
  "schema_version": "2.0",
  "updated_at": "2026-07-12",
  "summary": "",
  "basic": { },
  "career_history": [ ],
  "career_gaps": [ ],
  "skills": { },
  "strengths": [ ],
  "job_change_axis": { },
  "company_score_axes": [ ],
  "targets": { },
  "salary": { },
  "notes": ""
}
```

| フィールド | 型 | 必須/任意 | 意味・記入基準 |
|---|---|---|---|
| `schema_version` | string | 必須 | 仕様のバージョン。現行は `"2.0"`。`"1.0"`・`"1.1"` も読める（後述「バージョンと移行」）。欠落は ERROR |
| `updated_at` | string | 任意 | `YYYY-MM-DD` 形式の最終更新日。更新のたびに書き直す。欠落は WARN |
| `summary` | string | 任意 | 職務要約。3〜4文で経験の全体像を示す |
| `basic` | object | 必須 | 基本情報。後述 |
| `career_history` | array | 必須 | 職歴の配列。1件以上必須。後述 |
| `career_gaps` | array | 任意 | 空白期間の説明の配列。後述 |
| `skills` | object | 任意 | 保有スキル。全カテゴリが空だと WARN。後述 |
| `strengths` | array | 任意 | 強みの短文の列挙。応募書類・面接の自己 PR の素材にする。行動証拠・他者フィードバックに基づく根拠付きの深化は `job-change-self-analysis` で行える（原本は同スキルの `self_analysis.json`。ここへは短文のみを反映する） |
| `job_change_axis` | object | 必須 | 転職の軸。後述 |
| `company_score_axes` | array | 2.0 のみ任意 | 企業スコアの採点に使う軸と重みの申告。`schema_version` が `2.0` のときにだけ有効。後述 |
| `targets` | object | 任意 | 志望対象。全カテゴリが空だと WARN。後述 |
| `salary` | object | 任意 | 年収。後述 |
| `notes` | string | 任意 | 補足メモ。選考上の留意点など |

## basic

基本情報。

| フィールド | 型 | 必須/任意 | 意味・記入基準 |
|---|---|---|---|
| `current_role` | string | 必須 | 現職の役割・肩書き。欠落は ERROR |
| `years_of_experience` | number | 任意 | 通算の実務経験年数 |
| `location` | string | 任意 | 居住地（都道府県レベルで足りる） |
| `education` | array | 任意 | 学歴の文字列の配列。新しい順に並べる |

## career_history

職歴の配列。1件以上必須。新しい職歴を先頭に置く。各要素は次のフィールドを持つ。

同じ時期に複数の職に就いていた場合（兼務・出向・副業・自営）は、それぞれを1件の要素として持ち、`period` が重なることを許容する。重なりは不整合ではない。どの立場での在籍かは `role` に書き分ける（例「バックエンドエンジニア」「業務委託（副業）」）。

| フィールド | 型 | 必須/任意 | 意味・記入基準 |
|---|---|---|---|
| `company` | string | 必須 | 在籍企業名。欠落は ERROR |
| `period` | string | 必須 | 在籍期間。`YYYY-MM〜YYYY-MM` 形式。在職中は `〜現在`。欠落は ERROR |
| `role` | string | 必須 | 担当した役割・役職。欠落は ERROR |
| `responsibilities` | array | 任意 | 担当業務の文字列の配列 |
| `achievements` | array | 任意 | 実績の配列。後述 |

### achievements

各要素は実績1件を表す。

| フィールド | 型 | 必須/任意 | 意味・記入基準 |
|---|---|---|---|
| `description` | string | 任意 | 実績の説明 |
| `metric` | string または null | 任意 | 定量値。「応答時間を40%短縮」「売上を年3000万円増」のように、数値・割合・金額で示す。定量化できない実績は `null` にする |
| `project` | string | 任意 | 案件・プロジェクトの呼び名。1つの職で複数の案件を並行して回した場合に、どの案件の成果かを区別する。案件が1つだけの職では書かない |
| `period` | string | 任意 | その案件の期間。`YYYY-MM〜YYYY-MM` 形式。在籍中の案件は `〜現在`。在籍期間の中に収まる。案件が1つだけの職では書かない |

`metric` は可能な限り定量値で埋める。全職歴を通して定量的な `metric` が1件もない場合、`validate_profile.py` は WARN を出す。`metric` には本人が述べた数値をそのまま書く。

`project` と `period` は任意であり、`validate_profile.py` は検査しない。聞き取りメモとの一致は監査担当（`job-change-profile-auditor`）が確かめる。

## career_gaps

空白期間（6か月以上、どの職歴の在籍期間にも覆われない期間）の説明の配列。各要素は次のフィールドを持つ。

| フィールド | 型 | 必須/任意 | 意味・記入基準 |
|---|---|---|---|
| `period` | string | 必須 | 空白期間。`YYYY-MM〜YYYY-MM` 形式。形式不一致・欠落は WARN |
| `explanation` | string | 必須 | 空白期間の理由。欠落・空は WARN |
| `activities` | array | 任意 | 期間中に行った活動の文字列の配列 |

どの職歴の在籍期間にも覆われない6か月以上の期間があり、対応する `career_gaps` の記載がないと、`validate_profile.py` は WARN を出す。この検査は `career_history[].period` を全件解析できる場合に限って行う。判定は全職歴の在籍期間の和集合に対して行うため、在籍期間の重なる職歴があっても空白を誤検出しない。

## skills

保有スキル。カテゴリ別に持つ。全カテゴリが空だと WARN。

| フィールド | 型 | 意味・記入基準 |
|---|---|---|
| `technical` | array | 技術スキルの文字列の配列（言語・フレームワーク・クラウドなど） |
| `business` | array | 業務スキルの文字列の配列（マネジメント・要件定義など） |
| `languages` | array | 語学の配列。各要素は `{"language": "英語", "level": "TOEIC 850"}` の形。形式不一致は WARN |
| `certifications` | array | 保有資格の文字列の配列 |
| `portable` | array | ポータブルスキルの配列。各要素は `{"skill": string, "category": "対課題" または "対人", "note": string（任意）}` の形。厚生労働省のポータブルスキル9要素（仕事のし方5・人との関わり方4）を補助分類として使う。`category` が「対課題」「対人」以外だと WARN |

## job_change_axis

転職の軸。転職理由・譲れない条件・望ましい条件を分けて持つ。応募書類の志望動機と面接の一貫性の土台になる。

| フィールド | 型 | 必須/任意 | 意味・記入基準 |
|---|---|---|---|
| `reasons` | array | 必須 | 転職理由の文字列の配列。1件以上必須（空だと ERROR）。現状の不満ではなく、次に実現したいことで書く。建設的な言い換えへの深化は `job-change-self-analysis` で行える（原本は同スキルの `self_analysis.json` の `reason_for_change`。ここへは短文のみを反映する） |
| `conditions` | array | **2.0 で必須** | 条件の配列。譲れない条件と望ましい条件を、軸・演算子・しきい値の形で構造化して持つ。後述 |
| `work_character_preferences` | array | **2.0 で必須** | 8つの作業特性それぞれへの希望度。過不足なく8件持つ。後述 |
| `must_conditions` | array | 1.x のみ | 譲れない条件の自由文の配列。2.0 では `conditions` へ移す。2.0 で非空なら WARN |
| `want_conditions` | array | 1.x のみ | 望ましい条件の自由文の配列。2.0 では `conditions` へ移す。2.0 で非空なら WARN |
| `priority_note` | string | 任意 | 必須条件の優先順位と、次に軸を再評価する時期のメモ |

### conditions（2.0）

条件の唯一の置き場所である。自由文と構造化データを並存させると同じ条件が2か所に載るため、1.x の `must_conditions` / `want_conditions` の文言は `statement` へ移し、元の配列は空にする。

| フィールド | 型 | 必須/任意 | 意味・記入基準 |
|---|---|---|---|
| `id` | string | 必須 | 条件の識別子。`^[a-z0-9][a-z0-9-]*$`。重複は ERROR。適合性評価の `must_condition_results[].ref` の参照先になる |
| `level` | string | 必須 | `must`（譲れない）／`want`（あれば望ましい）。他の値は ERROR |
| `statement` | string | 必須 | 条件の文言。面接・条件交渉で使う言葉で書く。空は ERROR |
| `axis` | string または null | 必須 | `references/screening-axes.md` の8軸 id のいずれか、または `null`（8軸に当てはまらない質的条件）。他の値は ERROR |
| `operator` | string | 必須 | `>=` / `<=` / `==` / `in` / `qualitative`。他の値は ERROR |
| `value` | number / string / array / null | 条件付き必須 | 比較する値。`operator` が `qualitative` 以外なのに `null` なら ERROR |
| `unit` | string | 任意 | `yen` / `h_month` / `days_year` / `ratio` / `none`。他の値は ERROR |
| `verification` | string | 必須 | どこで確認できるか。`posting`（求人票）／`research`（企業研究）／`interview`（面接）／`unverifiable`。他の値は ERROR |
| `priority` | integer | 任意 | 1が最優先。`level=must` の中での順位。欠落・重複は WARN |
| `note` | string | 任意 | 補足 |

```json
{
  "id": "cond-remote",
  "level": "must",
  "statement": "フルリモートが制度として保証されていること",
  "axis": "remote_certainty",
  "operator": "==",
  "value": "guaranteed",
  "unit": "none",
  "verification": "posting",
  "priority": 1
}
```

`axis` が `null` の条件は求人票からの機械的な判定ができない。`operator` を `qualitative` にし、`verification` を `research` または `interview` にする。この種の条件は求人検索の分類には用いず、適合性評価と面接での確認へ回す。

### work_character_preferences（2.0）

8つの作業特性それぞれに希望度を持たせる。**過不足なく8件**必要である（欠落・重複は ERROR）。「不要である」も明示させることで、未記入と無関心を区別する。特性 id の定義は `references/screening-axes.md` にある。

| フィールド | 型 | 必須/任意 | 意味・記入基準 |
|---|---|---|---|
| `trait` | string | 必須 | 8特性 id のいずれか。既定値以外・重複・欠落は ERROR |
| `desire` | string | 必須 | `must`（満たさないなら見送る）／`important`（重視する）／`neutral`（どちらでもよい）／`not_required`（不要である）。他の値は ERROR |
| `statement` | string | 条件付き必須 | 本人の言葉での補足。`desire=must` のときは必須（適合性評価で必須条件として文言が出るため） |
| `note` | string | 任意 | 補足 |

`desire=must` の特性は `conditions[level=must]` と同格の必須条件として扱う。適合性評価の `must_condition_results` はこの両方を対象にするため、同じ条件を2か所へ二重登録しない。

### 必須条件の件数

「必須条件は3件程度まで」のルールは、`conditions[level=must]` と `work_character_preferences[desire=must]` の**合計**で数える。合計が4件以上なら WARN とする。

### 年収の扱い

譲れない年収下限は `conditions`（`axis=salary_condition`）に、希望額は `salary.desired` に置く。前者は求人検索のしきい値として使い、後者は適合性評価の報酬次元が使う。下限が希望額を上回る場合は WARN とする。

## company_score_axes（2.0）

企業スコア（0〜100点）の採点に使う軸と重みの申告である。トップレベルの任意の配列であり、`schema_version` が `2.0` のときにだけ有効である。`1.0` / `1.1` にはこのフィールドが無く、書かれていても検査しない。

定量候補軸9個・点数への換算・重みの配分の規則の原本は `job-change-company-research/references/company-score-rubric.md` にある。企業研究へ渡すのは、`kind` が `quantitative` の軸の識別子の配列だけである。`weight`・`thresholds` と、定性軸の `label`・`definition`・`judgment` は渡さない。定性軸の記述は利用者が自分の言葉で書いたものであり、Web ツールを持つエージェントへ渡さない。

```json
"company_score_axes": [
  {
    "axis": "compensation_level",
    "kind": "quantitative",
    "weight": 40,
    "thresholds": {"zero": 4500000, "full": 7000000}
  },
  {"axis": "annual_holidays", "kind": "quantitative", "weight": 25},
  {
    "axis": "discretion",
    "kind": "qualitative",
    "weight": 35,
    "label": "裁量の大きさ",
    "definition": "設計方針を自分で決められること",
    "judgment": [
      {"score": 100, "condition": "求人票に設計裁量の記載があり、面接でも確認できた"},
      {"score": 50, "condition": "求人票に記載があるが未確認"},
      {"score": 0, "condition": "上位者の承認が必要と明記されている"}
    ]
  }
]
```

| フィールド | 型 | 必須/任意 | 意味・記入基準 |
|---|---|---|---|
| `axis` | string | 必須 | 軸の識別子。空は ERROR。同じ軸が2回以上現れるのも ERROR。定量軸では company-score-rubric.md の定量候補軸9個のキーのいずれかであり、他の値は ERROR。定性軸では利用者が付ける識別子（半角英小文字・数字・アンダースコア）であり、他の文字を含むと ERROR |
| `kind` | string | 必須 | `quantitative`（公表された数値を線形式で点数へ換算する軸）／`qualitative`（利用者が判定条件を決める軸）。他の値は ERROR |
| `weight` | integer | 必須 | 重み。1以上100以下の整数。他の値は ERROR。全軸の合計が 100 でなければ ERROR |
| `thresholds` | object | 定量軸のみ任意 | 点数の基準の上書き。`zero`（0点に相当する水準）と `full`（100点に相当する水準）をいずれも数値で持つ。定性軸に付けると ERROR。`zero` と `full` が数値でない場合、および両者が等しい場合は ERROR |
| `label` | string | 定性軸で必須 | 利用者の言葉での呼び名。空は ERROR |
| `definition` | string | 定性軸で必須 | 何をもってそう言うかの定義。判断できる粒度まで具体化する。空は ERROR |
| `judgment` | array | 定性軸で必須 | 判定条件の配列。1件以上必要。後述 |
| `note` | string | 任意 | その軸を選んだ理由を利用者の言葉で書く |

`thresholds` を書かない定量軸には、統計に基づく既定値を使う。既定値の原本は `job-change-fit-assessment/scripts/calculate_company_score.py` の定数であり、本文書は数値を持たない。既定値を持たない軸は、`thresholds` を書くまで採点されない。処遇水準（`compensation_level`）は既定値を持たない。この軸の基準は利用者の現年収と希望年収から決める。

### judgment（定性軸）

各要素は判定条件1件を表す。

| フィールド | 型 | 必須/任意 | 意味・記入基準 |
|---|---|---|---|
| `score` | integer | 必須 | その条件に合致したときの点数。0以上100以下の整数。他の値は ERROR |
| `condition` | string | 必須 | 何が確認できたらその点数かを書く。空は ERROR |

`score` の降順に並べ、上から順に条件を当てはめて最初に合致したものを採用する。降順に並んでいなければ WARN とする。どの条件にも当てはまらない場合の点数は `null`（判定できない）とし、中間の点数を推測で置かない。

定性軸は、`label`・`definition`・`judgment` のすべてがそろって初めて採点に入る。判定条件を書けない事柄は採点に入れず、面接での確認事項へ回す。

重みを配分したあとは、架空2社の比較で検算する。配分した重みで2社を採点し、「実際にどちらを選ぶか」という問いへの答えと点数の高い側が一致するかを確かめる（手順は company-score-rubric.md にある）。

申告した軸が、`job_change_axis` の必須条件（`conditions[level=must]`）や作業特性の希望度（`work_character_preferences`）と食い違うことがある。その場合、どちらが本当かをこの文書の側で決めない。両方を利用者へ提示し、本人に選ばせる。

配列が無い場合は、採点する軸の申告が無いものとして扱う。企業スコアは算出せず、軸と重みを仮定して採点しない。

## targets

志望対象。全カテゴリが空だと WARN。

| フィールド | 型 | 意味・記入基準 |
|---|---|---|
| `industries` | array | 志望業界の文字列の配列 |
| `roles` | array | 志望職種・ポジションの文字列の配列 |
| `companies` | array | 志望企業名の文字列の配列。企業研究サブスキルはここを起点に企業別ディレクトリを作る |

## salary

年収。単位は円。

| フィールド | 型 | 意味・記入基準 |
|---|---|---|
| `current` | number または null | 現年収 |
| `desired` | number または null | 希望年収 |

## 検証規則の要約

`validate_profile.py` は次を検査する。ERROR が1件でもあれば FAIL（終了コード 1）、ERROR 0件なら PASS（終了コード 0。WARN は許容）。

### ERROR（プロファイルとして成立しない）

- JSON として読み込めない
- `schema_version` の欠落または空
- `basic.current_role` の欠落または空
- `career_history` が空、または各要素で `company`・`period`・`role` のいずれかが欠落・空
- `job_change_axis.reasons` が空（有効な理由が1件もない）

`schema_version` が `2.0` のときは、次も ERROR とする。

- `conditions` が配列でない、または欠落している
- `conditions[]` の `id` の形式不一致・重複、`level` の値域外、`statement` の空、`axis` の値域外、`operator` の値域外、`verification` の値域外
- `operator` が `qualitative` 以外なのに `value` が `null`
- `unit` があるのに `yen`／`h_month`／`days_year`／`ratio`／`none` のいずれでもない
- `work_character_preferences` が配列でない、または欠落している
- `work_character_preferences` が8特性を過不足なく持たない（欠落・重複・未知の `trait`）
- `desire` の値域外、または `desire=must` なのに `statement` が空
- `company_score_axes` があるのに配列でない、またはその要素がオブジェクトでない
- `company_score_axes[].axis` の空・重複、`kind` の値域外、`kind` が `quantitative` の軸の `axis` が定量候補軸9個にない
- `kind` が `qualitative` の軸の `axis` が、半角英小文字・数字・アンダースコア以外の文字を含む
- `weight` が1以上100以下の整数でない、または `weight` の合計が 100 でない
- `thresholds` を `kind` が `qualitative` の軸が持つ、`zero`・`full` が数値でない、または `zero` と `full` が等しい
- `kind` が `qualitative` の軸で、`label`・`definition` が空、`judgment` が1件以上の配列でない、`judgment[].score` の値域外、`judgment[].condition` が空

### WARN（成立するが情報不足で成果物の質を下げる）

- 全職歴を通して定量的な `metric`（achievements の metric）が1件もない
- `skills` の全カテゴリが空
- `targets` の全カテゴリが空
- `updated_at` の欠落
- `schema_version` が既知のバージョン（`1.0`／`1.1`／`2.0`）以外である
- `schema_version` が `1.0` または `1.1` である（2.0 への移行を推奨する）
- `career_history[].period` が `YYYY-MM〜YYYY-MM` または `YYYY-MM〜現在` の形式でない
- `career_history[].period` が全件解析可能な場合に、どの職歴の在籍期間にも覆われない6か月以上の空白があり、対応する `career_gaps`（期間が重なるもの）がない
- `skills.languages` の要素が `{"language","level"}` を持つオブジェクトでない
- `salary.current` / `salary.desired` が number でも null でもない
- 必須条件の件数が4件以上である（1.x では `must_conditions` の件数、2.0 では `conditions[level=must]` と `work_character_preferences[desire=must]` の合計）
- `career_gaps[].period` の形式不一致、または `explanation` の欠落・空
- `skills.portable[].category` が「対課題」「対人」以外である

`schema_version` が `2.0` のときは、次も WARN とする。

- `conditions` に `level=must` が1件もない（必須条件がないと求人検索の選別が働かない）
- 同じ `axis` に `level=must` の条件が複数ある（判定では最も厳しいしきい値を採用する）
- `level=must` の条件に `priority` がない、または `priority` が重複している
- `must_conditions` / `want_conditions` が空でないまま残っている（移行漏れ）
- 必須の年収下限が `salary.desired` を上回っている
- `company_score_axes` が空配列である（採点する軸を1つも選んでいない）
- `company_score_axes` に `compensation_level` がない（既定で選択済みの軸である）
- `judgment` が `score` の降順に並んでいない

## バージョンと移行

| `schema_version` | 扱い |
|---|---|
| `1.0` / `1.1` | 従来の検査規則だけを適用する。`conditions` / `work_character_preferences` の欠落を検査せず、`company_score_axes` も検査しない。移行を促す WARN を1件出す |
| `2.0` | 従来の規則に加え、上記の 2.0 規則を適用する |

**1.x のプロファイルは、そのままでも検証を PASS する。** ゲートは壊れない。ただし 1.x のままでは下流のサブスキルがフォールバック動作になる。

| スキル | 1.x のときの動き |
|---|---|
| `job-change-job-search` | 求人の観測は通常どおり行うが、8軸の判定ができないため全件を「追加調査候補」とし、総合判定を「判定不能」にする |
| `job-change-fit-assessment` | 作業特性の一致と志向の一致の score を `null`（判断保留）にし、理由を verdict に書く。採点する軸の申告が無いため、企業スコアも算出しない |

**自動移行は行わない。** 自由文の条件（例「モダンな技術スタックが整備されていること」）を軸・演算子・しきい値へ機械的に割り付けることは推測であり、「事実を創作しない」原則に反する。移行は `job-change-profile` の対話（条件の構造化）で行う。
