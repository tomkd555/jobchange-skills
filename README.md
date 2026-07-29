# job-change skills

[![CI](https://github.com/tomkd555/jobchange-skills/actions/workflows/ci.yml/badge.svg)](https://github.com/tomkd555/jobchange-skills/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB.svg)](#必要なもの)
[![Harness](https://img.shields.io/badge/Harness-Claude%20Code%20%7C%20Codex-6b46c1.svg)](#導入)

日本の中途採用での転職を支援する AI エージェント用のスキル群です。

プロファイルの作成から面接対策までを、9つのスキルと13体のエージェントが担います。

設計の要は、出した答えを後から検証できる点にあります。企業について書いた内容には、出典 URL と証拠グレードを付けます。成果物の形式は、Python の検証スクリプトが機械的に検査します。書類を作成するエージェントと監査するエージェントは、判断が混ざらないよう別々に動きます。

Claude Code と Codex の両方で動きます。スキルの書き方は [Agent Skills](https://agentskills.io) の形式（`SKILL.md`・`references/`・`scripts/`）に従っています。

## 収録スキル

| スキル | 役割 | 主な成果物 |
|---|---|---|
| `job-change-support` | 入口となる hub。依頼内容を判別し、設定とプロファイルを確認したうえで各スキルへ渡します | `config.json`・`company_index.json` |
| `job-change-profile` | 職務経歴・スキル・転職の軸をヒアリングします | `profile.json` |
| `job-change-self-analysis` | 行動の記録と他者からの評価をもとに、自己分析を支援します | `self_analysis.json` |
| `job-change-job-search` | Web 検索により求人を集め、掲載ページの引用と出典 URL を付けます | `job_search_results.json` |
| `job-change-company-research` | 求人票を基に企業を調査します。出典 URL と証拠グレードを付与します | `job_posting.json`・`company_research.json` |
| `job-change-fit-assessment` | 求人と本人を7つの観点で照合します | `fit_assessment.json`・`time_analysis.json` |
| `job-change-documents` | 職務経歴書・履歴書・志望動機などを作成します | `documents/` 配下の各書類 |
| `job-change-exam-prep` | 応募先で使われる筆記試験と適性検査の種別を調べ、対策を立てます | `exam_assessment.json`・`exam-prep-plan.md` |
| `job-change-interview-prep` | 企業ごとの想定質問を作り、回答を評価します | 想定質問集・`interview_answers.json` |

## 証拠グレード

企業についての主張には、出典 URL とあわせて証拠グレードを付けます。以下のように証拠グレードを分類しています。

| グレード | 区分 | 具体例 |
|---|---|---|
| **A** | 一次・公式 | EDINET 有価証券報告書、決算説明資料、企業公式サイト、統合報告書、公的統計・政府の認定制度データベース、査読済みの学術研究 |
| **B** | 信頼できる二次 | 大手報道機関、就職四季報、業界レポート、公的機関の解説ページ |
| **C** | 口コミ・集計サイト | OpenWork・Glassdoor 等の口コミ集計、選考体験記の集計サイト |
| **D** | 個人ブログ・伝聞・未確認 | 個人ブログ、SNS の伝聞、出所不明の転載、単発の匿名投稿 |

グレードは、内容の正しさではなく誰が発信したかで決まります。企業自身が発信する評価的な主張（「風通しが良い」など）は、出所がグレードAでも内容の真偽は担保されないため、確信度を high にしません。C と D だけを根拠に事実を断定することも禁じています。

判定基準・C と D を根拠とする記述の書き方・複数の出所を突き合わせる手順は、[skills/job-change-company-research/references/evidence-grading.md](skills/job-change-company-research/references/evidence-grading.md) に定めています。

## 必要なもの

- Python 3.9 以上。検証スクリプトの実行に使います。標準ライブラリ以外の依存はありません。
- Web 検索と Web 取得ができる AI エージェント。求人検索と企業研究で使います。

## 導入

### Claude Code

次の2行で導入できます。

```
/plugin marketplace add https://github.com/tomkd555/jobchange-skills.git
/plugin install job-change@job-change-skills
```

すでにローカルへ clone 済みなら、URL の代わりにそのパスを指定します。プラグインを使わずに手作業で配置する方法は、[docs/install-claude-code.md](docs/install-claude-code.md) にあります。

### Codex

`skills/job-change-*` の9ディレクトリを、Codex のスキル探索先へ置きます。手順は [docs/install-codex.md](docs/install-codex.md) にあります。この文書は、AI エージェントに読ませてそのまま実行させることを想定して書いてあります。

なお知人がCodexユーザーであったため、codex版も作成していますが、自分自身でテストは行っていません。

## 使い方

`/job-change-support` を実行するか、「転職の準備をしたい」と伝えると hub が起動します。

hub は、まず利用者データの置き場所を尋ねます。置き場所は設定ファイルだけで決まり、既定値を持たないためです。現年収や居住地を含むデータをどこへ置くかは、自分自身で決定してください。設定ファイルの仕様と探索の順序は、[docs/configuration.md](docs/configuration.md) にあります。

その後、以下の順番で動作します。スキップする場合は直接スキルをコールしてください。

1. **プロファイル作成**（`job-change-profile`）: `profile.json` が無ければ、まずこれを作ります。
2. **自己分析**（`job-change-self-analysis`）: 強みと転職の軸を行動の記録で裏付けます。志望動機と面接の一貫性は、ここが土台になります。
3. **求人検索**（`job-change-job-search`）: 応募先がまだ決まっていないときの入口です。決まっているなら飛ばせます。
4. **企業研究**（`job-change-company-research`）: 求人票を取り込み、企業を調べます。
5. **適合性評価**（`job-change-fit-assessment`）: 7つの観点で評価します。
6. **応募書類作成**（`job-change-documents`）: 企業研究の結果を反映して書類を書きます。
7. **試験対策**（`job-change-exam-prep`）: 応募先で使われる検査の種別を調べ、対策を立てます。
8. **面接対策**（`job-change-interview-prep`）: 想定質問を作り、回答を評価します。

### 求人 URL から始める

求人 URL を渡すと、求人票の取り込み・企業研究・適合性評価が順に進みます。

### 個別の作業だけを頼むとき

「この会社を調べて」「SPI 対策」のように伝えると、hub はそのまま該当するスキルへ渡します。

## 成果物の例

企業研究が出す `company_research.json` は、主張1件ごとに出典 URL・証拠グレード・逐語引用・取得日を持ちます。企業名はreadme記載時点で架空です。

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

この例の `confidence` が `medium` にとどまるのは、出典がグレードAでも、内容が企業の自己申告にあたるためです。グレードC・Dだけを根拠に `high` を付けると、`validate_company_research.py` が ERROR を返します。

## データの取り扱い

利用者データは、個人情報を置く `career-private/` と、企業ごとの成果物を置く `companies/` に分けて保存します。

```
{data_root}/
├─ career-private/            個人情報。Web を使うエージェントへは渡しません
│   ├─ profile.json
│   ├─ self_analysis.json
│   ├─ company_index.json
│   ├─ commute.json
│   └─ fit/{企業スラッグ}/
├─ companies/{企業スラッグ}/    企業ごとの成果物
└─ job-search/{検索ID}/        求人検索の結果
```

`career-private/` を `companies/` の外側へ置いています。個人情報を切り離すためです。個人情報は、検索クエリにも fetch にも外部 API にも渡さないように指示をしていますが、LLMの仕様上、保証はできません。必ず自己責任で実行してください。

## 設計のルール

- 企業情報には、出典 URL と[証拠グレード](#証拠グレード)を必ず付けます。
- 経歴・スキル・転職の軸は、`profile.json` の1か所に集約します。
- 判断材料が足りない項目は `unknown` または保留とし、推測で補いません。

## 求人サイトの利用規約について

求人検索と求人票の取り込みでは、AI エージェントが求人サイトの公開ページを取得します。対象は、ログインなしで閲覧できるページに限っています。

ただし、自動的な取得を制限している求人サイトもあります。対象サイトの利用規約と `robots.txt` は、利用者自身で確認してください。取得の頻度も、サイトへ過度な負荷をかけない範囲に保ってください。

## リポジトリの構成

```
skills/job-change-*/          9スキル本体
  SKILL.md                    手順の定義
  references/                 判断基準とデータ形式の定義
  references/roles/           役割プロンプトの定義
  scripts/                    検証スクリプトとその単体テスト
  assets/                     架空の記入例
agents/                       Claude Code 用のエージェント定義13体
docs/                         設定と導入の手順
```

## 開発

```bash
# 全スキルの単体テスト
for d in skills/*/; do [ -d "$d/scripts/tests" ] && (cd "$d" && python -m unittest discover -s scripts/tests); done
```

## 範囲外

次の作業は扱いません。

- 求人への応募、転職エージェントサービスへの登録など、外部への送信をともなう操作
- 年収交渉
- 法律等に関する相談
- 新卒の就職活動（対応はそのうち）

## 免責

このスキル群が作る書類・評価・想定質問は、いずれも下書きです。応募に使う前に、本人が中身を確認してください。

企業情報には出典と証拠グレードを付けますが、これは収集した時点の公開情報であり、正確さと新しさを保証するものではありません。待遇・選考プロセス・労働条件は、応募先が公式に示す情報で確認してください。

LLMの仕様を理解したうえで、全て自己責任でお願いします。

## ライセンス

MIT License です。
