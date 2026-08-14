---
name: job-change-self-analysis
description: >-
  転職の自己分析を担うサブスキル。profile.json を土台に、行動エピソード（STAR素材）と他者フィードバックを
  内省と対等の必須要素として集め、興味・価値観・career adaptability の4次元・過去の行動の4軸で構造化し、
  根拠づけた強み、キャリア・ナラティブ、退職理由の建設的な言い換えの3点を持つ self_analysis.json を作る。
  面接対策（job-change-interview-prep）と志望動機の深化（job-change-documents）が読める成果物にする。
  強みは行動証拠または他者証言への対応づけを必須とし、内省単独に高い重みを与えない。質問を有限の構造化された問いに限って反すうを防ぎ、診断結果を確定ラベルとして扱わず、事実の創作・誇張をせず、metric を厳密に一致させる。
  作成と独立監査は専用エージェント（job-change-self-analysis-writer / job-change-self-analysis-auditor）が担う。
  job-change-support（hub）から振り分けられて動く。
  Use when the user does self-analysis for a job change in Japan — organizing strengths, taking stock of
  their career, deepening their reasons for changing jobs, or building a consistent career narrative for
  interviews and statements of motivation.
  trigger words: 自己分析, 強みの整理, キャリアの棚卸し, 転職の軸を深めたい, 自己PRの根拠, キャリア・ナラティブ,
  他己分析, モチベーショングラフ, 退職理由の言語化。
allowed-tools: Read, Write, Glob, Grep, Bash, AskUserQuestion, Agent, Skill
---

# job-change-self-analysis

転職の自己分析に取り組むとき、このスキル1つで棚卸しから成果物の納品までの手順がそろう。profile.json を土台に、行動エピソード（STAR素材）と他者フィードバックを内省と対等に集め、興味・価値観・career adaptability の4次元・過去の行動の4軸で構造化し、根拠づけた強み、キャリア・ナラティブ、退職理由の建設的な言い換えの3点を持つ self_analysis.json を作る。成果物は面接対策（job-change-interview-prep）と志望動機の深化（job-change-documents）が入力として読む。

本スキルは、行動証拠と他者視点を内省と併用する（根拠は `references/self-analysis-methods.md`）。作成と独立監査はそれぞれ専用エージェント（`job-change-self-analysis-writer`・`job-change-self-analysis-auditor`）が担い、本スキルはその起動・差し戻し・納品を統括する。

## 目的と原則

1. **他者視点と行動証拠を内省と併用する。** 強み（strengths）は、行動エピソード（behavioral_episodes）または他者証言（others_feedback）への対応づけを必須とし、内省単独の強みは認めない（検証スクリプトが ERROR とする）。他者フィードバックの受け取りは課題志向で行い、人格評価としてではなく行動と結果への対応づけとして記録する。

2. **有限の構造化された問いに限る（反すう防止）。** 質問は `references/question-bank.md` の有限の問いに限定し、無制限の「なぜ」の反復を促さない。深掘りが感情の反すうに陥らないようにし、必ず行動・事実（エピソード）へ対応づける。感情の将来予測（「転職すれば幸せになれる」）を確信・断定の根拠にしない。

3. **診断結果を確定ラベルとして扱わない。** 妥当性の弱い枠組み（Schein のキャリア・アンカー、商用の strengths ツール、RIASEC 自己診断ツール）は、内省を促す呼び水として限定的に使い、結果を「確定した自分」として扱わない。実務手法（Will-Can-Must・モチベーショングラフ・他己分析・ジョハリの窓）は聞き取りを進めるために使い、その出力は内省・行動・他者証言で裏付けてから成果物へ取り入れる。

4. **事実を創作・誇張しない。** 成果物に載せる経歴・実績・数値は profile.json に記載のある範囲に限る。behavioral_episodes の `metric`（定量値）は profile.json の実績と厳密一致させ、丸め・上振れをしない。規模・範囲・主体を表す言葉（大規模・全社・主導など）は、profile.json の記述で裏付けられる範囲を超えて用いない。

5. **個人情報を外部へ送信しない。** `profile.json`・`self_analysis.json` に含まれる個人情報は、検索クエリ・fetch・外部 API を含む一切の外部送信に用いない。対象の列挙と役割ごとの可否の原本は hub の `{HUB_SKILL_DIR}/references/pii-boundary.md` にある。本スキルは境界の内側にある `self_analysis.json` を作る側であり、writer（job-change-self-analysis-writer）・auditor（job-change-self-analysis-auditor）はいずれも Web 送信手段を持たないため、これらのパスを渡してよい。

## 範囲外

次は本スキルの範囲外とする。依頼された場合は、対応できない旨と、代わりの担当・行動を伝える。

- **適性検査の受検代行。** 心理検査・適性検査を利用者に代わって受検しない。検査対策は `job-change-exam-prep` が担う。
- **心理療法的な内省支援・メンタルヘルスの相談。** 本スキルは転職のための自己分析に限る。抑うつ・強い不安などメンタルヘルス不調は範囲外とし、専門家（医師・臨床心理士・カウンセラー等）への相談を促す。過度な内省（反すう）は有害であり、本スキルは有限の構造化された問いに範囲を限定する。
- **企業研究。** 企業の理念・事業・評判の調査は `job-change-company-research` が担う。本スキルは利用者自身の分析に限る。
- **応募書類の執筆。** 職務経歴書・志望動機書などの執筆は `job-change-documents` が担う。本スキルはその素材（根拠づけた強み・ナラティブ・退職理由）を作り、渡す。

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

利用者データは、非公開ディレクトリ `{DATA_ROOT}/career-private/` に置く。本スキルが読み書きするパスは次のとおり。

| パス | 役割 | 入出力 |
|---|---|---|
| `career-private/profile.json` | 利用者プロファイルの原本（hub が管理） | 入力（初期値として読む。Step 6 で値のみ反映） |
| `career-private/self_analysis.json` | 自己分析成果物の原本 | 出力（素材部は Step 1〜3 で逐次追記し、統合部は Step 4 で書く） |

- 素材部は `behavioral_episodes`・`others_feedback`・`interests`・`values`・`career_adaptability`、統合部は `strengths`・`career_narrative`・`reason_for_change` を指す。統合部が未作成のあいだは `validate_self_analysis.py` が FAIL するため、検証は Step 5 で行う。
- `self_analysis.json` のフィールド仕様・記入基準・検証規則の原本は `references/self-analysis-format.md` にある。記入例は `assets/self_analysis_example.json`（架空の人物）にある。
- スキル本体フォルダー（`skills/job-change-self-analysis/`）に利用者データを置かない。
- `career-private/` が未作成の場合は、必要になった時点で本スキルが作る。

## パイプライン

受付から納品まで Step 0〜6 を順に進める。`{SKILL_DIR}` は本スキルの絶対パス、`{PROFILE}` は `profile.json` の絶対パス、`{SELF}` は `self_analysis.json` の絶対パスに読み替える。

### Step 0 前提確認

- `profile.json` の有無を確認する。無ければ、自己分析は profile.json を土台にするため、hub（`job-change-support`）経由で `job-change-profile` サブスキルへ先に誘導する。
- `profile.json` を hub の `validate_profile.py` で検証する。FAIL（ERROR 1件以上）の場合の扱いは「合否ゲートと差し戻し」の表に従う。
- 既存の `self_analysis.json` があれば更新モードとし、既存の内容を初期値として読み、差分を追記・修正する。
- 既存の `self_analysis.json` の素材部が一部だけ埋まっている場合は、中断からの再開とみなす。埋まっている段階（Step 1〜3 のどれか）を飛ばして続きから進めることを利用者へ提案し、聞き直すかどうかは利用者に選ばせる。

### Step 1 行動エピソードの棚卸し

`profile.json` の `career_history`・`achievements` を素材として提示し、AskUserQuestion（選択式中心、1回最大4問・各最大4択、自由記述は具体値のみ）で STAR 形式（Situation / Task / Action / Result）へ構造化する。質問は `references/question-bank.md` の Step 1 の問いを使う。モチベーショングラフの考え方（時系列＋感情の起伏）は任意の補助とする。各エピソードに、可能なら `metric`（定量値。profile.json の実績と厳密一致）と `reproducibility`（再現性）を添える。聞き取った内容は、この Step の終わりに `{SELF}` の `behavioral_episodes` へ書き出す（形式の原本は `references/self-analysis-format.md`）。中断しても Step 1 を聞き直さずに再開するためである。

### Step 2 他者フィードバックの取り込み

過去の評価面談・他者から言われたことを、`others_feedback` として記録する（他己分析・ジョハリの窓）。question-bank.md の Step 2 の問いを使う。フィードバックは課題志向で受け取り、人格評価ではなく行動と結果への対応づけで記録し、`linked_episode_ids` でエピソードへ対応づける。この場で他者フィードバックが入手できない場合は、成果物を WARN のまま先へ進め、利用者へ収集を今後の課題として提示する（依頼文は `assets/feedback_request_template.md` を使う）。聞き取った内容は、この Step の終わりに `{SELF}` の `others_feedback` へ書き出す。中断しても Step 2 を聞き直さずに再開するためである。

### Step 3 興味・価値観・career adaptability の構造化質問

`references/question-bank.md` の Step 3 の有限の問いだけを使い、興味（RIASEC の枠組み）・価値観（エピソードへ対応づける）・career adaptability の4次元（concern / control / curiosity / confidence）を構造化する。無制限の「なぜ」の反復を禁じ、深掘りは必ずエピソード（事実）へ対応づける。Schein の8分類・CCI 型5問は呼び水として使い、結果を確定ラベルにしない。聞き取った内容は、この Step の終わりに `{SELF}` の `interests`・`values`・`career_adaptability` へ書き出す。中断しても Step 3 を聞き直さずに再開するためである。

### Step 4 統合（作成）

`job-change-self-analysis-writer` エージェント（model: opus）を起動し、Step 1〜3 で素材部を書き込んだ `{SELF}` と `{PROFILE}`・出力先 `{SELF}` を渡して、素材部を読ませる。作成担当は、strengths の根拠づけ（episode / feedback への対応づけ必須）、career_narrative の作成（ライフテーマ・転機・一貫する動機）、reason_for_change.constructive_version の作成（不満の列挙でなく発揮したい価値を軸に）を行う。戻り値を利用者へ提示し、AskUserQuestion の選択式で修正点を確認する。

### Step 5 機械検証＋独立監査

`validate_self_analysis.py` で `{SELF}` を検証し、PASS（ERROR 0件）を確認する。続いて `job-change-self-analysis-auditor` エージェント（model: opus、作成担当の判断理由を渡さない新規コンテキスト）を起動し、誇張・創作／一貫性／内省単独の重み／反すう・感情予測型の記述を監査する。指摘は Step 4 へ差し戻す（最大2回。以降は利用者の判断による）。

### Step 6 反映と接続案内

`profile.json` へ、`strengths`（self_analysis の strengths.statement の短文）と `job_change_axis.reasons`（constructive_version に基づく文言）を値のみ反映する。profile.json のスキーマは変更しない。反映後に hub の `validate_profile.py` を再実行して PASS を確認し、profile.json の `updated_at` を当日の日付へ書き換える。`self_analysis.json` は下流のサブスキルの入力であって単体の読み物ではないため、整形したファイルは作らない。代わりに、何が書かれたか（強み・価値観・関心・キャリアの物語・転職理由の建設的な言い換え）を利用者へ要約して示す。最後に、`self_analysis.json` を入力に使える下流の作業（`job-change-documents` の志望動機の深化、`job-change-interview-prep` の一貫性ある回答）を案内する。最終メッセージは結論から述べる。中身の無い節・同じ内容の繰り返し・定型の前置きを置かない。

## 合否ゲートと差し戻し

パイプラインには2つのゲートがある。

| ゲート | 通過条件と差し戻し先 |
|---|---|
| Step 0 のプロファイルゲート | `profile.json` が `validate_profile.py` で PASS していなければ着手しない。未作成・FAIL は hub（`job-change-support`）経由で `job-change-profile` サブスキルへ戻す。ただし FAIL の場合は、ERROR の内容を示し、利用者が欠落を承知で着手を希望するなら、欠けた項目の値を直接引用または前提とする記述を作らないという条件で進めてよい。どの項目が欠けたままかを成果物に明記する。 |
| Step 5 の検証・監査ゲート | `validate_self_analysis.py` が FAIL（ERROR 1件以上）の場合、または `job-change-self-analysis-auditor` の `verdict` が BLOCK の場合、または `severity` = must_fix の finding がある場合は、Step 4 で作成担当へ差し戻す。差し戻しは同一成果物につき最大2回まで行う。 |

差し戻し時は、監査の findings（target・evidence・fix）をそのまま作成担当へ渡し、反映後に Step 5 から再度通す。2回の差し戻しで解消しない指摘は、未決事項として利用者へ判断を委ねてから納品する（例: profile.json の実績だけでは強みの裏付けが足りない、という指摘は、他者フィードバックの追加収集か訴求の見直しが要るため利用者の判断事項とする）。機械検証の ERROR は差し戻しの上限にかかわらず解消してから納品し、未解決が監査の finding だけである場合に限り、未決事項として明記したうえで納品してよい。

## 役割の実行（ハーネス別）

本スキルのパイプラインは、専門の役割へ作業を委ねる形で書いてある。役割の内容は `references/roles/` に置き、これを原本とする。

| エージェント名 | 役割プロンプトの原本 |
|---|---|
| `job-change-self-analysis-writer` | `{SKILL_DIR}/references/roles/self-analysis-writer.md` |
| `job-change-self-analysis-auditor` | `{SKILL_DIR}/references/roles/self-analysis-auditor.md` |

ハーネス別の実行手順、起動する数の判断、作成と監査を分ける理由の原本は hub の `{HUB_SKILL_DIR}/references/role-execution.md` にある。

## エージェントのモデル方針

| エージェント | model | 責務 |
|---|---|---|
| `job-change-self-analysis-writer` | opus | strengths の根拠づけ・career_narrative の作成・reason_for_change の建設的言い換え（Step 4）と監査指摘の反映 |
| `job-change-self-analysis-auditor` | opus | 独立コンテキストでの誇張・一貫性・内省単独の重み・反すう/感情予測型記述の監査、検証スクリプトの再実行（Step 5） |

機械的検査は `validate_self_analysis.py` が担う。model は各エージェントの frontmatter に固定済みであり、起動時に上書きしない。

## スクリプトのCLI使用例

自己分析成果物の検証（終了コードは PASS で 0、FAIL で 1。WARN のみは PASS 扱い）。`{SKILL_DIR}` は本スキルの絶対パス、末尾のパスは検証対象の self_analysis.json のパスに読み替える。

```bash
python {SKILL_DIR}/scripts/validate_self_analysis.py {DATA_ROOT}/career-private/self_analysis.json
python {SKILL_DIR}/scripts/validate_self_analysis.py {DATA_ROOT}/career-private/self_analysis.json --json
```

`--json` は結果を JSON 形式（`status`・`error_count`・`warning_count`・`errors`・`warnings`）で出力する。記入例は `assets/self_analysis_example.json`、フィールド仕様と検証規則の原本は `references/self-analysis-format.md` にある。Step 0 のプロファイルゲートで用いる `validate_profile.py` は hub（`job-change-support`）のスクリプトである。

## references 一覧

| ファイル | 何を | いつ読むか |
|---|---|---|
| `references/self-analysis-methods.md` | 採用4軸の実証的裏付けと限界、内省の限界と他者視点併用の根拠、反すう防止の運用規則、論争点の両論併記、DOI 付き出典 | 原則の根拠を確認するとき、監査の観点を定めるとき |
| `references/self-analysis-format.md` | self_analysis.json のフィールド仕様・記入基準・検証規則（ERROR/WARN 一覧） | 成果物を作る/更新する/検証する全段階 |
| `references/question-bank.md` | Step 1〜3 で使う有限の構造化質問（STAR 棚卸し・他己分析・興味/価値観/adaptability・Schein 呼び水・CCI 型5問） | ヒアリングの各 Step で質問を選ぶとき |
| `references/narrative-guide.md` | キャリア・ナラティブの構成、退職理由の建設的言い換え手順、企業側評価との接続と留保、DOI 付き出典 | career_narrative・reason_for_change を作成/監査するとき |
