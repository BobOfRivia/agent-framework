# 开发环境与贡献指南

状态：规划。当前只有文档、声明schema、样例与校验工具；以下产品工程布局和命令由M0/M1实际建立后才能使用。

## 技术默认

Python 3.12 + uv、FastAPI、Pydantic、SQLAlchemy/Alembic、PostgreSQL、LangGraph/Deep Agents、pytest/ruff/type checker；Web为TypeScript/React和Vite。M0选定精确兼容版本并提交锁文件，不在设计阶段编造版本号。模型provider经adapter接入，首版至少一条真实模型路径。

首个支持矩阵：Linux云服务与macOS本地daemon；本地Windows/Linux和原生桌面壳为后续兼容工作。浏览器文件上传／任务控制属于Web客户端，本机文件／应用能力属于daemon。

## 建议代码布局（尚未创建）

```text
apps/api/                 API、认证、会话与应用服务
apps/worker/              durable job领取、执行与恢复
apps/web/                 项目群、任务、Creator和审阅界面
apps/local/               daemon、CLI、设备配对与本地执行
packages/domain/          Task/Agent/Policy/Artifact合同与规则
packages/runtime/         DeepAgentsRunner、checkpoint和框架适配
packages/capabilities/    注册构件、skills、工具和插件协议
packages/environments/    本地、Docker与后续云provider
packages/storage/         数据库、Outbox、artifact和memory实现
tests/                    领域、集成、故障注入、端到端
evals/                    真实模型样例、rubric与结果摘要
deploy/                   本机开发与远端私有Beta部署配置
```

M0可采用单Python发行包的src布局再按模块划分，避免为每个目录过早建独立发行包；只要依赖方向与角色清晰即可。API与worker分进程，不能由Web请求临时线程承载云任务。

## 配置与凭据

实施时提供 `.env.example` 和启动配置校验，至少覆盖：数据库DSN、artifact存储位置、模型provider/模型ID、secret provider、cloudworker能力、设备连接地址、sandboxprovider、预算及日志脱敏选项。示例只能用占位符，实际凭据不提交。

本地敏感目录采用用户授权的root_id映射，API不接收可直接执行的任意绝对路径。配置、AgentSpec与模板不含实际账号token。API主凭据不得进入生成代码的环境。

## 命令登记

| 命令 | 当前状态 |
| --- | --- |
| python3 tools/check_docs.py | 已提供：文档本地引用、JSON语法和围栏检查 |
| python3 tools/check_docs.py --schemas | 已提供：安装tools/requirements-docs.txt后校验schema和样例 |
| 产品安装、migration、API启动、worker启动、本地配对、Web启动、产品测试 | 待M0/M1建立并在此登记，当前不要假称可用 |

M0结束必须把真实可用命令替换进本表，包括首次安装、重建数据库、开发数据、重置测试环境、启动与停止。每个命令注明是否会清理数据或调用付费模型。

## 贡献和发布

分支按工作包命名，例如 `feat/wp-03-durable-tasks`。PR描述写问题、实现行为、实际验证、风险与关联R/AC。功能PR更新OpenAPI/schema、migration、关键合同测试和实施状态；文档PR只运行必要文档检查。

新依赖记录用途、许可与替代方案；通用主栈保留Deep Agents，编码直接复用Codex专用执行器，不自研coding loop。其他内核适配后置；变化用ADR记录。

首版应用许可证尚未选定，不能擅自发布包或添加授权声明。私有Beta的部署授权与公开开源分发分开处理。
