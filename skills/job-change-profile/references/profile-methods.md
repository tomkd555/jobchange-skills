# プロファイル設計の方法論（根拠と限界）

job-change-profile スキルの設計判断の根拠と限界を定める原本である。SKILL.md の原則・エージェント2体（writer / auditor）の監査観点がこのファイルを参照する。証拠グレードは A〜D の4段階（A=査読済みの学術研究・一次公式、B=信頼できる二次、C=口コミ・集計・HRブログ、D=個人ブログ・伝聞）で表記し、学術研究には DOI を記す。

## 採用側が書類選考で見る情報

採用側が中途採用の書類選考で評価する中核は、職務経歴・実績・スキルの内容と、それが求人要件へどう対応するかという点（relevance）である。加えて書類の提示品質（可読性・誤字の少なさ）が通過を左右する（確度: 可能性が非常に高い、80%以上90%未満）。

- 日本の採用担当者調査では、職務経歴・職務内容が最重視項目とされる（doda 調査で43.4%）[E1]。ただし IT 職に限れば「スキル・使用可能ツール」が最重視（48.4%）で、最重視項目は職種に依存する[E2]。**この2つの数値はそれぞれ単一の調査に由来する。**
- 学術的には、person-job／person-organization 適合が入社前アウトカム（採用意図・内定）と広く関連する（172研究のメタ分析）[E13]。履歴書の属性がどう読み取られるかは対象職務に依存する[E12]。アイトラッキングでは Experience セクションの注視が通過判定を予測した[E15]。

設計への含意: profile.json は、職務単位で経歴・成果・定量値を保持し、応募先ごとの関連性を応募書類サブスキルが再構成できる粒度を持つ。関連性そのものは応募先ごとに変わるため profile.json には固定して保持しない（古い対応づけが残るのを避ける）。

**確信度を下げる証拠（限界）**: 経歴の「量」自体は成果をほとんど予測しない。入社前職務経験の量・期間・種類と職務遂行の補正相関は .06 にとどまる[E14]。経歴を厚く書くこと自体は評価を保証しない。

## スキル分類

「技術/業務/語学/資格」という粗い区分は実務に存在するが、公的分類は専門スキルと転用可能スキルを分離し、転用可能性を文脈に依存する連続的な度合いとして扱う。汎用分類の一律適用はそれ単独では機能しない（確度: 可能性が非常に高い、80%以上90%未満）。

- O*NET はスキルを基礎スキルと転用可能スキル（cross-functional）に分け、各項目に操作的定義を付す[E40]。
- 厚生労働省はポータブルスキルを「業種・職種が変わっても持ち運びできる職務遂行上のスキル」と公的に定義し、仕事のし方（対課題）5要素と人との関わり方（対人）4要素の計9要素で構成する[E44]。
- ESCO はスキルの再利用性を transversal・cross-sectoral・sector-specific・occupation-specific の4段階で分類し、抽象的な横断スキルは職業文脈で具体化されて初めて使えると明文化する（スキル文脈化）[E47]。

設計への含意: profile.json は technical / business / languages / certifications を入口としつつ、ポータブルスキル9要素（対課題・対人）を補助分類（`skills.portable`）として持ち、専門スキルと転用可能スキルを分けて棚卸しできる構造にする。要件との対応づけは応募時に応募書類サブスキルが行う。

**確信度を下げる証拠（限界）**: 転用可能性は固定属性でなく文脈依存かつ動的で、汎用モデルより職務特化モデルが推奨される[E53]。スキル分類枠が棚卸し・転職成功を予測する定量的因果証拠は特定できていない（エビデンスギャップ）。

## must/want の根拠と限界

must/want の分離は要件工学の MoSCoW と同じ構造を持つ実務標準だが、分離しただけでは意思決定は改善しない。MUST は少数に絞りつつ、再評価を前提とするのが妥当である（確度: 可能性が高い、65%以上80%未満）。

- 日本の大手エージェントは希望条件を MUST/WANT に二分し優先順位を付けることを転職の軸の作り方として提示し[E54]、軸を3つ程度に絞ることを理想とする[E55]。求職の教科書も must-have は少数に絞るとする[E56]。要件工学の MoSCoW（Must/Should/Could/Won't）は同じ構造を持つ[E60]。

設計への含意: `job_change_axis` では、譲れない条件と望ましい条件の分離を維持しつつ、必須条件を3件程度までに絞り、`priority_note` に優先順位と再評価時期を残す。恣意的な MUST 偏重と軸の固定化を抑える。

**確信度を下げる証拠（限界）**: MoSCoW は各要件を相互順位付けする客観的方法論を欠き、どれを MUST とするかは主観に委ねられる[E61]。選択肢を絞ることの利得は、選択過多のメタ分析では平均効果量がほぼゼロであった[E69]。選好は聞き取りの過程で構成され経時変化する[E71][E66]。must/want 分離やマトリクスの効果を検証した グレードA・Bの実証研究は未取得である（エビデンスギャップ）。

## ATS・外資系対応の実像

プロファイルは標準見出しへ対応づけ可能な職務単位データと、英文レジュメ用の項目（性別・年齢・写真を除く）を保持すれば足り、過剰なキーワード最適化は不要である。「ATS が大量に自動却下する」という前提は神話である（確度: 可能性が高い、65%以上80%未満）。

- 主要 ATS は氏名・連絡先・要約・各職の職種名/会社/期間/成果・学歴・スキル一覧を構造化フィールドとして抽出する[E72]。標準見出しへの対応づけが要件である[E73]。
- 英文レジュメでは、日本語の履歴書と職務経歴書を統合し、逆時系列で記載する[E84]。性別・年齢・生年月日・顔写真・給与は記載しない[E85]。成果は Action Verb＋数値＋結果で示す[E86]。

設計への含意: 現行の career_history 単位（職務ごとの企業・期間・役割・成果）が標準見出しへ対応づけ可能である。氏名・年齢・性別・顔写真のフィールドは持たない（英文レジュメで記載しない項目であり、個人情報を最小限に持つ方針とも一致する）。ATS キーワード欄・キーワード最適化欄は設けない。

**確信度を下げる証拠（限界・神話の否定）**: 「75%が ATS に自動却下される」統計は2012年の企業マーケティング由来で裏付けがない[E77]。リクルーター25名調査では92%が自社 ATS は書式・内容で自動却下しないと回答した[E79]。キーワード詰め込みは現代 ATS が検知し減点する。**したがってキーワード最適化欄を設けない判断は、神話の否定に基づく。** ただし構造化整備の効果量はベンダー主張に依存し、対照研究は乏しい[E79]。

## 経歴詐称の帰結

正確性・網羅性・鮮度の管理が失敗様式を防ぐ。経歴詐称の帰結は重大性・業務関連性・時間経過で変わるが、虚偽は実務上高率で発覚し、帰結は限定的でない（確度: 可能性が高い、65%以上80%未満）。

- 日本では経歴詐称を理由とする懲戒解雇が有効となるには「事前発覚なら雇入れなかったといえ、かつ客観的相当性がある」双方の要件を満たす必要がある[E92]。業務に支障がないこと・古い犯罪歴であること・内容が軽微であることなどを理由に無効とされた裁判例もあり、すべての詐称が致命的ではない[E94]。詐称は文書偽造・金銭目的の詐欺・資格詐称で刑事罰の閾値を超える[E101]。詐称は社会保険・源泉徴収・リファレンスチェックの突合で客観的事実から露見する[E102]。
- 米国調査では、虚偽の申告で採用された人の41%が内定取消・18%が解雇で、何の帰結もなかった人は29%にとどまる[E97]。

設計への含意: profile.json は、聞き取りメモにある事実だけから起草する。実績値・期間・役職を推測で補完しない（SKILL.md 原則6）。空白期間は隠さず `career_gaps` に記録して説明可能にする。日付・年収・実績値のうち記憶が曖昧なものは証憑での任意の確認を案内する（`elicitation-guide.md`）。

## 争いのある数値（両論併記）

次の2つの数値は、母集団の違いや、対立する調査結果があるため、単独で断定に使わない。

- **書類選考通過率37.3%**[E7]: マイナビは中途採用の書類選考通過率を37.3%とするが、これは転職成功者に限定した値で、独立媒体の一般値（20〜30%）と食い違う。通過率の一般的な代表値としては争いがある。
- **経歴詐称の発覚率81.4%**[E95]: StandOutCV は81.4%が発覚するとする一方、別調査は約79%が未発覚とし、水準に争いがある。発覚率の代表値としては確定できない。

## 調査の限界とエビデンスギャップ（本スキルの前提）

- 定量化そのものの効果を単離した査読フィールド実験は未取得である（`quantification-guide.md` 参照）。
- must/want 分離・意思決定マトリクスの効果を検証した A/B級実証は未取得である。
- 日本の中途採用でグレードA（厚労省調査）による重視項目の一次数値は本文を取得できておらず、doda・Geekly のグレードB/C 調査（単一ソース）に依拠している。
- 空白期間が選考結果に与える影響の効果量の本文値は未取得である（`elicitation-guide.md` 参照）。

これらのギャップから、本スキルの設計は「証拠が強い骨子（構造化聞き取り・証憑での自己確認・失敗様式の回避・スキルの層分離）」を確定的に、「効果量が小さい論点（定量化の単離効果・must/want の意思決定改善）」を留保付きで扱う。

## 出典一覧

- [E1] doda（パーソルキャリア）. 中途採用の履歴書・職務経歴書で一番見られているのはどこ？. 2024. グレードB（単一ソース）. https://doda.jp/guide/saiyo/007.html
- [E2] Geekly（ギークリー）. 【採用担当150名に聞いた】応募書類で重視するポイントとは？. 2021-12. グレードC（単一ソース・自己報告）. https://www.geekly.co.jp/column/cat-jobsearch/resume_point_byrecruiter/
- [E7] マイナビ（マイナビ転職）. 書類選考とは？通過率は？突破する履歴書・職務経歴書の書き方を解説. 2025. グレードB（disputed）. https://tenshoku.mynavi.jp/knowhow/caripedia/276/
- [E12] Journal of Applied Psychology. Biodata phenomenology: Recruiters' perceptions and use of biographical information in resume screening. 1994. グレードA. DOI:10.1037/0021-9010.79.6.897. https://doi.org/10.1037/0021-9010.79.6.897
- [E13] Personnel Psychology. Consequences of Individuals' Fit at Work: A Meta-Analysis. 2005. グレードA. DOI:10.1111/j.1744-6570.2005.00672.x. https://doi.org/10.1111/j.1744-6570.2005.00672.x
- [E14] Personnel Psychology. A meta-analysis of the criterion-related validity of prehire work experience. 2019. グレードA. DOI:10.1111/peps.12335. https://doi.org/10.1111/peps.12335
- [E15] Machine Learning and Knowledge Extraction (MDPI). Using Machine Learning with Eye-Tracking Data to Predict if a Recruiter Will Approve a Resume. 2023. グレードA. DOI:10.3390/make5030038. https://doi.org/10.3390/make5030038
- [E40] O*NET Resource Center (U.S. Department of Labor). The O*NET Content Model. 2025. グレードA. https://www.onetcenter.org/content.html
- [E44] 厚生労働省. ポータブルスキル見える化ツール（職業能力診断ツール）. 2021. グレードA. https://www.mhlw.go.jp/stf/newpage_23112.html
- [E47] European Commission (ESCO). Skill contextualisation — ESCOpedia. 2025. グレードA. https://esco.ec.europa.eu/en/about-esco/escopedia/escopedia/skill-contextualisation
- [E53] Workitect. The One-Size-Fits-All Competency Model. 2023. グレードC. https://workitect.com/the-one-size-fits-all-competency-model/
- [E54] リクルートエージェント. 転職の軸とは？転職の軸の作り方や譲れない条件一覧. 2023-12-22. グレードC. https://www.r-agent.com/guide/start/21312/
- [E55] JAC Recruitment. 転職先の選び方｜キャリアを実現する業界・企業選びのポイントと具体例. 2024-12-02. グレードC. https://www.jac-recruitment.jp/market/knowhow/preparation/points-to-select/
- [E56] Saylor Academy (open textbook). Personal Decision Criteria When Considering Possible Job Targets. 2020. グレードB. https://saylordotorg.github.io/text_six-steps-to-job-search-success/s07-03-personal-decision-criteria-whe.html
- [E60] ProductPlan. MoSCoW Prioritization | Glossary. 2024. グレードB. https://www.productplan.com/glossary/moscow-prioritization/
- [E61] ProductPlan. MoSCoW Prioritization | Glossary. 2024. グレードB. https://www.productplan.com/glossary/moscow-prioritization/
- [E66] Vero Recruitment. Shifting Priorities. 2024. グレードC. https://verorecruitment.com/blog/shifting-priorities-career-advancement-tips
- [E69] Journal of Consumer Research. Can There Ever Be Too Many Options? A Meta-Analytic Review of Choice Overload. 2010. グレードA. DOI:10.1086/651235. https://doi.org/10.1086/651235
- [E71] American Psychologist. The construction of preference. 1995. グレードA. DOI:10.1037/0003-066x.50.5.364. https://doi.org/10.1037/0003-066x.50.5.364
- [E72] Resume Optimizer Pro. How Resume Parsers Actually Work: Inside Workday, Greenhouse, Lever, iCIMS, Taleo. 2026-04-22. グレードC. https://resumeoptimizerpro.com/blog/how-resume-parsers-actually-work
- [E73] Resume Optimizer Pro. How Resume Parsers Actually Work. 2026-04-22. グレードC. https://resumeoptimizerpro.com/blog/how-resume-parsers-actually-work
- [E77] UnchartedCareer. The '75% of resumes are auto-rejected' myth, traced to its source. 2026-07-04. グレードC. https://unchartedcareer.com/blog/the-75-of-resumes-are-auto-rejected-myth-traced-to-its-source
- [E79] Enhancv. Does the ATS Reject Your Resume? 25 Recruiters Explain What Really Happens. 2025-11-03. グレードC（単一ソース・ベンダー調査）. https://enhancv.com/blog/does-ats-reject-resumes/
- [E84] エンワールド・ジャパン. 英文レジュメの書き方ガイド. 2019-03-18. グレードC. https://www.enworld.com/candidates/career-advices/foreign-job-change/resume/how-to-write-english-resume.html
- [E85] エンワールド・ジャパン. 英文レジュメの書き方ガイド. 2019-03-18. グレードC. https://www.enworld.com/candidates/career-advices/foreign-job-change/resume/how-to-write-english-resume.html
- [E86] エンワールド・ジャパン. 英文レジュメの書き方ガイド. 2019-03-18. グレードC. https://www.enworld.com/candidates/career-advices/foreign-job-change/resume/how-to-write-english-resume.html
- [E92] 咲くやこの花法律事務所. 経歴詐称を理由に懲戒解雇できる？注意点や対応方法を裁判例付きで解説. 2022-12. グレードB. https://kigyobengo.com/media/useful/2984.html
- [E94] 咲くやこの花法律事務所. 経歴詐称を理由に懲戒解雇できる？. 2022-12. グレードB. https://kigyobengo.com/media/useful/2984.html
- [E95] StandOutCV. How many people lie on their resume to get a job? [Study]. 2023-12. グレードB（disputed）. https://standout-cv.com/usa/stats-usa/study-fake-job-references-resume-lies
- [E97] ResumeBuilder.com. 1 in 3 Americans admit to lying on resume. 2021-07-16. グレードB. https://www.resumebuilder.com/1-in-3-americans-admit-to-lying-on-resume/
- [E101] ベンナビ刑事事件（アシロ）. 経歴詐称とは｜成立要件と問われる罪. 2025. グレードC. https://keiji-pro.com/columns/213/
- [E102] ASHIATO（エン・ジャパン）. バックグラウンドチェックで経歴詐称や転職活動はバレない？. 2024-09-19. グレードC. https://ashiatohr.com/news/7ecucee-k
