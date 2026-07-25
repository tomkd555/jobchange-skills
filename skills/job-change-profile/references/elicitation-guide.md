# 聞き取りの方法論（想起手がかりと任意の自己確認の根拠）

<!-- textlint-disable jtf-style/4.3.2.大かっこ［］ -->
<!-- 本文中の [E1] 形式は出典 ID の記法である。半角大かっこを保つため、このファイルでは当該規則を無効化する。 -->

job-change-profile スキルの聞き取り設計の原本である。SKILL.md の原則・question-bank.md の質問設計・エージェント2体（writer / auditor）がこのファイルを参照する。証拠グレードは A〜D の4段階（A=査読済みの学術研究・一次公式、B=信頼できる二次、C=口コミ・集計・HRブログ、D=個人ブログ・伝聞）で表記し、学術研究には DOI を記す。表記形式は末尾の「出典一覧」に対応づける。

## 構造化した想起手がかりで聞き取る

自由記述に委ねず、事前に項目と順序を固定した構造的な枠に沿って聞くほうが、職務経歴・実績の想起は網羅的かつ正確になるとする証拠が優勢である（確度: 可能性が高い、65%以上80%未満）。

- 選抜手法の妥当性メタ分析で構造化面接は上位群に位置づけられ[E17]、面接の内容と構造が妥当性を規定する[E18]。構造化面接は非構造化面接の約2倍の妥当性を生んだ[E19]。
- 自伝的記憶は階層ネットワークであり、イベント・ヒストリー・カレンダー（時系列とテーマ横断を組み合わせた手がかり）はこの構造に沿って想起の完全性・正確性を高める[E20]。カレンダー型手法は回顧データの完全性・一貫性を高める[E24]。

運用: 聞き取りは「企業→在籍期間→役割→担当プロジェクト→成果」の時系列枠に沿って進める（question-bank.md の Step 1〜2）。転職・異動・昇進などの転機を時系列の手がかりに使う。個々の実績を単発で聞くのではなく、在籍期間のなかに位置づけて聞く。

**確信度を下げる証拠（限界）**: 構造化技法（イベント・ヒストリー・カレンダー）は、世帯員数・勤務先数などで過大報告を有意に増やす場合がある[E21]。構造化は万能ではなく、次の任意の自己確認と併用する。

## 自己報告の内在誤差と任意の自己確認

職務経歴の自己報告には内在的な誤差が残る。日付・在籍期間・実績値のうち記憶が曖昧なものは、聞き取りだけで確定とせず、エビデンスでの任意の確認を促す（確度: 可能性が高い、65%以上80%未満）。

- 作業歴の自己報告の妥当性は20〜100%（多くは70〜75%）で、誤分類13〜29%が残り、聞き手の技量が精度を左右する[E22]。回顧的な日付は前方テレスコーピング（実際より最近に寄せる系統バイアス）を受ける[E23]。
- 日本の採用実務では、社会保険・源泉徴収・リファレンスチェックによって客観的な記録と照合され、矛盾はそこで露見する[E102]。したがって聞き取り時点で「源泉徴収票・雇用保険の記録で日付を確認する」という任意の確認を促せば、詐称疑義と単純な誤記の双方を予防できる。

運用: 日付・年収・実績値のうち記憶が曖昧なものについては、聞き取り後に `assets/verification_checklist.md` を任意の自己確認として案内する（在籍期間は雇用保険・社会保険の記録と、年収は源泉徴収票と、実績値は人事評価資料・社内報告と照合する）。確認は利用者が任意に行うもので、書類の提出を求めない。エビデンスが手元になければ省いてよい。在籍期間・年収の情報を持たない書類（健康保険証など）は用いない。本スキルはエビデンスを代わりに取得しない。

**確信度を下げる証拠（限界）**: 誤差の大きさは分野・在職期間・想起手がかりに依存し一律でない[E22]。自己確認は「必ず誤りがある」という前提ではなく、系統誤差を減らす任意の手続きとして位置づける。

## 空白期間の扱い

職歴の骨格を確定したら、隣接する職歴間の空白期間（6か月以上）を機械的に検出し、説明と期間中の活動を聞く（確度: 可能性が高い、65%以上80%未満）。

- 空白期間は、3か月以内であれば問題視されにくいが、6か月以上は理由と計画性の説明が要る[E100]。
- 空白期間は、それ自体が依然として採用の可否と賃金に不利に働く。「空白は無害」という強い主張は成り立たない[E99]。

運用: 空白は隠すのではなく、`career_gaps` に期間・説明・期間中の活動（学習・資格取得・介護・療養など）を記録し、説明可能な形にする。これは詐称に頼らず正確性・網羅性を保つための欄であり、空白を有利に見せるための創作の場ではない。

**確信度を下げる証拠（限界）**: HBR による空白期間の研究については、効果量の本文値を取得できておらず、空白が選考結果に与える影響の定量的な大きさは本スキルとして確定していない（エビデンスギャップ）。

## 選択式を中心にした聞き取りの運用

- 聞き取りは AskUserQuestion の選択式を中心に運用する。1回の AskUserQuestion につき最大4問、各質問は最大4択とする。自由記述は、企業名・在籍期間・実績値のように選択式にできない項目に限る。
- 深掘りは、感情の反すうへ落とさず、事実（いつ・どの場面で・何をしたか）へ向ける。退職理由の建設的言い換え・強みの根拠づけといった内省の深掘りは本スキルの範囲外とし、`job-change-self-analysis` へ誘導する。
- 聞き取り結果は、聞き取り中に本体セッションが `career-private/profile_interview_notes.md` へ逐次追記する。これにより中断と再開に対応できる。起草担当（writer）は、このメモにある事実だけを使う。

## 更新運用

profile.json は一度作って終わりにせず、鮮度を保つ（確度: 可能性が高い、65%以上80%未満）。

- 古い情報の放置と網羅性の欠如は典型的な失敗であり、応募書類の作成では直近7〜10年を優先し、非該当業務を削る[E103]。四半期ごとの更新と、継続的に更新する文書（running document）でのキャリア棚卸しが英語圏・日本語圏の双方の資料で共通に推奨される[E104]。

運用: 実績が出るたび、最低でも四半期ごとに追記する。profile.json 自体は網羅的に保ち（直近7〜10年への絞り込みは応募書類の作成の段階で応募書類サブスキルが行う）、更新のたびに `updated_at` を書き換える。

## 出典一覧

<!-- textlint-disable -->
<!-- 書誌形式（発行元. 表題. 年. グレード. URL）で出典を並べる区画である。区切りのピリオドと社名の一部を和文の句読点・同義語として判定させないため、この節だけ無効化する。 -->

- [E17] Psychological Bulletin (APA). The validity and utility of selection methods in personnel psychology. 1998. グレードA. DOI:10.1037/0033-2909.124.2.262. https://doi.org/10.1037/0033-2909.124.2.262
- [E18] Journal of Applied Psychology (APA). The validity of employment interviews: A comprehensive review and meta-analysis. 1994. グレードA. DOI:10.1037/0021-9010.79.4.599. https://doi.org/10.1037/0021-9010.79.4.599
- [E19] Journal of Occupational Psychology. A meta-analytic investigation of the impact of interview format and degree of structure. 1988. グレードA. DOI:10.1111/j.2044-8325.1988.tb00467.x. https://doi.org/10.1111/j.2044-8325.1988.tb00467.x
- [E20] Memory. The structure of autobiographical memory and the event history calendar. 1998-07. グレードA. DOI:10.1080/741942610. https://doi.org/10.1080/741942610
- [E21] Public Opinion Quarterly. Event history calendars and question list surveys: a direct comparison of interviewing methods. 2001. グレードA. DOI:10.1086/320037. https://doi.org/10.1086/320037
- [E22] British Journal of Industrial Medicine. An investigation of the validity of self-reported work histories. 1987. グレードA. DOI:10.1136/oem.44.10.702. https://doi.org/10.1136/oem.44.10.702
- [E23] International Journal of Methods in Psychiatric Research. Forward telescoping bias in reported age of onset. 2005. グレードA. DOI:10.1002/mpr.2. https://doi.org/10.1002/mpr.2
- [E24] Quality & Quantity. Applications of calendar instruments in social surveys: a review. 2009. グレードA. DOI:10.1007/s11135-007-9129-8. https://doi.org/10.1007/s11135-007-9129-8
- [E99] Harvard Business Review (Groysberg, Lin). Research: Resume Gaps Still Matter. 2024-07-31. グレードB. https://hbr.org/2024/07/research-resume-gaps-still-matter
- [E100] JAC Recruitment. 面接での経歴の空白期間の好印象な答え方は？. 2024-06-12. グレードC. https://www.jac-recruitment.jp/market/knowhow/interview/interview-blank-period/
- [E102] ASHIATO（エン・ジャパン）. バックグラウンドチェックで経歴詐称や転職活動はバレない？. 2024-09-19. グレードC. https://ashiatohr.com/news/7ecucee-k
- [E103] Forbes JAPAN. 2026年の採用市場で差がつく「職務経歴書」5つの更新ポイント. 2026-03-15. グレードC. https://forbesjapan.com/articles/detail/93818
- [E104] Indeed / ResumeGenius 他. Guide To Updating Your Resume. 2024. グレードC. https://www.indeed.com/career-advice/resumes-cover-letters/guide-to-updating-your-resume

<!-- textlint-enable -->
