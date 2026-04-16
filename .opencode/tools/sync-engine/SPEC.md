# Onebot 双向同步引擎规格 (Bidirectional Sync Engine)

> **意图账本双向锚定 (Bidirectional Traceability)**
> 📌 **原始意图溯源**：[2026-04-16 意图 3] 架构基建的双向同步引擎 (.opencode/INTENTS.md)
> 🔄 **修订历史 (Changelog)**：
> - v1 (2026-04-16): 初始创建，替代繁琐的 Git Submodule 方案。

## 1. 核心意图 (Core Intent)
彻底解决 Onebot 基座与衍生业务项目之间“基建提取与下发”的工程物理同步问题。通过极简的 Shell 脚本实现“就地演进（向上反哺）”与“安全下发（向下同步）”。

## 2. 边界约束 (Constraints)
- 🚫 **同步禁区**：执行 `pull` 时，绝对禁止覆盖下游业务项目的 `opencode.json`（保护业务命令）和 `INTENTS.md`（保护业务意图池）。
- 🚫 **架构禁区**：严禁采用可能导致 Agent 执行 `git status` 时产生幻觉或迷失的 Git 嵌套（Submodule）方案。

## 3. 状态契约 (State Contract)
- **前置依赖**：本地需存在 Onebot 母体目录（仅 push 时需要）。
- **预期副作用 (pull)**：当前项目的 `.opencode/agents/`、`rules/`、`specs/`、`tools/` 和通用 `skills/` 被云端母体最新版本安全覆写。
- **预期副作用 (push)**：当前项目经过验证的 `.opencode/` 核心组件被逆向提取回本地母体仓库，并自动触发 Git Commit & Push。

## 4. 验收标准 (Acceptance Criteria)
- [ ] 标准 1：运行 `./onebot.sh pull` 后，业务特有的 `opencode.json` 保持不变。
- [ ] 标准 2：运行 `./onebot.sh push` 后，母体仓库新增对应的 commit 记录。

---

## 5. 实现细节 (Implementation Details)

### 核心愿景
Onebot 并不是一个静态的模板库，而是一个具备“自进化”能力的智能体基座。为了解决基座与衍生业务项目之间“基建提取与下发”的工程问题，我们引入了轻量的源码级双向同步引擎 `onebot.sh`。

## 二、 设计哲学
本引擎彻底摒弃了 Git Submodule 或全局挂载包等复杂的依赖管理模式，而是遵循“源码即资产”的原则，确保：
1. **就地演进 (Upstreaming)**：在具体业务的战壕里打磨基建规则，一旦成熟，一键反哺至母体。
2. **安全下发 (Downstreaming)**：母体进化后，子项目可以通过一键拉取吸纳最新认知，且绝对不会覆盖子项目的业务个性化配置。

## 三、 功能规格 (Functional Spec)

### 1. `pull` - 向下同步 (Downstream)
- **触发场景**：当 `onebot` 母体仓库在远端有更新，子项目需要吸纳最新的基建规则时。
- **执行逻辑**：
  1. 通过 `curl` 从远端（`main.zip`）拉取纯净源码。
  2. 解压至临时目录。
  3. **安全覆盖**：精准提取 `.opencode/agents/`、`.opencode/rules/`、`.opencode/specs/`、`.opencode/skills/deep-cure/`。
  4. **保护红线**：严禁覆盖根目录下的 `opencode.json`（其中包含业务注册命令）和业务专属的 `INTENTS.md`。

### 2. `push` - 向上反哺 (Upstream)
- **触发场景**：在子项目（如 `claw-swarm`）中，`platform-dev` 或 `biz-dev` 遇到了规则局限，就地修改了子项目的 `.opencode/` 基建并验证通过后。
- **执行逻辑**：
  1. 定位本地的 Onebot 母体仓库（默认 `~/opencode-workspace/onebot`）。
  2. **逆向提取**：将当前项目中经过业务验证的核心架构文件夹（`agents/`、`rules/`、`specs/`、`deep-cure/`）复制回母体仓库。
  3. **自动发布**：在母体仓库中自动执行 Git 的 Add、Commit（携带标准化提交信息）与 Push 操作。

## 四、 边界与约束
- 本引擎仅处理 `.opencode/` 目录内的“元架构”资产，不涉及任何业务代码的同步。
- 本脚本应作为业务项目的公共资产被跟踪在版本控制中，供任何开发者使用。