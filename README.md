# job-change skills

日本の中途採用での転職を支援する AI エージェント用スキル群である。プロファイルの管理から、自己分析・求人検索・企業研究・適合性評価・応募書類の作成・適性検査対策・面接対策までを、9つのスキルで扱う。

Claude Code と Codex の双方で動く。スキルの記述は [Agent Skills](https://agentskills.io) の形式（`SKILL.md` ＋ `references/` ＋ `scripts/`）に従う。

## 何をするか

| スキル | 役割 |
|---|---|
| `job-change-support` | 入口となる hub。依頼の内容を判別してサブスキルへ振り分け、設定とプロファイルのゲートを担う |
| `job-change-profile` | 職務経歴・スキル・転職の軸を聞き取り、`profile.json` を作る |
| `job-change-self-analysis` | 行動証拠と他者フィードバックから、キャリアの軸と強みを裏付ける |
| `job-change-job-search` | 無償の公開 Web 検索だけで求人を集め、引用と出典 URL を付す |
| `job-change-company-research` | 求人票の取り込みと企業研究。全主張に出典 URL と証拠グレードを付す |
| `job-change-fit-assessment` | 求人と本人を7次元で突き合わせ、年間拘束時間と実質時給を算定する |
| `job-change-documents` | 職務経歴書・履歴書・英文レジュメ・志望動機書を作る |
| `job-change-exam-prep` | 応募先で使われる筆記試験・適性検査の種別を調べ、対策を立てる |
| `job-change-interview-prep` | 企業固有の想定質問を作り、回答を評価する |

### 設計のルール

- **出典と証拠グレード。** 企業情報にはすべて出典 URL と証拠グレード（A=一次公式／B=信頼できる二次／C=口コミ集約／D=個人ブログ・伝聞）を付す。C・D 単独での断定を禁じる。
- **置き場所は1か所。** 利用者の経歴・スキル・転職の軸は `profile.json` の1か所に集約する。同じ情報を複数の場所に持たない。
- **個人情報を外部へ出さない。** Web 送信手段を持つ役割へ `profile.json` と非公開ディレクトリ（`career-private/`）の内容を渡さない。求人検索の条件は匿名化してから渡す。
- **機械検証。** 成果物の形式とルールは、Python の検証スクリプト（標準ライブラリのみ）で検査する。PASS を確認してから次の工程へ進む。
- **起草と監査の分離。** 起草者と監査者を別の文脈に置き、監査者へ起草者の判断理由を渡さない。

## 導入

利用者データの置き場所は設定ファイルだけが決める。既定の置き場所を持たないため、hub が初回の起動時に置き場所を尋ねる。詳細は [docs/configuration.md](docs/configuration.md) にある。

### Claude Code

```
/plugin marketplace add <このリポジトリの URL またはローカルパス>
/plugin install job-change@job-change-skills
```

導入後、`/job-change-support` を実行するか「転職の準備をしたい」と伝えると、hub が起動して設定の作成から案内する。手順の詳細は [docs/install-claude-code.md](docs/install-claude-code.md) にある。

### Codex

`skills/job-change-*` の9ディレクトリを Codex のスキル探索先へ置く。手順は [docs/install-codex.md](docs/install-codex.md) にある。install-codex.md は、AI エージェントに読ませて実行させることを想定して書いてある。

### Claude Code と Codex の差

| 項目 | Claude Code | Codex |
|---|---|---|
| 役割の実行 | 13体のサブエージェントへ委譲する | 本体が `references/roles/*.md` を読み、その役割として実行する |
| 起草と監査の独立性 | 別の文脈で実行するため保たれる | 同一の文脈になるため下がる。監査の段で起草時の判断理由を参照しないルールで補う |
| ツールの制限 | `tools` frontmatter で機械的に効く | 効かない。役割プロンプトの「扱ってよい入力」を自己ルールとして守る |
| スキルの起動 | 名前で自動判別、または `/skill-name` | 説明文からの自動判別 |

## 必要なもの

- Python 3.9 以上（検証スクリプトの実行に使う。標準ライブラリ以外の依存はない）
- Web 検索・取得ができる AI エージェント（求人検索と企業研究で使う）

## リポジトリの構成

```
skills/job-change-*/          9スキル本体
  SKILL.md                    手順の原本
  references/                 判断基準・データ形式の原本
  references/roles/           役割プロンプトの原本
  scripts/                    検証スクリプトとその単体テスト
  assets/                     架空の記入例
agents/                       Claude Code 用のエージェント定義（references/roles/ から同期生成）
tools/sync_roles.py           役割プロンプト → agents/ の生成と差分検査
tools/check_portability.py    環境依存パスの混入検査
docs/                         設定と導入の手順
```

`agents/` は写しである。役割の内容を変えるときは `skills/*/references/roles/*.md` を修正し、`python tools/sync_roles.py` を実行する。

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

## ライセンス

MIT License。[LICENSE](LICENSE) を参照する。
