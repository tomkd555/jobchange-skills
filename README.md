# job-change skills

[![CI](https://github.com/tomkd555/jobchange-skills/actions/workflows/ci.yml/badge.svg)](https://github.com/tomkd555/jobchange-skills/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB.svg)](#導入)
[![Harness](https://img.shields.io/badge/Harness-Claude%20Code%20%7C%20Codex-6b46c1.svg)](#導入)

日本の中途採用での転職を AI エージェントに手伝わせるためのスキル群です。プロファイルの作成から企業研究、応募書類、面接対策までを、スキルとエージェントで分担します。

企業の下調べを AI に任せたとき、出てきた文章のどこまでが裏の取れた事実で、どこからが推測なのかは、読んだだけでは区別がつきません。このスキル群はそこを設計の中心に置きました。企業についての記述には出典 URL とエビデンスレベルを付けます。成果物の形式は検証スクリプトが検査し、書いたエージェントとは別のエージェントが監査します。個人情報は、Web へ送信できるエージェントの作業場所から切り離す様に指示をしています。

## スキル一覧

| スキル | 役割 | 主な成果物 |
|---|---|---|
| `job-change-support` | 入口の hub。依頼を判別し、設定とプロファイルを確認してから各スキルへ渡します | `config.json`・`company_index.json` |
| `job-change-profile` | 職務経歴・スキル・転職の軸を聞き取ります | `profile.json` |
| `job-change-self-analysis` | 行動の記録と他者からの評価をもとに自己分析を進めます | `self_analysis.json` |
| `job-change-job-search` | Web 検索で求人を集め、掲載ページの引用と出典 URL を付けます | `job_search_results.json` |
| `job-change-company-research` | 求人票を起点に企業を調べます | `job_posting.json`・`company_research.json` |
| `job-change-fit-assessment` | 求人と本人を 7 つの観点で照合し、拘束時間と実質時給を算定します | `fit_assessment.json`・`time_analysis.json` |
| `job-change-documents` | 職務経歴書・履歴書・志望動機などを作成します | `documents/` 配下の各書類 |
| `job-change-exam-prep` | 筆記試験・適性検査の種別を調べ、対策を立てます | `exam_assessment.json`・`exam-prep-plan.md` |
| `job-change-interview-prep` | 企業ごとの想定質問を作り、回答に評価を返します | `interview_questions.json`・`interview_evaluation.json`・`interview-prep-report.md` |

## エビデンスレベル

企業についての主張には、1 件ごとに出典 URL・エビデンスレベル・原文のままの引用・取得日を付けます。レベルは A〜D の 4 段階で、内容がもっともらしいかどうかではなく、誰が発信したかで決まります。

| レベル | 区分 | 具体例 |
|---|---|---|
| **A** | 一次・公式 | EDINET 有価証券報告書、決算説明資料、企業公式サイト、統合報告書、公的統計・政府の認定制度データベース、査読済みの学術研究 |
| **B** | 信頼できる二次 | 大手報道機関、就職四季報、業界レポート、公的機関の解説ページ |
| **C** | 口コミ・集計サイト | OpenWork・Glassdoor 等の口コミ集計、選考体験記の集計サイト |
| **D** | 個人ブログ・伝聞・未確認 | 個人ブログ、SNS の伝聞、出所不明の転載、単発の匿名投稿 |

この分類から制約が 2 つ出ます。C と D だけを根拠に、事実は断定できません。また、企業自身が発信する評価的な主張（採用サイトの「風通しが良い」など）は、出所がレベル A でも確信度を high にできません。発信元が一次であることと、内容が検証済みであることは別だからです。

企業研究の成果物 `company_research.json` では、主張 1 件がこう記録されます。

```json
{
  "id": "C001",
  "topic": "philosophy",
  "statement": "パーパスとして「働くをなめらかに」を掲げ、統合報告書で行動指針を4項目に整理して明文化している。",
  "evidence": [
    {
      "source_url": "https://www.kakuu-cloudworks.example.co.jp/company/purpose/",
      "source_name": "架空クラウドワークス 企業サイト 理念ページ",
      "grade": "A",
      "quote": "私たちのパーパスは「働くをなめらかに」です。行動指針として、誠実・挑戦・協働・学習の4つを定めています。",
      "accessed": "2026-07-12"
    }
  ],
  "confidence": "medium"
}
```

この例の `confidence` が `medium` にとどまるのは、出典がレベル A でも、内容が企業の自己申告にあたるためです。レベル C・D だけを根拠に `high` を付けると、`validate_company_research.py` が ERROR を返します。判定基準の全体は [skills/job-change-company-research/references/evidence-grading.md](skills/job-change-company-research/references/evidence-grading.md) にあります。

## 検証と監査

9 本の検証スクリプトが、成果物の形式と内容の規則を検査します。終了コード 0 が PASS、1 が FAIL です。この終了コードが工程の通過条件で、エージェントの自己申告は判定に使いません。企業ごとの工程は、求人票の取り込み、企業研究、適合性評価の順に進み、前の段階が PASS しないうちは次へ入りません。

```bash
python skills/job-change-support/scripts/jc_config.py --show
python skills/job-change-support/scripts/validate_profile.py <profile.json> --json
```

作る側と監査する側も分けています。プロファイル・自己分析・企業研究・応募書類の 4 スキルでは、成果物を作る担当と監査する担当が別のエージェントです。監査担当には作成時の判断理由を渡さず、成果物と仕様だけを見て判定させます。書いた本人に点検させると、自分の判断をなぞるだけになりがちだからです。企業研究の監査は CLEAN・CONCERNS・BLOCK のいずれかを返し、BLOCK が付いた成果物は差し戻しになります。

中断した作業の再開位置は、成果物が存在するかと、いつ調べたものかの 2 点だけで決めます。会話の記憶には頼りません。再調査までの期限を過ぎたトピックだけが調べ直しの対象になります。期限は成果物ごとに違い、求人票は 30 日、評判は 90 日、理念・事業は 365 日、財務・報酬・働き方・選考プロセスは 180 日です。

検証スクリプトには 14 ファイルの単体テストがあり、CI が Python 3.9 と 3.13 の両方で実行します。

## 個人情報の分離

利用者データは 2 つの系統に分かれます。個人情報を置く `career-private/` と、それ以外を置く `companies/`・`job-search/` です。

```
{data_root}/
├─ career-private/            個人情報。Web を使うエージェントへは渡しません
│   ├─ profile.json
│   ├─ self_analysis.json
│   ├─ company_index.json
│   ├─ commute.json
│   └─ fit/{企業スラッグ}/
├─ companies/{企業スラッグ}/    企業ごとの成果物。{企業スラッグ}は応募先 1 社ごとの識別子
└─ job-search/{検索ID}/        求人検索の結果
```

企業研究・求人検索・求人票取込の 3 体のエージェントは WebSearch と WebFetch を持つため、`career-private/` 配下のパスも内容も受け取りません。企業研究の起動時に hub が渡すのは、企業を数値で採点する観点の名前だけです。逆に、適合性評価を担当するエージェントは Web ツールを一切持たず、個人情報を読める唯一の担当になっています。

ただし、この分離はエージェントへの指示と権限設計によるものです。LLM の仕様上、個人情報が外部へ出ないことの保証まではできません。

## 導入

Python 3.9 以上が必要です。検証スクリプトを動かすために使い、依存は標準ライブラリだけです。求人検索と企業研究には、Web 検索と Web 取得のできる AI エージェントが必要です。

### Claude Code

```
/plugin marketplace add https://github.com/tomkd555/jobchange-skills.git
/plugin install job-change@job-change-skills
```

clone 済みなら、URL の代わりにそのパスを指定します。プラグインを使わず手作業で配置する手順は [docs/install-claude-code.md](docs/install-claude-code.md) にあります。

### Codex

`skills/job-change-*` の 9 ディレクトリを、Codex のスキル探索先へ置きます。手順書は [docs/install-codex.md](docs/install-codex.md) で、AI エージェントに読ませてそのまま実行させる想定で書いてあります。Codex 版は、知人に Codex ユーザーがいたので作ったものの、まだテストしていません。

## 使い方

Claude Code では `/job-change-support` を実行します。Codex では「転職の準備をしたい」と伝えると hub が起動します。

初回の起動時に、hub が利用者データの置き場所を尋ねます。置き場所には既定値が無く、設定ファイルだけが決めるためです。ここには現年収・居住地・在籍企業名が記録されるので、クラウド同期フォルダや git の管理下は避けてください。設定ファイルの仕様は [docs/configuration.md](docs/configuration.md) にあります。

工程は次の順に進みます。飛ばしたい工程があれば、該当するスキルを直接呼び出してください。

1. プロファイル作成。`profile.json` が無ければまずここからです
2. 自己分析。省略できますが、志望動機と面接の一貫性はここが土台になります
3. 求人検索。応募先が決まっていれば飛ばせます
4. 企業研究。求人票の取り込みから始まります
5. 適合性評価。応募するかどうかをここで決めます
6. 応募書類の作成
7. 試験対策
8. 面接対策

求人 URL を渡すと、求人票の取り込みから適合性評価までが順に進みます。「この会社を調べて」「SPI 対策」のような個別の依頼は、hub がそのまま該当するスキルへ渡します。

## 注意

### 求人サイトの利用規約

求人検索と求人票の取り込みでは、AI エージェントが求人サイトの公開ページを取得します。対象はログインなしで閲覧できるページに限っていますが、自動的な取得を制限しているサイトもあります。対象サイトの利用規約と `robots.txt` は利用者自身で確認し、取得の頻度もサイトへ過度な負荷をかけない範囲に保ってください。

### サポート外

求人への応募や転職エージェントサービスへの登録といった外部への送信をともなう操作、年収交渉、法律に関する相談、新卒の就職活動は範囲外です。

新卒の就職活動への対応はそのうちやろうと思っています。

### 免責

このスキル群が作る書類・評価・想定質問は、いずれも下書きです。応募に使う前に、本人が中身を確認してください。企業情報は収集した時点の公開情報であり、正確さと最新性を保証しません。待遇・選考プロセス・労働条件は、応募先が公式に示す情報で確かめてください。LLM の仕様を理解したうえで、自己責任で使ってください。

## ライセンス

MIT License です。
