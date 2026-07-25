# キャリア・ナラティブと退職理由の建設的言語化

job-change-self-analysis スキルが、自己分析の素材（エピソード・他者証言・興味・価値観・career adaptability）を「一貫したキャリア・ナラティブ」と「退職理由の建設的な言語化」へ統合する基準の原本である。writer エージェントが career_narrative と reason_for_change を起草するとき、また面接対策・志望動機の深化（interview-prep / documents）が一貫性の根拠として読むときに参照する。証拠グレードと DOI 表記は self-analysis-methods.md と同じ規約に従う。

## なぜナラティブへ接続するのか

自己分析の成果は、面接・志望動機の一貫性を通じて選考へ接続する（確度: 可能性が高い、65%以上80%未満）。

- Career Construction Interview（CCI）は、5〜7問でライフテーマを聞き取り、自己概念と職業役割を結ぶ一貫したキャリアストーリー（narrative identity）を共同で構築する枠組みである[E43]。これは自己分析の結果を志望動機・面接回答の一貫性へつなぐ学術的な枠組みにあたる。
- 企業は転職理由・志望動機を面接の評価項目に含み、行動の再現性を見極める[E42]。企業は、能力を客観的に評価する基準が欠けていることを課題とするため[E24][E25]、応募者側の一貫した言語化は評価の接点になりうる。

**留保**: ナラティブの一貫性が選考評価（合否・内定率）を高めるという国内実証は取得できていない。本スキルは、この接続を「一貫性が評価の接点になりうる」という水準にとどめ、一貫性が合否を保証するとは扱わない。

## キャリア・ナラティブの構成要素

career_narrative を、CCI の枠組み（ライフテーマ・転機・一貫する動機）に沿って構成する。

| 要素 | 内容 |
|---|---|
| life_theme（ライフテーマ） | 複数のエピソードを貫く関心の主題。個別の成果の羅列ではなく、それらに共通して表れる方向を1文で表す。question-bank.md の CCI 型5問（憧れた人物・雑誌や番組・好きな物語・座右の銘・幼少期の記憶）の答えを素材にする。 |
| turning_points（転機） | 関心・行動が変わった節目。behavioral_episodes のうち、方向を決めた出来事を選ぶ。 |
| consistent_motivation（一貫する動機） | 複数の場面で繰り返し表れる動機。エピソードと価値観（values）から、一貫して働いている動機を抽出する。 |
| future_direction（今後の方向） | 一貫する動機が次に向かう先。reason_for_change の constructive_version と整合させる。 |

構成のルール:

1. ナラティブの各要素は、behavioral_episodes・others_feedback・values のいずれかの素材に裏付けられる範囲で書く。素材にない事実を創作しない。
2. 感情の将来予測（「この仕事に就けば満たされる」）をナラティブの根拠にしない[E55]。動機は過去の行動から抽出し、将来の感情の予測で代替しない。

## 退職理由の建設的な言語化

reason_for_change は、不満の列挙（raw_reasons）を、発揮したい価値を軸にした説明（constructive_version）へ変換する。

変換手順:

1. raw_reasons を加工せずに記録する。現状の不満や、退職を考える元の理由を、飾らずに列挙する。これは変換の出発点であり、そのまま外部へ出す文ではない。
2. 不満の裏にある「発揮したい価値」を特定する。各不満について、「では何を実現したいのか」を問い、values・career_narrative の consistent_motivation と対応づける。不満（避けたいこと）を、実現したいこと（向かいたいこと）へ言い換える。
3. constructive_version を、実現したいことを主語にして書く。現職の否定ではなく、発揮したい価値を軸に書く。constructive_version は raw_reasons と別の文でなければならない（同一の文字列のままであれば、検証器が WARN とする）。
4. consistency_note で profile.json との整合を確認する。profile.json の `job_change_axis.reasons`（次に実現したいことで書かれた転職理由）と、constructive_version の軸が一致するかを確認し、ずれがあれば説明する。

変換の例を次に示す。構造のみを示すものであり、実データは利用者の素材による。

- raw_reason（不満）:「今の環境では、運用の設計まで踏み込めない」
- 特定した価値:「個人の対応を仕組みへ残して再現性を上げたい」
- constructive_version（実現したいこと）:「個人の対応を仕組みへ残す働き方を、運用の設計まで担える範囲で発揮したい」

ルール: 不満は隠さない。ただし、不満の列挙で終わらせない。建設的言い換えは、事実（エピソード・価値観）に裏打ちされた「発揮したい価値」であって、現状を実際より良く見せる誇張ではない。

## 企業側の評価との接続

自己分析の成果を、企業が評価する観点へ接続する。ただし志望動機の重みは企業により変動する点に留保を置く。

- 20代を対象にした経験者採用の面接で、人事担当者が見るポイントとして最も多いのは人柄・社風との相性（86.2%）であり、経験・実績（60.8%）、転職理由（55.3%）、志望動機（49.4%）が続く[E40]。**この数値は、母集団を20代に限定した単一の調査に由来する。** 転職理由・志望動機が上位に入る一方、人柄・実績が上回る点は、自己分析の接続の価値と限界の双方を示す。
- 志望動機の重みは企業により変動する。スキル・経験を重視する企業では志望動機の優先度が低く、面接で聞かれない場合もある[E41]。
- 中途採用面接では、成果に至る行動プロセス（どの場面でどう考え、どう行動したか）に注目し、環境が変わっても機能する再現性を見極める[E42]。behavioral_episodes の reproducibility は、この再現性の観点へ直接対応する。

接続の運用:

1. STAR素材（behavioral_episodes）は、metric（定量値）と reproducibility（再現性）を備えると、企業の「能力の客観評価基準の欠如」[E25]という課題への接点になる。
2. career_narrative と reason_for_change.constructive_version は、面接の「一貫性」の観点（interview-prep が評価する）と、志望動機（documents が書く）の根拠として渡す。
3. 志望動機を最上位の決め手として扱わない。企業により重みが変わるため、人柄・相性・実績の裏付け（エピソード・他者証言）を併せて用意する。

## 出典一覧

<!-- textlint-disable -->
<!-- 書誌形式（発行元. 表題. 年. グレード. URL）で出典を並べる区画である。区切りのピリオドと社名の一部を和文の句読点・同義語として判定させないため、この節だけ無効化する。 -->

- [E24] 厚生労働省. 令和2年転職者実態調査の概況（採用時の問題 84.1%）. 2021-12. グレードA. https://www.mhlw.go.jp/toukei/list/dl/6-18c-r02-gaikyo.pdf
- [E25] 厚生労働省. 令和2年転職者実態調査の概況（問題の内訳）. 2021-12. グレードA. https://www.mhlw.go.jp/toukei/list/6-18c-r02.html
- [E40] 株式会社学情. 20代経験者採用で面接の際に見ているポイント（人事担当者アンケート 421社）. 2023-05. グレードB. https://prtimes.jp/main/html/rd/p/000001051.000013485.html
- [E41] Geekly（ギークリー）. 面接で志望動機を聞かれなかったのはなぜ？. 2024-08-30. グレードC. https://www.geekly.co.jp/column/cat-jobsearch/interview/jobinterview_reasons_for_application/
- [E42] Humanage, Inc.（i-note）. 中途採用で活躍する人材を見極める面接術（再現性）. 2025-05-30. グレードC. https://www.i-note.jp/assessment/tekisei-kensa/articles/028.html
- [E43] PMC（一次は Savickas 2011, APA Career Counseling）. Career construction theory: tools, interventions（CCI）. 2024. グレードA. https://pmc.ncbi.nlm.nih.gov/articles/PMC11026660/
- [E55] Current Directions in Psychological Science. Affective forecasting: Knowing what to want. 2005. グレードA. DOI:10.1111/j.0963-7214.2005.00355.x. https://doi.org/10.1111/j.0963-7214.2005.00355.x

<!-- textlint-enable -->
