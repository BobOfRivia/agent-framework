# 新编程会话开工说明

本文件是从规划进入编程的交接入口。基线日期：2026-11-15。

## 1. 已确认的决定

- 主运行栈 LangGraph / Deep Agents，具体版本由 M0 验证并锁定。
- 个人助手与数字员工采用同一基座；所有者／权限和 local/cloud 执行位置独立。
- 任务发起前显式选择位置。云任务直接委派云端 worker，用户离线继续；本地任务设备离线则等待。
- 云数字员工是持久身份和事件／计划任务能力；计算按需租用。
- 项目群容纳人、员工与个人助手；统筹员工调用真实任务服务完成拆解和协作。
- Creator 优先配置／提示词／技能装配；能力缺口可生成 Python 工具扩展，验证后发布。
- TaskWorkspace 持久，ExecutionSession 私有，沙箱可回收。不同主体与并行分支明确隔离。
- 初版可信私有 Beta，包含同部署个人／单团队空间隔离；完整公开 SaaS 以后再做。

## 2. 先检查真实状态

1. 读 [代理约定](AGENTS.md) 和 [实现状态](docs/implementation-status.md)。
2. 检查 git branch/status、现有代码、AGENTS 及最新提交，保留用户改动。
3. 读 [领域模型](docs/domain-model.md)、[开发计划](docs/development-plan.md)、[验收标准](docs/acceptance.md)。
4. 如尚无服务代码，从 M0 开始；不要直接构建完整聊天界面或引入另一套内核。

## 3. 第一个编程会话的具体任务

执行工作包 `WP-00` 和 `WP-01`：

- 建立 Python 3.12 项目管理、测试/lint、最小目录及 CI；版本选择以可安装、兼容性实验为依据。
- 验证 Deep Agents + LangGraph/PostgreSQL checkpointer 的组合；运行一个真实模型工具任务，保存并恢复 checkpoint。
- 验证工具审批 interrupt/resume、持久 pending call 与副作用防重放。
- 验证框架内置文件/shell/MCP/临时subagent不能绕过网关；恢复时action_key绑定持久意图而非新attempt。
- 验证云 worker 可独立于 HTTP 客户端退出继续执行；M0 可先做单机 spike，M7 才证明远端云场景。
- 验证开发 Docker 执行后宿主目录边界、环境回收和产物保留。
- 把精确依赖、实验过程、失败与替代方案记录在 `docs/compatibility-matrix.md`（该文件由 M0 创建）。

若模型凭据暂不可用：完成可重复 fake 测试与工程设置，明确标记真实模型 spike 未通过；不能宣称 M0 完成。版本无法支持某能力时优先调整 adapter，记录 ADR 和合同影响。

## 4. 推荐会话启动提示词

```text
请实现 agent-framework 的 M0（WP-00、WP-01），不要同时铺开全部里程碑。
先读 AGENTS.md、START_HERE.md、docs/implementation-status.md、
docs/domain-model.md、docs/development-plan.md、docs/testing-strategy.md。
核实当前 LangGraph/Deep Agents 兼容版本，建立可重复开发环境并运行
checkpoint、审批恢复和沙箱 spike。保留已有用户改动；未验证的行为明确标记。
完成后更新兼容矩阵、实际执行命令、验收证据与下一会话工作包。
```

M0 完成后的下一会话提示可改为“实现 M1 的 WP-02/03，满足对应 AC，保留既有合同”。

## 5. 开发时可自行采用的默认值

Python 3.12、FastAPI、PostgreSQL 作为事务与持久队列、独立 Python worker、React/TypeScript Web、Python 本地 daemon/CLI；先 Linux 云端 + macOS 本地支持，其他 OS 视验证结果扩展。MVP 采用一套注册审批的模型 provider，adapter 不写死厂商。

这些是项目可调整默认，非用户对语言或基础设施供应商的最终承诺。变化要写 ADR，不必为常规可逆实现选择反复等待确认。

## 6. 完成会话的交接格式

本次工作包；完成代码；测试与证据；未通过／未验证；合同变更；commit/PR；下一可领取工作包。同步写入 [实现状态](docs/implementation-status.md)。
