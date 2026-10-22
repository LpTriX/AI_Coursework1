# PDDL 交接清单

用途：和宫成田对齐接口，避免两人各自建立不兼容的模型。此处记录已经达成的约定；未确认项不要当成既定实现。

当前状态：尚未收到宫成田实现的基础 domain 或 Mission 2；Part 2C 尚未实现。

## 请宫成田提供

- 基础 `domain.pddl` 和 `mission2.pddl` 的可运行版本，以及对应 Git commit。
- 使用的规划器、版本或服务名称、运行方式，以及找到的实际计划。
- 对象类型与层级、所有重要谓词的参数顺序和含义。
- 部署、移动、拍照、扫描、发送数据、拾取和存储样本的动作说明。
- 未部署状态、数据内存空闲状态、车辆样本容量、着陆器样本容量如何表示。
- 月球车与着陆器归属如何表示和约束。
- Mission 2 中第二个着陆器的降落地点选择及理由；Mission 3 必须沿用。
- 地图连接按 Figure 3 的箭头方向逐项核对的记录。

## 双方共同确认

| 事项 | 已确认的约定 |
| --- | --- |
| 基础版本 commit | 待交接 |
| 对象类型和参数顺序 | 待交接 |
| 车辆 / 着陆器归属表示 | 待交接 |
| 部署状态表示 | 待交接 |
| 数据类型、持有和已传输状态 | 待交接 |
| 内存与两种样本容量表示 | 待交接 |
| 发送、部署、存储动作名称 | 待交接 |
| 第二个着陆器的位置 | 待交接 |
| 测试规划器与运行方式 | 待交接 |
| 后续基础模型变更如何同步 | 待双方确认 |

## 原始文件与命名

| 部分 | 文件 | 内部名称 |
| --- | --- | --- |
| 基础 domain | `PDDL/PartA&B/domain.pddl` | domain `lunar` |
| Mission 1 | `PDDL/PartA&B/mission1.pddl` | problem `lunar-mission-1`，domain `lunar` |
| Mission 2 | `PDDL/PartA&B/mission2.pddl` | problem `lunar-mission-2`，domain `lunar` |
| 扩展 domain | `PDDL/PartC/domain-ext.pddl` | domain `lunar-extended` |
| Mission 3 | `PDDL/PartC/mission3.pddl` | problem `lunar-mission-3`，domain `lunar-extended` |

以上名称已与原始 starter 核对。此表只是交接信息，不表示这些文件已完成或已上传。

## 交接验收

- 基础模型能在允许的规划器上运行 Mission 2。
- 计划符合数据、样本、归属和方向限制，而不只是“规划器说找到计划”。
- 参数化动作不含写死的 waypoint、车辆或着陆器身份。
- 基础测试证据与真实 commit 对应。
- 你理解基础动作后再自行扩展 Part 2C；不把未理解的版本直接拼进最终文件。
