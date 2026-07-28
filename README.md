# job-change skills

[![CI](https://github.com/tomkd555/jobchange-skills/actions/workflows/ci.yml/badge.svg)](https://github.com/tomkd555/jobchange-skills/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB.svg)](#必要なもの)
[![Harness](https://img.shields.io/badge/Harness-Claude%20Code%20%7C%20Codex-6b46c1.svg)](#導入)

日本の中途採用に応募されるみなさまを、AI エージェントがお手伝いするためのスキル群です。プロファイルの作成から、自己分析・求人検索・企業研究・適合性評価・応募書類の作成・適性検査対策・面接対策までを、9つのスキルと13体のエージェントで担います。

設計の要は、出した答えをご自身であとから確かめられるようにする点にあります。企業について書いた内容には、必ず出典 URL と証拠グレードを添えます。成果物の形式は、Python の検証スクリプトで機械的に検査します。書類を起草するエージェントと、それを監査するエージェントは、判断が混ざらないように別々に動かします。

Claude Code と Codex のどちらでもお使いいただけます。スキルの書き方は [Agent Skills](https://agentskills.io) の形式（`SKILL.md`・`references/`・`scripts/`）に従っています。

## 収録スキル

| スキル | 役割 | 主な成果物 |
|---|---|---|
| `job-change-support` | 入口となる hub。ご依頼の内容を判別し、設定とプロファイルを確認したうえで各スキルへ渡します | `config.json`・`company_index.json` |
| `job-change-profile` | 職務経歴・スキル・転職の軸をうかがいます | `profile.json` |
| `job-change-self-analysis` | 行動の記録と他者からの評価をもとに、強みとキャリアの軸を裏付けます | `self_analysis.json` |
| `job-change-job-search` | 無償で使える公開 Web 検索だけで求人を集め、掲載ページの引用と出典 URL を添えます | `job_search_results.json` |
| `job-change-company-research` | 求人票を取り込み、企業を調べます。書いた主張には出典 URL と証拠グレードを添えます | `job_posting.json`・`company_research.json` |
| `job-change-fit-assessment` | 求人とご本人を7つの観点で照らし合わせ、年間の拘束時間と実質時給を算定します | `fit_assessment.json`・`time_analysis.json` |
| `job-change-documents` | 職務経歴書・履歴書・英文レジュメ・志望動機書を書きます | `documents/` 配下の各書類 |
| `job-change-exam-prep` | 応募先で使われる筆記試験と適性検査の種別を調べ、対策を立てます | `exam_assessment.json`・`exam-prep-plan.md` |
| `job-change-interview-prep` | 企業ごとの想定質問を作り、回答を評価します | 想定質問集・`interview_answers.json` |

覚えていただくのは、入口の `job-change-support` だけで十分です。「転職の準備をしたい」とお伝えいただければ、hub がご依頼の内容を判別し、該当するスキルへ渡します。目的がはっきりしているときは、スキルを名前で直接呼び出していただいてもかまいません。

## 必要なもの

- Python 3.9 以上。検証スクリプトの実行に使います。標準ライブラリ以外の依存はありません。
- Web 検索と Web 取得ができる AI エージェント。求人検索と企業研究で使います。

## 導入

### Claude Code

このリポジトリは、ルートがそのままプラグインであり、マーケットプレイスでもあります。次の2行で導入できます。

```
/plugin marketplace add https://github.com/tomkd555/jobchange-skills.git
/plugin install job-change@job-change-skills
```

すでにローカルへ clone 済みであれば、URL の代わりにそのパスをお渡しください。プラグインを使わずに手作業で配置する方法は、[docs/install-claude-code.md](docs/install-claude-code.md) にあります。

### Codex

`skills/job-change-*` の9ディレクトリを、Codex のスキル探索先へ置きます。手順は [docs/install-codex.md](docs/install-codex.md) にあります。この文書は、AI エージェントに読ませてそのまま実行させることを想定して書いてあります。

### ハーネスによる違い

| 項目 | Claude Code | Codex |
|---|---|---|
| 役割の実行 | 13体のサブエージェントへ委譲します | 本体が `references/roles/*.md` を読み、その役割として実行します |
| 起草と監査の独立性 | 別々の文脈で動くため保たれます | 同じ文脈になるため弱まります。監査の段では起草時の判断理由を参照しない規則で補います |
| ツールの制限 | `tools` frontmatter が機械的に効きます | 効きません。役割プロンプトに書いた「扱ってよい入力」を自分で守ります |
| スキルの起動 | 名前で自動判別、または `/skill-name` | 説明文からの自動判別 |

## 使い方

### 最初の1回

`/job-change-support` を実行なさるか、「転職の準備をしたい」とお伝えいただくと hub が起動します。

hub は、まず利用者データの置き場所をおたずねします。置き場所は設定ファイルだけで決まり、既定値を持たないためです。現年収や居住地を含むデータをどこへ置くかは、ご自身でお決めいただくべきものと考えています。設定ファイルの仕様と探索の順序は、[docs/configuration.md](docs/configuration.md) にあります。

置き場所が決まりましたら、続けてプロファイルの作成へ入ります。職務経歴・スキル・転職の軸をうかがい、`profile.json` を作ります。このファイルは、以降のすべてのスキルが入力として読みます。

### 応募先が決まっているとき

hub は、次の順序をお示ししたうえで各スキルへ渡します。

1. **プロファイル作成**（`job-change-profile`）: `profile.json` が無ければ、まずこれを作ります。
2. **自己分析**（`job-change-self-analysis`）: 強みと転職の軸を行動の記録で裏付けます。志望動機と面接の一貫性は、ここが土台になります。
3. **求人検索**（`job-change-job-search`）: 応募先がまだ決まっていないときの入口です。決まっているなら飛ばしてかまいません。
4. **企業研究**（`job-change-company-research`）: 求人票を取り込み、企業を調べます。
5. **適合性評価**（`job-change-fit-assessment`）: 7つの観点で評価し、年間の拘束時間と実質時給を算定します。
6. **応募書類作成**（`job-change-documents`）: 企業研究の結果を反映して書類を書きます。
7. **試験対策**（`job-change-exam-prep`）: 応募先で使われる検査の種別を調べ、対策を立てます。
8. **面接対策**（`job-change-interview-prep`）: 想定質問を作り、回答を評価します。

自己分析と求人検索は任意ですので、飛ばしても先へ進めます。順序は選考の段階や締め切りに合わせて入れ替えていただけますが、次の2点だけは動かしません。企業研究は、応募書類の作成と面接対策より先に行います。適合性評価は、企業研究の後に行います。

### 求人 URL から始めるとき

求人 URL をお渡しいただくと、求人票の取り込み・企業研究・適合性評価が順に進みます。各段は、前の段の検証が PASS してから始まります。

適合性評価まで終わりましたら、結果（推奨・条件付き推奨・非推奨・判断保留）をお示しします。応募を進めるかどうかをお答えいただいてから、書類作成より後の段へ移ります。

途中で中断なさってもかまいません。再開する位置は、成果物のファイルの有無と、その鮮度だけで決まります。会話の記憶には頼りません。

### 個別の作業だけをご依頼のとき

「この会社を調べて」「SPI 対策」のようにお伝えいただければ、hub はそのまま該当するスキルへ渡します。ただし、設定とプロファイルの確認だけは、どのご依頼でも先に済ませます。

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
├─ companies/{企業スラッグ}/    企業ごとの成果物（個人情報ではありません）
└─ job-search/{検索ID}/        求人検索の結果
```

`career-private/` を `companies/` の外側へ置くのは、Web 検索や Web 取得を使うエージェントが読み書きする範囲から、個人情報を切り離すためです。現年収・希望年収・居住地・学歴・在籍企業名・実績は、検索クエリにも fetch にも外部 API にも渡しません。求人検索に用いる条件は、個人が特定できない形に整えてからお渡しします。

保存先はすべてご自身のローカルディスクです。このスキル群が成果物を外部へ送ることはありません。

## 設計のルール

- **出典と証拠グレードを必ず添えます。** 企業情報には、出典 URL と証拠グレード（A=一次公式／B=信頼できる二次／C=口コミ集約／D=個人ブログ・伝聞）を添えます。C と D だけを根拠に断定することは禁じています。
- **経歴の置き場所は1か所に限ります。** ご自身の経歴・スキル・転職の軸は `profile.json` に集約します。同じ情報を複数の場所へ持たせません。
- **個人情報を外部へ出しません。** Web を使うエージェントには、`profile.json` と `career-private/` の中身を渡しません。
- **形式は機械で検査します。** 成果物の形式と規則は、Python の検証スクリプト（標準ライブラリのみ）で検査します。PASS を確かめてから次の工程へ進みます。
- **起草と監査を分けます。** 起草するエージェントと監査するエージェントを別々の文脈に置き、監査側へ起草側の判断理由を渡しません。
- **材料が無い項目は埋めません。** 判断材料が足りない評価は `unknown` または保留とし、推測で補いません。

## 求人サイトの利用規約について

求人検索と求人票の取り込みでは、AI エージェントが求人サイトの公開ページを取得します。対象は、ログインなしで閲覧できるページに限っています。

ただし、自動的な取得を制限している求人サイトもあります。対象サイトの利用規約と `robots.txt` は、ご利用になるみなさまご自身でお確かめください。取得の頻度についても、サイトへ過度な負荷をかけない範囲でのご利用をお願いいたします。

## リポジトリの構成

```
skills/job-change-*/          9スキル本体
  SKILL.md                    手順の定義
  references/                 判断基準とデータ形式の定義
  references/roles/           役割プロンプトの定義
  scripts/                    検証スクリプトとその単体テスト
  assets/                     架空の記入例
agents/                       Claude Code 用のエージェント定義13体
tools/sync_roles.py           役割プロンプトから agents/ を生成し、差分を検査します
tools/check_portability.py    環境依存パスの混入を検査します
docs/                         設定と導入の手順
```

`agents/` の13ファイルは、`skills/*/references/roles/*.md` から `tools/sync_roles.py` が生成します。役割の内容を変えるときは生成元を直し、`python tools/sync_roles.py` を実行してください。`agents/` を直接編集なさらないようお願いいたします。

## 開発

```bash
# 全スキルの単体テスト
for d in skills/*/; do [ -d "$d/scripts/tests" ] && (cd "$d" && python -m unittest discover -s scripts/tests); done

# 役割プロンプトと agents/ の同期を検査
python tools/sync_roles.py --check

# 環境依存パス・個人情報の混入を検査（git が追跡しているファイルが対象）
python tools/check_portability.py
```

この3つは、GitHub Actions でも Python 3.9 と 3.13 の両方で実行しています。設定は [.github/workflows/ci.yml](.github/workflows/ci.yml) にあります。

## 範囲外

次の作業は扱いません。

- 求人への応募、転職エージェントサービスへの登録など、外部への送信をともなう操作
- 年収交渉の代行
- 法律とビザに関するご相談
- 新卒の就職活動

書類や返信文を作るところまでをお手伝いします。送信はご本人にお願いいたします。

## 免責

このスキル群が作る書類・評価・想定質問は、いずれも下書きです。応募にお使いになる前に、ご本人が中身をお確かめください。

企業情報には出典と証拠グレードを添えますが、これは収集した時点の公開情報にすぎず、正確さと新しさを保証するものではありません。待遇・選考プロセス・労働条件は、応募先が公式に示す情報でお確かめください。

## ライセンス

MIT License です。全文は [LICENSE](LICENSE) にあります。
