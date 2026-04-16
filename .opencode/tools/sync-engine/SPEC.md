# Onebot 双向同步引擎规格 (Bidirectional Sync Engine)

> **意图账本双向锚定 (Bidirectional Traceability)**
> 📌 **原始意图溯源**：[2026-04-16 意图 3] 架构基建的双向同步引擎 (.opencode/INTENTS.md)
> 🔄 **修订历史 (Changelog)**：
> - v1 (2026-04-16): 初始创建，替代繁琐的 Git Submodule 方案。

---

## 1. 核心意图 (Core Intent)
彻底解决 Onebot 基座与衍生业务项目之间“基建提取与下发”的工程物理同步问题。通过极简的 Shell 脚本实现“就地演进（向上反哺）”与“安全下发（向下同步）”。

## 2. 边界约束 (Constraints)
- 🚫 **同步禁区**：执行 `pull` 时，绝对禁止覆盖下游业务项目的 `opencode.json`（保护业务命令）和 `INTENTS.md`（保护业务意图池）。
- 🚫 **架构禁区**：严禁采用可能导致 Agent 执行 `git status` 时产生幻觉或迷失的 Git 嵌套（Submodule）方案。

## 3. 状态契约 (State Contract)
- **前置依赖**：本地需存在 `/home/imovation/opencode-workspace/onebot` 母体目录（仅 push 时需要）。
- **预期副作用 (pull)**：当前项目的 `.opencode/agents/`、`rules/`、`specs/`、`tools/` 和通用 `skills/` 被云端母体最新版本安全覆写。
- **预期副作用 (push)**：当前项目经过验证的 `.opencode/` 核心组件被逆向提取回本地母体仓库，并自动触发 Git Commit & Push。

## 4. 验收标准 (Acceptance Criteria)
- [ ] **标准 1**：运行 `./onebot.sh pull` 后，业务特有的 `opencode.json` 保持不变。
- [ ] **标准 2**：运行 `./onebot.sh push` 后，母体仓库新增对应的 commit 记录。
