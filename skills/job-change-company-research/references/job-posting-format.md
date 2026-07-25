# job_posting.json の原本仕様（job-posting-format）

求人URLから取り込んだ求人情報の構造化データ `job_posting.json` のフィールド仕様・記入基準・機械検証規則を定める原本である。求人票取込担当エージェント（job-change-posting-parser）がこの仕様に適合するオブジェクトを組み立て、`scripts/validate_job_posting.py` がこの仕様に照らして機械検査する。

出力先は `{DATA_ROOT}/companies/{企業スラッグ}/job_posting.json` である。ファイルを書くのは呼出元スキル（job-change-company-research 本体）であり、スラッグ解決後にのみ書く。posting-parser エージェントはファイルを書かず、`{company_name, aliases, job_posting}` を最終メッセージの JSON で返す。

## 全体構造

```json
{
  "schema_version": "1.0",
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
| `schema_version` | 文字列 | 現行は `"1.0"`。既知バージョン以外は WARN |
| `source_url` | 文字列 | 取り込んだ求人ページの URL。`http` で始まる |
| `fetched_at` | 文字列 | 取得日（`YYYY-MM-DD` の実在日付） |
| `company_name` | 文字列 | 求人票に記載された企業名 |
| `title` | 文字列 | 求人の職種・ポジション名 |

いずれかの欠落・空は ERROR となる。`source_url` が `http` で始まらない、`fetched_at` が `YYYY-MM-DD` 形式の実在日付でない場合も ERROR となる。

### 任意フィールド

| フィールド | 型 | 内容 |
|---|---|---|
| `employment_type` | 文字列 | 雇用形態（正社員・契約社員等） |
| `location` | オブジェクト | `work_location`（勤務地）・`remote_policy`（リモート方針） |
| `salary` | オブジェクト | `min`・`max`・`currency`・`basis`（年収/月給等）・`notes` |
| `working_hours` | オブジェクト | `scheduled_hours`（所定労働時間）・`break_minutes`（休憩分）・`discretionary`（裁量労働の真偽）・`overtime_notes` |
| `metrics` | オブジェクト | 後述の4メトリック |
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
| `monthly_overtime_h` | 月平均残業時間 | 時間 |
| `paid_leave_rate` | 有給取得率 | %（求人票の表記に合わせる） |
| `paid_leave_days_granted` | 有給付与日数（見込） | 日 |

各メトリックのフィールド:

| フィールド | 必須 | 記入基準 |
|---|---|---|
| `value` | 必須 | 数値。文字列や真偽値は不可 |
| `quote` | 必須 | 求人票からの引用（非空）。数値の根拠箇所を写す |

**ルール**: 求人票に明記がある場合のみ `value` と引用 `quote` を入れる。明記が無ければ `null` にする（推定・創作は禁止）。metrics 全体の欠落、および個別メトリックの `null` は正常であり、ERROR も WARN も出さない。metrics が存在してオブジェクトでない、または各メトリックが `null` でも `{value, quote}` でもない・`value` が非数値・`quote` が空の場合は ERROR となる。

## 取得できない場合の扱い

ログイン必須・動的描画・掲載終了などで取得できない場合は、取得できた範囲だけを埋める。欠損した項目は、該当フィールドを `null`（メトリック）にするか省略とし、`open_questions` に何が取得できなかったかを記録する。求人票にない数値を推定で埋めない。

## 機械検証規則（validate_job_posting.py）

`scripts/validate_job_posting.py` が決定的に検査する。ERROR が1件でもあれば FAIL（終了コード1）、ERROR 0件なら PASS（終了コード0。WARN があっても PASS）。

**ERROR（成果物として成立しない・型違反）**

- JSON として読み込めない
- ルートがオブジェクトでない
- `schema_version`・`source_url`・`fetched_at`・`company_name`・`title` のいずれかが欠落または空
- `source_url` が `http` で始まらない
- `fetched_at` が `YYYY-MM-DD` 形式の実在日付でない
- `metrics` が存在しオブジェクトでない
- `metrics` の各メトリックが存在し（非 null）、`{value, quote}` のオブジェクトでない・`value` が非数値・`quote` が空のいずれか
- `location`・`salary`・`working_hours`・`requirements` が存在しオブジェクトでない
- `selection_process`・`open_questions`・`benefits` が存在し配列でない
- `benefits` の要素がオブジェクトでない、または `name` が空

**WARN（成立するが情報が不足する）**

- `schema_version` が既知のバージョン（`1.0`）でない
