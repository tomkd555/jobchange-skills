# 給与・福利厚生・働き方の調査原本（compensation-benefits）

給与（topic=compensation）・福利厚生（topic=benefits）・働き方（topic=workstyle）を調査するときの観点と情報源カタログを定める原本である。証拠グレード（A〜D）の定義・判定基準・運用ルールは `references/evidence-grading.md` に従い、本ファイルでは重複定義しない。各情報源には、そのグレードの目安を付す。

収集した数値（年間休日・月平均残業・有給取得率・平均有給取得日数・平均年間給与）は、散文の claim に埋めるだけでなく、必ず `company_research.json` の `workstyle_metrics` へ構造化して格納する（形式は `references/company-research-format.md`。出典URL・グレード併記。見つからなければ null）。

## 調査観点

### 給与（compensation）

| 観点 | 内容 |
|---|---|
| 報酬制度の構造 | 等級・グレード制の有無、給与レンジ、賞与の回数と算定方式（業績連動か固定か）、昇給の仕組み、各種手当。採用サイトの報酬制度ページ・募集要項が一次情報（グレードA。ただし評価的表現は事実性を担保しない）。 |
| 平均年間給与の水準 | 有価証券報告書「従業員の状況」の平均年間給与（グレードA）。全従業員平均であり職種別・雇用形態別の内訳を欠く点を statement または open_questions に明示する（限界は `references/source-catalog.md` と `references/evidence-grading.md` を参照）。 |
| 求人票レンジとの照合 | 求人票（job_posting.json）の提示レンジと、有報の平均年間給与・公的統計の職種別水準を突き合わせる。開きがあれば open_questions に残す。 |
| 口コミの年収集計 | 口コミ集計サイトの年収データ（グレードC）は、十分な件数の集計値に限って傍証に用いる。個票・少件数は断定に使わない。 |

### 福利厚生（benefits）

| 観点 | 内容 |
|---|---|
| 制度の有無（事実） | 社会保険・退職金・住宅補助・育児/介護支援・カフェテリアプラン等。採用サイト・福利厚生ページが一次情報（グレードA）。 |
| 認定の有無（事実） | くるみん・えるぼし・健康経営優良法人・ユースエール等の認定は、根拠法と所管が明確な一次情報（グレードA）。ただし認定は最低基準の充足を示すもので、総合的な働きやすさを保証しない。認定を根拠に「働きやすい」と断定しない。 |
| 制度と運用の区別 | 制度が「ある」ことと「使われている」ことは別である。育休取得率・有給取得率などの運用実績（workstyle）と突き合わせる。 |

### 働き方（workstyle）

| 観点 | 内容 |
|---|---|
| 労働時間・残業 | 所定労働時間、月平均所定外労働時間、裁量労働・フレックス・リモートの方針。しょくばらぼの自主開示（グレードA）、求人票、就職四季報（グレードB）。 |
| 休暇 | 年間休日数、有給取得率、平均有給取得日数。しょくばらぼ・就職四季報・求人票。 |
| 定着率 | 3年後定着率・平均勤続年数。就職四季報（グレードB）・有報の平均勤続年数（グレードA）。 |
| 口コミの働き方評価 | 残業実態・休暇取得のしやすさの口コミ（グレードC）は、集約総合スコアに限って条件付きの傍証に用いる。個票は選択バイアスで極端化するため断定に使わない。 |

## 情報源カタログ

### 一次・公式（グレードA）

| 情報源 | 主に分かること | topic | 出典URL |
|---|---|---|---|
| EDINET 有価証券報告書「従業員の状況」 | 平均年間給与・平均勤続年数・平均年齢・従業員数 | compensation/financials/workstyle | 閲覧サイト https://disclosure2.edinet-fsa.go.jp/WEEK0010.aspx （EDINETについて https://www.fsa.go.jp/search/20130917.html ） |
| 厚生労働省「しょくばらぼ」 | 中途採用比率・定着率・月平均所定外労働時間・有給取得率（企業の自主開示） | workstyle/benefits | https://shokuba.mhlw.go.jp/ |
| 採用サイト 報酬制度・福利厚生ページ | 等級・給与レンジ・賞与算定式・手当・福利厚生制度 | compensation/benefits | 各企業ドメイン（company 所有ページ。評価的表現は confidence を high にしない） |
| くるみん／プラチナくるみん／トライくるみん | 次世代育成支援（子育て支援）の認定 | benefits | https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/kodomo/shokuba_kosodate/kurumin/index.html |
| えるぼし／プラチナえるぼし | 女性活躍推進（5基準）の認定 | benefits/workstyle | https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/0000091025_00002.html |
| 健康経営優良法人（ホワイト500） | 健康経営の顕彰 | benefits | https://www.meti.go.jp/policy/mono_info_service/healthcare/kenkoukeiei_yuryouhouzin.html |
| ユースエール | 若者の採用・育成に積極的な中小企業の認定 | benefits/workstyle | https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/0000100266.html |

認定の有無は事実（グレードA）だが、認定は最低基準の充足を示すものであり、企業の総合的な働きやすさを保証しない。

### 信頼できる二次（グレードB）

| 情報源 | 主に分かること | topic | 出典URL |
|---|---|---|---|
| 就職四季報（東洋経済新報社） | 3年後定着率・平均年収・残業時間・有給取得（掲載料無償の独自調査） | workstyle/compensation/reputation | https://str.toyokeizai.net/magazine/shushoku_all/ |

大手報道機関の記事・業界団体のレポートも、一次資料を編集した二次情報としてグレードBとする。

### 口コミ・集計サイト（グレードC）

| 情報源 | 主に分かること | topic | 出典URL |
|---|---|---|---|
| OpenWork | 年収集計・残業実態・有給取得・待遇面の総合評価（在籍証明の提出と目視審査あり） | compensation/workstyle/reputation | https://www.openwork.jp/ |

口コミは、集約総合スコアかつ十分な件数かつ複数照合を条件に傍証として用いる。個票・少件数・ファセット単位は事実の断定に使わない（根拠と限界は `references/evidence-grading.md` の「集約総合スコアの条件付き妥当性」「口コミの選択バイアス」を参照）。

## 年収水準の比較のための公的統計（対照）

企業単体の平均年間給与（有報）を、業界・職種・年齢の水準と比較して位置づけるために、公的統計を対照として使う。いずれも公的統計であり、事実としてグレードAで扱う。

| 統計 | 所管 | 主に分かること | 出典URL |
|---|---|---|---|
| 賃金構造基本統計調査 | 厚生労働省 | 職種別・年齢別・企業規模別・産業別の賃金（所定内給与・年間賞与） | 案内 https://www.mhlw.go.jp/toukei/list/chinginkouzou.html ／ データ（e-Stat）https://www.e-stat.go.jp/statistics/00450091 |
| 民間給与実態統計調査 | 国税庁 | 給与所得者の平均給与（性別・雇用形態別・企業規模別・業種別） | https://www.nta.go.jp/publication/statistics/kokuzeicho/minkan/top.htm |

比較の限界: 有報の平均年間給与は全従業員平均で職種別内訳を欠くため、公的統計の職種別・年齢別水準との比較は厳密な同一条件の対照ではない。比較はあくまで水準の把握にとどめ、単純な優劣の断定はしない。この限界を open_questions に残す。

## claim・workstyle_metrics への落とし込み

- 数値（年間休日・残業・有給取得率・平均有給取得日数・平均年間給与）を収集したら、対応する claim を作り、加えて `workstyle_metrics` へ構造化して格納する（value・source_url・grade）。
- 制度の「有無」は事実の claim にする（例:「健康経営優良法人2026に認定されている」grade=B）。制度の「良し悪し」は評価であり、断定しない。
- 求人票レンジと有報平均・公的統計の食い違いは open_questions に残す。
