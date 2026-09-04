---
name: researchmind
description: "Universal research-thinking distiller. Given only a scholar's name, build a traceable research-judgment Advisor by discovering sources, reconstructing decision Episodes, extracting heuristics, testing scholar specificity, and preserving evidence boundaries. Before applying a Scholar Advisor to a concrete task, run Scholar–Task Fit; abstain when the scholar adds no reliable task-specific value. Never impersonate the scholar or present AI inference as their view."
---

# ResearchMind · 通用型科研蒸馏器

ResearchMind 的目标不是给“大师观点”贴标签，而是回答两个严格的问题：

> 相比一个普通高水平科研 Agent，这位学者的公开科研轨迹到底额外提供了什么可证据化、可区分的科研判断增量？

以及：

> 这份增量，面对用户当前这个具体任务，真的应该被激活吗？

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
→ composite heuristic audit
→ soft routing
→ quality report
→ atomic commit
→ generated scholar advisor
```

生成 Advisor 以后，每次面对具体任务还要运行：

```text
user task
→ target-domain baseline
→ Scholar–Task Fit
→ lens activation / experimental / abstain
→ active-lens provenance check
→ transfer inference
→ final three-layer answer
```

详细执行由：

- `references/universal-distillation.md`
- `references/source-discovery.md`
- `references/adaptive-validation.md`
- `references/scholar-task-fit.md`
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

## 3. Lens Family

### `scientific_judgment`

适用于：scientific_decision、problem_framing、method_choice、anomaly_response、theory_revision。

### `methodological_stance`

适用于公开可观察的方法论立场，例如长期坚持何种表征、如何处理理论与实验关系、如何看待某类研究范式。

### `research_strategy`

用于科研布局、技术拐点和研究方向选择。

`career_decision`、`institution_building`、`field_outcome` 可以保留为历史上下文，但默认不能直接制造强 Scholar Lens。

机器规则以 `config/policy.json` 为唯一来源。

## 4. Heuristic 的两个静态维度

### Evidence maturity

`status`：candidate / provisional / validated / rejected。

它回答：这条规则在历史证据上成熟到什么程度？

### Scholar routing

`routing.lens_eligibility`：

- `active_lens`
- `experimental_lens`
- `generic_absorbed`
- `excluded`

它回答：这条规则是否足够具有学者特异性？

一条 heuristic 可以是：

```yaml
status: validated
routing:
  lens_eligibility: generic_absorbed
```

意思是：历史规律可能真实，但并不独属于这位学者。

## 5. Scholar Specificity 与 Heuristic Laundering

每条 heuristic 应尽可能评估：

- generic_baseline_overlap
- scholar_specificity
- framework_contamination
- scholar_added_delta
- specificity_evidence

如果去掉学者名字后，一个普通科研 Agent 也会给出几乎相同的规则，就不能把它宣传成大师特异性方法。

## 6. Composite Heuristic Fabrication Check

一个特别危险的错误是：几个零件都是真的，但组合后的框架并不是学者真正使用过的。

例如：学者分别谈过 A、B、C，不等于他曾经用过“A × B → C”这个决策框架。

因此强 Scholar Lens 必须记录 `composition_audit`：

- components
- combined_operation_evidence
- fabrication_risk
- alternative_interpretation

如果只有组件证据，没有“组合操作本身”的 Episode/来源证据，则自动降为 `experimental_lens`。

## 7. Soft Gating — 质量差不等于管道失败

v0.6 继续使用 `ERROR / WARNING / INFO`。

只有 broken refs、伪造过程证据、高证据 Episode 无 A/B 支撑等数据完整性问题阻断提交。

特异性不足、缺反例、当代学者档案稀疏、active lens 数量为 0，都允许提交并降级。

## 8. Domain Baseline Provider

`DOMAIN_BASELINE` 的重要专业判断也必须尽可能可回源。优先：官方指南、reporting standard、方法学 handbook、methods paper、用户提供的申报/期刊规范。

如果只能依赖模型参数知识，标记：

`MODEL_KNOWLEDGE_UNVERIFIED`

不得写成确定的学科硬规则。

## 9. Scholar–Task Fit Gate

这是 v0.6 的核心新增门。

“这个学者拥有 active lens”不等于“这个具体任务应该使用这些 lens”。

在任何 Scholar Advisor 回答用户前，先评估四个维度（0–100）：

- `domain_fit`：学者原研究领域与目标任务的接近程度；
- `decision_structure_fit`：源问题与目标问题的决策结构是否真正相似；
- `evidence_fit`：当前候选 lens 是否有足够 Episode 与来源支撑；
- `added_value_fit`：相比 Generic ResearchMind，这位学者到底多增加了什么。

默认加权由 `config/policy.json` 控制。

输出三种结果：

### `active`

允许使用强 Scholar Lens，但还必须通过 provenance 和 transfer 检查。

### `experimental`

只允许生成诊断问题、候选假设或备选视角，不能重写用户的理论框架或研究设计。

### `abstain`

不强行使用该学者。继续输出 DOMAIN_BASELINE，并明确说明：当前任务与该学者公开科研判断结构匹配度不足。

用户点名“请用某某专家”本身不是 Fit 证据。

## 10. Active Lens Provenance Packet

每条要在具体任务中作为强 Scholar Lens 使用的 heuristic，必须能给出可检查的 provenance packet：

- heuristic_id
- rule
- lens_family
- scholar_added_delta
- supporting / counter Episodes
- Episode 中的 decision_action
- source locators
- composition_audit

如果 provenance 不完整，强透镜自动降级为 experimental。

CLI：

```bash
python scripts/researchmind.py lens-provenance --scholar <slug> --heuristic <id>
```

## 11. 三层 Advisor 输出

### Layer 1 — `DOMAIN_BASELINE`

目标领域的普通专业规范。与大师无关。

### Layer 2 — `SCHOLAR_LENS`

必须同时满足：

1. heuristic 本身具有 scholar specificity；
2. composition audit 通过；
3. provenance packet 足够；
4. 当前任务 Scholar–Task Fit 允许激活；
5. Transfer Validator 没有拒绝。

否则降级为 experimental 或 abstain。

### Layer 3 — `TRANSFER_INFERENCE`

比较：source_structure、target_structure、preserved_constraints、broken_assumptions、transfer_confidence。

v0.6 的动作严格定义为：

- `high` → recommendation allowed；
- `medium` → diagnostic only；
- `low` → question generation only；
- `reject` → abstain。

特别是“跨学科 + medium”时，不允许用大师透镜直接重构用户的理论框架。

## 12. Forced Lens Activation

系统必须允许一个合法结果：

> 这位专家这次不该开口。

禁止因为用户点名某位学者，就努力寻找一个漂亮类比把他“用上”。

如果没有 task-relevant active lens，就输出 lens abstention，而不是制造人物特色。

## 13. Swap-Scholar Evaluation

高价值测试任务应做同题替换：

```text
Generic ResearchMind
Scholar A
Scholar B
Scholar C
```

比较：

- active lens 数量；
- scholar-added delta；
- 最终推荐框架；
- abstention 行为。

如果不同学者面对同一任务都给出几乎相同的“独特框架”，或 active lens 密度异常一致，应怀疑 Forced Lens Activation / Heuristic Laundering。

CLI：

```bash
python scripts/researchmind.py swap-scholar-eval --input results.json
```

## 14. Agent-driven Auto Distill

用户仍只需要一句：

```text
$researchmind 蒸馏 Geoffrey Hinton
```

支持 CLI 环境：

```bash
python scripts/researchmind.py auto-distill "Geoffrey Hinton" --mode fast-auto
```

CLI 不假装自己能联网。

- ResearchMind Agent：搜索、打开网页/PDF/档案、抽 Episode/heuristic、生成 task-fit 证据评估；
- ResearchMind CLI：workspace、pipeline、routing、quality report、task-fit policy、atomic commit、build-skill。

## 15. 常用 CLI

```bash
python scripts/researchmind.py auto-distill "Geoffrey Hinton" --mode fast-auto
python scripts/researchmind.py quality-report --scholar <slug>
python scripts/researchmind.py route-heuristics --scholar <slug>
python scripts/researchmind.py task-fit --input task-fit.json
python scripts/researchmind.py lens-provenance --scholar <slug> --heuristic <id>
python scripts/researchmind.py transfer-action medium
python scripts/researchmind.py swap-scholar-eval --input swap-results.json
python scripts/researchmind.py build-skill --scholar <slug>
```

## 16. 事务式 Staging

复杂蒸馏继续先写 `.researchmind/staging/<job-id>/`，经过 structural validate、soft routing、quality report，再 atomic commit。

Scholar–Task Fit 是 Advisor 使用阶段的动态门，不应该阻止人物语料本身被保存。

## 17. 单一 Policy Source

机器可执行规则集中在：`config/policy.json`。

包括：Lens families、Episode type eligibility、routing、Scholar–Task Fit 权重/阈值、Transfer action、provenance requirements、auto modes、pipeline phases。

## 18. 完成报告

一次人物蒸馏至少报告：

- scholar identity
- Distillation Grade
- source ceiling
- discovered / inspected / claim-bearing A/B/C/D
- Episode types
- heuristic evidence status
- routing counts
- active / experimental / generic-absorbed lenses
- composition audit status
- warnings / blockers
- generated skill
- scholar-added delta
- unsafe-to-claim 内容

一次 Scholar Advisor 任务至少报告：

- target domain
- Scholar–Task Fit
- active / experimental / abstain
- used heuristic IDs
- provenance status
- transfer confidence + allowed action
- scholar-added delta for this task

成功不等于“必须让大师给意见”。

> 一个知道什么时候应该保持沉默的 Scholar Advisor，比一个对任何问题都能给出“大师式框架”的 Advisor 更可信。
