# 风险、可逆默认与待决事项

状态：v0.1 设计基线，尚未实现。日期：2026-11-15。用于记录需要实验或产品决定的问题，不把尚未验证的能力写成已交付承诺。

## 1. 已确定，后续会话无需重新询问

- 自有Agent基座，采用 LangGraph / DeepAgents；Creator 生成受验证声明与不可变版本。
- 个人助手与组织数字员工是归属维度，执行位置由创建 Task 时显式选 local/cloud；无自动迁移。
- 用户离线或个人电脑关机后，已委派的 cloud Task 继续；local Task 依赖设备在线，不能凭空改云执行。
- 云任务需要仅本机存在的能力时，显式创建 local 子任务；涉及个人Space使用 DelegationRequest。
- 一个Task只有一个负责人；持久员工间委派创建独立Task/session/workspace，临时内部subagent遵循受限执行策略。
- TaskWorkspace持久，SandboxLease按ExecutionSession租用；唯一session键为 `(tenant_id,agent_instance_id,task_id)`。
- Space就是tenant边界；MVP覆盖同一部署个人空间与一个可信团队通过预授权pair协作。
- 主状态、blocked_reason、lease/fence与终态retry语义以[领域模型](domain-model.md)为准。
- devDocker不等于敌对多租户强隔离；任意第三方互联、专属sticky环境、进程热迁移后置。

## 2. 可逆的实现默认

| 项目 | 当前默认 | 何时重新评估 |
| --- | --- | --- |
| 控制面／执行 | FastAPI、Pythonworker、PostgreSQL+DBjobs | 实测吞吐、恢复或调度复杂度超出当前模型时 |
| UI／设备 | React Web、本地Pythondaemon+CLI、出站TLS连接 | 桌面发行、自动升级与本地集成需求明确后 |
| 沙箱 | session按需租用、完成/idle释放；API-only不开沙箱 | 实际工具需要长期机器状态或冷启动成本显著时 |
| 文件 | TaskWorkspace持久、独立任务写目录、产物版本不可变 | 经测量需要共享文件系统／大文件分层时 |
| 设备在线 | 心跳15s，离线45s | M3网络抖动与设备功耗实验后 |
| 最终验收 | 默认human review，内部只读子任务可显式auto | 有业务验收集、权限和回归证据后 |
| 数据清理 | beta不自动删除正式产物／账本，先做预览 | owner确定保留周期、备份和隐私删除要求后 |

这些默认不是上游产品、供应商或未来infra的承诺。修改默认需要同步schema、API、示例、ADR与验收用例。

## 3. 按里程碑阻塞的问题

| 问题 | 影响／必须取得的证据 | 阻塞范围 |
| --- | --- | --- |
| LangGraph/DeepAgents具体版本和checkpoint行为 | 固定版本后跑中断、恢复、重复节点、工具审批与并发session实验；确认内建工具可接ToolGateway | M0完成，进入稳定runtime前 |
| 云sandbox provider及文件持久化实现 | 测试创建/销毁/资源限额/重启/成本计量，决定持久卷或对象manifest；确认地域和实际可用性 | M2真云执行；本地Docker实验可先行 |
| 用户认证及部署入口 | owner、membership、个人Space、设备凭证的可信来源，TLS及secretstore配置 | 对非开发者开放beta前 |
| 外部IM适配 | 首版采用Web内置项目群；飞书等外部渠道以后再确定机器人身份、回调验签与附件权限 | 不阻塞M4内置群聊，启用外部渠道前验证 |
| 工具权限与账号范围 | 先选一组办公工具，明确每个读/写/发送能力及测试账号，验证scope和provider幂等支持 | 对应真实工具启用前 |
| 个人／团队pair委派策略 | 目标owner受理、预算承担方、可共享输入/结果、撤销语义的合同测试 | M4跨Space功能 |
| RPO/RTO与保留政策 | 联合DB/对象恢复实测、备份可访问性、账本保留窗口与隐私删除规则 | beta交付的恢复验收 |

以上是实施前置条件；不必一次性向用户收集全部答案。先完成可独立验证的阶段，在需要启用对应能力时提出具体可选方案。

## 4. 主要技术风险及处理

| 风险 | 处理与仍有的限制 |
| --- | --- |
| graph重复执行节点导致外部副作用重复 | ToolGateway稳定action_key+账本+provider幂等键；unknown进入recovery_required，仍不承诺exactly-once |
| 旧worker在网络分区后继续动作 | 有效lease/fence拦截状态、dispatch和产物；已发出的外部请求未必可撤回 |
| 聊天checkpoint被误当机器快照 | workspace、账本、graph分别持久；只在验证过的安全边界接续，浏览器/进程热迁移不在范围 |
| 同一员工并行任务污染上下文与文件 | session/task隔离、独立workspace、版本化产物；共享长期记忆写入带来源和CAS |
| 团队委派窃取个人权限 | 独立Space、预授权pair、目标受理、最小grant；源方不可读取目标Task私有资源 |
| shell/插件绕过工具权限 | 内建动作工具适配ToolGateway，代码在受限环境执行；可信beta不允许把prompt约束称为恶意代码隔离 |
| 本地盘或云临时盘丢失 | workspace持久化和恢复演练；未经授权备份的本地文件可能无法恢复 |
| prompt injection污染任务或记忆 | 外部内容当数据、权限在执行层检查、共享与长期记忆写入显式；不能承诺彻底消除模型受诱导 |
| 费用与任务爆炸 | 总预算预留、子任务深度/数量、Space配额与公平调度；provider迟到费用仍须对账 |
| 插件/模型/provider版本变化 | capability lock、不可变revision、版本兼容矩阵和恢复样本；升级前不假设旧checkpoint可读 |
| 资源释放失败持续计费 | inventory对账、孤儿清理队列和告警；不把业务终态与provider资源释放混成一项事务 |
| 结果在群里泄露敏感内容 | 发布/共享分别授权、按viewer投影事件和artifact；已合法下载内容无法远程召回 |

## 5. 许可证、服务条件与infra

当前技术路线不意味着任意依赖、模型、工具或sandbox服务均可不受限制商用。M0/M2/M6建立精确依赖清单，记录锁定版本、许可证文件、第三方通知、模型/API服务条件和再分发限制；没有核实前不写“全部可自由商用”。

开源SDK、托管服务、模型权重和品牌是不同授权对象。研究中的产品可作设计参考，不代表fork它或复用其账户登录方式已获得商业授权。尤其不能把旧项目的历史许可自动套用于当前改名／新版本。

供应商价格、配额、地域、国内网络可达性和数据驻留以实际账号与合同验证；本设计不锁定尚未选择的厂商，也不承诺无限免费、零冷启动、固定SLA或合规认证。

## 6. 明确后置的能力

- 任意第三方Agent发现与跨部署A2A联邦。
- 未审查工具/skills市场、运行中自改生产系统提示词及权限。
- 云本地自动迁移、浏览器/进程级热迁移、设备失联自动换位置。
- 每员工永久VM、个人全盘同步、cookie自动搬运。
- 面向恶意互不信任租户的公共生产隔离认证。
- 没有业务验收集的全自动关键外部写入。

这些项目不会阻塞当前范围内的Web/IM任务、显式云委派、本地设备任务和个人／团队受控协作。

## 7. 决策与证据记录

每项新决定记录：日期、owner、选项、选择理由、验证证据、影响合同、回滚办法。会改变领域状态、tenant边界、session唯一键、执行位置或权限含义的决定，先更新领域模型与ADR，再改代码。

研究链接是辅助证据，不能代替版本锁定后的本地实验：[OpenHands架构](https://docs.openhands.dev/sdk/arch/overview)、[OpenClaw信任边界](https://docs.openclaw.ai/gateway/security)、[LangGraph持久化](https://docs.langchain.com/oss/python/langgraph/persistence)。
