---
name: job-change-interview-prep
description: >-
  転職の面接対策を担うサブスキル。profile.json と（あれば）company_research.json を入力に、
  job-change-interview-coach（opus）で企業固有の想定質問を質問類型ごとに生成し、模擬面接で回答を
  1問ずつ収集し、STAR・具体性・一貫性・企業理解の4観点でフィードバックし、観点別の強みと優先改善点を
  総括する。company_research.json が無ければ企業非依存の一般対策へフォールバックする。日本の中途採用面接を中心に、
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

1. **企業固有の質問は company_research.json の claim を根拠とする。** 企業固有の想定質問は、対象企業の企業研究結果（company_research.json）の claims、特に topic=selection_process（選考プロセス・面接体験記）と topic=philosophy（理念）を根拠とする。company_research.json が無い場合は企業固有の質問を生成せず、企業非依存の一般対策へフォールバックする（フォールバックモード）。company_research.json があっても topic=selection_process の claims が0件の場合は、選考プロセスを前提とする質問（面接の回数・形式・各段階の評価観点を既知として扱う質問）を生成しない。この場合は topic=philosophy の claims だけを根拠に企業固有の質問を作り、選考プロセスの claims が0件である旨を利用者へ伝える（部分的なフォールバック）。claims が0件であることを、選考が単純であることの根拠にしない。`career-private/self_analysis.json` がある場合は、想定質問の生成と回答評価の入力に加える。`career-private/fit/{企業スラッグ}/fit_assessment.json` がある場合は、想定質問の生成の入力に加え、`condition_fit` の `met: "unknown"` の項目と `overall.open_questions` を、逆質問・確認事項の質問素材として用いる。`companies/{企業スラッグ}/exam_assessment.json` がある場合は、特定された検査種別と選考の段取りを読み、面接が選考のどの段階にあたるかを判断する前提として用いる（任意入力。無くても進める）。

2. **回答評価はアンカーで固定する。** 回答評価は STAR・具体性・一貫性・企業理解の4観点で行い、各観点を3段階（充足・一部・不足）で判定する。判定基準（アンカー）の原本は `references/evaluation-rubric.md` にあり、job-change-interview-coach は Step 3 でこのファイルを読んで判定する。評価は原本のアンカーに従い、甘くも辛くもしない。一貫性の観点で根拠として参照する先には、profile.json の `job_change_axis` に加え、self_analysis.json がある場合はその `career_narrative`（一貫する動機）と `reason_for_change`（建設的な言い換えと `job_change_axis.reasons` との整合の説明）を含める。

3. **個人情報を外部へ送信しない。** 利用者の個人情報は、検索クエリ・fetch・外部 API を含む一切の外部送信に用いない。対象の列挙と役割ごとの可否の原本は hub の `{HUB_SKILL_DIR}/references/pii-boundary.md` にある。本スキルの allowed-tools と job-change-interview-coach の tools はいずれも Web 送信手段（WebSearch・WebFetch）を含まないため、profile.json はそのまま渡してよい。Web 送信を伴う作業へ profile.json を渡さない。

4. **エージェントの model は固定である。** job-change-interview-coach の model は当該エージェントの frontmatter に opus で固定済みである。起動時に model を上書きしない。

## 範囲外

- **企業研究そのもの。** 企業の事業・財務・評判・選考プロセスの調査は `job-change-company-research` が担う。本スキルは調査済みの company_research.json を入力として用いる。
- **応募書類の作成。** 職務経歴書・履歴書・志望動機書の作成は `job-change-documents` が担う。
- **筆記試験・適性検査の対策。** SPI・玉手箱・オンラインアセスメント等の対策は `job-change-exam-prep` が担う。オンライン録画面接（HireVue 等）で問われる質問への回答準備は本スキルで扱うが、ゲーム型アセスメントの対策は扱わない。
- **面接日程の調整・応募先への送信。** 面接の日程調整、企業への返信・送信は行わない。想定問答と回答の改善までを支援し、送信は利用者本人が行う。
- **合否の予測。** 面接の合否や採用可能性を確率で予測しない。回答の観点別評価と改善提案までにとどめる。

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

## 中間成果物

パイプラインの各段階で次を生成する。企業を特定して進める場合（company モード）は `{DATA_ROOT}/companies/{企業スラッグ}/` 配下へ保存する。企業非依存のフォールバックモードでは企業スラッグが無いため、成果物は会話上で提示し、利用者が保存先を指定した場合のみ書き出す。`interview_answers.json` と `interview_evaluation.json` は利用者の回答をそのまま含むため個人情報であるが、本スキルと job-change-interview-coach はいずれも Web 送信手段を持たず、これらを読む役割も本スキルの外には無いため、他の成果物と同じ配置先に置く。

| ファイル | 内容 | 生成する Step |
|---|---|---|
| `interview_questions.json` | 質問類型ごとの想定質問（job-change-interview-coach の Step 1 出力 JSON をトップレベルごと保存する） | Step 1 |
| `interview_answers.json` | 質問 id と回答の対（Step 2 の逐次保存。中断からの再開に使う） | Step 2 |
| `interview_evaluation.json` | 4観点の評価（job-change-interview-coach の Step 3 出力 JSON をトップレベルごと保存する） | Step 3 |
| `interview-prep-report.md` | 観点別の強み・優先改善点・再演習の提案 | Step 4 |

上の3つの JSON の形式の原本は `references/interview-format.md` にある。`interview_questions.json` と `interview_evaluation.json` は job-change-interview-coach の出力 JSON（Step 1・Step 3）にそのまま従い、`degraded`・`degraded_reason` を含むトップレベルごと保存する。`questions`・`evaluations` の配列だけを取り出して保存しない。`degraded` が落ちると、その質問群が企業固有のものか企業非依存のフォールバックかをファイルから判別できず、中断からの再開時に合否ゲートを再確認できないためである。

## パイプライン

Step 0〜4 を順に進める。`{HUB_SKILL_DIR}` は転職支援 hub（job-change-support）の絶対パスに読み替える。

### Step 0 読込とゲート

1. `{DATA_ROOT}/career-private/profile.json` の所在を Read / Glob で確認する。無ければ hub（job-change-support）へ戻し、プロファイルの初回作成を先行させる。
2. プロファイルゲート（必須）を通す。profile.json は `validate_profile.py`（job-change-support の scripts）が PASS（ERROR 0件）であることを前提とする。hub 経由で本スキルへ入る場合、hub がルーティング前に PASS を確認済みである。単独で起動された場合は、本スキルが自分で `validate_profile.py` を実行して PASS を確かめる。FAIL の場合は ERROR の内容を利用者へ示し、`job-change-profile` での整備を勧める。ただし、利用者が欠落を承知のうえで着手を希望する場合は、欠けた項目の値を直接引用または前提とする質問を作らず、その項目を根拠とする評価も行わないという条件で進めてよい。その場合は、どの項目が欠けたままかを報告に明記する。hub から振り分けられ、hub が既にこの選択を利用者へ求めている場合は、再度問わずにその選択に従う。hub と本スキルが同じ選択を2回求めないためである。
3. 企業スラッグの解決に入る前に、`validate_company_index.py`（job-change-support の scripts）で一覧を検証する。FAIL（ERROR 1件以上）なら指摘内容を利用者へ示し、修復されるまで解決へ進まない。
4. 対象企業の企業スラッグを `career-private/company_index.json` で解決したうえで（詳細は job-change-support の `references/company-index-format.md`）、company_research.json（`companies/{企業スラッグ}/company_research.json`）の有無を確認する。同フォルダーに `interview_answers.json` が存在する場合は、`interview_questions.json` の `questions[].id` の集合から `interview_answers.json` の `answers[].question_id` の集合を差し引き、残った id の質問を「残りの質問」として提示し、そこからの再開を利用者へ提案する。差分は会話の記憶ではなくこの2ファイルだけで決める。`interview_questions.json` が無い場合は再開できないため、Step 1 からやり直す。company_research.json が無い場合は、AskUserQuestion で次を利用者へ明示して選ばせる。
   - (A) 企業研究を先に実施する。hub へ戻して `job-change-company-research` を起動し、company_research.json を得てから本スキルへ戻る。
   - (B) フォールバックモードを選ぶ。企業非依存の一般対策として進め、以降は企業固有の想定質問を生成せず、企業理解の観点による評価も対象外とする。
5. company_research.json がある場合は、`check_freshness.py`（job-change-support の scripts）で当該企業の `_manifest.json` を判定する。`stale` のトピックがあれば、その旨と対象トピック名を利用者へ示し、`job-change-company-research` での差分再調査を提案する。利用者が再調査せずに進むことを選んだ場合は、古い情報に基づく旨と対象トピック名を Step 4 の `interview-prep-report.md` へ明記して進む。判定規則と TTL の原本は job-change-support の `references/freshness-policy.md` にある。
6. `career-private/self_analysis.json` の有無を確認する。あれば Step 1・Step 3 の入力に加える。無くても進行できるが、自己分析（`job-change-self-analysis`）を先に実行すればキャリア・ナラティブと転職理由の建設的な言語化を一貫性の観点の根拠に使えることを、利用者へ明示する。
7. `career-private/fit/{企業スラッグ}/fit_assessment.json` の有無を確認する。あれば Step 1 の入力に加える。想定質問の生成時に、`condition_fit` の `met: "unknown"` の項目と `overall.open_questions` を、逆質問・確認事項の質問素材として用いる。無くても進行できる。fit_assessment.json は career-private 配下の成果物であり、Web ツールを持つエージェントへは渡さない。
8. 個人情報の取り扱いルールを確認する。profile.json の内容を外部送信に用いない。本スキルと job-change-interview-coach はいずれも Web 送信手段を持たないため、profile.json（あれば self_analysis.json・fit_assessment.json も）をそのまま渡してよい。

### Step 1 想定質問の生成

1. job-change-interview-coach（opus）を Agent ツールで起動し、Step 1 を指示する。指示書に次を渡す。
   - 実行するステップ = 1。
   - profile.json の絶対パス。company_research.json（あれば）・self_analysis.json（あれば）・fit_assessment.json（あれば）・exam_assessment.json（あれば）・求人票（あれば）の絶対パス。
   - 本スキルの絶対パス（`{SKILL_DIR}`）。出力形式の原本 `references/interview-format.md` の所在として渡す。
2. コーチは質問類型ごとに想定質問を生成し、各質問に interviewer_intent（面接官の評価観点）と basis（company_research の claim id または profile の該当箇所）を付して返す。フォールバックモードでは degraded: true とし、企業固有の claim を根拠に用いる質問は生成しない。company_research.json はあるが topic=selection_process の claims が0件の場合は、その旨を指示書に明記し、選考プロセスを前提とする質問を生成させない（部分的なフォールバック）。`fit_assessment.json` がある場合、`condition_fit` の `met: "unknown"` の項目と `overall.open_questions` を、逆質問・確認事項の質問素材として加える。無い場合は company_research.json・profile.json のみを素材とする。
3. コーチが返した JSON を、`degraded`・`degraded_reason` を含むトップレベルごと `interview_questions.json` として保存する（company モード時）。`questions` 配列だけを取り出さない。形式の原本は `references/interview-format.md` にある。質問類型・評価観点・外資系の質問形式の原本は、それぞれ `references/question-bank.md`・`references/evaluation-rubric.md`・`references/foreign-interviews.md` にある。
4. 保存した `interview_questions.json` を `validate_interview_artifacts.py` で検証する（company モード時。ゲート）。FAIL（ERROR 1件以上）なら Step 2 へ進まず、ERROR の内容を指示書へ添えてコーチを再起動する。

### Step 2 模擬面接

1. 本スキル（オーケストレーター）が、生成した想定質問を1問ずつ提示する。利用者の回答をテキストで収集し、回答ごとに次の質問へ進む。
2. 全問を課す必要はない。利用者が指定した範囲（質問類型・問数）で実施してよい。回答を受け取るごとに、`{"question_id": …, "answer": …, "answered_at": …}` の1件を `companies/{企業スラッグ}/interview_answers.json` の `answers` 配列へ追記保存する（フォールバックモードでは企業スラッグが無いため会話上に保持する）。`question_id` には、提示した質問の `interview_questions.json` での `id` をそのまま書く。`answer` には利用者の回答をそのまま写し、要約・言い換えをしない。形式の原本は `references/interview-format.md` にある。
3. この段階では評価・添削・言い換えをしない（評価は Step 3）。回答を誘導しない。
4. Step 3 へ進む前に、`interview_answers.json` を `validate_interview_artifacts.py` で検証する（company モード時。ゲート）。`--questions` に `interview_questions.json` を渡し、`question_id` が質問側に実在することを確かめる。FAIL なら ERROR を解消してから Step 3 へ進む。

### Step 3 回答の評価とフィードバック

1. job-change-interview-coach（opus）を Agent ツールで起動し、Step 3 を指示する。指示書に次を渡す。
   - 実行するステップ = 3。
   - profile.json の絶対パス。company_research.json（あれば）・self_analysis.json（あれば）の絶対パス。
   - 本スキルの絶対パス（`{SKILL_DIR}`）。出力形式の原本 `references/interview-format.md` の所在として渡す。
   - 評価対象の質問一覧と回答（company モード時は `interview_answers.json` から読み込む。フォールバックモードでは会話上に保持した対を用いる）。
2. コーチは各回答を STAR（scores.star）・具体性（scores.specificity）・一貫性（scores.consistency）・企業理解（scores.company_fit）の4観点について、3段階（充足・一部・不足）で評価し、feedback と improvement に根拠参照（profile の該当箇所、self_analysis.json の narrative・reason_for_change、または claim id）を付して返す。フォールバックモードでは企業理解の観点を対象外とし、degraded: true とする。
3. 評価アンカーの原本は `references/evaluation-rubric.md`（コーチの判定定義と一致）である。コーチが返した JSON を、`degraded`・`degraded_reason` を含むトップレベルごと `interview_evaluation.json` として保存する（company モード時）。`evaluations` 配列だけを取り出さない。回答そのものは `interview_answers.json` に残っており、`question_id` で対応が付く。形式の原本は `references/interview-format.md` にある。
4. 保存した `interview_evaluation.json` を `validate_interview_artifacts.py` で検証する（company モード時。ゲート）。`--questions` に `interview_questions.json` を渡す。FAIL なら Step 4 へ進まず、ERROR の内容を指示書へ添えてコーチを再起動する。

### Step 4 総括

1. 全評価を観点別に集計し、強み（充足の多い観点）と優先改善点（不足の観点と、その具体的な補い方）を整理する。改善案は `references/evaluation-rubric.md` のアンカーに沿い、STAR の欠落要素の補い方や、企業理解の反映方法を含める。
2. 再演習の提案（評価の弱い観点・質問類型に絞った再度の模擬面接）を添える。
3. 観点別の強み・優先改善点・再演習の提案を `interview-prep-report.md` にまとめる（company モード時は company フォルダーへ保存する）。総括の判断・改善案は評価アンカーと根拠参照に基づき、profile.json・company_research.json に無い事実を前提に置かない。
4. 報告書と最終メッセージはいずれも結論から述べる。中身の無い節・同じ内容の繰り返し・定型の前置きを置かない。

## 合否ゲートと差し戻し

パイプラインには3つのゲートがある。

- Step 0 のプロファイルゲート（必須）では、`validate_profile.py` が PASS でなければ Step 1 へ進まない。profile.json が未作成、または FAIL（ERROR 1件以上）の場合は、hub（job-change-support）でのプロファイル整備を先行させ、PASS を確認してから戻る。ただし FAIL の場合は、ERROR の内容を示し、利用者が欠落を承知で着手を希望するなら、欠けた項目の値を直接引用または前提とする質問を作らず、その項目を根拠とする評価も行わないという条件で進めてよい。どの項目が欠けたままかを報告に明記する。hub が既にこの選択を利用者へ求めている場合は、再度問わずにその選択に従う。
- コーチ出力ゲート（Step 1・Step 3）では、job-change-interview-coach の返す JSON が次を満たすことを確認する。満たさない場合は、不足内容を指示書へ添えてコーチを再起動する。
  - `{"error": ...}` でない（入力の欠落による返答でない）。
  - スキーマに適合する（Step 1 は `questions`、Step 3 は `evaluations`）。
  - `degraded` と `degraded_reason` が company_research.json の有無と整合する（company_research.json が無い場合は degraded: true）。company_research.json があり topic=selection_process の claims が0件の場合も degraded: true とし、`degraded_reason` に選考プロセスの claims が0件である旨を書く。
  - Step 3 の `scores` の各値が「充足」「一部」「不足」のいずれかである。
  - Step 3 の `feedback` と `improvement` に根拠参照（profile の該当箇所、self_analysis.json の narrative・reason_for_change、または claim id）を含む。
- 成果物ゲート（Step 1・Step 2・Step 3、company モード時）では、保存した `interview_questions.json`・`interview_answers.json`・`interview_evaluation.json` を `validate_interview_artifacts.py` が PASS（ERROR 0件）とすることを確認する。FAIL なら次の Step へ進まない。この検証スクリプトは形式・`degraded` の整合・`question_id` の相互参照だけを見て、質問や評価の内容の当否は見ない。フォールバックモードでは成果物をファイルへ書き出さない場合があり、そのときはこのゲートを適用しない。

差し戻しは同一ステップにつき最大2回とする。2回で解消しない場合は、当該の質問または評価を未決事項として利用者へ提示し、判断を委ねてから次へ進む。

## 役割の実行（ハーネス別）

本スキルのパイプラインは、専門の役割へ作業を委ねる形で書いてある。役割の内容は `references/roles/` に置き、これを原本とする。

| エージェント名 | 役割プロンプトの原本 |
|---|---|
| `job-change-interview-coach` | `{SKILL_DIR}/references/roles/interview-coach.md` |

ハーネス別の実行手順と、起動する数の判断の原本は hub の `{HUB_SKILL_DIR}/references/role-execution.md` にある。

## エージェントのモデル方針

| エージェント | model | 責務 |
|---|---|---|
| `job-change-interview-coach` | opus | Step 1: 質問類型ごとの想定質問生成 ／ Step 3: 回答の4観点評価とフィードバック |

model はエージェントの frontmatter に固定済みであり、起動時に上書きしない。

## スクリプトのCLI使用例

本スキルの検証スクリプトは `validate_interview_artifacts.py` の1本である。Step 1・Step 2・Step 3 で保存した成果物を、それぞれ次のように検証する。検証対象の種別はトップレベルのキーから判別されるため、引数で指定しない。

```bash
python {SKILL_DIR}/scripts/validate_interview_artifacts.py {DATA_ROOT}/companies/{企業スラッグ}/interview_questions.json
python {SKILL_DIR}/scripts/validate_interview_artifacts.py {DATA_ROOT}/companies/{企業スラッグ}/interview_answers.json --questions {DATA_ROOT}/companies/{企業スラッグ}/interview_questions.json
python {SKILL_DIR}/scripts/validate_interview_artifacts.py {DATA_ROOT}/companies/{企業スラッグ}/interview_evaluation.json --questions {DATA_ROOT}/companies/{企業スラッグ}/interview_questions.json --json
```

Step 0 で用いる3本はいずれも hub（job-change-support）のスクリプトであり、hub 経由で入る場合は hub がルーティング前に実行済みである。単独で起動された場合は本スキルが次を実行する。`{HUB_SKILL_DIR}` は hub スキルの絶対パスに読み替える。

```bash
python {HUB_SKILL_DIR}/scripts/validate_profile.py {DATA_ROOT}/career-private/profile.json --json
python {HUB_SKILL_DIR}/scripts/validate_company_index.py {DATA_ROOT}/career-private/company_index.json
python {HUB_SKILL_DIR}/scripts/check_freshness.py {DATA_ROOT}/companies/{企業スラッグ}/_manifest.json
```

`validate_interview_artifacts.py`・`validate_profile.py`・`validate_company_index.py` の終了コードは PASS で 0、FAIL で 1（WARN のみは PASS 扱い）である。`check_freshness.py` は常に終了コード 0 を返し、`fresh`・`stale`・`missing` の分類を出力する。profile.json の仕様と検証規則の原本は job-change-support の `references/profile-format.md` にある。

## references 一覧

| ファイル | 何を | いつ読むか |
|---|---|---|
| `references/interview-format.md` | 3つの成果物（`interview_questions.json`・`interview_answers.json`・`interview_evaluation.json`）のフィールド仕様・記入基準・機械的な検証の規則 | Step 1〜Step 3 の保存と検証 |
| `references/question-bank.md` | 頻出質問の質問類型・面接官の評価観点・答え方の原則・逆質問の NG（出典付き） | Step 1 の想定質問生成、Step 2 の進行 |
| `references/evaluation-rubric.md` | 4観点（STAR・具体性・一貫性・企業理解）と3段階のアンカー、良い回答の要素、学術的根拠（DOI 付き） | Step 3 の評価、Step 4 の総括 |
| `references/foreign-interviews.md` | 外資系のビヘイビアラル/コンピテンシー面接・ケース面接の進め方と評価観点（出典付き） | 外資系選考の Step 1・Step 2・Step 3 |
