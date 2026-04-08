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
*Note: Consult `docs/ARCHITECTURE.md` for low-level design details.*
