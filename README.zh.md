# DELTA-X v2

**一个给科学 agent 的「发现」基准，在一个真实案例上从头到尾走通了一遍。**

[English](README.md) · [15 分钟上手](docs/00_START_HERE.md) · [封闭规则](docs/CONTAINMENT.md) · [已测结果](docs/RESULTS.md)

---

多数 agent 基准测的是「模型能不能把训练时见过的东西取回来」。这套题把那部分**减掉**：
每一个计分项的定义都保证**说出答案值 0 分，推导出答案才值分**——一个正确的区段如果没有
附上统计量，得 0；一个没有任何记录命令产出的数字，在评分之前就被划掉，对错都一样。

案例是同一个真核核苷酸转移酶家族里的两个旁系同源酶，它们在一个性质上不同——**顺式合成的
模板依赖性**。Agent 拿到 487 条序列、一个真实的 shell 和六道题。它拿不到区域名称、区域
数量，也拿不到文献。

**这套题不隐藏这两个蛋白是什么。** 盲化被实测过，不管用：三次零工具的闭卷运行里，
3/3 在第一句话就认出了家族。识别出来的部分会从分数里**扣掉**，而不是惩罚。

## 盒子里有什么

| | |
|---|---|
| **题目** | `tasks/` — 六份 brief，原文，和发给 agent 的一字不差 |
| **数据** | `data/` — 322 + 165 条物种唯一序列、7 条参考序列，268 KB，直接打包进来 |
| **测评框架** | `harness/` — 驱动、提示词组装、适配器、封闭审计、提交物打包 |
| **评分侧** | `grader/` — 答案键、评分规则、判分清单规格及其检查器 |
| **工具** | `env/` — 轻量层一条 conda 命令；GPU 层给的是老实的安装说明 |
| **复现** | `repro/` — 键里的每个数字，都能用随包的数据重新跑出来 |
| **结果** | `results/`、`grader/baselines/` — 两次实测 campaign，连原始记录一起 |

## 快速开始

```bash
git clone <本仓库> && cd delta-x
conda env create -f env/environment.yml && conda activate delta-x    # 轻量层，约 5 分钟
bash env/probe_env.sh ./ENVIRONMENT.md                               # 探测本机真实装了什么

# 先用 stub 把管道跑通，不花一个 token
harness/run_campaign.sh --run-id smoke --adapter stub --work ~/delta-x-runs --stages s1,s2

# 跑一次真实 campaign
harness/run_campaign.sh --run-id run1 --adapter claude_code --model opus \
    --work ~/delta-x-runs --environment ./ENVIRONMENT.md

# 评分
python3 -I harness/audit_containment.py  ~/delta-x-runs/run1      # 必做。exit 1 即该轮作废
python3 -I harness/collect_submission.py ~/delta-x-runs/run1 --out results/mine/run1
#   ... 按 grader/GRADING.md 评分，产出 results/mine/run1/scorecard.json ...
python3 -I grader/check_scorecard.py results/mine/run1/scorecard.json
python3 -I analysis/aggregate.py results/mine --label "我的系统" \
        --compare grader/baselines/BASELINE-v3-tooled/scorecards
```

要测**你自己的**系统，只需要写一个适配器——一个可执行文件，把一份提示词连同工作目录和
工具策略交给你的 agent。接口就一页：[`harness/adapters/README.md`](harness/adapters/README.md)，
`adapters/evoagenda.sh` 是模板，只有一行要填。Claude（Claude Code CLI）和 OpenAI／
OpenAI 兼容端点的适配器是现成可用的。

## 六道题

| 题 | 考察能力 | 工具 | 分 |
|---|---|---|---|
| DX01 | 会不会在**看数据之前**先提假设 | 无 | 0 —— 闸门；FAIL 则全场封顶 40 |
| DX02 | 能不能设计一个**可能失败**的方案：事先声明阈值、零假设、放弃条件 | 无 | 10 |
| DX02B | 把冻结的方案换算成**带数字和置信度**的预期 | 无 | 0 —— 只报，不计入总分 |
| DX03 | 能不能从序列**导出**区域，并知道自己的分辨率到哪一层 | MAFFT、HMMER、共进化、Python | 35 |
| DX04 | 能不能**选对统计量**——最显然的那个结构筛选会把正确答案排在两个错答案后面 | 结构预测、结构比对、PDB | 35 |
| DX05 | 能不能把几条独立证据合成一个**有边界**的结论，并说清它在哪里停 | 无 | 20 |

DX01、DX02、DX02B **完全不需要工具**，零安装即可运行。权重不是论证出来的，是按一次
实测闭卷基线定的：DX02 从 20 分砍到 10 分，就是因为旧 rubric 实测只能把三轮拉开
0.4 分（满分 20）。

## 四条跨题规则

1. **基线相减。** 一个零工具模型免费就能答对的项，值 0 分。说出那个区域的名字，值 0 分。
2. **溯源闸门。** 计分产物里任何一个没有 `execution_log.json` 记录背书的数字，在评分之前
   就被划掉——对错一样——而且它也不能再去支撑任何别的结论。
3. **判分清单就是分数。** 没有逐项对账的 `scorecard.json`，这个总分不得发布、引用或比较。
   `grader/check_scorecard.py` 是闸门。
4. **判伪造之前必须先做自复现检查。** 评分方要用记录的 `argv` 原样重跑**两次**，确认
   工具能复现**它自己**。MAFFT 只在固定线程数下确定；没有这条规则，一次诚实的多线程运行
   会被判成伪造。

## 封闭规则——跑任何东西之前先读

**本仓库里有答案键。** 读到 `grader/` 的 agent 不是被测量了，是被告知了。

- 驱动脚本**拒绝**在仓库内部起一次运行。
- `harness/audit_containment.py` 在读任何分数之前必须跑；命中即该轮**作废**——重跑，不是打折。
- 不要把点名本案例的 `CLAUDE.md`、`AGENTS.md` 之类放在受评 agent 会被启动的地方。
  本仓库自己的 `CLAUDE.md` 写得可以安全注入；设计者侧文档不行，清单在
  [docs/CONTAINMENT.md](docs/CONTAINMENT.md)。

## 目前的实测结果

两次 campaign 连原始记录一起随包发布。

| campaign | 系统 | n | 工具 | 覆盖范围 | 结果 |
|---|---|---|---|---|---|
| `BASELINE-v2-clean` | Claude Opus 5 | 3 | 全部封锁 | 只有 DX01、DX02 | 按现行规则重评 DX02：3.0 / 1.0 / 5.0 |
| `BASELINE-v3-tooled` | Claude Opus 5 | 5 | 真实 shell | 五道题全覆盖 | **均分 95.70 / 100，极差 5.0** |

最重要的结论不好听，而这正是它公开的理由：**这套题饱和了**，而机理是**判分规则跟题面
一起公开了**。提交物里现在直接出现以规则命名的字段——DX02 规则 2 在 14 个程序上
**一次都没命中**，DX03 的粒度罚则 5 轮**一次都没触发**。诚信面全程守住：0 次伪造、
0 次封闭泄漏、没有任何带分数的数字被划掉。下一版需要的是**重切题目、或把裁决规则移出
题面**，而不是在都贴着天花板的项之间挪权重。逐项区分度和两个负面结果见
[docs/RESULTS.md](docs/RESULTS.md)。

## 目录

```
tasks/      六份题面 + 一份 ENVIRONMENT.md 样例            受评 agent 可见
data/       发给 agent 的序列                              受评 agent 可见
harness/    驱动、提示词组装、适配器、审计
env/        工具安装，分三层
grader/     KEY.md、GRADING.md、SCORECARD.md、rubric、基线  设计者侧
repro/      键里每个数字背后的脚本与清单                    设计者侧
analysis/   判分清单 -> 表格、极差、逐项区分度
docs/       上手、封闭、评分、结果、FAQ                      设计者侧
results/    放你自己的 campaign
```

## 许可与引用

代码 MIT；题面、数据整理、答案键与文档 CC BY 4.0。见 [LICENSE](LICENSE) 与
[CITATION.cff](CITATION.cff)。如果你要发布一次测量，请把判分清单里的 `measured_scope`
一并写出来：**没有声明覆盖范围的分数，和声明了的分数不可比。**
