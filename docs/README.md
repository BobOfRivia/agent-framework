# 项目文档索引

状态：v0.1 规划基线；更新：2026-11-15。先看 [新会话开工说明](../START_HERE.md)，当前实现程度以 [状态记录](implementation-status.md) 为准。

## 产品与研究

- [产品需求与初版范围](product-requirements.md)
- [用户流程与交互](user-experience.md)
- [框架适配与产品参照](research-and-fit.md)

## 架构与合同

- [整体架构](architecture/overview.md)
- [运行时、LangGraph 与 Deep Agents](architecture/runtime.md)
- [领域模型与状态机](domain-model.md)
- [API、事件和设备协议](api-and-events.md)
- [能力、技能与插件](architecture/capabilities.md)
- [Creator、测试和发布](architecture/creator.md)
- [执行环境、工作区和沙箱](architecture/execution-environments.md)
- [设计决策 ADR](architecture/decisions.md)
- [安全、授权和个人／团队边界](security-and-permissions.md)

## 实施与验收

- [开发计划与工作包](development-plan.md)
- [验收标准](acceptance.md)
- [测试与评估策略](testing-strategy.md)
- [需求—实现—验收追踪](traceability.md)
- [开发环境与贡献指南](development-guide.md)
- [运行、部署与恢复](operations.md)
- [风险、假设与待决问题](risks-and-open-questions.md)
- [实施状态和交接](implementation-status.md)
- [文档基线校验记录](documentation-validation.md)

## 声明合同与样例

- [AgentRevision schema](../schemas/agent-revision.schema.json)
- [Task 创建 schema](../schemas/task-create.schema.json)
- [事件 schema](../schemas/task-event.schema.json)
- [研究员](../examples/agents/researcher.json)、[分析员](../examples/agents/analyst.json)、[统筹员工](../examples/agents/coordinator.json)、[个人助手](../examples/agents/personal-assistant.json)
- [云端任务](../examples/tasks/cloud-research.json)、[本地任务](../examples/tasks/local-analysis.json)
- [Creator 需求与扩展验收例](../examples/creator/requests.md)

## 文档冲突与变更

产品范围以 PRD 为准，状态／隔离／恢复合同以领域模型为准，公开字段以 schema/API 合同为准。需要修改这些边界时，先记录 ADR，再同步相关测试与追踪表。所有已发布 AgentRevision 与任务输入合同均记录 schema_version。

外部资料只证明其对应能力，项目总体设计属于本仓库的工程决策。未运行过的上游特性必须在 M0 验证，不能依据文章或能力名称宣称项目验收完成。
