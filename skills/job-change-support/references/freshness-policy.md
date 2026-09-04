# 再調査期限のポリシー（freshness-policy）

企業別の成果物に再調査が必要かどうか（fresh・stale・missing）を判定する方針の原本である。判定の根拠は `companies/{企業スラッグ}/_manifest.json` であり、その仕様と TTL 対応表もここに置く。判定するツールは `scripts/check_freshness.py` である。

## 方針

- `companies/{企業スラッグ}/` は消さずに残す保管場所であり、TTL を超過しても成果物ファイルの削除・移動は行わない。
- TTL 超過は、hub（job-change-support）が `job-change-company-research` へ「stale と判定されたトピックだけを調べ直すこと」を指示する根拠になる。stale でないトピック・fresh な成果物は再調査しない。既存の成果物をそのまま再利用する。
- `_manifest.json` を書くのは、各成果物を作るスキル自身である。`job_posting` の欄は `job-change-company-research` が求人票の取得時に、`company_research` の欄は同スキルがトピック調査の完了時に、それぞれ更新する。`check_freshness.py` は判定のみを担い、`_manifest.json` を書き換えない。

## `_manifest.json` の仕様

```json
{
  "schema_version": 1,
  "artifacts": {
    "job_posting": {
      "updated_at": "2026-07-01",
      "source_url": "https://example.com/jobs/123"
    },
    "company_research": {
      "updated_at": "2026-07-10",
      "audit_verdict": "CLEAN",
      "audited_at": "2026-07-10",
      "topics": {
        "philosophy": {"last_researched": "2026-06-01"},
        "workstyle": {"last_researched": "2026-07-10"}
      }
    }
  }
}
```

| フィールド | 型 | 意味 |
|---|---|---|
| `schema_version` | number | 仕様のバージョン。現行は `1` |
| `artifacts` | object | 成果物名をキーとするオブジェクト |
| `artifacts.job_posting` | object \| null | 求人票の取得状況。`updated_at`（`YYYY-MM-DD`）・`source_url` を持つ。`source_url` は URL から取り込んだ場合のみ値を持ち、本文・ファイル・対話から作った場合は `null` である。未取得は `null` |
| `artifacts.company_research` | object \| null | 企業研究の実施状況。`updated_at`（最終更新日）と、トピック名をキーとし `last_researched`（`YYYY-MM-DD`）を値に持つ `topics` オブジェクト、および `audit_verdict`・`audited_at` を持つ。未実施は `null` |
| `artifacts.company_research.audit_verdict` | string | 独立監査の判定。`CLEAN`・`CONCERNS`・`BLOCK` のいずれか。書くのは `job-change-company-research` である |
| `artifacts.company_research.audited_at` | string | 監査を行った日付（`YYYY-MM-DD`） |

`artifacts` には、上記2件のほかに、`exam_assessment` などの成果物を `{updated_at: "YYYY-MM-DD"}` の形で自由に追加してよい。記録してよいのは成果物名と日付だけであり、個人情報とその派生値は書かない（原本は `pii-boundary.md`）。`check_freshness.py` は `job_posting`・`company_research` の2件は常に判定の対象とする。

これに加えて、次の任意成果物は、`artifacts` に記録がある場合に限り判定する。記録が無い場合と、値が `null` の場合（未取得の明示）は `missing` にせず、判定結果に現れない。記録があって `updated_at` が欠落・不正な場合、またはオブジェクトでない場合は `missing` とする。上記以外のキーは判定せず読み飛ばす。

| 任意成果物 | 書き手 | TTL（日） |
|---|---|---|
| `interview_intel` | `job-change-interview-prep`（Step 0.9 の面接情報の調査の完了時に `{updated_at: "YYYY-MM-DD"}` を書く） | 180 |

任意成果物が `stale` または `missing` と判定された場合、hub は `job-change-company-research` ではなく、その成果物を書いたスキルへ再調査を渡す。

## トピック名と TTL 対応表

`company_research.topics` のキーは、`job-change-company-research` スキルの `references/company-research-format.md` が定める8種のトピック名と一致させる。TTL（日数）はトピックの性質で決める。性質は、報道・ニュース、給与・福利厚生・働き方、理念・事業の3つに分け、対応は次のとおりとする。

| topic | 分類 | TTL（日） |
|---|---|---|
| `philosophy` | 恒常系 | 365 |
| `business` | 恒常系 | 365 |
| `financials` | 給与・福利厚生・働き方系 | 180 |
| `compensation` | 給与・福利厚生・働き方系 | 180 |
| `benefits` | 給与・福利厚生・働き方系 | 180 |
| `workstyle` | 給与・福利厚生・働き方系 | 180 |
| `reputation` | 報道・ニュース系 | 90 |
| `selection_process` | 既定 | 180 |

上の対応表に無いトピック名が `company_research.topics` に現れた場合は、既定 TTL（180日）を適用する。`job_posting` の TTL は `topics` とは別枠で 30日とする。

## 判定規則

判定の基準日は `--today` に指定した日付で、未指定なら実行時点の日付である。`check_freshness.py` はこの基準日と各成果物の最終日付との経過日数を求め、経過日数が TTL 以下であれば `fresh`、TTL を超えていれば `stale` とする。TTL ちょうどは `fresh` 側に含める。

- `job_posting`: `artifacts.job_posting` が無い・`null`、または `updated_at` が欠落・不正な日付形式の場合は `missing` とする。それ以外は `updated_at` と TTL=30日で判定する。
- `company_research`: `artifacts.company_research` が無い・`null` の場合、トピック単位の判定は行わず `company_research` 全体を `missing` とする。存在する場合は、`topics` 配下の各トピックについて `last_researched` の有無・形式を確認する。欠落・不正な場合はそのトピックを `missing` とし、それ以外は対応表の TTL で `fresh`/`stale` を判定する。`topics` が無い・`null`・オブジェクト以外の場合は、トピック単位の判定は行わず `company_research` 全体を `missing` とする。`topics` が空のオブジェクトの場合は、トピックが1件も無いものとして扱い、判定対象にしない。
- `_manifest.json` が存在しない、または JSON として読み込めない場合、`job_posting`・`company_research` の両方を `missing` として報告する。終了コードは 0 のままとする。再調査の要否を伝えるのが本ツールの役割であり、manifest 未整備を FAIL 扱いにしない。
