# 双轨模式守门人 (Dual-Mode Gatekeeper)

本项目采用双轨模式运行，通过 opencode agent 机制实现模式切换和权限强制。

## 模式选择

新会话启动时，使用 Tab 键切换 agent：

- **dev-mode** — 完整权限，遵循 Spec 驱动 + git 闭环
- **app-mode** — 所有编辑/命令需用户确认，禁止修改源码

权限由 opencode `permission` 配置机械强制，无需文本约束。

## 应用模式补充规范

应用模式下，如果用户要求修改核心源码，使用 `.github/ISSUE_TEMPLATE/app_feedback.md` 格式提交 Issue 反馈。