---
name: researchmind
description: "Universal research-thinking distiller. Given only a scholar's name, or a scholar plus papers, archives, manuscripts, notebooks, correspondence, interviews, oral histories, or local files, build a traceable research-judgment Skill by discovering sources, reconstructing research-decision episodes, contrastively extracting heuristics, validating boundaries, and generating a reusable scholar research advisor. Also use the resulting heuristics to audit research questions, hypotheses, designs, anomalies, and continue/stop decisions. Never impersonate the scholar or present AI inference as their view."
---

# ResearchMind · 通用型科研蒸馏器

ResearchMind 是一个“科研人物 Skill 生成器”。安装一次后，用户可以只给出一个学者名字：

```text
$researchmind 蒸馏 Geoffrey Hinton
$researchmind 蒸馏丹尼尔·卡尼曼，重点看他如何设计实验和处理反例
$researchmind 蒸馏屠呦呦 --depth deep
```

ResearchMind 必须从零完成：身份确认 → 来源发现 → 证据登记 → Research Episode 重建 → 成败/反例配对 → Research Heuristic 提炼 → 迁移边界验证 → 生成独立人物科研顾问 Skill。

目标不是总结“这个学者说过什么”，也不是模仿口吻，而是尽可能重建：

> 在当时的信息条件下，他/她面对什么研究问题，看到了什么证据，排除了什么，为什么采取某个科研动作，什么结果让其继续、修改、放弃或转向。

## 0. 输入与默认行为

支持四类入口：

1. 只有人名：`蒸馏 Richard Feynman`
2. 人名 + 聚焦维度：`蒸馏 Hinton，重点选题判断`
3. 人名 + 用户材料：论文 PDF、手稿、访谈、课程、档案等
4. 已有 scholar 数据目录：继续补证据、升级启发式或重新生成 Skill

只有人名时不要要求用户先整理资料。先完成身份消歧和公开来源侦察；只有存在同名且会实质影响结果时才询问一次。

默认蒸馏深度为 `standard`：

- `quick`：5–10 个高质量来源；至少 3 个 Episode；1–3 条 candidate/provisional heuristic。
- `standard`：20–40 个关键来源；5–10 个 Episode；3–7 条 heuristic；至少 2 组支持/反例结构。
- `deep`：系统加入论文、访谈、档案、通信、手稿、失败史与团队材料；优先补过程性一手资料。
- `golden`：逐条核验关键页码、档案号、时间码、手稿/通信原件；用于精品开源、方法学验证或高风险判断。

用户未指定时：`standard`。

## 1. Scholar Identity & Profile

开始搜索前先建立 `scholar_profile.json`，使用 `schemas/scholar_profile.schema.json`。

至少确认：

- canonical name / aliases
- field / subfields
- institutions
- active period
- major research programs
- major discoveries
- major failures, reversals, disputes or abandoned directions
- major collaborators / laboratories
- likely archival repositories
- source availability by type

不得因为一个人获奖、知名或高被引，就默认其所有研究行为都是最佳实践。

## 2. 通用目录结构

每位学者使用独立 slug：

```text
data/<scholar-slug>/
├── scholar_profile.json
├── distillation_manifest.json
├── source_registry.json
├── episodes/
├── heuristics/
├── evidence/
└── PRIMARY_SOURCE_QUEUE.md
```

生成的人物 Skill：

```text
generated/<scholar-slug>-research-advisor/
├── SKILL.md
├── scholar_profile.json
├── source_registry.json
├── episodes/
└── heuristics/
```

Pauling 位于 `data/pauling/`，只作为 Golden Set 示例，不是主流程特例。

可先运行：

```bash
python scripts/researchmind.py init-scholar "Geoffrey Hinton" --depth standard
```

## 3. Source Discovery — 自动资料发现

只有人名时，必须主动搜索公开资料。按下列优先级建立来源地图，详细规则见 `references/source-discovery.md`。

### A 类：同期过程性一手资料（最高优先）

- research/lab notebooks
- experimental logs
- manuscripts and drafts
- correspondence / letters / emails released in archives
- meeting notes
- research reports
- grant/project records when publicly available

### B 类：同期正式成果

- seminal papers and preprints
- supplementary materials
- technical reports
- patents
- datasets / code / protocols

### C 类：本人回顾

- Nobel / Turing / major prize lectures
- oral histories
- long interviews
- autobiographies / memoirs
- retrospective research talks

### D 类：第三方历史材料

- biographies
- history-of-science / intellectual-history research
- collaborator / student recollections
- institutional archival essays

原则：A > B > C > D。D 类不能单独升级为 A 类事实；C 类可能存在记忆重构，必须与同期材料区分。

## 4. Source Registry 与证据标签

每个关键来源必须登记到 `source_registry.json`：来源 ID、类型、作者、年份、URL/档案地址、稳定定位、inspection status、用途和限制。

每个关键判断必须属于：

- `DIRECT_EVIDENCE`：原始材料直接支持。
- `CROSS_SOURCE_SYNTHESIS`：多来源综合，不能写成学者原话。
- `TRANSFER_INFERENCE`：把启发式迁移到新研究问题。
- `INSUFFICIENT_EVIDENCE`：资料不足，停止补全。

禁止虚构 DOI、页码、档案号、时间码、实验记录、引文或“看起来合理”的科研经历。

## 5. Episode Discovery — 先找决策事件，不先做长总结

不要把几十篇论文直接压成“10 条方法论”。先扫描研究生涯，发现最能暴露科研判断的候选 Episode：

- major breakthrough
- anomaly / unexpected result
- theory or method shift
- failed model / failed experiment
- conflict with prevailing consensus
- long persistence that later succeeded
- persistence that later failed
- abandoned direction
- retraction/correction/reversal when relevant
- cross-disciplinary transfer
- decisive measurement or method choice
- continue / stop / pivot decision

优先选择能回答“为什么采取这个动作”的事件，而不是只选择最著名成果。

使用 `schemas/episode.schema.json`。重点提取：

- research_question
- context
- `known_at_the_time`
- `unknown_at_the_time`
- trigger_or_anomaly
- alternatives_considered
- decision_action
- decision_owner / contributors
- observed_result
- candidate_heuristics
- counter_episode_refs
- alternative_interpretations
- evidence_strength
- needs_primary_source_review

不知道就留空或标 unknown，不为了 Schema 完整而编造。

## 6. Temporal Firewall — 时间防火墙

历史 Episode 的 `known_at_the_time` 只能包含决策发生时已经存在或可获得的信息。

后来才发现的事实只能进入：

- `unknown_at_the_time`
- retrospective notes
- observed_result

禁止用后来正确答案反向塑造“当时一定已经知道”的故事。

## 7. Team Attribution — 禁止英雄归因

科研成果通常是团队产物。必须尽可能区分：

- decision owner
- experimental owner
- analytical owner
- collaborators
- data/material providers
- retrospective narrator

无法确认时写 `uncertain`。不得因为 Skill 以某位名人为入口，就把所有团队动作归于该人。

## 8. Contrastive Distillation — 成败双轨

真正高价值 heuristic 必须尽可能寻找：

```text
supporting episode
      ×
counter / failure / boundary episode
```

问：

1. 两个事件中什么“决策结构”相同？
2. 哪些条件改变后，原本有效的策略失效？
3. 哪些信号本应触发停止、重新测量或改模型？
4. 这是个人稳定习惯，还是一次偶然成功？

没有反例或边界案例时，heuristic 最多标为 `provisional`。

## 9. Heuristic Synthesis — 蒸馏科研判断规则

使用 `schemas/heuristic.schema.json`。

优先输出操作性规则，而不是人格标签。

差：

> 他有第一性原理思维。

好：

> 当全局解释自由度很高时，先列出不确定性显著更低的局部约束；只固定有独立证据支持的约束，再生成候选模型。若模型持续违反这些约束，优先改变拓扑而不是继续加自由参数。

`validated` 的最低要求：

- 至少两个不同 Episode 出现相同决策结构，或一个强支持 + 一个强反例清晰确定边界；
- 能生成对新问题的可检验动作；
- 能说明什么时候不能用；
- 来源可回溯；
- 关键过程证据强度足以支撑该抽象。

否则保持 `candidate` / `provisional`。

## 10. 跨学科 Transfer Validator

把自然科学、计算机、医学等启发式迁移到社会科学、管理学、教育学等领域前，强制输出：

1. `source_structure`
2. `target_structure`
3. `preserved_constraints`
4. `broken_assumptions`
5. `transfer_confidence`: `high / medium / low / reject`

只允许迁移“决策结构”，不能把具体物理、化学、生物机制当作跨领域普遍规律。

## 11. Source Availability Ceiling — 不同学者蒸馏深度不同

不是每位学者都存在手稿和实验日志。根据材料可得性明确标记蒸馏上限：

- `publication_only`：主要只有论文；可分析研究主题演化、公开论证与方法选择，但不能高置信重建真实决策过程。
- `public_retrospective`：论文 + 本人访谈/演讲；可加入本人回顾，但需防记忆重构。
- `process_evidence`：存在笔记、手稿、通信、草稿等；可重建较强 Episode。
- `golden_archive`：关键事件有直接过程证据、同期结果、团队材料和反例，可做高置信方法学蒸馏。

资料不足不是失败。必须降低 claim strength。

## 12. Generated Scholar Advisor

当达到所选深度的最低完成条件后运行：

```bash
python scripts/researchmind.py build-skill --scholar <slug>
```

生成的人物 Skill 不是“数字分身”，而是：

> 基于该学者公开科研材料重建的、可回源的科研判断顾问。

生成 Skill 必须继承四级证据标签、Temporal Firewall、Team Attribution、Contrastive Validation、Transfer Validator 和拒答规则。

## 13. Advisor Mode — 用蒸馏结果干活

当用户把真实科研任务交给某个人物 Skill 或 ResearchMind 时，按以下结构输出：

1. 当前科研决策类型
2. 匹配 heuristic
3. 支持 Episode + 反例 Episode
4. `TRANSFER_INFERENCE`
5. 边界检查
6. transfer confidence
7. 建议的最小下一步
8. 可回源证据
9. `INSUFFICIENT_EVIDENCE`（如有）

不得写“某学者认为你的选题应该……”除非该学者确实讨论过该具体问题。新问题一律属于迁移推演。

## 14. Evaluation

使用 `references/evaluation.md`：

- historical reconstruction：隐藏 Episode 后半段，预测下一步科研动作。
- counterexample detection：是否能识别同一方法的失效条件。
- cross-domain transfer：迁移是否保持结构、明确断裂假设。
- abstention：证据不足时是否会停止。

“回答得像某位学者”不是指标。

## 15. 完成标准

一次人物蒸馏结束时至少报告：

- scholar identity 与消歧结果
- depth
- source availability ceiling
- 来源总数及 A/B/C/D 分布
- Episode 数与 high/medium/low 分布
- supporting/counter pairs
- candidate / provisional / validated heuristic 数量
- 未解决的 primary-source blockers
- 生成 Skill 路径
- 适用范围和不能声称的内容

详细执行协议见 `references/universal-distillation.md`。
