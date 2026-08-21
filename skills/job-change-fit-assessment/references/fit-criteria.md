# 適合性評価の判定基準（fit-criteria）

`fit_assessment.json` の7次元（experience_proximity / aspiration_alignment / work_character_fit / condition_fit / culture_fit / compensation_fit / time_fit）の判定基準を定める。データ構造・検証規則の原本は `references/fit-format.md`、エビデンスレベルA〜Dの原本は `job-change-company-research` スキルの `references/evidence-grading.md` にある。

## 全次元に共通するルール

1. **evidence のない主張を書かない。** 各次元の verdict は evidence（1件以上）に対応づけ、裏付けのない印象・憶測を score や verdict に反映しない。
2. **エビデンスレベルC・D単独で断定しない。** 口コミ・伝聞（company_research 内でレベルC・Dが付いた claim）のみを根拠に、その次元を高い、または低いと断定しない。C・D を根拠にする場合は verdict を限定表現にする（「口コミでは〜という声がある。傍証にとどめる」）。レベルの定義と限定表現の書き方は evidence-grading.md に従う。
3. **企業が自社を良く見せる主張に高い確度を置かない。** 採用サイトの「風通しが良い」等は、company_research 側でレベルAでも confidence を high にしていない。これを culture_fit の断定材料にしない。
4. **材料が無いときは score を null（判断保留）にする。** 憶測で数値を埋めず、unknown を優先する方針を守る。
5. **profile・self_analysis に無い事実を創作しない。** 本人の経歴・強み・条件は profile.json と self_analysis.json の記載を根拠にする。

## score 1〜5 の一般的な目安

| score | 意味 |
|---|---|
| 5 | 要件・条件・志向がほぼすべて一致する。裏付けがそろう |
| 4 | おおむね一致する。軽微な不足や未確認がある |
| 3 | 部分的に一致する。長所と短所が拮抗する |
| 2 | 不一致が優勢である。相応の懸念がある |
| 1 | 明確に不一致である。重大な障害がある |
| null | 判断材料が不足し、数値を付けられない（判断保留） |

## 次元別の判定基準

### experience_proximity（経験の近さ）

job_posting の `requirements.must[]`・`requirements.want[]` と、profile の `career_history`・`skills` を突き合わせ、**現在の経験からの距離**を測る。

- 必須要件（must）の充足を主軸に置く。必須要件を満たさない場合は score を高くしない。
- 歓迎要件（want）の充足は加点要素とする。
- 経験年数・実績（profile の achievements の metric）を evidence に用いる。
- 不足する要件は `skill_gap_items` へ1件ずつ書き、`skill_gap` を3段階（および `none`・`unknown`）で示す。段階の判定基準は次のとおりである。

| 段階 | 判定基準 |
|---|---|
| `complementable_within_3m` | 隣接技術の実務経験があり、学習対象が固有の差分に限られる。独学と業務内での適用により3か月以内に習得できる |
| `needs_6_12m_study` | 隣接経験が乏しく、体系的な学習が必要である。または実務での適用機会を別途作る必要がある |
| `not_applicable_now` | 必須要件の中核（経験年数・特定領域の実務）を満たさず、短期の学習では埋まらない |

- **この次元は「やりたいか」を含まない。** 経験が近いことを、その仕事を望んでいる根拠に使わない。志向は `aspiration_alignment` で別に評価する。
- evidence の source は主に `job_posting`・`profile`。

### aspiration_alignment（志向の一致）

求人の業務内容が「今後やりたい仕事」に近いかを、**経験の近さとは独立に**評価する。

- self_analysis の `career_narrative.future_direction` を一次資料とし、`interests.domains`（RIASEC の領域名）・`interests.concrete_topics` と求人の技術領域・製品領域の重なりを見る。
- profile の `job_change_axis.reasons`（転職で次に実現したいこと）を補助資料とする。
- **経験の近さを志向の根拠に流用しない。** 「経験があるから志向にも合う」という推論を明示的に禁じる。
- self_analysis が無い場合（`inputs.self_analysis=false`）は score を高くせず、4以上を付けることを認めない。
- evidence には `self_analysis` または `profile` を必ず含める。求人票だけで志向を断定しない。
- evidence の `ref` は `interests.domains[0]`・`career_narrative.future_direction` のようなフィールドパスで書く。

### work_character_fit（作業特性の一致）

profile の `work_character_preferences[]`（8つの作業特性の希望度）と、求人・企業の実態を突き合わせる。特性の定義は job-change-support の `references/screening-axes.md` にある。

- 求人検索を経ている場合（`inputs.job_search_screening=true`）は、`job_search_results.json` の `axis_observations`（手を動かす比率・調整業務の比率・リモート確度・夜間対応）を evidence に用いる。
- 求人検索を経ていない場合は、job_posting の業務内容と company_research の働き方から同じ観点を読む。
- **求人票から判定できない3特性を推測で埋めない。** `clear_completion`（完了条件の明確さ）・`solo_completable`（一人で完結しやすさ）・`short_feedback`（結果を短期で確認できる度合い）は、求人票にも企業研究にもまず書かれない。verdict に「求人票・企業研究からは判定できない」と明記し、面接での確認事項として `overall.open_questions` へ挙げる。
- 希望度が `must` の特性を満たさない場合は score を高くしない。その特性は `must_condition_results` でも `met=no` になる。
- evidence の source は主に `job_search_screening`・`job_posting`・`company_research`・`profile`。

### condition_fit（条件適合）

job_posting の勤務条件（`location`・`employment_type`・`working_hours` 等）と、profile の `conditions[level=want]`・`targets` を突き合わせる。必須条件の充足は `must_condition_results` で別途判定するため、この次元では望ましい条件・志望対象との整合を扱う。

- リモート可否・勤務地・雇用形態・裁量労働などの条件が、本人の希望条件とどの程度一致するかを見る。
- job_posting の `scope_of_change` を、勤務地・職種の条件を見るときの材料に加える（後述）。
- evidence の source は主に `job_posting`・`profile`。

#### scope_of_change（変更の範囲）の扱い

job_posting の `scope_of_change` は、2024年4月から求人票への明示が義務づけられた3項目（業務の変更の範囲・就業場所の変更の範囲・有期契約の更新上限）を構造化したものである。形式の原本は `job-change-company-research` の `references/job-posting-format.md` にある。

| 状態 | 扱い |
|---|---|
| `work_location.unlimited` が真 | 転勤リスクとして `condition_fit` の evidence に含める。勤務地が入社時の1か所に留まる保証が無い旨を verdict に書く |
| `duties.unlimited` が真 | 職種転換リスクとして同様に扱う。現在の職務内容が続く保証が無い旨を verdict に書く |
| `contract_renewal_cap.stated` が真で上限がある | 有期契約の期間の上限として、雇用形態に関する条件の判定材料にする |
| いずれかが `null` | unknown のままにする。**記載を見つけられなかったことを、範囲が限定されている証拠として扱わない。** 確認事項を `overall.open_questions` へ入れる |

evidence は `{"source": "job_posting", "ref": "scope_of_change.work_location.unlimited", "note": "…"}` の形で書き、`ref` にはフィールドパスを、`note` には `quote`（求人票の記載の引用）を転記する。

`unlimited` が真であることは、それ自体では転勤・職種転換が起きる証拠ではなく、企業の裁量で起こしうるという事実である。verdict はこの区別を保った書き方にする。

`job_posting.json` の `schema_version` が `1.0` の場合、この節は適用しない。1.0 には `scope_of_change` が無く、取り込みの時点でこの3項目を見ていないためである。判定を変えず、`overall.open_questions` へ「求人票の取り込みが旧形式であり、業務・就業場所の変更の範囲を確認していない」と入れる。

### culture_fit（文化適合）

company_research の philosophy・workstyle・reputation トピックと、self_analysis の行動証拠・価値観を突き合わせる。

- **内省単独に重きを置かない。** self_analysis の主観的な自己申告だけで断定せず、self_analysis に記録された行動証拠（過去の具体的な行動・実績）との対応づけを優先する。
- 企業側の材料は、自社を良く見せる主張（レベルAでも confidence が high でないもの）を断定に使わず、事実（制度の有無・開示数値・認定）と分けて扱う。
- 口コミ由来（レベルC）は限定表現にとどめる。
- self_analysis が無い場合（inputs.self_analysis=false）は、行動証拠を欠くため score を高くせず、verdict にその旨を書くか null にする。
- evidence の source は主に `company_research`・`self_analysis`。

### compensation_fit（報酬適合）

希望年収と提示レンジ・業界平均を突き合わせる。

- job_posting の `salary`（提示レンジ）と、profile の `salary.desired`（希望年収）を突き合わせる。
- company_research の `company_metrics.compensation_level`（有価証券報告書の平均年間給与等）を参照点に加える。ただし全従業員平均であり職種別内訳を欠く限界を verdict または overall.open_questions に書く。
- 提示レンジ下限が希望を下回る場合は score を高くしない。上限との差、昇給余地の不確実性も勘案する。
- time_analysis.json に `comparison` があれば、実質時給の現職との差分（`comparison.delta.hourly_wage_binding_basis`・同 `labor_basis`）を verdict の根拠にする。額面年収の増加だけを根拠に score を高くしない。
- evidence の source は主に `job_posting`・`profile`・`company_research`・`time_analysis`。

### time_fit（時間適合）

time_analysis.json の年間拘束時間・実質時給と、must/want 条件（残業・通勤・労働時間に関するもの）を突き合わせる。

- time_analysis.json の `annual.binding_hours`（年間拘束時間）・`annual.labor_hours`（年間労働時間）・`effective_hourly_wage`（実質時給。拘束基準・労働基準）を主たる材料にする。
- 実質時給は、想定年収にレベル付きの根拠がある場合にのみ算出される（無ければ time_analysis 側で null）。null の場合は金額比較を断定に使わない。
- time_analysis の入力に統計フォールバックが使われた項目（`fallbacks_used`）は、実測でない旨を verdict に反映し、確度を上げすぎない。
- 残業・通勤・労働時間に関する must/want 条件との整合を見る。
- time_analysis.json に `comparison` があれば、年間拘束時間の現職との差分（`comparison.delta.annual_binding_hours`）を verdict の根拠にする。`comparison` が無い場合は、現職と比較できていない旨を verdict に書く。
- 通勤の負担を所要時間だけで表さない。commute.json の `transfers`（乗り換え回数）・`crowding`（混雑の程度）があれば verdict で触れる。長時間通勤は睡眠と運動を削るため、年収差で相殺できるとは限らない旨を、通勤片道が長い場合の verdict に書く（根拠は `references/fit-methods.md`）。
- evidence の source は主に `time_analysis`・`job_posting`。

## must_condition_results の判定

profile の必須条件（`conditions[level=must]` と `work_character_preferences[desire=must]`）の各条件を、job_posting・company_research の事実と突き合わせて `yes`・`no`・`unknown` で判定し、対応は `ref`（条件 id または特性 id）で1対1にする。

- 求人票・企業研究に明確な根拠がある場合のみ `yes`・`no` とし、その evidence を必ず添える。
- 根拠が見つからない条件は `unknown` とする（憶測で yes/no にしない）。`unknown` の条件は evidence を空にしてよい。
- **勤務地・リモートに関する必須条件は、`scope_of_change.work_location` も見て判定する。** 求人票の勤務地が条件を満たしていても、`work_location.unlimited` が真であれば、条件の充足は入社時点のものに留まる。この場合は `met` を `unknown` にせず、`yes` としたうえで evidence へ `scope_of_change.work_location.unlimited` を加え、`condition` の充足が就業場所の変更で失われうる旨を `note` に書く。求人票の勤務地が条件を満たさず、かつ `unlimited` が真の場合は `met=no` のままとする。職種・職務内容に関する必須条件と `duties.unlimited` の関係も同じ扱いとする。
- `scope_of_change` の該当項目が `null` の場合は、その項目を根拠に使わない。記載が見つからないことを、範囲が限定されている根拠にしない。
- `met=no` の条件が交渉・制度運用で解消しうる場合に限り `negotiable` を `true` にする。根拠（過去の交渉事例・制度の記載）を evidence へ添える。無根拠に `true` を付けない。
- 必須条件に `no` があるのに総合判定を `推奨` にすることは認めない（ERROR）。

## overall（総合判定）

7次元の score と must_condition_results を総合し、`推奨`・`条件付き推奨`・`非推奨`・`判断保留` のいずれかを付す。

| 状況 | 判定 |
|---|---|
| 必須条件をすべて満たし、主要次元の score が高い | `推奨` |
| 主要な適合はあるが未確認の条件が残る。または `met=no` の全件が `negotiable=true`（根拠付き） | `条件付き推奨` |
| 不一致が優勢。または交渉で解消できない必須条件が残る | `非推奨` |
| 入力が乏しく（inputs の多くが false）判断材料が不足する | `判断保留` |

- **経験が近いことだけを理由に推奨しない。** `experience_proximity` が高くても、`aspiration_alignment` または `work_character_fit` が低い場合は、その旨を rationale に明示し、`experience_proximity` の score の高さで打ち消さない。調整・管理・顧客折衝が中心の求人は、経験に近くても本人の希望と逆であることがある。
- `skill_gap` が `not_applicable_now` の場合は `推奨`・`条件付き推奨` にしない。
- rationale には、判定を分けた決め手と、条件付きの場合は解消すべき条件を書く。未確認の論点は `open_questions` に列挙する。求人票から判定できない作業特性（完了条件の明確さ・一人で完結しやすさ・結果を短期で確認できる度合い）は、必ず `open_questions` へ面接での確認事項として入れる。
- **直属上司の関与のしかたを必ず `open_questions` へ入れる。** 日本の従業員標本では上司との適合が定着と満足を左右するが、求人票と企業研究からは判定できない。8番目の次元を作らず、`culture_fit` の score にも織り込まず、面接での確認事項として立てる（根拠は `references/fit-methods.md`）。
- **判定がその時点の材料に基づくことを rationale に明記する。** 判定は現時点で得られている材料に基づくものであり、入社直後の満足の高さがそのまま持続するとは限らない。この注記を rationale の末尾へ置く（根拠は `references/fit-methods.md`）。
