---
name: job-change-interview-prep
description: >-
  転職の面接対策を担うサブスキル。job-change-interview-scout（sonnet）で対象企業の面接について口コミ・採用ページを
  調べて interview_intel.json を作り、profile.json と（あれば）company_research.json・interview_intel.json を入力に、
  job-change-interview-coach（opus）で企業固有の想定質問を質問類型ごとに生成し、模擬面接で回答を
  1問ずつ収集し、STAR・具体性・一貫性・企業理解の4観点でフィードバックし、観点別の強みと優先改善点を
  総括する。company_research.json も interview_intel.json も無ければ企業非依存の一般対策へフォールバックする。
  日本の中途採用面接を中心に、カジュアル面談と外資系のビヘイビアラル面接・ケース面接へ対応する。
  profile.json の個人情報は外部送信に用いない。
  Use when the user prepares for a job-change interview in Japan (including foreign-affiliated company
  selection) — researching what a company asks in interviews, generating expected questions, running a
  mock interview, getting answer feedback, or practicing behavioral / case interviews.
  trigger words: 面接対策, 想定問答, 想定質問, 逆質問, 行動面接, ビヘイビアラル面接, ケース面接, 模擬面接, カジュアル面談, 面接で聞かれること。
allowed-tools: Read, Write, Glob, Grep, Bash, Agent, AskUserQuestion, Skill
---

# job-change-interview-prep

転職の面接対策を行うとき、本スキルが想定質問の生成・模擬面接・回答評価・総括までの手順を定める。転職支援 hub（job-change-support）の面接対策として振り分けられて起動される。対象は日本の中途採用面接を中心とし、外資系のビヘイビアラル面接・ケース面接へ対応する。

対象企業の面接についての調査（Step 0.9）は専用エージェント job-change-interview-scout（sonnet）が、想定質問の生成（Step 1）と回答の評価（Step 3）は専用エージェント job-change-interview-coach（opus）が担う。本スキルはその起動、模擬面接の進行、総括を担う。

## 目的と原則

1. **企業固有の質問は company_research.json の claim と interview_intel.json を根拠とする。** 企業固有の想定質問は、対象企業の企業研究結果（company_research.json）の claims と、面接情報の調査結果（interview_intel.json）を根拠とする。前者では特に topic=selection_process（選考プロセス・面接体験記）と topic=philosophy（理念）の claims を、後者では報告された質問（`reported_questions`）・面接の形式（`format_facts`）・口コミの傾向（`themes`）を用いる。想定質問には出所（`provenance`: `general`=一般・`reported`=報告・`inferred`=推測）を付け、報告された質問はその言い回しのまま、推測した質問は推測である旨を添えて示す。出所と根拠の信頼度は別のものであり、1つの確度にまとめない（原本は `references/question-bank.md` の「想定質問の出所と示し方」）。company_research.json も interview_intel.json も無い場合は企業固有の質問を生成せず、企業非依存の一般対策へフォールバックする（フォールバックモード）。company_research.json があっても topic=selection_process の claims が0件で、interview_intel.json の `format_facts` も無い場合は、選考プロセスを前提とする質問を生成しない。面接の回数・形式・各段階の評価観点を既知として扱う質問がこれにあたる。この場合は topic=philosophy の claims だけを根拠に企業固有の質問を作る。そのうえで、選考プロセスの根拠が無い旨を利用者へ伝える（部分的なフォールバック）。claims が0件であることを、選考が単純であることの根拠にしない。就職差別につながるおそれのある事項に当たる質問は、どの出所からも想定質問として生成しない（一覧の原本は `references/question-bank.md` の「聞かれても答えなくてよい事項」）。`career-private/self_analysis.json` がある場合は、想定質問の生成と回答評価の入力に加える。`career-private/fit/{企業スラッグ}/fit_assessment.json` がある場合は、想定質問の生成の入力に加える。その `condition_fit` の `met: "unknown"` の項目と `overall.open_questions` は、逆質問・確認事項の質問素材として用いる。`companies/{企業スラッグ}/exam_assessment.json` がある場合は、特定された検査種別と選考の段取りを読む。面接が選考のどの段階にあたるかを判断する前提として用いる（任意入力。無くても進める）。

2. **回答評価はアンカーで固定する。** 回答評価は STAR・具体性・一貫性・企業理解の4観点で行い、各観点を3段階（充足・一部・不足）で判定する。判定基準（アンカー）の原本は `references/evaluation-rubric.md` にある。job-change-interview-coach は Step 3 でこのファイルを読んで判定する。評価は原本のアンカーに従い、甘くも辛くもしない。一貫性の観点で根拠として参照する先には、profile.json の `job_change_axis` を含める。self_analysis.json がある場合は、その `career_narrative`（一貫する動機）と `reason_for_change`（建設的な言い換えと `job_change_axis.reasons` との整合の説明）も参照先へ加える。

3. **個人情報を外部へ送信しない。** 利用者の個人情報は、検索クエリ・fetch・外部 API を含む一切の外部送信に用いない。対象の列挙と役割ごとの可否の原本は hub の `{HUB_SKILL_DIR}/references/pii-boundary.md` にある。本スキルの allowed-tools と job-change-interview-coach の tools は、いずれも Web 送信手段（WebSearch・WebFetch）を含まない。このため profile.json はそのまま渡してよい。job-change-interview-scout は Web 送信手段を持つため、渡してよいのは企業名・職種名・求人URL・出力先パスと、`companies/{企業スラッグ}/` の `company_research.json`・`job_posting.json` のパスに限る。`career-private/` 配下と、`companies/{企業スラッグ}/` の `interview_answers.json`・`interview_evaluation.json`・`interview_notes_user.md` は渡さない。

4. **エージェントの model は固定である。** job-change-interview-coach の model は当該エージェントの frontmatter に opus で、job-change-interview-scout の model は sonnet で固定済みである。起動時に model を上書きしない。

5. **利用者が持つ情報を Web より先に使う。** 転職エージェントから受け取った質問一覧や、過去に同じ企業の選考を受けた経験は、Web で集められる口コミより新しく、その企業の選考に直接結び付く。Step 0 で有無を確かめ、あれば `interview_notes_user.md` に書き留めて想定質問の素材にする。このファイルは本人の選考の経緯を含むため、Web 送信手段を持つ役割へ渡さない。

## 範囲外

- **企業研究そのもの。** 企業の事業・財務・評判・選考プロセスの調査は `job-change-company-research` が担う。本スキルは調査済みの company_research.json を入力として用いる。
- **応募書類の作成。** 職務経歴書・履歴書・志望動機書の作成は `job-change-documents` が担う。
- **筆記試験・適性検査の対策。** SPI・玉手箱・オンラインアセスメント等の対策は `job-change-exam-prep` が担う。オンライン録画面接（HireVue 等）で問われる質問への回答準備は本スキルで扱うが、ゲーム型アセスメントの対策は扱わない。
- **面接日程の調整・応募先への送信。** 面接の日程調整、企業への返信・送信は行わない。想定問答と回答の改善までを支援し、送信は利用者本人が行う。
- **合否の予測。** 面接の合否や採用可能性を確率で予測しない。回答の観点別評価と改善提案までにとどめる。

## パスの解決

利用者データの置き場所は設定ファイルの記述だけで決まる。既定の置き場所は無い。本文で `{DATA_ROOT}` と書いた箇所は、次のコマンドが返す `data_root` に読み替える。

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

パイプラインの各段階で次を生成する。企業を特定して進める場合（company モード。企業スラッグが解決済み）は `{DATA_ROOT}/companies/{企業スラッグ}/` 配下へ保存する。対象企業を特定せずに起動された場合は企業スラッグが無いため、成果物は会話上で提示し、利用者が保存先を指定した場合のみ書き出す。フォールバックモード（企業固有の根拠が無い）は企業スラッグの有無とは別の区別であり、企業スラッグがあればフォールバックモードでも同じ配置先へ保存する。`interview_notes_user.md`・`interview_answers.json`・`interview_evaluation.json` は利用者の情報と回答をそのまま含み、`interview_questions.json`・`interview-prep-report.md` は profile と回答から導いた内容を含むため、いずれも個人情報である。ただし本スキルと job-change-interview-coach はいずれも Web 送信手段を持たない。これらを読む役割も本スキルの外には無く、Web 送信手段を持つ役割の役割プロンプトはこれらのファイルを読まないよう定めているため、他の成果物と同じ配置先に置く（境界の原本は `{HUB_SKILL_DIR}/references/pii-boundary.md`）。

| ファイル | 内容 | 生成する Step |
|---|---|---|
| `interview_notes_user.md` | 利用者が転職エージェントや過去の選考で得た、その企業の面接についての情報（利用者の言葉のまま） | Step 0 |
| `interview_intel.json` | 対象企業の面接について口コミ・採用ページから集めた、報告された質問・面接の形式・口コミの傾向（job-change-interview-scout の出力 JSON。非個人情報） | Step 0.9 |
| `interview_questions.json` | 質問類型ごとの想定質問（job-change-interview-coach の Step 1 出力 JSON をトップレベルごと保存する） | Step 1 |
| `interview_answers.json` | 質問 id と回答の対（Step 2 の逐次保存。中断からの再開に使う） | Step 2 |
| `interview_evaluation.json` | 4観点の評価（job-change-interview-coach の Step 3 出力 JSON をトップレベルごと保存する） | Step 3 |
| `interview-prep-report.md` | 観点別の強み・優先改善点・再演習の提案 | Step 4 |

`interview_questions.json`・`interview_answers.json`・`interview_evaluation.json` の形式の原本は `references/interview-format.md` に、`interview_intel.json` の形式の原本は `references/interview-intel-format.md` にある。`interview_questions.json` と `interview_evaluation.json` は job-change-interview-coach の出力 JSON（Step 1・Step 3）にそのまま従う。`degraded`・`degraded_reason` を含むトップレベルごと保存する。`questions`・`evaluations` の配列だけを抽出して保存しない。`degraded` が落ちると、その質問群が企業固有のものか企業非依存のフォールバックかをファイルから判別できず、中断からの再開時に合否ゲートを再確認できないためである。

## パイプライン

Step 0〜4 を順に進める。`{HUB_SKILL_DIR}` は転職支援 hub（job-change-support）の絶対パスに読み替える。

### Step 0 読込とゲート

1. `{DATA_ROOT}/career-private/profile.json` の所在を Read / Glob で確認する。無ければ hub（job-change-support）へ戻し、プロファイルの初回作成を先行させる。
2. プロファイルゲート（必須）を通す。profile.json は `validate_profile.py`（job-change-support の scripts）が PASS（ERROR 0件）であることを前提とする。hub 経由で本スキルへ入る場合、hub がルーティング前に PASS を確認済みである。単独で起動された場合は、本スキルが自分で `validate_profile.py` を実行して PASS を確かめる。FAIL の場合は ERROR の内容を利用者へ示し、`job-change-profile` での整備を勧める。ただし、利用者が欠落を承知のうえで着手を希望する場合は、欠けた項目の値を直接引用または前提とする質問を作らず、その項目を根拠とする評価も行わないという条件で進めてよい。その場合は、どの項目が欠けたままかを報告に明記する。hub から振り分けられ、hub が既にこの選択を利用者へ求めている場合は、再度は問わず、その選択に従う。hub と本スキルが同じ選択を2回求めないためである。
3. 企業スラッグを解決する前に、`validate_company_index.py`（job-change-support の scripts）で一覧を検証する。FAIL（ERROR 1件以上）なら指摘内容を利用者へ示し、修復されるまで解決へ進まない。
4. 対象企業の企業スラッグを `career-private/company_index.json` で解決する（詳細は job-change-support の `references/company-index-format.md`）。そのうえで company_research.json（`companies/{企業スラッグ}/company_research.json`）の有無を確認する。同フォルダーに `interview_answers.json` が存在する場合は、`interview_questions.json` の `questions[].id` の集合から `interview_answers.json` の `answers[].question_id` の集合を差し引く。残った id の質問を「残りの質問」として提示し、そこからの再開を利用者へ提案する。差分は会話の記憶ではなくこの2ファイルだけで決める。`interview_questions.json` が無い場合は再開できないため、Step 1 からやり直す。company_research.json が無い場合は、AskUserQuestion で次を利用者へ明示して選ばせる。
   - (A) 企業研究を先に実施する。hub へ戻して `job-change-company-research` を起動し、company_research.json を得てから本スキルへ戻る。
   - (B) 企業研究は行わず、Step 0.9 の面接情報の調査だけを行う。`interview_intel.json` を企業固有の根拠として進める。
   - (C) フォールバックモードを選ぶ。企業固有の根拠を持たない一般対策として進め、以降は企業固有の想定質問を生成せず、企業理解の観点による評価も対象外とする。
5. company_research.json がある場合は、`check_freshness.py`（job-change-support の scripts）で当該企業の `_manifest.json` を判定する。`stale` のトピックがあれば、その旨と対象トピック名を利用者へ示し、`job-change-company-research` での差分再調査を提案する。利用者が再調査せずに進むことを選んだ場合はそのまま進んでよい。ただし、古い情報に基づく旨と対象トピック名を Step 4 の `interview-prep-report.md` へ明記する。判定規則と TTL の原本は job-change-support の `references/freshness-policy.md` にある。
6. `career-private/self_analysis.json` の有無を確認する。あれば Step 1・Step 3 の入力に加える。無くても進行できるが、自己分析（`job-change-self-analysis`）を先に実行すればキャリア・ナラティブと転職理由の建設的な言い換えを一貫性の観点の根拠に使えることを、利用者へ明示する。
7. `career-private/fit/{企業スラッグ}/fit_assessment.json` の有無を確認する。あれば Step 1 の入力に加える。想定質問の生成時に、`condition_fit` の `met: "unknown"` の項目と `overall.open_questions` を、逆質問・確認事項の質問素材として用いる。無くても進行できる。fit_assessment.json は career-private 配下の成果物であり、Web ツールを持つエージェントへは渡さない。
8. 個人情報の取り扱いルールを確認する。profile.json の内容を外部送信に用いない。本スキルと job-change-interview-coach はいずれも Web 送信手段を持たない。このため profile.json（あれば self_analysis.json・fit_assessment.json も）をそのまま渡してよい。
9. 利用者が持つ情報の有無を AskUserQuestion で1問だけ確かめる。転職エージェントから受け取った質問一覧や選考の傾向、過去に同じ企業の選考を受けた経験、カジュアル面談で聞いた内容が該当する。あれば、利用者の言葉のまま `companies/{企業スラッグ}/interview_notes_user.md` に書き留める（company モード時）。要約・言い換えをしない。無ければ作らない。
10. 対象とする選考段階（カジュアル面談・一次面接・二次面接・最終面接）を利用者へ確かめる。分からなければ `不明` とし、Step 0.9 の `format_facts` で補う。

### Step 0.9 面接情報の調査（job-change-interview-scout, sonnet）

企業スラッグが解決済みの場合に、対象企業の面接についての情報を Web から集める。対象企業を特定せずに起動された場合は行わない。

1. `companies/{企業スラッグ}/interview_intel.json` の有無と鮮度を確かめる。`_manifest.json` に `artifacts.interview_intel` の記録があれば `check_freshness.py` が判定する（TTL と判定規則の原本は `{HUB_SKILL_DIR}/references/freshness-policy.md`）。`fresh` なら再調査せず既存の成果物を使う。`stale` または未取得なら次へ進む。
2. 調査するかどうかを利用者へ確かめる。所要時間は Web 取得を伴う調査1回分であり、口コミサイトはログインなしで読める範囲に限られることを添える。利用者が要らないと言えば行わず、その旨を Step 4 の報告に書く。
3. job-change-interview-scout（sonnet）を Agent ツールで起動する。指示書に次を渡す。
   - 企業名（`company_index.json` の正式名称と別名）と職種名（`job_posting.json` の職種名。無ければ利用者が指定した職種名）。
   - 出力先パス `{DATA_ROOT}/companies/{企業スラッグ}/interview_intel.json`。
   - 本スキルの絶対パス（`{SKILL_DIR}`）と、job-change-company-research の絶対パス（`references/evidence-grading.md`・`references/source-catalog.md` の所在）。
   - あれば `companies/{企業スラッグ}/company_research.json` と `job_posting.json` のパス。いずれも非個人情報ツリーにある。
   - **渡さないもの**: `career-private/` 配下のパスと内容、`interview_notes_user.md`・`interview_answers.json`・`interview_evaluation.json`・`interview_questions.json`・`interview-prep-report.md`・`documents/` 配下のパス、利用者の氏名・経歴・年収。
4. スカウトが書き出した `interview_intel.json` を `validate_interview_intel.py` で再検証する（ゲート）。FAIL（ERROR 1件以上）なら ERROR の内容を指示書へ添えてスカウトを再起動する。PASS を確認したら、`_manifest.json` を Read し、`artifacts.interview_intel` だけを `{"updated_at": "YYYY-MM-DD"}` に差し替えて全体を Write で書き戻す。他の成果物の記録を落とさない。ファイルが無ければ `{"schema_version": 1, "artifacts": {"interview_intel": {...}}}` を作る。
5. `reported_questions` の `category` に `配慮事項` があれば、その内容を利用者へ「聞かれても答えなくてよい事項」として伝える（一覧の原本は `references/question-bank.md`）。`open_questions` に古い出典や新卒選考の記録に基づく旨があれば、それも伝える。

### Step 1 想定質問の生成

1. job-change-interview-coach（opus）を Agent ツールで起動し、Step 1 を指示する。指示書に次を渡す。
   - 実行するステップ = 1。
   - profile.json の絶対パス。company_research.json（あれば）・interview_intel.json（あれば）・interview_notes_user.md（あれば）・self_analysis.json（あれば）・fit_assessment.json（あれば）・exam_assessment.json（あれば）・求人票（あれば）の絶対パス。
   - 対象とする選考段階（Step 0 で確かめたもの。`不明` を含む）。
   - 本スキルの絶対パス（`{SKILL_DIR}`）。出力形式の原本 `references/interview-format.md` の所在として渡す。
2. コーチは質問類型ごとに想定質問を生成する。各質問には interviewer_intent（面接官の評価観点）・basis（company_research の claim id・interview_intel の id・`interview_notes_user.md` の該当箇所・profile の該当箇所）・provenance（`general`・`reported`・`inferred`）・stage（想定される選考段階）を付して返す。フォールバックモードでは degraded: true とし、企業固有の claim を根拠に用いる質問は生成しない。company_research.json はあるが topic=selection_process の claims が0件で、interview_intel.json の `format_facts` も無い場合は、その旨を指示書に明記する。選考プロセスを前提とする質問は生成させない（部分的なフォールバック）。`fit_assessment.json` がある場合は、`condition_fit` の `met: "unknown"` の項目と `overall.open_questions` を加える。いずれも逆質問・確認事項の質問素材である。無い場合は company_research.json・interview_intel.json・profile.json のみを素材とする。選考段階が `カジュアル面談` の場合は、逆質問と、自己紹介・転職理由の短い回答だけを生成させる。
3. コーチが返した JSON を、`degraded`・`degraded_reason` を含むトップレベルごと `interview_questions.json` として保存する（company モード時）。`questions` 配列だけを抽出しない。形式の原本は `references/interview-format.md` にある。質問類型・評価観点・外資系の質問形式の原本は、それぞれ `references/question-bank.md`・`references/evaluation-rubric.md`・`references/foreign-interviews.md` にある。
4. 保存した `interview_questions.json` を `validate_interview_artifacts.py` で検証する（company モード時。ゲート）。FAIL（ERROR 1件以上）なら Step 2 へ進まず、ERROR の内容を指示書へ添えてコーチを再起動する。

### Step 2 模擬面接

1. 本スキル（オーケストレーター）が、生成した想定質問を1問ずつ提示する。利用者の回答をテキストで収集し、回答ごとに次の質問へ進む。`provenance` が `reported` の質問を先に出し、`inferred` の質問は推測である旨を添えて出す。`配慮事項` は `notes` にのみ現れ、模擬面接では扱わない。`stage` が対象の選考段階と異なる質問は、利用者が求めない限り後回しにする。
2. 全問を課す必要はない。利用者が指定した範囲（質問類型・問数）で実施してよい。回答を受け取るごとに、`{"question_id": …, "answer": …, "answered_at": …}` の1件を `companies/{企業スラッグ}/interview_answers.json` の `answers` 配列へ追記保存する。企業スラッグが無い場合は会話上に保持する。`question_id` には、提示した質問の `interview_questions.json` での `id` をそのまま書く。`answer` には利用者の回答をそのまま転記し、要約・言い換えをしない。形式の原本は `references/interview-format.md` にある。
3. この段階では評価・添削・言い換えをしない（評価は Step 3）。回答を誘導しない。
4. Step 3 へ進む前に、`interview_answers.json` を `validate_interview_artifacts.py` で検証する（company モード時。ゲート）。`--questions` に `interview_questions.json` を渡し、`question_id` が質問側に実在することを確かめる。FAIL なら ERROR を解消してから Step 3 へ進む。

### Step 3 回答の評価とフィードバック

1. job-change-interview-coach（opus）を Agent ツールで起動し、Step 3 を指示する。指示書に次を渡す。
   - 実行するステップ = 3。
   - profile.json の絶対パス。company_research.json（あれば）・interview_intel.json（あれば）・self_analysis.json（あれば）の絶対パス。
   - 本スキルの絶対パス（`{SKILL_DIR}`）。出力形式の原本 `references/interview-format.md` の所在として渡す。
   - 評価対象の質問一覧と回答（company モード時は `interview_answers.json` から読み込む。企業スラッグが無い場合は会話上に保持した対を用いる）。
2. コーチは各回答を STAR（scores.star）・具体性（scores.specificity）・一貫性（scores.consistency）・企業理解（scores.company_fit）の4観点について、3段階（充足・一部・不足）で評価する。feedback と improvement には根拠参照（profile の該当箇所、self_analysis.json の narrative・reason_for_change、または claim id）を付して返す。フォールバックモードでは企業理解の観点を対象外とし、degraded: true とする。
3. 評価アンカーの原本は `references/evaluation-rubric.md`（コーチの判定定義と一致）である。コーチが返した JSON を、`degraded`・`degraded_reason` を含むトップレベルごと `interview_evaluation.json` として保存する（company モード時）。`evaluations` 配列だけを抽出しない。回答そのものは `interview_answers.json` に残っており、`question_id` で対応が付く。形式の原本は `references/interview-format.md` にある。
4. 保存した `interview_evaluation.json` を `validate_interview_artifacts.py` で検証する（company モード時。ゲート）。`--questions` に `interview_questions.json` を渡す。FAIL なら Step 4 へ進まず、ERROR の内容を指示書へ添えてコーチを再起動する。

### Step 4 総括

1. 全評価を観点別に集計し、強み（充足の多い観点）と優先改善点（不足の観点と、その具体的な補い方）を整理する。改善案は `references/evaluation-rubric.md` のアンカーに沿い、STAR の欠落要素の補い方や、企業理解の反映方法を含める。
2. 再演習の提案（評価の弱い観点・質問類型に絞った再度の模擬面接）を添える。
3. 観点別の強み・優先改善点・再演習の提案を `interview-prep-report.md` にまとめる（company モード時は company フォルダーへ保存する）。総括の判断・改善案は評価アンカーと根拠参照に基づき、profile.json・company_research.json・interview_intel.json に無い事実を前提に置かない。報告書には、想定質問の出所の内訳（`general`・`reported`・`inferred` の件数）、`interview_questions.json` の `notes`（聞かれても答えなくてよい事項・選考段階の前提・古い出典の注記）、面接情報を調査しなかった場合はその旨を書く。
4. 報告書と最終メッセージはいずれも結論から述べる。中身の無い節・同じ内容の繰り返し・定型の前置きを置かない。

## 合否ゲートと差し戻し

パイプラインには4つのゲートがある。

- Step 0.9 のスカウト出力ゲート（company モードで調査した場合）では、保存した `interview_intel.json` を `validate_interview_intel.py` で検証し、PASS（ERROR 0件）を確認する。FAIL なら ERROR の内容を指示書へ添えてスカウトを再起動する。`{"error": ...}` が返った場合は入力の欠落であり、指示書を直して再起動する。この検証は形式と出典の有無だけを見て、質問が本当に聞かれたかどうかは見ない。
- Step 0 のプロファイルゲート（必須）では、`validate_profile.py` が PASS でなければ Step 1 へ進まない。profile.json が未作成、または FAIL（ERROR 1件以上）の場合は、hub（job-change-support）でのプロファイル整備を先行させ、PASS を確認してから戻る。ただし FAIL の場合は ERROR の内容を示す。利用者が欠落を承知で着手を希望するなら、欠けた項目の値を直接引用または前提とする質問を作らず、その項目を根拠とする評価も行わないという条件で進めてよい。どの項目が欠けたままかを報告に明記する。hub が既にこの選択を利用者へ求めている場合は、再度は問わず、その選択に従う。
- コーチ出力ゲート（Step 1・Step 3）では、job-change-interview-coach の返す JSON が次を満たすことを確認する。満たさない場合は、不足内容を指示書へ添えてコーチを再起動する。
  - `{"error": ...}` でない（入力の欠落による返答でない）。
  - スキーマに適合する（Step 1 は `questions`、Step 3 は `evaluations`）。
  - `degraded` と `degraded_reason` が、企業固有の根拠の有無と整合する。`degraded` を `true` にする条件の原本は「目的と原則」1 であり、ここで再定義しない。`true` のときは `degraded_reason` に理由（企業固有の根拠が無い、または選考プロセスの根拠が無い）を書く。
  - Step 3 の `scores` の各値が「充足」「一部」「不足」のいずれかである。
  - Step 3 の `feedback` と `improvement` に根拠参照を含む。根拠参照とは、profile の該当箇所、self_analysis.json の narrative・reason_for_change、または claim id を指す。
- 成果物ゲート（Step 1・Step 2・Step 3、company モード時）では、保存した `interview_questions.json`・`interview_answers.json`・`interview_evaluation.json` を `validate_interview_artifacts.py` で検証し、PASS（ERROR 0件）を確認する。FAIL なら次の Step へ進まない。この検証スクリプトは形式・`degraded` の整合・`question_id` の相互参照・語彙だけを見て、質問や評価の内容の当否は見ない。企業スラッグが無い場合は成果物をファイルへ書き出さないことがあり、そのときはこのゲートを適用しない。

差し戻しは同一ステップにつき最大2回とする。2回で解消しない場合は、当該の質問または評価を未決事項として利用者へ提示し、判断を委ねてから次へ進む。

## 役割の実行（ハーネス別）

本スキルのパイプラインは、専門の役割へ作業を委ねる形で書いてある。役割の内容は `references/roles/` に置き、これを原本とする。

| エージェント名 | 役割プロンプトの原本 |
|---|---|
| `job-change-interview-scout` | `{SKILL_DIR}/references/roles/interview-scout.md` |
| `job-change-interview-coach` | `{SKILL_DIR}/references/roles/interview-coach.md` |

ハーネス別の実行手順と、起動する数の判断の原本は hub の `{HUB_SKILL_DIR}/references/role-execution.md` にある。サブエージェントを起動できないハーネスで本体がスカウトの役割を担う場合、本体は `career-private/` を読んでいることがある。その場合でも、スカウトの役割の作業中は個人情報を検索語にも成果物にも持ち込まない。

## エージェントのモデル方針

| エージェント | model | 責務 |
|---|---|---|
| `job-change-interview-scout` | sonnet | Step 0.9: 対象企業の面接についての Web 調査 → interview_intel.json |
| `job-change-interview-coach` | opus | Step 1: 質問類型ごとの想定質問生成 ／ Step 3: 回答の4観点評価とフィードバック |

model はエージェントの frontmatter に固定済みであり、起動時に上書きしない。

## スクリプトのCLI使用例

本スキルの検証スクリプトは `validate_interview_intel.py` と `validate_interview_artifacts.py` の2本である。前者は Step 0.9 で保存した `interview_intel.json` を検証する。後者は Step 1・Step 2・Step 3 で保存した成果物を、それぞれ次のように検証する。検証対象の種別はトップレベルのキーから判別されるため、引数で指定しない。

```bash
python {SKILL_DIR}/scripts/validate_interview_intel.py {DATA_ROOT}/companies/{企業スラッグ}/interview_intel.json --json
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

`validate_interview_intel.py`・`validate_interview_artifacts.py`・`validate_profile.py`・`validate_company_index.py` の終了コードは PASS で 0、FAIL で 1（WARN のみは PASS 扱い）である。`check_freshness.py` は常に終了コード 0 を返し、`fresh`・`stale`・`missing` の分類を出力する。profile.json の仕様と検証規則の原本は job-change-support の `references/profile-format.md` にある。

## references 一覧

| ファイル | 何を | いつ読むか |
|---|---|---|
| `references/interview-intel-format.md` | `interview_intel.json` のフィールド仕様・記入基準・機械的な検証の規則、報告された質問と推測した質問の区別 | Step 0.9 の調査と検証、Step 1 の入力 |
| `references/interview-format.md` | 3つの成果物（`interview_questions.json`・`interview_answers.json`・`interview_evaluation.json`）のフィールド仕様・記入基準・機械的な検証の規則 | Step 1〜Step 3 の保存と検証 |
| `references/question-bank.md` | 想定質問の出所と示し方、頻出質問の質問類型・面接官の評価観点（細目・年代・選考段階）・答え方の原則・逆質問の NG・カジュアル面談・聞かれても答えなくてよい事項・転職エージェント経由の情報（出典付き） | Step 0 の聞き取り、Step 1 の想定質問生成、Step 2 の進行 |
| `references/roles/interview-scout.md` | 面接情報調査担当の役割プロンプト | Step 0.9。サブエージェントを使えないハーネスでは本体が読む |
| `references/roles/interview-coach.md` | 想定質問の生成と回答評価の役割プロンプト | Step 1・Step 3。サブエージェントを使えないハーネスでは本体が読む |
| `references/evaluation-rubric.md` | 4観点（STAR・具体性・一貫性・企業理解）と3段階のアンカー、良い回答の要素、学術的根拠（DOI 付き） | Step 3 の評価、Step 4 の総括 |
| `references/foreign-interviews.md` | 外資系のビヘイビアラル/コンピテンシー面接・ケース面接の進め方と評価観点（出典付き） | 外資系選考の Step 1・Step 2・Step 3 |
