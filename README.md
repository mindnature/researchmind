# ResearchMind

> 安装一次，输入一个学者名字，把公开科研材料蒸馏成一个可回源、可降级、能区分“领域常识”和“学者特异性判断”的 Research Advisor Skill。

ResearchMind 是一个通用型科研思维蒸馏 Skill。它不做名人数字分身，也不把普通科研常识重新贴上“大师”标签。系统会从论文、手稿、研究笔记、通信、访谈、口述史、团队记录与失败案例中重建 Research Episodes，再将启发式分流为真正的 Scholar Lens、实验透镜或通用基线候选。

## 安装后怎么用

```text
使用 $skill-installer 安装：
https://github.com/mindnature/researchmind
```

然后直接：

```text
$researchmind 蒸馏 Geoffrey Hinton
```

也可以指定重点：

```text
$researchmind 蒸馏姚期智，重点看选题、形式化和技术拐点判断
$researchmind 蒸馏屠呦呦，使用 deep 模式
```

## v0.5 的核心变化

v0.4 强化了防伪，但真实自动化测试暴露了新的风险：质检过严会降低通车率，当代学者可能因为缺少 A 类档案而出现 Scholar Lens 贫血，`DOMAIN_BASELINE` 也可能悬空为模型即兴知识。

v0.5 的目标因此改成：

> 严格，但不断流；证据不足时自动降级，而不是逼 Agent 人工修 YAML。

### 1. Soft Gating

证据成熟度与人物特异性彻底分开。

`status` 管证据：

- candidate
- provisional
- validated
- rejected

`routing.lens_eligibility` 管使用位置：

- `active_lens`
- `experimental_lens`
- `generic_absorbed`
- `excluded`

因此一条历史上证据很强的 heuristic，也可能因为过于通用而被 `generic_absorbed`，不会强行进入 Scholar Lens。

低特异性不再阻断 staging 提交。

### 2. Error / Warning / Info

`ERROR` 才阻断提交，例如：

- broken refs；
- claim-bearing A source 未直接 inspected；
- high-evidence Episode 没有 inspected A/B 支撑。

`WARNING` 只降低能力，例如：

- generic overlap 高；
- specificity 低；
- 缺 counter Episode；
- C/D 级人物没有足够微观过程材料；
- 最终 active Scholar Lens = 0。

详见 `references/adaptive-validation.md`。

### 3. 三种 Lens Family

为避免当代学者因为没有实验笔记而完全“无透镜”，v0.5 区分：

- `scientific_judgment`：微观科研决策；
- `methodological_stance`：公开可观察的方法论立场；
- `research_strategy`：科研布局、技术拐点和方向选择。

例如 Hinton 长期坚持神经网络，可以进入 research strategy / methodological stance，但不会假装成实验室级微观决策证据。

机器可执行的 Episode 类型映射统一放在 `config/policy.json`。

### 4. Domain Baseline Provider

三层 Advisor 继续保留：

```text
DOMAIN_BASELINE
↓
SCHOLAR_LENS
↓
TRANSFER_INFERENCE
```

但现在 `DOMAIN_BASELINE` 也必须尽可能可回源。

优先使用：

- 官方指南；
- reporting standard；
- 方法学 handbook；
- methods paper；
- 用户提供的申报/期刊规范。

如果只能依赖模型参数知识，必须标记：

`MODEL_KNOWLEDGE_UNVERIFIED`

不得写成硬规则。

详见 `references/domain-baseline-provider.md` 和 `schemas/domain_baseline.schema.json`。

### 5. Agent-driven Auto Distill

用户仍只需要一句：

```text
$researchmind 蒸馏 Geoffrey Hinton
```

CLI 也提供统一入口：

```bash
python scripts/researchmind.py auto-distill "Geoffrey Hinton" --mode fast-auto
```

该命令会创建 staging + `pipeline.json`，但不会假装 Python 自己能上网。

职责分离：

```text
ResearchMind Agent
搜索 / 阅读网页 PDF 档案 / 调模型 / 抽 Episode

ResearchMind CLI
workspace / pipeline / routing / validation / atomic commit / build
```

支持模式：

- `fast-auto`
- `standard-auto`
- `deep-auto`

查看进度：

```bash
python scripts/researchmind.py pipeline-status --job-id <job-id>
```

更新状态：

```bash
python scripts/researchmind.py advance-pipeline \
  --job-id <job-id> \
  --phase source_discovery \
  --status completed
```

详见 `references/auto-distill.md`。

## 自动流程

```text
Scholar name
↓
Identity
↓
Source discovery
↓
Source Registry
↓
Episode extraction
↓
Heuristic synthesis
↓
Specificity assessment
↓
Soft routing
↓
Quality report
↓
Atomic commit
↓
Generated Research Advisor
```

即使最后没有 active Scholar Lens，流程仍可以完成。Advisor 会明确披露“人物特异性证据不足”，而不是为了产出数量硬造透镜。

## Distillation Grade

- `A_archival`
- `B_process_informed`
- `C_retrospective`
- `D_publication_based`

Grade 决定系统可以高置信重建到哪一层，不由人物名气决定。

## 单一 Policy Source

v0.5 将机器规则集中到：

```text
config/policy.json
```

包括：

- Lens family；
- Episode type eligibility；
- soft-routing destination；
- auto mode；
- pipeline phases。

CLI 已拆分为：

```text
runtime/core.py
runtime/policy.py
runtime/pipeline.py
scripts/researchmind.py
```

这样可以减少 SKILL / Schema / CLI / Tests 之间的 Policy Drift。

## 常用 CLI

```bash
python scripts/researchmind.py auto-distill "Geoffrey Hinton" --mode fast-auto
python scripts/researchmind.py validate
python scripts/researchmind.py quality-report --scholar pauling
python scripts/researchmind.py route-heuristics --scholar pauling
python scripts/researchmind.py commit-staged --job-id <job-id> --scholar <slug>
python scripts/researchmind.py build-skill --scholar pauling
python scripts/researchmind.py stats --scholar pauling
```

兼容命令：

```bash
python scripts/researchmind.py epistemic-validate
```

v0.5 中它只因为 blocking error 返回失败；warnings 会正常显示但不阻断自动管道。

## 项目状态

`v0.5.0-adaptive-distillation-auto-orchestration`

当前最重要的判断标准不是“能蒸馏出多少条大师方法”，而是：

> 同一个问题交给 Generic ResearchMind 和 Scholar Advisor 时，后者究竟增加了什么可回源、可区分、真正属于该人物研究轨迹的判断增量？

如果只有 1 条高质量 active lens，其余 5 条被诚实降级，也比 6 条通用科研常识套大师名字更有价值。

## License

Apache-2.0
