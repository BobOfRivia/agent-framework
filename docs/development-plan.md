# 开发计划与可领取工作包

状态：v0.1，2026-11-15。依赖 [PRD](product-requirements.md)、[领域合同](domain-model.md) 与 [验收标准](acceptance.md)。当前全部待实现，详见 [状态记录](implementation-status.md)。

## 1. 交付原则

先验证上游兼容性，再交付可运行纵切面：创建 Task -> 独立 worker -> 真正工具执行 -> 持久状态 -> 产物 -> 审阅。UI、Creator 和团队能力逐步接入同一链路，不建立彼此独立的演示系统。

[复用策略](architecture/reuse-strategy.md)为实施约束：开发产品语义与薄适配，复用现成执行、检查点、调度、沙箱、浏览器、文件和观测能力。下面的服务名称表示业务责任，不要求自行实现对应通用基础设施。

每个工作包提交代码、必要测试、实际命令结果、合同变更和下一会话交接。工作量 S/M/L 表示相对复杂度，非工期承诺；M0 后依据可用人员、模型预算和沙箱实验再估时。

```mermaid
flowchart LR
    M0["M0 兼容性与工程"] --> M1["M1 持久任务内核"]
    M1 --> M2["M2 真正Agent与沙箱"]
    M2 --> M3["M3 本地与授权恢复"]
    M3 --> M4["M4 群聊与统筹协作"]
    M4 --> M5["M5 配置式Creator"]
    M5 --> M6["M6 编码扩展发布"]
    M6 --> M7["M7 部署与验收"]
```

## 2. 里程碑

| 阶段 | 可演示结果 | 必须通过的 gate |
| --- | --- | --- |
| M0 | 已锁定依赖、checkpoint/审批/sandbox spike、调度选型 | 安装可重现；真实模型最小工具调用；恢复不重放已确认写入；成熟队列/Temporal评估与重试/恢复权威记录；沙箱边界记录 |
| M1 | API 创建 Task，关闭客户端后 worker 继续，状态可重新读取 | AC-02/03/08/09/18 的 deterministic 部分；不能依赖内存队列 |
| M2 | 研究／分析 Agent 生成真正文件，可释放环境并下载产物 | AC-01/10/11/13/19/24/25 的云路径 |
| M3 | 本地 daemon 领任务；离线等待；审批、暂停和恢复可观察 | AC-05/08/09/11/12/17/24 |
| M4 | 群内统筹分工；个人助手预授权参与；结果送审 | AC-06/07/13/20/26 |
| M5 | 用自然语言装配现有能力，测试并发布新员工版本 | AC-14/16/25 |
| M6 | Creator 发现工具缺口，编码专员生成一个可复用 Python 工具扩展 | AC-15/16/19；不是仅生成代码文本 |
| M7 | 独立云主机 + 本机客户端验收，备份恢复与完整样例跑通 | 所有必选 AC，通过完整矩阵且有证据 |

M0/M1 的单机验证不替代 M7 的真正云后台执行。任何关键安全失败或外部副作用未知，不得以 happy-path 演示通过 gate。

## 3. 工作包

| 编号 | 工作内容与产物 | 依赖 | 量级 | 验收映射 |
| --- | --- | --- | --- | --- |
| WP-00 | Python 项目、锁文件、lint/typecheck/test、最小 CI、前后端目录约定、配置校验 | 无 | S | AC-01/21 |
| WP-01 | 兼容矩阵；官方checkpoint/interrupt与Codex集成spike；评估现成队列vs外层Temporal并决定恢复权威；一个sandbox adapter实验 | WP-00 | M | AC-10/11/12/19/27 |
| WP-02 | Space/成员/AgentRevision/Instance/Task migration；认证、授权查询、版本固定、schema验证 | WP-01 | M | AC-01/02/03/25 |
| WP-03 | 接入M0选定的成熟调度实现；自有Task状态/授权/幂等与事件适配，映射执行权和SSE补拉；不自建通用队列 | WP-02 | L | AC-08/09/18/27 |
| WP-04 | DeepAgentsRunner和内置CodexRunner适配、原生session映射、事件/产物/取消控制、ToolGateway、可重复fake runner；不自研编码循环 | WP-03 | L | AC-10/11/17/24 |
| WP-05 | 复用backend/provider SDK和一个选定沙箱adapter；TaskWorkspace/租用策略、代码执行、artifact版本/ACL/provenance；不重写文件SDK | WP-04 | L | AC-13/19/24/25/27 |
| WP-06 | 本地daemon/CLI、一次性配对、TLS出站连接、根目录授权、心跳/离线/重连/撤销 | WP-05 | L | AC-05/07/24 |
| WP-07 | 权限交集、Approval参数绑定、pause/cancel/resume、unknown副作用核对、预算预留/结算 | WP-04/06 | L | AC-08/09/11/12/17 |
| WP-08 | Web项目群/私聊/任务线程、成员邀请、@路由、任务卡、artifact查看、审批/审阅操作 | WP-03/07 | L | AC-13/18/20 |
| WP-09 | 统筹员工调用Task工具；子任务依赖/并行预算；DelegationRequest个人团队协作；基础持久日程 | WP-07/08 | L | AC-06/07/20/26 |
| WP-10 | 能力Registry；Creator需求解析/装配；草稿编辑、样例测试、digest校验、不可变发布、实例化/回滚 | WP-05/09 | L | AC-14/16/25 |
| WP-11 | Creator委派内置Codex生成Python工具包；隔离构建、独立测试、权限声明、包hash、登记与版本发布 | WP-10 | L | AC-15/16/19 |
| WP-12 | 远端部署、标准身份源、OTel及单一观测后端、脱敏、secret/TLS、备份恢复、环境清理与成本控制 | WP-07/11 | M | AC-04/21/22/27 |
| WP-13 | 三套真实样例、故障注入回归、质量评估、需求追踪、Beta发布记录与新用户复现 | WP-12 | L | 全部AC，重点AC-23 |

WP-08 可在 WP-03 后以稳定 fake API 设计 UI，但正式集成必须等待授权/状态合同落地。WP-10 的 Registry/schema 可提前定义；不能提前接入未经过授权检查的动态代码。

## 4. 每阶段的实现清单

### M0：冻结风险而非猜上游 API

- 固定 Python、LangGraph、Deep Agents、LangChain模型集成、PostgreSQL checkpointer 的兼容版本和许可证。
- 复用官方checkpointer/序列化；通用规划、上下文、skills、文件工具和临时subagents直接采用Deep Agents能力，不另写同类manager。
- 评估成熟队列与外层Temporal：比较维护性、部署成本、事务投递、崩溃恢复、人审等待、定时和原生Codexjob续接；明确谁负责重试/恢复。当前不锁定Procrastinate或其他候选。
- 默认PG路线可保留官方持久checkpointer；若选Temporal，先在ADR和领域/API合同写清状态投影、命令入口、checkpoint与workflow重放的边界。官方深度集成的Preview能力不能未经验证作为稳定性依据。
- 创建 `docs/dispatch-decision.md`，写入候选、实验、选择、回退和受影响合同；未决前不开始WP-03。该文件由M0创建，目前尚不存在。
- 用成功/失败实验确认 `thread_id`、checkpointer setup、interrupt resume、工具结果持久化、恢复节点重入行为。
- 测试 API-only 与 code sandbox 两条能力路径；明确本机路径和沙箱路径映射。
- 验证文件工具、shell、MCP和临时subagent均经过授权/调用账本；验证恢复产生新attempt后，同一已持久tool intent的action_key保持稳定。若框架内置工具存在绕过路径，先禁用或替换，不能等到后期再补策略。
- 创建 `docs/compatibility-matrix.md`，包括日期、精确版本、测试命令和证据。该文件当前尚不存在。

### M1-M3：先形成可信执行闭环

- migration 与授权测试先行；产品状态不依赖 graph 内部对象。
- checkpoint 与 Task 状态更新之间定义可恢复桥接，不能假定跨系统事务。
- 准备外部写工具测试替身与调用账本，在杀进程场景验证幂等／unknown 分类。
- 本地与云端共用声明、工具合同、产物和事件接口，保留不同的路径、账号与环境能力。
- 所选队列/工作流引擎提供投递、重试与worker生命周期基础；产品只适配任务/授权/预算/调用账本。禁止SDK、队列和graph对同一不明副作用并行自动重试。

### M4：协作可验证

- 统筹 Agent 通过工具操作任务服务，不能仅输出自然语言“已委派”。
- 每个子任务必须有负责人、输入授权、预算、结果合同和父依赖。
- 个人助手只分享显式授权的资料；Team管理员读私有session必须被拒绝。
- final review 和 tool approval 是不同流程。定时任务以 `(schedule_id,scheduled_at)` 判重。

### M5-M6：Creator从装配到扩展

- 参数、prompt、skills修改均产生新发布版本，且旧任务保持原版本。
- v0.1 自动生成扩展只支持受限 Python 工具包；任意runtime、网络代理、权限策略插件后置。
- 验证报告包含配置digest、测试输入、结果和依赖；编辑后旧报告失效。
- 使用全新实例运行生成能力，证明它是可复用扩展。

### M7：真正的初版验收

- 在与用户电脑不同的云主机部署控制服务与worker，测试客户端关闭后任务完成并留下产物。
- 停机恢复、数据库/产物备份恢复、凭据撤销、清理失败重试均有记录。
- 发布仅限可信私有Beta；已知限制明确写入发布记录。

## 5. 阶段完成定义

代码可重复安装；相关正反例测试通过；设计与实际接口一致；日志/指标可定位失败；交付物存在；未验证项如实标记；工作包/AC证据有commit关联；下一会话能够复现。任一关键项缺失仍为进行中。
