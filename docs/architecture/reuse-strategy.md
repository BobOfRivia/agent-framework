# 成熟组件复用与自有边界

状态：已接受的复用方向与待验证选型；2026-11-16。本文不表示相关集成已经实现。产品语义以[领域合同](../domain-model.md)、接口以[API 与事件](../api-and-events.md)为准；执行与发布见[运行时](runtime.md)、[Codex 执行器](coding-executor.md)及[Creator](creator.md)。

## 1. 已确定的复用方向

目标是组装成熟执行能力，保留产品差异；不把“统一基座”实现为另一套通用 Agent SDK。确定复用某类组件，不等于已经选择供应商、精确版本或付费服务。

| 部位 | 复用内容 | 自有薄层 | 首次接入 |
| --- | --- | --- | --- |
| 通用 Agent | DeepAgents 的规划、skills、上下文压缩/卸载、文件工具、临时 subagents | 能力元数据、输入装配、授权、预算和验收；不重写同类管理器 | M0 验证，M2 接入 |
| 图运行与检查点 | LangGraph 控制流、interrupt、streaming 与官方 PostgreSQL checkpointer | Task/session/thread 映射、状态桥接和恢复核对；不自建 checkpoint 格式或序列化器 | M0/M1 |
| Coding Agent | 现成 Codex SDK/CLI 或经验证的官方集成入口 | CodingJob scope、原生会话引用、事件/回执、隔离与独立验收；不自研编码循环 | M0 验证，WP-04/11 |
| 云 sandbox | E2B 或 Daytona 的官方 SDK、可复用的框架 backend；首版只选一个 | SandboxLease、TaskWorkspace 挂载/快照、资源限制、回收和产物提交 | M0 比较，M2 选定 |
| 浏览器自动化 | Playwright；通过已有接口执行受控浏览器操作 | 账号/session 隔离、允许站点、下载产物与动作授权；不再实现浏览器协议或另造浏览器 Agent | 场景需要时接入 |
| 文档与 Office | 文档解析优先复用 Docling；Office 创建/修改按格式使用成熟库，例如 openpyxl、python-docx、python-pptx | 输入类型、业务模板、真实输出验证、ArtifactVersion；不自研 OCR/排版/文件格式引擎 | 对应任务需要时 |
| 登录认证 | OIDC + 现有 IdP 及成熟客户端/中间件 | 用户与 Space 映射、成员关系、资源授权和委派；不自研密码、MFA 或令牌签发平台 | M1 |
| 可观测性 | OpenTelemetry + 一个选定后端，复用已有 instrumentation | Task/attempt/job 关联、脱敏、可见性、成本和关键业务事件 | M0 选定，逐阶段接入 |
| 模型与工具协议 | 供应商官方 SDK、框架现有模型/MCP 适配 | 模型配置、已允许服务、凭据引用、超时、授权与调用账本 | 首次只接一个模型 provider |

DeepAgents 临时 subagent 不是持久员工；已有 skills、memory 或文件能力也不自动获得产品权限。保留其执行能力，通过适配层接入现有合同，而不是重复建设同名子系统。[官方 harness](https://docs.langchain.com/oss/python/deepagents/overview)

## 2. 必须掌握的五项产品核心

1. **Agent 身份与版本**：AgentDefinition、不可变 AgentRevision、个人/团队 AgentInstance，及版本锁定与记忆归属。
2. **Creator**：对话需求、配置/prompt/skills 优先装配、缺口编码委派、验证、发布和回滚。
3. **跨 Space 授权**：Membership、Grant、DelegationRequest、凭据范围及显式结果共享。
4. **任务与群协作**：TaskService、负责人、父子依赖、群路由、产品状态、预算和执行权。
5. **产物与验收**：ArtifactVersion、来源、ACL、必要文件、结果合同、review 与证据。

这些核心使用库实现基础能力，但不能直接继承某个框架对象作为业务权威。Conversation、ExecutionSession、框架 checkpoint、Codex 原生会话和 TaskWorkspace 继续分别建模。

## 3. 调度尚未选定：M0 必须作出决定

PostgreSQL 已确定承担业务事务存储；后台调度实现尚未选定。M0 比较“成熟 PostgreSQL 队列 + 薄调度”和“外层 Temporal”，提交 ADR 与实验结果，再确定 WP-03 实现。不要将旧文档中的 DB jobs 描述当作手写通用队列的授权。

| 候选路线 | 可复用部分 | 仍须由产品保证 |
| --- | --- | --- |
| 成熟 PG 队列库 | 入队、认领、定时、worker、重试与运维能力 | Task 状态、fence、授权、审批、预算、幂等账本、unknown 核对 |
| 外层 Temporal | 持久调度、计时、信号、子工作流、受控重试和长时间等待 | 员工/Space、Task 合同、业务授权、Artifact、验收及副作用账本 |

PG 队列库只是候选。Procrastinate 等前期候选须检查维护活跃度、许可、驱动/事务兼容、失联 worker 恢复、取消和升级路径，不能仅因已有功能列表就锁定。队列 job 不等于 Task；库的 retry 不能无条件重放外部写入。

Temporal 路线需同时验证服务运维、部署成本、工作流确定性、版本更新、事件历史与恢复。LangGraph/DeepAgents 的官方 Temporal 集成按 **Public Preview** 候选路径评估，不默认等于稳态生产能力；M0 记录所选版本的发布状态和限制。

必须在以下两种持久化方式中明确选择，不能随意叠加：

- **框架深度集成**：按官方 Temporal 插件合同，由 Temporal replay 管持久恢复；workflow 内不能继续把有 I/O 的 PostgreSQL checkpointer 当作普通确定性状态使用。
- **外层 workflow + Agent Activity**：可评估由 Temporal 管调度/等待、Activity 内执行 DeepAgents 或 Codex。Agent 原生 checkpoint/session 由适配器管理；Activity 重试必须先核对原 Task/session/job，不能默认从头启动。

每条路线写清 checkpoint 权威、重试权威、取消传播和 lease/fence 的对应关系；不让队列、图执行器与 Temporal 三方同时独立重试。官方集成说明不能替代本项目的故障实验。[Temporal DeepAgents 集成与限制](https://docs.temporal.io/develop/python/integrations/deepagents)

无论选哪条路线，外部副作用仍须经过产品调用/作业账本、稳定意图 ID、供应商幂等键和未知结果核对。Temporal、PG 队列与 LangGraph 都不替业务系统承诺 exactly-once。

## 4. 接口只覆盖必要控制

执行适配器保留最小的启动、查询、事件、暂停请求、取消及恢复语义，具体签名由 M0 冻结。能力矩阵声明是否支持安全暂停、审批桥接、进程重启续接、用量统计和环境重建。

不支持的控制明确拒绝或进入核对，不能把“有统一方法名”当作行为一致。不设计跨所有模型、工具、浏览器、执行器和 sandbox 的 universal SDK，也不承诺跨引擎 checkpoint 互换。

自有 DeepAgents 动作通过 ToolGateway 接入授权与账本；Codex 原生工具按 job scope、原生权限、环境隔离和回执治理，不宣称逐工具均被自有网关拦截。原生审批与恢复单独验证。

复用官方 SDK/MCP 只解决协议与连接，端点、账号、工具、资源范围与输入仍由产品验证；不能从用户配置直接启动未知服务或加载任意代码。

## 5. 首次接入与验证清单

首次支持 **一个模型 provider、一个云 sandbox、一个 trace 后端**。OIDC 只接一个已选 IdP；浏览器和文档能力按验收需求增量启用，不因本表存在就接入所有服务。

M0 交付物必须包含：

- 精确版本、依赖锁、许可与候选淘汰理由；供应商尚未选定的项目明确标注。
- 调度 ADR：PG 队列与外层 Temporal 的同场景对比、权威边界及选择结果。
- LangGraph 官方 PG checkpointer 的安装、setup、interrupt、恢复和节点重入实验；不另写保存格式。[官方 checkpointers](https://docs.langchain.com/oss/python/langgraph/checkpointers)
- DeepAgents 与 Codex 分别测试控制合同；fake 通过不能替代真实模型与原生执行证据。
- 云 sandbox 创建/销毁、文件保留、资源限额、网络与凭据边界；Docker 开发环境不推导敌对多租户安全。[官方 sandbox 接入](https://docs.langchain.com/oss/python/deepagents/sandboxes)
- 崩溃、审批重放、旧 fence、超时未知结果、重复回执、取消及备份恢复的故障注入。

后续接入复用同一套契约测试、样例和证据格式；只有真实需求与已验证缺口才增加第二个 provider 或替换组件。升级不自动改变运行中 Task 的 revision、授权和恢复格式。

## 6. 按需组件的官方依据

- [Playwright Python](https://playwright.dev/python/docs/intro)：复用浏览器自动化，不重写底层驱动。
- [Docling](https://docling-project.github.io/docling/)：复用文档解析，Office 输出按文件格式另用成熟库。
- [OpenID Connect Core](https://openid.net/specs/openid-connect-core-1_0.html)：复用身份认证；Space 与委派授权仍由产品决定。
- [OpenTelemetry](https://opentelemetry.io/docs/)：复用标准 instrumentation/导出链路；首版只选一个观测后端。

以上链接说明组件能力和边界，不代表已经选定精确版本、完成接入或通过本项目验收；当前进度见[实现状态](../implementation-status.md)。
