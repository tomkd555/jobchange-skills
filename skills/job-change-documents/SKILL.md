---
name: job-change-documents
description: >-
  転職の応募書類（職務経歴書・履歴書・英文レジュメ・志望動機書）を、profile.json の実績と求人要件・
  企業研究の結果に基づいて作成するサブスキル。求人要件と実績の対応表（アピールマッピング）を作り、
  書類種別ごとの標準形式で作成し、独立した監査（日本語の文法、誇張・創作の検出、要件との対応、英文レジュメの観点、分量）を通してから納品する。定量値は profile.json の metric と厳密一致させ、記載のない実績を
  創作しない、という原則を保つ。job-change-support（hub）から振り分けられて動く。個々の作成・監査は
  専用エージェント（job-change-document-writer / job-change-document-auditor）が担う。
  Use when the user writes job application documents for a career change in Japan (including
  foreign-affiliated selection) — a shokumu-keirekisho (work-history CV), rirekisho (resume), English
  resume, or statement of motivation — based on their profile and the target company's requirements.
  trigger words: 職務経歴書, 履歴書, 応募書類, 志望動機, レジュメ, 英文レジュメ, 職務要約, 自己PR。
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Agent, AskUserQuestion, Skill
---

# job-change-documents

転職の応募書類を作成するとき、このスキル1つで受付から納品までの手順がそろう。求人要件と利用者の実績を対応づけ、書類種別ごとの標準形式で作成し、作成担当とは独立した監査を通してから納品する。日本の中途採用を中心とし、外資系選考向けの英文レジュメにも対応する。

作成と監査はそれぞれ専用エージェント（`job-change-document-writer`・`job-change-document-auditor`）が担う。本スキルはその起動・差し戻し・納品を統括する。書類種別ごとの記述基準は `references/` で完結する。

## 目的と原則

1. **実績は profile.json の範囲内でのみ書く。** 書類に載せる経歴・実績・数値は、すべて `profile.json` に記載のある範囲に限る。記載のない実績・経歴を創作しない（虚偽記載の禁止）。定量値は `profile.json` の `achievements[].metric` と厳密一致させ、丸め・水増しをしない。規模・範囲・主体を表す言葉（大規模・全社・主導など）は、`profile.json` の記述で裏付けられる範囲を超えて用いない。

2. **求人要件と実績を対応づけてから書く。** 作成の前に、求人要件と `profile.json` の実績を突き合わせたアピールマッピング（要件・対応する実績・裏付け）を作る。訴求点は必ず求人要件に対応づける。要件に対応する実績が profile.json に無い項目は、該当なしとして扱い、創作で埋めない。

3. **作成と監査を分離する。** 作成担当の判断理由を渡さない新規コンテキストで監査担当を起動し、成果物そのものに基づいて検査させる。監査は書類を書き換えず、指摘（findings）だけを返す。反映は作成担当が行う。

4. **企業固有の調整には企業研究の結果を用いる。** 志望動機・企業別カスタマイズは、対象企業の `company_research.json`（理念・求める人物像など）を根拠とする。`company_research.json` が無い場合は企業固有の調整をせず、簡易対応（企業に依存しない汎用の書式・自己PRの骨子まで）である旨を利用者へ明示する。

5. **個人情報を外部へ送信しない。** 利用者の個人情報は、検索クエリ・fetch・外部 API を含む一切の外部送信に用いない。対象の列挙と役割ごとの可否の原本は hub の `{HUB_SKILL_DIR}/references/pii-boundary.md` にある。本スキルの job-change-document-writer と job-change-document-auditor はいずれも Web 送信手段を持たない。このため `profile.json`・`self_analysis.json`・`fit_assessment.json` をそのまま渡してよい。このルールは本スキルおよび下流のすべての手順で保つ。

## 範囲外

- **求人への応募実行・書類の外部送信。** 応募フォームからの送信、転職エージェントへの提出、スカウトへの返信など、利用者に代わって外部へ送信する操作は行わない。書類の作成までを支援し、送信は本人が行う。
- **プロファイルの新規作成。** `profile.json` の作成・検証は hub（`job-change-support`）が担う。本スキルは既存の `profile.json` を入力として用いる。
- **企業研究そのもの。** 企業の理念・事業・評判の調査は `job-change-company-research` が担う。本スキルはその成果物（`company_research.json`）を参照する。

## パスの解決

利用者データの置き場所は設定ファイルだけが決める。既定の置き場所を持たない。本文で `{DATA_ROOT}` と書いた箇所は、次のコマンドが返す `data_root` に読み替える。

hub（job-change-support）から振り分けられた場合は、hub が解決済みの `{DATA_ROOT}` を渡す。単独で起動された場合は、作業のどの段階よりも先に次を実行する。

```bash
python {HUB_SKILL_DIR}/scripts/jc_config.py --show
```

| 終了コード | 状態 | 対応 |
|---|---|---|
| 0 | 設定済み | 出力の `paths` に各データの絶対パスが入る。そのまま作業へ進む |
| 1 | 設定はあるが内容が不正 | 出力の `errors` を利用者へ示し、修復されるまで作業へ進まない |
| 2 | 未設定 | Skill ツールで `job-change-support` を起動して設定を作らせ、`{DATA_ROOT}` を解決してから戻る |

`{SKILL_DIR}` は本スキルの絶対パス、`{HUB_SKILL_DIR}` は同じ配置先にある `job-change-support` の絶対パスを指す。探索順序を含む設定ファイルの仕様は `docs/configuration.md` にある。

## データ配置

利用者データは2か所に分けて置く。非公開ディレクトリ `{DATA_ROOT}/career-private/` には profile.json 等の個人情報を置く。その外側のプロジェクト直下 `{DATA_ROOT}/` には企業別成果物などの非個人情報を置く。本スキルが読み書きするパスは次のとおり。

| パス | 役割 | 入出力 |
|---|---|---|
| `career-private/profile.json` | 利用者プロファイルの原本 | 入力（読むのみ） |
| `career-private/self_analysis.json` | 自己分析の成果物（原本は `job-change-self-analysis`） | 入力（任意。あれば志望動機書・自己PRの入力に加える。無くても進行できる） |
| `career-private/fit/{企業スラッグ}/fit_assessment.json` | 適合性評価の成果物（原本は `job-change-fit-assessment`） | 入力（任意。あればアピールマッピングの訴求点選定に加える。無くても進行できる） |
| `companies/{企業スラッグ}/company_research.json` | 企業研究の構造化データ | 入力（任意。無ければフォールバック） |
| `companies/{企業スラッグ}/documents/` | 作成した応募書類の出力先 | 出力 |
| `companies/{企業スラッグ}/documents/appeal-mapping.md` | アピールマッピング表 | 出力 |
| `companies/{企業スラッグ}/documents/tailoring-rationale.md` | 調整根拠の説明 | 出力 |

- 企業スラッグは hub と同じ規約に従い、`career-private/company_index.json` で解決する（例: 架空クラウドワークス社 → `kakuu-cloudworks`）。
- 企業に依存しない汎用書類（対象企業が未定の場合）は、`documents/` の下に置く。
- 書類ファイルは種別で命名を分ける（例: `shokumu-keirekisho.md`・`rirekisho.md`・`english-resume.md`・`motivation.md`）。
- アピールマッピング表は `documents/appeal-mapping.md`、調整根拠の説明は `documents/tailoring-rationale.md` へ書き出す。いずれも `profile.json` の実績を引くため個人情報を含むが、応募書類そのものと同じ配置先に置く。本スキルの2役割はいずれも Web 送信手段を持たず、`companies/{企業スラッグ}/documents/` を読む役割も本スキルの外には無い。

## 中間成果物

パイプラインの過程で次を作る。いずれも最終納品物へ含める。

| 中間成果物 | 内容 |
|---|---|
| アピールマッピング | 求人要件・対応する実績・裏付けの3列の対応表。作成担当が Step 1 で作り、出力 JSON（`appeal_mapping`）と成果物に載せる。誇張のない訴求の根拠であり、監査担当が求人要件との対応を検査するときに用いる。 |
| 形式選定の記録 | 職務経歴書で編年体式・逆編年体式・キャリア式のどれを選んだか、その理由（作成担当の出力 JSON の `format`）。 |

## パイプライン

受付から納品まで Step 0〜4 を順に進める。`{PROFILE}` は `profile.json` の絶対パスに、`{COMPANY_RESEARCH}` は対象企業の `company_research.json` の絶対パスに読み替える。`{SELF_ANALYSIS}` は `career-private/self_analysis.json` の絶対パス（あれば）とする。`{FIT_ASSESSMENT}` は `career-private/fit/{企業スラッグ}/fit_assessment.json` の絶対パス（あれば）とする。`{OUT_DIR}` は書類の出力先ディレクトリに読み替える。

### Step 0 受付

次を確認する。不明点の確認は AskUserQuestion で選択式を基本とし、1回最大4問・各4択までとする。

| 確認項目 | 内容 |
|---|---|
| 書類種別 | 職務経歴書／履歴書／英文レジュメ／志望動機書のいずれか（複数可）。 |
| 求人票 | 対象求人の要件。テキストまたはファイルで受け取る。無い場合は汎用の書式作成に範囲を限定する。 |
| 対象企業 | 企業別カスタマイズの対象。スラッグの解決に入る前に `validate_company_index.py`（hub の scripts）で一覧を検証し、FAIL（ERROR 1件以上）なら指摘内容を利用者へ示し、修復されるまで解決へ進まない。そのうえで企業スラッグを `career-private/company_index.json` で解決し（詳細は hub の `references/company-index-format.md`）、`{OUT_DIR}` を定める。 |

profile.json のゲートは必須である。

- `profile.json` は `validate_profile.py`（hub の scripts）が PASS（ERROR 0件）であることを前提とする。hub 経由で入る場合は、hub がルーティング前に確認済みである。本スキルが単独で起動された場合は、自分で `validate_profile.py` を実行して PASS を確かめる。
- `profile.json` が未作成の場合は先へ進まない。hub（`job-change-support`）のプロファイル整備へ戻し、作成してから再開する（プロファイルの作成は hub と `job-change-profile` の責務である）。
- 検証が FAIL（ERROR 1件以上）の場合は、ERROR の内容を利用者へ示し、`job-change-profile` での整備を勧める。ただし、利用者が欠落を承知のうえで着手を希望する場合は、欠けた項目の値を直接引用または前提とする記述を作らないという条件で進めてよい。その場合は、どの項目が欠けたままかを納品時に明記する。hub から振り分けられ、hub がすでにこの選択を利用者へ求めている場合は、再度問わずにその選択に従う。hub と本スキルが同じ選択を2回求めないためである。

`profile.json` の `career_history[].achievements` と `skills` が空の場合は、`job-change-profile` のセクション更新（職歴と実績・スキル）で深掘りしてから戻るよう案内する。実績とスキルはここで初めて要るようになる項目であり、プロファイルのライト初回では既定で飛ばしてある。検証は PASS するため、差し戻しではなく案内である。利用者がそのまま進めることを選んだ場合は、職歴の骨格だけで書ける範囲に限って作成し、実績の記載が無いことを納品時に明記する。

company_research.json の確認は任意であり、無い場合はフォールバックを明示する。

- 対象企業の `company_research.json` の有無を確認する。無い場合はエラーとしない。企業固有の調整をしないフォールバック動作とすることを利用者へ明示する。あわせて、企業研究（`job-change-company-research`）を先に実行すれば志望動機・企業別カスタマイズの精度が上がることも伝える。
- `company_research.json` がある場合は、`check_freshness.py`（hub の scripts）で当該企業の `_manifest.json` を判定する。`stale` のトピックがあれば、その旨と対象トピック名を利用者へ示し、`job-change-company-research` での差分再調査を提案する。利用者が再調査せずに進むことを選んだ場合は、古い情報に基づく旨と対象トピック名を Step 4 の調整根拠の説明へ明記して進む。判定規則と TTL の原本は hub の `references/freshness-policy.md` にある。

self_analysis.json も任意の入力である。

- `career-private/self_analysis.json` の有無を確認する。あれば志望動機書・自己PRの入力に加える。無くても進行できるが、自己分析（`job-change-self-analysis`）を先に実行すればキャリア・ナラティブと転職理由の建設的な言語化を反映できることを、利用者へ明示する。

fit_assessment.json も同じく必須ではない。

- `career-private/fit/{企業スラッグ}/fit_assessment.json` の有無を確認する。あればアピールマッピングの訴求点選定に、`dimensions` の `evidence` と `must_condition_results` を判断材料として加える。無くても進行できる（求人要件と `profile.json` の実績の突き合わせのみで進める）。fit_assessment.json は career-private 配下の成果物であり、Web ツールを持つエージェントへは渡さない。

### Step 1 作成

`job-change-document-writer` エージェント（model: opus）を起動し、Step 1（作成）を指示する。指示書には次を渡す。

- 実行するステップ（= 1）・書類種別・`{PROFILE}`・`{COMPANY_RESEARCH}`（あれば）・`{SELF_ANALYSIS}`（あれば）・`{FIT_ASSESSMENT}`（あれば）・求人票（あれば）・出力先 `{OUT_DIR}`。

作成担当には次を行う責務がある。求人要件と（あれば）企業研究の理念・求める人物像を抽出し、`profile.json` の実績と突き合わせてアピールマッピングを作る。そのうえで、書類種別ごとの標準形式を理由とともに選定して作成する。書類は `{OUT_DIR}` の下に書き出す。`company_research.json` が無い場合は企業固有の調整をしない。その旨を成果物と出力 JSON（`company_research_used: false`・`degraded_reason`）に明記する。`fit_assessment.json` がある場合、アピールマッピングの訴求点選定に `dimensions` の `evidence` と `must_condition_results` を判断材料として加える。無い場合は求人要件と `profile.json` の実績の突き合わせのみで進める。

志望動機書・自己PRでは、`self_analysis.json` がある場合、`career_narrative`（ライフテーマ・一貫する動機）を素材に用いる。根拠付きの `strengths`（episode_id・feedback_id に対応づけられた強み）も用いる。`reason_for_change.constructive_version`（発揮したい価値を軸にした転職理由の言い換え）も同様である。いずれも profile.json の実績と併せて用いる。`self_analysis.json` が無い場合は profile.json の `strengths`・`job_change_axis.reasons` のみを素材とする。この場合は、企業固有の調整のときとは異なり、フォールバックした旨を明示する必要はない。

### Step 2 独立監査

`job-change-document-auditor` エージェント（model: sonnet）を、作成担当の判断理由を渡さない新規コンテキストで起動し、Step 2（監査）を指示する。指示書には監査対象の書類ファイルの絶対パス・書類種別・`{PROFILE}`・求人票（あれば）を渡す。

監査担当が検査するのは次の4点である。

- **和文の文法と表記。** 職務経歴書・履歴書・志望動機書を対象に、役割プロンプトの「判断の原本」に挙げた観点（助詞・主述の対応・係り受け・並列・冗長表現・表記揺れ・誤字脱字）で見る。
- **誇張・創作。** `profile.json` と突き合わせ、記載のない実績・数値、metric との不一致、裏付けを超えた規模・範囲・主体の言葉を検出する。
- **求人要件との対応・定量性・分量。**
- **英文レジュメ。** 英語の文法・時制、アクション動詞（action verb）の適否（動詞始まり・主語省略）、定量性、ATS適合（表・画像・グラフィックの回避、求人票キーワードとの文脈整合）、分量（1〜2枚）を見る。和文の文法・表記の検査は対象外とする。

判定は `verdict`（BLOCK / CONCERNS / CLEAN）と `findings`（各 finding に `severity` = 重大 / 警告 / 軽微）で返る。

### Step 3 監査指摘の反映

`verdict` が CLEAN でなければ、findings を `job-change-document-writer` へ渡し、Step 3（監査指摘の反映）を指示する。指示書には Step 1 と同じ入力に加えて、監査担当の findings を渡す。

作成担当は findings を1件ずつ確認し、`profile.json` の範囲内で対応できる指摘を書類へ反映する。反映しなかった指摘は理由を明記する（例: profile.json に裏付けが無く、要求された加筆が創作になる場合）。

- `verdict` が BLOCK、または `severity` = 重大 の finding がある場合は、反映後に Step 2 へ戻して再監査する（差し戻しの1回に数える）。
- `verdict` が CONCERNS で重大 finding が無い場合（警告・軽微のみ）は、指摘を反映し、再監査は任意とする。反映を終えてから、または反映できなかった指摘を調整根拠に記録してから、Step 4 へ進む。

### Step 4 納品

`verdict` が CLEAN になった時点、または重大な finding が解消した時点で納品する。最終納品物は次の3点である。

1. **応募書類**（`{OUT_DIR}` 配下のファイル）。
2. **アピールマッピング表**（求人要件・対応する実績・裏付け）。`{OUT_DIR}/appeal-mapping.md` へ書き出す。
3. **調整根拠の説明**（選定した形式とその理由、企業別カスタマイズで何をどの `company_research.json` の claim に基づいて調整したか、および監査結果）。フォールバック時は企業固有の調整をしていない旨を書く。監査結果には最終 verdict と、未反映で残した指摘があればその理由を含める。`{OUT_DIR}/tailoring-rationale.md` へ書き出す。

最終メッセージには、作成した書類の種別とファイルパス、選定形式、監査の最終 verdict、未解決事項（あれば）を要約する。調整根拠の説明と最終メッセージはいずれも結論から述べる。中身の無い節・同じ内容の繰り返し・定型の前置きを置かない。

## 合否ゲートと差し戻し

パイプラインには2つのゲートがある。

| ゲート | 通過条件と差し戻し先 |
|---|---|
| Step 0 のプロファイルゲート | `profile.json` が `validate_profile.py` で PASS していなければ作成へ進まない。未作成・FAIL は hub のプロファイル整備へ戻す。ただし FAIL の場合は、ERROR の内容を示し、利用者が欠落を承知で着手を希望するなら、欠けた項目の値を直接引用または前提とする記述を作らないという条件で進めてよい。どの項目が欠けたままかを成果物に明記する。hub がすでにこの選択を利用者へ求めている場合は、再度問わずにその選択に従う。 |
| Step 2 の独立監査ゲート | `job-change-document-auditor` の `verdict` が BLOCK、または `severity` = 重大 の finding があれば Step 3 で作成担当へ差し戻す。差し戻しは同一書類につき最大2回まで行う。 |

差し戻し時は、監査の findings（target・evidence・fix）をそのまま作成担当へ渡し、反映後に Step 2 から再度通す。2回の差し戻しで解消しない指摘は、未決事項として調整根拠の説明に明記し、利用者へ判断を委ねてから納品する。例えば「profile.json の実績だけでは求人要件を十分に満たせない」という指摘は、経歴の補強か応募判断の見直しが要るため、利用者の判断事項とする。機械的な検証の ERROR は差し戻しの上限にかかわらず解消してから納品し、未解決が監査の finding だけである場合に限り、未決事項として明記したうえで納品してよい。

## 役割の実行（ハーネス別）

本スキルのパイプラインは、専門の役割へ作業を委ねる形で書いてある。役割の内容は `references/roles/` に置き、これを原本とする。

| エージェント名 | 役割プロンプトの原本 |
|---|---|
| `job-change-document-writer` | `{SKILL_DIR}/references/roles/document-writer.md` |
| `job-change-document-auditor` | `{SKILL_DIR}/references/roles/document-auditor.md` |

ハーネス別の実行手順、起動する数の判断、作成と監査を分ける理由の原本は hub の `{HUB_SKILL_DIR}/references/role-execution.md` にある。

## エージェントのモデル方針

| エージェント | model | 責務 |
|---|---|---|
| `job-change-document-writer` | opus | アピールマッピング・形式選定・作成（Step 1）と監査指摘の反映（Step 3） |
| `job-change-document-auditor` | sonnet | 独立コンテキストでの書類監査（Step 2）。和文の文法・表記も自身で検査する |

model は各エージェントの frontmatter に固定済みであり、起動時に上書きしない。

## スクリプトのCLI使用例

本スキルは固有のスクリプトを持たない。Step 0 で用いる3本はいずれも hub（`job-change-support`）のスクリプトであり、hub 経由で入る場合は hub がルーティング前に実行済みである。単独で起動された場合は本スキルが次を実行する。

```bash
python {HUB_SKILL_DIR}/scripts/validate_profile.py {DATA_ROOT}/career-private/profile.json
python {HUB_SKILL_DIR}/scripts/validate_profile.py {DATA_ROOT}/career-private/profile.json --json
python {HUB_SKILL_DIR}/scripts/validate_company_index.py {DATA_ROOT}/career-private/company_index.json
python {HUB_SKILL_DIR}/scripts/check_freshness.py {DATA_ROOT}/companies/{企業スラッグ}/_manifest.json
```

`validate_profile.py`・`validate_company_index.py` の終了コードは PASS で 0、FAIL で 1（WARN のみは PASS 扱い）である。`--json` は結果を JSON 形式（`status`・`error_count`・`warning_count`・`errors`・`warnings`）で出力する。`check_freshness.py` は常に終了コード 0 を返し、`fresh`・`stale`・`missing` の分類を出力する。profile.json のフィールド仕様の原本は hub の `references/profile-format.md` にある。

## references 一覧

| ファイル | 何を | いつ読むか |
|---|---|---|
| `references/shokumu-keirekisho.md` | 職務経歴書の3形式・使い分け・職務要約・実績の定量化・分量・採用担当者の観点 | 職務経歴書を作成/監査するとき |
| `references/rirekisho.md` | 履歴書様式の現行事情（厚労省様式例）・手書き/パソコン・使い回しの回避 | 履歴書を作成/監査するとき |
| `references/english-resume.md` | 英文レジュメの標準構成・記載しない個人情報・定量化・ATS対応 | 英文レジュメを作成/監査するとき |
| `references/tailoring.md` | 企業別カスタマイズ・志望動機の構成・アピールマッピング・誇張禁止基準 | 志望動機/企業別調整を行うとき、全書類の誇張検査の基準として |
