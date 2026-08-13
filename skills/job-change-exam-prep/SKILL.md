---
name: job-change-exam-prep
description: >-
  転職（中途採用）の筆記試験・適性検査対策を担うサブスキル。対象企業で使われる検査種別（SPI3・玉手箱・
  GAB/CAB・TG-WEB・TAL・内田クレペリン・性格検査・外資系オンラインアセスメント）を、受検案内 URL の
  ドメイン判別と job-change-exam-scout エージェントの調査で特定し、検査種別ごとに対策計画（科目別の
  学習項目・時間配分・教材方針・スケジュール）を作り、出題形式を模した自作問題で演習する。確定情報と
  推定を区別し、能力検査は反復練習、性格検査は一貫した正直な回答という、検査種別ごとの対策差に従う。実在の
  検査問題は複製しない。hub（job-change-support）から振り分けられて使う。
  Use when the user prepares for a written test or aptitude assessment in a Japanese mid-career job change
  (including foreign-affiliated online assessments) — identifying which test a company uses, building a
  study plan, and practicing question formats.
  trigger words: 適性検査, 適性検査対策, 筆記試験, SPI, SPI3, 玉手箱, GAB, CAB, TG-WEB, TAL,
  内田クレペリン, WEBテスト, テストセンター, ケース面接, フェルミ推定。
allowed-tools: Read, Write, Glob, Grep, Bash, Agent, AskUserQuestion, Skill
---

# job-change-exam-prep

中途採用の筆記試験・適性検査に備えるとき、このスキルが検査種別の特定から対策計画の作成・演習までを担う。対象は日本の中途採用で使われる検査を中心とし、外資系のオンラインアセスメントにも対応する。

検査は種別ごとに出題形式も対策の効き方も異なる。まず対象企業で使われる検査種別を特定し、種別に応じた対策計画を作り、出題形式を模した自作問題で演習する、という順で進める。検査種別の調査は専用エージェント `job-change-exam-scout` に委ね、本スキルはその起動・結果の突き合わせ・計画作成・演習を担う。

## 目的と原則

1. **検査種別を先に特定する。** 対策は検査種別に依存するため、種別が定まらないまま学習項目を決めない。受検案内 URL があれば `references/domain-detection.md` のドメイン判別で系統を即時に絞り、`job-change-exam-scout` の調査で種別を確定・補強する。確定情報（採用ページ等での明記）と推定（選考体験記からの類推）を区別し、推定を確定であるかのように書かない。

2. **対策は検査種別ごとに分ける。** 能力検査（SPI3・玉手箱・TG-WEB・GAB・CAB 等）は反復練習で得点が上がる。一方、性格検査・TAL・内田クレペリンは対策可能性が限定的であり、このうち性格検査では一貫した正直な回答を勧める。回答のゆがみ（faking）が妥当性へ与える影響は学術的に未決着であり、両論は `references/prep-methods.md` に併記する。この対策差の原本は `references/prep-methods.md` である。

3. **実在の検査問題を複製しない。** 演習は `references/assessment-catalog.md` の出題形式知識に基づき、形式を模した自作問題で行う。実在の検査問題・著作物の複製、受検代行、替え玉受検は行わない。

4. **個人情報を外部へ送信しない。** `job-change-exam-scout` は WebSearch・WebFetch を持つため、`profile.json` に含まれる個人情報（氏名・現年収・希望年収・居住地・学歴・在籍企業名・実績など）をこのエージェントへ渡さない。Step 1 の指示書には企業名・応募職種・求人票のみを渡す。本スキルは `profile.json` を必須の前提とせず、職種などを背景として参照する場合も、その内容を Web 送信手段を持つ手順へ回さない。

5. **ベンダー公表値は自己報告として扱う。** 検査提供元や対策媒体が公表する完了率・データ件数などの数値は、独立検証を経ていない自己報告値として扱い、断定の根拠にしない。

## 範囲外

次は本スキルの範囲外とする。依頼された場合は、対応できない旨を伝える。

- **受検の代行・替え玉受検・不正行為。** 利用者本人に代わって検査を受検する行為、替え玉受検、監視環境の回避は扱わない。
- **面接本番の想定問答。** 面接そのものの対策は `job-change-interview-prep` が担う。ケース面接・フェルミ推定については、筆記/オンライン選考の一環として思考の型を扱うが、面接での深掘りへの想定問答は `job-change-interview-prep` へ委ねる。
- **企業研究・応募書類作成。** それぞれ `job-change-company-research`・`job-change-documents` が担う。
- **合否・スコアの予測や保証。** 対策計画は学習の方針であり、合否やスコアを予測・保証しない。

## パスの解決

利用者データの置き場所は設定ファイルだけが決める。既定の置き場所を持たない。本文で `{DATA_ROOT}` と書いた箇所は、設定ファイルの `data_root` に読み替える。

hub（job-change-support）から振り分けられた場合は、hub が解決済みの `{DATA_ROOT}` を渡す。単独で起動された場合は、次の順に設定ファイルを探し、最初に見つかったものを Read で読む。

1. 環境変数 `JOB_CHANGE_CONFIG` が指すファイル
2. カレントディレクトリから上位へたどった最初の `.job-change/config.json`
3. `~/.job-change/config.json`

いずれの場所にも設定ファイルが無ければ未設定である。その場合は作業へ進まず、Skill ツールで `job-change-support` を起動して設定を作らせ、`{DATA_ROOT}` を解決してから戻る。

`{SKILL_DIR}` は本スキルの絶対パス、`{HUB_SKILL_DIR}` は同じ配置先にある `job-change-support` の絶対パスを指す。設定ファイルの仕様は `docs/configuration.md` にある。

## 中間成果物

企業別の成果物は `{DATA_ROOT}/companies/{企業スラッグ}/` 配下に置く。企業スラッグは hub と同じ規約に従い、`career-private/company_index.json` で解決する（例: 架空クラウドワークス社 → `kakuu-cloudworks`）。

| パス | 内容 | 生成する Step |
|---|---|---|
| `companies/{企業スラッグ}/exam_assessment.json` | 検査種別の調査結果（種別・実施段階・根拠 URL・確度・出題形式・推奨対策） | Step 1（`job-change-exam-scout` が書き出す） |
| `companies/{企業スラッグ}/exam-prep-plan.md` | 対策計画（検査種別ごとの学習項目・時間配分・教材方針・スケジュール） | Step 2 |

企業が特定できない汎用の対策依頼では、企業スラッグの代わりに `_general/` を用いて成果物を置く。

## パイプライン

Step 0 から Step 3 を順に進める。

### Step 0 受付

次を確認する。確認は AskUserQuestion で選択式を中心に行い、最大4問・各4択とする。

- 対象企業名（正式名称）。企業未定の汎用対策か、特定企業向けかを区別する。
- 応募職種（総合職・エンジニア職など。CAB/GAB の別や検査傾向の判断に影響する）。
- 受検案内 URL の有無。案内メール・受検ページの URL があるか。

受検案内 URL がある場合は、`references/domain-detection.md` のドメイン判別表に照らして系統を即時に判別し、確度を明示する。判別は URL 文字列の照合のみで行い、URL への外部アクセスやプロファイルの外部送信は伴わない。判別結果は暫定であり、確度は「推定」とする。日本 SHL 系（`e-exam`・`nsvs`・`tsvs`）は玉手箱・GAB・CAB のいずれかまでしか絞れないこと、ペーパー形式は URL 判別ができないこと、ドメインは変更されうることを併せて伝える。確定は Step 1 の調査で行う。

特定企業向けの場合は、企業スラッグを `career-private/company_index.json` で解決する（企業名が index に一致すればそのスラッグを使い、無ければ一度だけ導出して登録する。詳細は job-change-support の `references/company-index-format.md` を参照）。

`profile.json` は本スキルの必須前提ではない。職種の把握のために参照してよいが、その内容を Step 1 のエージェントへ渡さない（原則 4）。

### Step 1 検査種別の調査

`job-change-exam-scout` エージェント（model: sonnet）を Agent ツールで起動し、対象企業の中途採用で使われる検査種別を調査させる。

- 指示書に渡すもの: 企業名（正式名称）・応募職種（あれば）・求人票（あれば）。`companies/{企業スラッグ}/company_research.json` があれば、topic=selection_process の claims の要約（主張・出典URL・証拠グレード）も渡す。既に集めた証拠を捨てて調査をやり直させないためである。この要約は企業についての公開情報であり個人情報を含まないため、Web ツールを持つ調査担当へ渡してよい。`profile.json` は渡さない（原則 4）。
- 調査結果が、渡した claims と食い違う場合は、証拠グレードの高いほうを採用する。同じグレードなら調査日の新しいほうを採用し、`exam_assessment.json` の備考に双方の主張と採否の理由を残す。
- 出力先: エージェントは `{DATA_ROOT}/companies/{企業スラッグ}/exam_assessment.json` へ結果を書き出し、同一の JSON を返す。
- 出力 JSON の骨格（原本はエージェント定義）:

```json
{
  "company": "",
  "assessments": [
    {
      "type": "",
      "stage": "",
      "evidence": [{"source_url": "", "grade": "A|B|C|D", "quote": ""}],
      "confidence": "確定|推定",
      "format_notes": "",
      "prep_recommendations": []
    }
  ],
  "open_questions": []
}
```

`confidence` は、採用ページ等で種別が明記されていれば「確定」、選考体験記からの類推なら「推定」とする。根拠が単一の体験記のみである種別については、エージェントがその旨を出力に明記する。

企業が特定できず汎用対策とする場合は、本 Step を省略し、`references/domain-detection.md` の暫定判別（URL があれば）と、頻出検査（SPI3・玉手箱）を想定した基礎対策で Step 2 へ進む。

### Step 2 対策計画の作成

`exam_assessment.json` の `assessments` と、`references/assessment-catalog.md`・`references/prep-methods.md` を突き合わせ、検査種別ごとに対策計画を作る。計画は次を含む。

| 構成要素 | 内容 |
|---|---|
| 科目別の学習項目 | 検査種別の出題科目（言語・非言語・計数・英語・法則性・命令表・暗号など）ごとに、習得すべき項目を挙げる。`references/assessment-catalog.md` の出題形式を根拠にする。 |
| 時間配分 | 実施方式・制限時間の特徴（玉手箱・TG-WEB のように短時間で同一形式を連続出題する検査では時間管理が要点になる）を踏まえ、科目別の学習・演習の時間配分を示す。 |
| 教材方針 | 検査種別に対応する定番教材の系統を示す（`references/prep-methods.md`）。対策困難な検査（TAL 等）は、その旨を明示して過剰な教材投入を避ける。 |
| スケジュール | 受検までの日数に応じた学習順序を示す。反復練習が効く能力検査を優先し、性格検査は回答方針の確認にとどめる。 |

対策可能性の差（`references/prep-methods.md`）に従い、性格検査・TAL・内田クレペリンには過度な対策を勧めない。性格検査については、一貫した正直な回答を勧める。

確定情報と推定の区別を維持する。`confidence` が「推定」の種別は、対策計画に「推定である旨・根拠件数・確度」を明記し、確定種別と同等に断定しない。Step 0 の URL 暫定判別と Step 1 の調査結果が食い違う場合は、両方を提示し、確度の高いほうを優先する。

計画を `companies/{企業スラッグ}/exam-prep-plan.md`（汎用時は `_general/exam-prep-plan.md`）へ書き出す。

### Step 3 演習・模擬出題

`references/assessment-catalog.md` の出題形式知識に基づき、対象検査の形式を模した自作問題を出題し、採点・解説する。

- 対象は反復練習が有効な能力検査系（SPI3・玉手箱・TG-WEB・GAB・CAB）を中心とする。出題→利用者の解答→採点→解説→弱点科目の再出題、を繰り返す。
- 性格検査は演習の対象とせず、回答方針（一貫性・正直さ）の助言にとどめる。
- ケース面接・フェルミ推定は、思考の型（前提確認 → 構造分解 → 仮説 → 結論から述べる）に沿った練習とし、評価は数値の正確性でなく思考プロセスに重点を置く（`references/prep-methods.md`）。
- 実在の検査問題・著作物を複製しない（原則 3）。自作問題は形式のみを模す。

## 合否ゲートと差し戻し

本スキルには独立監査エージェントを置かない。ゲートは Step 1 の調査結果の妥当性に対して設ける。

- 種別特定ゲート（Step 1）では、`job-change-exam-scout` が有効な種別を返すことを求める。
  - エージェントが `{"error": "企業名が指定されていない"}` を返した場合は、Step 0 へ戻り企業名を確認する。
  - `assessments` が空で `open_questions` のみの場合は、検索範囲を広げる指示（別の選考体験記媒体・採用ページの確認）を付してエージェントへ再依頼する。再依頼は最大2回までとする。
  - 2回で種別が特定できない場合は、「種別不明」を未決事項として利用者へ伝える。そのうえで、頻出検査（SPI3・玉手箱）を想定した基礎対策に絞るか、受検案内の到着後に再調査するかを、利用者に委ねる。
- 確度ゲート（Step 2）では、`confidence` が「推定」の種別について、対策計画に推定である旨・根拠件数・確度を明記する。単一の体験記のみが根拠の種別は、その限界を特に明示する。確定種別と同等に断定しない。

## 役割の実行（ハーネス別）

本スキルのパイプラインは、専門の役割へ作業を委ねる形で書いてある。役割の内容は `references/roles/` に置き、これを原本とする。

| エージェント名 | 役割プロンプトの原本 |
|---|---|
| `job-change-exam-scout` | `{SKILL_DIR}/references/roles/exam-scout.md` |

**サブエージェントを起動できるハーネス（Claude Code）。** 各 Step の記述どおり、上表のエージェント名を Agent ツールで起動し、指示書を渡す。エージェント定義はリポジトリの `agents/` にあり、`references/roles/` の写しである。

**サブエージェントを起動できないハーネス（Codex ほか）。** 各 Step の「エージェントを起動する」を「役割プロンプトを読み、その役割として自分で実行する」と読み替える。手順は次のとおり。

1. 上表の役割プロンプトを Read で読む。
2. Step に書かれた指示書の項目を、そのまま自分への指示として扱う。
3. 役割プロンプトの「扱ってよい入力」のルールを守る。Web 送信手段を持たない役割として書かれている場合、その作業中は Web 検索・fetch を使わない。
4. 成果物の形式・検証・合否ゲートは、ハーネスによらず同一である。

## エージェントのモデル方針

| エージェント | model | 責務 |
|---|---|---|
| `job-change-exam-scout` | sonnet | 対象企業の検査種別の調査（種別・実施段階・根拠 URL・確度・出題形式・推奨対策） |

model はエージェント定義の frontmatter に固定済みであり、起動時に上書きしない。

## references 一覧

| ファイル | 何を | いつ読むか |
|---|---|---|
| `references/assessment-catalog.md` | 主要検査（SPI3・玉手箱・GAB/CAB・TG-WEB・TAL・内田クレペリン・性格検査・外資系オンラインアセスメント）の提供元・構成・実施方式・出題形式と出典 | Step 1 の結果解釈、Step 2 の学習項目設計、Step 3 の出題形式の把握 |
| `references/domain-detection.md` | 受検案内 URL のドメインによる検査系統の事前判別表と、その限界 | Step 0 で URL があるとき、Step 2 で暫定判別と調査結果を照合するとき |
| `references/prep-methods.md` | 検査種別ごとの対策可能性の差、練習効果と faking の学術的知見、定番教材の系統、ケース面接・フェルミ推定の型 | Step 2 の対策方針の決定、Step 3 の演習方針 |
