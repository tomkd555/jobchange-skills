# 自己分析の方法論（採用理論の根拠と限界）

<!-- textlint-disable jtf-style/4.3.2.大かっこ［］ -->
<!-- 本文中の [E1] 形式は出典 ID の記法である。半角大かっこを保つため、このファイルでは当該規則を無効化する。 -->

job-change-self-analysis スキルが採用する分析軸の実証的裏付けと限界を定める原本である。SKILL.md の原則・question-bank.md の質問設計・エージェント2体（writer / auditor）がこのファイルを参照する。証拠グレードは A〜D の4段階（A=査読済みの学術研究・一次公式、B=信頼できる二次、C=口コミ・集計・HRブログ、D=個人ブログ・伝聞）で表記し、学術研究には DOI を記す。表記形式は `[E番号] 文献名 (年) グレード DOI:xxx https://doi.org/xxx` とし、末尾の「出典一覧」に対応づける。

## 中核の制約: 内省は単独では信頼できない

本スキルの設計は、自己分析を内省単独で行ってはならないという制約を、最も裏付けの強い結論として置く（確度: ほぼ確実、90%以上）。

- 人は高次の認知過程を内省によって直接とらえることがほとんどできず、心的過程の言語報告は真の内省ではなく暗黙の因果理論に由来する[E45]。内省は無意識の心的過程への直接の経路を与えない。自己知識を高める有効な経路は、他者の目を通した自己観察と、自らの行動の観察である[E44]。人は自己の透明性を過信する（introspection illusion）[E51]。
- 他者評価（観察者評定）は、学業成績・職務遂行の予測において自己評価より高い予測妥当性を持ち、自己評価に対して増分的な妥当性を持つ（263標本・44,178名のメタ分析）[E49]。**この数値は単一の大規模メタ分析に由来する。**
- ただしフィードバックは万能ではない。フィードバック介入は平均では成績を高める（d=.41）が、3分の1超の介入では成績を低下させ、注意が課題から自己（人格）へ向かうほど有効性が下がる[E50]。**この d=.41 は単一の大規模メタ分析に由来する。**

この制約から、本スキルは次を運用規則とする。

1. 強み（strengths）は、行動証拠（behavioral_episodes）または他者証言（others_feedback）への対応づけを必須とする。内省だけを根拠とする強みは成果物として認めない（検証器が ERROR とする）。
2. 他者フィードバックの受け取りは課題志向で行う。「あなたはこういう人だ」という人格評価としてではなく、「どの行動が、どの結果につながったか」という行動と結果への対応づけとして記録する[E50]。
3. 内省で得た価値観・興味は、可能な限り過去の行動エピソードへ対応づけて裏付ける。

## 採用する4つの分析軸と実証的裏付け

分析の軸は「興味」「価値観」「career adaptability の4次元」「過去の行動」の4つに置く。妥当性・効果の裏付けが相対的に強い枠組みを採用する（確度: 可能性が非常に高い、80%以上90%未満）。

### 興味・興味適合（Holland の枠組み）

- 職業興味は職務業績（r=.14）・訓練成績（r=.26）と相関し、職務に焦点化した興味尺度では業績妥当性が .23 へ高まる[E1]。60研究・約568相関を統合したメタ分析で、興味と環境の適合（congruence）指標は個別の興味得点より業績予測力が高い[E2]。
- ただし興味適合と「全体的な職務満足」の関係は弱い。65年・105研究（N=39,602）のメタ分析で相関は ρ=0.19 にとどまり、適合は一般的職務満足よりも成果・キャリア満足との関連が強い[E11]。
- 運用: 興味は RIASEC の6領域（Realistic・Investigative・Artistic・Social・Enterprising・Conventional）の枠組みを軸名として使う。適合の高さを満足の保証と扱わない。興味診断の結果は確定ラベルとせず、内省と行動の裏付けを併せる。

### career adaptability の4次元

- 日本語版キャリア・アダプタビリティ尺度（CAAS-J）では、若年労働者を対象に4因子24項目モデルが高い適合度を示し、内的整合性は α=.97 であった[E8]。**この α=.97 は当該の単一研究に由来する。** 他言語版の典型値（α≈.93）よりやや上振れであり、単一の妥当性研究に基づく点に留保がある。
- concern（関心）・control（統制）・curiosity（好奇心）・confidence（自信）の4次元を分析の枠組みとする。次元名の枠組みのみ用い、尺度の項目文は転載しない（著作権のある尺度項目をそのまま転載することの禁止）。

### 過去の行動（行動証拠）

- 中途採用面接では、成果に至る行動プロセス（どの場面でどう考え、どう行動したか）に注目し、環境が変わっても機能する再現性を見極める[E42]。これは STAR／行動面接に自己分析の結果（過去の具体的行動）を載せる接点である。
- 前掲の内省の限界[E44]から、行動の観察は内省より信頼できる自己知識の経路である。behavioral_episodes を成果物の必須要素に置く根拠がここにある。

### 価値観

- 価値観は内省で言語化するが、単独では上記の内省の限界を受ける。過去の行動エピソードへ対応づけて裏付けることを運用規則とする（values は evidence_episode_ids でエピソードへ対応づける）。

### 補助: strengths 介入（well-being 面）

- signature strengths 介入のメタ分析（14論文・29効果量）で、ポジティブ感情 g=0.32、生活満足 g=0.42、抑うつ低減 g=0.21 であった[E12]。**効果は well-being（主観的幸福感）面での小〜中の効果であり、職務業績の向上を示すものではない。**
- 運用: 強みの言語化は自己記述で行い、商用の診断ツールに依存しない（後述の限界を参照）。

## 妥当性が弱い枠組みの限定使用

次の枠組みは、確定ラベルを与える診断としては用いず、内省を促す呼び水（質問群）としてのみ限定使用する。

- Schein のキャリア・アンカーは構成概念妥当性が弱い。Career Orientations Inventory は、7件の研究データを用いた最良適合モデルでも当てはまりが弱く[E7]、日本の大企業従業員1,083名でも創造性因子の概念的実在性の再検討が必要とされた[E6]。8分類は question-bank.md で呼び水として掲載してよいが、結果を確定した「自分のアンカー」として扱わない。
- 商用の strengths ツールは、独立した妥当性が限定的である。症状が主観的幸福感へ及ぼす影響を心理的強み・対人資源が緩衝するという主張は、223研究・N=127,587 のメタ分析で明確に支持されなかった[E10]。**この結果は単一の大規模メタ分析に由来する。** CliftonStrengths 等の商用ツールへの依存を避け、無償の自己記述で代替する。項目文をそのまま転載しない。
- RIASEC の自己診断ツールについては、キャリア介入としての有効性に関する既存の証拠が時代遅れで地理的にも限定的であり、決定的な結論を出せる段階にないと査読論文が指摘する[E23]。RIASEC は興味の枠組みとして使うが、診断ツールの介入効果を根拠にしない。

## 反すうを防ぐ運用規則

過度な内省は有害である（確度: 可能性が非常に高い、80%以上90%未満）。

- 反すう（rumination）は抑うつを悪化させ、問題解決を損ない、社会的支援をむしばむ。適応的な自己反省とは区別される[E52]。日本語話者を対象とした縦断研究でも、自己反すうは恐怖心の増加を予測する一方、自己内省は回避行動の減少を予測し、自己焦点の種類が効果を分ける[E54]。実務家も、内省が過剰になると逆効果になりうるとし、周囲との関係・観察を重視すべきと指摘する[E22]。
- 感情予測は系統的に誤る。人は将来の感情反応の強度・持続を過大評価する（インパクト・バイアス、焦点化が原因）[E55]。「この仕事に就けば幸せになれる／転職を後悔する」といった感情の将来予測は、自己分析の確信の根拠にしない。

運用規則:

1. 自己分析は question-bank.md の有限の構造化された問いに限定し、無制限の内省を促さない。
2. 「なぜ」の深掘りは、感情の反すうに落とさず、必ず行動・事実（エピソード）へ対応づける。
3. 感情の将来予測を、判断・断定の根拠にしない。emotion_note は当時の動機・感情の記録であり、将来の予測ではない。

## 論争点（両論併記）

- Dunning-Kruger 効果の機構は未決着である。能力下位者が自己を過大評価する現象（成績下位四分位が実測12パーセンタイルで自己を62パーセンタイルと推定）[E46]は数値として確認されるが、その機構を「メタ認知能力の欠如」とする解釈は争われている。非対称誤差は、平均への回帰と better-than-average ヒューリスティックで説明でき、両機構を除去すると消えるとの反論がある[E47]。一方、個人差データに適した検定では、効果が従来報告よりはるかに小さい可能性があるとの再解析もある[E48]。**本スキルは自己評価の過信の機構を断定しない**。この論争は、内省単独の自己評価を確定的に扱わない前記の運用規則を補強する。

## 実務手法の位置づけ

実務手法（Will-Can-Must、モチベーショングラフ、自分史／キャリアの棚卸し、他己分析、ジョハリの窓）は、進行の足場として有用である。ただし効果主張の多くは人材サービス提供者自身の自己報告であり[E14][E17][E19]、興味診断ツールの介入効果に関する証拠自体が弱い[E23]。

運用: 実務手法を質問設計・進行の足場として採用しつつ、「診断結果＝確定した自分」と扱わせない。手法の出力は内省・行動・他者証言で裏付けてから成果物へ取り入れる。

## 出典一覧

<!-- textlint-disable -->
<!-- 書誌形式（発行元. 表題. 年. グレード. URL）で出典を並べる節である。区切りのピリオドと社名の一部を和文の句読点・同義語として判定させないため、この節だけ無効化する。 -->

- [E1] Journal of Applied Psychology (APA). Are you interested? A meta-analysis of relations between vocational interests and performance/turnover. 2011. グレードA. DOI:10.1037/a0024343. https://doi.org/10.1037/a0024343
- [E2] Perspectives on Psychological Science (SAGE/APS). Vocational Interests and Performance: A Quantitative Summary. 2012. グレードA. DOI:10.1177/1745691612449021. https://doi.org/10.1177/1745691612449021
- [E6] 組織科学（組織学会）. キャリア・アンカー9因子モデルの適合性の検証. 2024. グレードA. DOI:10.11207/soshikikagaku.20240702-4. https://doi.org/10.11207/soshikikagaku.20240702-4
- [E7] Journal of Career Assessment (SAGE). Underlying Factor Structure of Schein's Career Anchor Model. 2013. グレードA. DOI:10.1177/1069072712475179. https://doi.org/10.1177/1069072712475179
- [E8] キャリア・カウンセリング研究（日本キャリア・カウンセリング学会）. 日本語版キャリア・アダプタビリティ尺度の開発. 2024. グレードA. DOI:10.34512/careercounseling.26.1_1. https://doi.org/10.34512/careercounseling.26.1_1
- [E10] Journal of Affective Disorders (Elsevier). Internalising symptoms and wellbeing: Meta-analysis of buffering. 2025. グレードA. DOI:10.1016/j.jad.2025.119809. https://doi.org/10.1016/j.jad.2025.119809
- [E11] Journal of Vocational Behavior (Elsevier). Interest fit and job satisfaction: A systematic review and meta-analysis. 2020. グレードA. DOI:10.1016/j.jvb.2020.103503. https://doi.org/10.1016/j.jvb.2020.103503
- [E12] Journal of Happiness Studies (Springer). The Impact of Signature Character Strengths Interventions: A Meta-Analysis. 2019. グレードA. DOI:10.1007/s10902-018-9990-2. https://doi.org/10.1007/s10902-018-9990-2
- [E14] リクルート（リクナビNEXT）. 自己分析のフレームワーク＆手法11種（Will-Can-Must）. 2021-05-28. グレードB（自己報告）. https://next.rikunabi.com/tenshokuknowhow/archives/25424/
- [E17] リクルート（リクナビNEXT）. 自己分析手法11種の一覧. 2021-05-28. グレードB（自己報告）. https://next.rikunabi.com/tenshokuknowhow/archives/25424/
- [E19] キャリコンスタディ（LIFE&CAREER LLC）. 【キャリコン】自己理解の支援. 2020-09-24. グレードC. https://careerconsultant-study.com/jikorikai-support/
- [E22] THE CAREER STORY（就活の教科書）. 法政大学 児美川孝一郎教授インタビュー. 2024-08-20. グレードC. https://reashu.com/story/professor-interview-komikawa/
- [E23] Frontiers in Organizational Psychology. RIASEC self-assessment tools as career interventions. 2026-04-24. グレードA. https://www.frontiersin.org/journals/organizational-psychology/articles/10.3389/forgp.2026.1792707/full
- [E42] Humanage, Inc.（i-note）. 中途採用で活躍する人材を見極める面接術（再現性）. 2025-05-30. グレードC. https://www.i-note.jp/assessment/tekisei-kensa/articles/028.html
- [E44] Annual Review of Psychology. Self-knowledge: its limits, value, and potential for improvement. 2004. グレードA. DOI:10.1146/annurev.psych.55.090902.141954. https://doi.org/10.1146/annurev.psych.55.090902.141954
- [E45] Psychological Review (APA). Telling more than we can know: Verbal reports on mental processes. 1977. グレードA. DOI:10.1037/0033-295X.84.3.231. https://doi.org/10.1037/0033-295X.84.3.231
- [E46] Journal of Personality and Social Psychology (APA). Unskilled and unaware of it. 1999. グレードA. DOI:10.1037/0022-3514.77.6.1121. https://doi.org/10.1037/0022-3514.77.6.1121
- [E47] Journal of Personality and Social Psychology (APA). Unskilled, unaware, or both? The better-than-average heuristic. 2002. グレードA. DOI:10.1037/0022-3514.82.2.180. https://doi.org/10.1037/0022-3514.82.2.180
- [E48] Intelligence (Elsevier). The Dunning-Kruger effect is (mostly) a statistical artefact. 2020. グレードA. DOI:10.1016/j.intell.2020.101449. https://doi.org/10.1016/j.intell.2020.101449
- [E49] Psychological Bulletin (APA). An other perspective on personality: Meta-analytic integration of observers' accuracy. 2010. グレードA. DOI:10.1037/a0021212. https://doi.org/10.1037/a0021212
- [E50] Psychological Bulletin (APA). The effects of feedback interventions on performance. 1996. グレードA. DOI:10.1037/0033-2909.119.2.254. https://doi.org/10.1037/0033-2909.119.2.254
- [E51] Advances in Experimental Social Psychology (Elsevier). The Introspection Illusion. 2009. グレードA. DOI:10.1016/s0065-2601(08)00401-2. https://doi.org/10.1016/s0065-2601(08)00401-2
- [E52] Perspectives on Psychological Science. Rethinking Rumination. 2008. グレードA. DOI:10.1111/j.1745-6924.2008.00088.x. https://doi.org/10.1111/j.1745-6924.2008.00088.x
- [E54] 感情心理学研究（日本感情心理学会）. 自己反すうと自己内省が社交不安に及ぼす影響. 2017. グレードA. DOI:10.4092/jsre.25.1_17. https://doi.org/10.4092/jsre.25.1_17
- [E55] Current Directions in Psychological Science. Affective forecasting: Knowing what to want. 2005. グレードA. DOI:10.1111/j.0963-7214.2005.00355.x. https://doi.org/10.1111/j.0963-7214.2005.00355.x

<!-- textlint-enable -->
