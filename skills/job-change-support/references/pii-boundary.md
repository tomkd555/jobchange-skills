# 個人情報の境界の原本（pii-boundary）

利用者の個人情報を、Web 送信手段を持つ役割へ渡さないための境界を定める原本である。hub と全サブスキルがこのファイルを参照する。

| 参照元 | 何に使うか |
|---|---|
| `job-change-support` | 各サブスキルへの振り分けと、企業研究へ渡す軸の絞り込み |
| `job-change-profile` / `job-change-self-analysis` | `career-private/` 配下の作成・更新をどの役割へ任せてよいかの判断 |
| `job-change-company-research` / `job-change-job-search` / `job-change-exam-prep` | Web 送信手段を持つ役割へ渡してよい材料の判断 |
| `job-change-documents` / `job-change-interview-prep` / `job-change-fit-assessment` | 個人情報とその派生値の置き場所と受け渡し先の判断 |

対象の列挙・例外・役割ごとの可否はここにのみ置き、参照元へ複製しない。参照元の SKILL.md は、原則としての規範（個人情報を外部送信に用いない）と、そのスキルに固有の帰結だけを書く。

役割プロンプト（`agents/*.md` と `skills/*/references/roles/*.md`）だけは例外で、規範の要点を原文どおりに持つ。役割プロンプトはサブエージェントへ単体で渡り、本ファイルを開けるとは限らないためである。たとえば `job-change-posting-parser` の `tools` は `WebFetch` と `WebSearch` だけで `Read` を持たず、参照先を開く手段が無い。これは意図した複製であり、本ファイルを変えたときは13の役割プロンプトも同時に直す。

## 境界の原則（広い列挙）

次を個人情報として扱い、検索クエリ・fetch・外部 API を含む一切の外部送信に用いない。

### profile.json の項目

対象は、氏名・現年収（`salary.current`）・希望年収（`salary.desired`）・居住地・学歴・在籍企業名（`career_history[].company`）・実績（`career_history[].achievements` の定量値を含む）である。`job_change_axis` の条件と `company_score_axes` の `weight`・`thresholds`・定性軸も、本人の判断と状況を映すため同じ扱いとする。

### career-private/ 配下のファイル

`{DATA_ROOT}/career-private/` 配下は、パスも内容も個人情報として扱う。

| ファイル | 個人情報である理由 |
|---|---|
| `profile.json` | 経歴・年収・氏名の原本 |
| `profile_interview_notes.md` | 聞き取りの生の記録 |
| `self_analysis.json` | 行動エピソード・他者からの評価・価値観 |
| `company_index.json` | 応募先の一覧が本人の志望を示す |
| `commute.json` | 通勤時間が居住地を示唆する |
| `fit/{企業スラッグ}/fit_assessment.json` | profile・自己分析・通勤から導いた派生値 |
| `fit/{企業スラッグ}/time_analysis.json` | 年収・労働時間・通勤時間から導いた派生値 |
| `fit/{企業スラッグ}/sources.json` | 派生値の算定に使った数値の出典メタ |
| `fit/{企業スラッグ}/qualitative_judgment.json` | 利用者が自分の言葉で書いた判定条件の適用結果 |
| `fit/current/time_analysis.json` | 現職の拘束時間・実質時給 |

派生値も原本と同じ境界の内側にある。個人情報から計算した値は、計算の結果であっても個人情報である。

### ツリーの名前は境界ではない

`career-private/` が個人情報、`companies/` と `job-search/` が非個人情報、という二分では実態を表せない。境界の本体は、Web 送信手段（WebSearch・WebFetch）を持つ役割へ個人情報のパスも内容も渡さないことである。ツリーの名前は、その判断の目安にすぎない。

`companies/{企業スラッグ}/` 配下のうち、次の成果物は個人情報を含む。いずれも書き出す役割と読む役割が Web 送信手段を持たないため、境界の内側にとどまる。

| ファイル | 個人情報である理由 | 読み書きする役割 |
|---|---|---|
| `documents/` 配下の応募書類 | 経歴・実績を `profile.json` から引いて本文に書く | `job-change-document-writer`・`job-change-document-auditor` |
| `documents/appeal-mapping.md` | 求人要件と `profile.json` の実績の対応表 | 同上 |
| `documents/tailoring-rationale.md` | どの実績を採用したかとその理由 | 同上 |
| `interview_answers.json` | 利用者の回答を要約・言い換えをせずそのまま転記する | `job-change-interview-coach` |
| `interview_evaluation.json` | 回答への評価と根拠参照 | 同上 |

これに対し、`companies/{企業スラッグ}/company_research.json`・`companies/{企業スラッグ}/exam_assessment.json` と `job-search/{検索ID}/` 配下は、Web 送信手段を持つ役割が読み書きする。該当するのは `job-change-company-researcher`・`job-change-research-auditor`・`job-change-exam-scout`・`job-change-job-searcher` である。ここへ個人情報とその派生値を書かない。適合性評価の派生値の置き場所を `career-private/fit/{企業スラッグ}/` 配下に限るのも、同じ理由による。

`_manifest.json` にも個人情報とその派生値を書かない。記録する項目の仕様は `freshness-policy.md` にある。

## 例外

境界を越えて Web 送信手段を持つ役割へ渡してよいのは、次の2つに限る。ほかに例外を作らない。

### 希望年収の下限

求人検索の条件として、希望年収の下限（`salary_min`）を渡してよい。求人検索は年収下限を軸として成立する手続きであり、下限の額だけでは個人を特定しない。現年収（`salary.current`）は渡さない。現年収と希望年収の両方がそろうと、在籍企業を推定できるだけの情報量になる。

この例外を使うのは `job-change-job-search` である。渡すのは匿名化した条件シートの `salary_min` の数値のみで、`profile.json` のパスも内容も渡さない。

### company_score_axes の quantitative 軸の識別子

企業研究（`job-change-company-research`）を起動するときは、`company_score_axes` のうち `kind` が `quantitative` の軸の識別子の配列だけを渡してよい。たとえば `["compensation_level", "monthly_overtime", "annual_holidays"]` のような配列である。この配列は氏名・在籍企業名・現年収を含まない。`weight`・`thresholds` は渡さない。重みと基準は利用者の判断であり、企業側の事実収集には要らない。`company_score_axes` が無い場合は、軸を渡さずに起動する。

定性軸（`kind` が `qualitative`）は、利用者が自分の言葉で書いた `label`・`definition`・`judgment` を持つため渡さない。定性軸の判定は、企業研究が集めた事実と求人票を材料に、Web ツールを持たない適合性評価が行う。定性軸について企業研究で追加の調査が要る場合は、利用者自身の言葉で重点観点として指示する。

## 機械検出できる3項目（狭い定義）

上の広い列挙は、材料を渡す前の判断に使う規範である。これに対し、成果物へ混入した個人情報を機械で検出する検査は、文字列一致で確実に検出できる3項目（現勤務先名・氏名らしき値・現年収）だけを対象とする。抽出元と検出規則の原本は `job-change-job-search` の `references/job-search-format.md` の「PII リント」にある。`scripts/validate_job_search_results.py` の実装（`_SALARY_MIN_FOR_LINT`・`_NAME_KEYS`）はこれと一致する。

希望年収の下限は検査対象に含めない。上の例外として検索条件に使うことを認めているためである。

狭い定義は広い列挙を置き換えない。機械が検出できるのは3項目だけであり、残りは渡す前の判断で守る。検査が PASS したことは、広い列挙を守った証拠にならない。

## 役割ごとの可否

Web 送信手段（WebSearch・WebFetch）を持つかどうかで、`career-private/` 配下を読んでよいかが決まる。各役割の `tools` は `agents/*.md` の frontmatter に固定してある。

| 役割 | Web 送信手段 | `career-private/` 配下 |
|---|---|---|
| `job-change-company-researcher` | あり（WebSearch・WebFetch） | 読まない。パスを渡されても開かない |
| `job-change-posting-parser` | あり（WebSearch・WebFetch） | 読まない。パスを渡されても開かない |
| `job-change-job-searcher` | あり（WebSearch・WebFetch） | 読まない。パスを渡されても開かない |
| `job-change-exam-scout` | あり（WebSearch・WebFetch） | 読まない。パスを渡されても開かない |
| `job-change-research-auditor` | あり（WebSearch・WebFetch） | 読まない。パスを渡されても開かない |
| `job-change-fit-assessor` | なし | 読んでよい。派生値の書き込み先も `career-private/fit/{企業スラッグ}/` 配下に限る |
| `job-change-profile-writer` | なし | 読んでよい |
| `job-change-profile-auditor` | なし | 読んでよい |
| `job-change-self-analysis-writer` | なし | 読んでよい |
| `job-change-self-analysis-auditor` | なし | 読んでよい |
| `job-change-document-writer` | なし | 読んでよい |
| `job-change-document-auditor` | なし | 読んでよい |
| `job-change-interview-coach` | なし | 読んでよい |

役割の `tools` を変更するときは、この表を必ず確認する。Web ツールを1つ足すだけで、その役割は個人情報を受け取れなくなる。

サブエージェントを起動できないハーネス（Codex ほか）では、本体が役割プロンプトを読んで自分にその役割を課す。本体は Web 送信手段を持ちうるが、その場合でも Web 送信手段を持たない役割の作業中は Web 送信手段を使わない。
