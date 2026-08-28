# 英文レジュメの記述基準
<!-- textlint-disable @textlint-ja/no-synonyms -->
<!-- 出典に社名「エンワールド・ジャパン」を含むため、「ジャパン」と「日本」を表記揺れと判定させない。 -->

外資系・グローバル企業に応募するときの英文レジュメ（English resume）について、記述基準を定めた原本である。作成担当（`job-change-document-writer`）は構成・表現・ATS対応に用いる。監査担当（`job-change-document-auditor`）は、英語の文法と時制の正しさ・アクション動詞（action verb）の適否・定量性・ATS適合・分量の検査に用いる。英文レジュメは和文の履歴書と別物であり、日本語の文法・表記の検査の対象外とする。

## 基本の書式

英文レジュメの書式の標準は次のとおりである（出典: エンワールド・ジャパン「英文レジュメの書き方ガイド」 https://www.enworld.com/candidates/career-advices/foreign-job-change/resume/how-to-write-english-resume.html 信頼できる二次）。

| 観点 | 内容 |
|---|---|
| 分量 | A4 またはレターサイズで1〜2枚以内にまとめる。 |
| 並べ方 | 職歴・学歴を新しい順（逆時系列）で記載する。 |
| 文体 | 各項目を動詞（action verb）から始め、不要な主語（I など）を省く。例: 「Led a team of 5 engineers ...」「Reduced response time by 40% ...」。 |

## 構成

英文レジュメは、主に次の項目で構成する（出典: 同 エンワールド・ジャパン 信頼できる二次）。

| 項目 | 内容 |
|---|---|
| PERSONAL INFORMATION | 氏名・連絡先。後述の「記載しない個人情報」に注意する |
| OBJECTIVE | 応募職種で何を目指すかの短い宣言 |
| SUMMARY | 経歴と強みの要約 |
| WORK EXPERIENCE | 職歴。新しい順。各職務を action verb 始まりの箇条書きで書く |
| EDUCATION | 学歴。新しい順 |
| QUALIFICATIONS（SPECIAL SKILLS） | 資格・スキル |
| ADDITIONAL INFORMATION | 補足情報 |

上の表はエンワールド1社の構成である。本スキルが用いる構成（SUMMARY を必須、OBJECTIVE を任意とし、Reverse-chronological・Combination・Functional の3スタイルを持つ）と、その根拠は `references/templates.md` にある。

## 記載しない個人情報

英文レジュメには、性別・年齢・生年月日・顔写真を記載しない（出典: 同 エンワールド・ジャパン 信頼できる二次）。これは欧米諸国で採用時の差別を防止する法律が厳格に定められているためであり、和文履歴書との最大の違いである。和文履歴書の感覚でこれらを載せない。

## 実績の定量化

- 箇条書きは「Action（動詞）＋ Project（対象・文脈）＋ Result（結果）」の型で書き、成果を「◯% improvement」「◯% increase」のように定量化する（出典: Yale Office of Career Strategy「Writing Impactful Resume Bullets」 https://ocs.yale.edu/resources/writing-impactful-resume-bullets/ 信頼できる二次）。チームの成果ではなく本人の貢献を書く。
- 定量値は `profile.json` の `achievements[].metric` と厳密一致させる。metric に無い数値を作らない。

## ATS対応

多くの企業が応募書類を ATS（Applicant Tracking System、応募者追跡システム）で処理する。ATS はキーワードで書類をスキャンし、ランク付けする（出典: Indeed「Get Your Resume Seen With ATS Keywords」 https://www.indeed.com/career-advice/resumes-cover-letters/ats-resume-keywords 信頼できる二次）。

| 指針 | 内容 |
|---|---|
| 求人票との文脈整合 | 求人票（job description）で使われている言葉を、経験の文脈に合う形で反映する。求人票のキーワードを、実際の職務・成果を記述する中で自然に用いる。 |
| キーワードの詰め込み（keyword stuffing）を避ける | 現代の NLP 型 ATS は、単純なキーワードの出現回数ではなく文脈・関連性を評価する。同じ言葉を不自然に反復すると低品質と判定されてスコアが下がり、人間の審査者にも不自然に映る。有効なのは、求人票からの正確な抽出と定量的な裏付けを伴う場合に限られる。要点は、求人票との文脈整合である。 |
| 表・画像・グラフィックを避ける | 表・画像・グラフィック（グラフ・チャートを含む）は ATS が正しくパースできないことがある。単純なテキスト書式で作る。 |

### ATS が有能な候補を取りこぼす問題

ATS は候補を誤りなく選別する仕組みではない。ATS対応は「通す」ためだけでなく、「誤って弾かれない」ための備えでもある（出典: Harvard Business School / Accenture「Hidden Workers: Untapped Talent」2021 を報告した二次記事 https://jobcannon.io/research/stats/hbs-accenture-hidden-workers-2021 口コミ・集約レベル。一次は Fuller & Raman らの HBS/Accenture 報告書）。

次の2つは別の統計であり、因果的に結合して述べない。

| 統計 | 内容 |
|---|---|
| 雇用主の88% | 有能で高スキルの候補が選考過程で取りこぼされている（vetted out）ことを認めた雇用主の割合。ATS を含む選考の仕組みが有能な候補を弾きうるという、雇用主側の自己認識である。この数値は単一の調査報告（HBS/Accenture 2021）に由来する（レベルC）。 |
| 約2700万人（hidden workers） | 就業状態で定義された hidden workers の総数であり、「ATS によって排除された人数」ではない。この総数と88%を、「ATS が2700万人を排除した」といった形で因果的に結び付けない。 |

この問題への実務的な対処が、求人票との文脈整合・様式の簡素化・企業別カスタマイズである。

### 日本国内の外資系 ATS の実態

日本で外資系企業が中途採用に用いる ATS の具体的なベンダーは、次のとおり確認できる（2026年7月時点）。

| ベンダー | 確認できた事実 |
|---|---|
| Workday | 米系の多国籍企業 NCR が、日本向けの外部採用サイトを Workday 上で運用している（URL が `ncr.wd1.myworkdayjobs.com/ext_jp`。日本語ロケール `ja-JP` の求人を含む。`subdomain.wdN.myworkdayjobs.com` は Workday Recruiting の確定的な URL 構造。出典: NCR 採用ページ URL、レベルB）。 |
| Greenhouse | 外資系テック企業（Anthropic・Databricks 等）が、日本拠点のポジションを Greenhouse の求人ボード（`job-boards.greenhouse.io`）上で公開・応募受付している（Anthropic の日本勤務職、Databricks の東京勤務職を確認。`job-boards.greenhouse.io` は Greenhouse の確定的な URL 構造。出典: 各社の Greenhouse 求人ボード URL、レベルB）。 |

Greenhouse は、日本語を含む言語でレジュメの「完全なパース機能（full parsing capabilities）」を公式サポート文書に明記している（出典: Greenhouse Support「Resume parsing with non-English languages」 https://support.greenhouse.io/hc/en-us/articles/205019689-Resume-parsing-with-non-English-languages レベルA）。ただしこれはベンダー自身の自称であり第三者検証ではない。対応言語リストに日本語は含まれるが、それは仕様上パースの対象だというだけである。日本語（CJK・分かち書きなし・全角）の実際の抽出精度を示す数値は同文書にない。

日本国内の人材紹介会社も、外資系向けに ATS対応の助言を実務で提示している。Morgan McKinley（外資系に強い人材紹介会社）は、企業側が ATS で応募情報を管理しているとする。そのうえで、求人票にあるキーワードを含める形でレジュメを編集すれば、ATS のスクリーニングを通過できる可能性が高まると助言している。あわせて、ファイル形式は PDF が望ましく、複雑な書式は ATS が処理しきれないことがあるとしている（出典: Morgan McKinley「英文レジュメの書き方：DX対応編」2023-10-05 https://www.morganmckinley.com/jp-ja/article/%E8%8B%B1%E6%96%87%E3%83%AC%E3%82%B8%E3%83%A5%E3%83%A1%E3%81%AE%E6%9B%B8%E3%81%8D%E6%96%B9%EF%BC%9ADX%E5%AF%BE%E5%BF%9C%E7%B7%A8 レベルB）。ただし発信者はレジュメ添削・紹介サービスを持つ人材紹介会社であり、ATS 対応の重要性を強調する利害を持つ（単一ソース）。

## この基準の適用範囲と限界

- 書式・構成・記載しない情報・定量化は、外資系専門エージェントと米大学キャリアセンターの規範的ガイド（信頼できる二次）に基づく。
- 日本国内での外資系 ATS の具体的なベンダー（Workday・Greenhouse）と、日本語書類が仕様上パース対象であること（Greenhouse 公式）は確認できた（上記「日本国内の外資系 ATS の実態」）。一方、外資系 ATS の導入率の一次定量データと、日本語レジュメの実際のパース精度を示す数値は、2026年7月時点の追加探索（IMARC の日本 ATS 市場レポート、Greenhouse 公式のパース対応文書、外資系向け人材紹介会社の解説記事）でも確認できていない。IMARC の市場レポートは方法論を開示しない単独ソース（レベルC）で個別数値の独立裏取りができず、Greenhouse 公式文書にも実際のパース精度の数値は無い。国内の外資系求人で ATS がどの程度用いられるかは、応募先・エージェントに確認するのが確実である。
- hidden workers の88%・2700万人は、単一の調査報告（HBS/Accenture 2021、レベルC）に由来する。断定的な因果表現には用いない。

<!-- textlint-enable @textlint-ja/no-synonyms -->
