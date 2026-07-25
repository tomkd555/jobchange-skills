# job-change skills

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB.svg)](#必要なもの)
[![Harness](https://img.shields.io/badge/Harness-Claude%20Code%20%7C%20Codex-6b46c1.svg)](#導入)

日本の中途採用での転職活動を支援する、AI エージェント用のスキル群である。プロファイルの管理・自己分析・求人検索・企業研究・適合性評価・応募書類の作成・適性検査対策・面接対策を、9つのスキルと13体のエージェントで扱う。

生成した内容を利用者があとから検証できる状態で渡すことを目的とする。企業情報には出典 URL と証拠グレードを必ず付け、成果物の形式は Python の検証スクリプトで機械的に検査し、起草する役割と監査する役割を別の文脈に分ける。

Claude Code と Codex の双方で動く。スキルの記述は [Agent Skills](https://agentskills.io) の形式（`SKILL.md` ＋ `references/` ＋ `scripts/`）に従う。

## 収録スキル

| スキル | 役割 | 主な成果物 |
|---|---|---|
| `job-change-support` | 入口となる hub。依頼の内容を判別してサブスキルへ振り分け、設定とプロファイルのゲートを担う | `config.json`・`company_index.json` |
| `job-change-profile` | 職務経歴・スキル・転職の軸を聞き取る | `profile.json` |
| `job-change-self-analysis` | 行動証拠と他者フィードバックから、キャリアの軸と強みを裏付ける | `self_analysis.json` |
| `job-change-job-search` | 無償の公開 Web 検索だけで求人を集め、引用と出典 URL を付す | `job_search_results.json` |
| `job-change-company-research` | 求人票の取り込みと企業研究。全主張に出典 URL と証拠グレードを付す | `job_posting.json`・`company_research.json` |
| `job-change-fit-assessment` | 求人と本人を7次元で突き合わせ、年間拘束時間と実質時給を算定する | `fit_assessment.json`・`time_analysis.json` |
| `job-change-documents` | 職務経歴書・履歴書・英文レジュメ・志望動機書を作る | `documents/` 配下の各書類 |
| `job-change-exam-prep` | 応募先で使われる筆記試験・適性検査の種別を調べ、対策を立てる | `exam_assessment.json`・`exam-prep-plan.md` |
| `job-change-interview-prep` | 企業固有の想定質問を作り、回答を評価する | 想定質問集・`interview_answers.json` |

利用者は hub だけを覚えればよい。「転職の準備をしたい」のように伝えれば、hub が依頼を判別して該当スキルへ振り分ける。個別のスキルを名前で直接呼び出してもよい。

## 必要なもの

- Python 3.9 以上。検証スクリプトの実行に使う。標準ライブラリ以外の依存はない
- Web 検索・取得ができる AI エージェント。求人検索と企業研究で使う

## 導入

### Claude Code

リポジトリのルートがそのままプラグインであり、マーケットプレイスでもある。

```
/plugin marketplace add https://github.com/tomkd555/jobchange-skills.git
/plugin install job-change@job-change-skills
```

ローカルに clone してある場合は、URL の代わりにそのパスを渡す。プラグインを使わずに手作業で配置する手順は [docs/install-claude-code.md](docs/install-claude-code.md) にある。

### Codex

`skills/job-change-*` の9ディレクトリを Codex のスキル探索先へ置く。手順は [docs/install-codex.md](docs/install-codex.md) にあり、AI エージェントに読ませて実行させることを想定して書いてある。

### ハーネスによる差

| 項目 | Claude Code | Codex |
|---|---|---|
| 役割の実行 | 13体のサブエージェントへ委譲する | 本体が `references/roles/*.md` を読み、その役割として実行する |
| 起草と監査の独立性 | 別の文脈で実行するため保たれる | 同一の文脈になるため下がる。監査の段で起草時の判断理由を参照しないルールで補う |
| ツールの制限 | `tools` frontmatter で機械的に効く | 効かない。役割プロンプトの「扱ってよい入力」を自己ルールとして守る |
| スキルの起動 | 名前で自動判別、または `/skill-name` | 説明文からの自動判別 |

## 使い方

### 最初の1回

`/job-change-support` を実行するか「転職の準備をしたい」と伝えると hub が起動する。利用者データの置き場所は設定ファイルだけが決めるため、既定の置き場所を持たない。hub は初回に置き場所を尋ね、設定ファイルを作ってから作業へ入る。設定ファイルの仕様と探索順序は [docs/configuration.md](docs/configuration.md) にある。

続けてプロファイルの作成へ入る。職務経歴・スキル・転職の軸を聞き取り、`profile.json` を作る。以降のすべてのスキルがこれを入力として読む。

### 応募先が決まっているとき

hub は次の順序を提示して振り分ける。自己分析と求人検索は任意であり、省略して次へ進んでよい。

1. **プロファイル作成**（`job-change-profile`）— `profile.json` が未作成なら先に作る
2. **自己分析**（`job-change-self-analysis`）— 強みと転職の軸を行動証拠で裏付ける。志望動機と面接の一貫性の土台になる
3. **求人検索**（`job-change-job-search`）— 応募先が未確定のときの入口。決まっていれば省略する
4. **企業研究**（`job-change-company-research`）— 求人票を取り込み、企業を調べる
5. **適合性評価**（`job-change-fit-assessment`）— 7次元の評価と、年間拘束時間・実質時給を算定する
6. **応募書類作成**（`job-change-documents`）— 企業研究の結果を反映して書類を作る
7. **試験対策**（`job-change-exam-prep`）— 応募先で使われる検査の種別を調べ、対策を立てる
8. **面接対策**（`job-change-interview-prep`）— 想定質問を作り、回答を評価する

企業研究を応募書類・面接対策より先に置く原則と、適合性評価を企業研究の後に置く原則は保つ。それ以外の順序は、選考の段階と締め切りに応じて調整してよい。

### 求人 URL から始めるとき

求人 URL を渡すと、求人票の取り込み・企業研究・適合性評価を段階ゲート付きで進める。各段は前段の検証が PASS してから起動する。評価結果（推奨・条件付き推奨・非推奨・判断保留）を示したうえで、応募を進めるかどうかを利用者に確認し、その判断を受けてから書類作成以降へ進む。

中断した場合は、成果物のファイルの有無と鮮度だけで再開位置を決める。会話の記憶には依存しない。

### 単一の作業だけを頼むとき

「この会社を調べて」「SPI 対策」のように個別に頼めば、該当スキルへ直接振り分ける。ただし設定とプロファイルのゲートは常に先行する。

## データの取り扱い

利用者データは、個人情報を置く非公開ディレクトリ `career-private/` と、その外側の企業別成果物とに分けて保存する。

```
{data_root}/
├─ career-private/            個人情報。Web ツールを持つ役割へ渡さない
│   ├─ profile.json
│   ├─ self_analysis.json
│   ├─ company_index.json
│   ├─ commute.json
│   └─ fit/{企業スラッグ}/
├─ companies/{企業スラッグ}/    企業別成果物（非個人情報）
└─ job-search/{検索ID}/        求人検索の結果
```

`career-private/` を `companies/` の外側へ置くのは、Web 送信手段を持つ役割が作業するツリーから個人情報を隔離するためである。現年収・希望年収・居住地・学歴・在籍企業名・実績は、検索クエリ・fetch・外部 API のいずれにも渡さない。求人検索の条件は匿名化してから検索担当へ渡す。

保存先はすべて利用者のローカルディスクである。このスキル群は成果物を外部へ送信しない。

## 設計のルール

- **出典と証拠グレード。** 企業情報にはすべて出典 URL と証拠グレード（A=一次公式／B=信頼できる二次／C=口コミ集約／D=個人ブログ・伝聞）を付す。C・D 単独での断定を禁じる。
- **置き場所は1か所。** 利用者の経歴・スキル・転職の軸は `profile.json` の1か所に集約する。同じ情報を複数の場所に持たない。
- **個人情報を外部へ出さない。** Web 送信手段を持つ役割へ `profile.json` と `career-private/` の内容を渡さない。
- **機械検証。** 成果物の形式とルールは、Python の検証スクリプト（標準ライブラリのみ）で検査する。PASS を確認してから次の工程へ進む。
- **起草と監査の分離。** 起草者と監査者を別の文脈に置き、監査者へ起草者の判断理由を渡さない。
- **材料が無い項目は埋めない。** 判断材料が不足する評価は `unknown` または保留とし、推測で補完しない。

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

`agents/` は `skills/*/references/roles/*.md` から生成する。役割の内容を変えるときは生成元を修正し、`python tools/sync_roles.py` を実行する。`agents/` を直接編集しない。

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

求人への応募・転職エージェントサービスへの登録などの外部送信、年収交渉の代行、法律・ビザ相談、新卒就活は扱わない。書類や返信文の作成までを支援し、送信は利用者本人が行う。

## 免責

このスキル群が作る書類・評価・想定質問は下書きである。応募に使う前に、利用者本人が内容を確認する。企業情報は出典と証拠グレードを付けて示すが、収集時点の公開情報に基づくものであり、正確性と最新性は保証しない。待遇・選考プロセス・労働条件は、必ず応募先の公式な情報で確認する。

## ライセンス

MIT License。[LICENSE](LICENSE) を参照。
