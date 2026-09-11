# job_search_results.json の原本仕様（job-search-format）

求人検索の成果物 `job_search_results.json` のフィールド仕様・記入基準・機械的な検証の規則を定める原本である。求人検索担当エージェント（job-change-job-searcher）がこの仕様で成果物を作る。`scripts/validate_job_search_results.py` は、この仕様に照らして機械的に検査する。

出力先は `{DATA_ROOT}/job-search/{YYYYMMDD}-{条件の短いスラッグ}/job_search_results.json` である。企業別の成果物ツリー（`companies/{企業スラッグ}/`）とは別に、`job-search/` 配下へ検索実行ごとのディレクトリを作る。

## 全体構造

```json
{
  "schema_version": "2.2",
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
  "search_sets": {
    "primary": {
      "roles": ["バックエンドエンジニア"],
      "industries": ["SaaS"],
      "salary_min": 6000000,
      "location": "東京都",
      "remote_policy": "リモート中心",
      "employment_type": "正社員"
    },
    "exploration": {
      "roles": ["サーバーサイドエンジニア", "Webアプリケーションエンジニア"],
      "industries": null,
      "dropped_conditions": ["industries"],
      "rationale": "業界の指定は選好であり必須条件ではないため探索集合では外した"
    }
  },
  "baseline": { "slug": "kakuu-cloudworks" },
  "improvement_axes": ["salary_condition", "annual_holidays"],
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
      "search_set": "primary",
      "role_match": "same",
      "related_info": { },
      "duty_items": [ ],
      "axis_observations": [ ],
      "axis_judgements": [ ],
      "classification": "apply_candidate",
      "classification_reasons": [
        {"axis": "remote_certainty", "reason": "フルリモート可の記載があり、必須条件を満たす"},
        {"axis": "annual_holidays", "reason": "年間休日125日で必須条件を満たす"},
        {"axis": "salary_condition", "reason": "提示下限650万円が希望する下限を満たす"}
      ],
      "baseline_comparison": { }
    }
  ],
  "search_log": [
    {
      "query": "サーバーサイドエンジニア-フルリモートの仕事-東京都",
      "url": "https://xn--pckua2a7gp15o89zb.com/...",
      "fetched_at": "2026-07-25",
      "hit_count": 312,
      "adopted_count": 1,
      "source": "求人ボックス",
      "search_set": "primary"
    }
  ],
  "screening": { },
  "coverage_notes": "求人ボックスの検索結果1ページ目を対象とした。",
  "open_questions": [ "" ]
}
```

`duty_items`・`axis_observations`・`axis_judgements`・`related_info`・`screening` は、上では骨格を示すために空で置いてある。`baseline`・`improvement_axes`・`baseline_comparison` も位置を示すために置いてあるだけで、`similar_better` モードでのみ用いる。上のように `fuzzy` で書くと WARN になる。`search_sets.exploration` は逆に `fuzzy` 専用であり、`similar_better` では `null` にする。実際の中身は後述の各節が定める。fuzzy の記入済みの全体像は `assets/job_search_results_example.json` にある。similar_better の全体像は `assets/job_search_results_similar_better_example.json` にある。こちらは `improvement_axes`・`baseline_comparison` を含む。

## フィールド仕様

### schema_version（文字列・必須）

現行は `"2.2"`。`"2.1"`・`"2.0"`・`"1.0"` も読める。欠落・空は ERROR。既知の4値以外は WARN。

| 版 | 加わるもの |
|---|---|
| `"1.0"` | 求人の基本項目・引用・出典URL |
| `"2.0"` | 観測層（`axis_observations`・`duty_items`）・判定層（`axis_judgements`・`classification`）・総括（`screening`） |
| `"2.1"` | 検索ログ（`search_log`）・改善軸（`improvement_axes`）・軸別比較（`results[].baseline_comparison`） |
| `"2.2"` | 探索集合（`search_sets`・`results[].search_set`・`results[].role_match`・`screening.exploration`）・関連情報（`results[].related_info`） |

新しい版で加わった検査は、古い版の成果物には適用しない。`"1.0"` の成果物は観測層の検査を受けず、`"2.0"` の成果物は `search_log` を求められず、`"2.1"` の成果物は `search_sets` を求められない。新しく作る成果物は `"2.2"` で書く。

### search_id（文字列・必須）

この検索実行の識別子。成果物を置くディレクトリ名と同じ値を書く（`job-search/20260725-remote-infra/` なら `"20260725-remote-infra"`）。欠落・空は ERROR。ディレクトリ名は成果物の外にあり、ファイルを読んだだけではどの検索実行のものかわからないため、同じ値を中へも書く。適合性評価は、`screening_source.search_id` に書いたこの値で検索実行を特定する。`screening_source` の仕様の原本は job-change-fit-assessment の `references/fit-format.md` にある。

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
| `similar_better` | 基準求人を上回る検索。基準求人（baseline）の条件を上回る求人の検索 |

### executed_at（文字列・必須）

検索した日付（`YYYY-MM-DD`）。欠落・空は ERROR。検索した日がいつかを後で確かめられるように記す。

### conditions（オブジェクト・必須）

検索に用いた条件。匿名化済みでなければならず、**現勤務先名・氏名・現年収を含めてはならない**。希望年収の下限（`salary_min` 等）は条件に含めてよい。オブジェクトでない場合は ERROR、空オブジェクトは WARN。

キーは自由だが、`roles`・`industries`・`salary_min`・`location`・`remote_policy`・`employment_type`・`other` を推奨する。`salary_min` は円単位の数値で書く。

### baseline（オブジェクト・任意）

`similar_better` モードで用いる基準求人の参照。`url`（求人ページURL）または `slug`（`companies/{企業スラッグ}/` のスラッグ）のいずれかを持つ。

- `similar_better` で `baseline` が無い場合は WARN（基準求人の記録を推奨する）。
- `fuzzy` で `baseline` がある場合は WARN（fuzzy では用いない）。
- `url` と `slug` のどちらも無い場合は ERROR。`slug` は企業スラッグの形式に一致しなければならない（不一致は ERROR）。形式の原本は job-change-support の `references/company-index-format.md` にある。

### results（配列・必須）

検索で得た求人の配列。配列でない場合は ERROR。空配列は WARN（取得できなかった事情は `coverage_notes` に記すことを推奨する）。各要素は次のフィールドを持つ。

| フィールド | 必須 | 記入基準 |
|---|---|---|
| `title` | 必須 | 求人のタイトル。欠落・空は ERROR |
| `company_name` | 必須 | 掲載企業名。欠落・空は ERROR |
| `url` | 必須 | 掲載ページのURL。`http` で始まる文字列でなければならない（不一致は ERROR） |
| `source_site` | 必須 | 掲載サイト名（求人ボックス・マイナビ転職エンジニア・type・Wantedly 等。対象サイトの原本は `query-catalog.md`）。欠落・空は ERROR |
| `match_notes` | 必須 | 条件との合致・不足の要約。欠落・空は ERROR |
| `quote` | 必須 | 掲載ページからの引用。欠落・空は ERROR |
| `salary_range` | 任意 | 給与レンジの文字列。掲載が「応相談」等で不明な場合は `null`。文字列でも null でもない値は ERROR |
| `location` | 任意 | 勤務地の文字列、または `null`。文字列でも null でもない値は ERROR |
| `remote_policy` | 任意 | リモート方針の文字列、または `null`。文字列でも null でもない値は ERROR |
| `annual_holidays` | 任意 | 年間休日。数値・文字列・`null` のいずれか（真偽値は ERROR） |
| `better_points` | 条件付き | 基準求人より改善している点の配列。`similar_better` 専用。配列でない、または非空の文字列でない要素を含むと ERROR |
| `baseline_comparison` | 条件付き | 基準求人との軸別比較。`similar_better` 専用。仕様は後述 |

`quote` には掲載ページの文言をそのまま転記する。取得できない求人を創作してはならない。給与が「応相談」「経験を考慮」等で数値が読めない場合は `salary_range` を `null` にする。

#### better_points とモードの整合

- `similar_better` モードで、ある result に `better_points` が無い・空の場合は WARN（基準求人より改善している点の記載を推奨する）。
- `fuzzy` モードで `better_points` に要素がある場合は WARN（`similar_better` 専用のため）。

### search_log（配列・2.1 で必須）

実行した検索を1件ずつ記録する。**検索の網羅性についての主張は、このログを唯一の根拠とする**。ログに無い検索は実行していない検索である。「網羅的に調べた」「主要な求人サイトを一通り確認した」といった、ログで裏づけられない記述を `coverage_notes` や報告に書いてはならない。書けるのは「このクエリでこの件数を見た」までである。

欠落・空配列・配列でない場合は ERROR（2.1）。`"2.0"` 以前の成果物では求めない。

4つの `null` 可のキーも、キー自体は省略できない（取得できなかったことを `null` で明示する）。

| フィールド | 必須 | 記入基準 |
|---|---|---|
| `query` | 必須 | 実行したクエリ文字列。URL文法で組み立てた場合はそのパス、`site:` 検索の場合は検索語をそのまま転記する。欠落・空は ERROR |
| `source` | 必須 | 取得元の名前（サイト名、または `WebSearch`）。欠落・空は ERROR |
| `url` | 必須（null 可） | 実際に叩いたURL。`site:` 検索で結果ページのURLが定まらない場合は `null`。`http` で始まらない文字列は ERROR |
| `fetched_at` | 必須（null 可） | 取得日時（`YYYY-MM-DD` の実在日付、または日付で始まる ISO 8601）。形式外・実在しない日付は ERROR |
| `hit_count` | 必須（null 可） | 検索結果の総件数。ページに表示が無ければ `null`。負値・整数でない値は ERROR |
| `adopted_count` | 必須（null 可） | そのクエリから `results` へ採用した件数。負値・整数でない値は ERROR |
| `search_set` | 2.2 で必須 | そのクエリが属する集合。`primary` または `exploration`。2値以外は ERROR |

`results[].search_set` が `exploration` の求人が1件以上あるのに、`search_set` が `exploration` の `search_log` の要素が1件も無い場合は ERROR とする（2.2）。探索集合の求人は、探索集合のクエリからしか採用できない。

`query` は成果物の一部であり、PII リント（後述）の検査対象に含まれる。氏名・現勤務先名・現年収を検索クエリへ入れれば、この検査で ERROR になる。

## 観測層（2.0）

求人票から読めた事実を記録する層であり、**書くのは求人検索担当エージェントである**。本人の条件を知らないまま、求人票の記載だけで埋められる範囲に限る。軸と分類語彙の原本は job-change-support の `references/screening-axes.md` にある。

### results[].duty_items（配列・必須）

求人票の業務内容の引用文を1件ずつ転記し、分類を付す。記載が無ければ空配列にする。

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

検証スクリプトは、真偽値を数値として扱わない（`true` は ERROR）。

`hands_on_ratio` と `coordination_ratio` は `duty_items` の分類件数から算出する。`duty_items` が3件未満のときは母数が足りないため、`stated` を `false`、`value` を `null` にする。検証スクリプトは `duty_items` から比率を再計算し、`value` と一致しなければ ERROR とする（許容差 0.01）。

`experience_distance` の観測層の構造は `screening-axes.md` が定める。検証スクリプトは、`value` が `null` でない場合を ERROR とする。`stated=true` のときは、`required_experience` が非空の文字列の配列でない場合と、`job_family` が非空の文字列でない場合も ERROR とする。距離の3値は判定層（`axis_judgements`）の語彙であり、観測層には現れない。

### improvement_axes（配列・similar_better 専用・2.1）

利用者が狙うと決めた改善軸の id を並べる。値は `salary_condition`・`remote_certainty`・`annual_holidays`・`overtime_hours`・`scope_of_change` の5つである。匿名化された条件であり、検索担当エージェントへ渡してよい。

この軸は尺度上の方向を持たず、`different` が改善なのか悪化なのかが軸の側から決まらない（無期から有期への変更も `different` になる）。したがって **`employment_type` は改善軸に取れない**。雇用形態の希望は `conditions.employment_type` の必須条件として扱う。`improvement_axes` に `employment_type` があれば ERROR とする。

`similar_better` で欠落・空の場合は WARN、`fuzzy` にある場合は WARN とする。配列でない、未知の軸 id、`employment_type`、重複は ERROR。

この配列は `baseline_comparison.overall` の導出に使う。**どの軸で上回りたいかは本人の選好であり、軸別の観測からは決まらない**ため、選好はこの配列の1か所へ集め、観測層には良し悪しを持ち込まない。

### results[].baseline_comparison（オブジェクト・similar_better 専用・2.1）

基準求人と候補求人を軸ごとに比べた結果を記録する。自由記述の `better_points` は残し、`baseline_comparison` は機械的に検査できる形で同じ比較を持つ。層をまたぐ唯一のフィールドである。

| 部分 | 層 | 書き手 |
|---|---|---|
| `axes[]` | 観測層 | 求人検索担当エージェント。比べる対象はどちらも求人票であり、本人の情報を要しない |
| `overall` | 判定層 | スキル本体。`improvement_axes`（本人の選好）を要するため |

`similar_better` で `baseline_comparison` が無い場合は WARN（2.1 以降）、`fuzzy` にある場合は WARN とする。`better_points` と同じ扱いである。

```json
"baseline_comparison": {
  "axes": [
    {
      "axis": "salary_condition",
      "relation": "higher",
      "baseline_value": "600万〜800万円（下限600万円）",
      "candidate_value": "700万〜950万円（下限700万円）",
      "quote": "年収700万〜950万円",
      "note": null
    }
  ],
  "overall": "better"
}
```

`axes` は次の6軸を過不足なく1件ずつ持つ（欠落・重複・未知の `axis` は ERROR）。上4軸は job-change-support の `references/screening-axes.md` の軸 id をそのまま用いる。下2軸は**基準比較専用の追加軸**であり、`screening-axes.md` の8軸には含まれない（8軸の判定・`screening.unmet_axis_summary` には現れない）。

| axis | 事実の尺度 | `higher` が指す側 |
|---|---|---|
| `salary_condition` | 提示レンジ下限の年額（円） | 金額が大きい |
| `remote_certainty` | リモートの度合い（フルリモート > 一部リモート > リモートなし） | リモートの度合いが大きい |
| `annual_holidays` | 年間休日日数 | 日数が多い |
| `overtime_hours` | 固定残業・みなし残業の時間数（記載が無ければ0時間ではなく `unknown`） | 時間数が多い |
| `employment_type`（追加軸） | 雇用形態が基準求人と同一か否か | 順序を持たないため `higher`・`lower` を使わない |
| `scope_of_change`（追加軸） | 就業場所・業務の変更の範囲の広さ（限定 < 無限定） | 範囲が広い |

`scope_of_change` は本スキルが作った軸ではない。2024年4月の職業安定法の改正で、求人情報に「従事すべき業務の変更の範囲」「就業場所の変更の範囲」「有期労働契約を更新する場合の基準」の3項目の明示が義務づけられた（厚生労働省 https://www.mhlw.go.jp/content/001114166.pdf レベルA）。この3項目のいずれも書かれていない求人票は、記載義務を満たしていない可能性がある。観測層では `unknown` にとどめ、記載が無い旨を `open_questions` に書く。

**`relation` は事実の関係だけを表す。良い・悪いは書かない**。尺度上でどちら側かは求人票2枚から決まる。どちら側が望ましいかは本人の選好であり、観測層では決められない（この分離の根拠は `search-methods.md` の「観測と判定を分ける」にある）。

| フィールド | 必須 | 記入基準 |
|---|---|---|
| `axis` | 必須 | 上の6軸 id のいずれか |
| `relation` | 必須 | `higher` / `lower` / `same` / `unknown`。`employment_type` だけは `same` / `different` / `unknown` の3値 |
| `baseline_value` | 条件付き必須 | 基準求人の値。`relation` が `unknown` 以外のときは非空必須 |
| `candidate_value` | 条件付き必須 | 候補求人の値。`relation` が `unknown` 以外のときは非空必須 |
| `quote` | 条件付き必須 | 候補求人の掲載ページからの引用。`relation` が `unknown` 以外のときは非空必須 |
| `note` | 任意 | 補足 |

**どちらかの求人票に記載が無い軸は `unknown` とする。記載が無いことを `same` と扱ってはならない**。記載の欠落は「基準求人と同じ条件である」ことを意味しない（根拠は `search-methods.md` の「記載が無いことを証拠に使わない」にある）。検証スクリプトは、`unknown` 以外の関係に両側の値と引用を要求し、この規則を機械的に担保する。引用できない比較は書けない。

基準求人の `job_posting.json` が `schema_version` `1.0` の場合、`scope_of_change` はそのファイルに存在しない。この軸は `unknown` とする（欠落を「変更の範囲が同じ」と読まない）。

#### overall の導出

`overall` は `better` / `not_better` の2値である。見るのは **`improvement_axes` に挙がった軸だけ**である。選ばれなかった軸は表示用の記録である。狙っていない軸の上下は本人にとっての良し悪しが定まらないため、総合判定へは反映しない。

各軸の改善方向は次のとおりである。

| axis | 改善方向 | 逆方向 |
|---|---|---|
| `salary_condition` | `higher` | `lower` |
| `annual_holidays` | `higher` | `lower` |
| `remote_certainty` | `higher` | `lower` |
| `overtime_hours` | `lower` | `higher` |
| `scope_of_change` | `lower` | `higher` |

`employment_type` はこの表に無い。観測（`same` / `different` / `unknown`）は記録して報告に使うが、総合判定には反映しない。有期から無期への転換のように向きのある希望も、`conditions` の必須条件として扱う。

| 条件 | overall |
|---|---|
| `improvement_axes` の1つ以上が改善方向、かつ `improvement_axes` のどれも逆方向でない | `better` |
| 上記以外 | `not_better` |

検証スクリプトはこの表から再計算し、`overall` と一致しなければ ERROR とする（6軸が揃っていない場合は照合しない）。どの軸で上回りたいかが決まらなければ、より良いかどうかは導けない。このため **`similar_better` で `improvement_axes` が空・欠落なのに `overall` が書かれている場合も ERROR とする**。`unknown` は改善にも悪化にも数えない。未確認の軸を残したまま `better` になりうるため、報告では `unknown` の軸を明示する。

## 探索集合と関連情報（2.2）

利用者の指定条件による検索（主集合）と、条件の偏りを点検するために広げた検索（探索集合）を区別して記録する。探索集合を作る理由と組み方の原本は `bias-checklist.md` にある。ここでは成果物側の記録だけを定める。

### search_sets（オブジェクト・2.2 で必須）

| フィールド | 必須 | 記入基準 |
|---|---|---|
| `primary` | 必須 | 利用者の指定条件。`conditions` と同じ内容をそのまま置く。オブジェクトでない場合は ERROR |
| `exploration` | 必須（null 可） | 探索集合の条件。作らなかった場合は `null`。オブジェクトでも null でもない値は ERROR |

`exploration` がオブジェクトの場合、次を持つ。

| フィールド | 必須 | 記入基準 |
|---|---|---|
| `roles` | 必須 | 探索集合で検索した職種名の配列。隣接職種・役職の段階をずらした呼称を並べる。該当が無ければ空配列。非空の文字列の配列でなければ ERROR |
| `industries` | 必須（null 可） | 業界の指定を外した場合は `null`。残した場合は配列。それ以外は ERROR |
| `dropped_conditions` | 必須 | 主集合から外した条件のキー名の配列（例: `["industries"]`）。該当が無ければ空配列。非空の文字列の配列でなければ ERROR |
| `rationale` | 必須 | 外した理由。利用者が必須でないと答えた条件であることを書く。欠落・空は ERROR |

`fuzzy` で `exploration` が `null` の場合は WARN（偏りの点検を省いている）。`similar_better` で `exploration` がオブジェクトの場合は WARN（fuzzy 専用）。`salary_min` は探索集合でも外さないため、`dropped_conditions` に `salary_min` を書かない。

### results[].search_set（文字列・2.2 で必須）

| 値 | 意味 |
|---|---|
| `primary` | 主集合（利用者の指定条件）のクエリから得た求人 |
| `exploration` | 探索集合のクエリから得た求人 |

2値以外は ERROR。`exploration` なのに `search_sets.exploration` が `null` の場合は ERROR（探索集合を作らずに探索の結果だけがある状態）。書くのは検索担当エージェントであり、採用したクエリの `search_log[].search_set` と同じ値を書く。

### results[].role_match（文字列・2.2 で必須）

求人の職種と、主集合の `roles` との関係を書く。

| 値 | 意味 |
|---|---|
| `same` | 主集合の職種名、またはその同義語（`query-catalog.md` の同義語表の言い換え1・2）と一致する |
| `adjacent` | 同義語表の「隣接職種」の欄に当たる職種、または役職の段階だけが異なる職種 |
| `different` | 上のいずれにも当たらない |

3値以外は ERROR。`primary` の求人が `different` の場合は WARN（クエリが条件から外れた可能性がある）。`role_match` は職種名の関係であり、経験との距離（`experience_distance`）ではない。距離の判定は判定層で、本人の経歴と照らして行う。

### results[].related_info（オブジェクト・任意）

求人票の外にある企業の関連事実のうち、ログイン不要で取得できたものを記録する。書くのは検索担当エージェントであり、求人票だけでは判定できない軸（`needs_more_research` の理由になった軸）の確認材料として集める。集める対象と出所は `query-catalog.md` の「関連情報の取得先」にある。取得しなかった場合はキーごと省略してよい。

| キー | 意味 | `value` の型 |
|---|---|---|
| `employee_count` | 従業員数 | 数値 |
| `founded_year` | 設立年 | 数値 |
| `listed` | 上場の有無 | 真偽値（真偽値を使えるのはこのキーだけ） |
| `capital_yen` | 資本金（円） | 数値 |
| `edinet_code` | EDINET コード | 文字列 |
| `certifications` | 取得している認定（くるみん・えるぼし・健康経営優良法人など） | 文字列の配列 |
| `review_aggregate` | 口コミ集計サイトの総合スコアと回答件数 | 文字列（例: `"3.4（回答42件）"`） |
| `posting_age` | 求人の掲載日または更新日 | 文字列（`YYYY-MM-DD`） |
| `salary_benchmark` | 同じ職種名で引いた相場の基準線 | 文字列（例: `"中央値553万円（求人ボックス給料ナビ）"`） |

上の9キー以外は ERROR。

#### related_info の各値

各キーの値は次のオブジェクトである。

| フィールド | 必須 | 記入基準 |
|---|---|---|
| `value` | 必須 | 上表の型。取得を試みて得られなかった場合は `null` |
| `source_url` | 必須 | 出典URL。`value` が `null` でないとき、`http` で始まらなければ ERROR |
| `grade` | 必須 | エビデンスレベル A〜D。`value` が `null` でないとき、4値以外は ERROR。定義の原本は `job-change-company-research/references/evidence-grading.md` |
| `as_of` | 必須（null 可） | 値の時点。`YYYY` または `YYYY-MM`。形式外は ERROR |
| `note` | 任意 | 補足（登記上の設立日と会社概要の設立年が異なる、口コミの本文はログインが必要なため件数だけを読んだ、など） |

`related_info` は企業研究（`company_research.json`）の代わりではない。取得できたのは求人票を読む過程で得られた事実だけであり、企業研究の8トピックの網羅も監査も経ていない。`review_aggregate` はレベルCであり、単独で事実を断定しない。

### screening.exploration（オブジェクト・2.2 で必須）

探索集合の実施記録。`screening` の中に置く。

| フィールド | 必須 | 記入基準 |
|---|---|---|
| `performed` | 必須 | 探索集合を実施したか（真偽値） |
| `result_count` | 必須（null 可） | `search_set` が `exploration` の result の件数。未実施なら `null` |
| `apply_candidate_count` | 必須（null 可） | そのうち `apply_candidate` の件数。未実施なら `null` |

3キーのいずれかが欠けると ERROR。`performed` が `true` のとき、2件数は整数で、実集計と一致しなければ ERROR。`performed` が `false` のとき、2件数は `null` でなければならず、`search_sets.exploration` がオブジェクトなら ERROR（探索集合があるのに未実施と記録している）。

## 判定層（2.0）

観測と本人の条件を突き合わせた結果を記録する。**スキル本体がローカルで書く**。`profile.json` を読む必要があるため、Web 送信手段を持つエージェントには書かせない。

### results[].axis_judgements（配列・必須）

8軸を過不足なく1件ずつ持つ（欠落・重複・未知の `axis` は ERROR）。

| フィールド | 必須 | 記入基準 |
|---|---|---|
| `axis` | 必須 | 8軸 id のいずれか |
| `level` | 必須 | `must` / `want` / `none`。profile の条件・作業特性の必須度から次の対応で決める。条件（`conditions[].level`）は `must`→`must`、`want`→`want`。作業特性（`work_character_preferences[].desire`）は `must`→`must`、`important`→`want`、`neutral`・`not_required`→`none`。profile に条件も特性も無い軸は `none` |
| `judgement` | 必須 | `meets` / `not_meets` / `unknown` |
| `threshold_ref` | 条件付き必須 | 判定に用いた profile の `conditions[].id` または `work_character_preferences[].trait`。`level` が `must`・`want` のときは必須 |
| `rationale` | 必須 | 判定の根拠。観測値としきい値の対比で書く。本人の経歴・現年収を書かない |

**推測を禁じる**。次はいずれも ERROR とする。

- 対応する観測が `stated=false` なのに `meets`・`not_meets` と判定する（記載の無い軸を推測で判定している）。
- 対応する観測の `value` が `null` なのに `meets`・`not_meets` と判定する（定性表現のみからの断定）。

### results[].classification（文字列・必須）

`apply_candidate`（応募候補）／`needs_more_research`（追加調査候補）／`excluded`（除外候補）のいずれか。他の値は ERROR。

分類は軸判定から機械的に導く。上から順に評価し、最初に該当したものを採用する。

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

**変更は厳格化する方向にしか認めない**。`apply_candidate` → `needs_more_research` → `excluded` の向きだけを認め、逆向きは ERROR とする。応募候補が0件のときに、根拠なく1件を作れないようにするためである。

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
| `exploration` | 2.2 で必須 | 探索集合の実施記録。仕様は「探索集合と関連情報」の節 |

`recommendation` も導出値である。

| 条件 | 値 |
|---|---|
| `axes_source` が `degraded` | `判定不能` |
| `counts.apply_candidate` が1件以上 | `応募推奨あり` |
| `counts.apply_candidate` が0件 | `応募推奨なし` |

**応募候補が0件のときに、最有力候補を選ばず、「応募推奨なし」と明記する**。検証スクリプトは、応募候補0件で `応募推奨あり` としている場合を ERROR とする。

### current_employer_exclusion

| フィールド | 必須 | 記入基準 |
|---|---|---|
| `performed` | 必須 | 除外処理を実施したか（真偽値） |
| `excluded_count` | 条件付き | 実施した場合は整数。未実施の場合は `null`。未実施なのに整数を入れると ERROR |
| `method` | 必須 | 判定方法（照合したフィールド）。未実施の場合はその理由 |

未実施のまま「除外0件」と報告することを構造的に防ぐためのフィールドである。スキル本体は、検証していない事項を成果として報告しない。

### coverage_notes（文字列・任意）

検索の対象範囲と限界（対象サイト・対象ページ数・会員登録が必要で範囲外とした求人・動的描画で取得できなかった項目など）を記す。

### open_questions（配列・任意）

裏取りできなかった論点、条件との差分で応募前に確認すべき点などを記す。

## 機械的な検証の規則（validate_job_search_results.py）

`scripts/validate_job_search_results.py` が機械的に検査する。ERROR が1件でもあれば FAIL（終了コード1）、ERROR 0件なら PASS（終了コード0。WARN があっても PASS）。

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
- `baseline` があり、`url` と `slug` のどちらも持たない、または `slug` が形式不一致
- `search_log` が配列でない、またはその要素がオブジェクトでない
- `search_log` の `query`・`source` が空、または `url`・`fetched_at`・`hit_count`・`adopted_count` のキーが欠落している
- `search_log` の `url` が `http` で始まらない、`fetched_at` が形式外または実在しない日付、`hit_count`・`adopted_count` が0以上の整数でも null でもない
- `improvement_axes` が配列でない、未知の軸 id を含む、`employment_type` を含む、または軸が重複している
- `similar_better` で `improvement_axes` が空・欠落なのに `baseline_comparison.overall` が書かれている
- `baseline_comparison` がオブジェクトでない、`axes` が配列でない、6軸を過不足なく持たない（欠落・未知 id・重複）、`relation` が軸ごとの既定値以外
- `baseline_comparison` の `relation` が `unknown` 以外なのに `baseline_value`・`candidate_value`・`quote` のいずれかが空
- `baseline_comparison.overall` が `better`・`not_better` 以外、または `improvement_axes` と `relation` からの導出結果と一致しない
- **PII 混入**（`--profile` 指定時のみ）: profile 由来の現勤務先名・氏名らしき値・現年収（`salary.current`）が成果物へ混入している

`schema_version` が `"2.1"` のときは、次も ERROR とする。

- `search_log` の欠落、または空配列

`schema_version` が `"2.2"` のときは、次も ERROR とする。

- `search_sets` がオブジェクトでない、`primary` がオブジェクトでない、`exploration` がオブジェクトでも null でもない
- `search_sets.exploration` の `roles`・`dropped_conditions` が非空の文字列の配列でない、`industries` が配列でも null でもない、`rationale` が空
- result の `search_set` が2値以外、または `exploration` なのに `search_sets.exploration` が null
- `search_log` の `search_set` が欠落、または2値以外
- `search_set` が `exploration` の result があるのに、`search_set` が `exploration` の `search_log` の要素が無い
- `--profile` 指定時: `level` が、profile の必須度から上の対応で決めた値と一致しない
- result の `role_match` が3値以外
- result の `related_info` がオブジェクトでない、9キー以外のキーを持つ、各値がオブジェクトでない、`value`・`source_url`・`grade`・`as_of` のキーが欠落している
- result の `related_info` で、`value` が null でないのに `source_url` が `http` で始まらない、または `grade` が4値以外。`listed` 以外の `value` が真偽値。`as_of` が形式外
- `screening.exploration` がオブジェクトでない、3キーのいずれかが欠落、`performed` が真偽値でない
- `screening.exploration.performed` が `true` なのに2件数が整数でない、または実集計と一致しない
- `screening.exploration.performed` が `false` なのに2件数が null でない、または `search_sets.exploration` がオブジェクトである

`schema_version` が `"2.0"`・`"2.1"`・`"2.2"` のときは、次も ERROR とする。

- `screening` の欠落、または非オブジェクト
- `axis_observations` / `axis_judgements` が8軸を過不足なく持たない（欠落・未知 id・重複）
- `duty_items` が配列でない、`duty_items[].quote` が空、`category` が既定8値以外
- `stated=true` なのに `quote` が空
- `stated=true` かつ `value` が `null` なのに `value_text` が空
- `value` が軸ごとの型・値域（原本は `screening-axes.md`）から外れている（列挙外の値、数値でない、負値、比率の値域外）
- `experience_distance` の観測の `value` が `null` でない
- `experience_distance` で `stated=true` なのに `required_experience`・`job_family` が形式を満たさない
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

- `schema_version` が既知の4値以外
- `--profile` が指定されていない（PII リントとしきい値の突き合わせが未実施である）
- `fuzzy`（2.2）で `search_sets.exploration` が null（偏りの点検を省いている）
- `similar_better`（2.2）で `search_sets.exploration` がオブジェクトである
- `primary` の result の `role_match` が `different` である
- すべての result が `excluded` である（必須条件が厳しすぎる可能性）
- 判定の半数超が `unknown` である（求人票の情報密度が低い）
- `salary_condition` の観測値が1万円未満である（万円単位で書いた取り違えの疑い）
- `conditions` が空オブジェクト
- `results` が空配列
- `similar_better` で `baseline` が無い
- `fuzzy` で `baseline` がある
- `similar_better` の result に `better_points` が無い・空
- `fuzzy` の result に `better_points` の要素がある
- `similar_better`（2.1）に `improvement_axes` が無い・空
- `fuzzy` に `improvement_axes` の要素がある
- `similar_better`（2.1）の result に `baseline_comparison` が無い
- `fuzzy` の result に `baseline_comparison` がある

## PII リント（--profile 指定時）

`--profile <profile.json>` を渡すと、スキーマ検査に加えて PII リントを行う。`profile.json` から次を抽出し、成果物 JSON 全体を文字列化して混入を検出する。混入があれば ERROR とする。

この3項目は、文字列一致で機械的に検出できる範囲である。個人情報の境界そのもの（何を渡してよいか、何が例外か）の原本は hub の `references/pii-boundary.md` にあり、リントの PASS はその境界を守った証拠にならない。

| 抽出対象 | 抽出元 |
|---|---|
| 現勤務先名 | `career_history` のうち在職中（`period` が `〜現在`）のエントリーの `company`。在職中を特定できない場合は先頭エントリーの `company`。 |
| 氏名らしき値 | `basic` 内の `name`・`full_name`・`氏名`・`kana`・`name_kana` の5キー。 |
| 現年収 | `salary.current`（数値）。10000 未満の値は、年収以外の数値との誤検出を避けるため抽出しない。希望年収の下限は検査対象に含めない（条件として書いてよい）。 |

profile.json の読み取りはローカルに閉じ、外部へ送信しない。記入例はいずれも架空データであり、`assets/job_search_results_example.json` と `assets/job_search_results_similar_better_example.json` にある。
