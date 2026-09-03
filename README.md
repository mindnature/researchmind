# ResearchMind

> 从科研历史中蒸馏可验证、可回源、可迁移但不过界的科研判断力。

ResearchMind 是一个面向 AI Agent / Codex 的科研决策蒸馏 Skill。它不试图模仿科学家的人格或口吻，而是从论文、研究笔记、手稿、通信、访谈、口述史和失败案例中重建“科研决策事件（Research Decision Episodes）”，再通过正反案例验证，提炼可用于新问题的科研启发式（Research Heuristics）。

首个 MVP 是 `Pauling Research Skill`，用于验证一个核心假设：能否从少量、可回源的真实科研事件中，提炼出至少一条经得住成功/失败对比、能够迁移到新科研问题、且明确标注边界的判断规则。

## 它和普通科研 RAG 有什么不同？

普通 RAG 更擅长回答：

- Pauling 关于蛋白质结构发表过什么？
- 某篇论文的结论是什么？

ResearchMind 重点回答：

- 当时有哪些已知信息、未知信息与候选解释？
- 研究者为什么选择 A，而不是 B？
- 哪个异常促使研究方向改变？
- 同一启发式在成功案例和失败案例中分别发生了什么？
- 这条启发式迁移到你的研究问题时，哪些结构保持不变，哪些前提已经破裂？

## 四种输出标签

ResearchMind 强制区分：

- `DIRECT_EVIDENCE`：原始材料明确支持。
- `CROSS_SOURCE_SYNTHESIS`：由两个及以上相互独立或不同类型证据综合得到。
- `TRANSFER_INFERENCE`：把已经验证的科研启发式迁移到一个新问题。
- `INSUFFICIENT_EVIDENCE`：材料不足，不应继续代替研究者补全。

任何新问题的诊断、规划或建议都不得伪装成历史人物本人说过的话。

## 核心流程

```text
Source Collector
      ↓
Source Normalizer
      ↓
Evidence Segmenter
      ↓
Research Episode Extractor
      ↓
Temporal Firewall + Team Attribution
      ↓
Heuristic Synthesizer
      ↓
Contrastive Validator
      ↓
Transfer Validator
      ↓
Research Advisor
      ↓
Evaluation Harness
```

## MVP 数据

第一版只提供 3 个 Pauling 事件的“可运行骨架”，不伪造手稿页码：

1. 1951 α-螺旋：硬约束驱动的结构建模成功案例。
2. 1949 镰状细胞贫血：从表型异常追溯到分子差异的团队研究案例。
3. 1953 DNA 三螺旋：漂亮模型在关键化学约束与数据不足下失败的反例。

未完成一手档案核对的字段会标记为 `needs_primary_source_review: true`。

## 安装（Codex Skill）

仓库上传后可将根目录作为 Skill 安装。推荐：

```text
使用 $skill-installer 安装：
https://github.com/<owner>/researchmind
```

安装后可直接说：

```text
$researchmind 用 Pauling 已验证的科研启发式审计这个选题：……
```

或：

```text
$researchmind 从这些公开科研档案中蒸馏一个新的科研人物 Skill：……
```

## 本地校验

无需第三方 Python 依赖：

```bash
python scripts/researchmind.py validate
python scripts/researchmind.py stats
python -m unittest discover -s tests
```

## 设计原则

1. Evidence first：结论强度不得高于证据强度。
2. Temporal firewall：只能用决策发生时已经可获得的信息解释当时判断。
3. No hero attribution：区分本人、合作者、实验人员、团队与后来的历史叙述。
4. Contrastive distillation：成功和失败必须成对研究。
5. Operational language：优先提炼可操作动作，不用抽象科学哲学词替代真实行为。
6. Transfer with boundaries：跨学科迁移必须检查结构同构与断裂前提。
7. Abstention is a feature：无法支持就明确拒答。
8. No impersonation：这是可回源科研顾问，不是“数字分身”。

## Pauling Golden Set 的公开来源入口

- Oregon State University：Pauling 46 本研究笔记概览（约 7,500 页）
  - https://news.oregonstate.edu/news/digital-research-collection-highlights-pauling-celebration
- OSU：Linus Pauling and the Structure of Proteins: A Documentary History
  - http://scarc.library.oregonstate.edu/coll/pauling/proteins/index.html
- OSU：Linus Pauling and the Race for DNA: A Documentary History
  - http://scarc.library.oregonstate.edu/coll/pauling/dna/index.html
- 1951 PNAS α-螺旋论文
  - https://pmc.ncbi.nlm.nih.gov/articles/PMC1063337/
- 1949 Science 镰状细胞贫血论文（CaltechAUTHORS）
  - https://authors.library.caltech.edu/records/ffg43-mm633
- 1953 PNAS DNA 三螺旋论文
  - https://pubmed.ncbi.nlm.nih.gov/16578429/
- Nobel Prize 1954 Lecture: Modern Structural Chemistry
  - https://www.nobelprize.org/uploads/2018/06/pauling-lecture.pdf

## 项目状态

`v0.1.0-mvp`：方法学骨架 + Pauling 三事件示例 + 校验器 + 评测设计。

下一阶段重点不是扩大人物数量，而是人工核验 3 个 Episode 的一手档案坐标，形成 Golden Set 后再评测启发式是否真的具有预测力和迁移价值。

## License

Apache-2.0
