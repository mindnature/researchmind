---
name: researchmind
description: "Universal research-thinking distiller. Given only a scholar's name, build a traceable research-judgment Advisor by discovering sources, reconstructing decision Episodes, extracting heuristics, softly routing generic vs scholar-specific rules, and preserving evidence boundaries. Supports adaptive degradation for sparse modern-scholar archives, source-backed domain baselines, and agent-driven one-click orchestration. Never impersonate the scholar or present AI inference as their view."
---

# ResearchMind · 通用型科研蒸馏器

ResearchMind 的目标不是给“大师观点”贴标签，而是回答一个更严格的问题：

> 相比一个普通高水平科研 Agent，这位学者的公开科研轨迹到底额外提供了什么可证据化、可区分、可迁移但不过界的科研判断增量？

安装后可以直接输入：

```text
$researchmind 蒸馏 Geoffrey Hinton
$researchmind 蒸馏姚期智，重点看选题和技术拐点判断
$researchmind 蒸馏屠呦呦 --depth deep
```

默认从名字开始，不要求用户预先整理论文。

## 1. 核心流程

```text
scholar name
→ identity resolution
→ source discovery
→ source registry
→ Research Episodes
→ contrastive heuristic synthesis
→ scholar specificity assessment
→ soft routing
→ quality report
→ atomic commit
→ generated scholar advisor
```

详细执行由：

- `references/universal-distillation.md`
- `references/source-discovery.md`
- `references/auto-distill.md`

共同约束。

## 2. 证据等级与 Distillation Grade

来源仍按 A/B/C/D：

- A：同期过程性一手资料；
- B：同期正式成果；
- C：本人回顾；
- D：第三方历史重建。

人物蒸馏等级：

- `A_archival`
- `B_process_informed`
- `C_retrospective`
- `D_publication_based`

当代学者常见 C/D 级并不是失败。系统必须降低微观心智推断强度，而不是为了“像大师”编造实验室细节。

## 3. Episode 不再只有一种

v0.5 将可用透镜拆成三个 family：

### `scientific_judgment`

适用于：

- scientific_decision
- problem_framing
- method_choice
- anomaly_response
- theory_revision

这是最接近微观科研决策的透镜。

### `methodological_stance`

适用于公开可观察的方法论立场，例如长期坚持何种表征、如何处理理论与实验关系、如何看待某类研究范式。

可使用：

- methodological_stance
- paradigm_shift_advocacy
- theory_revision
- research_program_strategy

### `research_strategy`

用于科研布局和技术拐点判断：

- research_program_strategy
- paradigm_shift_advocacy

`career_decision`、`institution_building`、`field_outcome` 可以保留为历史上下文，但默认不能直接制造强 Scholar Lens。

机器规则以 `config/policy.json` 为唯一来源。

## 4. Heuristic 的两个正交维度

不要把证据成熟度和人物特异性混成一个状态。

### Evidence maturity

`status`：

- candidate
- provisional
- validated
- rejected

它回答：

> 这条规则在历史证据上成熟到什么程度？

### Scholar routing

`routing.lens_eligibility`：

- `active_lens`
- `experimental_lens`
- `generic_absorbed`
- `excluded`

它回答：

> 这条规则能否作为该学者特异性透镜进入 Advisor？

因此一条 heuristic 可以是：

```yaml
status: validated
routing:
  lens_eligibility: generic_absorbed
```

意思是：历史规律可能真实，但并不独属于这位学者。

## 5. Scholar Specificity 与 Heuristic Laundering

每条 heuristic 都应尽可能评估：

- generic_baseline_overlap
- scholar_specificity
- framework_contamination
- scholar_added_delta
- specificity_evidence

如果去掉学者名字后，一个普通科研 Agent 也会给出几乎相同的规则，不能把它宣传成大师特异性方法。

如果规则只是 ResearchMind 自己的 Transfer Validator、证据纪律或目标学科常识被重新贴上学者名字，则属于 framework contamination / heuristic laundering。

## 6. Soft Gating — 质量差不等于管道失败

v0.5 使用 `ERROR / WARNING / INFO`：

### ERROR

阻断提交：

- broken refs / malformed data；
- claim-bearing A source 未直接 inspected 却当作过程证据；
- high-evidence Episode 没有 inspected A/B 支撑；
- 无法可靠解释的数据结构错误。

### WARNING

允许提交，但自动降低能力：

- specificity 低；
- generic overlap 高；
- framework contamination 高；
- validated heuristic 缺 counter Episode；
- C/D 级学者微观过程证据不足；
- Scholar Lens 被清零。

### INFO

记录实验透镜和语料边界。

详细规则：`references/adaptive-validation.md`。

## 7. Soft Routing

低特异性 heuristic 不再让 staging 卡死。

自动路由：

- specificity 强且 Episode 类型匹配 → `active_lens`；
- 证据有价值但特异性未充分证明 → `experimental_lens`；
- 高度通用 / 框架污染 → `generic_absorbed`；
- heuristic 自身 rejected → `excluded`。

`generic_absorbed` 只是 DOMAIN_BASELINE 候选，不会自动变成学科规范。

## 8. Domain Baseline Provider

三层 Advisor 继续保留：

### Layer 1 — `DOMAIN_BASELINE`

目标学科的普通规范。

但 v0.5 新增要求：重要 baseline claim 必须尽可能有独立来源。优先官方指南、方法学 handbook、methods paper、reporting standard、用户提供的申报/期刊规则。

每条重要 baseline claim 应标记：

- provenance_status
- confidence
- source / locator
- applicability

如果只能依赖模型参数知识，标：

`MODEL_KNOWLEDGE_UNVERIFIED`

并不得写成硬规则。

详见：`references/domain-baseline-provider.md`。

### Layer 2 — `SCHOLAR_LENS`

强结论只使用 `active_lens`。

`experimental_lens` 只能产生诊断问题或备选视角，并明确标 experimental。

如果 active lens = 0，直接告诉用户“当前人物特异性证据不足”，不要硬凑。

### Layer 3 — `TRANSFER_INFERENCE`

强制比较：

- source_structure
- target_structure
- preserved_constraints
- broken_assumptions
- transfer_confidence

`low` 只能提问；`reject` 不使用。

## 9. Agent-driven Auto Distill

用户仍只需要一句：

```text
$researchmind 蒸馏 Geoffrey Hinton
```

在支持 CLI 的环境中，可初始化：

```bash
python scripts/researchmind.py auto-distill "Geoffrey Hinton" --mode fast-auto
```

注意：CLI 不假装自己能联网。

职责分工：

- ResearchMind Agent：搜索、打开网页/PDF/档案、调用模型、抽取 Episode/heuristic；
- ResearchMind CLI：workspace、pipeline、staging、routing、quality report、atomic commit、build-skill。

`pipeline.json` 让 Codex、豆包或其他 Agent 可以断点继续。

## 10. 常用 CLI

```bash
python scripts/researchmind.py auto-distill "Geoffrey Hinton" --mode fast-auto
python scripts/researchmind.py pipeline-status --job-id <job-id>
python scripts/researchmind.py advance-pipeline --job-id <job-id> --phase source_discovery --status completed
python scripts/researchmind.py quality-report --scholar <slug>
python scripts/researchmind.py route-heuristics --scholar <slug>
python scripts/researchmind.py commit-staged --job-id <job-id> --scholar <slug>
python scripts/researchmind.py build-skill --scholar <slug>
```

`epistemic-validate` 保留为兼容入口；v0.5 中它只因 blocking error 返回失败，warnings 不再中断自动管道。

## 11. 事务式 Staging

复杂蒸馏继续先写：

```text
.researchmind/staging/<job-id>/
```

正式提交前：

1. structural validate；
2. soft routing；
3. quality report；
4. blocking errors 才 abort；
5. warnings 写入 report；
6. atomic commit；
7. build advisor。

这个机制保留 v0.4 的工程确定性，同时恢复自动化通车率。

## 12. 单一 Policy Source

机器可执行规则集中在：

`config/policy.json`

包括：

- Lens families；
- Episode type eligibility；
- routing destination；
- auto modes；
- pipeline phases。

Schema、CLI、tests、generated advisor 都应围绕该配置工作，减少 Policy Drift。

## 13. 完成报告

一次人物蒸馏最终至少报告：

- scholar identity
- depth / auto mode
- Distillation Grade
- source ceiling
- discovered / inspected / claim-bearing A/B/C/D
- Episode types
- heuristic evidence status
- routing counts
- active / experimental / generic-absorbed lenses
- warnings / blockers
- generated skill
- scholar-added delta
- unsafe-to-claim 内容

成功不等于“必须有很多 Scholar Lens”。

一个只有 1 条高质量 active lens、但其余内容被诚实降级的 Advisor，优于 10 条靠大师名字包装的通用科研建议。
