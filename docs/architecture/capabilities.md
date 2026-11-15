# 能力、技能与执行适配

实体、隔离和 ToolInvocation 语义见 [领域模型](../domain-model.md)，调用与事件合同见 [API 与事件](../api-and-events.md)。能力清单属于 AgentRevision 的锁定依赖，不是运行时授权本身。

## 四类内容的边界

| 类型 | 用途 | 不提供什么 |
| --- | --- | --- |
| 参数与 prompt | 职责、模型策略、业务约束、输出格式 | 不授予资源权限 |
| Skill | 可复用方法、模板、资源与验收指导，按需加载 | 不因加载而获得密钥、终端或网络权限 |
| Tool / Connector | 具备 schema 的确定性操作与业务系统接入 | 不绕过授权、调用记录和幂等检查 |
| 代码插件 | 既有配置无法表达的新工具或能力实现 | 不默认成为控制面或策略插件 |

能力元数据由项目维护。DeepAgents middleware 是该框架的实现机制，不承诺与其他内核的 lifecycle hook 或 capability 对象互换；对外暴露中立能力描述，对内由适配器装配。

## CapabilityDescriptor 最小契约

每个可发布能力必须包含以下元数据；字段名称可在数据/API 设计中统一，但语义不能缺失。

- 稳定 ID、不可变版本、描述、提供者、插件/代码引用和校验哈希。
- 参数 schema、输入输出契约；输出与错误应可序列化并支持大小限制。
- 所需工具、skill、资源与凭据引用；依赖版本和相互冲突的能力。
- 支持的环境 `local/cloud`、是否需要 sandbox、文件/命令/网络需求。
- 副作用类型、授权范围、审批要求、超时、幂等与重试约定。
- 使用成本与预算维度、Artifact 类型、测试证据和已知限制。

“有权限”不能只由配置中的 tools 列表判断：实例、任务、发起人委托、环境和组织规则共同限制实际可执行动作。配置过滤工具用于减少误调用，工具网关执行权威检查。

## 一次工具调用

1. Runtime 提交能力版本、动作、参数、Task/RunAttempt、lease/fence 与稳定调用 ID。
2. 网关校验执行权、有效授权、参数、额度与资源范围；需审批时先持久化具体请求，暂停执行。
3. 在环境适配器中解析短期凭据并执行。工具实现必须把外部业务幂等键与本次调用关联。
4. 保存结果、消耗、外部回执与 Artifact；超大输出保存为引用，返回必要摘要。
5. 未知结果不能当成失败后直接重试；具体恢复遵循 [运行时](runtime.md)。

API-only 能力直接调用受控连接器，无需创建 sandbox。需要文件或命令时使用该 Task 的 ExecutionSession；持久成果写入 TaskWorkspace，不能只留在容器临时目录。

## DeepAgents 复用与限制

复用其规划、skills 加载、文件工具、上下文压缩和临时 subagents。通过 backend 适配 TaskWorkspace，通过工具注册和 middleware 接入项目的调用检查与事件转换；是否能覆盖所有动作须在 M0 验证。

本地 shell backend 直接在宿主机运行，工作目录和路径规则不是完整隔离。开发 sandbox 可用 Docker，但这只是受控开发环境，不是敌对多租户生产安全边界。生产隔离方案另行设计，不能因接口名含 sandbox 就默认满足。

临时 subagent 默认采用最小工具与隔离上下文；需要 fork 时显式配置并核对继承内容。持久员工间只通过 TaskService 分派任务，不把员工注册表映射成无界 `task` 工具委派。同 tenant 创建子 Task；跨 tenant 创建 DelegationRequest，接收方仅在预授权 pair 范围内接单。

## 装配与版本约束

Creator 只能选择已登记且调用者可用的能力；先验证元数据、依赖和环境，再实例化实现。任意用户配置不得直接加载 Python 路径、未知 MCP 地址或未登记镜像。

AgentRevision 锁定能力与 skills 内容版本；撤销授权即时影响后续调用，不要求修改 revision。能力实现升级通过新版本和回归验证发布，不就地替换正在执行的代码。

官方依据：[Deep Agents backends](https://docs.langchain.com/oss/python/deepagents/backends)、[subagents](https://docs.langchain.com/oss/python/deepagents/subagents)、[Pydantic capabilities：可组合行为的参考设计](https://pydantic.dev/docs/ai/capabilities/overview/)。
