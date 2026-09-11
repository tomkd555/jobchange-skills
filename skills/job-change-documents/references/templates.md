# 応募書類テンプレートの選定基準

書類種別ごとに複数のスタイルのテンプレートを `assets/templates/` に置く。本書は、どのテンプレートをどの場面で選ぶか、各テンプレートの構成が何に基づくか、出典で食い違う点をどう決めたかの原本である。作成担当（`job-change-document-writer`）は Step 1 の形式選定でこの表から1つを選び、選んだテンプレートの構成を崩さずに埋める。監査担当（`job-change-document-auditor`）は、書類が選定されたテンプレートの必須項目を備えているかの検査に用いる。

テンプレートは構成の原本であり、記述の基準ではない。定量化・誇張禁止・企業別調整の基準は `shokumu-keirekisho.md`・`rirekisho.md`・`english-resume.md`・`tailoring.md` にある。

## テンプレートの記法

- `{profile.…}` は `profile.json` のフィールドを指す。作成担当はその値だけで埋め、値が無い項目は行ごと省くか「特になし」と書く（どちらにするかは各テンプレートが指定する）。
- `{…}` で `profile.` を伴わないものは、求人票・企業研究・作成日など profile.json 以外から埋める値である。
- `<!-- -->` は作成担当への記入指針であり、成果物には残さない。
- 見出しの文言は出典の表記をそのまま使う。応募先が様式を指定した場合はそれに従い、テンプレートは使わない。
- テンプレートは Markdown で書く。右寄せ・中央寄せ（日付・氏名・「以上」・表題）は Markdown では表せないため、指針に「右寄せ」と書いてある箇所は、Word・PDF などへ書き出すときに整える。Markdown のままでは位置指定を付けない。
- 日付は `profile.json` の `period`（`2022-04〜2024-03`）を「2022年4月から2024年3月まで」のように日本語の日付に書き換えてよい。`achievements[].metric` の文字列は一字一句そのまま転記する。この区別は監査担当も同じ基準で検査する。
- 文体は節ごとに分ける。職務要約・職務経歴・スキルは常体（である）、自己PR・志望動機は採用担当者へ向けた文であるため敬体（です・ます）で書く。1つの書類に常体と敬体が混在するのは、書類の節ごとに文体を分けるこの規則に従う限り欠陥ではない。

## テンプレート一覧

| ファイル | 書類種別 | スタイル | 向く場面 |
|---|---|---|---|
| `shokumu-keirekisho-chronological.md` | 職務経歴書 | 編年体式 | 同業界・同職種で一貫し、成長の過程を示したい |
| `shokumu-keirekisho-reverse.md` | 職務経歴書 | 逆編年体式 | 直近の職務が応募職に近い |
| `shokumu-keirekisho-career.md` | 職務経歴書 | キャリア式 | 転職回数が多い、分野をまたぐ経験を分野別に示したい |
| `shokumu-keirekisho-engineer.md` | 職務経歴書 | ITエンジニア式 | 技術職。テクニカルスキル節とプロジェクト単位の経歴が要る |
| `rirekisho-mhlw.md` | 履歴書 | 厚労省様式例 | 応募先の様式指定が無い場合の既定 |
| `rirekisho-conventional.md` | 履歴書 | 従来様式（旧 JIS 相当） | 応募先が配偶者・扶養家族・通勤時間欄のある様式を指定した |
| `english-resume-reverse-chronological.md` | 英文レジュメ | Reverse-chronological | 既定。同分野での転職 |
| `english-resume-combination.md` | 英文レジュメ | Combination | 業界・職種を変える転職。スキルを先に見せたい |
| `english-resume-functional.md` | 英文レジュメ | Functional | 職歴の空白や非連続が大きい。ATS には弱い |
| `motivation-rirekisho-field.md` | 志望動機 | 履歴書の志望動機欄 | 履歴書・職務経歴書の欄に書く 200〜300字 |
| `motivation-letter.md` | 志望動機 | 志望動機書（A4 1枚） | 応募先が志望動機書の提出を求めた |
| `self-pr.md` | 自己PR | 結論→証明→貢献 | 職務経歴書・履歴書の自己PR欄 |

## 職務経歴書

### 全スタイルに共通する骨格

調査した15出典（下記）の全部で、職務経歴書は次の5つを持つ。3形式の違いは「職務経歴」の内部の並べ方と単位だけで、節の構成は同じである（出典 S3・S4 は編年体式と逆編年体式に同一の節構成を示す）。

| 順 | 見出し | 必須 | 出典 |
|---|---|---|---|
| 1 | 表題「職務経歴書」、右寄せの日付と氏名 | 必須 | S2, S3, S6, S8 |
| 2 | 職務要約 | 必須 | 全出典 |
| 3 | 職務経歴 | 必須 | 全出典 |
| 4 | 活かせる経験・知識・スキル | 推奨 | S2, S3, S6, S8, S9, S13 |
| 5 | 資格・免許 | 必須（無ければ「特になし」） | S1, S2, S3, S8, S10 |
| 6 | 自己PR | 必須 | S1〜S4, S6〜S10, S12〜S14 |
| 7 | 志望動機・転職理由 | 任意 | S9, S10, S12 はいずれも「必須ではない」 |

職務経歴の会社概要は、会社名（正式名称）・事業内容・資本金・従業員数の4項目を核とし、売上高・設立年・上場区分を任意とする（S3, S8, S9, S10, S12, S13, S14）。`profile.json` には会社名と期間しか無いため、事業内容・資本金・従業員数は `company_research.json` の claim から埋めるか、無ければ行ごと省く。創作しない。

### 分量

| 項目 | 採用した基準 | 出典と食い違い |
|---|---|---|
| 総ページ数 | 社会人経験7年程度まで A4 1〜2枚、それ以上 2〜3枚 | S8。他は 1〜2枚（S1, S2）と 2〜3枚（S3, S6, S10）で割れる。S7 は制約自体を退ける。経験年数で場合を分ける唯一の出典を採用する |
| 職務要約 | 200〜300字（3〜5行） | 字数派 S2（250字前後）・S8（200〜300字）と行数派 S1（2〜5行）・S3（3〜4行）・S9（3〜5行）・S10（5行以内）。両方の範囲に収まる値 |
| 自己PR | 200〜400字 | S8。S1 は箇条書き3点か文章5行以内、S10 は300字前後。単独の自己PR（`self-pr.md`）は M7 に従い300字程度・最長400字とし、どちらの範囲にも入る300字前後を目安にする |

### 3形式の並べ方

| 形式 | 職務経歴の並べ方 | 補足 |
|---|---|---|
| 編年体式 | 古い順。会社ごとに1ブロック | S1（リクルートエージェント）は指定が無い場合の既定とする |
| 逆編年体式 | 新しい順。会社ごとに1ブロック | S8（リクナビNEXT）は「最も一般的」とする。S4 だけが「直近以外は概要のみ」とするが他に無いため任意の圧縮として扱う |
| キャリア式 | 分野（またはプロジェクト）ごとに1ブロック。冒頭に時系列の職歴を簡潔に置く | 冒頭の時系列一覧は S5 だけが指示するが、時系列が読めなくなる欠点を補うため採用する |

既定の選び方: 指定が無ければ編年体式と逆編年体式のどちらが標準かで出典が割れる（S1 vs S8）。本スキルは、直近の職務が応募職に近いなら逆編年体式、そうでなければ編年体式とする。転職回数が多い、または分野をまたぐならキャリア式とする。

### 職種による派生

- **ITエンジニア**: テクニカルスキル（環境・使用言語）の節が独立して増える（S7, S11, S12）。職務経歴はプロジェクト単位で書く（期間・案件・体制と役割・担当・成果・使用技術。S12, S15）。独立テンプレートとする。
- **営業**: 節は増えない。職務経歴の実績を年度ごとに「売上・目標達成率・社内順位」の絶対値と相対値で書く（S13）。編年体式・逆編年体式テンプレートの実績欄の指針として扱う。
- **管理職**: 節は増えない。「マネジメント経験欄」という独立の節は存在しない（S6）。会社ブロックに所属部門・役職・部下人数を加え、実績は人数だけでなく組織課題への取り組みで示す（S6, S14）。予算規模を求める出典は無い。

## 履歴書

### 2様式の使い分け

- **厚労省様式例**（2021年4月16日公開）を既定とする。日本規格協会が2020年7月に JIS 規格の解説から履歴書の様式例を削除し、厚生労働省がこれに代わる様式例を作成した（R3, R4, R5 一次・公式）。
- **従来様式**は、応募先が配偶者・扶養家族・通勤時間欄のある様式を指定した場合だけ使う（R29）。

### 厚労省様式例の項目

| 順 | 項目 | 扱い |
|---|---|---|
| 1 | 「　年　月　日現在」 | 提出日（郵送は投函日）。西暦・和暦は書類全体で統一（R9, R14, R21） |
| 2 | ふりがな・氏名 | 「ふりがな」表記ならひらがな、「フリガナ」ならカタカナ（R14） |
| 3 | 生年月日（満　歳） | |
| 4 | 性別 | 任意記載欄。空欄でよい。男・女の選択にしない（R24, R26, R28。厚労省は「性別の回答を強要することのないよう配慮」と述べる） |
| 5 | 写真 | 任意（R25）。貼る場合は縦4cm×横3cm、3か月以内の撮影（R9, R13, R14, R21） |
| 6 | ふりがな・現住所（〒）・電話・E-mail | 都道府県から省略しない（R14） |
| 7 | 連絡先 | 現住所と異なる場合のみ（R14） |
| 8 | 学歴・職歴（各別にまとめて書く） | 下記の記入規則 |
| 9 | 免許・資格 | 取得年月と正式名称 |
| 10 | 志望の動機、特技、好きな学科、アピールポイントなど | 200〜300字。`motivation-rirekisho-field.md` |
| 11 | 本人希望記入欄 | 希望が無ければ「貴社規定に従います」（R17, R21, R22）。「特になし」・空欄・待遇の具体額は書かない（R17, R22） |

厚労省様式例に無い項目（通勤時間・扶養家族数・配偶者・配偶者の扶養義務）は設けない。厚生労働省は、様式例に無い項目を設ける場合は公正な採用選考の観点で不適切にならないよう留意せよと述べている（R3）。

### 学歴・職歴の記入規則

| 規則 | 採用した書き方 | 出典と食い違い |
|---|---|---|
| 学歴の起点 | 最終学歴が高校卒業以上なら「○○高等学校 卒業」から | R13, R21。R9 は高卒者を高校入学からとし、R15 は大学院修了者に大学入学も許す。多数派を採用する |
| 職歴の順 | 古い順。社名は正式名称 | R13 |
| 退職の理由 | 「一身上の都合により退職」／「会社都合により退職」 | R15, R21 |
| 在職中 | 「現在に至る」。退職日が確定なら「現在に至る（○年○月○日退職予定）」 | R15。R13, R21 は「在職中」も可とするが、統一のため「現在に至る」に固定する |
| 末尾 | 次の行に右寄せで「以上」 | R9, R15, R21 |
| 職歴の空白 | 履歴書には書かない。職務経歴書の職務要約か自己PRで `profile.career_gaps` の説明を使う | 本スキルの整理 |

## 英文レジュメ

### 3スタイルの使い分け

| スタイル | 向く場面 | 出典 |
|---|---|---|
| Reverse-chronological | 既定。同分野で経歴が連続している | E8（Indeed）、E13（Michael Page Japan）、E15（Japan Dev） |
| Combination | 業界・職種を変える。スキルと実績を先に見せ、職歴は新しい順で残す | E9（Indeed）、E5（JMU） |
| Functional | 職歴の空白・非連続が大きく、職歴より能力で読ませたい | E7（Indeed）、E5（JMU）。見出しが分野名になるため ATS の標準見出し規則（E12）と相性が悪い |

### 節の構成

| 順 | 見出し | 必須 | 出典 |
|---|---|---|---|
| 1 | 氏名・連絡先（本文中に置く。ヘッダー/フッターに置かない） | 必須 | E4, E8, E12 |
| 2 | Summary | 必須 | E10, E13, E15 |
| 3 | Objective | 任意 | E10 |
| 4 | Work Experience（Combination では Skills / Key Achievements を先に置く。Functional では分野別の節に置き換え、末尾に Employment History の一覧を置く） | 必須 | E8, E9, E13 |
| 5 | Education | 必須 | E8, E14, E15 |
| 6 | Skills（資格はこの節の1行として書く） | 必須 | E12, E15 |
| 7 | Languages | 必須 | E15 |
| 8 | Additional Information | 任意 | エンワールド（`english-resume.md`） |

### 決めた点

- **Summary を必須、Objective を任意とする。** 既存の `english-resume.md` はエンワールドに従い OBJECTIVE を構成に含めるが、E15 は「Objective と呼ぶのは誤り」とし、E13 は Professional Summary/Career Profile のみ、E10 は Objective を経験の少ない人向けとする。本スキルの利用者は中途であるため Summary を採用する。
- **Education は Experience の後。** 中途向けの E8, E14, E15 は Experience を先に置く。学生向けの E2, E4 は Education 先行だが対象が違う。
- **Languages 節を必須とする。** 日本の外資系向けでは、E15 がこの節を必須とし、話す・読み書きを分けて書くよう指示する。JLPT の記載は任意とする。
- **在留資格は Summary に1行で書く。** E15 の指示。詳しい書式を示す出典は取得できなかったため1行に留める。
- **時制**: 現職は現在形、過去の職は過去形（E4）。E14 は書類全体で統一すればどちらでもよいとするが、E4 の方が明確である。
- **箇条書きの数**: 直近の職は3〜5、それ以前は3（E4 は3〜4、E8 は直近5・以前3。両方に収まる範囲）。1点は1〜2行。
- **分量**: 1枚。経験10年超なら2枚（E8）。E14 は最大 A4 3枚とするが、E2, E4, E5 は2枚を上限とする。
- **ATS 書式**: 1段組、表・テキストボックス・画像・スキルバーを使わない、氏名と連絡先をヘッダー/フッターに置かない、標準の見出し名（Work Experience / Education / Skills）、10〜12pt の標準フォント、テキストベースの PDF か .docx（E2, E11, E12, E15）。
- **記載しない個人情報**: 写真・年齢・生年月日・性別・婚姻状況（E1, E4, E15）。E14 は生年月日を書かせるが、他の全出典と矛盾するため採用しない。

## 志望動機・自己PR

### 3種類と分量

| 種類 | 構成 | 分量 | 出典 |
|---|---|---|---|
| 履歴書・職務経歴書の志望動機欄 | 書き出し（結論）→ 根拠となるエピソード → 締めくくり（入社後の貢献） | 200〜300字。書き出し約100字、中間60〜100字、締め60〜100字 | M1（リクルートエージェント）、M2（マイナビ転職）。字数配分は M2 |
| 志望動機書（A4 1枚） | 日付・表題「志望動機書」・氏名 → 導入 → 業界 → 企業 → 職種 → 貢献できること | 800〜1,000字。用紙の8割を埋める。段落ごとの配分（導入約100字、業界150〜200字、企業・職種・貢献は各約200字）は出典に無く、本スキルの整理である | M12, M13。M18 は800字程度 |
| 自己PR | 結論（強み）→ 証明（行動と結果）→ 貢献 | 300字程度、最長400字。強みは1つ、多くて3つ | M7（JAC）。M9 は600字まで許すが M7 の上限に合わせる |

### 決めた点

- **志望動機書に頭語・結語（拝啓・敬具）と時候の挨拶を付けない。** M11 だけが付けるとし、M12, M13, M14 は付けないとする。添え状と役割が重なるためでもある。
- **志望動機書のヘッダーは日付・表題・氏名とし、宛名は付けない。** M12, M13 に従う。M14 は宛名を付け、M18 は宛名を左上に置くが、多数派を採用する。
- **書き出しは企業に向けた結論にする。** M1 の「貴社を志望する理由は◯◯だからです」型。M2 の「私は○○に携わりたい」型は自分に向いた文になるため採用しない。
- **職務経歴書の志望動機欄の字数は定めない。** 取得できた出典に数値が無い。履歴書欄と同じ構成で、200〜300字を目安にする。
- **自己PRの構成に PREP・STAR の名前を使わない。** 中途向けの M3, M7, M9 はいずれも名前を使わず、名前を使う M20 は新卒向けである。構成は同じ（結論→証明→貢献）であり、名前だけ落とす。
- **書かないこと**: 待遇・勤務条件を主な理由にすること、前職への不満、他社にも通じる社風賛美、「学ばせていただく」型の受け身、「頑張ります」だけの意欲（M1, M2, M6, M11, M14）。

## 出典

エビデンスレベルの定義は `{HUB_SKILL_DIR}/references/evidence-grading.md` にある。人材紹介会社・転職サイトの実務解説は B（信頼できる二次）、個人運営メディアは C とした。厚生労働省の PDF・Excel は本文を機械抽出できなかったため、項目一覧は公式の HTML ページと複数の二次出典の一致で組んだ。doda・レバテック・Robert Walters は取得に失敗し、出典に含めていない。

### 職務経歴書（S）

| id | 発信者 | タイトル | URL | レベル |
|---|---|---|---|---|
| S1 | リクルートエージェント | 職務経歴書の書き方まとめ | https://www.r-agent.com/guide/resume/ | B |
| S2 | マイナビ転職 | 職務経歴書（職歴書）の書き方マニュアル完全版・例文集 | https://tenshoku.mynavi.jp/knowhow/sample/ | B |
| S3 | マイナビ転職エージェント | 「編年体式」「逆編年体式」の職務経歴書の書き方やポイントを紹介！ | https://mynavi-agent.jp/knowledge/prepare/683.html | B |
| S4 | エン転職 | 「編年体式」「逆編年体式」の職務経歴書の書き方 | https://employment.en-japan.com/tenshoku-daijiten/9217/ | B |
| S5 | エン転職 | キャリア式の職務経歴書の書き方 | https://employment.en-japan.com/tenshoku-daijiten/8248/ | B |
| S6 | JAC Recruitment | 職務経歴書の書き方 完全ガイド | https://www.jac-recruitment.jp/market/knowhow/resume/ | B |
| S7 | type転職エージェント | 【職務経歴書の書き方】簡単に作れるテンプレート・フォーマット付き | https://type.career-agent.jp/knowhow/documents/keirekisho/ | B |
| S8 | リクナビNEXT | 職務経歴書の書き方完全ガイド | https://next.rikunabi.com/tenshokuknowhow/shokurekisho/ | B |
| S9 | リクルートダイレクトスカウト | 職務経歴書の書き方と職種別の書き方見本 | https://directscout.recruit.co.jp/contents/article/28759/ | B |
| S10 | LHH転職エージェント | 職務経歴書の書き方・職種別サンプルダウンロード | https://www.lhh.com/ja-jp/insights/career-credentials | B |
| S11 | Green | プロフィールテンプレートの確認 | https://www.green-japan.com/guide/profile/templates | B |
| S12 | マイナビクリエイター | 職務経歴書の書き方 | https://mynavi-creator.jp/knowhow/article/resume-free-download | B |
| S13 | 日経転職版 | 法人営業の職務経歴書テンプレート | https://career.nikkei.com/knowhow/shokureki/000273/ | B |
| S14 | ジャスネットキャリア | 一般事業会社の管理職の職務経歴書の書き方とサンプル | https://career.jusnet.co.jp/resume/sample/cv_company_management/ | B |
| S15 | きっかけエージェント | ITエンジニア転職用｜履歴書・職務経歴書のテンプレートと書き方 | https://kikkakeagent.co.jp/column/guide/898 | B |

### 履歴書（R）

| id | 発信者 | タイトル | URL | レベル |
|---|---|---|---|---|
| R1 | 厚生労働省 ハローワークインターネットサービス | 履歴書・職務経歴書の書き方 | https://www.hellowork.mhlw.go.jp/member/career_doc01.html | A |
| R3 | 熊本労働局 | 厚生労働省履歴書様式例の作成について | https://jsite.mhlw.go.jp/kumamoto-roudoukyoku/newpage_00155.html | A |
| R4 | 石川労働局 | 履歴書様式例 | https://jsite.mhlw.go.jp/ishikawa-roudoukyoku/roudoukyoku/annai02/syokugyou_antei/job/rirekisyo_youshikirei.html | A |
| R5 | 栃木労働局 | 履歴書様式例（厚生労働省） | https://jsite.mhlw.go.jp/tochigi-roudoukyoku/newpage_01671.html | A |
| R9 | リクナビNEXT | 履歴書の書き方完全ガイド | https://next.rikunabi.com/tenshokuknowhow/rirekisho/ | B |
| R10 | リクナビNEXT | 転職活動の志望動機の文字数の目安は？ | https://next.rikunabi.com/tenshokuknowhow/rirekisho/douki/other01/ | B |
| R13 | マイナビ転職 | 履歴書の書き方【簡単作成】見本・記入例あり | https://tenshoku.mynavi.jp/knowhow/rirekisho/ | B |
| R14 | マイナビ転職 | 履歴書 基本情報欄の書き方 | https://tenshoku.mynavi.jp/knowhow/rirekisho/01/ | B |
| R15 | マイナビ転職 | 履歴書 学歴・職歴欄の書き方 | https://tenshoku.mynavi.jp/knowhow/rirekisho/02/ | B |
| R17 | マイナビ転職 | 【履歴書】本人希望記入欄の書き方と例文 | https://tenshoku.mynavi.jp/knowhow/rirekisho/05/ | B |
| R18 | マイナビ転職 | 【履歴書】配偶者・扶養家族とは？ | https://tenshoku.mynavi.jp/knowhow/rirekisho/09/ | B |
| R21 | タウンワークマガジン | 履歴書の書き方～転職編の基本ガイド | https://townwork.net/magazine/knowhow/resume/t_resume/ | B |
| R22 | エン転職 | 【本人希望記入欄】の書き方 | https://employment.en-japan.com/resume_guide/14204/ | B |
| R24 | laborblog.work | 履歴書のJIS規格様式は廃止、厚労省様式の性別欄は任意記載に | https://laborblog.work/resume/ | C |
| R25 | 日本法令 | 履歴書（厚生労働省履歴書様式例準拠） | https://www.horei.co.jp/iec/products/view/3155.html | B |
| R26 | keireki.net | 厚生労働省推奨の履歴書とは？JIS規格との違い | https://keireki.net/rkkksrds/ | C |
| R28 | Wikipedia 日本語版 | 履歴書 | https://ja.wikipedia.org/wiki/履歴書 | C |
| R29 | 履歴書Do | 履歴書の扶養家族と配偶者欄の書き方 | https://www.rirekisyodo.com/papers/rirekisho-dependent.html | C |

### 英文レジュメ（E）

| id | 発信者 | タイトル | URL | レベル |
|---|---|---|---|---|
| E1 | Harvard FAS Mignone Center for Career Success | Harvard College Guide to Creating a Strong Resume | https://careerservices.fas.harvard.edu/resources/create-a-strong-resume/ | B |
| E2 | MIT CAPD | Career toolkit: Crafting an effective resume | https://capd.mit.edu/resources/career-toolkit-crafting-an-effective-resume/ | B |
| E4 | Yale Office of Career Strategy | Resume Formatting and Common Errors | https://ocs.yale.edu/resources/resume-formatting/ | B |
| E5 | James Madison University Career Center | Choosing a Résumé Format | https://www.jmu.edu/career/students/career-prep/resumes/format.shtml | B |
| E7 | Indeed | Chronological vs Functional Resumes | https://www.indeed.com/career-advice/resumes-cover-letters/chronological-vs-functional-resume | B |
| E8 | Indeed | How to Write a Chronological Resume | https://www.indeed.com/career-advice/resumes-cover-letters/chronological-resume-tips-and-examples | B |
| E9 | Indeed | Combination Resume Tips and Examples | https://www.indeed.com/career-advice/resumes-cover-letters/combination-resume-tips-and-examples | B |
| E10 | Indeed | Resume Summary vs. Resume Objective | https://www.indeed.com/career-advice/resumes-cover-letters/resume-summary-vs-objective | B |
| E11 | Jobscan | Anatomy of an ATS Friendly Resume Format | https://www.jobscan.co/blog/20-ats-friendly-resume-templates/ | B |
| E12 | Jobscan | 5 Critical ATS Resume Formatting Mistakes to Avoid | https://www.jobscan.co/blog/ats-formatting-mistakes/ | B |
| E13 | Michael Page Japan | 3 impactful resume templates | https://www.michaelpage.co.jp/en/advice/career-advice/resume-and-cover-letter/resume-templates-writing | B |
| E14 | Daijob | CV | https://www.daijob.com/en/guide/tipsadvice/resume/cv/ | B |
| E15 | Japan Dev | How to write a perfect developer resume in Japan | https://japan-dev.com/blog/developer-english-resume-japan | B |

### 志望動機・自己PR（M）

| id | 発信者 | タイトル | URL | レベル |
|---|---|---|---|---|
| M1 | リクルートエージェント | 志望動機の書き方と例文54種 | https://www.r-agent.com/guide/motive/1672/ | B |
| M2 | マイナビ転職 | 履歴書の志望動機は「書き出し」と「締めくくり」で差を付ける！ | https://tenshoku.mynavi.jp/knowhow/shibodoki/01/ | B |
| M3 | マイナビ転職 | 自己PR例文・書き方・テンプレ | https://tenshoku.mynavi.jp/knowhow/pr_sample/ | B |
| M6 | type | 「魅力が伝わる」志望動機の書き方 | https://type.jp/tensyoku-knowhow/technique/reason/ | B |
| M7 | JAC Recruitment | 職務経歴書の自己PRの書き方 | https://www.jac-recruitment.jp/market/knowhow/resume/selfpr/ | B |
| M9 | エン転職 | 職務経歴書の自己PRの書き方 | https://employment.en-japan.com/tenshoku-daijiten/10181/ | B |
| M11 | ハタラクティブ＋ | 志望動機書の書き方とは？ | https://hataractive-plus.jp/article/resume/106/ | B |
| M12 | 40代 転職の極意 | 志望動機書のテンプレート | https://xn--u9j177ljjfdzyj6p.jp/siboudoukisyo/ | C |
| M13 | 転職エージェント総合ガイド | 志望動機書の書き方 | https://agent-guide.com/中谷充宏/志望動機書/ | C |
| M14 | ミライトーチResume | 志望動機書とは？書き方を解説 | https://miraitorch-career.com/service/motivation-letter/ | C |
| M18 | doda | 志望動機・志望理由の書き方 | https://doda.jp/guide/rireki/douki/ | B（検索結果の要約のみ。本文は取得できなかった） |
| M20 | PORTキャリア | 自己PRの構成作成ガイド｜PREP・STAR法 | https://www.theport.jp/portcareer/article/60948/ | C（新卒向け） |

## この基準の適用範囲と限界

- 出典はすべて2026年8月時点の Web ページである。厚生労働省の様式例そのものは本文を抽出できず、項目一覧は公式 HTML と二次出典の一致に基づく。
- 職務経歴書の分量と職務要約の長さは出典ごとに幅があり、本書の値は複数出典の範囲に収まる値を選んだものである。単一の正解ではない。
- 添え状（送付状）と英文カバーレターは本スキルの書類種別に含まれないため、テンプレートを置いていない。
