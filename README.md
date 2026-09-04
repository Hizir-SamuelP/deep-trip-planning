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

Tested against a no-skill baseline on 3 scenarios (open-ended planning, auditing an existing plan, a single hotel/transit question):

| | With skill | Baseline |
|---|---|---|
| Assertions passed | **25/25** | 19/25 |
| Avg tokens | 132.9k | 75.8k |
| Avg time | 690s | 377s |

The gap is **entirely structural habits, not research ability**. On the "audit this existing plan" scenario both tied 9/9 — when the prompt names what to check, the baseline finds it. The skill's value shows up in open-ended planning, where the baseline reliably omitted: per-day cut priorities, per-day weather fallbacks, dated countdowns (it wrote "2–3 weeks ahead" instead), and budget tiers for the one uncapped line item.

The sharpest single difference was **decision closure**: given a hotel A/B question, the baseline ended with "keep watching, switch if you find something better" — handing an open-ended task back to the user. The skill cites a threshold, back-solves the price at which switching would be worth it, and writes "this decision is now closed."

Cost: roughly +75% tokens and time. For a document you'll use for an entire trip, that trade is usually worth it.

## Install

**Claude Code / Cowork**

```bash
git clone https://github.com/Hizir-SamuelP/deep-trip-planning.git
mkdir -p ~/.claude/skills
cp -r deep-trip-planning/skills/deep-trip-planning ~/.claude/skills/
```

**Claude.ai** — upload `skills/deep-trip-planning/SKILL.md` and the `references/` folder as project files.

Then just ask naturally: *"Plan me 5 days in Lisbon in April"* or *"Look at this itinerary and tell me what's wrong with it."*

## Structure

```
skills/deep-trip-planning/
├── SKILL.md                        # 8-step workflow + decision rules (~215 lines)
└── references/
    ├── verification.md             # Day-of-week checks, holidays, policy changes,
    │                               #   seasonal windows, golden-hour back-solving
    ├── transit-and-maps.md         # Origin-based routing, 5 public-transit traps,
    │                               #   self-drive checklist, pass math, the 3-layer map method
    ├── lodging-decisions.md        # All-in price comparison, amenity-listing traps,
    │                               #   switching thresholds, closing the decision
    └── budget-and-customs.md       # Budget structure, uncapped line items,
                                    #   duty-free allowances, cash, baggage
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

`evals/evals.json` holds the test prompts. If you change `SKILL.md`, re-run them.

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

用 3 个场景（开放式规划、审查现成行程、单点酒店/交通问题）和"不带 skill"做了对照：

| | 带 skill | 基线 |
|---|---|---|
| 断言通过 | **25/25** | 19/25 |
| 平均 token | 132.9k | 75.8k |
| 平均耗时 | 690 秒 | 377 秒 |

**差距 100% 来自结构性习惯，不是查资料能力。** "审查现成行程"那题两边打平 9/9——当提示词本身点名了要查什么，基线也能查到。skill 的价值集中在开放式规划：基线稳定地漏掉每日删减层级、每日天气预案、带具体日期的倒计时（它写的是"提前 2–3 周"）、以及唯一无上限项的预算档位。

**最锋利的差异是"关闭决策"**：同一个酒店 A/B 问题，基线以"继续观察，找到更好的再换"收尾——把开放式任务丢回给用户；带 skill 的引用门槛、反推出对方要卖到多少才值得换、并写下"这个决策现在关闭"。

代价：多花约 75% 的 token 和时间。对一份要用一整趟旅行的文档来说，这个交换通常划算。

## 安装

**Claude Code / Cowork**

```bash
git clone https://github.com/Hizir-SamuelP/deep-trip-planning.git
mkdir -p ~/.claude/skills
cp -r deep-trip-planning/skills/deep-trip-planning ~/.claude/skills/
```

**Claude.ai** —— 把 `skills/deep-trip-planning/SKILL.md` 和 `references/` 目录作为项目文件上传。

然后正常提问就会触发：*"帮我规划 4 月里斯本 5 天"* 或 *"看看我这个行程有没有问题"*。

## 设计原则

**偏好是旋钮，不是默认值。** 早期版本把作者自己的习惯写死了——"全程只安排 1–2 顿正式好餐""排队超过 20–30 分钟就换店"。那是一个人的风格冒充普世方法。现在改成先问，再按答案填数字。

**解释为什么，而不是命令。** 每条指令都带上理由，模型才能举一反三，而不是死抠字面。

**要关闭决策。** 悬而未决的决定会一直消耗人的注意力。写下"不再比价"本身就是交付物的一部分。

**说清楚哪些没核实。** 标注"出发前 7 天去这里复核"，比假装确定有用得多。

## 欢迎贡献

特别欢迎这几类 issue 和 PR：

- **能泛化的地区性坑**（交通习惯、订房平台的表述陷阱、海关规则）
- **它服务得不够好的旅行方式**——这套方法是从城市 + 公共交通的行程里提炼出来再往外扩的，自驾、多城市、带娃带老人的实战检验还不够
- **失败报告**：它做出来的攻略在现场哪里崩了、为什么

`evals/evals.json` 是测试用例。改了 `SKILL.md` 记得重跑一遍。

## 相关

- **[niuma-recheck](https://github.com/Hizir-SamuelP/niuma-recheck)** —— 同一套思路的另一个方向。这个 skill 防的是「攻略写完了、到现场还得重查」；那个防的是「AI 说做完了、其实没有」。都是在堵「写下来」和「真的成立」之间的那道缝。

## 许可

MIT，见 [LICENSE](LICENSE)。
