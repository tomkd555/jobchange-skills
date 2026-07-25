# 回答評価の原本（4観点・3段階アンカー）

模擬面接で収集した回答を評価するアンカー（各段階の判定基準を言語化した記述）の原本である。job-change-interview-coach の Step 3 の判定定義と一致させる。評価は4観点で行い、各観点を3段階（充足・一部・不足）で判定する。企業非依存の縮退モードでは企業理解観点を対象外とする。

## 4観点と3段階のアンカー

各観点の JSON キー（`scores` 内）を併記する。

### STAR（`scores.star`）

状況（Situation）・課題（Task）・行動（Action）・結果（Result）の4要素の有無で判定する。

| 段階 | 判定 |
|---|---|
| 充足 | 4要素がそろっている。 |
| 一部 | 一部の要素が欠落している。 |
| 不足 | 大半の要素が欠落している。 |

### 具体性（`scores.specificity`）

数値・固有名詞による裏付けの有無で判定する。

| 段階 | 判定 |
|---|---|
| 充足 | 数値・固有名詞による裏付けがある。 |
| 一部 | 裏付けが部分的である。 |
| 不足 | 抽象論のみで裏付けがない。 |

### 一貫性（`scores.consistency`）

転職理由と志望動機の矛盾の有無で判定する。根拠参照先は profile.json の `job_change_axis` に加え、`self_analysis.json`（あれば）の `career_narrative`（一貫する動機）と `reason_for_change`（建設的な言い換えと `job_change_axis.reasons` との整合の説明）とする。

| 段階 | 判定 |
|---|---|
| 充足 | 矛盾がない。 |
| 一部 | 軽微な齟齬がある。 |
| 不足 | 明確な矛盾がある。 |

### 企業理解（`scores.company_fit`）

回答が company_research.json の claim に結び付いているかで判定する。縮退モード（company_research.json が無い場合）は対象外とする。

| 段階 | 判定 |
|---|---|
| 充足 | claim への明確な結び付きがある。 |
| 一部 | 結び付きが断片的である。 |
| 不足 | 結び付きがない。 |

## 良い回答の要素

高く評価される回答が備える要素である[E69]。

| 要素 | 内容 |
|---|---|
| 具体性 | 抽象論でなく、具体的な状況・行動で語る。 |
| 定量性 | 成果を数値で裏付ける。 |
| 主体性 | 本人が担った役割・判断・行動を主語にして述べる（他者・組織の成果と区別する）。 |
| アンサーファースト | 結論を先に述べ、根拠を後に続ける。 |
| 行動（Action）への時間配分 | 回答時間の50〜60%を Action に割き、STAR のうち Action の記述を厚くする。行動基準評定尺度（BARS）で採点するビヘイビアラル面接で特に重視される[E69]。 |

## 学術的根拠

面接対策で構造化面接・過去行動面接に沿った準備を推奨する根拠と、その限界・未決着点を示す。断定できない論点は両論を併記する。すべて DOI を付す。

### 構造化面接の予測的妥当性

構造化面接（質問と評価基準を事前に定めた面接）は、非構造化面接より予測的妥当性が高い。McDaniel et al.（1994）は245係数・N=86,311のメタ分析で、構造化面接が非構造化面接より妥当性が高いと結論した[E74]。Conway et al.（1995）は信頼性由来の妥当性上限を、高度に構造化した面接で .67、非構造化面接で .34 と推定した[E79]。

妥当性の絶対水準については、次の2つの推定が併存し、確定値として扱えない（両論併記）。

| 推定 | 内容 |
|---|---|
| 古典的推定（Schmidt & Hunter 1998） | 選考手法の予測的妥当性を85年分の研究で総括し、一般知的能力（GMA）単独 .51、GMA＋構造化面接 .63 等を示した[E73]。この .51 前後の値が長く標準として用いられてきた。 |
| 下方修正（Sackett et al. 2022） | 従来の推定は range restriction（選抜による分散の縮小）の過大補正を含むとして妥当性を下方修正し、構造化面接を相対的に最上位に位置づけた。構造化面接の妥当性は約 .42 と見積もられる[E75]。ただしこの下方修正（range restriction 補正の是非）は Oh, Le & Roth（2023）との間で係争中であり、いずれの係数も確定値ではない[E82]。相対順位（構造化面接・作業標本・GMA が上位）はおおむね保持される。 |

含意: 構造化・行動面接を前提とした STAR 準備は学術的に支持される。ただし妥当性の絶対水準は下方修正されており、面接手法を万能視しない。

### 過去行動面接と状況面接の優劣（未決着）

面接質問の形式は2種類に分かれる。過去の行動を問う過去行動面接（「〜のとき、実際にどう行動したか」）と、仮定の状況での対応を問う状況面接（「〜の状況なら、どう対応するか」）である。両者の優劣は学術的に未決着であり、両形式に備える必要がある（両論併記）。

- McDaniel et al.（1994）は状況面接を最上位とした[E74]。
- Taylor & Small（2002）は、過去行動（行動記述）質問が状況質問より高い妥当性（.63 対 .47）を示すと報告した[E78]。

### 印象操作と、事実に基づく準備の含意

Levashina & Campion（2007）は、面接で応募者の90%超が何らかの印象操作をすると報告した（単一研究由来。独立した研究による同水準の再現が得られていないため断定は避ける）[E80]。含意は、脚色すると深掘りで矛盾が露見しうるため、事実に基づく具体的な準備が最善という点にある。この含意は、上記の評価アンカー（具体性・一貫性を数値と固有名詞で裏付ける）と整合する。

## 出典

- [E69] CareerTestPrep. Behavioural Interview Questions: The Complete STAR Method Guide 2026. 2026-05-31. グレードB. https://www.careertestprep.com/blog/behavioural-interview-questions-star-method
- [E73] Psychological Bulletin. The validity and utility of selection methods in personnel psychology: Practical and theoretical implications of 85 years of research findings. 1998. グレードA. DOI:10.1037/0033-2909.124.2.262 https://doi.org/10.1037/0033-2909.124.2.262
- [E74] Journal of Applied Psychology. The validity of employment interviews: A comprehensive review and meta-analysis. 1994. グレードA. DOI:10.1037/0021-9010.79.4.599 https://doi.org/10.1037/0021-9010.79.4.599
- [E75] Journal of Applied Psychology. Revisiting meta-analytic estimates of validity in personnel selection: Addressing systematic overcorrection for restriction of range. 2022. グレードA. DOI:10.1037/apl0000994 https://doi.org/10.1037/apl0000994
- [E78] Journal of Occupational and Organizational Psychology. Asking applicants what they would do versus what they did do: A meta-analytic comparison of situational and past behaviour employment interview questions. 2002. グレードA. DOI:10.1348/096317902320369712 https://doi.org/10.1348/096317902320369712
- [E79] Journal of Applied Psychology. A meta-analysis of interrater and internal consistency reliability of selection interviews. 1995. グレードA. DOI:10.1037/0021-9010.80.5.565 https://doi.org/10.1037/0021-9010.80.5.565
- [E80] Journal of Applied Psychology. Measuring faking in the employment interview: Development and validation of an interview faking behavior scale. 2007. グレードA（単一研究）. DOI:10.1037/0021-9010.92.6.1638 https://doi.org/10.1037/0021-9010.92.6.1638
- [E82] Journal of Applied Psychology. Correcting for range restriction in meta-analysis: A reply to Oh et al. (2023). 2023. グレードA. DOI:10.1037/apl0001116 https://doi.org/10.1037/apl0001116
