# job-change skills

[![CI](https://github.com/tomkd555/jobchange-skills/actions/workflows/ci.yml/badge.svg)](https://github.com/tomkd555/jobchange-skills/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB.svg)](#導入)
[![Harness](https://img.shields.io/badge/Harness-Claude%20Code%20%7C%20Codex-6b46c1.svg)](#導入)

日本の中途採用での転職を AI エージェントに手伝わせるためのスキル群です。プロファイルの作成から企業研究、応募書類、面接対策まで行います。

## スキル一覧

| スキル | 役割 | 主な成果物 |
|---|---|---|
| `job-change-support` | 入口の hub。依頼を判別し、設定とプロファイルを確認してから各スキルへ渡します | `config.json`・`company_index.json` |
| `job-change-profile` | 職務経歴・スキル・転職の軸を聞き取り記録します | `profile.json` |
| `job-change-self-analysis` | 行動の記録・他者からの評価・行動傾向の聞き取りをもとに自己分析を進めます | `self_analysis.json` |
| `job-change-job-search` | Web 検索で求人を集め、掲載ページの引用と出典 URL を付けます | `job_search_results.json` |
| `job-change-company-research` | 求人を起点に企業を調べます | `job_posting.json`・`company_research.json` |
| `job-change-fit-assessment` | 条件と本人評価基準を紐づけます | `fit_assessment.json`・`time_analysis.json` |
| `job-change-documents` | 職務経歴書・履歴書・志望動機などを作成します | `documents/` 配下の各書類 |
| `job-change-exam-prep` | 筆記試験・適性検査の種別を調べ、対策を立てます | `exam_assessment.json`・`exam-prep-plan.md` |
| `job-change-interview-prep` | 企業の面接について口コミ・採用ページを調べ、企業ごとの想定質問を作り、回答に評価を返します | `interview_intel.json`・`interview_questions.json`・`interview_evaluation.json`・`interview-prep-report.md` |

## エビデンスレベル

企業についての主張には、1 件ごとに出典 URL・エビデンスレベル・原文のままの引用・取得日を付けます。レベルは A〜D の 4 段階で、内容がもっともらしいかどうかではなく、誰が発信したかで決まります。

| レベル | 区分 | 具体例 |
|---|---|---|
| **A** | 一次・公式 | EDINET 有価証券報告書、決算説明資料、企業公式サイト、統合報告書、公的統計・政府の認定制度データベース、査読済みの学術研究 |
| **B** | 信頼できる二次 | 大手報道機関、就職四季報、業界レポート、公的機関の解説ページ |
| **C** | 口コミ・集計サイト | OpenWork・Glassdoor 等の口コミ集計、選考体験記の集計サイト |
| **D** | 個人ブログ・伝聞・未確認 | 個人ブログ、SNS の伝聞、出所不明の転載、単発の匿名投稿 |

## 個人情報の分離

利用者データは 2 つの系統に分かれます。個人情報を置く `career-private/` と、それ以外を置く `companies/`・`job-search/` です。

```
{data_root}/
├─ career-private/            個人情報
│   ├─ profile.json
│   ├─ self_analysis.json
│   ├─ company_index.json
│   ├─ commute.json
│   └─ fit/{企業スラッグ}/
├─ companies/{企業スラッグ}/    企業ごとの成果物
└─ job-search/{検索ID}/        求人検索の結果
```

Web 検索と Web 取得を持つ 6 体のエージェント（企業研究とその監査・求人票の取り込み・求人検索・試験情報の調査・面接情報の調査）は、`career-private/` 配下をコンテキストに加えないようにしています。

この分離はエージェントへの指示と権限設計によるもので、個人情報が外部へ出ないということは保証できません。各人のハーネス設計に依存します。

## 導入

Python 3.9 以上が必要です。

Web searchと Web fetchの権限が必要です。

### Claude Code

```
/plugin marketplace add https://github.com/tomkd555/jobchange-skills.git
/plugin install job-change@job-change-skills
```

プラグインを使わず手作業で配置する手順は [docs/install-claude-code.md](docs/install-claude-code.md) にあります。

### Codex

`skills/job-change-*` の 9 ディレクトリを配置してください。手順書は [docs/install-codex.md](docs/install-codex.md) にあります。Codex 版は未テストです。

## 使い方

 `/job-change-support` を実行してください。


## 注意

### 求人サイトの利用規約

対象サイトの利用規約と `robots.txt` は利用者自身で確認し、取得の頻度をサイトへ過度な負荷をかけない範囲に保ってください。

### 免責

このスキル群が作る書類・評価・想定質問は下書きです。応募に使う前に本人が確認してください。企業情報は収集時点の公開情報であり、正確さと最新性を保証しません。待遇・選考プロセス・労働条件は応募先の公式情報で確かめてください。

## ライセンス

MIT License
