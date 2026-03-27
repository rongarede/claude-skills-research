---
name: ai-vibe-writing-skills
description: 中文/英文写作风格迁移与错误记忆工作流。适用于论文、学位论文、报告等场景，提供 style profile、error log、长期记忆与多智能体写作闭环。
---

# AI Vibe Writing Skills (Compatibility Wrapper)

该仓库原生是写作流程项目（含 `SKILLS.md` 与 `.ai_context/`），并非标准 Codex `SKILL.md` 结构。
本封装用于在 Codex 中直接触发并使用其能力。

## 何时使用

- 需要中文论文/学术写作风格迁移
- 需要“错题本”约束、长期记忆、语法检查
- 需要 outline -> writer -> review 的写作闭环

## 核心资源

- 总览：`SKILLS.md`
- 主说明：`README.md`
- 风格与记忆：`.ai_context/style_profile.md`、`.ai_context/error_log.md`、`.ai_context/memory/`
- 多智能体提示词：`.ai_context/prompts/6_outline_manager_agent.md` 到 `.ai_context/prompts/9_workflow_coordinator.md`

## 推荐流程

1. 首次使用先执行风格提取：读取 `.ai_context/prompts/1_style_extractor.md`
2. 写作时使用 `.ai_context/prompts/2_writer.md`
3. 纠错后更新 `.ai_context/error_log.md`
4. 长文任务按 `.ai_context/prompts/9_workflow_coordinator.md` 跑多智能体流程

## 注意

- 该技能是对上游仓库的兼容封装；上游更新时可重新拉取覆盖。
- 如需论文规范格式门禁，建议与 `latex-thesis-zh`、`peer-review`、`thesis-rewrite-review-orchestrator` 组合使用。
