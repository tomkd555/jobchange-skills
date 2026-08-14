# company_research.json の原本仕様（company-research-format）

企業研究の構造化データ `company_research.json` のフィールド仕様・記入基準・機械的な検証の規則を定める原本である。企業研究担当エージェント（job-change-company-researcher）がこの仕様で成果物を作り、`scripts/validate_company_research.py` がこの仕様に照らして機械的に検査する。

出力先は `{DATA_ROOT}/companies/{企業スラッグ}/company_research.json` である。

## 全体構造

```json
{
  "company": { "name": "", "securities_code": "", "edinet_code": "" },
  "research_date": "YYYY-MM-DD",
  "claims": [
    {
      "id": "C001",
      "topic": "philosophy",
      "statement": "反証可能な命題を1文で書く。",
      "evidence": [
        {
          "source_url": "https://...",
          "source_name": "",
          "grade": "A",
          "quote": "根拠となる引用。",
          "accessed": "YYYY-MM-DD"
        }
      ],
      "confidence": "medium"
    }
  ],
  "company_metrics": {
    "compensation_level": { "value": 6120000, "unit": "円", "source_url": "https://...", "grade": "A", "as_of": "2026-03" },
    "annual_holidays":    { "value": null,    "unit": "日", "source_url": null,          "grade": null, "as_of": null }
  },
  "open_questions": [ "" ]
}
```

## フィールド仕様

### company（オブジェクト・必須）

| フィールド | 必須 | 記入基準 |
|---|---|---|
| `name` | 必須 | 企業の正式名称。株式会社を含む正式表記で書く |
| `securities_code` | 任意 | 上場企業の証券コード（4桁）。非上場・海外企業は省略してよい |
| `edinet_code` | 任意 | EDINET コード（E + 5桁）。有報を出典に用いた場合は記す。無ければ省略してよい |

`name` が空の場合は機械的な検証で ERROR となる。`securities_code`・`edinet_code` は無くても ERROR にはならない。

### research_date（文字列・推奨）

調査を実施した日付（`YYYY-MM-DD`）。未設定の場合は機械的な検証で WARN となる。情報の鮮度を後で判断するために記す。

### claims（配列・必須、1件以上）

企業に関する主張の配列。1件以上が必須で、空の場合は ERROR となる。各 claim は次のフィールドを持つ。

| フィールド | 必須 | 記入基準 |
|---|---|---|
| `id` | 必須 | claim の識別子。`C001` から連番を推奨する（機械的な検証は連番までは要求しない） |
| `topic` | 必須 | 後述の8種のいずれか |
| `statement` | 必須 | 反証可能な命題を1文で書く（後述） |
| `evidence` | 必須 | 出典の配列。1件以上が必須 |
| `confidence` | 必須 | `high` / `medium` / `low` のいずれか |

#### topic（8種）

| topic | 対象 |
|---|---|
| `philosophy` | 理念・社是・パーパス・行動指針（`references/philosophy-analysis.md` を原本とする） |
| `business` | 事業内容・セグメント・製品/サービス・市場での位置づけ |
| `financials` | 業績・財務・平均年間給与・平均勤続年数・従業員数 |
| `compensation` | 給与制度・賞与・等級・報酬水準 |
| `benefits` | 福利厚生・休暇・認定制度（くるみん・えるぼし・健康経営優良法人等） |
| `workstyle` | 働き方・残業・有給取得率・リモート/フレックス・定着率 |
| `reputation` | 社外・在籍者からの評判（口コミ集計・報道など） |
| `selection_process` | 選考プロセス・選考段階・筆記/適性検査の有無・面接体験記 |

**必須トピック**は `philosophy`・`business`・`financials`・`compensation`・`benefits`・`workstyle`・`reputation` の7種で、いずれかが1件も無い場合は ERROR となる。`selection_process` は必須ではないが、0件の場合は WARN となる（下流の面接対策が根拠に使うため、収集を推奨する）。

#### statement（反証可能な命題）

statement は「反証可能な命題」で書く。真偽を出典で確認できる形にする。

- 良い例:「第10期の平均年間給与は6,120千円である。」「健康経営優良法人2026に認定されている。」「選考は書類→適性検査→一次面接→最終面接の4段階である。」
- 悪い例:「良い会社である。」「働きやすい。」（真偽を出典で確認できない評価。企業自身の自己宣伝的主張はこの形になりやすい）

評価的な内容を扱う場合は、「誰がそう評価しているか」を命題にする。例:「口コミ集計サイトの総合評価は3.6である（回答87件）。」

#### evidence（出典の配列、1件以上）

| フィールド | 必須 | 記入基準 |
|---|---|---|
| `source_url` | 必須 | 出典の URL。`http` で始まる文字列でなければならない |
| `source_name` | 推奨 | 出典の名称（媒体名・文書名） |
| `grade` | 必須 | `A` / `B` / `C` / `D`。判定基準は `references/evidence-grading.md` |
| `quote` | 必須 | 出典からの引用（非空）。命題の根拠になる箇所を写す |
| `accessed` | 推奨 | 参照した日付（`YYYY-MM-DD`） |

`source_url` が `http` で始まらない、`grade` が A〜D 以外、`quote` が空、のいずれも ERROR となる。

#### confidence（確度）

| 値 | 目安 |
|---|---|
| `high` | 一次・公式（A）または信頼できる二次（B）の裏付けがあり、複数出所で整合する事実 |
| `medium` | A・B の裏付けはあるが単一出所、または一部に限定が残る |
| `low` | C・D 中心で、傾向の傍証にとどまる |

**ルール**: レベルC・Dのみを根拠とする claim に `high` を与えてはならない（ERROR）。企業自身の評価的・自己宣伝的主張は、出典がレベルAでも `high` にしない（B 相当扱い。機械的な検証では判定できず監査エージェントの領分）。

### open_questions（配列・推奨）

裏取りできなかった論点、出所間の食い違い、一次情報の代表性の限界などを記す。例:「有報の平均年間給与は全従業員平均であり、応募職種の給与水準は判別できない。」

### company_metrics（オブジェクト・必須）

定量候補軸の実測値を、機械可読な数値として構造化するトップレベルの必須フィールドである。文章の `claims` とは独立に持ち、後続の処理（企業スコアの算出・実質時給の試算）が数値をそのまま使う。軸の定義・単位・方向の原本は `references/company-score-rubric.md` にある。

企業研究は実測値を集めるだけであり、点数化も格付けもしない。指示された軸に対応する指標を優先して集め、確認できなかった項目は `value` を `null` にする。推定値を入れない。

キーは定量候補軸の軸キーと同じにする。軸キー以外で置いてよいのは、拘束時間の算定に使う補助指標 `avg_paid_leave_days_taken`（平均有給取得日数・単位は日）だけである。

| 軸キー | 指標 | 単位 |
|---|---|---|
| `compensation_level` | 平均年間給与 | 円 |
| `annual_holidays` | 年間休日総数 | 日 |
| `monthly_overtime` | 月平均残業時間 | 時間 |
| `paid_leave_rate` | 年次有給休暇の取得率 | % |
| `turnover_rate` | 離職率 | % |
| `male_childcare_leave_rate` | 男性の育児休業取得率 | % |
| `revenue_growth` | 売上高の成長率（年率） | % |
| `operating_margin` | 営業利益率 | % |
| `equity_ratio` | 自己資本比率 | % |

各項目のフィールド:

| フィールド | 必須 | 記入基準 |
|---|---|---|
| `value` | 必須 | 数値、または確認できなかったことを表す `null`。文字列や真偽値は不可 |
| `unit` | 必須 | 上表の単位と同じ文字列 |
| `source_url` | `value` が非 null なら必須 | 出典の URL。`http` で始まる文字列 |
| `grade` | `value` が非 null なら必須 | `A`〜`D`。定義は `references/evidence-grading.md` |
| `as_of` | 推奨 | その値が指す時点（`YYYY-MM` または `YYYY`）。欠落は WARN |

**ルール**: 年間休日・残業・有給取得率・平均年間給与などの数値を収集した場合は、文章の claim に埋めるだけでなく、必ずこの company_metrics へ構造化して格納する（単位・出典URL・レベル併記）。確認できなければ `value` を `null` のままにする。

## 機械的な検証の規則（validate_company_research.py）

`scripts/validate_company_research.py` が機械的に検査する。ERROR が1件でもあれば FAIL（終了コード1）、ERROR 0件なら PASS（終了コード0。WARN があっても PASS）。

**ERROR（成果物として成立しない・ルール違反）**

- JSON として読み込めない
- `company` がオブジェクトでない／`company.name` が空
- `claims` が配列でない、または空
- claim の必須フィールド（`id`・`topic`・`statement`・`evidence`・`confidence`）の欠落
- `topic` が8種以外
- `confidence` が `high`/`medium`/`low` 以外
- `evidence` が空
- `source_url` が `http` で始まらない
- `grade` が A〜D 以外
- `quote` が空
- 必須7トピック（`philosophy`・`business`・`financials`・`compensation`・`benefits`・`workstyle`・`reputation`）のいずれかが1件も無い
- レベルC・Dのみを根拠とする claim に `confidence=high`
- `company_metrics` の欠落、または `company_metrics` が非オブジェクト
- `company_metrics` のキーが定量候補軸9個の軸キーでも `avg_paid_leave_days_taken` でもない
- `company_metrics` の各項目が非オブジェクト
- `value` が数値でも `null` でもない
- `unit` が軸ごとに定めた単位と異なる
- `value` が非 null の項目で、`source_url` が `http` 始まりの文字列でない
- `value` が非 null の項目で、`grade` が A〜D 以外

**WARN（成立するが根拠が弱い）**

- あるトピックの claim がすべてレベルC・Dのみの根拠である
- `selection_process` の claim が0件
- `research_date` が未設定
- `value` が非 null の項目に `as_of` が無い
- 定量候補軸9個のうち、`value` が非 null の軸が1つも無い

記入例は `assets/company_research_example.json`（架空企業）にある。
