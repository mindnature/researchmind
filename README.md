# ResearchMind

> 从科研历史中蒸馏可验证、可回源、可迁移但不过界的科研判断力。

ResearchMind 是一个面向 AI Agent / Codex 的科研决策蒸馏 Skill。它不试图模仿科学家的人格或口吻，而是从论文、研究笔记、手稿、通信、访谈、口述史和失败案例中重建“科研决策事件（Research Decision Episodes）”，再通过正反案例验证，提炼可用于新问题的科研启发式（Research Heuristics）。

首个实验对象是 `Pauling Research Skill`。项目当前验证的不是“AI 能否总结 Pauling”，而是一个更严格的问题：能否从可回源的科研历史中提炼出至少一条经得住成功/失败对比、能够迁移到新科研问题、且明确标注适用边界的科研判断规则。

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
- `TRANSFER_INFERENCE`：把已经验证或暂定的科研启发式迁移到一个新问题，并明确迁移置信度。
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

## Pauling Golden Set

当前包含 3 个经过第一轮证据升级的 Research Decision Episodes：

1. 1951 α-螺旋：高可信局部化学约束如何压缩结构搜索空间，以及研究者如何处理 5.1 Å 与约 5.4 Å 之间的冲突。
2. 1949 镰状细胞贫血：如何把氧依赖的细胞表型转译成可判别的血红蛋白分子测量，并保留 Pauling、Itano、Singer、Wells 等人的团队归因。
3. 1953 DNA 三螺旋：精确而漂亮的全局模型如何在数据不足、核心拥挤与关键约束未解决时继续推进，构成 α-螺旋案例的反例。

第一条核心启发式 `LP-H01-HARD-CONSTRAINT-FIRST` 已完成一次成功/失败对比蒸馏，但仍保持 `provisional`，没有提前升级为 `validated`。原因是最关键的 contemporaneous process records 仍未全部直接核验。

详细证据状态：[`data/pauling/GOLDEN_SET_STATUS.md`](data/pauling/GOLDEN_SET_STATUS.md)

一手档案待办：[`data/pauling/PRIMARY_SOURCE_QUEUE.md`](data/pauling/PRIMARY_SOURCE_QUEUE.md)

## 安装（Codex Skill）

可将仓库根目录作为 Skill 安装：

```text
使用 $skill-installer 安装：
https://github.com/mindnature/researchmind
```

安装后可以直接要求它审计真实科研问题，例如：

```text
$researchmind 用当前 Pauling ResearchMind 中证据强度足够的科研启发式审计这个选题：……
```

也可以提供新的公开科研档案，要求它按同一套 Episode → Contrast → Heuristic 方法继续扩展数据集。

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

## Pauling Golden Set 的主要公开来源入口

- Oregon State University：Pauling 46 本研究笔记概览（约 7,500 页）
  - https://news.oregonstate.edu/news/digital-research-collection-highlights-pauling-celebration
- OSU：Linus Pauling and the Structure of Proteins: A Documentary History
  - http://scarc.library.oregonstate.edu/coll/pauling/proteins/index.html
- Caltech：Linus Pauling Oral History Interview, 10 May 1984
  - https://digital.archives.caltech.edu/collections/OralHistories/OH_Pauling_L/
- 1951 PNAS α-螺旋论文（CaltechAUTHORS）
  - https://authors.library.caltech.edu/records/v4zz4-cqd29
- 1949 Science 镰状细胞贫血论文（CaltechAUTHORS）
  - https://authors.library.caltech.edu/records/ffg43-mm633
- OSU：Linus Pauling and the Race for DNA: A Documentary History
  - http://scarc.library.oregonstate.edu/coll/pauling/dna/index.html
- 1953 PNAS DNA 三螺旋论文
  - https://pubmed.ncbi.nlm.nih.gov/16578429/
- Nobel Prize 1954 Lecture: Modern Structural Chemistry
  - https://www.nobelprize.org/uploads/2018/06/pauling-lecture.pdf

## 项目状态

`v0.2.0-evidence-pass-1`

已完成：方法学骨架、三套 Schema、Temporal Firewall、Team Attribution、3 个 Pauling Episode 第一轮证据升级、H01 正反案例对比、H02 候选启发式、来源注册表、证据状态页、Primary Source Queue、校验器与测试。

下一阶段不扩人物。优先直接核验三个 P0 原始档案对象：1948 α-螺旋 contemporaneous notes/drawings、1952 年底 DNA notebooks/correspondence、Harvey Itano 1948 research report。只有这些 process-level primary sources 过关后，才考虑把 Episode 升为 `high`，把 H01 升为 `validated`。

## License

Apache-2.0
