# 开发代理工作约定

## 目标与阅读顺序

本仓库实现 LangGraph / Deep Agents 可组合 Agent 平台。用户明确要求：个人助手与数字员工两类身份，任务发布前选 local/cloud，云任务关机后继续；IM 群统筹；Creator 参数／提示词／能力装配，按需编码、测试和发布。

每次新会话先读 START_HERE.md、docs/implementation-status.md、docs/domain-model.md、docs/development-plan.md 和本次工作包引用的验收条目。产品代码尚未实现时，规划命令不是已存在命令。

## 不得隐式改变的产品边界

- 不自动将本地进行中任务迁云；换位置显式新建／委派任务。
- 不把数字员工等同常驻 VM，也不把临时 subagent 等同持久员工。
- 不把 IM Conversation 等同私有 ExecutionSession。
- 不以群成员／组织管理员身份读取个人助手私有记忆和账号；跨 Space 走 DelegationRequest。
- 不让 Creator 或生成代码自行授予凭据、扩大授权或绕过发布校验。
- 不将桌面 UI 长连接当作云任务运行保障。
- 不自研Coding Agent循环；内置编码员工使用Codex SDK/CLI专用执行器。通用员工继续Deep Agents，跨员工通过TaskService。Codex原生工具治理与自有ToolGateway区分，按docs/architecture/coding-executor.md执行。
- 不以 mock、本机容器或聊天完成文案替代真实云部署、文件产物和验收证据。

## 合同优先级

1. 用户当前明确要求优先；如影响基线，记录变更。
2. docs/domain-model.md 是状态／隔离／恢复规范；docs/api-and-events.md 是接口规范；schemas/ 是声明格式规范。
3. docs/product-requirements.md 定义范围，docs/acceptance.md 定义通过标准。
4. 架构和 ADR 解释设计选择；冲突先统一合同，不能在多个模块各自解释。

## 实施方法

- 一次领取一个可验收工作包；不跳过 M0 兼容性验证就猜测 upstream API。
- 先建立持久 Task/事件/租约，再把真正 Agent 执行接进来；保留真实模型路径和可重复 fake 路径。
- 全部查询有服务端空间授权；日志不含密钥。副作用经过工具网关并记录幂等账本。
- 框架特定调用限制在 adapter 中；优先组合现有能力。普通插件不得加载进高权限 API 控制进程。
- 先读docs/architecture/reuse-strategy.md。复用Deep Agents已有规划/技能/上下文/file/subagents和LangGraph官方checkpointer，不自建这些通用引擎；不自研通用队列、浏览器驱动、文件格式或trace平台。
- M0必须比较成熟队列与外层Temporal并明确选择；选Temporal须先修订持久化/状态/重试合同。多个组件不能同时决定同一动作恢复。每类provider先实现一个，未验证的可选服务不自动加入依赖。
- 代码目录与命令由阶段实现建立；不得为了“项目看起来完整”添加无行为空壳或伪造完成状态。
- 需要更改状态、schema、权限或依赖边界时，同时更新 ADR、合同与验收映射。
- 文档使用中文正文，标识符、协议字段和提交标题可用英文。仓库内链接使用相对路径。

## 验证与交接

- 运行与变更相关的真实检查；凭据不可用时区分 deterministic 通过、真实集成未验证。
- 产品化关键测试应覆盖 crash/restart、审批重放、旧 fence、跨 Space、设备失联与工具结果未知。
- 每次结束更新 docs/implementation-status.md：已完成包、实际命令结果、commit/PR、未验证项、下一步。
- 不在文档中写真实凭据或把本机绝对路径写成用户的默认运行目录。
- 不擅自选择代码许可证、付费基础设施、公开部署或删除用户数据；技术默认可按 ADR 实施。

## 本基线已有检查

`python3 tools/check_docs.py`；若已装 tools/requirements-docs.txt，执行 `python3 tools/check_docs.py --schemas`。

产品 lint/test/run 命令待实际搭建后补齐；更改本文时保持此说明准确。
