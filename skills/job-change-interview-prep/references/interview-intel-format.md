# interview_intel.json の原本仕様（interview-intel-format）

面接情報の調査の成果物 `interview_intel.json` のフィールド仕様・記入基準・機械的な検証の規則を定める原本である。面接情報調査担当（job-change-interview-scout）がこの仕様で成果物を作り、`scripts/validate_interview_intel.py` がこの仕様に照らして機械的に検査する。面接対策担当（job-change-interview-coach）は、この成果物を想定質問の素材として読む。

出力先は `{DATA_ROOT}/companies/{企業スラッグ}/interview_intel.json` である。企業別の非個人情報ツリーに置く。書くのは Web 送信手段を持つ役割であり、利用者の個人情報とその派生値をこのファイルに書かない（境界の原本は `{HUB_SKILL_DIR}/references/pii-boundary.md`）。

## 位置づけ

企業固有の想定質問の根拠は、これまで `company_research.json` の `topic=selection_process` の claims だけだった。企業研究の8トピックのうちの1つとして集めるため、面接の質問そのものの収集は浅くなりがちだった。`interview_intel.json` は、対象企業の面接についてだけを、口コミサイト・採用ページ・選考体験記から集め直した成果物である。

集めるのは次の3種類であり、いずれも「面接で何を聞かれるか」についての仮説であって事実ではない。

| 種類 | 内容 | 使い方 |
|---|---|---|
| 報告された質問（`reported_questions`） | 口コミや体験記で「聞かれた」と報告された質問文、または記述から推測した質問文 | 想定質問の候補。`kind` が出所の性質を示す |
| 面接の形式に関する事実（`format_facts`） | 選考の段階数・面接官の役職・オンラインか対面か・所要時間・筆記や適性検査の有無 | 段階に合わせた想定質問の前提。`exam_assessment.json` と重なる部分は両方を照らす |
| 口コミから読める傾向（`themes`） | 面接官が繰り返し確かめようとする事柄と、そこから見込まれる深掘りの方向 | 推測した質問（`kind: inferred`）の根拠 |

質問が「報告されたもの」か「推測したもの」かは `kind` で区別し、出所の信頼度は `grade` で区別する。この2つを1つの確度にまとめない。報告された質問はその言い回しのまま練習する価値があり、推測した質問は「聞かれる保証は無いが備える価値がある」ものとして利用者へ示す。どちらの枠で示すかを決めるのは `kind` であり、`grade` は根拠となる事実の信頼度を決める。

## 全体構造

```json
{
  "schema_version": "1.0",
  "company": "架空クラウドワークス株式会社",
  "role_title": "バックエンドエンジニア",
  "researched_at": "2026-09-04",
  "reported_questions": [
    {
      "id": "RQ001",
      "question": "現職を離れようと考えた理由を教えてください",
      "kind": "reported",
      "category": "転職理由",
      "stage": "一次面接",
      "source_url": "https://example.com/reviews/kuraudo-works/interview/1",
      "source_name": "転職会議",
      "grade": "C",
      "quote": "「現職を離れようと考えた理由を教えてください」と一次面接で聞かれた",
      "posted_at": "2025-11",
      "accessed": "2026-09-04"
    }
  ],
  "format_facts": [ ],
  "themes": [ ],
  "search_log": [ ],
  "coverage_notes": "",
  "open_questions": [ ]
}
```

記入済みの全体像は `assets/interview_intel_example.json`（架空データ）にある。

## フィールド仕様

### トップレベル

| フィールド | 必須 | 記入基準 |
|---|---|---|
| `schema_version` | 必須 | 現行は `"1.0"`。欠落・空は ERROR。既知の値以外は WARN |
| `company` | 必須 | 企業名。欠落・空は ERROR |
| `role_title` | 任意 | 対象の職種名。文字列または `null`。それ以外は ERROR |
| `researched_at` | 必須 | 調査した日付（`YYYY-MM-DD`）。欠落・形式外・実在しない日付は ERROR |
| `reported_questions` | 必須 | 配列。配列でない場合は ERROR。空配列は WARN |
| `format_facts` | 必須 | 配列。配列でない場合は ERROR。空配列は WARN |
| `themes` | 必須 | 配列。配列でない場合は ERROR。空配列は WARN |
| `search_log` | 必須 | 配列。欠落・配列でない・空配列は ERROR |
| `coverage_notes` | 任意 | 調査の範囲と限界。未記載は WARN |
| `open_questions` | 任意 | 裏取りできなかった論点の配列。配列でない、または非空の文字列でない要素は ERROR |

3配列がすべて空で `open_questions` も空の成果物は ERROR とする（内容が1件も無い成果物は、調査が失敗したのか対象が無いのかを判別できない）。何も見つからなかった場合は、見つからなかった旨と探した経路を `open_questions` と `coverage_notes` に書く。

### 3配列に共通するエビデンス項目

`reported_questions`・`format_facts`・`themes` の各要素は、次の項目を持つ。

| フィールド | 必須 | 記入基準 |
|---|---|---|
| `source_url` | 必須 | 出典URL。`http` で始まらない場合は ERROR |
| `source_name` | 任意 | 出典の名前（転職会議・キャリコネ・採用ページなど） |
| `grade` | 必須 | エビデンスレベル A〜D。4値以外は ERROR。`D` は WARN。定義の原本は `job-change-company-research/references/evidence-grading.md` |
| `quote` | 必須 | 出典からの引用。欠落・空は ERROR。質問を特定するのに必要な最小限の長さにとどめる |
| `posted_at` | 任意 | 出典の投稿日または公開日（`YYYY-MM` または `YYYY-MM-DD`）。読めた場合に書く |
| `accessed` | 必須（null 可） | 取得日（`YYYY-MM-DD`）。未記載・`null` は WARN。形式外・実在しない日付は ERROR |

レベルは発信者で決まる。企業の採用ページは A、大手の転職媒体が公開する調査や解説は B、口コミ・選考体験記の集計サイトは C、個人のブログ・SNS・匿名の掲示板は D である。元社員のブログは C ではなく D である。C・D だけを根拠に、その企業の面接についての事実を断定しない。

### reported_questions[]

| フィールド | 必須 | 記入基準 |
|---|---|---|
| `id` | 必須 | `RQ` に続く3桁以上の数字（`RQ001` 形式）。欠落・形式外・重複は ERROR |
| `question` | 必須 | 質問文。**常に質問の形で書く。**「〜を聞かれる可能性が高い」のような予測の文にしない。推測であることは `kind` が示す。欠落・空は ERROR |
| `kind` | 必須 | `reported`（出典に質問文そのものが報告されている）または `inferred`（出典の記述から質問文を推測した）。2値以外は ERROR |
| `category` | 任意 | 質問類型。語彙の原本は `question-bank.md` の「質問類型と job-change-interview-coach のカテゴリの対応」 |
| `stage` | 任意 | 聞かれた選考段階。`カジュアル面談`・`一次面接`・`二次面接`・`最終面接`・`不明` のいずれか。出典に段階の記載が無ければ `不明` |

`kind` が `reported` のとき、`quote` は質問文を含んでいなければならない。`question` と `quote` が重ならない場合は WARN（報告された質問と言いながら引用に質問が無い）。`kind` が `inferred` のとき、`quote` は推測の根拠となる記述である。

出典に「家族構成を聞かれた」「持ち家か賃貸かを聞かれた」のように、就職差別につながるおそれのある事項（`question-bank.md` の「聞かれても答えなくてよい事項」）に当たる質問が報告されている場合は、`kind: reported`・`category: 配慮事項` で記録する。事実として記録するためであり、練習する質問としてではない。面接対策担当はこの類型の質問を模擬面接に出さず、報告書で「答えなくてよい事項」として示す。

### format_facts[]

| フィールド | 必須 | 記入基準 |
|---|---|---|
| `id` | 必須 | `FF` に続く3桁以上の数字。欠落・形式外・重複は ERROR |
| `statement` | 必須 | 面接の形式についての1つの事実（段階数・面接官の役職・オンラインか対面か・所要時間・筆記や適性検査の有無・カジュアル面談の有無）。欠落・空は ERROR |

採用ページに選考の流れが書かれていれば、それを A として最初に記録する。口コミの記述（C）は、採用ページと食い違う場合に両方を並べ、どちらが新しいかを `posted_at` で示す。検査の種別は `exam_assessment.json`（`job-change-exam-prep`）と重なるため、ここでは有無と段階だけを書き、種別の推定は同スキルに任せる。

### themes[]

| フィールド | 必須 | 記入基準 |
|---|---|---|
| `id` | 必須 | `TH` に続く3桁以上の数字。欠落・形式外・重複は ERROR |
| `theme` | 必須 | 面接官が繰り返し確かめようとしている事柄。欠落・空は ERROR |
| `likely_probe` | 必須 | その傾向から見込まれる深掘りの方向。「〜と考えられる」の形で書く。欠落・空は ERROR |
| `count_note` | 任意 | 傾向の根拠となった回答の件数（例: 「回答12件中5件」）。件数が読めた場合に書く |

傾向は「複数の回答に同じ内容がある」ことを根拠にする。1件の回答から傾向を作らない。件数が少ない場合はその旨を `count_note` に書く。

### search_log[]

実行した検索を1件ずつ記録する。調査の範囲についての主張は、このログだけを根拠とする。

| フィールド | 必須 | 記入基準 |
|---|---|---|
| `query` | 必須 | 実行した検索語、または開いた URL のパス。欠落・空は ERROR |
| `source` | 必須 | 取得元の名前（サイト名、または `WebSearch`）。欠落・空は ERROR |
| `url` | 必須（null 可） | 実際に開いた URL。`http` で始まらない文字列は ERROR |
| `fetched_at` | 必須（null 可） | 取得日時（`YYYY-MM-DD`、または日付で始まる ISO 8601）。形式外は ERROR |
| `hit_count` | 必須（null 可） | 検索結果または回答の件数。負値・整数でない値は ERROR |
| `adopted_count` | 必須（null 可） | そのクエリから3配列へ採用した件数。負値・整数でない値は ERROR |

4つの `null` 可のキーも、キー自体は省略できない（取得できなかったことを `null` で明示する）。ログイン画面へリダイレクトされて読めなかった検索も、`hit_count` を `null` にして記録する。読めなかったことを「情報が無い」と解釈しない。

## 記入の規則

- 出典の文言を `quote` に転記する範囲は、質問または事実を特定するのに必要な最小限にとどめる。口コミの本文を丸ごと転記しない。成果物は利用者本人の面接準備のためのものであり、再配布しない。
- 出典が古いほど、根拠としての価値は下がる。`posted_at` が調査日の5年より前の出典だけを根拠とする質問・事実は、`open_questions` に「古い選考の記録であり、現在の選考と異なりうる」と書く。
- 新卒採用の選考体験記（就活会議・ONE CAREER の新卒向けページなど）は、選考の段階数や面接官の役職のような形式の事実にだけ使い、転職理由・実績の深掘りのような中途固有の質問の根拠にしない。使った場合は `open_questions` に「新卒選考の記録であり、中途の選考体系と異なりうる」と書く。
- 企業の採用ページの「求める人物像」「社員インタビュー」は A の出所だが、企業自身の評価的な主張であり、面接で確かめられる事柄の推測（`themes`）の根拠にはなっても、「聞かれた質問」（`kind: reported`）にはならない。
- 口コミサイトの「退職検討理由」「入社後のギャップ」は、面接の質問の記録ではない。そこから傾向（`themes`）を作る場合、`likely_probe` は面接官が確かめそうな方向として書き、企業に問題があるという断定にしない。
- 利用者の情報（氏名・経歴・現勤務先・年収）を検索語にも成果物にも入れない。指示書で受け取る企業名・職種名・求人URL・出力先だけで調査する。

## 機械的な検証の規則（validate_interview_intel.py）

`scripts/validate_interview_intel.py` が機械的に検査する。ERROR が1件でもあれば FAIL（終了コード1）、ERROR 0件なら PASS（終了コード0。WARN があっても PASS）。

```
python validate_interview_intel.py <interview_intel.json> [--json]
```

**ERROR（成果物として成立しない・ルール違反）**

- JSON として読み込めない、またはルート要素がオブジェクトでない
- `schema_version`・`company`・`researched_at` の欠落・空。`researched_at` が実在する `YYYY-MM-DD` でない
- `role_title` が文字列でも null でもない
- `reported_questions`・`format_facts`・`themes` のいずれかが配列でない、またはその要素がオブジェクトでない
- 各要素の `id` の欠落・形式外・同一配列内での重複
- `reported_questions[]` の `question` が空、`kind` が2値以外
- `format_facts[]` の `statement` が空
- `themes[]` の `theme`・`likely_probe` が空
- 各要素の `source_url` が `http` で始まらない、`grade` が4値以外、`quote` が空、`accessed` が形式外または実在しない日付
- `search_log` の欠落・配列でない・空配列、要素がオブジェクトでない、`query`・`source` が空、`url`・`fetched_at`・`hit_count`・`adopted_count` のキーが欠落、`url` が `http` で始まらない、`fetched_at` が形式外、`hit_count`・`adopted_count` が0以上の整数でも null でもない
- `open_questions` が配列でない、または非空の文字列でない要素を含む
- 3配列がすべて空で `open_questions` も空

**WARN（成立するが不足・整合上の注意）**

- `schema_version` が既知の値以外
- 3配列のいずれかが空
- `grade` が D
- `accessed` が未記載または null
- `kind` が `reported` なのに `question` と `quote` が重ならない
- `coverage_notes` が未記載

検証スクリプトは形式と出典の有無だけを検査する。質問が本当に聞かれたかどうか、傾向の読みが妥当かどうかは検査しない。`category`・`stage`・`posted_at`・`source_name`・`count_note` は検査しない。
