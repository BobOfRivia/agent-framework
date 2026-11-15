# agent-framework

基于 **LangGraph / Deep Agents** 的可组合 Agent 基座：创建个人助手与团队数字员工，在任务发布时显式选择本地或云端执行，通过项目群、统筹员工、任务和交付物完成协作。

**当前状态：设计文档仓库，产品代码尚未实现。** 本文与全部基线文档建立于 2026-11-15；开发阶段状态以 [实现记录](docs/implementation-status.md) 为准。

## 从新会话开始

先阅读 [START_HERE.md](START_HERE.md)，再按 [开发计划](docs/development-plan.md) 实现 M0。开发代理须遵循 [AGENTS.md](AGENTS.md)。

可直接复制以下提示到新的编程会话：

> 在 BobOfRivia/agent-framework 仓库开始实现。先读 AGENTS.md、START_HERE.md、docs/implementation-status.md、docs/domain-model.md 和 docs/development-plan.md。保持已确认的产品边界：任务创建前显式选择 local/cloud，无自动迁移；个人助手与员工身份独立于执行位置。先完成 M0 的版本冻结和风险 spike，再实现 M1；只在具备相应验收证据后更新里程碑状态。请检查真实仓库状态，不把文档中的规划目录与命令当作已实现代码。实现和验证后更新状态、决策与下一步交接。

## 初版目标

- Creator 通过参数、提示词、已登记工具与技能创建 Agent；存在能力缺口时调用编码专员，测试后发布扩展。
- 数字员工首版默认在云端；个人端聚焦本机私有文件、应用、本地项目与内网能力。内置编码员工直接接入现成Codex，详见[执行器设计](docs/architecture/coding-executor.md)。
- 同一执行基座承载个人助手和长期数字员工，配置、实例身份、私有记忆和授权分别管理。
- 发布任务时指定 local/cloud。云任务在独立云主机 worker 和沙箱中执行，用户关机后继续；本地设备离线则明确等待。
- 在类似 IM 的项目群邀请员工与个人助手，由统筹员工拆解和委派；系统记录负责人、依赖、状态、预算与验收。
- 任务可暂停、审批、恢复、取消、返工；提交带版本和来源的产物。恢复不能重复执行已确认的外部副作用。

首版是**单个可信团队的私有 Beta**，包含同一部署内个人／团队空间隔离与预授权协作。公开注册的敌对多租户 SaaS、完整原生桌面端、任意外部 Agent 联邦不在首版范围。详见 [PRD](docs/product-requirements.md)。

## 文档入口

| 需要回答的问题 | 文档 |
| --- | --- |
| 需求是否完整、什么属于初版 | [产品需求](docs/product-requirements.md) |
| 框架能覆盖什么、缺口在哪里 | [研究与适配分析](docs/research-and-fit.md) |
| 整体模块、部署与边界 | [架构总览](docs/architecture/overview.md) |
| Agent、Task、Session、沙箱如何建模 | [领域模型](docs/domain-model.md)、[执行环境](docs/architecture/execution-environments.md) |
| Creator 如何装配与编码扩展 | [Creator](docs/architecture/creator.md)、[能力模型](docs/architecture/capabilities.md) |
| 编程顺序与每阶段产出 | [开发计划](docs/development-plan.md) |
| 如何证明完成 | [验收标准](docs/acceptance.md)、[测试策略](docs/testing-strategy.md) |
| 如何从另一会话继续 | [开工说明](START_HERE.md)、[实现状态](docs/implementation-status.md) |

全部索引见 [docs/README.md](docs/README.md)。

## 技术基线

默认 Python 3.12、FastAPI、PostgreSQL、Python worker、LangGraph 与 Deep Agents；Web 使用 TypeScript / React；本地先提供 Python daemon + CLI。具体依赖版本由 M0 核实兼容性后锁定。模块化单体起步，API 与执行 worker 分进程部署。

云沙箱 provider 与持久工作区通过自有接口接入；开发 Docker 不能据此宣称具备敌对多租户强隔离。通用员工采用Deep Agents，编码员工复用Codex专用执行器；第一版不要求厂商托管控制面或LangSmith，不自研编码Agent loop。

## 当前可执行的校验

文档结构与 JSON 语法：

```bash
python3 tools/check_docs.py
```

增加 schema 与示例验证：

```bash
python3 -m pip install -r tools/requirements-docs.txt
python3 tools/check_docs.py --schemas
```

上述工具检查项目文档，不启动 Agent。产品安装、服务启动和测试命令在 M0/M1 实现后补齐并实际验证。

## 许可状态

本仓库暂未指定代码分发许可证；不得默认按 MIT、Apache-2.0 或其他许可对外分发。上游框架及扩展的许可证、版本和通知文件在 M0 记录。产品品牌与代码许可证由仓库所有者后续决定，不阻塞内部原型。
