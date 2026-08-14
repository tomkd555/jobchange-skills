# self_analysis.json 仕様

job-change-self-analysis スキルにおける、自己分析成果物 self_analysis.json の原本である。`scripts/validate_self_analysis.py` の実装は、この仕様に厳密に従う。

self_analysis.json は、profile.json（利用者データの原本。hub が管理）を土台に、強み・キャリアの軸を行動証拠と他者視点で根拠づけて深化させた成果物である。面接対策（job-change-interview-prep）と志望動機の深化（job-change-documents）が入力として読む。profile.json のスキーマは変更しない。自己分析の結果は profile.json の `strengths`（短文）と `job_change_axis.reasons`（constructive_version に基づく文言）へ値のみ反映する。

## 配置

- 原本の配置先: `{DATA_ROOT}/career-private/self_analysis.json`（非公開ディレクトリ）。
- career-private 配下のパスは、Web 送信手段（WebSearch・WebFetch）を持つエージェントへ渡さない。本スキルの writer・auditor は Web 送信手段を持たないため、渡してよい。
- スキル本体フォルダーに利用者データを置かない。`assets/self_analysis_example.json` は記入例であり、実データではない。

## ルート構造

```json
{
  "schema_version": "1.0",
  "updated_at": "2026-07-16",
  "behavioral_episodes": [ ],
  "others_feedback": [ ],
  "interests": { },
  "values": [ ],
  "career_adaptability": { },
  "strengths": [ ],
  "career_narrative": { },
  "reason_for_change": { },
  "notes": ""
}
```

| フィールド | 型 | 必須/任意 | 意味・記入基準 |
|---|---|---|---|
| `schema_version` | string | 必須 | 仕様のバージョン。現行は `"1.0"`。欠落・空は ERROR |
| `updated_at` | string | 任意 | `YYYY-MM-DD` 形式の最終更新日。欠落は WARN |
| `behavioral_episodes` | array | 必須 | 行動エピソード（STAR素材）の配列。1件以上必須。後述 |
| `others_feedback` | array | 任意 | 他者から受け取ったフィードバックの配列。0件は WARN。後述 |
| `interests` | object | 任意 | 興味。空は WARN。後述 |
| `values` | array | 任意 | 価値観の配列。空は WARN。後述 |
| `career_adaptability` | object | 任意 | career adaptability の4次元。後述 |
| `strengths` | array | 任意 | 根拠づけた強みの配列。後述 |
| `career_narrative` | object | 必須 | キャリア・ナラティブ。後述 |
| `reason_for_change` | object | 必須 | 退職・転職理由。後述 |
| `notes` | string | 任意 | 補足メモ |

## behavioral_episodes

行動エピソード（STAR素材）の配列。1件以上必須。強み・価値観・career adaptability は、ここへ対応づけて裏付ける。

| フィールド | 型 | 必須/任意 | 意味・記入基準 |
|---|---|---|---|
| `id` | string | 必須 | エピソードの識別子（例 `ep-1`）。他フィールドの参照先になる |
| `period` | string | 任意 | 時期。`YYYY-MM〜YYYY-MM` 形式 |
| `situation` | string | 必須 | 状況。欠落・空は ERROR |
| `task` | string | 任意 | 担った課題・役割 |
| `action` | string | 必須 | 実際に取った行動。欠落・空は ERROR |
| `result` | string | 必須 | 結果。欠落・空は ERROR |
| `metric` | string または null | 任意 | 定量値（例「応答時間を62%短縮」）。定量化できない場合は `null` |
| `reproducibility` | string または null | 任意 | 環境が変わっても機能する根拠（再現性）。企業は行動プロセスの再現性を見極める。このため、可能な範囲で書く |
| `emotion_note` | string または null | 任意 | 当時のモチベーション・感情の記録。将来の感情予測ではなく、当時の記録に限る |

- `metric` は可能な限り定量値で埋める。全エピソードを通して `metric` が1件もない場合、検証スクリプトは WARN を出す。
- `situation`・`action`・`result` の3つはエピソードの骨格であり、いずれかが欠けるとエピソードとして成立しないため ERROR とする。

## others_feedback

他者から受け取ったフィードバックの配列。0件は WARN（他者視点の収集を推奨）。

| フィールド | 型 | 必須/任意 | 意味・記入基準 |
|---|---|---|---|
| `id` | string | 必須 | フィードバックの識別子（例 `fb-1`）。strengths の参照先になる |
| `source_type` | string | 任意 | 出所。`上司`／`同僚`／`部下`／`顧客`／`友人・家族`／`評価面談` のいずれか |
| `content` | string | 任意 | 受け取った内容。人格評価ではなく、行動と結果への対応づけで記録する |
| `context` | string | 任意 | いつ・どの場面で受け取ったか |
| `linked_episode_ids` | array | 任意 | 関連する behavioral_episodes の id の配列 |

- フィードバックの受け取りは課題志向で行う。「どの行動が、どの結果につながったか」の形で記録し、「あなたはこういう人だ」という人格評価をそのまま記録しない。

## interests

興味。空（domains と concrete_topics がともに空）は WARN。

| フィールド | 型 | 意味・記入基準 |
|---|---|---|
| `domains` | array | 興味領域の文字列の配列。RIASEC の6領域名（Realistic・Investigative・Artistic・Social・Enterprising・Conventional）等を軸名として使う |
| `concrete_topics` | array | 具体的な関心事の文字列の配列 |

## values

価値観の配列。空は WARN。各要素は価値観1件を表す。

| フィールド | 型 | 意味・記入基準 |
|---|---|---|
| `value` | string | 価値観の記述 |
| `evidence_episode_ids` | array | 裏付けとなる behavioral_episodes の id の配列。内省単独に高い重みを与えないため、可能な限りエピソードへ対応づける |

## career_adaptability

career adaptability の4次元。次元名の枠組みのみを用い、尺度の項目文は転載しない。各次元は同じ構造を持つ。

| 次元 | 意味 |
|---|---|
| `concern` | 関心（将来のキャリアへの関心・準備） |
| `control` | 統制（自らの選択でキャリアを方向づける） |
| `curiosity` | 好奇心（可能性の探索） |
| `confidence` | 自信（課題を乗り越えられる自己効力） |

各次元のオブジェクトは次を持つ。

| フィールド | 型 | 意味・記入基準 |
|---|---|---|
| `self_note` | string | その次元についての自己記述 |
| `evidence_episode_ids` | array | 裏付けとなる behavioral_episodes の id の配列 |

## strengths

根拠づけた強みの配列。**内省単独の強みは認めない。** 各要素は、行動証拠（episode_ids）または他者証言（feedback_ids）の少なくとも一方へ対応づける。

| フィールド | 型 | 必須/任意 | 意味・記入基準 |
|---|---|---|---|
| `statement` | string | 必須 | 強みの短文。欠落・空は ERROR。profile.json の strengths へ反映する短文の素材になる |
| `episode_ids` | array | 条件付き必須 | 裏付けとなる behavioral_episodes の id の配列 |
| `feedback_ids` | array | 条件付き必須 | 裏付けとなる others_feedback の id の配列 |

- `episode_ids` と `feedback_ids` が両方とも空（有効な id が1件もない）の場合は ERROR（内省単独の強み）。少なくとも一方に実在する id を1件以上持つ。
- `episode_ids`・`feedback_ids` が参照する id は、実在する behavioral_episodes / others_feedback の id でなければならない（参照整合。実在しない id の参照は ERROR）。

## career_narrative

キャリア・ナラティブ。Career Construction Interview（CCI）の枠組み（ライフテーマ・転機・一貫する動機）に沿う。narrative-guide.md を参照する。

| フィールド | 型 | 必須/任意 | 意味・記入基準 |
|---|---|---|---|
| `life_theme` | string | 必須 | ライフテーマ。欠落・空は ERROR |
| `turning_points` | array | 任意 | 転機の文字列の配列 |
| `consistent_motivation` | string | 必須 | 一貫する動機。欠落・空は ERROR |
| `future_direction` | string | 任意 | 今後の方向 |

## reason_for_change

退職・転職理由。不満の列挙ではなく、発揮したい価値を軸にした建設的な言い換えへ変換する。narrative-guide.md を参照する。

| フィールド | 型 | 必須/任意 | 意味・記入基準 |
|---|---|---|---|
| `raw_reasons` | array | 必須 | 元の理由（不満を含む素の理由）の配列。1件以上必須（空は ERROR） |
| `constructive_version` | string | 必須 | 発揮したい価値を軸にした説明。欠落・空は ERROR |
| `consistency_note` | string | 任意 | profile.json の `job_change_axis.reasons` との整合の説明 |

- `constructive_version` が `raw_reasons` のいずれかと同一文字列のままの場合は WARN（建設的な言い換えができていない）。

## 検証規則の要約

`validate_self_analysis.py` は次を検査する。ERROR が1件でもあれば FAIL（終了コード 1）、ERROR 0件なら PASS（終了コード 0。WARN は許容）。読込は BOM 付き UTF-8（`utf-8-sig`）に対応する。

### ERROR（成果物として成立しない）

- JSON として読み込めない
- `schema_version` の欠落または空
- `behavioral_episodes` が空、または各要素で `situation`・`action`・`result` のいずれかが欠落・空
- `strengths` の要素で `statement` が欠落・空
- `strengths` の要素で `episode_ids` と `feedback_ids` が両方とも空（内省単独の強み）
- `strengths`・`values`・`career_adaptability` が参照する `episode_id` / `feedback_id` が実在しない（参照整合エラー）
- `career_narrative.life_theme` または `consistent_motivation` の欠落・空
- `reason_for_change.raw_reasons` が空、または `constructive_version` の欠落・空

### WARN（成立するが情報不足で成果物の質を下げる）

- `others_feedback` が0件（他者視点の欠落）
- 全エピソードを通して `metric` が1件もない
- `updated_at` の欠落
- `interests` が空（domains・concrete_topics がともに空）
- `values` が空
- `constructive_version` が `raw_reasons` と同一文字列のまま
