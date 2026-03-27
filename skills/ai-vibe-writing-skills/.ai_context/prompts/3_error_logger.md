# Context
你刚才的生成中出现了一个我不满意的点。我需要你将这个错误转化为一条永久性的“负面约束规则”，存入 `error_log.md`。

# Auto Trigger (自动触发)
当用户出现以下表达时，无需额外确认，立即触发本流程：
- “不要使用……”
- “别用……这个表述”
- “以后不要写……”
- “禁用……说法”

触发后必须执行：
1. 从用户原话中抽取被禁用表达（`<forbidden_expression>`）。
2. 追加一条可复用规则到 `error_log.md`（遵循下方 Rule Format）。
3. 立即重写当前文本，确保不再出现 `<forbidden_expression>`。

# My Correction
[在此处输入你的修改意见，例如：你刚才用了“In summary”，我写论文从来不用这个词，我习惯用“Conclusion”。或者：不要把“dataset”写成“data set”。]

# Action
1. 分析我的修改意见，提炼出一条通用的规则（Rule）。
2. 将这条规则追加到 `error_log.md` 文件中。
3. 如包含稳定事实或偏好，将其写入长期记忆（硬性/柔性）并按领域归类。
4. **重写** 刚才那段话，应用这条新规则。

# Rule Format for Error Log
请按以下格式更新错题本：
- **[日期] 错误类型**: [简短描述]
  - ❌ **Wrong**: [AI 刚才的写法]
  - ✅ **Right**: [用户希望的写法/风格]
  - 🔒 **Instruction**: [给未来 AI 的具体指令，例如：Default to American spelling; Never start a sentence with "Basically".]
