# Chengtian Gong — Part 1A and Parts 2A/2B: bilingual contribution draft

Status: contribution draft, not the complete group report. The pair must review the
content and merge Pinxin Liu's Part 1B and Part 2C sections. English prose is intended
for the final report; Chinese paragraphs support discussion and understanding.
Do not include both languages in the final report unless explicitly required.
The English paragraphs match `gong_contribution_english.md`.

状态：这是宫成田负责部分的双语草稿，不是完整小组报告。需要双方审阅，并合并
Pinxin Liu 的 Part 1B、Part 2C。英文用于最终报告，中文用于理解和讨论；最终报告
一般只留英文，否则容易超页。英文段落与 `gong_contribution_english.md` 一致。
姓名、学号、Canvas 组号和视频链接在最终标题页补齐。

## Part 1A — Sudoku as a CSP

### Variables and domains / 变量与取值域

A CSP is a set of variables, a domain of allowed values for each variable, and
constraints over combinations of values [2, 3]. Sudoku's variables are its 81
cells. Let X_rc be the digit in row r, column c, with r, c in {1,...,9}. A blank
cell can end up as any digit, so D_rc = {1,...,9}. A cell that starts with a clue
g_rc is fixed: D_rc = {g_rc}. The clues never change, and the input marker 0 is
not a solution value.

CSP 由变量、每个变量的允许取值，以及取值组合上的限制三部分组成 [2, 3]。
数独的变量就是 81 个格子：X_rc 表示第 r 行第 c 列的数字，r,c ∈ {1,...,9}。
空格最后可以填任何数字，所以 D_rc = {1,...,9}；一开始就给了线索 g_rc 的格子
直接固定为 D_rc = {g_rc}。题目给的线索不能改，输入里表示空格的 0 也不属于解。

### Constraints / 约束

Every row imposes AllDifferent(X_r1, ..., X_r9), for r in {1,...,9}, and every
column imposes AllDifferent(X_1c, ..., X_9c), for c in {1,...,9}. Every 3x3 box
imposes AllDifferent over its nine cells: AllDifferent({X_(3a+i,3b+j) : i,j in
{1,2,3}}), for a,b in {0,1,2}. That gives 27 constraints in total. Together with
the domains they force each digit 1-9 to appear exactly once in every row, column
and box. A solution is a complete assignment that satisfies all of them and keeps
every clue.

每行一条 AllDifferent(X_r1,...,X_r9)，r ∈ {1,...,9}；每列一条
AllDifferent(X_1c,...,X_9c)，c ∈ {1,...,9}。每个 3×3 九宫格对它的九个格子也有一条
AllDifferent({X_(3a+i,3b+j) | i,j ∈ {1,2,3}})，a,b ∈ {0,1,2}。加起来一共 27 条约束。
它们加上取值域，就保证每行、每列、每个宫里的 1–9 各出现一次。解是满足全部约束、
并且保留所有线索的完整赋值。

### Search complexity and pruning / 搜索复杂度与剪枝

Let m be the number of blank cells. Enumerating all assignments means checking 9^m
complete candidates. If checking one candidate costs fixed time on this fixed 9x9
board, the upper bound is O(9^m). Backtracking fills one blank at a time and checks
consistency before moving on [2, 4]. Without pruning its tree has at most
1 + 9 + ... + 9^m nodes, so O(9^m) is also a coarse worst-case upper bound for
backtracking — not a tight bound for every Sudoku instance. If constraint checking
is counted separately, its cost multiplies the node bound. Here m measures the work
on the fixed board size; this is not an asymptotic hardness claim for fixed 9x9
Sudoku.

设 m 是空格数。穷举所有赋值要检查 9^m 个完整候选；在固定 9×9 棋盘上，如果检查一个
候选的代价是常数，上界就是 O(9^m)。回溯每次只填一个空格，填之前先检查一致性 [2, 4]。
不剪枝时搜索树最多有 1 + 9 + ... + 9^m 个节点，所以 O(9^m) 也是回溯最坏情况的一个
粗略上界——不是每个数独实例都能达到的紧界。如果把约束检查单独算代价，还要乘到节点界上。
这里的 m 衡量的是固定棋盘上的工作量，我们不是在给固定 9×9 数独下渐近难度的结论。

Pruning stops a partial assignment as soon as it repeats a digit in a row, column
or box. Filling the remaining cells cannot fix that, so the whole subtree below the
bad assignment can be skipped without losing any solution. A conflict found with k
blanks left avoids up to 9^k complete extensions. In practice this usually cuts the
search a lot, but it does not give a polynomial worst-case bound. MRV, forward
checking and constraint propagation can cut it further [2]. When we describe the
actual solver, we should only name techniques it really implements.

剪枝的做法是：局部赋值一旦在行、列或宫里重复了数字就立刻停下。继续填空格也救不回这个
冲突，所以这个赋值下面的整棵子树都可以跳过，不会漏掉任何解。还剩 k 个空格时发现冲突，
最多可以省掉 9^k 个完整扩展。实际中剪枝一般能省下大量搜索，但它给不出多项式最坏时间界。
MRV、前向检查、约束传播还能继续减少探索 [2]；描述实际程序时，我们只提它真正实现了的技术。

## Parts 2A and 2B — Lunar planning

### Representation and assumptions / 表示与假设

The `lunar` domain uses only `:strips` and `:typing`. The types are `rover`,
`lander` and `waypoint`. `belongs-to` records which lander owns each rover,
`lander-at` fixes each landing site, and `connected` gives the directed roads.
`aboard` marks an undeployed rover; `rover-at` gives a deployed rover's current
waypoint. Deployment deletes the aboard fact and puts the rover at its own lander's
site; movement deletes the old location. Every action is parameterised — no action
rule names a particular mission object. We assume the initial state is well formed:
each rover has exactly one owner and exactly one aboard/location state, and each
lander has one fixed site.

`lunar` 域只用了 `:strips` 和 `:typing`，类型是 rover、lander、waypoint。
`belongs-to` 记录每辆车属于哪个着陆器，`lander-at` 固定着陆位置，`connected` 是有向道路。
`aboard` 表示还没部署的车，`rover-at` 是已部署车辆当前的地点。部署删掉 aboard 并把车放到
自己着陆器的位置；移动删掉旧位置。所有动作都是参数化的，没有哪个动作规则写死了具体任务里
的对象。我们假设初始状态是良构的：每辆车恰有一个归属、恰有一个 aboard/位置状态，每个
着陆器有固定地点。

### Capacity and completion / 容量与完成条件

`memory-free` is a single token shared by images and scans. Capturing either kind
of data consumes it. Transmitting held data restores it and records `image-saved`
or `scan-saved` at the receiving lander. Transmission requires ownership, the rover’s current location and the corresponding held data: the
rover does not have to be at the lander or to have visited it before. The source
waypoint records where the data came from; the current waypoint records where the
rover is now. So acquiring data on its own never satisfies a saved-data goal.

`memory-free` 是图像和扫描共用的一个令牌。获取任意一种数据都会消耗它；把手里数据发出去
会恢复它，并在接收着陆器记录 `image-saved` 或 `scan-saved`。发送还要求当前位置和已持有的对应数据，并检查归属——车不必在
着陆器旁边，也不必之前去过。source 记录数据在哪采的，current 记录车现在在哪。所以光获取
数据不能满足保存目标。

Samples use a separate `sample-free` token, so a rover can carry one sample and
one unsent data item at the same time. Collection consumes the token.
`store-sample` requires the rover and its own lander to share a waypoint; it
restores the rover's sample token, consumes the lander's `storage-free` token,
and records the sample's origin in `sample-stored`. No action restores lander
storage, so each lander stores at most one sample. The specification puts no
limit on the sample stock at a waypoint, so the domain adds no source-exhaustion
rule. We also add no sample-type or data-size distinctions.

样本用的是另一个 `sample-free` 令牌，所以一辆车可以同时带一个样本和一条未发送的数据。
采集消耗这个令牌；`store-sample` 要求车和自己的着陆器在同一地点，恢复车的样本令牌、
消耗着陆器的 `storage-free`、并把样本来源记进 `sample-stored`。没有任何动作恢复着陆器的
存储空间，所以每个着陆器最多存一个样本。题目没有限制地点上的样本数量，域里也就不加样本
耗尽规则；我们也没有加样本种类或数据大小的区分。

### Mission configuration / 任务设置

Mission 1 fixes Lander 1 at WP1 and starts Rover 1 aboard it. Figure 2 is encoded
as six directed edges. The goals require an image from WP5 and a scan from WP3
saved at Lander 1, plus a WP1 sample stored there. Mission 2 keeps Lander 1 and
the already deployed Rover 1 at WP2, as required. Lander 2 is fixed at WP1 with
Rover 2 aboard at the start. This choice (which the spec permits) makes storing
the WP1 sample straightforward, and Mission 3 must keep it. Figure 3 has nine
directed edges. All six goals name their receiving lander, so ownership splits
them three per rover. Both missions run on the same domain with no changes [1].

Mission 1 把 Lander 1 固定在 WP1，Rover 1 一开始在它舱内；图 2 编码为六条有向边。
目标是 WP5 的图像、WP3 的扫描存到 Lander 1，外加 WP1 的样本存进去。Mission 2 保留
题目要求的 Lander 1 和已部署 Rover 1 的 WP2 位置；Lander 2 选在 WP1，Rover 2 一开始
在舱内。这个选择（题目允许）让 WP1 的样本存储变得直接，Mission 3 也要保持。图 3 有九条
有向边。六个目标都写明接收着陆器，归属关系把目标分成每辆车三个。两个任务用同一个域，
没有任何改动 [1]。

### Validation and limitations / 测试与局限

In the saved run, Pyperplan 2.1 [5] with greedy best-first search and hFF found a
10-action plan for Mission 1 and a 20-action plan for Mission 2. We then replayed
each plan step by step against a separate implementation of the specification's
rules: every PDDL effect was compared with the expected state change, and location
and capacity invariants were checked after every step. All goals held at the end.
The checks included wireless transmission after leaving the data source, and
samples physically returning to the lander. The plans are valid solutions; we did
not check whether they are shortest.

保存的运行里，Pyperplan 2.1 [5] 用贪心最佳优先搜索加 hFF，给 Mission 1 找到 10 步计划、
Mission 2 找到 20 步。之后我们把每一步计划按另一份独立的题目规则实现重放：每个 PDDL 效果
都和预期状态变化比对，每步之后检查位置和容量不变量。结束时全部目标成立。检查包括离开
数据来源地之后的无线发送，以及样本真正带回着陆器。这些计划是有效解；我们没有检查它们
是否最短。

A further check compared 2,496 typed action instances in 16 constructed, coherent
states. All 63 allowed instances produced the expected effects, and all 2,433
forbidden instances were rejected. The cases covered reverse roads, sending data
that was never acquired, full memory, independent sample/data slots, remote sample
storage, full lander storage, and wrong ownership even when two landers share a
waypoint. Another instance renamed every rover, lander and waypoint and added a
third rover/lander pair with one extra image goal; the unchanged domain found a
valid 23-action plan. These are targeted checks, not an exhaustive test of every
reachable state. Raw plans, state traces, logs, file hashes and environment details
are saved in `evidence/base-pddl/`. Mission 3 and its astronaut tests are the
partner's separate work.

另一项检查在 16 个构造的一致状态上比较了 2,496 个带类型的动作实例：63 个允许的实例
效果全部正确，2,433 个禁止的实例全部被拒。覆盖的情形有反向道路、发送没采过的数据、
内存满、样本槽和数据槽独立、远程存样、着陆器存储已满、两个着陆器同地点时归属错误。
还有一个实例把所有 rover、lander、waypoint 都重命名，加了第三对车和着陆器以及一个额外
图像目标；没改动的域给出了有效的 23 步计划。这些是有针对性的检查，不是对每个可达状态的
穷尽测试。原始计划、状态轨迹、日志、文件哈希和环境信息都存在 `evidence/base-pddl/`。
Mission 3 和宇航员测试是队友单独的工作。

## References / 参考文献

[1] F29AI teaching team. *Coursework 1: Search and Automated Planning*, 2026,
pp. 2, 4–10, 13, 15. Local file: F29AI_2026_cw1.pdf.

[2] Russell, S. and Norvig, P. *Constraint Satisfaction Problems*, official AIMA
teaching slides, slides 3, 7, 11–13 and 18–21. The public slide file labels this
material Chapter 5; do not confuse that label with textbook edition chapter numbers.
https://aima.cs.berkeley.edu/4th-ed/slides-pdf/chapter05.pdf

[3] UC Berkeley CS188. *2.1 Constraint Satisfaction Problems*.
https://inst.eecs.berkeley.edu/~cs188/textbook/csp/csps.html

[4] UC Berkeley CS188. *2.2 Solving Constraint Satisfaction Problems*.
https://inst.eecs.berkeley.edu/~cs188/textbook/csp/solving.html

[5] Pyperplan contributors. *Pyperplan*, version 2.1.
https://github.com/aibasel/pyperplan

Web sources checked on 25 October 2026. The complexity calculation above is our
explicit search-tree derivation; the references support the CSP and backtracking concepts.

## Merge notes — exclude from final prose / 合并提示，不放入最终正文

- Reserve about one page for Part 1A, leaving up to three for Part 1B.
- Reserve about two pages for Parts 2A/2B, leaving about one for Part 2C.
- These are suggested allocations within shared limits, not additional allowances.
- Replace internal file pointers with concise evidence descriptions if space is tight.
- Add the group's cover page, member details, and video link.
- Do not claim Part 1B, Part 2C, the combined report, video, or submission are complete.

- Part 1A 留一页左右，Part 1B 最多三页。
- Parts 2A/2B 留两页左右，Part 2C 约一页。
- 这是在共享页数内的建议分配，不是额外增加页数。
- 空间紧张时把内部文件链接换成简短的证据说明。
- 补上小组实际的封面页、成员信息和视频链接。
- 不要声称 Part 1B、Part 2C、合并报告、视频或提交已完成。
