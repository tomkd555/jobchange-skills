# 鮮度ポリシー（freshness-policy）

`companies/{企業スラッグ}/_manifest.json` を根拠に、企業別成果物の鮮度（fresh・stale・missing）を判定する方針と、`_manifest.json` の仕様・TTL 対応表の原本である。判定するツールは `scripts/check_freshness.py` である。

## 方針

- `companies/{企業スラッグ}/` は恒久アーカイブである。TTL を超過しても、成果物ファイルの削除・移動は行わない。
- TTL 超過は、hub（job-change-support）が `job-change-company-research` へ「stale と判定されたトピック限定の差分再調査」を指示する根拠になる。stale でないトピック・fresh な成果物は再調査せず、既存の成果物をそのまま再利用する。
- `_manifest.json` の書き手は、各成果物を作るスキル自身である（`job_posting` は `job-change-company-research` が求人票取得時に、`company_research` は同スキルがトピック調査完了時に、それぞれ自分の担当箇所を更新する）。`check_freshness.py` は判定のみを担い、`_manifest.json` を書き換えない。

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
| `artifacts.company_research` | object \| null | 企業研究の実施状況。`updated_at`（最終更新日）と、トピック名をキーとし `last_researched`（`YYYY-MM-DD`）を値に持つ `topics` オブジェクトを持つ。未実施は `null` |

`artifacts` には、上記2件のほかに、`fit_assessment` 等の成果物を `{updated_at: "YYYY-MM-DD"}` の形で自由に追加してよい。`check_freshness.py` は `job_posting`・`company_research` の2件のみを既知成果物として判定対象にし、それ以外のキーは判定せず読み飛ばす。

## トピック名と TTL 対応表

`company_research.topics` のキーは、`job-change-company-research` スキルの `references/company-research-format.md` が定める8種のトピック名と一致させる。TTL（日数）はトピックの性質（報道・ニュース系／給与・福利厚生・働き方などの数値系／理念・事業などの恒常系）に応じて次のとおり分類する。

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

`check_freshness.py` は、`--today` に指定した日付（未指定時は実行時点の日付）を基準に、各成果物の最終日付との差分日数（経過日数）を求める。経過日数が TTL 以下であれば `fresh`、TTL を超えていれば `stale` とする（TTL ちょうどの経過日数は `fresh` 側に含める）。

- `job_posting`: `artifacts.job_posting` が無い・`null`、または `updated_at` が欠落・不正な日付形式の場合は `missing` とする。それ以外は `updated_at` と TTL=30日で判定する。
- `company_research`: `artifacts.company_research` が無い・`null` の場合、トピック単位の判定は行わず `company_research` 全体を `missing` とする。存在する場合は、`topics` 配下の各トピックについて、`last_researched` の有無・形式を確認し、欠落・不正な場合はそのトピックを `missing` とする。それ以外は対応表の TTL で `fresh`/`stale` を判定する。
- `_manifest.json` が存在しない、または JSON として読み込めない場合、`job_posting`・`company_research` の両方を `missing` として報告する（終了コードは 0 のままとする。鮮度情報の提供が本ツールの役割であり、manifest 未整備を FAIL 扱いにしない）。
