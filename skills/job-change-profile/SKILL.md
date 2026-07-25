---
name: job-change-profile
description: >-
  転職支援スキル群の profile.json 作成・更新に特化したサブスキル。利用者データの単一の原本である
  profile.json を、構造化した想起手がかり（時系列×プロジェクト単位）で聞き取り、実績の定量化・スキルの棚卸し・
  転職の軸の構造化を支援し、起草・機械検証・独立監査を経て作る。聞き取りは AskUserQuestion の選択式を中心に、
  1回最大4問×各4択で行い、自由記述は企業名・期間・実績値など選択式にできない項目に限る。日付・年収・実績値のうち記憶が曖昧なものについては、手元の証憑での任意確認を案内し、単純な誤記を予防する。起草と独立監査は専用エージェント
  （job-change-profile-writer / job-change-profile-auditor）が担う。job-change-support（hub）から振り分けられて動く。
  強みの根拠づけ・キャリアの物語化は job-change-self-analysis、応募書類の文面は job-change-documents が担う。
  Use when the user creates or updates a job-change profile in Japan — registering career history, taking stock of
  skills, quantifying achievements, or structuring must/want conditions into profile.json.
  trigger words: プロファイルを作りたい, 経歴を登録, 職務経歴の棚卸し, プロファイルを更新, 職歴の登録,
  実績の定量化, スキルの棚卸し, 転職の軸を登録。
allowed-tools: Read, Write, Glob, Grep, Bash, AskUserQuestion, Agent, Skill
---

# job-change-profile

転職支援スキル群で利用者データの単一の原本となる profile.json を作る、または更新するとき、このスキル1つで聞き取りから納品までの手順が揃う。構造化した想起手がかり（企業→在籍期間→役割→担当プロジェクト→成果の時系列枠）で聞き取り、実績の定量化・スキルの棚卸し・転職の軸の構造化を支援し、起草・機械検証・独立監査を経て profile.json を確定する。成果物は後続のサブスキル（企業研究・応募書類作成・面接対策・試験対策・自己分析）がすべて入力として読む。

profile.json の中核は、職務経歴・実績・スキルの内容と、それが求人要件へどう対応するかという点（relevance）である（根拠は `references/profile-methods.md`）。ただし関連性（relevance）は応募先ごとに変わるため、profile.json には固定して保持しない。応募時に応募書類サブスキルが再構成する。本スキルは、応募先ごとの relevance を再構成できる粒度（職務単位の経歴・成果・定量値）の正確性・網羅性・鮮度を保つことに責任を持つ。

## 目的と原則

1. **構造化した想起手がかりで聞き取る。** 自由記述に委ねず、時系列（在籍期間）×プロジェクト単位の枠に沿って聞く。構造化面接は非構造化面接の約2倍の妥当性を持ち、時系列・テーマ横断のカレンダー型手がかりは自伝的記憶の構造に沿って回顧の完全性・一貫性を高める（`references/elicitation-guide.md`）。

2. **自己報告の日付・実績値は任意の自己確認を案内する。** 作業歴の自己報告には内在的な誤差があり、日付は、実際より最近の出来事として記憶しやすい系統バイアス（前方テレスコーピング）を受ける。日本の採用実務では社会保険・源泉徴収・前職への照会（リファレンスチェック）で客観的に照合され、矛盾が露見する。そこで、日付・年収・実績値のうち記憶が曖昧なものに限り、手元にある証憑（源泉徴収票・雇用保険の記録など）での任意の自己確認を案内する。書類の提出を求めるものではなく、証憑が手元に無ければ省いてよい。在籍期間・年収の情報を持たない書類（健康保険証など）は用いない（`references/elicitation-guide.md`、確認様式は `assets/verification_checklist.md`）。

3. **実績は定量化を推奨しつつ、検証可能性を優先する。** 定量化困難な業務には、頻度・規模・対応人数・工程削減率・定性成果との接続という代替表現の型を用意する。ただし全実績への機械的な数値付与は強制しない。検証できない数値・過剰な数値は書類全体の信頼を毀損する（`references/quantification-guide.md`）。

4. **スキルは専門スキルと転用可能スキルを分ける。** technical / business / languages / certifications を入口としつつ、厚労省ポータブルスキルの9要素（対課題5・対人4）を補助分類として持ち、専門スキルと転用可能スキルを分けて棚卸しする。汎用分類の一律適用に依存しない（`references/profile-methods.md`）。

5. **転職の軸は必須条件を少数に絞り、再評価を前提とする。** 譲れない条件と望ましい条件の分離を維持しつつ、必須条件（`conditions[level=must]` と `work_character_preferences[desire=must]` の合計）を3件程度までに絞り、優先順位と再評価時期をメタ情報として残す。選好は聞き取りの過程で構成され経時変化するため、軸を固定した結論として扱わない（`references/profile-methods.md`）。深掘り（建設的言い換え・根拠づけ）は `job-change-self-analysis` へ誘導する。

6. **事実を捏造・補完しない。** profile.json に載せる経歴・実績・数値は、聞き取りメモに記録のある範囲に限る。実績値・期間・役職を推測で補完しない。捏造は懲戒・内定取消につながり、社会保険等の突合で高い確率で発覚する（`references/profile-methods.md`）。

7. **個人情報を外部へ送信しない。** profile.json に含まれる個人情報（現年収・希望年収・居住地・学歴・在籍企業名・実績など）は、検索クエリ・fetch・外部 API を含む一切の外部送信に用いない。非公開ディレクトリ `career-private/` 配下のパス（`profile.json`・`profile_interview_notes.md`）は、Web 送信手段（WebSearch・WebFetch）を持つエージェントへ一切渡さない。本スキルの writer・auditor は Web 送信手段を持たないため、これらのパスを渡してよい。

## 範囲外

次は本スキルの範囲外とする。依頼された場合は、対応できない旨と、代わりの担当・行動を伝える。

- **強みの根拠づけ・キャリアの物語化・退職理由の建設的言い換え。** `job-change-self-analysis` が担う。本スキルは軸の構造（reasons の短文）までを扱い、深掘りは `job-change-self-analysis` へ誘導する。
- **応募書類の文面作成。** 職務経歴書・履歴書・英文レジュメ・志望動機書の執筆は `job-change-documents` が担う。本スキルはその土台データ（profile.json）を作り、渡す。
- **企業別の要件対応づけ（アピールマッピング）。** relevance は応募先ごとに変わるため profile に固定保持しない。応募時に `job-change-documents` が profile.json の職務単位データから再構成する。
- **企業研究。** 企業の理念・事業・評判の調査は `job-change-company-research` が担う。

## パスの解決

利用者データの置き場所は設定ファイルだけが決める。既定の置き場所を持たない。本文で `{DATA_ROOT}` と書いた箇所は、設定ファイルの `data_root` に読み替える。

hub（job-change-support）から振り分けられた場合は、hub が解決済みの `{DATA_ROOT}` を渡す。単独で起動された場合は、次の順に設定ファイルを探し、最初に見つかったものを Read で読む。

1. 環境変数 `JOB_CHANGE_CONFIG` が指すファイル
2. カレントディレクトリから上位へ辿った最初の `.job-change/config.json`
3. `~/.job-change/config.json`

Bash が使える場合は、次のコマンドでも解決できる（`paths` に各データの絶対パスが入る）。

```bash
python {HUB_SKILL_DIR}/scripts/jc_config.py --show
```

いずれの場所にも設定ファイルが無ければ未設定である。その場合は作業へ進まず、hub（job-change-support）へ戻して設定の作成を先行させる。

`{SKILL_DIR}` は本スキルの絶対パス、`{HUB_SKILL_DIR}` は同じ配置先にある `job-change-support` の絶対パスを指す。設定ファイルの仕様は `docs/configuration.md` にある。

## データ配置

利用者データは、非公開ディレクトリ `{DATA_ROOT}/career-private/` に置く。本スキルが読み書きするパスは次のとおり。

| パス | 役割 | 入出力 |
|---|---|---|
| `career-private/profile.json` | 利用者プロファイルの単一の原本 | 出力（本スキルが作る・更新する） |
| `career-private/profile_interview_notes.md` | 聞き取りメモ | 出力（聞き取り中に本体セッションが逐次追記。中断再開に対応） |

- profile.json のフィールド仕様・記入基準・検証規則の原本は hub（`job-change-support`）の `references/profile-format.md` にある。本スキルはこれを編集しない。
- 記入例は hub の `assets/profile_example.json`（架空の人物）にある。本スキル側に複製を置かない。
- スキル本体フォルダ（`skills/job-change-profile/`）に利用者データを置かない。
- `career-private/` が未作成の場合は、必要になった時点で本スキルが作る。

## パイプライン

受付から納品まで Step 0〜6 を順に進める。`{SKILL_DIR}` は本スキルの絶対パス、`{HUB_SKILL_DIR}` は hub（`job-change-support`）の絶対パス、`{PROFILE}` は `profile.json` の絶対パス、`{NOTES}` は `profile_interview_notes.md` の絶対パスに読み替える。

聞き取りは本体セッションが AskUserQuestion で行う（サブエージェントは利用者と対話できない）。選択式を中心に、1回の AskUserQuestion につき最大4問・各質問は最大4択とする。自由記述は、企業名・在籍期間・実績値のように選択式にできない項目に限る。質問は `references/question-bank.md` の有限の構造化質問を使い、反芻を招く自由回答の質問を置かない。

### Step 0 前提確認

- `profile.json` の有無を確認する。有れば hub の `validate_profile.py` で検証し、現状を把握する。
- モードを AskUserQuestion で確認する。選択肢は「初回作成」「区画更新（basic / 職歴 / スキル / 軸 / 志望 / 年収 のどれか）」「全面点検」。
- 更新モードでは、既存の profile.json を読み、対象区画のみを聞き取り対象にする。

### Step 1 職歴の骨格（時系列）

古い順または新しい順に、企業×在籍期間×役割の一覧をまず確定する。転職・異動・昇進などの転機を時系列の手がかりにする。カレンダー型（時系列×テーマ横断）の想起手がかりは自伝的記憶の構造に沿い、回顧の完全性・一貫性を高める（`references/elicitation-guide.md`）。骨格を確定したら、隣接する職歴間の空白期間（6ヶ月以上）を機械的に検出し、その場で説明と期間中の活動を聞き、`career_gaps` に記録する。在籍中の職は period を `〜現在` と書く。

### Step 2 職務ごとの深掘り（プロジェクト単位）

職歴1件ずつ、担当業務（responsibilities）→主要プロジェクト→実績（achievements）の順で聞く。実績については「何を・どの規模で・どう変えたか」を聞く。定量化は `references/quantification-guide.md` の型（前年度比・件数・頻度・規模・対応人数・工程削減率・定性成果の接続）で支援する。数値が出ない実績は無理に数値化せず、工夫や評価された点を具体化して `metric` を `null` にする。検証できない数値は書かない。

### Step 3 スキル棚卸し

technical / business / languages / certifications を、Step 2 の発話から逆引きで確認する（候補を選択肢として提示し、選ばせる）。そのうえで、厚労省ポータブルスキルの9要素（対課題5・対人4）を選択式で確認し、`skills.portable` に入れる（category は「対課題」か「対人」）。要件との対応づけは応募時に応募書類サブスキルが行う旨を伝える。詳細は `references/profile-methods.md` のスキル分類の節にある。

### Step 4 転職の軸・志望対象・年収

reasons（1件以上必須）→ 条件（`conditions`）→ 作業特性の希望（`work_character_preferences`）→ targets → salary の順で聞く。軸の建設的言い換え・根拠づけは `job-change-self-analysis` へ誘導する。根拠は `references/profile-methods.md` の must/want の節による。

#### 条件の構造化

条件は自由文ではなく、軸・演算子・閾値の形で構造化して `job_change_axis.conditions[]` へ入れる。フィールド仕様は hub の `references/profile-format.md`、軸の語彙は hub の `references/screening-axes.md` を読む。この構造化により、求人検索が求人票の記載と条件を機械的に突き合わせられるようになる。

条件1件ごとに、次を AskUserQuestion で確定する（1回の質問で複数の条件をまとめて扱ってよい）。

1. 譲れない条件か、あれば望ましい条件か（`level`）。
2. 8軸のどれに当たるか、または軸に当てはまらない質的条件か（`axis`）。
3. 軸に当たる場合は、比較のしかたと閾値（`operator`・`value`・`unit`）。例: 残業なら「月何時間以下か」、年間休日なら「年何日以上か」、年収なら「下限はいくらか」。
4. どこで確認できるか（`verification`）。求人票の記載で判定できるものは `posting`、企業研究が要るものは `research`、面接で聞くしかないものは `interview` とする。

軸に当てはまらない質的条件（例「モダンな技術スタックが整備されていること」）は、`axis` を `null`、`operator` を `qualitative`、`value` を `null` にし、`verification` を `research` または `interview` にする。この種の条件は求人検索の分類には用いられず、企業研究と面接での確認へ回る旨を利用者へ伝える。

#### 作業特性の希望

8つの作業特性それぞれについて、希望度（`must` / `important` / `neutral` / `not_required`）を確認する。特性の定義は hub の `references/screening-axes.md` にある。2回の AskUserQuestion（4特性ずつ）で埋まる。

「どちらでもよい」「不要である」も明示的に選ばせる。未記入のまま置くと、下流が推測で補う余地が生じるためである。`desire=must` を選んだ特性には、本人の言葉での条件文（`statement`）を1文で聞く。

`clear_completion`・`solo_completable`・`short_feedback` の3特性は求人票からは判定できない。これらに `must` や `important` を選んだ場合は、面接での確認事項になる旨をその場で伝える。

#### 必須条件の件数

`conditions[level=must]` と `work_character_preferences[desire=must]` の合計が4件以上になったら、優先順位を付けて絞る対話を挟む。必須条件が多いほど、求人検索が「応募推奨なし」を返しやすくなる。順位と再評価時期を `job_change_axis.priority_note` へ残す。

#### 1.x からの移行

既存の `profile.json` が `schema_version` `1.0` または `1.1` の場合、`must_conditions` / `want_conditions` の自由文が残っている。**機械的に軸へ割り付けない。** 自由文から閾値を推測することは事実の創作に当たる。

移行モードでは、既存の自由文を1件ずつ提示し、上記「条件の構造化」の4項目を対話で確定する。全件を移し終えたら `must_conditions` / `want_conditions` を空配列にし、続けて作業特性8件を確認する。最後に `schema_version` を `2.0` へ、`updated_at` を当日へ書き換える。

利用者が移行を望まない場合は 1.x のまま残す。その場合、求人検索の8軸判定と適合性評価の作業特性の次元が働かない旨を1回だけ伝える。

### Step 5 起草→機械検証→独立監査

聞き取りの結果は、その途中で本体セッションが `{NOTES}`（`profile_interview_notes.md`）へ逐次追記し集約しておく（中断再開に対応）。`job-change-profile-writer` エージェント（model: opus）を起動し、`{NOTES}`・既存 `{PROFILE}`（更新時）・hub の `references/profile-format.md`・出力先 `{PROFILE}` を渡す。起草担当はメモにある事実だけから profile.json を起草・更新する。戻り値を受け、本体セッションが hub の `validate_profile.py` を実行して ERROR 0 を確認する。続いて `job-change-profile-auditor` エージェント（model: opus、起草担当の判断理由を渡さない新規コンテキスト）を起動して監査する。`verdict` が BLOCK、または `severity` = must_fix の finding があれば Step 5 の起草へ差し戻す（最大2回。以降は利用者判断）。

### Step 6 任意の自己確認と更新運用

日付・年収・実績値のうち記憶が曖昧なものについて、手元にある証憑（源泉徴収票・雇用保険の記録など）での任意の自己確認を案内する（様式は `assets/verification_checklist.md`）。書類の提出を求めるものではなく、手元に無ければ省いてよい。更新運用（実績が出るたびに追記し、少なくとも四半期に一度は見直す。応募書類へ書き起こすときは直近7〜10年を優先する）を案内し、`updated_at` を当日の日付へ書き換える。最後に、profile.json を入力に使える下流の作業（`job-change-self-analysis` の自己分析、`job-change-company-research` の企業研究、`job-change-documents` の応募書類作成）を案内する。

## 合否ゲートと差し戻し

パイプラインには1つの検証・監査ゲートがある。

| ゲート | 通過条件と差し戻し先 |
|---|---|
| Step 5 の検証・監査ゲート | hub の `validate_profile.py` が FAIL（ERROR 1件以上）の場合、または `job-change-profile-auditor` の `verdict` が BLOCK の場合、または `severity` = must_fix の finding がある場合は、Step 5 の起草へ差し戻す。差し戻しは同一成果物につき最大2回まで行う。 |

差し戻し時は、監査の findings（target・evidence・fix）をそのまま起草担当へ渡し、反映後に Step 5 の機械検証から再度通す。2回の差し戻しで解消しない指摘は、未決事項として利用者へ判断を委ねてから納品する（例: 聞き取りメモだけでは実績値の裏付けが足りない、という指摘は、証憑での確認が要るため利用者の判断事項とする）。

## 役割の実行（ハーネス別）

本スキルのパイプラインは、専門の役割へ作業を委ねる形で書いてある。役割の内容は `references/roles/` に置き、これを原本とする。

| エージェント名 | 役割プロンプトの原本 |
|---|---|
| `job-change-profile-writer` | `{SKILL_DIR}/references/roles/profile-writer.md` |
| `job-change-profile-auditor` | `{SKILL_DIR}/references/roles/profile-auditor.md` |

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
| `job-change-profile-writer` | opus | 聞き取りメモから profile.json を起草・更新（Step 5）と監査指摘の反映。メモに無い事実を創作しない |
| `job-change-profile-auditor` | opus | 独立コンテキストでの創作・誇張・時系列整合・metric 検証可能性・軸の件数の監査、検証器の再実行（Step 5） |

起草はメモの事実への忠実さと粒度の判断を、監査は創作・誇張の検出と時系列整合の裁定を要し、いずれも判断負荷が高いため両者を opus とする。機械的検査は hub の `validate_profile.py` が担う。model は各エージェントの frontmatter に固定済みであり、起動時に上書きしない。

## スクリプトのCLI使用例

profile.json の検証には hub（`job-change-support`）の `validate_profile.py` を用いる（本スキルは検証スクリプトを持たない。二重管理しない）。終了コードは PASS で 0、FAIL で 1、WARN のみは PASS 扱いである。`{HUB_SKILL_DIR}` は hub の絶対パス、末尾のパスは検証対象の profile.json のパスに読み替える。

```bash
python {HUB_SKILL_DIR}/scripts/validate_profile.py {DATA_ROOT}/career-private/profile.json
python {HUB_SKILL_DIR}/scripts/validate_profile.py {DATA_ROOT}/career-private/profile.json --json
```

`--json` は結果を JSON 形式（`status`・`error_count`・`warning_count`・`errors`・`warnings`）で出力する。profile.json のフィールド仕様・検証規則の原本は hub の `references/profile-format.md`、記入例は hub の `assets/profile_example.json` にある。

## references 一覧

| ファイル | 何を | いつ読むか |
|---|---|---|
| `references/elicitation-guide.md` | 時系列×プロジェクト単位の想起手がかりの根拠、自己報告の内在誤差と任意の自己確認、空白期間の扱い、選択式優先の運用、更新運用、DOI/URL 付き出典 | 聞き取りの方針を定めるとき、監査の観点を確認するとき |
| `references/question-bank.md` | Step 1〜4 で使う有限の構造化質問と、各質問が埋めるフィールドの対応表、AskUserQuestion 用の選択肢案 | ヒアリングの各 Step で質問を選ぶとき |
| `references/quantification-guide.md` | 定量化の型と代替表現、検証可能性の優先と捏造リスク、定量化の効果の限界、職種依存、DOI/URL 付き出典 | 実績の聞き取り・起草・監査で定量表現を判断するとき |
| `references/profile-methods.md` | 採用側が見る情報、スキル分類、must/want の根拠と限界、ATS の実像、経歴詐称の帰結、設計の限界とエビデンスギャップ、DOI/URL 付き出典 | 設計判断の根拠を確認するとき、監査の観点を定めるとき |
