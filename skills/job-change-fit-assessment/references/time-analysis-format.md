# time_analysis.json の原本仕様（time-analysis-format）

`time_analysis.json` の仕様と、`scripts/calculate_time_analysis.py` による算定の仕組みを定める原本である。応募先候補の求人票・企業研究・利用者入力から、1日および年間の拘束時間・労働時間・実質時給を決定的に算定し、time_fit（時間適合）評価の根拠として使う。

## 配置と扱い

生成物は `career-private/fit/{企業スラッグ}/time_analysis.json` に置く。比較の基準となる現職の算定結果は、応募先の企業に対応しないため `career-private/fit/current/time_analysis.json` に置き、全企業で使い回す。拘束時間・実質時給は年収・通勤時間などの個人情報から導く派生値であるため、`career-private/` 配下に隔離し、Web 送信手段（WebSearch・WebFetch）を持つエージェントへ渡さない。

## 定義式

`calculate_time_analysis.py` は次の式で算定する。分母は「年間実出勤日数」に一本化する。

- 月出勤日数 = `(365 − 年間休日) ÷ 12`
- 日次残業 = `月平均残業時間 ÷ 月出勤日数`
- 1日拘束時間 = `所定労働時間 + 休憩 + 日次残業 + 通勤片道 × 2`
- 有給取得日数 = `取得日数実績（あれば）／なければ 付与日数見込 × 取得率(%) ÷ 100`
- 年間実出勤日数 = `365 − 年間休日 − 有給取得日数`
- 年間拘束時間 = `年間実出勤日数 × 1日拘束時間`
- 年間労働時間 = `年間実出勤日数 × (所定労働時間 + 日次残業)`
- 実質時給（binding_basis）= `想定年収 ÷ 年間拘束時間`
- 実質時給（labor_basis）= `想定年収 ÷ 年間労働時間`

レベル付きの想定年収が無いとき、`effective_hourly_wage` は `null` にする。実質時給を創作しない。

内部計算では丸めをかけない。出力時にのみ、時間は小数第1位、日数と円は整数へ丸める。

## 感度分析

`sensitivity` は、他の入力を固定して次の1項目だけを動かしたときの、年間拘束時間の増減値（時間）を持つ。

- `overtime_plus10h` / `overtime_minus10h`: 月平均残業を ±10 時間動かしたときの増減
- `commute_plus15min` / `commute_minus15min`: 通勤片道を ±15 分動かしたときの増減

年間実出勤日数は残業・通勤に依存しないため、増減値はプラス側とマイナス側で符号が反転した対称値になり、基準の水準には依存しない。

## 現職との比較

応募先の拘束時間・実質時給は、単体の絶対値では良し悪しを判断できない。現職についても同じ式で算定し、その差分を time_fit と compensation_fit の判断材料にする。

現職の算定結果を `--baseline-json` へ渡すと、出力へ `comparison` が加わる。渡さなければ `comparison` は出力しない。

| キー | 内容 |
|---|---|
| `current` | 現職の値。`annual_binding_hours`・`annual_labor_hours`・`hourly_wage_binding_basis`・`hourly_wage_labor_basis` の4項目を持つ。 |
| `delta` | 「応募先 − 現職」の差分。項目は `current` と同じ。 |

どちらか一方でも数値として取れない項目は、`current`・`delta` ともに `null` にする。時間は小数第1位、円は整数へ丸める。

現職の算定に使う年収・労働時間・通勤時間は利用者入力（`user`）で取り、通勤時間は下記「通勤時間が未入力のときの扱い」と同じ系統を使う。

## 入力の優先度

各入力の値は、次の優先順で決める。上位で確定した値を使い、下位へ下がるほど確度は落ちる。決定した出所は各入力の `source`（`posting` / `research` / `user` / `fallback`）に記録する。

| 優先度 | 出所 | 内容 |
|---|---|---|
| 1 | 求人票（`posting`） | `job_posting.json` の `working_hours`・`metrics` に引用付きで載る値。最優先とする。 |
| 2 | 企業研究の指標（`research`） | `company_research.json` の `company_metrics`（月平均残業は `monthly_overtime`、年間休日は `annual_holidays`、有給取得率は `paid_leave_rate`、有給取得日数は `avg_paid_leave_days_taken`）。同一項目に複数の候補があるときはエビデンスレベル（A → B → C → D）が最も高いものを採用する。エビデンスレベルの定義の原本は `job-change-company-research` の `references/evidence-grading.md` にある。C・D 単独での断定は避け、値を採用するときも確度を下げて扱う。 |
| 3 | 利用者入力（`user`） | 通勤時間など、利用者本人が申告する値。 |
| 4 | 統計フォールバック（`fallback`） | 上位のいずれでも埋まらない項目に、官公庁の一次統計に基づく既定値を適用する。 |

呼び出し側（fit-assessment スキル本体）が優先度に従って値を決め、確定値を CLI 引数へ、各値の出所のメタデータを `--sources-json` へ渡す。スクリプト自身は `job_posting.json`・`company_research.json` を読まず、渡された値と、未指定項目へのフォールバック適用だけを行う。

## 通勤時間が未入力のときの扱い

通勤片道の時間は、次の1系統だけで扱う。

1. `career-private/commute.json` の当該スラッグの `one_way_minutes` があれば、それを使う。
2. 無ければ、AskUserQuestion で1回だけ確認する。
3. それでも不明なら、統計フォールバックを適用し、`fallbacks_used` と `assumptions` に明示する。

住所からのジオコーディングや Web 経路検索は行わない。

## フォールバック定数の原本

統計フォールバックの値・調査名・調査年・出典 URL の原本は、`calculate_time_analysis.py` 内の定数 `FALLBACKS`（統計値）と `STATUTORY_DEFAULTS`（所定労働時間・休憩の法定既定値）である。本文書には数値を重複して書かない。定数を変更するときはスクリプトの当該定数を直接編集する。

`FALLBACKS` の各項目には、厚生労働省・総務省いずれかの一次統計（官公庁ドメイン）の最新公表値を裏取りして設定し、`{value, survey, survey_year, source_url}` を保持させる。フォールバックを適用した項目は、生成物の `fallbacks_used`（構造化した記録）と `assumptions`（値・調査名・調査年・URL を含む文）の双方に必ず残す。

## 出力構成

```
{
  "inputs": { "<入力キー>": {"value", "source", "source_url"|null, "grade"|null}, ... },
  "daily": {"scheduled_hours", "break_h", "daily_overtime_h", "commute_oneway_h", "binding_hours"},
  "annual": {"working_days", "paid_leave_taken_days", "binding_hours", "labor_hours"},
  "effective_hourly_wage": {"binding_basis", "labor_basis"} | null,
  "sensitivity": {"overtime_plus10h", "overtime_minus10h", "commute_plus15min", "commute_minus15min"},
  "comparison": {"current": {...}, "delta": {...}},
  "assumptions": [ ... ],
  "fallbacks_used": [ {"field", "value", ...}, ... ]
}
```

`inputs` には算定に使った数値のみを載せる。有給取得日数の実績（`paid_leave_taken`）を与えたときは、その値を `inputs` に載せ、付与日数・取得率は算定に使わないため載せない。実績を与えないときは、付与日数（`paid_leave_granted`）と取得率（`paid_leave_rate`。単位は % で、企業研究の `company_metrics.paid_leave_rate` と同じ尺度）を載せ、付与日数 × 取得率 ÷ 100 で取得日数を推計する。

記入例は `assets/time_analysis_example.json`（架空データ）にある。

## CLI

```bash
python scripts/calculate_time_analysis.py \
    [--scheduled-hours H] [--break-minutes M] [--overtime-h-month H] \
    [--annual-holidays D] [--paid-leave-rate R] [--paid-leave-granted D] \
    [--paid-leave-taken D] [--commute-oneway-min M] [--salary YEN] \
    [--sources-json PATH] [--baseline-json PATH] [--out PATH] [--json]
```

`--baseline-json` には現職の `time_analysis.json` のパスを渡す。指定しなかった項目にはフォールバックを適用する。`--out` は指定パスへ書き出し（親ディレクトリが無ければ作成する）、`--json` は結果を標準出力へ書き出す。年間休日が 365 以上、有給取得率が 0〜100（%）の範囲外など、入力に矛盾があるときは終了コード 2 で明確なメッセージを返す。
