# 测试、评估与证据策略

状态：实施目标；产品测试尚未建立。验收合同见 [acceptance.md](acceptance.md)。

## 1. 分层验证

| 层级 | 验证内容 | 是否需要真实模型 |
| --- | --- | --- |
| 声明/合同 | schema、未知字段、能力依赖、环境兼容、状态转换、事件格式 | 否 |
| 领域单元 | 授权交集、预算、审批摘要、版本固定、委派深度、review规则 | 否 |
| 持久集成 | 真PostgreSQL事务/队列/Outbox/租约、checkpointer、重启 | 否；runner可fake |
| 环境集成 | 真Docker执行、目录隔离、回收、真实本地daemon和TLS配对 | 否 |
| 框架适配 | 真DeepAgents loop、工具、interrupt/resume、模型provider格式 | 是，另有fake回归 |
| 业务评估 | Creator、统筹、报告准确性、表格计算、可复用代码扩展 | 是 |
| 部署验收 | 独立云机、客户端离线、恢复演练、秘密撤销 | 是，含确定性故障路径 |

组件选型还有AC-27：锁定版本、许可与维护评估、标准adapter合同和恢复权威；成熟库的单元测试通过不替代本产品集成/隔离/故障实验。只验证首批实际接入的provider，不搭建多provider平台后再证明最小闭环。

不要为每个prompt写精确字符串断言。确定性状态与计算使用机器断言；开放式内容使用明确rubric、证据引用与必要人工复核。

## 2. 必须覆盖的故障注入点

在提交Task前后、Outbox投递前后、领取lease后、模型响应后、审批请求写入后、外部工具发出后回执前、checkpoint写入前后、artifact上传后登记前、取消和旧worker晚回结果时注入故障。

每个点回答：权威状态在哪里；可否安全重试；哪个幂等键判重；旧lease如何失效；是否保留产物；unknown如何呈现。不能以进程没有报错作为通过。

PostgreSQL业务事务与框架checkpoint不共享原子事务时，增加可恢复的执行账本和reconciler。用测试证明中间状态最终进入queued、blocked/recovery_required或终态，而不是永久running。

上述为PG参考路线。若选Temporal，测试workflow重放、activity重试、状态投影与原生Codexjob续接，并先变更相应合同。每种副作用只允许一个自动重试控制者，超时未知时各层均不得各自发起重试。

## 3. 权限与隔离负例

- 个人和团队Space的Task、memory、session、artifact、日志、下载授权不可互读。
- 传入其他Space ID、旧审批、旧fence、失效设备token、猜测artifact路径均被拒绝。
- 统筹不能替个人助手批准私有数据共享；移除群成员与撤销grant影响后续调用。
- 模型输出、网页、技能文件、生成代码均不能作为扩大权限的依据。
- 代码插件既验证输入，也通过受控网关获得外部动作；不能仅检查模型工具列表。

## 4. 真实模型评估

固定输入集合，记录模型精确ID、配置、AgentRevision、工具版本、调用预算和数据快照。每场景5次，按AC-23评分。失败保留脱敏trace和文件，标记原因：模型、prompt、工具、上下文、授权、依赖、调度或样本问题。

先建立低成本smoke：一个工具任务、一项代码计算、一次配置Creator。完整评估在release gate和相关行为变化后运行，避免每次文档修改都重复昂贵调用。

测试凭据隔离于生产；外发副作用使用受控测试服务；实际邮件/业务写入另有明确测试授权。

## 5. 建议CI层次

PR快速检查：docs/schema、lint/typecheck、单元、PostgreSQL集成、Docker边界用例。模型评估由维护者触发或发布前执行，凭据只对可信分支开放，不能把secret交给不可信PR代码。

M0创建真实CI和命令后在[开发指南](development-guide.md)中登记。当前已有的检查仅是 `python3 tools/check_docs.py` 和安装文档依赖后的 `--schemas`。

## 6. 证据目录目标

实现阶段在 `docs/evidence/<milestone>/<date>/` 保存摘要、命令结果及脱敏ID，较大文件放受控对象存储并记录hash。报告包含通过、失败、未运行三种状态；失败重跑保留原结果，不只保留最后一次成功。

真实用户资料、私有模型上下文和凭据不能上传公开Git仓库。公开证据使用合成数据；内部证据使用访问控制链接。
