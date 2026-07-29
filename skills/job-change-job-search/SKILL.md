---
name: job-change-job-search
description: >-
  転職の求人検索を担うサブスキル。無償の公開Web検索だけで求人を探し、掲載ページの引用と出典URLを付した
  job_search_results.json を作る。2モードを持つ。fuzzy（曖昧条件検索）は利用者の曖昧な希望（例「リモート多め・
  年収600万以上・SaaS系」）を構造化条件シートへ変換し、AskUserQuestion で確認してから検索する。similar_better
  （類似高待遇検索）は基準求人（job_posting.json または URL）から条件を抽出し、どの軸（年収・休日・リモート・残業）の
  改善を狙うかを確認してから検索する。検索の実行は求人検索担当エージェント（job-change-job-searcher）が担い、
  スキル本体は条件の組み立て・匿名化・現勤務先求人の除外・機械検証（validate_job_search_results.py の PII リント）を担う。
  匿名化ルールとして、エージェントへ渡す条件に現勤務先名・氏名・現年収を含めない（希望年収を下限として条件に含めることは可）。profile.json の
  パス・内容は Web ツール保持エージェントへ渡さない。利用者が結果から企業を選んだら、hub の Step 0 手順で company_index.json
  へスラッグ登録し、企業研究の求人票取込へ接続する。job-change-support（hub）から振り分けられて動く。
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

1. **無償の公開Web検索だけで探す。** 有償の求人API・会員限定の非公開求人には依存しない。検索方法のカタログは `references/query-catalog.md` にある（各サイトのログイン要否・URL構造・取得項目・制約・縮退方法）。会員登録が必要な求人を範囲外にした場合は、成果物の `coverage_notes` に記す。

2. **掲載ページの引用と出典URLを付す。** 各求人には、掲載ページからの引用（`quote`）と出典URL（`url`）・掲載サイト名（`source_site`）を必ず付す。取得できない求人を創作しない。給与が「応相談」等で数値が読めない場合は `salary_range` を `null` にする。

3. **匿名化を徹底する。** 検索担当エージェントへ渡す条件には、現勤務先名・氏名・現年収を含めない。希望年収の下限を条件に含めることは可とする。`profile.json` のパス・内容を Web ツール保持エージェントへ渡さない。条件はスキル本体が組み立て、匿名化した文字列としてのみ渡す。

4. **現勤務先の求人を除外する。** 検索結果に現勤務先の求人が含まれうる。除外はスキル本体がローカルで行う（`profile.json` を Web ツールへ渡さないため、除外判定はエージェントの外で行う）。

5. **個人情報を外部へ送信しない。** `profile.json`（現年収・在籍企業名・氏名等）を、検索クエリ・fetch・外部APIを含む一切の外部送信に用いない。非公開ディレクトリ `career-private/` 配下のパスを Web ツール保持エージェントへ渡さない。

## 範囲外

- **求人への応募・エージェント登録等の外部送信。** 応募フォームの送信・スカウト返信・転職エージェントへの登録は行わない。求人の収集までを支援し、応募は本人が行う。
- **企業研究・求人票の構造化取込。** 選んだ企業の企業研究（`company_research.json`）と求人票の構造化（`job_posting.json`）は job-change-company-research が担う。本スキルは検索結果を集め、選定後に企業研究へ接続する。
- **適合性評価。** 実質時給・拘束時間・7次元の適合性評価は job-change-fit-assessment が担う。本スキルは求人票の記載だけで判定できる8軸のスクリーニングにとどめ、企業研究・自己分析・通勤時間を要する評価は行わない。
- **利用者プロファイルの作成・管理。** profile.json の作成・更新・検証は hub（job-change-support）が担う。本スキルは PII リントの入力として profile.json をローカルで読むのみで、内容を外部へ渡さない。

## パスの解決

利用者データの置き場所は設定ファイルだけが決める。既定の置き場所を持たない。本文で `{DATA_ROOT}` と書いた箇所は、設定ファイルの `data_root` に読み替える。

hub（job-change-support）から振り分けられた場合は、hub が解決済みの `{DATA_ROOT}` を渡す。単独で起動された場合は、次の順に設定ファイルを探し、最初に見つかったものを Read で読む。

1. 環境変数 `JOB_CHANGE_CONFIG` が指すファイル
2. カレントディレクトリから上位へたどった最初の `.job-change/config.json`
3. `~/.job-change/config.json`

Bash が使える場合は、次のコマンドでも解決できる（`paths` に各データの絶対パスが入る）。

```bash
python {HUB_SKILL_DIR}/scripts/jc_config.py --show
```

いずれの場所にも設定ファイルが無ければ未設定である。その場合は作業へ進まず、hub（job-change-support）へ戻して設定の作成を先行させる。

`{SKILL_DIR}` は本スキルの絶対パス、`{HUB_SKILL_DIR}` は同じ配置先にある `job-change-support` の絶対パスを指す。設定ファイルの仕様は `docs/configuration.md` にある。

## データ配置

検索実行ごとに `job-search/{YYYYMMDD}-{条件の短いスラッグ}/` を作り、`job_search_results.json` を置く。企業別の成果物ツリー（`companies/{企業スラッグ}/`）とは別である。

| パス | 内容 |
|---|---|
| `job-search/{YYYYMMDD}-{条件の短いスラッグ}/job_search_results.json` | 求人検索の成果物。仕様は `references/job-search-format.md` |

- 条件の短いスラッグは、主条件をローマ字・英数字で表した簡潔な識別子とする（例: `remote-saas-be`）。日付は検索実行日（`executed_at`）に合わせる。
- スキル本体フォルダー（`skills/job-change-job-search/`）に実データを置かない。`assets/job_search_results_example.json` は架空の記入例である。

## 中間成果物: job_search_results.json

検索結果は `job_search_results.json`（`schema_version` は `2.0`）に集約する。構造は3層である。

| 層 | フィールド | 書き手 |
|---|---|---|
| 観測層 | `results[]` の title・company_name・url・source_site・salary_range・location・remote_policy・annual_holidays・match_notes・quote・better_points・`duty_items`・`axis_observations` | 検索担当エージェント（Web ツールを持つ。profile を読まない） |
| 判定層 | `results[]` の `axis_judgements`・`classification`・`classification_reasons`・`classification_override`・`slug` | スキル本体（ローカル。profile を読む） |
| 総括 | `screening`（分類ごとの件数・総合判定・軸ごとの未充足件数・現勤務先除外の実施記録） | スキル本体 |

この分離により、個人情報を Web ツール保持エージェントへ渡さずに条件判定が成立する。完全な仕様・記入基準・検証規則は `references/job-search-format.md` を原本とする。

## モード

### mode=fuzzy（曖昧条件検索）

利用者の曖昧な希望を構造化条件シートへ変換し、確認してから検索する。

1. 利用者の希望（例「リモート多め・年収600万以上・SaaS系」）を、次の軸へ構造化して条件シートを起草する。
   - 職種（`roles`）・業界（`industries`）・年収下限（`salary_min`、円単位の数値）・勤務地/リモート（`location`・`remote_policy`）・雇用形態（`employment_type`）・その他条件（`other`）。
   - 現勤務先名・氏名・現年収は条件に含めない（原則3）。希望年収の下限は `salary_min` として含めてよい。
2. 構造化した条件シートを AskUserQuestion で確認する。選択式を中心に、最大4問・各4択までとする。曖昧な軸（リモートの頻度・年収の下限・職種の範囲など）を優先して確認する。
3. 確認済みの条件を匿名化した文字列として、求人検索担当エージェント（job-change-job-searcher）へ渡し、`mode=fuzzy` で検索させる。

### mode=similar_better（類似高待遇検索）

基準求人から条件を抽出し、どの軸の改善を狙うかを確認してから検索する。

1. 基準求人を受け取る。所在は `companies/{企業スラッグ}/job_posting.json`（取込済みの求人票）または URL のいずれかである。URL を渡された場合、本スキルは WebFetch を持たないため条件を抽出できない。先に Skill ツールで `job-change-company-research` を起動して Step 0.5 の求人票取込を実行させ、作られた `job_posting.json` を基準求人にする。
2. 基準求人から職種・年収・年間休日・リモート方針・残業などの条件を抽出する。抽出時も、現勤務先名・氏名・現年収は条件へ持ち込まない。
3. どの軸の改善を狙うか（年収・休日・リモート・残業）を AskUserQuestion で確認する。
4. 抽出した基準条件と改善軸を匿名化した文字列として、求人検索担当エージェントへ渡し、`mode=similar_better` で検索させる。`baseline`（基準求人の URL または企業スラッグ）を成果物へ記録するよう指示する。エージェントは、基準求人の条件を上回る点を各求人の `better_points` に列挙する。

## パイプライン

`{SKILL_DIR}` は本スキルの絶対パス、`{results.json}` は成果物のパス（`job-search/{YYYYMMDD}-{スラッグ}/job_search_results.json`）に読み替える。

### Step 0 受付とモード判別

依頼が fuzzy（曖昧な希望からの検索）か similar_better（基準求人を上回る検索）かを判別する。基準となる求人・URLが示されていれば similar_better、漠然とした希望であれば fuzzy とする。判別が曖昧な場合は AskUserQuestion で確認する。

### Step 1 条件の組み立てと確認

モードに応じて条件を組み立て（上記「モード」の手順）、AskUserQuestion で確認する。ここで組み立てる条件は匿名化済みでなければならない（現勤務先名・氏名・現年収を含めない）。

### Step 2 検索の実行（job-change-job-searcher, sonnet）

求人検索担当エージェント（job-change-job-searcher）を Agent ツールで起動する。指示書には次を渡す。

- モード（`fuzzy` または `similar_better`）。
- 匿名化済みの検索条件（文字列。現勤務先名・氏名・現年収を含めない）。
- 出力先ディレクトリ（`job-search/{YYYYMMDD}-{スラッグ}/`）。
- similar_better の場合は基準条件・改善軸・`baseline`（URL または企業スラッグ）。
- 本スキルの絶対パス `{SKILL_DIR}`（`references/query-catalog.md`・`references/job-search-format.md` の所在）と、hub の絶対パス `{HUB_SKILL_DIR}`（`references/screening-axes.md` の所在）。
- **観測層まで**を書く指示（`duty_items` の引用文と分類、8軸の `axis_observations`）。判定層と `screening` は書かせない。

**profile.json は渡さない**（原則5。searcher は WebSearch・WebFetch を持つ）。**しきい値も渡さない。** 残業の上限・年間休日の下限・作業特性の希望は本人の条件であり、判定はスキル本体が Step 3.5 で行う。既に匿名化条件として許容されている `salary_min` だけは例外とし、検索条件に含めてよい。

エージェントは `references/query-catalog.md` の検索方法に従って求人を集め、`references/job-search-format.md` の形式で job_search_results.json を作る。8軸と業務分類の語彙は `{HUB_SKILL_DIR}/references/screening-axes.md` を読む。

### Step 3 現勤務先求人の除外（スキル本体）

エージェントが返した job_search_results.json から、現勤務先の求人をスキル本体がローカルで除外する。`career-private/profile.json` の `career_history` のうち在職中（`period` が `〜現在`）のエントリーの `company` に一致する `company_name` を持つ result を取り除く。除外した件数と企業名は、利用者への報告に含める（成果物には残さない）。

### Step 3.5 8軸判定と3分類（スキル本体）

検索担当エージェントが書くのは観測層（求人票から読めた事実）までである。本人の条件との突き合わせは、`profile.json` を読めるスキル本体がローカルで行う。この分担により、個人情報を Web ツール保持エージェントへ渡さずに条件判定が成立する。

1. `{DATA_ROOT}/career-private/profile.json` を Read で読み、`schema_version` を確認する。
2. `job_change_axis.conditions[]` と `work_character_preferences[]` から、8軸ごとの必須度（`must` / `want` / `none`）としきい値を読み取る。同じ軸に必須条件が複数ある場合は、最も厳しいしきい値を採る。
3. 各 result の `axis_observations` としきい値を突き合わせ、`axis_judgements` を書く。観測が `stated=false`、または `value` が `null` の軸は `unknown` にする。**記載が無いことを、条件を満たす証拠にも満たさない証拠にも使わない。**
4. `references/job-search-format.md` の決定表から `classification` を導き、`classification_reasons` を書く。導出結果を手で変える場合は、厳格化する方向にのみ `classification_override` を付ける。
5. `screening` を導出値として書く。`counts`・`unmet_axis_summary` は実集計と一致させる。`current_employer_exclusion` には Step 3 の実施結果を記録する（未実施なら `performed: false`・`excluded_count: null`）。

`profile.json` の `schema_version` が `1.0` または `1.1` の場合は縮退動作にする。観測層はそのまま残し、全軸を `level: none`・`judgement: unknown`、全 result を `needs_more_research`、`screening.axes_source` を `degraded`、`recommendation` を `判定不能` にする。分類結果を「応募候補」として提示せず、`job-change-profile` での条件の構造化を案内する。

判定に使う語彙（8軸・8作業特性・業務分類）の原本は、hub（`job-change-support`）の `references/screening-axes.md` にある。

### Step 4 機械検証と PII リント（スキル本体）

除外後の job_search_results.json を、`--profile` 付きで検証する。

```bash
python {SKILL_DIR}/scripts/validate_job_search_results.py {results.json} --profile {DATA_ROOT}/career-private/profile.json
```

`--profile` により、スキーマ検査に加えて PII リント（現勤務先名・氏名・現年収の混入検出）が働く。ERROR が1件でもあれば FAIL である。PII 混入の ERROR が出た場合は、混入箇所を成果物から除去してから再検証する（匿名化の漏れであり、そのまま納品しない）。PASS（ERROR 0件）を確認してから納品する。profile.json の読み取りはこの検証のためのローカル処理に閉じ、外部へ送信しない。

### Step 5 納品と接続

検証 PASS の job_search_results.json を納品する。報告は分類ごとにまとめ、`screening.recommendation` を先に述べる。

1. 総合判定として `screening.recommendation` と `rationale` を最初に伝える。`応募推奨なし` の場合は、その旨を明記し、無理に最有力候補を選ばない。
2. `classification` が `apply_candidate` の求人を、満たしている必須条件とともに列挙する。
3. `needs_more_research` の求人を、判定できなかった軸（`unknown` の軸）と、それを確認する手段（企業研究か面接か）とともに列挙する。
4. `excluded` の求人を、満たさなかった必須条件とともに簡潔に列挙する。注意書きを付け、応募候補と同じ表には並べない。
5. 利用者が企業を選んだら、hub（job-change-support）の Step 0 手順で `career-private/company_index.json` へ企業スラッグを登録し、`companies/{企業スラッグ}/` を作り、当該 result の `slug` へ追記する。続いて job-change-company-research の Step 0.5（求人票取込）へ接続する。求人ページの URL があればそれを入口とし、無ければ、検索結果へ写し取った掲載内容を本文として渡す。

similar_better では各求人の `better_points`（基準求人より改善している点）を併記する。

#### 報告のルール

**検証していない事項を成果として報告しない。** 報告してよい数値は次に限る。

| 報告してよい数値 | 出所 |
|---|---|
| 分類ごとの件数 | `screening.counts` |
| 軸ごとの未充足・判定不能の件数 | `screening.unmet_axis_summary` |
| 現勤務先求人の除外件数 | `screening.current_employer_exclusion.excluded_count`（`performed` が `true` のときのみ） |

`current_employer_exclusion.performed` が `false` の項目は「未検証」と書く。「0件」と書かない。機械検証の PASS は「形式が整い、PII が混入しておらず、分類と総合判定が軸判定と整合している」ことを示すのであって、求人が本人に合っていることを示すのではない。この区別を報告に反映する。

## 合否ゲート

| ゲート | 通過条件と差し戻し先 |
|---|---|
| Step 4 の機械検証・PII リント | `validate_job_search_results.py --profile` が PASS（ERROR 0件）でなければ納品しない。PII 混入の ERROR は匿名化の漏れであり、成果物から除去してから再検証する。 |
| 応募推奨 | `screening.recommendation` が `応募推奨なし` の場合、既定では企業研究・適合性評価へ接続しない。必須条件の見直し（`job-change-profile` の条件更新）、または検索条件・検索経路の見直しへ戻す。応募候補が0件のときに、除外候補や追加調査候補から最有力候補を仕立てない。**例外**: 満たさない必須条件を求人ごとにすべて列挙したうえで、利用者が特定の求人について先へ進むことを明示的に希望した場合は、その求人を企業研究へ接続してよい。この判定の材料は求人票の記載だけであり、判定そのものが企業研究や面接で覆りうるためである。接続する場合は、どの必須条件が未充足のままかを引き継ぎに明記する。利用者が希望していないのに、本スキルから接続を提案しない。 |
| 縮退の明示 | `screening.recommendation` が `判定不能`（profile が 1.x）の場合、判定できていない旨を明示する。分類結果を「応募候補」として提示せず、`job-change-profile` での条件の構造化を案内する。 |

## 役割の実行（ハーネス別）

本スキルのパイプラインは、専門の役割へ作業を委ねる形で書いてある。役割の内容は `references/roles/` に置き、これを原本とする。

| エージェント名 | 役割プロンプトの原本 |
|---|---|
| `job-change-job-searcher` | `{SKILL_DIR}/references/roles/job-searcher.md` |

**サブエージェントを起動できるハーネス（Claude Code）。** 各 Step の記述どおり、上表のエージェント名を Agent ツールで起動し、指示書を渡す。エージェント定義はリポジトリの `agents/` にあり、`references/roles/` から同期生成されている。

**サブエージェントを起動できないハーネス（Codex ほか）。** 各 Step の「エージェントを起動する」を「役割プロンプトを読み、その役割として自分で実行する」と読み替える。手順は次のとおり。

1. 上表の役割プロンプトを Read で読む。
2. Step に書かれた指示書の項目を、そのまま自分への指示として扱う。
3. 役割プロンプトの「扱ってよい入力」のルールを守る。Web 送信手段を持たない役割として書かれている場合、その作業中は Web 検索・fetch を使わない。
4. 成果物の形式・検証・合否ゲートは、ハーネスによらず同一である。

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

`--json` は結果を JSON 形式（`status`・`error_count`・`warning_count`・`errors`・`warnings`）で出力する。`--profile` を付けると、PII リント（現勤務先名・氏名・現年収の混入検出）に加え、`threshold_ref` が profile の条件・特性に実在するか、`level` が profile の必須度と一致するかを検査する。`--profile` を付けずに実行すると、それらが未実施である旨の WARN が出る。記述例は `assets/job_search_results_example.json`、フィールド仕様と検証規則の原本は `references/job-search-format.md` にある。単体テストは次で実行する。

```bash
cd {SKILL_DIR} && python -m unittest discover -s scripts/tests
```

## references 一覧

| ファイル | 何を | いつ読むか |
|---|---|---|
| `references/job-search-format.md` | job_search_results.json のフィールド仕様・記入基準・機械検証規則・PII リント | 成果物を作る/読む/検証する全段階 |
| `references/query-catalog.md` | 無償の公開Web検索で求人を探す方法（サイト別のログイン要否・URL構造・取得項目・制約・縮退方法） | Step 2 の検索、検索担当エージェントへの指示 |
| `references/search-methods.md` | 探索の量と就業の質の関係、満足化の運用、観測と判定を分ける理由の根拠（出典付き） | 報告のしかたを決める段階、応募推奨なしのときの提案を組み立てる段階 |
| `{HUB_SKILL_DIR}/references/screening-axes.md` | 8スクリーニング軸・8作業特性・業務分類の語彙と境界例 | Step 2 の観測、Step 3.5 の判定 |
| `references/roles/job-searcher.md` | 検索担当の役割プロンプト（観測層までを担う） | Step 2。サブエージェントを使えないハーネスでは本体が読む |
