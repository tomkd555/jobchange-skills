# job-change skills

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB.svg)](#必要なもの)
[![Harness](https://img.shields.io/badge/Harness-Claude%20Code%20%7C%20Codex-6b46c1.svg)](#導入)

日本の中途採用に応募する人を AI エージェントが支援するためのスキル群である。プロファイルの作成から、自己分析・求人検索・企業研究・適合性評価・応募書類の作成・適性検査対策・面接対策までを、9つのスキルと13体のエージェントで担う。

設計の要は、出した答えを利用者があとから検証できるようにする点にある。企業について書いた内容には、必ず出典 URL と証拠グレードを添える。成果物の形式は、Python の検証スクリプトで機械的に検査する。書類を起草するエージェントと、それを監査するエージェントは、判断が混ざらないように別々に動かす。

Claude Code と Codex のどちらでも動く。スキルの書き方は [Agent Skills](https://agentskills.io) の形式（`SKILL.md`・`references/`・`scripts/`）に従っている。

## 収録スキル

| スキル | 役割 | 主な成果物 |
|---|---|---|
| `job-change-support` | 入口となる hub。依頼の内容を判別し、設定とプロファイルを確認したうえで各スキルへ渡す | `config.json`・`company_index.json` |
| `job-change-profile` | 職務経歴・スキル・転職の軸を聞き取る | `profile.json` |
| `job-change-self-analysis` | 行動の記録と他者からの評価をもとに、強みとキャリアの軸を裏付ける | `self_analysis.json` |
| `job-change-job-search` | 無償で使える公開 Web 検索だけで求人を集め、掲載ページの引用と出典 URL を添える | `job_search_results.json` |
| `job-change-company-research` | 求人票を取り込み、企業を調べる。書いた主張には出典 URL と証拠グレードを添える | `job_posting.json`・`company_research.json` |
| `job-change-fit-assessment` | 求人と本人を7つの観点で照らし合わせ、年間の拘束時間と実質時給を算定する | `fit_assessment.json`・`time_analysis.json` |
| `job-change-documents` | 職務経歴書・履歴書・英文レジュメ・志望動機書を書く | `documents/` 配下の各書類 |
| `job-change-exam-prep` | 応募先で使われる筆記試験と適性検査の種別を調べ、対策を立てる | `exam_assessment.json`・`exam-prep-plan.md` |
| `job-change-interview-prep` | 企業ごとの想定質問を作り、利用者の回答を評価する | 想定質問集・`interview_answers.json` |

利用者が覚えるのは、入口の `job-change-support` だけでよい。「転職の準備をしたい」と伝えれば、hub が依頼の内容を判別し、該当するスキルへ渡す。目的がはっきりしているときは、スキルを名前で直接呼び出してもよい。

## 必要なもの

- Python 3.9 以上。検証スクリプトの実行に使う。標準ライブラリ以外の依存はない。
- Web 検索と Web 取得ができる AI エージェント。求人検索と企業研究で使う。

## 導入

### Claude Code

このリポジトリは、ルートがそのままプラグインであり、マーケットプレイスでもある。次の2行で導入できる。

```
/plugin marketplace add https://github.com/tomkd555/jobchange-skills.git
/plugin install job-change@job-change-skills
```

すでにローカルへ clone してあるなら、URL の代わりにそのパスを渡す。プラグインを使わずに手作業で配置する方法は、[docs/install-claude-code.md](docs/install-claude-code.md) に書いてある。

### Codex

`skills/job-change-*` の9ディレクトリを、Codex のスキル探索先へ置く。手順は [docs/install-codex.md](docs/install-codex.md) にある。この文書は、AI エージェントに読ませてそのまま実行させることを想定して書いてある。

### ハーネスによる違い

| 項目 | Claude Code | Codex |
|---|---|---|
| 役割の実行 | 13体のサブエージェントへ委譲する | 本体が `references/roles/*.md` を読み、その役割として実行する |
| 起草と監査の独立性 | 別々の文脈で動くため保たれる | 同じ文脈になるため弱まる。監査の段では起草時の判断理由を参照しない規則で補う |
| ツールの制限 | `tools` frontmatter が機械的に効く | 効かない。役割プロンプトに書いた「扱ってよい入力」を自分で守る |
| スキルの起動 | 名前で自動判別、または `/skill-name` | 説明文からの自動判別 |

## 使い方

### 最初の1回

`/job-change-support` を実行するか、「転職の準備をしたい」と伝えると hub が起動する。

hub は、まず利用者データの置き場所を尋ねる。置き場所は設定ファイルだけで決まり、既定値が無いためである。現年収や居住地を含むデータをどこへ置くかは、利用者が決めるべきものである。設定ファイルの仕様と探索の順序は、[docs/configuration.md](docs/configuration.md) にある。

置き場所が決まると、続けてプロファイルの作成へ入る。職務経歴・スキル・転職の軸を聞き取り、`profile.json` を作る。このファイルは、以降のすべてのスキルが入力として読む。

### 応募先が決まっているとき

hub は、次の順序を示したうえで各スキルへ渡す。

1. **プロファイル作成**（`job-change-profile`）: `profile.json` が無ければ、まずこれを作る。
2. **自己分析**（`job-change-self-analysis`）: 強みと転職の軸を行動の記録で裏付ける。志望動機と面接の一貫性は、ここが土台になる。
3. **求人検索**（`job-change-job-search`）: 応募先がまだ決まっていないときの入口である。決まっているなら飛ばしてよい。
4. **企業研究**（`job-change-company-research`）: 求人票を取り込み、企業を調べる。
5. **適合性評価**（`job-change-fit-assessment`）: 7つの観点で評価し、年間の拘束時間と実質時給を算定する。
6. **応募書類作成**（`job-change-documents`）: 企業研究の結果を反映して書類を書く。
7. **試験対策**（`job-change-exam-prep`）: 応募先で使われる検査の種別を調べ、対策を立てる。
8. **面接対策**（`job-change-interview-prep`）: 想定質問を作り、回答を評価する。

自己分析と求人検索は任意であり、飛ばしても先へ進める。順序は選考の段階や締め切りに合わせて入れ替えてよいが、次の2点だけは動かさない。企業研究は、応募書類の作成と面接対策より先に行う。適合性評価は、企業研究の後に行う。

### 求人 URL から始めるとき

求人 URL を渡すと、求人票の取り込み・企業研究・適合性評価が順に進む。各段は、前の段の検証が PASS してから始まる。

適合性評価まで終わると、結果（推奨・条件付き推奨・非推奨・判断保留）が示される。応募を進めるかどうかを利用者が答えてから、書類作成より後の段へ移る。

途中で中断しても構わない。再開する位置は、成果物のファイルの有無と、その鮮度だけで決まる。会話の記憶には頼らない。

### 個別の作業だけを頼むとき

「この会社を調べて」「SPI 対策」のように頼めば、hub はそのまま該当するスキルへ渡す。ただし、設定とプロファイルの確認だけは、どの依頼でも先に行う。

## データの取り扱い

利用者データは、個人情報を置く `career-private/` と、企業ごとの成果物を置く `companies/` に分けて保存する。

```
{data_root}/
├─ career-private/            個人情報。Web を使うエージェントへは渡さない
│   ├─ profile.json
│   ├─ self_analysis.json
│   ├─ company_index.json
│   ├─ commute.json
│   └─ fit/{企業スラッグ}/
├─ companies/{企業スラッグ}/    企業ごとの成果物（個人情報ではない）
└─ job-search/{検索ID}/        求人検索の結果
```

`career-private/` を `companies/` の外側へ置くのは、Web 検索や Web 取得を使うエージェントが読み書きする範囲から、個人情報を切り離すためである。現年収・希望年収・居住地・学歴・在籍企業名・実績は、検索クエリにも fetch にも外部 API にも渡さない。求人検索へ渡す条件は、個人が特定できない形にしてから渡す。

保存先はすべて利用者のローカルディスクである。このスキル群が成果物を外部へ送ることはない。

## 設計のルール

- **出典と証拠グレードを必ず添える。** 企業情報には、出典 URL と証拠グレード（A=一次公式／B=信頼できる二次／C=口コミ集約／D=個人ブログ・伝聞）を添える。C と D だけを根拠に断定することは禁じる。
- **経歴の置き場所は1か所に限る。** 利用者の経歴・スキル・転職の軸は `profile.json` に集約する。同じ情報を複数の場所へ持たせない。
- **個人情報を外部へ出さない。** Web を使うエージェントには、`profile.json` と `career-private/` の中身を渡さない。
- **形式は機械で検査する。** 成果物の形式と規則は、Python の検証スクリプト（標準ライブラリのみ）で検査する。PASS を確認してから次の工程へ進む。
- **起草と監査を分ける。** 起草するエージェントと監査するエージェントを別々の文脈に置き、監査側へ起草側の判断理由を渡さない。
- **材料が無い項目は埋めない。** 判断材料が足りない評価は `unknown` または保留とし、推測で補わない。

## リポジトリの構成

```
skills/job-change-*/          9スキル本体
  SKILL.md                    手順の定義
  references/                 判断基準とデータ形式の定義
  references/roles/           役割プロンプトの定義
  scripts/                    検証スクリプトとその単体テスト
  assets/                     架空の記入例
agents/                       Claude Code 用のエージェント定義13体
tools/sync_roles.py           役割プロンプトから agents/ を生成し、差分を検査する
tools/check_portability.py    環境依存パスの混入を検査する
docs/                         設定と導入の手順
```

`agents/` の13ファイルは、`skills/*/references/roles/*.md` から `tools/sync_roles.py` が生成する。役割の内容を変えるときは生成元を直し、`python tools/sync_roles.py` を実行する。`agents/` を直接編集してはならない。

## 開発

```bash
# 全スキルの単体テスト
for d in skills/*/; do [ -d "$d/scripts/tests" ] && (cd "$d" && python -m unittest discover -s scripts/tests); done

# 役割プロンプトと agents/ の同期を検査
python tools/sync_roles.py --check

# 環境依存パス・個人情報の混入を検査
python tools/check_portability.py
```

## 範囲外

次の作業は扱わない。

- 求人への応募、転職エージェントサービスへの登録など、外部への送信を伴う操作
- 年収交渉の代行
- 法律とビザに関する相談
- 新卒の就職活動

書類や返信文を作るところまでを支援する。送信は利用者本人が行う。

## 免責

このスキル群が作る書類・評価・想定質問は、いずれも下書きである。応募に使う前に、利用者本人が中身を確かめる必要がある。

企業情報には出典と証拠グレードを添えるが、これは収集した時点の公開情報にすぎず、正確さと新しさを保証するものではない。待遇・選考プロセス・労働条件は、応募先が公式に示す情報で確かめる必要がある。

## ライセンス

MIT License である。全文は [LICENSE](LICENSE) にある。
