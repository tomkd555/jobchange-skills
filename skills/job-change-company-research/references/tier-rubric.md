# Tier 格付けの原本仕様（tier-rubric）

企業研究の結論として付す **Tier** の定義・評価軸・格付け基準・記入形式を定める原本である。企業研究担当エージェント（job-change-company-researcher）がこの基準で `company_research.json` の `tier` を付け、独立監査（job-change-research-auditor）がこの基準に照らして妥当性を検査し、`scripts/validate_company_research.py` が構造・列挙・参照を機械検査する。

## Tier の性格

Tier は**企業そのものの質**を表す格付けである。利用者プロファイル（希望年収・保有スキル・転職の軸）には依存しない。したがって、同じ企業は誰にとっても同じ Tier になる。

- 「この企業は自分に合うか」という個人適合の判定は Tier では行わない。それは適合性評価（job-change-fit-assessment、`fit_assessment.json`）の役割であり、求人票・自己分析・通勤データを突き合わせて別途行う。
- Tier は `company_research.json` の claims と workstyle_metrics だけから算出する。profile.json は入力に取らない。

Tier は、企業スラッグの接頭辞（例 `A_ベータシステムズ` の `A_`）とは別物である。接頭辞は初期分類のための命名上の名残として残し、Tier の変化でディレクトリ名（スラッグ）をリネームしない。機械可読な Tier は本仕様の `tier` フィールドを原本とする。

## 評価軸（4軸）

各軸を `high` / `medium` / `low` / `unknown` の4段で評価する。判定は `claims`（および `workstyle_metrics`）の証拠に基づく。

| 軸キー | 名称 | 何を見るか | 主な根拠トピック |
|---|---|---|---|
| `financial_soundness` | 財務健全性・規模 | 売上・利益の水準、利益率、自己資本・継続性、事業規模。赤字・債務超過・継続疑義は低評価の材料 | `financials` |
| `growth` | 成長性 | 増収増益のトレンド、中期経営計画の実現度、市場・受注の拡大。縮小・一過性要因は割り引く | `financials`・`business` |
| `tech_advancement` | 技術先進性 | クラウド/AI/内製開発の度合い、パートナー等級（AWS APN Tier 等）・認定、技術発信（登壇・技術ブログ）、先進案件への関与機会 | `business`・`philosophy` |
| `compensation_level` | 処遇水準 | 平均年間給与、該当職種の報酬レンジ、賞与・等級制度、福利厚生・認定（くるみん・えるぼし・健康経営優良法人等）の充実 | `compensation`・`benefits`・`workstyle_metrics.avg_annual_salary` |

### 軸評価のルール

- 証拠グレードの下限を守る。`high` は A（一次公式）または B（信頼できる二次）の claim に支えられていなければならない。C・D（口コミ・伝聞）のみを根拠に `high` を付けない。
- 自己宣伝を根拠にしない。企業自身の評価的・自己宣伝的主張（採用サイトの「先進的」「風通しが良い」等。company_research 上で confidence を high にできない主張）を根拠に `high` を付けない。事実（開示数値・認定の有無・パートナー等級）で裏付ける。
- 不明を明示する。判定に足る証拠が無い軸は `unknown` にする。推測で埋めない。`unknown` の軸は `basis` に「何が確認できなかったか」を書く。

各軸には次を記す。

| フィールド | 必須 | 記入基準 |
|---|---|---|
| `rating` | 必須 | `high` / `medium` / `low` / `unknown` のいずれか |
| `basis` | 必須 | その評価に至った根拠を1〜2文で書く（非空） |
| `claim_ids` | 必須 | 根拠にした claim の id の配列。`rating` が `high`/`medium`/`low` のときは1件以上を推奨する。`unknown` のときは空配列 `[]` でよい。記載する id は `claims` に実在しなければならない |

## 総合 Tier の格付け基準

4軸の `rating` から総合 Tier（`level`）を次のとおり定める。`unknown` の軸は集計から除いて `high`（H）・`medium`（M）・`low`（L）の数を数える。

| Tier | 基準 |
|---|---|
| **S** | H が3以上、かつ L が0（全体に卓越。財務・成長・技術・処遇のいずれも高水準） |
| **A** | S に届かず、H が2以上、かつ L が0（堅実に良好） |
| **B** | S・A に届かず、L が1以下（標準的。際立った強みが限定的であるか、軽微な弱みがある） |
| **C** | L が2以上、または `financial_soundness` が `low`（課題が目立つ。財務・継続性に懸念があるものを含む） |

### 暫定格付け（provisional）

`unknown` の軸が2以上ある場合は、既知の軸から最も妥当な `level` を付けつつ、`provisional` を `true` にする。証拠が集まり次第、格付けを見直す前提であることを示す。`unknown` が1以下なら `provisional` は `false` とする。

## 記入形式（company_research.json の `tier`）

`company_research.json` のトップレベルに、次の `tier` オブジェクトを**必須**で置く（欠落は機械検証で ERROR）。

```json
"tier": {
  "level": "A",
  "provisional": false,
  "rubric_version": 1,
  "assessed_date": "YYYY-MM-DD",
  "axes": {
    "financial_soundness": { "rating": "high",   "basis": "…", "claim_ids": ["C010"] },
    "growth":              { "rating": "high",   "basis": "…", "claim_ids": ["C011", "C005"] },
    "tech_advancement":    { "rating": "medium", "basis": "…", "claim_ids": ["C003"] },
    "compensation_level":  { "rating": "high",   "basis": "…", "claim_ids": ["C020"] }
  },
  "rationale": "総合判定の根拠を1〜3文で書く。"
}
```

| フィールド | 必須 | 記入基準 |
|---|---|---|
| `level` | 必須 | `S` / `A` / `B` / `C` のいずれか。上記の格付け基準に従う |
| `provisional` | 必須 | 真偽値。`unknown` 軸が2以上なら `true`、1以下なら `false` |
| `rubric_version` | 推奨 | 本ルーブリックのバージョン。現行は `1` |
| `assessed_date` | 推奨 | 格付けを行った日付（`YYYY-MM-DD`） |
| `axes` | 必須 | 上記4軸すべて（`financial_soundness`・`growth`・`tech_advancement`・`compensation_level`）を持つオブジェクト |
| `rationale` | 必須 | 総合 `level` に至った根拠（非空） |

## 機械検証と監査の分業

| 担い手 | 検査する範囲 |
|---|---|
| 機械検証（validate_company_research.py） | `tier` の存在（欠落は ERROR）、`level` の列挙、4軸の網羅、各軸 `rating` の列挙、`claim_ids` の型と参照実在（`claims` に無い id を指すと ERROR）といった構造・列挙・参照を検査する。格付けの妥当性そのものは判定しない。 |
| 独立監査（job-change-research-auditor） | 各軸の `rating` が根拠 claim の証拠グレードに照らして妥当か（C・D単独や自己宣伝を根拠に `high` にしていないか）、`level` が4軸から格付け基準どおりに導かれているか、`provisional` の要否を検査する。妥当でなければ finding 化する。 |

この分業は証拠グレード（grade）の扱いと同じである。機械検証は列挙（A〜D）を、監査はグレード付与の妥当性を検査する。
