# job_search_results.json の原本仕様（job-search-format）

求人検索の成果物 `job_search_results.json` のフィールド仕様・記入基準・機械検証規則を定める原本である。求人検索担当エージェント（job-change-job-searcher）がこの仕様で成果物を作り、`scripts/validate_job_search_results.py` がこの仕様に照らして機械検査する。

出力先は `{DATA_ROOT}/job-search/{YYYYMMDD}-{条件の短いスラッグ}/job_search_results.json` である。企業別の成果物ツリー（`companies/{企業スラッグ}/`）とは別に、`job-search/` 配下へ検索実行ごとのディレクトリを作る。

## 全体構造

```json
{
  "schema_version": "2.0",
  "search_id": "20260725-remote-infra",
  "mode": "fuzzy",
  "executed_at": "YYYY-MM-DD",
  "conditions": {
    "roles": ["バックエンドエンジニア"],
    "industries": ["SaaS"],
    "salary_min": 6000000,
    "location": "東京都",
    "remote_policy": "リモート中心",
    "employment_type": "正社員"
  },
  "baseline": { "slug": "kakuu-cloudworks" },
  "results": [
    {
      "title": "バックエンドエンジニア（SaaS・自社開発）",
      "company_name": "架空アトラス株式会社",
      "url": "https://example.com/jobs/atlas-backend",
      "source_site": "求人ボックス",
      "salary_range": "650万〜900万円",
      "location": "東京都渋谷区（フルリモート可）",
      "remote_policy": "フルリモート可",
      "annual_holidays": 125,
      "match_notes": "年収下限・リモート・自社SaaSの3条件に合致する。",
      "better_points": [],
      "quote": "年収650万〜900万円／フルリモート可／年間休日125日",
      "duty_items": [ ],
      "axis_observations": [ ],
      "axis_judgements": [ ],
      "classification": "apply_candidate",
      "classification_reasons": [
        {"axis": "remote_certainty", "reason": "フルリモート可の記載があり、必須条件を満たす"},
        {"axis": "annual_holidays", "reason": "年間休日125日で必須条件を満たす"},
        {"axis": "salary_condition", "reason": "提示下限650万円が希望する下限を満たす"}
      ]
    }
  ],
  "screening": { },
  "coverage_notes": "求人ボックスの検索結果1ページ目を対象とした。",
  "open_questions": [ "" ]
}
```

`duty_items`・`axis_observations`・`axis_judgements`・`screening` は、上では骨格を示すために空で置いてある。`baseline` も位置を示すために置いてあるだけで、`similar_better` モードでのみ用いる（上のように `fuzzy` で書くと WARN になる）。実際の中身は後述の各節が定める。記入済みの全体像は `assets/job_search_results_example.json` にある。

## フィールド仕様

### schema_version（文字列・必須）

現行は `"2.0"`。`"1.0"` も読める。欠落・空は ERROR。既知の2値以外は WARN。

`"2.0"` では、観測層（`axis_observations`・`duty_items`）・判定層（`axis_judgements`・`classification`）・総括（`screening`）が加わり、必須になる。`"1.0"` の成果物はそのまま検証を通り、これらの検査を受けない。

### search_id（文字列・必須）

この検索実行の識別子。成果物を置くディレクトリ名と同じ値を書く（`job-search/20260725-remote-infra/` なら `"20260725-remote-infra"`）。欠落・空は ERROR。ディレクトリ名は成果物の外にあり、ファイルを読んだだけではどの検索実行のものか分からないため、同じ値を中へも書く。適合性評価の `screening_source.search_id`（原本は job-change-fit-assessment の `references/fit-format.md`）がこの値で検索実行を特定する。

形式は次の正規表現に一致しなければならない（不一致は ERROR）。

```
^[0-9]{8}-[0-9a-z][0-9a-z-]*$
```

8桁の実行日（`YYYYMMDD`）・ハイフン・条件の短いスラッグ（英小文字・数字・ハイフン。先頭はハイフン不可）である。日付の部分は `executed_at` と同じ日にする。

### mode（文字列・必須）

検索モードを指す。次の2値のいずれかとする。欠落・空、または2値以外は ERROR となる。

| 値 | 意味 |
|---|---|
| `fuzzy` | 曖昧条件検索。利用者の希望を構造化した条件シートに基づく検索 |
| `similar_better` | 類似高待遇検索。基準求人（baseline）の条件を上回る求人の検索 |

### executed_at（文字列・必須）

検索した日付（`YYYY-MM-DD`）。欠落・空は ERROR。求人情報の鮮度を後で判断するために記す。

### conditions（オブジェクト・必須）

検索に用いた条件。匿名化済みでなければならない。**現勤務先名・氏名・現年収を含めてはならない。** 希望年収の下限（`salary_min` 等）を条件に含めることは可とする。オブジェクトでない場合は ERROR、空オブジェクトは WARN。

キーは自由だが、`roles`・`industries`・`salary_min`・`location`・`remote_policy`・`employment_type`・`other` を推奨する。`salary_min` は円単位の数値で書く。

### baseline（オブジェクト・任意）

`similar_better` モードで用いる基準求人の参照。`url`（求人ページURL）または `slug`（`companies/{企業スラッグ}/` のスラッグ）のいずれかを持つ。

- `similar_better` で `baseline` が無い場合は WARN（基準求人の記録を推奨する）。
- `fuzzy` で `baseline` がある場合は WARN（fuzzy では用いない）。
- `url` も `slug` も無い場合は ERROR。`slug` は企業スラッグの形式（原本は job-change-support の `references/company-index-format.md`）に一致しなければならない（不一致は ERROR）。

### results（配列・必須）

検索で得た求人の配列。配列でない場合は ERROR。空配列は WARN（取得できなかった事情は `coverage_notes` に記すことを推奨する）。各要素は次のフィールドを持つ。

| フィールド | 必須 | 記入基準 |
|---|---|---|
| `title` | 必須 | 求人のタイトル。欠落・空は ERROR |
| `company_name` | 必須 | 掲載企業名。欠落・空は ERROR |
| `url` | 必須 | 掲載ページのURL。`http` で始まる文字列でなければならない（不一致は ERROR） |
| `source_site` | 必須 | 掲載サイト名（求人ボックス・Indeed・Green・type 等）。欠落・空は ERROR |
| `match_notes` | 必須 | 条件との合致・不足の要約。欠落・空は ERROR |
| `quote` | 必須 | 掲載ページからの引用。欠落・空は ERROR |
| `salary_range` | 任意 | 給与レンジの文字列。掲載が「応相談」等で不明な場合は `null`。文字列でも null でもない値は ERROR |
| `location` | 任意 | 勤務地の文字列、または `null`。文字列でも null でもない値は ERROR |
| `remote_policy` | 任意 | リモート方針の文字列、または `null`。文字列でも null でもない値は ERROR |
| `annual_holidays` | 任意 | 年間休日。数値・文字列・`null` のいずれか（真偽値は ERROR） |
| `better_points` | 条件付き | 基準求人より改善している点の配列。`similar_better` 専用。配列でない、または非空の文字列でない要素を含むと ERROR |

`quote` は掲載ページの文言をそのまま写す。取得できない求人を創作してはならない。給与が「応相談」「経験を考慮」等で数値が読めない場合は `salary_range` を `null` にする。

#### better_points とモードの整合

- `similar_better` モードで、ある result に `better_points` が無い・空の場合は WARN（基準求人より改善している点の記載を推奨する）。
- `fuzzy` モードで `better_points` に要素がある場合は WARN（`similar_better` 専用のため）。

## 観測層（2.0）

求人票から読めた事実を記録する。**求人検索担当エージェントが書く。** 本人の条件を知らないまま、求人票の記載だけで埋められる範囲に限る。軸と分類語彙の原本は job-change-support の `references/screening-axes.md` にある。

### results[].duty_items（配列・必須）

求人票の業務内容の引用文を1件ずつ写し、分類を付す。記載が無ければ空配列にする。

| フィールド | 必須 | 記入基準 |
|---|---|---|
| `quote` | 必須 | 業務内容の引用文。空は ERROR |
| `category` | 必須 | `build` / `operate` / `verify` / `automate` / `coordinate` / `manage` / `customer_facing` / `other` のいずれか。他の値は ERROR |

### results[].axis_observations（配列・必須）

8軸を過不足なく1件ずつ持つ（欠落・重複・未知の `axis` は ERROR）。

| フィールド | 必須 | 記入基準 |
|---|---|---|
| `axis` | 必須 | 8軸 id のいずれか |
| `stated` | 必須 | 求人票に当該軸への記載があるか（真偽値） |
| `value` | 必須 | 軸ごとの型は次表のとおり（値域と単位は `screening-axes.md` が定める）。記載が無い、または定性表現しか無く値へ落とせない場合は `null` |
| `value_text` | 条件付き必須 | 定性表現の要約。`stated=true` かつ `value` が `null` のときは必須 |
| `quote` | 条件付き必須 | 掲載ページからの引用。`stated=true` のときは非空必須 |
| `note` | 任意 | 補足 |

`value` が `null` でない場合、検証スクリプトは軸ごとに次を検査する。列挙値・値域・単位そのものは job-change-support の `references/screening-axes.md` にあり、ここへは複製しない。

| 軸 id | 型 | 検査 |
|---|---|---|
| `remote_certainty` | 列挙 | `screening-axes.md` の当該軸の列挙値以外は ERROR |
| `oncall_load` | 列挙 | `screening-axes.md` の当該軸の列挙値以外は ERROR |
| `overtime_hours` | 数値 | 数値でない、または負値は ERROR |
| `annual_holidays` | 数値 | 数値でない、または負値は ERROR |
| `hands_on_ratio` | 数値 | 数値でない、または `screening-axes.md` の値域から外れる値は ERROR |
| `coordination_ratio` | 数値 | 数値でない、または `screening-axes.md` の値域から外れる値は ERROR |
| `salary_condition` | 数値 | 数値でない、または負値は ERROR。1万円未満は万円単位との取り違えを疑って WARN |
| `experience_distance` | — | `value` は `null` 固定。非 null は ERROR |

真偽値は数値として扱わない（`true` は ERROR）。

`hands_on_ratio` と `coordination_ratio` は `duty_items` の分類件数から算出する。`duty_items` が3件未満のときは母数が足りないため、`stated` を `false`、`value` を `null` にする。検証スクリプトは `duty_items` から比率を再計算し、`value` と一致しなければ ERROR とする（許容差 0.01）。

`experience_distance` の観測層の構造は `screening-axes.md` が定める。検証スクリプトは、`value` が `null` でない場合を ERROR とし、`stated=true` のときに `required_experience` が非空の文字列の配列でない場合と、`job_family` が非空の文字列でない場合を ERROR とする。距離の3値は判定層（`axis_judgements`）の語彙であり、観測層には現れない。

## 判定層（2.0）

観測と本人の条件を突き合わせた結果を記録する。**スキル本体がローカルで書く。** `profile.json` を読む必要があるため、Web 送信手段を持つエージェントには書かせない。

### results[].axis_judgements（配列・必須）

8軸を過不足なく1件ずつ持つ（欠落・重複・未知の `axis` は ERROR）。

| フィールド | 必須 | 記入基準 |
|---|---|---|
| `axis` | 必須 | 8軸 id のいずれか |
| `level` | 必須 | `must` / `want` / `none`。profile の条件・作業特性の必須度を転記する |
| `judgement` | 必須 | `meets` / `not_meets` / `unknown` |
| `threshold_ref` | 条件付き必須 | 判定に用いた profile の `conditions[].id` または `work_character_preferences[].trait`。`level` が `must`・`want` のときは必須 |
| `rationale` | 必須 | 判定の根拠。観測値としきい値の対比で書く。本人の経歴・現年収を書かない |

**推測を禁じる規則。** 次はいずれも ERROR とする。

- 対応する観測が `stated=false` なのに `meets`・`not_meets` と判定する（記載の無い軸を推測で判定している）。
- 対応する観測の `value` が `null` なのに `meets`・`not_meets` と判定する（定性表現のみからの断定）。

### results[].classification（文字列・必須）

`apply_candidate`（応募候補）／`needs_more_research`（追加調査候補）／`excluded`（除外候補）のいずれか。他の値は ERROR。

分類は軸判定から決定的に導く。上から順に評価し、最初に該当したものを採用する。

| 条件 | 分類 |
|---|---|
| `level=must` の軸に `not_meets` が1件以上ある | `excluded` |
| `level=must` の軸に `unknown` が1件以上ある | `needs_more_research` |
| 8軸のうち `unknown` が4件以上ある | `needs_more_research` |
| 上記のいずれにも該当しない | `apply_candidate` |

検証スクリプトはこの表から再計算し、`classification` と一致しなければ ERROR とする。

### results[].classification_reasons（配列・必須）

1件以上必要である（空は ERROR）。各要素は `axis`（8軸 id）と `reason`（非空文字列）を持つ。

### results[].classification_override（オブジェクトまたは null・任意）

導出結果を手で変えた場合にのみ書く。`from`（導出結果）・`to`（実際の分類）・`reason`（非空）を持つ。

**変更は厳格化する方向にしか認めない。** `apply_candidate` → `needs_more_research` → `excluded` の向きだけを認め、逆向きは ERROR とする。応募候補が0件のときに、根拠なく1件を作る経路を塞ぐためである。

### results[].slug（文字列または null・任意）

企業研究へ進めることを決めた後、`company_index.json` で解決した企業スラッグを追記する。これが求人検索の成果物と企業別ツリーを結ぶ唯一の連結キーである。

## screening（オブジェクト・2.0 で必須）

スクリーニングの総括。欠落・非オブジェクトは ERROR。

| フィールド | 必須 | 記入基準 |
|---|---|---|
| `screened_at` | 必須 | 判定日（`YYYY-MM-DD`） |
| `profile_schema_version` | 必須 | 判定に用いた profile の `schema_version`。フォールバックの有無を後から検証できるようにする |
| `axes_source` | 必須 | `job_change_axis.conditions`（通常）／`degraded`（profile が 1.x で軸判定ができない） |
| `counts` | 必須 | `apply_candidate`・`needs_more_research`・`excluded`・`total` の整数。実集計と不一致は ERROR |
| `recommendation` | 必須 | `応募推奨あり` / `応募推奨なし` / `判定不能` |
| `rationale` | 必須 | 判定の根拠（非空） |
| `unmet_axis_summary` | 必須 | 8軸それぞれの `{axis, not_meets, unknown}` の件数。実集計と不一致は ERROR |
| `current_employer_exclusion` | 必須 | 現勤務先求人の除外の実施記録。後述 |

`recommendation` も導出値である。

| 条件 | 値 |
|---|---|
| `axes_source` が `degraded` | `判定不能` |
| `counts.apply_candidate` が1件以上 | `応募推奨あり` |
| `counts.apply_candidate` が0件 | `応募推奨なし` |

**応募候補が0件のときに、最有力候補を選ばない。** 「応募推奨なし」と明記する。検証スクリプトは、応募候補0件で `応募推奨あり` としている場合を ERROR とする。

### current_employer_exclusion

| フィールド | 必須 | 記入基準 |
|---|---|---|
| `performed` | 必須 | 除外処理を実施したか（真偽値） |
| `excluded_count` | 条件付き | 実施した場合は整数。未実施の場合は `null`。未実施なのに整数を入れると ERROR |
| `method` | 必須 | 判定方法（照合したフィールド）。未実施の場合はその理由 |

未実施のまま「除外0件」と報告することを構造的に防ぐためのフィールドである。検証していない事項を成果として報告しない。

### coverage_notes（文字列・任意）

検索の対象範囲と限界（対象サイト・対象ページ数・会員登録が必要で範囲外とした求人・動的描画で取得できなかった項目など）を記す。

### open_questions（配列・任意）

裏取りできなかった論点、条件との差分で応募前に確認すべき点などを記す。

## 機械検証規則（validate_job_search_results.py）

`scripts/validate_job_search_results.py` が決定的に検査する。ERROR が1件でもあれば FAIL（終了コード1）、ERROR 0件なら PASS（終了コード0。WARN があっても PASS）。

```
python validate_job_search_results.py <job_search_results.json> [--json] [--profile <profile.json>]
```

**ERROR（成果物として成立しない・ルール違反）**

- JSON として読み込めない
- `schema_version` の欠落・空
- `search_id` の欠落・空、またはディレクトリ名の形式（`{YYYYMMDD}-{条件の短いスラッグ}`）に一致しない
- `mode` の欠落・空、または `fuzzy`/`similar_better` 以外
- `executed_at` の欠落・空
- `conditions` がオブジェクトでない
- `results` が配列でない
- result の `title`・`company_name`・`source_site`・`match_notes`・`quote` の欠落・空
- result の `url` が `http` で始まらない
- result の `salary_range`・`location`・`remote_policy` が文字列でも null でもない
- result の `annual_holidays` が数値・文字列・null のいずれでもない
- result の `better_points` が配列でない、または非空の文字列でない要素を含む
- `baseline` があり、`url` も `slug` も持たない、または `slug` が形式不一致
- **PII 混入**（`--profile` 指定時のみ）: profile 由来の現勤務先名・氏名らしき値・現年収（`salary.current`）が成果物へ混入している

`schema_version` が `"2.0"` のときは、次も ERROR とする。

- `screening` の欠落、または非オブジェクト
- `axis_observations` / `axis_judgements` が8軸を過不足なく持たない（欠落・未知 id・重複）
- `duty_items` が配列でない、`duty_items[].quote` が空、`category` が既定8値以外
- `stated=true` なのに `quote` が空
- `stated=true` かつ `value` が `null` なのに `value_text` が空
- `value` が軸ごとの型・値域（原本は `screening-axes.md`）から外れている（列挙外の値、数値でない、負値、比率の値域外）
- `experience_distance` の観測の `value` が `null` でない、または `stated=true` なのに `required_experience`・`job_family` が形式を満たさない
- `stated=false` の軸を `meets`・`not_meets` と判定している
- `value` が `null` の軸を `meets`・`not_meets` と判定している
- `level` が `must`・`want` なのに `threshold_ref` が空、または `rationale` が空
- 比率2軸が `stated=true` なのに `duty_items` が3件未満、または再計算した比率と `value` が一致しない
- `classification` が既定3値以外、`classification_reasons` が空
- `classification` が導出結果と一致せず、有効な `classification_override` も無い
- `classification_override` が分類を緩める方向である
- `screening.counts` / `unmet_axis_summary` が実集計と一致しない
- 応募候補が0件なのに `recommendation` が `応募推奨あり`、または1件以上なのに `応募推奨なし`
- `axes_source` が `degraded` なのに `recommendation` が `判定不能` 以外
- `current_employer_exclusion.performed` が `false` なのに `excluded_count` が整数、または `true` なのに整数でない
- `--profile` 指定時: `threshold_ref` が profile の条件 id・特性 id に実在しない、または `level` が profile の必須度と一致しない

**WARN（成立するが不足・整合上の注意）**

- `schema_version` が既知の2値以外
- `--profile` が指定されていない（PII リントとしきい値の突き合わせが未実施である）
- すべての result が `excluded` である（必須条件が厳しすぎる可能性）
- 判定の半数超が `unknown` である（求人票の情報密度が低い）
- `salary_condition` の観測値が1万円未満である（万円単位で書いた取り違えの疑い）
- `conditions` が空オブジェクト
- `results` が空配列
- `similar_better` で `baseline` が無い
- `fuzzy` で `baseline` がある
- `similar_better` の result に `better_points` が無い・空
- `fuzzy` の result に `better_points` の要素がある

## PII リント（--profile 指定時）

`--profile <profile.json>` を渡すと、スキーマ検査に加えて PII リントを行う。`profile.json` から次を抽出し、成果物 JSON 全体を文字列化して混入を検出する。混入があれば ERROR とする。

この3項目は、文字列一致で機械的に検出できる範囲である。個人情報の境界そのもの（何を渡してよいか、何が例外か）の原本は hub の `references/pii-boundary.md` にあり、リントの PASS はその境界を守った証拠にならない。

| 抽出対象 | 抽出元 |
|---|---|
| 現勤務先名 | `career_history` のうち在職中（`period` が `〜現在`）のエントリーの `company`。在職中を特定できない場合は先頭エントリーの `company`。 |
| 氏名らしき値 | `basic` 内の `name`・`full_name`・`氏名`・`kana`・`name_kana` の5キー。 |
| 現年収 | `salary.current`（数値）。10000 未満の値は、年収以外の数値との誤検出を避けるため抽出しない。希望年収の下限は検査対象に含めない（条件化を許容する）。 |

profile.json の読み取りはローカルに閉じ、外部へ送信しない。記入例は `assets/job_search_results_example.json`（架空データ）にある。
