---
name: job-change-documents
description: >-
  転職の応募書類（職務経歴書・履歴書・英文レジュメ・志望動機書）を、profile.json の実績と求人要件・
  企業研究の結果に基づいて作成するサブスキル。求人要件と実績の対応表（アピールマッピング）を作り、
  書類種別ごとの標準形式で起草し、独立した監査（日本語文法、誇張・創作の検出、要件との対応、英文レジュメの観点、分量）を通してから納品する。定量値は profile.json の metric と厳密一致させ、記載のない実績を
  創作しない、という原則を保つ。job-change-support（hub）から振り分けられて動く。個々の起草・監査は
  専用エージェント（job-change-document-writer / job-change-document-auditor）が担う。
  Use when the user writes job application documents for a career change in Japan (including
  foreign-affiliated selection) — a shokumu-keirekisho (work-history CV), rirekisho (resume), English
  resume, or statement of motivation — based on their profile and the target company's requirements.
  trigger words: 職務経歴書, 履歴書, 応募書類, 志望動機, レジュメ, 英文レジュメ, 職務要約, 自己PR。
allowed-tools: Read, Write, Edit, Glob, Grep, Agent, AskUserQuestion, Skill
---

# job-change-documents

転職の応募書類を作成するとき、このスキル1つで受付から納品までの手順がそろう。求人要件と利用者の実績を対応づけ、書類種別ごとの標準形式で起草し、起草担当とは独立した監査を通してから納品する。日本の中途採用を中心とし、外資系選考向けの英文レジュメにも対応する。

起草と監査はそれぞれ専用エージェント（`job-change-document-writer`・`job-change-document-auditor`）が担い、本スキルはその起動・差し戻し・納品を統括する。書類種別ごとの記述基準は `references/` で完結する。

## 目的と原則

1. **実績は profile.json の範囲内でのみ書く。** 書類に載せる経歴・実績・数値は、すべて `profile.json` に記載のある範囲に限る。記載のない実績・経歴を創作しない（虚偽記載の禁止）。定量値は `profile.json` の `achievements[].metric` と厳密一致させ、丸め・上振れをしない。規模・範囲・主体を表す語（大規模・全社・主導など）は、`profile.json` の記述で裏付けられる範囲を超えて用いない。

2. **求人要件と実績を対応づけてから書く。** 起草の前に、求人要件と `profile.json` の実績を突き合わせたアピールマッピング（要件・対応する実績・裏付け）を作る。訴求点は必ず求人要件に対応づける。要件に対応する実績が profile.json に無い項目は、該当なしとして扱い、創作で埋めない。

3. **起草と監査を分離する。** 起草担当の判断理由を渡さない新規コンテキストで監査担当を起動し、成果物そのものに基づいて検査させる。監査は書類を書き換えず、指摘（findings）だけを返す。反映は起草担当が行う。

4. **企業固有の調整には企業研究の結果を用いる。** 志望動機・企業別カスタマイズは、対象企業の `company_research.json`（理念・求める人物像など）を根拠とする。`company_research.json` が無い場合は企業固有の調整をせず、簡易対応（企業に依存しない汎用の書式・自己PRの骨子まで）である旨を利用者へ明示する。

5. **個人情報を外部へ送信しない。** `profile.json` に含まれる個人情報（現年収・希望年収・居住地・学歴・在籍企業名・実績など）は、検索クエリ・fetch・外部 API を含む一切の外部送信に用いない。本スキルの起草・監査エージェントは Web 送信手段を持たないが、このルールは本スキルおよび下流のすべての手順で保つ。

## 範囲外

- **求人への応募実行・書類の外部送信。** 応募フォームからの送信、転職エージェントへの提出、スカウトへの返信など、利用者に代わって外部へ送信する操作は行わない。書類の作成までを支援し、送信は本人が行う。
- **プロファイルの新規作成。** `profile.json` の作成・検証は hub（`job-change-support`）が担う。本スキルは既存の `profile.json` を入力として用いる。
- **企業研究そのもの。** 企業の理念・事業・評判の調査は `job-change-company-research` が担う。本スキルはその成果物（`company_research.json`）を参照する。
- **証明写真の撮影・作成、書類の印刷・製本などの物理的な作業。** これらは扱わない。

## パスの解決

利用者データの置き場所は設定ファイルだけが決める。既定の置き場所を持たない。本文で `{DATA_ROOT}` と書いた箇所は、設定ファイルの `data_root` に読み替える。

hub（job-change-support）から振り分けられた場合は、hub が解決済みの `{DATA_ROOT}` を渡す。単独で起動された場合は、次の順に設定ファイルを探し、最初に見つかったものを Read で読む。

1. 環境変数 `JOB_CHANGE_CONFIG` が指すファイル
2. カレントディレクトリから上位へたどった最初の `.job-change/config.json`
3. `~/.job-change/config.json`

いずれの場所にも設定ファイルが無ければ未設定である。その場合は作業へ進まず、hub（job-change-support）へ戻して設定の作成を先行させる。

`{SKILL_DIR}` は本スキルの絶対パス、`{HUB_SKILL_DIR}` は同じ配置先にある `job-change-support` の絶対パスを指す。設定ファイルの仕様は `docs/configuration.md` にある。

## データ配置

利用者データは、非公開ディレクトリ `{DATA_ROOT}/career-private/`（profile.json 等の個人情報）と、その外側のプロジェクト直下 `{DATA_ROOT}/`（企業別成果物などの非個人情報）に分けて置く。本スキルが読み書きするパスは次のとおり。

| パス | 役割 | 入出力 |
|---|---|---|
| `career-private/profile.json` | 利用者プロファイルの原本 | 入力（読むのみ） |
| `career-private/self_analysis.json` | 自己分析の成果物（原本は `job-change-self-analysis`） | 入力（任意。あれば志望動機書・自己PRの入力に加える。無くても進行できる） |
| `career-private/fit/{企業スラッグ}/fit_assessment.json` | 適合性評価の成果物（原本は `job-change-fit-assessment`） | 入力（任意。あればアピールマッピングの訴求点選定に加える。無くても進行できる） |
| `companies/{企業スラッグ}/company_research.json` | 企業研究の構造化データ | 入力（任意。無ければ縮退） |
| `companies/{企業スラッグ}/documents/` | 作成した応募書類の出力先 | 出力 |

- 企業スラッグは hub と同じ規約に従い、`career-private/company_index.json` で解決する（例: 架空クラウドワークス社 → `kakuu-cloudworks`）。
- 企業に依存しない汎用書類（対象企業が未定の場合）は、`documents/` の下に置く。
- 書類ファイルは種別で命名を分ける（例: `shokumu-keirekisho.md`・`rirekisho.md`・`english-resume.md`・`motivation.md`）。

## 中間成果物

パイプラインの過程で次を作る。いずれも最終納品物へ含める。

| 中間成果物 | 内容 |
|---|---|
| アピールマッピング | 求人要件・対応する実績・裏付けの3列の対応表。起草担当が Step 1 で作り、出力 JSON（`appeal_mapping`）と成果物に載せる。誇張のない訴求の根拠であり、監査担当が要件対応の検査に用いる。 |
| 形式選定の記録 | 職務経歴書で編年体式・逆編年体式・キャリア式のどれを選んだか、その理由（起草担当の出力 JSON の `format`）。 |

## パイプライン

受付から納品まで Step 0〜4 を順に進める。`{PROFILE}` は `profile.json` の絶対パス、`{COMPANY_RESEARCH}` は対象企業の `company_research.json` の絶対パス、`{SELF_ANALYSIS}` は `career-private/self_analysis.json` の絶対パス（あれば）、`{FIT_ASSESSMENT}` は `career-private/fit/{企業スラッグ}/fit_assessment.json` の絶対パス（あれば）、`{OUT_DIR}` は書類の出力先ディレクトリに読み替える。

### Step 0 受付

次を確認する。不明点の確認は AskUserQuestion で選択式を基本とし、1回最大4問・各4択までとする。

| 確認項目 | 内容 |
|---|---|
| 書類種別 | 職務経歴書／履歴書／英文レジュメ／志望動機書のいずれか（複数可）。 |
| 求人票 | 対象求人の要件。テキストまたはファイルで受け取る。無い場合は汎用の書式作成に範囲を限定する。 |
| 対象企業 | 企業別カスタマイズの対象。企業スラッグを `career-private/company_index.json` で解決し（詳細は hub の `references/company-index-format.md`）、`{OUT_DIR}` を定める。 |

profile.json のゲートは必須である。

- `profile.json` は `validate_profile.py`（hub の scripts）が PASS（ERROR 0件）であることを前提とする。hub がルーティング前に PASS を確認済みであり、本スキルは Bash を持たないため検証を自ら実行しない。
- `profile.json` が未作成、または検証が FAIL（ERROR 1件以上）の場合は、本スキルで先へ進まない。hub（`job-change-support`）のプロファイル整備へ戻し、PASS を確認してから再開する（プロファイルの作成・検証は hub の責務である）。

company_research.json の確認は任意であり、無い場合は縮退を明示する。

- 対象企業の `company_research.json` の有無を確認する。無い場合はエラーとせず、企業固有の調整をしない縮退動作とすること、および企業研究（`job-change-company-research`）を先に実行すれば志望動機・企業別カスタマイズの精度が上がることを、利用者へ明示する。

self_analysis.json の確認は任意である。

- `career-private/self_analysis.json` の有無を確認する。あれば志望動機書・自己PRの入力に加える。無くても進行できるが、自己分析（`job-change-self-analysis`）を先に実行すればキャリア・ナラティブと転職理由の建設的な言語化を反映できることを、利用者へ明示する。

fit_assessment.json の確認は任意である。

- `career-private/fit/{企業スラッグ}/fit_assessment.json` の有無を確認する。あればアピールマッピングの訴求点選定に、`dimensions` の `evidence` と `must_condition_results` を参照材料として加える。無くても進行できる（求人要件と `profile.json` の実績の突き合わせのみで進める）。fit_assessment.json は career-private 配下の成果物であり、Web ツール保持エージェントへは渡さない。

### Step 1 起草

`job-change-document-writer` エージェント（model: opus）を起動し、Step 1（起草）を指示する。指示書には次を渡す。

- 実行するステップ（= 1）・書類種別・`{PROFILE}`・`{COMPANY_RESEARCH}`（あれば）・`{SELF_ANALYSIS}`（あれば）・`{FIT_ASSESSMENT}`（あれば）・求人票（あれば）・出力先 `{OUT_DIR}`。

起草担当には次を行う責務がある。求人要件と（あれば）企業研究の理念・求める人物像を抽出し、`profile.json` の実績と突き合わせてアピールマッピングを作り、書類種別ごとの標準形式を理由とともに選定して起草する。書類は `{OUT_DIR}` の下に書き出す。`company_research.json` が無い場合は企業固有の調整をせず、その旨を成果物と出力 JSON（`company_research_used: false`・`degraded_reason`）に明記する。`fit_assessment.json` がある場合、アピールマッピングの訴求点選定に `dimensions` の `evidence` と `must_condition_results` を参照材料として加える。無い場合は求人要件と `profile.json` の実績の突き合わせのみで進める。

志望動機書・自己PRでは、`self_analysis.json` がある場合、`career_narrative`（ライフテーマ・一貫する動機）と根拠付きの `strengths`（episode_id・feedback_id に対応づけられた強み）、`reason_for_change.constructive_version`（発揮したい価値を軸にした転職理由の言い換え）を、profile.json の実績と併せて素材に用いる。`self_analysis.json` が無い場合は profile.json の `strengths`・`job_change_axis.reasons` のみを素材とし、この場合は、企業固有の調整のときとは異なり、縮退した旨を明示する必要はない。

### Step 2 独立監査

`job-change-document-auditor` エージェント（model: sonnet）を、起草担当の判断理由を渡さない新規コンテキストで起動し、Step 2（監査）を指示する。指示書には監査対象の書類ファイルの絶対パス・書類種別・`{PROFILE}`・求人票（あれば）を渡す。

監査担当が検査するのは次の4点である。

- **和文の文法と表記。** 職務経歴書・履歴書・志望動機書を対象に、役割プロンプトの「判断の原本」に挙げた観点（助詞・主述の対応・係り受け・並列・冗長表現・表記揺れ・誤字脱字）で見る。
- **誇張・創作。** `profile.json` と突き合わせ、記載のない実績・数値、metric との不一致、裏付けを超えた規模・範囲・主体の語を検出する。
- **求人要件との対応・定量性・分量。**
- **英文レジュメ。** 英語の文法・時制、アクション動詞（action verb）の適否（動詞始まり・主語省略）、定量性、ATS適合（表・画像・グラフィックの回避、求人票キーワードとの文脈整合）、分量（1〜2枚）を見る。和文の文法・表記の検査は対象外とする。

判定は `verdict`（BLOCK / CONCERNS / CLEAN）と `findings`（各 finding に `severity` = 重大 / 警告 / 軽微）で返る。

### Step 3 監査指摘の反映

`verdict` が CLEAN でなければ、findings を `job-change-document-writer` へ渡し、Step 3（監査指摘の反映）を指示する。指示書には Step 1 と同じ入力に加えて、監査担当の findings を渡す。

起草担当は findings を1件ずつ確認し、`profile.json` の範囲内で対応できる指摘を書類へ反映する。反映しなかった指摘は理由を明記する（例: profile.json に裏付けが無く、要求された加筆が創作になる場合）。

- `verdict` が BLOCK、または `severity` = 重大 の finding がある場合は、反映後に Step 2 へ戻して再監査する（差し戻しの1回に数える）。
- `verdict` が CONCERNS で重大 finding が無い場合（警告・軽微のみ）は、指摘を反映し、再監査は任意とする。反映を終えてから、または反映できなかった指摘を調整根拠に記録してから、Step 4 へ進む。

### Step 4 納品

`verdict` が CLEAN になった時点、または重大な finding が解消した時点で納品する。最終納品物は次の3点。

1. **応募書類**（`{OUT_DIR}` 配下のファイル）。
2. **アピールマッピング表**（求人要件・対応する実績・裏付け）。
3. **調整根拠の説明**（選定した形式とその理由、企業別カスタマイズで何をどの `company_research.json` の claim に基づいて調整したか、および監査結果）。縮退時は企業固有の調整をしていない旨を書く。監査結果には最終 verdict と、未反映で残した指摘があればその理由を含める。

最終メッセージには、作成した書類の種別とファイルパス、選定形式、監査の最終 verdict、未解決事項（あれば）を要約する。

## 合否ゲートと差し戻し

パイプラインには2つのゲートがある。

| ゲート | 通過条件と差し戻し先 |
|---|---|
| Step 0 のプロファイルゲート | `profile.json` が `validate_profile.py` で PASS していなければ起草へ進まない。未作成・FAIL は hub のプロファイル整備へ戻す。 |
| Step 2 の独立監査ゲート | `job-change-document-auditor` の `verdict` が BLOCK、または `severity` = 重大 の finding があれば Step 3 で起草担当へ差し戻す。差し戻しは同一書類につき最大2回まで行う。 |

差し戻し時は、監査の findings（target・evidence・fix）をそのまま起草担当へ渡し、反映後に Step 2 から再度通す。2回の差し戻しで解消しない指摘は、未決事項として調整根拠の説明に明記し、利用者へ判断を委ねてから納品する。例えば「profile.json の実績だけでは求人要件を十分に満たせない」という指摘は、経歴の補強か応募判断の見直しが要るため、利用者の判断事項とする。

## 役割の実行（ハーネス別）

本スキルのパイプラインは、専門の役割へ作業を委ねる形で書いてある。役割の内容は `references/roles/` に置き、これを原本とする。

| エージェント名 | 役割プロンプトの原本 |
|---|---|
| `job-change-document-writer` | `{SKILL_DIR}/references/roles/document-writer.md` |
| `job-change-document-auditor` | `{SKILL_DIR}/references/roles/document-auditor.md` |

**サブエージェントを起動できるハーネス（Claude Code）。** 各 Step の記述どおり、上表のエージェント名を Agent ツールで起動し、指示書を渡す。エージェント定義はリポジトリの `agents/` にあり、`references/roles/` から同期生成されている。

**サブエージェントを起動できないハーネス（Codex ほか）。** 各 Step の「エージェントを起動する」を「役割プロンプトを読み、その役割として自分で実行する」と読み替える。手順は次のとおり。

1. 上表の役割プロンプトを Read で読む。
2. Step に書かれた指示書の項目を、そのまま自分への指示として扱う。
3. 役割プロンプトの「扱ってよい入力」のルールを守る。Web 送信手段を持たない役割として書かれている場合、その作業中は Web 検索・fetch を使わない。
4. 成果物の形式・検証・合否ゲートは、ハーネスによらず同一である。

本スキルは起草と監査を別の役割へ分け、監査者に起草者の判断理由を渡さないことで独立性を保つ。サブエージェントを使えないハーネスでは、同一の文脈で両方を担うためこの独立性が下がる。その場合、監査の段では起草時の判断理由・迷った箇所・書き換えの経緯を一切参照せず、成果物と原本（`references/` の仕様）だけを見て判定する。判定を終えるまで、起草側の意図を補って読まない。

## エージェントのモデル方針

| エージェント | model | 責務 |
|---|---|---|
| `job-change-document-writer` | opus | アピールマッピング・形式選定・起草（Step 1）と監査指摘の反映（Step 3） |
| `job-change-document-auditor` | sonnet | 独立コンテキストでの書類監査（Step 2）。和文の文法・表記も自身で検査する |

起草は求人要件と実績を対応づけて表現を組み立てる判断を要するため opus、監査は定められた基準への照合が中心であるため sonnet とする。model は各エージェントの frontmatter に固定済みであり、起動時に上書きしない。

## スクリプトのCLI使用例

本スキルは固有のスクリプトを持たない。Step 0 のプロファイルゲートで用いる `validate_profile.py` は hub（`job-change-support`）のスクリプトである。次のコマンドは hub がルーティング前に実行するものであり、本スキルは Bash を持たないため自ら実行しない（掲載は前提確認のため）。終了コードは PASS で 0、FAIL で 1（WARN のみは PASS 扱い）である。

```bash
python {HUB_SKILL_DIR}/scripts/validate_profile.py {DATA_ROOT}/career-private/profile.json
python {HUB_SKILL_DIR}/scripts/validate_profile.py {DATA_ROOT}/career-private/profile.json --json
```

`--json` は結果を JSON 形式（`status`・`error_count`・`warning_count`・`errors`・`warnings`）で出力する。profile.json のフィールド仕様の原本は hub の `references/profile-format.md` にある。

## references 一覧

| ファイル | 何を | いつ読むか |
|---|---|---|
| `references/shokumu-keirekisho.md` | 職務経歴書の3形式・使い分け・職務要約・実績の定量化・分量・採用担当者の観点 | 職務経歴書を起草/監査するとき |
| `references/rirekisho.md` | 履歴書様式の現行事情（厚労省様式例）・手書き/パソコン・使い回しの回避 | 履歴書を起草/監査するとき |
| `references/english-resume.md` | 英文レジュメの標準構成・記載しない個人情報・定量化・ATS対応 | 英文レジュメを起草/監査するとき |
| `references/tailoring.md` | 企業別カスタマイズ・志望動機の構成・アピールマッピング・誇張禁止基準 | 志望動機/企業別調整を行うとき、全書類の誇張検査の基準として |
