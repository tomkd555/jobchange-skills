# job-change skills

[![CI](https://github.com/tomkd555/jobchange-skills/actions/workflows/ci.yml/badge.svg)](https://github.com/tomkd555/jobchange-skills/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3-3776AB.svg)](#導入)
[![Harness](https://img.shields.io/badge/Harness-Claude%20Code%20%7C%20Codex-6b46c1.svg)](#導入)

日本の中途採用での転職を AI エージェントに手伝わせるためのスキル群です。希望を一文で書くと求人検索が始まり、気になった求人を公式情報で調べ、2 社以上を比べて決めるところまでを支えます。

## スキル一覧

| スキル | 役割 | 主な成果物 |
|---|---|---|
| `job-change-support` | 入口の hub。データの保存先を確認し、依頼を 3 つのスキルへ渡します | `config.json`・`company_index.json` |
| `job-change-job-search` | 希望の一文を条件シートにし、無償の公開 Web 検索と利用者の Chrome で求人を集めます。求人ごとに法定記載の点検と必須条件との照合を付けます | `wishes.json`・`job_search_results.json` |
| `job-change-posting-check` | 求人 1 件と、その会社の有価証券報告書・厚生労働省・しょくばらぼの公表値を 1 つの JSON に記録し、希望条件と照合します | `posting-check.json`・`matches/{求人 ID}.json` |
| `job-change-decision` | 価値観を条件として記録し、2〜5 件の求人や内定を書き出して比べます。重みはスイング法で聞き、5 通りの順位を並べ、決めた理由と妥協した項目を記録します | `decisions/{日付}-{件名}.json` |

書類作成、面接対策、適性検査の対策は、この版には含みません。3 つのスキルを実際の転職活動で使って確かめた後に、別の計画で作り直します。

## 使い方

`/job-change-support` を実行するか、「リモート中心、年収 600 万円以上、SaaS 業界の求人を探したい」のように希望を一文で書いてください。

1. **求人検索:** 希望の一文を 6 項目（職種、業界、年収の下限、勤務地とリモート、雇用形態、その他）の条件シートに整え、あいまいな項目だけを 0〜2 回確かめます。結果は求人ごとに 1 行の表で、必須条件との照合（満たす・満たさない・不明）と、記載のない法定項目（要確認）を付けます。
2. **求人チェック:** 気になった求人を 1 件ずつ調べます。求人票の条件、有価証券報告書の従業員数・平均年齢・平均勤続年数・平均年間給与・業績、労働基準関係法令違反の公表、しょくばらぼの残業時間と有給休暇の取得率を、出典 URL 付きで並べます。
3. **意思決定の支援:** 2 件以上の求人チェックがそろったら、必須条件で絞り、候補の間で値が異なる項目を表にし、重みを聞いて 5 通りの順位を並べます。決めるのは利用者です。

現在の勤務先名と現在の年収は、どのスキルも聞かず、記録しません。

## データの形

利用者のデータは 4 種類の JSON で、同じ項目の辞書（`skills/job-change-support/references/field-catalog.md`）を使います。測った値はどのファイルでも `{value, unit, source_url, grade, as_of, quote}` の形です。`export_flat.py` が 4 種類を「1 行 = 1 候補 × 1 項目」の CSV に書き出すので、表計算ソフトで比較や振り返りができます。

```
{data_root}/
├─ career-private/              個人情報
│   ├─ wishes.json              条件シートと価値観、その変更の記録
│   ├─ company_index.json
│   ├─ matches/{求人 ID}.json     希望条件との照合
│   └─ decisions/{決定 ID}.json   比較と決定の記録
├─ companies/{企業スラッグ}/postings/{求人 ID}/posting-check.json
├─ job-search/{検索 ID}/job_search_results.json
└─ export/flat.csv
```

## エビデンスレベル

企業についての値には、1 件ごとに出典 URL、エビデンスレベル、引用、基準時点を付けます。レベルは A〜D の 4 段階で、誰が発信したかだけで決まります。求人チェックは A（有価証券報告書、厚生労働省、求人票、企業の公式サイト）だけを使います。報道、認定制度、口コミは使いません。

## 個人情報の分離

Web 検索と Web 取得を持つエージェントは、求人検索担当と求人調査担当の 2 体です。この 2 体のコンテキストへは、`career-private/` 配下を加えません。求人検索担当が受け取るのは、条件 ID と条件の文と必須か希望かだけの匿名化した条件シートです。求人調査担当が受け取るのは、会社名と求人票の本文か URL です。

しょくばらぼ、Indeed、Green のように WebFetch で読めないページは、メインのセッションが利用者の Chrome（Claude in Chrome 拡張機能）で開いて読みます。各サイトの利用規約に沿うかどうかは利用者の判断です。

この分離はエージェントへの指示と権限設計によるものです。個人情報が外部へ出ないことの保証は、各人のハーネス設計に依存します。

## 導入

Python 3 が必要です。Web 検索と Web 取得の権限が必要です。Chrome で読む手順には Claude in Chrome 拡張機能が必要です。

### Claude Code

```
/plugin marketplace add https://github.com/tomkd555/jobchange-skills.git
/plugin install job-change@job-change-skills
```

手作業で配置する手順は [docs/install-claude-code.md](docs/install-claude-code.md) にあります。

### Codex

`skills/job-change-*` の 4 ディレクトリを配置してください。手順書は [docs/install-codex.md](docs/install-codex.md) にあります。Codex では Chrome で読む手順が動かないため、しょくばらぼと Indeed、Green の値は入りません。Codex 版は動作を確認していません。

## 1.x からの移行

2.0.0 は 1.x の `profile.json`、`axis.json`、`self_analysis.json`、`fit_assessment.json`、`company_research.json` を読みません。これらのファイルは `career-private/` に残したまま使えます。職歴の記録は、後続の書類作成スキルの計画で `career.json` へ移します。条件は、求人検索を 1 回実行すると `wishes.json` として作り直されます。

## 注意

### 求人サイトの利用規約

対象サイトの利用規約と `robots.txt` は利用者自身で確認し、取得の頻度をサイトへ過度な負荷をかけない範囲に保ってください。

### 免責

このスキル群が作る一覧・調査結果・比較表は判断の材料です。応募や承諾の前に本人が確認してください。企業情報は収集時点の公開情報であり、正確さと最新性を保証しません。待遇、選考プロセス、労働条件は応募先の公式情報で確かめてください。

## ライセンス

MIT License
