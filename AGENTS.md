# 🛑 关键指令：双轨模式守门人 (Dual-Mode Gatekeeper) 🛑

本项目严格按照“双轨模式 (Dual-Mode)”架构运行。作为 Agent，你**必须**在每个新会话中强制执行以下初始化协议。

## 1. 强制初始化拦截
当用户在此工作空间开启新会话时，如果会话模式尚未锁定，你**绝不能**直接执行用户的请求。
相反，你的**第一个动作**必须是使用 `question` 工具（提问工具）要求用户选择工作模式：
"⚠️ 检测到新会话。请选择当前工作模式（一旦选择，本会话期间不可更改）："
选项：
- "[1] 应用模式 (APP MODE) - 仅限运行、测试、配置，禁止修改核心代码，可提交 Issue 反馈。"
- "[2] 开发模式 (DEV MODE) - 允许修改代码、修复 Issue、并提交 Git Push。"

## 2. 会话锁定与命名固化
一旦用户选择了模式，你的下一条回复**必须**完全以以下文字开头：
- 如果是应用模式: `# [应用模式 APP MODE] 已锁定`
- 如果是开发模式: `# [开发模式 DEV MODE] 已锁定`
紧接着补充说明：“请留意，后续的会话自动命名将包含此模式标识。当前会话已永久锁定为该模式，如需切换请使用 `/new` 开启新会话。”
**绝对禁止**在同一个会话中允许模式切换。

## 3. 应用模式规范 (App Mode Workflow)
如果锁定在应用模式 (APP MODE)：
- **权限限制**：你被**严格禁止**使用 `Write` 或 `Edit` 工具来修改项目源码（例如 `.sh`, `bin/`, `lib/` 等）。如果用户要求，你仅可修改像 `swarm.yaml` 这样的配置文件。
- **反馈流程**：当用户想要提供反馈或报告问题时，总结当前的上下文/任务，识别出问题/建议，然后使用 `Bash` 工具运行 `gh issue create`，并使用 `.github/ISSUE_TEMPLATE/app_feedback.md` 中定义的格式提交到 GitHub 仓库。

## 4. 开发模式规范 (Dev Mode Workflow)
如果锁定在开发模式 (DEV MODE)：
- **权限开放**：赋予完整的文件读写和执行权限。
- **开发闭环**：在实现一个功能后，你**必须**使用 `git status`, `git diff` 检查变更，向用户请求确认，确认后依次运行 `git add`, `git commit -m "..."`, 以及 `git push`。
- **Issue 处理闭环**：如果被要求解决某个 Issue，使用 `gh issue view <ID>` 读取内容，分析代码库，提出修复预案，在用户批准后，编写代码修复它并使用包含 `Fixes #ID` 的 message 提交 (commit)。

---

# 🐝 Claw-Swarm Agent Guidelines

This document provides high-signal instructions for agentic coding assistants (like you) to avoid common mistakes in the `claw-swarm` environment.

## 🛠️ Management Commands (CLI)

Prefer declarative management via `swarm.yaml` and `./bin/claw-apply`.

### Pod Management
- **Apply Configuration**: `./bin/claw-apply` (Syncs `swarm.yaml` to systemd units).
- **Check Cluster Status**: `./bin/claw-status` (Shows memory, models, and health).
- **Interactive TUI**: `./bin/claw-tui <NAME>` (Injects correct env/token for debugging).
- **Manual Provision/Repair**:
  - Provision: `./bin/clawctl <NAME> <PORT> <TOKEN>`
  - Repair/Unify: `./bin/claw-repair <NAME>`
  - Remove: `./bin/claw-rm <NAME>`
- **Systemd Check**: `systemctl --user list-units "openclaw-gateway*"`

### Feishu/Lark Multi-Bot Support

- **Add a Feishu Bot to existing Pod**:
  ```bash
  ./bin/claw-bot-add <PROFILE_NAME> <BOT_ID> <APP_ID> <APP_SECRET> [USER_ID]
  ```
  Example:
  ```bash
  ./bin/claw-bot-add aimee bot2 cli_xxx yyy ou_123
  ```

- **Create Agent and bind to Bot**:
  ```bash
  ./bin/claw-agent-create <PROFILE_NAME> <AGENT_NAME> [BOT_ID]
  ```
  Example:
  ```bash
  ./bin/claw-agent-create aimee aimee2 bot2
  ```

- **Bind existing Agent to Bot**:
  ```bash
  ./bin/claw-bot-bind <PROFILE_NAME> <BOT_ID> <AGENT_NAME>
  ```

- **Configure Feishu (interactive or direct)**:
  ```bash
  ./bin/claw-lark <PROFILE_NAME> [BOT_ID] [APP_ID] [APP_SECRET]
  ```
  Example:
  ```bash
  ./bin/claw-lark aimee bot2 cli_xxx yyy
  ```

## 🤖 Model Management & Troubleshooting

When users report model issues (e.g., "stuck on big-pickle"), use the **`opencode-model-manager`** skill.

### 1. Configuration Hierarchy
- **Local First**: Modify `~/.opencode/opencode.json` within the Pod's isolated environment.
- **Global Fallback**: `~/.config/opencode/opencode.json` is only used if local config is missing.

### 2. Common Fixes
- **Fallback to "big-pickle"**: Usually means the `opencode-antigravity-auth` plugin is broken or Google auth expired.
- **Fixing Plugin**: In `~/.opencode/node_modules/opencode-antigravity-auth/dist/src/plugin/storage.js`, ensure:
  `import * as lockfile from "proper-lockfile";` (NOT default import).
- **Verification**: Use `/new` in the client to reset session context, then ask the agent: "What is your full model ID?"

## 📐 Architecture & Constraints

### 1. The "Pod" Isolation Principle (CRITICAL)
- **Isolation**: Each profile MUST have its own directory (`~/.openclaw-<NAME>`).
- **Plugins**: NEVER symlink `extensions/`. ALWAYS hard copy (`cp -r`) to prevent dependency bleeding.
- **Environment**: Always inject `OPENCLAW_STATE_DIR`, `OPENCLAW_CONFIG_PATH`, and `TMPDIR` in systemd units.

### 2. Code Conventions
- **Systemd**: Deploy as User Units in `~/.config/systemd/user/`.
- **Naming**: Service units MUST match `openclaw-gateway-<name>.service`.

---

## 📱 Matrix Channel Support

### Declarative Configuration (Recommended)
Add Matrix config to `swarm.yaml`:

```yaml
pods:
  - name: main
    matrix:
      enabled: true
      homeserver: https://matrix.org
      accessToken: "${MATRIX_TOKEN}"  # SecretRef format
      encryption: true
      dm:
        policy: pairing
      autoJoin: "allowlist"
```

### CLI Management

- **Add/Update Matrix Config**:
  ```bash
  ./bin/claw-matrix-add <PROFILE> --homeserver <URL> --token <TOKEN> --encryption
  ```

- **E2EE Verification**:
  ```bash
  ./bin/claw-matrix-verify <PROFILE> status
  ./bin/claw-matrix-verify <PROFILE> status --verbose
  ./bin/claw-matrix-verify <PROFILE> bootstrap
  ./bin/claw-matrix-verify <PROFILE> backup status
  ```

- **Device Management**:
  ```bash
  ./bin/claw-matrix-devices <PROFILE> list
  ./bin/claw-matrix-devices <PROFILE> prune-stale
  ```

- **Pairing Approval**:
  ```bash
  ./bin/claw-matrix-pairing <PROFILE> list
  ./bin/claw-matrix-pairing <PROFILE> approve <CODE>
  ```

- **Profile Settings**:
  ```bash
  ./bin/claw-matrix-profile <PROFILE> set-name "Bot Name"
  ./bin/claw-matrix-profile <PROFILE> set-avatar <URL>
  ```

- **Direct Message Repair**:
  ```bash
  ./bin/claw-matrix-direct <PROFILE> inspect --user-id @user:server
  ./bin/claw-matrix-direct <PROFILE> repair --user-id @user:server
  ```

### Supported Configuration Fields

All Matrix configuration fields from official docs are supported:
- Authentication: `accessToken`, `password`, `userId`, multi-account
- Encryption: `encryption`, `startupVerification`
- DM: `dm.policy`, `dm.allowFrom`, `dm.sessionScope`, `dm.threadReplies`
- Groups: `groupPolicy`, `groupAllowFrom`, `autoJoin`, `historyLimit`
- Messaging: `streaming`, `blockStreaming`, `threadReplies`, `markdown`
- Thread Bindings: `threadBindings.enabled`, `idleHours`, `maxAgeHours`
- Exec Approvals: `execApprovals.enabled`, `approvers`, `target`
- Network: `proxy`, `network.dangerouslyAllowPrivateNetwork`
- Per-room: `groups.<room>.*`

---
*Note: Consult `docs/ARCHITECTURE.md` for low-level design details.*