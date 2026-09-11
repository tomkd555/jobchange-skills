---
name: job-change-job-search
description: >-
  転職の求人検索を担うサブスキル。無償の公開Web検索だけで求人を探し、掲載ページの引用と出典URLを付した
  job_search_results.json を作る。2モードを持つ。fuzzy（曖昧条件検索）は利用者の曖昧な希望（例「リモート多め・
  年収600万以上・SaaS系」）を構造化条件シートへ変換し、AskUserQuestion で確認してから検索する。similar_better
  （基準求人を上回る検索）は基準求人（job_posting.json または URL）から条件を抽出し、どの軸（年収・リモート・年間休日・
  固定残業・変更の範囲）の改善を狙うかを確認してから検索する。検索へ渡す条件は匿名化し、現勤務先名・氏名・現年収を含めない
  （希望年収を下限として含めることは可）。利用者が結果から企業を選んだら、企業研究の求人票の取り込みへ接続する。
  job-change-support（hub）から振り分けられて動く。
  Use when the user wants to search for job openings for a job change in Japan using only free public web search —
  either from a vague wish list (fuzzy mode) or by finding roles that beat a baseline posting (similar_better mode) —
  and needs sourced results with verbatim quotes rather than fabricated listings, with their current employer, name,
  and current salary kept out of the query.
  trigger words: 求人検索, 求人を探す, 求人を探して, 転職先を探す, リモートの求人, 年収600万以上の求人,
  似た求人でもっと良い条件, 今より良い条件の求人, この求人より良いところ, 求人を絞り込む。
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Agent, AskUserQuestion, Skill
---

# job-change-job-search

転職の求人を探すとき、本スキル1つで条件の組み立てから検索・検証・納品までの手順がそろう。無償の公開Web検索だけで求人を探し、すべての求人に掲載ページの引用と出典URLを付す。

本スキルは hub（job-change-support）から振り分けられて動く。検索の実行（Web調査）は求人検索担当エージェント（job-change-job-searcher）が担う。判断基準は `references/` で自己完結する。

## 目的と原則

1. **無償の公開Web検索だけで探す。** 有償の求人API・会員限定の非公開求人には依存しない。検索方法のカタログは `references/query-catalog.md` にある。求人ページの開き方の3系統・サイト別のURL文法と制約・対象外にしたサイトとその理由・取得の可否を決める規則・クエリの展開規則・年収下限の再判定・重複の排除・相場の基準線・関連情報の取得先・掲載終了の確認を載せる。会員登録が必要な求人を範囲外にした場合は、成果物の `coverage_notes` に記す。robots.txt が AI クローラーの取得を明示的に拒んでいるサイトは、技術的に取得できても対象外とする。

2. **掲載ページの引用と出典URLを付す。** 各求人には、掲載ページからの引用（`quote`）と出典URL（`url`）・掲載サイト名（`source_site`）を必ず付す。取得できない求人を創作しない。給与が「応相談」等で数値が読めない場合は `salary_range` を `null` にする。

3. **匿名化を徹底する。** 検索担当エージェントへ渡す条件には、現勤務先名・氏名・現年収を含めない。希望年収の下限を条件に含めることは可とする。本スキルに関わる個人情報の境界の例外はこれだけであり、理由と規定は `{HUB_SKILL_DIR}/references/pii-boundary.md` にある。`profile.json` のパス・内容を Web ツールを持つエージェントへ渡さない。条件はスキル本体が組み立て、匿名化した文字列としてのみ渡す。

4. **現勤務先の求人を除外する。** 検索結果に現勤務先の求人が含まれうる。除外はスキル本体がローカルで行う（`profile.json` を Web ツールへ渡さないため、除外判定はエージェントの外で行う）。

5. **個人情報を外部へ送信しない。** 利用者の個人情報を、検索クエリ・fetch・外部APIを含む一切の外部送信に用いない。対象の列挙と例外の原本は hub の `{HUB_SKILL_DIR}/references/pii-boundary.md` にある。job-change-job-searcher は WebSearch・WebFetch を持つため、`profile.json` と `career-private/` 配下のパス・内容を渡さない。本スキルに関わる例外は希望年収の下限だけであり、匿名化した条件シートの `salary_min` として渡してよい（原則3）。現年収（`salary.current`）は例外に含まれず、渡さない。`commute.json` から導いた駅名も渡さない。

6. **利用者の条件はそのまま検索し、偏りは別枠で点検する。** 利用者の希望は主集合（`search_sets.primary`）としてそのまま検索する。条件の書き方に紛れ込んだ「本人が選んだわけではない絞り込み」（職種名・業界・規模・フルリモート・役職の段階の固定など）は、Step 1 で必須か選好かを1問で確かめ、選好と答えた条件を外した探索集合（`search_sets.exploration`）を最大6本の追加クエリで作る。探索集合は主集合を置き換えず、主集合の本数を削らない。利用者が要らないと言えば作らない。点検する偏りの一覧と探索集合の組み方の原本は `references/bias-checklist.md` にある。

## 範囲外

- **求人への応募・エージェント登録等の外部送信。** 応募フォームの送信・スカウト返信・転職エージェントへの登録は行わない。求人の収集までを支援し、応募は本人が行う。
- **企業研究と、求人票の構造化した取り込み。** 選んだ企業の企業研究と求人票の構造化は job-change-company-research が担う。成果物は `company_research.json` と `job_posting.json` である。本スキルは検索結果を集め、選定後に企業研究へ接続する。
- **適合性評価。** 実質時給・拘束時間・7次元の適合性評価は job-change-fit-assessment が担う。本スキルは求人票の記載だけで判定できる8軸のスクリーニングにとどめ、企業研究・自己分析・通勤時間を要する評価は行わない。
- **利用者プロファイルの作成・管理。** profile.json の作成・更新・検証は hub（job-change-support）と `job-change-profile` が担う。本スキルは Step 3.5 の軸判定と Step 4 の PII リントのために profile.json をローカルで読むだけで、内容を外部へも Web ツールを持つエージェントへも渡さない。

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

## データ配置

検索実行ごとに `job-search/{YYYYMMDD}-{条件の短いスラッグ}/` を作り、`job_search_results.json` を置く。企業別の成果物ツリー（`companies/{企業スラッグ}/`）とは別である。

| パス | 内容 |
|---|---|
| `job-search/{YYYYMMDD}-{条件の短いスラッグ}/job_search_results.json` | 求人検索の成果物。仕様は `references/job-search-format.md` |
| `job-search/{YYYYMMDD}-{条件の短いスラッグ}/job-search-report.md` | 検索結果を人が読める形へ整形したレポート。スキル本体が Step 5 で書く |

- 条件の短いスラッグは、主条件をローマ字・英数字で表した簡潔な識別子とする（例: `remote-saas-be`）。日付は検索実行日（`executed_at`）に合わせる。
- スキル本体フォルダー（`skills/job-change-job-search/`）に実データを置かない。`assets/` の2つの記入例は架空である。

## 中間成果物: job_search_results.json

検索結果は `job_search_results.json`（`schema_version` は `2.2`）に集約する。構造は3層である。

| 層 | フィールド | 書き手 |
|---|---|---|
| 観測層 | `results[]` の title・company_name・url・source_site・salary_range・location・remote_policy・annual_holidays・match_notes・quote・better_points・`search_set`・`role_match`・`related_info`・`duty_items`・`axis_observations`・`baseline_comparison.axes`、およびトップレベルの `search_sets`・`search_log`・`improvement_axes` | 検索担当エージェント（Web ツールを持つ。profile を読まない） |
| 判定層 | `results[]` の `axis_judgements`・`classification`・`classification_reasons`・`classification_override`・`slug`・`baseline_comparison.overall` | スキル本体（ローカル。profile を読む） |
| 総括 | `screening`（分類ごとの件数・総合判定・軸ごとの未充足件数・現勤務先除外の実施記録・探索集合の実施記録） | スキル本体 |

この分離により、個人情報を Web ツールを持つエージェントへ渡さずに条件判定が成立する。完全な仕様・記入基準・検証規則は `references/job-search-format.md` を原本とする。

## モード

### mode=fuzzy（曖昧条件検索）

利用者の曖昧な希望を構造化条件シートへ変換し、確認してから検索する。

1. 利用者の希望（例「リモート多め・年収600万以上・SaaS系」）を、次の軸へ構造化して条件シートを作成する。
   - 職種（`roles`）・業界（`industries`）・年収下限（`salary_min`、円単位の数値）・勤務地/リモート（`location`・`remote_policy`）・雇用形態（`employment_type`）・その他条件（`other`）。
   - 現勤務先名・氏名・現年収は条件に含めない（原則3）。希望年収の下限は `salary_min` として含めてよい。
2. 構造化した条件シートを AskUserQuestion で確認する。選択式を中心に、最大4問・各4択までとする。曖昧な軸（リモートの頻度・年収の下限・職種の範囲など）を優先して確認する。
3. 条件シートを `references/bias-checklist.md` の「利用者側の偏りの一覧」に照らし、該当する条件について「必須か、選好か」を確認の1問に含める。選好と答えた条件を外し、隣接職種・役職の段階・リモート表現を広げた探索集合の条件シートを作る。探索集合を作るかどうかを利用者に確かめ、要らないと言われれば作らない。年収下限は探索集合でも外さない。
4. 確認済みの条件（主集合）と探索集合の条件を、いずれも匿名化した文字列として求人検索担当エージェント（job-change-job-searcher）へ渡し、`mode=fuzzy` で検索させる。

### mode=similar_better（基準求人を上回る検索）

基準求人から条件を抽出し、どの軸の改善を狙うかを確認してから検索する。

1. 基準求人を受け取る。所在は `companies/{企業スラッグ}/job_posting.json`（取り込み済みの求人票）または URL のいずれかである。URL を渡された場合、本スキルは WebFetch を持たないため条件を抽出できない。先に Skill ツールで `job-change-company-research` を起動して Step 0.5 の求人票の取り込みを実行させる。作られた `job_posting.json` を基準求人にする。
2. 基準求人から職種・年収・年間休日・リモート方針・残業・**雇用形態**・**就業場所と業務の変更の範囲**を抽出する。後ろの2つは軸別比較の6軸に含まれるため、欠かすと当該軸が `unknown` のままになる。`job_posting.json` の `schema_version` が `1.0` の場合、そのファイルに `scope_of_change` は無い。この場合は当該軸を `unknown` として扱い、求人票を取り込み直すかどうかを利用者に確かめる。抽出時も、現勤務先名・氏名・現年収は条件へ持ち込まない。
3. どの軸の改善を狙うかを AskUserQuestion で確認する。選択肢は年収・リモート・年間休日・固定残業・変更の範囲の5つであり、選ばれた軸の id を `improvement_axes` として記録する。雇用形態は選択肢に入れない（尺度上の方向を持たないため改善軸に取れない。希望があれば `conditions.employment_type` の必須条件として扱う）。軸 id と改善方向の原本は `references/job-search-format.md` にある。
4. 抽出した基準条件と `improvement_axes` を匿名化した文字列として、求人検索担当エージェントへ渡し、`mode=similar_better` で検索させる。`baseline`（基準求人の URL または企業スラッグ）を成果物へ記録するよう指示する。エージェントは、基準求人の条件を上回る点を各求人の `better_points` に列挙し、6軸の `baseline_comparison.axes` を書く。

## パイプライン

`{SKILL_DIR}` は本スキルの絶対パスを指す。`{results.json}` は成果物のパス（`job-search/{YYYYMMDD}-{スラッグ}/job_search_results.json`）に読み替える。

### Step 0 受付とモード判別

依頼が fuzzy（曖昧な希望からの検索）か similar_better（基準求人を上回る検索）かを判別する。基準となる求人・URLが示されていれば similar_better、漠然とした希望であれば fuzzy とする。判別が曖昧な場合は AskUserQuestion で確認する。

### Step 1 条件の組み立てと確認

モードに応じて条件を組み立て（上記「モード」の手順）、AskUserQuestion で確認する。ここで組み立てる条件は匿名化済みでなければならない（現勤務先名・氏名・現年収を含めない）。

### Step 2 検索の実行（job-change-job-searcher, sonnet）

求人検索担当エージェント（job-change-job-searcher）を Agent ツールで起動する。指示書には次を渡す。

- モード（`fuzzy` または `similar_better`）。
- 匿名化済みの検索条件（文字列。現勤務先名・氏名・現年収を含めない）。
- 出力先ディレクトリ（`job-search/{YYYYMMDD}-{スラッグ}/`）と、成果物のトップレベルの `search_id` へ書く値。`search_id` にはディレクトリ名と同じ `{YYYYMMDD}-{スラッグ}` を入れる。
- similar_better の場合は、基準条件・`improvement_axes`（改善軸の id の配列）・`baseline`（URL または企業スラッグ）を渡す。あわせて基準求人の求人票のパス `{DATA_ROOT}/companies/{企業スラッグ}/job_posting.json` を渡す。このファイルは企業別の非個人情報ツリーにあり、本人の情報を含まないため、Web ツールを持つエージェントへ渡してよい。基準求人が URL 由来で `job_posting.json` がまだ無い場合は、先に Step 0.5（求人票の取り込み）で job-change-company-research に作らせてから、そのパスを渡す。
- fuzzy の場合は、探索集合の条件シート（Step 1 で作ったもの。作らなかった場合は「探索集合なし」と明記する）。エージェントはこれを `search_sets.exploration` に転記し、探索集合のクエリを主集合の12本とは別枠で投げる。
- 本スキルの絶対パス `{SKILL_DIR}`（`references/query-catalog.md`・`references/job-search-format.md`・`references/bias-checklist.md` の所在）。
- hub の絶対パス `{HUB_SKILL_DIR}`（`references/screening-axes.md`・`references/market-data-sources.md` の所在）。
- **観測層まで**を書く指示。観測層は、`duty_items` の引用文と分類、8軸の `axis_observations`、実行したクエリの `search_log`、求人ごとの `search_set`・`role_match`・`related_info`、トップレベルの `search_sets` を指す。similar_better ではこれに、6軸の `baseline_comparison.axes` と `improvement_axes` の転記が加わる。判定層（`baseline_comparison.overall` を含む）と `screening` は書かせない。

**profile.json は渡さない**（原則5。searcher は WebSearch・WebFetch を持つ）。残業の上限・年間休日の下限・作業特性の希望といったしきい値も渡さない。これらは本人の条件であり、判定はスキル本体が Step 3.5 で行う。すでに匿名化条件として許容されている `salary_min` だけは例外とし、検索条件に含めてよい。

エージェントは `references/query-catalog.md` の検索方法に従って求人を集める。job_search_results.json は `references/job-search-format.md` の形式で作る。8軸と業務分類の語彙は `{HUB_SKILL_DIR}/references/screening-axes.md` を読む。

### Step 3 現勤務先求人の除外（スキル本体）

エージェントが返した job_search_results.json から、現勤務先の求人をスキル本体がローカルで除外する。在職中のエントリーは、`career-private/profile.json` の `career_history` のうち `period` が `〜現在` のものである。そのエントリーの `company` に一致する `company_name` を持つ result を取り除く。除外した件数と企業名は、利用者への報告に含める（成果物には残さない）。

### Step 3.5 8軸判定と3分類（スキル本体）

検索担当エージェントが書くのは観測層（求人票から読めた事実）までである。本人の条件との突き合わせは、`profile.json` を読めるスキル本体がローカルで行う。この分担により、個人情報を Web ツールを持つエージェントへ渡さずに条件判定が成立する。

1. `{DATA_ROOT}/career-private/profile.json` を Read で読み、`schema_version` を確認する。
2. `job_change_axis.conditions[]` と `work_character_preferences[]` から、8軸ごとの必須度としきい値を読み取る。必須度は `must` / `want` / `none` の3値である。同じ軸に必須条件が複数ある場合は、最も厳しいしきい値を採用する。
3. 各 result の `axis_observations` としきい値を突き合わせ、`axis_judgements` を書く。観測が `stated=false`、または `value` が `null` の軸は `unknown` にする。**記載が無いことを、条件を満たす証拠にも満たさない証拠にも使わない**。
4. `references/job-search-format.md` の決定表から `classification` を導き、`classification_reasons` を書く。導出結果を手で変える場合は、厳格化する方向にのみ `classification_override` を付ける。
5. similar_better では、各求人の `baseline_comparison.overall` を書く。`improvement_axes` に挙げた軸だけを見て、1つ以上が改善方向であり、かつどれも逆方向でなければ `better`、それ以外は `not_better` とする。改善方向の対応表は `references/job-search-format.md` にある。エージェントが書いた `relation`（事実の関係）に良し悪しを与えるのはこの段階だけである。
6. `screening` を導出値として書く。`counts`・`unmet_axis_summary` は実集計と一致させる。`current_employer_exclusion` には Step 3 の実施結果を記録する（未実施なら `performed: false`・`excluded_count: null`）。`exploration` には探索集合の実施の有無と、`search_set` が `exploration` の求人の件数・そのうち応募候補の件数を書く（未実施なら `performed: false` と `null`）。探索集合の求人も主集合と同じ規則で判定し分類する。分類は「どう見つけたか」に依存しない。

`profile.json` の `schema_version` が `1.0` または `1.1` の場合はフォールバック動作にする。観測層はそのまま残す。全軸は `level: none`・`judgement: unknown`、全 result は `needs_more_research` にする。`screening.axes_source` は `degraded`、`recommendation` は `判定不能` にする。分類結果を「応募候補」として提示せず、`job-change-profile` での条件の構造化を案内する。

判定に使う語彙（8軸・8作業特性・業務分類）の原本は、hub（`job-change-support`）の `references/screening-axes.md` にある。

### Step 4 機械的な検証と PII リント（スキル本体）

除外後の job_search_results.json を、`--profile` 付きで検証する。

```bash
python {SKILL_DIR}/scripts/validate_job_search_results.py {results.json} --profile {DATA_ROOT}/career-private/profile.json
```

`--profile` を付けると、スキーマ検査に加えて PII リント（現勤務先名・氏名・現年収の混入検出）も実行する。ERROR が1件でもあれば FAIL である。PII 混入の ERROR が出た場合は、混入箇所を成果物から除去してから再検証する（匿名化の漏れであり、そのまま納品しない）。PASS（ERROR 0件）を確認してから納品する。profile.json の読み取りはこの検証のためのローカル処理に閉じ、外部へ送信しない。

### Step 5 納品と接続

検証 PASS の job_search_results.json を納品する。報告は分類ごとにまとめ、`screening.recommendation` を先に述べる。中身の無い節・同じ内容の繰り返し・定型の前置きを置かない。

納品に先立ち、スキル本体が job_search_results.json を人が読める求人検索レポートへ整形する。出力先は `job-search/{search_id}/job-search-report.md` である。`search_id` は成果物のトップレベルの値であり、ディレクトリ名と同じ `{YYYYMMDD}-{スラッグ}` である。このレポートは非個人情報ツリーに置くため、現勤務先名・氏名・現年収を書かない（境界の原本は `{HUB_SKILL_DIR}/references/pii-boundary.md`）。

- 冒頭に `screening.recommendation` と `rationale`、分類ごとの件数（`screening.counts`）を置く。
- 分類（`apply_candidate`・`needs_more_research`・`excluded`）ごとに求人を表にする（求人名・企業名・掲載サイト・出典URL・年収レンジ・勤務地／リモート方針・`want` の未充足の件数）。分類ごとに表を分け、`excluded` の求人を応募候補と同じ表に並べない。`want` の未充足の件数は、`axis_judgements` のうち `level` が `want` で `judgement` が `not_meets` の軸の数であり、報告の列であって成果物のフィールドではない。この件数で並べ替えて順位表にしない。
- 探索集合の求人（`search_set` が `exploration`）は、各分類の表の中で「視野を広げた検索から」の小節に分けて置く。主集合の表より上に置かない。`match_notes` にあるどの偏りの点検から出た求人かを添える。探索集合だけに応募候補がある場合は、その旨を `rationale` に書き、主集合の応募候補の代わりに最有力候補として示さない。探索集合を作らなかった場合は、作らなかったことと理由を1行で書く。
- 求人ごとに8軸の判定を表にする（軸・必須度・しきい値・観測値・`yes`/`no`/`unknown`）。スクリーニングの根拠として `classification_reasons` を添え、`classification_override` を付けた求人はその旨と理由を書く。観測が無い軸は `unknown` と書き、条件を満たす証拠にも満たさない証拠にも使わない。
- `related_info` がある求人は、従業員数・設立年・上場の有無・認定・口コミの総合スコア・掲載日・相場の基準線を、出典URLとエビデンスレベルを添えて1行で書く。レベルCの値（口コミの総合スコア・給料ナビの中央値）は参考値である旨を添える。`related_info` は企業研究の代わりではなく、`needs_more_research` の求人を企業研究へ進めるかどうかの判断材料にとどめる。
- 過去の検索結果との照合はスキル本体がローカルで行う。`{DATA_ROOT}/job-search/` 配下の過去の成果物を読み、同じ正規化企業名と職種名の求人が60日以上離れた別の `search_id` にもあれば `open_questions` に書く（規則は `references/query-catalog.md` の「掲載終了と再掲載の確認」）。過去の成果物には判定層が含まれるため、検索担当エージェントへ渡さない。
- `open_questions` にある掲載終了の疑い（URL の再取得で読めなくなった求人）と、過去の検索にも現れていた求人は、そのまま報告に書く。
- 軸ごとの未充足・判定不能の件数（`screening.unmet_axis_summary`）を表にする。
- 現勤務先求人の除外は `screening.current_employer_exclusion` のとおりに書く。`performed` が `false` なら未検証と書き、0件と書かない。除外した企業名は現勤務先名にあたるため、レポートには書かず利用者への報告だけで伝える。

1. 総合判定として `screening.recommendation` と `rationale` を最初に伝える。`応募推奨なし` の場合は、その旨を明記し、無理に最有力候補を選ばない。
2. `classification` が `apply_candidate` の求人を、満たしている必須条件とともに列挙する。
3. `needs_more_research` の求人を、判定できなかった軸（`unknown` の軸）と、それを確認する手段（企業研究または面接）とともに列挙する。
4. `excluded` の求人を、満たさなかった必須条件とともに簡潔に列挙する。注意書きを付け、応募候補と同じ表には並べない。
5. 利用者が企業を選んだら、hub（job-change-support）の Step 0 手順で `career-private/company_index.json` へ企業スラッグを登録する。`companies/{企業スラッグ}/` を作り、当該 result の `slug` へ追記する。追記後に Step 4 の検証を再実行し、PASS（ERROR 0件）を確認する。続いて job-change-company-research の Step 0.5（求人票の取り込み）へ接続する。求人ページの URL があればそれを入口とし、無ければ、検索結果へ転記した掲載内容を本文として渡す。

similar_better では各求人の `better_points`（基準求人より改善している点）を併記する。`baseline_comparison.axes` の6軸は、軸・改善軸に選んだか・`relation`・基準求人の値・候補求人の値の表にする。`overall` が `better` の求人と `not_better` の求人を分けて示し、`improvement_axes` に挙げた軸のどれで上回ったかを添える。`unknown` の軸は「未確認」と書き、基準求人と同じとは書かない。

#### 報告のルール

**検証していない事項を成果として報告しない。**報告してよい数値は次に限る。

| 報告してよい数値 | 出所 |
|---|---|
| 分類ごとの件数 | `screening.counts` |
| 軸ごとの未充足・判定不能の件数 | `screening.unmet_axis_summary` |
| 探索集合の件数・そのうち応募候補の件数 | `screening.exploration`（`performed` が `true` のときのみ） |
| 求人ごとの `want` の未充足の件数 | `results[].axis_judgements` から数える |
| 現勤務先求人の除外件数 | `screening.current_employer_exclusion.excluded_count`（`performed` が `true` のときのみ） |
| 実行したクエリの本数・ヒット件数・採用件数 | `search_log` |

書いてよいのは `search_log` にあるクエリとその件数までであり、**検索の網羅性は主張しない**。「網羅的に調べた」「主要な求人サイトを一通り確認した」とは書かない。

`current_employer_exclusion.performed` が `false` の項目は「未検証」と書く。「0件」と書かない。機械的な検証の PASS は「形式が整い、PII が混入しておらず、分類と総合判定が軸判定と整合している」ことを示すのであって、求人が本人に合っていることを示すのではない。この区別を報告に反映する。

## 合否ゲート

| ゲート | 通過条件と差し戻し先 |
|---|---|
| Step 4 の機械的な検証・PII リント | `validate_job_search_results.py --profile` が PASS（ERROR 0件）でなければ納品しない。PII 混入の ERROR は匿名化の漏れであり、成果物から除去してから再検証する。 |
| 応募推奨 | `screening.recommendation` が `応募推奨なし` の場合、既定では企業研究・適合性評価へ接続しない。必須条件の見直し（`job-change-profile` の条件更新）、または検索条件・検索経路の見直しへ戻す。応募候補が0件のときに、除外候補や追加調査候補から最有力候補を仕立てない。**例外**: 満たさない必須条件を求人ごとにすべて列挙したうえで、利用者が特定の求人について先へ進むことを明示的に希望した場合は、その求人を企業研究へ接続してよい。この判定の材料は求人票の記載だけであり、判定そのものが企業研究や面接で覆りうるためである。接続する場合は、どの必須条件が未充足のままかを引き継ぎに明記する。利用者が希望を示していない場合は、本スキルから接続を提案しない。 |
| フォールバックの明示 | `screening.recommendation` が `判定不能`（profile が 1.x）の場合、判定できていない旨を明示する。分類結果を「応募候補」として提示せず、`job-change-profile` での条件の構造化を案内する。 |

## 役割の実行（ハーネス別）

本スキルのパイプラインは、専門の役割へ作業を委ねる形で書いてある。役割の内容は `references/roles/` に置き、これを原本とする。

| エージェント名 | 役割プロンプトの原本 |
|---|---|
| `job-change-job-searcher` | `{SKILL_DIR}/references/roles/job-searcher.md` |

ハーネス別の実行手順と、起動する数の判断の原本は hub の `{HUB_SKILL_DIR}/references/role-execution.md` にある。

## エージェントのモデル方針

| エージェント | model | 責務 |
|---|---|---|
| `job-change-job-searcher` | sonnet | 匿名化条件からの公開Web検索 → job_search_results.json ＋ 引用・出典URL付与 |

model はエージェントの frontmatter に固定済みであり、起動時に上書きしない。

## スクリプトのCLI使用例

求人検索結果の検証（終了コードは PASS で 0、FAIL で 1。WARN のみは PASS 扱い）。`{SKILL_DIR}` は本スキルの絶対パス、`{results.json}` は検証対象のパスに読み替える。

```bash
python {SKILL_DIR}/scripts/validate_job_search_results.py {results.json}
python {SKILL_DIR}/scripts/validate_job_search_results.py {results.json} --json
python {SKILL_DIR}/scripts/validate_job_search_results.py {results.json} --profile {DATA_ROOT}/career-private/profile.json
```

`--json` は結果を JSON 形式（`status`・`error_count`・`warning_count`・`errors`・`warnings`）で出力する。`--profile` を付けると、PII リント（現勤務先名・氏名・現年収の混入検出）が加わる。さらに `threshold_ref` が profile の条件・特性に実在するか、`level` が profile の必須度と一致するかも検査する。`--profile` を付けずに実行すると、PII リントとしきい値の突き合わせが未実施である旨の WARN が出る。記述例は `assets/` にある。fuzzy は `job_search_results_example.json`、similar_better は `job_search_results_similar_better_example.json` である。フィールド仕様と検証規則の原本は `references/job-search-format.md` である。単体テストは次で実行する。

```bash
cd {SKILL_DIR} && python -m unittest discover -s scripts/tests
```

## references 一覧

| ファイル | 何を | いつ読むか |
|---|---|---|
| `references/job-search-format.md` | job_search_results.json のフィールド仕様・記入基準・機械的な検証の規則・PII リント | 成果物を作る/読む/検証する全段階 |
| `references/query-catalog.md` | 無償の公開Web検索で求人を探す方法（求人ページの開き方の3系統・サイト別のURL文法と制約・対象外と未確認のサイト・取得の可否を決める規則・クエリの展開規則・年収下限の再判定・重複の排除・相場の基準線・関連情報の取得先・掲載終了の確認） | Step 2 の検索、検索担当エージェントへの指示 |
| `references/bias-checklist.md` | 利用者側の条件の偏りの一覧と点検の問い、探索集合の位置づけと組み方、探索集合の結果の扱い、報告に添える未充足の件数 | Step 1 の条件の確認、Step 5 の報告 |
| `references/search-methods.md` | 探索の量と就業の質の関係、満足化の運用、観測と判定を分ける理由、探索集合を別枠にする理由の根拠（出典付き） | 報告のしかたを決める段階、応募推奨なしのときの提案を組み立てる段階 |
| `{HUB_SKILL_DIR}/references/screening-axes.md` | 8スクリーニング軸・8作業特性・業務分類の語彙と境界例 | Step 2 の観測、Step 3.5 の判定 |
| `{HUB_SKILL_DIR}/references/market-data-sources.md` | 相場データの出所と扱いの規則 | Step 2 の相場の基準線と関連情報 |
| `{HUB_SKILL_DIR}/references/pii-boundary.md` | 個人情報の境界と例外の原本 | 条件を組み立て、エージェントへ渡す全段階 |
| `references/roles/job-searcher.md` | 検索担当の役割プロンプト（観測層までを担う） | Step 2。サブエージェントを使えないハーネスでは本体が読む |
