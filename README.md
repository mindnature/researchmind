# ResearchMind

> 安装一次，输入一个学者名字，把公开科研材料蒸馏成一个可回源、能帮你做科研判断的专家 Skill。

ResearchMind 是一个通用型科研蒸馏 Skill。它不是论文摘要器，也不是“名人数字分身”。它要做的是从论文、研究笔记、手稿、通信、访谈、口述史、团队记录和失败案例中重建 Research Decision Episodes，再从正反案例中提炼具有边界条件的 Research Heuristics。

## 安装后怎么用

在 Codex / 支持 Skill 的 Agent 中安装仓库根目录：

```text
使用 $skill-installer 安装：
https://github.com/mindnature/researchmind
```

然后可以只输入一个名字：

```text
$researchmind 蒸馏 Geoffrey Hinton
```

也可以指定重点和深度：

```text
$researchmind 蒸馏丹尼尔·卡尼曼，重点研究他如何设计实验和处理反例
```

```text
$researchmind 蒸馏屠呦呦，使用 deep 模式
```

如果你已经有论文、手稿、访谈、课程转写或本地档案，也可以直接一起提供。

## ResearchMind 会自动做什么

```text
学者名字
   ↓
身份确认与同名消歧
   ↓
建立 scholar profile
   ↓
自动发现论文 / 档案 / 手稿 / 通信 / 访谈 / 口述史 / 科学史资料
   ↓
建立可回源 Source Registry
   ↓
扫描研究生涯中的关键科研决策事件
   ↓
重建 Research Episodes
   ↓
Temporal Firewall + Team Attribution
   ↓
寻找成功 × 失败 × 转向 × 边界案例
   ↓
Contrastive Distillation
   ↓
提炼 Research Heuristics
   ↓
Transfer Validator + Evaluation
   ↓
生成 <scholar>-research-advisor Skill
```

## 它蒸馏的不是“名言”，而是科研动作

普通人物总结容易得到：

> 这个科学家很有好奇心、坚持、第一性原理思维。

ResearchMind 要得到的是类似：

> 当全局解释自由度很高时，先列出不确定性显著更低、且有独立证据支持的局部约束；只在这些约束内生成候选模型。若候选模型持续违反硬约束，优先更换模型拓扑，而不是继续增加自由参数。

这种规则才能被用于新的选题、假设、研究设计和异常结果判断。

## 四种蒸馏深度

### quick

适合先判断一个学者值不值得深挖。

- 5–10 个高质量来源
- 至少 3 个 Episode
- 1–3 条 candidate / provisional heuristic

### standard（默认）

适合大多数科研人物。

- 20–40 个关键来源
- 5–10 个 Episode
- 3–7 条 heuristic
- 主动寻找至少 2 组支持/反例结构

### deep

加入论文之外的过程证据：档案、通信、草稿、团队材料、失败史和方法转向。

### golden

逐条核验关键页码、档案号、时间码和一手科研过程材料。适合精品开源、方法学研究和高可信科研判断。

## 不是每个学者都能蒸馏到同样深度

ResearchMind 会标记 `source_availability_ceiling`：

- `publication_only`：主要只有论文。
- `public_retrospective`：论文 + 本人访谈/演讲。
- `process_evidence`：存在笔记、手稿、通信、草稿等过程材料。
- `golden_archive`：核心 Episode 有直接过程证据、团队材料和反例，可做高置信蒸馏。

“通用”意味着可以从任何可识别学者开始，不意味着所有人都能被高置信还原。

## 证据纪律

每个关键判断必须属于以下之一：

- `DIRECT_EVIDENCE`：来源直接支持。
- `CROSS_SOURCE_SYNTHESIS`：多来源综合，不能伪装成学者原话。
- `TRANSFER_INFERENCE`：把启发式迁移到你的新科研问题。
- `INSUFFICIENT_EVIDENCE`：资料不足，停止补全。

同时强制执行：

- Temporal Firewall：不能用后来知道的正确答案解释早期决定。
- Team Attribution：不能把团队科研神化成一个人的行为。
- Contrastive Distillation：高手成功和翻车都要研究。
- Transfer Validator：跨学科只能迁移决策结构，不能做漂亮类比。
- Abstention：材料不够时必须拒绝代替学者“发言”。

## 通用数据结构

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

最终人物专家：

```text
generated/<scholar-slug>-research-advisor/
├── SKILL.md
├── scholar_profile.json
├── source_registry.json
├── episodes/
└── heuristics/
```

## CLI

ResearchMind 的 CLI 只负责脚手架、结构校验和打包；来源搜索与学术判断由安装了 Skill 的 Agent 按 `SKILL.md` 执行。

初始化任意学者：

```bash
python scripts/researchmind.py init-scholar "Geoffrey Hinton" --depth standard
```

中文姓名也支持；如需可读英文目录名，可显式指定 slug：

```bash
python scripts/researchmind.py init-scholar "屠呦呦" --slug tu-youyou --depth deep
```

查看已经初始化的人物：

```bash
python scripts/researchmind.py list-scholars
```

校验：

```bash
python scripts/researchmind.py validate
python scripts/researchmind.py validate --scholar pauling
```

统计：

```bash
python scripts/researchmind.py stats
python scripts/researchmind.py stats --scholar pauling
```

生成独立人物 Skill：

```bash
python scripts/researchmind.py build-skill --scholar pauling
```

测试：

```bash
python -m unittest discover -s tests -v
```

仓库包含 GitHub Actions CI，用于自动运行结构校验、单元测试和参考人物 Skill 打包测试。

## Pauling Golden Set

`data/pauling/` 现在只是 ResearchMind 的第一个高质量参考样例，不再是代码特例。

当前已建立：

- α-螺旋结构建模 Episode
- 镰状细胞贫血分子病 Episode
- DNA 三螺旋失败 Episode
- `Hard-constraint-first model reduction` 正反案例启发式
- Primary Source Queue

这套样例用于验证 ResearchMind 的方法，而不是限制 ResearchMind 只能蒸馏 Pauling。

## 通用执行协议

- `SKILL.md`：Agent 主入口
- `references/universal-distillation.md`：从人名到人物 Skill 的完整流程
- `references/source-discovery.md`：自动学术资料发现协议
- `schemas/scholar_profile.schema.json`：人物档案 Schema
- `schemas/episode.schema.json`：科研决策 Episode
- `schemas/heuristic.schema.json`：科研启发式

## 项目状态

`v0.3.0-universal-scholar-distiller`

当前版本已经完成“Pauling 原型 → 通用人物蒸馏框架”的工程解耦：核心 Skill 接受任意学者名字，数据目录按 scholar 隔离，CLI 支持初始化任意学者并生成独立科研顾问 Skill。

下一阶段重点是用第二位、第三位学者做真实 end-to-end 测试，检验通用流程在不同学科和不同档案可得性条件下是否稳定。

## License

Apache-2.0
