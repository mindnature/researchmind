---
name: researchmind
description: "Universal research-thinking distiller. Given only a scholar's name, or a scholar plus papers, archives, manuscripts, notebooks, correspondence, interviews, oral histories, or local files, build a traceable research-judgment Skill by discovering sources, reconstructing research-decision episodes, contrastively extracting heuristics, testing scholar specificity, validating transfer boundaries, and generating a reusable scholar research advisor. Separate generic domain review from scholar-specific epistemic lenses. Never impersonate the scholar or present AI inference as their view."
---

# ResearchMind · 通用型科研蒸馏器

ResearchMind 是一个“科研人物 Skill 生成器”。安装一次后，只给一个学者名字也能启动：

```text
$researchmind 蒸馏 Geoffrey Hinton
$researchmind 蒸馏丹尼尔·卡尼曼，重点看他如何设计实验和处理反例
$researchmind 蒸馏屠呦呦 --depth deep
```

ResearchMind 从零完成：身份确认 → 来源发现 → 证据登记 → Research Episode 重建 → 成败/反例配对 → Research Heuristic 提炼 → Scholar Specificity Gate → 迁移边界验证 → 生成独立人物科研顾问 Skill。

目标不是总结“这个学者说过什么”，也不是把通用科研常识换上大师名字，而是尽可能重建：

> 在当时的信息条件下，这位研究者面对什么问题、使用什么表征、优先看哪些约束、排除什么解释、采取什么科研动作，以及什么信号会触发继续、修改、停止或转向。

## 0. 输入与默认行为

支持：

1. 只有人名；
2. 人名 + 聚焦维度；
3. 人名 + 用户提供论文/手稿/访谈/本地材料；
4. 已有 scholar workspace 的继续蒸馏或升级。

只有人名时不要要求用户先整理资料。先做身份消歧和公开来源侦察；只有同名会实质污染语料时才询问。

默认 `standard`：

- `quick`：5–10 个高质量来源，至少 3 个 Episode；
- `standard`：20–40 个关键来源，5–10 个 Episode，3–7 条 heuristic；
- `deep`：系统加入档案、通信、手稿、失败史和团队材料；
- `golden`：逐条核验关键页码、档案号、时间码和过程性一手资料。

## 1. Scholar Identity & Profile

先建立 `scholar_profile.json`，确认 canonical name、aliases、fields、institutions、active period、major research programs、major contributions、失败/转向/争议、主要合作者和可能的档案馆。

同时必须填写：

- `source_availability_ceiling`
- `distillation_grade`
- `evidence_profile`

Distillation Grade：

- `A_archival`：核心 Episode 有充分同期过程档案；
- `B_process_informed`：部分过程证据能约束重建；
- `C_retrospective`：以论文 + 本人回顾为主；
- `D_publication_based`：主要依赖正式成果，只能做成果轨迹级分析。

详细规则见 `references/distillation-grade.md`。

不得因为学者获奖、知名或高被引，就默认其所有研究行为都是最佳实践。

## 2. 通用目录与事务式写入

正式数据：

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

复杂蒸馏任务优先使用 staging：

```text
.researchmind/staging/<job-id>/data/<scholar-slug>/
```

写完后执行结构校验 + epistemic consistency validation，全部通过才 atomic commit 到 `data/<slug>/`。禁止多工具写入一半就把半成品当正式数据。

CLI：

```bash
python scripts/researchmind.py stage-scholar "Geoffrey Hinton"
python scripts/researchmind.py commit-staged --job-id <job-id> --scholar geoffrey-hinton
```

见 `references/transactional-pipeline.md`。

## 3. Source Discovery

按 A/B/C/D 建来源地图，详见 `references/source-discovery.md`。

A. 同期过程性一手资料：notebooks、drafts、correspondence、lab/research reports、meeting notes。

B. 同期正式成果：papers、preprints、supplements、technical reports、patents、data/code。

C. 本人回顾：major-prize lectures、oral histories、long interviews、memoirs、retrospective talks。

D. 第三方历史材料：biographies、history-of-science scholarship、collaborator/student recollections、institutional archival essays。

原则：A > B > C > D。D 不能偷偷替代 A；C 必须与同期证据分开。

不仅搜成功，还要主动搜：失败、争议、被放弃方向、理论转向、反例、修正和团队成员材料。

## 4. Source Registry 与证据纪律

每个关键来源登记：source ID、class、作者、年份、URL/档案地址、stable locator、inspection status、用途和局限。

不要把“搜到”当成“读过”。统计时区分：

- discovered sources
- inspected sources
- claim-bearing sources

每个关键判断必须属于：

- `DIRECT_EVIDENCE`
- `CROSS_SOURCE_SYNTHESIS`
- `TRANSFER_INFERENCE`
- `INSUFFICIENT_EVIDENCE`

禁止虚构 DOI、页码、档案号、时间码、实验记录、引文或科研经历。

## 5. Episode Discovery 与 Episode Type Gate

先找决策事件，不先把论文压成“十条方法”。

优先寻找：breakthrough、anomaly、method/theory shift、failed model、conflict with consensus、abandoned direction、cross-domain transfer、decisive measurement、continue/stop/pivot。

每个 Episode 应标 `episode_type`：

可以直接参与科研 heuristic 蒸馏的类型：

- `scientific_decision`
- `problem_framing`
- `method_choice`
- `anomaly_response`
- `theory_revision`

以下默认不能直接生成“科研判断 heuristic”：

- `career_decision`
- `research_program_strategy`
- `institution_building`
- `field_outcome`

后者可以进入 Research Leadership 或 science-of-science 分析，但不能为了扩大样本强行当作科研微观决策。

## 6. Temporal Firewall

`known_at_the_time` 只能放决策发生时可得的信息。后来发现的事实进入 `unknown_at_the_time`、retrospective notes 或 observed result。

禁止用结果反推“当时一定已经知道”。

## 7. Team Attribution

必须尽可能区分 decision owner、experimental owner、analytical owner、collaborators、data/material providers、retrospective narrator。

无法确认时写 uncertain。不得因为 Skill 以名人为入口，就把团队动作全部归于该人。

## 8. Contrastive Distillation

高价值 heuristic 尽可能绑定：

```text
supporting episode × counter/failure/boundary episode
```

问：什么决策结构重复？什么条件变化后策略失效？哪些信号应该触发停止或换模型？这是稳定习惯还是一次偶然成功？

没有反例/边界时，heuristic 最多 `provisional`。

## 9. Heuristic Synthesis

优先提炼操作规则：

`trigger → representation → exclusion rule → action → stop/change condition`

拒绝仅有：好奇、坚持、严谨、独立思考、第一性原理、提出好问题、跟随证据等泛化美德，除非它们被多个 Episode 转换为有区分度的操作程序。

## 10. Scholar Specificity Gate — 防止 Heuristic Laundering

这是 v0.4 的一级规则。

每条 candidate heuristic 都要问：

> 去掉学者名字，一个普通高水平科研 Agent 会不会也给出几乎同样的规则？

还要检查：

1. 是否只是 ResearchMind 自己的规则被重新归因给学者；
2. 是否只是目标学科的通用审稿规范；
3. 是否在多个该学者 Episode 中以相似的操作结构重复出现；
4. 是否存在足以区分“什么时候用/什么时候不用”的边界。

启发式的 `specificity` 包含：

- status: `not_tested / pass / review / reject`
- generic_baseline_overlap
- scholar_specificity
- framework_contamination
- scholar_added_delta
- specificity_evidence

`validated` heuristic 必须通过 specificity gate。详细见 `references/scholar-specificity.md`。

如果 Generic ResearchMind 与 Scholar Advisor 对同一 held-out 任务给出的实质判断几乎可互换，则该 heuristic 不得宣传为该学者的特异性科研方法。

## 11. Transfer Validator

跨领域迁移强制输出：

- source_structure
- target_structure
- preserved_constraints
- broken_assumptions
- transfer_confidence: `high / medium / low / reject`

解释规则：

- high：可与目标学科证据共同支持建议；
- medium：主要用于诊断，具体建议需目标学科依据；
- low：只能作为问题生成器；
- reject：禁止使用该类比。

不能因为一个类比“很有大师味道”就迁移具体计算机、物理、化学或生物机制。

## 12. Advisor Mode — 三层输出

跨学科或复杂科研评审必须拆成三层，见 `references/advisor-three-layer.md`。

### Layer 1 — `DOMAIN_BASELINE`

使用目标学科的普通研究规范审计。明确这些建议与该学者无关。

例如 DID 平行趋势、问卷信效度、统计功效、benchmark leakage 等不能因为输出来自“姚期智顾问”就强行挂姚期智 heuristic 编号。

### Layer 2 — `SCHOLAR_LENS`

强 scholar-specific 建议只允许调用 `specificity.status = pass` 的启发式。

必须说明：

- heuristic
- supporting/counter Episodes
- scholar-added delta
- 为什么这不是普通科研顾问也会给出的同一建议

未通过 specificity gate 的 heuristic 只能标记为 experimental lens。

### Layer 3 — `TRANSFER_INFERENCE`

给出结构同构与断裂条件。low 只能提问，不能下建议；reject 不使用。

一个高质量回答可能有 10 条 DOMAIN_BASELINE 但只有 1 条 SCHOLAR_LENS。这是正确行为，不要为了“像大师”硬凑。

## 13. Epistemic Validation

`python scripts/researchmind.py epistemic-validate` 检查的不只是 JSON：

- validated heuristic 是否通过 specificity gate；
- validated research heuristic 是否只引用合格科研 Episode 类型；
- high-evidence Episode 是否至少绑定 inspected A/B source；
- claim-bearing A source 是否 inspected 且有 stable locator。

这仍不能替代外部事实核验。年份、术语、原文、归属和历史因果链必须由 Agent 打开原始来源核实，不能因为 CLI 绿色通过就宣称史实正确。

## 14. Generated Scholar Advisor

完成所选深度后运行：

```bash
python scripts/researchmind.py build-skill --scholar <slug>
```

生成顾问必须展示 Distillation Grade、source ceiling，并继承三层 Advisor、specificity gate、Temporal Firewall、Team Attribution、Transfer Validator 和拒答规则。

## 15. Evaluation

使用 `references/evaluation.md`：

- historical reconstruction
- counterexample detection
- cross-domain transfer
- abstention
- generic baseline A/B
- heuristic laundering test
- framework contamination test
- three-layer separation test

“回答得像某位学者”不是指标。

真正指标是：这个人物 Skill 是否提供了可证据化、可区分、优于 generic baseline 的科研判断增量。

## 16. 完成报告

一次蒸馏至少报告：

- scholar identity / disambiguation
- requested depth
- Distillation Grade
- source availability ceiling
- discovered / inspected / claim-bearing sources A/B/C/D
- Episode 类型与证据强度
- supporting/counter pairs
- candidate / provisional / validated heuristics
- specificity gate 通过/复核/拒绝/未测试数量
- primary-source blockers
- generated Skill path
- scholar-added delta
- unsafe-to-claim 内容

详细协议见：

- `references/universal-distillation.md`
- `references/scholar-specificity.md`
- `references/advisor-three-layer.md`
- `references/distillation-grade.md`
- `references/transactional-pipeline.md`
