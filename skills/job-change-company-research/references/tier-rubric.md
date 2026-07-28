# Tier 格付けの原本仕様（tier-rubric）

企業研究の結論として付す **Tier** の候補軸・評価基準・総合格付けの規則・記入形式を定める原本である。軸の評価（`rating` と `basis`）は企業研究担当エージェント（job-change-company-researcher）が `company_research.json` の `tier` へ書き、独立監査（job-change-research-auditor）が妥当性を検査し、`scripts/validate_company_research.py` が構造・列挙・参照を機械検査する。総合の格付け（`level`）は利用者の重視軸に依存するため、適合性評価スキル（job-change-fit-assessment）が算出する。

## 軸の評価と総合の格付けを分ける理由

企業のどの側面を重んじるかは利用者によって異なる。日本標本の政策捕捉法では、給与と社風の順位が自己効力感の高低や性別で入れ替わり、勤務医の離散選択実験では夜間業務を避ける度合いが既婚女性と50歳以上で強い。豪州の政策捕捉法では、企業魅力度の評価の分散の40%が回答者間の差に帰属する。全利用者へ同じ重みを当てる根拠は無い（根拠と限界は `job-change-fit-assessment/references/fit-methods.md`）。

そこで担い手を次のように分ける。

| 対象 | 内容 | 担い手 |
|---|---|---|
| 軸の `rating` と `basis` | 企業側の事実。誰が見ても同じ | 企業研究（`company_research.json` の `tier.axes`） |
| 総合の `level` | 利用者が重んじる軸に依存する | 適合性評価（`fit_assessment.json` の `company_tier`） |

企業研究担当は Web 検索と Web 取得を持つため、`profile.json` を渡してはならない。渡すのは評価する軸の識別子の配列だけである。この配列は氏名・在籍企業名・現年収を含まないため、個人情報の境界を越えない。

Tier は、企業スラッグの接頭辞（例 `A_ベータシステムズ` の `A_`）とは別物である。接頭辞は初期分類のための命名上の名残として残し、Tier の変化でディレクトリ名（スラッグ）をリネームしない。

## 候補軸

利用者は次の候補から重視する軸を選ぶ。既定で選択済みなのは `compensation_level` だけであり、他は利用者が選んだときにだけ評価の対象になる。

| 軸キー | 名称 | 何を見るか | 主な根拠トピック | 既定 |
|---|---|---|---|---|
| `compensation_level` | 処遇水準 | 平均年間給与、該当職種の報酬レンジ、賞与・等級制度、福利厚生・認定の充実 | `compensation`・`benefits`・`workstyle_metrics.avg_annual_salary` | 選択済み |
| `financial_soundness` | 財務健全性・規模 | 売上・利益の水準、利益率、自己資本・継続性、事業規模。赤字・債務超過・継続疑義は低評価の材料 | `financials` | 候補 |
| `retention` | 定着 | 平均勤続年数、3年後定着率、離職率。同業・同規模の水準と照らす | `workstyle`・`reputation`・`workstyle_metrics` | 候補 |
| `work_style` | 働き方 | 月平均残業時間、年間休日、有給取得率、リモート勤務・フレックスの可否と運用実態 | `workstyle`・`workstyle_metrics` | 候補 |
| `employment_stability` | 雇用の安定性 | 雇用形態、事業の継続性、人員削減の履歴、労働基準関係法令違反の公表事案 | `workstyle`・`financials`・`reputation` | 候補 |
| `growth` | 成長性 | 増収増益のトレンド、中期経営計画の実現度、市場・受注の拡大。縮小・一過性要因は割り引く | `financials`・`business` | 候補 |
| `tech_advancement` | 技術先進性 | クラウド・AI・内製開発をどの程度進めているか、パートナー等級・認定、技術発信、先進案件への関与機会 | `business`・`philosophy` | 候補 |

`growth` と `tech_advancement` を既定から外すのは、この2軸を属性として検証した日本の研究を特定できていないためである。処遇水準を既定で選択済みとするのは、日本標本の政策捕捉法で給与水準が仕事内容に次ぐ重みを持つと推定されているためである。

## 軸評価のルール

各軸を `high` / `medium` / `low` / `unknown` の4段で評価する。判定は `claims`（および `workstyle_metrics`）の証拠に基づく。

- 証拠グレードの下限を守る。`high` は A（一次公式）または B（信頼できる二次）の claim に支えられていなければならない。C・D（口コミ・伝聞）のみを根拠に `high` を付けない。
- 自己宣伝を根拠にしない。企業自身の評価的・自己宣伝的主張（採用サイトの「先進的」「風通しが良い」等。company_research 上で confidence を high にできない主張）を根拠に `high` を付けない。事実（開示数値・認定の有無・パートナー等級）で裏付ける。
- 不明を明示する。判定に足る証拠が無い軸は `unknown` にする。推測で埋めない。`unknown` の軸は `basis` に「何が確認できなかったか」を書く。
- 評価するのは、指示書で渡された軸だけである。軸の指定が無い場合は `compensation_level` だけを評価する。

各軸には次を記す。

| フィールド | 必須 | 記入基準 |
|---|---|---|
| `rating` | 必須 | `high` / `medium` / `low` / `unknown` のいずれか |
| `basis` | 必須 | その評価に至った根拠を1〜2文で書く（非空） |
| `claim_ids` | 必須 | 根拠にした claim の id の配列。`rating` が `high`/`medium`/`low` のときは1件以上を推奨する。`unknown` のときは空配列 `[]` でよい。記載する id は `claims` に実在しなければならない |

## 重視の段階

利用者は選んだ軸へ、次の3段階のいずれかを付ける。重みを百分率などの数値で申告させない。自己申告した数値は、実際の選択から推定した重みとずれるためである。候補から選ばせ、「この2社ならどちらを選ぶか」という形の比較で順位を確かめる。

| 段階 | 値 | 意味 |
|---|---|---|
| 最重視 | `top` | ここが低い企業は候補にしない軸 |
| 重視 | `high` | 総合の格付けに反映する軸 |
| 参考 | `reference` | 見ておきたいが格付けには反映しない軸 |

段階の申告の形式は、hub の `references/profile-format.md` の `company_quality_axes` を原本とする。

## 総合 Tier の格付け規則

適合性評価が、企業研究の軸評価と利用者の重視段階から `level` を決める。

対象軸は、段階が `top` または `high` の軸のうち `rating` が `unknown` でないものである。`reference` の軸は集計に入れず、報告で併記する。

| Tier | 規則 |
|---|---|
| **C** | `top` の軸に `low` がある。または対象軸の `low` が2以上 |
| **S** | C に当たらず、`top` の軸が1件以上あってそのすべてが `high`、かつ対象軸に `low` が無い |
| **A** | C・S に当たらず、対象軸の `high` が2以上、かつ `low` が0 |
| **B** | 上記のいずれにも当たらない |

判定は C・S・A・B の順に当てはめる。

`provisional`（暫定）は、段階が `top` または `high` の軸のうち `rating` が `unknown` のものが2以上ある場合、または `top` の軸に `unknown` がある場合に `true` にする。証拠が集まり次第、格付けを見直す前提であることを示す。

次の2つの場合、`level` は算出せず `null` にする。重みを仮定して格付けしない。

- 利用者が重視軸を申告していない場合。段階が `reference` の軸だけを申告した場合もこれに含める。
- 段階が `top` または `high` の軸がすべて `unknown` で、対象軸が1件も無い場合。この場合は `provisional` を `true` にする。

この規則の実装は `job-change-fit-assessment/scripts/calculate_company_tier.py` である。規則を変えるときは、本文書・スクリプト・単体テストをそろえて変える。

## 記入形式（company_research.json の `tier`）

`company_research.json` のトップレベルに、次の `tier` オブジェクトを**必須**で置く（欠落は機械検証で ERROR）。

```json
"tier": {
  "rubric_version": 2,
  "assessed_date": "YYYY-MM-DD",
  "axes": {
    "compensation_level": { "rating": "high",   "basis": "…", "claim_ids": ["C020"] },
    "retention":          { "rating": "medium", "basis": "…", "claim_ids": ["C011"] }
  }
}
```

| フィールド | 必須 | 記入基準 |
|---|---|---|
| `rubric_version` | 推奨 | 本ルーブリックのバージョン。現行は `2` |
| `assessed_date` | 推奨 | 軸を評価した日付（`YYYY-MM-DD`） |
| `axes` | 必須 | 評価した軸のオブジェクト。1軸以上。キーは候補軸のいずれかでなければならない |

総合の `level`・`provisional`・`rationale` は `company_research.json` に置かない。これらは利用者の重視段階に依存するため、適合性評価が `fit_assessment.json` の `company_tier` へ書く。

## 機械検証と監査の分業

| 担い手 | 検査する範囲 |
|---|---|
| 機械検証（validate_company_research.py） | `tier` の存在（欠落は ERROR）、`axes` が1軸以上あること、キーが候補軸の列挙に含まれること、各軸 `rating` の列挙、`basis` の非空、`claim_ids` の型と参照実在（`claims` に無い id を指すと ERROR）を検査する。軸評価の妥当性そのものは判定しない。 |
| 独立監査（job-change-research-auditor） | 各軸の `rating` が根拠 claim の証拠グレードに照らして妥当か（C・D単独や自己宣伝を根拠に `high` にしていないか）、指示された軸を過不足なく評価しているかを検査する。妥当でなければ finding 化する。 |
| 機械算出（calculate_company_tier.py） | 総合の `level` と `provisional` を、上記の格付け規則どおりに決定的に算出する。 |

この分業は証拠グレード（grade）の扱いと同じである。機械検証は列挙（A〜D）を、監査はグレード付与の妥当性を検査する。
