# 適合性評価データの原本（fit-format）

適合性評価の成果物 `fit_assessment.json` のフィールド仕様・検証規則・記入例を定める原本である。`job-change-fit-assessment` スキル本体と `job-change-fit-assessor` エージェントがこのファイルを参照する。判定基準（各次元の score の目安・evidence の付け方）の原本は `references/fit-criteria.md` にある。

## 配置

`fit_assessment.json` の出力先は次のとおりである。

```
{DATA_ROOT}/career-private/fit/{企業スラッグ}/fit_assessment.json
```

利用者プロファイル・自己分析に由来する派生値を含むため、非公開ディレクトリ `career-private/` 配下に置く。Web 送信手段（WebSearch・WebFetch）を持つエージェントへ渡してはならない。企業スラッグは `career-private/company_index.json` で解決済みの値をそのまま使う。形式の原本は job-change-support の `references/company-index-format.md` にある。

## トップレベルの構造

```json
{
  "schema_version": "2.0",
  "slug": "kakuu-cloudworks",
  "assessed_at": "2026-07-25",
  "inputs": { "job_posting": true, "company_research": true, "self_analysis": true, "time_analysis": true, "job_search_screening": true },
  "dimensions": [ /* 7次元。後述 */ ],
  "must_condition_results": [ /* profile の必須条件と ref で1対1。後述 */ ],
  "company_score": { /* 企業スコア（0〜100点）。任意。後述 */ },
  "overall": { "recommendation": "条件付き推奨", "rationale": "…", "open_questions": ["…"] }
}
```

| フィールド | 型 | 必須 | 内容 |
|---|---|---|---|
| `schema_version` | string | 必須 | 現行は `"2.0"`。`"1.0"` も読める（後述「バージョンと移行」） |
| `slug` | string | 必須 | 企業スラッグ。形式の原本は job-change-support の `references/company-index-format.md` にある |
| `assessed_at` | string | 必須 | 評価日。`YYYY-MM-DD` |
| `inputs` | object | 必須 | 各入力の有無を真偽値で記録。2.0 のキーは `job_posting`・`company_research`・`self_analysis`・`time_analysis`・`job_search_screening` の5つ |
| `screening_source` | object | 任意 | 求人検索のスクリーニング結果への参照。`{search_id, result_index, classification, screened_at}`。後述 |
| `dimensions` | array | 必須 | 次元の評価。2.0 では過不足なく7件 |
| `must_condition_results` | array | 必須 | 必須条件の判定。profile の必須条件と1対1 |
| `company_score` | object | 任意 | 企業スコア（0〜100点）。`{total, coverage, provisional, axes, rationale}` |
| `overall` | object | 必須 | 総合判定 |

## dimensions（7次元）

各次元は次の構造を持つ。2.0 の id は7種で、過不足なく全て存在する。

| id | 評価対象 | 主な入力元 |
|---|---|---|
| `experience_proximity` | 求人の要件・業務内容と、本人の実務経験の距離。技術要件の不足は `skill_gap` で3段階に表す | job_posting / profile |
| `aspiration_alignment` | 業務内容が「今後やりたい仕事」に近いか。経験の近さとは独立に評価する | self_analysis / profile / job_posting |
| `work_character_fit` | 8つの作業特性の希望と、求人・企業の実態の一致 | profile / job_posting / company_research / job_search_screening |
| `condition_fit` | 望ましい条件（`level=want`）と勤務条件の一致 | job_posting / profile |
| `culture_fit` | 理念・働き方・評判と、行動証拠・価値観 | company_research / self_analysis |
| `compensation_fit` | 提示レンジと希望年収・業界水準 | job_posting / profile / company_research |
| `time_fit` | 年間拘束時間・実質時給と、時間に関する条件 | time_analysis / job_posting |

**経験の近さと志向の一致を別の軸として扱う。** 経験が近くても、調整・管理・顧客折衝が中心で本人の志向と合わない求人を「推奨」へ押し上げないためである。

```json
{
  "id": "experience_proximity",
  "score": 4,
  "verdict": "判定の要約。1〜数文",
  "skill_gap": "complementable_within_3m",
  "skill_gap_items": [ /* 後述 */ ],
  "evidence": [
    { "source": "job_posting", "ref": "requirements.must[0]", "note": "根拠の説明" }
  ]
}
```

| フィールド | 型 | 内容 |
|---|---|---|
| `id` | string | 上表の7種のいずれか |
| `score` | integer \| null | 1〜5 の整数。判断材料が不足する場合は `null`（判断保留） |
| `verdict` | string | 判定の要約（非空） |
| `evidence` | array | 1件以上。各要素は下記 |
| `skill_gap` | string | `experience_proximity` のみ。後述 |
| `skill_gap_items` | array | `experience_proximity` のみ。後述 |

evidence の各要素:

| フィールド | 型 | 内容 |
|---|---|---|
| `source` | string | `company_research`・`job_posting`・`profile`・`self_analysis`・`time_analysis`・`job_search_screening` のいずれか（`job_search_screening` は 2.0 のみ） |
| `ref` | string | 参照子。company_research の claim id（例 `C012`）、job_posting のフィールドパス（例 `salary.min`）、time_analysis のフィールドパス（例 `annual.binding_hours`）など |
| `note` | string | その evidence が示す内容の説明 |

### skill_gap（技術要件の不足の3段階）

`experience_proximity`（経験の近さ）の内訳として持つ。

| 値 | 意味 |
|---|---|
| `none` | 不足が無い |
| `complementable_within_3m` | 3か月以内に補完できる |
| `needs_6_12m_study` | 6〜12か月の学習が要る |
| `not_applicable_now` | 現時点では応募が難しい |
| `unknown` | 判断材料が不足する |

`skill_gap_items[]` は不足要件ごとの内訳である。`none`・`unknown` のときは空配列でよい。

| フィールド | 型 | 内容 |
|---|---|---|
| `requirement` | string | 求人票の必須・歓迎要件の引用文（非空） |
| `gap_level` | string | `complementable_within_3m`・`needs_6_12m_study`・`not_applicable_now` のいずれか |
| `basis` | string | 段階を分けた根拠（非空）。隣接技術の保有・学習量の見積りなど |
| `evidence` | array | 1件以上 |

`skill_gap` は `skill_gap_items[].gap_level` の**最も重い段階と一致させる**（不一致は ERROR）。総合の見栄えを良くするために全体の段階だけを軽くする経路を塞ぐ。

## must_condition_results

profile の必須条件（`conditions[level=must]` と `work_character_preferences[desire=must]`）と、`ref` で1対1に対応させる。文字列一致ではなく id 集合の一致で検査する。材料が無い条件を憶測で `yes`・`no` にせず、`unknown` を優先する。

```json
{
  "ref": "cond-remote",
  "condition": "リモート勤務が可能であること",
  "met": "yes",
  "negotiable": false,
  "evidence": [ { "source": "job_posting", "ref": "location.remote_policy", "note": "フルリモート可と明記" } ]
}
```

| フィールド | 型 | 内容 |
|---|---|---|
| `ref` | string | profile の `conditions[].id` または `work_character_preferences[].trait`（2.0 で必須。重複は ERROR） |
| `condition` | string | 条件の文言（非空）。`statement` のコピーであり、利用者向けの表示に使う |
| `met` | string | `yes`・`no`・`unknown` のいずれか |
| `negotiable` | boolean | 任意。`met=no` の条件が交渉・制度運用で解消しうるか。既定は `false`。`true` にするには evidence が1件以上要る |
| `evidence` | array | 根拠。`met` が `yes`・`no` のときは1件以上必須。`unknown` のときは空でよい |

## company_score

応募先企業を 0〜100 点で採点した結果である。軸ごとの実測値は、企業研究が `company_research.json` の `company_metrics` へ書く。その実測値を、利用者が `profile.json` の `company_score_axes` で申告した軸と重みで採点した結果は、`profile.json` を読める適合性評価が `company_score` へ書く。

算出は `scripts/calculate_company_score.py` が決定的に行う。定量候補軸9個・点数への換算・基準の決め方・重みの配分・総合点の規則の原本は、job-change-company-research の `references/company-score-rubric.md` にある。統計由来の既定基準の原本は `scripts/calculate_company_score.py` の定数 `DEFAULT_THRESHOLDS` である。

総合点は、利用者が選んだ軸と配分した重みに基づく数値であり、企業そのものの質の絶対評価ではない。異なる利用者の点数どうしを比べない。比べてよいのは、同じ利用者が同じ軸と重みで採点した企業どうしだけである。

```json
"company_score": {
  "total": 72,
  "coverage": 85,
  "provisional": false,
  "axes": [
    {
      "axis": "compensation_level", "kind": "quantitative", "weight": 40,
      "value": 6480000, "unit": "円", "score": 65,
      "threshold_source": "user", "thresholds": { "zero": 4500000, "full": 7000000 },
      "grade": "A", "source_url": "https://..."
    },
    {
      "axis": "tech_discretion", "kind": "qualitative", "weight": 35,
      "value": null, "unit": null, "score": 50,
      "threshold_source": null, "thresholds": null,
      "grade": null, "source_url": null,
      "evidence": "求人票の『設計から関与』の記載に合致した"
    },
    {
      "axis": "annual_holidays", "kind": "quantitative", "weight": 25,
      "value": null, "unit": "日", "score": null,
      "threshold_source": null, "thresholds": null,
      "grade": null, "source_url": null,
      "reason": "企業研究に実測値が無い"
    }
  ],
  "rationale": "点数に効いた軸と、判定できなかった軸を書く"
}
```

| フィールド | 型 | 内容 |
|---|---|---|
| `total` | integer \| null | 総合点。判定できた軸だけの加重平均を四捨五入した 0〜100 の整数。判定できた軸が1つも無い場合は `null` とし、軸も重みも仮定して採点しない |
| `coverage` | integer | 判定できた軸の `weight` の合計（0〜100）。重みの合計が 100 のため、そのまま総合点の裏付けの割合になる |
| `provisional` | boolean | 暫定の点数であること。`coverage` が `calculate_company_score.py` の定数 `COVERAGE_THRESHOLD` を下回るとき、および `total` が `null` のとき `true` |
| `axes` | array | 利用者が申告した軸を申告順に並べる。判定できなかった軸も `score` を `null` にして並べる |
| `rationale` | string | 点数に効いた軸と、判定できなかった軸をその理由とともに書く（非空）。スクリプトが決定的に組み立てる |

`axes` の各要素:

| フィールド | 型 | 内容 |
|---|---|---|
| `axis` | string | 軸の識別子（非空）。profile の `company_score_axes[].axis` をそのまま写す |
| `kind` | string | `quantitative`（公表された数値を線形式で点数へ写す軸）・`qualitative`（利用者が判定条件を決める軸）のいずれか |
| `weight` | integer | 重み。1〜100 の整数。profile の申告をそのまま写す |
| `value` | number \| null | 定量軸の実測値。`company_metrics` の当該軸の `value`。定性軸と、実測値が無い軸は `null` |
| `unit` | string \| null | 実測値の単位。定性軸は `null` |
| `score` | integer \| null | その軸の点数（0〜100 の整数）。実測値か基準を欠く定量軸、判定結果を得られない定性軸は `null` |
| `threshold_source` | string \| null | 点数の基準の出所。`user`（profile の `thresholds`）・`statistic`（`DEFAULT_THRESHOLDS`）のいずれか。基準が無い軸と定性軸は `null` |
| `thresholds` | object \| null | 適用した基準。`{zero, full}`。基準が無い軸と定性軸は `null` |
| `grade` | string \| null | 実測値のエビデンスレベル（A〜D）。`company_metrics` の当該軸の `grade` を写す。定性軸は `null` |
| `source_url` | string \| null | 実測値の出典 URL。`company_metrics` の当該軸の `source_url` を写す。定性軸は `null` |
| `evidence` | string \| null | 定性軸のみ。判定条件のどれに合致したかの説明。fit-assessor の判定結果をそのまま写す |
| `reason` | string | 判定できなかった軸のみ。実測値が無い・基準が無い・判定結果が無いのいずれであるかを書く |

定量軸の基準は、profile の `thresholds`（`threshold_source` は `user`）を統計由来の既定（同 `statistic`）より優先する。どちらも無い軸は `score` を `null` にし、推測した基準で点数を作らない。実測値が無い軸も 0 点にせず `null` にする。0 点は「低い水準であることを確認した」という意味であり、材料が無いことと区別する。

定性軸の点数は、fit-assessor が求人票と企業研究の事実を判定条件（profile の `judgment`）へ当てはめた結果である。どの条件にも合致しない軸は `score` を `null` にし、中間の点数を推測で置かない。

## overall

```json
{
  "recommendation": "条件付き推奨",
  "rationale": "判定の根拠を数文で",
  "open_questions": ["未確認の論点"]
}
```

| フィールド | 型 | 内容 |
|---|---|---|
| `recommendation` | string | `推奨`・`条件付き推奨`・`非推奨`・`判断保留` のいずれか |
| `rationale` | string | 総合判定の根拠（非空） |
| `open_questions` | array | 未確認・未決の論点。空配列でもよい |

## screening_source

求人検索（`job-change-job-search`）のスクリーニングを経てこの評価へ来た場合に、そのときの判定の出所を書く。求人検索を経ずに企業研究から入った場合は書かない。

```json
{
  "search_id": "20260725-remote-infra",
  "result_index": 0,
  "classification": "apply_candidate",
  "screened_at": "2026-07-25"
}
```

| フィールド | 型 | 内容 |
|---|---|---|
| `search_id` | string | 参照先の検索実行の識別子。`{DATA_ROOT}/job-search/{検索ID}/job_search_results.json` のトップレベルの `search_id` をそのまま写す。値はディレクトリ名 `{検索ID}` と同じである。形式と記入基準の原本は job-change-job-search の `references/job-search-format.md` にある |
| `result_index` | integer | 参照先 `results[]` のうち当該求人を指す添字（0始まり） |
| `classification` | string | 参照先 `results[result_index].classification` の値 |
| `screened_at` | string | 参照先 `screening.screened_at`（判定日。`YYYY-MM-DD`） |

`search_id` と `result_index` の2つで、どのファイルのどの求人を見て判定したかが定まる。求人検索の判定と適合性評価の判定が食い違った軸は、検証スクリプトが `result_index` で参照先を引いて WARN として報告する。

## 中間成果物（sources.json・qualitative_judgment.json）

Step 2 で fit-assessor が作る2つのファイルである。どちらも `fit_assessment.json` と同じ `{DATA_ROOT}/career-private/fit/{企業スラッグ}/` 配下へ置く。定性軸の判定条件は利用者が自分の言葉で書いたものであり、その判定結果も個人情報の派生値であるため、非個人情報ツリー（`companies/` 配下）へは置かない。置き場所を決めない一時ファイルにもしない。中断したあとの再開で、ファイルの有無から Step 2 のどこまで済んでいるかを決めるためである。

### sources.json

拘束時間の算定に使った各数値の出典メタである。`calculate_time_analysis.py` の `--sources-json` へ渡し、スクリプトは各キーのメタを `time_analysis.json` の `inputs` へ写す。

```
{DATA_ROOT}/career-private/fit/{企業スラッグ}/sources.json
```

```json
{
  "monthly_overtime_h": { "value": 18, "source": "research", "source_url": "https://...", "grade": "B" },
  "annual_holidays": { "value": 125, "source": "posting", "source_url": "https://...", "grade": "A" },
  "commute_oneway_min": { "value": 45, "source": "user", "source_url": null, "grade": null }
}
```

キーは `calculate_time_analysis.py` の入力の識別子で、`scheduled_hours`・`break_minutes`・`monthly_overtime_h`・`annual_holidays`・`paid_leave_rate`・`paid_leave_granted`・`paid_leave_taken`・`commute_oneway_min`・`salary` を取りうる。CLI 引数で値を渡した項目だけを書く。渡さずに統計フォールバックへ委ねた項目はここへ書かない（スクリプトが `source` を `fallback` として補う）。

| フィールド | 型 | 内容 |
|---|---|---|
| `value` | number | 抽出した値。CLI 引数へ渡した値と同じものを控えとして書く。点数の算出にはスクリプトが CLI 引数の値を使う |
| `source` | string | `posting`（求人票 metrics）・`research`（企業研究の指標）・`user`（利用者の申告）・`fallback` のいずれか。既定値以外は `user` として扱われる |
| `source_url` | string \| null | 出典 URL。利用者の申告など URL が無い場合は `null` |
| `grade` | string \| null | 出典のエビデンスレベル（A〜D）。原本は job-change-company-research の `references/evidence-grading.md`。利用者の申告など付けられない場合は `null` |

### qualitative_judgment.json

profile の `company_score_axes` のうち `kind` が `qualitative` の軸について、判定条件（`judgment`）へ事実を当てはめた結果である。`calculate_company_score.py` の `--qualitative-json` へ渡し、スクリプトは `matched_score` をそのまま `company_score.axes[].score` へ、`evidence` を同 `evidence` へ写す。

```
{DATA_ROOT}/career-private/fit/{企業スラッグ}/qualitative_judgment.json
```

```json
{
  "tech_discretion": { "matched_score": 50, "evidence": "求人票の『設計から関与』の記載に合致した" },
  "team_autonomy": { "matched_score": null, "evidence": null }
}
```

キーは profile の `company_score_axes[].axis`（定性軸のみ）である。

| フィールド | 型 | 内容 |
|---|---|---|
| `matched_score` | integer \| null | 最初に合致した判定条件の `score`。profile の当該軸の `judgment[].score` に無い値を書くと `calculate_company_score.py` が終了コード 2 で拒む。どの条件にも合致しない軸は `null` とし、中間の点数を推測で置かない |
| `evidence` | string \| null | どの記載が条件に合致したかの説明。`matched_score` が `null` のときは `null` でよい |

## 検証規則（validate_fit_assessment.py）

機械検証の原本は `scripts/validate_fit_assessment.py` である。終了コードは PASS（ERROR 0件）で 0、FAIL（ERROR 1件以上）で 1。WARN のみは PASS 扱いとする。

### ERROR（成立しない）

- ルートがオブジェクトでない。
- `schema_version`・`slug`・`assessed_at` の欠落または空。`slug` が企業スラッグの形式（原本は job-change-support の `references/company-index-format.md`）に一致しない。
- `inputs` がオブジェクトでない。版に応じたキー（1.0 は4つ、2.0 は5つ）のいずれかの欠落、または真偽値でない。
- `dimensions` が配列でない。版に応じた id（1.0 は5つ、2.0 は7つ）に過不足がある（欠落・未知 id・重複）。
- 次元の `score` が 1〜5 の整数でも `null` でもない。`verdict` の欠落または空。
- 次元の `evidence` が空、または `source` が既定値以外（1.0 は5値、2.0 は6値）。
- `must_condition_results` が配列でない。`condition` の欠落または空。`met` が `yes`・`no`・`unknown` 以外。`met` が `yes`・`no` なのに `evidence` が空。
- `overall.recommendation` が既定の4値以外。`overall.rationale` の欠落または空。`overall.open_questions` が配列でない。
- `company_score` があってオブジェクトでない。`total` が 0〜100 の整数でも `null` でもない。`coverage` が 0〜100 の整数でない。`provisional` が真偽値でない。`axes` が配列でない。`axes[]` の `axis` が空、`kind` が `quantitative`・`qualitative` 以外、`weight` が 1〜100 の整数でない、`score` が 0〜100 の整数でも `null` でもない。`rationale` の欠落または空。

`schema_version` が `2.0` のときは、次も ERROR とする。

- `dimensions` の id が7種と一致しない（1.0 の `skill_fit` を使っている場合を含む）。
- `inputs` に `job_search_screening` が無い、または真偽値でない。
- `experience_proximity` の `skill_gap` が既定5値以外、`skill_gap_items` が配列でない。
- `skill_gap_items[]` の `requirement`・`basis` が空、`gap_level` が既定3値以外、`evidence` が空。
- `skill_gap` が `skill_gap_items[].gap_level` の最も重い段階と一致しない。
- `must_condition_results[].ref` の欠落・空・重複。
- `negotiable` が真偽値でない、または `negotiable=true` なのに `evidence` が空。
- **満たさない必須条件（`met=no`）があるのに `recommendation` が `推奨`。**
- `met=no` のうち `negotiable` が `true` でないものが残るのに `recommendation` が `条件付き推奨`。
- `skill_gap` が `not_applicable_now` なのに `recommendation` が `推奨`・`条件付き推奨`。
- `aspiration_alignment` の `score` が非 null なのに、evidence に `self_analysis` も `profile` も含まれない。
- `inputs.self_analysis` が `false` なのに `aspiration_alignment.score` が4以上。
- `--profile` 指定時: `must_condition_results` の `ref` 集合が profile の必須条件の集合と一致しない。

### WARN（成立するが質を下げる）

- `schema_version` が既知バージョン（`1.0`／`2.0`）でない。
- `assessed_at` が `YYYY-MM-DD` 形式でない。
- 次元の `score` が `null`（判断保留であることの明示）。
- evidence の `ref` が欠落または空。
- `inputs` の全キーが `false`（評価の根拠が乏しい）。
- 満たさない must 条件（`met=no`）があるのに `recommendation` が `推奨`（1.0 のみ。2.0 では ERROR）。
- `--profile` が指定されていない（必須条件との1対1が未検証である）。
- `inputs` の3つ以上が `false` なのに `recommendation` が `推奨`。
- `inputs.self_analysis` が `false`（志向の根拠が弱い）。
- `company_score.total` が `null`（判定できた軸が無く、総合点を算出できていない）。
- `company_score.provisional` が `true`（判定できた軸の重みの合計が足りず、少数の軸に引きずられる点数である）。
- `--screening` 指定時: 求人検索で必須条件を満たすと判定した求人が、求人票の取込後に `met=no` になっている。

## バージョンと移行

| `schema_version` | 扱い |
|---|---|
| `1.0` | 5次元（`skill_fit`・`condition_fit`・`culture_fit`・`compensation_fit`・`time_fit`）。`inputs` は4キー。`must_condition_results` に `ref` を要求しない。従来の規則のみを適用する |
| `2.0` | 7次元。`inputs` は5キー。上記の 2.0 規則を追加で適用する |

1.0 の成果物はそのまま検証を通る。企業別ディレクトリを恒久アーカイブとして扱う方針と整合させ、過去の評価を読めない状態にしない。1.0 で7次元の id を使う、2.0 で `skill_fit` を使う、といった混在は ERROR とする。

## 記入例

架空企業の完全な記入例は `assets/fit_assessment_example.json` にある。単体テストはこの記入例が検証を PASS することを確認する。
