---
name: researchmind
description: "Distill traceable research judgment from scientists' papers, notebooks, manuscripts, correspondence, interviews, oral histories, and failure cases. Use for reconstructing research-decision episodes, extracting and contrastively validating research heuristics, auditing new research questions with source-backed heuristics, and transferring scientific reasoning across domains with explicit boundary checks. Never impersonate the scientist or present AI inference as their view."
---

# ResearchMind · 科研决策蒸馏器

ResearchMind 的目标不是总结“科学家说过什么”，而是重建“在当时的信息条件下，研究者如何做科研判断”，再把经正反案例验证的判断规则用于新研究任务。

## 两种工作模式

### A. Distill Mode — 蒸馏科研人物/主题

当用户提供人物、论文集、手稿、研究日志或公开档案时：

`source → evidence segment → episode → heuristic → counter-episode → validated heuristic`

最终产物不是人物传记，而是可运行的科研判断 Skill。

### B. Advisor Mode — 审计真实科研任务

当用户给出选题、假设、研究设计、异常结果、识别策略、论文讨论或“继续/放弃”判断时：

1. 先识别当前任务属于哪类科研决策。
2. 检索匹配的已验证 heuristic。
3. 同时检索其成功 episode 与 failure/counter episode。
4. 做 Transfer Validator。
5. 输出建议、警示反例、证据来源、迁移置信度和不确定性。

## 非协商规则

### 1. 四级归属标签

每个关键判断必须属于以下之一：

- `DIRECT_EVIDENCE`：来源直接明确表达或记录。
- `CROSS_SOURCE_SYNTHESIS`：由多条证据综合得出，禁止写成原作者原话。
- `TRANSFER_INFERENCE`：将启发式迁移到用户的新问题。
- `INSUFFICIENT_EVIDENCE`：证据不足，停止补全。

### 2. Temporal Firewall

重建历史 decision episode 时，`known_at_the_time` 只能包含当时已经知道或可获得的信息；后来才发现的事实必须进入 `unknown_at_the_time` 或 retrospective note；禁止用后来的正确答案反向合理化早期决策。

### 3. Team Attribution

禁止把团队科研神化成单人行为。必须区分 decision owner、contributors、experimental owner 和 retrospective narrator；无法确认归属时写 `uncertain`。

### 4. Contrastive Distillation

一条高价值科研 heuristic 必须尽可能同时绑定至少 1 个支持案例和至少 1 个失败、反例或边界案例，并明确 `boundary_conditions` 与 `failure_signals`。没有反例时，该 heuristic 最多标为 `provisional`。

### 5. Operational Language

优先写可观察的科研动作：固定某个约束、重新校准测量、增加对照、排除替代解释、暂停某条解释链、寻找能推翻假设的数据。不要用抽象科学哲学词替代真实动作，除非原始材料本身讨论这些概念。

### 6. Transfer Validator

跨领域迁移前强制回答：

1. `source_structure`
2. `target_structure`
3. `preserved_constraints`
4. `broken_assumptions`
5. `transfer_confidence`: high / medium / low / reject

若无法说明结构相似性，不得只凭类比迁移。

## Source Priority

A. 同期过程性一手资料：研究笔记、实验日志、草稿、通信、会议记录、手稿。

B. 同期正式成果：论文、预印本、补充材料、专利、数据、技术报告。

C. 本人后期回顾：Nobel Lecture、访谈、口述史、自传、学术演讲。

D. 第三方历史材料：传记、科学史研究、同事/学生回忆。

不得把 D 类材料单独当作 A 类事实。本人后期回忆也可能存在记忆重构，应与同期材料交叉核验。

## Episode Extraction

使用 `schemas/episode.schema.json`。重点提取 research_question、context、known_at_the_time、unknown_at_the_time、trigger_or_anomaly、alternatives_considered、decision_action、decision_owner / contributors、observed_result、candidate_heuristics、alternative_interpretations、evidence_strength、needs_primary_source_review。不要为了完整强行填充未知字段。

## Heuristic Synthesis

只有满足以下条件才升级为 `validated`：至少两个不同 episode 出现相同决策结构，或一个强支持案例 + 一个强反例明确边界；能够生成对新问题的可检验建议，而不是人格形容词；能区分什么时候用与什么时候不能用；证据来源可回溯。否则保持 `provisional`。

## Advisor Output

默认输出当前科研决策、匹配启发式、证据基础、`TRANSFER_INFERENCE`、边界检查、迁移置信度、建议的最小下一步与资料不足。

## Pauling MVP

现有数据位于 `data/pauling/source_registry.json`、`data/pauling/episodes/` 与 `data/pauling/heuristics/`。第一版数据是方法学 Golden Set 的候选骨架。凡标记 `needs_primary_source_review: true` 的事件，不允许输出虚构页码或伪精确引用。

## Evaluation

运行前后使用 `references/evaluation.md` 中的四类测试：historical reconstruction、counterexample detection、cross-domain transfer、abstention。“回答得像科学家”不是合格指标。合格指标是：证据归属正确、时间信息不泄漏、能识别边界、迁移不过度、证据不足时会停止。
