# 需求—设计—开发—验收追踪

基线：2026-11-15。R编号与[产品需求](product-requirements.md)一致；AC编号与[验收标准](acceptance.md)一致。该表追踪设计覆盖，不代表实现完成。

| 需求 | 主要设计合同 | 工作包 | 必选验收 |
| --- | --- | --- | --- |
| R-01 身份与版本 | [领域模型](domain-model.md)、[Creator](architecture/creator.md) | WP-02/10 | AC-01/02/16 |
| R-02 能力装配 | [能力模型](architecture/capabilities.md)、[Agent schema](../schemas/agent-revision.schema.json) | WP-04/10 | AC-01/24/25 |
| R-03 Creator扩展 | [Creator](architecture/creator.md) | WP-10/11 | AC-14/15/16 |
| R-04 local/cloud选择 | [环境](architecture/execution-environments.md)、[Task schema](../schemas/task-create.schema.json) | WP-02/05/06 | AC-03/24/25 |
| R-05 云后台运行 | [运行时](architecture/runtime.md)、[运维](operations.md) | WP-03/09/12 | AC-04/10/26 |
| R-06 本地设备 | [API设备协议](api-and-events.md)、[环境](architecture/execution-environments.md) | WP-06/07 | AC-05/08/24 |
| R-07 IM项目群 | [用户流程](user-experience.md)、[API](api-and-events.md) | WP-08 | AC-18/20 |
| R-08 统筹委派 | [领域委派](domain-model.md)、[权限](security-and-permissions.md) | WP-09 | AC-06/07 |
| R-09 Session/任务与恢复 | [领域状态机](domain-model.md)、[运行时](architecture/runtime.md) | WP-03/04/07 | AC-08/09/10/11 |
| R-10 文件产物 | [领域模型](domain-model.md)、[环境](architecture/execution-environments.md) | WP-05/08 | AC-13 |
| R-11 权限审批 | [安全](security-and-permissions.md)、[API](api-and-events.md) | WP-02/06/07 | AC-02/07/12/19 |
| R-12 观测预算 | [运行时](architecture/runtime.md)、[运维](operations.md) | WP-03/07/12 | AC-17/18/21 |
| R-13 测试发布 | [Creator](architecture/creator.md)、[测试策略](testing-strategy.md) | WP-01/10/11/13 | AC-14/15/16/23 |
| R-14 协作审阅 | [用户流程](user-experience.md)、[领域状态机](domain-model.md) | WP-08/09 | AC-06/08/13/20 |

## 实现缺口的归属

LangGraph负责持久控制与checkpoint，Deep Agents负责执行harness；员工归属、跨Space授权、任务权威状态、Creator治理、artifact与审阅均由本产品合同提供。框架存在对应名词不能视为需求已完成。

新增需求须新增R编号、明确MVP范围并分配WP/AC；改变既有需求语义要记录ADR，不能只修改一处提示词。
