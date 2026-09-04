# deep-trip-planning

**A Claude Skill that turns "a list of places" into an itinerary you can actually follow on the day.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Stars](https://img.shields.io/github/stars/Hizir-SamuelP/deep-trip-planning?style=social)](https://github.com/Hizir-SamuelP/deep-trip-planning/stargazers)
[![Agent Skills](https://img.shields.io/badge/Agent-Skills-6B4FBB)](https://code.claude.com/docs/en/skills)

[中文说明见下方 ↓](#中文说明)

---

## Why this exists

Most trip plans don't fail because the places were wrong. They fail for two reasons:

1. **Information was verified as "exists" but not as "open on that day, at that hour."** A map saying "Open now" tells you nothing about a Tuesday three months from now.
2. **Decisions had no thresholds.** Every option stays open, so on the day, tired and hungry, you're still deciding.

This skill encodes a workflow for closing both gaps. It was extracted from a real 8-day trip that went through the full cycle — planning, verification, budget, hotel comparison, a mid-planning airport change — and then generalized.

## What it actually does

Give Claude a trip to plan (or an existing plan to review) and it will:

- **Ask about your travel style first**, then turn your preferences into concrete numbers — queue-walkaway thresholds, how many reservations, how much buffer per day. It does not assume you want what the author wanted.
- **Verify to the day and hour** — day-of-week opening hours, public holidays and long weekends, policy changes taking effect mid-trip, whether the season you're chasing actually overlaps your dates.
- **Write transit segment by segment** from a fixed origin, with the traps that maps don't show you (express trains that skip your station, same-named stations that are physically separate, last buses that are earlier than you'd think).
- **Back-solve from golden hours** — if you must be somewhere at 09:00, work backwards through transit to a departure time. If it doesn't work, change the transport, don't accept "a bit later is fine."
- **Compare lodging on all-in prices**, apply a switching threshold, and then **explicitly close the decision** so you stop re-comparing.
- **Produce a countdown table** of every hard date: ticket release, free-cancellation deadlines, registration cutoffs.

## Benchmark

Scenarios and assertions live in `skills/deep-trip-planning/evals/evals.json`. Each case was run once with the skill and once without, then graded assertion by assertion:

| Case | With skill | Without | Δ |
|---|---|---|---|
| Japan multi-city, 4 cities in 10 days | 6/6 | 2/6 | +0.67 |
| Hokkaido winter self-drive | 6/7 | 3/7 | +0.43 |
| Kyoto with elderly parents (limits unstated) | 5/5 | 4/5 | +0.20 |
| Europe, 3 countries over New Year | 7/7 | 6/7 | +0.14 |
| Kyoto with elderly parents (limits stated) | 7/7 | 7/7 | 0.00 |
| Tokyo with a 2.5-year-old | 6/6 | 6/6 | 0.00 |

Read these honestly.

**Where the skill earns its place: multi-city and self-drive.** What it adds there is unglamorous — a per-city origin instead of one, luggage between checkout and check-in, drive-time margins, the return-the-car-to-boarding-pass back-solve, offline map coverage, and an overload judgment the user never asked for. The baseline lost those four multi-city points on discipline, not on knowledge.

**Where it adds nothing: elderly and toddler pacing.** The model already slows those itineraries down on its own — naps, closure days, turnaround points, downgrade ladders. Both cases tied, so no elderly- or child-specific content was added to the skill. Writing down what the model already does only costs context.

**Counting assertions hides severity.** The multi-country case differs by a single point, and that point matters more than the four in multi-city: the baseline told the user which consulate to apply to. The rule was right, the conclusion was not the plan's to make, and being wrong there costs the trip.

**A note for anyone writing evals against this skill:** do not write assertions of the form "does it know fact X." They do not discriminate, because the baseline searches too — it independently found the mainland-licence bar in Japan, the Kanazawa transfer that changed in 2024, and that Swiss VAT must be reclaimed at the Swiss border. What separates the runs is whether the disciplined work got done: margins, back-solves, per-fact sourcing, closed decisions.

Single runs, no standard deviation. The baseline was isolated by forbidding it to read this repository, which is an approximation, not a clean context.

## Install

**Claude Code / Cowork**

```bash
/plugin marketplace add Hizir-SamuelP/deep-trip-planning
/plugin install deep-trip-planning@hizir-skills
```

**Manual installation** (for environments that do not use the plugin system)

```bash
git clone https://github.com/Hizir-SamuelP/deep-trip-planning.git
mkdir -p ~/.claude/skills
cp -r deep-trip-planning/skills/deep-trip-planning ~/.claude/skills/
```

The marketplace is named `hizir-skills` and also carries [niuma-recheck](https://github.com/Hizir-SamuelP/niuma-recheck), so `/plugin install niuma-recheck@hizir-skills` works from the same marketplace.

That command copies the complete skill, including `scripts/`, `references/`, and `assets/`. Do not install only `SKILL.md`: the date checker is a hard safety requirement.

**English edition** — install the complete Chinese skill above as the shared script provider, then copy `skills/deep-trip-planning-en` beside it. The English edition deliberately shares the one checked date script; it does not carry an independently drifting copy.

**Claude.ai** — upload the entire `skills/deep-trip-planning/` folder, including `SKILL.md`, `scripts/`, `references/`, and `assets/`. If the interface cannot preserve that folder, do not ask it to calculate weekdays from memory; supply a verified calendar instead.

Then just ask naturally: *"Plan me 5 days in Lisbon in April"* or *"Look at this itinerary and tell me what's wrong with it."*

## Structure

```
skills/deep-trip-planning/
├── SKILL.md                        # Workflow + decision rules
├── scripts/trip_dates.py           # Network-verified weekdays, holidays, long weekends
├── evals/evals.json                # Regression and trigger cases
├── assets/planning-templates.md    # Output, daily, countdown, packing, emergency templates
└── references/
    ├── verification.md             # Day-of-week checks, holidays, policy changes,
    │                               #   seasonal windows, golden-hour back-solving
    ├── transit-and-maps.md         # Origin-based routing, 5 public-transit traps,
    │                               #   self-drive checklist, pass math, the 3-layer map method
    ├── lodging-decisions.md        # All-in price comparison, amenity-listing traps,
    │                               #   switching thresholds, closing the decision
    ├── budget-and-customs.md       # Budget structure, uncapped line items,
    │                               #   duty-free allowances, cash, baggage
    ├── entry-and-health.md         # Entry, health, passport, medication, insurance checks
    └── decision-thresholds.md      # Decision closures and source boundaries

skills/deep-trip-planning-en/       # English parallel skill; shares the script above
├── SKILL.md
├── assets/
├── evals/
└── references/
```

Progressive disclosure: `SKILL.md` loads when the skill triggers; reference files load only when that part of the workflow needs them.

## Design principles

**Preferences are dials, not defaults.** Early drafts baked in the author's own habits — "at most 1–2 nice meals per trip," "walk away after 20–30 minutes of queueing." That's one traveler's style presented as universal method. The skill now asks first and fills the numbers in from the answer.

**Explain why, don't command.** Instructions carry their reasoning so the model can generalize past the letter of the rule.

**Close decisions.** An open decision keeps costing the user attention. Writing "not comparing further" is part of the deliverable.

**Say what you couldn't confirm.** Marking "verify 7 days before departure, here's where" is more useful than false confidence.

## Contributing

Issues and PRs welcome — especially:

- **Region-specific traps** that generalize (transit quirks, booking-platform conventions, customs rules)
- **Travel styles this doesn't serve well** — it was extracted from an urban public-transit trip and generalized outward, so self-drive, multi-city, and family travel have had less real-world exercise
- **Failure reports**: a plan it produced that broke on the ground, and why

`skills/deep-trip-planning/evals/evals.json` holds the test prompts. If you change `SKILL.md`, re-run them.

## Related

- **[niuma-recheck](https://github.com/Hizir-SamuelP/niuma-recheck)** — the same idea pointed the other way. This skill exists so a plan doesn't fall apart on the ground; that one exists so a worker AI's "it's done" doesn't go unverified. Both are about closing the gap between *written down* and *actually true*.

## License

MIT — see [LICENSE](LICENSE).

---

<a name="中文说明"></a>

# 深度旅行攻略制作法（中文说明）

**一个 Claude Skill，把"列了一堆地方"变成"当天照着走就行"的攻略。**

## 为什么做这个

绝大多数攻略失败不是因为地方选错了，而是两件事：

1. **信息核到了"存在"，却没核到"那一天那个钟点"。** 地图上写"营业中"，和你三个月后周二几点去毫无关系。
2. **决定没有门槛。** 于是每个选项都还开着，到了现场又累又饿还得现想。

这个 skill 把堵住这两个口子的流程固化了下来。它是从一趟真实的 8 天行程里提炼的——规划、核验、预算、酒店比价、中途改机场，整个周期都走了一遍——然后再抽象成通用方法。

## 它实际会做什么

给 Claude 一趟要规划的行程（或一份要审查的现成行程），它会：

- **先问你的旅行风格**，再把偏好落成具体数字——排队多久就走、订几个餐厅、每天留多少缓冲。**它不会假设你想要的和作者想要的一样。**
- **核验精确到"哪一天几点"**——按星期几核营业时间、查法定假日和连假、查有没有制度在你旅行期间生效、查你追的那个季节窗口是否真的覆盖你的日期。
- **交通逐段写死**，从固定原点展开，并标出地图不会告诉你的坑（快车不停你住的那站、同名车站其实是两个站、末班车比想象中早）。
- **从黄金时段倒推**——必须 09:00 到，就一路倒推出发时间。**推不成立就换交通方式，而不是接受"晚一点也行"。**
- **住宿全部换算成含税终价再比**，套用换房门槛，然后**明确关闭这个决策**，让你不再反复比价。
- **产出倒计时表**，收进每一个硬日期：抢票开售、免费取消截止、注册办账号的截止。

## 实测对比

场景与 assertion 都在 `skills/deep-trip-planning/evals/evals.json`。每个用例用 skill 跑一遍、不用 skill 跑一遍，再逐条判定：

| 用例 | 用 skill | 不用 | Δ |
|---|---|---|---|
| 日本多城市·10 天四城 | 6/6 | 2/6 | +0.67 |
| 北海道冬季自驾 | 6/7 | 3/7 | +0.43 |
| 京都带老人（限制未言明） | 5/5 | 4/5 | +0.20 |
| 欧洲三国跨年 | 7/7 | 6/7 | +0.14 |
| 京都带老人（限制已言明） | 7/7 | 7/7 | 0.00 |
| 东京带 2 岁半小孩 | 6/6 | 6/6 | 0.00 |

这几个数字要照实读。

**skill 站得住的地方是多城市和自驾。** 它加的全是不起眼的东西：每座城各有自己的原点而不是套一个、退房到入住之间的行李、车程余量、还车到值机的倒推、离线地图覆盖，以及用户没问也要给的过载判断。基线在多城市丢的那四分，丢的是纪律不是知识。

**加不上分的地方是带老人和带娃。** 模型本来就会把这类行程放慢——午睡、闭馆日、折返点、降级方案，它自己都会想到。两题都打平，所以 skill 里**没有**增加任何老人或儿童专属内容。把模型已经会做的事再写一遍，只是消耗上下文。

**断言计数掩盖严重度。** 多国那题只差 1 分，而那 1 分比多城市的 4 分都重：基线直接告诉用户该向哪国领馆递签。规则讲对了，但这个结论不该由攻略来下，而递错国的代价是整趟作废。

**给要为这个 skill 写 eval 的人：** 不要写"它知不知道事实 X"这种断言，它不区分——基线也会联网搜，而且独立查出了中国驾照在日本不能驾驶、金泽换乘在 2024 年之后的变化、以及瑞士退税要在瑞士边境办。真正拉开差距的是**纪律有没有做完**：余量、倒推、逐条来源、关闭决策。

单次运行，无标准差。基线用"禁止读取本仓库"来近似隔离，不是完全干净的上下文。

## 安装

**Claude Code / Cowork**

```bash
/plugin marketplace add Hizir-SamuelP/deep-trip-planning
/plugin install deep-trip-planning@hizir-skills
```

**手动安装**（不使用插件系统的环境）

```bash
git clone https://github.com/Hizir-SamuelP/deep-trip-planning.git
mkdir -p ~/.claude/skills
cp -r deep-trip-planning/skills/deep-trip-planning ~/.claude/skills/
```

市场名叫 `hizir-skills`，里面还挂着 [niuma-recheck](https://github.com/Hizir-SamuelP/niuma-recheck)，所以 `/plugin install niuma-recheck@hizir-skills` 也能从同一个市场装。

这条命令会复制完整 skill，包括 `scripts/`、`references/` 和 `assets/`。不能只装 `SKILL.md`：日期脚本是硬性安全要求。

**英文版** —— 先按上面方式完整安装中文版（它提供唯一一份共享脚本），再把 `skills/deep-trip-planning-en` 复制到其同级目录。英文版刻意复用这份脚本，不保留会漂移的第二个副本。

**Claude.ai** —— 上传完整的 `skills/deep-trip-planning/` 目录，包括 `SKILL.md`、`scripts/`、`references/` 和 `assets/`。如果界面不能保留目录结构，就不要让模型心算星期几；改为提供已核验的日历。

然后正常提问就会触发：*"帮我规划 4 月里斯本 5 天"* 或 *"看看我这个行程有没有问题"*。

## 设计原则

**偏好是旋钮，不是默认值。** 早期版本把作者自己的习惯写死了——"全程只安排 1–2 顿正式好餐""排队超过 20–30 分钟就换店"。那是一个人的风格冒充普世方法。现在改成先问，再按答案填数字。

**解释为什么，而不是命令。** 每条指令都带上理由，模型才能举一反三，而不是死抠字面。

**要关闭决策。** 悬而未决的决定会一直消耗人的注意力。写下"不再比价"本身就是交付物的一部分。

**说清楚哪些没核实。** 标注"出发前 7 天去这里复核"，比假装确定有用得多。

## 欢迎贡献

特别欢迎这几类 issue 和 PR：

- **能泛化的地区性坑**（交通习惯、订房平台的表述陷阱、海关规则）
- **它服务得不够好的旅行方式**——这套方法是从城市 + 公共交通的行程里提炼出来再往外扩的。自驾、带老人、带娃、多城市、多国都已有 eval 实测（见「实测对比」）。**仍未检验的是：邮轮、长途巴士背包、无固定住宿的游牧式行程，以及南半球与热带雨季**
- **失败报告**：它做出来的攻略在现场哪里崩了、为什么

`skills/deep-trip-planning/evals/evals.json` 是测试用例。改了 `SKILL.md` 记得重跑一遍。

## 相关

- **[niuma-recheck](https://github.com/Hizir-SamuelP/niuma-recheck)** —— 同一套思路的另一个方向。这个 skill 防的是「攻略写完了、到现场还得重查」；那个防的是「AI 说做完了、其实没有」。都是在堵「写下来」和「真的成立」之间的那道缝。

## 许可

MIT，见 [LICENSE](LICENSE)。
