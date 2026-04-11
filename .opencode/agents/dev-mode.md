---
description: 开发模式 — 完整读写权限，遵循 Spec 驱动开发流程和 git 闭环
mode: primary
permission:
  edit: allow
  bash: allow
  write: allow
  webfetch: allow
---

# 开发模式 (DEV MODE)

你正在开发模式下工作。拥有完整的文件读写和执行权限。

核心开发流程：

1. **Spec 驱动与迭代追溯**：遵循 core-rules.md 中始终生效的规则（先 Spec 再代码、迭代追溯等）
2. **git 闭环**：实现后用 `git status`、`git diff` 检查变更，向用户确认后 git add/commit/push
3. **Issue 处理**：修复 Issue 时，commit message 包含 `Fixes #ID`