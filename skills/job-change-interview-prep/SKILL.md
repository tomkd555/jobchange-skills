---
name: job-change-interview-prep
description: >-
  転職の面接対策を担うサブスキル。profile.json と（あれば）company_research.json を入力に、
  job-change-interview-coach（opus）で企業固有の想定質問を質問類型ごとに生成し、模擬面接で回答を
  1問ずつ収集し、STAR・具体性・一貫性・企業理解の4観点でフィードバックし、観点別の強みと優先改善点を
  総括する。company_research.json が無ければ企業非依存の一般対策へ縮退する。日本の中途採用面接を中心に、
  外資系のビヘイビアラル面接・ケース面接へ対応する。profile.json の個人情報は外部送信に用いない。
  Use when the user prepares for a job-change interview in Japan (including foreign-affiliated company
  selection) — generating expected questions, running a mock interview, getting answer feedback, or
  practicing behavioral / case interviews.
  trigger words: 面接対策, 想定問答, 想定質問, 逆質問, 行動面接, ビヘイビアラル面接, ケース面接, 模擬面接。
allowed-tools: Read, Write, Glob, Grep, Bash, Agent, AskUserQuestion, Skill
---

# job-change-interview-prep

転職の面接対策を行うとき、本スキルが想定質問の生成・模擬面接・回答評価・総括までの手順をそろえる。転職支援 hub（job-change-support）の面接対策として振り分けられて起動される。対象は日本の中途採用面接を中心とし、外資系のビヘイビアラル面接・ケース面接へ対応する。

想定質問の生成（Step 1）と回答の評価（Step 3）は専用エージェント job-change-interview-coach（opus）が担う。本スキルはその起動、模擬面接の進行、総括を担う。

## 目的と原則

1. **企業固有の質問は company_research.json の claim を根拠とする。** 企業固有の想定質問は、対象企業の企業研究結果（company_research.json）の claims、特に topic=selection_process（選考プロセス・面接体験記）と topic=philosophy（理念）を根拠とする。company_research.json が無い場合は企業固有の質問を生成せず、企業非依存の一般対策へ縮退する（縮退モード）。company_research.json があっても topic=selection_process の claims が0件の場合は、選考プロセスを前提とする質問（面接の回数・形式・各段階の評価観点を既知として扱う質問）を生成しない。この場合は topic=philosophy の claims だけを根拠に企業固有の質問を作り、選考プロセスの claims が0件である旨を利用者へ伝える（部分縮退）。claims が0件であることを、選考が単純であることの根拠にしない。`career-private/self_analysis.json` がある場合は、想定質問の生成と回答評価の入力に加える。`career-private/fit/{企業スラッグ}/fit_assessment.json` がある場合は、想定質問の生成の入力に加え、`condition_fit` の `met: "unknown"` の項目と `overall.open_questions` を、逆質問・確認事項の質問素材として用いる。`companies/{企業スラッグ}/exam_assessment.json` がある場合は、特定された検査種別と選考の段取りを読み、面接が選考のどの段階にあたるかを判断する前提として用いる（任意入力。無くても進める）。

2. **回答評価はアンカーで固定する。** 回答評価は STAR・具体性・一貫性・企業理解の4観点で行い、各観点を3段階（充足・一部・不足）で判定する。判定基準（アンカー）の原本は `references/evaluation-rubric.md` にあり、job-change-interview-coach の判定定義と一致させる。評価は原本のアンカーに従い、甘くも辛くもしない。一貫性観点の根拠参照先には、profile.json の `job_change_axis` に加え、self_analysis.json がある場合はその `career_narrative`（一貫する動機）と `reason_for_change`（建設的な言い換えと `job_change_axis.reasons` との整合の説明）を含める。

3. **個人情報を外部へ送信しない。** `profile.json` に含まれる個人情報（氏名・現年収・希望年収・居住地・学歴・在籍企業名・実績など）は、検索クエリ・fetch・外部 API を含む一切の外部送信に用いない。本スキルの allowed-tools と job-change-interview-coach の tools はいずれも Web 送信手段（WebSearch・WebFetch）を含まないため、profile.json はそのまま渡してよい。Web 送信を伴う作業へ profile.json を渡さない。

4. **エージェントの model は固定である。** job-change-interview-coach の model は当該エージェントの frontmatter に opus で固定済みである。起動時に model を上書きしない。

## 範囲外

- **企業研究そのもの。** 企業の事業・財務・評判・選考プロセスの調査は `job-change-company-research` が担う。本スキルは調査済みの company_research.json を入力として用いる。
- **応募書類の作成。** 職務経歴書・履歴書・志望動機書の起草は `job-change-documents` が担う。
- **筆記試験・適性検査の対策。** SPI・玉手箱・オンラインアセスメント等の対策は `job-change-exam-prep` が担う。オンライン録画面接（HireVue 等）で問われる質問への回答準備は本スキルで扱うが、ゲーム型アセスメントの対策は扱わない。
- **面接日程の調整・応募先への送信。** 面接の日程調整、企業への返信・送信は行わない。想定問答と回答の改善までを支援し、送信は利用者本人が行う。
- **合否の予測。** 面接の合否や採用可能性を確率で予測しない。回答の観点別評価と改善提案までにとどめる。

## パスの解決

利用者データの置き場所は設定ファイルだけが決める。既定の置き場所を持たない。本文で `{DATA_ROOT}` と書いた箇所は、設定ファイルの `data_root` に読み替える。

hub（job-change-support）から振り分けられた場合は、hub が解決済みの `{DATA_ROOT}` を渡す。単独で起動された場合は、次の順に設定ファイルを探し、最初に見つかったものを Read で読む。

1. 環境変数 `JOB_CHANGE_CONFIG` が指すファイル
2. カレントディレクトリから上位へたどった最初の `.job-change/config.json`
3. `~/.job-change/config.json`

いずれの場所にも設定ファイルが無ければ未設定である。その場合は作業へ進まず、Skill ツールで `job-change-support` を起動して設定を作らせ、`{DATA_ROOT}` を解決してから戻る。

`{SKILL_DIR}` は本スキルの絶対パス、`{HUB_SKILL_DIR}` は同じ配置先にある `job-change-support` の絶対パスを指す。設定ファイルの仕様は `docs/configuration.md` にある。

## 中間成果物

パイプラインの各段で次を生成する。企業を特定して進める場合（company モード）は `{DATA_ROOT}/companies/{企業スラッグ}/` 配下へ保存する。企業非依存の縮退モードでは企業スラッグが無いため、成果物は会話上で提示し、利用者が保存先を指定した場合のみ書き出す。

| ファイル | 内容 | 生成する Step |
|---|---|---|
| `interview_questions.json` | 質問類型ごとの想定質問（job-change-interview-coach の Step 1 出力形式。`questions` 配列） | Step 1 |
| `interview_answers.json` | 質問と回答の対（Step 2 の逐次保存。中断からの再開に使う） | Step 2 |
| `interview_evaluation.json` | 収集した回答と、4観点の評価（job-change-interview-coach の Step 3 出力形式。`evaluations` 配列） | Step 3 |
| `interview-prep-report.md` | 観点別の強み・優先改善点・再演習の提案 | Step 4 |

`interview_questions.json` と `interview_evaluation.json` の形式は job-change-interview-coach の出力 JSON（Step 1・Step 3）にそのまま従う。

## パイプライン

Step 0〜4 を順に進める。`{HUB_SKILL_DIR}` は転職支援 hub（job-change-support）の絶対パスに読み替える。

### Step 0 読込とゲート

1. `{DATA_ROOT}/career-private/profile.json` の所在を Read / Glob で確認する。無ければ hub（job-change-support）へ戻し、プロファイルの初回作成を先行させる。
2. プロファイルゲート（必須）を通す。profile.json は `validate_profile.py`（job-change-support の scripts）が PASS（ERROR 0件）であることを前提とする。hub 経由で本スキルへ入る場合、hub がルーティング前に PASS を確認済みである。単独で起動された場合は、本スキルが自分で `validate_profile.py` を実行して PASS を確かめる。FAIL の場合は ERROR の内容を利用者へ示し、`job-change-profile` での整備を勧める。ただし、利用者が欠落を承知のうえで着手を希望する場合は、欠けた項目の値を直接引用または前提とする質問を作らず、その項目を根拠とする評価も行わないという条件で進めてよい。その場合は、どの項目が欠けたままかを報告に明記する。
3. 対象企業の企業スラッグを `career-private/company_index.json` で解決したうえで（詳細は job-change-support の `references/company-index-format.md`）、company_research.json（`companies/{企業スラッグ}/company_research.json`）の有無を確認する。同フォルダーに `interview_answers.json` が存在する場合は、残りの質問からの再開を利用者へ提案する。company_research.json が無い場合は、AskUserQuestion で次を利用者へ明示して選ばせる。
   - (A) 企業研究を先に実施する。hub へ戻して `job-change-company-research` を起動し、company_research.json を得てから本スキルへ戻る。
   - (B) 縮退モードを選ぶ。企業非依存の一般対策として進め、以降は企業固有の想定質問を生成せず、企業理解観点の評価も対象外とする。
4. `career-private/self_analysis.json` の有無を確認する。あれば Step 1・Step 3 の入力に加える。無くても進行できるが、自己分析（`job-change-self-analysis`）を先に実行すればキャリア・ナラティブと転職理由の建設的な言語化を一貫性観点の根拠に使えることを、利用者へ明示する。
5. `career-private/fit/{企業スラッグ}/fit_assessment.json` の有無を確認する。あれば Step 1 の入力に加える。想定質問の生成時に、`condition_fit` の `met: "unknown"` の項目と `overall.open_questions` を、逆質問・確認事項の質問素材として用いる。無くても進行できる。fit_assessment.json は career-private 配下の成果物であり、Web ツール保持エージェントへは渡さない。
6. 個人情報の取り扱いルールを確認する。profile.json の内容を外部送信に用いない。本スキルと job-change-interview-coach はいずれも Web 送信手段を持たないため、profile.json（あれば self_analysis.json・fit_assessment.json も）をそのまま渡してよい。

### Step 1 想定質問の生成

1. job-change-interview-coach（opus）を Agent ツールで起動し、Step 1 を指示する。指示書に次を渡す。
   - 実行するステップ = 1。
   - profile.json の絶対パス。company_research.json（あれば）・self_analysis.json（あれば）・fit_assessment.json（あれば）・exam_assessment.json（あれば）・求人票（あれば）の絶対パス。
2. コーチは質問類型ごとに想定質問を生成し、各質問に interviewer_intent（面接官の評価観点）と basis（company_research の claim id または profile の該当箇所）を付して返す。縮退モードでは degraded: true とし、企業固有の claim を根拠に用いる質問は生成しない。company_research.json はあるが topic=selection_process の claims が0件の場合は、その旨を指示書に明記し、選考プロセスを前提とする質問を生成させない（部分縮退）。`fit_assessment.json` がある場合、`condition_fit` の `met: "unknown"` の項目と `overall.open_questions` を、逆質問・確認事項の質問素材として加える。無い場合は company_research.json・profile.json のみを素材とする。
3. コーチが返した `questions` 配列を `interview_questions.json` として保存する（company モード時）。質問類型・評価観点・外資系の質問形式の原本は、それぞれ `references/question-bank.md`・`references/evaluation-rubric.md`・`references/foreign-interviews.md` にある。

### Step 2 模擬面接

1. 本スキル（オーケストレーター）が、生成した想定質問を1問ずつ提示する。利用者の回答をテキストで収集し、回答ごとに次の質問へ進む。
2. 全問を課す必要はない。利用者が指定した範囲（質問類型・問数）で実施してよい。回答を受け取るごとに、提示した質問と利用者の回答の対を `companies/{企業スラッグ}/interview_answers.json` へ追記保存する（縮退モードでは企業スラッグが無いため会話上に保持する）。
3. この段では評価・添削・言い換えをしない（評価は Step 3）。回答を誘導しない。

### Step 3 回答の評価とフィードバック

1. job-change-interview-coach（opus）を Agent ツールで起動し、Step 3 を指示する。指示書に次を渡す。
   - 実行するステップ = 3。
   - profile.json の絶対パス。company_research.json（あれば）・self_analysis.json（あれば）の絶対パス。
   - 評価対象の質問一覧と回答（company モード時は `interview_answers.json` から読み込む。縮退モードでは会話上に保持した対を用いる）。
2. コーチは各回答を STAR（scores.star）・具体性（scores.specificity）・一貫性（scores.consistency）・企業理解（scores.company_fit）の4観点について、3段階（充足・一部・不足）で評価し、feedback と improvement に根拠参照（profile の該当箇所、self_analysis.json の narrative・reason_for_change、または claim id）を付して返す。縮退モードでは企業理解観点を対象外とし、degraded: true とする。
3. 評価アンカーの原本は `references/evaluation-rubric.md`（コーチの判定定義と一致）である。コーチが返した `evaluations` を、収集した回答とともに `interview_evaluation.json` として保存する（company モード時）。

### Step 4 総括

1. 全評価を観点別に集計し、強み（充足の多い観点）と優先改善点（不足の観点と、その具体的な補い方）を整理する。改善案は `references/evaluation-rubric.md` のアンカーに沿い、STAR の欠落要素の補い方や、企業理解の反映方法を含める。
2. 再演習の提案（評価の弱い観点・質問類型に絞った再度の模擬面接）を添える。
3. 観点別の強み・優先改善点・再演習の提案を `interview-prep-report.md` にまとめる（company モード時は company フォルダーへ保存する）。総括の判断・改善案は評価アンカーと根拠参照に基づき、profile.json・company_research.json に無い事実を前提に置かない。

## 合否ゲートと差し戻し

パイプラインには2つのゲートがある。

- Step 0 のプロファイルゲート（必須）では、`validate_profile.py` が PASS でなければ Step 1 へ進まない。profile.json が未作成、または FAIL（ERROR 1件以上）の場合は、hub（job-change-support）でのプロファイル整備を先行させ、PASS を確認してから戻る。
- コーチ出力ゲート（Step 1・Step 3）では、job-change-interview-coach の返す JSON が次を満たすことを確認する。満たさない場合は、不足内容を指示書へ添えてコーチを再起動する。
  - `{"error": ...}` でない（入力の欠落による返答でない）。
  - スキーマに適合する（Step 1 は `questions`、Step 3 は `evaluations`）。
  - `degraded` と `degraded_reason` が company_research.json の有無と整合する（company_research.json が無い場合は degraded: true）。company_research.json があり topic=selection_process の claims が0件の場合も degraded: true とし、`degraded_reason` に選考プロセスの claims が0件である旨を書く。
  - Step 3 の `scores` の各値が「充足」「一部」「不足」のいずれかである。
  - Step 3 の `feedback` と `improvement` に根拠参照（profile の該当箇所、self_analysis.json の narrative・reason_for_change、または claim id）を含む。

差し戻しは同一ステップにつき最大2回とする。2回で解消しない場合は、当該の質問または評価を未決事項として利用者へ提示し、判断を委ねてから次へ進む。

## 役割の実行（ハーネス別）

本スキルのパイプラインは、専門の役割へ作業を委ねる形で書いてある。役割の内容は `references/roles/` に置き、これを原本とする。

| エージェント名 | 役割プロンプトの原本 |
|---|---|
| `job-change-interview-coach` | `{SKILL_DIR}/references/roles/interview-coach.md` |

**サブエージェントを起動できるハーネス（Claude Code）。** 各 Step の記述どおり、上表のエージェント名を Agent ツールで起動し、指示書を渡す。エージェント定義はリポジトリの `agents/` にあり、`references/roles/` から同期生成されている。

**サブエージェントを起動できないハーネス（Codex ほか）。** 各 Step の「エージェントを起動する」を「役割プロンプトを読み、その役割として自分で実行する」と読み替える。手順は次のとおり。

1. 上表の役割プロンプトを Read で読む。
2. Step に書かれた指示書の項目を、そのまま自分への指示として扱う。
3. 役割プロンプトの「扱ってよい入力」のルールを守る。Web 送信手段を持たない役割として書かれている場合、その作業中は Web 検索・fetch を使わない。
4. 成果物の形式・検証・合否ゲートは、ハーネスによらず同一である。

## エージェントのモデル方針

| エージェント | model | 責務 |
|---|---|---|
| `job-change-interview-coach` | opus | Step 1: 質問類型ごとの想定質問生成 ／ Step 3: 回答の4観点評価とフィードバック |

model はエージェントの frontmatter に固定済みであり、起動時に上書きしない。

## スクリプトのCLI使用例

本スキルは検証スクリプトを持たない。Step 0 のプロファイルゲートは、hub（job-change-support）の `validate_profile.py` の PASS を前提とする。次のコマンドはhub がルーティング前に実行するものであり、本スキルは Bash を持たないため自ら実行しない（掲載は前提確認のため）。`{HUB_SKILL_DIR}` は hub スキルの絶対パスに読み替える。

```bash
python {HUB_SKILL_DIR}/scripts/validate_profile.py {DATA_ROOT}/career-private/profile.json --json
```

終了コードは PASS で 0、FAIL で 1（WARN のみは PASS 扱い）である。仕様と検証規則の原本は job-change-support の `references/profile-format.md` にある。

## references 一覧

| ファイル | 何を | いつ読むか |
|---|---|---|
| `references/question-bank.md` | 頻出質問の質問類型・面接官の評価観点・答え方の原則・逆質問の NG（出典付き） | Step 1 の想定質問生成、Step 2 の進行 |
| `references/evaluation-rubric.md` | 4観点（STAR・具体性・一貫性・企業理解）と3段階のアンカー、良い回答の要素、学術的根拠（DOI 付き） | Step 3 の評価、Step 4 の総括 |
| `references/foreign-interviews.md` | 外資系のビヘイビアラル/コンピテンシー面接・ケース面接の進め方と評価観点（出典付き） | 外資系選考の Step 1・Step 2・Step 3 |
