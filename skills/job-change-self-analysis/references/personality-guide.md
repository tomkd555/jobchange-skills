# 性格・行動傾向の扱い（personality-guide）

<!-- textlint-disable jtf-style/4.3.2.大かっこ［］ -->
<!-- 本文中の [E1] 形式は出典 ID の記法である。半角大かっこを保つため、このファイルでは当該規則を無効化する。 -->

job-change-self-analysis スキルで、性格・行動傾向を自己申告として集め、行動証拠と他者証言に対応づけて成果物へ載せるときの原本である。`self_analysis.json` の `personality` の記入基準、Step 3.5 の問い（`question-bank.md`）、エージェント2体（writer / auditor）の判断がこのファイルを参照する。内省の限界と反すう防止の根拠は `self-analysis-methods.md` にあり、ここへは複製しない。エビデンスレベルは A〜D の4段階で表記し、学術研究には DOI を記す。

## 位置づけ

性格の自己申告は、行動エピソードと他者証言に次ぐ3つ目の素材である。自己申告は本人の自己像を表すが、特性そのものの証拠ではない（`self-analysis-methods.md` の「内省は単独では信頼できない」）。したがって、自己申告の項目は次の3つの役割に限る。

1. エピソードの想起を促す呼び水。項目へ答えたら、その傾向が表れたエピソードを1つ挙げてもらい、`linked_episode_ids` で対応づける。
2. 自己像と他者証言の一致・不一致を可視化する材料（ジョハリの窓）。不一致はそのまま記録し、都合の良い側へ寄せない。
3. 作業特性の希望（`work_character_preferences`）・志向・面接での自己PRと弱みの説明に、行動に根ざした言葉を与える材料。

自己申告だけで強みを作らない。エピソードにも他者証言にも対応づかない自己申告は、`personality.markers` に残るが `strengths` の根拠にならない。

## 使ってよい道具と使わない道具

性格に関する検査は、公開の可否と利用条件が道具ごとに違う。本スキルが問いとして出してよいのは、公開されていて再配布・改変が許される項目群に限る。

| 道具 | 利用条件 | 本スキルでの扱い |
|---|---|---|
| IPIP（International Personality Item Pool） | パブリックドメイン。複製・編集・翻訳・利用のいずれも許可や料金を要しない[E1] | ビッグファイブ5因子と誠実さ・謙虚さ（HEXACO 由来の IPIP 版）の枠組みと項目の趣旨を使ってよい。項目は本スキルの二者択一の形に書き直して出す |
| HEXACO-PI-R（原版） | 非営利の学術研究に限り無償。それ以外は著者への連絡を要する[E2] | 原版の項目は使わない。誠実さ・謙虚さの枠組みだけを IPIP 版の趣旨で使う |
| Short Grit Scale（Grit-S） | 非営利の研究・教育に限り無償。商用利用・広い公開配布・採用のような利害のある場面での利用は著者の条件で除かれている[E3] | 尺度は使わない。「やり抜く力」という構成概念だけを参照し、本スキルが独自に書いた二者択一の項目で聞く |
| General Self-Efficacy Scale（GSE） | 原版（英語）は研究目的で無償。日本語の標準尺度（一般性セルフ・エフィカシー尺度）は有償の検査である[E4] | 尺度は使わない。「自己効力感」という構成概念だけを参照し、本スキルが独自に書いた項目で聞く |
| O*NET Interest Profiler | CC BY 4.0。出典を示せば翻訳を含む改変も許される[E5] | 本スキルは採点する検査を出さないため、項目は使わない。興味（RIASEC）の枠組みの名称だけを使う |
| O*NET Work Importance Profiler ほかの Career Exploration Tools の内容 | CC BY-ND 4.0。項目をそのまま使うことは許されるが、改変（日本語への書き直しを含む）は別の開発者ライセンスと検証の義務を要する[E5] | 項目を日本語へ書き直して出すことはしない。仕事の価値の枠組みの名称だけを使う |
| VPI 職業興味検査（日本版） | 有償の検査キットであり、JILPT は販売していない[E6] | 使わない。RIASEC は枠組みの名称としてだけ使う |
| 厚生労働省 job tag の自己診断ツール・JILPT キャリア・インサイト・VRT カード・GATB | 公的機関が提供し、利用者が自分で受けられる。ハローワークで受けられるものもある | 本スキルからは出さない。利用者が受けた結果を持ち込んだ場合は、呼び水として扱い、確定した判定にしない |
| Schein のキャリア・アンカー質問票 | 有償の出版物 | 8分類の呼び水としてだけ使う（`question-bank.md`） |
| Career Construction Interview（Savickas） | 論文で公開された面接の枠組みであり、採点する尺度ではない | 5つの設問の趣旨を本スキルの言葉で書いた問いを使う（`question-bank.md` の CCI 型の5問）。原文の設問をそのまま転載しない |
| VIA 性格の強み | 本編の調査票は VIA Institute の知的財産。公開研究版（GACS・SSS）も集団を対象とする研究目的に限られる[E7]。24の強みの名称を転載してよいかは利用規約で確かめていない | 調査票は出さない。24の強みの名称は、強みを言葉にする候補として会話で示すにとどめ、成果物へ一覧として転載しない |
| CliftonStrengths（ギャラップ） | 商標と著作権で保護され、テーマ名と説明の転載が禁じられている[E8] | 出さない。名称も転載しない |
| MBTI・16Personalities | 4文字の型に分類する。下位尺度の再検査信頼性は不均一で、思考―感情の尺度は .61 にとどまる[E9]。16Personalities は採点モデルが公開されておらず、独立した妥当性研究は確認できていない[E10] | 出さない。利用者が「私は INFP です」のように型を名乗った場合は、型を否定も肯定もせず、「その型で言うと、どんな行動が思い当たりますか」と聞いてエピソードへ移る |
| SPI3・玉手箱（性格検査の部分は OPQ）・TAL などの企業側の適性検査 | 採用側の意思決定のための商用検査。項目は非公開。受検者本人に結果は返らない | 出さない。何を測るかの説明にとどめ、対策は `job-change-exam-prep` へ回す |
| ミイダス・グッドポイント診断・doda キャリアタイプ診断・エン転職の診断 | 各社が自社データで作った無償の診断。独立の妥当性検証は公開されていない | 出さない。項目も転載しない。強みの呼び名の候補として、公開されている18の呼び名（グッドポイント診断）を語彙表に載せる |
| ダークトライアド（SD3 など） | 研究用の尺度は公開されている | 出さない。他者のリスク判定のための尺度であり、自己分析に建設的な用途が無く、自己ラベルとして有害になりうる |

## 構成概念の語彙

`personality.markers[].construct` に使える識別子は次の表に限る。`validate_self_analysis.py` はこの表と同じ語彙を持ち、表に無い識別子を ERROR とする。表の第1列（バックティック囲み）が識別子である。

| 識別子 | 名称 | 由来 | 何を見るか |
|---|---|---|---|
| `conscientiousness` | 誠実性 | ビッグファイブ（IPIP） | 計画・段取り・やり切りの傾向 |
| `emotional_stability` | 情緒安定性 | ビッグファイブ（IPIP） | 負荷のかかる場面での平静さと回復 |
| `extraversion` | 外向性 | ビッグファイブ（IPIP） | 人と関わる場面でのエネルギーの向き |
| `agreeableness` | 協調性 | ビッグファイブ（IPIP） | 対立の場面での折り合いのつけ方 |
| `openness` | 開放性 | ビッグファイブ（IPIP） | 未知の方法・領域への向かい方 |
| `honesty_humility` | 誠実さ・謙虚さ | HEXACO（IPIP 版） | 成果の帰属と率直さ |
| `grit` | やり抜く力 | 構成概念のみ参照（尺度は使わない） | 長期の目標への持続 |
| `self_efficacy` | 自己効力感 | 構成概念のみ参照（尺度は使わない） | 難所を自分の手順で越えられるという見込み |
| `planning_style` | 進め方 | 本スキルの枠組み | 計画先行か、即応しながらの調整か |
| `collaboration_style` | 協働の型 | 本スキルの枠組み | 単独で集中するか、対話で進めるか |
| `change_orientation` | 変化への向き | 本スキルの枠組み | 安定した環境か、変化の多い環境か |
| `decision_style` | 判断の型 | 本スキルの枠組み | 数字と計測を先に置くか、仮説と直感を先に置くか |
| `feedback_timing` | 評価を受ける間隔 | 本スキルの枠組み | 短い間隔で結果を知りたいか、節目でまとめて知りたいか |
| `stress_trigger` | 負荷の要因 | 本スキルの枠組み | 曖昧さ・締切・対人摩擦・単調のどれが最も消耗させるか |
| `recovery_style` | 回復の型 | 本スキルの枠組み | 一人で整えるか、人と話して整えるか |

ビッグファイブ5因子と誠実さ・謙虚さは、職務遂行との関連が最も繰り返し確かめられた枠組みである[E11][E12]。本スキルの枠組みの7項目は、作業特性の希望（hub の `screening-axes.md`）と適合性評価の文化適合に接続するために置く。15項目すべての項目文は本スキルが書いたものであり、他の検査の項目を転載していない。ビッグファイブの項目も IPIP の項目の翻訳ではなく、因子の趣旨に沿って場面と行動で書き直したものである。

## 聞き方

自己申告は、行動に根ざした二者択一で聞く。望ましさが釣り合う2つの行動を並べ、どちらが自分に近いかを選ばせる。単一の文に「当てはまる／当てはまらない」で答える形式より、望ましい側へ寄せる歪みが小さい[E13][E14]。AskUserQuestion の選択式（最大4択）はこの形式に向く。

守ること。

- 2つの選択肢はどちらも「強みとして働く場面がある」書き方にする。「計画的」対「場当たり的」のように、一方が明らかに望ましい対は作らない。
- 形容詞（誠実・怠惰・無責任）ではなく、場面と行動で書く。「締切が迫ったとき、まず残りの作業を書き出す」のように書く。
- 1項目に答えるたびに、その傾向が表れたエピソードを1つ挙げてもらう。既存の `behavioral_episodes` から選ばせ、無ければその場で1件を STAR で聞く。挙がらなければ `linked_episode_ids` を空のままにする。エピソードにも他者証言にも対応づかない項目は WARN になるが、成果物としては成立する。
- 「どちらも同じくらい」「場面による」も選択肢として受ける。無理に一方へ寄せない。
- 1回の Step で出す問いは16問（15の構成概念。`stress_trigger` だけ2問。内訳は `question-bank.md`）までとし、追加の「なぜ」を重ねない（反すう防止）。
- 他者証言（`others_feedback`）に同じ傾向についての記述があれば `feedback_ids` で対応づける。自己申告と他者証言が食い違う場合は、`note` に食い違いをそのまま書く。

確定した文言は `question-bank.md` の Step 3.5 にある。

## 結果の書き方

- 型やタイプの名称で人を分類しない。「〜型です」「〜タイプです」「あなたは内向型です」と書かない。`personality.presentation` に型やタイプの名称が含まれる場合、検証スクリプトが WARN を出す。
- 描写文で書く。「事前に計画を固めてから着手する行動が、ep-1 と ep-2 で繰り返し見られる」のように、過去形・エピソード対応づけで書く。
- 数値・パーセンタイル・5段階の点数を付けない。数値は測定されたように見え、根拠より強く読まれる。
- 一時点の自己像として書く。「現時点でこう自己申告している」であり、確定した特性ではない。
- 誰にでも当てはまる文（「慎重なときもあれば大胆なときもある」）を書かない。その文が別の人のエピソード集へそのまま移せるなら、根拠づけができていない（バーナム効果[E15]）。監査担当はこの観点で検査する。
- 自己申告と他者証言の不一致は、不一致のまま書く。

## 下流への接続

| 接続先 | 使い方 |
|---|---|
| `job_change_axis.work_character_preferences`（hub の profile.json） | `planning_style` は `clear_completion` と、`collaboration_style` は `solo_completable` と、`feedback_timing` は `short_feedback` の希望度と突き合わせる。食い違いがあれば `notes` に書き、どちらが本当かをスキルの側で決めない |
| `job-change-fit-assessment` の `culture_fit`・`work_character_fit` | `change_orientation`・`stress_trigger`・`recovery_style` を、企業研究の働き方・評判の事実と突き合わせる材料にする。自己申告単独で score を上げない |
| `job-change-interview-prep` の自己PR・弱み | `strengths` の根拠（エピソード・他者証言）と `personality.markers` の描写を、弱みの質問への答えの素材にする。弱みは「負荷の要因」と「回復の型」から、改善行動を添えて語れる |
| `job-change-exam-prep` の性格検査 | 性格検査は一貫した正直な回答を勧める（同スキルの `prep-methods.md`）。ここで整理した自己像は、その一貫性を保つための材料であり、検査の回答を作り込むためのものではない |
| 厚生労働省のジョブ・カード | `behavioral_episodes` と `career_narrative` の内容は、ジョブ・カードのキャリア・プランシートの自己理解の欄と重なる。別途ジョブ・カードが要る利用者には、この成果物を流用できる旨を伝える[E16] |

## 限界

- 性格が職務遂行を説明する割合は小さい。54件のメタ分析を統合した研究では、誠実性と総合的な職務遂行の相関は ρ=.19、外向性 .10、協調性 .10、神経症傾向 -.12、開放性 .13 である[E11]。誠実性単独で説明できる分散は4%に満たず、5因子を合わせても数パーセントにとどまる。これらは統計的な補正を経た相関であり、補正の妥当性を疑う立場からは、さらに低く見積もられる[E18]。適合性評価で、性格の適合を経験の近さやスキルの適合より重く扱わない。
- 説明できる割合が小さいにもかかわらず Step 3.5 を置くのは、面接の弱みと自己PR、性格検査での一貫した回答、作業特性の希望との突き合わせに、行動に根ざした言葉が要るためである。この目的に対して15項目は上限であり、利用者が省略を望めば Step 3.5 全体を飛ばしてよい。
- 職種で効き方が変わる。誠実性はどの職種群でも妥当性を持つが、外向性は管理職と営業職で妥当性が高い[E12]。
- 自己申告と他者評価は、誠実性と情緒安定性で食い違いやすい。この2つの構成概念を `strengths` の根拠に使うときは、他者証言の対応づけを強く勧める。
- 興味の適合と職務満足の相関は弱い（ρ=.19。`self-analysis-methods.md` の [E11]）。興味の一致を満足の保証として扱わない。
- 上司との適合は満足・定着と関連するが、職務遂行との関連は弱い[E17]。求人票と企業研究からは判定できないため、面接での確認事項に残す（`job-change-fit-assessment` の `fit-criteria.md`）。

## 出典一覧

<!-- textlint-disable -->
<!-- 書誌形式（発行元. 表題. 年. レベル. URL）で出典を並べる節である。区切りのピリオドと社名の一部を和文の句読点・同義語として判定させないため、この節だけ無効化する。 -->

- [E1] International Personality Item Pool (Oregon Research Institute). IPIP Home — public domain statement. レベルA. https://ipip.ori.org/
- [E2] HEXACO Personality Inventory-Revised (Lee & Ashton). Download terms. レベルA. https://hexaco.org/hexaco-inventory
- [E3] Angela Duckworth. Research — measures and terms of use. レベルA. https://www.angeladuckworth.com/measures （原著: Duckworth, A. L. & Quinn, P. D. Journal of Personality Assessment. 2009. DOI:10.1080/00223890802634290）
- [E4] Schwarzer, R. & Jerusalem, M. Generalized Self-Efficacy scale. In Measures in health psychology: A user's portfolio. 1995. レベルB（著者による公開版の二次配布）. https://www.researchgate.net/publication/311570532_The_general_self-efficacy_scale_GSE
- [E5] O*NET Resource Center. O*NET Career Exploration Tools Content License. レベルA. https://www.onetcenter.org/license_tools.html
- [E6] 労働政策研究・研修機構. VPI 職業興味検査. レベルA. https://www.jil.go.jp/institute/seika/tools/VPI.html
- [E7] VIA Institute on Character. Public Domain Surveys. レベルA. https://www.viacharacter.org/researchers/assessments/noregistration
- [E8] Gallup, Inc. Product Terms of Use. レベルA. https://login.gallup.com/Home/ProductTerms
- [E9] Journal of Best Practices in Health Professions Diversity. Randall, K., Isaacson, M. & Ciro, C. Validity and Reliability of the Myers-Briggs Personality Type Indicator: A Systematic Review and Meta-Analysis. 2017. レベルA. https://gwern.net/doc/psychology/personality/2017-randall.pdf
- [E10] Medical News Today. Myers-Briggs: 16 personality types and their accuracy. レベルC. https://www.medicalnewstoday.com/articles/myers-briggs-16-personality-types
- [E11] Journal of Personality (Wiley). Zell, E. & Lesick, T. L. Big Five Personality Traits and Performance: A Quantitative Synthesis of 50+ Meta-Analyses. 2022. レベルA. DOI:10.1111/jopy.12683. https://doi.org/10.1111/jopy.12683
- [E12] Personnel Psychology (Wiley). Barrick, M. R. & Mount, M. K. The Big Five Personality Dimensions and Job Performance: A Meta-Analysis. 1991. レベルA. DOI:10.1111/j.1744-6570.1991.tb00688.x. https://doi.org/10.1111/j.1744-6570.1991.tb00688.x
- [E13] Frontiers in Psychology. A Meta-Analysis of the Faking Resistance of Forced-Choice Personality Inventories. 2021. レベルA. https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2021.732241/full
- [E14] Frontiers in Psychology. Controlling for Response Biases in Self-Report Scales: Forced-Choice vs. Psychometric Modeling of Likert Items. 2019. レベルA. https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2019.02309/full
- [E15] Current Psychology (Springer). Accepting personality test feedback: A review of the Barnum effect. レベルA. https://link.springer.com/article/10.1007/BF02686623
- [E16] 厚生労働省. ジョブ・カード制度. レベルA. https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/koyou_roudou/jinzaikaihatsu/jobcard_system.html
- [E17] Personnel Psychology (Wiley). Kristof-Brown, A. L., Zimmerman, R. D. & Johnson, E. C. Consequences of Individuals' Fit at Work: A Meta-Analysis. 2005. レベルA. DOI:10.1111/j.1744-6570.2005.00672.x. https://doi.org/10.1111/j.1744-6570.2005.00672.x
- [E18] Journal of Applied Psychology (APA). Sackett, P. R. ほか. Revisiting meta-analytic estimates of validity in personnel selection: Addressing systematic overcorrection for restriction of range. 2022. レベルA. DOI:10.1037/apl0000994. https://doi.org/10.1037/apl0000994

<!-- textlint-enable -->
