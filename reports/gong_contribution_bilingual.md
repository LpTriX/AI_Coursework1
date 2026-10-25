# Chengtian Gong — Part 1A and Parts 2A/2B: bilingual contribution draft

Status: contribution draft, not the complete group report. The pair must review the
content and merge Pinxin Liu's Part 1B and Part 2C sections. English prose is intended
for the final report; Chinese paragraphs support discussion and understanding.
Do not include both languages in the final report unless explicitly required.

状态：这是宫成田负责部分的双语草稿，不是完整小组报告。需要双方审阅，并合并
Pinxin Liu 的 Part 1B、Part 2C。英文用于最终报告，中文用于理解和讨论；最终报告
通常只保留英文，否则容易超页。姓名、学号、Canvas 组号和视频链接在最终标题页补齐。

## Part 1A — Sudoku as a CSP

### Variables and domains / 变量与取值域

A CSP describes variables, their permitted values, and restrictions on combinations
of values [2, 3]. For Sudoku, let X = {X_rc | r,c in {1,...,9}}, where X_rc is the
digit in row r and column c. There are 81 variables. For a blank cell,
D_rc = {1,...,9}; for a given clue g_rc, D_rc = {g_rc}. Thus, clues cannot change,
and the input marker 0 is not a solution value.

CSP 用变量、允许取值和取值组合的限制描述问题 [2, 3]。令
X = {X_rc | r,c ∈ {1,...,9}}，其中 X_rc 表示第 r 行、第 c 列的数字，共 81 个变量。
空格的取值域为 {1,...,9}；已给定数字 g_rc 的格子取值域为单元素集合 {g_rc}。
所以原有线索不能改变，输入中的 0 也不属于解的取值。

### Constraints / 约束

Impose AllDifferent(X_r1,...,X_r9) for each r in {1,...,9}, and
AllDifferent(X_1c,...,X_9c) for each c in {1,...,9}. For every a,b in {0,1,2},
impose AllDifferent({X_(3a+i,3b+j) | i,j in {1,2,3}}) on the corresponding
3-by-3 box. These 27 AllDifferent constraints, together with the domains, ensure
that every row, column and box contains each digit 1–9 exactly once. A solution
is a complete assignment satisfying all constraints and preserving all clues.

对每一行 r，要求 AllDifferent(X_r1,...,X_r9)；对每一列 c，要求
AllDifferent(X_1c,...,X_9c)。对所有 a,b ∈ {0,1,2}，相应九宫格满足
AllDifferent({X_(3a+i,3b+j) | i,j ∈ {1,2,3}})。27 个 AllDifferent 约束结合取值域，
保证每一行、每一列和每个九宫格中的 1–9 各出现一次。解是满足所有约束并保留线索的完整赋值。

### Search complexity and pruning / 搜索复杂度与剪枝

Let m be the number of blank cells. Enumerating all assignments tries 9^m complete
candidates. With fixed-cost checking for this fixed 9-by-9 board, this gives an
O(9^m) upper bound. Backtracking assigns one blank at a time and checks consistency
before continuing [2, 4]. Its unpruned tree has at most 1 + 9 + ... + 9^m nodes,
so O(9^m) is also a coarse worst-case upper bound; this is not a tight bound for
every Sudoku instance. If constraint-checking work is modelled separately, it
multiplies the search-node bound. Here m parameterises the work within the fixed
board size, rather than asserting an asymptotic hardness result for fixed 9-by-9 Sudoku.

令 m 为空格数量。枚举全部赋值会尝试 9^m 个完整候选。在固定 9×9 棋盘、单次检查成本
视为常数的口径下，其上界为 O(9^m)。回溯每次只给一个空格赋值，并先检查一致性再继续
[2, 4]。未经剪枝的搜索树最多有 1 + 9 + ... + 9^m 个节点，因此 O(9^m) 也是一个粗略的
最坏情况上界，并非每个数独实例都能达到的紧确界。若把约束检查成本单独计算，应再乘上
相应成本。这里用 m 描述固定棋盘内的工作规模，而不是声称固定 9×9 数独具有某种渐近困难性。

Pruning rejects a partial assignment as soon as it repeats a digit in a row, column
or box. Such a conflict cannot be repaired by assigning the remaining blanks, so
all descendants of that assignment can be skipped without losing a valid solution.
For example, a conflict with k blanks remaining avoids exploring up to 9^k complete
extensions. This often reduces practical work substantially, but does not establish
a polynomial worst-case bound. MRV, forward checking and propagation can further
reduce exploration [2]; these techniques should be discussed as properties of the
implemented solver only where they are actually present.

剪枝在局部赋值出现行、列或九宫格重复时立即停止。继续填其他空格不能修复已经产生的冲突，
因此可以安全跳过该节点的全部后代。例如，发现冲突时若还剩 k 个空格，就可能避免检查最多
9^k 个完整扩展。它通常显著减少实际搜索量，但不能据此得出多项式最坏时间。
MRV、前向检查和约束传播还可能进一步减少探索 [2]；描述实际程序时，只能声称实现了确实存在的技术。

## Parts 2A and 2B — Lunar planning

### Representation and assumptions / 表示与假设

The `lunar` domain uses only `:strips` and `:typing`, with types `rover`, `lander`
and `waypoint`. `belongs-to` fixes ownership, `lander-at` fixes landing sites,
and `connected` records directed roads. `aboard` and `rover-at` distinguish
undeployed rovers from deployed ones. Deployment removes the aboard fact and
places the rover at its own lander; movement removes the previous location.
Every action is parameterised, with no mission-specific object names in its rules.
This model assumes well-formed initial states: each rover has one owner and one
location or aboard state, and each lander has one stationary landing site.

`lunar` 只使用 `:strips`、`:typing`，对象类型为 rover、lander、waypoint。
`belongs-to` 固定归属，`lander-at` 固定着陆位置，`connected` 表示有向道路。
`aboard` 和 `rover-at` 区分未部署与已部署车辆。部署删除 aboard 状态，并把车辆放到
所属着陆器的位置；移动删除旧位置。全部动作都使用参数，没有写死具体任务中的对象。
模型假定初始状态合法：车辆有且仅有一个归属，并且要么在舱内、要么位于一个地点；
每个着陆器有一个固定着陆位置。

### Capacity and completion / 容量与完成条件

`memory-free` is a single token shared by images and scans. Acquiring either kind
consumes it; transmitting held data restores it and records `image-saved` or
`scan-saved` at the receiving lander. Transmission checks ownership but has no
co-location or previous-visit condition. Its source waypoint identifies where the
data was acquired; its current waypoint identifies the rover's present position.
Acquisition alone cannot satisfy a saved-data goal.

`memory-free` 是图像和扫描共用的一个空闲标记。获取任一数据会消耗它；发送已持有的数据
会恢复它，并在接收着陆器记录 `image-saved` 或 `scan-saved`。发送检查归属，但不要求
位置相同或过去访问过着陆器。source 参数表示数据来源，current 参数表示车辆当前位置，
两者可以不同。仅获取数据不能满足保存目标。

Samples use a separate `sample-free` token, so a rover may carry one sample and
one unsent data item together. Collection consumes that token. `store-sample`
requires the rover and its own lander to share a waypoint, restores the rover's
sample token, consumes the lander's `storage-free` token, and records provenance
in `sample-stored`. No action restores lander storage. Consequently each lander
stores at most one sample. The specification does not impose a finite stock of
samples at a source waypoint, so no additional source-exhaustion restriction is
introduced. No sample type or data-size distinctions are added.

样本使用独立的 `sample-free` 标记，因此车辆可以同时携带一个样本和一项未发送数据。
采样消耗样本空闲标记；`store-sample` 要求车辆与其所属着陆器位于同一地点，恢复车辆样本槽，
消耗着陆器的 `storage-free`，并在 `sample-stored` 中保留样本来源。没有动作恢复着陆器存储空间，
因此每个着陆器最多存一个样本。题目未规定某地点的样本有限，故未额外添加样本源耗尽限制，
也没有自行加入样本类别或数据大小限制。

### Mission configuration / 任务设置

Mission 1 fixes Lander 1 at WP1 and starts Rover 1 aboard it. Figure 2 is encoded
with six directed edges. Its goals require an image from WP5 and a scan from WP3
saved at Lander 1, plus a WP1 sample stored there. Mission 2 preserves the required
WP2 positions of Lander 1 and deployed Rover 1. Lander 2 is fixed at WP1 with
Rover 2 initially aboard. This permitted choice makes the WP1 sample storage
straightforward and must be retained in Mission 3. Figure 3 has nine directed
edges. All six goals name their required receiving lander; ownership therefore
assigns three goals to each rover. Both missions use the same domain unchanged [1].

Mission 1 把 Lander 1 固定在 WP1，Rover 1 初始位于其舱内；图 2 编码为六条有向边。
目标是将 WP5 图像、WP3 扫描保存到 Lander 1，并把 WP1 样本存入其中。
Mission 2 保留题目指定的 Lander 1、已部署 Rover 1 的 WP2 初始位置；Lander 2 选择 WP1，
Rover 2 初始未部署。该选择便于完成 WP1 样本存储，Mission 3 应保持一致。
图 3 编码为九条有向边。六个目标都指定接收着陆器，因此归属关系使每辆车各承担三个目标。
两项任务使用完全相同的 domain [1]。

### Validation and limitations / 测试与局限

Pyperplan 2.1 [5], using greedy best-first search with the hFF heuristic, found a
10-action plan for Mission 1 and a 20-action plan for Mission 2 in the saved run.
Every action was replayed against a separate implementation of the specification's
rules, comparing PDDL effects with expected state changes and checking location
and capacity invariants. All mission goals held at the end. The checks included
wireless transmission after leaving a data source and physical sample return.
The plans are valid solutions; no shortest-plan claim is made.

保存的实际运行中，Pyperplan 2.1 [5] 使用 hFF 启发式的贪心最佳优先搜索，为 Mission 1、2
分别找到 10 步、20 步计划。测试程序用独立实现的题目规则逐步重放计划，比较 PDDL 动作效果
与预期状态变化，同时检查位置和容量不变量；最终全部目标成立。检查包括离开数据来源地点后
无线发送，以及把样本实际带回着陆器。这些是有效计划，不声称最短。

A further check compared 2,496 typed action instances across 16 constructed,
coherent states: 63 allowed instances had the expected effects, and 2,433 forbidden
instances were rejected. Cases included reverse roads, sending unacquired data,
full memory, independent sample/data slots, remote sample storage, full lander
storage, and incorrect ownership even for co-located landers. An additional
instance renamed every rover, lander and waypoint, added a third rover and lander,
and required an extra image; the unmodified domain found a valid 23-action plan.
These are targeted checks, not exhaustive verification of every reachable state.
Raw plans, state traces, logs, file hashes and environment details are saved in
`evidence/base-pddl/`. Mission 3 and its astronaut tests are the partner's separate work.

另一项检查在 16 个构造的合法状态下比较了 2,496 个带类型的动作实例：63 个允许实例的效果正确，
2,433 个禁止实例均被拒绝。包括逆行、发送未获取数据、内存满、数据槽与样本槽独立、远程存样、
着陆器存储已满，以及即使着陆器同地点也禁止跨归属操作。额外实例重命名全部车辆、着陆器与地点，
加入第三辆车和第三个着陆器及额外图像目标；未经修改的 domain 找到有效的 23 步计划。
这些是针对性检查，不是全部可达状态的穷尽验证。原始计划、状态轨迹、日志、文件哈希和环境信息
均保存在 `evidence/base-pddl/`。Mission 3 及宇航员测试仍由队友单独完成。

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
explicit search-tree derivation; the references support CSP and backtracking concepts.

## Merge notes — exclude from final prose / 合并提示，不放入最终正文

- Reserve about one page for Part 1A, leaving up to three for Part 1B.
- Reserve about two pages for Parts 2A/2B, leaving about one for Part 2C.
- These are suggested allocations within shared limits, not additional allowances.
- Replace internal file pointers with concise evidence descriptions if space is tight.
- Add the group's cover page, member details, and video link.
- Do not claim Part 1B, Part 2C, the combined report, video, or submission are complete.
