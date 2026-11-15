# job-change skills

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3-3776AB.svg)](#インストール)

日本の中途採用での転職活動を支援する Claude Code プラグインです。求人検索、求人チェック、企業研究、意思決定の 4 つの手順があり、調べた情報には出典を付けます。

## インストール

```
/plugin marketplace add https://github.com/tomkd555/jobchange-skills.git
/plugin install job-change@job-change-skills
```

求人検索と求人チェックでは、一部の求人サイトのページを Claude in Chrome で読みます。また、プラグインはどの手順でも Python のスクリプトを実行するため、Python 3 が必要です。

手動でのインストールは [docs/install-claude-code.md](docs/install-claude-code.md)、Codex でのインストールは [docs/install-codex.md](docs/install-codex.md) で説明しています。

## 使い方

手順ごとに、次の表の例のように依頼します。

| 手順 | 依頼の例 | プラグインが行うこと |
|---|---|---|
| 求人検索 | 求人を探して | 利用者が一文で書いた希望から希望条件を作り、求人を探します。 |
| 求人チェック | この求人を調べて | 1 件の求人と、その企業について公表されている数値を記録し、希望条件と比べます。 |
| 企業研究 | この会社を調べて | 1 社について、出典と引用を付けた報告書を作ります。報告書には、会社の概要、配属先で担当する仕事の実態、残業と年収の実態、直近の業績とリスク、面接で確認する点をまとめます。 |
| 意思決定 | 2 社で迷っている | 2〜5 件の求人や内定を比べ、利用者がどれを選んだかを記録します。 |

初回の依頼では、プラグインがデータの保存先を尋ね、設定ファイルに記録します。設定ファイルは [docs/configuration.md](docs/configuration.md) で説明しています。

## 個人情報の扱い

- 現在の勤務先名と現在の年収は尋ねず、ファイルにも記録しません。
- Web を検索するサブエージェントには、求人検索では匿名化した希望条件を、求人チェックと企業研究では会社名と求人の情報を渡します。
- 応募、転職エージェントへの登録、スカウトへの返信は、利用者自身が行います。

## ライセンス

MIT
