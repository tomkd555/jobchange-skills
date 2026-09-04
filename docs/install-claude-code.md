# Claude Code への導入

## プラグインとして導入する（推奨）

リポジトリのルートがそのままプラグインであり、マーケットプレイスでもある。次の2行で9スキルと14エージェントを配置できる。

```
/plugin marketplace add <このリポジトリの URL またはローカルパス>
/plugin install job-change@job-change-skills
```

ローカルに clone してある場合は、URL の代わりにそのパスを渡す。

```
/plugin marketplace add C:/path/to/jobchange_Skills
/plugin install job-change@job-change-skills
```

導入後、`/plugin` で `job-change` が有効になっていることを確認する。スキルの一覧は `/help` またはスラッシュコマンドの補完（`/job-change-` と入力する）で確認できる。

更新は次のコマンドで行う。

```
/plugin marketplace update job-change-skills
```

## 手作業で導入する

プラグインを使わない場合は、次のとおり配置する。

| 置くもの | 置き先 |
|---|---|
| `skills/job-change-*` の9ディレクトリ | `~/.claude/skills/` |
| `agents/job-change-*.md` の14ファイル | `~/.claude/agents/` |

9スキルは相互に参照するため、一括で置く。プロジェクト単位にしたい場合は、`~/.claude/` の代わりに `<プロジェクト>/.claude/` へ置く。

コピーの代わりにシンボリックリンクでもよい。Claude Code は `~/.claude/skills/<名前>` のシンボリックリンクをたどる。

```powershell
# Windows（管理者権限または開発者モードが要る）
New-Item -ItemType SymbolicLink -Path "$HOME\.claude\skills\job-change-support" -Target "C:\path\to\jobchange_Skills\skills\job-change-support"
```

```bash
# macOS / Linux
ln -s /path/to/jobchange_Skills/skills/job-change-support ~/.claude/skills/job-change-support
```

## 初回の設定

利用者データの置き場所は設定ファイルの記述だけで決まる。既定の置き場所は無い。

導入後に「転職の準備をしたい」と伝えるか `/job-change-support` を実行すると、hub が設定の有無を確認する。未設定なら置き場所を尋ねられるので、選択肢から選ぶか任意の絶対パスを答える。この置き場所には現年収・居住地・在籍企業名を含む個人情報が保存されるため、同期や共有の対象になっていないディレクトリを選ぶ。

対話を待たずに作る場合は次を実行する。

```bash
python ~/.claude/skills/job-change-support/scripts/jc_config.py --init --data-root /absolute/path/to/job-change-data
```

プラグインとして導入した場合、スキルの実体はプラグインの導入先にある。パスは `/plugin` の詳細表示で確認できる。

設定の確認は次のとおりである。

```bash
python <スキルの配置先>/job-change-support/scripts/jc_config.py --show
```

終了コード 0 で `data_root` と各データの絶対パスが出力されれば導入は完了である。設定の仕様は [configuration.md](configuration.md) にある。

## 動作確認

1. `/job-change-support` を実行し、hub が設定ゲートを通ること（未設定なら対話が始まること）を確認する。
2. 「プロファイルを作りたい」と伝え、`job-change-profile` へ振り分けられることを確認する。
3. 聞き取りを終えたら、`{data_root}/career-private/profile.json` が作られ、`validate_profile.py` が PASS することを確認する。

## つまずきやすい点

- **Python が見つからない。** 検証スクリプトは `python` で呼ばれる。`python3` でしか呼び出せない環境では、設定ファイルの `python` を `python3` にする。
- **スキルが一覧に表示されない。** 起動中のセッションで新しくスキルディレクトリを作った場合は、Claude Code の再起動が必要である。既存ディレクトリ内の `SKILL.md` の変更は再起動なしで反映される。
- **エージェントが見つからない。** `agents/` を置き忘れていないか確認する。プラグインとして導入した場合は自動で配置される。エージェントがなくても、各スキルの「役割の実行（ハーネス別）」に従えば本体だけで進められる。
