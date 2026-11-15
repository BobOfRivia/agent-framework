# LangGraph / Deep Agents适配评估与产品参照

资料核查截至2026-11-15；本仓库尚未运行框架实验。本页区分官方能力、借鉴设计和本项目需要实现的合同，不以文档宣传替代测试。

## 1. 选型结论

LangGraph / Deep Agents能够作为本项目的主执行栈，支持状态化运行、工具循环、文件上下文、子任务和人工中断等基础。完整需求还包括员工身份、Creator发布、设备、跨Space授权、任务协作、产物与审阅；这些由本产品层实现。

因此结论是“有合理的技术实现路径”，而非“引入框架就已经满足全部需求”。M0须证明版本组合、原生工具授权、检查点恢复和副作用账本能协同工作；不能在未验证前承诺所有上游高级API稳定。

## 2. 框架覆盖与项目补齐

| 需求 | 可复用基础 | 本项目补齐 |
| --- | --- | --- |
| 单员工通用执行 | Deep Agents工具、规划、skills和上下文管理 | 自有能力元数据、权限网关、预算和事件 |
| 持久工作 | LangGraph checkpointer/store/interrupt | Task权威状态、leases/fence、恢复对账与artifact |
| 内部临时并行 | Deep Agents subagents | 最小权限、预算、临时写目录边界；持久员工委派另建Task |
| 本地／云端 | backend/环境适配思路 | 用户显式选择、设备协议、TaskWorkspace、云worker、沙箱生命周期 |
| 个人助手／员工 | 共用同一执行定义 | Space/owner/记忆/账号授权、长期身份 |
| 群聊统筹 | 工具调用和可编排运行 | 人/Agent群成员、任务工具、跨Space受理、审核 |
| Creator | 可配置Agent、skills与工具 | 声明schema、Registry、草稿/测试/发布/版本绑定、代码扩展 |

LangGraph文档将自身定位为长任务状态编排运行时；Deep Agents在其上提供完整harness。这与本项目“产品合同在外、执行适配在内”的分层匹配。[LangGraph官方](https://docs.langchain.com/oss/python/langgraph/overview)、[Deep Agents官方](https://docs.langchain.com/oss/python/deepagents/overview)

## 3. 重要技术边界

- Checkpointer保存图状态，store保存跨线程数据；二者不自动成为业务Task数据库或外部动作幂等账本。[持久化](https://docs.langchain.com/oss/python/langgraph/persistence)
- interrupt恢复可能重新进入节点；审批和外部写入需分离并判重。[中断](https://docs.langchain.com/oss/python/langgraph/interrupts)
- 本地文件或shell backend的工作目录不是完整OS隔离；文件、命令、网络和凭据分别控制。[Backends](https://docs.langchain.com/oss/python/deepagents/backends)
- subagent上下文隔离不等于不同员工凭据和文件安全域；持久协作交给TaskService。[Subagents](https://docs.langchain.com/oss/python/deepagents/subagents)

本页不锁定精确框架版本。M0创建兼容矩阵和可重现spike，具体API以所锁版本官方文档和实际测试为准。

## 4. 已落地产品的可借鉴部分

| 产品 | 与本项目相似的设计 | 不能据此推导的能力 |
| --- | --- | --- |
| GenTeam | 云端与本机CLI Agent同群、角色、任务负责人、线程和交接 | 本机断连会暂停；不代表本地任务能自动云接管 |
| Dust Pods | 人/Agent围绕conversation/task/files协作，工具可操作任务 | 现有任务状态不自动等于本项目审核/取消/恢复语义 |
| 扣子团队与云电脑 | 项目资产、可配置员工、电脑关机后云端工作继续 | 官方FAQ仍明确Agent不能主动调度其他Agent；多人多Agent不等于已有自主统筹 |
| Agno Studio/Registry | 登记构件，对话/可视装配，草稿、测试、发布和当前版本 | 不代表其全部平台能力已纳入本仓库，也不要求引入第二套主runtime |

直接来源：[GenTeam帮助](https://www.genspark.ai/helpcenter/genteam)、[Dust Agent工具](https://docs.dust.tt/docs/user-documentation/pods/agent-tools)、[扣子云电脑](https://docs.coze.cn/cozespace_device)、[扣子FAQ](https://docs.coze.cn/cozespace_coze_app_faq)、[Agno Registry](https://docs.agno.com/agent-os/studio/registry)、[Studio版本](https://docs.agno.com/agent-os/studio/introduction)。这些产品描述会变化，后续引用应重新核实日期。

## 5. 抽象思想的参考

OpenHands将Agent、会话与不同Workspace执行模式分开，适合借鉴本地/远端环境接口。[官方架构](https://docs.openhands.dev/sdk/arch/overview)

Pydantic AI的capability/AgentSpec展示声明式能力组合；但spec具有构造代码同等authority，不能把用户配置直接加载成高权限工具。[Agent Specs](https://pydantic.dev/docs/ai/core-concepts/agent-spec/)

本项目吸收这些边界和发布思想，不复制厂商产品内部代码，不依赖未选择服务的登录态、付费账号或商业许可。上游SDK、模型和托管服务的许可需逐项核实。

## 6. 满足需求的验证路径

R-01到R-14均有对应设计、WP和AC，详见[追踪表](traceability.md)。框架能力不足时先在adapter中处理或关闭该能力；如果M0证明核心网关或恢复合同无法成立，记录失败实验和ADR，再讨论调整，不能通过删减验收掩盖问题。
