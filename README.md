# ResearchMind

## 通用型科研思维蒸馏器

> 输入一个学者名字，蒸馏他的科研判断力。

[![CI](https://github.com/mindnature/researchmind/actions/workflows/ci.yml/badge.svg)](https://github.com/mindnature/researchmind/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/License-Apache--2.0-blue.svg)](LICENSE)
![Version](https://img.shields.io/badge/ResearchMind-v0.5-6f42c1)

论文告诉我们一位学者最后发现了什么。

ResearchMind 想进一步追问：

> **他当时为什么会这样判断？**

面对一个陌生问题，他先看什么？多个解释同时存在时，他怎么排除？什么证据会让他继续坚持？什么异常会迫使他修改模型？一个方向什么时候值得长期投入，什么时候应该停止？

ResearchMind 是一个面向科研场景的通用型 Agent Skill。它尝试从论文、手稿、科研笔记、通信、访谈、口述史、研究失败、理论转向以及团队记录中，重建真实发生过的 **Research Decision Episodes**，再将其中反复出现、能够被证据支持的科研判断方法蒸馏为可调用的 **Research Advisor Skill**。

**不是总结“大牛说过什么”。**

而是尝试重建：

> **大牛在真正做科研的时候，是怎么做决定的。**

[快速开始](#快速开始) · [ResearchMind 蒸馏什么](#researchmind-蒸馏什么) · [为什么它和普通人物-skill-不同](#为什么它和普通人物-skill-不同) · [工作原理](#工作原理) · [安装](#安装) · [CLI](#cli)

---

## 快速开始

安装 ResearchMind 后，只需要告诉 Agent：

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
论文 / 手稿 / 档案 / 访谈 / 口述史
        ↓
Research Episode 重建
        ↓
成功 × 失败 × 转向 × 边界案例
        ↓
Research Heuristic 蒸馏
        ↓
Scholar Specificity 检验
        ↓
迁移边界验证
        ↓
生成独立 Research Advisor Skill
```

最终可以得到：

```text
姚期智 Research Advisor
Hinton Research Advisor
Feynman Research Advisor
Pauling Research Advisor
……
```

之后，你可以直接把自己的科研问题交给它。

```text
用姚期智科研顾问分析我的大模型安全选题。
```

```text
用 Pauling 科研顾问检查我的实验设计，
重点看我有没有为了保住原假设而忽略反例。
```

```text
用 Hinton 科研顾问分析：
这个 AI 研究方向值得继续做三年吗？
```

---

## ResearchMind 蒸馏什么？

ResearchMind 不把“金句”和“观点”当作最终产品。

它重点蒸馏六类科研判断。

### 01｜问题怎么选

为什么这个问题值得研究？什么只是热门话题，什么可能形成长期研究方向？

### 02｜问题怎么重新定义

高手经常不是直接解决问题，而是先改变问题的表示方式。

```text
原问题
  ↓
新的抽象
  ↓
新的约束
  ↓
新的可研究问题
```

### 03｜假设怎么产生和排除

面对多个可能解释：研究者如何提出候选假设？先排除什么？什么证据具有真正的区分力？

### 04｜异常怎么处理

实验结果和预期不一致时：

```text
忽略？
解释？
补参数？
换方法？
修改理论？
还是放弃整个模型？
```

很多真正重要的科研判断，都发生在这里。

### 05｜什么时候坚持，什么时候转向

顶尖研究者并不只是“坚持”。真正困难的是：

> 什么情况下值得坚持？
>
> 什么信号意味着应该停止？

ResearchMind 会主动寻找成功案例和失败案例进行对比。

### 06｜研究边界在哪里

一种科研方法在什么条件下有效？什么时候会失效？哪些判断只能用于原学科？哪些决策结构可以迁移到新的研究问题？

---

## 不只研究成功，也研究失败

ResearchMind 不做“大师崇拜”。

一个科研方法只有成功案例，没有失败案例，很容易产生幸存者偏差。因此系统会主动寻找：

```text
成功
×
失败
×
争议
×
理论转向
×
放弃方向
```

例如 Pauling：

```text
α-helix
成功

   ×

DNA triple helix
失败
```

ResearchMind 真正关心的不是：

> Pauling 很擅长建立分子模型。

而是：

> **为什么相似的建模方式一次成功、一次失败？**

什么约束发生了变化？什么异常本来应该触发模型放弃？

这才可能形成真正能够迁移的 **Research Heuristic**。

---

## 为什么它和普通人物 Skill 不同？

### 1. 防止“大师名字 + 通用科研常识”

如果一条建议是：

> 要提出重要的问题。

那么费曼可以说，姚期智可以说，Hinton 可以说，任何科研导师都可以说。

这种规则不能因为前面挂了一个大师名字，就变成“大师科研思维”。

ResearchMind 把这种问题称为：

> **Heuristic Laundering — 启发式贴标签。**

因此每条候选 heuristic 都要经过 **Scholar Specificity** 检验：

```text
普通科研 Agent 会不会也这么说？

其他学者是不是也普遍这样做？

这是 ResearchMind 自己的方法论，
还是这个学者真实反复出现的决策结构？

这个学者到底增加了什么？
```

只有存在明确 **Scholar-Added Delta** 的方法，才有资格进入强 Scholar Lens。

### 2. 三层科研顾问

ResearchMind 不允许“大师名字”覆盖目标学科自己的专业规范。

因此生成的 Research Advisor 强制分为三层：

#### `DOMAIN_BASELINE`

目标学科自己的方法学规范。

例如 DID 平行趋势、问卷信效度、统计功效、benchmark leakage、实验重复与识别策略。

这些不是姚期智、费曼或 Hinton 的观点。

#### `SCHOLAR_LENS`

只调用真正具有人物特异性的科研判断，并说明它比一个普通高水平科研 Agent 多看到了什么。

#### `TRANSFER_INFERENCE`

解释这个学者的决策结构为什么可以或不可以迁移到当前问题。

```text
原研究情境和你的问题哪里相似？
什么约束被保留？
什么假设已经断裂？
这条方法可以直接使用？
只能辅助诊断？
只能启发提问？
还是根本不能迁移？
```

一个高质量 Advisor 完全可能给出：

```text
DOMAIN_BASELINE：8 条
SCHOLAR_LENS：1 条
```

这不是失败。

恰恰意味着系统没有为了“像大师”而硬造观点。

---

## 不同学者，可以蒸馏到不同深度

ResearchMind 不假装所有学者都留下了完整科研档案。

因此项目引入 **Distillation Grade**。

| Grade | 含义 | 可支持的蒸馏深度 |
|---|---|---|
| `A_archival` | 档案级 | 有较丰富科研笔记、手稿、通信、实验记录，可尝试重建微观决策 |
| `B_process_informed` | 过程证据级 | 有部分同期过程材料，可约束科研过程重建 |
| `C_retrospective` | 公开回顾级 | 主要依赖论文、本人访谈、演讲、口述史，适合研究轨迹与方法论立场 |
| `D_publication_based` | 成果轨迹级 | 主要只有正式论文，只进行成果与研究程序层面的蒸馏 |

ResearchMind 宁可降低蒸馏等级，也不会为了生成一个“很像大师”的 Skill 去填补不存在的证据。

---

## 当代学者也可以蒸馏

当代学者往往没有公开实验日志。

因此 ResearchMind v0.5 将人物透镜拆成三种 Lens Family：

```text
Scientific Judgment
科研判断

Methodological Stance
方法论立场

Research Strategy
科研布局
```

即使无法重建某一次实验室中的微观决策，仍然可以研究：

- 他长期怎样选择问题；
- 怎样看待一种研究范式；
- 怎样判断技术拐点；
- 为什么在别人放弃一个方向时继续投入。

这样可以覆盖更多仍然活跃的学者，同时不伪装成“档案级重建”。

---

## 自动蒸馏，但允许诚实降级

ResearchMind 的目标是：

> **输入一个名字，尽可能自动跑到底。**

不是一旦证据不够就停止运行。

v0.5 引入 Adaptive Distillation，质量问题分成：

```text
ERROR
必须停止

WARNING
允许继续，但能力降级

INFO
展示当前蒸馏状态
```

例如一位学者最终可能得到：

```text
Distillation Grade：C
Research Episodes：8
Heuristics：6

Active Scholar Lens：2
Experimental Lens：2
Generic Absorbed：2
```

系统仍然可以生成 Advisor，只是会明确告诉你：

> 哪些东西值得高置信使用，哪些东西还只是实验性推断。

---

## 工作原理

ResearchMind 的核心流程：

```text
01 Scholar Identity
身份消歧

02 Source Discovery
寻找论文、档案、访谈、手稿、失败史

03 Evidence Registry
记录来源等级与真实检查状态

04 Research Episode Extraction
重建科研决策事件

05 Temporal Firewall
只使用当时真正已知的信息

06 Team Attribution
区分学者本人、合作者和实验执行者

07 Contrastive Distillation
成功 × 失败 × 边界案例

08 Heuristic Synthesis
提炼可操作科研规则

09 Scholar Specificity Gate
排除通用科研常识

10 Adaptive Routing
Active / Experimental / Generic

11 Transfer Validator
验证跨领域迁移

12 Research Advisor
生成可调用科研顾问
```

机器执行策略集中维护在 [`config/policy.json`](config/policy.json)，减少 SKILL、CLI、Schema 和 Tests 之间的 Policy Drift。

---

## 安装

在支持 Agent Skills 的 AI Agent 中，直接告诉它：

```text
帮我安装这个 Skill：
https://github.com/mindnature/researchmind
```

安装完成后：

```text
蒸馏 Geoffrey Hinton
```

即可启动。

也可以指定人物与重点：

```text
蒸馏 Daniel Kahneman，重点看实验设计和反例处理。
```

```text
蒸馏屠呦呦，使用 deep 模式。
```

---

## CLI

ResearchMind CLI 负责 workspace、pipeline、routing、validation、atomic commit 和 Skill build。

ResearchMind Agent 负责搜索、阅读网页/PDF/档案、调用模型和抽取 Episode。

### 一键创建自动蒸馏任务

```bash
python scripts/researchmind.py auto-distill "Geoffrey Hinton" --mode fast-auto
```

支持：

- `fast-auto`
- `standard-auto`
- `deep-auto`

查看进度：

```bash
python scripts/researchmind.py pipeline-status --job-id <job-id>
```

常用命令：

```bash
python scripts/researchmind.py validate
python scripts/researchmind.py quality-report --scholar pauling
python scripts/researchmind.py route-heuristics --scholar pauling
python scripts/researchmind.py commit-staged --job-id <job-id> --scholar <slug>
python scripts/researchmind.py build-skill --scholar pauling
python scripts/researchmind.py stats --scholar pauling
```

事务式写入使用：

```text
.researchmind/staging/<job-id>/
        ↓
validation + quality report
        ↓
atomic commit
        ↓
data/<scholar>/
```

即使 Agent 中途退出，也可以根据 pipeline checkpoint 继续。

---

## ResearchMind 不是什么

它不是：

```text
论文总结器
名人聊天机器人
大师角色扮演器
科研万能答案生成器
```

它也不能蒸馏：

```text
没有留下任何证据的直觉
从未公开过的真实心理活动
只存在于成功结果之后的“事后智慧”
```

ResearchMind 能做的是：

> **从能够被检查的科研历史中，尽可能重建可验证的科研判断结构。**

---

## 项目的最终目标

今天的大模型已经很擅长：

```text
找论文
读论文
总结论文
写论文
```

ResearchMind 想继续往前走一步。

科研真正困难的地方，往往不是：

> “这篇论文讲了什么？”

而是：

> “现在这些证据到底意味着什么？”
>
> “这个假设还值得继续吗？”
>
> “出现这个异常，我应该修改模型还是推翻模型？”
>
> “这个问题真的值得做三年吗？”
>
> “什么时候应该坚持，什么时候应该转向？”

这些问题没有标准答案。

ResearchMind 想做的，就是从真实科研历史中，蒸馏那些曾经帮助顶尖研究者做出判断、也曾经让他们犯错的决策结构。

---

## 项目状态

当前版本：`v0.5 — Adaptive Distillation & Auto Orchestration`

Pauling 是当前第一个 Golden Set 方法学样例。项目当前重点不是快速堆更多人物，而是持续提高：

1. 人物特异性；
2. 证据可靠性；
3. 跨学科迁移边界；
4. 自动蒸馏通车率；
5. Advisor 对 Generic ResearchMind 的真实增量。

真正的评价标准不是“能生成多少条大师方法”，而是：

> **同一个问题交给 Generic ResearchMind 和 Scholar Advisor 时，后者究竟增加了什么可回源、可区分、真正属于这个人物研究轨迹的判断增量？**

---

## License

Apache-2.0

---

> **论文保存科研结果。ResearchMind 试图保存科研判断。**

**ResearchMind｜从科研历史中，蒸馏可回源、可验证、可迁移但不过界的科研判断力。**
