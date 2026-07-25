# 設定ファイル

転職支援スキル群は、利用者データの置き場所を設定ファイルだけで決める。既定の置き場所を持たない。設定が確定するまで、hub（`job-change-support`）はどのサブスキルへも振り分けない。

置き場所を暗黙に決めない理由は2つある。第一に、利用者データには現年収・居住地・在籍企業名などの個人情報が含まれ、どこへ置くかは利用者が決めるべきである。第二に、スキル本体を置いたディレクトリへ既定で書き込むと、スキルを更新・再導入するたびに個人情報の所在が変わる。

## 探索順序

次の順に探し、最初に見つかったものを使う。

| 順 | 場所 | 用途 |
|---|---|---|
| 1 | 環境変数 `JOB_CHANGE_CONFIG` が指すファイル | 一時的な切り替え、CI |
| 2 | カレントディレクトリから上位へたどった最初の `.job-change/config.json` | 案件ごと・リポジトリごとに分ける場合 |
| 3 | `~/.job-change/config.json` | 通常の利用 |

`JOB_CHANGE_CONFIG` が指すファイルが存在しない場合は、その指定を無視して 2 以降を探す。

## 内容

```json
{
  "schema_version": "1.0",
  "data_root": "/absolute/path/to/job-change-data",
  "private_dir": "career-private",
  "companies_dir": "companies",
  "job_search_dir": "job-search",
  "python": "python"
}
```

| キー | 必須 | 既定 | 内容 |
|---|---|---|---|
| `schema_version` | 任意 | `"1.0"` | 設定ファイルの版 |
| `data_root` | **必須** | なし | 利用者データを置くディレクトリ。絶対パスで書く。先頭の `~` はホームディレクトリへ展開される |
| `private_dir` | 任意 | `career-private` | 個人情報を置くディレクトリ名。`data_root` 直下の単純な名前で書く（パス区切り文字を含められない） |
| `companies_dir` | 任意 | `companies` | 企業別成果物を置くディレクトリ名 |
| `job_search_dir` | 任意 | `job-search` | 求人検索結果を置くディレクトリ名 |
| `python` | 任意 | `python` | 検証スクリプトを実行するコマンド。`python3` や絶対パスも書ける |

## ディレクトリ構成

```
{data_root}/
├─ career-private/          ← 個人情報。Web ツールを持つエージェントへ渡さない
│   ├─ profile.json
│   ├─ self_analysis.json
│   ├─ company_index.json
│   ├─ commute.json
│   └─ fit/{企業スラッグ}/{fit_assessment,time_analysis}.json
├─ companies/{企業スラッグ}/  ← 企業別成果物（非個人情報）
└─ job-search/{YYYYMMDD}-{スラッグ}/job_search_results.json
```

`career-private/` を `companies/` の外側へ置くのは、Web 送信手段を持つエージェントが作業するツリーから個人情報を隔離するためである。`private_dir` の名前を変えてもこの隔離は保たれる。

## 作成

hub は、初めて起動した時点で設定がなければ置き場所を尋ねる。手作業で作る場合は次を実行する。

```bash
python <スキルの配置先>/job-change-support/scripts/jc_config.py --init --data-root /absolute/path/to/job-change-data
```

既に設定ファイルがある場合は上書きせず、終了コード 1 を返す。

## 確認

```bash
python <スキルの配置先>/job-change-support/scripts/jc_config.py --show
```

探索順序に従って確定した設定と、各データの絶対パスを JSON で出力する。終了コードは、成功なら 0、設定は見つかったが内容が不正なら 1、未設定なら 2 である。

個別のパスだけが必要な場合は `--path` を使う。キーは `data_root`・`private`・`companies`・`job_search`・`profile`・`company_index`・`self_analysis`・`commute` である。

```bash
python .../jc_config.py --path profile
```

いずれのオプションもディレクトリを作らない。ディレクトリは、各スキルが成果物を書く時点で作る。

## スキル本文でのパス表記

各 SKILL.md と references は、データのパスを `{DATA_ROOT}/career-private/profile.json` のように書く。`{DATA_ROOT}` は `jc_config.py --show` が返す `data_root` に読み替える。ディレクトリ名を既定から変えている場合は、`--show` が返す `paths` を使う。

スキル本体を指すプレースホルダは2種類ある。`{SKILL_DIR}` はそのスキル自身のディレクトリを指し、`{HUB_SKILL_DIR}` は `job-change-support` のディレクトリを指す。
