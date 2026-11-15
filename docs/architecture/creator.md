# 对话式 Agent Creator

AgentDraft、AgentRevision、AgentInstance 的字段与权限以 [领域模型](../domain-model.md) 为准；Creator API 见 [API 与事件](../api-and-events.md)。配置式 Creator 为 M5，按需代码扩展为 M6；依赖与 M0-M7 阶段状态见 [实现状态](../implementation-status.md)。

## 职责与输入

Creator 将用户目标变成可验证、可部署的 AgentRevision。优先选择已有能力，再生成参数、提示词和 skills；仅在能力确实缺失时编写插件代码。个人助手与数字员工使用同一创建流程，ownership 由实例化阶段绑定到个人或团队 Space。

对话至少收集职责、输入来源、交付物、验收规则、可用工具、数据范围、是否允许外部写入与成本上限。Creator 可展示 local/cloud 能力差异；具体 Task 的执行环境仍由发布任务时显式选择。

## 草稿到发布的流程

1. **理解目标**：整理角色与任务样例，指出缺少的输入或权限；不把模糊承诺直接编成配置。
2. **检索装配**：查询 CapabilityRegistry，选择确定版本，验证参数与依赖；优先复用已有连接器和技能。
3. **生成草稿**：生成行为配置、instructions、skills、验收规则和示例任务；展示相对于已有 revision 的变更。
4. **识别缺口**：说明为何已有能力不足，再委派内置Codex执行隔离的代码工作子任务；复用现成编程Agent，不给生产凭据或发布权限。
5. **测试验证**：先做静态校验，再在选定测试环境运行样例和失败场景，保存测试证据与 Artifact。
6. **准备发布**：汇总有效能力、授权需求、依赖锁、环境限制、测试结果和已知限制，生成具体发布包。
7. **发布版本**：发布服务检查调用者权限、最新草稿 digest 与验证门槛，创建不可变 AgentRevision；生成 AgentInstance 时绑定个人或团队 Space。编辑草稿立即使旧 validation_digest 失效。

## 发布包

以下是项目约定的建议产物，而不是 DeepAgents 的原生配置格式：

| 产物 | 内容与版本方式 |
| --- | --- |
| agent.yaml/json | 中立 AgentSpec、参数、工具与 skill 引用、输出契约、执行配置 |
| instructions.md / skills/ | 行为说明、流程和资源；内容哈希锁定 |
| plugins/ | 仅缺失能力所需代码；独立包版本、依赖锁及可复现构建标识 |
| evals/ | 正常样例、输出验收、关键失败场景与期望结果 |
| agent.lock.json | revision 所需的策略、运行包、能力、技能与镜像等确切依赖 |
| release.json | 发布者、变更摘要、包哈希、验证证据和环境兼容性 |

包内不保存真实凭据、个人聊天记录或租约。部署时解析凭据引用；权限可独立撤销。运行事件记录实际使用的模型标识与执行版本，不能只记录一个可能变化的模型别名。

## 发布门槛

- Schema 与参数校验通过；只允许注册表中可使用的能力及端点，实例化前完成检查。
- 输入、输出及 Artifact 验收采用真实运行时验证，不能仅依赖模型遵循 JSON Schema 提示。
- local/cloud 的所需能力分别验证；不支持的环境明确拒绝，不自动换环境。
- 有代码时验证构建、依赖、权限需求和隔离执行；外部副作用使用可核对的测试替身或专用测试资源。
- Codex提交patch/diff、测试命令和真实退出码后，发布服务在干净环境独立验证；不以编码Agent的完成文案代替验收。集成边界见[Codex执行器](coding-executor.md)。
- 通过任务完成、失败、审批、取消与重试的相关场景；测试规模随变更风险调整，保存可复查证据。

未通过验证的草稿不得变为可调度版本。Creator 可以自动完成测试与准备发布，但不能修改自身授权或绕过发布服务；需要新增授权时展示具体资源与动作。

## 更新与回滚

修改配置、prompt、skills 或插件均生成新 revision。新任务可选择新版本；运行中的 Task 继续绑定原版本与依赖。回滚改变未来任务使用的版本，不重写已发布 revision，不撤销已经发生的外部动作。failed/cancelled 的任务需要重新执行时创建 retry_of_task_id 指向原任务的新 Task，而不是恢复终态。

首版不生成任意控制面扩展或建立插件市场；新增 runtime、策略或 workspace provider 按可信工程代码评审。详见 [能力](capabilities.md) 与 [决策](decisions.md)。

参考：[Deep Agents customization](https://docs.langchain.com/oss/python/deepagents/customization)、[Pydantic Agent Specs：配置构造具有代码同等权限](https://pydantic.dev/docs/ai/core-concepts/agent-spec/)。
