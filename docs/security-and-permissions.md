# 安全、授权与个人／团队边界

状态：v0.1 设计基线，尚未实现。日期：2026-11-15。规范状态与实体见[领域模型](domain-model.md)，执行位置与资源见[执行环境](architecture/execution-environments.md)。

## 1. 首版承诺范围

首版面向单个可信团队的 beta，同时支持同一部署内的个人 Space 和团队 Space。`tenant_id=space_id` 从首版进入查询、存储、队列、checkpoint、产物和设备授权；可信团队不是省略隔离的理由。

本版本不承诺可安全承载公开、互不信任、可上传任意代码的多租户生产服务。开发用 Docker 提供受限执行与生命周期验证，不替代此级别的隔离评估。Space owner/admin 也不因此拥有另一个个人 Space 的权限。

## 2. 权限计算与执行主体

登录、身份验证与token校验优先对接标准OIDC身份源及成熟客户端，不自建密码、MFA或OAuth协议。用户认证并不等于员工动作授权；下列资源、委派与审批规则仍由产品执行。选定身份源及启用范围由M0/M1记录，不能默认所有候选服务已集成。

每次工具执行的有效权限为：

```text
caller 已授权的委派范围
  ∩ callee AgentInstance / 固定 revision 配置
  ∩ owner 所绑定账号的实际 scope
  ∩ 目标 Space 的 tenant policy
```

还须校验具体资源 ACL、有效 lease/fence、预算、deadline 和必要审批。缺少任一授权则拒绝或进入明确等待状态；不能以“Agent 判断必要”为理由提升权限。

Task 保留原始发起人、代表谁执行、委派链、目标 owner 与策略版本。群里 `@` 某个员工只表示路由请求，拉入个人助手也不等于批准调用其私人账号。管理员角色、展示人格、工具执行 principal 分开记录。

AgentRevision 发布不可变且不含凭据。工具、shell、browser 和内建文件能力都进入 ToolGateway 的 `prepare -> authorize/approval -> dispatch -> record outcome` 路径。接入 DeepAgents 时必须替换／包裹会产生实际动作的内建工具；未接入授权账本的高权限能力暂不启用。Python 代码层“调用了网关”不构成恶意插件无法绕开的安全沙箱；M6 自定义代码仍需独立执行与审查。

本段逐工具承诺只适用于自有Deep Agents路径。内置Codex是专用执行器，平台限制job scope、输入、工作区、网络、账号、资源和正式结果发布，配合原生审批，不宣称拦截所有内部调用。首版Codex不提供生产写入/外发/正式发布凭据；旧fence阻止新job和正式产物接纳，仍运行的原生命令需由进程/环境停止或核对处理。详见[执行器边界](architecture/coding-executor.md)。

## 3. Space 与数据授权

- API 根据已认证 principal、membership/grant 和路径交叉计算 Space；不信任 body 中的 owner/tenant 字段。
- 所有资源查询、队列认领、checkpoint thread 映射包含 Space。opaque ID、event cursor、文件路径和对象存储 key 都不是授权证明。
- TaskWorkspace、ArtifactVersion、日志、缓存分别记录 owner 与 scope；单独测越权读取、列表、下载、搜索和事件订阅。
- 数据库行级策略可作为补充；应用服务层授权与后台 worker 授权仍然必需。后台账号不能因可访问全库而跳过 Space 检查。
- 普通错误与观测数据不泄露其他 Space 是否存在、员工名字、文件内容或凭据状态。

长期记忆按个人／员工／项目 scope 保存来源、版本和保留策略。群聊历史不自动注入所有员工，个人记忆不自动同步到团队检索索引。共享动作产生显式 Grant；撤销后禁止新读取／新下载授权，已合法下载到接收方的数据无法假称远程召回。

## 4. 跨 Space 委派

首版必须支持个人助手与单团队员工通过预授权固定 Agent pair 协作：

1. 源 Space 创建 DelegationRequest，声明目标、目标 agent、输入授权引用、结果 scope、预算承担者与期限。
2. 目标 owner 或其预授权 policy 检查 pair、caller、输入用途、工具范围和预算，明确受理或拒绝。
3. 受理后在目标 Space 创建 Task；`parent_task_id` 仅允许同 Space，跨 Space 保留受限 relation。
4. 双方只能获取各自允许的请求／状态视图。源方不能靠目标 task ID 读取 session、记忆、日志或账号。
5. 目标方发布被批准共享的 ArtifactVersion/grant；回传 scoped artifact refs，不直接暴露私有 storage_ref。

团队任务需要个人本机能力时，也按此流程创建目标个人 Space 的 local Task。结果共享与任务受理是不同授权，不能把“允许读个人文件完成分析”等同“允许向全群公开原文件”。真正跨部署、任意第三方联邦和自动信任 A2A Agent Card 后置。

## 5. 工具授权与审批

审批绑定 `task_id + revision_digest + action_key + args_digest + resource_scope + expires_at + approver_id`。只有具备对应 scope 的人或既有明确 policy 能批准；参数、对象、revision、期限变化后旧批准失效。

审批前保存 pending call 与 checkpoint，进入 blocked / waiting_approval 并释放运行租约。批准后 blocked -> queued，取得新 attempt/fence，实际 dispatch 前重新校验授权。拒绝或过期时记录denied observation并转queued，Agent仅可在原授权范围内调整，无法完成则failed；同一摘要不得反复申请绕过拒绝。已执行动作的核对另走recovery_required，拒绝不等于撤销外部动作。

最终成果 review 与工具执行 approval 分开：review 校验具体产物版本；review 通过不能倒推授权此前未批准的外部操作。

默认把外部发送、发布、删除、生产写入等能力声明为需要人审，具体按工具 schema 和 owner policy 决定。只读内部子任务可显式配置 auto review；不得在提示词里写“默认同意”来替代服务端策略。

## 6. 凭据与本地设备

凭据由 Vault/secret store 或本机系统 Keychain 管理；AgentSpec、RunContext、checkpoint、workspace、artifact、普通日志只保存 credential ref，不保存长期主密钥。

优先让 connector／凭据代理用短期、最小 scope 凭据执行动作。必须启动外部进程时，仅向该受限进程提供本次调用所需的短期凭据，结束即销毁；禁止把组织所有主密钥长期注入 sandbox shell environment，禁止通过模型输出或命令行参数传递。调试转储、环境快照、stdout 与异常报告同样需要脱敏。

设备配对码一次性、有短期过期时间；claim 后绑定设备 owner 与个人 Space，设备凭据可撤销、轮换。daemon 主动出站连接，校验服务器身份与协议。派发携带允许根目录 ID、action scope、fence 和有效期；本机验证授权路径，不能只做字符串前缀检查，须处理 `..`、symlink、路径替换竞态和越界归档解压。

撤销后停止新派发并撤销未用授权，尽力停止已在运行的命令。网络分区期间无法保证远程即时终止已启动进程；本机不得在租约不可验证或失效后继续新动作，重新连接后先核对。用户电脑已经关机时，云 worker 不会自动取得其文件或浏览器登录态。

## 7. 沙箱、插件与不可信内容

开发 provider 默认仅挂载该任务允许的目录，不挂 Docker socket、宿主 secret 目录或其他 Space 的 home。不需要的网络、命令和资源能力关闭；CPU、内存、超时等限制按宿主能力验证。shell 对任务目录的访问边界必须由 OS/provider 实施，不能仅依赖 prompt。

搜索结果、文档、网页、IM 附件和其他 agent 的结果作为数据处理，不能覆盖系统授权。工具返回标注来源；产物预览按不可信内容隔离，防止 HTML/脚本在主应用 origin 获得登录态。

Creator 产出的 skills、提示词和工具包先是草稿。测试环境使用模拟／低权限账号；发布不自动绑定生产凭据或扩大工具范围。依赖固定版本并记录许可来源；未验证的动态下载和任意 marketplace 安装后置。

## 8. 首版安全验收

| 阶段 | 必须证明的性质 |
| --- | --- |
| M1 | A Space 的用户／worker 不能读取 B 的 Task、session 或事件；旧 fence 不能改状态；创建请求可判重 |
| M2 | workspace/产物路径越界被拒绝；产物版本不可覆盖；重复工具动作不盲目重复副作用；沙箱清理失败不跨任务复用 |
| M3 | 配对码不可重用；撤销设备拒绝新动作；离线未知结果进入 recovery_required；过期／改参审批失效；日志不含测试密钥 |
| M4 | 组织管理员不能读取个人空间；仅授权 pair 可请求；目标受理与结果共享分别执行；群成员不能透传他人私有账号权限 |
| M5/M6 | Creator 无法通过 spec 注入任意工具实现；未验证草稿不能发布；插件测试与正式身份／凭据隔离 |

公开敌对多租户生产上线前另做 threat model、隔离突破、凭据代理、网络策略、插件供应链和恢复测试；此项不是当前可信 beta 已完成的承诺。

## 9. 参考

- [OpenClaw 安全边界](https://docs.openclaw.ai/gateway/security)明确一个 Gateway 一个信任域，角色与共享会话不等于敌对多租户隔离。
- [A2A 授权规范](https://a2a-protocol.org/latest/specification/)区分任务状态、认证和授权；协议对象本身不能取代目标服务对操作 scope 的判断。
