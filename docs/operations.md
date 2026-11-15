# 调度、运维与恢复

状态：v0.1 运维设计，尚未实现。日期：2026-11-15。本文的组件、指标和 runbook 是交付目标，不表示已经有可运行命令或监控面板。

## 1. 首版运行形态

默认FastAPI控制面、PostgreSQL业务库、Python worker、React Web和本地daemon/CLI。dispatch由M0在成熟持久队列与外层Temporal中选择，不能将下文参考流程解释为要求自研通用队列。云/本地共享产品合同；具体队列、认证服务与观测后端尚未安装或选定。

生产配置与开发配置分开。开发 Docker sandbox 仅用于可信 beta 的能力和生命周期验证，公开恶意多租户生产能力参见[风险清单](risks-and-open-questions.md)。详细状态转换以[领域模型](domain-model.md)为准。

## 2. 调度适配与执行权（PG参考路径）

本节是当前PG参考合同：队列库承担投递、worker生命周期、重试/定时；薄层映射产品Task、执行权和账本。若M0选Temporal，先把API命令、Task数据库投影、workflow历史、恢复引用和预算/审批信号的权威写入合同，再替换本节；禁止在现有调度旁简单并行再加一套。

1. 创建 Task 与其初始 DomainEvent/Outbox 在同一事务提交，HTTP 返回 202。
2. 调度器按 `available_at`、能力、Space 配额和设备状态选择任务；数据库短事务认领，不能在数据库行锁内等待 LLM 或 shell。
3. 领取工作时原子检查当前状态、预算预留和 active lease，创建 RunAttempt、递增 fence，转 running。
4. worker 按配置续约；事件／工具 dispatch／正式产物写入再次校验 fence。队列投递与回调都允许重复，按稳定 ID 判重。
5. 过期 lease 先作废旧执行权，再检查工具账本与 checkpoint。安全段可重排；未知外部结果进入 blocked / recovery_required。
6. Outbox 独立重试通知；通知失败不回滚已完成任务。轮询／SSE 从持久事件补拉，不靠内存广播认定成功。

任务 queued/running/blocked 等业务状态不从 job 的投递次数推导。worker 接单 ack 不等于工具执行成功，lease 过期不等于外部动作没有发生。取消的 Task 即使收到旧回调，也不能复活。

调度至少限制每 Space、每 AgentInstance、每设备、每云 provider 的并发。队列按 Space 做公平轮转或等价限额，避免一个员工创建大量子任务独占 worker。任务派生深度、子任务数量和总预算同样有服务端上限；轮询和失败重试带退避与抖动。

## 3. 预算与容量

Task 固定 token／模型费用、工具费用、sandbox 时间、最长时长与子任务预算策略。执行前预留，在每个工具／模型动作前检查剩余额度；最终记录 provider receipt 和实际消耗，估算值与结算值分开。

`max_runtime_seconds` 按同Task各attempt累计的活跃执行时间计算，排队、blocked、review等待不计，恢复不清零；并行分支活跃秒数相加。另有独立 `deadline_at`，默认创建后24小时，等待同样不能越过deadline；到期按领域合同结束，不因resume延长。

同 Space 子任务预留来自父任务允许的总预算，不能把父子预算重复当成可消费余额。跨 Space DelegationRequest 指定承担方及上限，目标方受理时确认；未明确承担方则拒绝受理。

超预算停止新增动作并保存可恢复结果，按主状态合同转 failed；不能自动加钱或无限重试。已提交的 provider 请求可能事后产生费用，预算不是供应商账单的绝对硬上限。provider 不返回价格或账单尚未结算时显示 unknown/estimated，不用零代替。

容量不足与 provider 故障采用有界排队和 backoff。不得因资源不足把指定 local 任务移到 cloud，也不得改用权限或数据地域不匹配的 provider。任务 deadline 到期与用户取消分别保留原因。

## 4. 可观测性

复用OpenTelemetry和一个选定的LLM观测后端，优先已有LangGraph/Deep Agents集成；不自建trace采集、查询与评估平台。业务状态/审计仍按产品合同持久化，观测trace不是Task状态来源。脱敏、存储地域与Space可见性在导出前校验。

每条 trace 关联 Space、Task、ExecutionSession、RunAttempt、fence、工具 call_id 与 delegation relation；跨 Space 页面仅显示 viewer 被授权的数据。高频 token delta 与终端输出为非权威流，业务状态、最终结果和正式产物必须持久化。

| 维度 | 首批指标／排查信息 |
| --- | --- |
| 调度 | queued 数量、最久等待时间、claim/renew 失败、lease expiry、旧 fence 拒绝 |
| 任务 | 成功／失败率、运行时长、各 blocked_reason 数量与等待时长、review积压 |
| 工具 | latency、失败／unknown、副作用判重、审批请求／超期、provider receipt |
| 设备 | 在线状态、心跳间隔、重连次数、待核对 command、本地容量 |
| 沙箱 | provision 时间、活跃／空闲环境、释放失败、孤儿资源、存储用量 |
| 费用 | reserved/consumed/unsettled、预算拒绝、每 Task 的模型／工具／计算成本 |
| 数据 | DB/对象存储备份状态、恢复演练结果、Outbox延迟、manifest一致性 |

聚合指标避免把私有内容放入 labels；长 ID 适合日志/trace 查询，不默认成为无界 metrics label。日志不保存主密钥、OAuth refresh token、完整环境变量、隐藏推理或未经批准的文件正文。审计与调试日志分别授权，保留/清理周期由 owner 配置。

告警聚焦需要行动的状态：持续调度停止、DB不可用、未知副作用积压、费用异常、设备凭据撤销失败、孤儿沙箱超限、备份/恢复验证失败。单纯人审等待与用户暂停不当成基础设施故障。

## 5. 备份范围与恢复目标

必须联合备份 PostgreSQL 中的任务/事件/授权/revision/账本/checkpoint、云 TaskWorkspace manifest、ArtifactVersion 内容及其 hash。数据库备份只含 storage_ref 而对象已丢失时，不算完整恢复。

若采用Temporal，还要对workflow历史、版本与保留/恢复方案制定一致性策略；不能只备份产品PG就宣称可恢复。采用官方集成时checkpoint归属按M0决策调整，不在PG和workflow历史间保存两套独立恢复权威。

密钥由独立 secret store 的备份／恢复流程管理，不能把主密钥混入 workspace 归档。备份加密、权限隔离，并至少保留一个不依赖同一运行节点的副本。RPO/RTO、备份频率和保留周期在部署选型后实测约定；本文件不编造可用性或零数据丢失承诺。

本地私有 TaskWorkspace 默认不上传；用户需独立配置本机备份。控制面恢复后发现设备或文件缺失，应显示等待／需要恢复，不能静默改成云文件。artifact grant 和删除记录必须随备份恢复，防止撤销共享的数据重新变为可见。

恢复演练应使用隔离环境、替代测试凭据并禁用真实外部写工具；从生产备份启动的系统不能自动重发历史邮件或消息。

## 6. 故障处理 Runbook

### 6.1 worker 或控制面重启

先恢复 DB 连接与 migrations 兼容性，再启动读服务；以持久 lease 为准核对未结束 attempt。旧 fence 失效后，从账本区分 completed、未派发和 unknown 工具。仅安全工作回 queued；unknown 进入 recovery_required。最后开放新任务调度，核对 Outbox 和沙箱清理队列。

### 6.2 本机离线／设备撤销

15 秒心跳、45 秒离线是初始默认。未执行本地任务进入 waiting_device；已开始且结果不明的动作进入 recovery_required。重连先核对未确认事件再接单，不重放全部历史命令。撤销设备后拒绝新连接／新动作，尽力停止现有动作并明确展示无法确认终止的工作。

### 6.3 外部动作结果未知

冻结该 action_key 的自动重试，检查 provider receipt、幂等键和外部业务记录。授权操作者选择“确认已完成／确认未执行／放弃”，记录证据与审计；尚未知则继续保持blocked。确认未执行前还须确定旧进程已终止；确认后由新 attempt 接续，放弃则终止。不能只按“超时”选择重发。

### 6.4 沙箱释放失败或孤儿资源

以 SandboxLease 与 provider inventory 对账。先确认没有有效 attempt，再停止环境；最终文件未归档时标记并处理，不先删除唯一副本。记录资源费用、重试次数和人工处理入口。清理程序本身按 Space／environment ownership 校验，不能按名字通配删除。

### 6.5 数据恢复

暂停写入与调度，恢复相互匹配的数据库和对象内容；验证 schema、hash、ACL、grants、工具账本和checkpoint。全部旧执行租约失效，设备重新核对。先用只读测试任务验收，再逐步开放真实执行。恢复到较旧备份时，对外部已经发生而DB未记录的动作进入核对流程，不自动追赶重放。

## 7. 升级与删除

AgentRevision/lock 不变；运行中的 Task 不随实例默认 revision 更新。框架、checkpoint schema、工具包和沙箱模板升级先用固定恢复样本验证，保留回滚路径。数据库 migration 的回滚能力与业务兼容窗口单独评估，不能假设降级总是安全。

删除计算、删除Task、删除产物与删除审计是不同操作。beta 默认不自动删除正式产物、工具账本和审计；先提供 owner 可审阅的保留策略与清理预览。对账本、幂等键的保留至少覆盖对应 Task 的保留期与可能回调窗口；隐私删除与审计保留冲突见风险清单。

## 8. 阶段验收

- M1：双 worker 重复认领、Outbox重复投递、旧 fence、SSE断线补拉。
- M2：worker被终止后的checkpoint恢复、文件manifest一致性、孤儿沙箱清理和API-only零沙箱路径。
- M3：设备断线／关机、重复命令、撤销、pause/resume/cancel、改参审批和unknown动作核对。
- M4：父子任务预算、跨Space受理／共享、群聊重复回调与权限负例。
- beta交付：至少一次隔离恢复演练；报告实测恢复时间、数据缺口、费用差异和未解决事项。

[Temporal Activities官方文档](https://docs.temporal.io/activities)可用于理解重试、幂等与执行边界。调度实现尚待M0选择，本项目当前未实现DB队列或Temporal运行链，也不因此宣称具备任一组件的全部保证。
