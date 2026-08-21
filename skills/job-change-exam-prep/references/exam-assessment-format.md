# exam_assessment.json の原本仕様（exam-assessment-format）

検査種別の調査結果 `exam_assessment.json` のフィールド仕様・記入基準・機械的な検証の規則を定める原本である。選考試験の調査担当エージェント（job-change-exam-scout）がこの仕様で成果物を作る。`scripts/validate_exam_assessment.py` は、この仕様に照らして機械的に検査する。

出力先は `{DATA_ROOT}/companies/{企業スラッグ}/exam_assessment.json` である。企業が特定できない汎用の対策依頼では、企業スラッグの代わりに `_general/` を用いる。

## 全体構造

```json
{
  "company": "架空クラウドワークス株式会社",
  "assessments": [
    {
      "type": "SPI3",
      "stage": "書類選考通過後・一次面接前",
      "evidence": [
        {
          "source_url": "https://example.com/careers/process",
          "grade": "A",
          "quote": "書類選考の通過者には、一次面接の前に SPI3（テストセンター）の受検を案内します。"
        }
      ],
      "confidence": "確定",
      "format_notes": "テストセンター方式。言語・非言語の能力検査と性格検査で構成される。",
      "prep_recommendations": ["非言語の頻出分野を反復練習する", "テストセンター方式の操作に慣れておく"]
    }
  ],
  "open_questions": ["性格検査の実施が同一日程かどうかは確認できていない。"]
}
```

記入済みの全体像は `assets/exam_assessment_example.json`（架空データ）にある。

## フィールド仕様

### company（文字列・必須）

調査対象の企業名（正式名称）。欠落・空は ERROR。

### assessments（配列・必須）

特定した検査種別の配列。配列でない場合は ERROR。空配列は WARN（種別を特定できなかった事情を `open_questions` に記すことを推奨する）。`assessments` が空で `open_questions` も空の場合は、成果物が何も述べていないため ERROR とする。

### assessments[].type（文字列・必須）

検査の名称。欠落・空は ERROR。名称の語彙の原本は `references/assessment-catalog.md` であり、ここへは複製しない。カタログが扱わない検査名は WARN として通す（カタログに載らない検査を企業が使う場合があるため、ERROR にはしない）。

### assessments[].stage（文字列・必須）

選考のどの段階で実施されるか（「書類選考の通過後」「一次面接前」など）。欠落・空は WARN。段階が不明でも成果物としては成立するため、ERROR にはしない。

### assessments[].evidence（配列・必須）

その種別を特定した根拠。配列でない場合は ERROR。空配列は ERROR とする（出典 URL のない断定を禁じるためである）。各要素は次を持つ。

| フィールド | 必須 | 記入基準 |
|---|---|---|
| `source_url` | 必須 | 根拠ページの URL。`http` で始まる文字列でなければならない（欠落・不一致は ERROR） |
| `grade` | 必須 | エビデンスレベル `A` / `B` / `C` / `D` のいずれか。他の値・欠落は ERROR |
| `quote` | 必須 | 根拠ページからの引用。欠落・空は ERROR |

`grade` の定義と付与ルールの原本は `job-change-company-research/references/evidence-grading.md` である。選考試験の文脈での当てはめは、役割プロンプト `references/roles/exam-scout.md` に書いてある。採用ページ・企業公式の選考案内をレベル A、選考体験記の集計サイトをレベル C、個人ブログの単発体験記をレベル D とする。

### assessments[].confidence（文字列・必須）

その種別の確度。次の2値のいずれかとする。欠落・空、または2値以外は ERROR。

| 値 | 意味 |
|---|---|
| `確定` | 採用ページ・企業公式の選考案内など、レベル A の出典で種別が明記されている |
| `推定` | 選考体験記など、レベル A 以外の出典からの類推である |

`確定` は、`evidence` に `grade` が `A` の要素を1件以上含むことを要件とする。含まない場合は ERROR とする（単一の伝聞のみを根拠に「確定」とすることを構造的に防ぐ）。

`推定` で `evidence` が1件のみの場合は WARN とする。根拠が単一の体験記のみである種別に当たり、対策計画でその限界を明示する必要があるためである。

### assessments[].format_notes（文字列・必須）

出題形式（科目構成・時間・実施方式の特徴）の要約。欠落・空は WARN。

### assessments[].prep_recommendations（配列・必須）

一般的な推奨対策の方向性。非空の文字列の配列とする。配列でない、または非空の文字列でない要素を含む場合は ERROR。空配列は WARN。

### open_questions（配列・必須）

裏取りできなかった論点、受検案内の到着後に確認すべき点などを記す。配列でない、または非空の文字列でない要素を含む場合は ERROR。

## 機械的な検証の規則（validate_exam_assessment.py）

`scripts/validate_exam_assessment.py` が機械的に検査する。ERROR が1件でもあれば FAIL（終了コード1）、ERROR 0件なら PASS（終了コード0。WARN があっても PASS）。

```
python validate_exam_assessment.py <exam_assessment.json> [--json]
```

**ERROR（成果物として成立しない・ルール違反）**

- JSON として読み込めない、またはルート要素がオブジェクトでない
- `company` の欠落・空
- `assessments` が配列でない
- `assessments` が空で `open_questions` も空
- `type` の欠落・空
- `evidence` が配列でない、または空配列
- `source_url` が欠落、または `http` で始まらない
- `grade` が `A`／`B`／`C`／`D` 以外
- `quote` の欠落・空
- `confidence` が `確定`／`推定` 以外
- `confidence` が `確定` なのに `evidence` にレベル A の要素が無い
- `prep_recommendations`・`open_questions` が配列でない、または非空の文字列でない要素を含む

**WARN（成立するが不足・確度上の注意）**

- `assessments` が空配列
- `type` が `assessment-catalog.md` の扱う検査名ではない
- `stage` の欠落・空
- `confidence` が `推定` で `evidence` が1件のみ
- `format_notes` の欠落・空
- `prep_recommendations` が空配列

## 機械的な検査が及ばない範囲

次は機械では判定できず、人の判断に残る。

- 出典の内容が本当にその検査種別を述べているか（`quote` と `type` の対応）。
- エビデンスレベルの付与そのものの妥当性（口コミを A へ格上げしていないか、採用ページを C へ格下げしていないか）。
- 複数の出典が食い違う場合の採否。
- 「推定」の種別を対策計画でどこまで前提にしてよいかの線引き。
