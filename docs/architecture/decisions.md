# 架构决策记录

以下 ADR 为当前设计基线。M0 发现实际框架行为与假设不符时，应记录证据并修订相关决策；不得凭文档示例编造已验证的实现能力。

实体/状态规范见 [领域模型](../domain-model.md)，接口规范见 [API 与事件](../api-and-events.md)；发生冲突时先同步规范与 ADR。v0.1 中 tenant 是 Space，`tenant_id = space_id`。

## ADR-001：模块化单体与单一执行栈

**决策**：FastAPI + Postgres + worker；Web 使用 TypeScript / React，本地先提供 Python daemon + CLI。DeepAgents 负责常规执行，LangGraph 承载状态与控制。

**理由与代价**：减少首版基础设施与双运行时维护，保留领域/应用/基础设施边界。Temporal、多 runtime、原生桌面客户端后置；新内核通过适配器接入，不能反向改写产品状态模型。

**验证**：M0 冻结实际依赖版本及锁文件，跑通单个云任务、本地任务、checkpoint 与审批恢复。[官方分层](https://docs.langchain.com/oss/python/langgraph/overview)。

## ADR-002：行为版本、身份归属与执行环境独立

**决策**：AgentRevision 不可变；AgentInstance 绑定个人或团队 Space。个人助手与数字员工共用定义，不通过不同基类表达。Task 发布前明确选 local/cloud。

**理由与代价**：允许同一能力复用到两种产品形态，同时避免把云端执行等同团队 ownership。首版不自动迁移；本地设备不可用时等待设备，电脑关闭不影响已经在云端执行的任务。

**验证**：同一 revision 可实例化为个人与团队员工；环境切换必须通过明确的新任务选择，不能发生隐式数据上传。

## ADR-003：持久协作围绕 Task，而非框架 subagent

**决策**：每个 Task 一位负责人；同 tenant 跨员工工作创建独立子 Task，由 TaskService 管理。跨 tenant 使用 DelegationRequest，在接收方创建 Task；MVP 限同部署预授权个人/单团队合作 pair。统筹 Agent 决定分工与验收，确定性服务管理状态、租约与调度；A2A 跨部署后置。

**理由与代价**：IM 群成员关系和消息历史不具备可靠任务执行语义。DeepAgents subagent 仅用于单个员工内部临时委派，计入父任务预算，不能自行创建持久员工。

**验证**：并行员工有独立子任务与产物引用；子任务失败、取消或等待依赖不会被主任务自动忽略。[官方 subagents 边界](https://docs.langchain.com/oss/python/deepagents/subagents)。

## ADR-004：TaskWorkspace 持久，sandbox 按 session 租用

**决策**：Task 默认持久 TaskWorkspace；ExecutionSession 唯一键为 `(space_id, agent_instance_id, task_id)`，checkpoint 都在原 session 中恢复。Conversation 不表示执行 session；并行分支通过独立子 Task 隔离，API-only 不创建 sandbox。

**理由与代价**：业务成果不能随临时容器销毁。Session 持有环境引用，WorkspaceService 负责生命周期与回收；安装状态、进程和临时目录不会因文件持久化而自动恢复。

**验证**：销毁开发 sandbox 后可重建并读取已提交产物；不能声称恢复进程内存。[官方 backends](https://docs.langchain.com/oss/python/deepagents/backends)。

## ADR-005：租约与 fencing 管执行权，业务幂等管副作用

**决策**：RunAttempt 每次只有一个有效 lease，同一 Task 只有一个有效执行者；每次执行权变化更新 fence。审批/暂停阻塞释放执行权，恢复经 queued 创建新 attempt；未知副作用使用 blocked(recovery_required)。failed/cancelled 不 resume，retry 创建关联原任务的新 Task。所有状态提交与新工具动作验证 fence。

**理由与代价**：checkpoint、队列投递和心跳都不能保证外部副作用 exactly-once。失联不代表请求没有执行；需保存调用记录、业务幂等键和未知结果的核对流程。

**验证**：旧 worker 恢复后不能覆盖状态或再发新动作；超时后的发送不能盲目重复，取消不能宣称撤回已发生的外部操作。

## ADR-006：Creator 配置优先、代码按需、发布不可变

**决策**：对话式 Creator 优先参数、prompt、skills 与已有能力；缺口才转为隔离的 coding/test 任务。发布服务校验并产生不可变 revision 和依赖锁。

**理由与代价**：生成代码不是默认装配机制；用户配置具有执行权，须先检查再实例化。Skills 与 prompt 不能授予权限。回滚只改变新任务选用的版本，不重写历史。

**验证**：未通过契约、环境和相关失败场景验证的包不可调度；发布包不含真实凭据。[Agent Specs 的权限提醒](https://pydantic.dev/docs/ai/core-concepts/agent-spec/)。

## ADR-007：抽象外部执行合同，不抽象隐藏思考过程

**决策**：产品掌握 Task/Run/Policy/Artifact、能力元数据与事件；框架状态与 checkpoint 保持适配器私有。未来策略扩展描述 plan/action/observe 等可观察控制流。

**理由与代价**：ReAct、ReWOO 和完整 harness 不共享内部 state。框架 middleware 不承诺跨内核复用；外部 Codex/Claude 运行器若不暴露内部循环，只能作为粗粒度 backend，不能伪装支持策略切换。

**验证**：不依赖读取隐藏 CoT；新策略有版本化状态与恢复验证，不承诺运行中的任意跨策略迁移。[Deep Agents 与 LangGraph 的层次](https://docs.langchain.com/oss/python/deepagents/overview)。

## ADR-008：开发容器与生产隔离明确区分

**决策**：Docker 仅作为受控开发 sandbox；不据此宣称具备敌对多租户生产隔离。工具网关验证授权；环境边界、凭据和资源限制分别设计。

**理由与代价**：路径根目录、提示词和 subagent 上下文隔离都不能替代系统隔离；生产部署前须有独立安全验收。

**验证**：M0 明确开发信任边界，检查本地 shell 与容器挂载；生产准入标准由安全文档定义，本文不替代。[官方本地 backend 限制](https://docs.langchain.com/oss/python/deepagents/backends)。
