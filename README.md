# job-change skills

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3-3776AB.svg)](#インストール)


転職活動のサポートを目指したスキル群です。

## インストール

### Claude Code

```
/plugin marketplace add https://github.com/tomkd555/jobchange-skills.git
/plugin install job-change@job-change-skills
```
Claude in Chrome も別途導入ください。

## スキル

### job-change-support

転職活動を支援するスキルです。データの保存先を設定したうえで、次の 3 つの手順を進めます。設定ファイルは [docs/configuration.md](docs/configuration.md) で説明しています。

- 求人検索: 希望の一文から求人を探します。
- 求人チェック: 1 件の求人と、その企業の公式の数値を記録します。
- 意思決定: 2〜5 件の求人や内定を比べて、選んだ結果を記録します。
