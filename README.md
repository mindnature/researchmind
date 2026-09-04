# ResearchMind

## 通用型科研思维蒸馏器

> 输入一个学者名字，蒸馏他的科研判断力。真正调用时，还要先判断：这位学者这次到底该不该开口。

[![CI](https://github.com/mindnature/researchmind/actions/workflows/ci.yml/badge.svg)](https://github.com/mindnature/researchmind/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/License-Apache--2.0-blue.svg)](LICENSE)
![Version](https://img.shields.io/badge/ResearchMind-v0.6-6f42c1)

论文告诉我们一位学者最后发现了什么。

ResearchMind 想进一步追问：

> **他当时为什么会这样判断？**

面对一个陌生问题，他先看什么？多个解释同时存在时，他怎么排除？什么证据会让他继续坚持？什么异常会迫使他修改模型？一个方向什么时候值得长期投入，什么时候应该停止？

ResearchMind 从论文、手稿、科研笔记、通信、访谈、口述史、研究失败、理论转向和团队记录中重建 **Research Decision Episodes**，再蒸馏可回源的 **Research Heuristics**，最终生成可调用的 **Research Advisor Skill**。

它不做“大师数字分身”，也不保证每个大师对每个问题都有价值。

> **一个真正可信的专家顾问，必须知道什么时候自己的经验根本不该用。**

[快速开始](#快速开始) · [为什么 v06 很重要](#为什么-v06-很重要) · [ScholarTask Fit](#scholartask-fit) · [工作原理](#工作原理) · [安装](#安装) · [CLI](#cli)

---

## 快速开始

安装后，只需要告诉 Agent：

```text
蒸馏 Geoffrey Hinton
```

或者：

```text
蒸馏姚期智，重点研究他的科研选题、问题形式化和研究方向判断。
```

ResearchMind 会自动进入：

```text
学者身份确认
        ↓
科研资料发现
        ↓
Research Episode 重建
        ↓
成功 × 失败 × 转向 × 边界案例
        ↓
Research Heuristic 蒸馏
        ↓
Scholar Specificity
        ↓
Composite Heuristic Audit
        ↓
生成 Research Advisor
```

之后可以直接调用：

```text
用姚期智科研顾问分析我的大模型安全选题。
```

但 v0.6 不会因为你点名姚期智，就强迫姚期智一定给出一个“独特框架”。

真正调用前还会先做：

```text
当前任务
   ↓
Scholar–Task Fit
   ↓
active / experimental / abstain
```

---

## 为什么 v0.6 很重要

真实测试暴露了一个比幻觉更隐蔽的问题。

假设我们蒸馏了一位养老金研究专家，然后让他评审“低空物流运营”项目。

一个普通 AI 很容易这样做：

```text
专家谈过“参加”
专家谈过“集中管理”
专家谈过“覆盖和成本”
        ↓
AI 拼成
“参加强度 × 协调集中度”框架
        ↓
再把它强行迁移到低空物流
```

每个零件可能都是真的。

但组合后的框架未必真的是这位专家使用过的科研判断结构。

更危险的是：模型会因为用户明确说“用这位专家评”，就认为自己必须找到一个办法把专家“用上”。

ResearchMind 把这两个问题分别定义为：

> **Composite Heuristic Fabrication** — 组合式启发式伪造

以及：

> **Forced Lens Activation** — 强制透镜激活

v0.6 专门解决这两个问题。

---

## Scholar–Task Fit

“这个学者拥有一个强 heuristic”与“这个 heuristic 适合你的任务”是两回事。

ResearchMind v0.6 在每次 Scholar Advisor 真正回答问题前，先评估四个维度：

| 维度 | 判断什么 |
|---|---|
| Domain Fit | 学者原领域与目标任务有多接近 |
| Decision-Structure Fit | 两个问题的决策结构是否真正相似 |
| Evidence Fit | 当前候选透镜有没有足够 Episode 和来源支撑 |
| Added-Value Fit | 相比 Generic ResearchMind，这位学者到底多增加了什么 |

系统输出三种结果。

### `active`

允许使用强 Scholar Lens，但仍需通过 provenance 和 transfer 检查。

### `experimental`

只能生成诊断问题、候选假设和备选视角。

不能因为一个漂亮类比，就直接改写你的理论框架、识别策略或研究设计。

### `abstain`

专家不参与。

系统继续用 `DOMAIN_BASELINE` 做正常专业审查，并明确告诉你：

> 当前任务与该学者公开科研判断结构的匹配度不足。

这不是失败。

这是 ResearchMind 想要的能力。

---

## 中等迁移不再等于“可以给建议”

v0.6 把 Transfer Confidence 对应动作写死：

```text
high    → recommendation allowed
medium  → diagnostic only
low     → question generation only
reject  → abstain
```

因此一个跨学科迁移即使被判为 `medium`，也不能再出现这种行为：

> 一边说“迁移置信度中等”，一边用大师框架重构整个申报书。

---

## Active Lens Provenance Packet

任何要作为强 Scholar Lens 使用的 heuristic，都必须能回答：

```text
heuristic_id 是什么？
支持它的是哪几个 Research Episode？
学者当时实际做了什么决策？
对应哪些原始来源？
source locator 在哪里？
与 Generic ResearchMind 相比增加了什么？
组合式 heuristic 有没有真实联合证据？
```

ResearchMind 会为强透镜生成 `lens_provenance/` 证据包。

如果证据包不完整，自动降级到 experimental。

---

## Composite Heuristic Fabrication Check

几个真实概念不能自动拼成一个“大师框架”。

例如：

```text
Source A → 学者谈 A
Source B → 学者谈 B
Source C → 学者谈 C
```

不能直接推导：

```text
A × B → C
= 该学者的核心科研框架
```

除非有 Episode 或来源能证明，这个组合结构本身确实在学者的研究决策中出现过。

否则只允许：

```text
experimental_lens
```

而不是 active lens。

---

## Swap-Scholar Evaluation

ResearchMind v0.6 还加入了一个反作弊测试。

把同一个科研问题分别交给：

```text
Generic ResearchMind
Scholar A
Scholar B
Scholar C
```

然后比较：

- active lens 数量；
- scholar-added delta；
- 最终推荐框架；
- 是否知道 abstain。

如果换谁都能流畅生成一套“大师独特二维框架”，说明系统不是在蒸馏专家，而是在根据名字现场做创造性类比。

真正好的 Scholar Advisor 应该表现出明显的能力密度差异。

---

## 三层科研顾问

ResearchMind 的输出继续保持物理隔离。

### `DOMAIN_BASELINE`

目标领域自己的专业规范。

与大师无关，并尽可能有独立方法学/官方来源。

### `SCHOLAR_LENS`

只有同时通过 Scholar Specificity、Composition Audit、Scholar–Task Fit、Provenance 和 Transfer 的透镜，才允许给强建议。

### `TRANSFER_INFERENCE`

明确告诉你：

- 哪些结构相似；
- 哪些约束被保留；
- 哪些假设已经断裂；
- 这次迁移只能提问、诊断，还是允许形成建议。

---

## ResearchMind 蒸馏什么？

它重点研究：

1. 问题怎么选；
2. 问题怎么重新定义；
3. 假设怎么产生和排除；
4. 异常结果怎么处理；
5. 什么时候坚持、转向或停止；
6. 一种科研方法什么时候会失效。

它不只研究成功，也主动寻找失败、争议、放弃方向和理论转向。

---

## Distillation Grade

不是所有学者都留下了相同深度的科研档案。

- `A_archival`：档案级
- `B_process_informed`：过程证据级
- `C_retrospective`：公开回顾级
- `D_publication_based`：成果轨迹级

ResearchMind 宁可降低蒸馏等级，也不为了“像大师”补写不存在的微观心理过程。

---

## Adaptive Distillation

质量检查继续采用：

```text
ERROR   → 阻断
WARNING → 允许继续但降低能力
INFO    → 展示状态
```

所以输入一个资料稀缺的当代学者，系统仍然可以跑到底，只是最终可能得到：

```text
Active Lens: 0
Experimental Lens: 2
Generic Absorbed: 4
```

这比硬造 6 条“大师方法”更有价值。

---

## 工作原理

```text
01 Scholar Identity
02 Source Discovery
03 Evidence Registry
04 Research Episode Extraction
05 Temporal Firewall
06 Team Attribution
07 Contrastive Distillation
08 Heuristic Synthesis
09 Scholar Specificity Gate
10 Composite Heuristic Audit
11 Adaptive Routing
12 Build Research Advisor
13 Scholar–Task Fit
14 Active Lens Provenance
15 Transfer Validator
16 Three-Layer Answer / Lens Abstention
```

---

## 安装

在支持 Agent Skills 的 AI Agent 中直接告诉它：

```text
帮我安装这个 Skill：
https://github.com/mindnature/researchmind
```

然后：

```text
蒸馏 Geoffrey Hinton
```

即可启动。

---

## CLI

初始化自动蒸馏：

```bash
python scripts/researchmind.py auto-distill "Geoffrey Hinton" --mode fast-auto
```

质量与路由：

```bash
python scripts/researchmind.py quality-report --scholar pauling
python scripts/researchmind.py route-heuristics --scholar pauling
```

任务适配：

```bash
python scripts/researchmind.py task-fit --input task-fit.json
```

查看强透镜证据：

```bash
python scripts/researchmind.py lens-provenance --scholar <slug> --heuristic <id>
```

查看迁移动作：

```bash
python scripts/researchmind.py transfer-action medium
```

Swap-Scholar 测试：

```bash
python scripts/researchmind.py swap-scholar-eval --input swap-results.json
```

---

## ResearchMind 不是什么

它不是：

- 名人聊天机器人；
- 大师角色扮演器；
- 论文摘要器；
- “换一个专家名字也能说同样话”的模板评审 Agent。

ResearchMind 想做的是：

> 从真实科研历史中蒸馏可检查的判断结构，并且知道这些判断什么时候可以迁移，什么时候只能启发，什么时候应该完全保持沉默。

---

## 项目状态

`v0.6 — Scholar–Task Fit & Lens Abstention`

当前最重要的成功标准不再是：

> “这个专家能给多少建议？”

而是：

> **当这个专家真的不适合当前问题时，ResearchMind 能不能识别出来，并拒绝借大师名字制造价值。**

---

> 论文保存科研结果。  
> ResearchMind 试图保存科研判断，也保存这些判断的适用边界。

Apache-2.0
