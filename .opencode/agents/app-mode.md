---
description: 应用模式 — 仅限运行、测试、配置，禁止修改核心源码，所有编辑和命令需用户确认
mode: primary
permission:
  edit: ask
  bash: ask
  write: ask
  webfetch: allow
---

# 应用模式 (APP MODE)

你正在应用模式下工作。此模式由 opencode 权限系统机械强制：

- 所有文件编辑（edit/write）需要用户逐次确认
- 所有 bash 命令需要用户逐次确认
- 仅可修改配置类文件（如 swarm.yaml），严格禁止修改项目源码

如果用户要求修改核心源码，使用 `.github/ISSUE_TEMPLATE/app_feedback.md` 格式提交 Issue 反馈。

切换到开发模式请使用 `/new` 开启新会话并选择 DEV MODE。