# 运行时与失败恢复

本页说明执行机制；实体与状态以 [领域模型](../domain-model.md) 为权威，事件与设备协议见 [API 与事件](../api-and-events.md)。v0.1 中 `tenant_id = space_id`。

## 执行对象与不变量

- 一个 Task 只有一位负责人；parent_task_id 只用于同 tenant 的父子任务。跨 tenant 经 DelegationRequest 在接收方创建独立 Task，不复用父子关系。
- AgentInstance 的 ownership 与执行环境独立。Task 发布时固定 `local` 或 `cloud`，不自动切换。
- 每个 Task 默认拥有持久 TaskWorkspace；每个 `(space_id, agent_instance_id, task_id)` 最多一个持续的 ExecutionSession。该 Task 的 checkpoint 都属于同一 session；会话与 IM Conversation 无关。
- Sandbox 按 ExecutionSession 租用；API-only 任务无需 sandbox。并行分支通过独立子 Task 获得独立 workspace/session，显式发布和交换产物。
- 每个 RunAttempt 至多一个有效 lease；同一 Task 同时至多一个有效执行者。租约更新必须产生可验证的 fencing token，旧执行者不能提交状态或发起新副作用。

## 状态机

Task 状态仅为 `queued / running / blocked / review / succeeded / failed / cancelled`。

| 转换 | 条件 |
| --- | --- |
| queued → running | 对应环境可用，取得 lease/fence，准备执行资源 |
| queued/running → blocked | 明确写入 reason：waiting_device、waiting_approval、waiting_input、waiting_dependency、user_paused、recovery_required |
| blocked → queued | 对应等待条件已满足，通过授权检查后重新调度 |
| running → review | 产物等待验收 |
| running/review → succeeded | 任务验收规则满足；父任务按依赖策略汇总 |
| running → queued | 已确认能够安全重试，调度新 RunAttempt |
| running → failed | 不可恢复错误或预算耗尽 |
| queued/blocked/review → failed | deadline到期；blocked必要依赖不可恢复或核对后放弃 |
| review → queued | 要求修订；保存反馈并创建下一次执行尝试 |
| 非终态 → cancelled | 取消被接受，撤销执行权，记录已产生的结果 |

失败或取消的子任务不能由父任务默认为成功；依赖未满足时父任务进入 `blocked(waiting_dependency)`，由明确的失败处理策略决定继续、修订或终止。终态不能被迟到的 worker 回报覆盖。failed/cancelled 不 resume；手动 retry 创建新 Task 并记录 retry_of_task_id。

MVP 默认 human review，最终交付先进入 review；内部只读子任务可按服务端允许的 auto 策略在契约检查通过后成功。

## 正常执行路径

1. TaskService 在事务中登记任务、负责人、环境、验收规则与 AgentRevision；调度事件与状态一同持久化。
2. 调度器先确认目标可用；local 设备不可达时记录 `blocked(waiting_device)`。目标 worker 接单时取得有效 lease/fence。
3. 创建或连接 ExecutionSession；附着 TaskWorkspace，按需创建 sandbox。运行前检查能力、环境、数据和授权是否兼容。
4. 执行适配层启动 DeepAgents；LangGraph 承载状态、检查点、中断与控制流程。所有工具调用经过网关，记录稳定调用 ID、授权决策与结果。
5. Worker 更新心跳和执行事件，登记 Artifact；验收通过后完成，否则进入 review。TaskService 才能提交产品级状态转换。

## 审批、重试与恢复

审批等待写入任务 `blocked(waiting_approval)` 和 checkpoint 引用，释放有效执行 lease。审批绑定具体动作、参数摘要、资源与 revision；恢复先 blocked → queued，再创建新 RunAttempt、获取新 lease/fence 并检查授权，在原 ExecutionSession 中继续，不能用旧审批覆盖新的动作。用户暂停使用 user_paused，外部结果待核对使用 recovery_required，二者不能互相替代。

| 故障 | 恢复动作 |
| --- | --- |
| Worker 进程崩溃或 lease 到期 | 撤销旧执行权；确认无未知副作用后，新 RunAttempt 可引用兼容 checkpoint，保持原 local/cloud 位置与 session，按需重建物理环境 |
| 本地电脑关机 | 等待原设备恢复；不得把任务和本地数据静默发往云端 |
| 云 sandbox 被销毁 | 在原 ExecutionSession 中从持久 TaskWorkspace 重建环境；进程、安装状态与临时目录不视为已保存 |
| 工具请求超时、外部结果未知 | 进入 blocked(recovery_required)，停止盲目重试；核对记录后明确恢复或终止 |
| Checkpoint 与新版本不兼容 | 优先使用任务锁定的旧执行包恢复；无法恢复时保留产物并阻塞核对，版本迁移需显式新建 Task，不能给旧 Task 静默换 revision |
| 用户取消 | 阻止新工具动作并请求停止；已发出的外部请求可能仍完成，继续记录事实 |

检查点不保证外部副作用 exactly-once。发送、写入等操作使用业务幂等键；供应商不支持幂等且结果未知时必须核对。重放可能重新进入中断所在节点，因此副作用与等待应拆开，并以调用记录去重。

## 策略扩展边界

第一阶段以 DeepAgents 常规执行为主。自有执行策略只约束可观察的计划、动作、事件与终止条件，不要求模型输出隐藏思维链。未来原生 ReAct/ReWOO 可通过版本化策略合同接入 LangGraph；策略内部状态保持私有，不强制跨策略转换 checkpoint。

跨员工协调使用 TaskService；单个 Run 内的临时 subagent 由 DeepAgents 管理并计入父任务预算。框架 checkpoint 引用与产品事件分开保存，不把框架消息结构当作 Task 权威数据。

## M0 必须验证

冻结 Python、LangGraph、DeepAgents、模型适配器和 checkpoint 实现的实际版本及依赖锁；验证 checkpoint 重启、审批恢复、租约失效、sandbox 中断和未知副作用处理。此处不预设未验证的库 API。

官方依据：[LangGraph interrupts 与节点重入](https://docs.langchain.com/oss/python/langgraph/interrupts)、[Deep Agents backends](https://docs.langchain.com/oss/python/deepagents/backends)、[subagents](https://docs.langchain.com/oss/python/deepagents/subagents)。
