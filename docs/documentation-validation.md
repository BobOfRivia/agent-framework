# 文档基线校验记录

日期：2026-11-15。范围：项目文档、声明schema、样例及交接合同。产品实现与真实模型／云环境尚未验收。

## 已执行检查

- `python3 tools/check_docs.py`：本地Markdown引用存在、代码围栏平衡、JSON语法与R/AC/WP编号覆盖。
- `uv run --no-project --with 'jsonschema>=4.23,<5' python tools/check_docs.py --schemas`：Draft2020-12 schema自检，4个Agent定义、2个Task样例、事件样例通过；cloud携带device、本地缺device、注入tenant_id的负例均被拒绝。
- `python3 -m py_compile tools/check_docs.py`：校验工具语法通过。

文档结构检查由Python3.9.6运行；schema检查使用临时uv环境Python3.15.2、jsonschema4.26.0。产品默认Python3.12的框架兼容性仍属于M0，没有因此被提前确认。

## 独立合同审查与修正

1. M0增加内置文件/shell/MCP/临时subagent的网关覆盖及稳定action_key实验。
2. Task增加acceptance_contract，children采用同一创建合同。
3. 补齐各blocked_reason的解除操作，审批拒绝、补充资料、未知动作核对有确定路径。
4. 本地文件仅登记获授权元数据；相对路径映射和正文默认留设备，变化须新版本。
5. 定义用allowed_roles，实例绑定实际员工；模板不固化另一部署的实例ID。
6. 明确预算跨attempt累计、子树预留、等待计时、deadline与跨Space费用归属。
7. 统一最终成果review和工具approval；临时内部subagent与持久员工委派分别建模。

## 验证边界

本地链接校验不验证所有外部网站可达，也不渲染Mermaid图；图已人工检查结构。schema只证明声明结构，不证明能力存在、授权有效或实现正确。任何真实产品能力仍须按[验收标准](acceptance.md)提交证据。

最终文件数量和本地引用数量以运行校验工具的输出为准；新增文档后应重新执行。

## 后续设计澄清

按用户要求新增Codex专用执行器、ADR-009、员工与任务样例，数字员工首版cloud，个人端聚焦本机能力。schema预算改为运行时能力校验，不能把不可观测的Codex内部调用次数宣称为硬限制。上面的4个Agent/2个Task记录属于最初基线，更新后校验覆盖5个Agent/3个Task；实际集成仍待M0。

复用策略修订：新增ADR-010、AC-27，开发计划与开工说明增加调度选型gate，PG参考合同与Temporal备选明确区分。未安装新的产品依赖，未把候选服务标成已实现。文档检查同步要求AC-01至AC-27覆盖；实际框架/调度/沙箱实验仍待M0。
