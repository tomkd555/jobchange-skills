# job_posting.json の原本仕様（job-posting-format）

取り込んだ求人情報の構造化データ `job_posting.json` のフィールド仕様・記入基準・機械的な検証の規則を定める原本である。求人票の取り込み担当エージェント（job-change-posting-parser）がこの仕様に適合するオブジェクトを組み立て、`scripts/validate_job_posting.py` がこの仕様に照らして機械的に検査する。

出力先は `{DATA_ROOT}/companies/{企業スラッグ}/job_posting.json` である。ファイルを書くのは呼び出し元スキル（job-change-company-research 本体）であり、スラッグ解決後にのみ書く。posting-parser エージェントはファイルを書かず、`{company_name, aliases, job_posting}` を最終メッセージの JSON で返す。

## 取り込みの入口

求人票は、企業ごとの工程の最初で必ず作る。入口は4通りあり、`source_type` で区別する。

| `source_type` | 入口 | 取り込みのしかた | `source_url` |
|---|---|---|---|
| `url` | 求人ページの URL | ページを取得して構造化する | URL（必須） |
| `text` | 求人票の本文 | 貼り付けられた本文を構造化する | null または省略 |
| `file` | 求人票の PDF・画像 | 利用者が示したファイルを読み取って構造化する | null または省略 |
| `dialogue` | 企業名のみ | 対話で必須項目を聞き取って構造化する | null または省略 |

`url` 以外の入口でも、参考として URL を書くこと自体は妨げない。`source_url` を検査するのは `source_type` が `url` のときだけである。

## 全体構造

```json
{
  "schema_version": "1.1",
  "source_type": "url",
  "source_url": "https://recruit.example.co.jp/jobs/1234",
  "fetched_at": "2026-07-17",
  "company_name": "架空クラウドワークス株式会社",
  "title": "バックエンドエンジニア（中途）",
  "employment_type": "正社員",
  "location": { "work_location": "東京都渋谷区", "remote_policy": "週3リモート可" },
  "salary": { "min": 6000000, "max": 9000000, "currency": "JPY", "basis": "年収", "notes": "" },
  "working_hours": { "scheduled_hours": 7.5, "break_minutes": 60, "discretionary": false, "overtime_notes": "" },
  "metrics": {
    "annual_holidays": { "value": 125, "quote": "年間休日125日" },
    "monthly_overtime_h": { "value": 20, "quote": "月平均残業20時間" },
    "paid_leave_rate": { "value": 71.0, "quote": "有給取得率71%" },
    "paid_leave_days_granted": { "value": 20, "quote": "有給付与20日" }
  },
  "scope_of_change": {
    "duties": { "stated": true, "unlimited": false, "quote": "変更の範囲: バックエンド開発およびこれに関連する業務" },
    "work_location": { "stated": true, "unlimited": true, "quote": "変更の範囲: 会社の定める場所" },
    "contract_renewal_cap": null
  },
  "requirements": { "must": [ "" ], "want": [ "" ] },
  "benefits": [ { "name": "書籍購入補助", "quote": "技術書は全額会社負担" } ],
  "selection_process": [ "書類選考", "適性検査", "一次面接", "最終面接" ],
  "open_questions": [ "" ]
}
```

## フィールド仕様

### 必須フィールド

| フィールド | 型 | 記入基準 |
|---|---|---|
| `schema_version` | 文字列 | 現行は `"1.1"`。`"1.0"` も既知バージョンとして受け入れる。それ以外は WARN |
| `source_type` | 文字列 | 取り込みの入口。`url` / `text` / `file` / `dialogue` のいずれか |
| `fetched_at` | 文字列 | 取得日（`YYYY-MM-DD` の実在日付）。対話で埋めた場合は聞き取った日 |
| `company_name` | 文字列 | 求人票に記載された企業名 |
| `title` | 文字列 | 求人の職種・ポジション名 |

`source_url` は、`source_type` が `url` のときに限り必須であり、`http` で始まる文字列でなければならない。それ以外の入口では null または省略してよい。

上表のフィールドのいずれかが欠落または空の場合は ERROR となる。加えて、`source_type` が4つの値のいずれでもないとき、`source_type` が `url` でありながら `source_url` が `http` で始まらないとき、`fetched_at` が `YYYY-MM-DD` 形式の実在日付でないときも ERROR となる。

### 任意フィールド

| フィールド | 型 | 内容 |
|---|---|---|
| `employment_type` | 文字列 | 雇用形態（正社員・契約社員等） |
| `location` | オブジェクト | `work_location`（勤務地）・`remote_policy`（リモート方針） |
| `salary` | オブジェクト | `min`・`max`・`currency`・`basis`（年収/月給等）・`notes` |
| `working_hours` | オブジェクト | `scheduled_hours`（所定労働時間）・`break_minutes`（休憩分）・`discretionary`（裁量労働の真偽）・`overtime_notes` |
| `metrics` | オブジェクト | 後述の4メトリック |
| `scope_of_change` | オブジェクト | 後述の3項目（schema_version 1.1 以降） |
| `requirements` | オブジェクト | `must`（必須要件の配列）・`want`（歓迎要件の配列） |
| `benefits` | 配列 | 各要素は `{name, quote}`。`name` は非空 |
| `selection_process` | 配列 | 選考段階を順に並べた文字列配列 |
| `open_questions` | 配列 | 取得できなかった項目・要確認事項 |

任意フィールドは、存在する場合に上表の型へ反していれば ERROR となる（オブジェクトであるべきものが配列・スカラー、配列であるべきものがオブジェクト・スカラー等）。存在しなければ検査しない。

### metrics（オブジェクト・任意）

求人票に明記がある働き方数値を、機械可読な形で持つ。4つのキーを持ち、各値は `{value, quote}` のオブジェクト、または `null`。

| キー | 内容 | 単位の目安 |
|---|---|---|
| `annual_holidays` | 年間休日数 | 日 |
| `monthly_overtime_h` | 月平均の残業時間 | 時間 |
| `paid_leave_rate` | 有給取得率 | %（求人票の表記に合わせる） |
| `paid_leave_days_granted` | 有給付与日数（見込） | 日 |

各メトリックは次のフィールドを持つ。

| フィールド | 必須 | 記入基準 |
|---|---|---|
| `value` | 必須 | 数値。文字列や真偽値は不可 |
| `quote` | 必須 | 求人票からの引用（非空）。数値の根拠箇所をそのまま転記する |

**ルール**: 求人票に明記がある場合のみ `value` と引用 `quote` を入れる。明記が無ければ `null` にする（推定・創作は禁止）。metrics 全体の欠落、および個別メトリックの `null` は正常であり、ERROR も WARN も出さない。metrics が存在してオブジェクトでない、または各メトリックが `null` でも `{value, quote}` でもない・`value` が非数値・`quote` が空の場合は ERROR となる。

### scope_of_change（オブジェクト・任意。schema_version 1.1 以降）

2024年4月1日施行の職業安定法施行規則の改正により、求人には次の3項目の明示が義務づけられている（厚生労働省 https://www.mhlw.go.jp/stf/newpage_32105.html ）。転勤・職種転換・雇止めのリスクを見積もる材料であり、下流の適合性評価が使う。3つのキーを持ち、各値は `{stated, unlimited, quote}` のオブジェクト、または `null`。

| キー | 対応する明示義務の項目 |
|---|---|
| `duties` | 従事すべき業務の変更の範囲 |
| `work_location` | 就業場所の変更の範囲 |
| `contract_renewal_cap` | 有期労働契約を更新する場合の更新上限（通算契約期間または更新回数の上限） |

各項目は次のフィールドを持つ。

| フィールド | 型 | 記入基準 |
|---|---|---|
| `stated` | 真偽値 | 求人票にその項目の記載があれば真、無ければ偽 |
| `unlimited` | 真偽値 | 記載があっても範囲を限定していなければ真。判定基準は後述 |
| `quote` | 文字列 | 求人票からの引用。`stated` が真のときは非空必須 |

```json
"scope_of_change": {
  "duties": { "stated": true, "unlimited": false, "quote": "変更の範囲: バックエンド開発およびこれに関連する業務" },
  "work_location": { "stated": true, "unlimited": true, "quote": "変更の範囲: 会社の定める場所" },
  "contract_renewal_cap": { "stated": false, "unlimited": false, "quote": "無期雇用のため対象外" }
}
```

**ルール**: 求人票を読んで確認できた内容だけを書く。項目そのものを求人票の中に見つけられなかった場合は、その項目を `null` にする。`stated` を偽にするのは、求人票がその項目に触れており、かつ範囲の明示が無いと読み取れた場合（無期雇用のため更新上限が対象外である旨の記載など）に限る。`null` と `stated: false` の違いは、「求人票を読んだが該当箇所が見つからなかった」と「求人票が触れているが範囲を明示していない」の違いである。

**`unlimited` の判定基準**: 記載された範囲が、企業の裁量で後から広げられる書き方であれば真とする。

| 記載の例 | `unlimited` |
|---|---|
| 「変更の範囲: 会社の定める業務」「会社の定める場所」「会社の指示する業務全般」 | 真 |
| 「変更の範囲: 会社内のすべての業務」「当社の全事業所（将来設置されるものを含む）」 | 真 |
| 「変更の範囲: バックエンド開発およびこれに関連する業務」 | 偽 |
| 「変更の範囲: 本社および東京23区内の事業所」「変更なし」 | 偽 |
| 「更新上限: 通算契約期間5年」「更新回数3回まで」 | 偽 |

判断に迷う書き方（例えば「原則として現在の勤務地」のように、例外の範囲が読み取れないもの）は、`unlimited` を偽にしたうえで、その旨を `open_questions` へ書く。`open_questions` へ回すのは、この種の曖昧な記載に限る。記載内容そのものは `scope_of_change` に入るため、重ねて `open_questions` へ書かない。

3項目とも `null`（および `scope_of_change` 自体の欠落）は WARN となる。2024年4月以降に掲載された求人票には明示義務があり、3項目すべてを取得できていないことは取り込みの不足を疑わせるためである。

`schema_version` が `1.0` の場合、`scope_of_change` は検査しない。1.0 にはこのフィールドが無く、既存の成果物をそのまま読めるようにするためである。検査から外すのは 1.0 だけであり、以降のバージョンでは検査する。

## 取得できない場合の扱い

ログイン必須・動的描画・掲載終了などで取得できない場合は、取得できた範囲だけを埋める。欠損した項目は、該当フィールドを `null`（メトリック）にするか省略とし、`open_questions` に何が取得できなかったかを記録する。求人票にない数値を推定で埋めない。

この扱いは入口によらない。`source_type` が `dialogue` の場合に利用者が答えられなかった項目も、同じ扱いとする。推定で補わず、`open_questions` に書く。

## 機械的な検証の規則（validate_job_posting.py）

`scripts/validate_job_posting.py` が機械的に検査する。ERROR が1件でもあれば FAIL（終了コード1）、ERROR 0件なら PASS（終了コード0。WARN があっても PASS）。

**ERROR（成果物として成立しない・型違反）**

- JSON として読み込めない
- ルートがオブジェクトでない
- `schema_version`・`source_type`・`fetched_at`・`company_name`・`title` のいずれかが欠落または空
- `source_type` が `url` / `text` / `file` / `dialogue` のいずれでもない
- `source_type` が `url` でありながら `source_url` が `http` で始まらない
- `fetched_at` が `YYYY-MM-DD` 形式の実在日付でない
- `metrics` が存在しオブジェクトでない
- `metrics` の各メトリックが存在し（非 null）、`{value, quote}` のオブジェクトでない・`value` が非数値・`quote` が空のいずれか
- `schema_version` が `1.0` 以外で、`scope_of_change` が存在しオブジェクトでない
- `schema_version` が `1.0` 以外で、`scope_of_change` の各項目が存在し（非 null）、オブジェクトでない・`stated` が真偽値でない・`unlimited` が真偽値でない・`stated` が真なのに `quote` が空・`quote` が文字列でないのいずれか
- `location`・`salary`・`working_hours`・`requirements` が存在しオブジェクトでない
- `selection_process`・`open_questions`・`benefits` が存在し配列でない
- `benefits` の要素がオブジェクトでない、または `name` が空

**WARN（成立するが情報が不足する）**

- `schema_version` が既知のバージョン（`1.0` / `1.1`）でない
- `schema_version` が `1.0` 以外で、`scope_of_change` の3項目がすべて `null`（`scope_of_change` 自体の欠落を含む）
