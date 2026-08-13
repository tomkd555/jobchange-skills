# Codex への導入

この文書は、AI エージェント（Codex）に読ませて実行させることを想定して書いてある。利用者は「`docs/install-codex.md` のとおりに導入して」と伝えるだけでよい。各手順には、成功したかどうかを機械的に判定できる完了条件を付けてある。

## 前提

- Codex CLI が使えること。
- Python 3.9 以上が使えること。検証スクリプトは標準ライブラリのみを使う。
- このリポジトリを clone 済みであること。以下ではその場所を `<REPO>` と書く。

## 手順1: スキルを配置する

Codex はスキルを次の場所から読む。用途に合うほうを選ぶ。

| 置き先 | 適用範囲 |
|---|---|
| `$HOME/.agents/skills/` | すべての作業ディレクトリ |
| `<作業ディレクトリ>/.agents/skills/` | そのリポジトリのみ（Codex は上位ディレクトリもたどる） |

`<REPO>/skills/` の下にある `job-change-*` の9ディレクトリを、選んだ置き先へそのままコピーする。9スキルは相互に参照するため、一括で置く。個別に選んで置かない。

```bash
mkdir -p "$HOME/.agents/skills"
cp -r <REPO>/skills/job-change-* "$HOME/.agents/skills/"
```

Windows の PowerShell では次のとおりである。

```powershell
New-Item -ItemType Directory -Force "$HOME\.agents\skills"
Copy-Item -Recurse "<REPO>\skills\job-change-*" "$HOME\.agents\skills\"
```

**完了条件。** 次のコマンドが `9` を出力する。

```bash
ls -d "$HOME"/.agents/skills/job-change-* | wc -l
```

## 手順2: agents/ は配置しない

`<REPO>/agents/` にある13ファイルは Claude Code 専用のエージェント定義であり、Codex では使わない。コピーしない。

Codex では、各スキルの本体が `references/roles/*.md` を読み、その役割として自分で実行する。読み替えの手順は各スキルの `SKILL.md` の「役割の実行（ハーネス別）」に書いてある。

**完了条件。** 次のコマンドが `13` を出力する（役割プロンプトがスキル側にそろっている）。

```bash
ls "$HOME"/.agents/skills/job-change-*/references/roles/*.md | wc -l
```

## 手順3: 設定ファイルを作る

利用者データの置き場所は設定ファイルだけが決める。既定の置き場所を持たない。

**この置き場所には、現年収・居住地・在籍企業名・実績を含む個人情報が保存される。** 置き場所は必ず利用者に確認する。エージェントは独断で決めない。同期や共有の対象になっているディレクトリを避けるよう伝える。

利用者が答えた場所を絶対パスにして、次を実行する。

```bash
python "$HOME/.agents/skills/job-change-support/scripts/jc_config.py" --init --data-root /absolute/path/to/job-change-data
```

`~/.job-change/config.json` が作られる。既に設定がある場合は上書きせず終了コード 1 を返すので、その場合は既存の設定をそのまま使う。

**完了条件。** 次のコマンドが終了コード 0 を返し、`"status": "ok"` と `data_root` を含む JSON を出力する。

```bash
python "$HOME/.agents/skills/job-change-support/scripts/jc_config.py" --show
```

設定の仕様は [configuration.md](configuration.md) にある。`python3` でしか動かない環境では、作成された `~/.job-change/config.json` の `python` を `python3` に書き換える。

## 手順4: 動作を確認する

1. Codex で「転職の準備をしたい」と伝え、`job-change-support` が起動することを確認する。
2. hub が設定ゲートを通り（手順3で作成済みのため通るはず）、依頼に応じたサブスキルを提示することを確認する。

**完了条件。** hub が設定の再作成を求めず、振り分け先のサブスキルを提示する。

## Claude Code との差

Codex にはサブエージェントの仕組みがない。このスキル群は次のように振る舞いを変える。

| 項目 | Claude Code | Codex |
|---|---|---|
| 役割の実行 | 13体のサブエージェントへ委譲する | 本体が `references/roles/*.md` を読み、その役割として実行する |
| 起草と監査の独立性 | 別の文脈で実行するため保たれる | 同一の文脈になるため下がる |
| ツールの制限 | 役割の `tools` frontmatter が機械的に効く | 効かない |

このうち下の2項目は、ルールで補う必要がある。エージェントは次を守る。

- **監査の段階では、起草時の判断理由・迷った箇所・書き換えの経緯を参照しない。** 成果物と `references/` の仕様だけを見て判定する。起草側の意図を補って読まない。
- **Web 送信手段を持たない役割として作業している間は、Web 検索とページ取得を使わない。** とくに `profile.json` を読んだ後に求人検索や企業研究へ移る場合、読んだ個人情報を検索クエリへ持ち込まない。
- **Web 送信手段を持つ役割として作業している間は、`{data_root}/career-private/` 配下のファイルを開かない。** パスを渡されても開かない。

各役割プロンプトの冒頭「扱ってよい入力」に、その役割で守るべきルールが書いてある。役割として作業を始める前に必ず読む。

## つまずきやすい点

- **スキルが認識されない。** 置き先が `.agents/skills/` であることを確認する。`.codex/skills/` は使わない。ディレクトリ名は `job-change-support` のようにスキル名と一致させる。
- **`jc_config.py --show` が終了コード 2 を返す。** 設定ファイルが見つかっていない。手順3を実行する。環境変数 `JOB_CHANGE_CONFIG` を設定している場合は、それが実在するファイルを指しているか確認する。
- **検証スクリプトが動かない。** `python --version` の出力が 3.9 以上であることを確認する。標準ライブラリ以外の依存はないので、パッケージのインストールは不要である。
