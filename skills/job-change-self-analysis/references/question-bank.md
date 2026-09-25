# Structured question set (question-bank)

<!-- textlint-disable jtf-style/4.3.2.大かっこ［］ -->
<!-- The [E1] form in the body is the notation for a source id. This file disables that rule to keep the half-width square brackets. -->

This is the canonical definition of the fixed, structured questions used in Steps 1-3.5 of the job-change-self-analysis skill. Unlimited repetition of "why" is forbidden, and probing further always maps to a behaviour or a fact (an episode) (the grounds are the rumination-prevention operating rules in self-analysis-methods.md).

## Rules for use

- Questions run mainly through AskUserQuestion's choice form. Each AskUserQuestion call carries at most 4 questions, and each question carries at most 4 options. Free text is limited to an item the choice form cannot handle, such as a concrete value in an episode: a time, a situation, or a number.
- Probing further never leads the user into emotional rumination; the question always points to a fact (when, in what situation, what did the person do). An affective forecast ("will changing jobs bring happiness?") never grounds a firm conclusion.
- The frameworks below (Schein's anchor categories, the CCI questions, and the like) are used as a prompt for introspection. A diagnostic result is never treated as a settled judgment.
- The item text of a copyrighted psychological scale (CAAS, VPI, CliftonStrengths, and the like) is never reproduced or asked as it stands. The description stays at the name of a dimension or a framework. The list of instruments that may and may not be asked is in `personality-guide.md`. MBTI, 16Personalities, employer-side aptitude tests, and any company's free diagnostic tool are never offered.

## Step 1: Taking stock of behavioural episodes (STAR material)

Show the user `career_history` and `achievements` from profile.json as material for the options, and structure the answer into STAR (Situation / Task / Action / Result). Use the idea of a motivation graph (arranging events along a timeline and attaching the rise and fall of feelings) as an optional aid.

Prompting questions:

- これまでで、手応えを感じた仕事・工夫して乗り越えた場面はどれか (Which piece of work gave you a sense of accomplishment, or which situation did you get through with some ingenuity?). Present options drawn from profile.json's `achievements`.
- その場面の状況（Situation）はどうだったか。何を任され（Task）、実際に何をしたか（Action）、どうなったか（Result）。(What was the situation? What were you tasked with, what did you actually do, and what happened?)
- その結果を数値で表せるか（Result の metric）。表せない場合は `null` でよい。(Can the result be expressed as a number — the metric for Result? When it cannot, `null` is fine.)
- その進め方は、会社や環境が変わっても機能したか（reproducibility）。別の場面で同じ進め方が効いた例はあるか。(Did that approach work even when the company or environment changed — reproducibility? Is there an example where the same approach worked in a different situation?)
- そのとき、どんな動機・感情で取り組んでいたか（emotion_note。当時の記録であり、将来の予測ではない）。(What motivation or feeling were you working with at the time — emotion_note, a record from that time, and never a forecast of the future.)

Among the STAR elements, Situation, Action, and Result are required (an episode does not stand without them). Probing further points to 「どの場面で・何をしたか」 (in what situation, and what did you do).

## Step 2: Incorporating feedback from others (evaluation by others, the Johari window)

Evaluation by others has higher predictive validity than self-evaluation (self-analysis-methods.md). Collect, as a record, points raised in a past performance review and things others have said, and check them against self-perception (the Johari window: the agreement and disagreement between what the self notices and what others notice).

Prompting questions:

- 過去の評価面談・1on1で、上司や同僚から具体的に指摘されたことは何か (In a past performance review or a 1-on-1, what did a manager or colleague specifically point out to you?). Present `source_type` in choice form: 上司 (manager) / 同僚 (colleague) / 部下 (subordinate) / 顧客 (client) / 友人・家族 (friend or family) / 評価面談 (performance review).
- それはどの場面・どの仕事に対する指摘だったか（linked_episode_ids へ対応づける）。(Which situation, or which piece of work, was that comment about?) Map it with `linked_episode_ids`.
- 自分では強みと考えていなかったものの、他者から評価された点はあるか（ジョハリの窓の「自分は気づかないが他者は気づく」領域）。(Is there a point you underestimated yourself, though others valued it?) — the Johari window's region where others notice what you overlook.

Record feedback with a task-oriented focus. Avoid a judgment of character such as "you are this kind of person," and record it rephrased into the form "which action led to which result." When feedback from others cannot be obtained on the spot, proceed with the deliverable left in a WARN state. Show the user that collecting feedback from others remains an open task. Use `assets/feedback_request_template.md` for the request text to others.

## Step 3: Structured questions on interests, values, and career adaptability

### Interests (the RIASEC framework)

- 業務のうち、時間を忘れて取り組めるのはどの種類の活動か (Among your tasks, which kind of activity can you lose yourself in?). Present the six RIASEC domains as options: Realistic 現場・技術 (hands-on / technical), Investigative 調査・分析 (research / analysis), Artistic 創作・表現 (creation / expression), Social 支援・教育 (support / education), Enterprising 企画・推進 (planning / driving), Conventional 管理・整備 (administration / organising).
- その領域に当てはまる具体的なテーマ・題材は何か（concrete_topics）。(What concrete theme or subject matter fits that domain? — `concrete_topics`.)

RIASEC is used as the axis names of the interests framework. A diagnostic tool's result is never treated as a settled judgment.

### Values (mapped to behaviour)

- 仕事で判断に迷ったとき、最後に優先したものは何か。それはどのエピソードで表れたか（evidence_episode_ids へ対応づける）。(When you were torn over a decision at work, what did you end up prioritising, and in which episode did that show up?) Map it with `evidence_episode_ids`.
- 譲れないと感じた場面はどこか。何を守ろうとしたか。(In what situation did you feel you could not give ground, and what were you trying to protect?)

Values are put into words through introspection. Introspection alone never grounds the weight given to a value; back it up by mapping it to an episode.

### The four dimensions of career adaptability

Only the framework of dimension names is used (no scale item is reproduced). For each dimension, collect a self-description (`self_note`) and a supporting episode (`evidence_episode_ids`).

- concern（関心）: 将来のキャリアを見据えて、早めに準備・行動した場面はあるか (Is there a situation where you looked ahead to your future career and prepared or acted early)?
- control（統制）: 外部要因に流されず、自分の選択で状況を方向づけた場面はあるか (Is there a situation where you steered things by your own choice, holding your course against outside factors)?
- curiosity（好奇心）: 未知の分野・可能性を自ら調べ、試した場面はあるか (Is there a situation where you looked into and tried an unfamiliar field or possibility on your own)?
- confidence（自信）: 難所を、自分の手順・経験で乗り越えられた場面はあるか (Is there a situation where you got through a difficulty using your own approach or experience)?

## Step 3.5: Self-report of personality and behavioural tendencies (forced choice)

The canonical definition is in `personality-guide.md`. Ask a behaviour-grounded forced choice, and each time an item is answered, have the person name one episode where that tendency showed up (choose from the existing `behavioral_episodes`, and when none fits, ask for one episode in STAR form on the spot). When none comes up, leave `linked_episode_ids` empty. When feedback from others describes the same tendency, map it with `feedback_ids`. Ask about the 15 constructs across 16 questions (`stress_trigger` alone gets 2 questions), split into 4 AskUserQuestion calls of 4 questions each. Never layer an additional "why" on top.

The four options take the same form for every item. The first and second options are two paired behaviours, the third is "it depends on the situation," and the fourth is "neither applies." Record the four presented options in `personality.markers[].options` exactly as they read. When the person picks one of the first four directly, write that option's sentence as it stands in `response`. When the person picks the fourth and writes a close behaviour freely under Other, omit `options`, put that free text in `response`, and write the mismatch with the options in `note`.

| `construct` | `header` | `question` | Option 1 | Option 2 |
|---|---|---|---|---|
| `planning_style` | Approach (進め方) | 新しい仕事に着手するとき、ご自身に近いのはどちらですか。(When starting new work, which is closer to you?) | **段取りを先に固める** — 手順と順序を書き出してから着手します。(Settle the plan first — write out the steps and order before starting.) | **着手して組み替える** — まず動かし、状況に合わせて順序を変えます。(Start and rearrange — get moving first, then change the order to fit the situation.) |
| `conscientiousness` | Seeing it through (やり切り方) | 締切が近いとき、ご自身に近いのはどちらですか。(When a deadline is close, which is closer to you?) | **残りを書き出して片づける** — 残作業を一覧にし、上から順に終わらせます。(List the rest and clear it — list the remaining work and finish it from the top.) | **要点に絞って仕上げる** — 影響の大きい部分を選び、そこに時間を集めます。(Narrow to what matters and finish it — pick the highest-impact part and put your time there.) |
| `decision_style` | Decision style (判断の型) | 方針を決めるとき、ご自身に近いのはどちらですか。(When settling a direction, which is closer to you?) | **数字を先に置く** — 計測や集計の結果を見てから決めます。(Numbers first — decide after looking at measured or aggregated results.) | **仮説を先に置く** — まず仮説を立て、動かしながら確かめます。(Hypothesis first — form a hypothesis, then test it while moving.) |
| `emotional_stability` | Under strain (負荷の下で) | 障害や苦情が重なった場面で、ご自身に近いのはどちらですか。(When failures or complaints pile up, which is closer to you?) | **手順に戻る** — 決めてある手順に沿って一つずつ処理します。(Return to the procedure — handle things one by one, along a set procedure.) | **状況を組み替える** — その場で優先順位を組み替えて対処します。(Rearrange the situation — reorder priorities on the spot and deal with it.) |
| `stress_trigger` | Source of strain (消耗の要因) | 最も消耗するのはどの場面ですか。(Which situation drains you most?) | **曖昧なまま進む場面** — 何を求められているかが決まらないまま進みます。(A situation that proceeds without clarity — moving ahead without a settled sense of what is asked.) | **締切に追われる場面** — 期限が重なり、時間が足りません。(A situation chased by deadlines — deadlines overlap and time runs short.) |
| `stress_trigger` | Source of strain, second question (消耗の要因（2）) | 同じく、消耗するのはどちらの場面ですか。(Likewise, which situation drains you?) | **人との摩擦がある場面** — 意見が食い違い、調整が続きます。(A situation with friction with people — opinions clash and adjustment continues.) | **同じ作業が続く場面** — 変化のない作業が長く続きます。(A situation where the same work continues — unchanging work goes on for a long time.) |
| `recovery_style` | Recovery style (回復の型) | 消耗したあと、ご自身に近いのはどちらですか。(After being drained, which is closer to you?) | **一人で整える** — 一人の時間を取って立て直します。(Settle down alone — take time alone to recover.) | **人と話して整える** — 誰かと話すことで立て直します。(Settle down by talking — recover by talking with someone.) |
| `collaboration_style` | Collaboration style (協働の型) | 力を発揮しやすいのはどちらですか。(Which lets you perform better?) | **単独で集中する** — 一人で集中する時間が長いほど進みます。(Concentrate alone — the more time spent concentrating alone, the more progress.) | **対話で進める** — 相談や議論を挟むほど進みます。(Move forward through dialogue — the more discussion, the more progress.) |
| `extraversion` | Engaging with people (人との関わり) | 初めての相手が多い場に出たあと、ご自身に近いのはどちらですか。(After being in a setting full of people you're meeting for the first time, which is closer to you?) | **勢いがつく** — 人と話したあとのほうが動けます。(It energises you — you can move better after talking with people.) | **一度休む** — 人と話したあとは、一度静かな時間が要ります。(You need a rest — after talking with people, you need a quiet moment.) |
| `agreeableness` | A situation of conflict (対立の場面) | 意見が食い違ったとき、ご自身に近いのはどちらですか。(When opinions clash, which is closer to you?) | **先に相手の案を通す** — 相手の案を試してから自分の案を出します。(Let the other person's proposal go first — try their proposal before offering your own.) | **先に自分の案を通す** — 自分の案の根拠を示してから相手の案を聞きます。(Put your own proposal first — show its grounds before hearing theirs.) |
| `openness` | An unfamiliar method (未知の方法) | 使ったことのない方法を勧められたとき、ご自身に近いのはどちらですか。(When recommended a method you've never used, which is closer to you?) | **まず試す** — 小さく試してから判断します。(Try it first — try it on a small scale, then judge.) | **実績を先に見る** — 他所での実績を確かめてから判断します。(Check the track record first — confirm results elsewhere before judging.) |
| `change_orientation` | Orientation toward change (変化への向き) | 環境として力を発揮しやすいのはどちらですか。(As an environment, which lets you perform better?) | **安定した環境** — 役割と手順が決まっている環境です。(A stable environment — one where roles and procedures are set.) | **変化の多い環境** — 役割と手順が変わり続ける環境です。(A highly changeable environment — one where roles and procedures keep changing.) |
| `feedback_timing` | Interval for evaluation (評価の間隔) | 結果の知り方として、ご自身に近いのはどちらですか。(In how you learn results, which is closer to you?) | **短い間隔で知る** — 日々の結果をすぐ確かめたいほうです。(Learn at short intervals — you want to check daily results right away.) | **節目でまとめて知る** — 区切りでまとめて確かめたいほうです。(Learn gathered at milestones — you want to check things gathered at a milestone.) |
| `grit` | A long-term goal (長期の目標) | 数年がかりの目標について、ご自身に近いのはどちらですか。(About a goal that takes several years, which is closer to you?) | **同じ目標を続ける** — 一度決めた目標を、途中で変えずに続けます。(Keep the same goal — continue a goal you set, without changing it partway.) | **目標を更新する** — 状況に合わせて目標そのものを見直します。(Update the goal — revisit the goal itself to fit the situation.) |
| `honesty_humility` | Attribution of results (成果の帰属) | 成果を報告するとき、ご自身に近いのはどちらですか。(When reporting a result, which is closer to you?) | **関わった人を先に挙げる** — 誰が何をしたかを先に述べます。(Name the people involved first — state who did what, first.) | **自分の判断を先に挙げる** — 自分が何を決めたかを先に述べます。(Name your own judgment first — state what you decided, first.) |
| `self_efficacy` | Expectation toward a difficulty (難所への見込み) | 経験のない難所に当たったとき、ご自身に近いのはどちらですか。(When facing a difficulty you have no experience with, which is closer to you?) | **自分の手順で越えられると見込む** — これまでの手順を当てはめれば進めると考えます。(Expect to get through it your own way — you think applying your existing approach will work.) | **先に詳しい人を探す** — 経験者を見つけて進め方を確かめます。(Look for an expert first — find someone experienced and confirm how to proceed.) |

The wording of the common options 3 and 4 is as follows.

| Option | Wording |
|---|---|
| Option 3 | **場面による** — どちらも同じくらいあります。(It depends on the situation — both apply about equally.) |
| Option 4 | **どちらも当てはまらない** — Other で近い行動をお書きください。(Neither applies — please write the closest behaviour under Other.) |

The question placed after each item (free text, once): 「その傾向が表れた場面を、これまでに挙げたエピソードから1つ選ぶとどれですか。無ければ、新しく1つ教えてください」(Which one of the episodes you've already named shows this tendency? If none does, tell me a new one.)

The result of a self-report is never returned as the name of a type or category. In the deliverable, `personality.presentation` writes the mapping between the chosen behaviour and the episode as a descriptive passage ("How to write the result" in `personality-guide.md`).

### Candidate names for a strength

This is vocabulary that may be shown as a candidate when a strength is hard to put into words. Once the episode and feedback from others are both in hand, have the person choose a name that fits the two of them. A strength is never built from the name alone.

- The 18 names GOOD POINT diagnosis publishes (親密性 intimacy, 社交性 sociability, 受容力 acceptance, 現実志向 realism, 慎重性 carefulness, 冷静沈着 calm composure, 柔軟性 flexibility, 俊敏性 agility, 継続力 persistence, 挑戦心 a spirit for challenge, 自立 independence, 感受性 sensitivity, 高揚性 exuberance, 悠然 composure, 自己信頼 self-trust, バランス balance, 独創性 originality, 決断力 decisiveness). Only the names are used; the diagnosis's items and scoring are not used (`personality-guide.md`).
- The vocabulary of VIA's 24 strengths (within the scope of the public research version).

### Schein's career anchors (a prompt; never settle a label)

Schein's eight categories — 専門・職能別コンピタンス (technical/functional competence) / 全般管理コンピタンス (general managerial competence) / 自律・独立 (autonomy/independence) / 保障・安定 (security/stability) / 起業家的創造性 (entrepreneurial creativity) / 奉仕・社会貢献 (service/dedication to a cause) / 純粋な挑戦 (pure challenge) / 生活様式 (lifestyle) — may be presented as a prompt for introspection on values. Because their construct validity is weak (self-analysis-methods.md), the result is never treated as a settled judgment such as "this is your anchor." Its use is limited to using the category name as a cue for checking whether a matching behavioural episode exists.

### The five CCI-style questions (material for the career narrative)

In the Career Construction Interview (the framework of Savickas's career construction theory [E43]), the interviewer and the client elicit a life theme across 5-7 questions, and jointly build a consistent career story. The following five questions are used to collect material for the narrative (`career_narrative`). The five questions are written in this skill's own words, carrying the intent of each question in that framework (the terms of use are in the instruments table in `personality-guide.md`).

1. 幼少期に憧れた人物は誰か。その人物のどこに引かれたか (Who did you admire as a child, and what drew you to that person?) — a role model is a clue to the ideal self.
2. よく読む雑誌・見る番組・好きなサイトは何か (What magazine do you often read, what show do you watch, what site do you like?) — a clue to the environment your interest turns toward.
3. 好きな物語（本・映画）は何か。その筋書きのどこが好きか (What story — a book or a film — do you like, and what part of its plot do you like?) — a clue to the pattern of your own story.
4. 座右の銘・好きな言葉は何か (What is your motto, or a phrase you like?) — a clue to the advice you give yourself.
5. 幼少期の最も古い記憶は何か (What is your earliest childhood memory?) — a clue to the origin of your present interest.

These answers are material for putting the life theme, the turning points, and the consistent motivation into words. They are never treated as a diagnostic result, and connect to the structure in narrative-guide.md.

The detail of the citation ([E43], including its DOI and URL) is in the sources list of self-analysis-methods.md and narrative-guide.md.
