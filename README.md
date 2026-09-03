# ResearchMind

> 安装一次，输入一个学者名字，把公开科研材料蒸馏成一个可回源、能区分“通用学术规范”和“学者特异性判断”的 Research Advisor Skill。

ResearchMind 是一个通用型科研思维蒸馏 Skill。它不是论文摘要器，也不是“名人数字分身”。它从论文、研究笔记、手稿、通信、访谈、口述史、团队记录和失败案例中重建 Research Decision Episodes，再通过正反案例和人物特异性检验提炼 Research Heuristics。

## 安装后怎么用

```text
使用 $skill-installer 安装：
https://github.com/mindnature/researchmind
```

然后只输入一个名字即可：

```text
$researchmind 蒸馏 Geoffrey Hinton
```

也可以指定重点和深度：

```text
$researchmind 蒸馏丹尼尔·卡尼曼，重点研究他如何设计实验和处理反例
$researchmind 蒸馏屠呦呦，使用 deep 模式
```

## ResearchMind 会自动做什么

```text
学者名字
   ↓
身份确认与同名消歧
   ↓
Scholar Profile + Distillation Grade
   ↓
自动发现论文 / 档案 / 手稿 / 通信 / 访谈 / 口述史 / 科学史资料
   ↓
Source Registry：区分 discovered / inspected / claim-bearing
   ↓
扫描关键科研决策事件
   ↓
Research Episodes + Episode Type Gate
   ↓
Temporal Firewall + Team Attribution
   ↓
成功 × 失败 × 转向 × 边界案例
   ↓
Contrastive Distillation
   ↓
Research Heuristics
   ↓
Scholar Specificity Gate
   ↓
Generic Baseline A/B + Framework Contamination 检测
   ↓
Transfer Validator
   ↓
生成 <scholar>-research-advisor Skill
```

## v0.4 解决什么问题

前一版已经证明“输入人物 → 自动找源 → Episodes → Heuristics → 独立 Advisor”可以跑通。但真实测试暴露了一个更深的问题：一个高水平 AI 很容易把通用科研常识或目标学科的审稿规范，重新贴上“大师 heuristic”的标签。

ResearchMind v0.4 把这个风险定义为：

> **Heuristic Laundering — 启发式贴标签 / 洗白。**

例如：DID 平行趋势、问卷信效度、空间计量样本单元等，本质上属于社会科学 `DOMAIN_BASELINE`，不能因为当前调用的是“姚期智科研顾问”，就硬挂到姚期智 heuristic 下面。

因此 v0.4 新增四个核心机制。

### 1. Scholar Specificity Gate

每条 heuristic 必须检查：

- `generic_baseline_overlap`
- `scholar_specificity`
- `framework_contamination`
- `scholar_added_delta`
- `specificity_evidence`

`validated` heuristic 必须通过 specificity gate。

如果把学者名字删掉后，一个普通高水平科研 Agent 仍会给出几乎相同的规则，则这条规则不能宣传成“该学者的独特科研思维”。

详见 `references/scholar-specificity.md`。

### 2. 三层 Advisor

真实科研评审强制拆成：

#### `DOMAIN_BASELINE`

目标领域的普通专业规范。与大师无关。

#### `SCHOLAR_LENS`

只调用通过 Scholar Specificity Gate 的学者特异性 heuristic，并说明其 `scholar-added delta`。

#### `TRANSFER_INFERENCE`

解释为什么该学者的决策结构可以或不可以迁移到当前问题。低置信迁移只能作为问题生成器，不直接给建议。

详见 `references/advisor-three-layer.md`。

### 3. Distillation Grade

`depth` 是用户想做多深，`distillation_grade` 是证据实际允许蒸馏多深。

- `A_archival`：档案级，核心 Episode 有充分同期过程证据。
- `B_process_informed`：过程证据级，部分同期材料能约束重建。
- `C_retrospective`：公开回顾级，以论文 + 本人访谈/演讲为主。
- `D_publication_based`：成果轨迹级，主要只有正式论文和公开元数据。

每位学者还记录 evidence profile：过程证据覆盖、论文覆盖、本人回顾覆盖、第三方依赖、微观决策重建能力等。

详见 `references/distillation-grade.md`。

### 4. Transactional Staging

为避免 Agent 多次写文件时出现“manifest 写进去了、Episode 丢了几个”的半成品状态，v0.4 增加事务式 staging：

```text
.researchmind/staging/<job-id>/
   ↓
结构校验
   ↓
epistemic consistency validation
   ↓
全部通过
   ↓
atomic commit
   ↓
data/<scholar>/
```

单个 JSON 写入也使用临时文件 + `os.replace`。

详见 `references/transactional-pipeline.md`。

## Episode Type Gate

不是所有“人生大事件”都能用于蒸馏科研判断。

可直接参与科研 heuristic 的 Episode：

- `scientific_decision`
- `problem_framing`
- `method_choice`
- `anomaly_response`
- `theory_revision`

以下默认不能直接生成科研 heuristic：

- `career_decision`
- `research_program_strategy`
- `institution_building`
- `field_outcome`

这样可以避免把“回国办班”“建立研究院”“某领域几十年后终于工程化”等事件，硬当成某位学者的微观科研决策证据。

## 证据纪律

每个关键判断必须属于：

- `DIRECT_EVIDENCE`
- `CROSS_SOURCE_SYNTHESIS`
- `TRANSFER_INFERENCE`
- `INSUFFICIENT_EVIDENCE`

同时强制执行：

- Temporal Firewall
- Team Attribution
- Contrastive Distillation
- Scholar Specificity Gate
- Transfer Validator
- Abstention

结构校验通过不等于历史事实已经正确。年份、术语、原文、人物归属和因果链仍必须由 Agent 打开原始来源核验。

## 数据结构

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

生成的独立人物顾问：

```text
generated/<scholar-slug>-research-advisor/
├── SKILL.md
├── scholar_profile.json
├── source_registry.json
├── episodes/
└── heuristics/
```

## CLI

初始化：

```bash
python scripts/researchmind.py init-scholar "Geoffrey Hinton" --depth standard
```

复杂任务推荐事务式流程：

```bash
python scripts/researchmind.py stage-scholar "Geoffrey Hinton"
python scripts/researchmind.py commit-staged --job-id <job-id> --scholar geoffrey-hinton
```

校验：

```bash
python scripts/researchmind.py validate
python scripts/researchmind.py epistemic-validate
python scripts/researchmind.py epistemic-validate --scholar pauling
```

统计：

```bash
python scripts/researchmind.py stats --scholar pauling
```

统计会分别显示 discovered / inspected / claim-bearing sources，以及 specificity gate 状态。

生成独立人物 Skill：

```bash
python scripts/researchmind.py build-skill --scholar pauling
```

测试：

```bash
python -m unittest discover -s tests -v
```

## Evaluation

v0.4 的评测不仅看“像不像大师”，而是加入：

- historical reconstruction
- counterexample detection
- cross-domain transfer
- abstention
- Generic Baseline A/B
- Heuristic Laundering Test
- Framework Contamination Test
- Three-Layer Separation Test

真正的成功标准是：

> 这个 Scholar Advisor 是否提供了可回源、可区分、超出 generic baseline 的科研判断增量。

## Pauling Golden Set

`data/pauling/` 是当前第一个方法学参考样例。其 Distillation Grade 目前为 `B_process_informed`：已有较丰富档案与过程证据，但部分关键 contemporaneous objects 仍在 Primary Source Queue 中，因此没有为了“看起来成熟”而把 heuristic 强行升级成 validated。

## 项目状态

`v0.4.0-scholar-specificity-evidence-reliability`

当前重点不再是快速扩充更多科学家，而是解决三个更关键的问题：

1. 如何证明一条 heuristic 真正具有 Scholar Specificity；
2. 如何把通用领域审稿规范与大师认知透镜分开；
3. 如何让蒸馏数据在跨 Agent / 多工具写入时保持事务一致性。

## License

Apache-2.0
