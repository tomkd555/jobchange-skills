# job-change skills

[![CI](https://github.com/tomkd555/jobchange-skills/actions/workflows/ci.yml/badge.svg)](https://github.com/tomkd555/jobchange-skills/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3-3776AB.svg)](#導入)
[![Harness](https://img.shields.io/badge/Harness-Claude%20Code%20%7C%20Codex-6b46c1.svg)](#導入)

日本の中途採用での転職を AI エージェントに手伝わせるためのスキル群です。プロファイルの作成から企業研究、応募書類、面接対策まで行います。

## スキル一覧

| スキル | 役割 | 主な成果物 |
|---|---|---|
| `job-change-support` | 入口の hub。依頼を判別し、設定・職歴の記録・転職の軸を確認してから各スキルへ渡します | `config.json`・`company_index.json` |
| `job-change-profile` | 職務経歴・実績・スキルを聞き取り記録します | `profile.json` |
| `job-change-axis` | 転職理由・条件・仕事の特性・企業の採点軸を聞き取り、転職の軸として記録します | `axis.json` |
| `job-change-self-analysis` | 行動の記録・他者からの評価・行動傾向の聞き取りをもとに自己分析を進めます | `self_analysis.json` |
| `job-change-job-search` | Web 検索で求人を集め、掲載ページの引用と出典 URL を付けます。主条件に加えて、条件を良くする・範囲を広げる派生レーンを並列に検索し、結果に出た全企業の基本情報と公表値も集めます | `job_search_results.json` |
| `job-change-company-research` | 求人を起点に企業を調べます | `job_posting.json`・`company_research.json` |
| `job-change-fit-assessment` | 条件と本人が決めた評価基準を紐づけます | `fit_assessment.json`・`time_analysis.json` |
| `job-change-documents` | 職務経歴書・履歴書・志望動機などを作成します。応募先を決める前の汎用版も作れます | `documents/` 配下の各書類 |
| `job-change-exam-prep` | 筆記試験・適性検査の種別を調べ、対策を立てます | `exam_assessment.json`・`exam-prep-plan.md` |
| `job-change-interview-prep` | 企業の面接について口コミ・採用ページを調べ、企業ごとの想定質問を作り、回答に評価を返します | `interview_intel.json`・`interview_questions.json`・`interview_evaluation.json`・`interview-prep-report.md` |

## 書類の系統と軸の系統

書類の整備と転職の軸は、別々の系統として進められます。

| 系統 | スキル | 原本 |
|---|---|---|
| 書類 | `job-change-profile`・`job-change-documents` | `profile.json`（職歴・実績・スキル） |
| 軸 | `job-change-axis`・`job-change-self-analysis` | `axis.json`（転職理由・条件・仕事の特性・採点軸・希望年収） |

職歴の聞き取りが済めば、応募先を決める前でも汎用の職務経歴書と履歴書を作れます。求人検索と適合性評価は両方の原本を使います。

schema_version 2.0 以前の `profile.json` は、職歴と転職の軸を 1 つのファイルに持っています。このファイルは最初の更新時に、バックアップを取ったうえで `profile.json` と `axis.json` へ分かれます。

## エビデンスレベル

企業についての主張には、1 件ごとに出典 URL・エビデンスレベル・原文のままの引用・取得日を付けます。レベルは A〜D の 4 段階で、誰が発信したかだけで決まります。

| レベル | 区分 | 具体例 |
|---|---|---|
| **A** | 一次・公式 | EDINET 有価証券報告書、決算説明資料、企業公式サイト、統合報告書、公的統計・政府の認定制度データベース、査読済みの学術研究 |
| **B** | 信頼できる二次 | 大手報道機関、就職四季報、業界レポート、公的機関の解説ページ |
| **C** | 口コミ・集計サイト | OpenWork・Glassdoor 等の口コミ集計、選考体験記の集計サイト |
| **D** | 個人ブログ・伝聞・未確認 | 個人ブログ、SNS の伝聞、出所不明の転載、単発の匿名投稿 |

## 個人情報の分離

利用者データは 2 つの系統に分かれます。個人情報を保存する `career-private/` と、企業別の成果物と求人検索結果を保存する `companies/`・`job-search/` です。

```
{data_root}/
├─ career-private/            個人情報
│   ├─ profile.json
│   ├─ axis.json
│   ├─ self_analysis.json
│   ├─ company_index.json
│   ├─ commute.json
│   ├─ documents/             応募先を決める前の汎用書類
│   └─ fit/{企業スラッグ}/
├─ companies/{企業スラッグ}/    企業ごとの成果物
└─ job-search/{検索ID}/        求人検索の結果
```

企業研究とその監査・求人票の取り込み・求人検索・試験情報の調査・面接情報の調査を担う 6 体のエージェントは、Web 検索と Web 取得を持ちます。この 6 体のコンテキストへは、`career-private/` 配下を加えません。

この分離はエージェントへの指示と権限設計によるものです。個人情報が外部へ出ないことの保証は、各人のハーネス設計に依存します。

## 導入

Python 3 が必要です。

Web 検索と Web 取得の権限が必要です。

### Claude Code

```
/plugin marketplace add https://github.com/tomkd555/jobchange-skills.git
/plugin install job-change@job-change-skills
```

プラグインを使わず手作業で配置する手順は [docs/install-claude-code.md](docs/install-claude-code.md) にあります。

### Codex

`skills/job-change-*` の 10 ディレクトリを配置してください。手順書は [docs/install-codex.md](docs/install-codex.md) にあります。Codex 版は動作を確認していません。

## 使い方

 `/job-change-support` を実行してください。


## 注意

### 求人サイトの利用規約

対象サイトの利用規約と `robots.txt` は利用者自身で確認し、取得の頻度をサイトへ過度な負荷をかけない範囲に保ってください。

### 免責

このスキル群が作る書類・評価・想定質問は下書きです。応募で使う前に本人が確認してください。企業情報は収集時点の公開情報であり、正確さと最新性を保証しません。待遇・選考プロセス・労働条件は応募先の公式情報で確かめてください。

## ライセンス

MIT License
