# company_research.json の原本仕様（company-research-format）

企業研究の構造化データ `company_research.json` のフィールド仕様・記入基準・機械検証規則を定める原本である。企業研究担当エージェント（job-change-company-researcher）がこの仕様で成果物を作り、`scripts/validate_company_research.py` がこの仕様に照らして機械検査する。

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
  "tier": {
    "level": "A",
    "provisional": false,
    "rubric_version": 1,
    "assessed_date": "YYYY-MM-DD",
    "axes": {
      "financial_soundness": { "rating": "high",   "basis": "…", "claim_ids": ["C010"] },
      "growth":              { "rating": "high",   "basis": "…", "claim_ids": ["C011"] },
      "tech_advancement":    { "rating": "medium", "basis": "…", "claim_ids": ["C003"] },
      "compensation_level":  { "rating": "high",   "basis": "…", "claim_ids": ["C020"] }
    },
    "rationale": "総合判定の根拠。"
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

`name` が空の場合は機械検証で ERROR となる。`securities_code`・`edinet_code` は無くても ERROR にはならない。

### research_date（文字列・推奨）

調査を実施した日付（`YYYY-MM-DD`）。未設定の場合は機械検証で WARN となる。情報の鮮度を後で判断するために記す。

### claims（配列・必須、1件以上）

企業に関する主張の配列。1件以上が必須で、空の場合は ERROR となる。各 claim は次のフィールドを持つ。

| フィールド | 必須 | 記入基準 |
|---|---|---|
| `id` | 必須 | claim の識別子。`C001` から連番を推奨する（機械検証は連番までは要求しない） |
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

**ルール**: グレードC・Dのみを根拠とする claim に `high` を与えてはならない（ERROR）。企業自身の評価的・自己宣伝的主張は、出典がグレードAでも `high` にしない（B 相当扱い。機械検証では判定できず監査エージェントの領分）。

### open_questions（配列・推奨）

裏取りできなかった論点、出所間の食い違い、一次情報の代表性の限界などを記す。例:「有報の平均年間給与は全従業員平均であり、応募職種の給与水準は判別できない。」

### workstyle_metrics（オブジェクト・任意）

働き方・報酬の主要数値を、機械可読な集約値として構造化するトップレベルの任意フィールドである。散文の `claims` とは独立に、追加のフィールドとして持つ。後続の処理（実質時給の試算など）が数値をそのまま使えるようにするための転記であり、根拠は対応する `claims` の evidence にある。

5つのキーを持つ。各値は `{value, source_url, grade}` のオブジェクト、または `null`（見つからなければ null のままにする。創作しない）。

| キー | 内容 | 単位の目安 |
|---|---|---|
| `annual_holidays` | 年間休日数 | 日 |
| `monthly_overtime_h` | 月平均残業時間 | 時間 |
| `paid_leave_rate` | 有給取得率 | %（またはIR表記に合わせた率） |
| `avg_paid_leave_days_taken` | 平均有給取得日数（実績） | 日 |
| `avg_annual_salary` | 平均年間給与（想定年収の対照に使う） | 円 |

各メトリックのフィールド:

| フィールド | 必須 | 記入基準 |
|---|---|---|
| `value` | 必須 | 数値。文字列や真偽値は不可 |
| `source_url` | 必須 | 出典の URL。`http` で始まる文字列 |
| `grade` | 必須 | `A`〜`D`。定義は `references/evidence-grading.md` |

**ルール**: 年間休日・残業・有給取得率・平均年間給与などの数値を収集した場合は、散文の claim に埋めるだけでなく、必ずこの workstyle_metrics へ構造化して格納する（出典URL・グレード併記）。見つからなければ `null` のままにする。

### tier（オブジェクト・必須）

企業研究の結論として付す、**企業そのものの質**の格付けである。トップレベルの必須フィールドで、欠落は機械検証で ERROR となる。利用者プロファイル（希望年収・スキル・転職の軸）には依存せず、`claims` と `workstyle_metrics` だけから算出する。軸の定義・評価ルール・格付け基準・記入形式の原本は `references/tier-rubric.md` にある。

4軸（`financial_soundness`・`growth`・`tech_advancement`・`compensation_level`）を `high`/`medium`/`low`/`unknown` で評価し、その集計から総合 `level`（`S`/`A`/`B`/`C`）を付す。

| フィールド | 必須 | 記入基準 |
|---|---|---|
| `level` | 必須 | `S`/`A`/`B`/`C` のいずれか。格付け基準は `references/tier-rubric.md` |
| `provisional` | 必須 | 真偽値。`unknown` 軸が2以上なら `true`、1以下なら `false` |
| `rubric_version` | 推奨 | ルーブリックのバージョン（現行 `1`）。欠落は WARN |
| `assessed_date` | 推奨 | 格付けを行った日付（`YYYY-MM-DD`）。欠落は WARN |
| `axes` | 必須 | 4軸すべてを持つオブジェクト。各軸は `{rating, basis, claim_ids}` |
| `rationale` | 必須 | 総合 `level` に至った根拠（非空） |

各軸（`axes.<軸>`）のフィールド:

| フィールド | 必須 | 記入基準 |
|---|---|---|
| `rating` | 必須 | `high`/`medium`/`low`/`unknown` のいずれか |
| `basis` | 必須 | 評価の根拠を書く（非空） |
| `claim_ids` | 必須 | 根拠 claim の id の配列。`claims` に実在する id でなければならない。`unknown` のときは空配列でよい |

**ルール**: `high` は A・B グレードの claim に支えられていなければならず、C・D 単独や企業の自己宣伝的主張を根拠に `high` を付けない（機械検証では判定できず、監査エージェントの領分）。判定に足る証拠が無い軸は `unknown` にし、推測で埋めない。

## 機械検証規則（validate_company_research.py）

`scripts/validate_company_research.py` が決定的に検査する。ERROR が1件でもあれば FAIL（終了コード1）、ERROR 0件なら PASS（終了コード0。WARN があっても PASS）。

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
- グレードC・Dのみを根拠とする claim に `confidence=high`
- `workstyle_metrics` が存在し、オブジェクトでない
- `workstyle_metrics` の各メトリックが存在し（非 null）、`value` が非数値・`source_url` が `http` 始まりでない・`grade` が A〜D 以外のいずれか
- `tier` の欠落、または `tier` が非オブジェクト
- `tier.level` が `S`/`A`/`B`/`C` 以外、`tier.provisional` が非真偽値、`tier.rationale` が空
- `tier.axes` が非オブジェクト、または4軸（`financial_soundness`・`growth`・`tech_advancement`・`compensation_level`）のいずれかが欠落
- いずれかの軸の `rating` が `high`/`medium`/`low`/`unknown` 以外、`basis` が空、`claim_ids` が非配列、または `claim_ids` が `claims` に存在しない id を参照

**WARN（成立するが根拠が弱い）**

- あるトピックの claim がすべてグレードC・Dのみの根拠である
- `selection_process` の claim が0件
- `research_date` が未設定
- `workstyle_metrics` 全体が欠落している
- `workstyle_metrics` の個別メトリックが欠落または `null` である
- `tier.rubric_version` または `tier.assessed_date` が未設定
- `rating` が `high`/`medium`/`low` の軸に根拠 `claim_ids` が無い

記入例は `assets/company_research_example.json`（架空企業）にある。
