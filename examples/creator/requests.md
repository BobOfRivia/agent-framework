# Creator验收需求与能力目录样例

以下是设计样例，不是已安装的工具；实际Registry和技能内容由WP-04/10实现。JSON中的实例ID与artifact ID为演示占位，使用前由开发数据或API创建。

## 最小能力目录目标

| 能力ID／版本 | 参数示例 | 动作权限 | 位置与隔离 |
| --- | --- | --- | --- |
| web.search / 0.1.0 | max_results:10 | web.search | local/cloud，通过受控网络工具 |
| file.read / 0.1.0 | 无；root授权由实例/任务绑定 | file.read | local/cloud，仅获授权工作区 |
| code.python / 0.1.0 | timeout_seconds:120 | code.execute | local/cloud，隔离环境，默认无网络 |
| coding.codex / 0.1.0 | 任务scope由CodexRunner绑定 | coding.execute | 现成Codex专用执行器；团队员工cloud，job边界治理 |
| artifact.publish / 0.1.0 | 无 | artifact.publish | local/cloud，提交hash/类型/ACL |
| task.delegate / 0.1.0 | 无 | task.delegate | 目标须允许，限制深度/预算与输入共享 |
| task.inspect / 0.1.0 | 无 | task.read | 仅当前Space/受限委派视图 |

技能目标：research.with-sources/0.1.0 规定来源与证据要求；data.analysis/0.1.0 规定数据检查、计算和产物格式。技能参数和内容必须版本化，并通过兼容与权限检查，不能据技能文本自动获得权限。

## C1：只装配已有能力

用户输入：“创建一个研究员，为小团队整理竞品资料。允许互联网检索，输出带来源的报告，结果给我审核。”

预期：使用researcher定义和现有目录；保存结构化草稿、缺失信息提示、样例任务和验证报告；不生成新的平台代码；验证通过后发布，实例化时另行绑定owner、工具账号与scope。不能把“发布定义”视为“授权所有动作”。

## C2：局部配置变化

用户输入：“把研究员改成只研究指定网站，每次最多检索8条，报告增加风险和来源日期。”

预期：更新prompt/能力参数/网络allowlist申请与测试，生成新revision；旧任务继续用旧revision；未获授权的站点限制不能因文本变化扩大。

## C3：确有代码缺口

用户输入：“创建供应商评分员工。读取CSV，字段为vendor、price、quality、delivery_days；按给定权重归一化评分，输出排名。现有目录没有这个评分工具。”

预期步骤：

1. Creator补齐权重、归一化、缺值和同分规则，形成可判定输入输出。
2. 内置Codex编码员工在构建沙箱生成Python工具包、manifest、参数schema与依赖锁；平台不实现另一套coding loop。
3. 测试正常样本、缺字段、非法数值、零范围、路径越权；用确定性参考值校验。
4. 工具通过后登记新版本，Creator装配新员工，再用全新实例运行。
5. 发布报告记录包hash、权限要求、测试证据；任何失败不能成为当前版本。

## C4：跨Space分享边界

用户输入：“让我的个人助手参加团队研究群，只分享我指定资料的摘要。”

预期：创建群成员邀请与预授权DelegationRequest scope；原始文件和个人记忆留在个人Space；只将批准的摘要ArtifactVersion共享到团队。Team统筹无法遍历个人目录、调用私人邮箱或读取其他私聊。

## 声明格式与业务验证

JSON schema只验证结构。Registry还须验证ID存在、能力config的专属schema、网络/执行环境、角色授权与依赖兼容。task的artifact引用需在实际Space中存在并具有授权，示例ID本身不能用于绕过检查。
