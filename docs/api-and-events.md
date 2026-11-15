# API、设备协议与执行事件

状态：v0.1 设计合同，尚未实现；日期：2026-11-15。以 [领域模型](domain-model.md) 为状态权威。本文为实现目标，不是当前可调用 API；实现阶段生成 OpenAPI 并做合同测试。

## 1. 通用规则

- HTTP 前缀 `/v1`，JSON 字段使用 snake_case，ID 用 opaque UUID/ULID，时间为 RFC3339 UTC；前端按用户时区显示。
- 所有请求认证。space_id 来自路径并与 principal 的 membership/grant 交叉验证，不能信任请求体中的 owner/tenant 字段。
- 创建及有副作用控制操作携带 `Idempotency-Key`。相同 key+相同规范化 body 返回原结果；不同 body 返回 409。任务创建键至少保留至 Task 保留期结束，工具动作账本独立保存。
- Task 创建返回 `202 {task_id,state,events_url}`。禁止让长任务生命周期依赖 HTTP/SSE 连接。
- 列表使用 opaque cursor + limit（默认 30，最大 100）；不能暴露底层主键遍历其他 Space。
- 错误结构：`{error:{code,message,request_id,retryable,details}}`。details 不包含密钥、私有文件内容或其他 Space 元数据。
- 常见状态码：401 未认证；403 无权限；404 不可见或不存在；409 版本/状态冲突；422 schema/能力不兼容；429 容量限制；503 可重试依赖失败。
- 可变资源用 `row_version`／`If-Match` 防覆盖；未知字段拒绝。Action 的授权必须执行时再次检查。

## 2. 主要端点

| API | 语义 | 阶段 |
| --- | --- | --- |
| GET /v1/me/spaces | 当前用户可见个人／团队空间 | M1 |
| GET /v1/spaces/{space_id}/capabilities | 可装配能力、版本、参数 schema、可用位置和权限要求 | M1/M5 |
| GET/POST /v1/spaces/{space_id}/agents | 列出／实例化已发布版本；模板不复制凭据与私有记忆 | M1 |
| PATCH /v1/spaces/{space_id}/agents/{id} | 修改展示名、受授权的默认版本等；不修改历史 revision | M5 |
| POST /v1/spaces/{space_id}/tasks | 按 task-create schema 创建任务、固定 revision 与位置，写事务 Outbox | M1 |
| GET /v1/spaces/{space_id}/tasks/{id} | 业务状态、原因、允许的结果和操作，非全部内部模型历史 | M1 |
| POST /v1/spaces/{space_id}/tasks/{id}/pause | 请求安全边界暂停；可返回 pending 操作而不假称已停止 | M3 |
| POST /v1/spaces/{space_id}/tasks/{id}/resume | blocked 条件已满足后转 queued | M3 |
| POST /v1/spaces/{space_id}/tasks/{id}/cancel | 撤销执行权，记录无法撤销或未知的外部动作 | M3 |
| POST /v1/spaces/{space_id}/tasks/{id}/retry | 创建新 Task，返回新的 task_id | M3 |
| POST /v1/spaces/{space_id}/tasks/{id}/inputs | 追加资料／artifact引用，解除waiting_input；不允许改execution或授权范围 | M3 |
| POST /v1/spaces/{space_id}/tasks/{id}/reconcile | 核对unknown动作：confirm_completed/confirm_not_executed/abandon，必须带证据与操作者授权 | M3 |
| POST /v1/spaces/{space_id}/tasks/{id}/reviews | accept/rework，必须指向具体 ArtifactVersion | M4 |
| POST /v1/spaces/{space_id}/tasks/{id}/children | 同 Space 委派，限制负责人、深度、预算和输入 | M4 |
| POST /v1/spaces/{space_id}/delegations | 跨 Space 发起受限请求，源方不能直接创建目标私有 Task | M4 |
| POST /v1/spaces/{space_id}/delegations/{id}/accept | 目标 owner/policy 受理并创建目标 Task；批准共享与输入 grant | M4 |
| POST /v1/spaces/{space_id}/approvals/{id}/decide | approve/reject；验证操作者、expiry、参数及 revision 摘要 | M3 |
| GET /v1/spaces/{space_id}/tasks/{id}/events | SSE，支持 Last-Event-ID 和补拉 | M1 |
| POST/GET /v1/spaces/{space_id}/artifacts | 受限上传／目录；大文件使用短期上传授权并在提交时校验 hash/大小 | M2 |
| GET /v1/spaces/{space_id}/artifacts/{id}/versions/{version}/content | 鉴权后生成短期下载或流式内容 | M2 |
| POST/GET /v1/spaces/{space_id}/rooms | 项目群／私聊／任务线程 | M4 |
| POST /v1/spaces/{space_id}/rooms/{id}/members | 邀请人或 Agent；个人助手需要 owner 同意及委派 scope | M4 |
| POST /v1/spaces/{space_id}/rooms/{id}/messages | 写消息；显式 @ 或创建任务动作按规则分派，不广播唤醒所有员工 | M4 |
| POST /v1/spaces/{space_id}/creator/drafts | 需求输入，产生草稿和有界 Creator Task | M5 |
| PATCH /v1/spaces/{space_id}/creator/drafts/{id} | CAS 编辑，清除过期 validation_digest | M5 |
| POST /v1/spaces/{space_id}/creator/drafts/{id}/validate | 静态校验、受限测试，生成验证报告 | M5 |
| POST /v1/spaces/{space_id}/creator/drafts/{id}/publish | 校验最新 digest 后发布不可变 revision，无自动扩大授权 | M5 |
| POST /v1/spaces/{space_id}/creator/drafts/{id}/extensions | 缺口交给编码专员，生成 Python 工具包草稿 | M6 |
| POST /v1/device-pairings | 登录用户生成一次性短时配对码 | M3 |
| POST /v1/device-pairings/claim | 本机换取设备专用凭证，绑定 owner/Space/设备授权 | M3 |
| POST /v1/devices/{id}/revoke | 撤销连接和后续工具派发权限 | M3 |
| POST /v1/devices/{id}/local-files | 已配对设备登记获授权文件元数据，返回local ArtifactVersion引用，不上传文件正文 | M3 |

任务最小请求见 [示例](../examples/tasks/cloud-research.json)。字段合同由 [schema](../schemas/task-create.schema.json) 定义。服务端补足 assignee 的授权 revision、space_id、execution session 和预算预留；客户端不能使用 capability 配置字段直接注入工具实现。

## 3. 运行接口

内部 `AgentRunner` 暴露 `start(context), resume(checkpoint, input), request_pause(), cancel(), events()` 的语义合同；具体 Python 签名在 M0 spike 后冻结。

`RunContext` 至少含 task_id、session_id、revision/lock digest、principal/delegation scope、输入产物引用、deadline、预算预留、effective policy、workspace handle、lease fence。不要把原始主密钥作为 RunContext 的序列化字段。

工具必须通过 ToolGateway：`prepare -> authorize/approval -> dispatch -> record outcome`。普通 Python callable、shell 和插件不能绕过这一入口取得额外 authority。

Task与children创建请求必须携带acceptance_contract。审批拒绝/过期注入denied observation，补充输入与unknown核对分别使用inputs/reconcile端点；状态迁移细则见领域合同“阻塞条件如何解除”。通用resume不能代替这些操作。

## 4. 本地设备协议

本地 daemon 主动发起 TLS WebSocket 连接 `/v1/devices/connect`；服务端验证设备凭证、协议版本、所有者和可用 scope。MVP 不开放本机公网监听端口。

帧结构：`{protocol_version:"1", type, message_id, correlation_id?, sent_at, payload}`。服务端派发至少携带 `task_id, session_id, attempt_id, fence, command_id, expires_at, allowed_root_ids, action_scope`。执行器拒绝过期、旧 fence、未登记根目录和未知命令类型。

| 帧 | 方向 | 作用 |
| --- | --- | --- |
| hello / welcome | 双向握手 | 版本、设备 ID、容量与已授权能力摘要 |
| heartbeat | 设备→服务端 | 存活、活动 attempt；默认 15s，上限与阈值可配置 |
| run.assign / run.ack | 服务端→设备／确认 | 派发本地 Task attempt；ack 只是接单，不等于产生副作用 |
| run.event | 设备→服务端 | 持久结果和状态事件；带稳定 sequence/message_id |
| run.pause / run.cancel | 服务端→设备 | 安全暂停／尽力中止；必须回报实际状态 |
| run.reconcile | 双向 | 重连核对活动 fence、checkpoint 和未确认结果 |

默认 45s 未收到心跳可标记设备离线；不能仅凭离线就认定工具没有执行。已开始动作结果不明时进入 recovery_required。重连事件去重、旧 owner 拒绝和结果核对必须有集成测试。

任务位置 local/cloud 不因设备重连变化。本地输入未授权上传时，只能留在设备；需要回传的产物由 owner 授权并校验目标 Space。

本地文件引用登记：daemon在已授权root_id下解析相对路径并检查symlink逃逸，保存本机manifest `(file_token,root_id,relative_path,sha256,size,mtime)`。云端仅保存用户批准的元数据 `(device_id,root_id,opaque file_token,sha256,size,mime_type,display_name)` 与ACL，不保存原始绝对路径或文件正文。每次读取重新校验hash/大小与根目录授权；内容变化须登记新ArtifactVersion，不能静默读取新内容。cloud任务收到location=local的引用应拒绝直接解析，或通过显式本地子任务取得经授权结果，不能偷偷上传。

## 5. 持久事件

事件 envelope 的规范见 [schema](../schemas/task-event.schema.json)：

```json
{"schema_version":"1","event_id":"evt_01","space_id":"space_team_demo","task_id":"task_01","sequence":1,"type":"task.created","occurred_at":"2026-11-15T00:00:00Z","payload":{"state":"queued"}}
```

event_id 全局唯一，sequence 在一个 Task 内严格递增。UI 可以至少一次收到事件，通过 event_id 去重；Last-Event-ID 是补拉游标，不是权限令牌。游标过期返回明确的 events_cursor_expired 并指引重新读取 Task 快照。

| 事件 | 最小 payload |
| --- | --- |
| task.created / task.state_changed | state, blocked_reason?, row_version |
| run.started / run.finished / run.lease_lost | attempt_id, fence, outcome? |
| tool.prepared / tool.completed / tool.unknown | call_id, capability_id, safe_summary, receipt_ref? |
| approval.requested / approval.decided | approval_id, action_digest, decision? |
| task.child_created / delegation.updated | opaque relation_ref, public_state |
| artifact.published | artifact_id, version, digest, mime_type |
| budget.updated / budget.exceeded | reserved, consumed, remaining, unit |
| task.review_requested / task.reviewed | artifact_versions, review_id, decision? |

token delta、模型中间输出、终端高频日志使用独立非权威流；默认不写入完整业务事件表。最终答复、状态和产物必须持久化。禁止将模型隐藏推理、凭据、全量私有 tool payload 广播到群。

## 6. 并发、幂等与授权负例

- 同 key 不同 Task body：409，不能创建第二个任务。
- 同一审批被两次批准：返回原决定；更改参数后旧审批失效。
- worker 在新 fence 生效后返回：事件可记为诊断，不能改当前 Task 状态或发布正式产物。
- 已取消任务的 SSE 仍可读取已授权历史，但不能用旧签名开始新工具动作。
- Team 管理员不能据 personal agent ID 查询个人 session；跨 Space 返回受限 delegation 视图。
- Artifact 下载授权过期后不能继续复用；已撤销 grant 不能创建新下载链接。

字段错误码与端点 OpenAPI 示例在 M1-M6 随对应功能补齐，并保留本设计与实际接口的变更记录。
