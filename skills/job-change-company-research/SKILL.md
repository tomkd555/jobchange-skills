---
name: job-change-company-research
description: >-
  転職の企業研究を担うサブスキル。企業名と重点観点を受け、公式資料・報道・口コミサイト等から情報を集め、
  すべての主張に出典URLとエビデンスレベル（A=一次公式／B=信頼できる二次／C=口コミ集計／D=個人ブログ・伝聞）を
  付した company_research.json を作り、機械検証と独立監査を通してから、トピック別の企業研究レポートを納品する。
  求人情報URLを渡された場合は、求人票を取り込んで job_posting.json を作ってから調査へ入る。
  指示された軸の指標について公表値を集めるところまでを担い、点数化・重み付け・格付けは行わない（profile 非依存）。
  job-change-support（hub）から振り分けられて動く。
  Use when the user researches a target company for a job change in Japan (including foreign-affiliated
  selection) — its philosophy, business, financials, compensation, benefits, work style, reputation, and
  selection process — or imports a job posting from a URL, and needs sourced, evidence-graded findings
  rather than unverified hearsay.
  trigger words: 企業研究, 会社を調べる, 企業分析, 事業内容, 財務, 平均年収, 有価証券報告書, 評判, 口コミ,
  選考プロセス, 理念, パーパス, 求人URL, 求人票の取り込み, この求人を調べて。
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Agent, AskUserQuestion, Skill
---

# job-change-company-research

転職の企業研究に取り組むとき、本スキル1つで収集から納品までの手順がそろう。すべての企業情報に出典URLとエビデンスレベルを付し、機械検証と独立監査で妥当性を担保したうえで、トピック別の企業研究レポートを納品する。

本スキルは hub（job-change-support）から振り分けられて動く。収集・作成は企業研究担当エージェント（job-change-company-researcher）が、独立監査は企業研究監査担当エージェント（job-change-research-auditor）が担う。判断基準は `references/` で自己完結する。

## 目的と原則

1. **すべての主張に出典とエビデンスレベルを付与する。** 企業情報の各主張（claim）には、出典URL・引用・エビデンスレベル（A=一次公式／B=信頼できる二次／C=口コミ集計／D=個人ブログ・伝聞・未確認）・確度（confidence）を付す。レベルの定義・判定基準・運用ルールの原本は `references/evidence-grading.md` にある。このファイルは hub と各エージェントも参照する原本である。

2. **C・D単独で事実を断定しない。** 口コミ・伝聞（C・D）のみを根拠に事実を断定しない。C・D を根拠とする記述は限定表現で書く（「口コミでは〜という声がある。選択バイアスがあり傍証にとどめる」）。口コミは、集約された総合スコアであること・十分な件数があること・複数の情報源で照合できることの3つを条件に、傍証として用いる。個票、件数の少ない集計、評価項目ごとの個別スコアは、事実の断定に使わない。

3. **企業自身の主張にConfidence highを与えない。** 企業が発信する評価的・自己宣伝的な主張（採用サイトの「風通しが良い」等）は、出典がレベルAでも内容の真偽は担保されない。当該企業が所有するページ由来である旨を出典に明示し、confidence を high にしない（B 相当扱い）。事実（掲げていること、開示された数値、認定の有無）と評価（社風の良し悪し）を分けて claim にする。

4. **一次情報も万能ではない。** レベルAの一次情報にも代表性・比較可能性の限界がある（有報の平均年間給与は全従業員平均で職種別内訳を欠く等）。限界を statement または open_questions に明示する。

5. **個人情報を外部へ送信しない。** 利用者の個人情報を、検索クエリ・fetch・外部APIを含む一切の外部送信に用いない。対象の列挙と例外の原本は hub の `{HUB_SKILL_DIR}/references/pii-boundary.md` にある。本スキルの job-change-company-researcher と job-change-posting-parser、監査を担う job-change-research-auditor はいずれも WebSearch・WebFetch を持つため、`profile.json` と `career-private/` 配下のパス・内容を渡さない。渡してよいのは `company_score_axes` の quantitative 軸の識別子の配列だけである（原本の例外）。重点観点は利用者の指示から与える。

6. **指示された軸の指標について実測値を出典付きで集める。評価も格付けもしない。** 企業研究は、指示書で渡された軸の識別子の配列（例 `["compensation_level", "annual_holidays"]`）に対応する定量指標の公表値を集め、`company_metrics` へ `value`・`unit`・`source_url`・`grade`・`as_of` を書く。軸の指定が無い場合は `compensation_level` を集める。実測値は企業側の事実であり、利用者プロファイル（希望年収・スキル・転職の軸）には依存しないため、profile.json を要しない。点数化・重み付け・総合点は、利用者がどの軸をどれだけ重んじるかに依存するため、適合性評価（job-change-fit-assessment）が算出する。定量候補軸9個の定義・単位・方向・出所と記入形式の原本は `references/company-score-rubric.md` にある。確認できなかった項目は `value` を `null` にし、推定値・概算値を入れない。

## 範囲外

- **利用者プロファイルの作成・管理。** profile.json の作成・更新・検証は hub（job-change-support）が担う。本スキルは profile.json を入力に取らない（原則5のとおり、Web 調査担当へ profile.json を渡さない）。
- **応募書類・面接・試験対策の生成。** 企業研究の結果（company_research.json）を根拠として使うのは下流のサブスキル（job-change-documents／job-change-interview-prep／job-change-exam-prep）であり、本スキルはそれらを実行しない。
- **選考試験種別の詳細調査。** 選考プロセスの概要（段階・筆記/適性検査の有無）は topic=selection_process として扱うが、検査種別（SPI3・玉手箱等）の特定と対策は job-change-exam-prep（job-change-exam-scout）が担う。
- **投資助言・企業の優劣の断定。** 財務情報は事実として整理するが、株式の売買判断や「良い/悪い会社」の断定はしない。

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

## 中間成果物: company_research.json

企業研究の判断はすべて `company_research.json` に集約する。出力先は `{DATA_ROOT}/companies/{企業スラッグ}/company_research.json` である（企業スラッグは企業別ディレクトリ名に使う識別子であり、形式の原本は job-change-support の `references/company-index-format.md` にある。Step 0 で `career-private/company_index.json` を引いて解決し、以後は再導出しない。例: 架空クラウドワークス株式会社 → `kakuu-cloudworks`、`S_アクメクラウド`）。

```json
{
  "company": { "name": "", "securities_code": "", "edinet_code": "" },
  "research_date": "YYYY-MM-DD",
  "claims": [
    { "id": "C001", "topic": "philosophy", "statement": "反証可能な命題",
      "evidence": [ { "source_url": "https://...", "source_name": "", "grade": "A", "quote": "引用", "accessed": "YYYY-MM-DD" } ],
      "confidence": "medium" }
  ],
  "company_metrics": {
    "compensation_level": { "value": 6120000, "unit": "円", "source_url": "https://...", "grade": "A", "as_of": "2026-03" },
    "annual_holidays": { "value": null, "unit": "日", "source_url": null, "grade": null, "as_of": null }
  },
  "open_questions": [ "" ]
}
```

topic は `philosophy`・`business`・`financials`・`compensation`・`benefits`・`workstyle`・`reputation`・`selection_process` の8種である。`company_metrics` は定量候補軸の実測値である（後述の原則6）。フィールドの完全な仕様・記入基準・検証規則は `references/company-research-format.md` を原本とし、記述例は `assets/company_research_example.json`（架空企業）にある。

## パイプライン

サブスキルとして次の Step 0〜4 を順に進める。`{SKILL_DIR}` は本スキルの絶対パス、`{company_research.json}` は成果物のパス（`companies/{企業スラッグ}/company_research.json`）に読み替える。

### Step 0 受付

次を確認する。不明点は AskUserQuestion で選択式を中心に尋ね、最大4問・各4択までとする。

- 対象企業名（正式名称）。曖昧な場合（グループ会社・持株会社・同名企業がある等）は候補を挙げて確認する。
- 重点観点（あれば）。理念・事業・財務・給与・福利厚生・働き方・評判・選考のどれを厚く見るか。指定が無ければ8トピックを均等に扱う。
- 求人票の入手経路。求人情報URL・求人票の本文・PDF や画像のファイルのいずれかを受け取る。どれも無い場合は Step 0.5 で対話により埋めるため、その旨だけを確認する。

企業スラッグは `career-private/company_index.json` で解決する。企業名が index の `name` または `aliases` に一致すればそのスラッグを使い、一致が無いときのみ一度だけ導出して index へ登録し、`companies/{企業スラッグ}/` を作る（詳細は job-change-support の `references/company-index-format.md` を参照）。

### Step 0.5 求人票の取込（必須）

企業ごとの工程の最初である。ここで作る `job_posting.json` は、この後の企業研究と適合性評価が入力として読む。取込を飛ばして先へ進まない。

入口は4通りある。利用者が用意できる材料に応じて選び、いずれの場合も同じ `job_posting.json` を作る。仕様は `references/job-posting-format.md` にある。

| 入口 | `source_type` | 担い手 |
|---|---|---|
| 求人情報URL | `url` | job-change-posting-parser |
| 求人票の本文（貼り付け） | `text` | 本スキル |
| 求人票の PDF・画像 | `file` | 本スキル |
| 企業名のみ（求人が特定できない） | `dialogue` | 本スキル |

**求人情報URLの場合（job-change-posting-parser, sonnet）。** 求人票取込担当エージェントを Agent ツールで起動し、求人URLと `{SKILL_DIR}`（`references/job-posting-format.md` の所在）を渡す。エージェントは WebFetch でページを取得し、`{company_name, aliases, job_posting}` の JSON を返す（ファイルは書かない）。**利用者の個人情報（原則5の列挙）は渡さない**（posting-parser は WebFetch を持つ）。返却された `company_name`・`aliases` を使い、Step 0 と同じ手順でスラッグを解決する（一致が無いときのみ一度だけ導出して登録する）。

**求人票の本文・ファイルの場合。** 本スキルが仕様に従って `job_posting` オブジェクトを組み立てる。本文は利用者が貼り付けたものをそのまま読み、ファイルは Read で読む。`source_type` を `text` または `file` とし、`source_url` は null にする。企業名とスラッグは Step 0 で確認・解決したものを使う。

**企業名しか無い場合。** 応募職種（`title`）を対話で確認し、給与・勤務地・雇用形態・要件のうち利用者が答えられる項目だけを埋める。`source_type` を `dialogue`、`source_url` を null にする。答えられなかった項目を推定で補わず、`open_questions` に「何が未確認か」を書く。求人票の記載が少ないことは差し戻しの理由にならない。未確認の項目は、この後の企業研究と面接での確認事項へ回す。

**共通の後処理。**

1. 組み立てた `job_posting` オブジェクトを、本スキルが `companies/{企業スラッグ}/job_posting.json` へ Write で書く（スラッグ解決後にのみ書く）。
2. 次で検証し、PASS（ERROR 0件）を確認する。ERROR があれば、URL 入口なら posting-parser へ差し戻し、それ以外なら本スキルが埋め直し、埋められない欠損は `open_questions` に残す。

   ```bash
   python {SKILL_DIR}/scripts/validate_job_posting.py {job_posting.json} --json
   ```

3. `companies/{企業スラッグ}/_manifest.json` の `artifacts.job_posting` を `{updated_at: 取得日, source_url: 取り込んだ求人URL}` に更新する（後述「_manifest.json の更新」）。URL 以外の入口では `source_url` を null にする。

取り込んだ求人票は、Step 1 の収集で選考プロセス・求める人物像の照合に使い、`job_posting.metrics`（年間休日・残業・有給取得率・付与日数）は company_research の `company_metrics` を補強する材料になる。

### Step 1 収集・作成（job-change-company-researcher, opus）

企業研究担当エージェント（job-change-company-researcher）を Agent ツールで起動し、company_research.json を作らせる。指示書には次を渡す。

- 企業名（正式名称）・重点観点（あれば）・出力先ディレクトリ・求人票の所在（あれば）。
- 実測値を集める軸の識別子の配列（例 `["compensation_level", "annual_holidays"]`）。呼出元から軸の指定が無い場合は `["compensation_level"]` を渡す。利用者が定義した定性軸の記述は渡さない（本人の状況を映すため。判定は適合性評価が行う）。定性軸に関わる事柄を調べる必要がある場合、利用者が自分の言葉で重点観点として指示する。
- 本スキルの絶対パス `{SKILL_DIR}`（references と scripts の所在）。

重点観点は、8トピック（理念・事業・財務・給与・福利厚生・働き方・評判・選考）の強弱指定へ正規化して渡す。利用者の自由記述に含まれる個人情報（原則5、原本は `{HUB_SKILL_DIR}/references/pii-boundary.md`）は指示書に含めず、該当トピックの強弱指定へ言い換える。

**profile.json は渡さない**（原則5。researcher は WebSearch・WebFetch を持つため）。Step 0.5 で job_posting.json を作った場合は、その所在を指示書に渡し、選考プロセス・求める人物像の照合に使わせる。エージェントは `references/evidence-grading.md`・`references/company-research-format.md`・`references/source-catalog.md`・`references/philosophy-analysis.md`・`references/compensation-benefits.md`・`references/company-score-rubric.md` を原本とする。これらに従い、収集した主張を claims 配列へ集約する。平均年間給与・年間休日・月平均残業・有給取得率・離職率などの数値は、文章の claim に埋めるだけでなく `company_metrics` へ構造化して格納する（単位・出典URL・レベル併記。確認できなければ value を null）。

指示書で渡された軸の指標を優先して集め、`company_metrics` の各項目へ実測値と出典を書く（原則6。profile を要しない、企業側の事実の収集）。点数も格付けも付けない。重点観点として渡された事柄は、確認できた事実と出典を claims へ書く。自分で `validate_company_research.py` を PASS させてから返す（`company_metrics` の欠落・構造不正は ERROR になる）。これが本エージェントの責務である。

### Step 2 機械検証

researcher が返した company_research.json を、オーケストレーター側でも検証する。

```bash
python {SKILL_DIR}/scripts/validate_company_research.py {company_research.json} --json
```

ERROR が1件でもあれば Step 1 へ差し戻す。PASS（ERROR 0件）になるまで先へ進まない。WARN のみは PASS 扱いだが、内容を記録し、必要ならトピックの裏付け追加を促す。

### Step 3 独立監査（job-change-research-auditor, opus）

企業研究監査担当エージェント（job-change-research-auditor）を、収集担当の判断理由を渡さない新規コンテキストで起動する。指示書には company_research.json の絶対パス、Step 1 で収集を指示した軸の識別子の配列、`{SKILL_DIR}` を渡す。

監査は次を行う。判定は `BLOCK` / `CONCERNS` / `CLEAN` で返る。

- `validate_company_research.py` の再実行（結果を `validation_rerun`＝ERROR 0件なら PASS、そうでなければ FAIL として記録）。`validation_rerun` が FAIL の場合、verdict は無条件で BLOCK である。
- claims を層化抽出し、出典URLが実在するか、引用が原文と一致するかを確認する（レベルAの財務系 claim と confidence=high の claim を必ず標本に含める）。
- レベル付与の妥当性（口コミをA・Bへ格上げしていないか、一次情報をCへ格下げしていないか）。
- レベルC・D単独の断定、企業自身の自己宣伝的主張への confidence high 付与の有無。
- 必須7トピック（`philosophy`・`business`・`financials`・`compensation`・`benefits`・`workstyle`・`reputation`）の網羅状況と、`selection_process` の充足状況（0件は WARN 相当で、収集を推奨）。`selection_process` の欠落は重大扱いにしない。
- `company_metrics` の妥当性（`references/company-score-rubric.md` 基準）。実測値が出典の記載と一致するか、エビデンスレベルの付与が妥当か、指示された軸の指標を過不足なく集めているかを検査する。

verdict が `BLOCK` の場合、または severity=重大の finding があれば Step 1 へ差し戻す。差し戻し時は監査の findings（target・evidence・fix）を researcher へそのまま渡す。

### Step 4 納品

company_research.json を、人が読める企業研究レポート `companies/{企業スラッグ}/company-research-report.md` へ整形して納品する。

- 冒頭に、軸ごとの実測値と単位・出典・エビデンスレベル・時点を示す。確認できなかった軸は「確認できず」と書く。企業側の事実であり利用者との適合ではない旨と、点数化と総合点は適合性評価が算出する旨を1文ずつ添える。
- トピック別（理念・事業・財務・給与・福利厚生・働き方・評判・選考プロセス）に、主張＋出典＋レベル＋確度を読める形で並べる。
- open_questions（裏取りできなかった論点・出所の食い違い・一次情報の代表性の限界）を明記する。
- C・D を根拠とする記述は、レポート上でも限定表現を保つ（「口コミでは〜という声がある。傍証にとどめる」）。

納品時に、`companies/{企業スラッグ}/_manifest.json` の `artifacts.company_research` を更新する（後述「_manifest.json の更新」）。`updated_at` を調査日にし、調査したトピックそれぞれの `last_researched` を調査日にする。あわせて Step 3 の監査で得た verdict を `audit_verdict` に、監査を行った日付を `audited_at` に書く。差し戻して再監査した場合は、最後の監査の verdict と日付を書く。

企業スラッグの接頭辞（ディレクトリ名）は変更しない。`career-private/company_index.json` の分類・一覧用のフィールドへ、企業の点数や格付けを書かない。点数は適合性評価が算出するためである。

最終メッセージには、軸ごとの実測値と出典の要点、主要トピックの要点、検証結果（validate の PASS・監査の verdict）、残る未決事項（差し戻し2回で解消しなかった論点があれば）を要約する。レポートと最終メッセージはいずれも結論から述べる。中身の無い節・同じ内容の繰り返し・定型の前置きを置かない。

## _manifest.json の更新

`companies/{企業スラッグ}/_manifest.json` は、企業別成果物の最終更新日と、company_research のトピック別の最終調査日を持つ記録である。本スキルはこの記録の書き手であり、鮮度の判定そのものは hub の責務である（本スキルは判定しない）。

構造は次のとおり。トピック名は company_research の既存トピック名（`philosophy`・`business`・`financials`・`compensation`・`benefits`・`workstyle`・`reputation`・`selection_process`）を使う。

```json
{
  "schema_version": 1,
  "artifacts": {
    "job_posting": { "updated_at": "YYYY-MM-DD", "source_url": "https://..." },
    "company_research": {
      "updated_at": "YYYY-MM-DD",
      "audit_verdict": "CLEAN",
      "audited_at": "YYYY-MM-DD",
      "topics": { "financials": { "last_researched": "YYYY-MM-DD" } }
    }
  }
}
```

- `_manifest.json` が無ければ作る。あれば該当箇所のみを更新し、他の成果物（`fit_assessment` 等）の記録は残す。
- Step 0.5 で job_posting.json を作ったときは `artifacts.job_posting` を更新する。
- Step 4 の納品時に `artifacts.company_research.updated_at` と、調査したトピックの `topics.<トピック名>.last_researched` を更新する。同時に `audit_verdict`（Step 3 の verdict。`CLEAN`・`CONCERNS`・`BLOCK` のいずれか）と `audited_at`（監査を行った日付）を書く。差し戻して再監査した場合は最後の監査の結果で上書きする。

### トピック限定の差分再調査

呼出元（hub）から対象トピックの指定を受けた場合、そのトピックだけを再調査する。

1. 指定トピックのみを重点観点として Step 1 の researcher を起動し、当該トピックの claims を得る。
2. 既存の company_research.json を読み、指定トピックの claims だけを差し替え（マージ）、他トピックの claims はそのまま残す。
3. 指定トピックに対応づく `company_metrics` の項目を再取得し、値・出典URL・レベル・時点（`as_of`）を更新する。再取得の対象外の項目はそのまま残す。確認できなくなった項目は `value` を `null` に戻す。
4. Step 2 の機械検証を再度通す（PASS を確認する）。
5. `_manifest.json` の `artifacts.company_research.topics.<指定トピック>.last_researched` のみを更新する（他トピックの `last_researched` は変えない）。`updated_at` は今回の調査日にする。

鮮度が切れたトピックの判定・再調査の指示は hub が行い、本スキルは指定されたトピックの再調査と記録の更新を担う。

## 合否ゲートと差し戻し

パイプラインには2つのゲートがある。

| ゲート | 通過条件と差し戻し先 |
|---|---|
| Step 2 の機械検証ゲート | `validate_company_research.py` が PASS（ERROR 0件）でなければ Step 3 以降へ進まない。ERROR は Step 1 へ差し戻す。 |
| Step 3 の独立監査ゲート | `job-change-research-auditor` の verdict が `BLOCK`、または severity=重大の finding があれば Step 1 へ差し戻す。 |

差し戻しは同一企業の調査につき最大2回まで行う。2回で解消しない指摘は、company-research-report.md の未決事項へ記録し、利用者へ判断を委ねてから納品する。機械検証の ERROR は差し戻しの上限にかかわらず解消してから納品し、未解決が監査の finding だけである場合に限り、未決事項として明記したうえで納品してよい。差し戻し時は、機械検証の ERROR 内容または監査の findings をそのまま researcher へ渡し、修正後に再度 Step 2 から通す。

## 役割の実行（ハーネス別）

本スキルのパイプラインは、専門の役割へ作業を委ねる形で書いてある。役割の内容は `references/roles/` に置き、これを原本とする。

| エージェント名 | 役割プロンプトの原本 |
|---|---|
| `job-change-company-researcher` | `{SKILL_DIR}/references/roles/company-researcher.md` |
| `job-change-research-auditor` | `{SKILL_DIR}/references/roles/research-auditor.md` |
| `job-change-posting-parser` | `{SKILL_DIR}/references/roles/posting-parser.md` |

ハーネス別の実行手順、起動する数の判断、作成と監査を分ける理由の原本は hub の `{HUB_SKILL_DIR}/references/role-execution.md` にある。

## エージェントのモデル方針

| エージェント | model | 責務 |
|---|---|---|
| `job-change-company-researcher` | opus | 一次情報と二次以下の情報の収集 → company_research.json ＋ 出典・レベル付与 |
| `job-change-research-auditor` | opus | 独立コンテキストでの出典実在・引用一致・レベル妥当性・トピック網羅の監査 |
| `job-change-posting-parser` | sonnet | 求人URLの取得 → job_posting.json の仕様に沿ったオブジェクトの組み立て（ファイルは書かない） |

この方針は各エージェントの frontmatter に固定済みであり、起動時に model を上書きしない。

## スクリプトのCLI使用例

企業研究データの検証（終了コードは PASS で 0、FAIL で 1。WARN のみは PASS 扱い）。`{SKILL_DIR}` は本スキルの絶対パス、`{company_research.json}` は検証対象のパスに読み替える。

```bash
python {SKILL_DIR}/scripts/validate_company_research.py {company_research.json}
python {SKILL_DIR}/scripts/validate_company_research.py {company_research.json} --json
python {SKILL_DIR}/scripts/validate_job_posting.py {job_posting.json}
python {SKILL_DIR}/scripts/validate_job_posting.py {job_posting.json} --json
```

`--json` は結果を JSON 形式（`status`・`error_count`・`warning_count`・`errors`・`warnings`）で出力する。記述例は `assets/company_research_example.json`、フィールド仕様と検証規則の原本は `references/company-research-format.md`（企業研究）と `references/job-posting-format.md`（求人票取込）にある。単体テストは次で実行する。

```bash
cd {SKILL_DIR} && python -m unittest discover -s scripts/tests
```

## references 一覧

| ファイル | 何を | いつ読むか |
|---|---|---|
| `references/evidence-grading.md` | エビデンスレベルA〜Dの定義・判定基準・C/D断定禁止・自己宣伝的主張の確度制限・ソース突合・裏取り知見（口コミの選択バイアス・集約スコアの妥当性・有報の限界） | レベルと確度を付ける/検査する全段階 |
| `references/company-research-format.md` | company_research.json のフィールド仕様・記入基準・機械検証規則 | company_research.json を書く/読む/検証する全段階 |
| `references/source-catalog.md` | 情報源カタログ（EDINET有報・IR開示・就職四季報・しょくばらぼ・認定制度・口コミサイト）と各源の記載内容・限界・出典URL | Step 1 の収集、Step 3 の監査 |
| `references/philosophy-analysis.md` | 理念・社是・パーパス分析の収集源と分析手順（明文→行動指針→人事制度→開示との一貫性検証）、自己宣伝的主張の確度制限との関係 | topic=philosophy の収集・分析 |
| `references/compensation-benefits.md` | 給与・福利厚生・働き方の調査観点と情報源カタログ（有報・しょくばらぼ・認定制度・就職四季報・OpenWork・公的統計）、company_metrics への格納ルール | topic=compensation/benefits/workstyle の収集 |
| `references/company-score-rubric.md` | 定量候補軸9個（軸キー・指標・単位・方向・出所）の定義と `company_metrics` の記入形式、点数化・重み・総合点を適合性評価が担う分業 | Step 1 の実測値の収集、Step 3 の company_metrics 監査 |
| `references/job-posting-format.md` | job_posting.json のフィールド仕様・記入基準・機械検証規則（4通りの入口と `source_type` を含む） | Step 0.5 で求人票を取り込む/検証する段階 |
