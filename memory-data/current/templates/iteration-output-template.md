# Iteration Output Template

For a full iteration request, structure the result using this fixed template.

This output format is mandatory. Iteration responses must follow it instead of a shorter ad hoc summary.

`迭代结果`

`一、记忆清洗`

- 应保留为耐久记忆的内容：
- 重复、近重复、过时或作用域错误的内容：
- 建议修正、合并、降级为假设的内容：
- 本轮是否执行了实际清理操作：
- 若已执行，具体改动与验证结果：

`二、人格评估`

- 候选影响人格的记忆：
- 每条候选的证据来源：
- 每条候选影响的人格维度：
- `权限边界 / 记忆边界 / 执行顺序 / 认知模型 / 迭代机制 / 其他`
- 风险判断：
- `可自动小迭代 / 需要用户确认 / 不应进入人格`
- 是否建议现在发布到 `AGENTS.md`：
- 本轮是否已得到用户确认：

`三、AGENTS.md 候选评估`

- 候选写入 `AGENTS.md` 的记忆：
- 每条候选的来源类型：
- `用户直接指令 / 跨任务重复成功 / 长期边界`
- 每条候选的默认行为影响面：
- 每条候选是否满足全局稳定性：
- 每条候选是否更适合留在 `memory / workflow / skill`：
- 建议归类：
- `可进入 AGENTS.md 候选 / 暂留人格层 / 暂留 workflow / 暂留 skill / 不应提升`
- 本轮是否已获得发布确认：

`四、工作流迭代评估`

- 当前哪些工作流与真实执行不一致：
- 建议新增的步骤：
- 建议删除或降级的步骤：
- 建议调整的顺序：
- 建议补强的验证标准：
- 这些变更属于：
- `更新现有工作流 / 新建工作流候选 / 暂留记忆`

`五、skill 晋升评估`

- 候选 skill 的记忆或工作流：
- 每个候选的触发条件是否清晰：
- 每个候选的步骤是否稳定可教：
- 每个候选是否已有重复成功证据：
- 每个候选应归类为：
- `更新现有 skill / 新建 skill 候选 / 暂不晋升`
- 需要用户确认的 skill 动作：

`六、执行建议`

- 只写入记忆的内容：
- 可进入人格但必须先确认的内容：
- 可进入 `AGENTS.md` 候选但必须先确认的内容：
- 应修订的现有工作流或 harness：
- 可晋升为 skill 的候选：
- 本轮明确不应推进的内容：
- 下一步最小动作建议：

For a partial iteration request, return only the relevant section plus a short execution suggestion, but keep the same field names inside that section.
