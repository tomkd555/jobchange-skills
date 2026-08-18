---
name: job-change-profile
description: >-
  転職支援スキル群の profile.json 作成・更新に特化したサブスキル。利用者データの単一の原本である
  profile.json を、構造化した想起手がかり（時系列×プロジェクト単位）で聞き取り、実績の定量化・スキルの棚卸し・
  転職の軸の構造化を支援し、作成・機械的な検証・独立監査を経て作る。聞き取りは AskUserQuestion の選択式を中心に、
  1回最大4問×各4択で行い、自由記述は企業名・期間・実績値など選択式にできない項目に限る。兼務・出向・副業のような同時期の複数所属と、1つの職の中で並行して回した複数の案件のどちらも記録できる。作成と独立監査は専用エージェント
  （job-change-profile-writer / job-change-profile-auditor）が担う。job-change-support（hub）から振り分けられて動く。
  強みの根拠づけ・キャリアの物語化は job-change-self-analysis、応募書類の文面は job-change-documents が担う。
  Use when the user creates or updates a job-change profile in Japan — registering career history, taking stock of
  skills, quantifying achievements, or structuring must/want conditions into profile.json.
  trigger words: プロファイルを作りたい, 経歴を登録, 職務経歴の棚卸し, プロファイルを更新, 職歴の登録,
  実績の定量化, スキルの棚卸し, 転職の軸を登録。
allowed-tools: Read, Write, Glob, Grep, Bash, AskUserQuestion, Agent, Skill
---

# job-change-profile

転職支援スキル群で利用者データの単一の原本となる profile.json を作る、または更新するとき、このスキル1つで聞き取りから納品までの手順がそろう。構造化した想起手がかり（企業→在籍期間→役割→担当プロジェクト→成果の時系列枠）で聞き取り、実績の定量化・スキルの棚卸し・転職の軸の構造化を支援し、作成・機械的な検証・独立監査を経て profile.json を確定する。成果物は後続のサブスキル（企業研究・応募書類作成・面接対策・試験対策・自己分析）がすべて入力として読む。

profile.json の中核は、職務経歴・実績・スキルの内容と、それが求人要件へどう対応するかという点（relevance）である（根拠は `references/profile-methods.md`）。ただし関連性（relevance）は応募先ごとに変わるため、profile.json には固定して保持しない。応募時に応募書類サブスキルが再構成する。本スキルは、応募先ごとの relevance を再構成できる粒度（職務単位の経歴・成果・定量値）の正確性・網羅性・鮮度を保つことに責任を持つ。

## 目的と原則

1. **構造化した想起手がかりで聞き取る。** 自由記述に委ねず、時系列（在籍期間）×プロジェクト単位の枠に沿って聞く。構造化面接は非構造化面接の約2倍の妥当性を持ち、時系列・テーマ横断のカレンダー型手がかりは自伝的記憶の構造に沿って想起の完全性・一貫性を高める（`references/elicitation-guide.md`）。

2. **利用者の申告を裏取りしない。** 述べられた経歴・実績・数値は、そのまま事実として記録する。証拠書類の提示を求めず、「それは証明できるか」という形の問いを置かない。本人が自分から不確かだと述べた値だけ、その旨をメモへ残す（`references/elicitation-guide.md`）。創作の抑止は、作成担当が聞き取りメモにある事実だけを使い、監査担当が成果物とメモを照合することで働く（原則6）。

3. **実績は定量化を推奨しつつ、無理に数値化しない。** 定量化困難な業務には、頻度・規模・対応人数・工程削減率・定性成果との接続という代替表現の型を用意する。ただし全実績への機械的な数値付与は強制しない。過剰な数値は書類全体の信頼を毀損する（`references/quantification-guide.md`）。

4. **スキルは専門スキルと転用可能スキルを分ける。** technical / business / languages / certifications を入口としつつ、厚労省ポータブルスキルの9要素（対課題5・対人4）を補助分類として持ち、専門スキルと転用可能スキルを分けて棚卸しする。汎用分類の一律適用に依存しない（`references/profile-methods.md`）。

5. **転職の軸は必須条件を少数に絞り、再評価を前提とする。** 譲れない条件と望ましい条件の分離を維持しつつ、必須条件（`conditions[level=must]` と `work_character_preferences[desire=must]` の合計）を3件程度までに絞り、優先順位と再評価時期をメタ情報として残す。選好は聞き取りの過程で構成され経時変化するため、軸を固定した結論として扱わない（`references/profile-methods.md`）。深掘り（建設的言い換え・根拠づけ）は `job-change-self-analysis` へ誘導する。

6. **事実を創作・補完しない。** profile.json に載せる経歴・実績・数値は、聞き取りメモに記録のある範囲に限る。実績値・期間・役職を推測で補完しない。経歴の詐称は懲戒・内定取消につながり、社会保険等の突合で高い確率で発覚する（`references/profile-methods.md`）。

7. **個人情報を外部へ送信しない。** profile.json に含まれる個人情報は、検索クエリ・fetch・外部 API を含む一切の外部送信に用いない。対象の列挙と役割ごとの可否の原本は hub の `{HUB_SKILL_DIR}/references/pii-boundary.md` にある。本スキルは境界の内側にある `profile.json`・`profile_interview_notes.md` を作る側であり、writer（job-change-profile-writer）・auditor（job-change-profile-auditor）はいずれも Web 送信手段を持たないため、これらのパスを渡してよい。

## 範囲外

次は本スキルの範囲外とする。依頼された場合は、対応できない旨と、代わりの担当・行動を伝える。

- **強みの根拠づけ・キャリアの物語化・退職理由の建設的言い換え。** `job-change-self-analysis` が担う。本スキルは軸の構造（reasons の短文）までを扱い、深掘りは `job-change-self-analysis` へ誘導する。
- **応募書類の文面作成。** 職務経歴書・履歴書・英文レジュメ・志望動機書の執筆は `job-change-documents` が担う。本スキルはその土台データ（profile.json）を作り、渡す。
- **企業別の要件対応づけ（アピールマッピング）。** relevance は応募先ごとに変わるため profile に固定保持しない。応募時に `job-change-documents` が profile.json の職務単位データから再構成する。
- **企業研究。** 企業の理念・事業・評判の調査は `job-change-company-research` が担う。

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
| `career-private/profile.json` | 利用者プロファイルの単一の原本 | 出力（本スキルが作る・更新する） |
| `career-private/profile_interview_notes.md` | 聞き取りメモ。記載形式の原本は `references/elicitation-guide.md` にある | 出力（聞き取り中に本体セッションが逐次追記。中断再開に対応） |

- profile.json のフィールド仕様・記入基準・検証規則の原本は hub（`job-change-support`）の `references/profile-format.md` にある。本スキルはこれを編集しない。
- 記入例は hub の `assets/profile_example.json`（架空の人物）にある。本スキル側に複製を置かない。
- スキル本体フォルダー（`skills/job-change-profile/`）に利用者データを置かない。
- `career-private/` が未作成の場合は、必要になった時点で本スキルが作る。

## パイプライン

受付から納品まで Step 0〜6 を順に進める。`{SKILL_DIR}` は本スキルの絶対パス、`{HUB_SKILL_DIR}` は hub（`job-change-support`）の絶対パス、`{PROFILE}` は `profile.json` の絶対パス、`{NOTES}` は `profile_interview_notes.md` の絶対パスに読み替える。

聞き取りは本体セッションが AskUserQuestion で行う（サブエージェントは利用者と対話できない）。選択式を中心に、1回の AskUserQuestion につき最大4問・各質問は最大4択とする。1つの問いで複数の答えを受けたい場合は `multiSelect: true` を使い、問いを分けて回数を増やさない。自由記述は、企業名・在籍期間・実績値のように選択式にできない項目に限る。質問は `references/question-bank.md` の有限の構造化質問を使い、反すうを招く自由回答の質問を置かない。利用者へ発する質問文と選択肢のラベルは敬体で書く。選択肢を事前に列挙できる質問については、`references/question-bank.md` に確定した文言があり、それをそのまま使う（言い回しをその場で作らない）。

### Step 0 前提確認

- `profile.json` の有無を確認する。有れば hub の `validate_profile.py` で検証し、現状を把握する。
- モードを AskUserQuestion で確認する。選択肢は「初回作成」「セクション更新（basic / 職歴 / スキル / 軸 / 志望 / 年収 のどれか）」「全面点検」。
- 更新モードでは、既存の profile.json を読み、対象セクションのみを聞き取り対象にする。

### Step 1 職歴の骨格（時系列）

古い順または新しい順に、企業×在籍期間×役割の一覧をまず確定する。転職・異動・昇進などの転機を時系列の手がかりにする。根拠は `references/elicitation-guide.md` にある。在籍中の職は period を `〜現在` と書く。

骨格が出そろったら、同じ時期に複数の職に就いていた期間があったかを1問で確かめる（兼務・出向・副業・自営）。あった場合は、その職も `career_history` の1件として企業・期間・役割を聞き、どの立場での在籍かを `role` に書き分ける（例「業務委託（副業）」）。在籍期間が重なることは不整合ではない。

並行の在籍を含めて骨格が確定したら、どの職歴の在籍期間にも覆われない期間（6か月以上）を機械的に検出し、その場で説明と期間中の活動を聞き、`career_gaps` に記録する。判定は全職歴の在籍期間の和集合に対して行う。隣どうしの職歴だけを見ると、本業と重なる副業がある場合に存在しない空白を検出する。

### Step 2 職務ごとの深掘り（プロジェクト単位）

職歴1件ずつ、担当業務（responsibilities）→主要プロジェクト→実績（achievements）の順で聞く。実績については「何を・どの規模で・どう変えたか」を聞く。定量化は `references/quantification-guide.md` の型（前年度比・件数・頻度・規模・対応人数・工程削減率・定性成果の接続）で支援する。数値が出ない実績は無理に数値化せず、工夫や評価された点を具体化して `metric` を `null` にする。利用者が述べた数値は、その出所を問わずそのまま記録する。

1つの職の中で複数の案件を並行して回していた場合は、実績1件ごとに案件の呼び名（`project`）と、その案件の期間（`period`）も聞き、どの案件のいつの成果かを区別できるようにする。担当した案件が1つだけの職では、この2つを聞かない。

### Step 3 スキル棚卸し

technical / business / languages / certifications を、Step 2 の発話から逆引きで確認する（候補を選択肢として提示し、選ばせる）。そのうえで、厚労省ポータブルスキルの9要素（対課題5・対人4）を選択式で確認し、`skills.portable` に入れる（category は「対課題」か「対人」）。要件との対応づけは応募時に応募書類サブスキルが行う旨を伝える。詳細は `references/profile-methods.md` のスキル分類の節にある。

### Step 4 転職の軸・志望対象・年収

reasons（1件以上必須）→ 条件（`conditions`）→ 作業特性の希望（`work_character_preferences`）→ 企業スコアの採点軸（`company_score_axes`）→ targets → salary の順で聞く。軸の建設的言い換え・根拠づけは `job-change-self-analysis` へ誘導する。根拠は `references/profile-methods.md` の must/want の節による。

#### 条件の構造化

条件は自由文ではなく、軸・演算子・しきい値の形で構造化して `job_change_axis.conditions[]` へ入れる。フィールド仕様は hub の `references/profile-format.md`、軸の語彙は hub の `references/screening-axes.md` を読む。

条件1件ごとに、次を AskUserQuestion で確定する（1回の質問で複数の条件をまとめて扱ってよい）。

1. 譲れない条件か、あれば望ましい条件か（`level`）。
2. 8軸のどれに当たるか、または軸に当てはまらない質的条件か（`axis`）。
3. 軸に当たる場合は、比較のしかたとしきい値（`operator`・`value`・`unit`）。例: 残業なら「1か月あたりの上限時間」、年間休日なら「年間の下限日数」、年収なら「下限額」。
4. どこで確認できるか（`verification`）。求人票の記載で判定できるものは `posting`、企業研究が要るものは `research`、面接で聞くしかないものは `interview` とする。

軸に当てはまらない質的条件（例「モダンな技術スタックが整備されていること」）は、`axis` を `null`、`operator` を `qualitative`、`value` を `null` にし、`verification` を `research` または `interview` にする。この種の条件は求人検索の分類には用いられず、企業研究と面接での確認へ回る旨を利用者へ伝える。

#### 作業特性の希望

8つの作業特性それぞれについて、希望度（`must` / `important` / `neutral` / `not_required`）を確認する。特性の定義は hub の `references/screening-axes.md` にある。2回の AskUserQuestion（4特性ずつ）で埋まる。

「どちらでもよい」「不要である」も明示的に選ばせる。`desire=must` を選んだ特性には、本人の言葉での条件文（`statement`）を1文で聞く。

`clear_completion`・`solo_completable`・`short_feedback` の3特性は求人票からは判定できない。これらに `must` や `important` を選んだ場合は、面接での確認事項になる旨をその場で伝える。

#### 必須条件の件数

`conditions[level=must]` と `work_character_preferences[desire=must]` の合計が4件以上になったら、優先順位を付けて絞る対話を挟む。順位と再評価時期を `job_change_axis.priority_note` へ残す。

#### 企業スコアの採点軸

企業を0〜100点で採点する軸と重みを決め、`company_score_axes[]` へ入れる。定量候補軸9個・点数への換算・重みの配分の規則は `job-change-company-research` の `references/company-score-rubric.md`、フィールド仕様は hub の `references/profile-format.md` にある。次の順で決める。

1. 定量候補軸9個（処遇水準・年間休日総数・月平均残業時間・有給休暇の取得率・離職率・男性の育児休業取得率・売上高の成長率・営業利益率・自己資本比率）を提示し、重視するものを選ばせる。1回の AskUserQuestion で3問に分け、各問が3軸を `multiSelect: true` で受ける（1問あたりの選択肢は最大4件のため、9軸を1問へは入れられない）。処遇水準（`compensation_level`）は既定で選択済みとし、外すかどうかだけ確認する。
2. 数値にならない事柄で重視したいものがあれば、定性軸として作る。ラベル（呼び名）・定義（何をもってそう言うか）・判定条件（何が確認できたら何点か。3段階程度）を利用者と決める。判定条件まで決められない事柄は採点に入れず、面接での確認事項へ回す旨をその場で伝える。
3. 選んだ軸への重みの配分（合計100）と、定量軸で使う基準を1回の AskUserQuestion でまとめて聞く。第1問は重みの配分で、選んだ軸の数に応じた配分案を選択肢に置き、当てはまるものが無ければ自由記述で受ける。第2問は、統計に基づく既定の基準をそのまま使うか、自分の基準を使うかである。重みが0になる軸は置かず、採点に入れない軸は外す。
4. 自分の基準を使うと答えた軸は、100点となる水準（`full`）と0点となる水準（`zero`）を自由記述で聞き、`thresholds` へ入れる（数値の聞き取りであり、AskUserQuestion は使わない）。処遇水準（`compensation_level`）は既定の基準を持たないため、必ず聞く。現年収を `zero`、希望年収（またはそれを上回る水準）を `full` に置く聞き方を既定とし、本人が別の置き方を望めばそれに従う。
5. 配分した重みで架空2社を採点し、点数の高い側と「実際にどちらを選ぶか」への答えが一致するかを検算する。軸名どうしの抽象的な比較ではなく、企業像の比較で聞く（例: 「A社は年収が現職より120万円高いが残業が月30時間、B社は年収が現職と同水準で残業が月5時間。どちらを選ぶか」）。

検算が食い違った場合は、配分を見直すか、配分と実際の選択の両方を記録して利用者へ提示する。どちらが本当の判断かをスキルの側で決めない。軸を1つも選ばない場合は、企業スコアが出ない旨をその場で伝える。

#### 採点軸と必須条件の食い違い

選んだ採点軸と重みが、`conditions[level=must]` や `work_character_preferences` の希望度と食い違うことがある（例: 残業の上限を必須条件にしているのに `monthly_overtime` を軸に選んでいない、`compensation_level` に最大の重みを置いたのに年収の条件が `want` のままである）。

どちらが本当かをスキルの側で決めない。食い違う組み合わせをそのまま利用者へ提示し、どう扱うか（軸や重みを見直す・必須条件を見直す・両方このままにする）を本人に選ばせる。聞き取りメモには、提示した食い違いと、利用者が選んだ扱いの両方を残す。

#### 1.x からの移行

既存の `profile.json` が `schema_version` `1.0` または `1.1` の場合、`must_conditions` / `want_conditions` の自由文が残っている。**機械的に軸へ割り付けない。** 自由文からしきい値を推測することは事実の創作に当たる。

移行モードでは、既存の自由文を1件ずつ提示し、上記「条件の構造化」の4項目を対話で確定する。全件を移し終えたら `must_conditions` / `want_conditions` を空配列にし、続けて作業特性8件と企業スコアの採点軸を確認する。最後に `schema_version` を `2.0` へ、`updated_at` を当日へ書き換える。

利用者が移行を望まない場合は 1.x のまま残す。その場合、求人検索の8軸判定と適合性評価の作業特性の次元が働かない旨を1回だけ伝える。

### Step 5 作成→機械的な検証→独立監査

聞き取りの結果は、その途中で本体セッションが `{NOTES}`（`profile_interview_notes.md`）へ逐次追記し集約しておく（中断再開に対応）。`job-change-profile-writer` エージェント（model: opus）を起動し、`{NOTES}`・既存 `{PROFILE}`（更新時）・hub の `references/profile-format.md`・出力先 `{PROFILE}` を渡す。作成担当はメモにある事実だけから profile.json を作成・更新する。戻り値を受け、本体セッションが hub の `validate_profile.py` を実行して ERROR 0 を確認する。続いて `job-change-profile-auditor` エージェント（model: opus、作成担当の判断理由を渡さない新規コンテキスト）を起動して監査する。`verdict` が BLOCK、または `severity` = must_fix の finding があれば Step 5 の作成へ差し戻す（最大2回。以降は利用者判断）。

### Step 6 更新運用の案内と納品

更新運用（実績が出るたびに追記し、少なくとも四半期に一度は見直す。応募書類へ書き起こすときは直近7〜10年を優先する）を案内し、`updated_at` を当日の日付へ書き換える。profile.json は下流のサブスキルの入力であって単体の読み物ではないため、整形したファイルは作らない。代わりに、何が書かれたか（職務要約・職歴の件数と在籍期間・スキル・転職の軸と必須条件・企業スコアの採点軸・年収）を利用者へ要約して示す。最後に、profile.json を入力に使える下流の作業（`job-change-self-analysis` の自己分析、`job-change-company-research` の企業研究、`job-change-documents` の応募書類作成）を案内する。最終メッセージは結論から述べる。中身の無い節・同じ内容の繰り返し・定型の前置きを置かない。

## 合否ゲートと差し戻し

パイプラインには1つの検証・監査ゲートがある。

| ゲート | 通過条件と差し戻し先 |
|---|---|
| Step 5 の検証・監査ゲート | hub の `validate_profile.py` が FAIL（ERROR 1件以上）の場合、または `job-change-profile-auditor` の `verdict` が BLOCK の場合、または `severity` = must_fix の finding がある場合は、Step 5 の作成へ差し戻す。差し戻しは同一成果物につき最大2回まで行う。 |

差し戻し時は、監査の findings（target・evidence・fix）をそのまま作成担当へ渡し、反映後に Step 5 の機械的な検証から再度通す。2回の差し戻しで解消しない指摘は、未決事項として利用者へ判断を委ねてから納品する（例: 聞き取りメモに記録の無い数値が profile.json にある、という指摘は、聞き直すか削るかを利用者に選ばせる）。機械的な検証の ERROR は差し戻しの上限にかかわらず解消してから納品し、未解決が監査の finding だけである場合に限り、未決事項として明記したうえで納品してよい。

## 役割の実行（ハーネス別）

本スキルのパイプラインは、専門の役割へ作業を委ねる形で書いてある。役割の内容は `references/roles/` に置き、これを原本とする。

| エージェント名 | 役割プロンプトの原本 |
|---|---|
| `job-change-profile-writer` | `{SKILL_DIR}/references/roles/profile-writer.md` |
| `job-change-profile-auditor` | `{SKILL_DIR}/references/roles/profile-auditor.md` |

ハーネス別の実行手順、起動する数の判断、作成と監査を分ける理由の原本は hub の `{HUB_SKILL_DIR}/references/role-execution.md` にある。

## エージェントのモデル方針

| エージェント | model | 責務 |
|---|---|---|
| `job-change-profile-writer` | opus | 聞き取りメモから profile.json を作成・更新（Step 5）と監査指摘の反映。メモに無い事実を創作しない |
| `job-change-profile-auditor` | opus | 独立コンテキストでの創作・誇張・時系列整合・並行在籍・軸の件数の監査、検証スクリプトの再実行（Step 5） |

機械的検査は hub の `validate_profile.py` が担う。model は各エージェントの frontmatter に固定済みであり、起動時に上書きしない。

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
| `references/elicitation-guide.md` | 時系列×プロジェクト単位の想起手がかりの根拠、並行在籍と空白期間の扱い、選択式優先の運用、聞き取りメモの記載形式、更新運用、DOI/URL 付き出典 | 聞き取りの方針を定めるとき、監査の観点を確認するとき |
| `references/question-bank.md` | Step 1〜4 で使う有限の構造化質問と、各質問が埋めるフィールドの対応表、質問文の文体、AskUserQuestion へ渡す確定した選択肢の文言 | ヒアリングの各 Step で質問を選ぶとき、質問文を書くとき |
| `references/quantification-guide.md` | 定量化の型と代替表現、事実と異なる数値のリスク、定量化の効果の限界、職種依存、DOI/URL 付き出典 | 実績の聞き取り・作成・監査で定量表現を判断するとき |
| `references/profile-methods.md` | 採用側が見る情報、スキル分類、must/want の根拠と限界、ATS の実像、経歴詐称の帰結、設計の限界とエビデンスギャップ、DOI/URL 付き出典 | 設計判断の根拠を確認するとき、監査の観点を定めるとき |
